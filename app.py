import streamlit as st
from db import create_lead, read_lead, update_lead_score, search_leads
from grok_client import qualify_lead, generate_message
import json

# --------------------------------------------------------------
# TOAST NOTIFICATION FOR NEW LEAD
# --------------------------------------------------------------



# ---------- PAGE ----------
st.set_page_config(page_title="Grok SDR Demo", layout="wide")
st.title("Grok-Powered SDR: Qualify & Outreach Like Never Before!")

# ---------- SIDEBAR ICP ----------
st.sidebar.header("Enter your criteria")
user_icp = st.sidebar.text_input(
    "Define what's important (e.g., 'AI sales tools, >50 employees')",
    "Tech companies seeking AI automation",
    key="icp_input"
)

# ---------- SESSION STATE FOR CHAT ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}      # {lead_id: [{"role":..., "content":...}, ...]}
if "selected_lead" not in st.session_state:
    st.session_state.selected_lead = None

# ---------- TABS ----------
tab1, tab2, tab3 = st.tabs(["Add Lead", "Search & Qualify", "View History"])

# --------------------------------------------------------------
# TAB 1 – Add Lead
# --------------------------------------------------------------
with tab1:
    st.header("Add New Lead")
    col1, col2, col3 = st.columns(3)
    with col1: name = st.text_input("Name")
    with col2: company = st.text_input("Company")
    with col3: email = st.text_input("Email")
    notes = st.text_area("Notes")
    if st.button("Add Lead", key="add_lead_btn"):
        if name and company and email:
            lead_id = create_lead({"name": name, "company": company, "email": email, "notes": notes})
            st.success(f"Lead added! ID: {lead_id}")
        else:
            st.error("Fill all fields")

# --------------------------------------------------------------
# TAB 2 – Search & Qualify + AI CHAT + CALENDLY
# --------------------------------------------------------------
with tab2:
    st.header("Search & Qualify Leads")
    query = st.text_input("Search by name/company/email", key="search_query")
    if query:
        leads = search_leads(query)
        for lead in leads:
            # ---- Lead expander -------------------------------------------------
            with st.expander(f"{lead['name']} @ {lead['company']} (Score: {lead['score']})"):
                # ---- Re-Qualify ------------------------------------------------
                if st.button(f"Re-Qualify {lead['name']}", key=f"qual_{lead['id']}"):
                    full_lead = read_lead(lead['id'])
                    qual = qualify_lead(full_lead, user_icp)
                    update_lead_score(lead['id'], qual['score'], user_icp)
                    st.rerun()
                    st.info(f"**Explanation**: {qual['explanation']}")
                    st.info(f"**Next**: {qual['next_action']}")

                # ---- Select lead for chat ----------------------------------------
                if st.button(f"Open AI Assistant for {lead['name']}", key=f"chat_{lead['id']}"):
                    st.session_state.selected_lead = lead['id']
                    if lead['id'] not in st.session_state.chat_history:
                        st.session_state.chat_history[lead['id']] = []

                # ---- Show chat if this lead is selected -------------------------
                if st.session_state.selected_lead == lead['id']:
                    st.markdown("### AI Assistant Chat")
                    # display history
                    for msg in st.session_state.chat_history[lead['id']]:
                        if msg["role"] == "user":
                            st.markdown(f"**You:** {msg['content']}")
                        else:
                            st.markdown(f"**Grok:** {msg['content']}")

                    # user input
                    user_msg = st.text_input("Ask Grok to generate an email or anything else…", key=f"user_msg_{lead['id']}")
                    col_send, col_cal = st.columns([3, 1])
                    with col_send:
                        send = st.button("Send", key=f"send_{lead['id']}")
                    with col_cal:
                        cal = st.button("Get Calendly Link", key=f"cal_{lead['id']}")

                    # ---- SEND MESSAGE ------------------------------------------------
                    if send and user_msg:
                        # append user message
                        st.session_state.chat_history[lead['id']].append({"role": "user", "content": user_msg})

                        # call Grok (email generation is a special case)
                        full_lead = read_lead(lead['id'])
                        if "email" in user_msg.lower():
                            grok_reply = generate_message(full_lead, "intro")
                        else:
                            # generic Grok call 
                            prompt = f"""
                            You are an SDR assistant for {full_lead['name']} at {full_lead['company']}.
                            ICP: {user_icp}
                            User says: {user_msg}
                            Respond helpfully in 2-3 sentences.
                            """
                            # reuse the same client from grok_client (assumes MOCK=False for real API)
                            from grok_client import client, MOCK
                            if MOCK:
                                grok_reply = "Here's a quick reply based on your request."
                            else:
                                resp = client.chat.completions.create(
                                    model="grok-beta",
                                    messages=[{"role": "user", "content": prompt}],
                                    temperature=0.7,
                                    max_tokens=200
                                )
                                grok_reply = resp.choices[0].message.content.strip()

                        st.session_state.chat_history[lead['id']].append({"role": "assistant", "content": grok_reply})
                        st.rerun()

                    # ---- CALENDLY LINK ------------------------------------------------
                    if cal:
                        full_lead = read_lead(lead['id'])
                        prompt = f"""
                        Generate a personal Calendly scheduling link for a 15-minute discovery call
                        with {full_lead['name']} at {full_lead['company']}.
                        Use the format: https://calendly.com/your-handle/15min
                        Replace "your-handle" with a realistic placeholder.
                        """
                        from grok_client import client, MOCK
                        if MOCK:
                            cal_link = "https://calendly.com/demo-sdr/15min"
                        else:
                            resp = client.chat.completions.create(
                                model="grok-beta",
                                messages=[{"role": "user", "content": prompt}],
                                temperature=0.0,
                                max_tokens=50
                            )
                            cal_link = resp.choices[0].message.content.strip()

                        st.session_state.chat_history[lead['id']].append(
                            {"role": "assistant", "content": f"Schedule a meeting: {cal_link}"}
                        )
                        st.rerun()

# --------------------------------------------------------------
# TAB 3 – View History
# --------------------------------------------------------------
with tab3:
    st.header("Lead History")
    lead_id = st.number_input("Lead ID to View", min_value=1, key="history_id")
    if lead_id:
        lead = read_lead(lead_id)
        if lead:
            st.json(lead)
        else:
            st.error("Lead not found")

# --------------------------------------------------------------
# FOOTER – Model Evals
# --------------------------------------------------------------
if st.button("Run Model Evals", key="run_evals"):
    import subprocess, sys
    result = subprocess.run([sys.executable, "-m", "pytest", "evals.py", "-v"],
                            capture_output=True, text=True)
    st.code(result.stdout)