################################################################################
# Document Q&A Assistant                                                       #
# Projet Portfolio - NLP & Machine Learning                                    #
# Autrice: Naja                                                                #
# Description: Interface Streamlit principale                                  #
################################################################################

import streamlit as st
import os
from pathlib import Path

# mes modules
from src.document_processor import DocumentProcessor
from src.qa_engine import QAEngine
from src.text_analyzer import TextAnalyzer
from src.visualizations import Visualizer

# config de la page streamlit
st.set_page_config(
    page_title="Document Q&A Assistant",
    page_icon="🤖",
    layout="wide"
)

# charge le CSS personnalisé
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# initialisation des classes (ça prend du temps au premier lancement)
@st.cache_resource
def charger_modeles():
    """Charge les modèles une seule fois"""
    print("Chargement des modèles...")
    
    processor = DocumentProcessor()
    qa = QAEngine()
    analyzer = TextAnalyzer()
    viz = Visualizer()
    
    return processor, qa, analyzer, viz

# titre et description
st.title("Document Q&A Assistant")
st.markdown("Assistant intelligent pour l'analyse de documents")
st.write("")  # espaço

# charge les modèles
try:
    doc_processor, qa_engine, text_analyzer, visualizer = charger_modeles()
except Exception as e:
    st.error(f"❌ Erreur lors du chargement des modèles: {e}")
    st.info("Vérifiez que tous les packages sont installés (requirements.txt)")
    st.stop()

# sidebar pour l'upload
with st.sidebar:
    st.header("📁 Uploader un document")
    
    fichier = st.file_uploader(
        "Choisissez un fichier",
        type=['pdf', 'txt', 'docx'],
        help="Formats supportés: PDF, TXT, DOCX"
    )
    
    st.markdown("---")
    st.markdown("### À propos")
    st.info("""
    Ce projet utilise:
    - **CamemBERT** pour le Q&A
    - **spaCy** pour l'analyse linguistique
    - **Plotly** pour les visualisations
    """)

