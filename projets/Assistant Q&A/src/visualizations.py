################################################################################
# Document Q&A Assistant                                                       #
# Projet Portfolio - NLP & Machine Learning                                    #
# Autrice: Naja                                                                #
# Description: Génération de graphiques (wordcloud, barres, etc.)             #
################################################################################

import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO
import base64

class Visualizer:
    
    def __init__(self):
        # config de base pour les graphiques
        self.couleurs = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
    
    def creer_wordcloud(self, frequences):
        """Génère un nuage de mots à partir des fréquences"""
        
        if not frequences:
            return None
        
        # transforme la liste de tuples en dict pour wordcloud
        freq_dict = dict(frequences)
        
        # config du wordcloud - j'ai testé plusieurs tailles
        wc = WordCloud(
            width=800,
            height=400,
            background_color='white',
            colormap='viridis',  # j'aime bien cette palette
            max_words=50
        ).generate_from_frequencies(freq_dict)
        
        # sauvegarde en base64 pour l'afficher dans streamlit
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        
        # conversion en image pour streamlit
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        return buf
    
    def graphique_frequences(self, frequences, titre="Mots les plus fréquents"):
        """Crée un graphique à barres des fréquences"""
        
        if not frequences or len(frequences) == 0:
            return None
        
        # sépare mots et comptes
        mots = [f[0] for f in frequences[:15]]  # limite à 15 pour la lisibilité
        comptes = [f[1] for f in frequences[:15]]
        
        # graphique horizontal (plus lisible pour les mots longs)
        fig = go.Figure(data=[
            go.Bar(
                y=mots[::-1],  # inverse pour avoir les + fréquents en haut
                x=comptes[::-1],
                orientation='h',
                marker=dict(color='#2ca02c')
            )
        ])
        
        fig.update_layout(
            title=titre,
            xaxis_title="Fréquence",
            yaxis_title="",
            height=500,
            margin=dict(l=150)  # marge gauche pour les longs mots
        )
        
        return fig
    
    def graphique_entites(self, entites):
        """Graphique des types d'entités trouvées"""
        
        if not entites:
            return None
        
        # compte les types d'entités
        types_ent = {}
        for ent in entites:
            type_e = ent['type']
            types_ent[type_e] = types_ent.get(type_e, 0) + 1
        
        if not types_ent:
            return None
        
        # camembert pour les entités (plus visuel)
        fig = go.Figure(data=[
            go.Pie(
                labels=list(types_ent.keys()),
                values=list(types_ent.values()),
                hole=0.3  # donut chart, plus moderne
            )
        ])
        
        fig.update_layout(
            title="Distribution des entités nommées",
            height=400
        )
        
        return fig
    
    def graphique_pos(self, pos_dict):
        """Distribution des parties du discours"""
        
        if not pos_dict:
            return None
        
        # trie par fréquence décroissante
        pos_sorted = sorted(pos_dict.items(), key=lambda x: x[1], reverse=True)
        
        # prend que les 10 premiers pour pas surcharger
        pos_sorted = pos_sorted[:10]
        
        categories = [p[0] for p in pos_sorted]
        valeurs = [p[1] for p in pos_sorted]
        
        fig = px.bar(
            x=categories,
            y=valeurs,
            labels={'x': 'Type', 'y': 'Nombre'},
            title="Types de mots (POS tags)",
            color=valeurs,
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(height=400)
        
        return fig