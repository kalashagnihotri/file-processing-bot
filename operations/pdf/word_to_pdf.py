import os
try:
    from docx2pdf import convert
    DOCX2PDF_AVAILABLE = True
except ImportError:
    DOCX2PDF_AVAILABLE = False

def convert_word_to_pdf(input_path, output_path):
    try:
        if not DOCX2PDF_AVAILABLE:
            return "Error: Word to PDF conversion not available. Please install docx2pdf: pip install docx2pdf"
        
        convert(input_path, output_path)
        return f"Converted Word to PDF: {output_path}"
    except Exception as e:
        return f"Error converting Word to PDF: {e}"