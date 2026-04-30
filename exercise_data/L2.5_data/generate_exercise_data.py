import os
import json
import random
import glob
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_JUSTIFY

# Directory Setup - Saving in the same folder as this script
DATA_DIR = "."

# Custom Styles
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='PremiumTitle', parent=styles['Title'], fontSize=28, textColor=colors.HexColor("#1A237E"), spaceAfter=30, alignment=TA_CENTER))
styles.add(ParagraphStyle(name='LetterBody', parent=styles['Normal'], alignment=TA_JUSTIFY, leading=14))
styles.add(ParagraphStyle(name='FooterText', parent=styles['Italic'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER))

def cleanup_old_files():
    """Checks and deletes existing exercise files before generating fresh ones."""
    extensions = ['*.pdf', '*.json', '*.html', '*.csv', '*.db']
    print("🧹 Cleaning up old exercise data...")
    for ext in extensions:
        files = glob.glob(os.path.join(DATA_DIR, ext))
        for f in files:
            if os.path.basename(f) != "generate_exercise_data.py":
                try:
                    os.remove(f)
                    print(f"   Deleted: {os.path.basename(f)}")
                except Exception as e:
                    print(f"   Error deleting {f}: {e}")

def create_erp_db():
    """Generates a professional SQLite database simulating a multi-department ERP system."""
    db_path = os.path.join(DATA_DIR, "erp_simulation.db")
    print(f"🗄️ Generating ERP Database: {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. ADMIN - Employee Management
    cursor.execute('''CREATE TABLE admin_employees (
        id INTEGER PRIMARY KEY,
        name TEXT,
        dept TEXT,
        role TEXT,
        salary REAL,
        joined_date TEXT
    )''')
    depts = ["Sales", "Marketing", "Admin", "R&D", "Factory"]
    roles = ["Manager", "Engineer", "Analyst", "Lead", "Associate"]
    for i in range(1, 51):
        cursor.execute("INSERT INTO admin_employees VALUES (?, ?, ?, ?, ?, ?)",
                       (i, f"Employee_{i}", random.choice(depts), random.choice(roles), 
                        random.randint(40000, 150000), "2024-01-01"))

    # 2. SALES - Order Tracking
    cursor.execute('''CREATE TABLE sales_orders (
        order_id INTEGER PRIMARY KEY,
        customer_name TEXT,
        product_id TEXT,
        amount REAL,
        status TEXT,
        order_date TEXT
    )''')
    for i in range(1001, 1201):
        cursor.execute("INSERT INTO sales_orders VALUES (?, ?, ?, ?, ?, ?)",
                       (i, f"Client_{random.randint(1, 20)}", f"HW-{random.randint(100, 999)}",
                        random.uniform(500, 50000), random.choice(["Shipped", "Pending", "Cancelled"]), "2026-04-15"))

    # 3. MARKETING - Campaigns & Leads
    cursor.execute('''CREATE TABLE marketing_campaigns (
        id INTEGER PRIMARY KEY,
        campaign_name TEXT,
        budget REAL,
        leads_generated INTEGER,
        conversion_rate REAL
    )''')
    campaigns = ["Social Blast", "Search Dominance", "Email Nurture", "Trade Show 2026", "Webinar Series"]
    for idx, name in enumerate(campaigns):
        cursor.execute("INSERT INTO marketing_campaigns VALUES (?, ?, ?, ?, ?)",
                       (idx+1, name, random.randint(5000, 20000), random.randint(100, 500), random.uniform(0.01, 0.15)))

    # 4. R&D - Project Milestones
    cursor.execute('''CREATE TABLE rnd_projects (
        project_id INTEGER PRIMARY KEY,
        name TEXT,
        budget_allocated REAL,
        progress_pct INTEGER,
        status TEXT
    )''')
    projects = ["Project Phoenix", "Quantum Engine", "Neural Interface", "Sustainable Factory", "Edge AI Hub"]
    for idx, name in enumerate(projects):
        cursor.execute("INSERT INTO rnd_projects VALUES (?, ?, ?, ?, ?)",
                       (idx+1, name, random.randint(100000, 500000), random.randint(0, 100), random.choice(["Active", "On Hold", "Completed"])))

    # 5. FACTORY - Production & Maintenance
    cursor.execute('''CREATE TABLE factory_production (
        machine_id TEXT PRIMARY KEY,
        output_units INTEGER,
        last_maintenance TEXT,
        downtime_hours REAL,
        efficiency_pct REAL
    )''')
    for i in range(1, 11):
        cursor.execute("INSERT INTO factory_production VALUES (?, ?, ?, ?, ?)",
                       (f"MAC-{i:03d}", random.randint(5000, 20000), "2026-03-20", random.uniform(0, 48), random.uniform(85, 99)))

    conn.commit()
    conn.close()
    print("   Success: ERP database created with 5 department tables.")

def create_premium_logo(color=colors.HexColor("#1A237E")):
    d = Drawing(120, 50)
    d.add(Rect(0, 0, 40, 40, fillColor=color, strokeColor=None))
    d.add(Rect(10, 10, 20, 20, fillColor=colors.white, strokeColor=None))
    d.add(String(50, 20, "TECH-CORP", fontSize=14, fontName="Helvetica-Bold", fillColor=color))
    d.add(String(50, 8, "ELITE SOLUTIONS", fontSize=7, fontName="Helvetica", fillColor=colors.grey))
    return d

def create_report():
    path = os.path.join(DATA_DIR, "sample_report.pdf")
    doc = SimpleDocTemplate(path, pagesize=letter, topMargin=72, bottomMargin=72)
    story = []

    # Randomized stats for interest
    acc_val = round(random.uniform(98.5, 99.9), 2)
    eff_val = random.randint(35, 55)

    # --- Page 1: Premium Cover ---
    story.append(Spacer(1, 1.5*inch))
    story.append(create_premium_logo())
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("2026 ANNUAL STRATEGIC ANALYSIS", styles['PremiumTitle']))
    story.append(Paragraph("A COMPREHENSIVE OVERVIEW OF GLOBAL AUTOMATION INITIATIVES", styles['Heading3']))
    story.append(Spacer(1, 2*inch))
    
    line = Drawing(450, 2)
    line.add(Line(0, 0, 450, 0, strokeColor=colors.HexColor("#1A237E"), strokeWidth=2))
    story.append(line)
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"DOCUMENT ID: TC-AR-2026-{random.randint(1000, 9999)}", styles['Normal']))
    story.append(Paragraph("CLASSIFICATION: TOP SECRET / INTERNAL ONLY", styles['Normal']))
    story.append(PageBreak())

    # --- Page 2: Letter of Transmittal ---
    story.append(Paragraph("Letter of Transmittal", styles['Heading1']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("To: The Board of Directors, Tech-Corp Global", styles['Normal']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "Dear Board Members,<br/><br/>"
        "It is my privilege to present the Annual Strategic Analysis for the fiscal year 2026. "
        "This document details our unprecedented shift towards autonomous operations and the "
        "successful integration of decentralized inference networks into our core infrastructure.<br/><br/>"
        "Respectfully,<br/><br/><b>Dr. Aris Thorne</b><br/>Chief Automation Officer", styles['LetterBody']
    ))
    story.append(PageBreak())

    # --- Page 3: Executive Summary ---
    story.append(Paragraph("Executive Summary", styles['Heading1']))
    summary_text = (
        f"The fiscal year 2026 marked a pivotal transition for Tech-Corp. By leveraging advanced "
        f"Python-based automation and localized large language models, we have transformed our "
        f"back-office operations from a cost center into a primary driver of efficiency. <br/><br/>"
        f"Our proprietary 'L2.5 Framework' has enabled the extraction of structured intelligence "
        f"from over 1.4 million unstructured PDF documents with a verified accuracy of {acc_val}%. "
        f"This achievement has directly contributed to a {eff_val}% increase in our bottom-line margins."
    )
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 30))

    # Pie Chart
    d = Drawing(400, 200)
    pc = Pie()
    pc.x = 150; pc.y = 50; pc.width = 100; pc.height = 100
    pc.data = [eff_val, 100-eff_val-15, 15]
    pc.labels = ['Automated', 'Human-in-the-loop', 'Manual Legacy']
    pc.sideLabels = True
    pc.slices[0].fillColor = colors.HexColor("#1A237E")
    pc.slices[1].fillColor = colors.HexColor("#3949AB")
    pc.slices[2].fillColor = colors.HexColor("#C5CAE9")
    d.add(pc)
    story.append(d)
    story.append(Paragraph(f"<center><i>Chart 1.1: Global Operational Efficiency Distribution (Target: {eff_val}%)</i></center>", styles['Italic']))
    story.append(PageBreak())

    # --- Page 4: Growth Trends ---
    story.append(Paragraph("Technical Growth Trends", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    # Line Chart
    lc_drawing = Drawing(400, 200)
    lc = HorizontalLineChart()
    lc.x = 30; lc.y = 30; lc.height = 125; lc.width = 300
    trend = [10]
    for _ in range(5):
        trend.append(trend[-1] + random.randint(10, 20))
    lc.data = [tuple(trend)]
    lc.categoryAxis.categoryNames = ['Q1', 'Q2', 'Q3', 'Q4', 'Q1-26', 'Q2-26']
    lc.lines[0].strokeColor = colors.HexColor("#1A237E")
    lc_drawing.add(lc)
    story.append(lc_drawing)
    story.append(Paragraph(f"<center><i>Chart 1.2: Accuracy Progression (Final Yield: {trend[-1]}%)</i></center>", styles['Italic']))
    
    doc.build(story)
    print(f"Created elaborate report: {path}")

def create_detailed_invoice(name, inv_num, date, items):
    path = os.path.join(DATA_DIR, name)
    doc = SimpleDocTemplate(path, pagesize=letter, topMargin=50, bottomMargin=50, leftMargin=50, rightMargin=50)
    story = []

    # Header section
    header_data = [[create_premium_logo(), f"OFFICIAL INVOICE\nRef: {inv_num}\nDate: {date}"]]
    header_table = Table(header_data, colWidths=[3.5*inch, 2.5*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor("#1A237E")),
        ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 40))

    # Client Info
    story.append(Paragraph("<b>BILLED TO:</b>", styles['Normal']))
    story.append(Paragraph("<b>Enterprise Solutions Group</b><br/>Global Logistics Hub, Bld 4<br/>Dubai Design District, UAE", styles['Normal']))
    story.append(Spacer(1, 30))

    # Line items table
    data = [["Service Description", "Unit Price", "Qty", "Total"]]
    subtotal = 0
    for item, base_price, base_qty in items:
        price = round(base_price * random.uniform(0.95, 1.05), 2)
        qty = base_qty + random.randint(-1, 2)
        if qty < 1: qty = 1
        total = price * qty
        data.append([item, f"${price:,.2f}", str(qty), f"${total:,.2f}"])
        subtotal += total
    
    tax = subtotal * 0.08
    grand_total = subtotal + tax

    data.append(["", "", "Subtotal", f"${subtotal:,.2f}"])
    data.append(["", "", "Tax (8%)", f"${tax:,.2f}"])
    data.append(["", "", "Grand Total", f"${grand_total:,.2f}"])

    t = Table(data, colWidths=[3.2*inch, 0.9*inch, 0.7*inch, 1.2*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A237E")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (2, -1), (3, -1), 'Helvetica-Bold'), 
        ('FONTSIZE', (2, -1), (3, -1), 12),
        ('GRID', (0, 0), (-1, -4), 0.5, colors.lightgrey),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('LINEBELOW', (2, -2), (3, -2), 1, colors.black),
        ('LINEBELOW', (2, -1), (3, -1), 2, colors.HexColor("#1A237E")),
    ]))
    story.append(t)

    story.append(Spacer(1, 60))
    story.append(Paragraph("This is a computer-generated invoice. No signature required.", styles['FooterText']))
    
    doc.build(story)
    print(f"Created professional invoice: {path}")

