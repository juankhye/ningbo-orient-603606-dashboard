"""
Generate the layman pre-read PDF for the Ningbo Orient dashboard.
Writes to: Ningbo-Orient-Pre-Read.pdf
"""
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, KeepTogether, HRFlowable, Flowable)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

# ---- Color palette (matches dashboard, optimized for print) ----
NAVY     = colors.HexColor("#0e1a30")
TEXT     = colors.HexColor("#1a2235")
CYAN     = colors.HexColor("#0073b3")        # darker than dashboard for print contrast
CYAN_LT  = colors.HexColor("#00a4d6")
COPPER   = colors.HexColor("#c25425")
MUTED    = colors.HexColor("#6a7691")
LIGHT_BG = colors.HexColor("#eef6fb")
SOFT_BG  = colors.HexColor("#f7f9fc")
BORDER   = colors.HexColor("#d6dee8")
GREEN    = colors.HexColor("#2b9968")
RED      = colors.HexColor("#c24a5f")
YELLOW   = colors.HexColor("#c79a1a")

# ---- Style sheet ----
def make_styles():
    S = {}
    S['cover_eyebrow'] = ParagraphStyle('ce', fontName='Helvetica-Bold', fontSize=10,
        textColor=CYAN, leading=14, spaceAfter=18, alignment=TA_CENTER,
        spaceBefore=4)
    S['cover_title'] = ParagraphStyle('ct', fontName='Helvetica-Bold', fontSize=42,
        textColor=NAVY, leading=46, alignment=TA_CENTER, spaceAfter=10)
    S['cover_subtitle'] = ParagraphStyle('cst', fontName='Helvetica', fontSize=18,
        textColor=CYAN, leading=24, alignment=TA_CENTER, spaceAfter=30)
    S['cover_lede'] = ParagraphStyle('cl', fontName='Helvetica', fontSize=12,
        textColor=TEXT, leading=18, alignment=TA_CENTER, spaceAfter=18,
        leftIndent=36, rightIndent=36)
    S['cover_meta'] = ParagraphStyle('cm', fontName='Helvetica', fontSize=10,
        textColor=MUTED, leading=14, alignment=TA_CENTER, spaceAfter=4)

    S['section'] = ParagraphStyle('sec', fontName='Helvetica-Bold', fontSize=22,
        textColor=NAVY, leading=28, spaceBefore=12, spaceAfter=14)
    S['section_num'] = ParagraphStyle('secn', fontName='Helvetica-Bold', fontSize=10,
        textColor=CYAN, leading=12, spaceAfter=4, letterSpacing=1.5)
    S['subsection'] = ParagraphStyle('sub', fontName='Helvetica-Bold', fontSize=14,
        textColor=NAVY, leading=20, spaceBefore=18, spaceAfter=8)
    S['body'] = ParagraphStyle('b', fontName='Helvetica', fontSize=11,
        textColor=TEXT, leading=17, spaceAfter=10, alignment=TA_LEFT)
    S['lede'] = ParagraphStyle('led', fontName='Helvetica', fontSize=13,
        textColor=TEXT, leading=20, spaceAfter=14, alignment=TA_LEFT)
    S['callout_body'] = ParagraphStyle('cob', fontName='Helvetica', fontSize=10.5,
        textColor=TEXT, leading=16, spaceAfter=0, alignment=TA_LEFT,
        leftIndent=12, rightIndent=12, spaceBefore=8, borderPadding=0)
    S['callout_label'] = ParagraphStyle('col', fontName='Helvetica-Bold', fontSize=9,
        textColor=CYAN, leading=12, spaceAfter=2, leftIndent=12, spaceBefore=10)
    S['bullet'] = ParagraphStyle('bul', fontName='Helvetica', fontSize=11,
        textColor=TEXT, leading=17, spaceAfter=6,
        leftIndent=22, bulletIndent=8, alignment=TA_LEFT)
    S['mini'] = ParagraphStyle('mi', fontName='Helvetica', fontSize=9,
        textColor=MUTED, leading=13, spaceAfter=4)
    S['tag'] = ParagraphStyle('tg', fontName='Helvetica-Bold', fontSize=8,
        textColor=CYAN, leading=10, spaceAfter=0, letterSpacing=1)
    S['kpi_num'] = ParagraphStyle('kn', fontName='Helvetica-Bold', fontSize=22,
        textColor=CYAN, leading=26, alignment=TA_CENTER)
    S['kpi_lbl'] = ParagraphStyle('kl', fontName='Helvetica', fontSize=8.5,
        textColor=MUTED, leading=12, alignment=TA_CENTER, spaceAfter=0)
    S['toc_line'] = ParagraphStyle('toc', fontName='Helvetica', fontSize=11,
        textColor=TEXT, leading=20, spaceAfter=2)
    return S

