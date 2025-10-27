# TP_PythonAlgo_MarionNaja

## FAQ_Gouv

### Contexte
Dans le cadre du Master 1 Industrie de la langue, ce projet a pour objectif de mettre en œuvre une chaîne de traitement de données textuelles, depuis l'extraction des données via le web scraping jusqu'à la classification supervisée à l'aide d'un modèle Transformer.

## Objectifs
1. **Constitution du corpus** - Nous avons extrait des paires questions-réponses à partir de sites web du gouvernement français à l'aide des bibliothèques BeautifulSoup et Selenium.
2. **Entraînement du classificateur** - Nous avons entraîné le transformer Flan_T5_small afin de distinguer si une question provient ou non d'un site gouvernemental.
3. **Création d'une API** Elle a été développée afin d'effectuer des inférences sur de nouvelles entrées textuelles.

## Choix du modèle
Modèle sélectionné : google/flan-t5-small

Nous avons choisi le modèle flan-t5-small pour plusieurs raisons:

  - Taille réduite : Avec environ 80 millions de paramètres, il est assez léger pour s'entraîner rapidement sur nos ressources limitées, tout en offrant de bonnes performances.
  - Architecture T5 : Le modèle T5 (Text-to-Text Transfer Transformer) traite toutes les tâches NLP comme des problèmes de conversion texte-à-texte. Cela le rend polyvalent et adapté à notre tâche de classification.
  - Pré-entraînement Flan : La version Flan de T5 a été fine-tunée sur des instructions en langage naturel, ce qui améliore ses capacités de compréhension du français et de généralisation.
  - Équilibre performance/ressources : Ce modèle constitue un bon compromis entre performance, efficacité et besoins en ressources computationnelles, permettant d'obtenir de bons résultats sans nécessiter de GPU haut de gamme.

Pour l'adapter à notre tâche de classification binaire, nous avons ajouté une tête de classification personnalisée qui convertit les représentations du modèle en logits pour nos deux catégories : gouvernemental et non-gouvernemental.

## Structure du projet
  → dataset_faq.csv - Corpus structuré : question, réponse, étiquette

  → appel-scraper.ipynb - Script appelant le scraping (notebook Jupyter)

  → inference.py - Script d'inférence locale avec pipeline

  → model_faq.py - Classe définissant le modèle de classification utilisant Flan-T5-small et ses paramètres d'entraînement

  → modelo_entraine_faq/ - Répertoire avec le modèle fine-tuné sauvegardé

  → README.md - Ce fichier, contenant la description du projet

  → scraper.py - Script de scraping avec 12 fonctions

  → train.py - Script d'entraînement et d'évaluation du modèle

## Structures de données manipulées

### Datasets
- **DatasetDict (HuggingFace)** : Ensemble structuré contenant les 3 sous-ensembles train/validation/test
- **Dataset** : Chaque sous-ensemble contient des exemples avec :
  - question : Texte de la question (str)
  - réponse : Texte de la réponse associée (str) 
  - gouvernement : Étiquette binaire (0 = non-gouvernemental, 1 = gouvernemental)

### Tokenizer
  - **Tokenizer** : Convertit le texte en tokens numériques
  - Utilise `||` pour séparer questions et réponses
  - Génère :
  - `input_ids`: IDs numériques des tokens
  - `attention_mask`: Masque pour distinguer tokens réels et padding
  - Troncature à 512 tokens maximum

