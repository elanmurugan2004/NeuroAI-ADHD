from pathlib import Path
import joblib
from tensorflow.keras.models import load_model

ROOT_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT_DIR / "models"

_bilstm = None
_transformer = None
_preprocessor = None
_meta = None


def _require_file(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Required model file not found: {path}")


def load_ensemble_models():
    global _bilstm, _transformer, _preprocessor, _meta

    bilstm_path = MODEL_DIR / "bilstm_model.h5"
    transformer_path = MODEL_DIR / "transformer_model.h5"
    preprocessor_path = MODEL_DIR / "preprocessor.pkl"
    meta_path = MODEL_DIR / "ensemble_meta.pkl"

    _require_file(bilstm_path)
    _require_file(transformer_path)
    _require_file(preprocessor_path)
    _require_file(meta_path)

    if _bilstm is None:
        _bilstm = load_model(str(bilstm_path), compile=False)

    if _transformer is None:
        _transformer = load_model(str(transformer_path), compile=False)

    if _preprocessor is None:
        _preprocessor = joblib.load(preprocessor_path)

    if _meta is None:
        _meta = joblib.load(meta_path)

    return _bilstm, _transformer, _preprocessor, _meta