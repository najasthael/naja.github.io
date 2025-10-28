################################################################################
# Document Q&A Assistant                                                       #
# Projet Portfolio - NLP & Machine Learning                                    #
# Autrice: Naja Sthael G S Ferreira                                            #
# Description: Traitement et extraction de texte depuis différents formats     #
################################################################################

from docx import Document
from pathlib import Path
import PyPDF2

class DocumentProcessor:
   
    def __init__(self):
        self.formats_ok = [".pdf", ".txt", ".docx"]  # mudei
   
    def extract_text(self, file_path):
        chemin = Path(file_path)  # mudei
        ext = chemin.suffix.lower()  # mudei
       
        if ext == ".pdf":
            return self.lire_pdf(file_path)  # mudei
        elif ext == ".txt":
            return self.lire_txt(file_path)  # mudei
        elif ext == ".docx":
            return self.lire_docx(file_path)  # mudei
        else:
            raise ValueError(f"Extension sans support: {ext}")
   
    def lire_pdf(self, file_path):
        texte = ""  # mudei
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)  # mudei
                for pg in reader.pages:  # mudei
                    contenu = pg.extract_text()  # mudei
                    if contenu:
                        texte += contenu + "\n"
        except FileNotFoundError:
            print(f"Fichier introuvable: {file_path}")
            return ""
        except Exception as e:
            print(f"Erreur PDF: {e}")
            return ""
        return texte
   
    def lire_txt(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            contenu = f.read()  # mudei
        return contenu
   
    def lire_docx(self, file_path):
        doc = Document(file_path)
        texte = ""  # mudei
        for p in doc.paragraphs:  # mudei
            texte += p.text + "\n"
        return texte