################################################################################
# Fine-Tuning Projet FAQ-Gouv                                                  #
# Projet de Master 1 - Industrie de la langue - Université Grenoble-Alpes      #
# Auteurs: Naja Ferreira et Marion Leteillier                                  #
# Description: Script qui fait le scraping.                                    #
################################################################################

import csv
import time
import re
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import requests


# Fonction pour démarrer le driver Selenium avec Firefox
def demarre_driver():
    """
    Initialise et configure le driver Selenium pour Firefox.
    
    Returns:
        WebDriver: Instance du driver Firefox configuré, ou None en cas d'erreur
    """
    options = Options()
    options.headless = True  # Fait le scraping sans ouvrir la fenêtre du navigateur
    geckodriver = Service("C:/Users/Naja/Downloads/geckodriver.exe")  # Chemin du Geckodriver
    try:
        driver = webdriver.Firefox(service=geckodriver, options=options)
        return driver
    except Exception as e:
        # Gestion des exceptions - affiche l'erreur et retourne None
        print(f"Erreur du driver de Selenium : {e}")
        return None

# Fonction pour enregistrer les données dans un fichier CSV
def enregistrer_csv(donnees, nom_fichier):
    """
    Enregistre les données scrapées dans un fichier CSV.
    
    Args:
        donnees: Liste de dictionnaires contenant les données à sauvegarder
        nom_fichier: Nom du fichier CSV de destination
    """
    try:
        with open(nom_fichier, mode='a', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['question', 'reponse', 'gouvernement'], quoting=csv.QUOTE_ALL)
            f.seek(0, 2)  # Positionne le curseur à la fin du fichier
            if f.tell() == 0:
                # Première ligne avec les noms des colonnes, si elle est vide
                writer.writeheader()
            # Écrit toutes les lignes de données
            writer.writerows(donnees)
    except Exception as e:
        print(f"Erreur lors de l'enregistrement du CSV {nom_fichier}: {e}")

def data_1(driver, url, source_gouv=True):
    """
    Scrape les FAQ du site service-public.fr.
    
    Args:
        driver: Instance WebDriver Selenium
        url: URL de la FAQ à scraper
        source_gouv: Booléen indiquant si c'est un site gouvernemental (True par défaut)
    """
    try:
        driver.get(url)
        # Pause pour laisser le site se charger complètement
        time.sleep(5) 
        # Analyse du HTML avec BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Extraction des éléments contenant les questions
        li_elements = soup.select('li[data-test="reference"]')
        resultats = []
        
        for li in li_elements:
            try:
                a = li.find('a')
                if a:
                    # Récupère le texte de la question
                    question = a.get_text(strip=True)
                    # Suit le lien vers la page de réponse
                    driver.get(a['href']) 

                    try:
                        # Attend que le contenu de la réponse soit chargé (max 10 secondes)
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "p[data-test='contenu-texte']"))
                        )
                        # Analyse la page de réponse
                        sous_soup = BeautifulSoup(driver.page_source, 'html.parser')
                        # Sélectionne tous les paragraphes contenant la réponse
                        contenu_html_list = sous_soup.select("p[data-test='contenu-texte']")
                        # Joint tous les paragraphes en un seul texte
                        reponse = "\n".join([p.get_text(separator='\n', strip=True) for p in contenu_html_list]) if contenu_html_list else "[SANS CONTENU]"
                    except Exception as e:
                        # Gère les exceptions - timeout ou élément non trouvé
                        reponse = f"[ERREUR AU CHARGEMENT DU CONTENU] {str(e)}"

                    # Ajoute les données à la liste de résultats
                    resultats.append({
                        'question': question,
                        'reponse': reponse,
                        'gouvernement': 1 if source_gouv else 0  # 1 pour gouvernemental, 0 pour non-gouvernemental
                    })
            except Exception as e:
                print(f"Erreur lors du traitement d'un élément de data_1: {e}")

        # Sauvegarde les résultats dans un fichier CSV
        enregistrer_csv(resultats, 'data_gouv_1.csv')
    except Exception as e:
        print(f"Erreur générale dans data_1: {e}")