# zone principale
if fichier is not None:
    
    # sauvegarde temporaire du fichier
    dossier_upload = Path("data/uploads")
    dossier_upload.mkdir(parents=True, exist_ok=True)
    
    chemin_fichier = dossier_upload / fichier.name
    with open(chemin_fichier, "wb") as f:
        f.write(fichier.getbuffer())
    
    st.success(f"✓ Fichier '{fichier.name}' chargé")
    
    # extraction du texte
    with st.spinner("Extraction du texte..."):
        try:
            texte = doc_processor.extract_text(str(chemin_fichier))
        except Exception as e:
            st.error(f"Erreur extraction: {e}")
            st.stop()
    
    if not texte or len(texte) < 10:
        st.warning("⚠️ Le document semble vide ou illisible")
        st.stop()
    
    # tabs pour organiser l'interface
    tab1, tab2, tab3 = st.tabs(["💬 Questions-Réponses", "📊 Analyse du texte", "📄 Texte brut"])
    
    # TAB 1: Q&A
    with tab1:
        st.subheader("Posez vos questions")
        
        question = st.text_input(
            "Votre question:",
            placeholder="Ex: De quoi parle ce document ?",
            key="question_input"
        )
        
        if st.button("🔍 Rechercher la réponse", type="primary"):
            if question:
                with st.spinner("Recherche en cours..."):
                    # trouve la réponse
                    resultat = qa_engine.poser_question(question, texte)
                    
                    if resultat['score'] > 0:
                        st.markdown("### 💡 Réponse trouvée:")
                        st.success(resultat['reponse'])
                        
                        # affiche le score de confiance
                        confiance = resultat['score'] * 100
                        st.metric("Confiance", f"{confiance:.1f}%")
                        
                        # montre le contexte autour de la réponse
                        if st.checkbox("Voir le contexte dans le document"):
                            debut, fin = resultat['position']
                            contexte = qa_engine.trouver_contexte(texte, debut, fin)
                            
                            st.markdown("**Extrait du document:**")
                            st.info(contexte)
                    else:
                        st.warning("❌ Pas de réponse trouvée pour cette question")
            else:
                st.warning("Entrez une question d'abord!")
    
    # TAB 2: Analyses
    with tab2:
        st.subheader("Analyse linguistique du document")
        
        with st.spinner("Analyse en cours..."):
            stats = text_analyzer.analyser_texte(texte)
        
        # statistiques basiques
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📝 Caractères", f"{stats['nb_chars']:,}")
        with col2:
            st.metric("📖 Mots", f"{stats['nb_mots']:,}")
        with col3:
            st.metric("💬 Phrases", f"{stats['nb_phrases']:,}")
        
        st.markdown("---")
        
        # deux colonnes pour les graphiques
        col_gauche, col_droite = st.columns(2)
        
        with col_gauche:
            st.markdown("#### Mots les plus fréquents")
            if stats['mots_frequents']:
                fig_freq = visualizer.graphique_frequences(stats['mots_frequents'])
                if fig_freq:
                    st.plotly_chart(fig_freq, use_container_width=True)
            
            # nuage de mots
            st.markdown("#### Nuage de mots")
            if stats['mots_frequents']:
                wc = visualizer.creer_wordcloud(stats['mots_frequents'])
                if wc:
                    st.image(wc, use_column_width=True)
        
        with col_droite:
            st.markdown("#### Types de mots (POS)")
            if stats['pos_tags']:
                fig_pos = visualizer.graphique_pos(stats['pos_tags'])
                if fig_pos:
                    st.plotly_chart(fig_pos, use_container_width=True)
            
            # entités nommées
            st.markdown("#### Entités nommées")
            if stats['entites']:
                fig_ent = visualizer.graphique_entites(stats['entites'])
                if fig_ent:
                    st.plotly_chart(fig_ent, use_container_width=True)
                
                # liste des entités trouvées
                with st.expander("Voir la liste des entités"):
                    for ent in stats['entites'][:20]:  # limite à 20
                        st.write(f"- **{ent['texte']}** ({ent['type']})")
            else:
                st.info("Aucune entité nommée détectée")
        
        # bigrammes en bas
        st.markdown("---")
        st.markdown("#### Expressions fréquentes (bigrammes)")
        with st.spinner("Calcul des bigrammes..."):
            bigrammes = text_analyzer.extraire_bigrammes(texte, top=15)
        
        if bigrammes:
            fig_bg = visualizer.graphique_frequences(
                bigrammes,
                titre="Paires de mots fréquentes"
            )
            if fig_bg:
                st.plotly_chart(fig_bg, use_container_width=True)
    
    # TAB 3: Texte brut
    with tab3:
        st.subheader("Contenu du document")
        
        # montre un extrait par défaut
        nb_chars_preview = 2000
        if len(texte) > nb_chars_preview:
            st.text_area(
                "Aperçu (premiers 2000 caractères):",
                texte[:nb_chars_preview] + "\n\n[...]",
                height=400
            )
            
            if st.checkbox("Afficher tout le texte"):
                st.text_area("Texte complet:", texte, height=600)
        else:
            st.text_area("Texte complet:", texte, height=400)

else:
    # page d'accueil quand pas de fichier
    st.info("👈 Uploadez un document dans la barre latérale pour commencer")
    
    st.markdown("### 🎯 Fonctionnalités")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Questions-Réponses:**
        - Posez des questions en français
        - Réponses basées sur CamemBERT
        - Localisation dans le document
        - Score de confiance
        """)
    
    with col2:
        st.markdown("""
        **Analyse linguistique:**
        - Statistiques du texte
        - Mots les plus fréquents
        - Entités nommées (NER)
        - Nuage de mots
        - Types de mots (POS tags)
        """)
    
    st.markdown("---")
    st.markdown("*Projet réalisé avec Streamlit, spaCy, Transformers et Plotly*")