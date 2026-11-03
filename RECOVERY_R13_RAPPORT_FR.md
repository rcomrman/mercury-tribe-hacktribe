# Mercury Dust — R13 : coordination graphique et finalisation des preuves

3 novembre 2026 — branche exclusive `recovery/mercury-dust`. Base technique R12 : **9c4ba62541648ff057800c3b98619cdaa30092d8**. Reprise du commit intermédiaire **58bbfba748f499135a44170d170ec36d63023fa4**, conservé dans l'historique.

**R13 est achevée comme recherche logicielle bornée : les vingt scénarios par VSB, les archives originales retrouvées, le rejeu et la vérification indépendante ont effectivement réussi.** Aucun point de coordination global sûr ni récupération indépendante sur instrument n'est pour autant démontré. **RESEARCH_ONLY : aucun flash, firmware installable, intervention matérielle ou modification de routine native.** R14 est seulement proposée, pas commencée.

La dernière reprise a retrouvé le volume intact, conservé une archive avant synchronisation et intégré **2c2c578e9e3d7c1b3aed7f24112a525331ed47d1** sans réécriture de l’historique. Les preuves ont été publiées en priorité dans **6e413908a00edb9d877a6f7844b7ed9eca4b4786**, dont la tête distante a été vérifiée. Le vérificateur indépendant a réussi à nouveau sur ces archives ; les SHA-256 du manifeste et des deux VSB originaux ont été revérifiés. Cette reprise finale ne présente aucun nouveau rejeu comme une archive historique.

## 1. Ce qui a été retrouvé, comparé et reproduit

Le volume de la première session a été retrouvé avec la tête locale R12 et les répertoires R13 non suivis. Les **92 fichiers originaux** — sources, records, traces, résultats et audit — ont été conservés et hashés avant la synchronisation sur la sauvegarde GitHub. Leur origine est établie par cette conservation préalable et les contrôles croisés, pas par une déduction fondée uniquement sur leurs dates. Ce n'est pas une attestation cryptographique antérieure à l'interruption.

Les trois fichiers exécutables centraux, `tests/recovery_r13/coordinator.h`, `native.c` et `tools/recovery_r13/run.py`, étaient **identiques octet par octet** à la retranscription du commit intermédiaire. La retranscription de l'audit avait omis les quatorze lignes de couverture ; celle des modèles avait raccourci des explications et contre-exemples. Les versions originales plus complètes ont été restaurées. Aucune différence du programme ARM ou de ses attentes n'a été nécessaire pour obtenir le premier rejeu réussi.

Deux validations distinctes sont publiées :

1. **Archives originales retrouvées** : reparsing des quarante cas, oracles d'image, fautes exactes, correspondance entre VSB et modèle recalculé. Elles restent séparées dans `reports/recovery_r13/recovered_original/` avec un manifeste SHA de 92 fichiers.
2. **Nouvelles exécutions** : reconstruction du banc et rejeu du lanceur demandé. Le premier rejeu, avant instrumentation complémentaire, produit des records bruts identiques aux originaux pour les **40 cas**. Les traces binaires diffèrent ; leurs lignes d'instructions natives sont identiques pour les 40 cas. Les traces originales ne sont ni réétiquetées ni remplacées par le rejeu.

La revue a identifié une lacune d'observation réelle au **cas 16** : l'assertion vérifiant le diviseur corrigé était placée après un appel natif qui atteint la faute GPIO avant de retourner. Elle était donc inaccessible. La même assertion a été déplacée dans l'observateur de faute Linux, avec un record de diagnostic de valeur1. Le cas 18 émet maintenant explicitement ses 32 callbacks et ses indices de queue32/32. **Les fautes attendues, les images et les instructions Korg ne sont pas modifiées.** Cette lacune et sa correction sont conservées dans [validation_notes.json](reports/recovery_r13/validation_notes.json) ; aucun test ARM n'a échoué sur les attentes sauvegardées pendant la reprise.

Après ces deux ajouts d'observation, le lanceur complet puis le vérificateur autonome passent à nouveau :

- **40 scénarios ARM**, vingt par VSB, tous identiques entre les deux VSB ;
- **26 sorties normales de processus et 14 fautes attendues**, sept par VSB, toutes à **01E260BC**, signal11 ;
- **32 images V30 par VSB** comparées intégralement par SHA à l'oracle R1 ;
- états **DRAW, READ, CRITICAL et FAULT**, demandes différées, emprunts et refus vérifiés par des oracles explicites ;
- **31 plages originales identiques**, 118 candidats d'arêtes directes et matrice de 14 domaines ;
- modèle borné : **168 états, 252 transitions**, six arêtes de fin de scan et 27 états de dessin avec demande différée ;
- 52 archives de records R12 relues sans réexécuter R12, dont ses contre-exemples de publication et de sémaphore ;
- 92 fichiers originaux retrouvés toujours conformes au manifeste, et tous les chemins suivis avant R13 identiques à R12.

