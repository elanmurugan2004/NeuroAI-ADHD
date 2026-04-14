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
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
    f1_score,
    balanced_accuracy_score,
)

from tensorflow.keras import layers, models, callbacks
from tensorflow.keras.models import Model

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "training_multimodal_official_ho.csv"
MODELS_DIR = ROOT / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42
MAX_CONN_FEATURES = 500
TEST_SIZE = 0.20
VAL_SIZE_FROM_REMAINING = 0.20

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
        if num == 1:
            return 1
        if num == 0:
            return 0
        return None
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
            layers.Bidirectional(layers.LSTM(24, return_sequences=False)),
            layers.Dropout(0.35),
            layers.Dense(24, activation="relu"),
            layers.Dropout(0.25),
            layers.Dense(1, activation="sigmoid"),
        ]
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="binary_crossentropy",
        metrics=["accuracy", tf.keras.metrics.AUC(name="auc")],
    )
    return model


def build_transformer_model(n_features: int):
    inp = layers.Input(shape=(n_features, 1))

    x = layers.Dense(32)(inp)

    attn = layers.MultiHeadAttention(num_heads=2, key_dim=16, dropout=0.10)(x, x)
    x = layers.Add()([x, attn])
    x = layers.LayerNormalization()(x)

    ff = layers.Dense(64, activation="relu")(x)
    ff = layers.Dropout(0.15)(ff)
    ff = layers.Dense(32)(ff)
    x = layers.Add()([x, ff])
    x = layers.LayerNormalization()(x)

    x = layers.GlobalAveragePooling1D()(x)
    x = layers.Dropout(0.35)(x)
    x = layers.Dense(24, activation="relu")(x)
    x = layers.Dropout(0.25)(x)
    out = layers.Dense(1, activation="sigmoid")(x)

    model = Model(inp, out)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=8e-4),
        loss="binary_crossentropy",
        metrics=["accuracy", tf.keras.metrics.AUC(name="auc")],
    )
    return model


def select_top_connectivity_features(X_train_df, y_train, conn_cols, k):
    conn_cols = [str(c) for c in conn_cols]
    k = min(k, len(conn_cols))

    conn_train = X_train_df[conn_cols].apply(pd.to_numeric, errors="coerce").copy()

    medians = conn_train.median(axis=0)
    medians = medians.fillna(0.0)
    conn_train = conn_train.fillna(medians)

    selector = SelectKBest(score_func=f_classif, k=k)
    selector.fit(conn_train, y_train)

    selected = conn_train.columns[selector.get_support()].tolist()
    selected = [str(c) for c in selected]
    selected = sorted(selected, key=lambda x: int(str(x).split("_")[1]))

    return selected


