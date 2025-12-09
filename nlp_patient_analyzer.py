"""
NLP Patient Text Analyzer for Veterinary Assistance
Analyzes patient descriptions to extract diseases, symptoms, and patient information
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False


class AnimalType(Enum):
    """Supported animal types in veterinary context"""
    DOG = "dog"
    CAT = "cat"
    BIRD = "bird"
    RABBIT = "rabbit"
    HORSE = "horse"
    COW = "cow"
    OTHER = "other"


@dataclass
class PatientInfo:
    """Extracted patient information"""
    animal_type: Optional[str]
    age: Optional[str]
    breed: Optional[str]
    gender: Optional[str]
    weight: Optional[str]


@dataclass
class SymptomExtraction:
    """Extracted symptom information"""
    symptom: str
    duration: Optional[str]
    severity: Optional[str]
    frequency: Optional[str]
    context: Optional[str]


@dataclass
class DiseaseExtraction:
    """Extracted disease information"""
    disease_name: str
    confidence: float
    related_symptoms: List[str]


@dataclass
class AnalysisResult:
    """Complete analysis result"""
    patient_info: PatientInfo
    symptoms: List[SymptomExtraction]
    suspected_diseases: List[DiseaseExtraction]
    raw_text: str
    key_phrases: List[str]


class VeterinaryNLPAnalyzer:
    """
    Main NLP analyzer for veterinary patient text
    """

    def __init__(self):
        """Initialize the analyzer with symptom and disease dictionaries"""
        self.symptoms_dict = self._load_symptoms_dictionary()
        self.diseases_dict = self._load_diseases_dictionary()
        self.animal_patterns = self._load_animal_patterns()
        self.severity_patterns = self._load_severity_patterns()
        
        # Try to load spaCy model if available
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("Warning: spaCy model not found. Install with: python -m spacy download en_core_web_sm")

    @staticmethod
    def _load_symptoms_dictionary() -> Dict[str, List[str]]:
        """Load comprehensive veterinary symptoms dictionary"""
        return {
            # Gastrointestinal symptoms
            "vomiting": ["vomit", "vomiting", "threw up", "regurgitation"],
            "diarrhea": ["diarrhea", "diarrhoea", "loose stool", "runs", "soft stool"],
            "constipation": ["constipated", "constipation", "hard stool", "straining"],
            "loss_of_appetite": ["loss of appetite", "anorexia", "not eating", "refusing food", "inappetence"],
            "abdominal_pain": ["abdominal pain", "belly pain", "stomach pain", "tender abdomen", "painful stomach"],
            
            # Respiratory symptoms
            "cough": ["cough", "coughing", "coughs"],
            "sneezing": ["sneeze", "sneezing"],
            "nasal_discharge": ["nasal discharge", "runny nose", "nasal mucus"],
            "labored_breathing": ["labored breathing", "difficulty breathing", "short of breath", "shortness of breath"],
            "wheezing": ["wheeze", "wheezing"],
            
            # Dermatological symptoms
            "itching": ["itch", "itching", "scratching", "pruritus", "itchy"],
            "hair_loss": ["hair loss", "alopecia", "losing fur", "bald"],
            "skin_lesion": ["skin lesion", "sore", "wound", "scab"],
            "rash": ["rash", "hives", "eruption"],
            "red_skin": ["red skin", "redness", "erythema"],
            
            # Neurological symptoms
            "seizure": ["seizure", "seizures", "convulsion", "fit"],
            "lethargy": ["lethargy", "lethargic", "sluggish", "no energy", "not active"],
            "incoordination": ["incoordination", "lack of coordination", "wobbly", "unsteady"],
            "tremor": ["tremor", "trembling", "shaking"],
            
            # Ocular symptoms
            "discharge_eye": ["eye discharge", "eye drainage", "watery eyes"],
            "redness_eye": ["red eyes", "eye redness", "conjunctivitis"],
            "swelling_eye": ["eye swelling", "swollen eyes"],
            
            # General symptoms
            "fever": ["fever", "fevered", "high temperature"],
            "dehydration": ["dehydration", "dehydrated"],
            "weight_loss": ["weight loss", "losing weight"],
            "lethargy": ["lethargy", "lethargic", "listless"],
            "swelling": ["swelling", "swollen", "edema", "enlarged"],
        }

    @staticmethod
    def _load_diseases_dictionary() -> Dict[str, Dict]:
        """Load veterinary diseases with associated information"""
        return {
            "gastroenteritis": {
                "keywords": ["gastroenteritis", "gastro", "gi upset"],
                "common_symptoms": ["vomiting", "diarrhea", "abdominal_pain", "loss_of_appetite"],
                "severity": "moderate"
            },
            "parvovirus": {
                "keywords": ["parvovirus", "parvo", "cpv"],
                "common_symptoms": ["vomiting", "diarrhea", "lethargy", "loss_of_appetite", "fever"],
                "severity": "severe"
            },
            "pancreatitis": {
                "keywords": ["pancreatitis", "pancreatic"],
                "common_symptoms": ["vomiting", "abdominal_pain", "lethargy", "loss_of_appetite"],
                "severity": "moderate"
            },
            "otitis": {
                "keywords": ["otitis", "ear infection", "ear mite"],
                "common_symptoms": ["itching", "discharge"],
                "severity": "mild"
            },
            "dermatitis": {
                "keywords": ["dermatitis", "allergies", "allergy"],
                "common_symptoms": ["itching", "rash", "hair_loss", "red_skin"],
                "severity": "mild"
            },
            "pneumonia": {
                "keywords": ["pneumonia", "respiratory infection"],
                "common_symptoms": ["cough", "labored_breathing", "fever", "lethargy"],
                "severity": "severe"
            },
            "conjunctivitis": {
                "keywords": ["conjunctivitis", "pink eye", "eye infection"],
                "common_symptoms": ["discharge_eye", "redness_eye", "swelling_eye"],
                "severity": "mild"
            },
            "epilepsy": {
                "keywords": ["epilepsy", "seizure disorder"],
                "common_symptoms": ["seizure", "tremor"],
                "severity": "moderate"
            }
        }

    @staticmethod
    def _load_animal_patterns() -> Dict[str, List[str]]:
        """Load patterns to identify animal type"""
        return {
            "dog": ["dog", "canine", "puppy", "pup"],
            "cat": ["cat", "feline", "kitten"],
            "bird": ["bird", "parrot", "cockatiel", "budgie", "canary"],
            "rabbit": ["rabbit", "bunny", "hutch"],
            "horse": ["horse", "pony", "equine", "colt"],
            "cow": ["cow", "cattle", "bovine", "calf"],
        }

    @staticmethod
    def _load_severity_patterns() -> Dict[str, List[str]]:
        """Load patterns to identify symptom severity"""
        return {
            "mild": ["slight", "mild", "minor", "little", "somewhat"],
            "moderate": ["significant", "moderate", "considerable", "notable"],
            "severe": ["severe", "severe", "extreme", "critical", "very", "extremely"],
        }

    def analyze(self, patient_text: str) -> AnalysisResult:
        """
        Analyze patient text and extract relevant information
        
        Args:
            patient_text: Raw patient description text
            
        Returns:
            AnalysisResult with extracted information
        """
        text = patient_text.lower()
        
        # Extract information
        patient_info = self._extract_patient_info(text)
        symptoms = self._extract_symptoms(text)
        suspected_diseases = self._extract_diseases(text, symptoms)
        key_phrases = self._extract_key_phrases(text)
        
        return AnalysisResult(
            patient_info=patient_info,
            symptoms=symptoms,
            suspected_diseases=suspected_diseases,
            raw_text=patient_text,
            key_phrases=key_phrases
        )

    def _extract_patient_info(self, text: str) -> PatientInfo:
        """Extract patient demographic information"""
        animal_type = self._extract_animal_type(text)
        age = self._extract_age(text)
        breed = self._extract_breed(text)
        gender = self._extract_gender(text)
        weight = self._extract_weight(text)
        
        return PatientInfo(
            animal_type=animal_type,
            age=age,
            breed=breed,
            gender=gender,
            weight=weight
        )

    def _extract_animal_type(self, text: str) -> Optional[str]:
        """Extract animal type from text"""
        for animal, patterns in self.animal_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    return animal
        return None

    @staticmethod
    def _extract_age(text: str) -> Optional[str]:
        """Extract age information"""
        # Match patterns like "5 years old", "3 year old", "8 months old"
        age_pattern = r'(\d+)\s*(year|yr|month|mon|week|wk|day)s?\s*old'
        match = re.search(age_pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
        return None

    @staticmethod
    def _extract_breed(text: str) -> Optional[str]:
        """Extract breed information"""
        # Common dog breeds
        breeds = [
            "labrador", "golden retriever", "german shepherd", "bulldog",
            "poodle", "beagle", "dachshund", "boxer", "husky", "chihuahua",
            "persian", "siamese", "maine coon", "ragdoll", "british shorthair"
        ]
        for breed in breeds:
            if breed in text:
                return breed
        return None

    @staticmethod
    def _extract_gender(text: str) -> Optional[str]:
        """Extract gender information"""
        if re.search(r'\b(male|m|tom|buck)\b', text, re.IGNORECASE):
            return "male"
        elif re.search(r'\b(female|f|queen|doe)\b', text, re.IGNORECASE):
            return "female"
        return None

    @staticmethod
    def _extract_weight(text: str) -> Optional[str]:
        """Extract weight information"""
        # Match patterns like "25 kg", "50 lbs", "5.5 kg"
        weight_pattern = r'(\d+\.?\d*)\s*(kg|pounds|lbs|lb|kilograms)'
        match = re.search(weight_pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
        return None

    def _extract_symptoms(self, text: str) -> List[SymptomExtraction]:
        """Extract all symptoms mentioned in text"""
        symptoms = []
        
        for symptom_key, patterns in self.symptoms_dict.items():
            for pattern in patterns:
                # Find all occurrences
                for match in re.finditer(rf'\b{re.escape(pattern)}\b', text, re.IGNORECASE):
                    start_pos = max(0, match.start() - 100)
                    end_pos = min(len(text), match.end() + 100)
                    context = text[start_pos:end_pos].strip()
                    
                    duration = self._extract_duration(context)
                    severity = self._extract_severity(context)
                    frequency = self._extract_frequency(context)
                    
                    symptoms.append(SymptomExtraction(
                        symptom=symptom_key,
                        duration=duration,
                        severity=severity,
                        frequency=frequency,
                        context=context
                    ))
        
        # Remove duplicates while preserving best information
        return self._deduplicate_symptoms(symptoms)

    @staticmethod
    def _extract_duration(context: str) -> Optional[str]:
        """Extract symptom duration"""
        duration_pattern = r'(for\s+)?(\d+)\s*(day|week|month|year|hour|minute)s?'
        match = re.search(duration_pattern, context, re.IGNORECASE)
        if match:
            return match.group(0)
        return None

    def _extract_severity(self, context: str) -> Optional[str]:
        """Extract symptom severity"""
        for severity_level, patterns in self.severity_patterns.items():
            for pattern in patterns:
                if pattern in context.lower():
                    return severity_level
        return None

    @staticmethod
    def _extract_frequency(context: str) -> Optional[str]:
        """Extract symptom frequency"""
        frequency_pattern = r'(daily|twice a day|once a day|every\s+\d+\s+hours|often|frequently|occasionally|intermittent)'
        match = re.search(frequency_pattern, context, re.IGNORECASE)
        if match:
            return match.group(0)
        return None

    def _extract_diseases(self, text: str, symptoms: List[SymptomExtraction]) -> List[DiseaseExtraction]:
        """Extract potential diseases based on keywords and symptoms"""
        diseases = []
        extracted_symptom_keys = {s.symptom for s in symptoms}
        
        for disease_name, disease_info in self.diseases_dict.items():
            # Check if disease keywords appear in text
            keyword_match = any(
                keyword in text for keyword in disease_info["keywords"]
            )
            
            # Check symptom overlap
            symptom_overlap = sum(
                1 for symptom in disease_info["common_symptoms"]
                if symptom in extracted_symptom_keys
            )
            
            # Calculate confidence
            if keyword_match:
                confidence = 0.8 + (symptom_overlap * 0.05)
            elif symptom_overlap > 0:
                confidence = 0.4 + (symptom_overlap * 0.1)
            else:
                confidence = 0.0
            
            # Only include if confidence > 0.3
            if confidence > 0.3:
                diseases.append(DiseaseExtraction(
                    disease_name=disease_name,
                    confidence=min(confidence, 1.0),
                    related_symptoms=[s for s in disease_info["common_symptoms"] if s in extracted_symptom_keys]
                ))
        
        # Sort by confidence
        diseases.sort(key=lambda x: x.confidence, reverse=True)
        return diseases

    @staticmethod
    def _extract_key_phrases(text: str) -> List[str]:
        """Extract key medical phrases from text"""
        # Simple extraction of capitalized words and medical terms
        phrases = []
        words = text.split()
        
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 3:
                phrases.append(word)
        
        return list(set(phrases))[:10]  # Return top 10 unique phrases

    @staticmethod
    def _deduplicate_symptoms(symptoms: List[SymptomExtraction]) -> List[SymptomExtraction]:
        """Remove duplicate symptoms, keeping the one with most information"""
        seen = {}
        for symptom in symptoms:
            if symptom.symptom not in seen:
                seen[symptom.symptom] = symptom
            else:
                # Keep the one with more details
                existing = seen[symptom.symptom]
                if (symptom.duration or symptom.severity or symptom.frequency):
                    if not (existing.duration or existing.severity or existing.frequency):
                        seen[symptom.symptom] = symptom
        
        return list(seen.values())

    def format_analysis_report(self, result: AnalysisResult) -> str:
        """Format analysis result as readable report"""
        report = []
        report.append("=" * 60)
        report.append("PATIENT ANALYSIS REPORT")
        report.append("=" * 60)
        
        # Patient Info
        report.append("\n[PATIENT INFORMATION]")
        if result.patient_info.animal_type:
            report.append(f"  Animal Type: {result.patient_info.animal_type}")
        if result.patient_info.age:
            report.append(f"  Age: {result.patient_info.age}")
        if result.patient_info.breed:
            report.append(f"  Breed: {result.patient_info.breed}")
        if result.patient_info.gender:
            report.append(f"  Gender: {result.patient_info.gender}")
        if result.patient_info.weight:
            report.append(f"  Weight: {result.patient_info.weight}")
        
        # Symptoms
        report.append("\n[EXTRACTED SYMPTOMS]")
        if result.symptoms:
            for symptom in result.symptoms:
                severity_str = f" ({symptom.severity})" if symptom.severity else ""
                duration_str = f" for {symptom.duration}" if symptom.duration else ""
                freq_str = f" - {symptom.frequency}" if symptom.frequency else ""
                report.append(f"  • {symptom.symptom}{severity_str}{duration_str}{freq_str}")
        else:
            report.append("  No symptoms extracted")
        
        # Suspected Diseases
        report.append("\n[SUSPECTED CONDITIONS]")
        if result.suspected_diseases:
            for disease in result.suspected_diseases:
                conf_percent = disease.confidence * 100
                report.append(f"  • {disease.disease_name} ({conf_percent:.1f}% confidence)")
                if disease.related_symptoms:
                    report.append(f"    Related symptoms: {', '.join(disease.related_symptoms)}")
        else:
            report.append("  No conditions suspected")
        
        report.append("\n" + "=" * 60)
        return "\n".join(report)


if __name__ == "__main__":
    # Example usage
    analyzer = VeterinaryNLPAnalyzer()
    
    sample_text = """
    I have a 5 year old golden retriever male weighing about 65 lbs.
    He has been vomiting and has diarrhea for the past 3 days.
    He seems lethargic and is not eating well. He appears to have stomach pain.
    He also has a slight fever.
    """
    
    result = analyzer.analyze(sample_text)
    print(analyzer.format_analysis_report(result))
    
    print("\nDetailed JSON Output:")
    print(json.dumps({
        "patient_info": {
            "animal_type": result.patient_info.animal_type,
            "age": result.patient_info.age,
            "breed": result.patient_info.breed,
            "gender": result.patient_info.gender,
            "weight": result.patient_info.weight
        },
        "symptoms_count": len(result.symptoms),
        "diseases_count": len(result.suspected_diseases)
    }, indent=2))
