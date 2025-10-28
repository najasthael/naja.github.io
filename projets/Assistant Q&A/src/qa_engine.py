################################################################################
# Document Q&A Assistant                                                       #
# Projet Portfolio - NLP & Machine Learning                                    #
# Autrice: Naja Sthael G S Ferreira                                            #
# Description: Moteur Q&A avec CamemBERT (ça prend du temps à charger...)      #
################################################################################

from transformers import pipeline
import torch

class QAEngine:
   
    def __init__(self):
        # vérifie si j'ai un GPU (spoiler: non, mais bon)
        self.device = 0 if torch.cuda.is_available() else -1
        
        print("Chargement du modèle CamemBERT...")
        print("⚠️  Attention: ça peut prendre 2-3 minutes la première fois!")
        
        # j'ai testé plusieurs modèles, celui-là marche mieux en français
        try:
            self.qa_model = pipeline(
                "question-answering",
                model="deepset/roberta-base-squad2",
                device=self.device,
                use_fast=False
            )
            print("✓ Modèle chargé!")
        except Exception as e:
            print(f"Erreur chargement: {e}")
            print("Essayez: pip install transformers torch")
            raise
   
    def poser_question(self, question, texte):
        """Cherche la réponse dans le texte"""
        
        if not texte or not question:
            return {
                "reponse": "Texte ou question vide",
                "score": 0.0,
                "position": (0, 0)
            }
        
        # le modèle plante si le texte est trop long, donc je limite
        # après plusieurs tests, 3000 caractères ça passe bien
        taille_max = 3000
        if len(texte) > taille_max:
            texte = texte[:taille_max]
            print(f"⚠️  Texte tronqué à {taille_max} caractères")
        
        try:
            resultat = self.qa_model(
                question=question,
                context=texte
            )
            
            return {
                "reponse": resultat["answer"],
                "score": round(resultat["score"], 3),  # 3 décimales suffisent
                "position": (resultat["start"], resultat["end"])
            }
        
        except Exception as e:
            print(f"Erreur pendant la recherche: {e}")
            return {
                "reponse": "Erreur lors de la recherche",
                "score": 0.0,
                "position": (0, 0)
            }
   
    def trouver_contexte(self, texte, debut, fin, marge=150):
        """Extrait le contexte autour de la réponse"""
        # j'ai mis 150 au lieu de 100, donne plus de contexte
        
        start = max(0, debut - marge)
        end = min(len(texte), fin + marge)
        
        extrait = texte[start:end]
        
        # parfois ça commence au milieu d'un mot, je rajoute ...
        if start > 0:
            extrait = "..." + extrait
        if end < len(texte):
            extrait = extrait + "..."
        
        return extrait