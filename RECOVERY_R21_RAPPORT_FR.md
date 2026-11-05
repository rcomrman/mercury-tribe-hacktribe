# MERCURY DUST — RAPPORT R21
## Voie Mercury persistante à empreinte fixe, sans nouvel abonnement natif

Date du banc : 5 novembre 2026. Branche : `recovery/mercury-dust`.
Base préservée : `33ebf0884ed082dbce0065d53709cdd322042f4b`.

## Résumé accessible

R21 démontre qu'un moteur Mercury peut rester vivant dans une zone de taille
fixe, produire V30 dans trois buffers privés et survivre aux changements de
page sans construire ni détruire d'objet Korg. Il conserve les huit presets,
les douze paramètres et quatre mini-LFO au total. La route candidate ne crée
aucun observateur natif.

Cette simplification est réelle mais locale. Elle ne donne pas la propriété du
framebuffer Korg, ne suspend pas ses autres auteurs et ne prouve pas qu'un
composant Mercury peut être inséré avec autorité dans une page de l'instrument.
Le résultat est donc **GO pour la poursuite logicielle en laboratoire** et
**NO GO pour intégration matérielle, firmware, flash ou essai sur instrument**.

## Architecture obtenue

Une structure statique contient le bridge V30, l'interface Mercury et le pool
R12. Ses états sont `INIT`, `ACTIVE`, `INACTIVE` et `FAULT`. L'initialisation
est refusée après le premier appel. Le calcul et le commit sont séparés : un
arrêt logique entre les deux abandonne la frame sans changer la publication.
`FAULT` est terminal et conserve les adresses du stockage.

Le chemin B exécute la fonction native existante `C006EA10`. Sur chacune des
deux VSB, elle appelle exactement une fois les trois méthodes virtuelles +8 du
graphe statique du banc. Elle ne passe par aucune des entrées d'inscription ou
de retrait R20 et n'écrit pas l'image native. R21 ne modifie aucun octet VSB.

La publication C est fermée par défaut. Un jeton explicitement limité à la
fixture permet d'étudier une copie complète. Une copie à mi-course donne une
image mixte, et un auteur non participant peut invalider une copie complète.
Ce sont des contre-exemples conservés, pas un protocole matériel.

## Comparaison

| Stratégie | Décision | Motif |
|---|---|---|
| A — V30 privé vers interface contrôlée | GO laboratoire | empreinte fixe, aucune dépendance Korg de durée de vie |
| B — chemin natif existant `C006EA10` | GO laboratoire limité | zéro abonnement, mais insertion dans la page réelle non autorisée |
| C — copie sous conditions vers `C031B310` | NO GO matériel | autorité globale et participation de tous les accès non prouvées |

A est aujourd'hui le chemin défendable le moins intrusif. B fournit un point de
calcul intéressant mais pas encore un point de publication. C reste interdite
hors contre-expérience contrôlée.

## Accès et concurrence

Le triple buffer garantit localement qu'un lecteur retenu et un écrivain ne
partagent pas le même slot. Il requiert toujours une sérialisation extérieure
de ses métadonnées. Cette propriété ne s'étend pas à `C031B310`, au shadow LCD,
aux tâches UI, services, diagnostics, IRQ/FIQ, DMA ou alias calculés. Les 14
domaines R13 restent donc des obligations. `INACTIVE` signifie que Mercury
refuse de rendre ; il ne certifie aucune cessation native.

La faute LCD logique `0x01e260bc` place le prototype en `FAULT` et bloque les
opérations suivantes. Les fautes natives historiques restent les seules preuves
du comportement du worker face au MMIO absent. R21 ne présente pas son signal
logique comme une réponse matérielle fictive.

## Budgets mesurés