Les records finaux sont identiques aux originaux pour **36 cas sur 40**. Les quatre différences correspondent exactement aux deux nouveaux diagnostics sur chacun des VSB. Une fois ces diagnostics retirés et les numéros de séquence renormalisés pour comparaison, les **40 flux correspondent exactement**. Les lignes d'instructions natives correspondent aussi pour les 40 cas. Voir [comparaison du premier rejeu](reports/recovery_r13/baseline_replay_comparison.json) et [comparaison originale/finale](reports/recovery_r13/original_final_comparison.json).

Les fichiers `observations_intermediaires.json` et `extrait_sorties_observees.txt` restent des témoignages historiques de l'interruption. Leurs mentions d'archives alors inaccessibles décrivent l'état au commit58bbfba, pas l'état final présent. Le rapport de ce commit reste consultable dans l'historique.

## 2. Résultat technique et décision

**Aucun point de coordination extérieur unique, sûr et couvrant tous les accès n'est identifié dans le graphe inspecté.** Une coordination entre acteurs participants protège la composition dans le banc ; les accès qui ne la consultent pas passent toujours outre. L'absence de point global prouvé est un résultat de recherche, pas un motif pour patcher les routines ou fabriquer une réponse périphérique.

La piste retenue pour une recherche ultérieure consiste à coordonner des domaines complets : composition UI, lecture périodique LCD, opérations Korg synchrones dessin+LCD, démarrage exclusif et erreurs. L'admission de ces domaines et leur progression restent à prouver. La couverture finale est détaillée dans la [carte des accès](documents/RECOVERY_R13_GRAPHICS_ACCESS_MAP_FR.md) et les choix dans les [architectures](documents/RECOVERY_R13_PUBLICATION_ARCHITECTURES_FR.md).

Le triple buffer privé R12 est inclus tel quel. Tous les fichiers R1–R12, V30, huit presets, douze paramètres, quatre mini-LFO au total et IFX sont préservés. Aucun VSB n'est publié ou modifié. Les originaux de **0x200100 octets** sont contrôlés avant/après :

| Original | SHA-256 |
|---|---|
| user_custom (2).VSB | `81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03` |
| user_backup.VSB | `06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052` |

## 3. Découvertes natives

### Une autre voie UI

La tâche4 passe par C002D030 : le wrapper charge son gestionnaire puis appelle son slot virtuel +0xC. Cette frontière est une candidate commune à plusieurs modes UI, mais elle n'est pas une frontière globale LCD.

Le mode de service7 sélectionne le mode UI2. C002D07C mène alors au constructeur C0083478, qui installe la table C00E4BB8 :
- slot +0xC : C0083428, vidange de queue ;
- slot +0x10 : C00833F0, dispatcher ;
- slot +0x18 : C0083374, parcours graphique alternatif.

La chaîne testée est C002D030 → C0083428 → C00833F0 → C0083374. Le parcours active une page, appelle les slots enfant +8, retire les marqueurs puis demande l'opcode2 LCD. Il ne passe pas par C006F178. La queue, la construction du message, le publisher, le dispatcher et le parcours sont natifs ; le gestionnaire, la page et le composant Mercury sont fournis comme fixtures. Le constructeur général de cette UI n'est pas exécuté.

Cela est distinct des pages secondaires du gestionnaire principal : C00836E4 appelle C006EAE0, qui peut construire les pages23/24 par C006E9A0 ; C006F178 parcourt ensuite ses deux emplacements. Protéger seulement le callback Mercury ne couvre ni les autres widgets ni les transitions précédant le dessin.

### Progression et démarrage

C006038C dessine un rectangle puis demande successivement les opcodes2 et3. Les appels directs identifiés :
- C004D81C, dans C004D5CC ;
- C004D928, dans C004D860 ;
- C0060420, branche terminale du configurateur C006040C.

C006040C remplace un diviseur nul par1 avant de dessiner une progression initiale. C004D598 construit/récupère l'objet de progression à C0366D5C. C004D860 a trois appelants directs identifiés : C002AE90 dans la tâche initiale C002AB7C, C0031250 dans un service, C0038E40 dans un autre service. Le contexte complet des deux derniers n'est pas attribué.

