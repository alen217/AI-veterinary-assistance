from dataset import load_skin_datasets

DATA_DIR = "../data"

train_loader, val_loader, test_loader, classes = load_skin_datasets(DATA_DIR)

print("Classes:", classes)
print("Train batches:", len(train_loader))
print("Validation batches:", len(val_loader))
print("Test batches:", len(test_loader))
