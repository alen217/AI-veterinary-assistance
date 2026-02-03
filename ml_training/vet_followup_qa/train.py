"""
Training Script for Veterinary Follow-Up Question Model
Trains the custom transformer model on synthetic veterinary data
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from typing import List, Dict
import json
import os
from tqdm import tqdm
import matplotlib.pyplot as plt
from model import VetFollowUpQuestionModel, VetQuestionVocabulary
from training_data import VetFollowUpDatasetGenerator


class VetQADataset(Dataset):
    """PyTorch Dataset for veterinary Q&A"""
    
    def __init__(self, data: List[Dict], vocab: VetQuestionVocabulary, 
                 context_max_len: int = 100, question_max_len: int = 50):
        self.data = data
        self.vocab = vocab
        self.context_max_len = context_max_len
        self.question_max_len = question_max_len
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        example = self.data[idx]
        
        # Build context string
        context_text = self._build_context_text(example['context'])
        
        # Convert to indices
        context_indices = self.vocab.sentence_to_indices(context_text, self.context_max_len)
        
        # Get a random question from the example
        if example['questions']:
            question = example['questions'][0]['question']
        else:
            question = "How can I help your pet?"
        
        question_indices = self.vocab.sentence_to_indices(question, self.question_max_len)
        
        return {
            'context': torch.tensor(context_indices, dtype=torch.long),
            'question': torch.tensor(question_indices, dtype=torch.long)
        }
    
    def _build_context_text(self, context: Dict) -> str:
        """Convert context dict to text"""
        parts = []
        
        # Patient info
        patient = context['patient']
        animal = patient.get('animal_type', 'pet')
        age = patient.get('age', '')
        if age:
            parts.append(f"{animal} {age}")
        else:
            parts.append(animal)
        
        # Symptoms
        for symptom in context['symptoms']:
            name = symptom.get('name', '').replace('_', ' ')
            duration = symptom.get('duration', '')
            severity = symptom.get('severity', '')
            
            symptom_text = f"has {name}"
            if duration:
                symptom_text += f" for {duration}"
            if severity:
                symptom_text += f" {severity} severity"
            
            parts.append(symptom_text)
        
        return " ".join(parts)


def build_vocabulary(dataset: List[Dict]) -> VetQuestionVocabulary:
    """Build vocabulary from dataset"""
    vocab = VetQuestionVocabulary()
    
    print("🔤 Building vocabulary...")
    for example in tqdm(dataset):
        # Add context words
        context_text = VetQADataset([], vocab)._build_context_text(example['context'])
        vocab.add_sentence(context_text)
        
        # Add question words
        for q in example['questions']:
            vocab.add_sentence(q['question'])
    
    print(f"✅ Vocabulary built: {vocab.n_words} words")
    return vocab


def train_epoch(model, dataloader, optimizer, criterion, device, teacher_forcing_ratio=0.5):
    """Train for one epoch"""
    model.train()
    epoch_loss = 0
    
    for batch in tqdm(dataloader, desc="Training"):
        context = batch['context'].to(device)
        question = batch['question'].to(device)
        
        optimizer.zero_grad()
        
        # Forward pass
        outputs = model(context, question, teacher_forcing_ratio)
        
        # Calculate loss (ignore padding)
        outputs = outputs[:, 1:].reshape(-1, outputs.shape[-1])
        question = question[:, 1:].reshape(-1)
        
        loss = criterion(outputs, question)
        loss.backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        
        optimizer.step()
        epoch_loss += loss.item()
    
    return epoch_loss / len(dataloader)


def evaluate(model, dataloader, criterion, device):
    """Evaluate model"""
    model.eval()
    epoch_loss = 0
    
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Evaluating"):
            context = batch['context'].to(device)
            question = batch['question'].to(device)
            
            outputs = model(context, question, teacher_forcing_ratio=0)
            
            outputs = outputs[:, 1:].reshape(-1, outputs.shape[-1])
            question = question[:, 1:].reshape(-1)
            
            loss = criterion(outputs, question)
            epoch_loss += loss.item()
    
    return epoch_loss / len(dataloader)


def train_model(
    train_data: List[Dict],
    val_data: List[Dict],
    vocab: VetQuestionVocabulary,
    num_epochs: int = 50,
    batch_size: int = 32,
    learning_rate: float = 0.001,
    embed_dim: int = 256,
    hidden_dim: int = 512,
    save_path: str = "vet_followup_model.pth"
):
    """Main training function"""
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🖥️  Using device: {device}")
    
    # Create datasets
    train_dataset = VetQADataset(train_data, vocab)
    val_dataset = VetQADataset(val_data, vocab)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    
    # Create model
    model = VetFollowUpQuestionModel(vocab.n_words, embed_dim, hidden_dim).to(device)
    print(f"📦 Model created with {sum(p.numel() for p in model.parameters())} parameters")
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss(ignore_index=0)  # Ignore padding
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=3, factor=0.5)
    
    # Training loop
    train_losses = []
    val_losses = []
    best_val_loss = float('inf')
    
    print(f"\n🚀 Starting training for {num_epochs} epochs...\n")
    
    for epoch in range(num_epochs):
        print(f"Epoch {epoch+1}/{num_epochs}")
        
        # Decrease teacher forcing over time
        teacher_forcing_ratio = 1.0 - (epoch / num_epochs) * 0.5
        
        train_loss = train_epoch(model, train_loader, optimizer, criterion, 
                                device, teacher_forcing_ratio)
        val_loss = evaluate(model, val_loader, criterion, device)
        
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        
        print(f"Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")
        
        # Learning rate scheduling
        scheduler.step(val_loss)
        
        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'vocabulary': vocab,
                'embed_dim': embed_dim,
                'hidden_dim': hidden_dim,
                'train_loss': train_loss,
                'val_loss': val_loss
            }, save_path)
            print(f"✅ Saved best model (val_loss: {val_loss:.4f})")
        
        print()
    
    # Plot training curves
    plt.figure(figsize=(10, 5))
    plt.plot(train_losses, label='Train Loss')
    plt.plot(val_losses, label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.title('Training Progress')
    plt.savefig('training_curve.png')
    print("📊 Saved training curve to training_curve.png")
    
    return model, vocab


def main():
    """Main training pipeline"""
    
    print("="*70)
    print("🐾 VETERINARY FOLLOW-UP QUESTION AI - TRAINING")
    print("="*70 + "\n")
    
    # Step 1: Generate dataset
    dataset_path = "vet_followup_dataset.json"
    if not os.path.exists(dataset_path):
        print("📝 Generating training dataset...")
        generator = VetFollowUpDatasetGenerator()
        generator.save_dataset(dataset_path, num_examples=5000)
    else:
        print(f"✅ Found existing dataset: {dataset_path}")
    
    # Step 2: Load dataset
    print("\n📂 Loading dataset...")
    with open(dataset_path, 'r') as f:
        dataset = json.load(f)
    
    train_data = dataset['train']
    val_data = dataset['validation']
    print(f"   Training examples: {len(train_data)}")
    print(f"   Validation examples: {len(val_data)}")
    
    # Step 3: Build vocabulary
    vocab = build_vocabulary(train_data + val_data)
    
    # Step 4: Train model
    print("\n" + "="*70)
    model, vocab = train_model(
        train_data=train_data,
        val_data=val_data,
        vocab=vocab,
        num_epochs=50,
        batch_size=32,
        learning_rate=0.001,
        embed_dim=256,
        hidden_dim=512,
        save_path="vet_followup_model.pth"
    )
    
    print("\n" + "="*70)
    print("✅ TRAINING COMPLETE!")
    print("="*70)
    print("\nModel saved to: vet_followup_model.pth")
    print("To use the model, run: python test_model.py")


if __name__ == "__main__":
    main()
