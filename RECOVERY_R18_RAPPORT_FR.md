# MERCURY DUST — R18

## Couverture des observateurs, ancres immutables et quarantaine bornée

4 novembre 2026. Base : `c4fe851f64d325bc6311e4aa7cbee85ce2707cab`. Branche exclusive : `recovery/mercury-dust`. Aucun firmware installable, patch natif, flash ou essai matériel.

## Décision

**GO pour le prototype de laboratoire à pool monotone, sous contrats explicites. NO GO pour son intégration native, la destruction globale des objets Korg et la récupération LCD. Primitive commune de synchronisation : NON PROUVÉE.**

R18 fournit un inventaire de chaque candidat statique demandé, un prototype d'ancres à deux propriétaires et une quarantaine fixe sans réutilisation. Un ancien callback peut atteindre un thunk encore vivant après fermeture ; le thunk refuse alors le travail de son propriétaire retiré. Les callbacks entrés avant fermeture gardent leurs emprunts jusqu'au retour. La cinquième génération est refusée, sans réutiliser les quatre premières.

Trois limites sont démontrées : l'ancre ne protège pas un slot natif effacé pendant résolution ; une adresse stable ne protège pas une vtable ou un pointeur de payload modifié ; l'inscription native publie son slot avant d'ajouter le sujet dans le vecteur inverse. Aucun compteur local ne donne donc un droit général de destruction.

**Validation : 62 scénarios ARM, 31 par VSB : 54 retours normaux, six fautes attendues et deux timeouts hôte de callbacks volontairement non retournants.** Les31 paires de records et de lignes natives de blocs traduits correspondent exactement. Le modèle borné totalise140624 états, avec contre-exemples de réutilisation ABA et d'expiration suivie de destruction. Aucune réponse GPIO/SPI n'est simulée.

## Reprise et préservation

Le rapport R17, ses cartes, son architecture et les contrats R15–R16 nécessaires ont été relus. Les142 empreintes du manifeste R17 ont été vérifiées, ainsi que ses records et résultats par son vérificateur indépendant. Ses expériences ARM n'ont pas été rejouées. Les outils ARM926/QEMU et les deux fichiers VSB originaux du volume de travail sont disponibles.

La branche distante a été vérifiée au commit de départ. Les sauvegardes suivantes ont été publiées avec vérification de leur tête distante :

- `48c1a64a7c7f97301c8777b9391f49f4f1d957ab` : inventaire de couverture et vérification des archives antérieures.
- `a9262c49f86b2996f2efe111db520814b71a55e4` : premières60 expériences, modèle et preuves avant rédaction finale.
- `9d96026f0f03a5ab75e7ee6bd6840535bf32d114` :62 expériences avec fenêtre d'inscription/inverse et contrats de quarantaine.

Toutes les preuves nouvelles sont identifiées R18. Les précédentes versions restent dans ces commits ; aucun résultat historique n'est présenté comme retrouvé ou régénéré à l'identique. Le vérificateur contrôle tous les chemins suivis au commit de base et les142 entrées SHA R17. Aucun chemin R1–R17 n'est modifié. V30, huit presets, douze paramètres, quatre mini-LFO au total, IFX, triple buffer et VSB sont conservés.

## 1. Classement des observateurs et racines

La liste complète est publiée en JSON et CSV, avec désassemblage des voisinages, mots de code des témoins et chemins compressés. Elle comporte316 lignes :119 inscriptions,120 notifications ordinaires, deux invocations,12 retraits,51 destructeurs inverses, une notification périodique et11 resets de compteur.

Chaque ligne indique cible, adresse B/BL, empreinte du voisinage identique entre VSB, hint de prologue, racines syntaxiques, attribution de tâche, propriétaire UNKNOWN et absence de garde installée. Les239 candidats d'inscription/notification sont tous classés, sans être déclarés239 fonctions ni239 chemins exécutés.

| Classe | Inscription | Notification ordinaire |
|---|---:|---:|
| Possibilité syntaxique depuis au moins une des dix tâches |35|21|
| Aucune tâche attribuée par ce CFG |84|99|
| Total |119|120|

