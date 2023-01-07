# -*- coding: latin-1 -*-

#Imports
from os import listdir, rename, startfile, path, makedirs, remove
from os.path import isfile, join
import shutil
from PIL import Image

#Constantes
conf_pathRaws = r"Scans\Raws"        #Chemin vers le dossier contenant des chapitres de scans bruts
conf_pathOutput = r"Scans\Output"    #Chemin vers le dossier contenant les chapitres avec les scans standardisés

conf_extension = ".png"

conf_sharp_mode = False
conf_slow_prog = True

debug_mode = True              #Si True, affiche les messages de debug (peut être foireux pour certains messages. Ce sera à corriger.)








#Début du programme

def getFiles(path):
    """
    Récupère la liste des fichiers d'un dossier.
    
    Arguments :
    - path : le chemin du dossier (chaîne de caractères)
    
    Retourne la liste des noms des fichiers du dossier.
    """
    
    files = [f for f in listdir(path) if isfile(join(path,f))]
    return files

def open_images(path):
    """
    Ouvre toutes les images contenues dans un dossier.
    
    Arguments :
    - path : le chemin du dossier contenant les images (chaîne de caractères)
    
    Retourne une liste d'objets Image de la bibliothèque Pillow.
    """
    
    images = []
    for filename in listdir(path):
        # On vérifie que le fichier est une image
        if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".PNG") or filename.endswith(".JPG"):
            # Chargement de l'image
            image = Image.open(join(path, filename))
            images.append(image)
    return images


def imgMerge(img1, img2):
    """
    Fusionne deux images verticalement.
    
    Arguments :
    - img1 : la première image à fusionner (objet Image de la bibliothèque Pillow)
    - img2 : la deuxième image à fusionner (objet Image de la bibliothèque Pillow)
    
    Retourne l'image fusionnée.
    """
    
    
    #On redimensionne l'image la plus large à la largeur de l'image la moins large. ça permet d'éviter la génération d'une bande blanche sur la droite de l'image si les deux images n'ont pas la même largeur.
    min_width = min(img1.width, img2.width)
    new_height = 0
    if img1.width > img2.width:
        new_height = int(min_width * img1.height / img1.width)
        img1 = img1.resize((min_width, new_height))
    elif img2.width > img1.width:
        new_height = int(min_width * img2.height / img2.width)
        img2 = img2.resize((min_width, new_height))

    # Fusionner les images en les concaténant verticalement
    image = Image.new('RGB', (max(img1.width, img2.width), img1.height + img2.height),"WHITE")
    
    image.paste(img1, (0, 0))
    image.paste(img2, (0, img1.height))
    
    # Renvoyer la nouvelle image fusionnée
    return image


def save_image(image, filename):
    """
    Sauvegarde une image dans un fichier.
    
    Arguments :
    - image : l'image à sauvegarder (objet Image de la bibliothèque Pillow)
    - filename : le nom du fichier dans lequel sauvegarder l'image (chaîne de caractères)
    """

    # On vérifie que le fichier a bien une extension
    if not filename.endswith(".jpg") and not filename.endswith(".png"):
        filename += conf_extension
    image.save(filename)

    
def open_image_with_windows_explorer(image_path):
    """
    Ouvre une image avec l'explorateur d'images de Windows.
    
    Arguments :
    - image_path : le chemin de fichier de l'image (chaîne de caractères)
    
    Retourne True si l'image a été ouverte avec succès, False sinon.
    """
    
    try:
        # Ouvrir le fichier avec l'application associée sur le système
        startfile(image_path)
        return True
    except Exception as e:
        # Affichage de l'erreur en cas d'échec
        print(f"Impossible d'ouvrir l'image : {e}")
        return False

    
def imgListMerge(imgList):
    """
    Fusionne une liste d'images en une seule image.
    
    Arguments :
    - imgList : la liste d'images à fusionner (liste d'objets Image de la bibliothèque Pillow)
    
    Retourne l'image fusionnée.
    """
    
    for i in range(len(imgList)-1):
        imgList[i+1] = imgMerge(imgList[i], imgList[i+1])
    return imgList[len(imgList)-1]


