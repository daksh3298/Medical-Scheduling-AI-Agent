from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os

# Create output directory
os.makedirs("app/data/sample_reports", exist_ok=True)

# ============================================================
# REPORT 1: BLOOD WORK
# ============================================================
def generate_blood_work():
    doc = SimpleDocTemplate(
        "app/data/sample_reports/blood_work.pdf",
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    
    styles = getSampleStyleSheet()
    story = []
    
    # Header
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=20,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1e40af'),
        alignment=TA_CENTER,
        spaceAfter=4
    )
    
    sub_header_style = ParagraphStyle(
        'SubHeader',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica',
        textColor=colors.HexColor('#6b7280'),
        alignment=TA_CENTER,
        spaceAfter=2
    )
    
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Normal'],
        fontSize=14,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=6
    )
    
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Normal'],
        fontSize=12,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#2563eb'),
        spaceBefore=12,
        spaceAfter=6
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica',
        textColor=colors.HexColor('#374151'),
        spaceAfter=4
    )
    
    note_style = ParagraphStyle(
        'Note',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Oblique',
        textColor=colors.HexColor('#6b7280'),
        spaceAfter=4
    )
    
    # Hospital Header
    story.append(Paragraph("City General Hospital", header_style))
    story.append(Paragraph("123 Medical Drive, San Diego, CA 92101", sub_header_style))
    story.append(Paragraph("Phone: (619) 555-0100 | Email: lab@citygeneralhospital.com", sub_header_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2563eb')))
    story.append(Spacer(1, 10))
    
    # Report Title
    story.append(Paragraph("COMPLETE BLOOD WORK REPORT", header_style))
    story.append(Spacer(1, 10))
    
    # Patient Info Table
    patient_data = [
        ["Patient Name:", "John Smith", "Report ID:", "BW-2024-1215"],
        ["Age:", "45 years", "Date:", "December 15, 2024"],
        ["Gender:", "Male", "Doctor:", "Dr. Sarah"],
        ["Patient ID:", "patient_1", "Lab Tech:", "Maria Johnson"],
    ]
    
    patient_table = Table(patient_data, colWidths=[120, 180, 120, 180])
    patient_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#374151')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    
    story.append(patient_table)
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
    
    # SECTION 1: Complete Blood Count
    story.append(Paragraph("1. Complete Blood Count (CBC)", section_style))
    
    cbc_data = [
        ["Test", "Result", "Normal Range", "Unit", "Status"],
        ["Hemoglobin", "14.2", "12.0 - 17.0", "g/dL", "✓ NORMAL"],
        ["Red Blood Cells", "4.8", "4.5 - 5.5", "million/uL", "✓ NORMAL"],
        ["White Blood Cells", "11.5", "4.5 - 11.0", "thousand/uL", "⚠ HIGH"],
        ["Platelets", "250", "150 - 400", "thousand/uL", "✓ NORMAL"],
        ["Hematocrit", "42", "38.3 - 48.6", "%", "✓ NORMAL"],
        ["MCV", "88", "80 - 100", "fL", "✓ NORMAL"],
    ]
    
    cbc_table = Table(cbc_data, colWidths=[160, 80, 120, 80, 80])
    cbc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
        ('TEXTCOLOR', (4,2), (4,2), colors.HexColor('#dc2626')),  # WBC high - red
        ('TEXTCOLOR', (4,1), (4,1), colors.HexColor('#16a34a')),  # Normal - green
        ('TEXTCOLOR', (4,3), (4,3), colors.HexColor('#16a34a')),
        ('TEXTCOLOR', (4,4), (4,4), colors.HexColor('#16a34a')),
        ('TEXTCOLOR', (4,5), (4,5), colors.HexColor('#16a34a')),
        ('TEXTCOLOR', (4,6), (4,6), colors.HexColor('#16a34a')),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
    ]))
    
    story.append(cbc_table)
    
    # SECTION 2: Metabolic Panel
    story.append(Paragraph("2. Metabolic Panel", section_style))
    
    metabolic_data = [
        ["Test", "Result", "Normal Range", "Unit", "Status"],
        ["Blood Sugar (Fasting)", "95", "70 - 100", "mg/dL", "✓ NORMAL"],
        ["Total Cholesterol", "220", "< 200", "mg/dL", "⚠ HIGH"],
        ["HDL Cholesterol", "45", "> 40", "mg/dL", "✓ NORMAL"],
        ["LDL Cholesterol", "140", "< 130", "mg/dL", "⚠ HIGH"],
        ["Triglycerides", "180", "< 150", "mg/dL", "⚠ HIGH"],
        ["Creatinine (Kidney)", "1.1", "0.7 - 1.3", "mg/dL", "✓ NORMAL"],
        ["Uric Acid", "6.2", "3.5 - 7.2", "mg/dL", "✓ NORMAL"],
    ]
    
    metabolic_table = Table(metabolic_data, colWidths=[160, 80, 120, 80, 80])
    metabolic_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
        ('TEXTCOLOR', (4,2), (4,2), colors.HexColor('#16a34a')),
        ('TEXTCOLOR', (4,3), (4,3), colors.HexColor('#dc2626')),
        ('TEXTCOLOR', (4,4), (4,4), colors.HexColor('#16a34a')),
        ('TEXTCOLOR', (4,5), (4,5), colors.HexColor('#dc2626')),
        ('TEXTCOLOR', (4,6), (4,6), colors.HexColor('#dc2626')),
        ('TEXTCOLOR', (4,7), (4,7), colors.HexColor('#16a34a')),
        ('TEXTCOLOR', (4,8), (4,8), colors.HexColor('#16a34a')),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
    ]))
    
    story.append(metabolic_table)
    
    # Doctor's Notes
    story.append(Paragraph("3. Doctor's Notes", section_style))
    story.append(Paragraph("• White Blood Cell count is slightly elevated. Patient advised to monitor for signs of infection or inflammation.", normal_style))
    story.append(Paragraph("• Total Cholesterol and LDL levels are above normal range. Patient advised to follow a low-fat, low-cholesterol diet.", normal_style))
    story.append(Paragraph("• Triglycerides are elevated. Reduce sugar and refined carbohydrate intake.", normal_style))
    story.append(Paragraph("• All other parameters are within normal limits.", normal_style))
    story.append(Paragraph("• Follow-up blood work recommended in 3 months.", normal_style))
    story.append(Spacer(1, 10))
    
    # Signature
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Dr. Sarah Johnson, MD", ParagraphStyle('sig', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold', textColor=colors.HexColor('#1f2937'))))
    story.append(Paragraph("General Physician | License No: CA-12345", note_style))
    story.append(Paragraph("City General Hospital, San Diego, CA", note_style))
    story.append(Paragraph("This report is confidential and intended for the named patient only.", note_style))
    
    doc.build(story)
    print("✅ blood_work.pdf generated")

