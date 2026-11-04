# MERCURY DUST — R19

## Admission des inscriptions en construction et propriété du sujet périodique UI

4 novembre 2026. Base vérifiée : `6808871b54c10e130e085ab4e658bc8bf3cbf1bb`. Branche exclusive : `recovery/mercury-dust`.

## Décision

**GO pour la transaction de laboratoire sous sérialisation extérieure et durées de vie fixes. NO GO pour intégration native, destruction globale et récupération indépendante du LCD. Primitive native commune : NON PROUVÉE.**

R19 distingue désormais réservation, tuple écrit, slot actif, inverse présent, vrai retour du constructeur, fermeture logique et retrait physique d'un lien recensé. Une inscription en cours garde ses obligations même après demande de fermeture. L'inverse vide ou déjà rempli ne remplace jamais le vrai retour.

Le sujet périodique `état+0x24` est relié par instructions à une racine partagée `C0691244`, créée à la demande avec une allocation de 904 octets. `état+0x2C` reprend la racine `C0348844`, avec allocation de 1064 octets. Ces objets ne sont pas inférés comme propriétés exclusives d'une page. Un propriétaire concret d'inscription est également identifié : le constructeur `C00852B0` inscrit une clé inline à objet+0x38, tandis que son callback utilise l'objet entier.

**62 scénarios ARM ont été exécutés : 50 retours normaux, huit fautes attendues, deux sorties contrôlées avec constructeur encore suspendu et deux timeouts hôte.** Les 31 paires de records et de listes de blocs natifs traduits sont identiques entre les VSB. Le modèle borné explore 21 919 états. Les archives et le vérificateur conservent explicitement les contre-exemples.

## 1. Reprise, archives et conservation

Le rapport R18, les cartes R17/R18, l'architecture de fermeture R17, celle des ancres R18 et les documents R16 de propriété/retrait CPU ont été lus. Les 154 empreintes R18 ont été contrôlées et son vérificateur exécuté sur les archives existantes, sans rejouer les anciennes expériences ARM.

La branche et la tête distante ont été vérifiées au commit demandé. Sauvegardes publiées et vérifiées :

- `4910b6c5c850fbb47c79c4d0f3c89d15cf688c94` : audit de reprise et des racines UI partagées.
- `2170d59af4f932975302ed78c7743f35d175559f` : prototype corrigé, 62 expériences, modèle et premières preuves indépendantes.
- `37e77961c6c632dcd3f8128a40365c0b87d8873d` : contrats, fenêtres natives, propriétaire d'inscription concret et mesures mémoire.

Aucun chemin suivi au commit de base n'est modifié ; le vérificateur contrôle l'arbre complet et les 154 SHA R18. R1–R18, V30, huit presets, douze paramètres, quatre mini-LFO au total, IFX et triple buffer restent intacts. Les deux VSB sont lus et leurs empreintes recontrôlées ; ils ne sont pas ajoutés au dépôt.

Il n'y a ni patch d'instruction native, ni firmware installable, ni flash, ni essai matériel. Les fichiers binaires produits dans `build/` servent uniquement au banc Linux ARM ou au désassemblage.

## 2. Graphe de propriété du sujet périodique

Le pont antérieur est conservé : tâche4 → wrapper `C002D030` → gestionnaire principal → tick `C00836E4` → `C006EAE0` → `C006EB74` → `C0082728` → `C007061C`. Cette route dépend du gestionnaire et de ses états ; elle ne donne pas un contexte exclusif à tous les appels.

### Création et partage des objets d'état

Le constructeur UI `C00838E0` appelle `C006E6EC` sur ui+0x10. Ce constructeur d'état :

1. Consulte `C0691244`. Si nul, alloue 904, appelle `C00826A8` et publie le résultat dans la racine. Il copie ensuite le pointeur dans état+0x24.
2. Alloue aussi un enfant propre au chemin d'état, indépendamment de cette racine.
3. Consulte `C0348844`. Si nul, alloue 1064, appelle `C008241C`, publie dans cette seconde racine, puis copie dans état+0x2C.

Huit branches candidates vers chacun des deux constructeurs et les LDR littéraux des racines sont recensés. Les initialisations paresseuses inspectées ne possèdent pas de verrou commun démontré. Le partage est prouvé localement ; une initialisation unique atomique pendant toute la vie du système ne l'est pas.

