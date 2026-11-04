# R17 — fermeture expérimentale du graphe d'observateurs

## Décision et périmètre

GO pour l'expérience CPU bornée ; NO GO pour destruction native, intégration ou récupération matérielle. Le code nouveau se trouve uniquement dans le banc Linux ARM. Il réutilise sans modification le registre R16, la file R15 et ses dépendances R12–R14. Aucun wrapper n'est installé dans Korg.

La protection étudiée est une **admission avant les chargements natifs**, suivie d'une **mutation différée jusqu'au retour du parcours**. Retenir seulement les objets ne protège pas le tuple de fermeture : le retrait peut encore effacer la méthode entre deux instructions de C007061C.

## Graphe possédé de la fixture

Cinq ressources logiques distinctes sont décrites : sujet S, clé K, allocation de contexte C, ancre de méthode/vtable M, stockage du vecteur inverse I. Un propriétaire et une génération par ressource ; cinq emprunts d'inscription ; cinq emprunts supplémentaires par parcours admis ; cinq par commande encore retenue. Trois registres R16 de deux objets représentent cinq objets et un emplacement inutilisé.

Les tableaux sont statiques et restent alloués jusqu'à la fin du processus. Les tokens décrivent des engagements logiques, pas des références ajoutées à l'allocateur Korg. M représente une méthode et une vtable de fixture permanentes ; aucune fermeture arbitraire ni copie profonde de vtable n'est qualifiée. Pour un contexte ajusté, le propriétaire doit retenir toute l'allocation contenant le sous-objet. Pour une méthode virtuelle, il doit aussi garantir l'immuabilité et la durée de vie de la vtable jusqu'à résolution et retour.

Le sous-graphe admis possède une seule clé connue et un tuple attendu. `begin` parcourt les 32 slots et refuse un slot actif avec clé, contexte, méthode ou ajustement inconnus. Il ne couvre donc pas un sujet général avec 32 propriétaires différents. Étendre ce contrat impose un inventaire de tous les slots et de leurs propriétaires avant la sélection.

## Contrats des transitions

| Transition | Préconditions et effet | Refus / responsabilité restante |
|---|---|---|
| Inscription gardée | Graphe préparé avec ses cinq références ; OPEN ; aucun parcours ; appel natif inchangé | Refus si fermeture ou parcours. Pas un service général d'allocation/inscription |
| Admission du parcours | Gate extérieur tenu, OPEN, tuple connu, capacité et ticket disponibles | Toute acquisition partielle est annulée ; aucun appel natif si échec |
| Sélection / résolution | Cinq emprunts déjà acquis avant C0070688 ; slot et vtable immuables | Un appel natif non participant peut violer cette précondition |
| Invocation | Callback avec contexte/ajustement natifs ; emprunts du parcours maintenus | Compter seulement à l'entrée laisse la fenêtre de résolution ouverte |
| Réentrée | Nouveau parcours et cinq emprunts distincts, ticket distinct ; trois cadres maximum | Refus si fermé, quatrième cadre, saturation ou numéro maximal ; aucun rebouclage |
| Demande de fermeture | OPEN → CLOSING ; retraite des cinq objets ; refus des nouvelles admissions | Retour immédiat de la demande ; aucune attente de son propre callback |
| Retour du parcours | Vrai dernier accès natif effectué ; validation cadre/ticket ; libération de ses cinq emprunts | Le ticket seul n'authentifie pas un appelant ; le vrai retour est une précondition |
| Retrait physique | CLOSING et aucun parcours : C00705DC puis compaction de fixture du vecteur inverse | Ne doit pas se produire entre chargement de this et chargement de méthode |
| Retrait des producteurs connus | Après retrait physique, detach et libération des cinq références d'inscription | Pas un join Korg ; aucun alias caché ni producteur non déclaré n'est retiré |
| Commande en attente | Cinq emprunts restent jusqu'au refus avant exécution et ACK explicite R15 | Pas d'annulation d'un appel déjà commencé ; pas de faux retour natif réussi |
| Inactivité locale | Fermé, retiré, aucun cadre/callback/commande, aucun slot actif ni relation inverse, cinq objets localement inactifs | Prédicat instantané du graphe recensé ; jamais permission globale de free |

La compaction déplace les relations conservées dans un vecteur de fixture préalloué et met sa fin à jour ; elle supprime tous les doublons vers ce sujet. Elle n'appelle pas C0041B74 : celui-ci libérerait le stockage, incompatible avec ce tableau statique. L'autorité d'effectuer cette compaction pendant l'exécution native n'est pas démontrée. Si une relation vers un autre sujet reste dans le vecteur, la fermeture du graphe complet reste refusée.

