"""
Confusion matrix evaluation script for the skin disease classifier.

Loads the trained ResNet-18 model, runs inference on the held-out test set,
and produces publication-ready outputs:
  - outputs/confusion_matrix.png   – heatmap (raw counts + normalised)
  - outputs/confusion_matrix.csv   – raw count matrix
  - outputs/classification_report.csv – per-class precision/recall/F1
  - outputs/evaluation_summary.txt – plain-text summary with all metrics

Usage (from repo root):
    python ml_training/skin_disease/evaluate_confusion_matrix.py
"""

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import torch
from sklearn.metrics import classification_report, confusion_matrix
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODEL_PATH = os.path.join(REPO_ROOT, "ava", "skin_disease", "model.pth")
TEST_DIR = os.path.join(REPO_ROOT, "ml_training", "skin_disease", "data", "test")
OUTPUT_DIR = os.path.join(REPO_ROOT, "ml_training", "skin_disease", "outputs")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CLASSES = ["fungal", "mange", "normal", "wound"]
BATCH_SIZE = 32

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_model(num_classes: int):
    """Build ResNet-18 with a replaced FC head (mirrors ava/skin_disease/model.py)."""
    import torch.nn as nn
    from torchvision import models

    model = models.resnet18(pretrained=False)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


def load_model(model_path: str, num_classes: int, device: torch.device):
    """Load the saved model weights from *model_path*."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")

    model = get_model(num_classes)
    checkpoint = torch.load(model_path, map_location=device)

    # Support both raw state-dict and checkpoint-dict formats
    state_dict = checkpoint.get("model_state", checkpoint)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    return model


def build_test_loader(test_dir: str) -> DataLoader:
    """Return a DataLoader for the test split (no augmentation)."""
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225]),
    ])
    dataset = datasets.ImageFolder(test_dir, transform=transform)
    return DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=False,
                      num_workers=0)


def run_inference(model, loader, device: torch.device):
    """Return (true_labels, predicted_labels) numpy arrays."""
    all_true, all_pred = [], []

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            outputs = model(images)
            preds = torch.argmax(outputs, dim=1).cpu().numpy()
            all_true.extend(labels.numpy())
            all_pred.extend(preds)

    return np.array(all_true), np.array(all_pred)


def plot_confusion_matrix(cm: np.ndarray, class_names: list,
                          output_path: str) -> None:
    """Save a side-by-side (raw + normalised) confusion matrix heatmap."""
    cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True) * 100

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Skin Disease Classifier — Confusion Matrix", fontsize=14,
                 fontweight="bold")

    for ax, data, fmt, title, vmax in [
        (axes[0], cm,      "d",    "Raw Counts",         None),
        (axes[1], cm_norm, ".1f",  "Normalised (%)",     100),
    ]:
        sns.heatmap(
            data,
            annot=True,
            fmt=fmt,
            cmap="Blues",
            xticklabels=class_names,
            yticklabels=class_names,
            vmin=0,
            vmax=vmax,
            linewidths=0.5,
            linecolor="grey",
            ax=ax,
            cbar_kws={"shrink": 0.8},
        )
        ax.set_title(title, fontsize=12)
        ax.set_xlabel("Predicted Label", fontsize=11)
        ax.set_ylabel("True Label", fontsize=11)
        ax.tick_params(axis="x", rotation=45)
        ax.tick_params(axis="y", rotation=0)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {output_path}")


def save_confusion_matrix_csv(cm: np.ndarray, class_names: list,
                               output_path: str) -> None:
    df = pd.DataFrame(cm, index=class_names, columns=class_names)
    df.index.name = "true \\ predicted"
    df.to_csv(output_path)
    print(f"  Saved: {output_path}")


def save_classification_report_csv(true_labels: np.ndarray,
                                   pred_labels: np.ndarray,
                                   class_names: list,
                                   output_path: str) -> pd.DataFrame:
    report = classification_report(
        true_labels, pred_labels,
        target_names=class_names,
        output_dict=True,
    )
    df = pd.DataFrame(report).T
    df.to_csv(output_path)
    print(f"  Saved: {output_path}")
    return df


def compute_class_distribution(loader) -> dict:
    """Count samples per class from an ImageFolder-backed DataLoader."""
    dataset = loader.dataset
    counts = {}
    for class_name in dataset.classes:
        idx = dataset.class_to_idx[class_name]
        counts[class_name] = sum(1 for _, label in dataset.samples
                                 if label == idx)
    return counts


def save_evaluation_summary(true_labels: np.ndarray,
                             pred_labels: np.ndarray,
                             class_names: list,
                             class_dist: dict,
                             output_path: str) -> None:
    """Write a human-readable summary to *output_path*."""
    report_str = classification_report(
        true_labels, pred_labels, target_names=class_names
    )
    accuracy = (true_labels == pred_labels).mean()

    lines = [
        "=" * 60,
        "  Skin Disease Classifier — Evaluation Summary",
        "=" * 60,
        "",
        f"Model path : {MODEL_PATH}",
        f"Test dir   : {TEST_DIR}",
        "",
        "--- Test-set distribution ---",
    ]
    total = sum(class_dist.values())
    for cls, count in class_dist.items():
        lines.append(f"  {cls:<10}: {count:>4} samples")
    lines += [
        f"  {'TOTAL':<10}: {total:>4} samples",
        "",
        f"Overall accuracy : {accuracy:.4f}  ({accuracy*100:.2f}%)",
        "",
        "--- Classification report ---",
        report_str,
    ]

    with open(output_path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"  Saved: {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Validate paths
    if not os.path.isdir(TEST_DIR):
        print(f"ERROR: Test directory not found: {TEST_DIR}")
        print("       Please create data/test/<class>/ folders and populate them.")
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\nDevice : {device}")

    # ---- Load model ----
    print(f"Loading model from {MODEL_PATH} …")
    model = load_model(MODEL_PATH, num_classes=len(CLASSES), device=device)

    # ---- Build data loader ----
    print(f"Loading test set from {TEST_DIR} …")
    test_loader = build_test_loader(TEST_DIR)
    class_dist = compute_class_distribution(test_loader)
    print(f"  Test set size : {sum(class_dist.values())} images")
    for cls, n in class_dist.items():
        print(f"    {cls}: {n}")

    # ---- Inference ----
    print("Running inference …")
    true_labels, pred_labels = run_inference(model, test_loader, device)

    accuracy = (true_labels == pred_labels).mean()
    print(f"  Overall accuracy : {accuracy:.4f}  ({accuracy*100:.2f}%)")

    # ---- Confusion matrix ----
    cm = confusion_matrix(true_labels, pred_labels)

    print("\nGenerating outputs …")
    plot_confusion_matrix(
        cm, CLASSES,
        os.path.join(OUTPUT_DIR, "confusion_matrix.png"),
    )
    save_confusion_matrix_csv(
        cm, CLASSES,
        os.path.join(OUTPUT_DIR, "confusion_matrix.csv"),
    )
    save_classification_report_csv(
        true_labels, pred_labels, CLASSES,
        os.path.join(OUTPUT_DIR, "classification_report.csv"),
    )
    save_evaluation_summary(
        true_labels, pred_labels, CLASSES, class_dist,
        os.path.join(OUTPUT_DIR, "evaluation_summary.txt"),
    )

    print("\nDone. All outputs saved to:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
