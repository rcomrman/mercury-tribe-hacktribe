# R27 — capture SPI ARM : résultat partiel

## Résultat

Pour les huit presets et les deux VSB, une frame V30 est calculée sur ARM,
dessinée par `C0015824`, copiée en shadow par `C0015AB4`, puis proposée en huit
pages à `C001851C`. Les **1 024 écritures successives** vers le registre SPI de
fixture sont observées et comparées à la frame. Seize exécutions fournissent
16 384 écritures, avec adresse et valeur enregistrées.

Le worker et le sender complet ne sont pas utilisés dans ce nouveau chemin :
la fixture appelle `C001851C` directement, comme R26. La séquence EXIT et les
fautes après plusieurs pages ne sont pas exécutées. Le résultat est donc un
**succès partiel**, pas la démonstration d'une chaîne ou d'une restauration
complète. Aucun transfert physique n'est effectué.

## Méthode de capture

Le code VSB est chargé en lecture/exécution ; GPIO n'est pas mappé. Une zone
RAM locale simule les registres SPI avec le bit 0x200 positionné. Le stub GDB
de QEMU place un point d'arrêt à `C001862C`, juste avant l'instruction ARM
`str r2, [r3, #0x3c]`. Le banc lit les registres, enregistre l'adresse
`r3+0x3c` et la valeur `r2`, retire le point d'arrêt, exécute l'instruction
originale pas à pas puis rétablit le point d'arrêt. Il n'envoie aucun paquet
d'écriture mémoire et ne modifie aucune instruction VSB. C'est une observation
d'opérandes **avant** écriture, non un accusé de réception matériel.

Chaque capture contient 1 024 paires little-endian `(adresse, valeur)` dans
`reports/recovery_r27/*writes.gz` ; l'octet bas est comparé aux pages V30 et au
shadow. Les 16 captures passent, et un vérificateur indépendant détecte la
corruption d'un octet et l'échange de deux pages différentes. Les traces de
captures ne prouvent ni le contenu d'une FIFO réelle ni les interruptions.

## Limites et coût du raccordement

Le chemin dessine chaque frame par 8 192 appels à `C0015824`, suivi de huit
comparaisons et 1 024 écritures de données. Une copie de 1 024 octets en RAM de
fixture supprimerait ces appels mais ne prouve ni l'autorité de modifier la
source réelle ni sa cohérence pendant un scan concurrent. Aucune mesure de
cycles instrument ou de marge permettant d'affirmer 10 FPS n'est produite.

Changements de paramètres et mini-LFO, plusieurs frames, demandes concurrentes,
EXIT pendant publication, restauration partielle et injection de faute :
**non exécutés dans R27**. Leurs tests hôte antérieurs ne remplacent pas une
séquence ARM capturée. Le blocage suivant est la simulation des dépendances du
sender complet (GPIO, disponibilité SPI et délai matériel) sans altérer les
instructions natives, puis la capture de la restauration de huit pages.

Reproduction : `PATH=/workspace/mercury-tools/bin:$PATH bash
tests/run_recovery_r27.sh custom.VSB backup.VSB`. Le stub GDB exige des sockets
TCP locaux. Les deux VSB sont validés par SHA et restent en lecture seule.
Aucun flash, hook installé, firmware installable ou essai matériel.
