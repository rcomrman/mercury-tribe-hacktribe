# Mercury Dust — R25 : premier prototype LCD natif en laboratoire

## Verdict : succès partiel

Une image issue du moteur V30 traverse les primitives graphiques et le
comparateur ARM originaux dans une fixture isolée. Le worker atteint le sender,
qui se heurte à la première écriture GPIO, faute `0xBC` avec handle nul. La
routine de transmission des 128 octets n'est pas atteinte : aucune donnée
physiquement transmise ni argument de cette routine n'est revendiqué.

Le V30 est calculé sur l'hôte avec les sources inchangées et des entrées
musicales synthétiques, puis ses octets sont inclus dans le banc ARM. Ce test
ne compile pas V30 dans le processus ARM et ne valide pas le transport musical
depuis le séquenceur réel.

## Chaîne expérimentale

Pour les huit presets, une frame V30 est produite par `tests/recovery_r1/frames.c`.
La fixture utilise 8 192 appels de la primitive Korg `C0015824` pour dessiner
l'image dans une RAM anonyme mappée à l'adresse graphique native. Le code VSB
est chargé en lecture/exécution ; les VSB d'entrée sont vérifiés par SHA et
restent inchangés. Le framebuffer est comparé aux 1 024 octets V30.

La voie comparateur appelle `C0015AB4` huit fois, force=1, et vérifie chaque
page de 128 octets après copie dans le shadow. La voie worker appelle
`C0015FA0`, qui passe par le comparateur et entre dans `C001613C`, puis tombe
sur GPIO `0xBC` : les registres ne sont pas remplacés par un faux périphérique.
L'image du sender et son shadow ne doivent pas être assimilés à des données
réellement envoyées au LCD.

**32 exécutions ARM** : huit presets × deux voies × deux VSB. Les seize paires
de records sont identiques. Les seize fautes GPIO sont attendues. Les traces
`in_asm` établissent des blocs traduits, pas un comptage exhaustif d'exécution.
Un vérificateur distinct relit les snapshots et les pages des deux images.

L'image [comparaison V30 / shadow ARM](reports/recovery_r25/comparaison_v30_shadow.png)
montre huit références et leurs shadows ; ce ne sont pas des captures d'écran
matériel ni des pages transmises physiquement.

## Cadence et transitions simulées

Une fixture hôte distincte utilise le moteur persistant et le triple buffer R21.
Elle exécute 80 frames à des instants **logiques** espacés de 100 ms, change
de preset tous les dix cycles et injecte des ticks 24 PPQN synthétiques. Elle
copie les huit pages d'un slot emprunté et vérifie leur égalité avec la frame
privée, puis conserve et restaure une image Korg synthétique. Aucun ordonnanceur
ARM réel, débit LCD ou marge audio n'est mesuré ; le bridge R21 utilise son
propre delta de rendu, cette expérience ne qualifie pas la synchronisation BPM
sur l'instrument.

Les contrôles négatifs du banc hôte détectent une page corrompue et une
restauration partielle. Une demande Korg est représentée par un indicateur
local pendant une publication ; EXIT suspend une copie à mi-frame, empêche sa
continuation et libère le lecteur. Une faute rend l'état terminal. Ce sont des
ordres séquentiels de fixture, pas des préemptions matérielles ou un protocole
de restauration Korg. La faute ARM après comparaison est observée au GPIO ; le
transfert réellement interrompu et l'ACK physique restent non exécutés.

| Propriété | Résultat |
|---|---|
| Image V30, huit presets | démontrée avec entrées synthétiques sur hôte |
| Pixels Korg et huit pages comparateur | démontrés dans QEMU sur les deux VSB |
| Worker → sender | entrée observée, arrêt à la frontière GPIO |
| 128 octets présentés à la routine SPI | non démontré dans cette chaîne |
| 10 FPS, EXIT, faute, concurrence | modèle hôte séquentiel, non matériel |
| LCD réel, ACK, audio, synchronisation native | non démontrés ; NO GO matériel |

Reproduire avec `PATH=/workspace/mercury-tools/bin:$PATH bash
tests/run_recovery_r25.sh custom.VSB backup.VSB`. Les fichiers VSB sont exigés
par SHA et ne sont ni modifiés ni publiés.

La piste mérite d'être poursuivie en laboratoire pour rapprocher le calcul V30
de l'exécution ARM et observer, avec une interface de transport explicitement
simulée, les octets effectivement proposés au sender. Une telle fixture devra
préserver la frontière entre données observées et transmission physique ; elle
n'autorise aucun flash ni essai sur instrument.
