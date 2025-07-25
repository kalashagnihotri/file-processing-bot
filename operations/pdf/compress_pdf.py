import PyPDF2
import os
import logging

logger = logging.getLogger(__name__)

def compress_pdf(input_path, output_path):
    """
    Compress PDF file with comprehensive error handling.
    
    Args:
        input_path (str): Path to input PDF file
        output_path (str): Path for output compressed PDF file
        
    Returns:
        str: Success message with compression stats or detailed error description
    """
    try:
        # Validate input file exists and is readable
        if not os.path.exists(input_path):
            return f"Error: Input PDF file does not exist: {input_path}"
        
        if not os.access(input_path, os.R_OK):
            return f"Error: Cannot read input PDF file (permission denied): {input_path}"
        
        # Check file size
        original_size = os.path.getsize(input_path)
        if original_size == 0:
            return f"Error: Input PDF file is empty: {input_path}"
        
        if original_size > 50 * 1024 * 1024:  # 50MB limit
            return f"Error: PDF file too large ({original_size / 1024 / 1024:.1f}MB). Maximum: 50MB"
        
        # Validate output directory
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                return f"Error: Cannot create output directory: {e}"
        
        # Read and process PDF
        try:
            with open(input_path, 'rb') as input_file:
                pdf_reader = PyPDF2.PdfReader(input_file)
                
                # Check if PDF is encrypted
                if pdf_reader.is_encrypted:
                    return f"Error: PDF is password protected. Please unlock first."
                
                # Check if PDF has pages
                if len(pdf_reader.pages) == 0:
                    return f"Error: PDF has no pages to compress"
                
                pdf_writer = PyPDF2.PdfWriter()
                
                # Process each page with error handling
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page.compress_content_streams()  # Basic compression
                        pdf_writer.add_page(page)
                    except Exception as e:
                        logger.warning(f"Could not compress page {page_num + 1}: {e}")
                        # Add page without compression
                        pdf_writer.add_page(page)
                
                # Write compressed PDF
                try:
                    with open(output_path, 'wb') as output_file:
                        pdf_writer.write(output_file)
                except Exception as e:
                    return f"Error: Cannot write compressed PDF: {e}"
        
        except PyPDF2.errors.PdfReadError as e:
            return f"Error: Invalid or corrupted PDF file: {e}"
        except Exception as e:
            return f"Error: Cannot process PDF file: {e}"
        
        # Verify output and calculate compression
        if not os.path.exists(output_path):
            return f"Error: Compressed PDF was not created successfully"
        
        compressed_size = os.path.getsize(output_path)
        if compressed_size == 0:
            return f"Error: Compressed PDF is empty (processing failed)"
        
        # Calculate compression ratio
        if original_size > 0:
            reduction = ((original_size - compressed_size) / original_size) * 100
            size_mb = compressed_size / 1024 / 1024
            
            logger.info(f"PDF compressed: {reduction:.1f}% reduction, final size: {size_mb:.2f}MB")
            return f"Successfully compressed PDF: {os.path.basename(output_path)} (Reduced by {reduction:.1f}%, Size: {size_mb:.2f}MB)"
        else:
            return f"Successfully compressed PDF: {os.path.basename(output_path)}"
    
    except MemoryError:
        return f"Error: PDF too large to process (insufficient memory)"
    except PermissionError:
        return f"Error: Permission denied accessing PDF files"
    except Exception as e:
        logger.error(f"Unexpected error in PDF compression: {e}")
        return f"Error compressing PDF: {str(e)}"