### Logits et sorties du modèle
  - **Logits** : Scores bruts non normalisés sortant du modèle
  - Format pour classification binaire: `[score_classe_0, score_classe_1]`
  - La classe prédite correspond à l'indice du score le plus élevé avec (argmax)
  - **ModelOutput** : Sortie complète du modèle contenant :
  - `logits`: Scores par classe
  - Autres informations comme `hidden_states`, `attentions` (si demandées)

    Les logits sont les sorties brutes du modèle, avant l'application d'une fonction d'activation comme softmax :

      - Format : Pour chaque exemple, le modèle retourne un vecteur de taille 2 : [score_classe_0, score_classe_1]
      - Interprétation :

          score_classe_0 : Score pour la catégorie "non-gouvernemental"
          score_classe_1 : Score pour la catégorie "gouvernemental"

      - Prédiction : La classe prédite correspond à l'indice du score le plus élevé (via la fonction argmax)
      - Exemple : Avec des logits [0.2, 3.7], la classe prédite sera 1 (gouvernemental)

    Ce format brut permet non seulement de déterminer la classe prédite, mais aussi d'évaluer la confiance du modèle dans sa prédiction en comparant les valeurs des deux scores.


## Architecture du modèle
  - **Modèle de base** : google/flan-t5-small
  - **Transformation** : Ajout d'une tête de classification pour la tâche binaire
  - **Couches ajoutées** :
  - Dense (projection linéaire)
  - Couche de sortie (logits)

## Évaluation des performances
  - **Métriques principales** : 
  - Accuracy globale
  - Précision par classe
  - Rappel par classe
  - F1-score par classe
  - **Procédure** : Évaluation sur l'ensemble de test après entraînement

## Organisation des fichiers
  - `model_faq.py`: Définition de la classe du modèle
  - `scraper.py`: Fonctions de scraping pour collecter les données
  - `train.py`: Script d'entraînement
  - `inference.py`: Démonstration d'inférence sur de nouvelles données
  - `dataset_faq.csv`: Jeu de données collecté et prétraité

## Difficultés rencontrées et solutions
  - **Déséquilibre des classes** : Implémentation de techniques de rééquilibrage
  - **Variations des structures HTML** : Adaptation des fonctions de scraping par site
  - **Encodage des caractères** : Utilisation de UTF-8-SIG pour préserver les accents

## Outils de scraping
GeckoDriver
Pour la collecte des données, nous avons utilisé Selenium avec GeckoDriver comme interface avec le navigateur Firefox :

  - Rôle : GeckoDriver est un pilote qui permet à Selenium d'interagir avec Firefox pour automatiser la navigation et l'extraction de données de sites web.
  - Fonctionnement : Il agit comme un proxy entre Selenium et Firefox, traduisant les commandes Selenium en actions concrètes dans le navigateur.
  - Installation : Le fichier exécutable geckodriver.exe doit être présent dans le répertoire du projet ou dans le PATH du système.
  - Configuration en mode headless : Nous avons configuré Firefox en mode headless (sans interface graphique) pour optimiser les performances et permettre l'exécution sur des serveurs sans affichage.


## Description de l'API (Mini-cahier des charges)

### scraper.py
Ensemble de fonctions indépendantes qui font le scraping de plusieurs sites différents à travers BeautifulSoup et Selenium. Le script courant ne fonctionne que sur Mozilla Firefox.
- **`demarre_driver()`**
  Lance un navigateur Firefox en mode headless.
- **`enregistrer_csv(donnees, nom_fichier)`**
  Enregistre les résultats des fonctions `data_1()` à `data_12()` dans un fichier CSV en entourant le contenu des colonnes "question", "reponse" et "gouvernement" entre guillemets. Les données sont encodées en _utf-8-sig_ pour garantir la bonne visualisation sur les principaux outils.
- **`data_1() à data_12()`**
  Fonctions spécifiques pour extraire les données de sites divers (gouvernementaux et non gouvernementaux).
  À la fin de chaque fonction, les données sont séparées entre les colonnes "question", "reponse" et "gouvernement", tout en attribuant les valeurs 0 ou 1 selon l'origine gouvernnementale du site.


### appel_scraper.py
Script qui fait appel aux fonctions issues de `scraper.py`. Il permet de contrôler les appels aux fonctions de scraping par activation/désactivation via des commentaires.


