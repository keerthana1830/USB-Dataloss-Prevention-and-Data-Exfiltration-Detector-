import os
import csv
try:
    import PyPDF2
    import docx
except ImportError:
    PyPDF2 = None
    docx = None

class SensitivityScanner:
    def __init__(self):
        self.sensitive_keywords = ['password', 'salary', 'confidential', 'bank', 'invoice', 'customer', 'secret']

    def scan_file(self, file_path, extension):
        keywords_found = []
        try:
            if not os.path.exists(file_path):
                return []
            
            ext = extension.lower()
            content = ""

            if ext == '.txt':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            elif ext == '.csv':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read() # simplified read for regex/keywords
            elif ext == '.pdf' and PyPDF2 is not None:
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted: content += extracted
            elif ext == '.docx' and docx is not None:
                doc = docx.Document(file_path)
                for para in doc.paragraphs:
                    content += para.text

            content_lower = content.lower()
            for kw in self.sensitive_keywords:
                if kw in content_lower:
                    keywords_found.append(kw)
        except Exception as e:
            pass # ignore errors on locked files
            
        return list(set(keywords_found))
