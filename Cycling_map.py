import geotiler
import matplotlib.pyplot as plt
from datetime import datetime
import math
import xml.etree.ElementTree as ET
import os
import shutil
import numpy as np


def list_len_sync(list1, list2):
    """
    :param list1: liste1 en entrée
    :param list2: liste2 en entrée
    :return: liste1 et liste2 de la même longueur. La longueur finale est la longueur initiale la plus petite
    """
    if len(list1) != len(list2):
        dif = len(list1) - len(list2)
        if dif > 0:
            for i in range(dif):
                list1.pop()
        elif dif < 0:
            for i in range(abs(dif)):
                list2.pop()
    return list1, list2


def parsefile(file):
    """

    :param file: fichier.gpx
    :return:    name : le nom de la sortie
                alt : liste contenant toutes les altitudes enregistrées
                lat : liste contenant toutes les latitudes enregistrées
                long : liste contenant toutes les longitudes enregistrées
                time : liste contenant toutes les horaires enregistrées
                hb : liste contenant toutes les valeurs de fréquence cardiaque enregistrées
    """
    lat = []  # latitude
    long = []  # longitude
    alt = []  # altitude
    time = []  # temps
    hb = []  # heartbeat

    # FICHIER A LIRE
    name = file
    # OUVERTURE DU XML ET PARSING
    ET.fromstring(open(file).read())
    tree = ET.parse(file)

    # PARSING DU XML ET CREATION LISTES ALTITUDE & TEMPS
    for elem in tree.iter():
        if elem.tag.endswith('name'):
            name = elem.text
        if elem.tag.endswith('ele'):
            alt.append(float(elem.text))
        if elem.tag.endswith('hr'):
            hb.append(float(elem.text))
        if elem.tag.endswith('time'):
            time.append(elem.text)
    # PARSING DU XML ET AJOUT DE LA LATITUDE ET LONGITUDE DANS DES LISTES
        if elem.tag.endswith('trkpt'):
            lat.append(float(elem.attrib['lat']))
            long.append(float(elem.attrib['lon']))
    open(file).close()

    return name, alt, lat, long, time, hb


def timevalues(time):
    # RENSEIGNEMENT DU FORMAT DATE
    """

    :param time: liste des temps de la sortie cycliste
    :return:    temps : temps total de la sortie
                jour : jour de la sortie cycliste
    """
    date_format = '%Y-%m-%dT%H:%M:%SZ'
    try:
        jour = datetime.strptime(time[1], date_format)
    except(ValueError):
        date_format = '%Y-%m-%dT%H:%M:%S.000Z'
        jour = datetime.strptime(time[1], date_format)
    # CALCUL DU TEMPS TOTAL
    temps = datetime.strptime(time[-1], date_format) - datetime.strptime(time[0], date_format)
    return temps, jour


def cumuldeniv(alt, coef) :
    """
    :param alt: liste des altitudes
    :param coef: coefficient de lissage pour eviter les erreurs de gps
    :return:
    """
    deniv = 0
    for i in range(len(alt)):
        try:
            if alt[i + coef] > alt[i]:
                deniv = deniv + alt[i + 1] - alt[i]
        except IndexError:
            pass
    return deniv


def distanceSpeed(time, lat, long):
    """
    :param time: liste du temps d'enregistrement d'une donnée
    :param lat: liste des latitudes
    :param long: liste des longitudes
    :return:    distance : distance totale
                kilom : liste du kilometrage
                vit : liste de la vitesse entre 2 points
    """
    date_format = '%Y-%m-%dT%H:%M:%SZ'
    distance = 0
    kilom = []
    vit = []
    for i in range(len(time)):
        try:
            a = datetime.strptime(time[i], date_format)
            b = datetime.strptime(time[i + 1], date_format)
            delta = str(b - a)
            coupe = delta.split(':')
            # Calcul d'une distance entre 2 point de latitude et longitude donnée
            c = math.acos(math.sin(math.radians(lat[i])) * math.sin(math.radians(lat[i + 1])) + math.cos(
                math.radians(lat[i])) * math.cos(math.radians(lat[i + 1])) * math.cos(
                math.radians(long[i] - long[i + 1]))) * 6371
            distance = distance + c
            kilom.append(distance)
            try:
                speed = 36 * c / int(coupe[2])
            except ZeroDivisionError:
                speed = 0
            vit.append(speed * 100)
        except (ValueError, IndexError):
            pass
    return distance, kilom, vit


def meanSpeed(vit, coef):
    """
    :param vit: liste de la vitesse entre 2 points
    :param coef: coefficient pour la moyenne flottante
    :return: liste de la vitesse flottante sur coef valeurs
    """
    Mvit = []
    for i in range(int(len(vit))):
        try:
            numsum = 0
            for j in range(coef):
                numsum = numsum + vit[i + j]
            Mvit.append(float(numsum / coef))
        except IndexError:
            pass
    return Mvit


