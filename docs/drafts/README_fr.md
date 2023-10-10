
[[English](https://github.com/MathieuChailloux/BioDispersal/blob/master/docs/drafts/README.md) | [Français](https://github.com/MathieuChailloux/BioDispersal/blob/master/docs/drafts/README_fr.md)]

# Aperçu

*BioDispersal* est un plugin QGIS qui permet de modéliser les continuités écologiques par le calcul d’aires potentielles de dispersion des espèces en se basant sur la perméabilité des milieux.

*BioDispersal* définit une procédure en 7 étapes depuis le prétraitements des données jusqu'au calcul des aires de dispersion.
Le paramétrage de l'outil peut être exporté et importé par le biais d'un fichier de configuration.

Voici un exemple de carte de dispersion produite par *BioDispersal* :

![dispEx](/docs/pictures/BioDispersalExamplePicture.png)

*BioDispersal* a été développé par l'[*UMR TETIS*](https://www.umr-tetis.fr) - [*IRSTEA*](http://www.irstea.fr), 
en mission pour le [*centre de ressources Trame verte et bleue*](http://www.trameverteetbleue.fr/) 
(piloté par le [*Ministère de la Transition Écologique et Solidaire*](https://www.ecologique-solidaire.gouv.fr/)).

# Contact

*Développement* : Mathieu Chailloux (mathieu@chailloux.org)

*Coordination* : Jennifer Amsallem (jennifer.amsallem@irstea.fr)
    
# Citation

> Chailloux, M. & Amsallem, J. (2018) BioDispersal : a QGIS plugin for modelling potential dispersal areas

# Installation

*BioDispersal* doit être lancé depuis QGIS 3.4 ou version supérieure avec la bilbiothèque GRASS.

Aller dans le menu *Installer/gérer les extensions*, taper *BioDispersal* dans la barre de recherche et appuyer sur *Installer*. Une icône de cerf apparaît alors dans la barre d'outils.

# Documentation

Documentation disponible :
 - [Tutoriels vidéo](https://www.youtube.com/playlist?list=PL0Wd1JAi6QuHdwALwwJqj5TcfNYvjRbcs)
 - [Notice d'utilisation](https://github.com/MathieuChailloux/BioDispersal/blob/master/docs/fr/NoticeUtilisation_BioDispersal_v1.1.pdf)
 - [Qualification des réservoirs de biodiversité](https://github.com/MathieuChailloux/BioDispersal/blob/master/docs/fr/QualifPatch.pdf)
 - [Présentation de la méthode](https://www.umr-tetis.fr/jdownloads/plateformes/MethodePermeabiliteMilieux.pdf)

# Exemple

Des données d'exemple sont fournies avec le plugin (répertoire *sample_data/BousquetOrb*).

Pour produire la carte ci-dessus, ouvrir le fichier de configuration *BousquetOrb.xml* depuis *BioDispersal* et lancer les étapes 3,4,5,6,7.
 
# Étapes

*BioDispersal* définit une procédure en **7 étapes**:
 1. Définition des paramètres généraux
 2. Déclaration des sous-trames
 3. Sélection et classification des données d'entrée
 4. Fusion et hiérarchisation des données sélectionnées
 5. Définition des coefficients de friction
 6. Pondération des couches de friction si nécessaire (étape optionnelle)
 7. Calcul des aires de dispersion
    
Chaque étape est détaillée dans le panneau d'aide.
    
# Liens
 - [Page web *BioDispersal*](https://www.umr-tetis.fr/index.php/fr/production/donnees-et-plateformes/plateformes/415-biodispersal)
 - [Dépôt git](https://github.com/MathieuChailloux/BioDispersal)
 - [IRSTEA](http://www.irstea.fr)
 - [UMR TETIS](https://www.umr-tetis.fr)
 - [Centre de ressources Trame verte et bleue](http://www.trameverteetbleue.fr/)
 - [Ministère de la Transition Écologique et Solidaire](https://www.ecologique-solidaire.gouv.fr/)

