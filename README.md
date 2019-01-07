


# Overview

*BioDispersal* is a QGIS 3 plugin.

Its purpose is to compute ecological continuities based on environments permeability 
and animals potential dispersal areas.
*BioDispersal* has been designed as a 7-steps plugin from raw data preprocessing to 
the final dispersal areas computation.
Parameters settings can be saved to and loaded from a configuration file.

It has been developped by *Mathieu Chailloux* at ![*IRSTEA*](http://www.irstea.fr), 
on mission for the ![*French ecological network resource center*](http://www.trameverteetbleue.fr/) 
(driven by ![*French ministry of ecology*](https://www.ecologique-solidaire.gouv.fr/)).

![dispEx](/docs/pictures/BioDispersalExamplePicture.png)

# Documentation

Available documentation (only in french for now):
 - [Modelling method description](https://github.com/MathieuChailloux/BioDispersal/blob/gh-pages/docs/fr/MethodePermeabiliteMilieux.pdf)
 - [User guide](https://github.com/MathieuChailloux/BioDispersal/blob/gh-pages/docs/fr/Notice_Plugin_BioDispersal1.0.pdf)

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
    
**Links** :
 - [BioDispersal homepage](https://mathieuchailloux.github.io/BioDispersal/)
 - [BioDispersal git repository](https://github.com/MathieuChailloux/BioDispersal)
 - [IRSTEA](http://www.irstea.fr)
 - [UMR TETIS](https://www.umr-tetis.fr)
 - [French ecological network resource center](http://www.trameverteetbleue.fr/)
 - [French ministry of ecology](https://www.ecologique-solidaire.gouv.fr/)

[..]: # [cerf](https://github.com/MathieuChailloux/BioDispersal/blob/gh-pages/icons/cerf.png)
