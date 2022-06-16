import csv
from os import path, mkdir, listdir
from math import sin, cos, radians
from tkinter import Button, Label, Tk, StringVar
from tkinter import filedialog as fd
import threading
from shutil import rmtree
from open3d import io

## Fonction executée lorsque le bouton d'importation est pressé
def select_file():
    ## Execution de l'importation et de la conversion
    ## dans un thread dédié pour permettre le rafraichissement
    ## du label d'état
    th = threading.Thread(target=convert_file)
    th.start()


def convert_file():
    ## Réinitialisation de la couleur de l'état
    state_label.config(foreground="black")
    ## Ouverture d'une boite de dialogue pour la selection de l'emplacement
    filepath = fd.askopenfilename(
        title='Choisir un fichier',
        filetypes=[("Tableur", " .csv")])
    ## Si l'opération à été avortée, on sort de la fonction
    if filepath == "":
        state.set("En attente d'un fichier...")
        return
    ## On retire le bouton de l'affichage pour éviter un conflit
    open_button.pack_forget()
    ## On définit une série de variables pour l'emplacement des différents dossiers et noms de fichiers
    root_path = path.dirname(filepath)
    root_path = root_path + '/'
    output_name = path.basename(filepath)
    output_name = output_name[0: len(output_name) - 4]
    generated_path = root_path + output_name + '/'
    csv_dir = generated_path + output_name + '_csv'
    ply_dir = generated_path + output_name + '_ply'
    ## Lecture du fichier grâce à la bibliothèque csv
    state.set("Lecture du fichier choisi")
    with open(filepath, newline='') as csvinput:
        r = csv.reader(csvinput, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
        lines = list(r)
        ## Création des dossiers de sortie et suppression des précédents
        state.set("Création des dossiers de sortie")
        if path.isdir(root_path + output_name):
            rmtree(root_path + output_name)
        mkdir(root_path + output_name)
        mkdir(csv_dir)
        mkdir(ply_dir)
        temp = []
        lenlines = len(lines)
        ## On transforme les coordonnées polaires en coordonnées cartésiennes
        state.set("Passage des coordonnées polaires en cartésiennes...\nCette opération peut durer un moment")
        for i in range(1, lenlines):
            d = lines[i][1]
            phi = radians(lines[i][0])
            teta = radians(lines[i][2])
            temp.append([d * sin(phi) * cos(teta), d * cos(phi) * cos(teta), d * sin(teta)])
            ## Source : https://medium.com/hackernoon/lidar-basics-the-coordinate-system-a26529615df9

        ## Ecriture du nouveau fichier csv en coordonnées cartésiennes
        with open(csv_dir + '/' + output_name + '.csv', 'w', newline='') as csvoutput:
            state.set("Ecriture des nouvelles données")
            writer = csv.writer(csvoutput, delimiter=' ', quotechar=' ')
            writer.writerows(temp)

    ## Création des fichiers ply avec Opend3D
    for filename in listdir(csv_dir):
        state.set("Génération du modèle 3D")
        pcd = io.read_point_cloud(csv_dir + "/" + filename, format='xyz')
        io.write_point_cloud(ply_dir + "/" + filename[0:len(filename) - 4] + ".ply", pcd)

    ## Passage du label en vert et affichage du bouton
    state_label.config(foreground="green")
    open_button.pack(expand=True)

## Pour l'empacketage une piste est d'utiliser pyinstaller avec la ligne de code suivante
## pyinstaller "chemin-du-script\main.py" --onefile  --hidden-import=numpy --noconsole --upx-dir=upx
