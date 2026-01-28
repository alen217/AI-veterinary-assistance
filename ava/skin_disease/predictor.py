import os
import torch
from torchvision import transforms
from PIL import Image

from ava.skin_disease.model import get_model


class SkinDiseasePredictor:
    """
    Skin disease classifier wrapper.
    Loads model lazily and predicts safely.
    """

    CLASSES = ["fungal", "mange", "normal", "wound"]

    def __init__(self):
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
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
        
        # Check if the file is a checkpoint dictionary or just weights
        if "model_state" in checkpoint:
            state_dict = checkpoint["model_state"]  # Extract just the weights
        else:
            state_dict = checkpoint  # It was already just weights
            
        self.model.load_state_dict(state_dict)
        self.model.to(self.device)
        self.model.eval()

    def predict(self, image_path: str) -> tuple[str, float]:
        """
        Returns (label, confidence)
        """

        image = Image.open(image_path).convert("RGB")
        image = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.model(image)
            probs = torch.softmax(outputs, dim=1)
            idx = torch.argmax(probs, dim=1).item()

        return (
            self.CLASSES[idx],
            float(probs[0][idx])
        )
