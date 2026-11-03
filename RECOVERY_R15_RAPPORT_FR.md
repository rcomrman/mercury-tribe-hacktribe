# Mercury Dust — R15 : dispatch, conservation et cessation des accès

3 novembre2026. Branche exclusive `recovery/mercury-dust`. Base **81d6dcbe84d9d75ca817633c8d035b827a9409ad**. RESEARCH_ONLY : aucun flash, firmware installable, patch natif, changement de main ou force-push.

## 1. Conclusion

**GO pour poursuivre la recherche logicielle sur des codecs de commandes explicites et leur durée de vie. NO GO pour un raccordement transparent aux trois frontières Korg, la cessation globale des accès ou la libération/restauration des ressources LCD réelles.**

R15 précise les trois frontières demandées. Elles ont des contrats différents : l'UI consomme une queue mutable, le service construit des handles temporaires et appelle plusieurs méthodes synchrones, le callback périodique entre directement dans le worker. Aucune n'est une frontière globale couvrant les autres et les chemins de démarrage/progression/diagnostic.

Une file expérimentale conserve les valeurs scalaires, l'ordre FIFO, l'identité de commande, la génération de cible et le résultat terminal jusqu'à **acquittement explicite du destinataire**. Elle distingue acceptée, attente, refus, exécution et fin réelle. Elle ne fournit aucune annulation ni nouvelle valeur de retour à substituer aux fonctions Korg.

**58 scénarios ARM**,29 par VSB : **54 terminaisons normales et quatre fautes GPIO attendues**, records identiques entre VSB et mêmes lignes d'instructions natives. Le modèle abstrait indépendant explore **1360 états et4068 transitions**,152 arêtes de vrai retour et152 états de blocage conservant la commande active. L'audit compare **21 plages identiques** et vérifie les instructions déterminantes. Ces résultats sont de laboratoire, pas une sûreté matérielle.

## 2. Reprise, preuves et préservation

Le rapport R14, sa carte de contextes, son architecture d'admission et sa frontière de récupération ont été lus intégralement. Les rapports R11–R13 et les sources utiles ont été consultés pour les tâches, primitives, progression et durées de vie. Les expériences R1–R14 ne sont pas relancées. Les **155 entrées SHA-256 du manifeste R14** sont vérifiées en lecture seule.

Le banc inclut sans modification le chargeur R9, le pool R12, le gate R13 et l'admission R14. Le vérificateur exige que **tous les chemins suivis par la base81d6dcb restent identiques**. V30, huit presets, douze paramètres, quatre mini-LFO au total, IFX, triple buffer et anciennes preuves sont conservés.

Les deux VSB originaux, chacun0x200100 octets, sont hashés avant/après exécution et ne sont ni modifiés ni publiés :

| Original | SHA-256 |
|---|---|
| user_custom (2).VSB | `81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03` |
| user_backup.VSB | `06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052` |

Aucun nouveau rendu artistique n'est nécessaire à R15 : les images V30 validées R14 sont préservées par leurs preuves et l'absence de modification des sources, sans attribuer à R15 un nouveau test de32 frames qu'elle n'effectue pas.

## 3. Frontières natives étudiées

[Carte détaillée et matrice PROUVÉ/PARTIEL/NON COUVERT/INCONNU](documents/RECOVERY_R15_DISPATCH_BOUNDARIES_FR.md).

### C002D030 — UI

r0=wrapper ; wrapper+4=gestionnaire ; appel virtuel gestionnaire.vtable+0xC. Appel direct identifié à C002B1EC depuis tâche4. Le gestionnaire est résolu **au moment d'exécuter le wrapper**. Les messages ne sont pas des arguments de cette fonction : les consommateurs principal/alternatif les extraient de leurs queues, sur leur pile, et peuvent traiter plusieurs événements dans un appel.

Un report de l'invocation ne conserve donc pas automatiquement une commande, sa page ni son gestionnaire initial. Les cas10/11 montrent le changement de cible résolue et une rétention CPU privée contrôlée ; le second ne prouve pas la rétention native des pages. La réentrée du wrapper est possible dans la fixture : le cas12 conserve une profondeur extérieure après le retour intérieur.

