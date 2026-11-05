# MERCURY DUST — R20

## Admission des destructeurs d'abonnés et autorité de retrait des sujets partagés

5 novembre 2026. Branche exclusive : `recovery/mercury-dust`.
Base demandée : `dce3fdc74b8dd0a0168f8ae920375fab52c6b31a`.
Reprise de la phase1 déjà publiée : `a220be8a5ac338f5bf8af79d838a8e8e05127fca`,
dont le parent direct est cette base. Aucun historique n'a été réécrit.

## Décision

**GO pour la recherche de laboratoire sur un domaine entièrement participant ou
une quarantaine bornée. NO GO pour l'intégration matérielle, la destruction
globale des objets natifs, le flash et la récupération indépendante du LCD.**
La primitive native commune de synchronisation reste **NON PROUVÉE**.

R20 est conclue comme recherche logicielle bornée. Elle ne résout pas toutes les
durées de vie Korg. Elle apporte une chaîne native concrète, des contrôles avant
libération, un modèle vérifié indépendamment et un bilan de faisabilité qui
recommande de réduire le graphe d'intégration plutôt que de supposer sa maîtrise.

**48 expériences ARM sur les deux VSB** : 32 retours normaux, huit sorties
contrôlées avant free, six fautes attendues et deux timeouts hôte. Les24 paires
d'enregistrements et de listes de blocs natifs traduits sont identiques. Les
15411 états du modèle sont réexplorés par un interpréteur indépendant. Aucun
free natif n'est exécuté dans ces expériences R20.

## 1. Reprise, conservation et périmètre

Le rapport R19 a été lu intégralement, les architectures R16–R19 consultées et
les conclusions historiques nécessaires au bilan R1–R20 examinées. Le
vérificateur R19 et ses150 empreintes passent sur les archives existantes, sans
rejouer les expériences ARM antérieures. Le contrôle R19 couvre aussi ses154 SHA
R18. Les2420 fichiers présents au commit de phase1 restent identiques, y compris
l'ensemble R1–R19 et les sept fichiers du premier audit R20.

Le volume initial était sur `work`, à la fusion R1. La tête distante a été
consultée par le connecteur GitHub, puis récupérée et placée sur la branche
demandée. L'échec initial d'accès au proxy du terminal confiné a été résolu par
l'accès réseau autorisé ; aucun contournement du proxy n'a été effectué.

Sauvegardes intermédiaires publiées et têtes distantes vérifiées :

- `950dc5ba8829bbed73a1a0f64ae5770347755f39` : seconde inscription native,
  graphe complété et vérification des archives conservées.
- `7ef1a1b` : expériences ARM validées, modèle, vérificateur et architectures.

Les sources V30, huit presets, douze paramètres et quatre mini-LFO au total,
les IFX et le triple buffer restent inchangés. R20 ne redessine pas de nouvelles
images V30 et ne revendique pas une mesure audio/IFX. Les VSB restent lus seuls,
hashés avant/après, non publiés. Les binaires de `build/` sont exclusivement des
ELF Linux/QEMU et des enveloppes de désassemblage, jamais un firmware installable.

## 2. Destructeurs et références natives

La [carte native complétée](documents/RECOVERY_R20_NATIVE_GRAPH_FR.md) et les
cartes de phase1 distinguent les faits locaux et les droits encore inconnus.

| Élément | Fait établi | Obligation restante |
|---|---|---|
| `C00852B0` | Constructeur d'un objet alloué76 octets au site `C0065298` ; clé inline+0x38 | Ses dépendances globales et son allocation profonde ne sont pas toutes qualifiées |
| `C0085078` | Accède à l'objet entier ; si +0x48 actif, inverse bit0 de +0x49 et marque +0x14 | Aucun test de fermeture ou de vtable |
| `C00851B4` | Modifie les vtables et appelle l'inverse sur objet+0x38 | « Non supprimant » ne veut pas dire sans free |
| `C0041B74` | Retire les sujets de la liste inverse par `C00705DC` | Tente ensuite free du vecteur à `C0041BB4`, sans join des callbacks |
| `C00705DC` | Efface la première entrée ayant la clé | Ne supprime ni une méthode déjà chargée ni une copie de fermeture |
| `C007061C` | Charge clé, contexte, méthode et ajustement, puis invoque | Le tuple doit rester stable pendant toute la résolution |
| `C00851F4` | Appelle le corps puis tente free extérieur à `C0085204` | Retour du corps insuffisant pour prouver le dernier accès |
| `C00851EC` / `C0085210` | Ajustement du this secondaire de−0x38 | Conserver le sous-objet impose de conserver l'allocation entière |

