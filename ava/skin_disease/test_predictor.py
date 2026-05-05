from predictor import SkinDiseasePredictor

print("Running skin disease inference test...")

predictor = SkinDiseasePredictor()
result = predictor.predict("../imaging/skin_disease/data/test/fungal/fung1.jpeg")

print("Prediction result:", result)
