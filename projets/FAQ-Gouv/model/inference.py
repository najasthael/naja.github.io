################################################################################
# Fine-Tuning Projet FAQ-Gouv                                                  #
# Projet de Master 1 - Industrie de la langue - Université Grenoble-Alpes      #
# Auteurs: Naja Ferreira et Marion Leteillier                                  #
# Description: Script d'inférence pour la classification                       #
################################################################################


from transformers import pipeline

# Chargement du modèle entraîné et de son tokenizer
# pipeline est une fonction HuggingFace qui simplifie l'utilisation des modèles
classifier = pipeline(
    "text-classification",              # Type de tâche - classification de texte
    model="./modele_entraine_faq",      # Chemin vers le modèle sauvegardé
    tokenizer="./modele_entraine_faq"   # Chemin vers le tokenizer (même dossier que le modèle)
)

# Demande à l'utilisateur d'entrer un texte à classifier
texte = input("Posez une question ou insérez un contenu et le modèle va faire la classification: ")

# Utilisation du modèle pour prédire la classe du texte entré
# Le résultat inclut l'étiquette (label) et le score de confiance
resultat = classifier(texte)

# Affichage du résultat
print(resultat)

# Attente d'une entrée utilisateur pour garder la fenêtre ouverte
sortie = input("Appuyez sur une touche pour quitter...")