def convert_webp_to_png(source_folder):
    """
    Convertit tous les fichiers .webp d'un dossier en .png.
    
    Arguments :
    - source_folder : le chemin du dossier contenant les fichiers .webp à convertir (chaîne de caractères)
    """
    
    # Parcours du dossier source
    webPDetected = False
    for filename in listdir(source_folder):
      # Si le fichier est une image WebP
      if filename.endswith('.webp'):
        # Chargement de l'image WebP
        if webPDetected == False:
            if debug_mode :
                print("WebP detecté, début de la conversion des fichiers en PNG...", end="\r")
            webPDetected = True
        webp_image = Image.open(path.join(source_folder, filename))
        # Conversion de l'image en RGB
        rgb_image = webp_image.convert('RGB')
        # Enregistrement de l'image dans le dossier de destination
        rgb_image.save(path.join(source_folder, filename.replace('.webp', '.png')))
        # Suppression de l'image WebP originale
        remove(path.join(source_folder, filename))
    
    if debug_mode:
        print('Conversion terminée !')



def is_color_close_to_white(color):
    """
    Vérifie si une couleur est proche du blanc (ou du noir pour les fonds noir. Malgré son nom, la fonction a un peu changé pour coller à certaines situations).
    
    Arguments :
    - color : la couleur à vérifier (tuple de 3 entiers entre 0 et 255)
    
    Retourne True si la couleur est proche du blanc, False sinon.
    """
    
    r, g, b = color
    close_to_white = r > 240 and g > 240 and b > 240
    close_to_black = r < 5 and g < 5 and b < 5
    return close_to_white or close_to_black


def split_image_by_white_bands(image,sharp_mode, slow_prog):
    """
    Découpe une image en plusieurs images en enlevant les bandes de couleur blanche.
    
    Arguments :
    - image : l'objet "Image" de la bibliothèque Pillow à découper
    
    Retourne une liste d'objets "Image" de la bibliothèque Pillow représentant les images découpées.
    """
    
    #Précise le mode de découpage (sharp_mode = True : découpage plus précis mais plus lent, sharp_mode = False : découpage moins précis mais plus rapide)
    sharpness = 5
    if sharp_mode:
        sharpness = 1

    #Si slow_prog = True, évite les découpages trop rapides (pour éviter les erreurs). Ralentit un peu le programme.
    progression_speed = 50
    if slow_prog:
        progression_speed = 10
    
    # Liste des images découpées
    images = []
    
    # Charger les pixels de l'image en mémoire
    pixels = image.load()
    
    # Largeur et hauteur de l'image
    width, height = image.size
    
    #print("Taille de l'image",str(image.height))
    
    # Scanner l'image ligne par ligne pour trouver les bandes de blanc
    y1 = 0
    while y1 < height:
        # Trouver la première ligne non blanche
        while y1 < height and all([is_color_close_to_white(pixels[x, y1]) for x in range(0,width,sharpness)]):
            y1 += progression_speed
        
        # Si on a trouvé une ligne non blanche, on remonte jusqu'à la dernière ligne blanche
        if y1 < height:
            y2 = y1
            while y2 > 0 and not all([is_color_close_to_white(pixels[x, y2 - 1]) for x in range(0,width,sharpness)]):
                y2 -= 1
            
            # On avance jusqu'à la dernière ligne non blanche
            y3 = y1
            while y3 < height and not all([is_color_close_to_white(pixels[x, y3]) for x in range(0,width,sharpness)]):
                if (y3 + progression_speed) <= height:
                    y3 += progression_speed
                else:
                    y3 = height

            #si on a trouvé une ligne blanche, on remontre jusqu'à la dernière ligne non blanche
            y4 = y3
            while y4 > 0 and all([is_color_close_to_white(pixels[x, y4 - 1]) for x in range(0,width,sharpness)]):
                y4 -= 1
            
            # On ajoute la sélection à la liste si elle fait une hauteur de plus de 5 px
            if y4 - y2 > 5:
                
                #print("Image trouvée :", str(y4- y2), "px de haut")
                images.append(image.crop((0, y2, width, y4)))
                if debug_mode:
                    print("Nombre d'images découvertes : " + "{:0>3d}".format(len(images)), end="\r")
            
            # On avance au début de la prochaine bande de couleur blanche
            y1 = y3
        else:
            # Si on n'a pas trouvé de ligne non blanche, on avance au début de la prochaine bande de couleur blanche
            y1 += progression_speed
    
    # Renvoyer la liste des images découpées
    if debug_mode:
        print()
    return images