def data_2(driver, url, source_gouv=True):
    """Extrait les FAQs du site culture.gouv.fr"""
    try:
        driver.get(url)
        time.sleep(5)  # Temps de chargement
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        li_elements = soup.select('a.xiti')  # Sélecteurs spécifiques pour les questions
        resultats = []

        for a in li_elements:
            try:
                if a:
                    question = a.get_text(strip=True)
                    driver.get(a['href']) 

                    try:
                        # Attend que l'élément contenant la réponse soit chargé
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ezrichtext-field"))
                        )
                        sous_soup = BeautifulSoup(driver.page_source, 'html.parser')
                        contenu_html_list = sous_soup.select("div.ezrichtext-field")
                        reponse = "\n".join([p.get_text(separator='\n', strip=True) for p in contenu_html_list]) if contenu_html_list else "[SANS CONTENU]"
                    except Exception as e:
                        reponse = f"[ERREUR AU CHARGEMENT DU CONTENU] {str(e)}"

                    resultats.append({
                        'question': question,
                        'reponse': reponse,
                        'gouvernement': 1 if source_gouv else 0
                    })
            except Exception as e:
                print(f"Erreur lors du traitement d'un élément de data_2: {e}")
        
        enregistrer_csv(resultats, 'data_gouv_2.csv')
    except Exception as e:
        print(f"Erreur générale dans data_2: {e}")

