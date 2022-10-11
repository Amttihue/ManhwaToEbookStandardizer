from os import listdir, rename
from os.path import isfile, join
from PIL import Image #TODO Importer Pillow pour la manipulation d'images

#Constantes
pathRaws = r"Scans\Raws"
pathOutput = r"Scans\Output"

extension = ".jpg"


#Fonction prenant en argument un chemin et renvoyant la liste des noms des fichiers de ce dossier
def getFiles(path):
    files = [f for f in listdir(path) if isfile(join(path,f))]
    return files

print(getFiles(pathRaws))

def imgMerge(img1,img2):
    print("void")







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