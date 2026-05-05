import torch.nn as nn
from torchvision import models


def get_model(num_classes, freeze_backbone=True):
    # Use updated API (future-proof)
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)

    # Freeze backbone if required
    if freeze_backbone:
        for param in model.parameters():
            param.requires_grad = False

    # Replace classifier with dropout (better generalization)
    model.fc = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(model.fc.in_features, num_classes)
    )

    return model