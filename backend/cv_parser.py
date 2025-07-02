import docx
import pdfplumber
import os

def extract_text_from_docx(docx_path):
    """Extracts text from a DOCX file.
    
    Args:
        docx_path (str): Path to the DOCX file
        
    Returns:
        str: Extracted text or None if error occurs
    """
    try:
        if not os.path.exists(docx_path):
            print(f"File not found: {docx_path}")
            return None
            
        doc = docx.Document(docx_path)
        return '\n'.join(para.text for para in doc.paragraphs)
    except Exception as e:
        print(f"Error reading DOCX file {docx_path}: {e}")
        return None

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text or None if error occurs
    """
    try:
        if not os.path.exists(pdf_path):
            print(f"File not found: {pdf_path}")
            return None
            
        text_content = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
        return '\n'.join(text_content)
    except Exception as e:
        print(f"Error reading PDF file {pdf_path}: {e}")
        return None

def parse_cv(file_path):
    """Parse CV file and extract text content.
    
    Args:
        file_path (str): Path to the CV file (PDF or DOCX)
        
    Returns:
        str: Extracted text or None if unsupported format or error occurs
    """
    if not file_path or not isinstance(file_path, str):
        print("Invalid file path provided")
        return None
        
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None

    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.docx':
        return extract_text_from_docx(file_path)
    elif file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    else:
        print(f"Unsupported file type: {file_extension}")
        return None