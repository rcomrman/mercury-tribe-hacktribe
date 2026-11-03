# R13 — carte et matrice de couverture graphique, intermédiaire

Base R12 9c4ba62541648ff057800c3b98619cdaa30092d8. Aucun protocole R13 installé dans le firmware. Les mentions « protégé » concernent exclusivement des appels médiatisés dans la fixture. Le graphe indirect, les accès calculés, IRQ/FIQ et DMA ne sont pas exhaustivement établis.

~~~mermaid
flowchart TD
 T4[Tâche4 C002B144] --> W[C002D030 wrapper]
 W --> U[C0083848 / C00834FC]
 W --> A[C0083428 / C00833F0]
 U --> G[C00836E4 / C006F178]
 A --> V[C0083374 autre cycle]
 G --> F[C031B310 source fixe]
 V --> F
 S[C006EAE0 pages23/24] --> G
 T2[Tâche2 compteur] --> C[C002A71C / opcode3]
 B[Tâche1 démarrage] --> P[C004D860]
 P --> Q[C006040C / C006038C progression]
 Q --> F
 Q --> D[C0015DD0]
 C --> D
 E[C00298BC diagnostic] --> F
 E --> D
 D --> L[C0015FA0 worker]
 L --> R[C0015AB4 comparaison et copie]
 F --> R
 R --> H[C031B710 shadow]
 H --> X[GPIO / SPI]
 B --> I[C0015EB8 init]
 I --> L
~~~

| Domaine | Contexte établi ou limite | Accès | Protection de fixture / défaut |
|---|---|---|---|
| UI principale | Tâche4, vtable C00E4C50 | C00836E4→C006F178 et deux emplacements | Candidate par wrapper ; preuves R7/R11 conservées |
| UI alternative | Tâche4, mode UI2 issu service7, vtable C00E4BB8 | C0083374 | Protégée cas5 si encadrée ; contournement cas6 sinon |
| Pages secondaires | Tick principal et autres appelants à recenser | C006EAE0→C006E9A0 pages23/24, puis parcours | Envelopper la transaction avant mise à jour, pas seulement Mercury |
| Worker périodique | Tâche2 | Timer→C002A71C→op3→worker | Médiation callback testée cas17, limitée à cette voie |
| Progression | Tâche1 prouvée ; deux services amont non complètement attribués | Rectangle puis op2/op3 synchrones | Non protégée par timer/UI seuls ; cas3/4/16 |
| Démarrage LCD | Tâche1 | Efface source/shadow et force directement le worker | Hors wrapper UI et hors seule interception op3 |
| Diagnostic | Contexte d'erreur possiblement imbriqué | Effacement/dessin, LCD/GPIO, boucle | Non protégé ; pas de suppression sûre démontrée |
| Comparateur direct | Worker connu ; autres aliases inconnus | Source fixe vers shadow | Bypass cas2/9/14 |
| Contrôles LCD | Tous appelants non attribués | Opcode7 accède au matériel sans scan | Bypass cas10 ; pas procédure d'annulation prouvée |
| Pixel writer | Widgets et services, contexte partiel | C0015824 | Non médiatisé globalement |
| Range writer | Rectangle et nombreux widgets | C003F55C→C0015988 | Non médiatisé globalement |
| Pixel reader | C0071EC8, contexte à préciser | C0015900 | Inconnu hors chemins étudiés |
| Adresses calculées | Alias/IRQ/FIQ/DMA à établir | Accès indirects potentiels | Inconnu, absence non prouvée |
| Vidange UI | Tâche4 et producteurs | Boucle jusqu'à file vide | Longue transaction sans borne locale ; cas18 |

## Arêtes directes précisées

- C004D81C → C006038C, dans C004D5CC.
- C004D928 → C006038C, dans C004D860.
- C0060420 → C006038C, fin de C006040C.
- C002AE90 → C004D860, dans C002AB7C : provenance démarrage établie.
- C0031250 → C004D860, dans C0031234 : contexte complet ouvert.
- C0038E40 → C004D860, dans C0038D80 : contexte complet ouvert.
- Le getter C004D598 associe l'objet progression à C0366D5C.

## Frontières candidates

C002D030 est une candidate commune à plusieurs gestionnaires UI, pas à toutes les opérations graphiques. Le champ callback+C d'un compteur est un point de coordination extérieur pour ce compteur seulement. Le dispatcher LCD concentre beaucoup de commandes, mais l'initialisation appelle aussi directement le worker et des commandes ne sont pas de simples demandes graphiques.

Le scan aligné exécuté avant interruption donnait31 plages identiques et118 arêtes candidates pour les cibles choisies. Des données peuvent se décoder comme branches ARM ; ce résultat ne prouve ni un graphe indirect exhaustif ni un point dominant global.

Les traces et JSON bruts correspondants sont inaccessibles au moment de cette sauvegarde. Le script d'audit retranscrit doit être réexécuté avant validation finale.
