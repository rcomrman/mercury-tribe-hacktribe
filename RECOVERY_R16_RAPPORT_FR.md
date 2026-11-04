# Mercury Dust — R16 : codecs typés, propriétaires et retrait des références

4 novembre2026. Branche exclusive `recovery/mercury-dust`. Base **65d776f53718a1dadbeea1998c01e3a9791475df**. RESEARCH_ONLY : aucun patch Korg, flash, firmware installable, changement de main, force-push ou essai matériel.

## 1. Résultat et décision

**GO recherche logicielle sur des codecs explicites et un graphe de références connu. NO GO raccordement natif général, cessation CPU globale, arrêt du transport LCD, destruction de ses ressources ou récupération indépendante.**

R16 qualifie un vrai payload pointé de taille connue : le contraste LCD lit **un octet**, copié dans son descripteur, sans retenir le pointeur dans ce corps. Une enveloppe de laboratoire possède cet octet et conserve un emprunt de cible jusqu'au résultat/ACK. Cela n'autorise pas un report transparent des appels synchrones Korg.

La découverte principale concerne les observateurs natifs : **clé d'inscription et contexte `this` du callback sont deux pointeurs distincts**. Une réinscription avec la même clé ne remplace pas l'ancien contexte. Le retrait efface le slot du sujet, mais conserve les pointeurs du vecteur inverse et ne termine pas le callback déjà entré. Un registre ne suivant que la clé serait incomplet.

Le nouveau registre distingue objets, générations, propriétaires, producteurs et fiches individuelles d'emprunts. Il refuse doubles retraits, mauvais détenteurs et anciens tokens après réemploi de fixture. Les références filles gardent le domaine vivant pendant une réentrée ou la fin d'une commande déjà retenue. Des alias non participants continuent néanmoins d'appeler un objet lorsque ce registre annonce un calme **local**.

Validation finale : **68 scénarios ARM**,34 par VSB ; **62 sorties normales et six fautes GPIO attendues**, records et lignes d'instructions natives identiques entre VSB. Le modèle borné explore **2448 états et6890 transitions**, dont76 états localement calmes et288 états conservant un callback bloqué. L'audit compare **20 plages originales identiques** et vérifie les instructions contractuelles. Les échecs initiaux sont archivés séparément.

## 2. Reprise et préservation

Le rapport R15 et ses trois documents de dispatch/conservation/cessation ont été lus intégralement. Les sources/audits R12–R14 utiles ont été consultés ; les expériences antérieures ne sont pas relancées. Les **145 entrées SHA du manifeste R15** sont vérifiées en lecture seule, puis le vérificateur exige que **tous les chemins suivis par la base65d776f restent identiques**.

Les bancs R9/R12–R15 sont réutilisés par inclusion sans modifier leurs sources ou preuves. V30, huit presets, douze paramètres, quatre mini-LFO au total, IFX et triple buffer restent intacts. R16 ne revendique aucun nouveau rendu V30 : ses images et preuves antérieures sont préservées, sans rejeu inutile.

Les deux VSB originaux de0x200100 octets sont hashés avant/après les nouvelles exécutions, jamais modifiés ni publiés :

| Original | SHA-256 |
|---|---|
| user_custom (2).VSB | `81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03` |
| user_backup.VSB | `06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052` |

Le moteur artistique et les objets natifs n'ont pas été remplacés par des simulacres de périphériques. Les objets/callbacks de laboratoire sont nommés comme fixtures ; aucune instruction originale n'est patchée.

## 3. Codecs natifs retenus

[Carte complète par famille](documents/RECOVERY_R16_NATIVE_CODECS_FR.md).

