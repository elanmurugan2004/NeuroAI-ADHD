from pathlib import Path
import re
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

PHENO_FILE = ROOT / "data" / "raw" / "official_adhd200" / "phenotypic" / "adhd200_preprocessed_phenotypics.tsv"
TS_ROOT = ROOT / "data" / "raw" / "official_adhd200" / "timeseries"
OUT_FILE = ROOT / "data" / "processed" / "training_multimodal_official_ho.csv"


def norm_col(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(name).strip().lower()).strip("_")


def normalize_subject_id(value):
    if pd.isna(value):
        return None
    text = str(value).strip()
    match = re.search(r"(\d+)", text)
    if not match:
        return None
    return match.group(1).zfill(7)


def pick_subject_column(df: pd.DataFrame) -> str:
    normalized = {norm_col(c): c for c in df.columns}
    candidates = [
        "scandir_id",
        "scan_dir_id",
        "subject",
        "subject_id",
        "id",
    ]
    for key in candidates:
        if key in normalized:
            return normalized[key]
    raise ValueError(f"Could not find subject column in phenotypic file. Columns: {list(df.columns)}")


def get_first_available(meta: dict, keys):
    for key in keys:
        if key in meta and pd.notna(meta[key]) and str(meta[key]).strip() != "":
            return meta[key]
    return None


def normalize_sex(value):
    if value is None or pd.isna(value):
        return None
    text = str(value).strip().lower()
    if text in {"male", "m", "1"}:
        return "M"
    if text in {"female", "f", "0", "2"}:
        return "F"
    return str(value).strip()


def normalize_handedness(value):
    if value is None or pd.isna(value):
        return None
    text = str(value).strip().lower()
    if text in {"right", "r", "1"}:
        return "R"
    if text in {"left", "l", "2"}:
        return "L"
    if text in {"both", "ambidextrous", "a", "mixed"}:
        return "A"
    return str(value).strip()


def normalize_label(meta: dict):
    direct = get_first_available(meta, ["dx", "adhd", "label"])
    if direct is not None:
        text = str(direct).strip().lower()

        if text in {"1", "1.0", "adhd", "yes", "true", "case"}:
            return 1
        if text in {"0", "0.0", "control", "tdc", "no", "false", "typical"}:
            return 0

        try:
            num = float(direct)
            if num == 1:
                return 1
            if num == 0:
                return 0
        except Exception:
            pass

    diag = get_first_available(meta, ["diagnosis", "diagnosis_using_cdis", "adhd_subtype", "subtype"])
    if diag is not None:
        text = str(diag).strip().lower()
        if "adhd" in text:
            return 1
        if "tdc" in text or "control" in text or "typically developing" in text:
            return 0

    tdc = get_first_available(meta, ["tdc"])
    if tdc is not None:
        text = str(tdc).strip().lower()
        if text in {"1", "1.0", "true"}:
            return 0
        if text in {"0", "0.0", "false"}:
            return 1

    return np.nan


def load_phenotypic_table():
    if not PHENO_FILE.exists():
        raise FileNotFoundError(f"Phenotypic file not found: {PHENO_FILE}")

    df = pd.read_csv(PHENO_FILE, sep="\t")
    df.columns = [norm_col(c) for c in df.columns]

    subject_col = pick_subject_column(df)
    df["subject"] = df[subject_col].apply(normalize_subject_id)
    df = df[df["subject"].notna()].copy()
    df = df.drop_duplicates(subset=["subject"], keep="first")

    pheno_map = {}
    for _, row in df.iterrows():
        meta = row.to_dict()

        age = get_first_available(meta, ["age"])
        sex = get_first_available(meta, ["sex", "gender"])
        handedness = get_first_available(meta, ["handedness"])
        iq = get_first_available(meta, ["full_4_iq", "full_2_iq", "iq", "viq", "piq"])
        site = get_first_available(meta, ["site"])
        diagnosis = get_first_available(meta, ["dx", "diagnosis_using_cdis", "adhd_subtype", "subtype", "diagnosis"])

        pheno_map[row["subject"]] = {
            "subject": row["subject"],
            "age": float(age) if age is not None and str(age) != "nan" else np.nan,
            "sex": normalize_sex(sex),
            "handedness": normalize_handedness(handedness),
            "iq": float(iq) if iq is not None and str(iq) != "nan" else np.nan,
            "site": str(site).strip() if site is not None else None,
            "diagnosis_text": str(diagnosis).strip() if diagnosis is not None else None,
            "adhd": normalize_label(meta),
        }

    return pheno_map


def choose_one_timeseries_file(subject_files):
    """
    Pick one consistent HO time-course file per subject.
    Preference:
    1. snwmrda + rest_1
    2. sfnwmrda + rest_1
    3. snwmrda
    4. sfnwmrda
    """
    def score(path: Path):
        name = path.name.lower()
        if name.startswith("snwmrda") and "_rest_1_" in name:
            return (0, name)
        if name.startswith("sfnwmrda") and "_rest_1_" in name:
            return (1, name)
        if name.startswith("snwmrda"):
            return (2, name)
        if name.startswith("sfnwmrda"):
            return (3, name)
        return (4, name)

    return sorted(subject_files, key=score)[0]