### model_faq.py
Contient une classe appelée FAQClassifier, avec plusieurs méthodes qui permettent :
- de charger et préparer les données (`charger_donnees`, `preparer_dataset`, `preprocess`) ;
- d'entraîner et évaluer le modèle (`entrainer`, `evaluer`, `compute_metrics`) ;
- d'effectuer des prédictions ou de sauvegarder le modèle (`tester_sur_un_echantillon`, `sauvegarder_modele`).

- **`def __init__(self, modele_nom="google/flan-t5-small", num_labels=2):`**
  Cette fonction charge le modèle à travers l'argument _modele_nom_.
  L'argument _num_label_ spécifie le nombre de catégories dans le dataset.
- **`def charger_donnees(self, chemin_csv, decoupage=(0.7, 0.15, 0.15)):`**
  La fonction charge le dataset en CSV. L'argument _chemin_csv_ vient du fichier _train.py_ et montre le dossier où se trouve le ficher du dataset.
  L'argument _decoupage_ définit la proportion de distribution des données entre entraînement (70%), validation (15%) et test (15%). Il s'agit d'une proportion standard pour les entraînements des Transformers.
  Dans la fonction, les données sont donc réparties, puis la classe _Dataset_ venant de _HuggingFace_ les adapte au format d'entraînement propre à cette plateforme.
  Enfin, les lignes du dataset sont mises dans un dictionnaire par _DatasetDict_, également une classe de la bibliothèque de Hugging Face.
- **`def preprocess(self, exemples):`**
  Cette fonction prépare les données textuelles avant l'entraînement.
  Elle applique un tokenizer spécifique au modèle Flan-T5-small afin de transformer les questions et étiquettes du dataset en séquences numériques (tokens) compatibles avec le modèle.
  Plus précisément, chaque question est introduite comme une entrée (input_ids), tandis que la classe attendue (gouvernementale ou non) est convertie en label numérique.
  Le tokenizer applique aussi des règles comme la troncature (pour limiter la longueur) et le padding (pour égaliser les tailles de séquence).
- **`def preparer_dataset(self):`**
  Dans cette fonction, la méthode `map` de la classe Dataset (Hugging Face) applique la fonction preprocess à chaque exemple du corpus (train, validation, test). Cela permet de transformer l’ensemble du jeu de données de manière vectorisée. C'est aussi cette fonction qui envoie l'argument _exemples_ à `def preprocess`.
- **`def compute_metrics(self, p):`**
  Cette méthode permet de calculer la précision (accuracy) du modèle après chaque phase d’évaluation. Elle est appelée automatiquement par le Trainer de Hugging Face pendant l’entraînement ou les tests. L'attribut d'instance `p.predictions` (de la classe `EvalPrediction`) contient les sorties brutes du modèle (logits).
- **`def entrainer(self, output_dir="./results", epochs=5, patience=2):`**
  Cette méthode lance le fine-tuning du modèle Flan-T5-small à partir des données préparées.
  Elle utilise la classe Trainer de Hugging Face, qui automatise les étapes d'entraînement, validation et évaluation.
  L'argument `output_dir` définit où les resultats de l'entraînement seront sauvegardés, `epoch` détermine combien de fois il fera des époques, `patience` établit le _early stopping_.
- **`def sauvegarder_modele(self, chemin="./modele_entraine_faq"):`**
  Cette méthode d’instance permet de sauvegarder l’état du modèle fine-tuné ainsi que le tokenizer associé dans un dossier local. L’argument chemin est un paramètre qui définit le répertoire de sortie où seront enregistrés les fichiers du modèle. La méthode utilise les méthodes save_pretrained() du modèle et du tokenizer de Hugging Face, ce qui rend les fichiers réutilisables avec from_pretrained() plus tard.
- **`def evaluer(self):`**
  La méthode courante évalue la performance à partir de l'ensemble de validation. Elle appelle la méthode `.evaluate()` du Trainer de Hugging Face, qui retourne automatiquement les métriques calculées par `compute_metrics`, telles que la précision (accuracy).
  Cette étape est utile pour surveiller l’apprentissage pendant l'entraînement, notamment lorsqu’on utilise un EarlyStoppingCallback.