Les arrêts avant free concernent deux ressources différentes : le tableau
inverse et l'abonné extérieur. Les registres arrêtés donnent bien le pointeur
vers le stockage permanent de fixture, confirmé par les records. Le constructeur
ou destructeur suspendu n'est ensuite pas repris dans les sorties contrôlées.

Le cas de méthode déjà résolue démontre une écriture **après le retour du
destructeur non supprimant**, sur l'objet statique conservé. Il ne provoque aucun
use-after-free. Le changement de vtable ne peut pas annuler cette méthode directe.

### Deux inscriptions, trois racines à distinguer

Le constructeur abonné inscrit la même clé et le même this sur :

1. `*C0691244` : méthode `C0085078`, ajustement0, période10.
2. `(*C03405BC)+4` : méthode `C0085278`, ajustement0, période0.

La deuxième relation n'est pas `C0348844`, racine de l'objet UI associé étudié en
R19. Son callback relit le modèle global et peut modifier +0x48/+0x14 de l'abonné.
Il est exécuté dans le cas21. Limiter la preuve au périodique ou aux deux racines
UI omettrait donc une dépendance réelle du propriétaire choisi pour R20.

## 3. Autorité sur les sujets partagés

| Relation / droit | Statut R20 |
|---|---|
| Copie des racines UI vers état+0x24/+0x2C | PROUVÉ localement par R19 et audit conservé |
| Création paresseuse904/1064 et plusieurs chemins d'accès | PROUVÉ statiquement dans les corps inspectés |
| Racine modèle `C03405BC`, objet788, sujet intégré+4 | PROUVÉ localement ; constructeur/getter exécutés sur fixture précréée |
| Publication/remplacement des deux racines UI | PARTIEL : effets candidats de fenêtres linéaires |
| Propriété de la clé intégrée et nettoyage inverse par l'abonné | PROUVÉ localement |
| Autorité de cet abonné pour détruire ses sujets | INCONNUE ; aucune déduction depuis la relation inverse |
| Absence de tout alias calculé, cadre suspendu ou accès indirect | INCONNUE |
| Dernier propriétaire des trois racines | INCONNU |
| Primitive commune / ordre mémoire / IRQ-FIQ-DMA | NON PROUVÉ |

L'audit de phase1 conserve32 lectures,16 écritures candidates et cinq
publications d'alias candidates. Il suppose la conservation ABI de certains
registres et ne résout pas la faisabilité des branches : ce n'est pas une preuve
exhaustive d'absence d'autres écritures. Les pointeurs de vtable et branches
directes sont des candidats, pas un inventaire de tous les appelants calculés.

Le départ d'une page n'établit ni destruction des racines ni fin des autres
emprunts. Le corps de base d'état est exécuté et conserve ses deux alias ; cela
ne prouve pas leur immortalité. Une capacité native de free ne prouve aucun droit
du dernier propriétaire. **Aucune libération des sujets partagés n'est admise.**

## 4. Architectures expérimentales et contrats

La [comparaison détaillée](documents/RECOVERY_R20_ARCHITECTURES_FR.md) décrit le
prototype spécialisé, son inventaire et ses limites.

**A — Coordination complète.** Réservation avant construction, vraie fin avant
libération de l'obligation, acquisition du cadre avant sélection, conservation
jusqu'au retour du parcours, fermeture sans attente de son propre callback,
destructeur différé. Après drainage local, la fixture retire ses deux relations,
détache son inverse permanent puis appelle le corps natif avec inverse nul. Ce
corps peut revenir sans free ; cela ne devient jamais une autorisation de free
extérieur. L'inventaire refuse la relation supplémentaire du modèle+4.

