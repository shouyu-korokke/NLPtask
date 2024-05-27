import pandas as pd
from transformers import BertTokenizerFast, BertForTokenClassification
import torch

# Load the trained model
model = BertForTokenClassification.from_pretrained('path_to_trained_model')

# Load the tokenizer
tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')

# Load your data
df = pd.read_csv(r"path_to_your_data.csv")

# Initialize lists to store predictions
predictions = []

# Iterate over each row in the dataframe
for index, row in df.iterrows():
    # Extract the raw text from the row
    raw_text = row["Raw Text"]
    if pd.isna(raw_text):
        continue  # Skip to the next row if raw text is NaN

    # Tokenize the input text
    tokenized_input = tokenizer(raw_text, truncation=True, padding=True, return_tensors="pt")

    # Perform inference
    with torch.no_grad():
        outputs = model(**tokenized_input)

    # Process the model outputs (example: convert logits to predicted labels)
    predicted_labels = torch.argmax(outputs.logits, dim=2)

    # Convert predicted labels back to tokens
    predicted_tokens = tokenizer.convert_ids_to_tokens(predicted_labels[0])

    # Store predictions
    predictions.append(predicted_tokens)

# Add predictions to the dataframe
df['Predictions'] = predictions

# Save the dataframe with predictions
df.to_csv("processed_data.csv", index=False)

print("Data processed and saved to processed_data.csv")
