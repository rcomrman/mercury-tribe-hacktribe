# R19 — coûts et capacité du protocole

Tailles réellement émises dans les records ARM de la source finale :

| Structure | Octets |
|---|---:|
| Relation R19, dont token de constructeur48 et identité/états |100|
| Huit relations + neuf mots de contrôle |836|
| Pool monotone R18 inchangé, quatre générations |1616|
| Clés et inverses préalloués, huit de chaque |256|
| Sujet904 + objet associé1064, avec quatre gardes32 bits |1984|
| Somme de ces structures |**4692**|

Le surcoût du registre R19 seul est836 octets. Les coûts totaux incluent des objets de fixture et le pool historique réutilisé. Ils ne représentent pas une réserve disponible sur l'Electribe. S'ajoutent notamment états UI de laboratoire, vtable, fermeture temporaire, tableaux du test de saturation, piles, snapshots et journaux. La pile GDB fait8192 octets, exclusivement instrumentation.

Une obligation constructeur occupe deux leases CONTINUATION dans le registre R18 du payload et du bundle d'ancres, plus48 octets déjà réservés dans sa ligne de relation. Les clés, sujets et stockages inverses ne sont pas alloués dynamiquement : ils vivent pendant tout le banc. Cette précondition forte remplace leur gestion de durée de vie réelle ; il serait faux de prétendre que les deux tokens épinglent cinq allocations natives arbitraires.

Une seule construction est admise par le registre de sujet à la fois ; les autres sont refusées avant effet. Huit identités de relation ne sont jamais recyclées. Le pool conserve au plus quatre générations et deux propriétaires par génération. Une entrée réentrante conserve sa propre paire d'emprunts ; la capacité R16 peut imposer un refus supplémentaire, surtout si un constructeur de l'autre propriétaire détient déjà une paire.

Ni un délai, ni un compteur nul, ni un inverse vide ne réemploient une adresse. Un constructeur ou callback qui ne retourne pas garde ses obligations et bloque le drainage ; les nouvelles admissions deviennent conservativement refusées. Le protocole n'assure pas une progression illimitée à mémoire fixe.

Le constructeur UI natif réserve904 et1064 octets pour les deux objets partagés audités, mais alloue aussi d'autres enfants et peut appeler des services. Les pages, contextes, buffers et pointeurs profonds réels n'ont pas une borne mémoire totale prouvée. Les réservations de pile natives R11 ne prouvent pas une marge libre ; aucune latence audio, cycles CPU ou débit LCD n'est mesuré ici.
