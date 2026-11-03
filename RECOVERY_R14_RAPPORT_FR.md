# Mercury Dust — R14 : admission exclusive et frontière de récupération LCD

3 novembre2026. Branche exclusive `recovery/mercury-dust`, base validée **cb0d8caf9cb70d182f6e64ea7e72d8c796cd4e96**. RESEARCH_ONLY : aucun flash, firmware installable, modification de routine native ou intervention matérielle.

## 1. Résultat et décision

R14 fournit un protocole d'admission expérimental plus précis que R13 : propriétaire logique, ticket de domaine, image complète, fin de scan en huit pages, réservations CRITICAL et fermeture différée. Il conserve le triple buffer et le coordinateur existants. Les scénarios montrent la cohérence des acteurs **coopératifs et sérialisés**, le maintien des emprunts à l'erreur et les contournements natifs.

Deux routes jusque-là ouvertes sont attribuées au dispatcher de services en **tâche5** : services17 et34. Leurs appels à C004D860 passent un drapeau nul : ils ne déclenchent pas les appels de progression conditionnels identifiés dans ce service. Le démarrage passe au contraire le drapeau1. Cette précision réduit l'incertitude de la carte sans déclarer tout le service sans effet graphique.

**64 scénarios ARM** sur les deux VSB : **58 terminaisons normales, six fautes GPIO attendues**, 32 images V30 comparées par VSB, égalité exacte des records entre VSB. Le modèle abstrait explore **1180 états et2181 transitions**, avec40 arêtes de fin de scan et536 états de fermeture conservant une autorité active. Les transitions du modèle sont supposées atomiques ; cela n'est pas une preuve IRQ/multitâche.

**GO recherche logicielle sur l'admission par domaines. NO GO cohérence globale sur Electribe, récupération indépendante et intégration matérielle.** Aucun point extérieur unique n'est démontré couvrir tous les appels ; aucun mécanisme natif inspecté n'établit la chaîne détection→confinement→annulation→restauration.

## 2. Reprise et préservation

Les quatre documents demandés ont été lus intégralement : rapport R13, carte R13, architectures R13 et architecture triple buffer R12. Le manifeste R13 publié, soit **201 fichiers référencés**, est vérifié en lecture seule. R1–R13 ne sont pas rejouées ni réécrites. Le générateur artistique R1 inchangé fournit seulement les entrées des nouveaux essais R14.

Le vérificateur exige que **tous les chemins suivis par cb0d8ca restent identiques**, en plus de revalider les SHA R13. Cela couvre sources V30, pool R12, contrats, IFX et anciennes preuves. Les deux originaux sont lus, hashés avant/après les essais, jamais modifiés ni publiés :

| VSB original, chacun0x200100 octets | SHA-256 |
|---|---|
| user_custom (2).VSB | `81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03` |
| user_backup.VSB | `06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052` |

Les huit presets, douze paramètres, quatre mini-LFO au total et IFX sont conservés. Aucune recherche MD53/MD54 ni redéveloppement artistique n'est recommencé.

## 3. Nouvelles preuves natives et contextes

Voir la [carte actualisée](documents/RECOVERY_R14_GRAPHICS_CONTEXT_MAP_FR.md), l'[audit structuré](reports/recovery_r14/audit.json) et le [désassemblage compressé](reports/recovery_r14/native_disassembly.txt.gz). **20 plages** comparées identiques entre VSB. Les mots d'instructions déterminants sont explicitement vérifiés par l'auditeur.

### Route service17

C002A598, tâche5, appelle C002D844 après C000085C(4). Ce consommateur appelle C002D684, qui choisit un objet depuis C03404C8 et appelle des méthodes virtuelles. C002DB78 construit le service17 par C0030F3C ; l'objet est rangé à table+0x44 et installe C00A7608. Le slot+8 vaut C003128C. Après des opérations préalables réussies, C0031338 appelle C0031234. À C0031250, ce dernier appelle C004D860 avec r0=0 et r1=0.

### Route service34

C002DD10 construit le service34 par C00392A4 et le range à table+0x88. La table C00A7B58 a pour slot+8 C0038D80. Le chemin qui atteint C0038E40 conserve r7=0 depuis C0038E00 ; r0/r1 sont chargés depuis r7. La progression est donc également désactivée pour cet appel à C004D860. Le service24 voisin utilise C00A7AF8/C0038A54 : il ne doit pas être confondu avec34.