**B — Quarantaine.** Aucun destructeur ni retrait physique ; objets, slots,
vecteurs et adresses restent conservés. Un thunk de fixture refuse le nouveau
travail fermé. Les callbacks Korg bruts ne possèdent pas ce thunk : la conservation
seule n'arrête pas leurs écritures. Quatre propriétaires sont disponibles ; le
cinquième est refusé, sans recyclage ni croissance prétendument illimitée.

Toutes ces transitions exigent une sérialisation extérieure. Les intercalations
GDB représentent une expérience contrôlée, pas l'ordonnancement natif. Aucun
verrou n'est maintenu pendant une notification ou un LCD. Un callback bloqué
conserve ses obligations ; le protocole privilégie le maintien du stockage et
peut perdre sa vivacité. Compteur local nul, timeout et changement de page ne
donnent aucun droit de destruction réelle.

## 5. Expériences ARM/QEMU sur les deux VSB

Chaque cas est exécuté une fois par VSB. Les objets, sujets et inverses sont
conservés jusqu'à la fin du processus Linux. Le domaine nominal contient deux
sujets périodiques904 de fixture ; le second ne représente pas l'objet UI1064.
Le cas21 utilise séparément le véritable modèle788 et son sujet+4.

| Cas | Expérience | Résultat |
|---:|---|---|
|0|Inscription à clé inline, callback natif, fermeture|Deux liens retirés après retour ; corps inverse nul revenu ; aucun free|
|1|Fermeture avant écriture du tuple|Destructeur et notification refusés pendant construction|
|2|Fermeture après actif, avant inverse|Même refus ; construction et inverse terminent avant nettoyage|
|3|Inverse présent, constructeur pas encore revenu|Obligation constructeur conservée|
|4|Callback natif déjà résolu dans parcours participant|Destructeur différé jusqu'au retour ; le callback accepté peut encore écrire|
|5|Même callback hors domaine participant|Corps destructeur revenu ; méthode déjà chargée écrit encore|
|6|Destructeur réel, deux sujets inverses|Deux retraits natifs effectués, arrêt avant free du vecteur|
|7|Variante supprimante avec inverse nul|Corps revenu, arrêt avant free extérieur76|
|8|Notification pendant destructeur non participant|Callback natif écrit après changement de vtable ; arrêt avant free du vecteur|
|9|Notification pendant destructeur participant|Admission refusée avant appel natif|
|10|Deux propriétaires, deux sujets|Retirer le premier conserve les relations et le travail du second|
|11|Réentrée et fermeture intérieure|Deux parcours/callbacks distincts ; aucun destructeur avant les deux retours|
|12|Demande de changement de page dans callback|Construction refusée pendant parcours, rejouée après retour ; ancienne génération conservée|
|13|Callback de fixture sans retour|Timeout hôte ; parcours/callback/relations toujours retenus au dernier snapshot|
|14|Fermeture puis worker LCD|Faute GPIO `0x01E260BC` ; obligations conservées|
|15|Quarantaine quatre propriétaires|Cinquième refusé ; quatre appels anciens atteignent le thunk et refusent le travail|
|16|Copie brute de fermeture après drainage local|Callback natif écrit malgré compteurs locaux nuls et retour du corps destructeur|
|17|Clé hors inventaire|Préflight refuse le destructeur, aucune suppression attribuée à cette clé|
|18|Deux états partageant les racines|Destructeur de base d'état conserve les alias ; aucun droit de free partagé|
|19|Trois cadres et ticket maximal|Quatrième refusé ; double fin refusée ; pas de rebouclage|
|20|Ancienne copie vers thunk en quarantaine|Adresse conservée ; travail refusé après fermeture|
|21|Constructeur complet et deux inscriptions réelles|Retour sous capacité inverse de fixture préprovisionnée ; second callback exécuté ; domaine à deux sujets refuse sa destruction ; chaîne native arrêtée avant free|
|22|Même constructeur sans préprovisionnement|Faute heap `C06A293C`, slot publié et constructeur encore retenu|
|23|Destructeur hors domaine entre chargements|Tuple effacé pendant résolution ; faute attendue à zéro, stockage conservé|

Le constructeur21 remet initialement l'inverse à zéro. Le debugger appelle une
fonction de fixture avant son premier appel d'inscription ; elle fournit une
capacité statique. Aucun allocator n'est remplacé, aucune allocation réussie
n'est simulée et aucune instruction Korg n'est modifiée. Ce cas valide le chemin
sur des ressources explicitement fournies, pas le heap natif général. Le
contrôle22 conserve précisément cette limite.

