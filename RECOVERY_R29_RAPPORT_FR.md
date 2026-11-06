# R29 — EXIT et faute dans un banc ARM sérialisé

## Verdict : succès partiel

Un contrôleur expérimental ARM accepte une demande EXIT à plusieurs points du
worker original, laisse la publication engagée terminer, puis restaure huit
pages Korg dans la fixture. **Quatorze exécutions** couvrent sept points sur
les deux VSB ; les commandes et les octets capturés ont été vérifiés.

Une faute simulée après trois pages passe à `FAULT` ; le débogueur arrête alors
le processus avant la prochaine écriture. **Aucune récupération après faute
n'est démontrée.** Ce résultat ne prouve ni exclusion native, ni interruption
matérielle sûre, ni réception par l'écran.

## Contrôleur et méthode

Le contrôleur nouveau suit `KORG_ACTIVE → ENTERING → MERCURY_ACTIVE →
EXIT_REQUESTED → RESTORING → KORG_ACTIVE`, avec `FAULT`. La demande EXIT ne
coupe pas le worker : le contrôleur attend son retour puis force huit pages
d'une source Korg conservée. Il refuse implicitement une nouvelle publication
Mercury dans ce scénario séquentiel ; aucun arbitre Korg installé n'est prouvé.

Comme R28, GPIO et SPI sont des tableaux RAM et le temps est fourni par une
valeur de registre synthétique lors des lectures de timer. Les écritures SPI
sont capturées aux instructions originales par points d'arrêt QEMU. Une
fonction de fixture, sur pile dédiée, enregistre la demande EXIT pendant que
le worker est suspendu ; les registres du contexte interrompu sont restaurés
exactement avant reprise. Cette injection de débogage ordonne les opérations ;
elle ne reproduit pas une IRQ ou une préemption réelle. Aucun octet VSB n'est
modifié.

## Matrice des scénarios

| Cas par VSB | Frontière d'EXIT | Résultat de fixture |
|---:|---|---|
| 0 | avant worker | PASS : Mercury non publié, huit pages Korg capturées |
| 1 | avant copie de la première page dans shadow | PASS : demande enregistrée, worker achevé puis restauration |
| 2 | après copie de la première page | PASS : shadow intermédiaire vérifié, puis restauration |
| 3 | avant entrée sender | PASS : drain puis restauration |
| 4 | après première page | PASS : drain puis restauration |
| 5 | pendant les écritures de la première page | PASS : demande ne coupe pas la publication |
| 6 | après dernière page, avant retour worker | PASS : restauration après retour |
| 7 | faute avant la première donnée de la quatrième page | BLOCKED : `FAULT`, processus arrêté par le banc, aucune reprise |

Le vérificateur indépendant relit tous les snapshots et les commandes/données.
Il vérifie huit pages Mercury suivies de huit pages Korg pour les cas 1–6 ; le
cas 0 ne contient que les huit pages Korg. Pour le cas 7, trois pages complètes
et les quatre commandes de la quatrième sont conservées. Il rejette une
corruption et une restauration tronquée. Les deux VSB ont chacun passé les
contrôles ; le résultat ne certifie pas une fin de transfert physique.

## Limites de robustesse et décision

La stratégie d'attente est viable **dans le modèle sérialisé avec un worker qui
revient**. Une attente SPI ou timer bloquée peut empêcher EXIT indéfiniment :
aucune annulation native sûre n'est démontrée. L'interruption immédiate du
worker n'est pas qualifiée. Le shadow peut déjà avoir avancé avant une faute.

EXIT répété, demandes Korg multiples et concurrentes, faute pendant attente
SPI ou temporisation, interruption en milieu de page, faute pendant
restauration, reprise d'une faute réversible et faute persistante sont
**NON EXÉCUTÉS / BLOCKED**, et non des PASS. L'arrêt externe du cas 7 ne doit
pas être interprété comme une primitive de récupération. Une prochaine étape
doit tester ces cas en contrôlant explicitement les participants et conserver
les états partiels sans déclarer de restauration sur simple retour logique.

Reproduction : `PATH=/workspace/mercury-tools/bin:$PATH bash
tests/run_recovery_r29.sh custom.VSB backup.VSB` ; le stub QEMU exige des
sockets TCP locaux. Les GPIO/SPI et l'horloge sont hypothétiques. Aucun flash,
firmware installable, hook installé ou essai sur l'Electribe.
