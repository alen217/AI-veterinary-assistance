from typing import List
from nlp_patient_analyzer import SymptomExtraction
from follow_up_questions import FollowUpQuestion


def apply_answer(
    symptoms: List[SymptomExtraction],
    question: FollowUpQuestion,
    answer: str,
    symptom_to_check: str = None
):
    q = question.question.lower()
    ans = answer.lower()

    for s in symptoms:
        match_by_name = s.symptom.replace("_", " ") in q
        match_by_key = symptom_to_check and s.symptom == symptom_to_check
        
        if match_by_name or match_by_key:
            if "severe" in q:
                s.severity = ans

            elif "how often" in q:
                s.frequency = ans

            elif "how long" in q:
                s.duration = ans