| Famille | Contrat natif démontré / propriétaire et sortie | Décision de report |
|---|---|---|
| LCD2 via C0015DD0 | Descripteur C031BB2C natif partagé ; aucun payload ; active1 pose octet+5. Retour0 également inactif | Codec d'intention explicite, pas une transmission ni un instantané de framebuffer ; fusion/report non transparents par défaut |
| LCD4 via C0015DD0→C0015F44 | Entrée pointée1 octet possédée par l'appelant jusqu'à lecture ; `LDRB` à C0015F5C, valeur stockée desc+8 et flag+0xC. Aucun pointeur retenu dans ce corps ni sortie dans l'entrée | Capture propriétaire d'un octet pour une nouvelle API Mercury explicite ; **NON REPORTABLE TRANSPARENT** si l'appelant exige l'effet immédiat dans le descripteur |
| UI type0 via C0070AF0/C0083FE8 | Message16 octets, type+deux mots nuls ici ; queue/manager restent natifs, pas d'ACK fiable d'exécution | Codec UI0 seulement, pas messages8/16 ni payloads à pointeurs génériques ; intention différable uniquement avec contrat nouveau |
| Observateur C0070778 | Sujet, clé, champ r2 et fermeture3 mots/12 octets ; copie de contexte/méthode/ajustement, pas de propriété des objets ; écrit slot et vecteur inverse | **NON REPORTABLE GÉNÉRIQUE** sans durée de vie de clé, contexte, sujet et méthode/vtable ; aucune convention de retour succès exploitable établie |
| Progression C006040C/C006038C | Objet16 octets, écrit champs+4/+8/+C, dessine puis appelle LCD2/LCD3 synchrones ; objet natif partagé via getter C004D598/C0366D5C | **NON REPORTABLE** dans le périmètre : effets immédiats et continuation native, aucun futur résultat/refus compatible démontré |
| Services17/34 via C002D684 | Deux mots pouvant être des pointeurs, objets/handles temporaires sur pile et nettoyage au retour | **NON REPORTABLE GÉNÉRIQUE** ; tailles/propriétaires des pointees complets toujours ouverts |

La portée connue du descripteur LCD comprend32 octets utilisés par les chemins déjà étudiés ; ce n'est pas une preuve de toute extension/alias de classe. Le publisher UI lit notamment manager+0xC et octet+0x70 ; les gestionnaires/pages/enfants ne sont pas des objets propriétaires de Mercury.

Les résultats LCD0 actif/inactif sont ambigus : un vrai retour0 du dispatcher ne confirme ni consommation par le worker ni réception physique. Au cas3, le setter inactif revient0 sans modifier valeur128/flag0. Au cas0, l'octet initial42 est conservé malgré sa mutation à7 après capture ; le cas1 montre qu'un pointeur superficiellement conservé lit au contraire7. Le cas4 place l'entrée de capture en dernier octet d'une page ; la lecture native ultérieure utilise l'enveloppe. La lecture native d'un seul octet est aussi confirmée par ses instructions, sans prétendre que tout pointeur natif est ainsi reportable.

Les codecs supposent un contrat de conversation nouveau et explicite. Aucun WAIT ou succès différé n'est retourné à la place d'une fonction synchrone native. L'enveloppe ne peut pas rendre le descripteur ou les objets Korg propriétaires de Mercury.

## 4. Références natives nouvellement cartographiées

[Carte des détenteurs et sites natifs](documents/RECOVERY_R16_CPU_REFERENCE_MAP_FR.md), [audit](reports/recovery_r16/audit.json), [désassemblage compressé](reports/recovery_r16/native_disassembly.txt.gz).

### Inscription, notification, retrait

- **C0070778** parcourt32 entrées de24 octets à partir de sujet+4. Elle cherche d'abord la clé, puis un slot inactif ; elle ajoute aussi le sujet au vecteur de la clé situé à+4/+8/+C. Une croissance peut dépendre de l'allocateur ; le banc fournit une capacité suffisante et n'exerce pas cette allocation.
- La clé occupe entrée+0 ; `this` est entrée+4 ; mots méthode/ajustement à+8/+C ; r2 est stocké à+0x10, sémantique complète non qualifiée ; flag actif à+0x14. Le sujet de fixture réserve772 octets pour ce chemin.
- **C0070688** parcourt les slots actifs et appelle **C007061C**. Cette dernière charge le contexte depuis+4 et utilise une représentation de méthode pouvant ajuster `this`/charger une entrée virtuelle. Seule la forme directe à ajustement0 est testée R16.
- **C00705DC** efface le premier slot de clé égale puis retourne ; elle ne retire pas son pointeur du vecteur inverse de la clé.
- **C0041B74** parcourt le vecteur inverse, demande le retrait dans chaque sujet puis libère le stockage du vecteur. Cette destruction n'est pas un join de tous les callbacks ni une recherche globale d'alias ; son exécution complète avec les vrais allocateurs/services n'est pas revendiquée.

### Deux propriétaires potentiels, pas un seul pointeur

Le cas32 enregistre une cléA mais un contexteB ; le callback natif reçoit réellement B. Retenir la clé ne retient donc pas automatiquement le contexte. Un contexte ajusté de sous-objet ou sa table virtuelle exige encore un contrat de taille et de propriétaire ; la copie des trois mots de fermeture ne copie pas cet objet.

