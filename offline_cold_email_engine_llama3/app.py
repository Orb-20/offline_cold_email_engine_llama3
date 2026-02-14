import streamlit as st
import json
import csv
import io
import time
from utils.intelligence import analyze_web_data, analyze_prospect
from utils.generator import generate_outreach_sequence, optimize_profile, generate_reply
from utils.web_research import perform_web_research
from database.database import init_db, save_email, get_all_records

init_db()
st.set_page_config(page_title="AI Career OS Pro", layout="wide", page_icon="⚡")

# --- PREMIUM CSS STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; font-family: 'Inter', sans-serif; }
    .css-card { background-color: #1E2129; border: 1px solid #30333D; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
    .stMetric { background-color: #161920 !important; border: 1px solid #30333D !important; }
    .stButton>button { background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%); color: white; border: none; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=50)
    st.title("Career OS Pro")
    st.caption("v6.0 | Bulk & Copy Update")
    
    st.markdown("### 👤 Your Profile")
    user_resume = st.text_area("📄 Paste Resume / Skills", height=150, placeholder="E.g. Senior DevOps Engineer...")
    campaign_goal = st.selectbox("🎯 Objective", ["Get a Job", "Freelance Client", "Networking"])
    
    st.markdown("---")
    st.info("💡 Pro Tip: For Bulk mode, ensure your CSV has a 'url' column.")

st.title("⚡ AI Career Intelligence OS")

# --- MAIN TABS ---
tab_engine, tab_bulk, tab_brand, tab_dash = st.tabs([
    "🚀 Single Mode", "📂 Bulk Generation", "✨ Brand Optimizer", "📊 History"
])

# === TAB 1: SINGLE INTELLIGENCE ENGINE ===
with tab_engine:
    # 1. SEARCH INPUT
    with st.container():
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        c1, c2 = st.columns([3, 1])
        with c1:
            linkedin_url = st.text_input("🔗 Target LinkedIn URL", placeholder="https://linkedin.com/in/username")
            user_notes = st.text_input("📝 Pitch / Context", placeholder="e.g. I noticed they use AWS...")
        with c2:
            st.write("")
            st.write("")
            if st.button("🔥 Run Analysis", use_container_width=True):
                if not linkedin_url:
                    st.error("Please enter a URL.")
                else:
                    with st.status("🕵️ Activating Agents...", expanded=True) as status:
                        st.write("🕷️ Agent 1: Deep Web Scraping...")
                        raw = perform_web_research(linkedin_url)
                        
                        if "error" in raw:
                            status.update(label="❌ Search Failed", state="error")
                            st.error(raw["error"])
                        else:
                            st.write("🧠 Agent 2: LLaMA3 Cognitive Processing...")
                            analysis = analyze_web_data(raw, campaign_goal, user_resume)
                            
                            st.session_state["raw"] = raw
                            st.session_state["analysis"] = analysis
                            st.session_state["notes"] = user_notes
                            status.update(label="✅ Analysis Complete!", state="complete")
        st.markdown('</div>', unsafe_allow_html=True)

    # 2. RESULTS
    if "analysis" in st.session_state:
        data = st.session_state["analysis"]
        ident = data.get("identity", {})
        
        # Header
        st.markdown(f"## 🎯 {ident.get('full_name', 'Unknown Target')}")
        st.caption(f"**{ident.get('role', 'Unknown Role')}** @ {ident.get('company', 'Unknown Company')}")

        # Metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Fit Score", f"{data.get('resume_alignment', {}).get('match_score', 0)}%")
        c2.metric("Response Prob", f"{data.get('strategic_advice', {}).get('response_probability', 0)}%")
        c3.metric("Psychology", data.get('psychological_profile', {}).get('communication_style', 'Unknown').split()[0])
        status = data.get('recruiter_intelligence', {}).get('hiring_status', 'Unknown')
        c4.metric("Status", status, delta="Hot" if "Active" in status else None)
        
        st.divider()

        # Generator
        c_gen, c_view = st.columns([1, 2])
        
        with c_gen:
            st.markdown("### 📧 Outreach")
            if st.button("⚡ Generate Sequence", type="primary"):
                with st.spinner("Drafting..."):
                    seq = generate_outreach_sequence(data, st.session_state["notes"], campaign_goal, user_resume)
                    st.session_state["seq"] = seq
                    save_email(ident.get('full_name'), ident.get('role'), ident.get('company'), "N/A", "Pro", json.dumps(seq), "Seq")
        
        with c_view:
            if "seq" in st.session_state:
                s = st.session_state["seq"]
                
                # USING ST.CODE FOR ONE-CLICK COPY
                st.info("👇 Click the copy icon in the top right of each block.")
                
                tab_c, tab_e, tab_f = st.tabs(["1️⃣ Connect", "2️⃣ Email", "3️⃣ Follow-up"])
                with tab_c:
                    st.markdown("**Connection Request**")
                    st.code(s.get("step1_connection_request"), language="text")
                with tab_e:
                    st.markdown(f"**Subject:** {s.get('step2_email_subject')}")
                    st.code(s.get("step2_email_body"), language="text")
                with tab_f:
                    st.markdown("**Follow-up**")
                    st.code(s.get("step3_followup_body"), language="text")

# === TAB 2: BULK GENERATION (NEW) ===
with tab_bulk:
    st.header("📂 Bulk Cold Email Generator")
    st.markdown("Upload a CSV with a column named `url` (LinkedIn links). The AI will process them one by one.")
    
    # Global Inputs
    with st.container(border=True):
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            bulk_role = st.text_input("Your Role / Title", placeholder="e.g. Freelance Designer")
        with col_b2:
            bulk_pitch = st.text_input("Global Context / Pitch", placeholder="e.g. Offering SEO services...")
    
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    
    if uploaded_file and st.button("🚀 Start Bulk Generation"):
        if not user_resume:
            st.error("Please add your Resume in the Sidebar first!")
        else:
            # Read CSV
            stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
            reader = csv.DictReader(stringio)
            rows = list(reader)
            
            if "url" not in reader.fieldnames:
                st.error("CSV must have a column named 'url'")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()
                results = []
                
                for i, row in enumerate(rows):
                    url = row['url']
                    status_text.text(f"⏳ Processing {i+1}/{len(rows)}: {url}...")
                    
                    # 1. Research
                    raw = perform_web_research(url)
                    if "error" in raw:
                        results.append({**row, "status": "Failed", "error": raw["error"]})
                        continue
                        
                    # 2. Analyze
                    analysis = analyze_web_data(raw, campaign_goal, user_resume)
                    ident = analysis.get("identity", {})
                    
                    # 3. Generate
                    # Merge row-specific context if exists, else use global
                    row_context = row.get('context', bulk_pitch)
                    seq = generate_outreach_sequence(analysis, row_context, campaign_goal, user_resume)
                    
                    # 4. Save Row
                    results.append({
                        "linkedin_url": url,
                        "name": ident.get("full_name"),
                        "role": ident.get("role"),
                        "company": ident.get("company"),
                        "connection_msg": seq.get("step1_connection_request"),
                        "email_subject": seq.get("step2_email_subject"),
                        "email_body": seq.get("step2_email_body"),
                        "followup_body": seq.get("step3_followup_body"),
                        "status": "Success"
                    })
                    
                    # Update Progress
                    progress_bar.progress((i + 1) / len(rows))
                    time.sleep(1) # Rate limit safety
                
                status_text.success("✅ Bulk Generation Complete!")
                
                # Convert to CSV for Download
                output = io.StringIO()
                if results:
                    writer = csv.DictWriter(output, fieldnames=results[0].keys())
                    writer.writeheader()
                    writer.writerows(results)
                    
                    st.download_button(
                        label="📥 Download Generated Emails (CSV)",
                        data=output.getvalue(),
                        file_name="cold_email_results.csv",
                        mime="text/csv"
                    )
                    
                    st.dataframe(results)

# === TAB 3: BRANDING ===
with tab_brand:
    st.header("✨ AI Profile Optimizer (F13)")
    jd = st.text_area("Paste Job Description")
    if st.button("Optimize"):
        with st.spinner("Optimizing..."):
            res = optimize_profile(user_resume, jd)
            st.subheader("Headline")
            st.code(res.get("optimized_headline"), language="text")
            st.subheader("About Section")
            st.code(res.get("about_section_rewrite"), language="text")

# === TAB 4: HISTORY ===
with tab_dash:
    st.header("📊 History")
    st.dataframe(get_all_records(), use_container_width=True)