Une garde du timer ne couvre aucun de ces appels synchrones. Refuser le scan en donnant au service critique un retour ordinaire n'est pas une équivalence sémantique prouvée.

### Les commandes LCD ne sont pas un protocole de pause

Dans le dispatcher inspecté :
- opcode1 appelle C0015F84 et efface la source ; il ne gèle pas sa composition ;
- opcode5 appelle un corps sans effet utile sur la demande ;
- opcode3 appelle le worker ;
- opcode7 entre dans une séquence GPIO/SPI distincte, sans passer par la comparaison d'image ;
- quand active !=1, même opcode0 est rejeté par le test initial.

Mettre directement active=0 dans une fixture bloque le worker, mais pas un appel direct au comparateur. Ce n'est pas une procédure native sûre de suspension/reprise. Aucun setter global de pause extérieure fiable n'est déduit de ces états de banc.

## 4. Coordinateur de laboratoire

[Architectures comparées](documents/RECOVERY_R13_PUBLICATION_ARCHITECTURES_FR.md).

Le nouveau coordinateur a les états IDLE, DRAW, READ, FAULT et CRITICAL. Son état C mesuré par les records initiaux vaut 32 octets, incluant le handle privé. Le pool R12 reste à 3 112 octets. Ce sont des tailles du banc ARM, pas de la RAM instrument disponible.

- begin DRAW retient une image du triple buffer.
- La copie est comptée ; end DRAW refuse une composition incomplète.
- Une demande pendant DRAW reste mémorisée ; elle ne lance pas de lecture.
- READ ne commence qu'à IDLE et doit couvrir les huit pages.
- Une nouvelle composition est refusée pendant READ.
- Une demande arrivant pendant READ est conservée pour plus tard.
- Une opération interrompue ne retourne pas arbitrairement à IDLE.
- Une phase CRITICAL candidate exclut de nouvelles compositions et demandes périodiques pendant une opération Korg synchrone complète.

Le code est séquentiel, sans atomiques, IRQ mask ni sémaphore installé. Chaque transition est supposée sérialisée par le banc. Ce n'est ni un hook ni une preuve de comportement multitâche réel.

La préparation par huit appels au comparateur original est un oracle de cohérence mémoire. Elle ne constitue pas un envoi et ne doit surtout pas être suivie d'une prétendue validation LCD fondée sur source=shadow.

## 5. Expériences finales reproduites et vérifiées

| Cas | Expérience | Résultat vérifié par le runner et les oracles indépendants |
|---:|---|---|
| 0 | Triple R12, 32 compositions en deux morceaux, demandes médiatisées | Scan différé ; 32 images source/shadow conformes |
| 1 | Tentative end DRAW après64 octets | Refus, emprunt conservé ; fin complète puis scan |
| 2 | Comparateur direct au milieu de DRAW | Shadow384 nouveaux/640 anciens malgré coordinateur |
| 3 | Progression native pendant DRAW, LCD inactif de fixture | La source change hors médiation même sans worker |
| 4 | Même progression, LCD actif | Première page partielle copiée puis faute GPIO ; DRAW reste actif |
| 5 | Événement type0 via UI alternative native, wrapper encadré | Composant fixture dessiné ; demande2 ; image V30 cohérente |
| 6 | UI alternative hors garde pendant une lecture par pages | Shadow384 anciens/640 nouveaux ; C006F178 absent du chemin |
| 7 | Opcode1 pendant DRAW | Source entièrement effacée |
| 8 | Opcode5 avant worker | Ne suspend pas ; copie partielle puis faute |
| 9 | active=0, opcode0 et comparateur direct | Pas de reprise par opcode0 ; comparateur lit toujours la source partielle |
| 10 | Opcode7 pendant DRAW | Accès GPIO sans préparation de pages ; faute |
| 11 | Worker original, source=shadow | Retour sans sender ; demande persistante, aucune confirmation physique |
| 12 | Nouvelle image complète, lecture médiatisée par worker | Première page préparée puis faute ; READ conservé |
| 13 | Nouvelle composition demandée pendant READ | Refus ; ancien scan cohérent puis nouveau traitement |
| 14 | Seulement copie complète protégée, scan non médiatisé | Mélange entre deux publications pourtant complètes |
| 15 | FAULT injecté pendant DRAW puis fermeture | Emprunt conservé ; fermeture non achevée |
| 16 | Configurateur progression avec diviseur0 | Diviseur corrigé à1 ; appel LCD synchrone atteint la faute |
| 17 | Timer natif C002A7EC avec callback de fixture | Diffère pendant DRAW ; worker réel après fin, puis faute GPIO |
| 18 | La callback republie pendant la vidange UI | 32 messages traités dans un appel ; demande LCD toujours différée |
| 19 | Progression native dans une phase CRITICAL isolée | Barre complète dans source/shadow avant faute sur dernière page |

