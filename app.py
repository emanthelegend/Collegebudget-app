import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import google.generativeai as genai
import json

class CollegeBudgetApp:
    def __init__(self):
        self.setup_page_config()
        self.setup_session_state()
        self.initialize_data()
        self.setup_gemini()

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
        
        .chat-message {
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 10px;
        }
        
        .user-message {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: 20%;
        }
        
        .assistant-message {
            background: #f0f8ff;
            color: #333;
            border: 1px solid #e1e5e9;
            margin-right: 20%;
        }
        </style>
        """, unsafe_allow_html=True)

    def setup_session_state(self):
        if 'onboarding_step' not in st.session_state:
            st.session_state.onboarding_step = 1
        if 'user_profile' not in st.session_state:
            st.session_state.user_profile = {}
        if 'school_services' not in st.session_state:
            st.session_state.school_services = {}
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

    def setup_gemini(self):
        """Set up Google Gemini API"""
        try:
            api_key = st.secrets.get("GEMINI_API_KEY", "")
            if api_key:
                genai.configure(api_key=api_key)
                st.session_state.gemini_model = genai.GenerativeModel('gemini-pro')
            else:
                st.session_state.gemini_model = None
        except Exception as e:
            st.session_state.gemini_model = None

    def initialize_data(self):
        self.metro_areas = {
            'New York, NY': 1.8, 'San Francisco, CA': 2.0, 'Los Angeles, CA': 1.6,
            'Boston, MA': 1.5, 'Washington, DC': 1.4, 'Seattle, WA': 1.4,
            'Chicago, IL': 1.2, 'Miami, FL': 1.1, 'Denver, CO': 1.1,
            'Atlanta, GA': 1.0, 'Dallas, TX': 0.9, 'Houston, TX': 0.9,
            'Phoenix, AZ': 0.9, 'Philadelphia, PA': 1.1, 'Other/Small City': 0.8
        }
        
        self.base_budget = {
            'Rent': 800, 'Food': 350, 'Transportation': 150, 'Healthcare': 100,
            'Technology': 80, 'Academic': 150, 'Fitness': 50, 'Entertainment': 100,
            'Personal Care': 50, 'Utilities': 120, 'Emergency Fund': 100, 'Investments': 50
        }
        
        self.school_services_savings = {
            'health_center': {'category': 'Healthcare', 'savings': 80},
            'counseling': {'category': 'Healthcare', 'savings': 120},
            'gym': {'category': 'Fitness', 'savings': 50},
            'meal_plan_required': {'category': 'Food', 'savings': 300},
            'meal_plan_optional': {'category': 'Food', 'savings': 200},
            'campus_shuttle': {'category': 'Transportation', 'savings': 60},
            'free_parking': {'category': 'Transportation', 'savings': 100},
            'free_software': {'category': 'Technology', 'savings': 200},
            'computer_labs': {'category': 'Technology', 'savings': 100},
            'textbook_program': {'category': 'Academic', 'savings': 400}
        }

    def main(self):
        st.markdown('<h1 class="main-header">🎓 Smart College Budget Planner</h1>', 
                   unsafe_allow_html=True)
        
        with st.sidebar:
            st.markdown("### 🧭 Navigation")
            page = st.selectbox("Choose Your Journey", [
                "🏠 Get Started",
                "📊 Budget Analysis", 
                "💬 AI Chat Support",
                "💡 Smart Tips"
            ])
            
            if st.session_state.user_profile:
                st.markdown("### ✅ Profile Complete!")
                st.success(f"Budget: ${st.session_state.user_profile.get('monthly_budget', 0):,}")
                st.info(f"Location: {st.session_state.user_profile.get('metro_area', 'Not set')}")
            else:
                st.markdown("### ⏳ Complete Your Profile")
                st.progress(st.session_state.onboarding_step / 4)

        if page == "🏠 Get Started":
            self.show_onboarding()
        elif page == "📊 Budget Analysis":
            self.show_budget_analysis()
        elif page == "💬 AI Chat Support":
            self.show_ai_chat()
        elif page == "💡 Smart Tips":
            self.show_smart_tips()

    def show_onboarding(self):
        st.markdown("## 👋 Welcome! Let's Build Your Perfect Budget")
        
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
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown("### 💰 Tell Us About Your Finances")
        
        col1, col2 = st.columns(2)
        
        with col1:
            monthly_budget = st.number_input(
                "💵 Monthly Budget After Tuition ($)", 
                min_value=0, max_value=10000, value=1500, step=50
            )
            
            metro_area = st.selectbox(
                "📍 Where do you go to school?",
                list(self.metro_areas.keys())
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
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown("### 🏫 What Services Does Your School Provide?")
        
        tab1, tab2, tab3, tab4 = st.tabs(["🏥 Health", "🍕 Food", "🚗 Transport", "💻 Tech"])
        
        services = {}
        
        with tab1:
            services['health_center'] = st.checkbox("✅ Campus health center", help="Saves ~$80/month")
            services['counseling'] = st.checkbox("✅ Mental health services", help="Saves ~$120/month")
            services['gym'] = st.checkbox("✅ Campus gym", help="Saves ~$50/month")
        
        with tab2:
            meal_plan = st.radio("Meal Plan:", ["Required", "Optional", "None"])
            if meal_plan == "Required":
                services['meal_plan_required'] = True
                st.success("💰 Saves ~$300/month!")
            elif meal_plan == "Optional":
                services['meal_plan_optional'] = True
        
        with tab3:
            services['campus_shuttle'] = st.checkbox("✅ Campus shuttle", help="Saves ~$60/month")
            services['free_parking'] = st.checkbox("✅ Free parking", help="Saves ~$100/month")
        
        with tab4:
            services['free_software'] = st.checkbox("✅ Free software", help="Saves ~$200/month")
            services['computer_labs'] = st.checkbox("✅ Computer labs", help="Saves ~$100/month")
            services['textbook_program'] = st.checkbox("✅ Textbook program", help="Saves ~$400/month")
        
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
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown("### 🎯 What Are Your Goals?")
        
        goals = []
        if st.checkbox("🆘 Build emergency fund"):
            goals.append("emergency_fund")
        if st.checkbox("📈 Start investing"):
            goals.append("investing")
        if st.checkbox("✈️ Save for travel"):
            goals.append("travel")
        if st.checkbox("🎓 Post-graduation fund"):
            goals.append("post_grad")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                st.session_state.onboarding_step = 2
                st.rerun()
        with col2:
            if st.button("Complete Setup →", type="primary"):
                st.session_state.user_profile['goals'] = goals
                st.session_state.onboarding_step = 4
                st.rerun()

    def onboarding_step_4(self):
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown("## 🎉 Setup Complete!")
        st.markdown('</div>', unsafe_allow_html=True)
        
        total_savings = sum(
            self.school_services_savings[service]['savings'] 
            for service, is_available in st.session_state.school_services.items() 
            if is_available and service in self.school_services_savings
        )
        
        st.success(f"🎊 Your school saves you **${total_savings:,.0f}/month**!")
        
        if st.button("🚀 See My Budget Analysis", type="primary"):
            st.balloons()
            st.success("Navigate to 'Budget Analysis' to see your results!")

    def show_budget_analysis(self):
        if not st.session_state.user_profile:
            st.warning("⚠️ Please complete onboarding first!")
            return
        
        st.markdown("## 📊 Your Budget Analysis")
        
        budget_data = self.calculate_budget()
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Monthly Budget", f"${budget_data['total']:,.0f}")
        with col2:
            st.metric("School Savings", f"${budget_data['savings']:,.0f}")
        with col3:
            st.metric("Emergency Fund", f"${budget_data['emergency']:,.0f}")
        with col4:
            st.metric("Investments", f"${budget_data['investments']:,.0f}")
        
        # Chart
        fig = px.pie(
            values=list(budget_data['breakdown'].values()),
            names=list(budget_data['breakdown'].keys()),
            title="Your Monthly Budget Breakdown"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Budget table
        st.markdown("### 📋 Detailed Breakdown")
        budget_df = pd.DataFrame([
            {"Category": k, "Amount": f"${v:.0f}"} 
            for k, v in budget_data['breakdown'].items()
        ])
        st.dataframe(budget_df, use_container_width=True)

    def show_ai_chat(self):
        st.markdown("## 💬 AI Financial Assistant")
        
        if not st.session_state.user_profile:
            st.warning("⚠️ Complete your profile first to get personalized advice!")
            return
        
        st.markdown("Ask me anything about budgeting, saving, investing, or managing money in college!")
        
        # Display chat history
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message">🧑‍🎓 {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message assistant-message">🤖 {message["content"]}</div>', unsafe_allow_html=True)
        
        # Chat input
        user_input = st.chat_input("Ask me a financial question...")
        
        if user_input:
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # Get AI response
            with st.spinner("Thinking..."):
                ai_response = self.get_ai_response(user_input)
            
            # Add AI response to history
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            
            st.rerun()

    def get_ai_response(self, user_question):
        """Get personalized response from Gemini AI"""
        try:
            if not st.session_state.gemini_model:
                return self.get_fallback_response(user_question)
            
            # Build context about the user
            context = self.build_user_context()
            
            system_prompt = f"""You are a knowledgeable and friendly college financial advisor AI assistant. 