def Map(name, alt, lat, long, distance, deniv, jour, temps, kilom, hb, topo='grenoble'):
    """
    :param name: nom de la sortie
    :param alt: liste des altitudes
    :param lat: liste de latitudes
    :param long: liste des longitudes
    :param distance: distance totale
    :param deniv: denivelé cumulé
    :param jour: jour
    :param temps: temps total
    :param kilom: liste du kilometrage
    :param hb: liste de la fréquence cardiaque
    :param topo: optionnel, gère les ordonnées du graphique pour avoir des graphs homogènes si sortie depuis grenoble

    Créé un fichier .pdf résumant la sortie vélo
    """
    # CREATION DES ABSCISSES ET HOMOGENEISATION DU NOMBRE DE POINTS
    alt.pop(0)
    # CALCUL DE LA VITESSE MOYENNE

    coupe = str(temps).split(':')
    total = int(coupe[0]) + int(coupe[1]) / 60 + int(coupe[2]) / 3600
    Vbarre = "%.2f" % (distance / total)

    distance = float("%.2f" % distance)
    deniv = float("%.2f" % deniv)

    maxLat, minLat, maxLon, minLon = max(lat), min(lat), max(long), min(long)

    # Parametrage zoom
    zoom = 12

    if (maxLat - minLat or maxLon - minLon) < 0.02:
        zoom = 16
    elif (maxLat - minLat or maxLon - minLon) < 0.05:
        zoom = 15
    elif (maxLat - minLat or maxLon - minLon) < 0.1:
        zoom = 14
    elif (maxLat - minLat and maxLon - minLon) < 0.2:
        zoom = 13
    # print(str(maxLat - minLat), str(maxLon - minLon))
    print('zoom = ' + str(zoom))
    # createthe plot
    map = geotiler.Map(center=((maxLon + minLon) / 2, ((maxLat + minLat) / 2)), zoom=zoom, size=(1750, 2000))
    image = geotiler.render_map(map)

    ymax, ymin = max(alt) + 50, min(alt) - 50
    # valeurs par défaut selon lieux
    if topo == 'grenoble':
        ymax, ymin = 1500, 100

    # PLOT DES COURBES
    fig = plt.figure(figsize=(15, 8), dpi=1000)
    plt.suptitle(name + ' ' + str(jour.date()) + '\n' + 'denivelé={}m, vitesse moy={}km/h'.format(deniv, Vbarre) + '\n'
                 + 'distance = {}km, temps = {}'.format(distance, temps), fontsize=10)

    # ALTITUDE
    kilom = list_len_sync(kilom, alt)[0]
    alt = list_len_sync(kilom, alt)[1]

    ax2 = fig.add_subplot(121)
    ax2.set_ylabel('Altitude (m)')
    ax2.grid(axis='y', color='grey', alpha=0.5)
    ax2.set_xlim(0, max(kilom))
    ax2.set_ylim(ymin, ymax)
    ax2.fill_between(kilom, 0, alt, color='grey', label='Altitude')
    ax2.legend(loc=2)
    # heartbeat
    if hb != []:
        hb = list_len_sync(kilom, hb)[1]
        ax1 = ax2.twinx()
        ax1.plot(kilom, hb, color='blue', label='bpm')
        ax1.set_ylim(60, 210)
        ax1.set_yticks(np.arange(70, 210, 20.0))
        ax1.set_xlim(0, max(kilom))
        ax1.legend(loc=1)
    # TRAJET
    ax3 = fig.add_subplot(122)

    ax3.axis('off')
    Long = []
    Lat = []
    for i in range(len(lat)):
        x, y = map.rev_geocode((float(long[i]), float(lat[i])))
        Long.append(x)
        Lat.append(y)
    ax3.imshow(image)
    ax3.plot(Long, Lat, c='blue', linewidth=1)
    plt.draw()
    plt.savefig('pdf\\' + str(jour.date()) + ' ' + name + '.pdf', bbox_inches='tight')


def main():
    """

    lorsque executé dans le repertoire contenant des fichiers .gpx, créé pour chaque fichier .gpx un fichier .pdf, puis le déplace dans le sous dossier pdf
    :return:
    """

    if not os.path.exists(os.getcwd() + '\\/pdf'):
        os.makedirs(os.getcwd() + '\\/pdf')
    f = []
    coef = 30
    for file in os.listdir(os.getcwd()):
        f.append(file)
    for i in range(len(f)):
        if f[i].endswith('.gpx'):
            print('Creation du profil pour le fichier :' + f[i])
            Map(parsefile(f[i])[0],
                parsefile(f[i])[1],
                parsefile(f[i])[2],
                parsefile(f[i])[3],
                distanceSpeed(parsefile(f[i])[4],parsefile(f[i])[2],parsefile(f[i])[3])[0],
                cumuldeniv(parsefile(f[i])[1], coef),
                timevalues(parsefile(f[i])[4])[1],
                timevalues(parsefile(f[i])[4])[0],
                distanceSpeed(parsefile(f[i])[4],parsefile(f[i])[2],parsefile(f[i])[3])[1],
                parsefile(f[i])[5])
            try:
                shutil.move(f[i], 'pdf\\')
            except(shutil.Error):
                os.remove(f[i])


if __name__ == '__main__':
    main()