Une erreur d’indice dans la carte intermédiaire attribuait cette route au service35. La relecture des instructions de construction a établi **34** : r1=34 à C002DD08, appel à C002DD10 et stockage+0x88 à C002DD18. Ces mots sont désormais explicitement testés. Les [notes de validation](reports/recovery_r14/validation_notes.json) conservent cette correction ; aucun scénario ARM ni faute attendue n’en dépendait.

### Portée du drapeau

C004D864 conserve r1 en r7 ; les tests conditionnent les appels de progression C004D8B4, C004D928 et C004DCD0. Les deux appels C004D5CC reçoivent ce même drapeau en r2. C004D808..810 teste son exemplaire sauvegardé avant C004D81C ; une autre condition sur le signe s'applique aussi. Drapeau0 suffit à supprimer cet appel de progression identifié, sans prouver l'innocuité de tous les autres sous-appels.

Le démarrage C002AE8C charge r1=1 avant C002AE90. C006038C dessine directement la source puis demande LCD2 et LCD3 synchrones. C006040C configure un diviseur et y branche. Le getter C004D598 récupère un objet partagé ; il ne fournit aucune exclusion implicite.

**Confirmé statiquement** : routes configurées tâche5, tables/slots, paramètres et tests. **Non démontré dynamiquement** : exécution complète des services17/34, stockage, états et erreurs de tous leurs sous-services. Les appelants indirects supplémentaires restent possibles. La matrice garde les lecteurs/écrivains calculés et IRQ/FIQ/DMA dans les inconnus.

## 4. Protocole d'admission expérimental

Voir l'[architecture détaillée](documents/RECOVERY_R14_ADMISSION_ARCHITECTURE_FR.md) et [admission.h](tests/recovery_r14/admission.h).

- DRAW exige un domaine libre, sans suspicion/fermeture ni READ/CRITICAL prioritaire ; il retient un handle R12. COPY et fin contrôlent owner, ticket et génération du lecteur.1024 octets sont nécessaires pour terminer.
- READ mémorisé attend la fin de DRAW. Le scan coopératif garde le domaine pendant les huit comparaisons, et refuse un début de composition ou CRITICAL concurrent. Une page répétée/hors ordre ou une fin prématurée est refusée.
- CRITICAL exige une source complète et l'absence de lecteur/écrivain privé, en plus d'IDLE. Il réserve le domaine entier pour une opération native synchrone. La réentrée du même owner est aussi refusée.
- Une demande CRITICAL non admise ne fait **aucun appel natif**. Le bit d'intention n'est ni une file conservant tous les arguments ni un retour de succès à Korg. Une future adaptation doit encore prouver la sémantique de report/refus de chaque appelant.
- La fermeture rejette les nouvelles admissions, mais permet la fin réelle d'un domaine déjà admis. Elle ne détruit pas les ressources d'un worker bloqué.
- Une suspicion injectée conserve phase, owner, emprunts et blocage de fermeture. Elle interdit la réutilisation coopérative ; aucune annulation n'est fournie.

Le scan par comparateurs natifs **sans sender** est un test de cohérence mémoire. Le vrai worker est exercé séparément et atteint la faute GPIO sans retour. Le compteur de pages n'est pas installé à l'intérieur du worker : un wrapper extérieur de firmware ne pourrait pas supposer ces observations internes sans un autre contrat de fin et de couverture. Un simple retour natif peut aussi correspondre à un LCD inactif ou une image inchangée.

`critical_returned` est réservé à un **vrai retour** d'une opération dont la source complète est établie. Il ne détecte pas qu'un appelant aurait menti ou qu'un accès caché aurait eu lieu. Les API séquentielles ne rendent pas les métadonnées atomiques. L'admission n'est pas installée sur les services Korg et ne protège pas une routine qui ne la consulte pas.

### Coût et progression

Taille ARM mesurée : **64 octets** pour admission (gate R13 de32 octets inclus), soit **3176 octets avec le pool R12 de3112**, augmentation32 octets par rapport à gate R13+pool. Aucun emplacement RAM libre, marge de pile ou temps de copie physique n'est déduit. L'image privée reste1024 octets ; artiste→slot puis slot→source représente au moins2048 octets écrits, hors composition/comparaison/shadow.

Ticket et source_epoch épuisés refusent une nouvelle admission plutôt que de reboucler. Le heartbeat u32 n'est pas une horloge ; son wrap et les faux positifs restent des contraintes de détection. Aucune réinitialisation sûre de session n'est ajoutée.

