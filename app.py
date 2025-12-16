import streamlit as st
from main import VeterinaryAIAssistant

st.set_page_config(
    page_title="Veterinary AI Assistant",
    layout="wide"
)

st.title("🐾 Veterinary AI Patient Analysis System")
st.write("Analyze pet symptoms and receive AI-assisted clinical insights.")

# Input section
patient_text = st.text_area(
    "Describe your pet's symptoms",
    height=180,
    placeholder="Example: My dog has been vomiting for 2 days and seems lethargic..."
)

generate_questions = st.checkbox(
    "Generate follow-up questions",
    value=True
)

analyze_btn = st.button("Analyze Patient")

if analyze_btn and patient_text.strip():
    with st.spinner("Analyzing patient data..."):
        with VeterinaryAIAssistant() as assistant:
            result = assistant.analyze_patient_text(
                patient_text,
                generate_questions=generate_questions
            )

    st.success("Analysis completed")

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Patient Info",
        "Symptoms",
        "Possible Conditions",
        "Recommendations",
        "Follow-up Questions"
    ])

    # Tab 1 – Patient Info
    with tab1:
        p = result["patient_analysis"].patient_info
        st.json({
            "Animal": p.animal_type,
            "Age": p.age,
            "Breed": p.breed,
            "Gender": p.gender,
            "Weight": p.weight
        })

    # Tab 2 – Symptoms
    with tab2:
        if result["patient_analysis"].symptoms:
            for s in result["patient_analysis"].symptoms:
                st.markdown(f"""
                **{s.symptom.replace('_', ' ').title()}**  
                Severity: {s.severity}  
                Duration: {s.duration}  
                Frequency: {s.frequency}
                ---
                """)
        else:
            st.info("No symptoms detected")

    # Tab 3 – Diseases
    with tab3:
        for d in result["database_matches"]:
            st.subheader(d["name"])
            st.progress(min(d["confidence"], 1.0))
            st.write(f"**Severity:** {d['severity']}")
            st.write(d["description"])
            st.write(f"**Treatment:** {d['treatment']}")
            st.divider()

    # Tab 4 – Recommendations
    with tab4:
        r = result["recommendations"]
        st.warning(r["urgency"])
        st.markdown("### Recommended Actions")
        for a in r["recommended_actions"]:
            st.write(f"- {a}")

        st.markdown("### Emergency Signs")
        for e in r["when_to_seek_immediate_care"]:
            st.write(f"⚠ {e}")

    # Tab 5 – Questions
    with tab5:
        if result["follow_up_questions"]:
            for i, q in enumerate(result["follow_up_questions"], 1):
                st.write(f"{i}. {q.question}")
        else:
            st.info("No follow-up questions generated")

else:
    st.info("Enter patient details to begin analysis.")
