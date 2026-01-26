import os
from torchvision import datasets
from torch.utils.data import DataLoader

def load_data(
    data_dir,
    batch_size,
    train_transform=None,
    val_transform=None
):
    train_path = os.path.join(data_dir, "train")
    val_path = os.path.join(data_dir, "val")
    test_path = os.path.join(data_dir, "test")

    train_dataset = datasets.ImageFolder(
        train_path,
        transform=train_transform
    )

    val_dataset = datasets.ImageFolder(
        val_path,
        transform=val_transform
    )

    test_dataset = datasets.ImageFolder(
        test_path,
        transform=val_transform
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False
    )

    return train_loader, val_loader, test_loader, train_dataset.classes