- **`def evaluer_ensemble_test(self):`**
  Cette méthode permet d’évaluer le modèle final sur le jeu de test, afin de mesurer sa généralisation.
  Elle utilise également le `Trainer` `.evaluate()` mais applique des métriques supplémentaires (comme le classification_report de sklearn) pour obtenir plus de détails sur la performance par classe.
  Les résultats affichent la précision, le rappel et le F1-score.
- **`def tester_sur_un_echantillon(self):`**
  Méthode pratique pour tester rapidement le modèle sur un exemple tiré au hasard du jeu de test.
  Elle affiche la question, la classe attendue, la prédiction du modèle, ainsi que la précision globale.
  Cela permet de vérifier manuellement la cohérence du modèle.

### train.py
Script qui fait appel aux fonctions issues de `model_faq.py`


## Résultats des tests
Des évaluations ont été réalisées à partir de jeux de données de tailles et d’équilibres différents, au fur et à mesure que l'on augmentait la taille du dataset :


|  Fichier  | Taille test | Accuracy |                               Commentaire                                  |
|------------|-------------|----------|------------------------------------------------------------------------------|
| test1.txt |     84      |  84,5 %  | Données déséquilibrées (686/147)                                           |
| test2.txt |     716     |  96,2 %  | Corpus large à cause d'une erreur lors de l'union des scrapings dans un seul csv et bien étiqueté                                              |
| test3.txt |     143     |  79,7 %  | Mauvaise détection de la classe minoritaire                                |
| test4.txt |     145     |  71,7 %  | F1-score élevé sur la classe majoritaire uniquement                        |
| test5.txt |     180     |  43 %    | Très bon rappel pour "non gouvernemental", mais faible performance globale |
| test6.txt |     180     |  67,8 %  | Accuracy final assez satisfaisante, avec une tendance pour la classe "gouvernemental", mais pouvant s'améliorer avec plus de données                                                                            |


	
## Des améliorations pour le futur

    Ajouter une interface web pour l’API.
    Étendre le scraping et fine-tuning à d'autres langues (multilingue).
    Intégrer Chrome comme alternative à Firefox lors du scraping.
    Intégration de nouvelles sources de données non gouvernementales
    Intégration complète et automatique des csv générés lors du scraping
    Évaluation sur d'autres tâches comme la détection de thème
    Augmenter la quantité et équilibrer des données

## Utilisation

  1. Scraping : Exécuter les fonctions dans appel-scraper.py ou rajouter des fonctions sur scraper.py pour augmenter le corpus.
  2. Entraînement :

    python train.py

  3. Inférence locale (il faut avoir déjà entraîné le modèle):

    python inference.py

## Technologies utilisées
  - Pandas
  - NumpPy
  - Selenium
  - BeautifulSoup
  - Requests
  - Transformers (Hugging Face)
  - Datasets (Hugging Face)
  - Scikit-learn
  - CSV
  - RE
  - OS
  - SYS



## Support
En cas de besoin, vous pouvez nous contacter via la plateforme pédagogique ou ouvrir une issue dans le dépôt GitLab.
    

## Contribution
Les contributions sont bienvenues ! Veuillez respecter les conventions de nommage et documenter vos ajouts. Pour commencer :

    Forker le projet
    Créer une branche dédiée
    Ajouter vos modifications
    Soumettre une merge request

## Auteurs
Cette API a été développée par Marion Leteillier et Naja Ferreira, dans le cadre du Master 1 Industries de la Langue (Université Grenoble Alpes, 2024–2025).


## Statut du projet
Le projet est actif dans le cadre du semestre S2. Des évolutions futures sont possibles selon la réutilisation dans d’autres contextes académiques ou professionnels.
