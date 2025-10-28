################################################################################
# Document Q&A Assistant                                                       #
# Projet Portfolio - NLP & Machine Learning                                    #
# Autrice: Naja Sthael G S Ferreira                                            #
# Description: Analyse linguistique du texte avec spaCy et statistiques        #
################################################################################

import spacy
from collections import Counter
import re

class TextAnalyzer:
   
    def __init__(self):
        """Charge le modèle spaCy français"""
        
        modele = "fr_core_news_md"
        
        try:
            self.nlp = spacy.load(modele)
            print(f"✓ spaCy {modele} chargé")
        except OSError:
            print(f"❌ Modèle {modele} pas installé!")
            print(f"Lancez: python -m spacy download {modele}")
            raise
   
    def analyser_texte(self, texte):
        """Fait toutes les analyses du texte"""
        
        doc = self.nlp(texte)
        
        stats = {
            "nb_chars": len(texte),
            "nb_mots": len([t for t in doc if not t.is_space]),
            "nb_phrases": len([s for s in doc.sents]),
            "entites": self.extraire_entites(doc),
            "mots_frequents": self.mots_frequents(doc, top=20),
            "pos_tags": self.distribution_pos(doc)
        }
        
        return stats
   
    def extraire_entites(self, doc):
        """Trouve les entités nommées (personnes, lieux, etc.)"""
        
        entites = []
        for ent in doc.ents:
            entites.append({
                "texte": ent.text,
                "type": ent.label_,
                "debut": ent.start_char,
                "fin": ent.end_char
            })
        
        return entites
   
    def mots_frequents(self, doc, top=20):
        """Calcule les mots les plus fréquents (sans les mots vides)"""
        
        # j'enlève stopwords, ponctuation et mots trop courts
        mots = []
        for token in doc:
            if not token.is_stop and not token.is_punct and not token.is_space:
                if len(token.text) > 2:  # au moins 3 lettres
                    mots.append(token.text.lower())
        
        freq = Counter(mots).most_common(top)
        return freq
   
    def distribution_pos(self, doc):
        """Compte les types de mots (verbes, noms, adjectifs...)"""
        
        pos = [t.pos_ for t in doc if not t.is_space]
        distribution = Counter(pos)
        
        return dict(distribution)
   
    def extraire_bigrammes(self, texte, top=10):
        """Trouve les paires de mots fréquentes"""
        # j'ai ajouté ça après pour avoir plus d'analyse
        
        # nettoyage basique du texte
        mots = re.findall(r'\b\w+\b', texte.lower())
        
        # crée les paires de mots
        bigrammes = []
        for i in range(len(mots) - 1):
            bg = f"{mots[i]} {mots[i+1]}"
            bigrammes.append(bg)
        
        freq_bg = Counter(bigrammes).most_common(top)
        return freq_bg