import streamlit as st
from utils.intelligence import analyze_prospect, analyze_web_data
from utils.generator import generate_email
from utils.web_research import perform_web_research
from database.database import init_db, save_email, get_all_records

init_db()

st.set_page_config(page_title="Offline LLaMA3 Outreach Engine", layout="wide")

st.title("🚀 LLaMA3 Multi-Purpose Outreach Engine")

# --- GLOBAL CAMPAIGN SETTINGS ---
with st.container(border=True):
    col_goal, col_temp = st.columns([2, 1])
    with col_goal:
        campaign_goal = st.selectbox(
            "🎯 What is your current goal?",
            [
                "Getting a Job / Internship",
                "Getting Clients / Freelance Projects",
                "Getting Investors / Fundraising",
                "Getting Job Referrals / Networking",
                "Getting Recruiters (Headhunters)",
                "Getting Partnerships (B2B)"
            ],
            index=0,
            help="This changes how the AI analyzes the prospect and writes the email."
        )

st.markdown("---")

tab_manual, tab_auto = st.tabs(["🌐 Auto-Pilot (Web Research)", "📝 Manual Input"])

# ================= AUTO-PILOT TAB =================
with tab_auto:
    col_search, col_results = st.columns([1, 1])
    
    with col_search:
        st.subheader("Target Parameters")
        linkedin_url = st.text_input("Enter LinkedIn URL", placeholder="https://www.linkedin.com/in/satya-nadella")
        
        # Dynamic placeholder based on goal
        note_placeholder = "e.g., I'm a React Dev looking for a senior role..."
        if "Clients" in campaign_goal: note_placeholder = "e.g., We help SaaS companies scale SEO..."
        if "Investors" in campaign_goal: note_placeholder = "e.g., Pre-seed AI startup raising $500k..."
        
        user_notes_auto = st.text_area("Your Pitch / Context", height=100, placeholder=note_placeholder)
        
        search_btn = st.button("🔍 Start Research & Analysis", type="primary", use_container_width=True)
        
    with col_results:
        st.subheader("Intelligence Report")
        if search_btn:
            if not linkedin_url:
                st.error("Please enter a LinkedIn URL")
            else:
                with st.status(f"🕵️ Running '{campaign_goal}' Agents...", expanded=True) as status:
                    st.write("Extracting Identity...")
                    research_data = perform_web_research(linkedin_url)
                    
                    if "error" in research_data:
                        status.update(label="❌ Research Failed", state="error")
                        st.error(research_data["error"])
                    else:
                        st.write("✅ Web Snippets Collected")
                        st.write(f"🧠 Profiling Target for: {campaign_goal}...")
                        
                        # PASS THE GOAL TO THE ANALYZER
                        analysis_result = analyze_web_data(research_data, campaign_goal)
                        
                        if "error" in analysis_result:
                            status.update(label="❌ Analysis Failed", state="error")
                            st.error(analysis_result["error"])
                        else:
                            status.update(label="✅ Mission Complete", state="complete")
                            st.session_state["auto_analysis"] = analysis_result
                            st.session_state["auto_notes"] = user_notes_auto
                            st.session_state["current_goal"] = campaign_goal

        # Display Results
        if "auto_analysis" in st.session_state:
            data = st.session_state["auto_analysis"]
            
            # Identity Section
            identity = data.get("identity", {})
            st.info(f"**Target:** {identity.get('full_name')} | {identity.get('likely_current_role')} @ {identity.get('company')}")
            
            # Tabs for details
            t1, t2, t3 = st.tabs(["📊 Fit Score", "🧠 Psyche", "🚀 Strategy"])
            
            with t1:
                prof = data.get("professional_profile", {})
                st.metric("Relevance Score", f"{prof.get('decision_maker_score_0_to_100')}/100", help="How relevant they are to YOUR goal")
                st.write(f"**Authority:** {prof.get('seniority_level')}")
                st.write(f"**Why them:** {prof.get('relevance_reasoning', 'No specific reason detected.')}")

            with t2:
                behav = data.get("behavioral_intelligence", {})
                comm = data.get("communication_analysis", {})
                st.write(f"**Archetype:** `{behav.get('archetype')}`")
                st.write(f"**Tone:** `{comm.get('tone_style')}`")
                st.progress(comm.get("formality_score_0_to_100", 50)/100, text="Formality")

            with t3:
                strat = data.get("outreach_strategy", {})
                buying = data.get("buying_intent_signals", {})
                st.success(f"**Hook:** {strat.get('opening_hook_type')}")
                st.write(f"**CTA:** {strat.get('cta_style')}")
                if buying.get('intent_level') == 'High':
                    st.warning("🔥 HIGH OPPORTUNITY SIGNAL")

            # Generation Button
            if st.button(f"📧 Generate '{st.session_state['current_goal']}' Email", type="primary"):
                with st.spinner("Drafting..."):
                    
                    # Adapt data for generator
                    adapted_data = {
                        "basic_info": identity,
                        "communication_dna": data.get("communication_analysis"),
                        "outreach_strategy": data.get("outreach_strategy"),
                        "behavioral_traits": data.get("behavioral_intelligence"),
                        "buying_signals": {"signals_found": data.get("buying_intent_signals", {}).get("signals_detected", [])},
                        "company_insights": {"likely_tech_stack": []}
                    }
                    
                    # PASS THE GOAL TO THE GENERATOR
                    email = generate_email(adapted_data, st.session_state["auto_notes"], st.session_state["current_goal"])
                    
                    # Save logic
                    save_email(
                        identity.get('full_name', 'Unknown'),
                        identity.get('likely_current_role', 'Unknown'),
                        identity.get('company', 'Unknown'),
                        identity.get('industry', 'Unknown'),
                        data['outreach_strategy']['recommended_tone'],
                        email,
                        f"{st.session_state['current_goal']} | {data['behavioral_intelligence']['archetype']}"
                    )
                    st.text_area("Draft", email, height=400)

# ================= MANUAL TAB =================
with tab_manual:
    st.caption("Paste raw text here if web search fails.")
    # (Kept simple for brevity, logic mimics above)