Le cas33 tente de réinscrire la même clé avec un autre contexte/méthode. Le corps natif revient sur la clé déjà trouvée et le callback conserve l'ancien contexte. Son propriétaire doit donc continuer à le faire vivre : l'appel de registration n'est pas un remplacement atomique prouvé.

Le cas22 retire puis réinscrit : un slot actif pour la clé, mais deux pointeurs de sujet dans le vecteur inverse. Ce sont deux relations différentes. Le sujet doit rester vivant tant qu'un nettoyage peut encore le déréférencer depuis ce vecteur. Un registre de références entrantes vers la clé ne couvre pas cette dépendance sortante vers les sujets.

### Autres détenteurs conservés dans la carte

Queues/messages et handles de services, racines globales UI, wrapper+4, vecteurs de pages/enfants, compteurs/callbacks LCD, cadres de pile et appels réentrants restent des détenteurs distincts. Les sites d'append C00614FC, de remplacement de page C006E9A0, de suppression C006EFD0 et les parcours/destructeurs graphiques sont audités statiquement. Les transitions de page complètes avec fabrique/allocateur ne sont pas rejouées R16 : les tests changent des cibles de fixture, en conservant les preuves antérieures R8/R15.

## 5. Registre expérimental et fermeture

[Architecture](documents/RECOVERY_R16_RETIREMENT_ARCHITECTURE_FR.md), [registre C](tests/recovery_r16/registry.h).

Le registre contient deux objets et huit fiches individuelles. Chaque fiche donne objet/génération/détenteur/type/numéro unique. Un token doit correspondre à une fiche vivante et à la génération courante. Les catégories distinguent file, wrapper, service, callback, page et continuation ; les identités sont logiques, pas authentifiées par le noyau Korg.

LIVE autorise les acquisitions de producteurs connus ; RETIRING ferme ces nouvelles acquisitions. Les anciens emprunts restent détenus et peuvent engendrer un emprunt fils pour finir une commande déjà acceptée. Un retrait du parent ne libère pas les fils ; chaque cadre réentrant a son propre token. Un mauvais détenteur, un double retrait ou un token ancien après génération/série nouvelle sont refusés.

`local_quiet` signifie uniquement : objet RETIRING, producteurs **recensés** détachés et aucune fiche vivante. Il ne libère rien. Le réemploi de fixture est limité aux métadonnées d'objets CPU privés encore alloués ; la classe native LCD interdit ce réemploi, sans fournir pour autant une annulation physique.

Le cas6 couple un octet possédé et sa cible avec R15/R14 : commande conservée pendant READ, admission CRITICAL après les huit comparaisons, vrai appel natif, résultat DONE, cible encore retenue jusqu'à ACK. Les trois enveloppes réservées ne constituent pas une preuve de multiplexage complet de tous les services/objets natifs.

### Fenêtre non résolue avant entrée du callback

Pour certifier la cessation, l'emprunt doit couvrir le moment où le producteur **charge/résout** le pointeur natif, pas seulement l'entrée du callback. Si le contexte/méthode est déjà chargé alors que le retrait libère la référence d'inscription, un comptage à l'entrée peut arriver trop tard. R16 n'installe pas cette acquisition dans C0070688/C007061C ; la sérialisation et un éventuel join restent à prouver. Le callback de fixture instrumenté ne résout pas cette fenêtre native sous IRQ/préemption.

Les alias bruts des cas15/16 et l'inscription native volontairement omise du cas29 continuent à appeler la cible malgré un calme local. Le changement de génération protège les tokens, mais pas un pointeur brut vers la même adresse. Aucun objet réellement libéré n'est réutilisé dans ces contrôles négatifs.

## 6. Arrêt CPU, périphérique et destruction

[Étapes et certificats manquants](reports/recovery_r16/closure_certificates.json).

| Étape | Preuve R16 | Limite |
|---|---|---|
| Arrêt des nouvelles admissions | Registre RETIRING refuse Acquire externe | Pas installé sur les producteurs Korg |
| Vidange/ACK | Report d'un contraste et refus de cible périmée avant effets | Pas une continuation native générique |
| Fin des callbacks | Réentrée et retrait pendant notification, fiches filles conservées | Pas de join de tous les cadres/alias natifs |
| Retrait d'observateur | Slot natif effacé ; deuxième notification ne rappelle plus cette entrée | Callback déjà entré et vecteur inverse subsistent |
| Absence d'alias cachés / CPU global | Contre-exemples de wrapper, même adresse, inscription omise et clé/contexte distincts | **Non démontrée** |
| Absence périphérique/DMA | Worker et contrôle7 gardent leurs frontières GPIO/SPI ; aucun MMIO simulé | **Non démontrée**, aucune autorité indépendante identifiée |
| Autorisation de destruction/restauration | Aucune autorisation réelle délivrée, aucun free forcé | **NO GO** |

