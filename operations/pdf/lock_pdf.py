import PyPDF2
import os

def lock_pdf(input_path, output_path, password):
    try:
        pdf_reader = PyPDF2.PdfReader(input_path)
        pdf_writer = PyPDF2.PdfWriter()
        
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)
        
        # Encrypt the PDF with password
        pdf_writer.encrypt(password)
        
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)
        
        return f"Locked PDF with password: {output_path}"
    except Exception as e:
        return f"Error locking PDF: {e}"