import traceback
from ava.skin_disease.predictor import SkinDiseasePredictor


class SkinDiseaseAdapter:

    def __init__(self):
        try:
            self.predictor = SkinDiseasePredictor()
            self.available = True
            self.error = None

            print("✅ Skin Disease Model Loaded Successfully")

        except Exception as e:
            print("\n" + "=" * 40)
            print("❌ CRITICAL ERROR: Skin model failed to load")
            print(f"Error: {e}")
            print("\nFull Traceback:")
            traceback.print_exc()
            print("=" * 40 + "\n")

            self.predictor = None
            self.available = False
            self.error = str(e)

    def analyze_image(self, image_path: str):

        if not self.available:
            return {
                "available": False,
                "prediction": None,
                "confidence": None,
                "error": self.error,
            }

        try:
            label, conf = self.predictor.predict(image_path)

            return {
                "available": True,
                "prediction": label,
                "confidence": conf,
                "error": None,
            }

        except Exception as e:
            return {
                "available": False,
                "prediction": None,
                "confidence": None,
                "error": str(e),
            }