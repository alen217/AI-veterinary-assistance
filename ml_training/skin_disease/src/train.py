import torch
import torch.nn as nn
import torch.optim as optim
from dataset import load_data
from model import get_model

DATA_DIR = "../data"
EPOCHS = 10
BATCH_SIZE = 16
LR = 0.001

train_loader, val_loader, _, classes = load_data(DATA_DIR, BATCH_SIZE)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = get_model(len(classes)).to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.fc.parameters(), lr=LR)

for epoch in range(EPOCHS):
    model.train()
    running_loss = 0

    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    print(f"Epoch {epoch+1}/{EPOCHS} - Loss: {running_loss:.4f}")

torch.save(model.state_dict(), "../outputs/skin_model.pth")
print("Model saved to outputs/")
