"""
AVA-Style Display Engine
Implements Top-K disease display with explainability and match ratios
Based on IEEE Access AVA paper methodology
"""
from typing import List, Dict, Tuple
import streamlit as st


class AVADisplayEngine:
    """
    Displays disease predictions following AVA paper methodology:
    - Top-K ranking (Top-3, Top-5, Top-10)
    - Match count and match ratio display
    - Explainable symptom-disease mapping
    - Confidence visualization
    """
    
    def __init__(self):
        self.k_values = [3, 5, 10]
    
    def calculate_match_ratio(self, disease: Dict) -> float:
        """
        Calculate AVA match ratio: matched_symptoms / total_disease_symptoms
        This is the tie-breaker used in AVA paper
        """
        matched = disease.get('symptom_match_count', 0)
        total_symptoms = len(disease.get('common_symptoms', []))
        
        if total_symptoms == 0:
            return 0.0
        
        return matched / total_symptoms
    
    def get_matched_symptoms(self, disease: Dict, patient_symptoms: List) -> List[str]:
        """
        Get list of symptoms that matched between patient and disease
        For explainability display
        """
        disease_symptoms = set(disease.get('common_symptoms', []))
        patient_symptom_names = set([s.symptom if hasattr(s, 'symptom') else s for s in patient_symptoms])
        
        matched = disease_symptoms & patient_symptom_names
        return list(matched)
    
    def display_top_k_section(self, diseases: List[Dict], patient_symptoms: List):
        """
        Display Top-K results section like AVA paper
        Shows Top-3, Top-5, Top-10 with visual indicators
        """
        st.markdown("### 🎯 Top-K Disease Predictions (AVA Methodology)")
        
        total_diseases = len(diseases)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            top_3_count = min(3, total_diseases)
            st.metric("Top-3 Candidates", f"{top_3_count} diseases", 
                     help="Most likely 3 diseases based on symptom matching")
        with col2:
            top_5_count = min(5, total_diseases)
            st.metric("Top-5 Candidates", f"{top_5_count} diseases",
                     help="Top 5 disease candidates for differential diagnosis")
        with col3:
            top_10_count = min(10, total_diseases)
            st.metric("Top-10 Candidates", f"{top_10_count} diseases",
                     help="Extended list for comprehensive analysis")
        
        st.info("💡 **AVA Top-K Approach:** Shows multiple disease candidates instead of single prediction to support differential diagnosis")
    
    def display_explainability_panel(self, disease: Dict, patient_symptoms: List, rank: int):
        """
        Display explainability panel showing symptom-disease matching
        Key feature of AVA paper: transparent reasoning
        """
        matched_symptoms = self.get_matched_symptoms(disease, patient_symptoms)
        total_disease_symptoms = len(disease.get('common_symptoms', []))
        match_ratio = self.calculate_match_ratio(disease)
        
        with st.expander(f"🔍 Rank #{rank}: {disease.get('name', 'Unknown')} - Explainability Details"):
            # Match statistics
            st.markdown("#### 📊 Matching Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Matched Symptoms", f"{len(matched_symptoms)}/{total_disease_symptoms}")
            with col2:
                st.metric("Match Ratio", f"{match_ratio:.2%}", 
                         help="AVA metric: matched/total disease symptoms")
            with col3:
                st.metric("Confidence Score", f"{disease.get('confidence', 0):.1%}")
            
            # Matched symptoms display
            if matched_symptoms:
                st.markdown("#### ✅ Matched Symptoms")
                for symptom in matched_symptoms:
                    st.markdown(f"- ✅ **{symptom}**")
            
            # Missing symptoms that could help diagnosis
            all_disease_symptoms = set(disease.get('common_symptoms', []))
            missing_symptoms = all_disease_symptoms - set(matched_symptoms)
            
            if missing_symptoms and len(missing_symptoms) <= 5:
                st.markdown("#### ❓ Additional Symptoms to Check")
                st.info("These symptoms would help confirm/rule out this disease:")
                for symptom in list(missing_symptoms)[:5]:
                    st.markdown(f"- ❓ {symptom}")
            
            # Disease details
            st.markdown("#### 📋 Disease Information")
            st.markdown(f"**Scientific Name:** {disease.get('scientific_name', 'N/A')}")
            st.markdown(f"**Severity:** {disease.get('severity', 'Unknown')}")
            st.markdown(f"**Description:** {disease.get('description', 'No description available')}")
            
            # Treatment info
            if disease.get('treatment'):
                st.markdown("#### 💊 Treatment")
                st.markdown(disease.get('treatment'))
    
    def display_disease_ranking_table(self, diseases: List[Dict], patient_symptoms: List, k: int = 10):
        """
        Display disease ranking table with all AVA metrics
        Shows: Rank, Name, Matched Symptoms, Total Symptoms, Match Ratio, Confidence
        """
        st.markdown(f"### 📋 Detailed Top-{k} Ranking Table")
        
        # Prepare table data
        table_data = []
        for i, disease in enumerate(diseases[:k], 1):
            matched = len(self.get_matched_symptoms(disease, patient_symptoms))
            total = len(disease.get('common_symptoms', []))
            ratio = self.calculate_match_ratio(disease)
            confidence = disease.get('confidence', 0)
            
            severity_emoji = {
                'mild': '🟢',
                'moderate': '🟡', 
                'severe': '🔴'
            }.get(disease.get('severity', 'moderate'), '🟡')
            
            table_data.append({
                '🏆 Rank': f"#{i}",
                '🦠 Disease': disease.get('name', 'Unknown'),
                '✅ Matched': f"{matched}/{total}",
                '📊 Match Ratio': f"{ratio:.2%}",
                '🎯 Confidence': f"{confidence:.1%}",
                '⚠️ Severity': f"{severity_emoji} {disease.get('severity', 'Unknown')}"
            })
        
        # Display as dataframe
        import pandas as pd
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("""
        **Legend:**
        - **Matched:** Number of patient symptoms matching this disease / Total symptoms of disease
        - **Match Ratio:** AVA tie-breaker metric (matched / total)
        - **Confidence:** Overall confidence score considering multiple factors
        """)
    
    def display_ava_results(self, diseases: List[Dict], patient_symptoms: List, show_top_k: int = 10):
        """
        Main function to display all AVA-style results
        """
        if not diseases:
            st.warning("No diseases matched the symptoms.")
            return
        
        # Display Top-K section
        self.display_top_k_section(diseases, patient_symptoms)
        
        st.markdown("---")
        
        # Display ranking table
        self.display_disease_ranking_table(diseases, patient_symptoms, k=min(show_top_k, len(diseases)))
        
        st.markdown("---")
        
        # Display explainability for top diseases
        st.markdown("### 🔬 Explainable Disease Analysis")
        st.info("💡 **Explainability:** Understanding WHY each disease was predicted based on symptom matching")
        
        for i, disease in enumerate(diseases[:show_top_k], 1):
            self.display_explainability_panel(disease, patient_symptoms, i)


