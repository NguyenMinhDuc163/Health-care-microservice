# -*- coding: utf-8 -*-
"""
Created on Sat Apr 5 10:17:01 2025
@author: NGU MUỘI

streamlit run bot_chat.py
"""


# save as app.py
import streamlit as st
import random

st.set_page_config(page_title="Healthcare Assistant", page_icon="🏥")


# Simulated Bayesian reasoning
def bayesian_diagnosis(symptoms):
    if "fever" in symptoms and "cough" in symptoms:
        return "Flu", 0.85
    elif "fever" in symptoms and "headache" in symptoms:
        return "Dengue", 0.65
    elif "fatigue" in symptoms and "dizzy" in symptoms:
        return "Anemia", 0.60
    else:
        return "Uncertain", 0.40


# Simulated DRL Treatment Recommendation
def recommend_treatment(diagnosis):
    plans = {
        "Flu": "Take rest, fluids, and 500mg paracetamol every 6h.",
        "Dengue": "Hydrate heavily, paracetamol (NO ibuprofen), and monitor platelets.",
        "Anemia": "Start iron-rich diet and 325mg ferrous sulfate daily.",
        "Uncertain": "Please consult a physician for lab testing."
    }
    return plans.get(diagnosis, "Recommendation unavailable.")


# UI layout
st.title("🏥 Intelligent Healthcare Assistant")
st.write("Chat with your AI health assistant below 💬")

if "chat" not in st.session_state:
    st.session_state.chat = []

user_input = st.text_input("How are you feeling today?", key="input")

if user_input:
    # Add to chat
    st.session_state.chat.append(("You", user_input))

    # Extract symptoms (simple keyword match for demo)
    keywords = ["fever", "cough", "fatigue", "headache", "dizzy"]
    found = [k for k in keywords if k in user_input.lower()]

    # Simulated diagnosis
    diagnosis, confidence = bayesian_diagnosis(found)
    treatment = recommend_treatment(diagnosis)

    reply = f"🔍 I think you may have **{diagnosis}** (confidence: {int(confidence * 100)}%).\n\n"
    reply += f"💊 Recommended action: {treatment}"

    st.session_state.chat.append(("AI", reply))

# Display full chat
for speaker, msg in st.session_state.chat:
    if speaker == "You":
        st.markdown(f"**👤 {speaker}:** {msg}")
    else:
        st.markdown(f"**🤖 {speaker}:** {msg}")