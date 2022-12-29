# -*- coding: latin-1 -*-


from os import listdir, rename, startfile
from os.path import isfile, join
from PIL import Image

#Constantes
pathRaws = r"Scans\Raws"
pathOutput = r"Scans\Output"

extension = ".jpg"


#Fonction prenant en argument un chemin et renvoyant la liste des noms des fichiers de ce dossier
def getFiles(path):
    files = [f for f in listdir(path) if isfile(join(path,f))]
    return files

print(getFiles(pathRaws))

#Soit la fonction open_images qui prend en argument un répertoire source contenant des images à charger en mémoire,
#puis renvoie une liste d'objets Image de la bibliothèque Pillow
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


#Soit la fonction imgMerge qui prend en argument deux images précédemment chargées en mémoire,
#puis renvoie le résultat de la fusion verticale de ces deux images
def imgMerge(img1, img2):
    # Fusionner les images en les concaténant verticalement
    image = Image.new('RGB', (max(img1.width, img2.width), img1.height + img2.height))
    image.paste(img1, (0, 0))
    image.paste(img2, (0, img1.height))
    
    # Renvoyer la nouvelle image fusionnée
    return image


#Soit la fonction save_image qui prend en argument une image et un chemin de sauvegarde (path + nom)
#puis sauvegarde l'image dans le fichier correspondant
def save_image(image, filename):
    """
    Sauvegarde une image dans un fichier.
    
    Arguments :
    - image : l'image à sauvegarder (objet Image de la bibliothèque Pillow)
    - filename : le nom du fichier dans lequel sauvegarder l'image (chaîne de caractères)
    """

    # On vérifie que le fichier a bien une extension
    if not filename.endswith(".jpg") and not filename.endswith(".png"):
        filename += extension
    image.save(filename)


#Soit la fonction open_image_with_windows_explorer qui prend en argument un chemin d'accès à une image et l'ouvre dans la visionneuse de photos windows
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


#Soit la fonction imgListMerge qui prend en argument une liste d'images précédemment chargées en mémoire puis les fusionne les unes à la suite des autres
def imgListMerge(imgList):
    for i in range(len(imgList)-1):
        imgList[i+1] = imgMerge(imgList[i], imgList[i+1])
    return imgList[len(imgList)-1]

def is_color_close_to_white(color):
    r, g, b = color
    return r > 240 and g > 240 and b > 240


def split_image_by_white_bands(image):
    """
    Découpe une image en plusieurs images en enlevant les bandes de couleur blanche.
    
    Arguments :
    - image : l'objet "Image" de la bibliothèque Pillow à découper
    
    Retourne une liste d'objets "Image" de la bibliothèque Pillow représentant les images découpées.
    """
    # Liste des images découpées
    images = []
    
    # Charger les pixels de l'image en mémoire
    pixels = image.load()
    
    # Largeur et hauteur de l'image
    width, height = image.size
    
    # Scanner l'image ligne par ligne pour trouver les bandes de blanc
    y1 = 0
    nbwlines = 0
    foundCase = False
    while y1 < height:
        # Trouver la première ligne non blanche
        if not all([is_color_close_to_white(pixels[x, y1]) for x in range(0,width,1)]):
            #print("Trouvé une première ligne de couleur à la ligne {" + str(y1) +"}.")
            foundCase = True 
            y2 = y1

        # Trouver la dernière ligne non blanche
        while y1 < height and not all([is_color_close_to_white(pixels[x, y1]) for x in range(0,width,1)]): #On check tout les 10 pixels pour gagner du temps, pas besoin de trop de précision en largeur.
            y1 += 10
        
        #ajout du bloc à la liste
        if foundCase:
            #print("Case trouvée de la ligne", str(y2),"à la ligne",str(y1))
            if y1-y2 > 5:
                images.append(image.crop((0, y2, width, y1))) #Ajout de la sélection à la liste
            foundCase = False #fin de la détection de la case
            
            
        
        y1 += 5 #Pour optimiser la vitesse du programme j'ai changé le palier de 1 à 10. La rapidité est vraiment remarquable par rapport à la précédente version. Cependant, on perd beaucoup en précision. Des gardes fous de précision en mode detection de collision pourraient régler ça assez facilement.
        nbwlines += 5
    
    #print("Nombre de lignes blanches : " + str(nbwlines) + " sur " + str(height) + " lignes.")
    # Renvoyer la liste des images découpées
    return images





    
