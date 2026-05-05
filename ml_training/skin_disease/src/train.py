import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms

from dataset import load_data
from model import get_model   # OK here since script is local


# -------------------------
# CONFIG
# -------------------------
DATA_DIR = "../data"
OUTPUT_DIR = "../outputs"
EPOCHS = 20
BATCH_SIZE = 16
LR = 1e-4
FINE_TUNE_EPOCH = 5

os.makedirs(OUTPUT_DIR, exist_ok=True)


# -------------------------
# TRANSFORMS (FIXED)
# -------------------------
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(0.5),
    transforms.RandomRotation(15),
    transforms.ColorJitter(
        brightness=0.2,
        contrast=0.2,
        saturation=0.2
    ),
    transforms.ToTensor(),
    transforms.Normalize(   # 🔥 IMPORTANT FIX
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(   # 🔥 MATCH PREDICTOR
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# -------------------------
# LOAD DATA
# -------------------------
train_loader, val_loader, test_loader, classes = load_data(
    DATA_DIR,
    BATCH_SIZE,
    train_transform=train_transform,
    val_transform=val_transform
)


# -------------------------
# DEVICE & MODEL
# -------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = get_model(len(classes)).to(device)


# -------------------------
# LOSS & OPTIMIZER
# -------------------------
criterion = nn.CrossEntropyLoss()

optimizer = optim.Adam(
    model.fc.parameters(),
    lr=LR,
    weight_decay=1e-4
)


# -------------------------
# TRAINING LOOP
# -------------------------
best_val_acc = 0.0

for epoch in range(EPOCHS):

    # -------- UNFREEZE --------
    if epoch == FINE_TUNE_EPOCH:
        print("🔓 Unfreezing last ResNet block (layer4)")

        for name, param in model.named_parameters():
            if "layer4" in name:
                param.requires_grad = True

        optimizer = optim.Adam(
            filter(lambda p: p.requires_grad, model.parameters()),
            lr=1e-5,
            weight_decay=1e-4
        )

    # -------- TRAIN --------
    model.train()
    correct, total = 0, 0

    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        _, preds = torch.max(outputs, 1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)

    train_acc = correct / total

    # -------- VALIDATION --------
    model.eval()
    val_correct, val_total = 0, 0

    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)

            outputs = model(images)
            _, preds = torch.max(outputs, 1)

            val_correct += (preds == labels).sum().item()
            val_total += labels.size(0)

    val_acc = val_correct / val_total

    print(
        f"Epoch {epoch+1}/{EPOCHS} | "
        f"Train Acc: {train_acc:.4f} | "
        f"Val Acc: {val_acc:.4f}"
    )

    # -------- SAVE BEST --------
    if val_acc > best_val_acc:
        best_val_acc = val_acc

        torch.save({
            "model_state": model.state_dict(),
            "num_classes": len(classes),
            "classes": classes
        }, os.path.join(OUTPUT_DIR, "skin_model.pth"))

        print("✓ Best model updated")


# -------------------------
# TEST EVALUATION (NEW)
# -------------------------
model.eval()
test_correct, test_total = 0, 0

with torch.no_grad():
    for images, labels in test_loader:
        images, labels = images.to(device), labels.to(device)

        outputs = model(images)
        _, preds = torch.max(outputs, 1)

        test_correct += (preds == labels).sum().item()
        test_total += labels.size(0)

test_acc = test_correct / test_total
print(f"\nFinal Test Accuracy: {test_acc:.4f}")


print("\nTraining complete.")
print("Best Validation Accuracy:", best_val_acc)