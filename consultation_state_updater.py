from typing import List
from nlp_patient_analyzer import SymptomExtraction
from follow_up_questions import FollowUpQuestion


def apply_answer(
    symptoms: List[SymptomExtraction],
    question: FollowUpQuestion,
    answer: str
):
    q = question.question.lower()
    ans = answer.lower()

    for s in symptoms:
        if s.symptom.replace("_", " ") in q:

            if "severe" in q:
                s.severity = ans

            elif "how often" in q:
                s.frequency = ans

            elif "how long" in q:
                s.duration = ans