# ============================================================
# REPORT 2: DISCHARGE SUMMARY
# ============================================================
def generate_discharge_summary():
    doc = SimpleDocTemplate(
        "app/data/sample_reports/discharge_summary.pdf",
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    
    styles = getSampleStyleSheet()
    story = []
    
    header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=20, fontName='Helvetica-Bold', textColor=colors.HexColor('#1e40af'), alignment=TA_CENTER, spaceAfter=4)
    sub_header_style = ParagraphStyle('SubHeader', parent=styles['Normal'], fontSize=11, fontName='Helvetica', textColor=colors.HexColor('#6b7280'), alignment=TA_CENTER, spaceAfter=2)
    section_style = ParagraphStyle('Section', parent=styles['Normal'], fontSize=12, fontName='Helvetica-Bold', textColor=colors.HexColor('#2563eb'), spaceBefore=12, spaceAfter=6)
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=10, fontName='Helvetica', textColor=colors.HexColor('#374151'), spaceAfter=4)
    note_style = ParagraphStyle('Note', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Oblique', textColor=colors.HexColor('#6b7280'), spaceAfter=4)
    
    # Hospital Header
    story.append(Paragraph("City General Hospital", header_style))
    story.append(Paragraph("123 Medical Drive, San Diego, CA 92101", sub_header_style))
    story.append(Paragraph("Phone: (619) 555-0100 | Email: records@citygeneralhospital.com", sub_header_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2563eb')))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("DISCHARGE SUMMARY", header_style))
    story.append(Spacer(1, 10))
    
    # Patient Info
    patient_data = [
        ["Patient Name:", "John Smith", "Discharge ID:", "DS-2024-1210"],
        ["Age:", "45 years", "Admission Date:", "December 5, 2024"],
        ["Gender:", "Male", "Discharge Date:", "December 10, 2024"],
        ["Patient ID:", "patient_1", "Ward:", "General Medicine - Ward 3"],
        ["Attending Doctor:", "Dr. Sarah Johnson", "Total Stay:", "5 Days"],
    ]
    
    patient_table = Table(patient_data, colWidths=[130, 170, 120, 180])
    patient_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#374151')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    
    story.append(patient_table)
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
    
    # Diagnosis
    story.append(Paragraph("1. Primary Diagnosis", section_style))
    story.append(Paragraph("Hypertension Stage 1 with Hyperlipidemia", ParagraphStyle('bold', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold', textColor=colors.HexColor('#dc2626'), spaceAfter=4)))
    story.append(Paragraph("Secondary Diagnosis: Mild anxiety disorder", normal_style))
    
    # Reason for Admission
    story.append(Paragraph("2. Reason for Admission", section_style))
    story.append(Paragraph("Patient presented with persistent headaches, dizziness, and elevated blood pressure readings (160/100 mmHg) for 3 consecutive days. Patient also reported chest tightness and mild shortness of breath on exertion.", normal_style))
    
    # Treatment
    story.append(Paragraph("3. Treatment During Hospital Stay", section_style))
    story.append(Paragraph("• Day 1-2: IV fluids, continuous BP monitoring, ECG performed", normal_style))
    story.append(Paragraph("• Day 2: Started on oral antihypertensive medication (Lisinopril 10mg)", normal_style))
    story.append(Paragraph("• Day 3: BP stabilized at 130/85 mmHg. Blood work completed.", normal_style))
    story.append(Paragraph("• Day 4: Cardiology consultation done. Echo-cardiogram performed — normal.", normal_style))
    story.append(Paragraph("• Day 5: BP stable at 125/82 mmHg. Patient ambulatory. Cleared for discharge.", normal_style))
    
    # Medications on Discharge
    story.append(Paragraph("4. Medications on Discharge", section_style))
    
    med_data = [
        ["Medication", "Dosage", "Frequency", "Duration"],
        ["Lisinopril", "10mg", "Once daily (morning)", "90 days"],
        ["Aspirin", "81mg", "Once daily (with food)", "90 days"],
        ["Atorvastatin", "20mg", "Once daily (night)", "90 days"],
        ["Vitamin D3", "2000 IU", "Once daily", "90 days"],
    ]
    
    med_table = Table(med_data, colWidths=[160, 80, 160, 100])
    med_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
    ]))
    
    story.append(med_table)
    
    # Doctor Instructions
    story.append(Paragraph("5. Doctor's Instructions", section_style))
    story.append(Paragraph("• Monitor blood pressure daily at home. Target BP: below 130/80 mmHg.", normal_style))
    story.append(Paragraph("• Follow a low-sodium diet. Limit salt intake to less than 2g per day.", normal_style))
    story.append(Paragraph("• Avoid alcohol and smoking completely.", normal_style))
    story.append(Paragraph("• Light exercise recommended: 30 minutes walking daily.", normal_style))
    story.append(Paragraph("• Avoid stressful situations. Practice deep breathing or meditation.", normal_style))
    story.append(Paragraph("• Return to ER immediately if BP exceeds 160/100 mmHg or chest pain occurs.", normal_style))
    
    # Follow Up
    story.append(Paragraph("6. Follow-Up Appointment", section_style))
    
    followup_data = [
        ["Doctor", "Specialty", "Date", "Time"],
        ["Dr. Sarah Johnson", "General Medicine", "December 24, 2024", "10:00 AM"],
        ["Dr. Mark Wilson", "Cardiology", "January 5, 2025", "2:00 PM"],
    ]
    
    followup_table = Table(followup_data, colWidths=[160, 120, 140, 80])
    followup_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
        ('ALIGN', (2,0), (-1,-1), 'CENTER'),
    ]))
    
    story.append(followup_table)
    story.append(Spacer(1, 10))
    
    # Signature
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Dr. Sarah Johnson, MD", ParagraphStyle('sig', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold', textColor=colors.HexColor('#1f2937'))))
    story.append(Paragraph("General Physician | License No: CA-12345", note_style))
    story.append(Paragraph("City General Hospital, San Diego, CA", note_style))
    story.append(Paragraph("This document is confidential and intended for the named patient only.", note_style))
    
    doc.build(story)
    print("✅ discharge_summary.pdf generated")

