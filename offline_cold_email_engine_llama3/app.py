import streamlit as st
import json
import time

# Robust Imports
try:
    from utils.intelligence import analyze_web_data, analyze_prospect
    from utils.generator import generate_email, generate_outreach_sequence, optimize_profile
    from utils.web_research import perform_web_research
    from database.database import init_db, save_email, get_all_records
except ImportError:
    st.error("⚠️ Error importing modules. Please check 'utils' folder.")
    st.stop()

# Initialize
init_db()
st.set_page_config(page_title="AI Career OS v4", layout="wide", page_icon="⚡")

# Custom CSS for "Organized & Visible" Look
st.markdown("""
<style>
    .metric-card {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #4e4e4e;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚡ AI Career OS")
    st.caption("Offline LLaMA3 Engine")
    
    st.markdown("### 👤 User Profile")
    user_resume = st.text_area("📄 Paste Resume / Skills", height=150, placeholder="E.g., Senior Python Dev...")
    
    st.markdown("### 🎯 Campaign Goal")
    campaign_goal = st.selectbox("Current Objective", [
        "Getting a Job (Active)", 
        "Freelance Clients (B2B)", 
        "Networking & Mentorship", 
        "Fundraising / Investors"
    ])
    st.markdown("---")
    st.info("v4.0 | Dashboard Optimized")

# --- MAIN LAYOUT ---
tab_auto, tab_brand, tab_dash = st.tabs(["🕵️ Intelligence Engine", "🎨 Profile Optimizer", "📊 History Dashboard"])

# === TAB 1: INTELLIGENCE ENGINE ===
with tab_auto:
    # 1. Input Section (Compact)
    with st.container(border=True):
        c1, c2 = st.columns([1, 3])
        with c1:
            st.markdown("### 🎯 Target")
        with c2:
            linkedin_url = st.text_input("LinkedIn URL", placeholder="https://linkedin.com/in/...", label_visibility="collapsed")
        
        user_notes = st.text_input("💡 Context / Pitch (Optional)", placeholder="E.g., I saw their post about AI scaling...")

        if st.button("🚀 Run Intelligence Agents", type="primary"):
            if not linkedin_url:
                st.warning("Please paste a LinkedIn URL first.")
            else:
                with st.status("🕵️ orchestrating AI Agents...", expanded=True) as status:
                    st.write("🕷️ Agent 1: Scraping Public Data (Profile, Posts, Company)...")
                    raw_data = perform_web_research(linkedin_url)
                    
                    if "error" in raw_data:
                        status.update(label="❌ Scraping Failed", state="error")
                        st.error(raw_data["error"])
                    else:
                        st.write("🧠 Agent 2: LLaMA3 Analyzing Psychology & Strategy...")
                        analysis = analyze_web_data(raw_data, campaign_goal, user_resume)
                        st.session_state["analysis"] = analysis
                        st.session_state["notes"] = user_notes
                        status.update(label="✅ Intelligence Report Ready", state="complete")

    # 2. Dashboard Output Section
    if "analysis" in st.session_state:
        data = st.session_state["analysis"]
        ident = data.get("identity", {})
        intel = data.get("recruiter_intelligence", {})
        psy = data.get("psychological_profile", {})
        
        # --- HEADER CARD ---
        st.markdown("---")
        with st.container(border=True):
            col_profile, col_metrics = st.columns([2, 2])
            
            with col_profile:
                st.markdown(f"## {ident.get('full_name', 'Target Name')}")
                st.caption(f"**{ident.get('likely_current_role')}** @ {ident.get('company')}")
                st.caption(f"📍 {ident.get('location')}")
            
            with col_metrics:
                m1, m2, m3 = st.columns(3)
                m1.metric("Engagement", f"{intel.get('activity_score', 0)}/100")
                m2.metric("Hiring Status", intel.get("hiring_status", "Unknown"))
                # Status Color Badge
                status_color = "🟢" if "Active" in intel.get("hiring_status", "") else "🟡"
                m3.write(f"**Signal:** {status_color}")

        # --- DETAILED PANELS ---
        c_left, c_right = st.columns([1, 1])
        
        with c_left:
            st.markdown("### 🧠 Psychological Profile")
            with st.container(border=True):
                st.write(f"**Style:** {psy.get('communication_style')}")
                st.write(f"**Motivations:** {psy.get('motivations', 'Unknown')}")
                st.info(f"💡 **Tone Tip:** {psy.get('tone_preference')}")

        with c_right:
            st.markdown("### ⚖️ Resume Alignment")
            align = data.get("resume_alignment", {})
            with st.container(border=True):
                score = align.get("match_score", 0)
                st.progress(score / 100, text=f"Match Score: {score}%")
                st.write(f"**Strategy:** {align.get('alignment_strategy')}")

        # --- GENERATION SECTION ---
        st.markdown("### 📧 Outreach Sequence")
        
        # Generation Button Centered
        if st.button("⚡ Generate Personalized Sequence (F4)", use_container_width=True):
            with st.spinner("✍️ Drafting high-conversion copy..."):
                seq = generate_outreach_sequence(data, st.session_state["notes"], campaign_goal, user_resume)
                st.session_state["sequence"] = seq
                
                # Save to DB
                save_email(
                    ident.get("full_name"), ident.get("likely_current_role"), 
                    ident.get("company"), "N/A", psy.get("tone_preference"),
                    json.dumps(seq), "Sequence"
                )

        # Sequence Output (Visible & Organized)
        if "sequence" in st.session_state:
            s = st.session_state["sequence"]
            
            # Use Expanders for cleaner look, default open
            with st.expander("Step 1: Connection Request (LinkedIn)", expanded=True):
                st.text_area("Copy this:", s.get("step1_connection_request", ""), height=100, label_visibility="collapsed")
            
            with st.expander("Step 2: Primary Email", expanded=True):
                st.text_input("Subject:", s.get("step2_email_subject", ""))
                st.text_area("Body:", s.get("step2_email_body", ""), height=300)
            
            with st.expander("Step 3: Follow-Up (3 Days later)", expanded=False):
                st.text_area("Body:", s.get("step3_followup_body", ""), height=150)

# === TAB 2: BRANDING ===
with tab_brand:
    with st.container(border=True):
        st.header("✨ AI Profile Optimizer")
        st.caption("Past a job description to re-write your profile for it.")
        target_job = st.text_area("Target Job Description", height=200)
        
        if st.button("Optimize My Profile"):
            if not user_resume:
                st.error("Please add your Resume in the Sidebar first!")
            else:
                with st.spinner("Optimizing..."):
                    opt = optimize_profile(user_resume, target_job)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.subheader("New Headline")
                        st.info(opt.get("optimized_headline"))
                    with c2:
                        st.subheader("Skills to Add")
                        st.write(opt.get("skills_to_add"))
                    
                    st.subheader("About Section Rewrite")
                    st.text_area("Copy this:", opt.get("about_section_rewrite"), height=300)

# === TAB 3: DASHBOARD ===
with tab_dash:
    st.header("📊 Outreach History")
    records = get_all_records()
    if not records:
        st.info("No outreach generated yet.")
    else:
        st.dataframe(records, use_container_width=True)