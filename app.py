import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from openai import OpenAI
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class CollegeBudgetApp:
    def __init__(self):
        self.setup_page_config()
        self.setup_session_state()
        self.initialize_data()

    def setup_page_config(self):
        st.set_page_config(
            page_title="Smart College Budget Planner",
            page_icon="🎓",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
        st.markdown("""
        <style>
        .main-header {
            font-size: 3rem;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            font-weight: bold;
            margin-bottom: 2rem;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .insight-box {
            border-left: 5px solid #667eea;
            padding: 1rem;
            background: linear-gradient(90deg, #f8f9ff 0%, #e6f3ff 100%);
            margin: 1rem 0;
            border-radius: 5px;
        }
        
        .step-card {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            margin: 1rem 0;
        }
        
        .success-box {
            background: linear-gradient(90deg, #56ab2f 0%, #a8e6cf 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin: 1rem 0;
        }
        
        .stButton > button {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.5rem 2rem;
            font-weight: bold;
            transition: all 0.3s;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .chat-message {
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 10px;
            max-width: 80%;
        }
        
        .user-message {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: auto;
        }
        
        .assistant-message {
            background: #f0f8ff;
            color: #333;
            border: 1px solid #e1e5e9;
        }
        </style>
        """, unsafe_allow_html=True)

    def setup_session_state(self):
        """Initialize session state variables"""
        if 'onboarding_step' not in st.session_state:
            st.session_state.onboarding_step = 1
        if 'user_profile' not in st.session_state:
            st.session_state.user_profile = {}
        if 'school_services' not in st.session_state:
            st.session_state.school_services = {}
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'openai_client' not in st.session_state:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                st.session_state.openai_client = OpenAI(api_key=api_key)
            else:
                st.session_state.openai_client = None

    def initialize_data(self):
        """Initialize app data"""
        self.metro_areas = {
            'New York, NY': 1.8, 'San Francisco, CA': 2.0, 'Los Angeles, CA': 1.6,
            'Boston, MA': 1.5, 'Washington, DC': 1.4, 'Seattle, WA': 1.4,
            'Chicago, IL': 1.2, 'Miami, FL': 1.1, 'Denver, CO': 1.1,
            'Atlanta, GA': 1.0, 'Dallas, TX': 0.9, 'Houston, TX': 0.9,
            'Phoenix, AZ': 0.9, 'Philadelphia, PA': 1.1, 'Other/Small City': 0.8
        }
        
        self.base_budget = {
            'rent': 800, 'food': 350, 'transportation': 150, 'healthcare': 100,
            'technology': 80, 'academic': 150, 'fitness': 50, 'entertainment': 100,
            'personal_care': 50, 'utilities': 120, 'emergency_fund': 100, 'investments': 50
        }
        
        self.school_services_savings = {
            'health_center': {'category': 'healthcare', 'savings': 80},
            'counseling': {'category': 'healthcare', 'savings': 120},
            'gym': {'category': 'fitness', 'savings': 50},
            'meal_plan_required': {'category': 'food', 'savings': 300},
            'meal_plan_optional': {'category': 'food', 'savings': 200},
            'campus_shuttle': {'category': 'transportation', 'savings': 60},
            'free_parking': {'category': 'transportation', 'savings': 100},
            'free_software': {'category': 'technology', 'savings': 200},
            'computer_labs': {'category': 'technology', 'savings': 100},
            'textbook_program': {'category': 'academic', 'savings': 400}
        }

    def main(self):
        """Main app function"""
        # Header
        st.markdown('<h1 class="main-header">🎓 Smart College Budget Planner</h1>', 
                   unsafe_allow_html=True)
        
        # Sidebar navigation
        with st.sidebar:
            st.markdown("### 🧭 Navigation")
            page = st.selectbox("Choose Your Journey", [
                "🏠 Get Started",
                "📊 Budget Analysis", 
                "💡 AI Insights",
                "📈 Investment Guide",
                "💬 AI Chat Support"
            ])
            
            # Progress indicator
            if st.session_state.user_profile:
                st.markdown("### ✅ Profile Complete!")
                st.json(st.session_state.user_profile)
            else:
                st.markdown("### ⏳ Complete Your Profile")
                st.progress(st.session_state.onboarding_step / 4)

        # Route to pages
        if page == "🏠 Get Started":
            self.show_onboarding()
        elif page == "📊 Budget Analysis":
            self.show_budget_analysis()
        elif page == "💡 AI Insights":
            self.show_ai_insights()
        elif page == "📈 Investment Guide":
            self.show_investment_guide()
        elif page == "💬 AI Chat Support":
            self.show_ai_chat()

    def show_onboarding(self):
        """Onboarding flow"""
        st.markdown("## 👋 Welcome! Let's Build Your Perfect Budget")
        
        # Progress bar
        progress = st.progress(st.session_state.onboarding_step / 4)
        st.markdown(f"**Step {st.session_state.onboarding_step} of 4**")
        
        if st.session_state.onboarding_step == 1:
            self.onboarding_step_1()
        elif st.session_state.onboarding_step == 2:
            self.onboarding_step_2()
        elif st.session_state.onboarding_step == 3:
            self.onboarding_step_3()
        elif st.session_state.onboarding_step == 4:
            self.onboarding_step_4()

    def onboarding_step_1(self):
        """Step 1: Basic Info"""
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown("### 💰 Tell Us About Your Finances")
        
        col1, col2 = st.columns(2)
        
        with col1:
            monthly_budget = st.number_input(
                "💵 Monthly Budget After Tuition ($)", 
                min_value=0, max_value=10000, value=1500, step=50,
                help="Money available for living expenses each month"
            )
            
            metro_area = st.selectbox(
                "📍 Where do you go to school?",
                list(self.metro_areas.keys()),
                help="This affects cost-of-living adjustments"
            )
        
        with col2:
            housing = st.selectbox(
                "🏠 Housing Situation",
                ['Dorm/campus housing', 'Shared apartment', 'Solo apartment', 
                 'Living with family', 'Other']
            )
            
            year_in_school = st.selectbox(
                "🎓 Year in School",
                ['Freshman', 'Sophomore', 'Junior', 'Senior', 'Graduate Student']
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("Next: School Services →", type="primary"):
            st.session_state.user_profile.update({
                'monthly_budget': monthly_budget,
                'metro_area': metro_area,
                'housing': housing,
                'year_in_school': year_in_school
            })
            st.session_state.onboarding_step = 2
            st.rerun()

    def onboarding_step_2(self):
        """Step 2: School Services"""
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown("### 🏫 What Services Does Your School Provide?")
        st.markdown("*This helps us calculate how much you save vs. paying out-of-pocket*")
        
        # Create tabs for different service categories
        tab1, tab2, tab3, tab4 = st.tabs(["🏥 Health & Wellness", "🍕 Food", "🚗 Transport", "💻 Tech & Academic"])
        
        services = {}
        
        with tab1:
            st.markdown("**Health & Fitness Services:**")
            services['health_center'] = st.checkbox("✅ Campus health center", help="Saves ~$80/month on doctor visits")
            services['counseling'] = st.checkbox("✅ Mental health/counseling services", help="Saves ~$120/month on therapy")
            services['gym'] = st.checkbox("✅ Campus gym/fitness center", help="Saves ~$50/month on gym membership")
        
        with tab2:
            st.markdown("**Food & Dining:**")
            meal_plan = st.radio("Meal Plan Status:", ["Required", "Optional", "None"])
            if meal_plan == "Required":
                services['meal_plan_required'] = True
                st.success("💰 Saves ~$300/month on food costs!")
            elif meal_plan == "Optional":
                services['meal_plan_optional'] = True
                st.info("💰 Saves ~$200/month on food costs!")
            
            services['campus_dining'] = st.checkbox("✅ Affordable campus dining options")
        
        with tab3:
            st.markdown("**Transportation:**")
            services['campus_shuttle'] = st.checkbox("✅ Campus shuttle/bus service", help="Saves ~$60/month")
            services['free_parking'] = st.checkbox("✅ Free parking", help="Saves ~$100/month")
            services['transit_discount'] = st.checkbox("✅ Public transit discounts", help="Saves ~$40/month")
        
        with tab4:
            st.markdown("**Technology & Academic:**")
            services['free_software'] = st.checkbox("✅ Free software (Adobe, Office, etc.)", help="Saves ~$200/month")
            services['computer_labs'] = st.checkbox("✅ 24/7 computer lab access", help="Saves ~$100/month")
            services['textbook_program'] = st.checkbox("✅ Textbook rental/lending program", help="Saves ~$400/month")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                st.session_state.onboarding_step = 1
                st.rerun()
        with col2:
            if st.button("Next: Goals →", type="primary"):
                st.session_state.school_services = services
                st.session_state.onboarding_step = 3
                st.rerun()

    def onboarding_step_3(self):
        """Step 3: Goals and Preferences"""
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown("### 🎯 What Are Your Financial Goals?")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Primary Goals** (Select all that apply):")
            goals = []
            if st.checkbox("🆘 Build an emergency fund"):
                goals.append("emergency_fund")
            if st.checkbox("📈 Start investing for the future"):
                goals.append("investing")
            if st.checkbox("✈️ Save for study abroad/travel"):
                goals.append("travel")
            if st.checkbox("🎓 Save for post-graduation expenses"):
                goals.append("post_grad")
            if st.checkbox("💳 Pay off student loans"):
                goals.append("loans")
            if st.checkbox("😅 Just survive until graduation"):
                goals.append("survival")
        
        with col2:
            st.markdown("**Risk Tolerance:**")
            risk_tolerance = st.select_slider(
                "How comfortable are you with investment risk?",
                options=["Very Conservative", "Somewhat Conservative", "Moderate", "Somewhat Aggressive", "Very Aggressive"],
                value="Moderate"
            )
            
            st.markdown("**Spending Priorities:**")
            spending_style = st.radio(
                "Which describes you best?",
                ["Minimalist - only essentials", "Balanced - some fun spending", "Social - active lifestyle"]
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                st.session_state.onboarding_step = 2
                st.rerun()
        with col2:
            if st.button("Complete Setup →", type="primary"):
                st.session_state.user_profile.update({
                    'goals': goals,
                    'risk_tolerance': risk_tolerance,
                    'spending_style': spending_style
                })
                st.session_state.onboarding_step = 4
                st.rerun()

    def onboarding_step_4(self):
        """Step 4: Complete"""
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown("## 🎉 Setup Complete!")
        st.markdown("Your personalized budget analysis is ready!")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show preview of their profile
        st.markdown("### 📋 Your Profile Summary:")
        profile = st.session_state.user_profile
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Monthly Budget", f"${profile['monthly_budget']:,}")
        with col2:
            st.metric("Location", profile['metro_area'])
        with col3:
            st.metric("Year", profile['year_in_school'])
        
        # Calculate and show school savings
        total_savings = self.calculate_school_savings()
        st.success(f"🎊 Your school saves you approximately **${total_savings:,.0f} per month** in services!")
        
        if st.button("🚀 See My Budget Analysis", type="primary"):
            # Switch to budget analysis page
            st.balloons()
            # We'll simulate page switch by updating session state
            st.success("Navigate to 'Budget Analysis' in the sidebar to see your results!")

    def calculate_school_savings(self):
        """Calculate total monthly savings from school services"""
        total_savings = 0
        services = st.session_state.school_services
        
        for service, is_available in services.items():
            if is_available and service in self.school_services_savings:
                total_savings += self.school_services_savings[service]['savings']
        
        return total_savings

    def show_budget_analysis(self):
        """Main budget analysis dashboard"""
        if not st.session_state.user_profile:
            st.warning("⚠️ Please complete the onboarding first!")
            st.markdown("👈 Go to 'Get Started' in the sidebar")
            return
        
        st.markdown("## 📊 Your Personalized Budget Analysis")
        
        # Calculate optimized budget
        budget_data = self.calculate_optimized_budget()
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Monthly Budget", f"${budget_data['total_budget']:,.0f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("School Savings", f"${budget_data['school_savings']:,.0f}", 
                     delta=f"${budget_data['school_savings']*12:,.0f}/year")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Emergency Fund", f"${budget_data['emergency_fund']:,.0f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Investment Budget", f"${budget_data['investment_budget']:,.0f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Budget breakdown charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart
            fig_pie = self.create_budget_pie_chart(budget_data)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Bar chart comparison
            fig_bar = self.create_budget_comparison_chart(budget_data)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Detailed breakdown
        self.show_detailed_budget_breakdown(budget_data)

    def calculate_optimized_budget(self):
        """Calculate optimized budget based on user profile and school services"""
        profile = st.session_state.user_profile
        services = st.session_state.school_services
        
        # Start with base budget adjusted for metro area
        metro_multiplier = self.metro_areas[profile['metro_area']]
        adjusted_budget = {}
        
        for category, base_amount in self.base_budget.items():
            if category in ['rent', 'food', 'transportation', 'entertainment']:
                adjusted_budget[category] = base_amount * metro_multiplier
            else:
                adjusted_budget[category] = base_amount
        
        # Apply school service savings
        total_school_savings = 0
        for service, is_available in services.items():
            if is_available and service in self.school_services_savings:
                service_info = self.school_services_savings[service]
                category = service_info['category']
                savings = service_info['savings']
                
                if category in adjusted_budget:
                    adjusted_budget[category] = max(0, adjusted_budget[category] - savings)
                total_school_savings += savings
        
        # Reallocate surplus based on goals
        total_adjusted = sum(adjusted_budget.values())
        surplus = profile['monthly_budget'] - total_adjusted
        
        if surplus > 0:
            goals = profile.get('goals', [])
            if 'emergency_fund' in goals:
                adjusted_budget['emergency_fund'] += surplus * 0.4
            if 'investing' in goals:
                adjusted_budget['investments'] += surplus * 0.3
            if 'travel' in goals:
                adjusted_budget['entertainment'] += surplus * 0.3
        
        return {
            'budget_breakdown': adjusted_budget,
            'total_budget': profile['monthly_budget'],
            'school_savings': total_school_savings,
            'emergency_fund': adjusted_budget['emergency_fund'],
            'investment_budget': adjusted_budget['investments'],
            'surplus': surplus
        }

    def create_budget_pie_chart(self, budget_data):
        """Create pie chart of budget allocation"""
        breakdown = budget_data['budget_breakdown']
        
        # Filter out zero values and group small categories
        filtered_data = {k: v for k, v in breakdown.items() if v > 20}
        
        labels = list(filtered_data.keys())
        values