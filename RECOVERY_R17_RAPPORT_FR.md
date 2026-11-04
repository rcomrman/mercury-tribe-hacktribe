# MERCURY DUST — R17 : fermeture des observateurs Korg

## Résultat et décision

**GO pour un contrat CPU expérimental borné, avec admission avant résolution et retrait différé ; NO GO pour destruction globale, intégration dans Korg ou récupération matérielle.**

R17 démontre une difficulté supplémentaire par rapport à R16 : conserver les allocations ne suffit pas. Un retrait natif peut effacer la méthode alors que le processeur a déjà chargé le contexte `this`. Le banc reproduit une invocation à l'adresse zéro. À l'autre extrémité de cette fenêtre, une méthode déjà résolue est encore appelée après effacement de l'inscription.

Le candidat testé retient les ressources avant le parcours natif et reporte l'effacement du tuple jusqu'au retour du dernier parcours admis. Il fonctionne dans le sous-graphe de fixture recensé. Les appels natifs qui n'utilisent pas cette admission, les copies brutes, d'autres sujets et les générations réutilisées conservent des contre-exemples. Aucun droit général de libérer un contexte Korg n'est établi.

58 expériences ARM ont été exécutées sur les deux VSB : **54 retours normaux et quatre fautes attendues**, deux à l'adresse zéro et deux à0x01E260BC. Les 29 paires de records sont identiques octet par octet. Les listes de lignes natives des blocs traduits QEMU correspondent également. Le vérificateur indépendant confirme les assertions, les frontières d'injection, la conservation des instructions natives et des chemins historiques. Le modèle borné explore1080 états.

## Reprise, conservation et publications

Base imposée : `60eddcdd2cc06dff43b71d5459b147d8c835457f`, branche exclusive `recovery/mercury-dust`.

Les rapports et trois architectures R16 ont été lus intégralement lors de la reprise ; les frontières de dispatch et contrats R15 nécessaires ont été consultés. Les167 entrées SHA-256 du manifeste R16 ont été vérifiées. Les expériences R1–R16 n'ont pas été relancées. Les sources historiques des registres, files, pools et lanceurs restent inchangées ; elles sont incluses depuis le nouveau banc.

Sauvegardes intermédiaires publiées et têtes distantes vérifiées :

- `5597ec9c81060b43b6eb546bb6ec29a6135a83a1` : reprise et vérification des archives R16.
- `9a66e7e2a25eeccc1c4f2e250ae2617d455843f5` : audit natif et carte du cycle de vie.
- `3369838b4ff4f112a6e85dc8d963427417f88838` : premières preuves complètes ARM, modèle et vérification, avant rédaction finale.

Les présentes preuves sont **nouvelles pour R17**, produites dans cette session. Aucune trace régénérée n'est présentée comme une archive historique retrouvée. Le manifeste final décrit les fichiers effectivement publiés, leurs SHA-256 et les versions d'outils ; il ne s'inclut pas lui-même.

Le vérificateur compare tous les chemins présents dans l'arbre du commit de base, pas seulement quelques sources sélectionnées. Aucun chemin R1–R16 n'a été modifié. Cela préserve notamment V30, huit presets, douze paramètres, quatre mini-LFO au total, IFX, triple buffer et anciennes preuves. Aucun VSB n'est ajouté au dépôt, aucun firmware installable n'est généré, aucune instruction native n'est patchée.

## Audit natif : structures et arguments

Quinze plages désassemblées sont identiques dans les deux images. Le script contrôle aussi des mots exacts aux frontières critiques, au littéral GPIO et au store périphérique.

| Fonction | Arguments et comportement observés | Contraintes de durée de vie |
|---|---|---|
| C0070778 inscription | r0 sujet, r1 clé, r2 valeur supplémentaire, r3 triplet contexte/méthode/ajustement ; cherche clé existante, sinon slot libre | Sujet, clé et son vecteur doivent être valides ; le contexte a un propriétaire distinct |
| C0070688 notification | r0 sujet, r1 événement ; parcourt32 slots, teste actif, transmet sujet/slot/événement à C007061C | Sujet et tous tuples sélectionnables doivent rester valides pendant le parcours |
| C007061C invocation | r0 sujet, r1 slot, r2 événement ; lit clé, contexte, méthode et ajustement ; résout éventuellement la vtable ; BLX indirect | La cible résolue peut survivre en registres au retrait du slot ; méthode et contexte doivent former un tuple cohérent |
| C00705DC retrait | r0 sujet, r1 clé ; efface la première relation correspondante | Ne joint pas les cadres, ne libère pas le contexte, ne compacte pas le vecteur inverse |
| C0041B74 destructeur inverse | r0 objet-clé ; parcourt le vecteur des sujets, retire chaque relation puis appelle C0028DD4 sur le stockage | Les sujets référencés doivent encore être vivants ; aucune attente de callback n'apparaît dans ce corps |

