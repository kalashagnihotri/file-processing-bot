import PyPDF2
import os

def unlock_pdf(input_path, output_path, password):
    try:
        pdf_reader = PyPDF2.PdfReader(input_path)
        
        if pdf_reader.is_encrypted:
            pdf_reader.decrypt(password)
        
        pdf_writer = PyPDF2.PdfWriter()
        
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)
        
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)
        
        return f"Unlocked PDF: {output_path}"
    except Exception as e:
        return f"Error unlocking PDF: {e}"