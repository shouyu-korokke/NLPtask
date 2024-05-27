import pandas as pd
import numpy as np
from transformers import BertTokenizerFast, BertForTokenClassification, Trainer, TrainingArguments
from transformers import DataCollatorForTokenClassification
from datasets import Dataset

# Load the dataset with proper column separation
data = pd.read_csv('FastTrackDeliverables_corrected.csv', sep=';')

# Concatenate the 'title' and 'raw_text' columns into a new 'text' column
data['text'] = data['<title>'] + ' ' + data['<raw_text>']

# Handle NaN values in the 'text' column
data['text'].fillna('', inplace=True)

# Preprocessing function to tokenize data
tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')

def tokenize_and_align_labels(example):
    tokenized_inputs = tokenizer(example['text'], truncation=True, padding=True)

    label_ids = []
    for i, label in enumerate(example['labels']):
        if isinstance(label, list) or isinstance(label, np.ndarray):
            label_ids.append(label[:len(tokenized_inputs['input_ids'][i])])
        else:
            label_ids.append([])  # Handle cases where label is not list-like

    tokenized_inputs['labels'] = label_ids
    return tokenized_inputs

# Define labels for named entities
labels = ['B-LOCATION', 'I-LOCATION', 'B-DATE', 'I-DATE', 'B-VEHICLE', 'I-VEHICLE', 'B-CAUSALITY', 'I-CAUSALITY', 'B-INJURY', 'I-INJURY', 'B-REASON', 'I-REASON', 'B-ACTION', 'I-ACTION', 'O']

# Map entity labels to numeric values
label_map = {label: i for i, label in enumerate(labels)}

# Add labels to the dataset
data['labels'] = data['text'].apply(lambda x: [label_map['O']] * len(tokenizer.tokenize(str(x))))

# Preprocess and tokenize the dataset
tokenized_dataset = Dataset.from_pandas(data).map(tokenize_and_align_labels, batched=True)

# Define the model for token classification
model = BertForTokenClassification.from_pretrained('bert-base-uncased', num_labels=len(labels))

# Define the training arguments
training_args = TrainingArguments(
    output_dir='./results',
    evaluation_strategy='epoch',
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    weight_decay=0.01,
)

# Use the built-in data collator for padding
data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer)

# Initialize the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,  # No need to specify train/test keys
    eval_dataset=tokenized_dataset,   # No need to specify train/test keys
    tokenizer=tokenizer,
    data_collator=data_collator,
)

# Train the model
trainer.train()

model.save_pretrained(b"C:\Users\Filip Szmit\Desktop\SEM6\NLP\NLPtask")