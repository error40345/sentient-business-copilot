import streamlit as st
import os
import json
from datetime import datetime
from typing import Dict, List, Optional

from agents.roma_orchestrator import ROMAOrchestrator
from services.pdf_generator import PDFGenerator
from utils.state_manager import StateManager
from utils.config import Config

# Configure page
st.set_page_config(
    page_title="Sentient Business Copilot",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize configuration
config = Config()
state_manager = StateManager()

# Hide header anchor links and menu
st.markdown("""
    <style>
        .css-15zrgzn {display: none}
        .css-eczf16 {display: none}
        .css-jn99sy {display: none}
        header[data-testid="stHeader"] a {display: none}
        h1 a, h2 a, h3 a {display: none !important}
        .element-container a[href^="#"] {display: none !important}
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'business_plan' not in st.session_state:
    st.session_state.business_plan = {}
if 'current_stage' not in st.session_state:
    st.session_state.current_stage = "idea"
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = ROMAOrchestrator(config)

def main():
    # Header
    st.title("🏪 Sentient Business Copilot")
    st.markdown("*AI-powered business planning from idea to execution*")
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Dashboard")
        
        # Current stage indicator
        stages = ["idea", "research", "planning", "costing", "launch"]
        stage_icons = {"idea": "💡", "research": "🔍", "planning": "📋", "costing": "💰", "launch": "🚀"}
        
        st.subheader("Current Stage")
        for stage in stages:
            if stage == st.session_state.current_stage:
                st.write(f"**{stage_icons[stage]} {stage.title()}** ← Current")
            elif stages.index(stage) < stages.index(st.session_state.current_stage):
                st.write(f"✅ {stage_icons[stage]} {stage.title()}")
            else:
                st.write(f"⏳ {stage_icons[stage]} {stage.title()}")
        
        st.divider()
        
        # Business plan summary
        if st.session_state.business_plan:
            st.subheader("📋 Plan Summary")
            plan = st.session_state.business_plan
            
            if 'business_name' in plan:
                st.write(f"**Name:** {plan['business_name']}")
            if 'industry' in plan:
                st.write(f"**Industry:** {plan['industry']}")
            if 'location' in plan:
                st.write(f"**Location:** {plan['location']}")
            if 'estimated_cost' in plan:
                st.write(f"**Est. Cost:** ${plan['estimated_cost']:,}")
            
            st.divider()
            
            # Export PDF only
            if st.button("📄 Save as PDF", type="primary", use_container_width=True):
                generate_pdf()

    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Chat Interface")
        
        # Chat container
        chat_container = st.container()
        
        # Display chat history
        with chat_container:
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Describe your business idea or ask a question..."):
            process_user_input(prompt)
    
    with col2:
        st.header("📊 Business Insights")
        
        if st.session_state.business_plan:
            display_business_insights()
        else:
            st.info("💡 Start by describing your business idea in the chat!")

def process_user_input(prompt: str):
    """Process user input and generate AI response"""
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Show loading indicator
    with st.chat_message("assistant"):
        with st.spinner("🤖 Processing with ROMA agents..."):
            try:
                # Use ROMA orchestrator to process the request with chat history
                # Pass chat history WITHOUT the current message to avoid duplication
                response = st.session_state.orchestrator.process_request(
                    prompt, 
                    st.session_state.current_stage,
                    st.session_state.business_plan,
                    st.session_state.chat_history
                )
                
                # Add user message to chat history after orchestrator call
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                
                # Debug: Check if response is valid
                if not response or not isinstance(response, dict):
                    error_msg = "❌ Error: Invalid response from orchestrator"
                    st.error(error_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
                elif not response.get("message"):
                    error_msg = "❌ Error: Empty response from orchestrator"
                    st.error(error_msg)
                    st.write(f"Debug - Response received: {response}")
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
                else:
                    # Update business plan if new data is available
                    if response.get("business_plan_update"):
                        st.session_state.business_plan.update(response["business_plan_update"])
                        state_manager.save_business_plan(st.session_state.business_plan)
                    
                    # Update current stage if progression occurred
                    if response.get("next_stage"):
                        st.session_state.current_stage = response["next_stage"]
                    
                    # Display response
                    st.write(response["message"])
                    
                    # Add response to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": response["message"]
                    })
                
            except Exception as e:
                import traceback
                error_msg = f"❌ Error: {str(e)}"
                error_details = traceback.format_exc()
                st.error(error_msg)
                with st.expander("Error Details"):
                    st.code(error_details)
                st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
    
    # Auto-save and rerun to update UI
    state_manager.save_chat_history(st.session_state.chat_history)
    st.rerun()

def display_business_insights():
    """Display business plan insights in the sidebar"""
    plan = st.session_state.business_plan
    
    # Market insights
    if plan.get("market_data"):
        st.subheader("📈 Market Insights")
        market_data = plan["market_data"]
        
        if market_data.get("market_size"):
            st.metric("Market Size", f"${market_data['market_size']}")
        
        if market_data.get("growth_rate"):
            st.metric("Growth Rate", f"{market_data['growth_rate']}%")
        
        if market_data.get("competition_level"):
            st.write(f"**Competition:** {market_data['competition_level']}")
    
    # Financial projections
    if plan.get("financial_projections"):
        st.subheader("💰 Financial Projections")
        financials = plan["financial_projections"]
        
        if financials.get("startup_cost"):
            st.metric("Startup Cost", f"${financials['startup_cost']:,}")
        
        if financials.get("monthly_revenue_projection"):
            st.metric("Monthly Revenue (Projected)", f"${financials['monthly_revenue_projection']:,}")
        
        if financials.get("break_even_months"):
            st.metric("Break-even Timeline", f"{financials['break_even_months']} months")
    
    # Action items
    if plan.get("next_steps"):
        st.subheader("✅ Next Steps")
        for i, step in enumerate(plan["next_steps"][:5], 1):
            st.write(f"{i}. {step}")

def generate_pdf():
    """Generate PDF export of business plan"""
    try:
        pdf_generator = PDFGenerator()
        # Pass both business plan and chat history for complete PDF
        pdf_content = pdf_generator.generate_business_plan_pdf(
            st.session_state.business_plan,
            st.session_state.chat_history
        )
        
        st.download_button(
            label="📄 Download Business Plan PDF",
            data=pdf_content,
            file_name=f"business_plan_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        st.success("PDF ready for download")
    except Exception as e:
        st.error(f"❌ Error generating PDF: {str(e)}")


if __name__ == "__main__":
    main()