Un sujet de base contient un en-tête4 octets puis32 entrées de24 octets, soit au moins772 octets. Une entrée contient clé+0, contexte+4, méthode+8, ajustement encodé+12, valeur supplémentaire+16, actif à l'octet+20. Le stockage inverse est décrit par clé+4 début, +8 fin, +12 capacité. La méthode peut être un pointeur direct ou un décalage dans une vtable ; l'ajustement signé est obtenu par ASR1, le bit bas choisissant le cas virtuel.

La valeur supplémentaire ne reçoit pas un sens universel : **dans C0082728**, elle sert de diviseur de période. Cette notification possède32 compteurs à sujet+0x308, soit un sujet étendu d'au moins904 octets. Elle appelle C007061C à C0082770 avec événement0. La notification ordinaire le fait à C00706B4 avec l'événement reçu. Une protection du seul C0070688 laisse donc un chemin natif explicite sans protection.

Le scan trouve119 branches candidates vers l'inscription,120 vers la notification ordinaire, deux vers l'invocation,12 vers le retrait,51 vers le destructeur inverse et un pointeur aligné vers ce destructeur. Ce sont des candidats ARM alignés, pas une reconstruction exhaustive des chemins exécutables. Appels calculés, Thumb, IRQ/FIQ et DMA ne sont pas exclus. Les tâches de tous les sites ne sont pas attribuées ; les contextes UI/service/timer connus R15 restent distincts.

Le registre ne confond jamais clé A et contexte B. L'inscription répétée sous une clé déjà présente n'actualise pas la fermeture. Retrait puis réinscription peut ajouter une nouvelle occurrence du même sujet au vecteur inverse. Un simple slot inactif laisse donc un chemin inverse résiduel.

## Trois frontières CPU reproduites sans patch

1. Arrêt à **C007061C**, avant chargement de clé : retirer la relation conduit au saut de l'invocation ; aucun callback.
2. Arrêt à **C0070650**, contexte déjà chargé mais tuple méthode/ajustement non chargé : retirer efface les deux mots ; le chemin reprend avec contexte non nul et méthode nulle ; **SIGSEGV à0**.
3. Arrêt à **C007067C**, juste avant BLX : contexte ajusté et méthode sont déjà résolus ; retirer l'inscription ne change plus les registres ; **le callback s'exécute**.

Les cas gardés aux deux dernières frontières demandent la fermeture mais conservent le tuple et dix emprunts inscription+parcours. Le callback finit ; le retrait physique est effectué au retour du parcours. Le changement de page logique au même point garde également l'ancien contexte jusqu'au retour.

Méthode : stub GDB QEMU, breakpoints internes `Z0`, seconde pile de fixture, injection d'un appel C de retrait/fermeture, puis restauration exacte du paquet complet de registres. Les octets à l'adresse d'arrêt sont comparés avant, pendant et après breakpoint. Aucun paquet d'écriture mémoire `M` ou `X` n'est envoyé. Les58 exécutions comparent ensuite tous les2 Mio natifs chargés avec l'image originale, y compris dans le gestionnaire de faute.

Il s'agit d'une **intercalation simulée par le débogueur**, dont les effets sont exécutés par les instructions ARM natives. Ce n'est pas une préemption effectuée par l'ordonnanceur Korg, ni une preuve de comportement IRQ. Les points d'arrêt ne changent aucun octet Korg. Les snapshots et restaurations sont consignés dans `results.json`.

## Expériences ARM et contre-exemples

Chaque ligne représente un cas exécuté une fois sur chaque VSB. Tous les cas retournent normalement sauf6 et17, conservés comme fautes attendues.

