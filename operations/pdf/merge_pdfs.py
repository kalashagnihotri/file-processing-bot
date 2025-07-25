import PyPDF2
import os

def merge_pdfs(input_paths, output_path):
    try:
        pdf_writer = PyPDF2.PdfWriter()
        
        for path in input_paths:
            pdf_reader = PyPDF2.PdfReader(path)
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
        
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)
        
        return f"Merged {len(input_paths)} PDFs into: {output_path}"
    except Exception as e:
        return f"Error merging PDFs: {e}"