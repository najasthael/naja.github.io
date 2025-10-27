################################################################################
# Fine-Tuning Projet FAQ-Gouv                                                  #
# Projet de Master 1 - Industrie de la langue - Université Grenoble-Alpes      #
# Auteurs: Naja Ferreira et Marion Leteillier                                  #
# Description: Script pour l'exécution des différentes fonctions de scraping.  #
################################################################################

"""
Ce fichier appelle les fonctions définies dans scraper.py pour extraire
des FAQ depuis plusieurs sites web gouvernementaux et non-gouvernementaux.
"""     


from scraper import data_1, data_2, data_3, data_4, data_5, data_6, demarre_driver, data_7, data_8, data_9, data_10, data_11, data_12


def main():
    """
    Fonction principale qui initialise le driver Selenium et lance les
    fonctions de scraping pour différents sites web.
    """
    # Initialisation du driver Selenium
    driver = demarre_driver()
    
    # Vérification que le driver a bien été initialisé
    if driver is None:
        print("Erreur: Impossible de démarrer le driver Firefox. Vérifiez l'installation de geckodriver.")
        return

    try:
        # Liste des scrapers disponibles
        # Commentez ou décommentez pour activer le scraper souhaité
    
        try:
            print("Lancement du scraper 1 (service-public.fr)...")
            data_1(driver, "https://www.service-public.fr/particuliers/vosdroits/questions-reponses")
            print("Scraper 1 terminé avec succès.")
        except Exception as e:
            print(f"Erreur lors de l'exécution du scraper 1: {e}")
        
        try:
            print("Lancement du scraper 2 (culture.gouv.fr)...")
            data_2(driver, "https://www.culture.gouv.fr/fr/foire-aux-questions")
            print("Scraper 2 terminé avec succès.")
        except Exception as e:
            print(f"Erreur lors de l'exécution du scraper 2: {e}")
        
        try:
            print("Lancement du scraper 3 (préfectures-regions)...")
            data_3(driver, "https://www.prefectures-regions.gouv.fr/ile-de-france/Outils/FAQ")
            print("Scraper 3 terminé avec succès.")
        except Exception as e:
            print(f"Erreur lors de l'exécution du scraper 3: {e}")

        try:
            print("Lancement du scraper 4 (herault.gouv.fr)...")
            data_4(driver, "https://www.herault.gouv.fr/Outils/FAQ/Foire-aux-questions-generaliste")
            print("Scraper 4 terminé avec succès.")
        except Exception as e:
            print(f"Erreur lors de l'exécution du scraper 4: {e}")

        try:
            print("Lancement du scraper 5 (essonne.gouv.fr)...")
            data_5(driver, "https://www.essonne.gouv.fr/Demarches/Accueil-des-etrangers-dans-l-Essonne/Questions-Reponses/Titres-de-sejour")
            print("Scraper 5 terminé avec succès.")
        except Exception as e:
            print(f"Erreur lors de l'exécution du scraper 5: {e}")
        
        try:
            print("Lancement du scraper 6 (francetravail.fr)...")
            data_6(driver, "https://www.francetravail.fr/faq/")
            print("Scraper 6 terminé avec succès.")
        except Exception as e:
            print(f"Erreur lors de l'exécution du scraper 6: {e}")
        
        try:
            print("Lancement du scraper 7 (leboncoin.info)...")
            data_7(driver, "https://assistance.leboncoin.info/hc/fr")
            print("Scraper 7 terminé avec succès.")
        except Exception as e:
            print(f"Erreur lors de l'exécution du scraper 7: {e}")

        try:
            print("Lancement du scraper 8 (kleenex.fr)...")
            data_8(driver, "https://www.kleenex.fr/faqs")
            print("Scraper 8 terminé avec succès.")
        except Exception as e:
            print(f"Erreur lors de l'exécution du scraper 8: {e}")
        
        try:
            print("Lancement du scraper 9 (virtour.fr)...")
            data_9("https://virtour.fr/faq/")
            print("Scraper 9 terminé avec succès.")
        except Exception as e:
            print(f"Erreur lors de l'exécution du scraper 9: {e}")
        
        try:
            print("Lancement du scraper 10 (paulaschoice.fr)...")
            data_10("https://www.paulaschoice.fr/fr/frequently-asked-questions/faq.html")
            print("Scraper 10 terminé avec succès.")
        except Exception as e:
            print(f"Erreur lors de l'exécution du scraper 10: {e}")
        
        try:
            print("Lancement du scraper 11 (google maps)...")
            data_11("https://developers.google.com/maps/faq?hl=fr")
            print("Scraper 11 terminé avec succès.")
        except Exception as e:
            print(f"Erreur lors de l'exécution du scraper 11: {e}")

        # Exécution du scraper 12 (le seul activé par défaut)
        try:
            print("Lancement du scraper 12 (google profile)...")
            data_12("https://developers.google.com/profile/help/faq?hl=fr")
            print("Scraper 12 terminé avec succès.")
        except Exception as e:
            print(f"Erreur lors de l'exécution du scraper 12: {e}")

    except Exception as e:
        # Capture des erreurs globales
        print(f"Erreur générale: {e}")
    finally:
        # Fermeture du driver dans tous les cas
        try:
            if driver:
                driver.quit()
                print("Driver Selenium fermé avec succès.")
        except Exception as e:
            print(f"Erreur lors de la fermeture du driver: {e}")

# Point d'entrée principal du script
if __name__ == '__main__':
    # Exécution des scrapers
    main()