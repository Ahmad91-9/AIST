"""
Real Estate Expert System - Streamlit Application
A comprehensive property valuation tool combining rule-based expert system with ML predictions.
"""
import streamlit as st
from datetime import datetime

from expert_system.validator import validate_inputs
from expert_system.engine import RuleEngine
from expert_system.ml_manager import (
    MLModelManager, blend_predictions, generate_synthetic_ml_predictions
)
from utils.charts import (
    create_price_comparison_chart, create_risk_gauge, create_forecast_chart,
    create_roi_chart, create_adjustment_waterfall, create_confidence_chart
)
from utils.export import export_to_csv, export_to_pdf, create_summary_text

# Page config
st.set_page_config(
    page_title="Real Estate Expert System",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #7f8c8d;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        border-left: 4px solid #3498db;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'evaluation_result' not in st.session_state:
    st.session_state.evaluation_result = None
if 'ml_manager' not in st.session_state:
    st.session_state.ml_manager = MLModelManager()
if 'rule_engine' not in st.session_state:
    st.session_state.rule_engine = RuleEngine()


def render_sidebar_form():
    """Render the property input form in the sidebar."""
    st.sidebar.markdown("## Property Details")
    
    # Basic Information
    st.sidebar.markdown("### Basic Information")
    
    area = st.sidebar.number_input(
        "Area (sqm) *",
        min_value=1.0,
        max_value=50000.0,
        value=100.0,
        step=10.0,
        help="Total property area in square meters"
    )
    
    property_type = st.sidebar.selectbox(
        "Property Type *",
        options=['flat', 'house', 'commercial', 'plot'],
        index=0,
        help="Type of property"
    )
    
    location = st.sidebar.selectbox(
        "Location Type",
        options=['general', 'premium', 'urban_center', 'suburban', 'rural'],
        index=0,
        help="Location category affecting base price"
    )
    
    # Property Features
    st.sidebar.markdown("### Property Features")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        bedrooms = st.number_input("Bedrooms", min_value=0, max_value=20, value=2)
    with col2:
        bathrooms = st.number_input("Bathrooms", min_value=0, max_value=15, value=1)
    
    condition = st.sidebar.selectbox(
        "Condition",
        options=['new', 'like_new', 'used_good', 'needs_renovation'],
        index=2,
        help="Current condition of the property"
    )
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        age = st.number_input("Age (years)", min_value=0, max_value=200, value=10)
    with col2:
        floor = st.number_input("Floor", min_value=-5, max_value=200, value=1)
    
    parking = st.sidebar.selectbox(
        "Parking",
        options=['none', 'street', 'covered', 'garage'],
        index=0,
        help="Type of parking available"
    )
    
    # Market Factors
    st.sidebar.markdown("### Market Factors")
    
    amenities_score = st.sidebar.slider(
        "Amenities Score",
        min_value=0.0,
        max_value=5.0,
        value=3.0,
        step=0.5,
        help="Quality of amenities (0=poor, 5=excellent)"
    )
    
    demand_score = st.sidebar.slider(
        "Market Demand",
        min_value=0.0,
        max_value=5.0,
        value=3.0,
        step=0.5,
        help="Current market demand (0=low, 5=high)"
    )
    
    # Advanced Options (collapsible)
    with st.sidebar.expander("Advanced Options"):
        occupancy_rate = st.slider(
            "Occupancy Rate (%)",
            min_value=0,
            max_value=100,
            value=90,
            help="Expected rental occupancy percentage"
        ) / 100.0
        
        market_appreciation = st.slider(
            "Market Appreciation (%)",
            min_value=-20,
            max_value=20,
            value=3,
            help="Expected annual market appreciation"
        ) / 100.0
        
        crime_index = st.slider(
            "Crime Index",
            min_value=0.0,
            max_value=1.0,
            value=0.05,
            step=0.05,
            help="Area crime index (0=safe, 1=high crime)"
        )
        
        market_volatility = st.slider(
            "Market Volatility",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.05,
            help="Market price volatility (0=stable, 1=volatile)"
        )
        
        economic_index = st.slider(
            "Economic Index",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1,
            help="Local economic health (0=poor, 1=excellent)"
        )
        
        development_index = st.slider(
            "Development Index",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.1,
            help="Planned infrastructure development (0=none, 1=major)"
        )
    
    # Optional Financial Inputs
    with st.sidebar.expander("Financial Inputs (Optional)"):
        purchase_price = st.number_input(
            "Purchase Price ($)",
            min_value=0.0,
            value=0.0,
            step=10000.0,
            help="Original purchase price (for ROI calculation)"
        )
        
        annual_rent = st.number_input(
            "Annual Rent ($)",
            min_value=0.0,
            value=0.0,
            step=1000.0,
            help="Current or expected annual rent"
        )
        
        expenses = st.number_input(
            "Annual Expenses ($)",
            min_value=0.0,
            value=0.0,
            step=500.0,
            help="Annual operating expenses"
        )
    
    # Collect all inputs
    inputs = {
        'area': area,
        'property_type': property_type,
        'location': location,
        'bedrooms': bedrooms,
        'bathrooms': bathrooms,
        'condition': condition,
        'age': age,
        'floor': floor,
        'parking': parking,
        'amenities_score': amenities_score,
        'demand_score': demand_score,
        'occupancy_rate': occupancy_rate,
        'market_appreciation_score': market_appreciation,
        'crime_index': crime_index,
        'market_volatility': market_volatility,
        'economic_index': economic_index,
        'development_index': development_index
    }
    
    # Add optional financial inputs if provided
    if purchase_price > 0:
        inputs['purchase_price'] = purchase_price
    if annual_rent > 0:
        inputs['annual_rent'] = annual_rent
    if expenses > 0:
        inputs['expenses'] = expenses
    
    return inputs


def run_evaluation(inputs):
    """Run the expert system evaluation."""
    # Validate inputs
    validation = validate_inputs(inputs)
    
    if not validation.is_valid:
        return None, validation.errors, validation.warnings
    
    # Run expert system
    rule_engine = st.session_state.rule_engine
    expert_result = rule_engine.evaluate(validation.cleaned_data)
    
    # Get ML predictions (or synthetic if models not available)
    ml_manager = st.session_state.ml_manager
    ml_results = ml_manager.predict_all(validation.cleaned_data)
    
    # Check if any models are available
    any_available = any(r.get('available', False) for r in ml_results.values())
    
    if not any_available:
        # Generate synthetic predictions for demonstration
        ml_results = generate_synthetic_ml_predictions(expert_result, validation.cleaned_data)
    
    # Blend price predictions
    ml_price_data = ml_results.get('price', {})
    ml_price = ml_price_data.get('prediction')
    ml_confidence = ml_price_data.get('confidence', 0)
    
    final_price, blend_info = blend_predictions(
        expert_result['expert_price'],
        ml_price,
        ml_confidence
    )
    
    result = {
        'features': validation.cleaned_data,
        'expert_result': expert_result,
        'ml_results': ml_results,
        'final_price': final_price,
        'blend_info': blend_info,
        'timestamp': datetime.now().isoformat(),
        'warnings': validation.warnings
    }
    
    return result, [], validation.warnings


def render_results_dashboard(result):
    """Render the results dashboard."""
    expert = result['expert_result']
    ml_results = result['ml_results']
    blend_info = result['blend_info']
    features = result['features']
    
    # Key Metrics Row
    st.markdown("### Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Final Valuation",
            value=f"${result['final_price']:,.0f}",
            delta=f"{blend_info.get('ml_weight', 0)*100:.0f}% ML blend"
        )
    
    with col2:
        st.metric(
            label="Price per SQM",
            value=f"${expert.get('price_per_sqm', 0):,.0f}",
            delta=f"{features.get('area', 0):,.0f} sqm"
        )
    
    with col3:
        roi = expert.get('roi', 0)
        roi_delta = "Excellent" if roi >= 8 else ("Good" if roi >= 5 else "Moderate")
        st.metric(
            label="Estimated ROI",
            value=f"{roi:.1f}%",
            delta=roi_delta
        )
    
    with col4:
        risk = expert.get('risk_score', 0)
        risk_level = "Low" if risk < 0.3 else ("Medium" if risk < 0.6 else "High")
        st.metric(
            label="Risk Score",
            value=f"{risk:.2f}",
            delta=risk_level,
            delta_color="inverse" if risk >= 0.5 else "normal"
        )
    
    # Charts Row
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Price Analysis", "Risk & ROI", "Price Forecast", "Adjustment Trace"
    ])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Price comparison chart
            ml_price = ml_results.get('price', {}).get('prediction', expert['expert_price'])
            fig = create_price_comparison_chart(
                expert['expert_price'],
                ml_price,
                result['final_price']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # ML Confidence chart
            fig = create_confidence_chart(ml_results)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk gauge
            fig = create_risk_gauge(expert['risk_score'])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # ROI chart
            ml_roi = ml_results.get('roi', {}).get('prediction')
            fig = create_roi_chart(expert['roi'], ml_roi)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Forecast chart
        ml_1yr = ml_results.get('future_price_1yr', {}).get('prediction')
        ml_3yr = ml_results.get('future_price_3yr', {}).get('prediction')
        
        fig = create_forecast_chart(
            expert['expert_price'],
            expert['future_price_1yr'],
            expert['future_price_3yr'],
            ml_1yr,
            ml_3yr,
            features.get('market_volatility', 0.1)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Waterfall chart
            fig = create_adjustment_waterfall(expert.get('trace', {}))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Trace details table
            st.markdown("#### Adjustment Details")
            trace = expert.get('trace', {})
            steps = trace.get('steps', [])
            
            if steps:
                for step in steps:
                    with st.container():
                        st.markdown(f"**{step['rule'].replace('_', ' ').title()}**")
                        st.caption(f"Factor: {step['factor']:.4f} | {step['delta_pct']:+.2f}%")
                        st.caption(step['reason'])
                        st.markdown("---")


def render_detailed_results(result):
    """Render detailed results section."""
    expert = result['expert_result']
    ml_results = result['ml_results']
    features = result['features']
    
    st.markdown("### Detailed Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### Expert System")
        st.write(f"**Base Price:** ${expert.get('base_price', 0):,.2f}")
        st.write(f"**Expert Price:** ${expert.get('expert_price', 0):,.2f}")
        st.write(f"**Estimated Rent:** ${expert.get('estimated_rent', 0):,.2f}/year")
        st.write(f"**1-Year Forecast:** ${expert.get('future_price_1yr', 0):,.2f}")
        st.write(f"**3-Year Forecast:** ${expert.get('future_price_3yr', 0):,.2f}")
    
    with col2:
        st.markdown("#### ML Predictions")
        for model_name, data in ml_results.items():
            if data.get('available', False):
                pred = data.get('prediction')
                conf = data.get('confidence', 0) * 100
                
                if 'price' in model_name or model_name in ['rent']:
                    pred_str = f"${pred:,.2f}"
                elif model_name in ['roi', 'risk']:
                    pred_str = f"{pred:.2f}"
                else:
                    pred_str = f"${pred:,.2f}"
                
                st.write(f"**{model_name.replace('_', ' ').title()}:** {pred_str} ({conf:.0f}% conf)")
    
    with col3:
        st.markdown("#### Property Summary")
        st.write(f"**Type:** {features.get('property_type', 'N/A').title()}")
        st.write(f"**Area:** {features.get('area', 0):,.0f} sqm")
        st.write(f"**Location:** {features.get('location', 'N/A').title()}")
        st.write(f"**Condition:** {features.get('condition', 'N/A').replace('_', ' ').title()}")
        st.write(f"**Age:** {features.get('age', 0)} years")
        st.write(f"**Bedrooms:** {features.get('bedrooms', 0)}")
        st.write(f"**Bathrooms:** {features.get('bathrooms', 0)}")


def render_export_section(result):
    """Render export options."""
    st.markdown("### Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # CSV Export
        csv_content = export_to_csv(
            result['features'],
            result['expert_result'],
            result['ml_results'],
            {'final_price': result['final_price'], 'blend_info': result['blend_info']}
        )
        st.download_button(
            label="Download CSV Report",
            data=csv_content,
            file_name=f"valuation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # PDF Export
        try:
            pdf_content = export_to_pdf(
                result['features'],
                result['expert_result'],
                result['ml_results'],
                {'final_price': result['final_price'], 'blend_info': result['blend_info']}
            )
            st.download_button(
                label="Download PDF Report",
                data=pdf_content,
                file_name=f"valuation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )
        except ImportError:
            st.info("PDF export requires FPDF library")
    
    with col3:
        # Text Summary
        summary = create_summary_text(
            result['features'],
            result['expert_result'],
            {'final_price': result['final_price'], 'blend_info': result['blend_info']}
        )
        st.download_button(
            label="Download Text Summary",
            data=summary,
            file_name=f"valuation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )


def main():
    """Main application entry point."""
    # Header
    st.markdown('<p class="main-header">Real Estate Expert System</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Comprehensive property valuation combining rule-based analysis with ML predictions</p>',
        unsafe_allow_html=True
    )
    
    # Sidebar form
    inputs = render_sidebar_form()
    
    # Evaluate button
    if st.sidebar.button("Evaluate Property", type="primary", use_container_width=True):
        with st.spinner("Running evaluation..."):
            result, errors, warnings = run_evaluation(inputs)
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                st.session_state.evaluation_result = result
                
                if warnings:
                    for warning in warnings:
                        st.warning(warning)
    
    # Display results
    if st.session_state.evaluation_result:
        result = st.session_state.evaluation_result
        
        # Show warnings if any
        if result.get('warnings'):
            with st.expander("Validation Warnings", expanded=False):
                for w in result['warnings']:
                    st.warning(w)
        
        # Main dashboard
        render_results_dashboard(result)
        
        # Detailed results
        with st.expander("Detailed Results", expanded=False):
            render_detailed_results(result)
        
        # Export section
        with st.expander("Export Report", expanded=False):
            render_export_section(result)
        
        # Blend info
        st.markdown("---")
        blend_info = result['blend_info']
        st.info(
            f"**Blending Method:** {blend_info.get('method', 'N/A').replace('_', ' ').title()} | "
            f"**Expert Weight:** {blend_info.get('expert_weight', 1)*100:.0f}% | "
            f"**ML Weight:** {blend_info.get('ml_weight', 0)*100:.0f}% | "
            f"{blend_info.get('reason', '')}"
        )
    else:
        # Welcome message
        st.markdown("""
        ### Welcome to the Real Estate Expert System
        
        This tool provides comprehensive property valuations by combining:
        
        - **Rule-Based Expert System**: Uses industry-standard formulas and multipliers
        - **Machine Learning Models**: Predicts price, rent, ROI, risk, and future values
        - **Confidence-Weighted Blending**: Combines both approaches for optimal accuracy
        
        #### Getting Started
        
        1. Fill in the property details in the sidebar
        2. Adjust market factors as needed
        3. Click "Evaluate Property" to see results
        
        The system will provide:
        - Final valuation with ML/Expert blending
        - Risk assessment and ROI calculation
        - 1-year and 3-year price forecasts
        - Detailed breakdown of all adjustments
        - Export options (CSV, PDF, Text)
        """)
        
        # Quick stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("ML Models", "6", help="Price, Rent, ROI, Risk, 1yr, 3yr forecasts")
        with col2:
            st.metric("Rule Factors", "10+", help="Location, type, condition, age, etc.")
        with col3:
            st.metric("Export Formats", "3", help="CSV, PDF, Text")
        with col4:
            model_status = st.session_state.ml_manager.get_model_status()
            available = sum(1 for m in model_status.values() if m.get('available', False))
            st.metric("Active Models", str(available), help="Real ML models loaded")


if __name__ == "__main__":
    main()