| Relation | Statut | Portée |
|---|---|---|
| État intégré au gestionnaire à +0x10 | PROUVÉ | Paramètre du constructeur et du tick |
| état+0x24 alias de *C0691244 | PROUVÉ | Affectations natives, pas proximité d'adresses |
| Création paresseuse du sujet 904 / C00826A8 | PROUVÉ statique | Allocation complète non requalifiée dynamiquement |
| état+0x2C alias de *C0348844 | PROUVÉ | Allocation 1064 et constructeur C008241C |
| Plusieurs constructeurs utilisent ces racines | PROUVÉ comme candidats | Contexte exclusif de chaque instance non attribué |
| Propriété exclusive par la page courante | REJETÉE comme déduction | Les champs recopient des racines partagées |
| Persistance pendant tout le processus | PARTIEL | Hypothèse de singleton ; absence exhaustive de remplacement/free non prouvée |
| Autorité du dernier propriétaire / destruction globale | INCONNU | Alias indirects, cadres et autres destructeurs non exclus |

Le sujet périodique comporte 32 slots de 24 octets, une interface secondaire à +0x304 et 32 compteurs à +0x308. Sa vtable primaire vaut `C00E4B58`, celle du sous-objet `C00E4B68`. L'objet associé possède lui aussi le préfixe de 32 slots et une interface secondaire ; `C0082550` consomme 35 indices état/compteur. Aucun nom de classe métier n'est inventé.

Les constructeurs `C00826A8` et `C008241C` sont réellement exécutés sur des tableaux de fixture de tailles 904 et 1064, entourés de gardes. Le banc contrôle leurs champs documentés et les bornes d'écriture. Les octets de padding ne sont pas assimilés à des champs initialisés. Deux états de fixture sont ensuite raccordés aux mêmes racines ; leur chemin `C006EAE0` appelle réellement l'objet associé et le périodique.

Cette affectation des racines est une préparation de fixture, pas une allocation native simulée. Le constructeur d'état complet est essayé séparément et ne termine pas à la frontière de heap décrite plus bas.

### Propriétaire d'une inscription concret

Dans `C00852B0`, l'objet garde un sous-objet clé à +0x38. À `C00853A8` :

- sujet : *C0691244 ;
- clé : objet+0x38 ;
- contexte de callback : objet entier ;
- méthode directe : `C0085078`, ajustement0 ;
- période : 10.

Le destructeur `C00851B4` appelle `C0041B74` avec objet+0x38. Le thunk `C00851EC` ajuste le this secondaire de −0x38. La variante supprimante `C00851F4` appelle ensuite le free natif sur l'objet extérieur. L'inverse de cette clé se trouve donc dans les champs objet+0x3C/+0x40/+0x44.

Ces relations de contenance et de nettoyage sont prouvées par le flux local. Elles ne prouvent pas que la méthode déjà sélectionnée ait cessé avant la libération extérieure. Le sujet conserve une référence d'observateur, sans acquisition d'une propriété comptée démontrée sur l'objet.

### Destruction et transitions

`C006E6B0` appelle le destructeur inverse sur l'état lui-même. Le corps inspecté ne libère pas directement état+0x24 ou état+0x2C. `C0083898` l'appelle avec ui+16 ; sa variante supprimante libère ensuite le gestionnaire. Les transitions de page `C006E9A0`/`C006EFD0` peuvent détruire des gestionnaires courants, mais cela ne prouve pas la destruction de ces deux racines globales.

Les vtables des sujets donnent par ailleurs des corps de destructeurs et de free ; leur existence interdit d'affirmer que les objets sont immortels. Tous ces chemins complets et leurs alias ne sont pas qualifiés. Les statuts globaux restent PARTIEL/INCONNU.

## 3. La transaction native d'inscription

L'ordre de `C0070778` est reproduit sans modification :

| Phase | Instruction / fait | Obligation restante |
|---|---|---|
| Recherche de clé ou slot | C007078C–07A0 ; comparaison de clé avant actif | Un concurrent peut trouver une clé alors que le slot est encore inactif |
| Champs | Période, clé, méthode/ajustement, contexte | Le tuple est écrit en plusieurs instructions |
| Publication | C00707C8 : actif=1 | Le slot devient sélectionnable avant l'inverse |
| Inverse | C00707CC–07EC, ou croissance C00706C8 | Le constructeur est toujours actif |
| Sortie | C0070810 prépare la pile ; C0070814 retourne | L'appelant doit constater ce vrai retour |

