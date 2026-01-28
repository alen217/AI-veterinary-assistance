class SkinDiseaseAdapter:
    """
    Optional adapter for skin disease ML model.
    If ML dependencies or model are missing, adapter disables itself safely.
    """

    def __init__(self):
        try:
            from ava.skin_disease.predictor import SkinDiseasePredictor

            self.predictor = SkinDiseasePredictor()
            self.available = True
            self.error = None

        except Exception as e:
            print("\n" + "="*30)           # Add this
            print(f"CRITICAL ERROR: {e}")  # Add this
            print("="*30 + "\n")           # Add this

            self.predictor = None
            self.available = False
            self.error = str(e)

    def analyze_image(self, image_path: str) -> dict:
        """
        Run skin disease prediction if available.

        Returns:
        {
            "available": bool,
            "prediction": str | None,
            "confidence": float | None,
            "error": str | None
        }
        """

        if not self.available:
            return {
                "available": False,
                "prediction": None,
                "confidence": None,
                "error": self.error or "Skin disease ML model not available",
            }

        # Unpack the tuple directly
        prediction, confidence = self.predictor.predict(image_path)

        return {
            "available": True,
            "prediction": prediction,
            "confidence": confidence,
            "error": None,
        }
