import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms

from dataset import load_data
from model import get_model

# -------------------------
# CONFIG
# -------------------------
DATA_DIR = "../data"
EPOCHS = 20
BATCH_SIZE = 16
LR = 1e-4
FINE_TUNE_EPOCH = 5   # when to unfreeze last block

# -------------------------
# TRANSFORMS
# -------------------------
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(15),
    transforms.ColorJitter(
        brightness=0.2,
        contrast=0.2,
        saturation=0.2
    ),
    transforms.ToTensor(),
])

val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
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
# LOSS & OPTIMIZER (PHASE 1)
# -------------------------
criterion = nn.CrossEntropyLoss()

optimizer = optim.Adam(
    model.fc.parameters(),   # ONLY classifier
    lr=LR,
    weight_decay=1e-4
)

# -------------------------
# TRAINING LOOP
# -------------------------
best_val_acc = 0.0

for epoch in range(EPOCHS):

    # -------------------------
    # PHASE 2: UNFREEZE LAST BLOCK
    # -------------------------
    if epoch == FINE_TUNE_EPOCH:
        print("🔓 Unfreezing last ResNet block (layer4)")

        for name, param in model.named_parameters():
            if "layer4" in name:
                param.requires_grad = True

        optimizer = optim.Adam(
            filter(lambda p: p.requires_grad, model.parameters()),
            lr=1e-5,            # LOWER LR for fine-tuning
            weight_decay=1e-4
        )

    # -------------------------
    # TRAIN
    # -------------------------
    model.train()
    correct = 0
    total = 0

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

    # -------------------------
    # VALIDATION
    # -------------------------
    model.eval()
    val_correct = 0
    val_total = 0

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

    # -------------------------
    # SAVE BEST MODEL
    # -------------------------
    if val_acc > best_val_acc:
        best_val_acc = val_acc
        torch.save(model.state_dict(), "../outputs/skin_model.pth")
        print("✓ Best model updated")

print("Training complete. Best Val Acc:", best_val_acc)