Le contraste peut être copié dans le descripteur alors que le transport n'a pas commencé ou n'aboutit pas. Au cas24, son flag reste en attente quand le worker faute avant tout scan d'image ; les deux emprunts (commande et continuation CPU) restent conservés. Au cas26, la première page est copiée puis le sender faute. Le contrôle7 du cas31 accède au GPIO sans passer par le scan ; il n'est pas une annulation indépendante.

La boucle SPI C0015CDC, la configuration/commande LCD et les voies de diagnostic/arrêt antérieurement documentées ne fournissent pas un certificat de cessation périphérique. Aucun watchdog ou reset n'est inventé ; l'absence de tout mécanisme dans l'ensemble du firmware n'est pas conclue. Source=shadow, retrait d'un slot ou retour d'une fonction ne prouve pas l'absence de DMA/IRQ/FIQ ni la possibilité de restaurer Korg sans LCD.

## 7. Scénarios ARM finaux

Chaque scénario ci-dessous est exécuté sur les deux VSB. Les seuls codes88 attendus sont **24,26,31**, à01E260BC/signal11, soit six fautes. Les62 sorties normales incluent des contrôles négatifs validés.

| Cas | Résultat contrôlé |
|---:|---|
| 0 | Capture propriétaire42, octet appelant changé à7, setter lit42 ; voisins non écrits |
| 1 | Pointeur superficiel lit la valeur tardive7 |
| 2 | Codec demande2 : flag de demande, pas de transport ni réception |
| 3 | Setter inactif retourne0 sans effet contraste ; valeur128/flag0 conservés |
| 4 | Capture à la frontière de page, valeur255, lecture native de l'enveloppe |
| 5 | Message UI0 construit/copié nativement via publisher, queue de fixture |
| 6 | Contraste différé pendant READ, copie conservée, retour réel et emprunt jusqu'à ACK |
| 7 | Retraite interdit nouvelle acquisition ; emprunt existant bloque le calme local |
| 8 | Mauvais propriétaire, double release et double detach refusés |
| 9 | Fils de continuation pendant retraite ; retrait parent ne masque pas le fils |
| 10 | Notification native réentrante, deux cadres distincts ; extérieur encore retenu après intérieur |
| 11 | Cible de fixture changée, ancien emprunt conservé ; commande périmée refusée/ACK avant rebind |
| 12 | Cible ancienne retenue et invocation CPU explicite malgré changement du wrapper courant |
| 13 | Retrait natif + arrêt demandé pendant callback ; écriture ultérieure, fiche active conservée |
| 14 | Token périmé après réemploi de même adresse/génération nouvelle, nouvel emprunt intact |
| 15 | Alias wrapper omis : callback possible malgré calme local |
| 16 | ABA de pointeur brut : même adresse, nouvelle vtable ; token ancien refusé, raw alias appelle B |
| 17 | Huit fiches occupées, neuvième refusée ; aucun vol d'emprunt |
| 18 | Mauvais détenteur refusé, token correct libéré |
| 19 | Série maximale : refus sans wrap |
| 20 | Génération maximale : pas de réemploi |
| 21 | Registration native identique sans doublon ; retrait enlève le slot, pas le vecteur inverse |
| 22 | Retrait/réinscription : un slot actif, deux pointeurs inverse de sujet |
| 23 | Nouvelle acquisition externe refusée pendant retraite ; ancienne commande peut finir |
| 24 | Contraste copié puis worker fautif avant scan, deux références conservées |
| 25 | Progression native inactif LCD : configuration16 octets et barre immédiate dans source, shadow ancienne |
| 26 | Worker fautif après préparation de la première page, référence conservée |
| 27 | Refus de submit après fermeture : remboursement de la référence capturée, aucun faux appel natif |
| 28 | Publisher UI inactif : retour sans publication, pas d'ACK d'exécution |
| 29 | Inscription native omise du registre : callback après calme local annoncé |
| 30 | Double retrait natif idempotent sur slot ; double retrait de token refusé |
| 32 | CléA et contexteB : le callback reçoit B |
| 33 | Même clé réinscrite avec contexteB : ancien contexteA toujours appelé |
| 31 | Contrôle LCD7 après retraite locale : faute GPIO, pas d'annulation |