La publication C0083FE8 peut ignorer un gestionnaire absent/inactif et ne fournit pas ici d'accusé fiable que le consommateur a exécuté la commande. Les primitives, messages de transition/destruction et appels directs aux gestionnaires doivent rester recensés séparément.

### C002D684 — services

r0=gestionnaire de services ; r1=message16 octets. Type signé à+4 ; deux mots à+8/+0xC. Route configurée tâche5 via C002D844/C002D87C. Les mots sont copiés par C003B7D4 ; **les données qu'ils peuvent pointer ne sont pas copiées profondément**. Le cas9 conserve le mot pointeur puis observe la mutation de son pointee encore alloué.

Le dispatcher construit deux petits objets à partir de ces mots et deux handles sur sa pile. Il passe les handles au slot+8 du service, entre les slots+0xC et+0x10. Il modifie des états, peut émettre des commandes/changements UI et publie le résultat avant son nettoyage final. C002D5B0 appelle le destructeur virtuel+4 ; C00A4758 fournit C002D434, qui libère le petit objet par C0028DD4. Aucun contrat de rétention profonde du pointee ne résulte de ce corps.

Différer après cette entrée imposerait de retenir pile, handles, pointees, contexte et effets déjà réalisés. Le cas15 exerce le routage natif de nettoyage avec un destructeur de fixture ; il ne prétend pas avoir exécuté tout le service ou son allocateur. Le code complet C002D684 n'est pas déclaré dynamiquement validé par ces sous-expériences.

C002D88C appelle le slot+0x14 du service courant. De nombreuses tables y placent C002DE78 : un store octet+0x19=1. **C002D684 remet ce drapeau à0 à la prochaine entrée.** Le drapeau d'arrêt, le busy manager+0x10 ou son numéro courant ne forment pas un certificat durable de cessation.

### C002A71C — callback LCD

Cette fonction ignore les arguments entrants, charge le descripteur fixe C031BB2C, l'opcode3 et argument0 puis branche vers C0015DD0. Son adresse figure à C002A970 dans la construction du compteur ; C002A7EC appelle callback+0xC à l'échéance. La route est en tâche2 ; le worker est synchrone, sans création d'un contexte indépendant.

Les cas16–18 exercent ce vrai callback : retour sans transport lorsque source=shadow ; puis faute GPIO après première page préparée lorsque la source change. Ni retour, ni demande, ni égalité shadow/source ne prouve la réception LCD. Les fonctions d'initialisation forcée, progression synchrone, diagnostic et contrôle7 contournent au moins une des trois frontières.

## 4. Conservation des commandes

[Architecture complète](documents/RECOVERY_R15_COMMAND_CONSERVATION_FR.md), [source du modèle C](tests/recovery_r15/commands.h).

La file de capacité3 admet un codec connu : quatre mots **scalaires**, ID strictement croissant et génération de cible. ACCEPTED signifie copiée/admissible initialement ; WAITING signifie copiée/conservée mais non exécutée. La fonction de démarrage revalide l'admission R14 et la génération. RUNNING indique un domaine réservé ; il ne prouve pas encore une instruction native exécutée. Le compteur `admitted` compte ces réservations, pas les effets. RUNNING ne devient DONE qu'après un vrai retour natif ; `result` exige le bon ID et DONE. Aucun état ANNULÉE n'est implémenté.

Le FIFO conserve la tête bloquée. La saturation refuse sans consommer l'ID non accepté, permettant une nouvelle tentative. Un ID déjà accepté ne peut être exécuté deux fois. Une génération devenue périmée produit un refus avant effets et une réponse conservée, sans exécution sur un nouvel objet et sans annulation fictive.

Un résultat DONE ou refus terminal reste dans la file jusqu'à ACK. Sans ce contrat, le recyclage d'un slot aurait écrasé une réponse non consommée. Le cas25 vérifie rétention, absence de réexécution, refus d'une requête de résultat/ACK au mauvais ID et libération du seul slot de file après le bon ACK.

