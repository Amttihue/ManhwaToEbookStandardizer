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