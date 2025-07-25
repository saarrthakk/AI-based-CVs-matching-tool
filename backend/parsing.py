import PyPDF2
import docx

# extracting text from pdf files
def parse_pdf(file_path):
    
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        raise ValueError(f"Could not read PDF file: {e}")
    return text

# extracting text from docx files
def parse_docx(file_path):

    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        raise ValueError(f"Could not read DOCX file: {e}")
    return text

# parsing the CV file based on its extension
def parse_cv(file_path):

    if file_path.lower().endswith('.pdf'):
        return parse_pdf(file_path)
    elif file_path.lower().endswith('.docx'):
        return parse_docx(file_path)
    else:
        raise ValueError("Unsupported file type. Only PDF and DOCX are allowed.")