La fermeture de file refuse le nouveau travail et conserve les commandes admises jusqu'à leurs vraies fins et ACK. Elle ne ferme pas de force l'admission R14 : une fermeture prématurée de celle-ci, un worker non retournant ou une suspicion peut empêcher définitivement le drainage. Le cas23 garde RUNNING et l'autorité CRITICAL, sans retour inventé.

Les exécuteurs positifs du banc construisent réellement un message via C003B7FC et appellent LCD2, qui est une **demande**, puis enregistrent le résultat réellement retourné. Cela teste le codec scalaire et sa conversation ; ce n'est pas un report générique des services17/34 ni de leurs appels synchrones réels.

### Limite de compatibilité synchrone

Reporter avant appel nécessiterait de retenir une continuation et tous ses objets, sans conserver un domaine dont dépend l'opération différée. Un appelant conservant DRAW en attendant une commande CRITICAL qui exige IDLE crée un cycle d'attente. Retourner WAIT à la place de la valeur native change l'ABI ; refuser requiert un contrat d'erreur réellement pris en charge par l'appelant. Aucun tel contrat commun n'est démontré aux trois frontières.

**Aucune médiation transparente de tous les services synchrones n'est donc validée.** Le modèle refuse explicitement les payloads pointeurs déclarés comme tels, mais ne peut détecter un appelant qui ment sur un mot u32. Un registre de cible/génération, une propriété profonde des arguments, une conversation de réponse et leur synchronisation native restent à prouver.

## 5. Cessation : la frontière de sûreté

[Étude détaillée](documents/RECOVERY_R15_ACCESS_CESSATION_FR.md), [matrice structurée](reports/recovery_r15/cessation_matrix.json).

Les sept étapes demandées restent distinctes : demande d'arrêt ; timeout ; changement de tâche ; fin de callback ; cessation de tous les accès CPU ; absence d'accès périphérique/DMA ; libération sûre. Aucune implication automatique n'est ajoutée entre ces niveaux.

- Le callback de fixture appelé par le wrapper natif demande l'arrêt puis **écrit encore la source** avant de sortir, cas13.
- Le wrapper natif de stop C002D88C revient, mais un autre appel au wrapper UI peut encore atteindre son callback, cas28. Aucun retrait des entrées futures n'est effectué par le store commun d'arrêt.
- Le callback intérieur termine tandis que l'extérieur est encore à profondeur1 et peut écrire, cas12.
- C0000ACC consomme le bit de réveil ; cela n'arrête pas l'autorité CPU recensée, cas19.
- Un réveil natif rend un TCB prêt sans exécuter son callback ; le sélectionné plus prioritaire reste distinct et RUNNING/CRITICAL sont conservés, cas26.
- Les références de file et enregistrements peuvent survivre à un retour local, cas14/20.
- Un registre local déclare zéro référence, mais un alias brut volontairement omis permet une nouvelle entrée native, cas27. Le helper local n'est donc pas un certificat global, même avant de considérer le matériel.

Les objets restent alloués pendant ces contrôles négatifs. Aucun buffer réellement libéré n'est réutilisé par un callback actif. Le helper `r15_local_cpu_quiet` ne libère rien ; sa portée est uniquement celle des références explicitement recensées dans la fixture.

Le worker réellement non retournant reste une possibilité matérielle modélisée par une autorité retenue indéfiniment. Le banc sans MMIO atteint une faute GPIO ; il ne fabrique pas de statut SPI pour simuler une attente ou sa résolution. Le handler Linux observe puis termine le processus, sans annulation ou restauration native inventée.

La sortie de tâche, le masquage IRQ, les listes de prêts et les destructeurs ne prouvent ni retrait de tous les producteurs ni arrêt périphérique. Le diagnostic utilise toujours le LCD et peut masquer IRQ. Aucun watchdog/reset indépendant n'est inventé ; l'absence de tout watchdog dans l'ensemble du firmware n'est pas conclue.

