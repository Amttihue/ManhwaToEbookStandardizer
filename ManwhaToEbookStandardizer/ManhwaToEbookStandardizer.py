# -*- coding: latin-1 -*-

#Imports
from os import listdir, rename, startfile, path, makedirs, remove
from os.path import isfile, join
import shutil
from PIL import Image

#Constantes
conf_pathRaws = r"Scans\Raws"        #Chemin vers le dossier contenant des chapitres de scans bruts
conf_pathOutput = r"Scans\Output"    #Chemin vers le dossier contenant les chapitres avec les scans standardis�s

conf_extension = ".png"

conf_sharp_mode = False
conf_slow_prog = True

debug_mode = True              #Si True, affiche les messages de debug (peut �tre foireux pour certains messages. Ce sera � corriger.)








#D�but du programme

def getFiles(path):
    """
    R�cup�re la liste des fichiers d'un dossier.
    
    Arguments :
    - path : le chemin du dossier (cha�ne de caract�res)
    
    Retourne la liste des noms des fichiers du dossier.
    """
    
    files = [f for f in listdir(path) if isfile(join(path,f))]
    return files

def open_images(path):
    """
    Ouvre toutes les images contenues dans un dossier.
    
    Arguments :
    - path : le chemin du dossier contenant les images (cha�ne de caract�res)
    
    Retourne une liste d'objets Image de la biblioth�que Pillow.
    """
    
    images = []
    for filename in listdir(path):
        # On v�rifie que le fichier est une image
        if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".PNG") or filename.endswith(".JPG"):
            # Chargement de l'image
            image = Image.open(join(path, filename))
            images.append(image)
    return images


def imgMerge(img1, img2):
    """
    Fusionne deux images verticalement.
    
    Arguments :
    - img1 : la premi�re image � fusionner (objet Image de la biblioth�que Pillow)
    - img2 : la deuxi�me image � fusionner (objet Image de la biblioth�que Pillow)
    
    Retourne l'image fusionn�e.
    """
    
    
    #On redimensionne l'image la plus large � la largeur de l'image la moins large. �a permet d'�viter la g�n�ration d'une bande blanche sur la droite de l'image si les deux images n'ont pas la m�me largeur.
    min_width = min(img1.width, img2.width)
    new_height = 0
    if img1.width > img2.width:
        new_height = int(min_width * img1.height / img1.width)
        img1 = img1.resize((min_width, new_height))
    elif img2.width > img1.width:
        new_height = int(min_width * img2.height / img2.width)
        img2 = img2.resize((min_width, new_height))

    # Fusionner les images en les concat�nant verticalement
    image = Image.new('RGB', (max(img1.width, img2.width), img1.height + img2.height),"WHITE")
    
    image.paste(img1, (0, 0))
    image.paste(img2, (0, img1.height))
    
    # Renvoyer la nouvelle image fusionn�e
    return image


def save_image(image, filename):
    """
    Sauvegarde une image dans un fichier.
    
    Arguments :
    - image : l'image � sauvegarder (objet Image de la biblioth�que Pillow)
    - filename : le nom du fichier dans lequel sauvegarder l'image (cha�ne de caract�res)
    """

    # On v�rifie que le fichier a bien une extension
    if not filename.endswith(".jpg") and not filename.endswith(".png"):
        filename += conf_extension
    image.save(filename)

    
def open_image_with_windows_explorer(image_path):
    """
    Ouvre une image avec l'explorateur d'images de Windows.
    
    Arguments :
    - image_path : le chemin de fichier de l'image (cha�ne de caract�res)
    
    Retourne True si l'image a �t� ouverte avec succ�s, False sinon.
    """
    
    try:
        # Ouvrir le fichier avec l'application associ�e sur le syst�me
        startfile(image_path)
        return True
    except Exception as e:
        # Affichage de l'erreur en cas d'�chec
        print(f"Impossible d'ouvrir l'image : {e}")
        return False

    
def imgListMerge(imgList):
    """
    Fusionne une liste d'images en une seule image.
    
    Arguments :
    - imgList : la liste d'images � fusionner (liste d'objets Image de la biblioth�que Pillow)
    
    Retourne l'image fusionn�e.
    """
    
    for i in range(len(imgList)-1):
        imgList[i+1] = imgMerge(imgList[i], imgList[i+1])
    return imgList[len(imgList)-1]


