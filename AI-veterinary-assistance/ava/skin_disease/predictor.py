import torch
from torchvision import transforms
from PIL import Image
import os

from ava.skin_disease.model import get_model

print("Predictor module loaded")

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pth")

CLASSES = ["fungal", "mange", "normal", "wound"]

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

model = get_model(len(CLASSES))
state_dict = torch.load(MODEL_PATH, map_location=device)
model.load_state_dict(state_dict)
model.to(device)
model.eval()


def predict_skin_disease(image_path: str):
    print("Predict function called with:", image_path)

    image = Image.open(image_path).convert("RGB")
    image = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(image)
        probs = torch.softmax(outputs, dim=1)
        idx = torch.argmax(probs, dim=1).item()

    return {
        "prediction": CLASSES[idx],
        "confidence": float(probs[0][idx])
    }
