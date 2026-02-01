import streamlit as st
import pandas as pd
import json
import os
import asyncio
from core.orchestration import ScanOrchestrator
from schemas.finding import Finding

# Page Config
st.set_page_config(
    page_title="SentinelAI Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .risk-critical { color: #ff2b2b; font-weight: bold; }
    .risk-high { color: #ffa500; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Title
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://img.icons8.com/color/96/000000/cyber-security.png", width=80)
with col2:
    st.title("SentinelAI Enterprise")
    st.markdown("Automated Security Code Review & Remediation")

# Sidebar
st.sidebar.header("Scan Control")
target_path = st.sidebar.text_input("Project Path", ".")
run_btn = st.sidebar.button("🚀 Run New Scan")

# Logic
if "findings" not in st.session_state:
    st.session_state.findings = []
    # Try loading previous report
    if os.path.exists("sentinel_report.json"):
        with open("sentinel_report.json", "r") as f:
            data = json.load(f)
            # Convert dict back to objects roughly for display
            st.session_state.findings = data

if run_btn:
    with st.spinner(f"Scanning {target_path}... (This includes SAST + AI Analysis)"):
        try:
            orchestrator = ScanOrchestrator()
            # Run the async scan
            results = asyncio.run(orchestrator.scan_directory(target_path))
            # Serialize for session state
            serialized = [x.dict() for x in results]
            st.session_state.findings = serialized
            
            # Save report
            with open("sentinel_report.json", "w") as f:
                json.dump(serialized, f, default=str, indent=2)
                
            st.success(f"Scan Complete! Found {len(results)} issues.")
        except Exception as e:
            st.error(f"Scan Failed: {e}")

# Dashboard View
if st.session_state.findings:
    df = pd.DataFrame(st.session_state.findings)
    
    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Issues", len(df))
    if not df.empty and 'severity' in df.columns:
        crit = len(df[df['severity'] == 'CRITICAL'])
        high = len(df[df['severity'] == 'HIGH'])
        med = len(df[df['severity'] == 'MEDIUM'])
        
        c2.metric("Critical", crit, delta_color="inverse")
        c3.metric("High", high, delta_color="inverse")
        c4.metric("Medium", med)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "🔎 Findings Explorer", "🧠 AI Remediation"])
    
    with tab1:
        if not df.empty and 'severity' in df.columns:
            st.bar_chart(df['severity'].value_counts())
        else:
            st.info("No data to visualize.")

    with tab2:
        st.subheader("Detailed Findings")
        if not df.empty:
            # Filter
            severity_filter = st.multiselect("Filter Severity", ["CRITICAL", "HIGH", "MEDIUM", "LOW"], default=["CRITICAL", "HIGH"])
            if severity_filter:
                filtered_df = df[df['severity'].isin(severity_filter)]
            else:
                filtered_df = df
            
            st.dataframe(filtered_df[['severity', 'title', 'confidence_score', 'type']], use_container_width=True)

    with tab3:
        st.subheader("AI-Powered Fixes")
        if not df.empty:
            selected_idx = st.selectbox("Select Issue to Fix", options=range(len(df)), format_func=lambda x: f"{df.iloc[x]['severity']} - {df.iloc[x]['title']}")
            
            finding = df.iloc[selected_idx]
            
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.markdown("### 🛑 Vulnerable Code")
                st.caption(f"File: {finding['location']['file_path']} : Lines {finding['location']['start_line']}-{finding['location']['end_line']}")
                st.code(finding['location']['snippet'], language="python")
                
                st.markdown("#### Analysis")
                st.write(finding['description'])
            
            with col_right:
                st.markdown("### ✅ Secure Fix")
                if finding['remediation']:
                    st.success("AI Remediation Available")
                    st.code(finding['remediation']['fixed_code'], language="python")
                    st.info(finding['remediation']['description'])
                else:
                    st.warning("No AI remediation available for this finding.")
else:
    st.info("👈 Enter a path and click 'Run New Scan' to start.")

