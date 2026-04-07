from pathlib import Path
import json
import joblib

ROOT_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT_DIR / "models"

_pipeline = None
_meta = None


def load_multimodal_model():
    global _pipeline, _meta

    if _pipeline is None:
        _pipeline = joblib.load(MODEL_DIR / "multimodal_pipeline.joblib")

    if _meta is None:
        with open(MODEL_DIR / "multimodal_meta.json", "r", encoding="utf-8") as f:
            _meta = json.load(f)

    return _pipeline, _meta