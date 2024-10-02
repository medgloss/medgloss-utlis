import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO
from PIL import Image

# Function to remove black background from the logo image
def remove_black_background(logo_path):
    img = Image.open(logo_path).convert("RGBA")
    datas = img.getdata()
    new_data = []
    for item in datas:
        if item[0] < 50 and item[1] < 50 and item[2] < 50:
            # Replace black with transparent
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    img.putdata(new_data)
    transparent_logo = "transparent_logo.png"
    img.save(transparent_logo, "PNG")
    return transparent_logo

# Function to create watermark with logo and URL
def create_watermark_with_logo(logo_path, link_url, output="watermark.pdf"):
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)
    
    width, height = A4
    logo_size = 0.8 * inch  # Size of the logo image

    # Header section
    c.drawImage(logo_path, 0.3 * inch, height - 1.1 * inch, logo_size, logo_size)  # Left logo
    c.drawImage(logo_path, width - 1.1 * inch, height - 1.1 * inch, logo_size, logo_size)  # Right logo

    # Function to draw URL with letter spacing
    def style_url(canvas, text, x, y):
        canvas.saveState()
        canvas.setFillColor(colors.Color(0.95, 0.4, 0.4))  # Color matching image
        canvas.setFont("Courier-BoldOblique", 28)  # Using Courier-BoldOblique to match style

        # Calculate total width of the text with custom spacing
        letter_spacing = 16  # Adjust for larger/smaller spacing between letters
        for i, char in enumerate(text):
            canvas.drawString(x + (i * letter_spacing), y, char)
        
        canvas.restoreState()

    # Calculate the starting x position to center the URL
    text_width = len(link_url) * 16  # Assuming each character takes up 10 units width
    start_x = (width - text_width) / 2

    # Draw the URL text at the top of the page
    style_url(c, link_url, start_x, height - 0.8 * inch)

    # Footer section
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.5)
    c.line(0.2 * inch, 1.3 * inch, width - 0.2 * inch, 1.3 * inch)  # Footer line
    
    # Left and right footer logos
    c.drawImage(logo_path, 0.3 * inch, 0.4 * inch, logo_size, logo_size)
    c.drawImage(logo_path, width - 1.1 * inch, 0.4 * inch, logo_size, logo_size)

    # Draw the URL text at the bottom of the page
    style_url(c, link_url, start_x, 0.8 * inch)

    c.save()
    packet.seek(0)  # Move the packet back to the beginning for reading
    return PyPDF2.PdfReader(packet)

# Function to apply watermark to PDF
def add_watermark_to_pdf(input_pdf, watermark_pdf, output_pdf):
    with open(input_pdf, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        pdf_writer = PyPDF2.PdfWriter()
        
        watermark_page = watermark_pdf.pages[0]  # Get the first page of the watermark

        # Apply watermark to each page in the input PDF
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page.merge_page(watermark_page)  # Merge the watermark
            pdf_writer.add_page(page)

        # Write the watermarked pages to a new file
        with open(output_pdf, "wb") as output_file:
            pdf_writer.write(output_file)
    print(f"Watermark added to {output_pdf}")

# Main execution block
if __name__ == "__main__":
    input_pdf_path = "sample.pdf"  # Path to the input PDF file
    logo_path = "brain_logo.png"  # Path to the logo image
    link_url = "www.medgloss.com"  # URL to be added as watermark
    output_pdf_path = "output_watermarked.pdf"  # Output file path

    # Remove black background from the logo and get the path to the transparent logo
    transparent_logo_path = remove_black_background(logo_path)
    
    # Create watermark with the transparent logo and URL
    watermark_pdf = create_watermark_with_logo(transparent_logo_path, link_url)
    
    # Apply watermark to the input PDF
    add_watermark_to_pdf(input_pdf_path, watermark_pdf, output_pdf_path)
