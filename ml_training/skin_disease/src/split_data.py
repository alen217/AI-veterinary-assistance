import os
import random
import shutil

BASE_DIR = "ml_training/skin_disease/data"
TRAIN_DIR = os.path.join(BASE_DIR, "train")
VAL_DIR = os.path.join(BASE_DIR, "val")
TEST_DIR = os.path.join(BASE_DIR, "test")

VAL_RATIO = 0.15
TEST_RATIO = 0.15

random.seed(42)

classes = ["fungal", "mange", "normal", "wound"]

for cls in classes:
    cls_train_dir = os.path.join(TRAIN_DIR, cls)
    images = os.listdir(cls_train_dir)
    random.shuffle(images)

    n_total = len(images)
    n_val = int(n_total * VAL_RATIO)
    n_test = int(n_total * TEST_RATIO)

    val_images = images[:n_val]
    test_images = images[n_val:n_val + n_test]

    for img in val_images:
        shutil.move(
            os.path.join(cls_train_dir, img),
            os.path.join(VAL_DIR, cls, img)
        )

    for img in test_images:
        shutil.move(
            os.path.join(cls_train_dir, img),
            os.path.join(TEST_DIR, cls, img)
        )

    print(f"{cls}: total={n_total}, val={len(val_images)}, test={len(test_images)}")
