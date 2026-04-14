import numpy as np

REGION_MEANINGS = {
    "Frontal Pole": "Associated with attention control, planning, and decision-making.",
    "Superior Frontal Gyrus": "Associated with executive function, working memory, and attention regulation.",
    "Middle Frontal Gyrus": "Associated with cognitive control and sustained attention.",
    "Inferior Frontal Gyrus": "Associated with response inhibition and behavioral control.",
    "Precentral Gyrus": "Associated with motor planning and voluntary movement control.",
    "Insular Cortex": "Associated with salience processing, awareness, and emotion-related integration.",
    "Frontal Medial Cortex": "Associated with emotional regulation, attention, and self-monitoring.",
    "Cingulate Gyrus": "Associated with attention shifting, error monitoring, and emotional processing.",
    "Parahippocampal Gyrus": "Associated with memory processing and contextual learning.",
    "Temporal Pole": "Associated with emotional and social information processing.",
    "Superior Temporal Gyrus": "Associated with auditory processing, language, and social perception.",
    "Inferior Temporal Gyrus": "Associated with visual processing and object recognition.",
    "Fusiform Cortex": "Associated with high-level visual recognition and pattern processing.",
    "Precuneus Cortex": "Associated with attention, self-related processing, and visuospatial integration.",
    "Lateral Occipital Cortex": "Associated with visual perception and interpretation.",
    "Postcentral Gyrus": "Associated with sensory processing and body awareness.",
}


def _safe_region_name(region_labels, idx):
    try:
        if region_labels is None:
            return f"Atlas Region {idx}"

        name = str(region_labels[idx]).strip()

        if not name or name.lower() in ["background", "unknown", "nan"]:
            return f"Atlas Region {idx}"

        return name
    except Exception:
        return f"Atlas Region {idx}"


def _contribution_level(score: float) -> str:
    if score >= 20:
        return "High"
    if score >= 10:
        return "Moderate"
    return "Mild"


def _region_meaning(region_name: str) -> str:
    region_name = str(region_name)
    for key, meaning in REGION_MEANINGS.items():
        if key.lower() in region_name.lower():
            return meaning
    return "Region identified by Explainable AI as influential for this scan."


def _region_group(region_name: str) -> str:
    name = str(region_name).lower()

    if any(x in name for x in ["frontal", "cingulate", "precentral"]):
        return "frontal executive-control"
    if any(x in name for x in ["temporal", "fusiform", "parahippocampal"]):
        return "temporal-limbic"
    if any(x in name for x in ["occipital", "precuneus"]):
        return "posterior visual-attention"
    if "insular" in name:
        return "salience-network"
    return "functionally relevant"


def _parse_connection_pair(connection_mapping, conn_idx, region_labels):
    default_a = f"Atlas Region {conn_idx}"
    default_b = f"Atlas Region {conn_idx}"

    if connection_mapping is None:
        return default_a, default_b

    try:
        pair = connection_mapping[conn_idx]
    except Exception:
        pair = None

    if pair is None:
        return default_a, default_b

    if isinstance(pair, (list, tuple)) and len(pair) >= 2:
        a, b = pair[0], pair[1]
        a = _safe_region_name(region_labels, a) if isinstance(a, int) else str(a)
        b = _safe_region_name(region_labels, b) if isinstance(b, int) else str(b)
        return a, b

    if isinstance(pair, dict):
        a = pair.get("region_1", pair.get("source", pair.get("a", default_a)))
        b = pair.get("region_2", pair.get("target", pair.get("b", default_b)))
        a = _safe_region_name(region_labels, a) if isinstance(a, int) else str(a)
        b = _safe_region_name(region_labels, b) if isinstance(b, int) else str(b)
        return a, b

    return default_a, default_b


def explain_multimodal_prediction(
    X,
    region_labels=None,
    connection_mapping=None,
    predicted_label=None,
    confidence=None,
):
    if X is None or len(X) == 0:
        return {
            "top_regions": [],
            "top_connections": [],
            "clinical_summary": "No explainability data available.",
            "recommendation": "Clinical review is recommended.",
            "interpretation_note": "This explanation reflects AI model influence and not direct tissue damage.",
        }

    row = X.iloc[0]
    conn_cols = [c for c in X.columns if str(c).startswith("conn_")]

    if not conn_cols:
        return {
            "top_regions": [],
            "top_connections": [],
            "clinical_summary": "Connectivity features were not available for explanation.",
            "recommendation": "Clinical review is recommended.",
            "interpretation_note": "This explanation reflects AI model influence and not direct tissue damage.",
        }

    region_scores = {}
    connection_scores = []

    for col in conn_cols:
        try:
            conn_idx = int(str(col).replace("conn_", ""))
        except Exception:
            continue

        try:
            value = float(row[col])
        except Exception:
            value = 0.0

        contribution = abs(value)

        region_a, region_b = _parse_connection_pair(
            connection_mapping,
            conn_idx,
            region_labels
        )

        region_scores[region_a] = region_scores.get(region_a, 0.0) + contribution
        region_scores[region_b] = region_scores.get(region_b, 0.0) + contribution

        connection_scores.append({
            "connection": f"{region_a} ↔ {region_b}",
            "contribution": round(contribution, 4),
            "level": _contribution_level(contribution),
        })

    sorted_regions = sorted(region_scores.items(), key=lambda x: x[1], reverse=True)

    top_regions = [
        {
            "region": region,
            "contribution": round(score, 4),
            "level": _contribution_level(score),
            "meaning": _region_meaning(region),
            "group": _region_group(region),
        }
        for region, score in sorted_regions[:8]
    ]

    top_connections = sorted(
        connection_scores,
        key=lambda x: x["contribution"],
        reverse=True
    )[:8]

    if top_regions:
        top_names = [r["region"] for r in top_regions[:3]]
        groups = list(dict.fromkeys([r["group"] for r in top_regions[:3]]))
        group_text = ", ".join(groups)
        label_text = predicted_label if predicted_label else "this assessment"

        clinical_summary = (
            f"For this uploaded scan, the most influential brain regions were "
            f"{', '.join(top_names)}. "
            f"These regions mainly reflect {group_text} patterns and contributed most to the AI decision for {label_text}."
        )
    else:
        clinical_summary = (
            "Region-level explanation could not identify strong dominant regions for this scan."
        )

    if confidence is not None:
        if confidence < 70:
            recommendation = "Low-confidence prediction. Specialist review is recommended."
        elif predicted_label == "ADHD":
            recommendation = "Clinical correlation and specialist evaluation are recommended."
        else:
            recommendation = "Clinical review is recommended."
    else:
        recommendation = "Clinical review is recommended."

    return {
        "top_regions": top_regions,
        "top_connections": top_connections,
        "clinical_summary": clinical_summary,
        "recommendation": recommendation,
        "interpretation_note": "This explanation reflects AI model influence and not direct structural damage.",
    }