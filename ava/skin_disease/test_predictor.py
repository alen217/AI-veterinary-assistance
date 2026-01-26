from predictor import predict_skin_disease

print("Running skin disease inference test...")

result = predict_skin_disease("test_image.jpeg")

print("Prediction result:", result)
