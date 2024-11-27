import pandas as pd 
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import openai
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.cloud import bigquery
import re
import numpy as np
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account


 

def generate_new_title(row, langage):
    row = row.fillna('')
    # Remplacer les occurrences de "beauty", "Beauty", "BEAUTY" par une chaîne vide dans la colonne 'brand'
    #row['brand'] = re.sub(r'beauty', '', row['brand'], flags=re.IGNORECASE)
    title = row['title']
    brand = row['brand']
    description = row['description']
    print(title)
    #size = row['size']

    if langage == 'FR':
        prompt = f'''Trouve-moi un titre optimal basé sur :
        - Marque : {brand if brand else "non spécifiée"},
        - Titre précédent : {title if title else "non spécifié"},
        - Description : {description if description else "non spécifiée"},
        et respectant les critères suivants :
        1. Marque : Inclure le nom de la marque s'il est connu et pertinent pour le produit.
        Si la marque est vide ou non spécifiée, ne pas inclure la marque dans la constitution du titre.
        2. Nom du produit : Soyez précis et descriptif, en incluant le nom du produit.
        3. Caractéristiques clés : Ajoutez uniquement les informations chiffrées présentes dans la description fournie, sans ajouter d'adjectifs superflus ni d'informations non présentes.
        4. **Ne prendre que les informations chiffrées (par exemple : volume, poids, taille) présentes dans la description fournie et ne pas prendre les informations chiffées superflues comme la référence, sans ajouter d'adjectifs ou de détails non présents **
        5. sans ajouter d'adjectifs ou de détails non présents dans les informations enn entrées
        5. Mots-clés : Intégrez des mots-clés pertinents pour améliorer la visibilité dans les résultats de recherche.
        6. Longueur appropriée : Gardez le titre suffisamment court pour qu'il reste lisible, en évitant les détails inutiles.
        7. Sans prix ni messages promotionnels.
        8. Doit inclure le volume ou le contenu.
        9. Ne doit pas contenir de code de pays comme EU, FR, US, même s'ils font partie du nom de la marque.
        10. Ne doit pas contenir "EU".
        11. Mettre un espacement entre le nombre et les ml (par ex : 100 ml au lieu de 100ml)
        12. La marque ne doit pas contenir des ajouts comme beauty mais seulement le nom de la marque (pareil pour toutes les marques, mettre Armani, Valentino, Yves Saint Laurent, Helena Rubinstein, Carita)
        13. Si c'est le même produit, par exemple Luminous Silk, la structure doit être la même
        14. Mettre un '-' entre la marque et le début du titre (par ex : Armani - Luminous Silk au lieu de Armani Luminous Silk)
        15. Enlever les doubles mentions de genre, dans certains titres on retrouve 'Homme' et 'For Man'
        16. Enlever les mots : Size
        17. Certains titres ont des apostrophes, il faut les retirer
        18. Ne pas mettre masculine fragrance mais Fragrance for men
        19. Pour les parfums, respectez la structure : Marque - Nom du produit - Type de produit - Taille - Informations complémentaires
        20. Pour le maquillage, respectez la structure : Marque - Nom du produit - Type de produit - Couleur - Taille (si l'information existe) - Informations complémentaires
        21. Enlever tous les guillemets dans le titre final
        Basé strictement sur ces exemples :
        - {brand} - Huile pour cheveux infusée au miel - Format voyage 50ml - Réparation et hydratation des cheveux
        - {brand} - Huile pour cheveux au miel par Mirsalehi - Réparation intense - Pré-coiffage, finition, et traitement de nuit
        - {brand} - Huile pour cheveux au miel - Format 100ml - Réparation des cheveux
        - {brand} - Huile à lèvres Miel d'Or - Huile soin des lèvres pour des lèvres douces et brillantes
        - {brand} - Parfum pour cheveux infusé au miel - Format 50ml - Notes florales du jardin d'abeilles de Mirsalehi
        '''


    elif langage == 'EN':
        prompt = f'''Find me an optimal title based on:
          - Brand: {brand},
          - Previous title: {title},
          - Description: {description},
        and adhering to the following criteria:
          1. Brand: Include the brand name if it is known and relevant to the product.
          2. Product Name: Be precise and descriptive, including the product name.
          3. Key Features: Add key product features that distinguish it.
          4. Keywords: Integrate relevant keywords to improve visibility in search results.
          5. Appropriate Length: Keep the title short enough to remain readable, avoiding unnecessary details.
          6. Without prices and promotional messages.
          7. Must include the volume/content.
          8. Should not contain country codes like EU, FR, US, even if they are part of the brand name.
          9. Should not contain "EU".
          10. Add spacing between the number and "ml" (e.g., 100 ml instead of 100ml).
          11. The brand name should not include additions like "beauty," only the brand name itself (same rule applies for all brands, use Armani, Valentino, Yves Saint Laurent, Helena Rubinstein, Carita).
          12. If it's the same product, such as "Luminous Silk," the structure should remain the same across all instances.
          13. Use a hyphen '-' between the brand and the start of the title (e.g., Armani - Luminous Silk instead of Armani Luminous Silk).
          14. Remove double gender mentions, such as "Homme" and "For Man" in the same title.
          15. Remove words like "Size".
          16. Some titles contain apostrophes, which should be removed.
          17. Do not use "masculine fragrance," instead use "Fragrance for men".
          18. For perfumes, follow the structure: Brand - Product Name - Type of Product - Size - Additional Information.
          19. For makeup, follow the structure: Brand - Product Name - Type of Product - Color - Size (if applicable) - Additional Information.
          20. The brand should not be Armani beauty but only Armani (same rule applies for all brands, use Valentino, Yves Saint Laurent, Helena Rubinstein, Carita).
          Based strictly on these examples:
            - {brand} - Honey-infused Hair Oil - Travel Size 50 ml - Hair Repair and Hydration
            - {brand} - Honey Hair Oil by Mirsalehi - Deep Repair - Pre-styling, finishing, and overnight treatment
            - {brand} - Honey Hair Oil - 100 ml Size - Hair Repair
            - {brand} - Lip Oil Gold Honey - Lip Care Oil for Soft and Shiny Lips
            - {brand} - Honey-infused Hair Perfume - 50 ml Size - Floral Notes from the Mirsalehi Bee Garden
        '''
    elif langage == 'ES':
      prompt = f'''Encuéntrame un título óptimo basado en:
          - Marca: {brand},
          - Título anterior: {title},
          - Descripción: {description},
        y siguiendo los siguientes criterios:
          1. Marca: Incluye el nombre de la marca si es conocido y relevante para el producto.
          2. Nombre del producto: Sé preciso y descriptivo, incluyendo el nombre del producto.
          3. Características clave: Añade las características clave del producto que lo distingan.
          4. Palabras clave: Integra palabras clave relevantes para mejorar la visibilidad en los resultados de búsqueda.
          5. Longitud adecuada: Mantén el título lo suficientemente corto para que sea legible, evitando detalles innecesarios.
          6. Sin precios ni mensajes promocionales.
          7. Debe incluir el volumen o contenido.
          8. No debe contener códigos de país como EU, FR, US, incluso si son parte del nombre de la marca.
          9. No debe contener "EU".
          10. Añade un espacio entre el número y "ml" (por ejemplo, 100 ml en lugar de 100ml).
          11. El nombre de la marca no debe incluir adiciones como "beauty", solo el nombre de la marca en sí (la misma regla se aplica a todas las marcas, utiliza Armani, Valentino, Yves Saint Laurent, Helena Rubinstein, Carita).
          12. Si es el mismo producto, como "Luminous Silk", la estructura debe mantenerse igual en todas las instancias.
          13. Usa un guion '-' entre la marca y el inicio del título (por ejemplo, Armani - Luminous Silk en lugar de Armani Luminous Silk).
          14. Elimina menciones dobles de género, como "Homme" y "For Man" en el mismo título.
          15. Elimina palabras como "Tamaño".
          16. Algunos títulos contienen apóstrofes, los cuales deben eliminarse.
          17. No uses "fragancia masculina", en su lugar usa "Fragancia para hombre".
          18. Para perfumes, sigue la estructura: Marca - Nombre del Producto - Tipo de Producto - Tamaño - Información Adicional.
          19. Para maquillaje, sigue la estructura: Marca - Nombre del Producto - Tipo de Producto - Color - Tamaño (si aplica) - Información Adicional.
          20. La marca no debe ser Armani beauty, sino solo Armani (la misma regla se aplica a todas las marcas, utiliza Valentino, Yves Saint Laurent, Helena Rubinstein, Carita).
          Basado estrictamente en estos ejemplos:
            - {brand} - Aceite de Pelo Infundido con Miel - Tamaño de Viaje 50 ml - Reparación e Hidratación del Cabello
            - {brand} - Aceite de Pelo con Miel de Mirsalehi - Reparación Profunda - Tratamiento Pre-peinado, Acabado y Nocturno
            - {brand} - Aceite de Pelo con Miel - Tamaño de 100 ml - Reparación del Cabello
            - {brand} - Aceite de Labios Miel Dorada - Aceite Cuidado Labial para Labios Suaves y Brillantes
            - {brand} - Perfume de Pelo Infundido con Miel - Tamaño de 50 ml - Notas Florales del Jardín de Abejas Mirsalehi
        '''
      
    elif langage == 'DE':
        prompt = f'''Finde einen optimalen Titel basierend auf:
          - Marke: {brand},
          - Vorheriger Titel: {title},
          - Beschreibung: {description},
        und unter Einhaltung der folgenden Kriterien:
          1. Marke: Nenne den Markennamen, wenn er bekannt und für das Produkt relevant ist.
          2. Produktname: Sei präzise und beschreibend, indem du den Produktnamen angibst.
          3. Hauptmerkmale: Füge wichtige Produktmerkmale hinzu, die es auszeichnen.
          4. Schlüsselwörter: Integriere relevante Schlüsselwörter, um die Sichtbarkeit in den Suchergebnissen zu verbessern.
          5. Angemessene Länge: Halte den Titel kurz genug, um lesbar zu bleiben, und vermeide unnötige Details.
          6. Keine Preise und Werbebotschaften.
          7. Muss das Volumen/den Inhalt enthalten.
          8. Darf keine Ländercodes wie EU, FR, US enthalten, selbst wenn sie Teil des Markennamens sind.
          9. Darf "EU" nicht enthalten.
          10. Füge einen Abstand zwischen der Zahl und "ml" ein (z. B. 100 ml anstelle von 100ml).
          11. Der Markenname sollte keine Zusätze wie "beauty" enthalten, nur der Markenname selbst (dies gilt für alle Marken, verwende Armani, Valentino, Yves Saint Laurent, Helena Rubinstein, Carita).
          12. Wenn es sich um dasselbe Produkt handelt, wie z. B. "Luminous Silk", sollte die Struktur in allen Fällen gleich bleiben.
          13. Verwende einen Bindestrich '-' zwischen der Marke und dem Anfang des Titels (z. B. Armani - Luminous Silk anstelle von Armani Luminous Silk).
          14. Entferne doppelte Geschlechtsangaben wie "Homme" und "For Man" im selben Titel.
          15. Entferne Wörter wie "Größe".
          16. Einige Titel enthalten Apostrophe, die entfernt werden sollten.
          17. Verwende nicht "maskuliner Duft", sondern "Duft für Männer".
          18. Für Parfums folge der Struktur: Marke - Produktname - Produkttyp - Größe - Zusätzliche Informationen.
          19. Für Make-up folge der Struktur: Marke - Produktname - Produkttyp - Farbe - Größe (falls zutreffend) - Zusätzliche Informationen.
          20. Die Marke sollte nicht "Armani beauty", sondern nur "Armani" sein (dies gilt für alle Marken, verwende Valentino, Yves Saint Laurent, Helena Rubinstein, Carita).
          Basierend strikt auf diesen Beispielen:
            - {brand} - Honig-infundiertes Haaröl - Reisegröße 50 ml - Haarreparatur und Feuchtigkeitspflege
            - {brand} - Honighaaröl von Mirsalehi - Tiefenreparatur - Vor dem Styling, Finish und Behandlung über Nacht
            - {brand} - Honighaaröl - 100 ml Größe - Haarreparatur
            - {brand} - Lippenöl Goldener Honig - Lippenpflegeöl für weiche und glänzende Lippen
            - {brand} - Honig-infundiertes Haarparfum - 50 ml Größe - Blumige Noten aus dem Mirsalehi Bienengarten
        '''
    elif langage == 'IT':
        prompt = f'''Trova un titolo ottimale basato su:
          - Marchio: {brand},
          - Titolo precedente: {title},
          - Descrizione: {description},
        e attenendoti ai seguenti criteri:
          1. Marchio: Includi il nome del marchio se è conosciuto e rilevante per il prodotto.
          2. Nome del prodotto: Sii preciso e descrittivo, includendo il nome del prodotto.
          3. Caratteristiche principali: Aggiungi le caratteristiche chiave del prodotto che lo distinguono.
          4. Parole chiave: Integra parole chiave rilevanti per migliorare la visibilità nei risultati di ricerca.
          5. Lunghezza adeguata: Mantieni il titolo abbastanza breve da essere leggibile, evitando dettagli superflui.
          6. Senza prezzi o messaggi promozionali.
          7. Deve includere il volume/contenuto.
          8. Non deve contenere codici paese come EU, FR, US, anche se fanno parte del nome del marchio.
          9. Non deve contenere "EU".
          10. Aggiungi uno spazio tra il numero e "ml" (ad esempio, 100 ml invece di 100ml).
          11. Il nome del marchio non deve includere aggiunte come "beauty", solo il nome del marchio stesso (la stessa regola vale per tutti i marchi, usa Armani, Valentino, Yves Saint Laurent, Helena Rubinstein, Carita).
          12. Se è lo stesso prodotto, come "Luminous Silk", la struttura deve rimanere la stessa in tutte le istanze.
          13. Usa un trattino "-" tra il marchio e l'inizio del titolo (ad esempio, Armani - Luminous Silk invece di Armani Luminous Silk).
          14. Rimuovi doppie menzioni di genere, come "Homme" e "For Man" nello stesso titolo.
          15. Rimuovi parole come "Taglia".
          16. Alcuni titoli contengono apostrofi, che devono essere rimossi.
          17. Non usare "fragranza maschile", usa invece "Fragranza per uomo".
          18. Per i profumi, segui la struttura: Marchio - Nome del Prodotto - Tipo di Prodotto - Formato - Informazioni Aggiuntive.
          19. Per il trucco, segui la struttura: Marchio - Nome del Prodotto - Tipo di Prodotto - Colore - Formato (se applicabile) - Informazioni Aggiuntive.
          20. Il marchio non deve essere Armani beauty, ma solo Armani (la stessa regola vale per tutti i marchi, usa Valentino, Yves Saint Laurent, Helena Rubinstein, Carita).
          Basato rigorosamente su questi esempi:
            - {brand} - Olio per Capelli Infuso al Miele - Formato da Viaggio 50 ml - Riparazione e Idratazione dei Capelli
            - {brand} - Olio per Capelli al Miele di Mirsalehi - Riparazione Profonda - Pre-styling, finishing e trattamento notturno
            - {brand} - Olio per Capelli al Miele - Formato 100 ml - Riparazione dei Capelli
            - {brand} - Olio per Labbra al Miele Dorato - Olio per Cura delle Labbra per Labbra Morbide e Luminose
            - {brand} - Profumo per Capelli Infuso al Miele - Formato 50 ml - Note Floreali dal Giardino delle Api di Mirsalehi
        '''
    elif langage == 'NL':
        prompt = f'''Vind een optimale titel op basis van:
            - Merk: {brand},
            - Vorige titel: {title},
            - Beschrijving: {description},
            en volg de volgende criteria:
            1. Merk: Voeg de merknaam toe als deze bekend en relevant is voor het product.
            2. Productnaam: Wees nauwkeurig en beschrijvend, inclusief de naam van het product.
            3. Belangrijkste kenmerken: Voeg de belangrijkste kenmerken van het product toe die het onderscheiden.
            4. Zoekwoorden: Integreer relevante zoekwoorden om de zichtbaarheid in zoekresultaten te verbeteren.
            5. Geschikte lengte: Houd de titel kort genoeg om leesbaar te blijven en vermijd overbodige details.
            6. Geen prijzen of promotionele berichten.
            7. Moet het volume/inhoud bevatten.
            8. Geen landcodes zoals EU, FR, US, zelfs als deze deel uitmaken van de merknaam.
            9. Mag geen "EU" bevatten.
            10. Voeg een spatie toe tussen het nummer en "ml" (bijv. 100 ml in plaats van 100ml).
            11. De merknaam mag geen toevoegingen bevatten zoals "beauty", alleen de merknaam zelf (dezelfde regel geldt voor alle merken, gebruik Armani, Valentino, Yves Saint Laurent, Helena Rubinstein, Carita).
            12. Als het hetzelfde product is, zoals "Luminous Silk", moet de structuur in alle gevallen hetzelfde blijven.
            13. Gebruik een koppelteken "-" tussen het merk en het begin van de titel (bijv. Armani - Luminous Silk in plaats van Armani Luminous Silk).
            14. Verwijder dubbele geslachtsvermeldingen, zoals "Homme" en "For Man" in dezelfde titel.
            15. Verwijder woorden zoals "Maat".
            16. Sommige titels bevatten apostrofs die moeten worden verwijderd.
            17. Gebruik geen "mannelijke geur", gebruik in plaats daarvan "Geur voor mannen".
            18. Voor parfums volg je de structuur: Merk - Productnaam - Producttype - Formaat - Aanvullende Informatie.
            19. Voor make-up volg je de structuur: Merk - Productnaam - Producttype - Kleur - Formaat (indien van toepassing) - Aanvullende Informatie.
            20. Het merk mag niet "Armani beauty" zijn, maar alleen "Armani" (dezelfde regel geldt voor alle merken, gebruik Valentino, Yves Saint Laurent, Helena Rubinstein, Carita).
            Gebaseerd strikt op deze voorbeelden:
            - {brand} - Honing Geïnfuseerde Haarolie - Reisformaat 50 ml - Herstel en Hydratatie van het Haar
            - {brand} - Honing Haarolie van Mirsalehi - Diep Herstel - Pre-styling, Afwerking en Nachtbehandeling
            - {brand} - Honing Haarolie - Formaat 100 ml - Haarherstel
            - {brand} - Gouden Honing Lippenolie - Verzorgende Lippenolie voor Zachte en Stralende Lippen
            - {brand} - Geur voor Haar Geïnfuseerd met Honing - Formaat 50 ml - Bloemige Noten uit de Bijentuin van Mirsalehi
        '''
        
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": "Vous êtes un assistant qui génère des titres commerciaux pour des produits."},
                {"role": "user", "content": prompt}
            ]
        )
        # Récupérer le contenu généré
        new_title = response['choices'][0]['message']['content'].strip()
        return new_title
    except Exception as e:
        print(f"Erreur lors de la génération du titre : {e}")
        return None
