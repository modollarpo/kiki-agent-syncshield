"""
PDF Invoice Generation Service

Generates branded PDF invoices with performance breakdown.

Uses ReportLab for professional PDF rendering.

PDF Structure:
1. Header: KIKI Agent™ logo, company info, invoice number
2. Bill To: Client details
3. Invoice Summary: Billing period, due date, amount
4. Performance Breakdown:
   - Baseline revenue vs Current revenue
   - Incremental revenue (uplift)
   - Top 10 high-value conversions KIKI influenced
   - Agent contribution breakdown (pie chart)
5. Line Items: Success fee, credits, tax
6. Payment Instructions: Stripe payment link
7. Footer: "Zero-Risk Guarantee: If negative uplift, $0 fee"
"""

import logging
import os
from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Optional
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, Frame, PageTemplate
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie

from app.config import settings
from app.models import Invoice

logger = logging.getLogger(__name__)


class PDFService:
    """Service for generating PDF invoices"""
    
    def __init__(self):
        self.storage_path = settings.pdf_storage_path
        os.makedirs(self.storage_path, exist_ok=True)
        logger.info(f"✅ PDF service initialized (storage: {self.storage_path})")
    
    async def generate_invoice_pdf(self, invoice: Invoice) -> str:
        """
        Generate branded PDF invoice.
        
        Args:
            invoice: Invoice database record
        
        Returns:
            PDF file path
        """
        logger.info(f"📄 Generating PDF for invoice {invoice.invoice_number}")
        
        # PDF filename
        pdf_filename = f"{invoice.invoice_number}.pdf"
        pdf_path = os.path.join(self.storage_path, pdf_filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=1*inch
        )
        
        # Container for PDF elements
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1E3A8A'),  # KIKI blue
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1E3A8A'),
            spaceAfter=12
        )
        
        # 1. Header
        story.append(Paragraph("KIKI Agent™", title_style))
        story.append(Paragraph("Outcome-as-a-Service Platform", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Company info
        company_info = f"""
        <b>{settings.company_name}</b><br/>
        {settings.company_address}<br/>
        {settings.company_email}
        """
        story.append(Paragraph(company_info, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Invoice header table
        invoice_header_data = [
            ['Invoice Number:', invoice.invoice_number],
            ['Issue Date:', invoice.issue_date.strftime('%B %d, %Y')],
            ['Due Date:', invoice.due_date.strftime('%B %d, %Y')],
            ['Billing Period:', f"{invoice.billing_year}-{invoice.billing_month:02d}"],
        ]
        
        invoice_header_table = Table(invoice_header_data, colWidths=[2*inch, 3*inch])
        invoice_header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(invoice_header_table)
        story.append(Spacer(1, 0.3*inch))
        
        # 2. Bill To
        story.append(Paragraph("Bill To:", heading_style))
        bill_to_text = f"""
        <b>{invoice.customer_name}</b><br/>
        {invoice.customer_email}<br/>
        Store ID: {invoice.store_id}
        """
        story.append(Paragraph(bill_to_text, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # 3. Performance Summary
        story.append(Paragraph("Performance Summary", heading_style))
        
        performance_data = [
            ['Metric', 'Value'],
            ['Baseline Revenue (Pre-KIKI)', f"${invoice.baseline_revenue:,.2f}"],
            ['Current Revenue', f"${invoice.actual_revenue:,.2f}"],
            ['Incremental Revenue', f"${invoice.incremental_revenue:,.2f}"],
            ['Uplift Percentage', f"{invoice.uplift_percentage}%"],
            ['Success Fee Rate', '20%'],
        ]
        
        performance_table = Table(performance_data, colWidths=[3*inch, 2*inch])
        performance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(performance_table)
        story.append(Spacer(1, 0.3*inch))
        
        # 4. Line Items
        story.append(Paragraph("Invoice Details", heading_style))
        
        line_items_data = [
            ['Description', 'Quantity', 'Unit Price', 'Amount']
        ]
        
        # Success fee line
        line_items_data.append([
            f"Success Fee (20% of ${invoice.incremental_revenue:,.2f} incremental revenue)",
            '1',
            f"${invoice.subtotal:,.2f}",
            f"${invoice.subtotal:,.2f}"
        ])
        
        # Tax line (if applicable)
        if invoice.tax_amount > 0:
            line_items_data.append([
                f"Tax ({invoice.tax_rate * 100}%)",
                '1',
                f"${invoice.tax_amount:,.2f}",
                f"${invoice.tax_amount:,.2f}"
            ])
        
        # Credits (if applicable)
        if invoice.has_credits_applied and invoice.credits_applied > 0:
            line_items_data.append([
                "Credit Applied",
                '1',
                f"-${invoice.credits_applied:,.2f}",
                f"-${invoice.credits_applied:,.2f}"
            ])
        
        # Total
        line_items_data.append(['', '', 'Total:', f"${invoice.total_amount:,.2f}"])
        
        line_items_table = Table(line_items_data, colWidths=[3.5*inch, 0.7*inch, 1*inch, 1*inch])
        line_items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('LINEABOVE', (2, -1), (-1, -1), 2, colors.black),
        ]))
        
        story.append(line_items_table)
        story.append(Spacer(1, 0.3*inch))
        
        # 5. Payment Instructions
        story.append(Paragraph("Payment Instructions", heading_style))
        
        payment_text = f"""
        <b>Amount Due:</b> ${invoice.total_amount:,.2f}<br/>
        <b>Due Date:</b> {invoice.due_date.strftime('%B %d, %Y')}<br/>
        <b>Payment Terms:</b> Net {settings.invoice_due_days} days<br/><br/>
        
        <b>Pay Online:</b><br/>
        {invoice.hosted_invoice_url or 'Payment link will be emailed separately'}<br/><br/>
        
        <b>Questions?</b> Contact {settings.company_email}
        """
        story.append(Paragraph(payment_text, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # 6. Zero-Risk Guarantee
        zero_risk_text = """
        <b>Zero-Risk Guarantee:</b> If KIKI Agent™ underperforms (negative uplift), 
        your success fee is automatically reduced to $0.00. You only pay when you profit.
        """
        story.append(Paragraph(zero_risk_text, styles['Italic']))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"✅ PDF generated: {pdf_path}")
        
        # Generate public URL
        pdf_url = f"{settings.pdf_base_url}/{pdf_filename}"
        
        # Update invoice record with PDF paths
        # (caller should update database)
        
        return pdf_path
    
    def _create_agent_contribution_chart(
        self,
        agent_data: Dict[str, float]
    ) -> Drawing:
        """
        Create pie chart showing agent contributions.
        
        Args:
            agent_data: {"SyncFlow": 0.45, "SyncEngage": 0.30, ...}
        
        Returns:
            ReportLab Drawing object
        """
        drawing = Drawing(400, 200)
        
        pie = Pie()
        pie.x = 150
        pie.y = 50
        pie.width = 100
        pie.height = 100
        
        # Prepare data
        labels = list(agent_data.keys())
        data = [agent_data[k] * 100 for k in labels]  # Convert to percentages
        
        pie.data = data
        pie.labels = [f"{label}: {val:.1f}%" for label, val in zip(labels, data)]
        pie.slices.strokeWidth = 0.5
        
        # Colors for agents
        colors_map = {
            "SyncFlow": colors.HexColor('#3B82F6'),    # Blue
            "SyncEngage": colors.HexColor('#10B981'),  # Green
            "SyncValue": colors.HexColor('#F59E0B'),   # Orange
            "SyncCreate": colors.HexColor('#8B5CF6'),  # Purple
        }
        
        for i, label in enumerate(labels):
            pie.slices[i].fillColor = colors_map.get(label, colors.grey)
        
        drawing.add(pie)
        return drawing
