
import streamlit as st
from utils.generator import generate_email
from utils.tone_analyzer import detect_tone
from database.database import init_db, save_email, get_all_records

init_db()

st.set_page_config(page_title="Offline LLaMA3 Cold Email Engine", layout="wide")

st.title("🦙 Offline LLaMA3 Cold Email Generator")

col1, col2 = st.columns(2)

with col1:
    st.header("Prospect Info")
    name = st.text_input("Name")
    role = st.text_input("Role")
    company = st.text_input("Company")
    industry = st.text_input("Industry")
    profile_text = st.text_area("Paste LinkedIn/About Text")
    notes = st.text_area("Extra Notes")

    auto_tone = detect_tone(profile_text)
    tone = st.selectbox("Tone", ["Professional", "Casual", "Friendly"], 
                        index=["Professional", "Casual", "Friendly"].index(auto_tone))

    if st.button("Generate Cold Email"):
        with st.spinner("Generating with LLaMA3..."):
            email = generate_email(name, role, company, industry, tone, notes)
            save_email(name, role, company, industry, tone, email)
            st.session_state["generated_email"] = email

with col2:
    st.header("Generated Email")
    if "generated_email" in st.session_state:
        st.text_area("Output", st.session_state["generated_email"], height=400)

st.markdown("---")
st.subheader("📊 Previous Outreach Records")

records = get_all_records()
for r in records:
    st.write(f"{r[0]} | {r[1]} @ {r[2]} | {r[3]} | Tone: {r[4]} | {r[5]}")