def process_chapter(pathRaws, pathOutput):
    """
    Traite les scans d'un chapitre et les sauvegarde dans un dossier.
    
    Arguments :
    - pathRaws : le chemin d'accès au dossier contenant les scans à traiter (chaîne de caractères)
    - pathOutput : le chemin d'accès au dossier où sauvegarder les scans traités (chaîne de caractères)
    """
    
    #Création du dossier de sauvegarde si il n'existe pas
    if not path.exists(pathOutput):
        makedirs(pathOutput)
        
    convert_webp_to_png(pathRaws) #Conversion des scans au format png

    raws = open_images(pathRaws)        #Liste des scans à traiter

    if debug_mode :
        print("Traitement des scans en cours...")
    raws = imgListMerge(raws)           #Fusion des scans

    splitted_images = []                #Liste des images découpées sur les scans
    spl_prog = 1                        #Progression de la découpe des scans
    
    max_height = 1500
    
    if debug_mode:
        print("Découpage des scans en cours...")
    splitted_images.extend(split_image_by_white_bands(raws,conf_sharp_mode, conf_slow_prog))
    if debug_mode:
        print("Découpage terminé, nombre de découpages : " + str(len(splitted_images)))
    
    max_height = max_height/720*splitted_images[0].width
    
    formatnbmerge = "{:0>" + str(len(str(len(splitted_images)))) + "d}" #Formatage du numéro de fusion
    merge_prog = 1
    
    #TODO : Mettre ce script dans une fonction
    #Fusion des images découpées selon la taille max
    cases = []
    for img in splitted_images:
        if debug_mode:
            print("Concaténation de l'image " + formatnbmerge.format(merge_prog) + "/" + str(len(splitted_images)), end="\r")
        
        if cases == []:
            cases.append(img)
        else:
            if (cases[len(cases) - 1].height + img.height > max_height):
                cases.append(img)
            else:
                cases[len(cases) - 1] = imgMerge(cases[len(cases) - 1],img)
    
    if debug_mode:
        print("Concaténation terminée, nombre de concaténations : " + str(len(cases)))
       
    
    
    formatnb = "{:0>" + str(len(str(len(cases)))) + "d}" #Formatage du numéro de sauvegarde
    nb_res = 1 #Nombre de résultats sauvegardés

    #Sauvegarde des images fusionnées
    for case in cases:
        if debug_mode:
            print("Sauvegarde de l'image " + formatnb.format(nb_res) + "/" + str(len(cases)) + " sauvegardée", end="\r")
        case.save(pathOutput + "\\" + formatnb.format(nb_res) + conf_extension) #On formate le nom de façon à ce que la première image ressorte en format 0x ou 00x selon le nombre d'images
        nb_res += 1
        
    if debug_mode:
        print()



def compress_to_cbz(src_path, archive_name='archive'):
    """
    Compresse le contenu du dossier dans une archive CBZ.
    
    Arguments :
    - src_path : Le chemin d'accès du dossier à compresser (chaîne de caractères)
    - archive_name (optionnel) : le nom de l'archive (chaîne de caractères)
    """
    
    # Créer un zipfile à partir de src_path et le renommer en .cbz
    shutil.make_archive(src_path + '/' + archive_name, 'zip', src_path, '.')
    rename(src_path + '/' + archive_name + '.zip', src_path + '/' + archive_name + '.cbz')
    
    # Récupérer la liste de tous les dossiers dans src_path
    folders = [f for f in listdir(src_path) if path.isdir(path.join(src_path, f))]

    # Pour chaque dossier, supprimer le dossier et tout son contenu
    for folder in folders:
        shutil.rmtree(path.join(src_path, folder))

                

def process_manhwa(pathRaws, pathOutput):
    """
    Traite les scans d'un manhwa et les sauvegarde dans un dossier.
    
    Arguments :
    - pathRaws : le chemin d'accès au dossier contenant des chapitres de scans à traiter (chaîne de caractères)
    - pathOutput : le chemin d'accès au dossier où sauvegarder les chapitres de scans traités (chaîne de caractères)
    """
    
    #Création du dossier de sauvegarde si il n'existe pas
    if not path.exists(pathOutput):
        makedirs(pathOutput)
    
    #Liste des chapitres à traiter
    chapters = listdir(pathRaws)
    
    #Boucle sur chaque chapitre
    for chapter in chapters:
        print("Traitement du chapitre " + chapter + "/" + str(len(chapters)))#, end="\r")
        process_chapter(pathRaws + "\\" + chapter, pathOutput + "\\" + chapter)
    #print()
    print("Traitement terminé, compression de l'archive")
    compress_to_cbz(pathOutput)
    print("Compression terminée")
    




process_manhwa(conf_pathRaws, conf_pathOutput)

#TODO: Corriger la génération d'images trop longues occasionnelles