READ demandé empêche un nouveau DRAW ; CRITICAL réservé empêche READ/DRAW. Cela limite la famine par nouvelles compositions dans le modèle, sans garantir l'équité. Des CRITICAL répétés, des READ continus ou une opération non retournante peuvent toujours empêcher d'autres progrès. La vidange UI native sans quota reste une longue transaction ; le contre-exemple R13 des32 callbacks est conservé, sans le rejouer.

## 5. Expériences ARM et résultats

Chaque cas est exécuté sur **les deux VSB**, avec code original chargé RX, cible ARM926EJ-S/ARMv5TE, freestanding -O2 et QEMU user-mode `-cpu arm926`. Aucun MMIO n'est mappé ni répondu. Les signaux Linux sont observés et terminent le processus, sans reprise Korg inventée.

| Cas | Observation requise / résultat |
|---:|---|
| 0 |32 images V30, copie384+640, READ refusé pendant DRAW, huit comparaisons puis images complètes conformes |
| 1 | CRITICAL réservé pendant DRAW refusé ; fin de composition puis admission, effacement natif1 exclusif et scan cohérent |
| 2 | Fin après64 octets refusée, emprunt retenu, puis fin complète |
| 3 | Mauvais owner/ticket et double fin refusés |
| 4 | Fin READ après une page, page répétée et page hors ordre refusées |
| 5 | Publication privée pendant READ permise, DRAW/CRITICAL refusés ; scan initial stable puis opération exclusive |
| 6 | Demande pendant READ conservée pour un second scan |
| 7 | Réentrées CRITICAL, DRAW et READ refusées ; retour de l'effacement natif puis scan |
| 8 | CRITICAL refusé avec emprunt privé ou écrivain privé ; admis après libération/abort |
| 9 | Fermeture pendant DRAW conserve l'emprunt et attend sa fin réelle |
| 10 | Fermeture pendant READ attend les huit pages |
| 11 | Fermeture pendant CRITICAL attend le vrai retour de l'effacement natif |
| 12 | Observation périmée ou heartbeat différent refusé ; suspicion injectée pendant DRAW conserve emprunt/owner |
| 13 | Worker réel sous READ : première page copiée puis faute01E260BC ; autorité READ conservée |
| 14 | Progression réelle sous CRITICAL : barre complète et shadow égale, puis même faute GPIO ; CRITICAL conservé |
| 15 | Comparateur direct contourne DRAW et copie384 nouveaux/640 anciens |
| 16 | Écrivain non participant entre pages3 et4 : scan mixte malgré compteur valide et READ terminé |
| 17 | CRITICAL sans retour conserve son owner ; nouvelle admission refusée |
| 18 | Source marquée incomplète à IDLE : READ/CRITICAL refusés |
| 19 | Ticket maximal : admissions refusées |
| 20 | Progression avec descripteur inactif : vrai retour, source modifiée, shadow ancienne ; aucune réception prouvée |
| 21 | Wrapper/queue/dispatcher/cycle UI alternatif natifs, widget fixture sous DRAW ; scan cohérent |
| 22 | Après refus CRITICAL pendant DRAW, appelant natif non participant continue : progression partielle puis faute GPIO |
| 23 | Arbitrage READ/CRITICAL empêche nouvelle composition ; traitement sans retour natif inventé |
| 24 | Suspicion et fermeture pendant READ : owner/pages conservés, ni fin ni destruction forcées |
| 25 | Suspicion et fermeture pendant CRITICAL : pas de retour fictif, owner conservé |
| 26 | Source_epoch maximal : refus conservateur sans wrap |
| 27 | Ancien ticket après une nouvelle admission : copie/fin refusées, nouveau handle intact |
| 28 | Expiration noyau native sur TCB fixture pendant READ : −50, prêt1, sélection/dispatch demandés, READ inchangé |
| 29 | Même expiration pendant CRITICAL : autorité conservée |
| 30 | Prise sémaphore native en contexte interdit : −25, ne libère ni ne termine READ |
| 31 | Sélection prête native : rang6 n'évince pas rang1 ; deuxième fixture rang0 sélectionnée ; READ reste actif |

Fautes attendues uniquement **13,14,22**, trois par VSB, soit six. Les autres58 terminaisons normales incluent des scénarios négatifs : leur sortie0 signifie que le contre-exemple attendu a été observé. Aucun échec d'attente inattendu n'a été constaté sur la validation finale. Aucune attente n'a été relâchée pour faire réussir un périphérique.

