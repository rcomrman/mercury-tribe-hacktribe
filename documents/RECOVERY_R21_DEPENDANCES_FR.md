# R21 — reprise et dépendances de la voie persistante

Base `33ebf0884ed082dbce0065d53709cdd322042f4b`, tête distante vérifiée identique.
Le rapport R20 a été lu intégralement et son bilan de faisabilité repris ; les
contrats R12–R14 sont conservés. Le vérificateur R20 passe sur les archives et
ses176 SHA, sans rejeu des expériences historiques. Aucun ancien fichier ne doit
changer. Les deux VSB restent en lecture seule.

## Composants réutilisés

Le moteur V30 est compilé depuis les sources existantes `md15_bridge`, profils,
`mercury_live`, événements, glitch et mux. Les12 paramètres et les quatre mini-LFO
au total restent dans `md_ui`/`mini_lfo4`, sans routage vers un paramètre natif.
Le pool R12 et les gardes R13/R14 sont inclus sans modification. Le mux interne
au bridge reste une simulation privée ; il n'est pas utilisé pour inventer une
transmission LCD. Les entrées musicales et changements de page restent préparés
par le laboratoire, pas issus du panneau ou du séquenceur matériel.

## Voie graphique candidate

`C006EA10`, appelé par le cycle natif `C006F178`, charge successivement trois
pointeurs à gestionnaire+0x34/+0x38/+0x3C puis leurs méthodes virtuelles+8. Il peut
être exécuté sans abonnement d'observateur, file d'événements ou allocation.
Le banc fournira un graphe statique explicite, avec un composant Mercury et deux
composants de fixture sans effet. Cela ne qualifie ni les véritables widgets
annexes Korg ni l'exécution complète de `C006F178`, déjà étudiée en R7.

La durée de vie fixe du composant simplifie sa conservation, mais pas la preuve
de l'autorité d'insérer ce composant sur instrument, de modifier une page ou de
copier dans la source fixe. Aucune insertion ou interception native n'est
installée par R21.

| Zone / acteur | Propriétaire dans le banc | Obligation native restante |
|---|---|---|
| Bridge V30 et UI privée | Stockage statique Mercury, initialisation unique | Sérialisation producteur et entrées réelles à qualifier |
| Trois images privées R12 | Un écrivain, un lecteur, génération sans rebouclage | Transactions de métadonnées atomiques par hypothèse extérieure |
| Composant, vtable et gestionnaire de fixture | Permanents et jamais recyclés | Durée de vie du gestionnaire réel, ordre de composition et publication d'adresse |
| Source fixe C031B310 | Aucun propriétaire exclusif natif démontré | Tous auteurs/lecteurs doivent respecter une fenêtre commune |
| Shadow C031B710 | Comparateur natif | Copie avant transfert ; pas un ACK matériel |
| Tâche4 / cycle UI principal et alternatif | Non exécutés entièrement par le nouveau parcours | Autres widgets et transitions restent des participants nécessaires |
| Tâche2 / worker périodique | Pas de nouvel abonnement | Lecteur source concurrent toujours existant |
| Services, progression, démarrage et diagnostic | Aucun remplacement | Autres accès graphiques/LCD non dominés par le seul callback Mercury |
| IRQ/FIQ/DMA et alias calculés | Hors preuve exhaustive | Absence non démontrée |

Les14 domaines de R13 sont conservés dans `reports/recovery_r21/native-map.json`.
Leur maintien comme obligations interdit de confondre réduction des dépendances
du nouveau composant et disparition des acteurs du firmware.

## Mesure de simplification prévue

Le candidat R20 concret avait deux inscriptions pour l'abonné natif, une clé
inline et un inverse, dix entrées natives de sa chaîne observateur/constructeur/
destructeur et trois racines de sujets/modèle. R21 cherche zéro inscription,
zéro inverse et aucun appel à ces dix entrées ou déréférencement de ces trois
racines dans la nouvelle voie. Ce comptage est limité à la voie expérimentale ;
il n'affirme pas que ces fonctions disparaissent du firmware ou de l'UI réelle.

La sortie minimale défendable reste une image privée complète. Les stratégies
vers source fixe seront exercées seulement sous une autorité explicitement
**de fixture**, avec contre-exemples de lecteurs et écrivains non participants.
Le mode par défaut doit refuser cette publication native.