| Élément | Taille du banc x86-64 |
|---|---:|
| moteur persistant complet | 7 664 octets |
| bridge V30 | 4 360 octets |
| UI, 12 paramètres et quatre LFO | 136 octets |
| pool R12 | 3 112 octets |
| trois images privées | 3 072 octets |
| métadonnées R12 | 40 octets |
| garde de publication | 24 octets |
| pile maximale déclarée par le compilateur | 1 200 octets |

Sept exécutions prolongées de 512 frames mesurent 9,233 à 11,064 ms, médiane
10,090 ms, soit 19,7 µs par frame sur cet hôte. Ce sont des mesures de processus
x86-64 compilé en `-O2`. Elles ne prouvent aucune RAM disponible, marge CPU,
contrainte audio ou cadence sur l'Electribe.

## Résultats reproductibles

Le scénario couvre les huit presets distincts, l'initialisation unique, 32 publications initiales, quatre
pages sans réallocation, arrêt entre calcul et commit, réactivation, 16 commits
avec lecteur retenu, réentrée refusée, publication interdite, copies partielle
et complète, 512 frames supplémentaires et état de faute terminal. Il termine
avec 563 calculs, 562 commits, six refus attendus et une génération R12 de 563.

Le vérificateur indépendant relit les octets VSB, les contrats ARM, les traces,
les résultats, les limites de structure et les 2 591 fichiers présents à la
tête R20. Il confirme leur conservation exacte. Les VSB restent aux SHA-256
`81b624…ffd03` et `06becf…45b052`.

Reproduction :

```sh
PATH=/workspace/mercury-tools/bin:$PATH \
bash tests/run_recovery_r21.sh custom.VSB backup.VSB
```

## Décision aux sept questions

1. **Dépendances supprimées :** 10 entrées natives de la route R20, deux
   inscriptions, leurs inverses et trois racines de sujets/modèle ne sont plus
   nécessaires à la nouvelle route. Elles ne disparaissent pas du firmware.
2. **Dépendances obligatoires :** V30 et R12 pour A ; `C006EA10`, un gestionnaire
   et trois composants valides pour B ; tous les auteurs/lecteurs et le worker
   LCD pour toute tentative C.
3. **Coordination globale :** non pour produire une frame privée ; oui avant
   toute insertion dans une page réelle ou publication vers le framebuffer.
4. **Limites démontrées :** 7 664 octets statiques, 1 200 octets de pile déclarée
   et les temps hôte ci-dessus. Aucune limite instrument n'est démontrée.
5. **Pages :** leur changement devient une mutation d'état sans allocation ni
   destruction. L'autorité sur la page native reste entière à prouver.
6. **Chemin le moins intrusif :** A, avec B comme appel de calcul candidat sans
   publication native.
7. **Preuves manquantes :** propriétaire et durée de vie des slots de page,
   droit d'insertion, inventaire dynamique des auteurs, fenêtre commune de
   publication, budget ARM/RTOS/audio, ACK LCD et protocole de faute réel.

## Proposition R22

R22 doit se limiter au blocage immédiat : **qualifier le contrat de composition
des trois slots lus par `C006EA10`**. Il faut cartographier, sur les deux VSB,
leurs constructeurs, auteurs, transitions de page et durées de vie, puis tenter
de démontrer en émulation si un slot existant et autorisé peut référencer un
composant persistant sans abonnement, patch ni écriture firmware. R22 doit
conserver un témoin de réentrée et un témoin de changement de page, mesurer le
budget ARM du callback, et conclure NO GO si l'autorité d'écriture ou la
cessation des anciens utilisateurs n'est pas dominée. La publication vers
`C031B310` restera hors périmètre tant que ce contrat n'est pas établi.

## Conclusion

R21 simplifie mesurablement la durée de vie de Mercury : le rendu privé n'a
plus besoin des observateurs et destructeurs R17–R20. Elle ne déplace pas cette
victoire vers une prétendue propriété du LCD. Le projet peut avancer vers R22
en laboratoire ; l'intégration matérielle demeure non autorisée.
