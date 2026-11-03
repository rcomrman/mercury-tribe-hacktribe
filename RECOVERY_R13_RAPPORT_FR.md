# Mercury Dust — R13, sauvegarde intermédiaire : coordination graphique Korg

3 novembre 2026. Branche exclusive recovery/mercury-dust. Base : 9c4ba62541648ff057800c3b98619cdaa30092d8.

**MISSION INTERROMPUE, NON VALIDÉE FINALEMENT. RESEARCH_ONLY.** L'environnement est devenu indisponible après les essais, avant le vérificateur indépendant et la publication des archives brutes. Cette sauvegarde est publiée par le connecteur GitHub. Elle ne doit pas être confondue avec un rapport R13 achevé.

## 1. État exact de la preuve

Les rapports R11/R12 et l'architecture R12 ont été lus intégralement. Le dépôt a été synchronisé sur R12 ; les deux VSB ont leurs SHA de référence. Les commandes ARM ont terminé avant l'interruption :
- 40 scénarios, vingt par VSB : 26 sorties normales de processus et quatorze fautes attendues à 01E260BC.
- Le runner exigeait les résultats, les empreintes des images, les chemins natifs et la correspondance exacte des records entre VSB.
- Le cas0 traitait les 32 images V30 sur chacun des deux VSB.
- L'audit exécuté indiquait 31 plages originales identiques et 118 candidats d'arêtes directes.
- Le modèle exécuté indiquait 168 états et 252 transitions pour deux compositions et des scans de huit pages.

**Les records, traces et JSON complets produits localement sont devenus inaccessibles avant leur publication.** Ces chiffres sont des observations de session, pas des archives indépendamment consultables dans ce commit. Aucun fichier de trace ou hash de trace n'a été fabriqué. Le vérificateur indépendant n'a pas été exécuté. Les sources sauvegardées ont été retranscrites depuis les commandes de la conversation ; leur identité octet par octet avec le volume inaccessible ne peut pas être vérifiée. Leur recompilation et leur réexécution sont obligatoires.

[État structuré](reports/recovery_r13/observations_intermediaires.json), [extrait des sorties](reports/recovery_r13/extrait_sorties_observees.txt).

## 2. Conclusion technique provisoire

**Aucun point de coordination extérieur unique, sûr et couvrant tous les accès n'est identifié dans le graphe inspecté.** Une coordination entre acteurs participants protège bien la composition dans le banc ; les accès qui ne la consultent pas passent toujours outre.

La piste à approfondir consiste à coordonner des domaines complets :
1. composition UI, y compris les variantes de gestionnaire et les pages secondaires ;
2. lecture périodique LCD ;
3. opérations Korg synchrones qui dessinent puis appellent elles-mêmes le LCD ;
4. démarrage exclusif ;
5. erreurs, encore sans solution sûre démontrée.

Le triple buffer privé R12 est inclus tel quel par le nouveau banc. Il ne remplace pas la protection de C031B310. Aucun fichier R1–R12, V30, IFX ou VSB n'est volontairement modifié. La sauvegarde distante ajoute seulement des chemins R13 au tree de R12.

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

Le nouveau coordinateur a les états IDLE, DRAW, READ, FAULT et CRITICAL. Son état C mesuré par les records initiaux vaut32 octets, incluant le handle privé. Le pool R12 reste3112 octets. Ce sont des tailles du banc ARM, pas de la RAM instrument disponible.

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

## 5. Expériences observées avant interruption

| Cas | Expérience | Observation attendue et exigée par le runner |
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

## 8. Reprise reproductible obligatoire

    export PATH=/workspace/mercury-tools/bin:$PATH
    bash tests/run_recovery_r13.sh custom.VSB backup.VSB

Le lanceur retranscrit doit être relu/recompilé. Il réutilise les sources R1/R9/R12 et produit seulement des ELF Linux de laboratoire dans build/. Les deux SHA VSB exacts sont exigés avant/après. Rejouer R13 pour régénérer les preuves si le volume original ne revient pas ; ne pas refaire R1–R12.

Avant de conclure :
1. Récupérer si possible le volume initial et ses traces ; ne pas déclarer les données perdues définitivement.
2. Comparer les sources retranscrites à celles du volume s'il revient.
3. Exécuter le lanceur complet et le vérificateur indépendant.
4. Publier les véritables records/traces, JSON et provenance ; ne pas remplacer les archives manquantes par des données reconstruites.
5. Contrôler tous les chemins suivis par R12, puis créer un commit de finalisation distinct.
6. Conserver cette sauvegarde intermédiaire dans l'historique, sans force-push.

## 9. Proposition R14

Après finalisation de R13 : **R14, admission des domaines Korg exclusifs et récupération indépendante**.
- Attribuer les contextes C0031234/C0038D80 et les autres appelants de progression.
- Qualifier une entrée exclusive à partir d'une source complète et sans emprunt actif.
- Étudier l'encadrement par callbacks/objets RAM sans modifier les instructions natives, avec durées de vie et couverture explicites.
- Définir le traitement des services synchrones et diagnostics sans les faire passer pour achevés quand ils sont différés.
- Borner les vidanges UI et les demandes sans casser leur sémantique native.
- Établir une autorité de reprise hors LCD, ou maintenir NO GO avec frontière précise.

Mercury conserve ses images privées et peut préparer des copies cohérentes dans un banc qui contrôle tous les accès. Ce qui manque pour l'Electribe reste une protection commune de toutes les voies natives et un retour sûr quand le transport bloque. Cette mission demeure inachevée faute de sauvegarde des preuves et de vérification finale.