def data_3(driver, url, source_gouv=True):
    """Extrait les FAQs d'une préfecture régionale"""
    try:
        driver.get(url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        faq_container = soup.select_one('div.faq')
        elements = list(faq_container.children) if faq_container else []
        resultats = []

        for element in elements:
            try:
                if element.name == 'div' and 'faq-item' in element.get('class', []):
                    question_tag = element.find('h3')
                    reponse_tag = element.find('div', class_='to_expand')

                    if question_tag and reponse_tag:
                        question = question_tag.get_text(strip=True)
                        reponse = reponse_tag.get_text(separator='\n', strip=True)

                        resultats.append({
                            'question': question,
                            'reponse': reponse,
                            'gouvernement': 1 if source_gouv else 0
                        })
            except Exception as e:
                print(f"Erreur lors du traitement d'un élément de data_3: {e}")

        enregistrer_csv(resultats, 'data_gouv_3.csv')
    except Exception as e:
        print(f"Erreur générale dans data_3: {e}")

def data_4(driver, url, source_gouv=True):
    """Extrait les FAQs des sites gouvernementaux utilisant des accordéons fr-accordion"""
    try:
        driver.get(url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        boutons = soup.select('.fr-accordion__btn')
        resultats = []

        for bouton in boutons:
            try:
                if bouton:
                    question = bouton.get_text(strip=True)
                    collapse_id = bouton.get('aria-controls')
                    collapse_div = soup.find('div', {'id': collapse_id})

                    if collapse_div:
                        response_paragraphs = collapse_div.select('p')
                        reponse = "\n".join([p.get_text(separator='\n', strip=True) for p in response_paragraphs]) if response_paragraphs else "[SANS CONTENU]"
                        
                        # Récupère aussi les liens qui peuvent faire partie de la réponse
                        try:
                            links = collapse_div.select('a.fr-link')
                            if links:
                                liens_text = "\n".join([f"Lien: {link['href']}" for link in links])
                                reponse += "\n" + liens_text
                        except Exception as e:
                            print(f"Erreur lors de la récupération des liens: {e}")

                        resultats.append({
                            'question': question,
                            'reponse': reponse,
                            'gouvernement': 1 if source_gouv else 0
                        })
            except Exception as e:
                print(f"Erreur lors du traitement d'un bouton d'accordéon: {e}")

        enregistrer_csv(resultats, 'data_gouv_4.csv')
    except Exception as e:
        print(f"Erreur générale dans data_4: {e}")

def data_5(driver, url, source_gouv=True):
    """Extrait les FAQs des sites avec la structure accordéon + contenu dans .inner"""
    try:
        driver.get(url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        boutons_questions = soup.select('.fr-accordion__btn')
        resultats = []

        for bouton in boutons_questions:
            try:
                question_texte = bouton.get_text(strip=True)
                collapse_id = bouton.get('aria-controls')

                collapse_div = soup.find('div', {'id': collapse_id})
                
                if collapse_div:
                    div_reponse = collapse_div.select_one('.inner')

                    if div_reponse:
                        try:
                            # Récupère le contenu de plusieurs façons possibles (paragraphes ou listes)
                            p_items = div_reponse.select('p')
                            li_items = div_reponse.select('ul > li')

                            reponse_texte = "\n".join([p.get_text(strip=True) for p in p_items]) if p_items else \
                                           "\n".join([li.get_text(strip=True) for li in li_items]) if li_items else "[SANS RÉPONSE]"

                            resultats.append({
                                'question': question_texte,
                                'reponse': reponse_texte,
                                'gouvernement': 1 if source_gouv else 0
                            })
                        except Exception as e:
                            print(f"Erreur lors de l'extraction du contenu: {e}")
            except Exception as e:
                print(f"Erreur lors du traitement d'un bouton de data_5: {e}")

        enregistrer_csv(resultats, 'data_gouv_5.csv')
    except Exception as e:
        print(f"Erreur générale dans data_5: {e}")

def data_6(driver, url, source_gouv=True):
    """Extrait les FAQs de France Travail (Pôle Emploi)"""
    try:
        driver.get(url)
        time.sleep(5)
        resultats = []

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # Trouve tous les liens qui contiennent "/faq/" dans leur URL
        liens_faq = soup.select('a[href*="/faq/"]')

        # Collecte et déduplique les URLs
        urls = []
        for lien in liens_faq:
            try:
                href = lien.get('href')
                if href and not href.startswith('http'):
                    full_url = "https://www.francetravail.fr" + href
                    urls.append(full_url)
            except Exception as e:
                print(f"Erreur lors de l'extraction d'une URL: {e}")

        urls = list(set(urls))

        # Visite chaque URL de FAQ
        for lien_url in urls:
            try:
                driver.get(lien_url)
                time.sleep(5)

                sous_soup = BeautifulSoup(driver.page_source, 'html.parser')

                question_tag = sous_soup.select_one('h1')
                reponse_tag = sous_soup.select_one('.cms')

                question_text = question_tag.get_text(strip=True) if question_tag else "[SANS QUESTION]"
                reponse_text = reponse_tag.get_text(separator='\n', strip=True) if reponse_tag else "[SANS RÉPONSE]"

                # Ignore les pages vides
                if question_text == "Questions et contacts" and reponse_text == "[SANS RÉPONSE]":
                    continue

                resultats.append({
                    'question': question_text,
                    'reponse': reponse_text,
                    'gouvernement': 1 if source_gouv else 0
                })
            except Exception as e:
                print(f"Erreur lors du traitement de l'URL {lien_url}: {e}")

        enregistrer_csv(resultats, 'data_gouv_6.csv')
    except Exception as e:
        print(f"Erreur générale dans data_6: {e}")

def data_7(driver, url):
    """Extrait les FAQs du site Le Bon Coin (non gouvernemental)"""
    try:
        driver.get(url)
        time.sleep(5)

        # Attend que les éléments soient chargés
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.blocks-item-link'))
            )
        except Exception as e:
            print(f"Erreur lors de l'attente des éléments: {e}")

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        categories = soup.select('.blocks-item-link')
        resultats = []

        for category in categories:
            try:
                # Accède à chaque catégorie
                category_url = "https://assistance.leboncoin.info" + category['href']
                driver.get(category_url)
                time.sleep(5)

                # Attend le chargement du bouton "Voir tous les articles"
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.see-all-articles'))
                    )
                except Exception as e:
                    print(f"Erreur lors de l'attente du bouton 'voir tous': {e}")
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                see_all_button = soup.select_one('.see-all-articles')

                if see_all_button:
                    # Charge tous les articles
                    driver.get("https://assistance.leboncoin.info" + see_all_button['href'])
                    time.sleep(5)

                # Parcourt les articles
                articles = soup.select('.article-list-link')
                for article in articles:
                    try:
                        article_url = "https://assistance.leboncoin.info" + article['href']
                        driver.get(article_url)
                        time.sleep(5)

                        soup = BeautifulSoup(driver.page_source, 'html.parser')

                        # Extrait la question et la réponse
                        question = soup.select_one('.article-header .article-title').get_text(strip=True)
                        reponse = soup.select_one('.article-body').get_text(strip=True)

                        resultats.append({
                            'question': question,
                            'reponse': reponse,
                            'gouvernement': 0  # Site non gouvernemental
                        })
                    except Exception as e:
                        print(f"Erreur lors du traitement d'un article: {e}")
            except Exception as e:
                print(f"Erreur lors du traitement d'une catégorie: {e}")

        enregistrer_csv(resultats, 'data_nongouv_7.csv')
    except Exception as e:
        print(f"Erreur générale dans data_7: {e}")

def data_8(driver, url):
    """Extrait les FAQs du site Kleenex (non gouvernemental)"""
    try:
        driver.get(url)
        time.sleep(5)

        # Attend que les questions (sous forme d'accordéon) soient chargées
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.card-header.collapsed'))
            )
        except Exception as e:
            print(f"Erreur lors de l'attente des cartes d'accordéon: {e}")

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        cards = soup.select('.card-header.collapsed')
        resultats = []

        for card in cards:
            try:
                question_element = card.select_one('.card-title')
                if question_element:
                    question_text = question_element.get_text(strip=True)

                    # Filtre certaines questions
                    if question_text.startswith('Kleenex'):
                        continue

                    # Tente de cliquer pour déplier la réponse
                    try:
                        driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, f"//*[normalize-space(text())='{question_text}']"))
                    except Exception as e:
                        print(f"Erreur lors du clic sur l'accordéon: {e}")

                    time.sleep(1)
                    soup = BeautifulSoup(driver.page_source, 'html.parser')

                    # Récupère la réponse via l'ID de l'accordéon
                    try:
                        collapse_id = card.get('data-target')
                        if collapse_id:
                            collapse_id = collapse_id.replace('#', '')
                            reponse_element = soup.find(id=collapse_id)
                            if reponse_element:
                                reponse_text = reponse_element.get_text(strip=True)
                            else:
                                reponse_text = "[SANS RÉPONSE]"
                        else:
                            reponse_text = "[SANS RÉPONSE]"

                        resultats.append({
                            'question': question_text,
                            'reponse': reponse_text,
                            'gouvernement': 0
                        })
                    except Exception as e:
                        print(f"Erreur lors de l'extraction de la réponse: {e}")

                    time.sleep(1)
            except Exception as e:
                print(f"Erreur lors du traitement d'une carte: {e}")

        enregistrer_csv(resultats, 'data_nongouv_8.csv')
    except Exception as e:
        print(f"Erreur générale dans data_8: {e}")

