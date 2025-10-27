################################################################################
# Fine-Tuning Projet FAQ-Gouv                                                  #
# Projet de Master 1 - Industrie de la langue - Université Grenoble-Alpes      #
# Auteurs: Naja Ferreira et Marion Leteillier                                  #
# Description: Script de l'entraînement du modèle flan-t5-small                #
################################################################################

from model_faq import FAQClassifier

# Initialiser le classifieur avec le modèle par défaut (google/flan-t5-small)
modele = FAQClassifier()

# Chargement des données depuis le fichier CSV
# Par défaut, les données seront divisées en 70% train, 15% validation, 15% test
modele.charger_donnees("./dataset_faq.csv")

# Prétraitement des données textuelles pour le modèle 
# Transforme le texte en tokens numériques
modele.preparer_dataset()

# Entraînement du modèle
# Utilise les paramètres par défaut: 5 époques, patience de 2 époques pour early stopping
modele.entrainer()

# Sauvegarde du modèle et du tokenizer pour une utilisation future
modele.sauvegarder_modele("./modele_entraine_faq")

# Évaluation du modèle sur l'ensemble de validation
resultats = modele.evaluer()
print("\nRésultats de l'évaluation : ", resultats)

# Test du modèle sur un exemple aléatoire
echantillon = modele.tester_sur_un_echantillon()
print("\nExemple d'échantillon testé : ", echantillon)

# Évaluation complète sur l'ensemble de test
evaluation = modele.evaluer_ensemble_test()
print("\nPrécision sur le test : ", evaluation["precision_test"])
print("\nRapport de classification :\n", evaluation["rapport_classification"])
