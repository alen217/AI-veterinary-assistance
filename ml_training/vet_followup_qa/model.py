"""
Custom Veterinary Follow-Up Question Generation Model
A transformer-based neural network trained specifically for generating
contextual veterinary follow-up questions.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple
import json
import numpy as np


class VetQuestionVocabulary:
    """Vocabulary builder for veterinary Q&A"""
    
    def __init__(self):
        self.word2idx = {"<PAD>": 0, "<SOS>": 1, "<EOS>": 2, "<UNK>": 3}
        self.idx2word = {0: "<PAD>", 1: "<SOS>", 2: "<EOS>", 3: "<UNK>"}
        self.word_count = {}
        self.n_words = 4
        
    def add_sentence(self, sentence: str):
        """Add words from sentence to vocabulary"""
        for word in sentence.lower().split():
            self.add_word(word)
    
    def add_word(self, word: str):
        """Add a word to vocabulary"""
        if word not in self.word2idx:
            self.word2idx[word] = self.n_words
            self.idx2word[self.n_words] = word
            self.word_count[word] = 1
            self.n_words += 1
        else:
            self.word_count[word] += 1
    
    def sentence_to_indices(self, sentence: str, max_length: int = 50) -> List[int]:
        """Convert sentence to indices"""
        indices = [self.word2idx.get(word.lower(), self.word2idx["<UNK>"]) 
                   for word in sentence.split()]
        indices = [self.word2idx["<SOS>"]] + indices + [self.word2idx["<EOS>"]]
        
        # Pad or truncate
        if len(indices) < max_length:
            indices += [self.word2idx["<PAD>"]] * (max_length - len(indices))
        else:
            indices = indices[:max_length]
        
        return indices
    
    def indices_to_sentence(self, indices: List[int]) -> str:
        """Convert indices back to sentence"""
        words = []
        for idx in indices:
            if idx == self.word2idx["<EOS>"]:
                break
            if idx not in [self.word2idx["<PAD>"], self.word2idx["<SOS>"]]:
                words.append(self.idx2word.get(idx, "<UNK>"))
        return " ".join(words)


class ContextEncoder(nn.Module):
    """Encodes patient context into fixed representation"""
    
    def __init__(self, vocab_size: int, embed_dim: int = 256, hidden_dim: int = 512):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers=2, 
                           batch_first=True, bidirectional=True, dropout=0.3)
        self.fc = nn.Linear(hidden_dim * 2, hidden_dim)
        
    def forward(self, x):
        """
        Args:
            x: (batch_size, seq_len) - tokenized context
        Returns:
            (batch_size, hidden_dim) - context embedding
        """
        embedded = self.embedding(x)  # (batch, seq, embed)
        lstm_out, (hidden, cell) = self.lstm(embedded)
        
        # Use last hidden state from both directions
        hidden = torch.cat((hidden[-2], hidden[-1]), dim=1)  # (batch, hidden*2)
        context = torch.tanh(self.fc(hidden))  # (batch, hidden)
        
        return context, lstm_out


class QuestionDecoder(nn.Module):
    """Generates follow-up questions from context"""
    
    def __init__(self, vocab_size: int, embed_dim: int = 256, hidden_dim: int = 512):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim + hidden_dim, hidden_dim, 
                           num_layers=2, batch_first=True, dropout=0.3)
        # Attention: concatenates [lstm_padded (hidden*2), encoder_outputs (hidden*2), product (hidden*2)] = hidden*6
        self.attention = nn.Linear(hidden_dim * 6, 1)
        # Output: concatenates [lstm_out (hidden), context_vector (hidden*2)] = hidden*3
        self.fc_out = nn.Linear(hidden_dim * 3, vocab_size)
        self.hidden_dim = hidden_dim
        
    def forward(self, x, context, encoder_outputs, hidden=None):
        """
        Args:
            x: (batch, 1) - current word
            context: (batch, hidden) - encoded context
            encoder_outputs: (batch, seq, hidden*2) - all encoder outputs for attention
            hidden: LSTM hidden state
        Returns:
            output: (batch, vocab_size) - word probabilities
            hidden: updated hidden state
        """
        embedded = self.embedding(x)  # (batch, 1, embed)
        
        # Concatenate context with embedding
        context_expanded = context.unsqueeze(1)  # (batch, 1, hidden)
        lstm_input = torch.cat((embedded, context_expanded), dim=2)  # (batch, 1, embed+hidden)
        
        lstm_out, hidden = self.lstm(lstm_input, hidden)  # (batch, 1, hidden)
        
        # Simplified attention mechanism
        # Project lstm_out to match encoder_outputs dimension for element-wise operations
        lstm_projected = lstm_out.repeat(1, encoder_outputs.size(1), 1)  # (batch, seq, hidden)
        
        # Pad lstm_projected to match encoder_outputs size (hidden -> hidden*2)
        lstm_padded = torch.cat([lstm_projected, lstm_projected], dim=2)  # (batch, seq, hidden*2)
        
        # Attention calculation
        attention_input = torch.cat((lstm_padded, encoder_outputs, 
                                    lstm_padded * encoder_outputs), dim=2)  # (batch, seq, hidden*6)
        attention_scores = self.attention(attention_input).squeeze(2)  # (batch, seq)
        attention_weights = F.softmax(attention_scores, dim=1).unsqueeze(1)  # (batch, 1, seq)
        
        # Apply attention
        context_vector = torch.bmm(attention_weights, encoder_outputs)  # (batch, 1, hidden*2)
        
        # Combine lstm output with context
        combined = torch.cat((lstm_out, context_vector), dim=2)  # (batch, 1, hidden+hidden*2)
        output = self.fc_out(combined.squeeze(1))  # (batch, vocab_size)
        
        return output, hidden, attention_weights


class VetFollowUpQuestionModel(nn.Module):
    """
    Complete model for generating veterinary follow-up questions
    Uses encoder-decoder architecture with attention
    """
    
    def __init__(self, vocab_size: int, embed_dim: int = 256, hidden_dim: int = 512):
        super().__init__()
        self.encoder = ContextEncoder(vocab_size, embed_dim, hidden_dim)
        self.decoder = QuestionDecoder(vocab_size, embed_dim, hidden_dim)
        self.vocab_size = vocab_size
        self.hidden_dim = hidden_dim
        
    def forward(self, context_input, question_input, teacher_forcing_ratio=0.5):
        """
        Training forward pass
        Args:
            context_input: (batch, context_len) - patient context
            question_input: (batch, question_len) - target question
            teacher_forcing_ratio: probability of using teacher forcing
        Returns:
            outputs: (batch, question_len, vocab_size) - predicted questions
        """
        batch_size = context_input.size(0)
        question_len = question_input.size(1)
        
        # Encode context
        context, encoder_outputs = self.encoder(context_input)
        
        # Initialize decoder
        decoder_input = question_input[:, 0].unsqueeze(1)  # Start token
        decoder_hidden = None
        
        outputs = torch.zeros(batch_size, question_len, self.vocab_size).to(context_input.device)
        
        for t in range(1, question_len):
            output, decoder_hidden, _ = self.decoder(
                decoder_input, context, encoder_outputs, decoder_hidden
            )
            outputs[:, t] = output
            
            # Teacher forcing
            teacher_force = torch.rand(1).item() < teacher_forcing_ratio
            top1 = output.argmax(1).unsqueeze(1)
            decoder_input = question_input[:, t].unsqueeze(1) if teacher_force else top1
        
        return outputs
    
    def generate_question(self, context_input, vocab, max_length=50, temperature=1.0):
        """
        Generate a single question from context (inference mode)
        Args:
            context_input: (1, context_len) - patient context
            vocab: VetQuestionVocabulary instance
            max_length: maximum question length
            temperature: sampling temperature (higher = more random)
        Returns:
            generated question string
        """
        self.eval()
        with torch.no_grad():
            # Encode context
            context, encoder_outputs = self.encoder(context_input)
            
            # Start with SOS token
            decoder_input = torch.tensor([[vocab.word2idx["<SOS>"]]]).to(context_input.device)
            decoder_hidden = None
            
            generated_indices = []
            
            for _ in range(max_length):
                output, decoder_hidden, _ = self.decoder(
                    decoder_input, context, encoder_outputs, decoder_hidden
                )
                
                # Temperature sampling
                probs = F.softmax(output / temperature, dim=1)
                next_word_idx = torch.multinomial(probs, 1).item()
                
                if next_word_idx == vocab.word2idx["<EOS>"]:
                    break
                
                generated_indices.append(next_word_idx)
                decoder_input = torch.tensor([[next_word_idx]]).to(context_input.device)
            
            return vocab.indices_to_sentence(generated_indices)


class VetQuestionGenerator:
    """
    Wrapper class for easy model usage
    Handles preprocessing, inference, and question generation
    """
    
    def __init__(self, model_path: str = None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.vocab = VetQuestionVocabulary()
        self.model = None
        self.context_max_len = 100
        self.question_max_len = 50
        
        if model_path:
            self.load_model(model_path)
    
    def load_model(self, model_path: str):
        """Load trained model and vocabulary"""
        checkpoint = torch.load(model_path, map_location=self.device)
        self.vocab = checkpoint['vocabulary']
        
        self.model = VetFollowUpQuestionModel(
            vocab_size=self.vocab.n_words,
            embed_dim=checkpoint.get('embed_dim', 256),
            hidden_dim=checkpoint.get('hidden_dim', 512)
        )
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.to(self.device)
        self.model.eval()
        
        print(f"✅ Loaded model from {model_path}")
        print(f"   Vocabulary size: {self.vocab.n_words}")
    
    def prepare_context(self, patient_info: Dict, symptoms: List[Dict]) -> str:
        """Convert patient data to text context"""
        context_parts = []
        
        # Patient info
        animal = patient_info.get('animal_type', 'pet')
        age = patient_info.get('age', 'unknown age')
        context_parts.append(f"{animal} {age}")
        
        # Symptoms
        for symptom in symptoms:
            name = symptom.get('name', symptom.get('symptom', '')).replace('_', ' ')
            duration = symptom.get('duration', '')
            severity = symptom.get('severity', '')
            
            symptom_str = f"has {name}"
            if duration:
                symptom_str += f" for {duration}"
            if severity:
                symptom_str += f" severity {severity}"
            
            context_parts.append(symptom_str)
        
        return " ".join(context_parts)
    
    def generate_questions(
        self, 
        patient_info: Dict, 
        symptoms: List[Dict],
        num_questions: int = 5,
        temperature: float = 0.8
    ) -> List[Dict]:
        """
        Generate follow-up questions for a veterinary case
        
        Args:
            patient_info: Patient demographic information
            symptoms: List of symptoms with details
            num_questions: Number of questions to generate
            temperature: Sampling temperature (0.7-1.0 recommended)
        
        Returns:
            List of generated questions with metadata
        """
        if not self.model:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Prepare context
        context_text = self.prepare_context(patient_info, symptoms)
        context_indices = self.vocab.sentence_to_indices(context_text, self.context_max_len)
        context_tensor = torch.tensor([context_indices]).to(self.device)
        
        # Generate multiple questions
        questions = []
        for i in range(num_questions):
            # Vary temperature slightly for diversity
            temp = temperature + (torch.rand(1).item() - 0.5) * 0.2
            temp = max(0.5, min(1.5, temp))
            
            question_text = self.model.generate_question(
                context_tensor, self.vocab, 
                max_length=self.question_max_len,
                temperature=temp
            )
            
            # Skip duplicates and low-quality questions
            if question_text and len(question_text.split()) >= 4:
                if not any(q['question'] == question_text for q in questions):
                    questions.append({
                        'question': question_text,
                        'category': 'ai_generated',
                        'priority': 4,  # Default priority
                        'reasoning': 'AI-generated contextual question',
                        'expected_answer_type': 'descriptive'
                    })
        
        return questions[:num_questions]


# Model metadata
MODEL_INFO = {
    "name": "VetFollowUpQuestionModel",
    "version": "1.0.0",
    "description": "Custom transformer-based model for veterinary follow-up question generation",
    "architecture": "Encoder-Decoder with Attention",
    "input": "Patient context (animal type, age, symptoms)",
    "output": "Contextual follow-up questions",
    "vocab_size": "Built from training data",
    "embed_dim": 256,
    "hidden_dim": 512,
}
