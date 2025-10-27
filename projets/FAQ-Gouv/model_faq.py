################################################################################
# Fine-Tuning Projet FAQ-Gouv                                                  #
# Projet de Master 1 - Industrie de la langue - Université Grenoble-Alpes      #
# Auteurs: Naja Ferreira et Marion Leteillier                                  #
# Description: Script de l'entraînement du modèle flan-t5-small                #
################################################################################

from datasets import Dataset, DatasetDict
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments, EarlyStoppingCallback
from sklearn.metrics import accuracy_score, classification_report
import numpy as np
import pandas as pd
import os
from random import choice

class FAQClassifier:
    def __init__(self, modele_nom="google/flan-t5-small", num_labels=2):
        """
        Initialise le classifieur FAQ avec un modèle pré-entraîné.
        
        Arguments:
            modele_nom: Nom du modèle à utiliser (le notre: google/flan-t5-small)
            num_labels: Nombre de catégories pour la classification (catégories binaires)
        """
        # Désactive le parallélisme des tokenizers qui peut causer des problèmes        
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        # Désactive Weights & Biases pour éviter des logs inutiles
        os.environ["WANDB_DISABLED"] = "true"

        # Charge le tokenizer du modèle à travers Hugging Face
        self.tokenizer = AutoTokenizer.from_pretrained(modele_nom)

        #Charge le modèle Flan-T5-small avec les deux catégories
        self.model = AutoModelForSequenceClassification.from_pretrained(modele_nom, num_labels=num_labels)

    def charger_donnees(self, chemin_csv, decoupage=(0.7, 0.15, 0.15)):

        """
        Charge les données depuis un CSV et les divise en ensembles train(70%)/validation(15%)/test(15%).
        
        Arguments:
            chemin_csv: Chemin vers le fichier CSV contenant les données
            decoupage: Proportions pour la division des données (train, validation, test)
        """


        # Charge le CSV dans un DataFrame pandas
        df = pd.read_csv(chemin_csv)

        # Calcule les indices des lignes du dataser pour les repartir
        train_fin = int(decoupage[0] * len(df))
        val_fin = int((decoupage[0] + decoupage[1]) * len(df))

        # Découpe le DataFrame en trois parties selon les indices des lignes
        train_df = df.iloc[:train_fin]
        val_df = df.iloc[train_fin:val_fin]
        test_df = df.iloc[val_fin:]

        # Convertit les DataFrames en objets Dataset de HuggingFace
        train_dataset = Dataset.from_pandas(train_df)
        val_dataset = Dataset.from_pandas(val_df)
        test_dataset = Dataset.from_pandas(test_df)

        # Création d'un dictionnaire Hugging Face avec les données
        self.dataset = DatasetDict({
            'train': train_dataset,
            'validation': val_dataset,
            'test': test_dataset
        })

    def preprocess(self, exemples):

        """
        Prétraite les exemples pour les adapter au format attendu par le modèle.
        
        Arguments:
            exemples: Dictionnaire d'exemples du dataset
            
        Retourne:
            Dictionnaire avec les entrées tokenisées et les labels
        """
        
        # Récupère les questions et réponses du dataset, avec une solution de secours (fallback)
        # si ces champs sont absents: utilise des listes vides de la taille du nombre d'étiquettes
        questions = exemples.get("question", [""] * len(exemples["gouvernement"]))
        reponses = exemples.get("reponse", [""] * len(exemples["gouvernement"]))

        textes_entree = []
        # Combine chaque paire question/réponse en un seul texte d'entrée
        for q, r in zip(questions, reponses):
            if isinstance(q, list):
                q = " ".join(q)
            if isinstance(r, list):
                r = " ".join(r)

            # Gestion des cas où les champs sont des listes
            # Certains champs dans le dataset peuvent être des listes de strings au lieu de strings simples
            # Cette partie convertit ces listes en chaînes de caractères uniques en les joignant
            if q and r:
                # Utilise un séparateur || pour distinguer question et réponse
                textes_entree.append(q + " || " + r)
            elif q:
                textes_entree.append(q)
            elif r:
                textes_entree.append(r)
            else:
                textes_entree.append("")

        # Tokenisation des textes d'entrée (conversion en IDs numériques)
        # max_length: tronque les textes trop longs à cette longueur
        # truncation: autorise la troncature
        # padding: ajoute des tokens de padding jusqu'à max_length
        model_inputs = self.tokenizer(
            textes_entree,
            max_length=512,
            truncation=True,
            padding="max_length"
        )

        # Ajoute les étiquettes (0 = non gouvernemental, 1 = gouvernemental)
        model_inputs["labels"] = exemples["gouvernement"]
        return model_inputs

    def preparer_dataset(self):
        """
        Applique la fonction de prétraitement à l'ensemble du dataset.
        Transforme le texte brut en tenseurs pour l'entraînement.
        """

        # map applique la fonction preprocess sur tout le dataset de façon optimisée
        self.dataset_tokenise = self.dataset.map(self.preprocess, batched=True)

    def compute_metrics(self, p):
        """
        Calcule les métriques d'évaluation à partir des prédictions.
        
        Arguments:
            p: Objet contenant predictions et labels
            
        Retourne:
            Dictionnaire avec les métriques calculées
        """
        # p.predictions contient les logits (scores bruts) du modèle
        # Les logits sont les sorties brutes de la dernière couche du modèle avant toute fonction d'activation
        # Pour une classification binaire, chaque exemple a deux logits:
        #   - Premier logit (indice 0): score pour la classe "non gouvernemental"
        #   - Second logit (indice 1): score pour la classe "gouvernemental"
        # La classe avec le score le plus élevé (déterminée par argmax) est considérée comme la prédiction'
        logits = p.predictions

        # Les sorties de certains modèles de Hugging Face peuvent parfois contenir les logits
        # dans un tuple avec d'autres informations (comme hidden_states, attentions, etc.)
        # Cette ligne vérifie si on a reçu un tuple et, si oui, extrait uniquement les logits
        # qui sont toujours le premier élément du tuple
        if isinstance(logits, tuple):
            logits = logits[0]

        # Classification binaire: transforme les logits en prédictions de classe
        # Les logits sont [score_classe_0, score_classe_1] pour chaque exemple
        # argmax donne l'indice du score le plus élevé (0 ou 1)
        if logits.shape[-1] == 2:
            preds = np.argmax(logits, axis=1)
        else:
            # Situation où il n'y a qu'un logit
            preds = logits.squeeze()

        # Calcule l'accuracy en comparant les prédictions aux vraies étiquettes    
        return {"accuracy": accuracy_score(p.label_ids, preds)}

    def entrainer(self, output_dir="./results", epochs=5, patience=2):
        """
        Configure et lance l'entraînement du modèle.
        
        Arguments:
            output_dir: Répertoire où sauvegarder les résultats
            epochs: Nombre d'époques d'entraînement
            patience: Nombre d'époques sans amélioration avant arrêt précoce
            (Le paramètre patience définit combien d'époques consécutives sans amélioration
            de la métrique de validation sont tolérées avant d'arrêter l'entraînement.
            Un patience=2 signifie qu'on arrête si après 2 époques la précision ne s'améliore plus)
        """
        # Configuration de tous les hyperparamètres d'entraînement
        args = TrainingArguments(
            output_dir=output_dir,
            eval_strategy="epoch",
            save_strategy="epoch",
            learning_rate=2e-5,
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            num_train_epochs=epochs,
            weight_decay=0.01,
            logging_dir="./logs",
            logging_steps=10,
            load_best_model_at_end=True,
            metric_for_best_model="accuracy",
        )

        # Création du Trainer qui va gérer l'entraînement et l'évaluation
        self.trainer = Trainer(
            model=self.model,
            args=args,
            train_dataset=self.dataset_tokenise["train"],
            eval_dataset=self.dataset_tokenise["validation"],
            compute_metrics=self.compute_metrics,  # Fonction de calcul des métriques
            callbacks=[EarlyStoppingCallback(early_stopping_patience=patience)], # Arrêt précoce
        )

        # Appel de l'entraînement
        self.trainer.train()

    def sauvegarder_modele(self, chemin="./modele_entraine_faq"):
        """
        Sauvegarde le modèle entraîné et son tokenizer pour une utilisation future.
        
        Arguments:
            chemin: Chemin où sauvegarder le modèle
        """
        self.trainer.save_model(chemin)
        self.tokenizer.save_pretrained(chemin)

    def evaluer(self):
        """
        Évalue le modèle sur l'ensemble de validation.
        
        Retourne:
            Dictionnaire avec les métriques d'évaluation
        """
        return self.trainer.evaluate()

    def tester_sur_un_echantillon(self):
        """
        Teste le modèle sur un exemple aléatoire de l'ensemble de test.
        
        Returns:
            Dictionnaire avec l'exemple, la classe attendue et la prédiction
        """
        # Choisir un échantillon aléatoire du dataset
        echantillon = choice(self.dataset["test"])

        texte_entree = echantillon["question"]
        classe_attendue = echantillon["gouvernement"]

        # Tokeniser et faire l'inférence avec le modèle
        input_ids = self.tokenizer(texte_entree, return_tensors="pt").input_ids.to(self.model.device)
        outputs = self.model(input_ids)

        # Les logits sont les scores bruts (non normalisés) pour chaque classe
        logits = outputs.logits
        # Convertir les logits en prédiction de classe avec argmax
        id_classe_prevue = logits.argmax(axis=-1).item()

        # Traduire les IDs numériques en noms de catégories lisibles
        if id_classe_prevue == 1:
            categorie_predite = "gouvernemental"
        else:
            categorie_predite = "non gouvernemental"

        # Traduire aussi la classe attendue si nécessaire
        if classe_attendue == 1:
            categorie_attendue = "gouvernemental"
        else:
            categorie_attendue = "non gouvernemental"

        return {
            "contenu": texte_entree,
            "attendue": categorie_attendue,
            "categorie_predite": categorie_predite
        }


    def evaluer_ensemble_test(self):
        """
        Évalue le modèle sur l'ensemble de test complet.
        
        Returns:
            Dictionnaire avec précision, rapport de classification et résultats détaillés
        """
        predictions = []
        references = []
        resultats = []

        # Parcourt tous les exemples du jeu de test
        for echantillon in self.dataset["test"]:
            texte_entree = echantillon["question"]
            classe_attendue = echantillon["gouvernement"]

            # Tokeniser et prédire comme dnas tester_sur_un_echantillon
            input_ids = self.tokenizer(texte_entree, return_tensors="pt").input_ids.to(self.model.device)
            outputs = self.model(input_ids)
            logits = outputs.logits if hasattr(outputs, "logits") else outputs[0]

            # Convertir les logits en prédiction de classe
            if logits.shape[-1] == 2:
                id_classe_prevue = logits.argmax(axis=-1).item()
            else:
                id_classe_prevue = (logits > 0).int().item()

            # Traduire la classe prévue
            categorie_predite = "gouvernemental" if id_classe_prevue == 1 else "non gouvernemental"
            categorie_attendue = "gouvernemental" if classe_attendue == 1 else "non gouvernemental"

            # Stocker pour les métriques
            predictions.append(id_classe_prevue)
            references.append(classe_attendue)

            # Stocker le détail pour l'affichage
            resultats.append({
                "contenu": texte_entree,
                "attendue": categorie_attendue,
                "categorie_predite": categorie_predite
            })

        # Calculer précision et fair un rapport
        precision = accuracy_score(references, predictions)
        rapport = classification_report(references, predictions, target_names=["Non gouvernemental", "Gouvernemental"], zero_division=0)

        return {
            "precision_test": precision,
            "rapport_classification": rapport,
            "resultats_detail": resultats
        }