def data_9(url, source_gouv=False):
    """Extrait les FAQs du site VirTour en utilisant requests (sans Selenium)"""
    try:
        entete = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        
        reponse = requests.get(url, headers=entete)
        soup = BeautifulSoup(reponse.text, 'html.parser')
        resultats = []
        
        # Récupère les questions et réponses via leurs classes CSS
        try:
            questions = soup.find_all('div', class_='toggle')
            reponses = soup.find_all('div', class_='next')
            
            # Association question-réponse par ordre d'apparition
            for question_div, reponse_div in zip(questions, reponses):
                try:
                    question_p = question_div.find('p')
                    reponse_p = reponse_div.find_all('p')
                    
                    question = question_p.get_text(strip=True) if question_p else "[SANS QUESTION]"
                    reponse = "\n".join([p.get_text(separator=' ', strip=True) for p in reponse_p]) if reponse_p else "[SANS RÉPONSE]"
                    
                    resultats.append({
                        'question': question,
                        'reponse': reponse,
                        'gouvernement': 1 if source_gouv else 0
                    })

                    time.sleep(0.5)  # Pause pour éviter surcharge du serveur
                except Exception as e:
                    print(f"Erreur lors du traitement d'une paire question/réponse: {e}")
        except Exception as e:
            print(f"Erreur lors de l'extraction des questions/réponses: {e}")
        
        enregistrer_csv(resultats, "data_nongouv_9.csv")
    except Exception as e:
        print(f"Erreur générale dans data_9: {e}")

