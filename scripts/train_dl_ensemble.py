from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score

from tensorflow.keras import layers, models, callbacks
from tensorflow.keras.models import Model

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "training_multimodal_official_ho.csv"
MODELS_DIR = ROOT / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

MAX_CONN_FEATURES = 1000
RANDOM_STATE = 42

np.random.seed(RANDOM_STATE)
tf.keras.utils.set_random_seed(RANDOM_STATE)


def find_target_col(df: pd.DataFrame) -> str:
    lower_map = {c.lower(): c for c in df.columns}
    candidates = ["adhd", "diagnosis", "dx", "label"]
    for c in candidates:
        if c in lower_map:
            return lower_map[c]
    raise ValueError(f"Target column not found. Available columns: {list(df.columns)}")


def to_binary(v):
    s = str(v).strip().lower()

    if s in {"1", "1.0", "adhd", "yes", "true", "case"}:
        return 1
    if s in {"0", "0.0", "control", "tdc", "no", "false", "typical"}:
        return 0

    try:
        num = float(v)
        return 1 if num == 1 else 0 if num == 0 else None
    except Exception:
        return None


def pick_existing_columns(df: pd.DataFrame, preferred_names):
    lower_map = {c.lower(): c for c in df.columns}
    selected = []
    for name in preferred_names:
        if name.lower() in lower_map:
            selected.append(lower_map[name.lower()])
    return list(dict.fromkeys(selected))


def build_bilstm_model(n_features: int):
    model = models.Sequential(
        [
            layers.Input(shape=(n_features, 1)),
            layers.Bidirectional(layers.LSTM(16, return_sequences=False)),
            layers.Dropout(0.30),
            layers.Dense(16, activation="relu"),
            layers.Dropout(0.20),
            layers.Dense(1, activation="sigmoid"),
        ]
    )

    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy", tf.keras.metrics.AUC(name="auc")],
    )
    return model