| Cas | Expérience | Résultat vérifié |
|---:|---|---|
| 0 | Notification gardée puis fermeture | Callback unique, retrait deux sens, inactivité locale |
| 1 | Demande de fermeture dans callback actif | Retrait différé, emprunts maintenus jusqu'au vrai retour |
| 2 | Retrait natif pendant callback actif | Le callback continue ; inverse encore présent avant finalisation |
| 3 | Retrait après résolution, avant BLX | Slot effacé mais callback quand même invoqué |
| 4 | Fermeture gardée au même BLX | Tuple intact pendant parcours, fermeture après retour |
| 5 | Retrait avant lecture de clé | Callback non invoqué |
| 6 | Retrait entre contexte et méthode | Invocation à0, SIGSEGV11 et exit88 ; allocations conservées |
| 7 | Fermeture gardée entre contexte et méthode | Aucun effacement prématuré, callback normal |
| 8 | Même clé, nouveau contexte/méthode | Ancienne fermeture conservée par Korg |
| 9 | Ancienne relation inverse puis réinscription | Deux occurrences constatées, compaction de fixture les retire |
| 10 | Callback réentrant | Deux cadres, emprunts indépendants, deux callbacks |
| 11 | Fermeture dans callback réentrant intérieur | Cadre extérieur toujours retenu ; retrait après les deux retours |
| 12 | Changement de page pendant notification | Nouvelle racine scalaire de fixture, ancien contexte retenu |
| 13 | Copie brute non enregistrée du slot | Invocation native après inactivité locale du graphe déclaré |
| 14 | Double fin de cadre / ancien ticket | Deuxième release refusée |
| 15 | Ancienne génération et même adresse | Token périmé refusé ; copie brute toujours capable d'appeler |
| 16 | Fermeture avec commande R15 en attente | Pins retenus jusqu'au refus avant effet et ACK, puis calme local |
| 17 | Fermeture puis worker LCD dans callback | Faute GPIO0x01E260BC ; cadre, callback et dix pins encore présents |
| 18 | Inscription après demande de fermeture | Admission gardée refusée ; inscription native directe encore possible |
| 19 | Relation inverse vers un autre sujet | Relation résiduelle bloque fermeture ; autre notification encore possible |
| 20 | Méthode directe et this ajusté de16 | Callback reçoit le sous-objet attendu |
| 21 | Méthode virtuelle et this ajusté de16 | Vtable et méthode résolues par le code natif |
| 22 | Notification périodique C0082728 après contournement | Callback événement0 malgré fermeture coopérative |
| 23 | Trois cadres, tentative d'un quatrième | Refus sans nouvelle référence ; drainage de trois cadres |
| 24 | Saturation lors d'une acquisition partielle | Rollback des pins déjà acquis, aucun cadre admis |
| 25 | Ticket maximal et fermeture répétée | Refus du rebouclage ; fermeture idempotente |
| 26 | Tuple actif avec contexte non recensé | Parcours gardé refusé avant les chargements natifs |
| 27 | Changement de page et fermeture après résolution | Ancien contexte retenu, page logique2, calme après retour |
| 28 | Deux slots natifs et fermeture dans le premier | Garde refuse le sujet inconnu ; parcours natif non gardé appelle encore le second |

Les contextes ordinaires sont systématiquement distincts de la clé. Les objets sont statiques et jamais libérés pour provoquer artificiellement une réussite ou un UAF. Les changements de page12/27 sont des fixtures scalaires : ils ne qualifient pas une destruction native complète de page. Le cas15 change les métadonnées de génération à adresse inchangée, sans réemploi réel d'allocateur. Le cas19 utilise explicitement une racine connue résiduelle ; le cas13 représente au contraire une copie omise de l'inventaire.

## Modèle borné

`model.py` explore six configurations : garde avant sélection avec retrait différé, retrait immédiat brut, compteur limité aux callbacks actifs ; chacune avec zéro ou une commande retenue. Deux parcours à usage unique et une demande de fermeture. Les états distinguent sélection, chargement du contexte, résolution, invocation, retour, release et faute. Les témoins négatifs sont publiés intégralement.

Les1080 états explorés ne donnent ni tuple déchiré ni callback après retrait physique pour le candidat gardé sous ses hypothèses. Les deux autres variantes possèdent les deux contre-exemples. Le vérificateur rejoue indépendamment les témoins négatifs et valide les transitions. Ce dernier ne constitue pas une seconde implémentation exhaustive indépendante du moteur d'exploration positif : le résultat positif reste celui du modèle publié et de ses hypothèses.

Le modèle suppose transitions atomiques, admission exhaustive avant chargement, identité fidèle des références et fin réelle avant release. Il ne démontre ni la primitive de gate, ni les propriétaires Korg, ni une borne de progrès. Un alias caché ou un appelant non participant sort du modèle ; les expériences ARM conservent justement ces contre-exemples.

## Architecture et risques

Le contrat détaillé, les alternatives et coûts sont dans `documents/RECOVERY_R17_CLOSURE_ARCHITECTURE_FR.md`. La matrice finale est dans `documents/RECOVERY_R17_RESIDUAL_REFERENCES_FR.md`, la carte native dans `documents/RECOVERY_R17_OBSERVER_LIFECYCLE_FR.md`.