S = make_styles()

# ---- Custom flowables ----
class SectionHeader(Flowable):
    """Bold cyan accent bar + section number + title"""
    def __init__(self, number, title):
        Flowable.__init__(self)
        self.number = number
        self.title = title
        self.width = 6.5 * inch
        self.height = 0.85 * inch

    def draw(self):
        c = self.canv
        # Vertical accent bar
        c.setFillColor(CYAN)
        c.rect(0, 8, 4, self.height - 8, fill=1, stroke=0)
        # Number label
        c.setFillColor(CYAN)
        c.setFont('Helvetica-Bold', 9)
        c.drawString(14, self.height - 16, f"SECTION {self.number:02d}")
        # Title
        c.setFillColor(NAVY)
        c.setFont('Helvetica-Bold', 22)
        c.drawString(14, 12, self.title)

class Callout(Flowable):
    """Light-blue callout box with label + body"""
    def __init__(self, label, body, color=CYAN, bgcolor=LIGHT_BG):
        Flowable.__init__(self)
        self.label = label
        self.body = body
        self.color = color
        self.bgcolor = bgcolor
        self.width = 6.5 * inch
        # Estimate height (rough)
        lines = max(2, len(body) // 88 + 1)
        self.height = 30 + lines * 14

    def draw(self):
        c = self.canv
        # Background
        c.setFillColor(self.bgcolor)
        c.setStrokeColor(self.color)
        c.setLineWidth(0.6)
        c.roundRect(0, 0, self.width, self.height, 8, fill=1, stroke=1)
        # Left accent bar
        c.setFillColor(self.color)
        c.rect(0, 0, 3, self.height, fill=1, stroke=0)
        # Label
        c.setFillColor(self.color)
        c.setFont('Helvetica-Bold', 9)
        c.drawString(16, self.height - 16, self.label.upper())
        # Body text wrap
        from reportlab.lib.utils import simpleSplit
        c.setFillColor(TEXT)
        c.setFont('Helvetica', 10.5)
        max_w = self.width - 36
        lines = simpleSplit(self.body, 'Helvetica', 10.5, max_w)
        y = self.height - 32
        for line in lines:
            c.drawString(16, y, line)
            y -= 14

class Divider(Flowable):
    """Horizontal subtle line"""
    def __init__(self, width=6.5*inch, color=BORDER):
        Flowable.__init__(self)
        self.width = width
        self.height = 1
        self.color = color
    def draw(self):
        c = self.canv
        c.setStrokeColor(self.color)
        c.setLineWidth(0.5)
        c.line(0, 0, self.width, 0)

class KPIRow(Flowable):
    """Row of KPI numbers for cover page"""
    def __init__(self, items):
        Flowable.__init__(self)
        self.items = items  # list of (number, label) tuples
        self.width = 6.5 * inch
        self.height = 70

    def draw(self):
        c = self.canv
        n = len(self.items)
        cell_w = self.width / n
        # Background box
        c.setFillColor(SOFT_BG)
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.6)
        c.roundRect(0, 0, self.width, self.height, 10, fill=1, stroke=1)
        for i, (num, lbl) in enumerate(self.items):
            x = i * cell_w
            # divider
            if i > 0:
                c.setStrokeColor(BORDER)
                c.line(x, 10, x, self.height - 10)
            # Number
            c.setFillColor(CYAN)
            c.setFont('Helvetica-Bold', 18)
            c.drawCentredString(x + cell_w/2, self.height - 30, num)
            # Label
            c.setFillColor(MUTED)
            c.setFont('Helvetica', 8.5)
            from reportlab.lib.utils import simpleSplit
            lines = simpleSplit(lbl, 'Helvetica', 8.5, cell_w - 16)
            y = self.height - 46
            for line in lines[:2]:
                c.drawCentredString(x + cell_w/2, y, line)
                y -= 11

class CoverBackdrop(Flowable):
    """Decorative element under cover title"""
    def __init__(self, width=6.5*inch):
        Flowable.__init__(self)
        self.width = width
        self.height = 4
    def draw(self):
        c = self.canv
        # Gradient bar
        steps = 60
        for i in range(steps):
            t = i / steps
            r = int(0x00 + (0x00 - 0x00) * t)
            g = int(0x73 + (0xa4 - 0x73) * t)
            b = int(0xb3 + (0xd6 - 0xb3) * t)
            c.setFillColorRGB(r/255, g/255, b/255)
            seg_w = self.width / steps
            c.rect(i * seg_w, 0, seg_w + 0.5, self.height, fill=1, stroke=0)

