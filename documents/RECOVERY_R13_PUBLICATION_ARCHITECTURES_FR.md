# R13 — architectures de publication candidates, intermédiaire

RESEARCH_ONLY. Le triple buffer privé tests/recovery_r12/pool.h est conservé sans modification. Aucune des architectures ci-dessous n'est installée ou déclarée sûre sur Electribe.

## 1. Comparaison

| Option | Gain sous contrat | Obstacle prouvé ou ouvert |
|---|---|---|
| Garde du callback périodique uniquement | Diffère le worker de tâche2 pendant DRAW | Progression, initialisation, contrôle7 et erreur la contournent |
| Garde C006F178 uniquement | Encadre le cycle principal | C0083374 alternatif et opérations synchrones hors cycle restent ouverts |
| Garde commune autour C002D030 | Couvre plusieurs modes UI et leurs événements | Vidange jusqu'à vide, durée inconnue ; autres domaines non couverts |
| Sémaphore coopératif global | Sérialiserait les participants | Les fonctions natives ne le prennent pas ; aucun ID libre établi |
| Verrou récursif | Évite un auto-blocage mécanique | Autorise un scan imbriqué d'une image extérieure incomplète |
| Verrou non récursif | Refuse le scan imbriqué | Auto-attente si le service synchrone doit finir avant le retour DRAW |
| Copie complète protégée seule | Publication privée/source cohérente à sa fin | Le scan de huit pages peut mélanger deux publications |
| Plafond de priorité / masquage IRQ | Limite certaines préemptions dans un contexte qualifié | Attentes, FIQ/DMA, réentrée, autres tâches et restitution restent ouverts |
| Coordination de domaines exclusifs | Peut encadrer une opération Korg complète, dessin puis lecture | Admission globale, erreurs, attentes matérielles et bornes toujours non prouvées |

Le double buffer privé reste correct avec backpressure ; le triple continue avec un ancien lecteur retenu. Leur différence ne supprime aucun accès non médiatisé à la source fixe.

## 2. Architecture à approfondir : domaines complets

~~~mermaid
stateDiagram-v2
 [*] --> IDLE
 IDLE --> DRAW: image privée retenue
 DRAW --> IDLE: composition complète / fin emprunt
 IDLE --> READ: demande mémorisée
 READ --> IDLE: fin réelle des lectures
 IDLE --> KORG_CRITICAL: source complète / domaine exclusif
 KORG_CRITICAL --> IDLE: retour natif réel
 DRAW --> FAULT: échec sans rollback sûr
 READ --> FAULT: transport bloqué ou erreur
 KORG_CRITICAL --> FAULT: erreur / absence de retour
~~~

Pendant DRAW, les demandes périodiques sont mémorisées, pas traitées. Pendant READ, aucune nouvelle composition ne commence. Un état partiellement composé ne doit pas être rendu lisible en passant arbitrairement à IDLE.

KORG_CRITICAL est admis seulement depuis une source complète sans lecture/composition active. Il exécute une opération native complète dont le code dessine avant son appel LCD synchrone. Les nouveaux dessins et scans périodiques attendent. Il ne faut pas mettre une seconde prise non récursive autour de chaque appel interne et créer une auto-attente, ni accepter toute réentrée au motif que l'appelant est le même.

Le cas19 n'observe que le cas isolé de progression : barre finie, source/shadow cohérentes, puis faute GPIO. Il ne prouve pas la terminaison matérielle de cette phase. Le domaine fatal peut encore survenir au milieu de n'importe quelle phase ; il n'a pas de solution sûre ici.

## 3. Conditions nécessaires

1. Connaître tous les auteurs et lecteurs, leurs appels synchrones et leurs contextes.
2. Médiatiser les métadonnées privées par de vraies primitives adaptées ARM926.
3. Couvrir l'ensemble de la composition Korg et l'intégralité du lecteur, pas une copie ou une page seulement.
4. Admettre les opérations synchrones à une frontière réellement quiescente ; ne pas faire passer un refus pour un succès.
5. Conserver les demandes différées et distinguer source_epoch, prepared_epoch et réception physique inconnue.
6. Borner le temps de chaque domaine, la vidange UI et les attentes ; ne pas bloquer tous les autres services.
7. Ne libérer ni slot, objet, pile ni autorité de lecture encore utilisés après une panne.

Les objets RAM, tables virtuelles et callbacks sont des candidats extérieurs qui peuvent être fournis dans le banc sans patcher les instructions originales. Leur remplacement réel, installation, durée de vie et couverture ne sont pas établis ni autorisés comme intégration matérielle par cette mission.

## 4. Mémoire et ARM926

Le coordinateur de fixture mesure32 octets dans les exécutions observées, dont un handle privé. Ajouté au pool triple R12 de3112 octets, cela représente3144 octets de structures distinctes ; aucune réserve instrument n'en découle. Les tableaux, pages et oracles du banc sont supplémentaires. Le bridge artistique contient déjà d'autres images ; leur réemploi n'est pas automatiquement compatible avec les emprunts.

Le coordinateur est du C séquentiel, sans atomiques ni masque d'IRQ. Les transitions multi-accès ne sont pas sûres sous préemption du seul fait de leur refus de réentrée séquentiel. ARM926 n'offre pas les primitives ARMv7 à supposer par habitude ; cache/MMU/write buffer et DMA restent à établir.

## 5. Récupération

Une lecture bloquée ne peut pas être débloquée par un timeout coopératif situé après son appel. Une fermeture ne peut pas réutiliser l'image ou supprimer l'objet tant qu'un emprunt réel existe. Source égale shadow n'est pas un accusé LCD ; l'opcode7 dépend lui aussi du matériel.

La piste exige une autorité indépendante de détection et de confinement/annulation avec état mémoire connu. Rien dans les essais ne démontre cette autorité.

Décision provisoire : GO recherche des domaines et de leur admission ; NO GO garantie de cohérence globale, récupération indépendante ou matériel. La mission R13 elle-même reste à finaliser après récupération/rejeu des preuves.
