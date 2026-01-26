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
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])


def load_data(data_dir, batch_size=16):
    train = datasets.ImageFolder(os.path.join(data_dir, "train"),
                                 transform=get_transforms(True))
    val = datasets.ImageFolder(os.path.join(data_dir, "val"),
                               transform=get_transforms(False))
    test = datasets.ImageFolder(os.path.join(data_dir, "test"),
                                transform=get_transforms(False))

    return (
        DataLoader(train, batch_size=batch_size, shuffle=True),
        DataLoader(val, batch_size=batch_size),
        DataLoader(test, batch_size=batch_size),
        train.classes
    )