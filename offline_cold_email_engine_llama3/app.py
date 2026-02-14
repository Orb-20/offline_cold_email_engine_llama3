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
            index=0
        )

st.markdown("---")

tab_manual, tab_auto = st.tabs(["🌐 Auto-Pilot (Web Research)", "📝 Manual Input"])

# ================= AUTO-PILOT TAB =================
with tab_auto:
    col_search, col_results = st.columns([1, 1])
    
    with col_search:
        st.subheader("Target Parameters")
        linkedin_url = st.text_input("Enter LinkedIn URL", placeholder="https://www.linkedin.com/in/satya-nadella")
        
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
            
            # --- 1. TARGET IDENTITY (FIXED) ---
            identity = data.get("identity", {})
            
            # Safe Fallbacks to prevent "****"
            full_name = identity.get('full_name') or "Unknown Target"
            role = identity.get('likely_current_role') or "Unknown Role"
            company = identity.get('company') or "Unknown Company"
            location = identity.get('location_if_known') or "Location Unknown"

            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"### 🎯 {full_name}")
                    st.markdown(f"**{role}** @ **{company}**")
                    st.caption(f"📍 {location}")
                with c2:
                    score = data.get("professional_profile", {}).get("decision_maker_score_0_to_100", 0)
                    st.metric("Fit Score", f"{score}/100")

            # --- 2. PROFESSIONAL PROFILE & INTERESTS ---
            t1, t2, t3 = st.tabs(["💼 Professional Profile", "🗣️ Interests & Activity", "🚀 Strategy"])
            
            with t1:
                prof = data.get("professional_profile", {})
                st.markdown("#### Expertise & Focus")
                # Safely handle list or missing data
                skills = prof.get("key_skills_and_expertise", [])
                if isinstance(skills, list) and skills:
                    st.info(f"**Core Skills:** {', '.join(skills)}")
                
                st.write(f"**Company Stage:** {prof.get('estimated_company_stage', 'Unknown')}")
                st.success(f"**Why them:** {prof.get('relevance_reasoning', 'Analysis incomplete.')}")

            with t2:
                interests = data.get("personal_interests", {})
                st.markdown("#### What they are talking about")
                
                if interests.get("recent_activity_summary"):
                    st.markdown(f"Found on Web: *\"{interests.get('recent_activity_summary')}\"*")
                
                topics = interests.get("topics_discussed_recently", [])
                if isinstance(topics, list) and topics:
                    st.write(f"**Topics:** {', '.join(topics)}")
                else:
                    st.caption("No specific recent topics found in snippets.")
                    
                comm = data.get("communication_analysis", {})
                st.markdown("---")
                st.caption(f"**Comm Style:** {comm.get('tone_style', 'Neutral')} | **Formality:** {comm.get('formality_score_0_to_100', 50)}%")

            with t3:
                strat = data.get("outreach_strategy", {})
                buying = data.get("buying_intent_signals", {})
                
                st.markdown(f"**Hook:** `{strat.get('opening_hook_type', 'Direct Value')}`")
                st.markdown(f"**CTA:** `{strat.get('cta_style', 'Direct Ask')}`")
                
                signals = buying.get('signals_detected', [])
                if signals:
                    st.warning(f"🔥 **Signals:** {', '.join(signals)}")
                else:
                    st.info("No strong buying signals detected yet.")

            # --- 3. GENERATION ---
            if st.button(f"📧 Generate '{st.session_state['current_goal']}' Email", type="primary", use_container_width=True):
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
                    
                    email = generate_email(adapted_data, st.session_state["auto_notes"], st.session_state["current_goal"])
                    
                    save_email(
                        full_name,
                        role,
                        company,
                        identity.get('industry', 'Unknown'),
                        data['outreach_strategy']['recommended_tone'],
                        email,
                        f"{st.session_state['current_goal']} | {data['behavioral_intelligence']['archetype']}"
                    )
                    st.text_area("Final Draft", email, height=400)

# ================= MANUAL TAB =================
with tab_manual:
    st.caption("Paste raw text here if web search fails.")
    # (Kept simple for brevity)