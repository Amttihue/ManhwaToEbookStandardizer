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

#Soit la fonction open_images qui prend en argument un r�pertoire source contenant des images � charger en m�moire,
#puis renvoie une liste d'objets Image de la biblioth�que Pillow
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


#Soit la fonction imgMerge qui prend en argument deux images pr�c�demment charg�es en m�moire,
#puis renvoie le r�sultat de la fusion verticale de ces deux images
def imgMerge(img1, img2):
    # Fusionner les images en les concat�nant verticalement
    image = Image.new('RGB', (max(img1.width, img2.width), img1.height + img2.height))
    image.paste(img1, (0, 0))
    image.paste(img2, (0, img1.height))
    
    # Renvoyer la nouvelle image fusionn�e
    return image


#Soit la fonction save_image qui prend en argument une image et un chemin de sauvegarde (path + nom)
#puis sauvegarde l'image dans le fichier correspondant
def save_image(image, filename):
    """
    Sauvegarde une image dans un fichier.
    
    Arguments :
    - image : l'image � sauvegarder (objet Image de la biblioth�que Pillow)
    - filename : le nom du fichier dans lequel sauvegarder l'image (cha�ne de caract�res)
    """

    # On v�rifie que le fichier a bien une extension
    if not filename.endswith(".jpg") and not filename.endswith(".png"):
        filename += extension
    image.save(filename)


#Soit la fonction open_image_with_windows_explorer qui prend en argument un chemin d'acc�s � une image et l'ouvre dans la visionneuse de photos windows
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


#Soit la fonction imgListMerge qui prend en argument une liste d'images pr�c�demment charg�es en m�moire puis les fusionne les unes � la suite des autres
def imgListMerge(imgList):
    for i in range(len(imgList)-1):
        imgList[i+1] = imgMerge(imgList[i], imgList[i+1])
    return imgList[len(imgList)-1]

def is_color_close_to_white(color):
    r, g, b = color
    return r > 250 and g > 250 and b > 250


def split_image_by_white_bands(image,sharp_mode):
    """
    D�coupe une image en plusieurs images en enlevant les bandes de couleur blanche.
    
    Arguments :
    - image : l'objet "Image" de la biblioth�que Pillow � d�couper
    
    Retourne une liste d'objets "Image" de la biblioth�que Pillow repr�sentant les images d�coup�es.
    """
    
    #Pr�cise le mode de d�coupage (sharp_mode = True : d�coupage plus pr�cis mais plus lent, sharp_mode = False : d�coupage moins pr�cis mais plus rapide)
    sharpness = 10
    if sharp_mode:
        sharpness = 5

    progression_speed = 50
    
    # Liste des images d�coup�es
    images = []
    
    # Charger les pixels de l'image en m�moire
    pixels = image.load()
    
    # Largeur et hauteur de l'image
    width, height = image.size
    
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
            if y3 - y2 > 5:
                images.append(image.crop((0, y2, width, y4)))
            
            # On avance au d�but de la prochaine bande de couleur blanche
            y1 = y3
        else:
            # Si on n'a pas trouv� de ligne non blanche, on avance au d�but de la prochaine bande de couleur blanche
            y1 += progression_speed
    
    # Renvoyer la liste des images d�coup�es
    return images



def process_scans(pathRaws, pathOutput):
    """
    Fonction principale qui prend en argument le chemin d'acc�s aux scans � traiter et le chemin d'acc�s au dossier de sauvegarde des scans trait�s
    puis traite les scans et les sauvegarde dans le dossier de sauvegarde
    """
    
    #Cr�ation du dossier de sauvegarde si il n'existe pas
    if not path.exists(pathOutput):
        makedirs(pathOutput)

    raws = open_images(pathRaws)        #Liste des scans � traiter

    splitted_images = []                #Liste des images d�coup�es sur les scans
    spl_prog = 1                        #Progression de la d�coupe des scans
    max_height = 1436
    if len(raws) > 0:
        max_height = int((raws[0].width/79))*209 #Hauteur maximale d'une concat�nation d'images (peut �tre plus grand si une image seule est plus grande que la limite)
    

    formatnbspl = "{:0>" + str(len(str(len(raws)))) + "d}" #Formatage du num�ro de d�coupage

    #D�coupage des scans
    for raw in raws:
        print("D�coupage de l'image " + formatnbspl.format(spl_prog) + "/" + str(len(raws)), end="\r")
        splitted_images.extend(split_image_by_white_bands(raw,True))
        spl_prog += 1
        
    print("D�coupage termin�, nombre de d�coupages : " + str(len(splitted_images)))
    

    
    formatnbmerge = "{:0>" + str(len(str(len(splitted_images)))) + "d}" #Formatage du num�ro de fusion
    merge_prog = 1
    
    #Fusion des images d�coup�es selon la taille max
    cases = []
    for img in splitted_images:
        print("Concat�nation de l'image " + formatnbmerge.format(merge_prog) + "/" + str(len(splitted_images)), end="\r")
        
        if cases == []:
            cases.append(img)
        else:
            if (cases[len(cases) - 1].height + img.height > max_height):
                cases.append(img)
            else:
                cases[len(cases) - 1] = imgMerge(cases[len(cases) - 1],img)
    
    print("Concat�nation termin�e, nombre de concat�nations : " + str(len(cases)))
       
    
    
    formatnb = "{:0>" + str(len(str(len(splitted_images)))) + "d}" #Formatage du num�ro de sauvegarde
    nb_res = 0 #Nombre de r�sultats sauvegard�s

    #Sauvegarde des images fusionn�es
    for case in cases:
        print("Sauvegarde de l'image " + formatnb.format(nb_res + 1) + "/" + str(len(cases)) + " sauvegard�e", end="\r")
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
    print("D�coupage de l'image " + formatnbspl.format(spl_prog) + "/" + str(len(images)))
    splitted_images.extend(split_image_by_white_bands(image,False))
    spl_prog += 1
    
