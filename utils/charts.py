"""Visualization functions for real estate expert system using Plotly."""
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List


def create_price_comparison_chart(expert_price: float, ml_price: float, final_price: float) -> go.Figure:
    """Create bar chart comparing expert, ML, and final prices."""
    fig = go.Figure()
    
    categories = ['Expert System', 'ML Model', 'Final (Blended)']
    values = [expert_price, ml_price if ml_price else 0, final_price]
    colors = ['#3498db', '#e74c3c', '#27ae60']
    
    fig.add_trace(go.Bar(
        x=categories,
        y=values,
        marker_color=colors,
        text=[f'${v:,.0f}' for v in values],
        textposition='outside',
        textfont=dict(size=14)
    ))
    
    fig.update_layout(
        title=dict(text='Price Comparison', font=dict(size=18)),
        yaxis_title='Price ($)',
        showlegend=False,
        height=400,
        margin=dict(t=60, b=40, l=60, r=40),
        plot_bgcolor='white',
        yaxis=dict(
            gridcolor='lightgray',
            tickformat='$,.0f'
        )
    )
    
    return fig


def create_risk_gauge(risk_score: float) -> go.Figure:
    """Create a gauge chart for risk score (0-1 scale)."""
    # Convert to percentage
    risk_pct = risk_score * 100
    
    # Determine color based on risk level
    if risk_pct < 30:
        color = '#27ae60'  # Green - Low risk
        risk_level = 'Low'
    elif risk_pct < 60:
        color = '#f39c12'  # Orange - Medium risk
        risk_level = 'Medium'
    else:
        color = '#e74c3c'  # Red - High risk
        risk_level = 'High'
    
    fig = go.Figure(go.Indicator(
        mode='gauge+number',
        value=risk_pct,
        number={'suffix': '%', 'font': {'size': 36}},
        title={'text': f'Risk Level: {risk_level}', 'font': {'size': 18}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': color, 'thickness': 0.75},
            'bgcolor': 'white',
            'borderwidth': 2,
            'bordercolor': 'gray',
            'steps': [
                {'range': [0, 30], 'color': '#d5f5e3'},
                {'range': [30, 60], 'color': '#fdebd0'},
                {'range': [60, 100], 'color': '#fadbd8'}
            ],
            'threshold': {
                'line': {'color': 'black', 'width': 2},
                'thickness': 0.8,
                'value': risk_pct
            }
        }
    ))
    
    fig.update_layout(
        height=350,
        margin=dict(t=60, b=20, l=40, r=40)
    )
    
    return fig


