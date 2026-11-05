# R23.3 — fin logicielle et transfert LCD

**Aucune primitive native prouvant la réception physique par le LCD n'a été
identifiée.** `C0015CDC` attend que le bit `0x200` d'un registre SPI soit à 1.
L'utilisation de ce bit avant chaque écriture suggère une disponibilité du
contrôleur, mais son sens matériel exact et la fin d'émission sur les broches
requièrent la documentation du contrôleur et des mesures indépendantes.

## Graphe et preuves ARM

Les plages `C00117C8..17FC`, `C0015CDC..5D14`, `C0016100..6230` et
`C0018398..86D4` ont été comparées octet pour octet entre les deux VSB. Les
images originales sont vérifiées par SHA avant et après les essais. Les
adresses ci-dessous renvoient aux instructions originales ; désassemblages
antérieurs dans `reports/recovery_r9/native_disassembly.txt` et
`reports/recovery_r23_1/lcd-disassembly.txt`.

| Étape | Instructions observées | Portée |
|---|---|---|
| Page | `C0016160 → C0016C18`, `C001617C..61A0 → C00160C4` | GPIO puis commandes ; première frontière périphérique, pas de preuve d'envoi |
| Attente | `C00161B0 → C0015CDC → C00117C8` | boucle jusqu'au bit observé ; aucun délai maximum dans cette boucle |
| Source | `C00161D0 → C0015A60`, `C00161D8 → C0015A98` | pointeur shadow et longueur, 128 octets pour une page |
| Données | `C0016200 → C0016100 → C001851C` | boucle d'écriture à SPI +0x3C ; retour local ne prouve pas le bus |
| Après données | `C0016210 → C0015CDC`, `C0016224 → C001673C` | nouvelle attente puis délai ; aucune lecture d'ACK LCD identifiée |

`C00117DC` lit le mot à base SPI +0x10 ; `C00117E0` masque `0x200`, et
`C00117E8..17F4` renvoie 0 ou 1. `C0015CF4..5D08` répète l'appel tant que
le résultat ne vaut pas 1. `C00185DC..862C` utilise ce même prédicat avant
d'écrire un mot comprenant l'octet source dans le registre +0x3C.
`C00185D0` initialise un compteur 1000 pour chaque octet ; son expiration mène
à `C00298BC` à `C00186BC`. La première vérification de configuration +0x40
peut également appeler `C00298BC` à `C0018584`. R9 a relevé que ce chemin
d'erreur peut lui-même utiliser le LCD ; aucun protocole général de reprise ou
absence de réentrée n'est établi.

`C001851C` retourne un indicateur local à `C00186C0..86C4`. Son appelant
`C0016100` revient sans contrôle explicite de cette valeur ; cela ne constitue
pas une confirmation de réception. Une interruption ou un retour tardif après
écriture restent NON OBSERVÉS sur le matériel. L'identification exhaustive des
IRQ/FIQ, DMA, files et FIFO est NON DÉMONTRÉE ; l'absence de telles opérations
dans cette boucle ne prouve pas leur absence ailleurs.

## Nouvelles expériences

Sur chaque VSB, cinq processus QEMU exécutent le code ARM original. Un tableau
de RAM locale tient lieu d'entrée de registre, **sans mapper le MMIO réel**.

| Cas | Entrée locale | Observation |
|---|---|---|
| 0 / 1 | bit 0x200 absent / présent | `C00117C8` retourne 0 / 1 |
| 2 / 3 | bit absent / présent | attente interrompue par timeout hôte / retour logiciel |
| 4 | bit maintenu à 1, données 0..127 | `C001851C` retourne 1 ; la dernière écriture en RAM contient le dernier octet |

Dix exécutions, avec résultats identiques entre VSB ; les traces ARM sont
enregistrées et relues par un vérificateur distinct. Le timeout signifie que
le banc a arrêté QEMU, pas que l'instrument rencontre une erreur. Le cas 4
montre une boucle de code sous hypothèse artificielle, pas une FIFO, une
transmission SPI réussie ni une réception d'écran. Les traces `in_asm` montrent
des blocs traduits, pas un comptage des 128 écritures ; le retour et la dernière
valeur sont les observations du banc.

## Quatre niveaux distincts

1. **Fin d'appel logiciel :** observable en QEMU avec le double RAM.
2. **Fin de l'attente SPI :** observable quand le bit lu vaut 1 ; son sens
   matériel précis reste inconnu.
3. **Fin de transmission du contrôleur :** NON DÉMONTRÉE, notamment après la
   dernière écriture et face aux interruptions et buffers éventuels.
4. **Réception effective par le LCD :** NON DÉMONTRÉE ; aucun ACK LCD connu.

La documentation du SoC et du contrôleur LCD, la configuration des registres,
un contrat d'ordonnancement couvrant tous les auteurs, et une observation du
bus seraient nécessaires avant de relier les niveaux 2 à 4. Aucune de ces
preuves ni un essai matériel n'est autorisé par ce rapport.

## Retour après EXIT

Les essais R9/R23.2 montrent que le shadow peut être copié avant une faute et
qu'un second comparateur peut alors retourner « inchangé ». Restaurer huit
pages exige donc une source Korg complète et stable, l'arrêt des auteurs et
transferts concurrents, un mécanisme légitime pour forcer chaque page même si
le shadow est égal, puis une preuve de fin adaptée au matériel. Le forçage
logiciel observé dans le comparateur ne démontre ni autorité d'appel, ni
livraison complète, ni récupération après faute. Retour EXIT et intégration
matérielle restent **NO GO**.

Reproduction : `PATH=/workspace/mercury-tools/bin:$PATH bash
tests/run_recovery_r23_3.sh custom.VSB backup.VSB`. Aucun hook, firmware
installable, flash ou essai sur instrument.