# ============================================================
# REPORT 3: PRESCRIPTION
# ============================================================
def generate_prescription():
    doc = SimpleDocTemplate(
        "app/data/sample_reports/prescription.pdf",
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    
    styles = getSampleStyleSheet()
    story = []
    
    header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=20, fontName='Helvetica-Bold', textColor=colors.HexColor('#1e40af'), alignment=TA_CENTER, spaceAfter=4)
    sub_header_style = ParagraphStyle('SubHeader', parent=styles['Normal'], fontSize=11, fontName='Helvetica', textColor=colors.HexColor('#6b7280'), alignment=TA_CENTER, spaceAfter=2)
    section_style = ParagraphStyle('Section', parent=styles['Normal'], fontSize=12, fontName='Helvetica-Bold', textColor=colors.HexColor('#2563eb'), spaceBefore=12, spaceAfter=6)
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=10, fontName='Helvetica', textColor=colors.HexColor('#374151'), spaceAfter=4)
    note_style = ParagraphStyle('Note', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Oblique', textColor=colors.HexColor('#6b7280'), spaceAfter=4)
    
    # Hospital Header
    story.append(Paragraph("City General Hospital", header_style))
    story.append(Paragraph("123 Medical Drive, San Diego, CA 92101", sub_header_style))
    story.append(Paragraph("Phone: (619) 555-0100 | Email: pharmacy@citygeneralhospital.com", sub_header_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2563eb')))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("MEDICAL PRESCRIPTION", header_style))
    story.append(Spacer(1, 10))
    
    # Patient + Doctor Info
    info_data = [
        ["PATIENT DETAILS", "", "DOCTOR DETAILS", ""],
        ["Name:", "John Smith", "Doctor:", "Dr. Sarah Johnson"],
        ["Age:", "45 years", "Specialty:", "General Medicine"],
        ["Patient ID:", "patient_1", "License No:", "CA-12345"],
        ["Date:", "December 10, 2024", "Contact:", "(619) 555-0101"],
    ]
    
    info_table = Table(info_data, colWidths=[100, 170, 100, 170])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#dbeafe')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('SPAN', (0,0), (1,0)),
        ('SPAN', (2,0), (3,0)),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
    
    # Diagnosis
    story.append(Paragraph("Diagnosis", section_style))
    story.append(Paragraph("Hypertension Stage 1 | Hyperlipidemia | Vitamin D Deficiency", normal_style))
    
    # Medications
    story.append(Paragraph("Prescribed Medications", section_style))
    
    med_data = [
        ["#", "Medicine", "Dosage", "Frequency", "Duration", "Instructions"],
        ["1", "Lisinopril", "10mg", "Once daily\n(morning)", "90 days", "Take with water\non empty stomach"],
        ["2", "Aspirin", "81mg", "Once daily\n(morning)", "90 days", "Take with food\nto avoid stomach upset"],
        ["3", "Atorvastatin", "20mg", "Once daily\n(night)", "90 days", "Take at bedtime\nAvoid grapefruit juice"],
        ["4", "Vitamin D3", "2000 IU", "Once daily", "90 days", "Take with\nfatty meal"],
        ["5", "Metformin", "500mg", "Twice daily", "30 days", "Take with meals\nMonitor blood sugar"],
    ]
    
    med_table = Table(med_data, colWidths=[25, 100, 60, 80, 70, 140])
    med_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (2,0), (4,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    story.append(med_table)
    
    # Special Instructions
    story.append(Paragraph("Special Instructions", section_style))
    story.append(Paragraph("• Take all medications as prescribed. Do not skip doses.", normal_style))
    story.append(Paragraph("• Monitor blood pressure daily. Keep a log and bring it to your next appointment.", normal_style))
    story.append(Paragraph("• Follow a low-sodium, low-fat diet. Increase fruits and vegetables.", normal_style))
    story.append(Paragraph("• Exercise: 30 minutes of brisk walking daily.", normal_style))
    story.append(Paragraph("• Avoid alcohol, smoking, and excessive caffeine.", normal_style))
    story.append(Paragraph("• If you experience dizziness, severe headache, or chest pain, seek emergency care immediately.", normal_style))
    story.append(Paragraph("• Do not stop medications without consulting your doctor.", normal_style))
    
    # Refills
    story.append(Paragraph("Refill Information", section_style))
    story.append(Paragraph("Refills allowed: 2 refills within 6 months of prescription date.", normal_style))
    story.append(Paragraph("Next Review: December 24, 2024 at 10:00 AM with Dr. Sarah Johnson", normal_style))
    story.append(Spacer(1, 10))
    
    # Signature
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
    story.append(Spacer(1, 8))
    
    sig_data = [
        ["", ""],
        ["_______________________", ""],
        ["Dr. Sarah Johnson, MD", ""],
        ["General Physician | CA-12345", ""],
        ["City General Hospital", ""],
    ]
    
    sig_table = Table(sig_data, colWidths=[300, 200])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTNAME', (0,2), (0,2), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#374151')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ]))
    
    story.append(sig_table)
    story.append(Spacer(1, 6))
    story.append(Paragraph("⚠️ This prescription is valid for 6 months from the date of issue.", note_style))
    story.append(Paragraph("This document is confidential and intended for the named patient only.", note_style))
    
    doc.build(story)
    print("✅ prescription.pdf generated")

# ============================================================
# RUN ALL
# ============================================================
if __name__ == "__main__":
    print("Generating sample medical reports...")
    generate_blood_work()
    generate_discharge_summary()
    generate_prescription()
    print("\n✅ All reports generated in app/data/sample_reports/")