Les appels originaux sont chargés RX ; les registres, objets, tables virtuelles, vecteurs et capacités sont des fixtures. Le banc n'exécute pas un ordonnanceur Korg complet ni une chaîne IRQ matérielle. Il n'émule ni GPIO/SPI fonctionnel ni DMA. Le handler SIGSEGV Linux enregistre l'état et termine le processus, sans reprendre Korg.

## 8. Échecs conservés et correction démontrée

[Notes](reports/recovery_r16/validation_notes.json), [archive initiale](reports/recovery_r16/failures/observer_abi_initial.tar.gz), [diagnostic](reports/recovery_r16/failures/observer_abi_diagnostic.json).

La première compilation a exécuté les cas0..8 puis arrêté le build9 pour un token `child` potentiellement non initialisé sur le chemin d'un CHECK court-circuité. Les nouveaux tokens ont été explicitement initialisés ; aucune source antérieure n'a changé et l'avertissement n'a pas été désactivé. Les helpers statiques inutilisés des seules bibliothèques importées sont exclus du seul avertissement `-Wunused-function` par diagnostic push/pop ; les nouvelles sources restent `-Wall -Wextra -Werror`.

Le premier rejeu complet64 cas a ensuite produit **dix échecs d'assertion161**, cas10/13/21/22/29 sur les deux VSB, en plus des six fautes GPIO attendues. La fixture avait construit une fermeture `[1, méthode, 0]` en prenant son premier mot pour un booléen. Le diagnostic observe événement37 mais `this=1` ; l'instruction C007062C recharge entrée+4 dans r3, et C0070670 en dérive le pointeur reçu par le callback.

La correction est `[objA, méthode, 0]`. L'assertion **`p==objA && event==37` est conservée**, pas relâchée. Les deux nouveaux cas32/33 testent précisément la distinction clé/contexte et la non-mise-à-jour d'une fermeture existante. L'archive initiale contient sources, records, traces, résultats et journal ; le diagnostic conserve source et records propres avec leurs empreintes. Ces fichiers sont des preuves exploratoires **de R16**, pas des archives historiques retrouvées.

Le vérificateur relit aussi cette archive, exige les dix échecs161 exacts et les six fautes initiales, puis vérifie le diagnostic. Le lanceur final n'a plus d'échec d'assertion inattendu ; ses six fautes GPIO ne sont jamais converties en succès périphérique.

## 9. Modèle, coût et preuves reproductibles

Le modèle borné contient une commande à octet possédé, des fiches individuelles, deux générations, capacité2 et série bornée4. Il explore mutation de l'entrée appelante, changement de racine de page, acquisition, dérivation, retraite, retrait de producteur, vrai retour, ACK et blocage. Les2448 états/6890 transitions conservent la cible pendant commande/callback, vérifient qu'un retrait parent ne supprime pas un fils, et n'autorisent le réemploi CPU de métadonnées qu'après disparition des références connues.

Ce théorème suppose un **graphe fermé, des opérations atomiques et des Release après les vrais derniers accès**. Un alias omis, un retrait prématuré ou la fenêtre avant entrée du callback en casse les hypothèses. Le modèle ne prouve ni sérialisation ARM926, ni équité, ni arrêt périphérique. Les contre-exemples correspondants sont conservés dans models.json.

Coûts ARM observés : registre256 octets, token16, enveloppe24. Trois enveloppes72, file R15=128, admission R14+pool R12=3176 ; total de ces structures distinctes **3632 octets**. Les objets/capacités natives, listes inverses, closures supplémentaires, piles et diagnostics ne sont pas inclus. Aucune zone RAM disponible, marge de pile, durée physique ou coexistence audio/IFX n'est déduite.

```bash
export PATH=/workspace/mercury-tools/bin:$PATH
bash tests/run_recovery_r16.sh 'custom.VSB' 'backup.VSB'
python3 tools/recovery_r16/verify.py
```

Le lanceur compile les34 cas R16 pour chaque original, reconstruit audit/modèle puis vérifie. Le second appel relit les archives sans nécessiter les VSB ni relancer les missions antérieures. Clang/LLD19.1.7, ARM926EJ-S ARMv5TE modeARM -O2 freestanding et QEMU Linux user-mode ; [versions exactes](reports/recovery_r16/execution_environment.json).