Le CFG parcourt les branches ARM directes, suppose le retour possible des appels et conserve les transferts PC indirects non résolus. Il ignore la faisabilité des conditions et l'appariement appel/retour. Ses chemins sont des possibilités syntaxiques, jamais une preuve de contexte exclusif. Tous les mots des chemins publiés sont identiques entre les deux VSB ; le vérificateur contrôle leurs arêtes.

Les enregistrements des dix tâches proviennent des adresses natives établies R11. Les racines supplémentaires isolent consommateur UI principal/alternatif, tick UI, dispatcher services, notification périodique, destructeur inverse, remplacement de page et IRQ15. Elles servent à expliciter les trous du graphe direct, sans inventer des tâches supplémentaires.

### Route périodique UI explicitée

Un pont typé séparé, vérifié par les mots de vtable/jump table/branches, raccorde les acquis R11 à :

```text
Tâche4 → C002D030 → gestionnaire principal C00E4C50
       → C0083848 → C00834FC → message type0
       → C00836E4 → C006EAE0 → C006EB74 → C0082728 → C007061C
```

Ce parcours exige le gestionnaire principal et des états précis ; il ne couvre pas les autres modes. Le tick utilise état=ui+0x10, puis le chemin périodique charge sujet=état+0x24 si état+0x18=0. Les propriétaires réels de ce sujet et de l'objet état+0x2C restent inconnus. Le périodique n'est donc pas assimilé à la seule tâche2. Ce pont conditionnel n'est pas injecté comme une arête certaine dans le CFG générique ; les comptes35/21 conservent leur sens limité.

Les deux branches natives vers C007061C restent C00706B4 et C0082770. L'invocation fait un BLX indirect à la méthode directe/virtuelle résolue. Le destructeur C0041B74 parcourt les sujets du vecteur inverse, appelle C00705DC puis libère le stockage. Appels indirects, autres vtables, IRQ/FIQ/DMA et propriétaires d'instances ne sont pas exhaustivement attribués.

Un résultat pratique : C006EAE0 commence par un chargement avant son push LR à C006EAE4. Le hint « nearest push LR » n'est donc pas une entrée de fonction prouvée. Aucune attribution de classe C++ n'est déduite de ce hint.

## 2. Architecture expérimentale des ancres

Une génération possède deux ancres de36 octets, un payload32 octets et deux ressources R16 : bundle des ancres et payload. Chaque ancre conserve vtable, index, génération de page, propriétaire et adresse du payload, après un préfixe de16 octets. Les mots de l'ancre, sa vtable et le code du thunk restent inchangés après publication. Le payload de démonstration est également immutable ; les sorties/counters sont externes.

La fixture exerce `this+16` en méthode directe et virtuelle, suivant l'encodage natif32/33. Les clés d'inscription, contextes et payload ne sont pas confondus. Deux clés/contextes peuvent partager le même payload avec des propriétaires distincts.

L'état mutable est hors du cœur logique : masque des propriétaires, registre de leases, tickets, rejets et statistiques. Il n'est pas isolé par une page matérielle read-only. Le hash est un contrôle du banc, pas une protection contre des écritures concurrentes et encore moins contre une vtable modifiée avant l'entrée dans le thunk.

À l'entrée du thunk, la fixture vérifie l'adresse du sous-objet connu, son propriétaire et l'état ouvert avant de prendre deux emprunts individuels. La première fermeture de propriétaire ne retire pas les droits de l'autre. Le dernier propriétaire retire les producteurs et les racines ; les callbacks déjà entrés gardent leurs tokens. Les numéros et tickets sont vérifiés au retour ; une réentrée reçoit une paire distincte. Trois paires simultanées sont possibles ; la quatrième est refusée avec rollback.

### Fenêtre sélection–entrée

Les cœurs d'ancre ne sont jamais libérés ou retargetés. Un callback déjà sélectionné mais non entré peut donc atteindre son ancien thunk et constater que le propriétaire est fermé. Il n'accède pas à un nouveau payload par réutilisation du même emplacement. Cela nécessite code, vtable et ancre stables, et une transition d'admission sérialisée ; la primitive native pour cette dernière demeure NON PROUVÉE.

Le protocole nominal **conserve les slots et vecteurs natifs** : les notifications fermées continuent d'appeler le thunk, qui refuse le travail. Il ne prétend pas avoir cessé les notifications natives. Un alias brut du payload, un destructeur concurrent ou une réécriture de vtable restent hors de cette admission.