Le retour natif est void. Un tableau plein peut revenir sans inscription ; une clé déjà existante ne reçoit pas le nouveau contexte. Le banc ne transforme ni ce retour ni le mot inverse en succès fictif.

## 4. Protocole expérimental

Le nouveau registre admet au plus huit identités de relation, sans recyclage. Avant C0070778, il vérifie fermeture, clé déjà recensée, capacité, ticket et absence d'autre constructeur/parcours participant, puis acquiert deux leases CONTINUATION sur ancres et payload R18. Le sujet, la clé et l'inverse vivent statiquement pendant toute la fixture ; leur durée de vie réelle n'est pas supposée résolue par ces deux tokens.

Une seule construction est réservée sur le sujet recensé. Le gate conceptuel n'est pas conservé pendant l'appel : c'est une obligation logique, pas un mutex tenu pendant une allocation. Une notification participante rencontrant BUILDING est différée/refusée avant l'appel natif ; l'appelant garde son événement. Aucune queue générale ou livraison de service Korg n'est simulée.

Le thunk de fixture refuse un travail pour une relation BUILDING, FAILED, CLOSING ou DETACHED. Un appel natif non participant peut néanmoins atteindre le thunk dès publication : l'ancre permanente rend ce refus possible, sans faire croire que le slot a cessé d'être appelé.

Au vrai retour, `r19_complete` vérifie slot actif, clé, contexte exact, méthode0, ajustement33, période1 et présence de l'inverse. Il s'agit du codec particulier de cette fixture, pas du codec natif période10/sub-objet+0x38 audité. La relation devient LIVE, CLOSING ou FAILED. Le retour de cette fonction accuse la restitution des obligations ; il ne vaut pas accusé de succès d'inscription native.

Une fermeture logique peut intervenir avant publication, après publication, après inverse ou dans un callback réentrant. Les constructeurs déjà admis restent retenus jusqu'à leur retour effectif. Les parcours retiennent leur obligation avant sélection/résolution ; les callbacks de travail gardent leurs propres emprunts. La fermeture intérieure ne doit jamais attendre son propre cadre.

Le retrait physique de fixture exige retour constaté, fermeture demandée, tuple concordant, zéro constructeur/parcours/callback recensé et table de sujet conforme à l'inventaire. Il appelle C00705DC puis compacte uniquement la relation inverse correspondante. Il ne libère rien et ne réemploie aucune adresse.

**Cette condition est locale et coopérative.** Inspecter les 32 slots ne découvre pas une copie brute de fermeture ni un pointeur déjà chargé hors des parcours participants. Les contre-exemples15/16 restent décisifs : faute à0 après effacement pendant résolution, ou callback déjà résolu encore invoqué après DETACHED. Aucun droit de destruction globale n'en découle.

Le mode de quarantaine permanente évite le retrait physique et conserve les relations. Il ne rend pas atomique une construction concurrente. Le candidat étudié combine donc obligation de construction R19, stabilité R18 et retrait différé R17, sans les installer dans le firmware.

## 5. Expériences ARM sur les deux VSB

Les nombres ci-dessous comptent chaque scénario une fois sur chaque VSB. 26 intercalations utilisent le stub GDB historique R17 sans le modifier : 24 restaurent exactement le paquet complet de registres ; deux sorties contrôlées ne reprennent pas le constructeur suspendu. Les breakpoints ne modifient aucun octet Korg, aucun paquet mémoire M/X n'est utilisé. Les 62 exécutions comparent les 2 Mio natifs chargés avec leur original.