Le vérificateur indépendant n'importe ni le runner ni les implémentations de registre/codec. Il reconstruit les oracles d'octets, champs du descripteur, générations, fiches restantes, séries, refus et états de file/ACK ; il exige les fautes exactes et les chemins d'instructions natifs. Les traces `in_asm` montrent des blocs traduits, pas toutes les occurrences ou un temps d'exécution.

- [Reprise R15](reports/recovery_r16/phase1.json), [audit natif](reports/recovery_r16/audit.json), [journal audit](reports/recovery_r16/audit.log).
- [Résultats ARM](reports/recovery_r16/results.json), [journal ARM](reports/recovery_r16/validation.log), [lanceur](reports/recovery_r16/launcher_validation.log), [vérification indépendante](reports/recovery_r16/independent_verification.log).
- Records/traces : `reports/recovery_r16/{0,1}_{0..33}.{records,trace}.gz`, [comparaison des rejeux](reports/recovery_r16/replay_comparison.json), [SHA/provenance](reports/recovery_r16/provenance.json).
- [Modèles](reports/recovery_r16/models.json), [journal modèles](reports/recovery_r16/models.log), [statut final](reports/recovery_r16/finalization.json).

Format R9 de2112 octets :16 u32 puis1024 source et1024 shadow. h1=500+cas ; h2=étape ; h5=séquence ; h6=garde0x39. Étape0 mesure registre/enveloppe ;50 mesure file/admission+pool ;1/20/89 donnent état objet0 et producteurs<<16|refs0 ;+100 générations ;+200 série puis compteurs file R15 ;+300 refus puis callbacks<<16|profondeur ;+400 calme local bit0/bit1 et producteurs/refs objet1.60 donne vrai retour/valeur,61 la réentrée,63 le faux calme,64 slot natif/vecteur inverse,65 delta `this−objA`/événement,66 contexteB/cléA,90 faute/signal. Les champs packés sont diagnostiques et limités aux bornes du banc.

Les68 flux finaux sont identiques au précédent commit de preuves corrigées, ainsi que leurs lignes d'instructions natives. Les échecs ABI initiaux restent séparés et ne sont jamais présentés comme le rejeu réussi.

## 10. Sauvegardes, limites prioritaires et proposition R17

Publications intermédiaires, avec tête distante vérifiée après chaque push :

- `b3fbfe0017da979d3d3809bcd0e263cbcb22e7d5` : reprise et manifeste R15.
- `cedba688935a94b3f12047894e37e80acd024f42` : codecs et audit natif.
- `15dfee09506e5eccd259a1dfa5c29bcd7079a28e` : registre,68 cas, échecs et correction ABI conservés.
- `6356568fc4bc31e802a1b9af6fa1b173c6752a99` : propriétaires clé/contexte et certificats de fermeture séparés.

**P0 :** fermer réellement le graphe clé/contexte/sujet/vecteurs/continuations et les racines UI/timer, avant tout certificat CPU. **P0 :** acquérir l'emprunt avant résolution native du pointeur et prouver la sérialisation/retraite. **P0 :** qualifier une autorité indépendante de cessation périphérique ou maintenir NO GO. **P1 :** définir les refus/continuations des appelants synchrones, coûts complets et progression ; aucune réinitialisation forcée des générations ou emprunts.

**R17 proposée, non commencée : fermeture des inscriptions et contextes d'observateurs.** Choisir un sous-graphe natif précis autour C0070778/C0070688/C00705DC ; inventorier séparément clé, `this`, méthode/ajustement, sujet et vecteur inverse. Étudier acquisition avant résolution et retrait avec callbacks déjà sélectionnés, en conservant le contrôle négatif d'alias et de contexte distinct. Définir un contrat d'ownership et de fermeture pour ce seul sous-ensemble, sans installer de hook. Continuer la recherche périphérique séparément ; aucune preuve CPU ne devra être promue en autorisation de destruction du LCD.

Mercury sait maintenant conserver un argument pointé de taille connue et suivre des emprunts individuels dans le banc. R16 montre aussi pourquoi retirer une inscription ne suffit pas : le callback peut déjà être en cours, son contexte peut être un autre objet et des alias peuvent rester. Pour avancer sur la vraie Electribe, il faut prouver la disparition de ces accès CPU puis, séparément, l'arrêt réel des accès matériels. Aucun flash ou essai matériel n'a été effectué.
