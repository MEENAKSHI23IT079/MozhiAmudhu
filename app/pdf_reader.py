"""PDF Reader Module

Responsible for extracting text from uploaded PDF files using pdfplumber.
Supports multi-page PDFs and handles various PDF formats.
"""

import pdfplumber
from typing import Union
import io


def extract_text(pdf_file_path: Union[str, io.BytesIO]) -> str:
    """
    Extract text from a PDF file using pdfplumber.
    
    Args:
        pdf_file_path: Path to PDF file (str) or file-like object (BytesIO)
        
    Returns:
        str: Extracted plain text from all pages of the PDF
        
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        Exception: If PDF cannot be read or processed
        
    Example:
        >>> text = extract_text('document.pdf')
        >>> print(text[:100])  # First 100 characters
    """
    try:
        # Open PDF with pdfplumber
        with pdfplumber.open(pdf_file_path) as pdf:
            # Extract text from all pages
            extracted_text = []
            
            for page_num, page in enumerate(pdf.pages, start=1):
                # Extract text from current page
                page_text = page.extract_text()
                
                if page_text:
                    # Add page text with optional page separator
                    extracted_text.append(page_text.strip())
                else:
                    # Handle empty pages
                    print(f"Warning: Page {page_num} is empty or text could not be extracted")
            
            # Combine all pages with double newline separator
            full_text = "\n\n".join(extracted_text)
            
            # Return cleaned text
            return full_text.strip()
            
    except FileNotFoundError:
        raise FileNotFoundError(f"PDF file not found: {pdf_file_path}")
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")


def extract_text_with_layout(pdf_file_path: Union[str, io.BytesIO]) -> str:
    """
    Extract text from PDF while attempting to preserve layout.
    
    Args:
        pdf_file_path: Path to PDF file (str) or file-like object (BytesIO)
        
    Returns:
        str: Extracted text with layout preservation
    """
    try:
        with pdfplumber.open(pdf_file_path) as pdf:
            extracted_text = []
            
            for page in pdf.pages:
                # Extract text with layout settings
                page_text = page.extract_text(
                    layout=True,
                    x_tolerance=3,
                    y_tolerance=3
                )
                
                if page_text:
                    extracted_text.append(page_text.strip())
            
            return "\n\n".join(extracted_text).strip()
            
    except Exception as e:
        raise Exception(f"Error extracting text with layout: {str(e)}")


def get_pdf_info(pdf_file_path: Union[str, io.BytesIO]) -> dict:
    """
    Get metadata information about the PDF.
    
    Args:
        pdf_file_path: Path to PDF file (str) or file-like object (BytesIO)
        
    Returns:
        dict: PDF metadata including page count, title, author, etc.
    """
    try:
        with pdfplumber.open(pdf_file_path) as pdf:
            info = {
                'page_count': len(pdf.pages),
                'metadata': pdf.metadata if pdf.metadata else {},
            }
            return info
    except Exception as e:
        raise Exception(f"Error getting PDF info: {str(e)}")


if __name__ == "__main__":
    # Test the module
    import sys
    
    if len(sys.argv) > 1:
        test_pdf = sys.argv[1]
        print(f"Testing PDF extraction on: {test_pdf}")
        print("=" * 50)
        
        # Get PDF info
        info = get_pdf_info(test_pdf)
        print(f"Pages: {info['page_count']}")
        print(f"Metadata: {info['metadata']}")
        print("=" * 50)
        
        # Extract text
        text = extract_text(test_pdf)
        print(f"\nExtracted {len(text)} characters")
        print(f"\nFirst 500 characters:\n{text[:500]}")
    else:
        print("Usage: python pdf_reader.py <path_to_pdf>")
