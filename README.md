Medgloss PDF Watermark Removal
Project Overview
The Medgloss PDF Watermark Removal tool is a Python-based project aimed at automating the addition and removal of watermarks in PDF files. It uses libraries like PyPDF2 and reportlab to efficiently manage PDF content and enhance document presentation.

This project is particularly useful for managing large volumes of PDF files in the Medgloss system, allowing seamless customization and branding of documents.

Features
Add Watermarks to PDFs: Apply a custom watermark to any PDF document.
Remove Watermarks from PDFs: Cleanly remove watermarks from PDF files.
Efficient Batch Processing: Handle multiple PDF files in a batch to save time.
Customizable Watermarks: Users can define their own text or image watermarks.
Secure File Handling: The original PDF structure is preserved while adding/removing watermarks.
Requirements
The project requires Python 3.x and the following libraries:

PyPDF2: For PDF manipulation.
reportlab: To create custom watermarks.
tkinter (optional): For GUI-based file selection (if GUI support is added).
Install the required libraries via pip:

pip install PyPDF2 reportlab
How to Use
1. Add Watermark to PDF
To add a watermark to a PDF file, use the following command:
python add_watermark.py input.pdf watermark.pdf output.pdf
input.pdf: The original PDF file to which the watermark will be added.
watermark.pdf: The PDF file containing the watermark (created using reportlab).
output.pdf: The output PDF with the watermark applied.
2. Remove Watermark from PDF
To remove a watermark from a PDF file, use:
python remove_watermark.py input.pdf output.pdf
input.pdf: The watermarked PDF file.
output.pdf: The output PDF with the watermark removed.
3. Create a Watermark
To create a watermark PDF using reportlab:
python create_watermark.py "Your Watermark Text" watermark.pdf
Replace "Your Watermark Text" with the desired text for your watermark.
watermark.pdf will be the generated PDF containing your custom watermark.
4. Batch Processing
For batch processing multiple PDF files, simply provide a directory as input, and the tool will automatically process all PDFs in the directory.
python batch_watermark.py input_directory/ output_directory/
input_directory/: Directory containing the PDFs to be processed.
output_directory/: Directory to save the processed PDFs.