def create_forecast_chart(current_price: float, price_1yr: float, price_3yr: float,
                          ml_1yr: float = None, ml_3yr: float = None,
                          volatility: float = 0.1) -> go.Figure:
    """Create line chart with price forecast and uncertainty bands."""
    fig = go.Figure()
    
    # Timeline
    years = [0, 1, 3]
    
    # Expert forecast
    expert_values = [current_price, price_1yr, price_3yr]
    
    # Calculate uncertainty bands based on volatility
    uncertainty_1yr = current_price * volatility * 0.5
    uncertainty_3yr = current_price * volatility * 1.5
    
    upper_band = [current_price, price_1yr + uncertainty_1yr, price_3yr + uncertainty_3yr]
    lower_band = [current_price, max(0, price_1yr - uncertainty_1yr), max(0, price_3yr - uncertainty_3yr)]
    
    # Add uncertainty band
    fig.add_trace(go.Scatter(
        x=years + years[::-1],
        y=upper_band + lower_band[::-1],
        fill='toself',
        fillcolor='rgba(52, 152, 219, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Uncertainty Range',
        showlegend=True
    ))
    
    # Expert forecast line
    fig.add_trace(go.Scatter(
        x=years,
        y=expert_values,
        mode='lines+markers',
        name='Expert Forecast',
        line=dict(color='#3498db', width=3),
        marker=dict(size=10)
    ))
    
    # ML forecast if available
    if ml_1yr is not None and ml_3yr is not None:
        ml_values = [current_price, ml_1yr, ml_3yr]
        fig.add_trace(go.Scatter(
            x=years,
            y=ml_values,
            mode='lines+markers',
            name='ML Forecast',
            line=dict(color='#e74c3c', width=2, dash='dash'),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        title=dict(text='Price Forecast (1 & 3 Year)', font=dict(size=18)),
        xaxis_title='Years from Now',
        yaxis_title='Estimated Price ($)',
        height=400,
        margin=dict(t=60, b=40, l=60, r=40),
        plot_bgcolor='white',
        legend=dict(
            yanchor='top',
            y=0.99,
            xanchor='left',
            x=0.01
        ),
        xaxis=dict(
            tickmode='array',
            tickvals=[0, 1, 3],
            ticktext=['Current', '1 Year', '3 Years'],
            gridcolor='lightgray'
        ),
        yaxis=dict(
            gridcolor='lightgray',
            tickformat='$,.0f'
        )
    )
    
    return fig


def create_roi_chart(roi: float, ml_roi: float = None) -> go.Figure:
    """Create ROI comparison chart."""
    fig = go.Figure()
    
    # Data
    if ml_roi is not None:
        categories = ['Expert ROI', 'ML ROI']
        values = [roi, ml_roi]
        colors = ['#3498db', '#e74c3c']
    else:
        categories = ['Estimated ROI']
        values = [roi]
        colors = ['#3498db']
    
    # Determine color based on ROI value
    bar_colors = []
    for v in values:
        if v >= 8:
            bar_colors.append('#27ae60')  # Green - excellent
        elif v >= 5:
            bar_colors.append('#3498db')  # Blue - good
        elif v >= 3:
            bar_colors.append('#f39c12')  # Orange - moderate
        else:
            bar_colors.append('#e74c3c')  # Red - poor
    
    fig.add_trace(go.Bar(
        x=categories,
        y=values,
        marker_color=bar_colors,
        text=[f'{v:.1f}%' for v in values],
        textposition='outside',
        textfont=dict(size=14)
    ))
    
    # Add reference lines
    fig.add_hline(y=5, line_dash='dash', line_color='gray', 
                  annotation_text='Average (5%)', annotation_position='right')
    fig.add_hline(y=8, line_dash='dash', line_color='green',
                  annotation_text='Excellent (8%)', annotation_position='right')
    
    fig.update_layout(
        title=dict(text='Return on Investment (ROI)', font=dict(size=18)),
        yaxis_title='Annual ROI (%)',
        showlegend=False,
        height=350,
        margin=dict(t=60, b=40, l=60, r=80),
        plot_bgcolor='white',
        yaxis=dict(
            gridcolor='lightgray',
            range=[0, max(max(values) * 1.3, 10)]
        )
    )
    
    return fig


def create_adjustment_waterfall(trace: Dict[str, Any]) -> go.Figure:
    """Create waterfall chart showing price adjustments."""
    steps = trace.get('steps', [])
    
    if not steps:
        # Return empty chart if no steps
        fig = go.Figure()
        fig.add_annotation(
            text="No adjustment data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14)
        )
        return fig
    
    # Prepare data for waterfall
    labels = ['Base Price']
    values = [trace.get('base_price', 0)]
    measures = ['absolute']
    
    for step in steps:
        labels.append(step['rule'].replace('_', ' ').title())
        delta = step['value_after'] - step['value_before']
        values.append(delta)
        measures.append('relative')
    
    labels.append('Final Price')
    values.append(trace.get('final_price', sum(values)))
    measures.append('total')
    
    fig = go.Figure(go.Waterfall(
        name='Price Adjustments',
        orientation='v',
        measure=measures,
        x=labels,
        y=values,
        textposition='outside',
        text=[f'${v:,.0f}' if i == 0 or i == len(values)-1 else f'{v:+,.0f}' 
              for i, v in enumerate(values)],
        connector={'line': {'color': 'rgb(63, 63, 63)'}},
        increasing={'marker': {'color': '#27ae60'}},
        decreasing={'marker': {'color': '#e74c3c'}},
        totals={'marker': {'color': '#3498db'}}
    ))
    
    fig.update_layout(
        title=dict(text='Price Breakdown (Waterfall)', font=dict(size=18)),
        yaxis_title='Price ($)',
        showlegend=False,
        height=450,
        margin=dict(t=60, b=100, l=60, r=40),
        plot_bgcolor='white',
        xaxis=dict(tickangle=-45),
        yaxis=dict(
            gridcolor='lightgray',
            tickformat='$,.0f'
        )
    )
    
    return fig


def create_confidence_chart(ml_results: Dict[str, Dict]) -> go.Figure:
    """Create horizontal bar chart showing ML model confidence levels."""
    models = []
    confidences = []
    colors = []
    
    for name, data in ml_results.items():
        if data.get('available', False):
            models.append(name.replace('_', ' ').title())
            conf = data.get('confidence', 0) * 100
            confidences.append(conf)
            
            # Color based on confidence
            if conf >= 70:
                colors.append('#27ae60')
            elif conf >= 50:
                colors.append('#f39c12')
            else:
                colors.append('#e74c3c')
    
    fig = go.Figure(go.Bar(
        x=confidences,
        y=models,
        orientation='h',
        marker_color=colors,
        text=[f'{c:.0f}%' for c in confidences],
        textposition='outside'
    ))
    
    fig.update_layout(
        title=dict(text='ML Model Confidence', font=dict(size=18)),
        xaxis_title='Confidence (%)',
        xaxis=dict(range=[0, 110]),
        height=300,
        margin=dict(t=60, b=40, l=120, r=40),
        plot_bgcolor='white'
    )
    
    return fig
