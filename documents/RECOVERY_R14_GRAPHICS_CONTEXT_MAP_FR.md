# R14 — carte des contextes et couverture

Base cb0d8ca. Carte additive : aucune preuve R13 réécrite. Instructions originales identiques sur les deux VSB dans les 20 plages de l'audit R14. Le scan ARM aligné est un ensemble de candidats, pas une preuve exhaustive sur appels indirects, Thumb, alias, IRQ/FIQ ou DMA.

## Contextes nouvellement attribués

La tâche **5**, entrée C002A598, attend via C000085C(4) puis appelle C002D844. Ce consommateur dépile via C003B81C et appelle C002D684. Le dispatcher choisit l'objet dans C03404C8 suivant le type signé du message, appelle sa vtable+0xC, son slot+8, puis +0x10. Il émet aussi des commandes UI et possède allocations/destructions. Ce n'est ni la tâche4 ni une transaction graphique atomique.

- Service **17** : C002DB78 construit par C0030F3C et range l'objet à table+0x44. Le constructeur installe C00A7608 ; slot+8=C003128C, qui appelle C0031234 à C0031338 après deux autres opérations réussies. C0031234 appelle C004D860 à C0031250 avec r0=0, **r1=0**.
- Service **34** : C002DD10 construit par C00392A4 et range à table+0x88. Le constructeur installe C00A7B58 ; slot+8=C0038D80. Le chemin C0038E00 conserve r7=0 quand il peut atteindre C0038E40 ; ce dernier appelle C004D860 avec r0=r7=0, **r1=r7=0**.
- Ne pas confondre service24, C0038C64/table C00A7AF8/slot C0038A54, avec service34. La proximité des adresses ne suffit pas à identifier l'objet.

Dans C004D860, r1 est conservé en r7. Le test de ce drapeau conditionne C0060384, C006040C à C004D8B4 et C004DCD0, et C006038C à C004D928. Les appels C004D5CC à C004DCF4/C004DD80 reçoivent ce même drapeau dans r2 ; son test conditionne aussi la progression interne. Ainsi **les deux routes précédemment ouvertes atteignent un service contenant du graphisme, mais désactivent ses appels de progression identifiés**. Cela ne prouve pas que tout sous-service, message UI ou appel indirect soit sans effet graphique.

Le démarrage C002AE90 passe au contraire **r1=1**. Le getter C004D598 fournit l'objet partagé C0366D5C ; aucun mutex graphique ni droit de réentrée ne découle de ce getter. C006038C dessine puis appelle LCD2/LCD3 synchrones ; C006040C configure puis y branche. Toute admission doit précéder l'opération entière, et non son seul scan interne.

## Matrice finale R14

« Couvert » ci-dessous signifie uniquement acteur coopératif exercé dans le banc R14. Aucun hook n'est installé.

| Accès/domaine | Contexte établi | Couverture et limite |
|---|---|---|
| UI principale | tâche4, wrapper C002D030, table C00E4C50 | Contrat de domaine proposé ; preuves R7/R11/R13 conservées ; tous widgets pas requalifiés |
| UI alternative | tâche4, C0083428/C00833F0/C0083374 | Couvert par admission de fixture ; contournement conservé |
| Pages secondaires | tick principal C006EAE0 puis C006F178 | Conditionnel à enveloppe avant update/destruction ; autres appels inconnus |
| Service17 | tâche5 configurée, slot8 C003128C | Route attribuée ; progression désactivée dans C004D860 ; médiation globale absente |
| Service34 | tâche5 configurée, slot8 C0038D80 | Même restriction ; erreurs/prérequis de stockage non rejoués intégralement |
| Progression démarrage | tâche1, r1=1 | Non couverte par seule garde UI ; admission CRITICAL candidate |
| Progression feuille | appelants directs recensés, objet partagé | Couvert seulement si l'appel extérieur est admis ; contournement prouvé |
| Worker périodique | tâche2, priorité initiale1 | READ coopératif couvert ; worker réel conserve son autorité à la faute |
| Initialisation LCD | tâche1, worker forcé direct | Non couverte par seul dispatcher LCD ; cycle de démarrage exclusif nécessaire |
| Diagnostic fatal | contexte d'erreur, potentiellement imbriqué | Non couvert, dépend du LCD ; aucune récupération prouvée |
| Comparateur direct | worker et appels directs | Non couvert s'il contourne l'admission ; scan mixte conservé |
| LCD7 / effacement1 | services/contrôles, tous contextes non attribués | Non couverts par READ coopératif ; GPIO distinct/écrasement source |
| Primitives pixels/plages et pixel reader | widgets/services partiels | Inconnu globalement ; aucune consultation automatique du protocole |
| Alias calculés, IRQ/FIQ/DMA | non exhaustivement recensés | Inconnu ; absence non démontrée |

## Services noyau et coordination

La boucle de tâche5 attend une durée logique4, puis vide sa queue sans quota natif établi ; un refus de l'attente ne supprime pas la consommation. La tâche2 de rang1 peut préempter tâche4 rang4 et tâche5 rang6. Inversement, un worker prêt en boucle active de rang1 peut empêcher un observateur de rang inférieur de tourner. Ces rangs sont initiaux et peuvent changer ; aucune latence physique n'est déduite.

C002D684 est un point extérieur candidat pour **les services qu'il distribue**, C002D030 pour l'UI, et le callback de compteur pour le worker périodique. Aucun n'est un dominateur de tous les dessins, diagnostics ou accès LCD. Le sémaphore natif n'est une exclusion que pour ceux qui l'acquièrent. Les attentes noyau, listes de tâches et sorties de tâche ne démontrent pas une annulation des accès mémoire/périphériques.

Preuves reproductibles : `tools/recovery_r14/audit.py`, `reports/recovery_r14/audit.json` et `native_disassembly.txt.gz`. La qualification des routes est statique ; l'exécution complète des services17/34, du stockage et de leur ordonnanceur reste explicitement hors preuve dynamique.