`r18_destroy` refuse toujours. Aucun free, recyclage par délai, réemploi de slot ou autorisation de destruction globale n'est implémenté. Le payload reste alloué même après local_quiet ; le cas15 en conserve un alias brut lisible. Les destructions des politiques négatives du modèle ne sont jamais exécutées sur les objets ARM.

## 3. Nouvelles fenêtres natives et contre-exemples

### Effacement du slot malgré une ancre stable

À C0070650, le contexte est déjà dans un registre mais la méthode n'est pas chargée. C00705DC efface le tuple ; le retour dans C007061C conduit à une invocation nulle. Le cas4 conserve toutes les allocations et faute à0. Les ancres ne remplacent donc pas le retrait différé R17 lorsqu'on veut nettoyer physiquement une relation.

### Vtable et pointeur interne mutables

Sur un objet de contrôle conservé à la même adresse, changer la vtable avant C007066C sélectionne la nouvelle méthode ; la changer après C007067C laisse l'ancienne méthode en registre. Une vtable nulle avant résolution faute à0. Changer le pointeur de payload après résolution appelle le même code avec un autre payload. Ces cas6/7/8/24 distinguent stabilité d'adresse, contenu immutable et durée de vie des sous-objets.

### Slot actif avant relation inverse

C0070778 écrit actif à C00707C8 puis met à jour le vecteur inverse, avec éventuellement croissance par C00706C8. Le cas30 s'arrête à C00707CC lors de la seconde inscription, après préparation de la nouvelle ancre. Le slot est sélectionnable, mais l'inverse est encore vide. La notification injectée appelle les deux générations ; la nouvelle est ensuite fermée logiquement. La reprise de l'inscription ajoute enfin sa relation inverse, alors que l'ancre est fermée.

Les trois records explicites sont `[slot visible=1, inverse=0]`, `[local_quiet=1, inverse=0]`, puis `[inverse=4 octets, actif=1]`. Ce calme est local aux deux ressources R16 ; il ne signifie pas inscription native terminée. Aucun stockage n'est libéré. Une destruction fondée sur l'inverse seul pourrait manquer un slot déjà publié ; l'admission doit aussi couvrir les inscriptions en construction.

## 4. Quarantaine : borne d'espace et refus de progression

Le pool fixe contient quatre slots monotones, jamais réutilisés. La génération de page est index+1 ; elle ne change pas dans une ancienne ancre. Le registre R16 de chaque slot est neuf et garde sa propre génération de ressource1. Les deux espaces d'identité sont explicitement distincts.

| Mesure ARM | Octets |
|---|---:|
| Ancre |36|
| Deux ancres + payload + registre + racines + état d'un slot |400|
| Pool de quatre slots + en-tête |1616|
| Emprunt d'invocation |48|
| Huit clés et huit vecteurs préalloués |192|
| Sujet étendu persistant |904|
| Pool + clés/vecteurs + sujet |**2712**|

La forme générale de cette fixture est920 octets fixes +448 par génération, jusqu'à quatre. Les vtables, compteurs, piles et journaux sont en sus. La pile d'injection GDB8192 est réservée au banc. Le payload32 n'est pas une borne sur les pages Korg ou leurs pointeurs profonds. Aucune RAM libre ni marge de pile de l'instrument n'est prouvée.

Après quatre générations conservées, une cinquième allocation est refusée. La page courante reste la quatrième. Les anciennes notifications sont refusées par leurs thunks, sans réemploi d'adresse. Un callback non retournant garde ses emprunts ; l'expiration et le débordement de ticks statistiques ne changent ni son stockage ni son droit de destruction.

**La mémoire fixe du prototype est bornée par construction. Une progression indéfinie à mémoire fixe avec des références anciennes de durée non bornée ne l'est pas.** Il faut refuser de nouvelles pages, augmenter la mémoire ou obtenir une vraie preuve de cessation avant réutilisation. R18 choisit le refus. Cela est un coût fonctionnel documenté, pas une récupération sûre.

## 5. Synchronisation : résultat NON PROUVÉ

