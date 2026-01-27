import os
from torchvision import datasets, transforms
from torch.utils.data import DataLoader


def get_transforms(train=True):
    if train:
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
        ])
    else:
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ])


def load_skin_datasets(data_dir, batch_size=16):
    train_dir = os.path.join(data_dir, "train")
    val_dir = os.path.join(data_dir, "val")
    test_dir = os.path.join(data_dir, "test")

    train_data = datasets.ImageFolder(
        train_dir, transform=get_transforms(train=True)
    )
    val_data = datasets.ImageFolder(
        val_dir, transform=get_transforms(train=False)
    )
    test_data = datasets.ImageFolder(
        test_dir, transform=get_transforms(train=False)
    )

    train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_data, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_data, batch_size=batch_size, shuffle=False)

    return train_loader, val_loader, test_loader, train_data.classes
