import os
import torch
from torchvision import transforms
from PIL import Image

from ava.skin_disease.model import get_model

class SkinDiseasePredictor:
    """
    Skin disease classifier wrapper.
    Loads model and predicts safely.
    """

    CLASSES = ["fungal", "mange", "normal", "wound"]

    def __init__(self):
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

        model_path = os.path.join(
            os.path.dirname(__file__),
            "model.pth"
        )

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Skin disease model not found: {model_path}"
            )

        # Load model
        self.model = get_model(len(self.CLASSES))
        checkpoint = torch.load(model_path, map_location=self.device)

        if isinstance(checkpoint, dict) and "model_state" in checkpoint:
            state_dict = checkpoint["model_state"]
        else:
            state_dict = checkpoint

        self.model.load_state_dict(state_dict)
        self.model.to(self.device)
        self.model.eval()

    def predict(self, image_path: str) -> tuple[str, float]:
        """
        Returns (label, confidence)
        """

        # -------- SAFE IMAGE LOAD --------
        try:
            image = Image.open(image_path).convert("RGB")
        except Exception as e:
            raise ValueError(f"Invalid image: {e}")

        image = self.transform(image).unsqueeze(0).to(self.device)

        # -------- INFERENCE --------
        with torch.no_grad():
            outputs = self.model(image)
            probs = torch.softmax(outputs, dim=1)

        # -------- DEBUG PRINT --------
        print("\n" + "=" * 30)
        print("RAW MODEL OUTPUTS:")
        for i, class_name in enumerate(self.CLASSES):
            print(f"  {class_name}: {probs[0][i].item():.4f}")
        print("=" * 30 + "\n")

        # -------- PREDICTION --------
        idx = torch.argmax(probs, dim=1).item()
        normal_idx = self.CLASSES.index("normal")

        # -------- SENSITIVITY LOGIC --------
        if idx == normal_idx:
            for i, score in enumerate(probs[0]):
                if i != normal_idx and score > 0.30:
                    print(f"⚠️ Overriding 'normal' → '{self.CLASSES[i]}'")
                    idx = i
                    break

        confidence = probs[0][idx].item()

        return self.CLASSES[idx], float(confidence)