Le cas14 a une barre x9..64/y61..62,56 octets0x71 sur la dernière page ; son égalité shadow/source avant faute n'est pas une transmission validée. Le cas16 montre surtout que des métadonnées localement valides ne détectent pas un écrivain caché. Le cas22 montre qu'un refus de notre adaptateur n'empêche pas physiquement une routine native d'entrer.

## 6. Modèle, contre-exemples et vérification indépendante

Le modèle indépendant décrit des sources par huit étiquettes de génération, deux générations au maximum. Il explore demandes, DRAW en deux morceaux, READ page par page, opérations CRITICAL, fermeture et suspicion. Il exige une génération unique pour chaque scan terminé ; les emprunts restent détenus dans tout DRAW actif, y compris après fermeture/suspicion. Les1180 états/2181 transitions comprennent40 fins de scan vérifiées. Il suppose ses transitions sérialisées et le vrai retour complet des opérations natives abstraites.

Le [comparatif des rejeux](reports/recovery_r14/replay_comparison.json) vérifie les64 flux bruts identiques au précédent commit de preuves R14, ainsi que les lignes d’instructions natives identiques entre rejeux et entre VSB. Les fichiers de traces complets peuvent différer ; chaque version publiée reste dans l’historique.

Le modèle conserve explicitement les contre-exemples suivants : copie seule insuffisante ; écrivain non participant ; timeout coopératif situé après un appel non retournant ; suspicion erronée ; déverrouillage forcé suivi de reprise de l'ancien lecteur ; deux admissions qui lisent IDLE avant leurs stores faute de sérialisation. Ces scénarios restent des modèles, non des préemptions observées sur instrument.

Le vérificateur ne réutilise ni le parseur ni les attentes du runner et n'importe pas le protocole. Il reparcourt les records bruts, reconstruit les images d'oracle, contrôle séquence, phases, owner/ticket, pages, fermeture, emprunts/epochs, codes de sortie et fautes. Il vérifie les chemins natifs dans les traces, les effets noyau des cas28..31, les32 images de chaque VSB, l'égalité exacte entre VSB, le manifeste R13 et tous les anciens chemins suivis.

Les assertions compilées vérifient aussi les refus intermédiaires ; les snapshots ne prétendent pas enregistrer chaque instruction. Les traces `in_asm` montrent des blocs traduits, pas des occurrences ni des durées. Le TCB prêt/sélectionné des cas28..31 n'est jamais exécuté comme changement de contexte réel. Le dernier cas utilise deux fixtures de sélection indépendantes avec remise à zéro des listes avant la seconde insertion.

## 7. Récupération : conclusions strictes

Voir [frontière détaillée](reports/recovery_r14/RECOVERY_BOUNDARY_FR.md).

- **Détection** : C0015CDC boucle sur le statut SPI sans délai dans son corps ; le timer noyau dépend d'IRQ/dispatch et n'est pas un surveillant LCD acquis. L'observateur injecté n'est pas une preuve d'indépendance native. La priorité seule ne suffit pas.
- **Confinement** : les participants refusent les admissions après suspicion sans voler d'emprunt. Les accès non participants restent possibles.
- **Annulation** : aucune preuve d'arrêt de tous les accès du worker/callbacks/périphérique. Un résultat d'attente−50 ou un TCB prêt ne la fournit pas.
- **Restauration** : aucune voie sûre prouvée ; le diagnostic natif utilise lui-même le LCD et tente de masquer IRQ. Les sorties de tâche et boucles terminales ne sont pas des resets matériels démontrés.

Aucun watchdog n'est inventé ; l'absence globale de watchdog dans le firmware n'est pas conclue. NO GO reste requis tant que cette chaîne d'autorité est inconnue.

## 8. Reproduction et preuves publiées

```bash
export PATH=/workspace/mercury-tools/bin:$PATH
bash tests/run_recovery_r14.sh 'custom.VSB' 'backup.VSB'
python3 tools/recovery_r14/verify.py
```

Le premier appel construit et exécute uniquement R14, en deux groupes : cas0..27 et cas28..31. Le second relit les archives et utilise `build/recovery_r14/frames.bin` dont le hash doit correspondre à l'oracle R1. Dans un nouveau checkout, lancer d'abord le lanceur avec les deux originaux ; aucun binaire/VSB n'est livré.