Les corps destructeurs des scénarios négatifs sont parfois appelés hors du
protocole pour observer leurs effets locaux ; ils n'obtiennent aucune permission
de free. Les objets ne sont jamais libérés ou réutilisés. Une garde GDB à l'entrée
`C0028DD4` reste installée dans **tous** les cas ; les sorties contrôlées
s'arrêtent en amont de cette entrée, sur les instructions d'appel de free.

## 6. Modèle et vérification indépendante

Le modèle sépare réservation, tuple, publication, inverse et vrai retour ; puis
sélection, résolution, entrée, retour callback et libération du cadre ; enfin
admission, retrait et retour du corps destructeur. Deux propriétaires et deux
parcours à usage unique, aucun réemploi. Une permission FREE n'est qu'une
transition symbolique d'une politique négative.

| Politique | États | Résultat |
|---|---:|---|
|Coordination complète|1361|Aucune violation sous hypothèses|
|Quarantaine avec thunk stable|1082|Aucune violation sous hypothèses|
|Comptage à l'entrée seulement|4175|Tuple déchiré et accès après retour destructeur|
|Un parcours externe omis|2569|Calme local insuffisant|
|Retour du corps pris comme certificat|6224|Permission de free avec référence encore vivante|

Total15411 états et39530 transitions. L'interpréteur indépendant ne charge pas
les transitions du générateur : il réexplore les cinq politiques et rejoue tous
les témoins négatifs. Cela ne couvre pas tous les graphes Korg, les IRQ/FIQ/DMA,
l'ordre mémoire/cache, le heap réel ou l'arrêt LCD. Une conservation d'état lors
d'un callback sans retour n'est pas une preuve de progression.

Le vérificateur relit les records2112 octets, reconstruit les en-têtes et SHA
source/shadow, vérifie séquences, issues, compteurs, tableaux et frontières. Il
compare les24 paires brutes et les listes de blocs natifs. Il reconstruit aussi
les octets des plages statiques depuis le désassemblage, les compare aux SHA et
contrôle les mots contractuels. Il vérifie la garde avant free, les18
restaurations exactes de registres et les huit sorties où le cadre natif n'est
volontairement pas repris. Aucun paquet d'écriture mémoire GDB M/X n'est utilisé.

Les traces `in_asm` indiquent des **blocs traduits**, pas un journal exhaustif des
instructions exécutées. La garde d'entrée free, les registres de frontière et
les contrôles du banc complètent ces traces. Le contrôle intégral des2 Mio natifs
est émis à chaque fin ou juste avant la boucle du callback sans retour. Un
timeout hôte ne prouve aucune annulation native. Les PID et ports ne sont pas
des différences de comportement Korg.

## 7. Mémoire, synchronisation et limites matérielles

Le domaine R20 fait136 octets. Quatre abonnés76 plus gardes font336, leurs
vecteurs64, deux sujets904 font1808 et le modèle788 fait788. Sous-total de ces
structures distinctes : **3132 octets**, hors copies, états, source/shadow, piles
et instrumentation. La pile GDB8192 n'est pas un budget instrument. Aucune RAM
libre, marge de pile, durée CPU ou latence audio n'est déduite de ces nombres.

Les helpers CPSR masquent I sans qualifier F ; les sémaphores peuvent attendre
et commuter selon leur contexte. Aucun mécanisme commun ne domine ici tous les
constructeurs, parcours, destructeurs et initialisations. `volatile`, les
compteurs et GDB n'établissent pas l'ordre mémoire ou la visibilité ARM926.

La faute heap ne prouve ni OOM ni défaut de l'Electribe. La faute GPIO est une
frontière non mappée de Linux. La shadow éventuellement copiée ne confirme pas
une réception LCD. Détection, confinement, annulation, restauration restent
distincts et non qualifiés. Aucun watchdog ou mécanisme de récupération n'est
inventé ; aucun essai matériel n'est autorisé.

## 8. Bilan R1–R20 et R21

Le [bilan complet de faisabilité](documents/RECOVERY_R20_FAISABILITE_R1_R20_FR.md)
répond aux sept questions de la mission.

