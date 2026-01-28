from ava.skin_disease.predictor import SkinDiseasePredictor

class SkinDiseaseAdapter:
    def __init__(self):
        self.predictor = SkinDiseasePredictor()

    def analyze_image(self, image_path: str) -> dict:
        """
        Returns:
        {
            "label": str,
            "confidence": float
        }
        """
        label, confidence = self.predictor.predict(image_path)
        return {
            "label": label,
            "confidence": confidence
        }