def create_full_catalog():
    path = os.path.join(DATA_DIR, "product_catalog.pdf")
    doc = SimpleDocTemplate(path, pagesize=letter, topMargin=36, bottomMargin=36)
    story = []

    story.append(Paragraph("PRODUCT & SERVICES CATALOG 2026", styles['PremiumTitle']))
    story.append(Spacer(1, 12))
    
    catalog_items = [
        ["CATEGORY", "SKU ID", "PRODUCT SPECIFICATION", "LEAD TIME", "UNIT PRICE"],
        ["HARDWARE", "HW-X1", "Quantum Neural Processor (7nm)", "14 Days", f"${random.randint(12000, 13000):,.2f}"],
        ["HARDWARE", "HW-X2", "Bio-Metric Feedback Loop", "7 Days", f"${random.randint(2500, 3000):,.2f}"],
        ["", "HW-X3", "High-Density Storage Array", "21 Days", f"${random.randint(4800, 5500):,.2f}"],
        ["SOFTWARE", "SW-A1", "Autonomous Intelligence License", "Instant", f"${random.randint(24000, 26000):,.2f}"],
        ["SOFTWARE", "SW-A2", "Secure Edge OCR Module", "Instant", f"${random.randint(1200, 1400):,.2f}"],
        ["", "SW-A3", "Real-time API Access (Tier 1)", "Monthly", f"${random.randint(450, 550):,.2f}"],
        ["SERVICES", "SRV-01", "Enterprise AI Integration", "Consult", f"${random.randint(400, 500):,.2f}/hr"],
        ["SERVICES", "SRV-02", "Security Protocol Audit", "1 Week", f"${random.randint(14000, 16000):,.2f}"],
        ["", "SRV-03", "Custom LLM Fine-Tuning", "Variable", "Contact Us"],
        ["TRAINING", "TR-01", "Developer Certification Hub", "24/7", f"${random.randint(2000, 2300):,.2f}"]
    ]

    t = Table(catalog_items, repeatRows=1, colWidths=[1.1*inch, 0.8*inch, 2.5*inch, 1.1*inch, 1.1*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A237E")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'LEFT'), 
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
        ('BACKGROUND', (0, 1), (0, 3), colors.HexColor("#E8EAF6")),
        ('BACKGROUND', (0, 4), (0, 6), colors.HexColor("#E3F2FD")),
        ('BACKGROUND', (0, 7), (0, 9), colors.HexColor("#F1F8E9")),
    ]))
    story.append(t)
    
    story.append(Spacer(1, 40))
    story.append(Paragraph("© 2026 Tech-Corp Global. All prices are in USD and subject to local VAT.", styles['FooterText']))
    
    doc.build(story)
    print(f"Created professional catalog: {path}")