def convert_webp_to_png(source_folder):
    """
    Convertit tous les fichiers .webp d'un dossier en .png.
    
    Arguments :
    - source_folder : le chemin du dossier contenant les fichiers .webp � convertir (cha�ne de caract�res)
    """
    
    # Parcours du dossier source
    webPDetected = False
    for filename in listdir(source_folder):
      # Si le fichier est une image WebP
      if filename.endswith('.webp'):
        # Chargement de l'image WebP
        if webPDetected == False:
            if debug_mode :
                print("WebP detect�, d�but de la conversion des fichiers en PNG...", end="\r")
            webPDetected = True
        webp_image = Image.open(path.join(source_folder, filename))
        # Conversion de l'image en RGB
        rgb_image = webp_image.convert('RGB')
        # Enregistrement de l'image dans le dossier de destination
        rgb_image.save(path.join(source_folder, filename.replace('.webp', '.png')))
        # Suppression de l'image WebP originale
        remove(path.join(source_folder, filename))
    
    if debug_mode:
        print('Conversion termin�e !')



def is_color_close_to_white(color):
    """
    V�rifie si une couleur est proche du blanc (ou du noir pour les fonds noir. Malgr� son nom, la fonction a un peu chang� pour coller � certaines situations).
    
    Arguments :
    - color : la couleur � v�rifier (tuple de 3 entiers entre 0 et 255)
    
    Retourne True si la couleur est proche du blanc, False sinon.
    """
    
    r, g, b = color
    close_to_white = r > 240 and g > 240 and b > 240
    close_to_black = r < 5 and g < 5 and b < 5
    return close_to_white or close_to_black


def split_image_by_white_bands(image,sharp_mode, slow_prog):
    """
    D�coupe une image en plusieurs images en enlevant les bandes de couleur blanche.
    
    Arguments :
    - image : l'objet "Image" de la biblioth�que Pillow � d�couper
    
    Retourne une liste d'objets "Image" de la biblioth�que Pillow repr�sentant les images d�coup�es.
    """
    
    #Pr�cise le mode de d�coupage (sharp_mode = True : d�coupage plus pr�cis mais plus lent, sharp_mode = False : d�coupage moins pr�cis mais plus rapide)
    sharpness = 5
    if sharp_mode:
        sharpness = 1

    #Si slow_prog = True, �vite les d�coupages trop rapides (pour �viter les erreurs). Ralentit un peu le programme.
    progression_speed = 50
    if slow_prog:
        progression_speed = 10
    
    # Liste des images d�coup�es
    images = []
    
    # Charger les pixels de l'image en m�moire
    pixels = image.load()
    
    # Largeur et hauteur de l'image
    width, height = image.size
    
    #print("Taille de l'image",str(image.height))
    
    # Scanner l'image ligne par ligne pour trouver les bandes de blanc
    y1 = 0
    while y1 < height:
        # Trouver la premi�re ligne non blanche
        while y1 < height and all([is_color_close_to_white(pixels[x, y1]) for x in range(0,width,sharpness)]):
            y1 += progression_speed
        
        # Si on a trouv� une ligne non blanche, on remonte jusqu'� la derni�re ligne blanche
        if y1 < height:
            y2 = y1
            while y2 > 0 and not all([is_color_close_to_white(pixels[x, y2 - 1]) for x in range(0,width,sharpness)]):
                y2 -= 1
            
            # On avance jusqu'� la derni�re ligne non blanche
            y3 = y1
            while y3 < height and not all([is_color_close_to_white(pixels[x, y3]) for x in range(0,width,sharpness)]):
                if (y3 + progression_speed) <= height:
                    y3 += progression_speed
                else:
                    y3 = height

            #si on a trouv� une ligne blanche, on remontre jusqu'� la derni�re ligne non blanche
            y4 = y3
            while y4 > 0 and all([is_color_close_to_white(pixels[x, y4 - 1]) for x in range(0,width,sharpness)]):
                y4 -= 1
            
            # On ajoute la s�lection � la liste si elle fait une hauteur de plus de 5 px
            if y4 - y2 > 5:
                
                #print("Image trouv�e :", str(y4- y2), "px de haut")
                images.append(image.crop((0, y2, width, y4)))
                if debug_mode:
                    print("Nombre d'images d�couvertes : " + "{:0>3d}".format(len(images)), end="\r")
            
            # On avance au d�but de la prochaine bande de couleur blanche
            y1 = y3
        else:
            # Si on n'a pas trouv� de ligne non blanche, on avance au d�but de la prochaine bande de couleur blanche
            y1 += progression_speed
    
    # Renvoyer la liste des images d�coup�es
    if debug_mode:
        print()
    return images