class QuestionStrategyEngine:
    """
    Implements AVA's two question recommendation strategies:
    1. Most Frequent Symptom Question
    2. Most Decisive Symptom Question
    """
    
    def __init__(self, database_repo):
        self.repo = database_repo
    
    def get_most_frequent_symptom(self, candidate_diseases: List[Dict], asked_symptoms: set) -> Tuple[str, str]:
        """
        Strategy 1: Find symptom that appears most frequently across candidate diseases
        This helps check the most common missing symptom
        """
        symptom_frequency = {}
        
        for disease in candidate_diseases:
            for symptom in disease.get('common_symptoms', []):
                if symptom not in asked_symptoms:
                    symptom_frequency[symptom] = symptom_frequency.get(symptom, 0) + 1
        
        if not symptom_frequency:
            return None, None
        
        most_frequent = max(symptom_frequency.items(), key=lambda x: x[1])
        symptom, frequency = most_frequent
        
        question = f"Does the animal show signs of {symptom.lower()}?"
        reasoning = f"This symptom appears in {frequency}/{len(candidate_diseases)} candidate diseases (most common)"
        
        return question, reasoning
    
    def get_most_decisive_symptom(self, candidate_diseases: List[Dict], asked_symptoms: set) -> Tuple[str, str]:
        """
        Strategy 2: Find symptom that best distinguishes between diseases
        This helps quickly eliminate wrong candidates
        """
        if len(candidate_diseases) <= 1:
            return None, None
        
        symptom_disease_map = {}
        
        for disease in candidate_diseases:
            for symptom in disease.get('common_symptoms', []):
                if symptom not in asked_symptoms:
                    if symptom not in symptom_disease_map:
                        symptom_disease_map[symptom] = []
                    symptom_disease_map[symptom].append(disease.get('name'))
        
        if not symptom_disease_map:
            return None, None
        
        # Find symptom that appears in roughly half the diseases (best separator)
        total_diseases = len(candidate_diseases)
        best_symptom = None
        best_score = float('inf')
        
        for symptom, disease_list in symptom_disease_map.items():
            count = len(disease_list)
            # Score: how close to 50/50 split
            score = abs(count - (total_diseases / 2))
            if score < best_score:
                best_score = score
                best_symptom = symptom
                best_diseases = disease_list
        
        if best_symptom:
            question = f"Does the animal show signs of {best_symptom.lower()}?"
            reasoning = f"This symptom distinguishes between diseases (present in {len(best_diseases)}/{total_diseases} candidates)"
            return question, reasoning
        
        return None, None
    
    def get_recommended_questions(self, candidate_diseases: List[Dict], asked_symptoms: set) -> List[Dict]:
        """
        Generate both question strategies and return them
        """
        questions = []
        
        # Strategy 1: Most Frequent
        q1, r1 = self.get_most_frequent_symptom(candidate_diseases, asked_symptoms)
        if q1:
            questions.append({
                'question': q1,
                'strategy': 'Most Frequent Symptom',
                'reasoning': r1,
                'type': 'frequent'
            })
        
        # Strategy 2: Most Decisive
        q2, r2 = self.get_most_decisive_symptom(candidate_diseases, asked_symptoms)
        if q2 and q2 != q1:  # Don't duplicate
            questions.append({
                'question': q2,
                'strategy': 'Most Decisive Symptom',
                'reasoning': r2,
                'type': 'decisive'
            })
        
        return questions