Le désassemblage vérifie les helpers CPSR et les services de sémaphore. C0000040 pose I sans poser F. C0000D80 vérifie le contexte, I et l'autorisation/état de dispatch, puis peut inscrire une attente et commuter via C0001760. C0000CA8 peut réveiller un attendant et demander un dispatch. Ces primitives ne sont pas un mutex commun auquel les observateurs participeraient déjà.

Les registres et le pool supposent une sérialisation extérieure de leurs transitions. Ni C ordinaire, ni volatile, ni hash, ni compteur ne démontrent visibilité et atomicité composées sur ARM926. Les caches/MMU, ordre des verrous, IRQ/FIQ et DMA ne sont pas qualifiés par les injections GDB.

Un gate éventuel devrait couvrir construction/selection, vtable et inverse, admission, fermeture et décisions de destruction, puis être relâché avant callback et attente. Il ne doit jamais être conservé pendant un LCD susceptible de bloquer. La fermeture intérieure ne doit pas attendre son propre callback. Aucun verrou commun couvrant les316 candidats et les routes indirectes n'est démontré ; ce statut reste **NON PROUVÉ**.

## 6. Expériences ARM sur chaque VSB

Les cas sont exécutés sur les deux images originales avec `-cpu arm926`. Les neuf intercalations par image utilisent le stub GDB R17 inchangé, une pile distincte et une restauration exacte du paquet de registres. Les breakpoints internes ne modifient pas les octets Korg ; aucun paquet mémoire M/X n'est envoyé. Chaque exécution, y compris faute et boucle non retournante, vérifie les2 Mio natifs chargés contre l'original.

| Cas | Expérience | Observation attendue et vérifiée |
|---:|---|---|
|0|Invocation normale puis retraite|Travail unique, calme local après retrait logique|
|1|Retrait avant notification|Ancien thunk invoqué, travail refusé|
|2|Fermeture après this, avant méthode|Tuple conservé, thunk refuse le propriétaire fermé|
|3|Fermeture après résolution, avant BLX|Ancien thunk vivant, aucun travail sur nouvelle génération|
|4|Retrait natif pendant résolution|SIGSEGV à0 malgré conservation de l'ancre|
|5|Emprunt préexistant, fermeture et retrait après drainage|Emprunt gardé jusqu'au leave explicite|
|6|Vtable changée avant résolution|Nouvelle méthode appelée sur adresse stable|
|7|Vtable changée après résolution|Ancienne méthode déjà en registre appelée|
|8|Vtable nulle avant résolution|SIGSEGV à0 ; allocations conservées|
|9|Sous-objet direct ajusté+16|Thunk reçoit le sous-objet attendu|
|10|Callback réentrant|Deux invocations avec paires d'emprunts distinctes|
|11|Fermeture dans cadre intérieur|Le cadre extérieur garde ses références jusqu'au retour|
|12|Deux propriétaires, retrait du premier|Premier refusé, second encore admis|
|13|Fermeture dans première notification à deux propriétaires|Deuxième thunk atteint mais travail refusé|
|14|Alias de slot copié non recensé|Ancien thunk fermé refuse son travail|
|15|Alias brut de payload|Toujours lisible après calme local, destruction refusée|
|16|Quatre pages successives et cinquième demande|Refus à saturation, page4 conservée, anciennes refusées|
|17|Fermeture puis worker LCD dans callback|Faute GPIO0x01E260BC ; emprunts conservés|
|18|Callback volontairement sans retour|Timeout hôte ; tokens encore détenus au dernier snapshot|
|19|Pool saturé avec emprunt retiré mais retenu|Délai sans effet ; calme seulement après leave explicite|
|20|Destruction demandée pendant notification périodique|Ancres conservées ; seconde invocation refusée|
|21|Fermeture après sélection périodique, avant BLX|Thunk vivant et refus de travail|
|22|Calme local mais clés/inverse natifs présents|Destruction refusée, périodique encore capable d'appeler|
|23|Réinscription même clé avec nouvelle ancre|Korg conserve l'ancienne fermeture, qui reste fermée|
|24|Pointeur payload changé à contexte stable|Le même code lit un autre payload : contre-exemple|
|25|Saturation de série/ticket|Refus sans emprunt résiduel|
|26|Délai et débordement des ticks|Ancienne ancre non recyclée, nouvelle génération ailleurs|
|27|Quarantaine pleine avec emprunt jamais libéré dans le scénario|Ancien slot non calme, nouvelles allocations refusées|
|28|Ticket étranger et double leave|Refus sans libération d'un autre emprunt|
|29|Trois paires puis quatrième tentative|Refus conservateur, drainage explicite des trois paires|
|30|Slot publié avant inverse lors d'inscription|Callback possible avant inverse ; relation ajoutée après fermeture logique|

