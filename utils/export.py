"""Export utilities for CSV, PDF, and text generation."""
import csv
import io
from datetime import datetime
from typing import Dict, Any, List

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False


def format_currency(value: float) -> str:
    """Format a number as currency."""
    return f"${value:,.2f}"


def format_percentage(value: float) -> str:
    """Format a number as percentage."""
    return f"{value:.2f}%"


def export_to_csv(features: Dict[str, Any], expert_result: Dict[str, Any],
                  ml_results: Dict[str, Dict], blended_result: Dict[str, Any]) -> str:
    """
    Export evaluation results to CSV format.
    Returns CSV content as a string.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Real Estate Valuation Report'])
    writer.writerow(['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow([])
    
    # Property Details
    writer.writerow(['PROPERTY DETAILS'])
    writer.writerow(['Field', 'Value'])
    for key, value in features.items():
        writer.writerow([key.replace('_', ' ').title(), str(value)])
    writer.writerow([])
    
    # Expert System Results
    writer.writerow(['EXPERT SYSTEM RESULTS'])
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Expert Price', format_currency(expert_result.get('expert_price', 0))])
    writer.writerow(['Base Price', format_currency(expert_result.get('base_price', 0))])
    writer.writerow(['Price per SQM', format_currency(expert_result.get('price_per_sqm', 0))])
    writer.writerow(['Estimated Annual Rent', format_currency(expert_result.get('estimated_rent', 0))])
    writer.writerow(['ROI', format_percentage(expert_result.get('roi', 0))])
    writer.writerow(['Risk Score', f"{expert_result.get('risk_score', 0):.2f}"])
    writer.writerow(['1-Year Forecast', format_currency(expert_result.get('future_price_1yr', 0))])
    writer.writerow(['3-Year Forecast', format_currency(expert_result.get('future_price_3yr', 0))])
    writer.writerow([])
    
    # ML Model Results
    writer.writerow(['ML MODEL PREDICTIONS'])
    writer.writerow(['Model', 'Prediction', 'Confidence', 'Available'])
    for model_name, data in ml_results.items():
        prediction = data.get('prediction')
        pred_str = format_currency(prediction) if prediction and 'price' in model_name else (
            format_percentage(prediction) if prediction and model_name in ['roi', 'risk'] else 
            str(prediction) if prediction else 'N/A'
        )
        writer.writerow([
            model_name.replace('_', ' ').title(),
            pred_str,
            format_percentage(data.get('confidence', 0) * 100),
            'Yes' if data.get('available', False) else 'No'
        ])
    writer.writerow([])
    
    # Blended Results
    writer.writerow(['BLENDED RESULTS'])
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Final Price', format_currency(blended_result.get('final_price', 0))])
    writer.writerow(['Blending Method', blended_result.get('blend_info', {}).get('method', 'N/A')])
    writer.writerow(['Expert Weight', format_percentage(blended_result.get('blend_info', {}).get('expert_weight', 1) * 100)])
    writer.writerow(['ML Weight', format_percentage(blended_result.get('blend_info', {}).get('ml_weight', 0) * 100)])
    writer.writerow([])
    
    # Adjustment Trace
    trace = expert_result.get('trace', {})
    steps = trace.get('steps', [])
    if steps:
        writer.writerow(['ADJUSTMENT TRACE'])
        writer.writerow(['Rule', 'Factor', 'Delta %', 'Reason'])
        for step in steps:
            writer.writerow([
                step.get('rule', ''),
                f"{step.get('factor', 1):.4f}",
                f"{step.get('delta_pct', 0):.2f}%",
                step.get('reason', '')
            ])
    
    return output.getvalue()


def export_to_pdf(features: Dict[str, Any], expert_result: Dict[str, Any],
                  ml_results: Dict[str, Dict], blended_result: Dict[str, Any]) -> bytes:
    """
    Export evaluation results to PDF format.
    Returns PDF content as bytes.
    """
    if not FPDF_AVAILABLE:
        raise ImportError("FPDF library not available")
    
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # ========== HEADER WITH GRADIENT-STYLE BANNER ==========
    # Dark blue header banner
    pdf.set_fill_color(30, 60, 114)
    pdf.rect(0, 0, 210, 45, 'F')
    
    # Title
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 24)
    pdf.set_y(12)
    pdf.cell(0, 10, 'Real Estate Valuation Report', 0, 1, 'C')
    
    # Subtitle
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(200, 220, 255)
    pdf.cell(0, 8, 'Comprehensive Property Analysis & ML-Enhanced Predictions', 0, 1, 'C')
    
    # Date line
    pdf.set_font('Helvetica', 'I', 9)
    pdf.set_text_color(180, 200, 230)
    pdf.cell(0, 6, f'Generated: {datetime.now().strftime("%B %d, %Y at %H:%M")}', 0, 1, 'C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(12)
    
    # ========== EXECUTIVE SUMMARY BOX ==========
    final_price = blended_result.get('final_price', 0)
    risk_score = expert_result.get('risk_score', 0)
    roi = expert_result.get('roi', 0)
    risk_level = 'Low' if risk_score < 0.3 else ('Medium' if risk_score < 0.6 else 'High')
    
    # Light gray background box
    pdf.set_fill_color(245, 247, 250)
    pdf.rect(10, pdf.get_y(), 190, 28, 'F')
    
    # Draw border
    pdf.set_draw_color(200, 200, 200)
    pdf.rect(10, pdf.get_y(), 190, 28, 'D')
    
    y_start = pdf.get_y() + 4
    
    # Final Valuation (large, centered)
    pdf.set_xy(10, y_start)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(63, 6, 'Final Valuation', 0, 0, 'C')
    pdf.cell(64, 6, 'Estimated ROI', 0, 0, 'C')
    pdf.cell(63, 6, 'Risk Level', 0, 1, 'C')
    
    pdf.set_xy(10, y_start + 8)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(30, 60, 114)
    pdf.cell(63, 10, format_currency(final_price), 0, 0, 'C')
    pdf.set_text_color(39, 174, 96)
    pdf.cell(64, 10, f'{roi:.1f}%', 0, 0, 'C')
    risk_color = (39, 174, 96) if risk_level == 'Low' else ((230, 150, 0) if risk_level == 'Medium' else (220, 53, 69))
    pdf.set_text_color(*risk_color)
    pdf.cell(63, 10, risk_level, 0, 1, 'C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(18)
    
    # ========== PROPERTY DETAILS SECTION ==========
    _pdf_section_header(pdf, 'Property Details', (52, 152, 219))
    
    # Two-column layout for property details
    pdf.set_font('Helvetica', '', 10)
    col_width = 95
    row_height = 7
    
    # Filter out internal/zero values for cleaner display
    display_features = {k: v for k, v in features.items() 
                       if v not in [0, 0.0, 'none', ''] or k in ['bedrooms', 'bathrooms', 'floor']}
    
    items = list(display_features.items())
    for i in range(0, len(items), 2):
        # Left column
        key1, val1 = items[i]
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(45, row_height, key1.replace('_', ' ').title() + ':', 0, 0, 'L')
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(50, row_height, str(val1), 0, 0, 'L')
        
        # Right column (if exists)
        if i + 1 < len(items):
            key2, val2 = items[i + 1]
            pdf.set_font('Helvetica', 'B', 9)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(45, row_height, key2.replace('_', ' ').title() + ':', 0, 0, 'L')
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(50, row_height, str(val2), 0, 1, 'L')
        else:
            pdf.ln()
    
    pdf.ln(6)
    
    # ========== EXPERT SYSTEM RESULTS ==========
    _pdf_section_header(pdf, 'Expert System Analysis', (39, 174, 96))
    
    expert_metrics = [
        ('Base Price', format_currency(expert_result.get('base_price', 0))),
        ('Expert Price', format_currency(expert_result.get('expert_price', 0))),
        ('Price per SQM', format_currency(expert_result.get('price_per_sqm', 0))),
        ('Est. Annual Rent', format_currency(expert_result.get('estimated_rent', 0))),
        ('1-Year Forecast', format_currency(expert_result.get('future_price_1yr', 0))),
        ('3-Year Forecast', format_currency(expert_result.get('future_price_3yr', 0))),
    ]
    
    _pdf_metrics_table(pdf, expert_metrics, 2)
    pdf.ln(6)
    
    # ========== ML MODEL PREDICTIONS ==========
    _pdf_section_header(pdf, 'ML Model Predictions', (142, 68, 173))
    
    # Table header
    pdf.set_fill_color(250, 250, 252)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(55, 8, 'Model', 1, 0, 'C', fill=True)
    pdf.cell(50, 8, 'Prediction', 1, 0, 'C', fill=True)
    pdf.cell(40, 8, 'Confidence', 1, 0, 'C', fill=True)
    pdf.cell(40, 8, 'Status', 1, 1, 'C', fill=True)
    
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(0, 0, 0)
    
    row_alt = False
    for model_name, data in ml_results.items():
        prediction = data.get('prediction')
        if prediction is not None:
            if 'price' in model_name or model_name == 'rent':
                pred_str = format_currency(prediction)
            elif model_name in ['roi', 'risk']:
                pred_str = f"{prediction:.2f}"
            else:
                pred_str = format_currency(prediction)
        else:
            pred_str = 'N/A'
        
        confidence = data.get('confidence', 0) * 100
        available = data.get('available', False)
        
        # Alternating row colors
        if row_alt:
            pdf.set_fill_color(248, 249, 252)
        else:
            pdf.set_fill_color(255, 255, 255)
        
        pdf.cell(55, 7, model_name.replace('_', ' ').title(), 1, 0, 'L', fill=True)
        pdf.cell(50, 7, pred_str, 1, 0, 'R', fill=True)
        
        # Confidence with color coding
        if confidence >= 80:
            pdf.set_text_color(39, 174, 96)
        elif confidence >= 50:
            pdf.set_text_color(230, 150, 0)
        else:
            pdf.set_text_color(220, 53, 69)
        pdf.cell(40, 7, f'{confidence:.0f}%', 1, 0, 'C', fill=True)
        
        # Status
        pdf.set_text_color(39, 174, 96) if available else pdf.set_text_color(150, 150, 150)
        pdf.cell(40, 7, 'Active' if available else 'Inactive', 1, 1, 'C', fill=True)
        pdf.set_text_color(0, 0, 0)
        
        row_alt = not row_alt
    
    pdf.ln(6)
    
    # ========== BLENDING METHODOLOGY ==========
    blend_info = blended_result.get('blend_info', {})
    _pdf_section_header(pdf, 'Valuation Methodology', (52, 73, 94))
    
    pdf.set_font('Helvetica', '', 10)
    method = blend_info.get('method', 'N/A').replace('_', ' ').title()
    expert_weight = blend_info.get('expert_weight', 1) * 100
    ml_weight = blend_info.get('ml_weight', 0) * 100
    
    pdf.cell(0, 7, f'Blending Method: {method}', 0, 1)
    pdf.cell(0, 7, f'Expert System Weight: {expert_weight:.0f}%  |  ML Model Weight: {ml_weight:.0f}%', 0, 1)
    
    reason = blend_info.get('reason', '')
    if reason:
        pdf.set_font('Helvetica', 'I', 9)
        pdf.set_text_color(100, 100, 100)
        pdf.multi_cell(0, 6, f'Note: {reason}')
        pdf.set_text_color(0, 0, 0)
    
    pdf.ln(4)
    
    # ========== ADJUSTMENT TRACE (if available) ==========
    trace = expert_result.get('trace', {})
    steps = trace.get('steps', [])
    if steps:
        # Check if we need a new page
        if pdf.get_y() > 220:
            pdf.add_page()
        
        _pdf_section_header(pdf, 'Price Adjustment Trace', (44, 62, 80))
        
        pdf.set_fill_color(250, 250, 252)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(35, 7, 'Rule', 1, 0, 'C', fill=True)
        pdf.cell(22, 7, 'Factor', 1, 0, 'C', fill=True)
        pdf.cell(22, 7, 'Delta', 1, 0, 'C', fill=True)
        pdf.cell(106, 7, 'Reason', 1, 1, 'C', fill=True)
        
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(0, 0, 0)
        
        for i, step in enumerate(steps):
            if i % 2 == 0:
                pdf.set_fill_color(255, 255, 255)
            else:
                pdf.set_fill_color(248, 249, 252)
            
            rule = step.get('rule', '')[:18]
            factor = step.get('factor', 1)
            delta = step.get('delta_pct', 0)
            reason = step.get('reason', '')[:55]
            
            pdf.cell(35, 6, rule, 1, 0, 'L', fill=True)
            pdf.cell(22, 6, f'{factor:.3f}', 1, 0, 'C', fill=True)
            
            # Color code delta
            if delta > 0:
                pdf.set_text_color(39, 174, 96)
            elif delta < 0:
                pdf.set_text_color(220, 53, 69)
            pdf.cell(22, 6, f'{delta:+.1f}%', 1, 0, 'C', fill=True)
            pdf.set_text_color(0, 0, 0)
            
            pdf.cell(106, 6, reason, 1, 1, 'L', fill=True)
    
    # ========== FOOTER ==========
    pdf.ln(10)
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 5, 'This report is generated for informational purposes only.', 0, 1, 'C')
    pdf.cell(0, 5, 'Actual property values may vary based on market conditions and other factors.', 0, 1, 'C')
    pdf.ln(3)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_text_color(30, 60, 114)
    pdf.cell(0, 5, 'Real Estate Expert System - Powered by ML & Rule-Based Analysis', 0, 1, 'C')
    
    # Return as bytes
    pdf_bytes = pdf.output()
    return bytes(pdf_bytes)


def _pdf_section_header(pdf: 'FPDF', title: str, color: tuple):
    """Helper to draw a styled section header."""
    pdf.set_fill_color(*color)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 9, f'  {title}', 0, 1, 'L', fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)


def _pdf_metrics_table(pdf: 'FPDF', metrics: List[tuple], cols: int = 2):
    """Helper to draw metrics in a multi-column layout."""
    pdf.set_font('Helvetica', '', 10)
    col_width = 190 // cols
    
    for i in range(0, len(metrics), cols):
        for j in range(cols):
            if i + j < len(metrics):
                label, value = metrics[i + j]
                pdf.set_font('Helvetica', '', 9)
                pdf.set_text_color(80, 80, 80)
                pdf.cell(col_width // 2, 7, label + ':', 0, 0, 'L')
                pdf.set_font('Helvetica', 'B', 10)
                pdf.set_text_color(0, 0, 0)
                pdf.cell(col_width // 2, 7, value, 0, 0, 'L')
        pdf.ln()


def create_summary_text(features: Dict[str, Any], expert_result: Dict[str, Any],
                        blended_result: Dict[str, Any]) -> str:
    """Create a human-readable summary of the valuation."""
    lines = []
    
    lines.append("=" * 50)
    lines.append("REAL ESTATE VALUATION SUMMARY")
    lines.append("=" * 50)
    lines.append("")
    
    # Property info
    lines.append(f"Property Type: {features.get('property_type', 'N/A').title()}")
    lines.append(f"Area: {features.get('area', 0):,.0f} sqm")
    lines.append(f"Location: {features.get('location', 'N/A').title()}")
    lines.append(f"Condition: {features.get('condition', 'N/A').replace('_', ' ').title()}")
    lines.append("")
    
    # Key results
    lines.append("-" * 50)
    lines.append("KEY RESULTS")
    lines.append("-" * 50)
    lines.append(f"Final Valuation: {format_currency(blended_result.get('final_price', 0))}")
    lines.append(f"Expert System Price: {format_currency(expert_result.get('expert_price', 0))}")
    lines.append(f"Price per SQM: {format_currency(expert_result.get('price_per_sqm', 0))}")
    lines.append("")
    
    # Investment metrics
    lines.append("-" * 50)
    lines.append("INVESTMENT METRICS")
    lines.append("-" * 50)
    lines.append(f"Estimated Annual Rent: {format_currency(expert_result.get('estimated_rent', 0))}")
    lines.append(f"ROI: {format_percentage(expert_result.get('roi', 0))}")
    
    risk = expert_result.get('risk_score', 0)
    risk_level = 'Low' if risk < 0.3 else ('Medium' if risk < 0.6 else 'High')
    lines.append(f"Risk Level: {risk_level} ({risk:.2f})")
    lines.append("")
    
    # Forecasts
    lines.append("-" * 50)
    lines.append("PRICE FORECASTS")
    lines.append("-" * 50)
    lines.append(f"1-Year Forecast: {format_currency(expert_result.get('future_price_1yr', 0))}")
    lines.append(f"3-Year Forecast: {format_currency(expert_result.get('future_price_3yr', 0))}")
    lines.append("")
    
    # Blending info
    blend_info = blended_result.get('blend_info', {})
    lines.append("-" * 50)
    lines.append("METHODOLOGY")
    lines.append("-" * 50)
    lines.append(f"Method: {blend_info.get('method', 'N/A').replace('_', ' ').title()}")
    lines.append(f"Expert Weight: {blend_info.get('expert_weight', 1)*100:.0f}%")
    lines.append(f"ML Weight: {blend_info.get('ml_weight', 0)*100:.0f}%")
    lines.append("")
    lines.append("=" * 50)
    
    return "\n".join(lines)