#splitted_images = split_image_by_white_bands(images[0])
print("Nombre d'images d�tect�es dans les images d'origine : " + str(len(splitted_images)))

save_subcases = False

if save_subcases:
    i = 0
    formatnb = "{:0>" + str(len(str(len(splitted_images)))) + "d}" #On d�finit le type de formatage pour avoir une progression propre quant � l'�tat de la sauvegarde
    for image in splitted_images:
        save_image(image, pathOutput + r"\test" + str(i) + ".png")
        i += 1
        print("Image " + formatnb.format(i) + "/" + str(len(splitted_images)) + " sauvegard�e")
        
else:
    save_image(imgListMerge(splitted_images), pathOutput + r"\test.jpg")

    open_image_with_windows_explorer(pathOutput + r"\test.jpg")

"""


"""
imgMerge : fusionne deux images (ou plus en bouclant son r�sultat), return une image ou un fichier temp (� voir avec l'outil utilis�)
^ pas aussi simple



VERSION AVANCEE
blankFinder : cherche les lignes de blanc d'une image, retourne des coordonn�es




-------------
Comment traiter l'image ?
1 ouvrir chaque image
2 y chercher du blanc
3 rogner le blanc des images (trouver un moyen de rogner celui qui est � l'int�rieur)
4 fusionner toutes les images trait�es celon des dimensions donn�es (ou relatives)

OU

Ouvrir et fusionner toutes les images en une seule immense image
la red�couper en extrayant dans l'ordre tout ce qui n'est pas du blanc
refusionner toutes les images en une seule immense image
la red�couper selon un format pr�d�finit (ou relatif ?)

si la m�moire ram peut g�rer la seconde solution, c'est s�rement la fa�on la plus simple de proc�der
sinon on peut proc�der par blocs de x images

wait, troisi�me solution qui est en fait la premi�re revisit�e avec la seconde :
1 ouvrir chaque image
2 en exporter tout ce qui n'est pas du blanc
3 tout fusionner en une immense image (ou par blocs)
4 red�couper selon un format pr�d�finit (ou relatif ?)

SOLUTION "FINALE" (la mienne, pas celle de l'autre moustachu)
apr�s une autre solution qui �viterait le d�coupage d'une illustration et 
de charger une image immenss�ment longue en m�moire, ce serait d'ex�cuter 
les deux premi�res �tapes de la troisi�me solution, de fusionner les images
selon une limite de pixels � respecter en hauteur quant au r�sultat de la 
dite fusion des images, sinon on ajoute pas l'image suivante � la fusion 
mais � la suivante.

�a �viterait le d�coupage fr�quent des textes et illustrations.
Cependant, une image trop longue de base serait tout de m�me d�coup�e
suivant la limite max impos�e, et ce malgr� le malencontreux d�coupage
d'une illustration ou d'un dialogue.

Afin d'y palier, si cette image anormalement longue est due � un changement
de couleur d'arri�re plan, il serait int�ressant, au lieu de seulement 
supprimer les blancs,de supprimer les blocs de noirs, voir de "simplement"
check si toute une ligne est de la m�me couleur. Cela pourrait cependant 
poser probl�me pour les d�grad�s (� moins de v�rifier si cette couleur est 
omnipr�sente sur tout le bloc mais ce serait chiant � faire en d�limitant 
le d�grad� de l'illustration)
Ainsi, v�rifier seulement le noir complet (en plus du blanc) serait peut 
�tre int�ressant, mais aussi dangereux (risque de supprimer des 
s�parateurs de dialognes, cases, etc)
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
