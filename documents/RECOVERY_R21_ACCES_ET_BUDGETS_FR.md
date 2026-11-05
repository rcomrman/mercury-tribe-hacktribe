# R21 — accès concurrents et budgets de laboratoire

| Ressource | Auteur/lecteur du prototype | Obligation |
|---|---|---|
| état V30/UI | producteur Mercury unique | sérialiser calcul, page et activation |
| triple buffer R12 | un écrivain, un lecteur | métadonnées sérialisées extérieurement |
| structure de page de fixture | callback statique | aucune destruction ; réentrée refusée |
| `C031B310` | auteurs natifs non bornés | coordination globale non démontrée |
| `C031B710` et worker LCD | comparateur/worker natif | copie complète ne vaut pas ACK matériel |
| tâches UI, services, IRQ/FIQ/DMA | hors prototype | absence de conflit non démontrée |

Mesures x86-64 du banc, compilateur `-O2` : structure moteur 7 664 octets,
bridge V30 4 360, UI 136, pool R12 3 112, garde de publication 24. Les trois
images R12 occupent exactement 3 072 octets ; leurs métadonnées occupent 40
octets. Le maximum déclaré par `-fstack-usage` est 1 200 octets. Sept processus
exécutent chacun le scénario complet, dont 512 frames prolongées ; leurs temps
sont conservés dans `results.json`. Ces durées incluent l'ordonnanceur hôte et
ne donnent ni marge CPU/audio ni budget RAM de l'Electribe.

Les tests couvrent l'initialisation unique, 32 publications successives,
changements de page sans réallocation, arrêt entre calcul et commit,
réactivation, lecteur retenu, double calcul/réentrée refusée, copie interdite,
copie partielle, copie complète, faute terminale et 512 frames. Le test ARM
exécute `C006EA10` sur les deux VSB et observe ses trois appels. La faute LCD
`0x01e260bc` est injectée dans la machine d'état ; les fautes natives R9/R20
restent les preuves d'accès matériel et ne sont pas remplacées par cette
injection logique.