| Cas | Expérience | Résultat |
|---:|---|---|
|0|Inscription, notification, fermeture|LIVE après retour, travail normal, lien détaché après drainage|
|1|Notification participante après actif/avant inverse|Différée ; travail seulement après vrai retour|
|2|Notification native pendant construction|Thunk atteint mais BUILDING refuse le travail|
|3|Fermeture avant écriture du tuple|Construction continue, obligations gardées, retrait après retour|
|4|Fermeture après publication/avant inverse|Slot actif et inverse vide ne déclenchent pas le retrait|
|5|Fermeture inverse présent/avant POP|Retour absent : retrait toujours refusé|
|6|Même fermeture avec quarantaine permanente|Slot et inverse conservés après retour ; travail fermé|
|7|Corps de destructeur inverse nul pendant construction|Pas de free ; exit87 contrôlé avec constructeur toujours suspendu|
|8|Inverse vide proposé comme critère de cessation|Critère rejeté, contre-exemple publié|
|9|Deux clés/propriétaires, même payload et sujet|Ancienne relation travaille, nouvelle BUILDING refuse, puis toutes deux LIVE|
|10|Notification réentrante|Deux cadres et deux paires d'emprunts distincts|
|11|Fermeture dans cadre réentrant intérieur|Aucun retrait avant retours intérieur et extérieur|
|12|Demande de page pendant notification|Construction refusée pendant parcours, rejouée après ; ancien alias refusé|
|13|Ancien slot/vtable/sous-objet conservé|Invocation réelle de l'ancien thunk fermé, sans réemploi d'adresse|
|14|Callback déjà résolu dans un parcours participant|Fermeture conserve le slot jusqu'au retour du parcours|
|15|Même résolution via parcours natif non recensé|Effacement prématuré, invocation nulle, faute à0|
|16|Méthode déjà chargée hors parcours recensé|Callback encore invoqué après retrait ; thunk refuse son travail|
|17|Réinscription gardée de même clé|Refus avant nouvel appel natif|
|18|Réinscription native de même clé/autre contexte|Korg garde le contexte précédent|
|19|32 slots déjà occupés|Appel revenu mais inscription FAILED, pas de succès ni retrait attribué|
|20|Croissance inverse réelle|Faute à C06A293C ; slot actif, inverse absent, constructeur toujours retenu|
|21|Destructeur inverse nul après détachement local|Corps exécuté sans free, pas de destruction d'allocation|
|22|Deux états, racines S/A partagées|Constructeurs de sujets et chemin C006EAE0 réellement exécutés|
|23|Destructeur base d'état, inverse propre nul|Ne libère pas les pointeurs +0x24/+0x2C dans ce corps|
|24|Constructeur UI complet tenté|Faute d'extension heap après +0x24, avant affectation +0x2C|
|25|Fermeture puis worker LCD dans callback|Faute GPIO0x01E260BC, parcours/callback/emprunts conservés|
|26|Callback volontairement sans retour|Timeout hôte, obligations toujours présentes au dernier snapshot|
|27|Ticket maximal, double fin, fermeture répétée|Refus sans nouvelle construction admise|
|28|Deux propriétaires puis retrait du premier|Seconde relation encore admise en notification périodique|
|29|Inscription native non participante pendant parcours|Nouveau tuple hors inventaire, nettoyage coopératif refusé|
|30|Une autre fermeture gagne la clé après préflight|Slot et inverse présents mais contexte différent : FAILED|

Les contextes/vtables des ancres et toutes les allocations de fixture restent conservés. Les transitions de pages sont des changements contrôlés de fixture, pas la destruction complète d'une page Korg arbitraire. Les constructeurs/destructeurs complets de l'abonné C00852B0 sont audités statiquement seulement.

### Contrôle du destructeur pendant construction

Le cas7 utilise réellement un vecteur nul. C0041B74 réécrit la vtable de la clé, constate le vecteur nul et retourne sans free. Le slot reste sélectionnable et atteint le thunk BUILDING. Le laboratoire termine ensuite explicitement ; il ne restaure ni ne reprend le constructeur. Le record81 indique construction=1, retour=0.

Aucun vecteur non vide n'est libéré pendant construction ; aucune clé détruite n'est réutilisée. Ce cas n'est ni une inscription terminée, ni une récupération, ni une autorisation d'exécuter le destructeur complet sur l'instrument.

### Frontières du heap et du LCD

Les cas20/24 exécutent l'extension de heap native jusqu'au store C000A3C4 vers C06A293C, cellule non mappée dans ce banc. Aucun allocator n'est remplacé et aucune réussite mémoire n'est fabriquée. La faute n'est pas interprétée comme OOM ni comme une erreur de la véritable Electribe. Le constructeur d'inscription20 reste BUILDING ; le constructeur d'état24 n'a affecté que son champ +0x24 parmi les deux alias étudiés.

Le cas25 atteint GPIO0x01E260BC. La copie éventuelle de shadow ne confirme aucune réception d'image. Le cas26 est une boucle de callback de fixture que l'hôte termine après timeout ; cela ne démontre aucune annulation native, cessation périphérique ni restauration Korg.

## 6. Modèle borné

Deux relations/propriétaires et deux parcours à usage unique ; chaque constructeur distingue réservation, tuple, publication, inverse et vrai retour. La fermeture, la sélection, la résolution, l'entrée, le retour de callback et la libération de son cadre sont séparés. Il n'y a aucun free.

