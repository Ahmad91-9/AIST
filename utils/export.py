"""Export utilities for CSV and PDF generation."""
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
    pdf.add_page()
    
    # Title
    pdf.set_font('Helvetica', 'B', 20)
    pdf.cell(0, 15, 'Real Estate Valuation Report', 0, 1, 'C')
    
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 8, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
    pdf.ln(10)
    
    # Property Details
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_fill_color(52, 152, 219)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, 'Property Details', 0, 1, 'L', fill=True)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_font('Helvetica', '', 10)
    col_width = 95
    for key, value in features.items():
        pdf.cell(col_width, 7, key.replace('_', ' ').title(), 1)
        pdf.cell(col_width, 7, str(value), 1)
        pdf.ln()
    pdf.ln(5)
    
    # Expert Results
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_fill_color(39, 174, 96)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, 'Expert System Results', 0, 1, 'L', fill=True)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_font('Helvetica', '', 10)
    expert_metrics = [
        ('Expert Price', format_currency(expert_result.get('expert_price', 0))),
        ('Base Price', format_currency(expert_result.get('base_price', 0))),
        ('Price per SQM', format_currency(expert_result.get('price_per_sqm', 0))),
        ('Estimated Rent (Annual)', format_currency(expert_result.get('estimated_rent', 0))),
        ('ROI', format_percentage(expert_result.get('roi', 0))),
        ('Risk Score', f"{expert_result.get('risk_score', 0):.2f}"),
        ('1-Year Forecast', format_currency(expert_result.get('future_price_1yr', 0))),
        ('3-Year Forecast', format_currency(expert_result.get('future_price_3yr', 0)))
    ]
    
    for metric, value in expert_metrics:
        pdf.cell(col_width, 7, metric, 1)
        pdf.cell(col_width, 7, value, 1)
        pdf.ln()
    pdf.ln(5)
    
    # ML Results
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_fill_color(231, 76, 60)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, 'ML Model Predictions', 0, 1, 'L', fill=True)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(60, 7, 'Model', 1)
    pdf.cell(60, 7, 'Prediction', 1)
    pdf.cell(35, 7, 'Confidence', 1)
    pdf.cell(35, 7, 'Status', 1)
    pdf.ln()
    
    pdf.set_font('Helvetica', '', 10)
    for model_name, data in ml_results.items():
        prediction = data.get('prediction')
        if prediction is not None:
            if 'price' in model_name:
                pred_str = format_currency(prediction)
            elif model_name in ['roi', 'risk']:
                pred_str = f"{prediction:.2f}"
            else:
                pred_str = format_currency(prediction)
        else:
            pred_str = 'N/A'
        
        pdf.cell(60, 7, model_name.replace('_', ' ').title(), 1)
        pdf.cell(60, 7, pred_str, 1)
        pdf.cell(35, 7, format_percentage(data.get('confidence', 0) * 100), 1)
        pdf.cell(35, 7, 'Yes' if data.get('available', False) else 'No', 1)
        pdf.ln()
    pdf.ln(5)
    
    # Blended Results
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_fill_color(155, 89, 182)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, 'Final Blended Results', 0, 1, 'L', fill=True)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(col_width, 10, 'Final Valuation:', 0)
    pdf.cell(col_width, 10, format_currency(blended_result.get('final_price', 0)), 0)
    pdf.ln()
    
    blend_info = blended_result.get('blend_info', {})
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(col_width, 7, 'Blending Method:', 0)
    pdf.cell(col_width, 7, blend_info.get('method', 'N/A'), 0)
    pdf.ln()
    pdf.cell(col_width, 7, 'Expert Weight:', 0)
    pdf.cell(col_width, 7, format_percentage(blend_info.get('expert_weight', 1) * 100), 0)
    pdf.ln()
    pdf.cell(col_width, 7, 'ML Weight:', 0)
    pdf.cell(col_width, 7, format_percentage(blend_info.get('ml_weight', 0) * 100), 0)
    pdf.ln(10)
    
    # Adjustment Trace
    trace = expert_result.get('trace', {})
    steps = trace.get('steps', [])
    if steps:
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_fill_color(52, 73, 94)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 10, 'Adjustment Trace', 0, 1, 'L', fill=True)
        pdf.set_text_color(0, 0, 0)
        
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(40, 7, 'Rule', 1)
        pdf.cell(25, 7, 'Factor', 1)
        pdf.cell(25, 7, 'Delta %', 1)
        pdf.cell(100, 7, 'Reason', 1)
        pdf.ln()
        
        pdf.set_font('Helvetica', '', 9)
        for step in steps:
            pdf.cell(40, 7, step.get('rule', '')[:20], 1)
            pdf.cell(25, 7, f"{step.get('factor', 1):.3f}", 1)
            pdf.cell(25, 7, f"{step.get('delta_pct', 0):.1f}%", 1)
            pdf.cell(100, 7, step.get('reason', '')[:50], 1)
            pdf.ln()
    
    # Model Provenance
    pdf.ln(10)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, 'Model Provenance', 0, 1)
    pdf.set_font('Helvetica', '', 9)
    
    for model_name, data in ml_results.items():
        meta = data.get('model_meta', {})
        if meta:
            pdf.cell(0, 6, f"{model_name}: hash={meta.get('hash', 'N/A')}, loaded={meta.get('loaded_at', 'N/A')[:19]}", 0, 1)
    
    # Footer
    pdf.ln(10)
    pdf.set_font('Helvetica', 'I', 8)
    pdf.cell(0, 5, 'This report is generated for informational purposes only.', 0, 1, 'C')
    pdf.cell(0, 5, 'Actual property values may vary based on market conditions.', 0, 1, 'C')
    
    return pdf.output()


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