Les contrôles de contexte mutable6/7/8/24 sont des objets distincts gardés alloués. Aucun free d'objet actif n'est utilisé pour obtenir une réussite. Les passages de pages sont des publications scalaires de fixture, pas une destruction native complète de page. Les anciennes routines graphiques V30 ne sont pas rejouées ou modifiées.

Les fautes4/8/17 sont conservées avec snapshots et traces. Le cas18 fait réellement une boucle de fixture ; le timeout tue le processus QEMU depuis l'hôte. Il ne prouve ni annulation de tâche Korg ni récupération indépendante. Le cas27 garde un emprunt de continuation dans une séquence finie ; il n'est pas présenté comme un véritable callback bloqué.

## 7. Modèle borné et vérification indépendante

Le modèle distingue sélection, résolution, entrée avec emprunt, retour et release. Deux acteurs à usage unique, deux slots, deux propriétaires par slot, une expiration et au plus trois événements de génération. Trois politiques sont comparées :

| Politique | États explorés | Résultat |
|---|---:|---|
| Conservation monotone, aucun recyclage |18118|Pas de hazard dans ce modèle, au plus deux stockages|
| Réutilisation dès compteur actif nul |99950|Témoin ABA : sélection ancienne routée vers nouvelle génération|
| Destruction sur expiration et actif nul |22556|Témoin d'accès après destruction, modèle négatif seulement|

Total140624 états. Le modèle positif conserve les ancres/payloads et suppose absence de mutation du slot pendant résolution, transitions atomiques et code immutable. Il ne modélise ni l'allocateur Korg, ni tous les alias, ni les périphériques, ni un gate réel. La permanence du stockage constitue ici le choix de conception, pas une découverte de cessation globale.

Le vérificateur ne se contente pas du texte PASS du lanceur : il reconstruit les en-têtes et images depuis les records, contrôle les sorties/fautes/timeout, compare les VSB, vérifie les arrêts/injections, mesure les structures et rejoue les témoins négatifs avec un interpréteur distinct. Il vérifie chaque candidat par rapport à l'inventaire R17, chaque chemin statique par les mots d'instructions archivés, puis les manifestes et les chemins historiques. Il ne refait pas une seconde exploration exhaustive indépendante du modèle positif : cette limite est conservée.

Les traces QEMU `in_asm` décrivent des blocs traduits, pas un journal d'exécution instruction par instruction ni une mesure de cycles. Les PID strace peuvent varier entre rejeux ; les lignes de code natif et records sont comparés séparément.

## 8. Provenance, reproduction et échecs de développement

Les VSB ne sont pas publiés. Leurs empreintes sont contrôlées à l'entrée et après les nouveaux essais :

- custom : `81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03`.
- backup : `06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052`.

Les fichiers `0_N` et `1_N` désignent ces deux VSB. Les records décompressés suivent le format R9 :2112 octets, seize mots d'en-tête et1024 octets source/shadow chacun. Les62 archives de records et62 traces sont gzip mtime0 ; `results.json` conserve leurs snapshots et métadonnées d'injection. Le lanceur complet a été exécuté avec succès ; son journal réel est `launcher-validation.log`. `replay-comparison.json` compare les62 records et listes de blocs natifs du dernier rejeu au commit9d96026 : ils sont identiques ; les PID des traces brutes restent propres au rejeu. Les SHA réels, versions d'outils et sources sont dans `provenance.json`. Ce manifeste ne se signe pas lui-même.

Le banc reprend le loader R9, le registre R16, le stub R17 et les linker/start historiques, sans modifier leurs sources. Il compile un exécutable **Linux de test uniquement**, jamais une image installable. Clang/LLD19.1.7 et QEMU10.0.13 sont utilisés ; les versions exactes sont scellées dans la provenance.

```sh
bash tests/run_recovery_r18.sh /chemin/custom.VSB /chemin/backup.VSB
python3 tools/recovery_r18/verify.py --manifest
```