## 6. Expériences et contre-exemples

Chaque cas ci-dessous est exécuté sur les deux originaux. Les numéros17 et18 sont les seules fautes attendues, à **01E260BC/signal11** ; les54 sorties normales incluent des contre-exemples observés avec succès.

| Cas | Observation contrôlée |
|---:|---|
| 0 | Acceptée mais non exécutée, résultat indisponible ; entrée réelle puis résultat et ACK |
| 1 | Commande conservée pendant DRAW ; mutation du tableau appelant sans perte de copie ; exécution après fin |
| 2 | FIFO de trois commandes, vrais retours dans l'ordre |
| 3 | Saturation puis réessai de l'ID refusé après place libre ; quatre exécutions ordonnées |
| 4 | Doublon refusé avant/après terminaison ; pas de double effet |
| 5 | Génération périmée : refus avant entrée et ACK, sans exécution |
| 6 | Fermeture avant exécution : nouveau travail refusé, ancien drainé |
| 7 | Fermeture et réentrée pendant RUNNING : ni drainage fictif ni réexécution |
| 8 | Codec pointeur non supporté refusé |
| 9 | Copie native de message superficielle : pointee mutable non conservé |
| 10 | Wrapper UI différé résout le nouveau gestionnaire |
| 11 | Rétention d'un objet CPU privé de fixture conserve la cible, sans preuve native de durée de vie |
| 12 | Réentrée native du wrapper ; retour intérieur avec extérieur encore actif |
| 13 | Arrêt demandé dans un callback, écriture CPU ultérieure |
| 14 | Enregistrement encore présent après retour local : pas de calme local |
| 15 | Nettoyage natif du handle appelle le destructeur virtuel de fixture |
| 16 | Callback LCD original retourne avec image inchangée, sans transport |
| 17 | Callback LCD original modifié en source : shadow préparée puis faute GPIO |
| 18 | Même frontière avec commande RUNNING/fermeture demandée : aucune terminaison fictive |
| 19 | Bit de réveil consommé, accès CPU encore possible |
| 20 | Références de file conservées puis retirées : portée locale seulement |
| 21 | Soumission imbriquée conservée, réexécution refusée tant que le domaine extérieur est actif |
| 22 | Commande conservée pendant READ, réservation CRITICAL, exécution après les huit pages |
| 23 | Suspicion/fermeture : commande active et autorité retenues |
| 24 | Écrivain privé bloque CRITICAL ; abandon réel de l'écrivain puis admission |
| 25 | DONE retenue jusqu'à ACK ; mauvais ID refusé, résultat non écrasé |
| 26 | TCB réveillé mais non exécuté, domaine actif conservé |
| 27 | Faux calme global : alias omis du registre permet un nouveau callback |
| 28 | Wrapper natif d'arrêt revient sans supprimer l'accès au callback |

Le code original est chargé RX par le chargeur R9 inchangé. Les objets, tables virtuelles, registres d'identité, queues et entrelacements sont des fixtures déclarées. Pas d'ordonnanceur Korg complet, d'IRQ/FIQ/DMA ou d'accès matériel simulés. Les instructions CPSR traversées en Linux user-mode ne prouvent aucun masquage réel.

## 7. Modèles et vérification indépendante

Le modèle abstrait utilise trois requêtes, capacité2, deux générations de cible. Il explore acceptation/refus, conflit externe, transition de page, entrée native, arrêt demandé, timeout, retour réel et ACK. Il exige conservation de toutes les commandes acceptées dans une partition file/actif/terminal acquitté, absence de double exécution, conservation d'un actif après timeout et aucun recyclage terminal avant ACK. Les transitions sont supposées atomiques ; il ne prouve pas les métadonnées C concurrentes, l'équité ou une borne de progression.

Les1360 états/4068 transitions comprennent152 arêtes de retour natif et152 états avec commande bloquée retenue. Le modèle garde explicitement l'incompatibilité synchrone, la perte par copie superficielle, le changement de manager, l'écrasement de réponse sans ACK, la réentrée, le stop sans cessation et le transport encore possible après retour.