| Politique | États | Résultat |
|---|---:|---|
| Garde avant constructeur et retrait différé |1 397|Pas de violation dans le modèle sous contrat|
| Quarantaine permanente et admission du thunk |3 934|Pas de retrait dangereux ; stockage toujours conservé|
| Retrait fondé sur inverse vide |11 793|Retrait avant retour, publication/inverse tardifs, cadre non cessé et tuple déchiré|
| Commit dès inverse présent |4 795|Retrait autorisé avant vrai retour, violation du contrat de construction|

Total : 21 919 états. Le modèle réserve un constructeur à la fois et suppose des slots distincts et des transitions atomiques ; la quarantaine seule ne démontre pas ces préconditions. Les violations négatives sont des transitions du modèle, jamais des frees réalisés dans les tests ARM.

Le vérificateur indépendant rejoue les témoins négatifs avec un interpréteur séparé et vérifie les transitions. Il ne refait pas une seconde exploration exhaustive indépendante de la politique positive. Il ne modélise ni tous les alias Korg, ni l'allocateur réel, ni IRQ/FIQ/DMA, ni l'arrêt du transport LCD.

## 7. Synchronisation, réentrée et mémoire

Le mécanisme requis serait un gate court sérialisant réservation, publication de métadonnées, fermeture et admission des parcours. Il serait relâché avant constructeur, notification et attente. La réservation du constructeur reste une obligation de durée de vie, sans conserver un mutex pendant l'appel. Un constructeur bloqué conserve cette obligation et impose un refus conservateur aux autres admissions.

Les helpers CPSR posent I sans poser F. Les services de sémaphore peuvent refuser certains contextes, inscrire une attente et commuter. Aucun verrou commun respecté par tous les constructeurs, notifications, destructeurs et initialisations paresseuses n'est démontré. `volatile`, un compteur nul et le stub GDB ne prouvent ni visibilité cache/ordre ARM926 ni exclusion IRQ/FIQ/DMA. **NON PROUVÉ**.

Mesures émises par la source finale :

| Structure | Octets |
|---|---:|
| Relation R19, dont obligation constructeur48 |100|
| Registre de huit relations et contrôle |836|
| Pool R18 réutilisé |1616|
| Clés/vecteurs de fixture |256|
| Sujets S/A et gardes |1984|
| Somme de ces structures |**4692**|

Le surcoût du seul registre R19 est836 octets. Les états UI, vtables, tableaux de saturation, piles et journaux s'ajoutent à cette somme. La pile GDB8192 est exclusivement instrumentation. Ces mesures ne prouvent pas de RAM libre ou de marge de pile sur l'Electribe.

Les deux tokens du constructeur retiennent ancres et payload ; sujet/clé/inverse sont permanents dans le banc. Un vrai graphe demanderait aussi leur propriété et leur durée de vie explicites. La mémoire profonde des pages natives, le temps CPU et l'impact audio restent non prouvés. Aucun buffer V30 ou triple buffer n'est modifié.

## 8. Preuves reproductibles et vérification

Les fichiers de `reports/recovery_r19/` comprennent :

- `ownership.json`, contrats d'instructions, graphe de propriété et candidats de racines ; `native-ownership.txt.gz`, désassemblage des plages identiques.
- 62 archives `0_N/1_N.records.gz` et 62 traces, `results.json` et `arm-run.log`.
- `model.json`, témoins complets et journal réel du modèle.
- Journal de vérification indépendant, manifeste des SHA réels et versions d'outils.
- Archive des premiers essais et journal de correction, conservés distinctement des preuves finales.

Chaque record décompressé fait 2112 octets : seize mots d'en-tête, source1024, shadow1024. Le vérificateur reconstruit en-têtes et empreintes depuis les archives brutes ; il contrôle les catégories de terminaison, les intercalations, la comparaison entre VSB, les tuples et retours, les contrats natifs et la conservation historique. Les groupes de snapshots sont lus par leur séquence de records, pas par un numéro de stage supposé unique.

Les traces QEMU `in_asm` décrivent des blocs traduits et non un journal exhaustif de chaque instruction exécutée. Les lignes de code natif sont comparées entre les VSB ; les PID strace et chemins du rejeu ne sont pas assimilés à une divergence native.

Les outils sont clang/LLD19.1.7 et QEMU10.0.13 ; les versions exactes sont enregistrées. Les SHA des VSB sont contrôlés à l'entrée et après essais :

