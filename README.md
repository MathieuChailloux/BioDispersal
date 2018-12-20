
# BioDispersal

BioDispersal is a QGIS 3 plugin.

Its purpose is to compute ecological continuities based on environments permeability and animals potential dispersal areas.

It has been developped by Mathieu Chailloux at *IRSTEA*, on mission for the *French ecological network resource center* (driven by *French ministry of ecology*).


This directory contains :
 - source files (*.py, *.ui, *.qrc, ...)
 - documentation files (docs/fr/*, only in french for now)
 - help files displayed in plugin (help/*)
 - a minimal example (sample_data/). To rerun this example, open QGIS, set workspace to sample_data directory, open BousquetOrb.xml and run steps 3,4,5,7.
      
BioDispersal is a **7 steps** plugin :
 1. Parameters setting
 2. Subnetworks definition
 3. Selection and classification from input data
 4. Data ranking to obtain a complete land use layer for each subnetwork
 5. Friction coefficients definition to obtain a permeability layer for each subnetwork
 6. Weighting of permeability layers if needed (optional step)
 7. Dispersal areas computation
    
Each step is detailed in plugin help panel.
    
**Links** :
 - BioDispersal homepage : https://tetis.teledetection.fr/index.php/fr/expertise-et-transfert/appui-aux-politiques-publiques/item/519-biodispersal
 - BioDispersal git repository : https://github.com/MathieuChailloux/BioDispersal
 - IRSTEA : http://www.irstea.fr
 - French ecological network resource center : http://www.trameverteetbleue.fr/
 - French ministry of ecology : https://www.ecologique-solidaire.gouv.fr/