Le moteur visuel, les rendus et certaines chaînes UI sont fonctionnels en
laboratoire. Des contrats natifs locaux sont suffisamment compris pour les
tester. L'intégration complète reste bloquée par la couverture des accès,
la synchronisation partagée, les durées de vie réelles, les budgets et le LCD.
La coordination complète est cohérente pour un graphe fermé ; sa généralisation
au firmware n'est ni démontrée ni une stratégie d'intégration déjà réaliste.

Une architecture moins intrusive est préférable comme **hypothèse à éprouver** :
**R21 — « Voie Mercury persistante à empreinte fixe, sans nouvel abonnement
natif »**. Réutiliser V30, le triple buffer et le chemin de dessin étudié ;
réduire les objets dont il faut prouver la construction/destruction ; inventorier
les accès réellement nécessaires et mesurer coûts, réentrée, changement de page
et blocage. La source graphique fixe et le transfert LCD conservent leurs
obligations de preuve. R21 n'est pas commencée et ne reçoit aucun GO matériel.

## 9. Preuves, reproduction et corrections

Artefacts :

- `reports/recovery_r20/native-map.*` et les deux documents de phase1, conservés.
- `supplement.json` / `supplement.txt.gz` : neuf plages identiques et seconde relation.
- 48 archives de records,48 traces et48 captures stderr, `results.json`, `arm-run.log`.
- `model.json`, `model.log`, `independent-verification.log` et `provenance.json`.
- `tests/recovery_r20/`, `tools/recovery_r20/`, lanceur et trois nouveaux documents.

```sh
# Outils clang/LLD19 et QEMU10 disponibles dans PATH ; accès loopback nécessaire.
bash tests/run_recovery_r20.sh /chemin/custom.VSB /chemin/backup.VSB

# Vérification des archives publiées : Python et Git, sans VSB ni émulation.
python3 tools/recovery_r20/verify.py --manifest
```

Les empreintes des VSB attendues sont :

- custom : `81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03` ;
- backup : `06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052`.

Versions réellement utilisées : clang/LLD19.1.7, QEMU10.0.13. Le lanceur complet
audite, modélise, exécute, vérifie, scelle puis vérifie les empreintes. Un rejeu
remplace uniquement les nouvelles preuves R20 ; conserver leur commit avant de
le lancer. Le manifeste exclut son propre fichier et le journal du lanceur encore
en cours d'écriture ; Git conserve ce dernier. Les empreintes sont celles des
fichiers réels, sans prétention de signature indépendante antérieure.

Le lanceur complet final a effectivement réussi ; son journal est
`launcher-validation.log`. `replay-comparison.json` compare ce rejeu au commit
intermédiaire `7ef1a1b` : les48 records bruts,48 listes de blocs natifs et48 SHA
d'ELF de fixture correspondent. Les identifiants hôte présents dans les traces
complètes ne sont pas assimilés à une divergence native.

`development-first48.tar.gz` conserve une première version expérimentale, avec
ses sources et preuves : ce n'est pas la validation finale. Les renforcements de
préflight, la découverte du modèle+4, le passage à la taille native76 et la
correction du contexte LCD sont documentés dans `development-notes.txt`.
Le vérificateur a signalé la faute0xBC du contexte incomplet ; les getters natifs
ont été fournis, puis les48 essais intégralement rejoués. Les hypothèses erronées
du premier vérificateur sur le journal RSP abrégé et stderr ont été corrigées.
Les contre-exemples et les fautes attendues restent publiés comme tels.

## Résumé simple

Retirer un nom d'une liste n'empêche pas quelqu'un qui l'a déjà lu de s'en
servir. R20 montre ce cas avec un véritable callback Korg : même après retour du
destructeur, l'ancienne méthode peut encore modifier l'objet conservé.

En laboratoire, on peut attendre tous les accès connus ou conserver les objets.
Sur l'Electribe, il manque la preuve que tous les chemins suivent cette règle,
ainsi que les garanties mémoire, audio et LCD. **La recherche peut continuer ;
l'instrument reste NO GO.** R21 devrait réduire le nombre de références à gérer
avec une voie de rendu persistante, sans nouvel abonnement natif.
