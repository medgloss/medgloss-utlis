from flask import Flask, request, send_file, render_template
from PIL import Image, ImageDraw, ImageFont
import io
import os
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

# Configure paths
LOGO_PATH = "static/transparent_logo.png"
WATERMARK_TEXT = "www.medgloss.com"
FONT_PATH = "static/fonts/RobotoMono-Regular.ttf"

# Register custom font for PDF
try:
    pdfmetrics.registerFont(TTFont('RobotoMono', FONT_PATH))
except:
    pass  # Will fallback to Helvetica if font registration fails

# Ensure the upload folder exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def create_watermark_template(pagesize=A4):
    """Create a single watermark template that can be applied to any page"""
    # Create buffer for watermark template
    watermark_buffer = io.BytesIO()
    
    # Create canvas with given pagesize
    c = canvas.Canvas(watermark_buffer, pagesize=pagesize)
    width, height = pagesize
    
    # Load and add logo to corners
    logo_size = 50
    margin = 20
    
    try:
        # Add logos to corners
        c.drawImage(LOGO_PATH, margin, height - margin - logo_size, 
                   width=logo_size, height=logo_size, mask='auto')
        c.drawImage(LOGO_PATH, width - margin - logo_size, 
                   height - margin - logo_size, width=logo_size, 
                   height=logo_size, mask='auto')
        c.drawImage(LOGO_PATH, margin, margin, width=logo_size, 
                   height=logo_size, mask='auto')
        c.drawImage(LOGO_PATH, width - margin - logo_size, margin, 
                   width=logo_size, height=logo_size, mask='auto')
    except Exception as e:
        print(f"Error adding logo: {str(e)}")
    
    # Set font - increased size from 16 to 20
    try:
        c.setFont("RobotoMono", 20)
    except:
        c.setFont("Helvetica", 20)
    
    # Set tomato color for text with increased opacity
    c.setFillColor(colors.tomato)
    c.setFillAlpha(0.8)  # Increased from 0.7 to 0.8
    
    # Add text at top and bottom center
    text_width = c.stringWidth(WATERMARK_TEXT)
    c.drawString(width/2 - text_width/2, height - 40, WATERMARK_TEXT)
    c.drawString(width/2 - text_width/2, 30, WATERMARK_TEXT)
    
    # Add diagonal watermark with decreased size and opacity
    c.saveState()
    c.translate(width/2, height/2)
    c.rotate(45)
    c.setFont("Helvetica", 48)  # Decreased from 80 (40% reduction)
    c.setFillAlpha(0.105)  # Decreased from 0.15 (30% reduction)
    text_width = c.stringWidth(WATERMARK_TEXT)
    c.drawString(-text_width/2, 0, WATERMARK_TEXT)
    c.restoreState()
    
    # Draw horizontal black line with adjusted length
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.5)
    line_length = width * 0.8
    start_x = (width - line_length) / 2
    c.line(start_x, 80, start_x + line_length, 80)
    
    c.save()
    watermark_buffer.seek(0)
    return watermark_buffer

def add_image_watermark(image_file):
    """Add watermark to image"""
    try:
        # Open the image
        img = Image.open(image_file)
        
        # Convert to RGBA if necessary
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Create drawing object
        draw = ImageDraw.Draw(img)
        
        # Calculate font size based on image dimensions
        font_size = int(min(img.width, img.height) * 0.05)  # 5% of smallest dimension
        font_size = max(40, min(font_size, 80))  # Constrain between 40 and 80
        
        # Try to use custom font, fallback to default if not available
        try:
            font = ImageFont.truetype(FONT_PATH, font_size)
        except:
            font = ImageFont.load_default()
        
        # Add text at top right corner with tomato color and increased opacity
        text_color = (255, 99, 71, 230)  # Increased alpha from 200 to 230
        
        # Calculate position for top right text
        margin = 20
        text_bbox = draw.textbbox((0, 0), WATERMARK_TEXT, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_position = (img.width - text_width - margin, margin)
        
        # Draw text
        draw.text(text_position, WATERMARK_TEXT, fill=text_color, font=font)
        
        # Save the watermarked image
        output = io.BytesIO()
        img.save(output, format='PNG')
        output.seek(0)
        return output
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")

def add_pdf_watermark(pdf_file):
    """Add watermark to PDF, handling multiple pages correctly"""
    try:
        # Create PDF reader and writer objects
        pdf_reader = PdfReader(pdf_file)
        pdf_writer = PdfWriter()
        
        # Create watermark template
        watermark_buffer = create_watermark_template()
        watermark_pdf = PdfReader(watermark_buffer)
        watermark_page = watermark_pdf.pages[0]
        
        # Process each page
        for page_num in range(len(pdf_reader.pages)):
            # Get the page
            page = pdf_reader.pages[page_num]
            
            # Get page size
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            
            # Create new watermark if page size differs from A4
            if abs(page_width - A4[0]) > 1 or abs(page_height - A4[1]) > 1:
                watermark_buffer = create_watermark_template((page_width, page_height))
                watermark_pdf = PdfReader(watermark_buffer)
                watermark_page = watermark_pdf.pages[0]
            
            # Merge watermark with page
            page.merge_page(watermark_page)
            
            # Add page to output
            pdf_writer.add_page(page)
        
        # Save the result
        output = io.BytesIO()
        pdf_writer.write(output)
        output.seek(0)
        return output
    
    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/add-watermark', methods=['POST'])
def watermark():
    if 'file' not in request.files:
        return 'No file provided', 400
    
    file = request.files['file']
    file_type = request.form.get('fileType')
    
    if file.filename == '':
        return 'No file selected', 400
    
    try:
        if file_type == 'image':
            output = add_image_watermark(file)
            return send_file(
                output,
                mimetype='image/png',
                as_attachment=True,
                download_name='watermarked.png'
            )
        elif file_type == 'pdf':
            output = add_pdf_watermark(file)
            return send_file(
                output,
                mimetype='application/pdf',
                as_attachment=True,
                download_name='watermarked.pdf'
            )
        else:
            return 'Invalid file type', 400
    except Exception as e:
        return f'Error processing file: {str(e)}', 500

if __name__ == '__main__':
    app.run(debug=True)