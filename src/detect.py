"""Train a neural autoencoder on normal log windows and flag windows it cannot reconstruct."""
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.neural_network import MLPRegressor

from preprocess import add_templates, parse_logs

WINDOW = 10  # log lines per window


def make_windows(df, window=WINDOW):
    texts, labels = [], []
    for i in range(0, len(df) - window + 1, window):
        chunk = df.iloc[i : i + window]
        texts.append(" ".join(chunk["level"].str.lower() + " " + chunk["template"]))
        labels.append(int(chunk["label"].max()))
    return texts, np.array(labels)


def main():
    df = add_templates(parse_logs())
    texts, y = make_windows(df)
    X = TfidfVectorizer(max_features=200).fit_transform(texts).toarray()

    split = int(len(X) * 0.7)
    X_train, X_test, y_test = X[:split], X[split:], y[split:]
    X_train_normal = X_train[y[:split] == 0]  # learn only what "normal" looks like

    # Autoencoder: compress to a small bottleneck, then reconstruct the input.
    ae = MLPRegressor(hidden_layer_sizes=(64, 16, 64), activation="relu",
                      max_iter=300, random_state=42)
    ae.fit(X_train_normal, X_train_normal)

    def errors(data):
        return np.mean((data - ae.predict(data)) ** 2, axis=1)

    threshold = np.percentile(errors(X_train_normal), 99)
    pred = (errors(X_test) > threshold).astype(int)

    print(f"Windows: train={len(X_train)} test={len(X_test)} | threshold={threshold:.5f}")
    print("\nConfusion matrix [[TN FP] [FN TP]]:")
    print(confusion_matrix(y_test, pred))
    print("\n", classification_report(y_test, pred, target_names=["normal", "anomaly"], zero_division=0))

    out = pd.DataFrame({"true": y_test, "pred": pred, "error": errors(X_test)})
    out.to_csv("data/results.csv", index=False)
    print("Saved data/results.csv")


if __name__ == "__main__":
    main()
