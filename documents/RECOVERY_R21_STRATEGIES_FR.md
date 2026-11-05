# R21 — comparaison des stratégies de rendu

| Stratégie | Dépendances | Complexité mesurée | Résultat | Risque restant |
|---|---|---:|---|---|
| A — calcul privé et interface contrôlée | V30 + R12 seulement | un producteur, trois buffers | **GO laboratoire** | l'interface réelle reste à identifier |
| B — callback dans `C006EA10` | A + gestionnaire/page existant | trois appels virtuels +8 | **GO laboratoire limité** | autorité d'insertion, ordre UI et durée de vie réels inconnus |
| C — copie conditionnelle vers `C031B310` | A + tous lecteurs/auteurs/LCD | fenêtre globale nécessaire | **NO GO matériel** | copie partielle, auteurs non participants, faute LCD |

A est le chemin le moins intrusif défendable : il livre une image privée
complète sans faire d'affirmation sur le framebuffer. B retire le besoin d'un
nouvel abonnement mais ne retire pas le besoin de raccorder un composant à une
page autorisée. C n'est admise que comme expérience négative de fixture.

Par rapport au candidat R20, la nouvelle voie n'appelle plus 10 entrées de la
chaîne abonnement/constructeur/destructeur et ne déréférence plus trois racines
de sujets/modèle. Ce compte porte sur la route Mercury, pas sur le firmware :
les 14 domaines graphiques historiques restent des obligations de coordination.