- custom : `81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03` ;
- backup : `06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052`.

```sh
bash tests/run_recovery_r19.sh /chemin/custom.VSB /chemin/backup.VSB
python3 tools/recovery_r19/verify.py --manifest
```

Le rejeu nécessite les outils ARM et l'accès loopback au stub QEMU. La vérification des preuves publiées ne nécessite que Python et Git, sans VSB ni émulation. Le lanceur audite, exécute modèle et expériences, vérifie, scelle puis vérifie les SHA. Un rejeu crée de nouvelles preuves ; conserver les archives antérieures par commit ou copie avant de les remplacer. Le manifeste ne s'inclut pas lui-même. Le lanceur complet final a été exécuté avec succès ; son véritable journal est `launcher-validation.log`. `replay-comparison.json` compare les 62 records et listes de blocs natifs au commit37e7796 : tous sont identiques, malgré l’isolation supplémentaire du descripteur temporaire de fixture. Il ne prétend pas comparer des exécutables de fixture identiques ou les PID strace.

## 9. Corrections et limites de preuve

`development-compile.log` conserve une erreur d'indentation du nouveau header, corrigée sans changer le code natif. `development-first60.tar.gz` conserve les 60 premiers records/traces, leur JSON et les sources de cette version de développement. Cette archive n'est pas présentée comme une version finale validée.

L'analyse a montré que vérifier seulement slot actif et inverse présent pouvait attribuer un contexte concurrent à la mauvaise transaction. Le registre final vérifie aussi le tuple exact, et le cas30 démontre le rejet de cette collision. Le descripteur temporaire de fermeture est aussi placé sur la pile de chaque appel, afin que le constructeur concurrent de contrôle ne réécrive pas celui du constructeur suspendu. La collision de clé est ainsi isolée d’un partage artificiel de descripteur temporaire. La source, ses tailles et les 62 preuves finales ont ensuite été rejouées et vérifiées. Les erreurs et contrôles négatifs ne sont pas effacés ni convertis artificiellement en succès.

Le résultat positif reste conditionnel à la participation de tous les accès concernés. Les tests15/16/29 démontrent justement que la présence d'une table cohérente et d'un compteur local nul ne recense pas les références déjà chargées hors protocole. Ni la clôture locale ni DETACHED ne sont un certificat de destruction réelle.

## 10. Obstacles et proposition R20

1. **Admission des destructeurs réels** : partir de l'abonné à clé inline+0x38, suivre tous ses cadres, aliases et appels au destructeur inverse puis au free extérieur. La chaîne native ne fournit pas ici de join.
2. **Autorité sur les sujets partagés** : attribuer les écritures/remplacements des racines C0691244/C0348844 et tous leurs aliases ; distinguer détenteur global, emprunteur et dernier propriétaire.
3. **Primitive commune** : établir les contextes tâche/IRQ, l'ordre mémoire et les règles de réentrée, sans garder de verrou pendant notification ou LCD. Sinon maintenir NON PROUVÉ.
4. **Allocations et mémoire profonde** : traiter la frontière de heap sans fabriquer d'allocator, puis borner pages et dépendances réelles ; ne pas confondre tailles de fixture et RAM disponible.
5. **Cessation périphérique** : continuer séparément détection, confinement, annulation, restauration. Aucun de ces quatre points ne découle de la copie dans la shadow ou du timeout hôte.

**R20 proposée : « Admission des destructeurs d'abonnés et autorité de retrait des sujets partagés »**. Périmètre concret : propriétaire natif C00852B0/clé+0x38, destructeurs C00851B4/C00851F4 et inverse C0041B74, anciennes sélections et références globales ; produire un modèle construction–notification–destruction avec arrêt avant tout free non autorisé, et comparer domaine entièrement médiatisé et maintien en quarantaine. Aucun patch natif ou matériel. R20 n'est pas commencée ici.

## Explication accessible

Mercury sait maintenant distinguer une inscription commencée, déjà visible et réellement terminée. En laboratoire, une demande de fermeture garde les références nécessaires jusqu'au vrai retour et jusqu'à la fin des parcours connus.

Le sujet périodique est partagé entre plusieurs objets ; retirer une page ne suffit donc pas à conclure qu'il peut disparaître. Il manque encore la preuve que tous les chemins Korg suivent la coordination, que les destructeurs attendent les anciens callbacks et qu'un LCD bloqué peut être maîtrisé indépendamment. Pour l'instrument, la décision reste **NO GO**.