Le protocole candidat interdit nouvelles admissions et nouvelles inscriptions gardées après CLOSING. Un cadre acquis avant sélection retient séparément sujet, clé, contexte, méthode/vtable et inverse. Le retrait du slot et la compaction inverse attendent la fin de tous les parcours admis. Les commandes déjà acceptées gardent leurs propres emprunts jusqu'au refus avant exécution et ACK. La fermeture intérieure est asynchrone : attendre son propre callback créerait un interblocage.

Une notification native déjà admise peut encore parcourir des slots après la demande de fermeture. Aucune promesse d'arrêt immédiat de toute nouvelle sélection interne n'est faite. Un protocole imposant cette règle plus forte nécessite une médiation par callback ou un parcours contrôlé, absents du système natif inchangé. Un sujet général à propriétaires multiples est également hors du candidat à une clé de cette mission.

Les sémaphores et helpers de masquage IRQ existent, mais aucun n'est établi comme verrou commun de tous ces chemins. Les routines observateurs ne consultent pas notre registre. Le helper qui pose I ne pose pas F. Tenir un mutex ou masquer les IRQ pendant le callback risquerait de bloquer la réentrée, la fermeture intérieure ou les attentes LCD. Le gate court requis par le candidat reste à qualifier avec tous les lecteurs et écrivains.

Mesures : métadonnées de fermeture1224 octets ; avec file R15 et admission/pool historiques,4528 octets réservés, hors objets natifs, autres fixtures, piles et journaux. Le banc réserve une pile d'injection de8192 octets, non proposée pour le firmware. Aucune RAM libre ni latence maximale ARM926/audio n'est prouvée. Le candidat ne change aucun framebuffer et conserve le triple buffer R12.

## Frontière LCD et récupération indépendante

Le cas17 entre directement dans C0015FA0 via le worker du banc après la demande de fermeture. Le helper natif C0016568 retourne la base GPIO0x01E26000, littéral à C0016594. Le chemin C0016B10 calcule pour les arguments observés l'offset0xBC et le store C0016B54 tente cet accès non mappé. La faute est donc à **0x01E260BC**, distincte de0xBC obtenu avec une dépendance nulle dans d'autres fixtures historiques.

Le snapshot conserve un parcours, un callback actif et dix emprunts. Les ressources restent retenues ; aucun faux retour n'est fabriqué. Le premier segment de shadow peut être copié avant cette frontière ; il ne confirme aucune réception LCD.

| Propriété | Résultat R17 |
|---|---|
| Détection d'une faute MMIO par Linux/QEMU | Observée dans le banc uniquement |
| Détection indépendante sur l'instrument | Non établie |
| Confinement CPU de références connues | Proposition conditionnelle : retenir les ressources et refuser nouvelles admissions |
| Annulation d'un worker déjà lancé | Non établie |
| Cessation GPIO/SPI/DMA | Non établie |
| Restauration / retour fiable à Korg | Non établi |

Aucun nouveau watchdog, aucun acquittement périphérique et aucune autorité d'annulation n'ont été inventés. La possibilité de garder indéfiniment un emprunt est un échec de progrès documenté, jamais une autorisation de destruction forcée.

## Développement, échecs conservés et corrections

Les journaux de développement sont conservés, distincts du journal final :

- `development-first-run.log` : premiers cas normaux puis refus de création de socket par le sandbox. Les essais GDB ont ensuite été exécutés avec accès réseau local autorisé. Il ne s'agissait pas d'une faute Korg.
- `development-task-step.log` : le callback périodique C002A71C revient sans transmettre dans l'état de fixture rencontré. Le point d'entrée direct du worker est utilisé pour la nouvelle expérience de rétention ; aucun succès LCD n'est revendiqué. Les mots de dépendance du descripteur sont écrits comme mots32 bits, pas comme octets.
- `development-verifier-mismatch.log` : attente initiale0xBC empruntée à une autre fixture, contredite par le véritable accès0x01E260BC. Le littéral natif GPIO et le store expliquent cette différence ; l'attente a été corrigée après analyse, sans modifier code natif ni réponse matérielle. Une assertion du vérificateur regardait aussi le snapshot intérieur à callback actif plutôt que l'état après retour : la définition conservatrice du prédicat calme est maintenue.

