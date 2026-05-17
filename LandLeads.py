import os
import streamlit as st
import pandas as pd
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool

# --- STREAMLIT UI CONFIGURATION ---
st.set_page_config(page_title="AEEG Landowner Scout", page_icon="⚡", layout="wide")

st.title("⚡ African Earth Energy Group (AEEG)")
st.subheader("Automated Landowner Lead-Generation Scout")
st.write("Scan geographical sectors near high-capacity Eskom substations to map out agricultural and corporate landowners.")

# --- SIDEBAR FOR SECURE CREDENTIALS ---
st.sidebar.header("Configuration Panel")
openai_key = st.sidebar.text_input("OpenAI API Key", type="password", help="Needed for agent intelligence")
serper_key = st.sidebar.text_input("Serper API Key", type="password", help="Needed for live web research execution")

st.sidebar.markdown("---")
st.sidebar.write("🔒 *API credentials are run locally in-session and never stored permanently.*")

# --- PARAMETERS & SECTOR SELECTION ---
col1, col2 = st.columns(2)

with col1:
    substation_choice = st.selectbox(
        "Select Target Eskom Substation Hub",
        [
            "Mokopane MTS (Limpopo)",
            "Drakensberg Substation (KwaZulu-Natal)",
            "Welkom Substation (Free State)"
        ]
    )

with col2:
    scan_radius = st.slider("Scan Radius Boundary (Kilometers)", min_value=2.0, max_value=15.0, value=5.0, step=0.5)

# --- EXECUTION ENGINE ---
if st.button("🚀 Deploy Lead-Generation Agents", use_container_width=True):
    # Validation step to protect API execution
    if not openai_key or not serper_key:
        st.error("❌ Action Blocked: Please enter both your OpenAI and Serper API keys in the sidebar.")
    else:
        # Map credentials dynamically to environment variables for CrewAI execution
        os.environ["OPENAI_API_KEY"] = openai_key
        os.environ["SERPER_API_KEY"] = serper_key

        with st.status("🕵️‍♂️ Agents are actively researching regional registries...", expanded=True) as status:
            try:
                search_tool = SerperDevTool()

                # Agent declarations
                property_locator = Agent(
                    role="South African Land Registry Scout",
                    goal="Identify corporate entities, agricultural businesses, and trusts owning parcels inside the selected zone.",
                    backstory="Expert in identifying agricultural enterprise zones and commercial estate registrations near key infrastructure hubs.",
                    tools=[search_tool],
                    verbose=True
                )

                contact_enricher = Agent(
                    role="B2B Contact Intelligence Specialist",
                    goal="Extract corporate designations, business email addresses, and phone numbers for identified land targets.",
                    backstory="Specialist in corporate data mining. Extracts official, professional contact details compliant with business tracking protocols.",
                    tools=[search_tool],
                    verbose=True
                )

                # Execute localized target definitions
                st.write(f"🗺️ Calculating coordinate zones within {scan_radius}km of {substation_choice}...")
                
                task_locate = Task(
                    description=f"Map out 3 distinct commercial farms or corporate agricultural trusts located within a {scan_radius}km radius of the {substation_choice} cluster in South Africa.",
                    agent=property_locator,
                    expected_output="A summary list of target corporate properties and enterprise titles."
                )

                task_enrich = Task(
                    description="""For each identified entity, trace and return:
                    - Principal Decision Maker / Landowner Designation
                    - Direct Business Email Address
                    - Official Corporate Office/Mobile Phone Number
                    
                    Format the output strictly as a clean Markdown table with columns:
                    | Substation Zone | Landowner Title / Corporate Designation | Email Address | Phone Number |""",
                    agent=contact_enricher,
                    expected_output="A markdown formatted dataset containing the targeted lead contact information."
                )

                crew = Crew(
                    agents=[property_locator, contact_enricher],
                    tasks=[task_locate, task_enrich],
                    verbose=2
                )

                # Initialize process execution loop
                st.write("🤖 Agents are running live web scraping & validation queries...")
                agent_output = crew.kickoff()
                
                status.update(label="✅ Search sequence complete!", state="complete", expanded=False)
                
                # --- DISPLAY EXTRACTED METRIC INSIGHTS ---
                st.success("🎉 Target Acquisition Successful! Review extracted leads below:")
                st.markdown(str(agent_output))
                
                # Simple convenience download option for CSV conversion
                st.download_button(
                    label="📥 Download Data Dump (.txt)",
                    data=str(agent_output),
                    file_name=f"aeeg_leads_{substation_choice.lower().replace(' ', '_')}.txt",
                    mime="text/plain"
                )

            except Exception as e:
                status.update(label="💥 Execution Error", state="error")
                st.error(f"An error occurred during agent execution: {str(e)}")