Le vérificateur indépendant n'importe ni le runner ni la file/protocole C. Il reparcourt les records bruts de2112 octets, reconstruit les images source/shadow, contrôle la séquence, les phases, compteurs, états terminaux, résultats réels/ACK, IDs et arguments. Il contrôle les marqueurs RUNNING/DONE, les fautes exactes et les chemins natifs des traces ; puis compare les VSB, revalide le manifeste R14 et tous les chemins antérieurs.

Les traces `in_asm` listent des blocs traduits, pas chaque occurrence ni une durée. Les assertions C couvrent aussi les refus intermédiaires ; aucune égalité source/shadow n'est utilisée comme accusé LCD. Les scans du cas22 testent la stabilité mémoire pendant READ, sans sender.

## 8. Échecs de développement conservés

[Notes](reports/recovery_r15/validation_notes.json) et journaux sous `reports/recovery_r15/failures/` :

1. Première compilation arrêtée par `-Werror` pour deux helpers hérités inutilisés. Les warnings n'ont pas été désactivés et R12–R14 n'ont pas changé. Des scénarios utiles utilisent l'abandon d'écrivain et la réservation CRITICAL.
2. Revue du modèle initial : risque d'écrasement d'une réponse terminale lors du recyclage. Ajout du contrat ACK et des requêtes de résultat liées à l'ID. Le probe antérieur est conservé dans `pre_ack_exploratory.tar.gz`, avec son SHA réel dans les notes/provenance ; c'est un artefact exploratoire de cette session, pas une archive historique retrouvée.
3. Dernière revue des observations : étape74 ajoutée pour vérifier explicitement les mots0/3 en plus des mots1/2 déjà observés à71. Le [comparatif des rejeux](reports/recovery_r15/replay_comparison.json) conserve la correspondance avec les preuves intermédiaires :58 flux identiques après retrait de ce seul diagnostic et renumérotation, ainsi que les mêmes lignes d’instructions natives. Le compteur d’admissions est nommé comme tel pour ne pas le confondre avec des effets natifs.
4. Premier vérificateur : table d'oracle omettant la fermeture de commande1 au cas18. Le C appelait déjà explicitement `r15_close` avant la faute. L'entrée corrigée exige close1/last_id1/head0 ; aucun résultat ARM, attente GPIO ou code natif n'a été relâché.

Aucun échec d'assertion ARM inattendu n'a été observé dans le lanceur final. Les échecs de compilation/vérificateur restent distincts des quatre fautes natives attendues.

## 9. Coûts, preuves et reproduction

La file mesure **128 octets ARM** ; le registre diagnostique local20. Avec admission R14+pool3176, ces structures distinctes représentent **3324 octets**, ou3304 sans le registre diagnostique. Ce coût ne comprend ni cibles, registre de générations, éventuels arguments profonds, réponses externes, piles et fixtures, ni code/source/shadow natifs. Aucune RAM libre ni borne de latence audio n'est démontrée.

```bash
export PATH=/workspace/mercury-tools/bin:$PATH
bash tests/run_recovery_r15.sh 'custom.VSB' 'backup.VSB'
python3 tools/recovery_r15/verify.py
```

Le premier appel compile et exécute uniquement les29 cas R15 sur chaque VSB, reconstruit l'audit et le modèle puis vérifie. Le second relit les archives sans exécuter les anciens bancs ni nécessiter les VSB. Clang/LLD19.1.7, ARM926EJ-S ARMv5TE en modeARM -O2 freestanding, QEMU Linux user-mode ; versions exactes dans l'environnement publié.