def build_transformer_model(n_features: int):
    inp = layers.Input(shape=(n_features, 1))

    x = layers.Dense(24)(inp)

    attn = layers.MultiHeadAttention(num_heads=2, key_dim=12)(x, x)
    x = layers.Add()([x, attn])
    x = layers.LayerNormalization()(x)

    ff = layers.Dense(48, activation="relu")(x)
    ff = layers.Dense(24)(ff)
    x = layers.Add()([x, ff])
    x = layers.LayerNormalization()(x)

    x = layers.GlobalAveragePooling1D()(x)
    x = layers.Dropout(0.30)(x)
    x = layers.Dense(16, activation="relu")(x)
    x = layers.Dropout(0.20)(x)
    out = layers.Dense(1, activation="sigmoid")(x)

    model = Model(inp, out)
    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy", tf.keras.metrics.AUC(name="auc")],
    )
    return model


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    print("Loading official dataset...")
    df = pd.read_csv(DATA_PATH)
    print("Raw shape:", df.shape)

    target_col = find_target_col(df)

    y = df[target_col].apply(to_binary)
    df = df.loc[y.notna()].copy()
    y = y.loc[y.notna()].astype(int)

    if y.nunique() < 2:
        raise ValueError("Need both ADHD and Control classes for training.")

    phenotype_cols = pick_existing_columns(
        df,
        ["age", "iq", "sex", "handedness", "site"]
    )

    all_conn_cols = sorted(
        [c for c in df.columns if c.startswith("conn_")],
        key=lambda x: int(x.split("_")[1])
    )

    if not all_conn_cols:
        raise ValueError("No conn_ columns found in dataset.")

    print("Phenotype columns:", phenotype_cols)
    print("All connectivity columns:", len(all_conn_cols))
    print("Class counts:", y.value_counts().to_dict())

    base_feature_cols = phenotype_cols + all_conn_cols
    X_full = df[base_feature_cols].copy()

    X_train_df, X_test_df, y_train, y_test = train_test_split(
        X_full,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    # Select top-variance connectivity features from TRAIN split only
    if len(all_conn_cols) > MAX_CONN_FEATURES:
        train_conn_var = X_train_df[all_conn_cols].apply(pd.to_numeric, errors="coerce").var(axis=0)
        selected_conn_cols = (
            train_conn_var.sort_values(ascending=False)
            .head(MAX_CONN_FEATURES)
            .index
            .tolist()
        )
    else:
        selected_conn_cols = all_conn_cols

    selected_conn_cols = sorted(
        selected_conn_cols,
        key=lambda x: int(x.split("_")[1])
    )

    feature_cols = phenotype_cols + selected_conn_cols

    X_train_df = X_train_df[feature_cols].copy()
    X_test_df = X_test_df[feature_cols].copy()

    categorical_cols = [c for c in phenotype_cols if c.lower() in {"sex", "handedness", "site"}]
    numeric_cols = [c for c in feature_cols if c not in categorical_cols]

    print("Selected connectivity columns:", len(selected_conn_cols))
    print("Total training columns:", len(feature_cols))
    print("Train shape before preprocessing:", X_train_df.shape)
    print("Test shape before preprocessing:", X_test_df.shape)

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric_cols,
            ),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_cols,
            ),
        ],
        sparse_threshold=0,
    )

    X_train = preprocessor.fit_transform(X_train_df)
    X_test = preprocessor.transform(X_test_df)

    if hasattr(X_train, "toarray"):
        X_train = X_train.toarray()
        X_test = X_test.toarray()

    X_train = np.asarray(X_train, dtype=np.float32)
    X_test = np.asarray(X_test, dtype=np.float32)

    print("Processed train shape:", X_train.shape)
    print("Processed test shape:", X_test.shape)

    joblib.dump(preprocessor, MODELS_DIR / "preprocessor.pkl")

    n_features = X_train.shape[1]
    X_train_seq = X_train.reshape(X_train.shape[0], n_features, 1)
    X_test_seq = X_test.reshape(X_test.shape[0], n_features, 1)

    classes = np.unique(y_train)
    weights = compute_class_weight(
        class_weight="balanced",
        classes=classes,
        y=y_train,
    )
    class_weight = {int(c): float(w) for c, w in zip(classes, weights)}
    print("Class weights:", class_weight)

    cb = [
        callbacks.EarlyStopping(
            monitor="val_loss",
            patience=5,
            restore_best_weights=True,
        ),
        callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=2,
            min_lr=1e-5,
        ),
    ]

    print("\nTraining BiLSTM...")
    bilstm = build_bilstm_model(n_features)
    bilstm.fit(
        X_train_seq,
        y_train,
        validation_split=0.2,
        epochs=20,
        batch_size=16,
        class_weight=class_weight,
        callbacks=cb,
        verbose=1,
    )
    bilstm.save(MODELS_DIR / "bilstm_model.h5")

    print("\nTraining Transformer...")
    transformer = build_transformer_model(n_features)
    transformer.fit(
        X_train_seq,
        y_train,
        validation_split=0.2,
        epochs=20,
        batch_size=16,
        class_weight=class_weight,
        callbacks=cb,
        verbose=1,
    )
    transformer.save(MODELS_DIR / "transformer_model.h5")

    print("\nEvaluating models...")
    bilstm_probs = bilstm.predict(X_test_seq, verbose=0).ravel()
    transformer_probs = transformer.predict(X_test_seq, verbose=0).ravel()
    ensemble_probs = (bilstm_probs + transformer_probs) / 2.0

    bilstm_preds = (bilstm_probs >= 0.5).astype(int)
    transformer_preds = (transformer_probs >= 0.5).astype(int)
    ensemble_preds = (ensemble_probs >= 0.5).astype(int)

    metrics = {
        "bilstm_accuracy": float(accuracy_score(y_test, bilstm_preds)),
        "transformer_accuracy": float(accuracy_score(y_test, transformer_preds)),
        "ensemble_accuracy": float(accuracy_score(y_test, ensemble_preds)),
        "bilstm_roc_auc": float(roc_auc_score(y_test, bilstm_probs)),
        "transformer_roc_auc": float(roc_auc_score(y_test, transformer_probs)),
        "ensemble_roc_auc": float(roc_auc_score(y_test, ensemble_probs)),
        "n_features_after_preprocessing": int(n_features),
        "selected_conn_feature_count": int(len(selected_conn_cols)),
        "train_size": int(len(y_train)),
        "test_size": int(len(y_test)),
        "class_weight": {str(k): float(v) for k, v in class_weight.items()},
    }

    print("\nBiLSTM accuracy:", metrics["bilstm_accuracy"])
    print("Transformer accuracy:", metrics["transformer_accuracy"])
    print("Ensemble accuracy:", metrics["ensemble_accuracy"])
    print("Ensemble ROC AUC:", metrics["ensemble_roc_auc"])

    print("\nEnsemble classification report:")
    print(classification_report(y_test, ensemble_preds, digits=4))

    print("Confusion matrix:")
    print(confusion_matrix(y_test, ensemble_preds))

    meta = {
        "dataset_path": str(DATA_PATH),
        "target_col": target_col,
        "ensemble_method": "average",
        "threshold": 0.5,
        "max_conn_features": MAX_CONN_FEATURES,
        "selected_conn_cols": selected_conn_cols,
        "phenotype_cols": phenotype_cols,
        "categorical_cols": categorical_cols,
        "numeric_cols": numeric_cols,
        "metrics": metrics,
        "class_names": {
            "0": "Control",
            "1": "ADHD",
        },
    }

    joblib.dump(meta, MODELS_DIR / "ensemble_meta.pkl")

    with open(MODELS_DIR / "dl_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print("\nSaved files:")
    print("- models/bilstm_model.h5")
    print("- models/transformer_model.h5")
    print("- models/preprocessor.pkl")
    print("- models/ensemble_meta.pkl")
    print("- models/dl_metrics.json")
    print("\nDONE.")


if __name__ == "__main__":
    main()