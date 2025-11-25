from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
from pathlib import Path
import io

class PDFReportGenerator:
    """Generate combined PDF reports"""
    
    def __init__(self, output_path="report.pdf"):
        self.output_path = output_path
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=30,
            alignment=1  # Center
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#374151'),
            spaceAfter=12,
            spaceBefore=12,
            borderColor=colors.HexColor('#d1d5db'),
            borderWidth=1,
            borderPadding=8
        ))
        
        self.styles.add(ParagraphStyle(
            name='FieldLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#6b7280'),
            spaceAfter=4
        ))
    
    def _format_aamva_section(self, section_title, section_data):
        """Format AAMVA data section"""
        story = []
        story.append(Paragraph(section_title, self.styles['SectionHeader']))
        
        if section_data:
            for field_name, field_value in section_data.items():
                story.append(Paragraph(
                    f"<b>{field_name}:</b> {field_value}",
                    self.styles['Normal']
                ))
        else:
            story.append(Paragraph("No data available", self.styles['FieldLabel']))
        
        story.append(Spacer(1, 0.15*inch))
        return story
    
    def generate_report(self, session_data):
        """Generate PDF from session data"""
        try:
            doc = SimpleDocTemplate(
                self.output_path,
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )
            
            story = []
            
            # Title: use name from PDF417 when available so it matches the
            # logical report name and filename pattern (Firstname_Lastname).
            title_text = "Scan Report"
            pdf417_data = session_data.get("pdf417") or {}
            for item in pdf417_data.get("pdf417_data", []):
                parsed = item.get("parsed") or {}
                user = parsed.get("user") or {}
                first = (user.get("first") or "").strip().replace(" ", "_")
                last = (user.get("last") or "").strip().replace(" ", "_")
                if first and last:
                    title_text = f"{first}_{last}"
                    break

            title = Paragraph(title_text, self.styles['CustomTitle'])
            story.append(title)
            story.append(Spacer(1, 0.3*inch))

            # Track whether we've already added at least one data section so
            # we only insert page breaks *between* sections, not before the
            # first one (which would create a nearly empty first page).
            has_content_sections = False
            
            # Barcode section
            if session_data.get("barcode"):
                story.append(Paragraph("Barcode Data", self.styles['SectionHeader']))
                barcode_data = session_data["barcode"]
                for barcode in barcode_data.get("barcodes", []):
                    story.append(Paragraph(
                        f"<b>Type:</b> {barcode.get('type', 'Unknown')}<br/>"
                        f"<b>Data:</b> {barcode.get('data', 'N/A')}",
                        self.styles['Normal']
                    ))
                story.append(Spacer(1, 0.2*inch))
                has_content_sections = True
            
            # PDF417 section with formatted AAMVA data
            if session_data.get("pdf417"):
                if has_content_sections:
                    story.append(PageBreak())
                story.append(Paragraph("PDF417 - Driver License Data", self.styles['SectionHeader']))
                pdf417_data = session_data["pdf417"]
                
                for data in pdf417_data.get("pdf417_data", []):
                    if data.get("format") == "AAMVA" and data.get("parsed"):
                        parsed = data["parsed"]
                        
                        if parsed.get("user"):
                            user = parsed["user"]
                            story.extend(self._format_aamva_section(
                                "Personal Information",
                                {
                                    "Last Name": user.get("last", ""),
                                    "First Name": user.get("first", ""),
                                    "Middle Name": user.get("middle", ""),
                                    "Date of Birth": user.get("dob", ""),
                                    "Sex": user.get("sex", "")
                                }
                            ))
                            
                            story.extend(self._format_aamva_section(
                                "Physical Description",
                                {
                                    "Eye Color": user.get("eyes", ""),
                                    "Height": user.get("height", ""),
                                    "Race/Ethnicity": user.get("race", ""),
                                    "Weight": user.get("weight", "")
                                }
                            ))
                            
                            story.extend(self._format_aamva_section(
                                "Address",
                                {
                                    "Street Address": user.get("street", ""),
                                    "City": user.get("city", ""),
                                    "State": user.get("state", ""),
                                    "Postal Code": user.get("postal", ""),
                                    "Country": user.get("country", "")
                                }
                            ))
                            
                            story.extend(self._format_aamva_section(
                                "Document Information",
                                {
                                    "ID Number": user.get("id", ""),
                                    "Restriction Codes": user.get("restrictions", ""),
                                    "Endorsement Codes": user.get("endorsements", ""),
                                    "Issue Date": user.get("issued", ""),
                                    "Expiration Date": user.get("expires", ""),
                                    "Vehicle Class": user.get("vehicle_class", ""),
                                    "Vehicle Classification": user.get("vehicle_classification", ""),
                                    "Card Revision Date": user.get("card_revision", "")
                                }
                            ))
                    else:
                        story.append(Paragraph(
                            f"<b>Data:</b> {data.get('data', 'N/A')}",
                            self.styles['Normal']
                        ))
                
                story.append(Spacer(1, 0.2*inch))
                has_content_sections = True
            
            # Checkbook section
            if session_data.get("checkbook"):
                if has_content_sections:
                    story.append(PageBreak())
                story.append(Paragraph("Checkbook Scan", self.styles['SectionHeader']))
                checkbook_path = session_data["checkbook"].get("path")
                if checkbook_path and Path(checkbook_path).exists():
                    try:
                        img = Image(checkbook_path, width=5*inch, height=3*inch)
                        story.append(img)
                    except:
                        story.append(Paragraph("Checkbook image could not be loaded", self.styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Card section
            if session_data.get("card_front") or session_data.get("card_back"):
                if has_content_sections:
                    story.append(PageBreak())
                story.append(Paragraph("Card Scans", self.styles['SectionHeader']))
                
                if session_data.get("card_front"):
                    story.append(Paragraph("Front:", self.styles['Normal']))
                    card_front_path = session_data["card_front"].get("path")
                    if card_front_path and Path(card_front_path).exists():
                        try:
                            img = Image(card_front_path, width=4*inch, height=2.5*inch)
                            story.append(img)
                        except:
                            story.append(Paragraph("Card front image could not be loaded", self.styles['Normal']))
                    story.append(Spacer(1, 0.2*inch))
                
                if session_data.get("card_back"):
                    story.append(Paragraph("Back:", self.styles['Normal']))
                    card_back_path = session_data["card_back"].get("path")
                    if card_back_path and Path(card_back_path).exists():
                        try:
                            img = Image(card_back_path, width=4*inch, height=2.5*inch)
                            story.append(img)
                        except:
                            story.append(Paragraph("Card back image could not be loaded", self.styles['Normal']))
                has_content_sections = True

            # Timestamp footer: add at the end so we don't create an almost
            # empty first page with only the generated timestamp.
            story.append(Spacer(1, 0.3*inch))
            timestamp = Paragraph(
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                self.styles['Normal']
            )
            story.append(timestamp)
            
            # Build PDF
            doc.build(story)
            return {"success": True, "path": self.output_path}
        
        except Exception as e:
            return {"error": str(e)}