def create_extra_files():
    pwd_path = os.path.join(DATA_DIR, "passwords.json")
    with open(pwd_path, "w") as f:
        json.dump({
            "environment": "Production",
            "pdf_password": "ExerciseSecure2026",
            "admin_credentials": {
                "user": "sys_admin",
                "key": f"TECH_CORP_{random.randint(100, 999)}_X"
            },
            "api_config": {
                "endpoint": "https://api.tech-corp.com/v2",
                "timeout": random.randint(30, 60)
            }
        }, f, indent=4)
    print(f"Created passwords.json")

    html_path = os.path.join(DATA_DIR, "mock_news_site.html")
    with open(html_path, "w") as f:
        f.write("<html><body><h1>Tech-Corp Briefing Feed</h1></body></html>")
    print(f"Created professional mock_news_site.html")

if __name__ == "__main__":
    print("💎 Initializing Ultra-Premium Exercise Data Engine...")
    cleanup_old_files()
    print("\n🚀 Generating New Randomized Content...")
    create_report()
    create_detailed_invoice("invoice_01.pdf", f"INV-{random.randint(1000, 1100)}", "2026-04-01", [
        ("Cloud Infrastructure Strategy", 1500.00, 2),
        ("Localized LLM Fine-Tuning", 25000.00, 1),
        ("Support Retainer (Annual)", 12000.00, 1)
    ])
    create_detailed_invoice("invoice_02.pdf", f"INV-{random.randint(1101, 1200)}", "2026-04-15", [
        ("Quantum Cluster Setup", 45000.00, 1),
        ("Custom API Middleware", 85.00, 40),
        ("On-Site Security Training", 2000.00, 5)
    ])
    create_detailed_invoice("invoice_03.pdf", f"INV-{random.randint(1201, 1300)}", "2026-04-30", [
        ("Full Stack Audit", 15000.00, 1),
        ("Documentation Generation Service", 50.00, 100)
    ])
    create_full_catalog()
    create_extra_files()
    
    # NEW: Create the ERP SQL Database
    create_erp_db()
    
    print("\n✨ All documents and ERP Database recreated!")