La première commande nécessite les outils ARM et le loopback du stub QEMU. La seconde vérifie les preuves publiées avec Python et Git, sans VSB ni émulation. Un rejeu produit de nouvelles preuves : les versions précédentes doivent être conservées par commit/archive avant remplacement. Les preuves intermédiaires publiées répondent à cette exigence.

Les journaux `development-compile.log` et `development-link.log` conservent deux défauts du nouveau banc : tableau inutilisé compté seulement par sizeof, puis helper ABI de mise à zéro manquant. Le tableau non réellement réservé a été retiré des coûts ; le helper `__aeabi_memclr4` a été ajouté au seul code Linux de fixture, sans changer Korg. Un défaut de lecture de groupe regex dans l'audit a également été corrigé avant publication des données. Ces échecs de construction ne sont pas des fautes matérielles et ne sont pas mélangés aux six fautes ARM attendues.

## 9. Comparaison R17 et limites matérielles

R17 protège un parcours admis en retenant ses ressources et en différant les mutations du slot jusqu'au dernier retour. Il exige une couverture des producteurs avant leurs chargements. R18 conserve de façon permanente, dans sa capacité finie, les cœurs accessibles aux anciennes sélections et refuse le travail depuis le thunk fermé. Cela permet une défense sur une inscription Mercury volontairement conçue pour ce thunk, mais ne transforme pas les inscriptions natives arbitraires.

Les deux restent nécessaires si l'on veut un jour nettoyer physiquement les relations : les ancres ne rendent pas C00705DC atomique avec la résolution. Le nouvel ordre « slot actif puis inverse » exige de couvrir aussi la construction. Les anciens pointeurs bruts de payload et les sujets/vecteurs non conservés restent des obstacles à la destruction.

Le worker atteint encore GPIO0x01E260BC et conserve ses emprunts. Une shadow copiée ne signifie jamais image reçue. Les quatre obligations suivantes restent distinctes : détection indépendante, confinement, annulation, restauration. Ni faute Linux, ni timeout hôte, ni calme local ne les prouvent. Aucun watchdog, reset ou retour sûr à Korg n'est inventé.

## 10. Obstacles priorisés et proposition R19

1. **Propriété native précise** : attribuer sujet état+0x24, clés, payloads, sous-objets, vtables et inverse sur la route UI conditionnelle ; les autres instances restent UNKNOWN.
2. **Inscription en construction** : fermer les admissions avant publication du slot, retenir constructeur et inverse jusqu'au vrai retour, puis définir quand un retrait deux sens serait autorisé.
3. **Gate compatible Korg** : établir les contextes tâche/IRQ, ordre mémoire et ordre des verrous sans tenir un verrou pendant un callback ou le LCD. Sans preuve, maintenir NON PROUVÉ.
4. **Bornes réelles** : taille profonde d'une page native, réserve RAM et budget pile/temps ; le petit payload32 octets ne les remplace pas.
5. **Cessation périphérique** : trouver une autorité indépendante ou conserver NO GO. Le pool saturé doit refuser, jamais forcer un retour ou une libération.

**R19 proposée : « Admission des inscriptions en construction et propriété du sujet périodique UI »**. Périmètre concret : partir du pont tâche4/gestionnaire principal, analyser les constructeurs/destructeurs de état+0x24 et leurs inverses, construire un modèle de transaction inscription/fermeture avec participants multiples, comparer garde avant constructeur et quarantaine permanente, puis tester les contre-exemples de publication partielle. Aucun patch natif ou matériel ; aucune réutilisation d'adresse sans preuve distincte. R19 n'est pas commencée dans R18.

## Explication accessible

Mercury sait conserver une ancienne « adresse de rappel » et refuser son travail après fermeture dans le laboratoire. Mais garder cette adresse ne suffit pas si Korg efface une autre partie de l'inscription ou change ce qu'elle pointe.

Nous avons donc un prototype qui préfère garder quatre générations et refuser la suivante plutôt que libérer trop tôt. Pour aller sur l'Electribe, il manque encore la preuve que les chemins natifs respectent la coordination, que la mémoire réelle suffit et qu'un LCD bloqué peut être maîtrisé indépendamment. La décision instrument reste **NO GO**.
