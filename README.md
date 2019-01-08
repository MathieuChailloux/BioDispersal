


# Overview

*BioDispersal* is a QGIS 3 plugin.

Its purpose is to compute ecological continuities based on environments permeability 
and animals potential dispersal areas.
*BioDispersal* has been designed as a 7-steps plugin from raw data preprocessing to 
the final dispersal areas computation.
Parameters settings can be saved to and loaded from a configuration file.

Below is an example of dispersal map created by *BioDispersal* :
![dispEx](/docs/pictures/BioDispersalExamplePicture.png)

It has been developped by *Mathieu Chailloux* at [*IRSTEA*](http://www.irstea.fr), 
on mission for the [*French ecological network resource center*](http://www.trameverteetbleue.fr/) 
(driven by [*French ministry of ecology*](https://www.ecologique-solidaire.gouv.fr/)).

# Installation

*BioDispersal* requires QGIS 3.
Go to plugins menu, install/manage plugins, activate experimental plugins and *BioDispersal* should be available.
Install it and a dear icon should appear. Otherwise, it is available in plugins menu.

# Documentation

Available documentation (only in french for now):
 - [Modelling method description](https://www.umr-tetis.fr/jdownloads/plateformes/Notice_Plugin_BioDispersal1.0.pdf)
 - [User guide](https://www.umr-tetis.fr/jdownloads/plateformes/MethodePermeabiliteMilieux.pdf)

# Sample data

A sample data set can be downloaded at TODO.

To produce above dispersal map, open configuration file *BousquetOrb.xml* 
and run steps 2,3,4,5,7. You should obtain such results (legend is manually assigned) :

GIF
 
# Steps

BioDispersal is a **7 steps** plugin :
 1. Parameters setting
 2. Subnetworks definition
 3. Selection and classification from input data
 4. Data ranking to obtain a complete land use layer for each subnetwork
 5. Friction coefficients definition to obtain a permeability layer for each subnetwork
 6. Weighting of permeability layers if needed (optional step)
 7. Dispersal areas computation
    
Each step is detailed in plugin help panel.

# Quotation

> Chailloux, M. & Amsallem, J. (2018) $BioDispersal$ : a QGIS plugin for modelling potential dispersal areas
    
# Links
 - [BioDispersal homepage](https://www.umr-tetis.fr/index.php/fr/production/donnees-et-plateformes/plateformes/415-biodispersal)
 - [BioDispersal git repository](https://github.com/MathieuChailloux/BioDispersal)
 - [IRSTEA](http://www.irstea.fr)
 - [UMR TETIS](https://www.umr-tetis.fr)
 - [French ecological network resource center](http://www.trameverteetbleue.fr/)
 - [French ministry of ecology](https://www.ecologique-solidaire.gouv.fr/)

