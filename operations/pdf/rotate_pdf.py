import PyPDF2
import os

def rotate_pdf(input_path, output_path, angle=90):
    try:
        pdf_reader = PyPDF2.PdfReader(input_path)
        pdf_writer = PyPDF2.PdfWriter()
        
        for page in pdf_reader.pages:
            rotated_page = page.rotate(angle)
            pdf_writer.add_page(rotated_page)
        
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)
        
        return f"Rotated PDF by {angle} degrees: {output_path}"
    except Exception as e:
        return f"Error rotating PDF: {e}"