def process_chapter(pathRaws, pathOutput):
    """
    Traite les scans d'un chapitre et les sauvegarde dans un dossier.
    
    Arguments :
    - pathRaws : le chemin d'acc�s au dossier contenant les scans � traiter (cha�ne de caract�res)
    - pathOutput : le chemin d'acc�s au dossier o� sauvegarder les scans trait�s (cha�ne de caract�res)
    """
    
    #Cr�ation du dossier de sauvegarde si il n'existe pas
    if not path.exists(pathOutput):
        makedirs(pathOutput)
        
    convert_webp_to_png(pathRaws) #Conversion des scans au format png

    raws = open_images(pathRaws)        #Liste des scans � traiter

    if debug_mode :
        print("Traitement des scans en cours...")
    raws = imgListMerge(raws)           #Fusion des scans

    splitted_images = []                #Liste des images d�coup�es sur les scans
    spl_prog = 1                        #Progression de la d�coupe des scans
    
    max_height = 1500
    
    if debug_mode:
        print("D�coupage des scans en cours...")
    splitted_images.extend(split_image_by_white_bands(raws,conf_sharp_mode, conf_slow_prog))
    if debug_mode:
        print("D�coupage termin�, nombre de d�coupages : " + str(len(splitted_images)))
    
    max_height = max_height/720*splitted_images[0].width
    
    formatnbmerge = "{:0>" + str(len(str(len(splitted_images)))) + "d}" #Formatage du num�ro de fusion
    merge_prog = 1
    
    #TODO : Mettre ce script dans une fonction
    #Fusion des images d�coup�es selon la taille max
    cases = []
    for img in splitted_images:
        if debug_mode:
            print("Concat�nation de l'image " + formatnbmerge.format(merge_prog) + "/" + str(len(splitted_images)), end="\r")
        
        if cases == []:
            cases.append(img)
        else:
            if (cases[len(cases) - 1].height + img.height > max_height):
                cases.append(img)
            else:
                cases[len(cases) - 1] = imgMerge(cases[len(cases) - 1],img)
    
    if debug_mode:
        print("Concat�nation termin�e, nombre de concat�nations : " + str(len(cases)))
       
    
    
    formatnb = "{:0>" + str(len(str(len(cases)))) + "d}" #Formatage du num�ro de sauvegarde
    nb_res = 1 #Nombre de r�sultats sauvegard�s

    #Sauvegarde des images fusionn�es
    for case in cases:
        if debug_mode:
            print("Sauvegarde de l'image " + formatnb.format(nb_res) + "/" + str(len(cases)) + " sauvegard�e", end="\r")
        case.save(pathOutput + "\\" + formatnb.format(nb_res) + conf_extension) #On formate le nom de fa�on � ce que la premi�re image ressorte en format 0x ou 00x selon le nombre d'images
        nb_res += 1
        
    if debug_mode:
        print()



def compress_to_cbz(src_path, archive_name='archive'):
    """
    Compresse le contenu du dossier dans une archive CBZ.
    
    Arguments :
    - src_path : Le chemin d'acc�s du dossier � compresser (cha�ne de caract�res)
    - archive_name (optionnel) : le nom de l'archive (cha�ne de caract�res)
    """
    
    # Cr�er un zipfile � partir de src_path et le renommer en .cbz
    shutil.make_archive(src_path + '/' + archive_name, 'zip', src_path, '.')
    rename(src_path + '/' + archive_name + '.zip', src_path + '/' + archive_name + '.cbz')
    
    # R�cup�rer la liste de tous les dossiers dans src_path
    folders = [f for f in listdir(src_path) if path.isdir(path.join(src_path, f))]

    # Pour chaque dossier, supprimer le dossier et tout son contenu
    for folder in folders:
        shutil.rmtree(path.join(src_path, folder))

                

def process_manhwa(pathRaws, pathOutput):
    """
    Traite les scans d'un manhwa et les sauvegarde dans un dossier.
    
    Arguments :
    - pathRaws : le chemin d'acc�s au dossier contenant des chapitres de scans � traiter (cha�ne de caract�res)
    - pathOutput : le chemin d'acc�s au dossier o� sauvegarder les chapitres de scans trait�s (cha�ne de caract�res)
    """
    
    #Cr�ation du dossier de sauvegarde si il n'existe pas
    if not path.exists(pathOutput):
        makedirs(pathOutput)
    
    #Liste des chapitres � traiter
    chapters = listdir(pathRaws)
    
    #Boucle sur chaque chapitre
    for chapter in chapters:
        print("Traitement du chapitre " + chapter + "/" + str(len(chapters)))#, end="\r")
        process_chapter(pathRaws + "\\" + chapter, pathOutput + "\\" + chapter)
    #print()
    print("Traitement termin�, compression de l'archive")
    compress_to_cbz(pathOutput)
    print("Compression termin�e")
    




process_manhwa(conf_pathRaws, conf_pathOutput)

#TODO: Corriger la g�n�ration d'images trop longues occasionnelles