def choose_best_weight_and_threshold(y_val, bilstm_val_probs, transformer_val_probs):
    best = None

    for bilstm_weight in np.arange(0.0, 1.01, 0.05):
        transformer_weight = 1.0 - bilstm_weight
        ensemble_probs = (
            bilstm_weight * bilstm_val_probs +
            transformer_weight * transformer_val_probs
        )

        for threshold in np.arange(0.35, 0.76, 0.01):
            preds = (ensemble_probs >= threshold).astype(int)

            acc = accuracy_score(y_val, preds)
            bal_acc = balanced_accuracy_score(y_val, preds)
            f1 = f1_score(y_val, preds, zero_division=0)

            candidate = (
                round(acc, 6),
                round(bal_acc, 6),
                round(f1, 6),
                -abs(threshold - 0.50),
            )

            if best is None or candidate > best["candidate"]:
                best = {
                    "candidate": candidate,
                    "bilstm_weight": float(round(bilstm_weight, 2)),
                    "transformer_weight": float(round(transformer_weight, 2)),
                    "threshold": float(round(threshold, 2)),
                    "val_accuracy": float(acc),
                    "val_balanced_accuracy": float(bal_acc),
                    "val_f1": float(f1),
                }

    return best


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

    phenotype_cols = [str(c) for c in pick_existing_columns(df, ["age", "iq", "sex", "handedness", "site"])]
    all_conn_cols = sorted(
    [str(c) for c in df.columns if str(c).startswith("conn_")],
    key=lambda x: int(str(x).split("_")[1]),
)

    if not all_conn_cols:
        raise ValueError("No conn_ columns found in dataset.")

    print("Phenotype columns (before cleanup):", phenotype_cols)
    print("All connectivity columns:", len(all_conn_cols))
    print("Class counts:", y.value_counts().to_dict())

    base_feature_cols = phenotype_cols + all_conn_cols
    X_full = df[base_feature_cols].copy()

    X_temp_df, X_test_df, y_temp, y_test = train_test_split(
        X_full,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    X_train_df, X_val_df, y_train, y_val = train_test_split(
        X_temp_df,
        y_temp,
        test_size=VAL_SIZE_FROM_REMAINING,
        random_state=RANDOM_STATE,
        stratify=y_temp,
    )

    dropped_all_nan_phenotype = [c for c in phenotype_cols if X_train_df[c].isna().all()]
    phenotype_cols = [c for c in phenotype_cols if c not in dropped_all_nan_phenotype]

    if dropped_all_nan_phenotype:
        print("Dropped all-NaN phenotype columns:", dropped_all_nan_phenotype)

    selected_conn_cols = select_top_connectivity_features(
        X_train_df=X_train_df,
        y_train=y_train,
        conn_cols=all_conn_cols,
        k=MAX_CONN_FEATURES,
    )

    feature_cols = [str(c) for c in (phenotype_cols + selected_conn_cols)]

    X_train_df = X_train_df[[str(c) for c in feature_cols]].copy()
    X_val_df = X_val_df[[str(c) for c in feature_cols]].copy()
    X_test_df = X_test_df[[str(c) for c in feature_cols]].copy()

    categorical_cols = [str(c) for c in phenotype_cols if str(c).lower() in {"sex", "handedness", "site"}]
    numeric_cols = [str(c) for c in feature_cols if str(c) not in categorical_cols]

    print("Selected connectivity columns:", len(selected_conn_cols))
    print("Total training columns:", len(feature_cols))
    print("Train shape before preprocessing:", X_train_df.shape)
    print("Validation shape before preprocessing:", X_val_df.shape)
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
        remainder="drop",
        sparse_threshold=0,
    )

    X_train = preprocessor.fit_transform(X_train_df)
    X_val = preprocessor.transform(X_val_df)
    X_test = preprocessor.transform(X_test_df)

    if hasattr(X_train, "toarray"):
        X_train = X_train.toarray()
        X_val = X_val.toarray()
        X_test = X_test.toarray()

    X_train = np.asarray(X_train, dtype=np.float32)
    X_val = np.asarray(X_val, dtype=np.float32)
    X_test = np.asarray(X_test, dtype=np.float32)

    print("Processed train shape:", X_train.shape)
    print("Processed validation shape:", X_val.shape)
    print("Processed test shape:", X_test.shape)

    joblib.dump(preprocessor, MODELS_DIR / "preprocessor.pkl")

    n_features = X_train.shape[1]

    X_train_seq = X_train.reshape(X_train.shape[0], n_features, 1)
    X_val_seq = X_val.reshape(X_val.shape[0], n_features, 1)
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
            monitor="val_auc",
            mode="max",
            patience=6,
            restore_best_weights=True,
        ),
        callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=2,
            min_lr=1e-5,
            verbose=1,
        ),
    ]

    print("\nTraining BiLSTM...")
    bilstm = build_bilstm_model(n_features)
    bilstm.fit(
        X_train_seq,
        y_train,
        validation_data=(X_val_seq, y_val),
        epochs=30,
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
        validation_data=(X_val_seq, y_val),
        epochs=30,
        batch_size=16,
        class_weight=class_weight,
        callbacks=cb,
        verbose=1,
    )
    transformer.save(MODELS_DIR / "transformer_model.h5")

    print("\nTuning ensemble on validation set...")
    bilstm_val_probs = bilstm.predict(X_val_seq, verbose=0).ravel()
    transformer_val_probs = transformer.predict(X_val_seq, verbose=0).ravel()

    best_ensemble = choose_best_weight_and_threshold(
        y_val=y_val,
        bilstm_val_probs=bilstm_val_probs,
        transformer_val_probs=transformer_val_probs,
    )

    print("Best validation BiLSTM weight:", best_ensemble["bilstm_weight"])
    print("Best validation Transformer weight:", best_ensemble["transformer_weight"])
    print("Best validation threshold:", best_ensemble["threshold"])
    print("Best validation accuracy:", best_ensemble["val_accuracy"])
    print("Best validation balanced accuracy:", best_ensemble["val_balanced_accuracy"])
    print("Best validation F1:", best_ensemble["val_f1"])

    print("\nEvaluating on test set...")
    bilstm_probs = bilstm.predict(X_test_seq, verbose=0).ravel()
    transformer_probs = transformer.predict(X_test_seq, verbose=0).ravel()

    ensemble_probs = (
        best_ensemble["bilstm_weight"] * bilstm_probs +
        best_ensemble["transformer_weight"] * transformer_probs
    )

    bilstm_preds = (bilstm_probs >= 0.5).astype(int)
    transformer_preds = (transformer_probs >= 0.5).astype(int)
    ensemble_preds = (ensemble_probs >= best_ensemble["threshold"]).astype(int)

    metrics = {
        "bilstm_accuracy": float(accuracy_score(y_test, bilstm_preds)),
        "transformer_accuracy": float(accuracy_score(y_test, transformer_preds)),
        "ensemble_accuracy": float(accuracy_score(y_test, ensemble_preds)),
        "bilstm_roc_auc": float(roc_auc_score(y_test, bilstm_probs)),
        "transformer_roc_auc": float(roc_auc_score(y_test, transformer_probs)),
        "ensemble_roc_auc": float(roc_auc_score(y_test, ensemble_probs)),
        "ensemble_balanced_accuracy": float(balanced_accuracy_score(y_test, ensemble_preds)),
        "ensemble_f1": float(f1_score(y_test, ensemble_preds, zero_division=0)),
        "n_features": int(n_features),
        "selected_conn_feature_count": int(len(selected_conn_cols)),
        "train_size": int(len(y_train)),
        "val_size": int(len(y_val)),
        "test_size": int(len(y_test)),
        "best_bilstm_weight": float(best_ensemble["bilstm_weight"]),
        "best_transformer_weight": float(best_ensemble["transformer_weight"]),
        "best_threshold": float(best_ensemble["threshold"]),
        "class_weight": {str(k): float(v) for k, v in class_weight.items()},
    }

    print("\nBiLSTM accuracy:", metrics["bilstm_accuracy"])
    print("Transformer accuracy:", metrics["transformer_accuracy"])
    print("Ensemble accuracy:", metrics["ensemble_accuracy"])
    print("Ensemble ROC AUC:", metrics["ensemble_roc_auc"])
    print("Ensemble balanced accuracy:", metrics["ensemble_balanced_accuracy"])
    print("Ensemble F1:", metrics["ensemble_f1"])

    print("\nEnsemble classification report:")
    print(classification_report(y_test, ensemble_preds, digits=4))

    print("Confusion matrix:")
    print(confusion_matrix(y_test, ensemble_preds))

    meta = {
        "dataset_path": str(DATA_PATH),
        "target_col": target_col,
        "ensemble_method": "weighted_average",
        "threshold": float(best_ensemble["threshold"]),
        "ensemble_weight_bilstm": float(best_ensemble["bilstm_weight"]),
        "ensemble_weight_transformer": float(best_ensemble["transformer_weight"]),
        "n_features": int(n_features),
        "max_conn_features": int(MAX_CONN_FEATURES),
        "selected_conn_cols": selected_conn_cols,
        "phenotype_cols": phenotype_cols,
        "categorical_cols": categorical_cols,
        "numeric_cols": numeric_cols,
        "feature_cols": feature_cols,
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