Pour le cas19 : image initiale11 ; barre à x9..64, y61..62, donc56 octets de la page7 deviennent71. Le worker original copie cette page avant de rencontrer le GPIO. L'égalité des1024 octets source/shadow ne prouve toujours aucune réception physique.

Les sorties normales des scénarios négatifs signifient que l'observation attendue a été atteinte, pas qu'une intégration est sûre. Le handler de faute est Linux : il observe et termine, ne reprend pas Korg et ne simule pas le périphérique.

Le code natif est chargé RX, sans modification d'instructions. L'activité du descripteur et les objets de services sont des fixtures ; les bases matérielles proviennent des getters originaux. Aucun MMIO n'est mappé. Le rectangle dirty C031BB10 est une donnée native, pas un canari universel. Des gardes entourent le pool, précèdent la source et suivent le descripteur dans les chemins choisis.

## 6. Priorités, attentes et réentrée

Les rangs initiaux restent tâche2=1, UI4=4. Un plafond de priorité ne traite ni FIQ/DMA ni toutes les réentrées, et une attente peut rendre la tâche non prête. Le bit de dispatch ou un retour −25 ne constitue pas une garde : R11 a déjà montré que les boucles ignorent ce retour et exécutent leur callback.

Un verrou récursif peut laisser la progression lire une composition extérieure incomplète. Un verrou non récursif peut bloquer le même appelant qui détient DRAW. Reporter silencieusement un service synchrone n'est pas justifié.

Le wrapper UI commun vide la file jusqu'à vide. L'encadrer comme une seule longue transaction a un coût de progression : un producteur peut remettre un événement après chaque consommation. Le cas18 en observe32 ; le modèle décrit la répétition qui maintient la file non vide. Aucune fréquence ou famine physique mesurée n'est déduite.

## 7. Récupération indépendante

Aucun mécanisme indépendant de récupération n'est validé. Un worker bloqué conserve l'autorité READ/CRITICAL ; un timeout dans son propre appelant ne s'exécute pas. Libérer une protection depuis ailleurs sans annulation démontrée expose la mémoire encore utilisée.

L'opcode7 n'est pas un arrêt logiciel acquis du worker : il commence lui-même par GPIO/SPI et des attentes. Le diagnostic fatal utilise le LCD, tente le masquage IRQ et peut entrer dans sa boucle terminale. Ni le triple buffer, ni une demande de rafraîchissement ni l'égalité shadow/source ne résolvent ce problème.

**GO recherche logicielle ; NO GO installation, flash, récupération indépendante et garantie globale de cohérence sur instrument.**

## 8. Preuves publiées et reproduction finale

```bash
export PATH=/workspace/mercury-tools/bin:$PATH
bash tests/run_recovery_r13.sh 'custom.VSB' 'backup.VSB'
python3 tools/recovery_r13/verify.py
```

Le lanceur compile le banc ARM926, exécute les vingt cas sur chacun des deux VSB, reconstruit l'audit statique et les modèles puis appelle le vérificateur. Le second appel ci-dessus permet de relire indépendamment les archives sans rejouer les expériences. Aucun ancien banc R1–R12 n'est relancé ; seul le générateur d'entrées R1 inchangé régénère les images V30 et son SHA publié est exigé.

Le vérificateur final **n'importe ni `run.decode` ni `run.validate`**. Il parse les records, construit ses oracles d'octets et contrôle séparément les phases, les demandes, le slot retenu, le nombre d'octets copiés, les codes de sortie, les fautes et les chemins natifs. Il compare les VSB, contrôle les archives originales et R12, puis exige l'absence de modification de tous les chemins R12 et la présence du commit intermédiaire dans les ancêtres Git.

