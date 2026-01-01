import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from io import BytesIO
import subprocess
import tempfile
from typing import List, Dict
from PIL import Image as PILImage
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


class PDFGenerator:
    """Generate PDF from translated content"""
    
    def __init__(self):
        """Initialize PDF generator with Korean font support"""
        # Register Korean font (using system fonts)
        # Note: You may need to adjust font path based on your system
        try:
            # Try to register a Korean font
            # Windows: Malgun Gothic
            # Linux: Noto Sans CJK KR
            font_paths = [
                "C:/Windows/Fonts/malgun.ttf",  # Windows
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",  # Linux
                "/System/Library/Fonts/AppleSDGothicNeo.ttc"  # macOS
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('Korean', font_path))
                    self.korean_font = 'Korean'
                    print(f"Registered Korean font: {font_path}")
                    break
            else:
                # Fallback to Helvetica
                self.korean_font = 'Helvetica'
                print("Warning: Korean font not found, using Helvetica")
        except Exception as e:
            print(f"Error registering font: {e}")
            self.korean_font = 'Helvetica'
    
    def generate_pdf(self, pages_data: List[Dict], output_path: str) -> str:
        """
        Generate PDF from translated pages data
        
        Args:
            pages_data: List of page dictionaries with translated paragraphs
            output_path: Path to save the PDF
            
        Returns:
            Path to generated PDF
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = self._create_styles()
        
        # Process each page
        for page_idx, page_data in enumerate(pages_data):
            print(f"Generating PDF page {page_idx + 1}/{len(pages_data)}")
            
            # Add page number
            page_num = Paragraph(
                f"<font name='{self.korean_font}'>페이지 {page_data['page']}</font>",
                styles['PageNumber']
            )
            elements.append(page_num)
            elements.append(Spacer(1, 0.2 * inch))
            
            # Add paragraphs
            for para in page_data.get('paragraphs', []):
                content = para.get('content', '')
                
                if not content.strip():
                    continue
                
                # Check if paragraph contains formulas
                if '$$' in content:
                    # Process mixed content (text + formulas)
                    self._add_mixed_content(elements, content, styles)
                else:
                    # Plain text paragraph
                    p = Paragraph(
                        f"<font name='{self.korean_font}'>{self._escape_html(content)}</font>",
                        styles['Normal']
                    )
                    elements.append(p)
                    elements.append(Spacer(1, 0.15 * inch))
            
            # Add page break except for last page
            if page_idx < len(pages_data) - 1:
                elements.append(PageBreak())
        
        # Build PDF
        doc.build(elements)
        print(f"PDF generated: {output_path}")
        
        return output_path
    
    def _create_styles(self):
        """Create custom styles for PDF"""
        styles = getSampleStyleSheet()
        
        # Normal paragraph style
        styles.add(ParagraphStyle(
            name='Normal',
            fontName=self.korean_font,
            fontSize=11,
            leading=16,
            alignment=TA_LEFT,
            spaceAfter=10
        ))
        
        # Page number style
        styles.add(ParagraphStyle(
            name='PageNumber',
            fontName=self.korean_font,
            fontSize=9,
            textColor='gray',
            alignment=TA_CENTER
        ))
        
        # Formula style
        styles.add(ParagraphStyle(
            name='Formula',
            fontName='Courier',
            fontSize=10,
            leading=14,
            leftIndent=20,
            rightIndent=20,
            spaceAfter=10,
            textColor='darkblue'
        ))
        
        return styles
    
    def _add_mixed_content(self, elements, content: str, styles):
        """Add content with mixed text and formulas"""
        # Split by formula blocks
        parts = re.split(r'(\$\$.*?\$\$)', content, flags=re.DOTALL)
        
        for part in parts:
            if part.startswith('$$') and part.endswith('$$'):
                # Formula block
                formula = part[2:-2].strip()
                
                # Try to render formula as image using LaTeX
                formula_img = self._render_formula(formula)
                
                if formula_img:
                    elements.append(formula_img)
                else:
                    # Fallback: show LaTeX code
                    p = Paragraph(
                        f"<font name='Courier'>[Formula: {self._escape_html(formula)}]</font>",
                        styles['Formula']
                    )
                    elements.append(p)
                
                elements.append(Spacer(1, 0.1 * inch))
            elif part.strip():
                # Text block
                p = Paragraph(
                    f"<font name='{self.korean_font}'>{self._escape_html(part)}</font>",
                    styles['Normal']
                )
                elements.append(p)
                elements.append(Spacer(1, 0.1 * inch))
    
    def _render_formula(self, formula: str):
        """Render LaTeX formula as image (requires LaTeX installation)"""
        try:
            # Create temporary LaTeX file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as f:
                latex_content = f"""
\\documentclass[border=2pt]{{standalone}}
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\begin{{document}}
${formula}$
\\end{{document}}
"""
                f.write(latex_content)
                tex_file = f.name
            
            # Compile with pdflatex
            output_dir = os.path.dirname(tex_file)
            result = subprocess.run(
                ['pdflatex', '-output-directory', output_dir, tex_file],
                capture_output=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Convert PDF to PNG
                pdf_file = tex_file.replace('.tex', '.pdf')
                png_file = tex_file.replace('.tex', '.png')
                
                subprocess.run(
                    ['convert', '-density', '300', pdf_file, png_file],
                    capture_output=True,
                    timeout=10
                )
                
                if os.path.exists(png_file):
                    # Load image and add to PDF
                    img = Image(png_file, width=4*inch, height=0.5*inch, kind='proportional')
                    
                    # Clean up temp files
                    for ext in ['.tex', '.pdf', '.png', '.aux', '.log']:
                        try:
                            os.remove(tex_file.replace('.tex', ext))
                        except:
                            pass
                    
                    return img
            
            # Clean up on failure
            try:
                os.remove(tex_file)
            except:
                pass
            
        except Exception as e:
            print(f"Formula rendering failed: {e}")
        
        return None
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        return text
