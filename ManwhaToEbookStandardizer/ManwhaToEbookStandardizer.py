# -*- coding: latin-1 -*-


from os import listdir, rename, startfile, path, makedirs
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
    return r > 250 and g > 250 and b > 250


def split_image_by_white_bands(image,sharp_mode):
    """
    Découpe une image en plusieurs images en enlevant les bandes de couleur blanche.
    
    Arguments :
    - image : l'objet "Image" de la bibliothèque Pillow à découper
    
    Retourne une liste d'objets "Image" de la bibliothèque Pillow représentant les images découpées.
    """
    
    #Précise le mode de découpage (sharp_mode = True : découpage plus précis mais plus lent, sharp_mode = False : découpage moins précis mais plus rapide)
    sharpness = 10
    if sharp_mode:
        sharpness = 5

    progression_speed = 50
    
    # Liste des images découpées
    images = []
    
    # Charger les pixels de l'image en mémoire
    pixels = image.load()
    
    # Largeur et hauteur de l'image
    width, height = image.size
    
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
            if y3 - y2 > 5:
                images.append(image.crop((0, y2, width, y4)))
            
            # On avance au début de la prochaine bande de couleur blanche
            y1 = y3
        else:
            # Si on n'a pas trouvé de ligne non blanche, on avance au début de la prochaine bande de couleur blanche
            y1 += progression_speed
    
    # Renvoyer la liste des images découpées
    return images



def process_scans(pathRaws, pathOutput):
    """
    Fonction principale qui prend en argument le chemin d'accès aux scans à traiter et le chemin d'accès au dossier de sauvegarde des scans traités
    puis traite les scans et les sauvegarde dans le dossier de sauvegarde
    """
    
    #Création du dossier de sauvegarde si il n'existe pas
    if not path.exists(pathOutput):
        makedirs(pathOutput)

    raws = open_images(pathRaws)        #Liste des scans à traiter

    splitted_images = []                #Liste des images découpées sur les scans
    spl_prog = 1                        #Progression de la découpe des scans
    max_height = 1436
    if len(raws) > 0:
        max_height = int((raws[0].width/79))*209 #Hauteur maximale d'une concaténation d'images (peut être plus grand si une image seule est plus grande que la limite)
    

    formatnbspl = "{:0>" + str(len(str(len(raws)))) + "d}" #Formatage du numéro de découpage

    #Découpage des scans
    for raw in raws:
        print("Découpage de l'image " + formatnbspl.format(spl_prog) + "/" + str(len(raws)), end="\r")
        splitted_images.extend(split_image_by_white_bands(raw,True))
        spl_prog += 1
        
    print("Découpage terminé, nombre de découpages : " + str(len(splitted_images)))
    

    
    formatnbmerge = "{:0>" + str(len(str(len(splitted_images)))) + "d}" #Formatage du numéro de fusion
    merge_prog = 1
    
    #Fusion des images découpées selon la taille max
    cases = []
    for img in splitted_images:
        print("Concaténation de l'image " + formatnbmerge.format(merge_prog) + "/" + str(len(splitted_images)), end="\r")
        
        if cases == []:
            cases.append(img)
        else:
            if (cases[len(cases) - 1].height + img.height > max_height):
                cases.append(img)
            else:
                cases[len(cases) - 1] = imgMerge(cases[len(cases) - 1],img)
    
    print("Concaténation terminée, nombre de concaténations : " + str(len(cases)))
       
    
    
    formatnb = "{:0>" + str(len(str(len(splitted_images)))) + "d}" #Formatage du numéro de sauvegarde
    nb_res = 0 #Nombre de résultats sauvegardés

    #Sauvegarde des images fusionnées
    for case in cases:
        print("Sauvegarde de l'image " + formatnb.format(nb_res + 1) + "/" + str(len(cases)) + " sauvegardée", end="\r")
        case.save(pathOutput + "\\" + str(nb_res) + ".jpg")
        nb_res += 1
        
    print()


    




process_scans(pathRaws, pathOutput)


"""  
###Tests des fonctions
images = open_images(pathRaws)


#On printn la longueur de images :
print("Nombre d'images dans le dossier d'input : " + str(len(images)))




splitted_images = []

spl_prog = 1
formatnbspl = "{:0>" + str(len(str(len(images)))) + "d}"
for image in images:
    print("Découpage de l'image " + formatnbspl.format(spl_prog) + "/" + str(len(images)))
    splitted_images.extend(split_image_by_white_bands(image,False))
    spl_prog += 1
    
#splitted_images = split_image_by_white_bands(images[0])
print("Nombre d'images détectées dans les images d'origine : " + str(len(splitted_images)))

save_subcases = False

if save_subcases:
    i = 0
    formatnb = "{:0>" + str(len(str(len(splitted_images)))) + "d}" #On définit le type de formatage pour avoir une progression propre quant à l'état de la sauvegarde
    for image in splitted_images:
        save_image(image, pathOutput + r"\test" + str(i) + ".png")
        i += 1
        print("Image " + formatnb.format(i) + "/" + str(len(splitted_images)) + " sauvegardée")
        
else:
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