# ---- Page header/footer ----
def add_page_chrome(canv, doc):
    """Header bar + page number on every non-cover page"""
    if doc.page == 1:
        return
    page_w, page_h = letter
    # Top header
    canv.setStrokeColor(BORDER)
    canv.setLineWidth(0.5)
    canv.line(0.75*inch, page_h - 0.55*inch, page_w - 0.75*inch, page_h - 0.55*inch)
    # Brand mark left
    canv.setFillColor(CYAN)
    canv.rect(0.75*inch, page_h - 0.5*inch, 9, 9, fill=1, stroke=0)
    canv.setFillColor(NAVY)
    canv.setFont('Helvetica-Bold', 9)
    canv.drawString(0.75*inch + 14, page_h - 0.48*inch, "Ningbo Orient (603606 CH)")
    canv.setFillColor(MUTED)
    canv.setFont('Helvetica', 8)
    canv.drawString(0.75*inch + 145, page_h - 0.48*inch, "·  Plain-English Pre-Read")
    # Page number right
    canv.setFillColor(MUTED)
    canv.setFont('Helvetica', 8)
    canv.drawRightString(page_w - 0.75*inch, page_h - 0.48*inch, f"Page {doc.page}")
    # Footer
    canv.setStrokeColor(BORDER)
    canv.line(0.75*inch, 0.55*inch, page_w - 0.75*inch, 0.55*inch)
    canv.setFillColor(MUTED)
    canv.setFont('Helvetica', 7.5)
    canv.drawString(0.75*inch, 0.4*inch, "Sources: AlphaSense · UBS · Morgan Stanley · Huatai · Guosheng · William O'Neil · Jefferies · Credit Suisse · Horizon Insights · company filings")
    canv.drawRightString(page_w - 0.75*inch, 0.4*inch, "Not investment advice")