Ces journaux sont des observations de développement, pas des résultats de la source finale. Les58 cas finaux sont passés avec la source publiée, puis vérifiés indépendamment. Le lanceur complet a ensuite été exécuté avec succès ; son véritable journal est `launcher-validation.log`. `replay-comparison.json` compare ces58 nouveaux records et listes de blocs natifs avec le commit de preuves3369838 : tous sont identiques. La source finale ajoute explicitement le refus d’inscription gardée au cas18 ; les anciens fichiers restent accessibles dans cet ancien commit. Les variations de PID dans les traces brutes sont conservées.

## Reproduction et vérification des archives

Outils employés : clang19.1.7, LLD19.1.7 et qemu-arm10.0.13, versions exactes enregistrées dans provenance.json. Le binaire créé est un banc Linux ARM `LINUX_TEST_ONLY.elf` dans `build/`, jamais une image installable. QEMU utilise `-cpu arm926`, des traces `-d in_asm` et `-strace`. Les blocs traduits ne constituent pas un journal exhaustif des exécutions instruction par instruction ni un compteur de fréquence.

Avec les deux VSB originaux disponibles localement :

```sh
bash tests/run_recovery_r17.sh /chemin/custom.VSB /chemin/backup.VSB
```

Les cas GDB exigent l'accès loopback au stub QEMU. Le lanceur audite, exécute le modèle puis les expériences, vérifie, scelle les résultats et vérifie le manifeste. Rejouer régénère des preuves nouvelles : conserver les archives précédentes avant de le faire. Des PID/chemins du texte de trace peuvent différer ; la comparaison inter-VSB porte sur records complets et lignes de code natif, pas sur les PID strace. Les archives gzip sont créées avec mtime0.

Sans VSB, compilateur ni QEMU, les preuves publiées se vérifient avec Python et Git :

```sh
python3 tools/recovery_r17/verify.py --manifest
```

Empreintes des VSB vérifiées à l'entrée et après les expériences :

- custom : `81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03`.
- backup : `06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052`.

Les fichiers `0_N` et `1_N` correspondent respectivement à ces deux images. Chaque record décompressé fait2112 octets : seize mots d'en-tête,1024 octets source,1024 octets shadow. `results.json` contient les en-têtes et SHA des deux images par snapshot ; le vérificateur les reconstruit depuis les archives brutes. Les58 traces et58 archives de records sont publiées séparément avec leurs SHA réels dans `provenance.json`, ainsi que désassemblage, modèle, journaux et sources.

## Obstacles priorisés et proposition R18

1. **Autorité avant toute résolution** : attribuer les119/120 candidats, la notification périodique, les appels directs/indirects, changements de vtable et destructeurs à leurs contextes. Chercher un domaine réellement médiatisable ; conserver explicitement les inconnus.
2. **Propriété complète d'un sujet partagé** : déterminer propriétaires de chaque slot et de chaque inverse, méthodes virtuelles, sous-objets et alias de pages/services. Un graphe à cinq ressources ne généralise pas automatiquement à32 propriétaires.
3. **Primitive de gate et progrès** : prouver exclusion courte, visibilité, réentrée et ordre des verrous sous ordonnanceur Korg ; mesurer sans garder le gate pendant un appel bloquant. Aucun masquage IRQ seul ne suffit à justifier les autres domaines.
4. **Alternative sans destruction** : étudier une ancre immutable et une quarantaine bornée lorsque tous les appelants ne peuvent pas participer. Déterminer son coût réel et la preuve de son maintien en RAM, sans l'installer.
5. **Cessation périphérique indépendante** : traiter séparément détection, confinement, annulation et restauration ; l'absence d'autorité conserve NO GO.

**R18 proposée : « Couverture des résolveurs d'observateurs et ancres immuables sous quarantaine bornée »**. Elle devrait produire un inventaire des racines par domaine, des tests à propriétaires multiples et vtable modifiée pendant sélection, une analyse de primitive commune ou une preuve d'obstacle, puis une comparaison mesurée avec l'absence de destruction. Pas de flash ni intégration matérielle sans validation distincte. R18 n'est pas commencée ici.

## Explication simple

Mercury sait produire ses images et les travaux graphiques précédents sont conservés. R17 montre pourquoi retirer un observateur n'arrête pas forcément ce qu'il allait appeler : le processeur peut déjà en avoir gardé l'adresse, ou avoir chargé seulement la moitié de ses informations.

Dans le laboratoire, nous savons demander la fermeture, empêcher les nouvelles entrées participantes et attendre les vrais retours avant d'effacer leurs références. Il reste à prouver que tous les chemins Korg suivent cette règle et que le matériel peut réellement terminer ou arrêter une transmission LCD. Tant que ces preuves manquent, on garde les objets concernés en vie et la décision pour l'instrument reste **NO GO**.
