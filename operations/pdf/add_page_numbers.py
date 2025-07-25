import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import os

def add_page_numbers(input_path, output_path, position='bottom-right'):
    try:
        pdf_reader = PyPDF2.PdfReader(input_path)
        pdf_writer = PyPDF2.PdfWriter()
        
        for page_num, page in enumerate(pdf_reader.pages, 1):
            # Create a new PDF with page number
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            
            # Set position for page number
            if position == 'bottom-right':
                x, y = 550, 30
            elif position == 'bottom-left':
                x, y = 50, 30
            elif position == 'top-right':
                x, y = 550, 750
            else:  # top-left
                x, y = 50, 750
            
            can.drawString(x, y, str(page_num))
            can.save()
            
            # Move to the beginning of the BytesIO buffer
            packet.seek(0)
            number_pdf = PyPDF2.PdfReader(packet)
            
            # Merge the page number with the original page
            page.merge_page(number_pdf.pages[0])
            pdf_writer.add_page(page)
        
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)
        
        return f"Added page numbers to PDF: {output_path}"
    except Exception as e:
        return f"Error adding page numbers: {e}"