def data_10(url, source_gouv=False):
    """Extrait les FAQs du site PaulasChoice (non gouvernemental)"""
    try:
        entete = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        
        url_base = "https://www.paulaschoice.fr"
        
        try:
            reponse = requests.get(url, headers=entete)
            soup = BeautifulSoup(reponse.text, "html.parser")
            
            # Trouve les sections contenant des liens vers des questions
            divs_contenu = soup.find_all("div", class_="content")
            liens = []
            
            # Collecte tous les liens des questions FAQ
            for div in divs_contenu:
                try:
                    for a in div.find_all("a", href=True):
                        lien = a['href']
                        if lien.startswith("https"):
                            liens.append(lien)
                        else:
                            liens.append(url_base + lien)
                except Exception as e:
                    print(f"Erreur lors de la collecte des liens: {e}")
        except Exception as e:
            print(f"Erreur lors du chargement de la page principale: {e}")
            return
        
        # Déduplique les liens
        liens = list(set(liens))
        resultats = []
        
        # Visite chaque lien pour extraire Q&R
        for lien in liens:
            try:
                sous_reponse = requests.get(lien, headers=entete)
                sous_soup = BeautifulSoup(sous_reponse.text, "html.parser")
                
                # Cherche les "ancres" qui précèdent les paires Q&R
                ancres = sous_soup.find_all("span", class_="anchor")
                for ancre in ancres:
                    try:
                        h2 = ancre.find_next("h2")  # Question en H2
                        p = ancre.find_next("p")    # Réponse en P
                        if h2 and p:
                            question = h2.get_text(strip=True)
                            reponse = p.get_text(separator=' ', strip=True)
                            resultats.append({
                                'question': question,
                                'reponse': reponse,
                                'gouvernement': 1 if source_gouv else 0
                            })
                    except Exception as e:
                        print(f"Erreur lors du traitement d'une ancre: {e}")
                time.sleep(1)
            except Exception as e:
                print(f"Erreur lors du traitement du lien {lien}: {e}")
        
        enregistrer_csv(resultats, "data_nongouv_10.csv")
    except Exception as e:
        print(f"Erreur générale dans data_10: {e}")

def data_11(url, source_gouv=False):
    """Extrait les FAQs des sites utilisant la structure DL/DT/DD (comme Google Maps)"""
    try:
        entete = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        
        try:
            reponse = requests.get(url, headers=entete)
            soup = BeautifulSoup(reponse.text, 'html.parser')
            resultats = []
            
            # Structure de type définition (DT=terme/question, DD=définition/réponse)
            questions = soup.find_all('dt')
            reponses = soup.find_all('dd')
            
            for question_dt, reponse_dd in zip(questions, reponses):
                try:
                    question = question_dt.get_text(strip=True)

                    # Traite les réponses qui peuvent avoir divers éléments HTML
                    reponse_elements = reponse_dd.find_all(['p', 'ul', 'ol', 'li'])
                    if reponse_elements:
                        reponse = "\n".join([elem.get_text(separator=' ', strip=True) for elem in reponse_elements])
                    else:
                        reponse = reponse_dd.get_text(separator=' ', strip=True)

                    resultats.append({
                        'question': question,
                        'reponse': reponse,
                        'gouvernement': 1 if source_gouv else 0
                    })

                    time.sleep(0.5)
                except Exception as e:
                    print(f"Erreur lors du traitement d'une définition: {e}")
        except Exception as e:
            print(f"Erreur lors du chargement de la page: {e}")
        
        enregistrer_csv(resultats, "data_nongouv_11.csv")
    except Exception as e:
        print(f"Erreur générale dans data_11: {e}")

def data_12(url, source_gouv=False):
    """Extrait les FAQs de sites avec structure H3 suivis de paragraphes (Google Profile Help)"""
    try:
        entete = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        
        try:
            reponse = requests.get(url, headers=entete)
            soup = BeautifulSoup(reponse.text, 'html.parser')
            resultats = []
            
            # Questions dans des H3
            questions = soup.find_all('h3')
            
            for question_h3 in questions:
                try:
                    question = question_h3.get_text(strip=True)
                    reponse_parts = []
                    
                    # Récupère tous les paragraphes qui suivent jusqu'au prochain élément non-p
                    suivant = question_h3.find_next_sibling()
                    while suivant and suivant.name == 'p':
                        reponse_parts.append(suivant.get_text(separator=' ', strip=True))
                        suivant = suivant.find_next_sibling()
                    
                    reponse = "\n".join(reponse_parts) if reponse_parts else "[SANS RÉPONSE]"
                    
                    resultats.append({
                        'question': question,
                        'reponse': reponse,
                        'gouvernement': 1 if source_gouv else 0
                    })

                    time.sleep(0.5)
                except Exception as e:
                    print(f"Erreur lors du traitement d'une question H3: {e}")
        except Exception as e:
            print(f"Erreur lors du chargement de la page: {e}")
        
        enregistrer_csv(resultats, "data_nongouv_12.csv")
    except Exception as e:
        print(f"Erreur générale dans data_12: {e}")