- [Audit initial des preuves R14](reports/recovery_r15/phase1.json), [audit natif](reports/recovery_r15/audit.json), [désassemblage compressé](reports/recovery_r15/native_disassembly.txt.gz), [journal audit](reports/recovery_r15/audit.log).
- [Résultats ARM](reports/recovery_r15/results.json), [journal ARM](reports/recovery_r15/validation.log), [journal du lanceur](reports/recovery_r15/launcher_validation.log), [journal indépendant](reports/recovery_r15/independent_verification.log).
- Records/traces : `reports/recovery_r15/{0,1}_{0..28}.{records,trace}.gz` ; SHA réels dans [provenance.json](reports/recovery_r15/provenance.json).
- [Modèles](reports/recovery_r15/models.json), [journal modèle](reports/recovery_r15/models.log), [outillage](reports/recovery_r15/execution_environment.json), [statut final](reports/recovery_r15/finalization.json).

Format R9 :16 u32, source1024 puis shadow1024. h1=400+cas ; h2=étape ; h5=numéro de séquence ; h6=garde0x39. Étape0 mesure128/20. Étapes1/20/89 : phase R14 et `count<<24|active<<20|admitted<<12|completed`. +100 : profondeur et `stop<<24|retired<<20|registered<<12|queued`. +200 : état du slot tête et `closing<<31|refused<<24|last_id<<8|head`. Un slot terminal peut rester lisible après ACK sans encore être compté dans la file ; les petits champs packés sont diagnostiques, non des compteurs universels sans limite. Étapes72/73 : ID et RUNNING/DONE ;74 : premier/quatrième mot scalaire ;70/71 : vrai retour et mots du message ;60/61/62 : observations de frontière ;90 : faute/signal. Aucun champ ne code une réception physique.

## 10. Sauvegarde et prochaines preuves

Les phases validées ont été poussées et leurs têtes distantes vérifiées :

- `d96f19f501cb1d457ebbcd21620f6a3964e95490` : reprise et manifeste R14.
- `f25dfd2b4fefcb8f27ff2b948ec1e00fdd9d8d34` : frontières, arguments et stop.
- `df68ef4de67641f64454cdf6872b83e52e19b27e` : file, ACK,58 cas et preuves.
- `a0565ae28887bfb396f7b573c4329954b323dcf3` : matrice de cessation et destructeur temporaire natif.

Ces commits restent dans l'historique ; les preuves finales proviennent du lanceur R15. R1–R14 restent inchangées. Aucun flash/firmware installable ou tentative matérielle.

### Obstacles priorisés et R16 proposée, non commencée

1. **P0 — Fermer le graphe CPU** : prouver le retrait de tous producteurs, queues, wrappers/alias, callbacks et continuations d'une cible. Le cas27 interdit de se contenter d'un compteur local.
2. **P0 — Arguments et ABI** : pour chaque commande native retenue, définir codec, propriété, outputs, résultat, durée de vie et règle réelle de refus/report. Aucun payload pointeur générique ni faux succès WAIT.
3. **P0 — Matériel** : prouver annulation/absence de transport en vol avant destruction ; aucun certificat périphérique disponible ici.
4. **P1 — Synchronisation et progression** : sérialisation ARM926 qualifiée, ordre des transitions de page, attente/ACK bornés, prévention des cycles DRAW→commande→CRITICAL. RAM, piles et latence audio restent ouvertes.
5. **P1 — Restauration** : état Korg connu, verrous cohérents et retour indépendant du LCD défaillant ; sinon NO GO.

**R16 : codecs par service et retrait des références CPU.** Choisir un sous-ensemble natif précisément identifié, qualifier ses entrées/outputs et ses pointees, puis rechercher les sites d'enregistrement/retrait et leurs époques de génération. Construire un modèle de registre exhaustif avec alias volontairement omis comme contrôle négatif. Rechercher une vraie autorité de cessation périphérique séparément, sans installation de hook ni matériel ; maintenir NO GO si elle manque.

Mercury sait conserver des images et, dans le banc, différer des commandes scalaires sans perdre leur ordre ou leur résultat. R15 explique pourquoi un arrêt demandé, un réveil ou un callback terminé ne suffit pas à libérer la mémoire. Pour afficher et récupérer de façon fiable sur l'Electribe, il manque encore la preuve qu'aucune voie Korg ni aucun transfert matériel ne pourra réutiliser ces ressources.