###Tests des fonctions
images = open_images(pathRaws)


#On printn la longueur de images :
print("Nombre d'images dans le dossier d'input : " + str(len(images)))




splitted_images = []

spl_prog = 1
for image in images:
    print("Découpage de l'image " + str(spl_prog) + " sur " + str(len(images)))
    splitted_images.extend(split_image_by_white_bands(image))
    spl_prog += 1

#splitted_images = split_image_by_white_bands(images[0])
print("Nombre d'images détectées dans les images d'origine : " + str(len(splitted_images)))


i = 0
for image in splitted_images:
    save_image(image, pathOutput + r"\test" + str(i) + ".png")
    print("Image " + str(i) + " sauvegardée")
    i += 1
    

"""
save_image(imgListMerge(splitted_images), pathOutput + r"\test.jpg")

open_image_with_windows_explorer(pathOutput + r"\test.jpg")
"""



"""
imgMerge : fusionne deux images (ou plus en bouclant son résultat), return une image ou un fichier temp (à voir avec l'outil utilisé)
^ pas aussi simple



VERSION AVANCEE
blankFinder : cherche les lignes de blanc d'une image, retourne des coordonnées




-------------
Comment traiter l'image ?
1 ouvrir chaque image
2 y chercher du blanc
3 rogner le blanc des images (trouver un moyen de rogner celui qui est à l'intérieur)
4 fusionner toutes les images traitées celon des dimensions données (ou relatives)

OU

Ouvrir et fusionner toutes les images en une seule immense image
la redécouper en extrayant dans l'ordre tout ce qui n'est pas du blanc
refusionner toutes les images en une seule immense image
la redécouper selon un format prédéfinit (ou relatif ?)

si la mémoire ram peut gérer la seconde solution, c'est sûrement la façon la plus simple de procéder
sinon on peut procéder par blocs de x images

wait, troisième solution qui est en fait la première revisitée avec la seconde :
1 ouvrir chaque image
2 en exporter tout ce qui n'est pas du blanc
3 tout fusionner en une immense image (ou par blocs)
4 redécouper selon un format prédéfinit (ou relatif ?)

SOLUTION "FINALE" (la mienne, pas celle de l'autre moustachu)
après une autre solution qui éviterait le découpage d'une illustration et 
de charger une image immenssément longue en mémoire, ce serait d'exécuter 
les deux premières étapes de la troisième solution, de fusionner les images
selon une limite de pixels à respecter en hauteur quant au résultat de la 
dite fusion des images, sinon on ajoute pas l'image suivante à la fusion 
mais à la suivante.

ça éviterait le découpage fréquent des textes et illustrations.
Cependant, une image trop longue de base serait tout de même découpée
suivant la limite max imposée, et ce malgré le malencontreux découpage
d'une illustration ou d'un dialogue.

Afin d'y palier, si cette image anormalement longue est due à un changement
de couleur d'arrière plan, il serait intéressant, au lieu de seulement 
supprimer les blancs,de supprimer les blocs de noirs, voir de "simplement"
check si toute une ligne est de la même couleur. Cela pourrait cependant 
poser problème pour les dégradés (à moins de vérifier si cette couleur est 
omniprésente sur tout le bloc mais ce serait chiant à faire en délimitant 
le dégradé de l'illustration)
Ainsi, vérifier seulement le noir complet (en plus du blanc) serait peut 
être intéressant, mais aussi dangereux (risque de supprimer des 
séparateurs de dialognes, cases, etc)
"""


"""
def countTotalFiles(c1,c2):
    return len(c1) + len(c2)
    

def collecFusion(path1,path2,path3):
    collec1 = getFiles(path1)
    collec2 = getFiles(path2)
    filesCount = countTotalFiles(collec1,collec2)
    maxDigit = len(str(filesCount))

    currentNumber = 1
    format = "{:0" + str(maxDigit) +"}"

    for f in collec1:
        rename(path1 + "\\" + f, path3 + "\\" + format.format(currentNumber) + extension)
        currentNumber += 1

    for f in collec2:
        rename(path2 + "\\" + f, path3 + "\\" + format.format(currentNumber) + extension)
        currentNumber += 1
"""


#collecFusion(pathCollec1,pathCollec2,pathCollec1)
