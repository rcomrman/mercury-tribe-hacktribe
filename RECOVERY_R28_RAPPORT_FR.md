# R28 — worker natif et restauration Korg en laboratoire

## Résultat

La chaîne `V30 ARM → source de fixture → C0015FA0 → C0015AB4 → C001613C →
C001851C` fonctionne sous QEMU avec des périphériques **simulés**. Pour chacun
des huit presets et des deux VSB, le même processus ARM calcule deux frames
Mercury puis force une image Korg synthétique distincte : les commandes et les
1 024 octets de chacune des trois publications sont capturés et vérifiés.

La restitution démontrée est une séquence **séquentielle de fixture**. Elle ne
constitue pas un automate EXIT complet : interruption en milieu de page,
réentrée, faute après trois pages et reprise n'ont pas été exécutées. La
demande Korg est un appel séquentiel à l'opcode 2, sans concurrence native.
La chaîne nominale est démontrée dans le banc ; le critère complet incluant
les tests d'interruption reste partiel. Aucun GO matériel.

## Fixture et hypothèses

Les images VSB sont chargées en RX et vérifiées par SHA. Le framebuffer est une
zone anonyme Linux à l'adresse attendue, alimentée par une copie de 1 024 octets
uniquement dans la fixture. Les GPIO et SPI sont des tableaux de RAM : le bit
SPI `0x200` est maintenu à 1 et la configuration +0x40 à `0x80000000`. Ces
valeurs sont des hypothèses du banc, pas une émulation fidèle du matériel.

La page du compteur est aussi une RAM de fixture. À chaque lecture, un point
d'arrêt QEMU à `C00163B8` remplace la valeur de registre r3 par un compteur
synthétique croissant. Les instructions ARM de délai continuent à s'exécuter ;
cette injection modifie un registre de débogage, **pas le code VSB**. Elle
remplace l'observation du timer réel et ne prouve aucune durée physique.

Des points d'arrêt sur `C00184A4` et `C001862C` enregistrent avant chaque `STR`
le PC, l'adresse et la valeur, puis l'instruction originale est exécutée pas à
pas. Les 4 commandes et 128 octets de chaque page sont capturés. Aucune
écriture de mémoire ou de code VSB n'est effectuée par le débogueur.

## Résultats et contrôles

16 processus (huit presets × deux VSB) produisent chacun trois publications :
deux frames V30 puis huit pages Korg. Chaque capture contient 3 168 écritures
(3 × 8 × 132), soit 50 688 écritures au total. La source, le shadow, les
commandes `[0xB0+page, 0x40, 0x10, 0]` et les octets sont comparés aux
références. La restauration est vérifiée dans le flux capturé, pas seulement
dans le framebuffer. Un vérificateur séparé rejette un octet corrompu, deux
pages échangées et un flux incomplet.

## Architectures et coûts

Le contrôle expérimental du worker est simple pour la séquence nominale mais ne
contrôle pas ses autres appelants. Un arbitre commun pourrait ordonner les
publications si tous les auteurs y participaient ; ce composant n'existe pas
dans le firmware étudié et n'est pas implémenté dans cette fixture. La copie
directe de 1 024 octets du banc évite les 8 192 appels pixel R25 ; aucune mesure
de cycles comparable n'a été exécutée et aucune écriture dans le framebuffer
réel n'est autorisée. 10 FPS et coexistence audio ne sont pas démontrés.

Les essais négatifs de flux vérifient le vérificateur, pas la robustesse du
worker face à une interruption ou à une panne SPI. Avant toute décision
matérielle il manque notamment l'autorité sur tous les auteurs, le drain,
IRQ/FIQ/DMA, les sémantiques GPIO/SPI/timer et la fin de transfert physique.

Reproduction : `PATH=/workspace/mercury-tools/bin:$PATH bash
tests/run_recovery_r28.sh custom.VSB backup.VSB` ; le débogueur requiert une
connexion TCP locale. Aucun flash, firmware installable ou essai matériel.
