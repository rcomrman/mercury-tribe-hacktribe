# R19 — propriété du sujet périodique UI, audit initial

Base6808871. Les154 SHA R18 et son vérificateur passent sans rejouer R1–R18. Les sources et archives historiques restent intactes.

## Faits natifs locaux

| Relation | Statut | Preuve |
|---|---|---|
| Gestionnaire UI principal contient l'état à +0x10 | PROUVÉ | C0083900–904 appelle C006E6EC avec ui+16 |
| état+0x24 reçoit *C0691244 | PROUVÉ | C006E73C et C006E744 |
| Si cette racine vaut0 : allocation904, constructeur C00826A8, publication globale | PROUVÉ localement | C006E71C–738 ; code sans gate commun dans ce corps |
| état+0x2C reçoit *C0348844 | PROUVÉ | C006E758–784 |
| Si cette seconde racine vaut0 : allocation1064, constructeur C008241C, publication globale | PROUVÉ localement | C006E768–778, littéral0x428 à C006E8A8 |
| Plusieurs constructeurs peuvent employer ces racines | PROUVÉ comme candidats statiques | Huit branches vers chacun des deux constructeurs ; tous les usages de littéraux sont recensés |
| Sujet privé appartenant exclusivement à une page | REJETÉ comme inférence | Les champs recopient des racines globales ; proximité des adresses insuffisante |
| Singleton partagé pendant tout le processus | PARTIEL | Création paresseuse et racines conservées, mais pas de preuve exhaustive de non-remplacement/libération |
| Propriétaire unique / autorité finale de destruction | INCONNU | Alias et appels calculés non exclus |

L'objet à +0x24 possède32 slots24 octets, une vtable secondaire à +0x304 et32 compteurs à +0x308, taille904. C0082728 consomme ces compteurs et utilise le mot slot+0x10 comme période. Le contexte, la méthode et l'ajustement du slot appartiennent à leurs propres allocations ; la clé reste distincte.

L'objet à +0x2C possède lui aussi le préfixe32 slots. C008241C initialise le reste jusqu'à1064 octets ; C0082550 consomme35 indices0..34 à partir de +0x308 par paires état/compteur. C00824A0 écrit ces paires à partir de paramètres. On conserve des noms structurels : aucune classe métier ou propriété profonde n'est inventée.

C006E6B0 appelle le destructeur inverse C0041B74 sur l'état lui-même, après changement de vtable. Il ne libère pas directement état+0x24 ou +0x2C dans ce corps. Le destructeur UI C0083898 l'appelle avec ui+16 ; C00838C4 libère ensuite le gestionnaire UI. Cela ne prouve pas l'absence d'autres destructeurs ou alias des objets globaux.

Les tables C00E4B58 et C00E4AE0 fournissent des corps de destructeurs différents du destructeur inverse d'une clé. Les thunks secondaires ajustent le this de−0x304. Il faut distinguer sujet, sous-objet d'interface et objet-clé, sans utiliser la proximité ou une même vtable comme preuve de propriétaire commun.

## Références et limites

`ownership.json` conserve les contrats d'instructions, les plages signées, les candidats d'appel et tous les LDR littéraux trouvés vers C0691244/C0348844. `native-ownership.txt.gz` conserve leurs voisinages et les corps pertinents. Ces candidats ARM alignés ne couvrent pas tous les alias indirects, Thumb, IRQ/FIQ ou DMA.

Le pont tâche4/gestionnaire principal établi R18 est conservé. Les racines globales peuvent aussi être consultées par d'autres constructeurs. Aucun rôle de tâche exclusif ni mécanisme de référence comptée n'est inféré.

## Fenêtre d'inscription à couvrir

C0070778 cherche une clé existante ou un slot libre. Il écrit période, clé, méthode/ajustement et contexte, puis actif à C00707C8. Il ne met à jour l'inverse qu'ensuite ; le vrai retour se trouve à C0070814. Le chemin de croissance C00706C8 peut allouer/copier/libérer le vecteur. Un slot actif et un inverse vide peuvent donc coexister avec un constructeur encore actif.

Les obligations du constructeur doivent être acquises avant son entrée et retenues jusqu'à son vrai retour. Une fermeture logique peut interdire de nouveaux travaux ; un retrait physique doit aussi attendre les parcours déjà admis et les inscriptions en cours. La primitive native commune reste NON PROUVÉE. Aucune destruction d'allocation native n'est autorisée par cet audit.