- [Résultats finaux](reports/recovery_r13/results.json), [journal ARM](reports/recovery_r13/validation.log), [journal du lanceur](reports/recovery_r13/launcher_validation.log), [vérification indépendante](reports/recovery_r13/independent_verification.log).
- Records et traces **du rejeu final** : `reports/recovery_r13/{0,1}_{0..19}.{records,trace}.gz`.
- Archives **de la première session retrouvée** : [manifeste original](reports/recovery_r13/recovered_original/manifest.json), puis mêmes noms de records/traces sous `recovered_original/reports/recovery_r13/`. Les sources originales archivées servent à l'identité et à la provenance ; la reproduction utilise les outils à la racine du dépôt.
- [Comparaison des sources et validation de récupération](reports/recovery_r13/recovery_validation.json), [notes de validation](reports/recovery_r13/validation_notes.json).
- [Audit et matrice structurée](reports/recovery_r13/access_graph.json), [désassemblage natif](reports/recovery_r13/native_disassembly.txt.gz), [journal audit](reports/recovery_r13/audit.log).
- [Modèles et contre-exemples](reports/recovery_r13/models.json), [journal modèle](reports/recovery_r13/models.log), [outillage](reports/recovery_r13/execution_environment.json), [provenance et SHA](reports/recovery_r13/provenance.json), [statut final](reports/recovery_r13/finalization.json).

Chaque record reprend le format R9 de2112 octets : seize u32 d'en-tête,1024 octets source et1024 octets shadow. Le numéro de cas vaut200+cas R13. Les observations de phase (étapes1/2/89) utilisent h3=phase et h4=(pending<<24)|(slot_lecteur<<16)|octets_copiés. Étape88 du cas16 observe le diviseur ; étape18 du cas18 observe les callbacks et les indices ; étape90 enregistre faute/signal ; étape20 enregistre phase finale et prepared_epoch. L'octet h7 appartient au rectangle dirty natif et ne doit pas être traité comme canari universel.

Les traces `in_asm` montrent des blocs traduits, pas chaque occurrence d'instruction. Les gardes de pool/zone adjacente sont contrôlées par assertions dans le banc, y compris dans l'observateur de faute ; les snapshots vérifient la source, la shadow et le descripteur. L'observation de SIGSEGV est une frontière Linux de laboratoire et n'est pas une exception Korg récupérée.

La compilation est Clang19.1.7, ARM926EJ-S en mode ARM, freestanding, -O2 ; QEMU utilise `-cpu arm926`. Les ELF Linux et les VSB lus restent hors Git. Aucune borne de cycles, pile native, RAM instrument disponible, IRQ/FIQ, DMA, cache/MMU ou coexistence audio/IFX n'est déduite des succès QEMU.

## 9. Limites et décision finale

R13 remplit la mission de recherche et de publication reproductible. Elle ne prouve ni la couverture de tous les appels indirects ou alias calculés, ni la possibilité d'installer un coordinateur sans modifier le fonctionnement réel de Korg. Les deux contextes de services amont de progression restent ouverts ; les diagnostics, le démarrage et les opérations de contrôle ne sont pas globalement médiatisés.

Les helpers du coordinateur sont des contrats séquentiels de fixture : `read_end` suppose que le lecteur a réellement terminé ; `critical_begin` suppose une source complète à IDLE et une admission déjà sérialisée. Ces préconditions ne sont pas des primitives noyau ni une preuve de détection d'un appelant non coopératif. La phase FAULT du cas15 est injectée par le banc ; lors des fautes GPIO, la phase DRAW/READ/CRITICAL antérieure est observée conservée jusqu'à l'arrêt du processus, pas convertie par une récupération native inventée.

**GO pour poursuivre la recherche logicielle. NO GO garantie de publication globale sur Electribe, récupération indépendante ou intégration matérielle.** Aucun flash, aucun force-push et aucune modification de main.

## 10. Proposition R14 — non commencée

**R14 : admission des domaines Korg exclusifs et autorité de reprise indépendante.** À partir des résultats réellement reproduits de R13 :

1. Attribuer les contextes de C0031234/C0038D80 et les autres entrées de progression ; conserver les accès inconnus dans la matrice.
2. Qualifier l'admission d'une opération native complète depuis une source cohérente, sans emprunt ni lecture actifs, et vérifier les retours/refus sans simuler un succès de service.
3. Étudier les points extérieurs RAM/callbacks et leurs durées de vie, sans installer de hook ; prouver la couverture des UI alternatives, pages secondaires et lecteurs synchrones.
4. Définir une borne ou une politique vérifiable pour les vidanges UI et les opérations bloquantes ; ne pas relâcher des ressources encore utilisées.
5. Établir une autorité de détection/confinement hors LCD, ou maintenir NO GO avec la frontière précise. Les chemins fatals doivent être traités explicitement.

Cette proposition ne lance ni de nouveaux tests R14 ni d'intégration. Mercury sait conserver et composer des images cohérentes quand le banc maîtrise tous les accès ; les vraies voies Korg non participantes et les blocages matériels empêchent encore d'en garantir l'affichage fiable et le retour sûr sur la véritable Electribe.
