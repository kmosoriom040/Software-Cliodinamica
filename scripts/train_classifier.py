"""Genera el dataset, entrena el MLP con dos conjuntos de rasgos y guarda el modelo.

Uso: python scripts/train_classifier.py --n 3000 --out data
"""

import argparse
from pathlib import Path

from cliodinamica.ml.classifier import evaluate
from cliodinamica.ml.dataset import INPUT_COLUMNS, generate_dataset
from cliodinamica.ml.labeling import FEATURE_COLUMNS


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=3000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="data")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    df = generate_dataset(args.n, seed=args.seed)
    df.to_csv(out / "dataset.csv", index=False)
    print("Distribución de clases:")
    print(df["label"].value_counts(normalize=True).round(3).to_string())

    for nombre, cols in (("trayectoria", FEATURE_COLUMNS), ("entradas", INPUT_COLUMNS)):
        clf, m = evaluate(df, cols, seed=args.seed)
        print(f"\nRasgos de {nombre}: exactitud = {m['accuracy']:.3f}")
        print("Matriz de confusión", m["labels"], m["confusion_matrix"])
        clf.save(out / f"clasificador_{nombre}.joblib")


if __name__ == "__main__":
    main()