# ---- Build the document ----
def build():
    out = "Ningbo-Orient-Pre-Read.pdf"
    doc = SimpleDocTemplate(out, pagesize=letter,
                            leftMargin=0.75*inch, rightMargin=0.75*inch,
                            topMargin=0.85*inch, bottomMargin=0.85*inch,
                            title="Ningbo Orient — Plain-English Pre-Read",
                            author="Research dashboard")
    story = []

    # ============ COVER PAGE ============
    story.append(Spacer(1, 1.3*inch))
    story.append(Paragraph("PRE-READ &nbsp;·&nbsp; SUBMARINE CABLES &nbsp;·&nbsp; CHINA A-SHARES", S['cover_eyebrow']))
    story.append(Paragraph("Ningbo Orient", S['cover_title']))
    story.append(Paragraph("Wires &amp; Cables Co. Ltd. &nbsp;<font color='#0073b3'>·</font>&nbsp; 603606 CH", S['cover_subtitle']))
    story.append(CoverBackdrop())
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(
        "Everything you need to know — in plain English — <i>before</i> you open the dashboard. "
        "What submarine cables actually are. Why this is one of the most defensible industrial businesses in the world. "
        "And why China's offshore-wind buildout has put Ningbo Orient at the centre of a multi-year boom.",
        S['cover_lede']))
    story.append(Spacer(1, 0.4*inch))

    story.append(KPIRow([
        ("RMB 42 bn", "Market cap"),
        ("33%", "China submarine cable share"),
        ("RMB 18.4 bn", "Order backlog (Apr 26)"),
        ("+26%", "FY25 net profit growth"),
        ("RMB 78", "UBS price target")
    ]))
    story.append(Spacer(1, 0.8*inch))
    story.append(Paragraph("Reading time: ~12 minutes", S['cover_meta']))
    story.append(Paragraph("Companion to the interactive dashboard at", S['cover_meta']))
    story.append(Paragraph("<font color='#0073b3'><b>juankhye.github.io/ningbo-orient-603606-dashboard</b></font>", S['cover_meta']))
    story.append(PageBreak())

    # ============ TABLE OF CONTENTS ============
    story.append(SectionHeader(0, "What's in this document"))
    story.append(Spacer(1, 18))
    toc_items = [
        ("1.", "The one-paragraph pitch", "If you only read one thing"),
        ("2.", "What is a submarine cable, really?", "The physical product, and the failure asymmetry that defines the industry"),
        ("3.", "Why this is a weirdly defensible business", "The five barriers that lock the market to three players"),
        ("4.", "What Ningbo Orient actually does", "Three business segments, one cash-cow product"),
        ("5.", "Why now? The two big tailwinds", "China's policy push and Europe's capacity crunch"),
        ("6.", "The numbers in plain English", "Revenue, margins, backlog, balance sheet, valuation"),
        ("7.", "What could break the story", "Three real risks worth tracking"),
        ("8.", "How to navigate the dashboard", "What each section covers"),
        ("9.", "Glossary", "Plain-English definitions of every jargon term"),
    ]
    for num, title, sub in toc_items:
        data = [[Paragraph(f"<b><font color='#0073b3'>{num}</font></b>", S['toc_line']),
                 Paragraph(f"<b>{title}</b><br/><font size='9' color='#6a7691'>{sub}</font>", S['toc_line'])]]
        t = Table(data, colWidths=[28, 5.8*inch])
        t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('LINEBELOW', (0,0), (-1,-1), 0.4, BORDER),
        ]))
        story.append(t)
    story.append(PageBreak())

    # ============ SECTION 1: THE PITCH ============
    story.append(SectionHeader(1, "The one-paragraph pitch"))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "Ningbo Orient is a Chinese industrial company that makes the giant electrical cables "
        "lying on the seafloor — the cables that carry electricity from offshore wind farms "
        "back to land. It is one of just three companies that dominate this business in China, "
        "and one of fewer than ten companies in the entire world that can manufacture the "
        "highest-voltage version of these cables. The world is now building offshore wind "
        "farms at the fastest rate in history: China alone plans to install 100 gigawatts of "
        "offshore wind by 2030 — roughly five times today's installed base. Every one of "
        "those wind farms needs Orient's cables to connect to the grid. The order book is "
        "full through 2027, the balance sheet is debt-free, and the stock trades at a "
        "discount to both its own history and its peers.", S['lede']))

    story.append(Callout(
        "Why this matters",
        "If you understand nothing else: this is an industrial business that economically behaves "
        "more like defence contracting than like a normal manufacturer. The customer cares about "
        "reliability above price. New competitors take a decade to break in. Existing players "
        "defend their share fiercely. That is what makes Orient interesting — not the topline growth alone, "
        "but the structural reasons that growth flows through to durable profits.",
        CYAN, LIGHT_BG))

    story.append(Spacer(1, 20))
    story.append(Paragraph("In five sentences", S['subsection']))
    bullets = [
        ("Structural duopoly with a moat dug by physics", "Cables fail catastrophically when wrong, so developers stick to a handful of qualified suppliers. China's top-3 control 87% of the market."),
        ("Order book locks in revenue through 2027", "RMB 18.4 billion of signed contracts — roughly 1.7 years of trailing revenue, weighted toward high-margin 500kV product."),
        ("China policy mandates the demand", "15th Five-Year Plan targets 100GW of installed offshore wind by 2030, implying ~10GW per year vs 5-7GW in the prior plan period."),
        ("Europe is the next leg, validated by delivery", "Orient delivered the UK's Inch Cape project in 2025 — proving Chinese cable meets European specs at 10% lower price."),
        ("Cheap on its own growth and vs. peers", "Trades at 18x 2027 earnings on 25% earnings growth, below the peer average and below its own 27x historical multiple."),
    ]
    for i, (head, body) in enumerate(bullets, 1):
        story.append(Paragraph(f"<font color='#0073b3'><b>{i}.</b></font>  <b>{head}.</b>  <font color='#1a2235'>{body}</font>", S['body']))
    story.append(PageBreak())

    # ============ SECTION 2: SUBMARINE CABLE 101 ============
    story.append(SectionHeader(2, "What is a submarine cable, really?"))

    story.append(Paragraph(
        "Picture a thick steel-wrapped rope, about as wide as your forearm, weighing 100 tonnes "
        "per kilometre, lying on the seabed and stretching as long as 200 kilometres. Inside that "
        "rope: three copper conductors carrying enough electricity to power a million homes, "
        "wrapped in plastic insulation, wrapped in lead to keep seawater out, wrapped in steel "
        "wires to survive being dragged by anchors and fishing trawlers.", S['body']))

    story.append(Paragraph("That is a submarine cable.", S['body']))

    story.append(Paragraph(
        "When you build a wind farm in the ocean, the cable is what carries the electricity "
        "those turbines generate back to a substation on shore. Without the cable, the entire "
        "wind farm is just an expensive ornament spinning uselessly in the water.", S['body']))

    story.append(Paragraph("Why this matters", S['subsection']))

    story.append(Paragraph(
        "Submarine cables look boring. They are not. A single 500-kilovolt HVDC submarine cable "
        "can cost €5–10 million <i>per kilometre</i>. A typical offshore wind farm needs 50–200 "
        "kilometres of them. That puts cable spending into the hundreds of millions of dollars "
        "per project — and submarine cables represent 8–13% of total offshore wind project cost, "
        "comparable to the cost of the turbines themselves.", S['body']))

    story.append(Paragraph("Now the kicker", S['subsection']))

    story.append(Paragraph(
        "Cables fail. Cables fail <i>catastrophically</i>. When a cable fails, the entire wind "
        "farm — which might have cost a billion dollars to build — goes offline. Repairs require "
        "specialised ships that are in short supply globally. A single cable failure can shut "
        "down a wind farm for six months.", S['body']))

    story.append(Callout(
        "The single most important number in this industry",
        "83% of all insurance claims in offshore wind trace back to cable failures. That one statistic "
        "explains everything that follows: why customers do not shop on price, why suppliers need "
        "track records before they get qualified, why banks demand pre-approved vendors, and why "
        "the global market is locked up by fewer than ten companies.",
        COPPER, colors.HexColor("#fdf1e8")))

    story.append(PageBreak())

    # ============ SECTION 3: THE MOAT ============
    story.append(SectionHeader(3, "Why this is a weirdly defensible business"))

    story.append(Paragraph(
        "If 83% of your project's insurance risk lives in a single component, you do not choose "
        "that component based on price. You choose it based on track record. You choose suppliers "
        "your bank trusts. You choose suppliers your insurer trusts. You choose suppliers your "
        "grid regulator has pre-approved.", S['body']))

    story.append(Paragraph(
        "This is why submarine cables are nothing like a normal industrial product. There are "
        "five reasons new competitors cannot break in:", S['body']))

    pillars = [
        ("Manufacturing is genuinely hard.",
         "Making a 500-kilovolt cable that survives 25 years underwater takes specialised chemical engineering "
         "(cross-linked polyethylene insulation), proprietary high-voltage testing equipment, and a manufacturing "
         "process that costs hundreds of millions of dollars to set up. Fewer than 10 companies on Earth can do it."),
        ("You need a deep-water port.",
         "Submarine cables are spooled onto cable-laying ships at the factory. Those ships are huge. They need "
         "deep-water access. There are only a handful of suitable ports in China, and getting permission to build a new "
         "one takes years — not months."),
        ("You need your own ships.",
         "Cable-laying vessels are scarce globally. If you don't own the ship, you can't deliver the project. Orient "
         "owns three of these ships, including an 18,000-tonne transport platform that ships completed cables straight to the UK."),
        ("You need to be on the &quot;approved supplier&quot; list.",
         "China's National Grid maintains a closed roster of just six companies that are approved to bid on high-voltage "
         "interconnection projects. Orient is one of those six. Banks won't finance a project that uses an unlisted supplier."),
        ("You need a track record.",
         "Even if you somehow built the manufacturing, the port, and the ships — wind farm developers won't risk their "
         "billion-dollar project on a supplier that's never delivered one before. New entrants need a customer willing to take "
         "a leap of faith on day one. That customer doesn't exist."),
    ]
    for i, (head, body) in enumerate(pillars, 1):
        story.append(Paragraph(
            f"<font color='#0073b3'><b>{i}.</b></font>  <b>{head}</b>  {body}", S['body']))

    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "<b>The result:</b> China's domestic submarine cable market is shared by three companies "
        "(Zhongtian 37%, Ningbo Orient 33%, Hengtong 17%) that together control 87% of the market. "
        "Globally the picture is similar — a tiny club of qualified suppliers.", S['body']))

    story.append(Callout(
        "An analogy",
        "This business is closer to defence contracting or commercial aviation (Boeing-Airbus) than to traditional "
        "industrial manufacturing. The customer cares about reliability above price. The barriers to entry are "
        "technological and regulatory rather than capital-only. Existing players defend their share fiercely.",
        CYAN, LIGHT_BG))

    story.append(PageBreak())

    # ============ SECTION 4: WHAT THEY DO ============
    story.append(SectionHeader(4, "What Ningbo Orient actually does"))

    story.append(Paragraph("The company sells three things:", S['body']))

    story.append(Paragraph("1. Submarine and high-voltage cables — the crown jewel", S['subsection']))
    story.append(Paragraph(
        "These are the multi-million-dollar cables described in Section 2. Voltage classes from "
        "35kV array cables (which connect turbines within a wind farm) through 220kV and 500kV "
        "export cables (which carry power back to shore) to ±525kV HVDC cables (for the longest "
        "distances). This segment is 50% of revenue and generates a 33% gross margin. It is where "
        "the moat lives, and where every story about this company has to start.", S['body']))

    story.append(Paragraph("2. Land cables — the workhorse", S['subsection']))
    story.append(Paragraph(
        "Medium- and low-voltage power and data cables used by utilities, telecoms, real estate, "
        "rail networks. This is a commodity business — many competitors, ~9% gross margin. Orient "
        "does it because it utilises manufacturing capacity and serves big state-owned customers, "
        "but nobody owns this stock for the land-cable business.", S['body']))

    story.append(Paragraph("3. Marine engineering services — the differentiator", S['subsection']))
    story.append(Paragraph(
        "This is the team that designs the cable route, lays the cable at sea, joints the cables "
        "together, tests them, and provides ongoing maintenance. Only ~7% of revenue, but it is "
        "the reason customers pick Orient over a pure cable maker. Increasingly, customers buy a "
        "&quot;turnkey&quot; package — cable plus installation plus maintenance — rather than just the "
        "cable. Orient is one of the few companies that can offer the whole package.", S['body']))

    story.append(Callout(
        "Mental model",
        "Orient is not a cable manufacturer competing on price. It is an infrastructure provider competing on "
        "reliability. It just happens that the infrastructure is shaped like a cable.",
        CYAN, LIGHT_BG))

    story.append(PageBreak())

    # ============ SECTION 5: TAILWINDS ============
    story.append(SectionHeader(5, "Why now? The two big tailwinds"))

    story.append(Paragraph(
        "Two megatrends are pushing demand for submarine cables harder than at any moment in "
        "history. Both run for at least five years.", S['body']))

    story.append(Paragraph("Tailwind 1 — China's 15th Five-Year Plan", S['subsection']))
    story.append(Paragraph(
        "China's central government has just published its 2026–2030 plan, with a target of 100 "
        "gigawatts of cumulative offshore wind capacity by 2030. Roughly 49 GW is installed today. "
        "To hit the target, China needs to install around 10 GW per year for five years. That's a "
        "39% step-up from the prior plan period. The pipeline already supports it — over 50 GW of "
        "projects have received initial approval, and 8.4 GW received final approval in 2025 alone.", S['body']))

    story.append(Paragraph(
        "Translation: a structural, government-backed demand tailwind running through 2030. "
        "Submarine cable suppliers can plan production years in advance because the demand is "
        "locked in by policy, not market sentiment.", S['body']))

    story.append(Paragraph("Tailwind 2 — Europe's capacity crunch", S['subsection']))
    story.append(Paragraph(
        "Here it gets interesting. Europe is also accelerating offshore wind aggressively — the "
        "Hamburg Declaration targets 100 GW in the North Sea by 2050; the UK's AR7 auction "
        "allocated 8.4 GW; France ran a record 10 GW tender. But European cable manufacturers "
        "(Prysmian, Nexans, NKT) are sold out through 2027–2028. They cannot add capacity quickly "
        "enough.", S['body']))

    story.append(Paragraph(
        "Meanwhile, Chinese suppliers including Orient have spare capacity, sell at ~10% below "
        "European prices (even after shipping costs), and now have a track record: Orient "
        "delivered cable for the UK's Inch Cape project in 2025, proving it can meet European "
        "technical standards.", S['body']))

    story.append(Callout(
        "Translation",
        "Europe has to buy Chinese cable for the next few years whether it wants to or not. The only question is "
        "how much before geopolitical concerns (the UK recently blocked another Chinese wind company on national-security "
        "grounds) start to kick in. For Orient, this means overseas revenue grows from 11.6% of total in 2025 to "
        "15–20% by 2030 — and at higher margins than domestic.",
        CYAN, LIGHT_BG))

    story.append(PageBreak())

    # ============ SECTION 6: THE NUMBERS ============
    story.append(SectionHeader(6, "The numbers in plain English"))

    facts = [
        ("Revenue (the top line)",
         "RMB 10.8 billion in 2025. UBS forecasts this grows to RMB 28 billion by 2030 — a 21% annual growth rate "
         "sustained over five years. That kind of growth is rare for an industrial company."),
        ("Gross margin (how much they keep per dollar of revenue)",
         "22% in 2025, projected to expand to 26% by 2030. The expansion comes from mix shift: more revenue from "
         "high-margin 500kV submarine cable, less from low-margin land cable."),
        ("Net profit (the bottom line)",
         "RMB 1.27 billion in 2025, up 26% year-on-year. Q1 2026 was even better — up 32% year-on-year. The trend is real."),
        ("Order book (the visibility)",
         "RMB 18.4 billion as of April 2026 — roughly 1.7 years of revenue already committed. Heavily weighted toward "
         "high-margin submarine and HV cable. This is not a &quot;hope it sells&quot; story; customers have already paid deposits."),
        ("Balance sheet (the resilience)",
         "Net cash position of RMB 2.2 billion. Debt-to-equity just 9.8%. This company can fund its expansion plans "
         "entirely from internal cash flow — no need to dilute shareholders or take on risky debt."),
        ("Valuation (what it costs to own)",
         "Trades at roughly 22.6× next year's earnings and 18× the year after's. For a company growing earnings ~25% "
         "per year, this is cheap. Peer companies trade at 23–27×. The stock's own historical average is 27×. So you're "
         "paying below average for above-average growth."),
    ]
    for head, body in facts:
        story.append(Paragraph(f"<b>{head}.</b>  {body}", S['body']))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Analyst target prices", S['subsection']))

    target_data = [
        ['Broker', 'Rating', 'Price target (RMB)', 'Upside'],
        ['UBS', 'Buy', '78.00', '+28%'],
        ['Morgan Stanley', 'Overweight', '69.63', '+14%'],
        ['Huatai', 'Overweight', '68.38', '+12%'],
        ['Credit Suisse', 'Outperform', '69.50', '+14%'],
    ]
    t = Table(target_data, colWidths=[1.7*inch, 1.4*inch, 1.6*inch, 1.4*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), CYAN),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('FONTSIZE', (0,1), (-1,-1), 10),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('TEXTCOLOR', (0,1), (-1,-1), TEXT),
        ('TEXTCOLOR', (-1,1), (-1,-1), GREEN),
        ('FONTNAME', (-1,1), (-1,-1), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [SOFT_BG, colors.white]),
        ('GRID', (0,0), (-1,-1), 0.4, BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(t)

    story.append(Spacer(1, 8))
    story.append(Paragraph("Consensus is bullish, with target prices about 14–28% above where the stock trades today.", S['mini']))

    story.append(PageBreak())

    # ============ SECTION 7: RISKS ============
    story.append(SectionHeader(7, "What could break the story"))

    story.append(Paragraph(
        "Every investment thesis has things that could kill it. Three risks are worth watching "
        "closely. Several smaller risks are real but secondary.", S['body']))

    story.append(Paragraph("Risk 1 — Copper", S['subsection']))
    story.append(Paragraph(
        "Submarine cables are basically copper conductors with insulation around them. Copper is "
        "40–50% of the raw-material cost. If copper prices spike 30% and Orient can't pass that "
        "through to customers, margins compress hard. The company hedges 100% of its submarine "
        "cable orders, which helps. But this is the single biggest input-cost risk.", S['body']))

    story.append(Paragraph("Risk 2 — Project delays", S['subsection']))
    story.append(Paragraph(
        "Offshore wind installation depends on weather, vessel availability, sea-use permits, "
        "military airspace clearance, and port logistics. Any of these can delay deliveries. "
        "When they do, Orient's revenue gets lumpy: Q2 2025 saw a 50% profit drop because Q1 "
        "deliveries pushed into Q3. This is the kind of quarterly volatility that scares "
        "short-term investors but doesn't change the long-term thesis.", S['body']))

    story.append(Paragraph("Risk 3 — A European ban", S['subsection']))
    story.append(Paragraph(
        "The UK government recently blocked a Chinese wind turbine maker (Mingyang) from "
        "building a factory in Scotland, citing national security. Submarine cables are arguably "
        "more sensitive infrastructure than turbines. If the UK or EU were to impose a similar "
        "ban on Chinese subsea cable imports, the 15–20% overseas revenue target would compress. "
        "The base case treats this as low-probability, but it is a real tail risk.", S['body']))

    story.append(Paragraph("Lesser risks worth knowing about", S['subsection']))
    smaller_risks = [
        "Capacity expansion by competitors Zhongtian and Hengtong could compress industry prices in a post-subsidy era.",
        "&quot;Sea-use&quot; bottlenecks (military airspace, port logistics, vessel availability) could cap installations below plan targets.",
        "Floating offshore wind technology could disappoint on timing, deferring the dynamic-cable opportunity.",
        "EU local-content rules could erode the 10% Chinese price advantage even without an outright ban.",
    ]
    for r in smaller_risks:
        story.append(Paragraph(f"<font color='#c25425'>•</font>  {r}", S['body']))

    story.append(PageBreak())

    # ============ SECTION 8: DASHBOARD GUIDE ============
    story.append(SectionHeader(8, "How to navigate the dashboard"))

    story.append(Paragraph(
        "The dashboard is structured top to bottom for reading in order. Here is what each "
        "section covers and the minimum you need from each.", S['body']))

    nav_items = [
        ("Hero / KPIs", "Quick at-a-glance numbers. Skim and move on."),
        ("Thesis", "Six bullet points distilling why this stock works. Start here."),
        ("Cable 101", "Annotated diagram of what a submarine cable physically looks like."),
        ("Voltage Ladder", "Why higher kilovolts = bigger moat. The technology hierarchy explained."),
        ("Three Segments", "Detailed financial breakdown of submarine, land cable, and EPC services."),
        ("Five Moat Pillars", "The five barriers to entry, scored individually."),
        ("Vessel Fleet", "The cable-laying ships Orient owns — what makes the business defensible operationally."),
        ("China Map", "Where in China the company manufactures vs where the demand is, province by province."),
        ("Europe Pipeline", "European projects in the order book and pipeline, including the Morocco–UK XLinks cable route."),
        ("Financials", "All historical and forecast numbers as interactive charts."),
        ("Cost Drivers", "What moves the P&amp;L (copper, segment mix shift)."),
        ("Valuation", "P/E analysis, peer comparison, scenario price targets."),
        ("Bull vs Bear", "Interactive toggle showing both sides of the debate."),
        ("Risk Matrix", "Risks ranked by probability and severity."),
        ("Timeline", "Key catalysts from now through 2030."),
        ("Floating Wind Option", "The long-term optionality not in the base case."),
        ("Live Chart", "Real-time stock chart from TradingView."),
    ]
    data = []
    for title, desc in nav_items:
        data.append([Paragraph(f"<b>{title}</b>", S['body']),
                     Paragraph(desc, S['body'])])
    t = Table(data, colWidths=[1.6*inch, 4.5*inch])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('LINEBELOW', (0,0), (-1,-1), 0.3, BORDER),
        ('TEXTCOLOR', (0,0), (0,-1), CYAN),
    ]))
    story.append(t)

    story.append(PageBreak())

    # ============ SECTION 9: GLOSSARY ============
    story.append(SectionHeader(9, "Glossary"))
    story.append(Paragraph("Definitions for every jargon term that appears in the dashboard.", S['body']))
    story.append(Spacer(1, 10))

    glossary = [
        ("Submarine cable", "A power cable that lies on the seabed. Wraps copper conductors in insulation, lead, and steel."),
        ("HVAC vs HVDC", "High-Voltage Alternating Current vs Direct Current. HVAC is cheaper to make but loses more power over long distances. HVDC is harder to manufacture but works for very long distances (over 100 km). HVDC is what makes the Morocco–UK interconnection possible."),
        ("500kV / ±525kV", "Voltage ratings. Higher is harder to manufacture but lets you carry more power over longer distances. 500kV AC and ±525kV DC are the cutting edge today; only ~10 companies globally can produce them."),
        ("XLPE", "Cross-Linked Polyethylene — the plastic insulation used in modern submarine cables. The specific chemistry is part of what makes high-voltage cable manufacturing genuinely hard."),
        ("Inter-array vs export cable", "Inter-array cables connect individual turbines within a wind farm (lower voltage, more competitors). Export cables connect the wind farm's substation to the grid on land (higher voltage, fewer competitors, higher margin). Orient makes both."),
        ("Dynamic cable", "A cable used with floating wind turbines. It moves with the turbine in waves and currents, so it needs special fatigue-resistance engineering. A specialised future market that Orient is already producing for."),
        ("EPC", "Engineering, Procurement, Construction. The &quot;turnkey&quot; service model where the supplier handles everything from design through installation, rather than just selling components."),
        ("CfD (Contracts for Difference)", "A subsidy mechanism European governments use to guarantee wind farm developers a stable electricity price for 15–20 years. Removes price risk, makes financing easier, supports the long-term demand pipeline for cables."),
        ("15th Five-Year Plan", "China's national policy framework for 2026–2030. Targets 100 GW of cumulative offshore wind installed capacity by 2030."),
        ("Order backlog", "Contracts already signed but not yet delivered or recognized as revenue. Gives forward visibility on revenue and earnings."),
        ("Gross margin", "Revenue minus the direct cost of producing the product, expressed as a percentage. Higher = more pricing power and structural defensibility."),
        ("Net cash", "Cash on the balance sheet minus debt. Positive net cash means the company has no net leverage and can fund growth internally."),
        ("P/E ratio", "Price per share divided by earnings per share. Lower = cheaper. Used to compare valuations across companies and across time."),
        ("ROIC", "Return on Invested Capital — how much profit the company generates per dollar of capital invested in the business. Higher = better business quality."),
        ("Oligopoly", "A market dominated by a small number of firms. China's submarine cable market is a 3-player oligopoly with 87% combined share."),
        ("Inch Cape", "A large UK offshore wind project off the east coast of Scotland. Orient supplies RMB 1.8 billion of cable for it; grid connection scheduled for 2027."),
        ("XLinks", "A proposed 4,000 km HVDC cable that would carry Moroccan solar power to the UK. Orient owns 2.4% of the developer."),
        ("Fanshi I &amp; II", "Major Chinese offshore wind projects developed by CGN. Orient supplies RMB 1.7 billion of cable; grid connection in 2025/2026."),
        ("Dongfang Haigong", "The brand name for Orient's fleet of three cable-laying and transport vessels. DHG-07 is the 18,000-tonne platform that ships completed cables to Europe."),
    ]
    for term, defn in glossary:
        story.append(Paragraph(f"<b><font color='#0073b3'>{term}</font></b>  &nbsp; {defn}", S['body']))

    story.append(Spacer(1, 24))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(Spacer(1, 14))
    story.append(Paragraph(
        "<i>End of pre-read. The dashboard at <font color='#0073b3'><b>juankhye.github.io/ningbo-orient-603606-dashboard</b></font> "
        "contains the supporting charts, financial tables, maps, and live stock data referenced above.</i>",
        S['mini']))

    # ============ BUILD ============
    doc.build(story, onFirstPage=add_page_chrome, onLaterPages=add_page_chrome)
    print(f"Wrote {out}")

if __name__ == "__main__":
    build()
