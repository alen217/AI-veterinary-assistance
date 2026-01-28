class SkinDiseaseAdapter:
    def __init__(self):
        try:
            from ava.skin_disease.predictor import SkinDiseasePredictor
            self.predictor = SkinDiseasePredictor()
            self.available = True
        except Exception as e:
            self.predictor = None
            self.available = False
            self.error = str(e)

    def predict(self, image):
        if not self.available:
            return {
                "available": False,
                "error": "Skin disease ML model not installed"
            }
        return self.predictor.predict(image)

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
