\# Document Q\&A Assistant



Assistant intelligent de questions-réponses sur des documents en utilisant le NLP et les Large Language Models.



\## À propos



Ce projet permet de télécharger des documents (PDF, TXT, DOCX) et de poser des questions en langage naturel. Le système utilise des modèles de langage pour extraire des réponses contextualisées et fournit des analyses linguistiques détaillées du corpus.



\## Fonctionnalités



\- Upload de documents (PDF, TXT, DOCX)

\- Questions-réponses en langage naturel

\- Analyse linguistique du texte (entités nommées, fréquences)

\- Visualisations interactives (nuage de mots, graphiques)

\- Localisation des réponses dans le document source

\- Export des analyses en Excel



\## Technologies utilisées



\- \*\*Python\*\* : Langage principal

\- \*\*Streamlit\*\* : Interface web interactive

\- \*\*Transformers (Hugging Face)\*\* : Modèles de langage pour Q\&A

\- \*\*spaCy\*\* : Analyse linguistique et NER

\- \*\*PyTorch\*\* : Framework de deep learning

\- \*\*Plotly\*\* : Visualisations interactives

\- \*\*openpyxl\*\* : Export Excel



\## Installation

```bash

pip install -r requirements.txt

python -m spacy download fr\_core\_news\_sm

```



\## Utilisation

```bash

streamlit run app.py

```



\## Structure du projet

```

document-qa-assistant/

├── app.py                      # Application principale

├── src/

│   ├── document\_processor.py   # Traitement des documents

│   ├── qa\_engine.py            # Moteur de questions-réponses

│   ├── text\_analyzer.py        # Analyse linguistique

│   └── visualizations.py       # Génération de graphiques

├── data/                       # Données temporaires

└── requirements.txt            # Dépendances

```



\## Auteur



Projet réalisé dans le cadre de mon portfolio personnel.