- [Audit initial R13](reports/recovery_r14/phase1.json), [audit natif R14](reports/recovery_r14/audit.json), [journal audit](reports/recovery_r14/audit.log).
- [Résultats admission](reports/recovery_r14/results.json), [résultats récupération](reports/recovery_r14/results_recovery.json).
- [Journal ARM admission](reports/recovery_r14/validation.log), [journal récupération](reports/recovery_r14/recovery_validation.log), [journal lanceur](reports/recovery_r14/launcher_validation.log), [vérification indépendante](reports/recovery_r14/independent_verification.log).
- Records/traces compressés : `reports/recovery_r14/{0,1}_{0..31}.{records,trace}.gz` ; SHA-256 réels dans [provenance.json](reports/recovery_r14/provenance.json).
- [Modèles](reports/recovery_r14/models.json), [journal modèles](reports/recovery_r14/models.log), [environnement](reports/recovery_r14/execution_environment.json).

Records au format R9 de2112 octets :16 u32 puis1024 octets source et1024 shadow. h1=300+cas ; h2=étape. Étape0 mesure64/3112. Étapes1/20/89 : h3=phase, h4=owner<<24|complete<<20|suspect<<19|closing<<18|pending<<17|critical_pending<<16|pages<<12|written. Étapes101/120/189 : ticket puis reader<<24|writer<<20|pool_closing<<19|source_epoch<<8|prepared_epoch. Ce dernier emballage est diagnostique et ses champs epoch ne sont pas décodables séparément à toutes grandes valeurs ; le cas26 vérifie explicitement l'épuisement par assertion ARM. Étape10 compare les32 frames ;60/61 observent les statuts noyau ;90=adresse de faute/signal. Aucun champ n'est un accusé de réception LCD.

La provenance référence les sources, documents et archives avec leurs SHA. Les coûts mesurés ne sont pas des mesures de latence, pile ou marge RAM. ARM926/ARMv5TE, caches/MMU/write buffer, IRQ/FIQ/DMA et coexistence audio/IFX nécessitent des preuves distinctes.

## 9. Sauvegardes et périmètre

Les phases validées ont été publiées avant rédaction finale :

- `894af9860b3ff4e69f4696a095008101e709026e` : manifeste R13 vérifié sans rejeu.
- `115c9574a6fa9463a25a86d51ae626e8be469b91` : routes des services, audit natif et carte.
- `712c77b2bcd008ec3c19de11db1e40e00f29a674` : admission,56 expériences et premières preuves.
- `5353f5ba8785c367d85d1c4b1108774c4e0e8dd5` : huit cas complémentaires noyau et frontière de récupération.

Chaque tête distante a été vérifiée après push. Les versions intermédiaires restent dans l'historique ; les archives actuelles proviennent du lanceur final R14. Les archives historiques R13 ne sont jamais régénérées ni remplacées. Aucun force-push, changement de main ou intégration matériel.

## 10. Obstacles priorisés et proposition R15

1. **Couverture native** : qualifier un ensemble de frontières extérieures pour tous auteurs/lecteurs, services, modes UI, démarrage et diagnostic ; aucun dominateur unique prouvé.
2. **Admission native sérialisée** : identifier identités, primitives, mémoire et règles de refus/attente à chaque frontière. Ne pas attribuer au sémaphore une protection des fonctions non participantes.
3. **Progression** : qualifier durée/budget des transactions complètes et vidanges ; ne pas imposer un quota qui modifie silencieusement les commandes natives.
4. **Autorité indépendante** : démontrer contexte/horloge/observations malgré le worker bloqué, puis confinement et annulation avant toute réutilisation mémoire.
5. **Retour Korg et transport** : état connu après annulation et restauration sans dépendre du chemin LCD en panne ; réception physique toujours inconnue.

**R15 proposée, non commencée : contrats des frontières de dispatch et preuve de quiescence.** Étudier séparément les trois points C002D030, C002D684 et callback LCD, leurs objets/arguments et tous leurs contournements. Construire un modèle de conservation de commandes avec refus/reprise explicites, sans installer de hook. Rechercher une preuve native de cessation d'accès après arrêt contrôlé, ou conserver NO GO avec frontière documentée. N'autoriser aucune libération forcée ni essai matériel.

Mercury sait préparer et conserver des images, puis composer/scanner une génération cohérente dans un laboratoire qui maîtrise les accès. R14 précise quand une opération exclusive peut entrer et pourquoi un timeout ne libère pas ses ressources. Pour la vraie Electribe, il manque toujours une médiation couvrant les voies Korg, une synchronisation native qualifiée et une récupération qui fonctionne lorsque le LCD ne répond plus.
