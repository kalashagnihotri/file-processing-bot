import PyPDF2
import os

def delete_pdf_page(input_path, output_path, page_number):
    try:
        pdf_reader = PyPDF2.PdfReader(input_path)
        pdf_writer = PyPDF2.PdfWriter()
        
        total_pages = len(pdf_reader.pages)
        
        if page_number < 1 or page_number > total_pages:
            return f"Error: Page number {page_number} is out of range (1-{total_pages})"
        
        for i, page in enumerate(pdf_reader.pages):
            if i + 1 != page_number:  # Skip the page to delete
                pdf_writer.add_page(page)
        
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)
        
        return f"Deleted page {page_number} from PDF: {output_path}"
    except Exception as e:
        return f"Error deleting page from PDF: {e}"