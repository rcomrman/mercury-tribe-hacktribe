# R26 — V30 calculé sur ARM et intégration LCD de laboratoire

## Verdict : succès partiel

Les sources V30 inchangées calculent directement 32 images sur ARM926 sous
QEMU, identiques octet par octet aux références hôte. Dans un même processus
ARM, elles traversent les primitives graphiques Korg et le comparateur natif :
les 1 024 octets du framebuffer puis du shadow sont identiques aux références,
pour les huit presets et les deux VSB.

La chaîne complète worker → sender → SPI simulé n'est **pas démontrée** : la
routine SPI `C001851C` est appelée séparément sur les pages du shadow avec un
double de registre en RAM. Elle retourne succès dans ce banc et le dernier
octet de chaque page est vérifié. Ce double écrase chaque écriture précédente :
il ne capture pas les 128 octets, n'émule pas la FIFO et ne démontre aucun
transfert physique. Aucun GO matériel.

## Exécution et vérification

Le banc reprend le générateur R1 : huit presets, quatre frames chacun, ticks et
notes synthétiques identiques sur hôte et ARM. Le bridge et le moteur graphique
sont compilés sans modification avec Clang ARM926, sans bibliothèque C liée.
Les 32 768 octets ARM sont comparés à la sortie hôte.

La fixture d'intégration charge le code original des deux VSB en lecture et
exécution dans un processus Linux ARM isolé. Elle calcule quatre frames par
preset, dessine avec `C0015824`, appelle `C0015AB4` pour huit pages, vérifie
source et shadow, puis appelle directement `C001851C` huit fois sur le shadow.
Son registre RAM fournit artificiellement le bit `0x200`. Les 16 exécutions
(8 presets × 2 VSB) produisent 64 frames, avec records identiques entre VSB.
Le vérificateur indépendant relit les snapshots et traces ; `in_asm` décrit des
blocs traduits, pas un journal de toutes les écritures.

[Comparaison visuelle V30 ARM / shadow Korg](reports/recovery_r26/comparaison_arm_shadow.png).
Ce n'est pas une capture d'écran physique.

## Ressources mesurées

ELF de rendu seul, ARM 32 bits, `-O2` : `.text` 12 512 octets, `.rodata` 732,
`.bss` 5 372 (bridge et snapshot de fixture). La plus grande pile locale
déclarée par le compilateur est `md_live_render`, 328 octets ; elle n'inclut
pas toute la chaîne d'appels. Le temps mural d'un processus QEMU complet pour
32 frames est enregistré dans `results.json` ; il inclut le démarrage et les
sorties et ne mesure pas les cycles du processeur de l'Electribe. Aucun coût
du transport physique, nombre fiable d'instructions ou budget audio n'est établi.
Les paramètres et quatre mini-LFO restent dans les sources R21 ; ils ne sont
pas exercés par cette fixture de rendu ARM.

## Limites et travaux restants

La séquence `KORG → MERCURY → EXIT → KORG`, les changements de paramètres,
10 FPS en temps logique sur ARM, l'interruption concurrente, les fautes et la
restauration huit pages ne sont **pas exécutés dans R26**. Les tests R25 hôte
ne remplacent pas ces preuves. Il faut une interface périphérique isolée qui
capture toutes les écritures du sender sans modifier les VSB, puis confronter
les 1 024 octets capturés aux frames ARM et tester les interruptions et EXIT.
Le résultat actuel justifie la poursuite logicielle, pas une intégration sur
instrument.

Reproduction : `PATH=/workspace/mercury-tools/bin:$PATH bash
tests/run_recovery_r26.sh custom.VSB backup.VSB`. Aucun flash, firmware
installable, hook installé ou essai matériel.