Student Profile:
{context}

Provide personalized, practical, and encouraging financial advice. Be specific and actionable. Use emojis to make it engaging. Keep responses concise but helpful (2-3 paragraphs max).

Always be supportive and remember this is a college student who may be new to personal finance."""

            full_prompt = f"{system_prompt}\n\nStudent Question: {user_question}"
            
            response = st.session_state.gemini_model.generate_content(full_prompt)
            return response.text
            
        except Exception as e:
            return self.get_fallback_response(user_question)

    def build_user_context(self):
        """Build context about user for AI"""
        profile = st.session_state.user_profile
        services = st.session_state.school_services
        
        context = f"""
        Monthly Budget: ${profile.get('monthly_budget', 0):,}
        Location: {profile.get('metro_area', 'Unknown')}
        Housing: {profile.get('housing', 'Unknown')}
        Year in School: {profile.get('year_in_school', 'Unknown')}
        Goals: {', '.join(profile.get('goals', ['Not specified']))}
        
        School Services Available: {', '.join([k.replace('_', ' ').title() for k, v in services.items() if v])}
        
        School Monthly Savings: ${sum(self.school_services_savings[service]['savings'] for service, is_available in services.items() if is_available and service in self.school_services_savings)}
        """
        
        return context

    def get_fallback_response(self, question):
        """Provide smart fallback responses when AI isn't available"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['invest', 'stock', 'save']):
            return "💰 Great question about investing! As a college student, start with these steps: 1) Build a $500-1000 emergency fund first, 2) Max out any employer 401k match if you work, 3) Consider low-cost index funds like FZROX or VTI for long-term growth. Even $50/month can grow significantly by graduation!"
        
        elif any(word in question_lower for word in ['budget', 'money', 'spend']):
            budget = st.session_state.user_profile.get('monthly_budget', 1500)
            return f"📊 With your ${budget:,} monthly budget, try the 50/30/20 rule: 50% for needs (rent, food, transport), 30% for wants (entertainment, dining out), and 20% for savings and debt payments. Track your spending for a week to see where your money actually goes!"
        
        elif any(word in question_lower for word in ['debt', 'loan', 'credit']):
            return "💳 Smart to think about debt management! Priority order: 1) Pay minimums on all debts, 2) Pay extra on highest interest rate debt first, 3) Consider student loan refinancing after graduation. Avoid credit card debt if possible - it's usually 20%+ interest!"
        
        else:
            return "🎯 Here's a key tip for college financial success: Take full advantage of your school's free services (you're already paying for them!), use your student email for discounts everywhere, and start building good money habits now. Small changes compound over time!"

    def show_smart_tips(self):
        st.markdown("## 💡 Smart Money Tips for College Students")
        
        tips = [
            "💰 Take advantage of all your school's free services - you're already paying for them!",
            "🍕 Meal prep on Sundays to save $200+ per month on food costs",
            "📱 Use your student email for discounts on Spotify, Adobe, Amazon Prime, and more",
            "📚 Buy used textbooks or rent them - can save $1000+ per year",
            "🚗 Use public transportation with student discounts instead of Uber/Lyft",
            "🏋️ Use your campus gym instead of paying for outside memberships",
            "🆘 Build an emergency fund of $500-1000 before focusing on investments",
            "📈 Start investing early - even $50/month can grow to thousands by graduation!"
        ]
        
        for i, tip in enumerate(tips, 1):
            st.info(f"**Tip {i}:** {tip}")

    def calculate_budget(self):
        profile = st.session_state.user_profile
        services = st.session_state.school_services
        
        metro_multiplier = self.metro_areas[profile['metro_area']]
        adjusted_budget = {}
        
        for category, base_amount in self.base_budget.items():
            if category in ['Rent', 'Food', 'Transportation', 'Entertainment']:
                adjusted_budget[category] = base_amount * metro_multiplier
            else:
                adjusted_budget[category] = base_amount
        
        total_savings = 0
        for service, is_available in services.items():
            if is_available and service in self.school_services_savings:
                service_info = self.school_services_