def filter_old_ids(df_old, df_new):
    df_old['id'] = df_old['id'].astype(str)
    df_new['id'] = df_new['id'].astype(str)

    # On sélectionne les ID présents dans df_new
    new_ids = df_new['id'].unique()
    
    # On filtre df_old pour ne garder que les lignes avec des ID qui ne sont pas dans new_ids
    filtered_df = df_old[~df_old['id'].isin(new_ids)]
    
    return filtered_df

def generate_new_title_streamlit(row, prompt):
    row = row.fillna('')
    # Remplacer les occurrences de "beauty", "Beauty", "BEAUTY" par une chaîne vide dans la colonne 'brand'
    #row['brand'] = re.sub(r'beauty', '', row['brand'], flags=re.IGNORECASE)
    title = row['title']
    brand = row['brand']
    description = row['description']
    prompt_global = f'''Trouve-moi un titre optimal basé sur :
        - Marque : {brand if brand else "non spécifiée"},
        - Titre précédent : {title if title else "non spécifié"},
        - Description : {description if description else "non spécifiée"},
        et respectant les critères suivants :  

        '''
    prompt = prompt_global + prompt
    #size = row['size']
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4", 
            messages=[
                {"role": "system", "content": "Vous êtes un assistant qui génère des titres commerciaux pour des produits."},
                {"role": "user", "content": prompt}
            ]
        )
        # Récupérer le contenu généré
        new_title = response['choices'][0]['message']['content'].strip()
        return new_title
    except Exception as e:
        print(f"Erreur lors de la génération du titre : {e}")
        return None
def filter_old_ids(df_old, df_new):
    df_old['id'] = df_old['id'].astype(str)
    df_new['id'] = df_new['id'].astype(str)

    # On sélectionne les ID présents dans df_new
    new_ids = df_new['id'].unique()
    
    # On filtre df_old pour ne garder que les lignes avec des ID qui ne sont pas dans new_ids
    filtered_df = df_old[~df_old['id'].isin(new_ids)]
    
    return filtered_df