def collect_subject_files():
    grouped = {}

    for file_path in TS_ROOT.rglob("*_ho_TCs.1D"):
        parent_name = file_path.parent.name
        if not re.fullmatch(r"\d{7}", parent_name):
            continue

        name = file_path.name.lower()

        if not (name.startswith("snwmrda") or name.startswith("sfnwmrda")):
            continue

        subject_id = parent_name
        grouped.setdefault(subject_id, []).append(file_path)

    selected = {}
    for subject_id, files in grouped.items():
        selected[subject_id] = choose_one_timeseries_file(files)

    return selected


def build_connectivity_features(ts_file: Path):
    numeric_rows = []

    with open(ts_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.lower().startswith("file"):
                continue

            parts = line.split(maxsplit=2)
            if len(parts) < 3:
                continue

            numeric_text = parts[2]

            nums = re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", numeric_text)
            if not nums:
                continue

            row = [float(x) for x in nums]
            numeric_rows.append(row)

    if not numeric_rows:
        raise ValueError(f"No numeric rows found in {ts_file}")

    row_lengths = {}
    for row in numeric_rows:
        row_lengths[len(row)] = row_lengths.get(len(row), 0) + 1

    target_len = max(row_lengths, key=row_lengths.get)
    numeric_rows = [row for row in numeric_rows if len(row) == target_len]

    arr = np.array(numeric_rows, dtype=float)
    arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)

    if arr.ndim != 2:
        raise ValueError(f"Unexpected array dimension: {arr.ndim} for {ts_file}")

    if arr.shape[0] < 5 or arr.shape[1] < 5:
        raise ValueError(f"Bad HO shape after parsing: {arr.shape} for {ts_file}")

    corr = np.corrcoef(arr, rowvar=False)
    corr = np.nan_to_num(corr, nan=0.0, posinf=0.0, neginf=0.0)

    tri = np.triu_indices(corr.shape[0], k=1)
    features = corr[tri]

    return arr.shape[0], arr.shape[1], features


def main():
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    print("Loading phenotypic table...")
    pheno_map = load_phenotypic_table()
    print(f"Phenotypic subjects: {len(pheno_map)}")

    print("Scanning HO time-course files...")
    selected_files = collect_subject_files()
    print(f"Subjects with HO time courses: {len(selected_files)}")

    rows = []
    skipped = []

    for subject_id, ts_file in selected_files.items():
        try:
            n_timepoints, n_regions, features = build_connectivity_features(ts_file)

            meta = pheno_map.get(subject_id, {})
            site_folder = ts_file.parents[1].name

            row = {
                "subject": subject_id,
                "site_folder": site_folder,
                "source_file": ts_file.name,
                "n_timepoints": n_timepoints,
                "n_regions": n_regions,
                "age": meta.get("age", np.nan),
                "sex": meta.get("sex"),
                "handedness": meta.get("handedness"),
                "iq": meta.get("iq", np.nan),
                "site": meta.get("site"),
                "diagnosis_text": meta.get("diagnosis_text"),
                "adhd": meta.get("adhd", np.nan),
            }

            for i, value in enumerate(features):
                row[f"conn_{i}"] = float(value)

            rows.append(row)

            if len(rows) <= 5:
                print("ADDED:", subject_id, ts_file.name, n_timepoints, n_regions, len(features), "label=", row["adhd"])

        except Exception as e:
            skipped.append((subject_id, str(e)))

            if len(skipped) <= 20:
                print("SKIPPED:", subject_id, ts_file.name, str(e))

    if not rows:
        print("\nNo rows added. First 20 skipped:\n")
        for item in skipped[:20]:
            print(item)
        raise RuntimeError("No rows were built. Check the extracted HO files.")

    df = pd.DataFrame(rows)

    front_cols = [
        "subject",
        "age",
        "sex",
        "handedness",
        "site",
        "iq",
        "adhd",
        "diagnosis_text",
        "site_folder",
        "source_file",
        "n_timepoints",
        "n_regions",
    ]
    conn_cols = [c for c in df.columns if c.startswith("conn_")]
    df = df[front_cols + conn_cols]

    df.to_csv(OUT_FILE, index=False)

    print("\nSaved:")
    print(OUT_FILE)
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"Connectivity columns: {len(conn_cols)}")

    print("\nADHD label counts:")
    print(df["adhd"].value_counts(dropna=False))

    if skipped:
        print(f"\nSkipped subjects: {len(skipped)}")
        print("First 10 skipped examples:")
        for item in skipped[:10]:
            print(item)


if __name__ == "__main__":
    main()