Une demande peut arriver dans un callback réentrant. Le cadre intérieur retourne et libère ses propres emprunts ; le cadre extérieur continue de retenir les siens. Le retrait attend le retour du dernier parcours. L'ancien parcours natif peut sélectionner d'autres slots avant son retour : la demande de fermeture ne promet pas d'arrêter instantanément chaque callback du parcours déjà admis.

## Gate et solutions comparées

| Architecture | Propriété recherchée | Préconditions / obstacle |
|---|---|---|
| Compteur à l'entrée du callback | Retenir les callbacks actifs | Insuffisant : fenêtre sélection–entrée ; modèle `active_only` et cas 3/6 |
| Retrait natif immédiat + objets retenus | Empêcher nouvelles sélections | Insuffisant : tuple effacé pendant sa résolution ; cas 6 |
| Mutex gardé pendant tout le callback | Exclure retrait et notification | Tous appelants doivent le consulter ; réentrée et fermeture intérieure peuvent s'interbloquer ; worker bloqué conserve le mutex |
| Gate court + emprunts avant parcours + mutations différées | Fermer admissions, laisser finir les parcours admis | Candidat testé ; tous les lecteurs/écrivains du tuple et de l'inverse doivent participer ; gate ARM non qualifié |
| Ancre permanente / quarantaine sans destruction | Éviter la disparition du contexte résolu | Solution de repli à étudier : coût RAM, code/vtable immuables, nombre borné et routage de chaque accès encore nécessaires |
| Copie privée d'une fermeture + référence retenue | Isoler le tuple de son slot | Le lecteur doit être médiatisé avant copie ; ne corrige pas les routes natives inchangées ; alias cas 13 |

Les primitives natives de sémaphore et les helpers CPSR existent dans les plages auditées. Cela ne prouve pas qu'elles dominent ces observateurs. Le helper C0000040 pose le bit I (0x80), sans poser le bit F (0x40). Un masquage IRQ n'est pas une preuve contre FIQ, DMA, un appel indirect, une attente ou une préemption ailleurs. Il ne doit pas entourer un callback arbitraire ni un worker pouvant attendre indéfiniment.

Le gate nécessaire doit sérialiser admission, vérification du tuple, changements de vtable, inscription/retrait, détachement d'inverse et fin de cadre. Il doit être relâché avant tout appel pouvant bloquer. Les emprunts doivent ensuite interdire toutes les mutations concernées jusqu'au retour. Aucune primitive native n'est qualifiée comme fournissant ce contrat global. Les essais GDB injectent une intercalation contrôlée avec pile distincte et restauration exacte des registres : ce n'est pas une preuve d'ordonnancement Korg.

## Coûts mesurés et limites ARM926

| Structure nouvelle de fermeture | Octets ARM |
|---|---:|
| Trois registres R16 | 768 |
| Trois cadres, cinq tokens de 16 octets plus ticket/état chacun | 264 |
| Cinq racines et cinq tokens de commande | 160 |
| Huit mots d'état de la fixture | 32 |
| Total métadonnées ci-dessus | **1224** |

La file R15 réserve séparément 128 octets ; admission R14 + pool R12, 3176 octets. Total réservé de ces structures : **4528 octets**, sans allocation nouvelle de framebuffer. Cela inclut des composants historiques réutilisés, pas seulement le coût marginal de R17. Les objets natifs de fixture ajoutent notamment sujet étendu904 + inverse32 =936 octets ; clé, contextes, copie brute, vtable, autres sujets, piles et journaux sont en sus. La pile GDB réservée fait8192 octets et appartient au banc seulement.

Ces nombres ne prouvent aucune RAM libre sur l'instrument. Les écritures ordinaires C ne constituent pas un protocole atomique ARM926. Visibilité mémoire, interruptions, verrous, caches, DMA, durées maximales et impact audio restent inconnus. Trois cadres réservent une capacité finie ; un parcours bloqué garde ses emprunts et empêche la fermeture au lieu d'autoriser une destruction forcée.

## Cessation périphérique séparée

Dans le cas17, le callback demande la fermeture puis entre directement dans le worker natif. L'accès GPIO échoue à0x01E260BC, soit base native0x01E26000 +0xBC. Le cadre et les dix références inscription+parcours restent présents au snapshot de faute. La copie préalable dans la shadow est visible mais n'atteste aucune transmission.

La faute Linux détecte une frontière non mappée du banc. Elle ne donne aucune autorité de détection, confinement, annulation ou restauration sur l'Electribe. Aucun watchdog nouveau, aucune réponse GPIO/SPI, aucun retour sûr à Korg ni arrêt DMA n'est démontré. **NO GO récupération indépendante maintenu.**
