# MERCURY DUST — PASSATION INTÉGRALE POUR UNE NOUVELLE CONVERSATION
**État arrêté au 31 octobre 2026 — derniers développements : V29.4**

> **RÈGLE DE LECTURE :** « testé / validé » signifie *test sur ordinateur, audit statique ou simulation*, sauf si le texte précise explicitement un essai sur l'instrument. **Aucune version Mercury Dust n'a été flashée ni testée sur une véritable Electribe.** Ne pas inférer qu'un fichier installable existe.

## 0. Résumé exécutif

**But :** intégrer **Mercury Dust**, un visualiseur de musique procédural et monochrome, dans le firmware **Hacktribe d'une Korg Electribe 2 Sampler**, en utilisant l'écran 128 × 64 de l'appareil **sans ordinateur**. La référence artistique approuvée est **Mercury Dust V30 Groove corrigée** ; la V31 avait été rejetée comme trop différente. Les visuels doivent vivre et évoluer en temps réel, avec liquide/mercure, gouttes, cordes, particules, désintégration, glitch, ambiance musicale adaptable du lofi/jungle à la techno/acid agressive. Pas de GIF prédéfini ni de visuels en couleurs.

**Périmètre immédiat impératif :** garder **8 presets**, **12 paramètres globaux**, le menu Korg/visualiseur et les boutons **SHIFT+BPF ON/OFF**, **SHIFT+HPF réglages**, **EXIT retour Korg**. **Masquer seulement** les réglages par piste pour le premier portage, sans détruire leurs données ni supprimer les fonctionnalités futures. Mini-LFO : **gelés** ; quand repris, **quatre LFO au total**, pas quatre par piste. **Pas besoin de MIDI externe** pour la première démonstration : privilégier une horloge/rappel interne Korg. Ne pas réinventer les menus ou les scènes déjà créés.

**État réel :** renderer C ARM926EJ-S, UI, simulations de relais LCD, pages de framebuffer, restauration Korg, audits binaires et deux branches V29.4 ont été développés. **Pas de SYSTEM.VSB Mercury installable**, pas de mesure en RAM à l'exécution, pas de branchement de boutons validé physiquement, pas de preuve du contexte du rappel LCD ou de la coexistence avec audio/SPI. L'utilisateur possède une SD de Hacktribe et une copie de son firmware sur PC, **sans JTAG**. Une sauvegarde SD/PC ne garantit pas le débrickage.

## 1. Fichiers et entrée conseillée pour la nouvelle conversation

1. Lire ce document en entier, puis `01_PROMPT_A_COLLER.md` si nécessaire.
2. Ouvrir **`02_SOURCE_V29_4_CAVE_ET_RESTAURATION.zip`** : base du travail récent avec le nouvel emplacement mémoire et restauration Korg après timeout, 28/28 contrôles statiques par VSB.
3. Ouvrir **`03_SOURCE_V29_4_SENTINELLES_FAILSAFE.zip`** : branche distincte avec protection `md25_state_intact` et logique de désarmement supplémentaires, 26/26 contrôles. **Les deux branches ne sont pas encore fusionnées ni validées ensemble** ; ne pas attribuer les protections d'une branche à l'autre.
4. Lire `documents/historique/` pour le détail des versions et `documents/technique/` pour les rapports/constats du dernier état.
5. Préserver le fichier **`references/Mercury_Dust_V30_Groove_CORRIGE.html`** (SHA-256 ci-dessous) comme source graphique de vérité. L'autre HTML V14 est un jalon antérieur, pas un substitut à V30.
6. Si l'analyse des firmwares doit être reproduite, demander à l'utilisateur de joindre **ses deux `.VSB` originaux** séparément. **Ils ne sont volontairement pas inclus dans ce dossier** : ne jamais supposer leur présence ni modifier les originaux.

## 2. Cahier des charges artistique et fonctionnel

### Identité visuelle

- Direction artistique : **V30 Groove**, validée par l'utilisateur, à ne pas remplacer par V31 ni par une interprétation approximative du moteur ARM V21.
- Écran Korg LCD : **128 × 64 pixels, noir et blanc / 1 bit par pixel** ; **8 pages de 128 octets = 1 024 octets**.
- Visuels évolutifs en direct, mouvement organique, mercure, liquide, cordes, formes mouvantes, poussières et effondrement/glitch. Le kick devra à terme être visiblement marqué. Ambiances calmes aussi bien que très agressives.
- Huit presets actuellement nommés dans `src/mercury_menu.c` : **FLOW, SILK, HYPNOSE, ACID, HARD TEK, LOFI, JUNGLE, COLLAPSE**.
- Les versions PC de référence montrent le style souhaité, **mais les formes C/ARM n'en sont pas encore un portage pixel à pixel fidèle** : signalé dès V23 ; ne pas annoncer le rendu final artistique comme terminé.
- Les rythmes doivent idéalement suivre le **tempo interne** et des **divisions RATE** ; pas de contrôle BPM/VITESSE arbitraire dans l'UI cible.

### Contrôles à garder dès le premier firmware utilisable

Dans `mercury_keys.c` / `mercury_menu.c` :

| Page | Paramètres globaux conservés | Valeurs visibles |
|---|---|---|
| **AMBIANCE** | PRESET, INTENSITE, CORDES, REACTION | preset 0–7, intensité 0–100, cordes 1–8, réaction 0–100 |
| **MOUVEMENT** | RATE, FLUIDITE, ONDULATION, CHAOS | RATE : 1/1, 1/2, 1/4, 1/8, 1/16, 1/32 ; autres 0–100 |
| **GLITCH** | GLITCH, COULURE, PERTE DATA, IMAGE FIGEE | 0–100 chacun |
| **PISTES** | IMPACT, SENSIBILITE, CORDE, ROLE | Page **masquée en V28+**, valeurs 16 pistes préservées, à réactiver plus tard |

Le code de menus et les profils existent ; **il faudra vérifier pour chacun des 12 réglages que sa modification a bien un effet perceptible sur le renderer natif** (plusieurs ports graphiques étaient partiels dans les premières versions).

### Boutons et comportement attendu

- **SHIFT + BPF** : ON depuis l'écran Korg ; OFF depuis **n'importe quelle** vue Mercury, même réglages/LFO.
- **SHIFT + HPF** : ouvrir les réglages / faire défiler les trois pages globales.
- Dans SETTINGS : **BPF** active/quitte l'édition, **LPF/HPF** parcourent les lignes ou diminuent/augmentent les valeurs.
- **EXIT** : abandonner Mercury et restaurer l'écran Korg.
- En mode Korg/OFF, conserver l'usage normal des filtres et des boutons ; un appui capturé et son relâchement doivent appartenir au même gestionnaire (éviter touche Korg orpheline).
- **SHIFT + LPF** correspond historiquement à la future page LFO, mais **les mini-LFO sont gelés** pour l'intégration initiale.
- Les codes `SHIFT=0x0A`, `LPF=0x12`, `HPF=0x14`, `BPF=0x16` viennent d'analyses antérieures et **restent à confirmer physiquement** ; **EXIT n'a pas de code physique définitivement vérifié**.

### Exclusions temporaires explicites

Pas de réglages visuels par piste à intégrer pour l'instant, pas de quatre LFO × seize pistes, pas de nouvelle interface ni de nouveau moteur visuel, pas de MIDI externe comme détour, pas de modification des IFX déjà personnalisés de la Hacktribe, pas de changement du séquenceur, des samples ou du DSP.

## 3. Parcours des versions et réalisations

| Version / génération | Progrès concret | Limite importante |
|---|---|---|
| **V30 HTML initial / V14** | Direction visuelle, prototypes PC interactifs. V30 Groove corrigée choisie comme DA définitive ; V31 rejetée. | Démo HTML = pas une implémentation firmware. |
| **V13–V21** | Portage d'un moteur procédural en C, huit presets, pages monochromes, événements/notes simulés, menus, calcul ARM926EJ-S, boutons envisagés ; tests hôte. | Fidélité au HTML V30 incomplète, aucun hook matériel. |
| **V22** | Multiplexage LCD équitable entre 8 pages, gestion des transmissions échouées, menu LFO et moteur de 4 mini-LFO *au total* ; propriété appui/relâchement. | LFO simulés seulement ; dossier ensuite gelé. |
| **V23** | Analyse ARM précise du dispatcher LCD, comparateur source/shadow, copies de 128 octets, chemin d'affichage et boutons, recherches d'horloge/routage audio ; compilations/tests. | SPI réel, contexte tâche et horloge non vérifiés. |
| **V24** | Test bout-en-bout 64 frames simulées, service visuel `md24_visual_service`, limite 40 ms (~25 FPS), restauration de 1 024 octets Korg, 13/13 sites ARM audités par VSB. | Pas de VSB flashable ; pas de véritable task hook. |
| **V25** | `md25_visual_boot`: état ARM préalloué en `.data` (~7 352 octets), zéro `.bss`, garde-fous de preuve, timeout 250 ms ; candidat rappel LCD `0xC002A71C` ; 14/14 contrôles statiques par firmware. | Les preuves d'initialisation étaient fournies par le simulateur, pas établies par la machine. |
| **V26** | Dissection du moteur de rappels Korg `0xC002A7EC` / `0xC002A818` ; compteur **20 appels**, ne pas confondre avec 20 ms ; 37/37 vérifications statiques et 10/10 corruptions détectées selon rapport V26. | Cadence réelle et contexte encore inconnus. |
| **V27** | Outil MIDI USB en lecture seule Windows/navigateur pour tester notes, clock, START/STOP. | **Mis de côté volontairement** : le premier affichage n'a pas besoin de MIDI externe. |
| **V28** | `md_set_global_only` : conserve 8 presets et 12 réglages globaux, **masque seulement la page PISTES** ; tests hôte. | Premier `%` dynamique nécessitait division ARM externe ; corrigé V29.1. |
| **V29** | Candidat relais de callback via pointeur Korg au lieu de réécrire un driver SPI. | Simulation ; aucun pointeur modifié dans un VSB réel. |
| **V29.1** | ARM `md30_callback_bridge` -> `md30_callback_visit` -> callback Korg original `0xC002A71C`, retour registre préservé ; ARM link sans `__aeabi_uidivmod`, état OFF par défaut. | Pas encore branché à la comparaison des pixels. |
| **V29.2** | Relais `md31_compare_veneer` / `md31_compare_visit`, choix Mercury/Korg ; opcode 2 pour marquer LCD dirty, opcode 3 original pour rendre ; ON/OFF universel, EXIT et relâchements testés ; 11/11 audits. | Tous les boutons sont des événements décodés simulés. |
| **V29.3** | Audit renforcé buffers LCD/callback/ABI, 26/26 checks, 12/12 altérations ; restauration unique à OFF ; mémoire ARM candidat `0xC01A2100`, relais `0xC01B0000`. | 10 valeurs ressemblant à des pointeurs trouvées dans la zone candidate. |
| **V29.4 – branche A « placement »** | Déplacement cœur à `0xC01D0000`, relais à `0xC01E0000`, zéro mot 32 bits aligné pointant vers la réservation sur les deux VSB ; 28/28 audits, 14/14 altérations ; watchdog OFF et restauration unique après retour du callback. | Contrôle *statique seulement* ; RAM à l'exécution inconnue. |
| **V29.4 – branche B « sentinelles »** | Ajout `md25_state_intact()`, vérification des sentinelles `magic`/`tail_guard`, désarmement, repli comparateur Korg si état corrompu ; tests de corruption sur hôte, 26/26 audits. | **Branche distincte**, encore non fusionnée avec placement V29.4 A. Sentinelles non exhaustives. |

Tous les résultats chiffrés sont ceux des **rapports de laboratoire**, pas des validations matérielles.

## 4. Architecture ARM / LCD étudiée

**Firmware examiné :** fichier `.VSB` avec en-tête `0x100` et image applicative d'environ **2 Mio** ; base de désassemblage de l'application ARM **`0xC0000000`**. Deux versions utilisateurs ont été analysées en **lecture seule** :

- Firmware personnalisé original : `user_custom.VSB`, SHA-256 **`81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03`**.
- Copie de sauvegarde : `user_backup.VSB`, SHA-256 **`06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052`**.

**Ne pas confondre la présence d'un mot dans les 2 Mio du fichier avec une preuve de mémoire libre, exécutable et stable pendant l'audio.** Le code embarqué se déplace dans la RAM ; le firmware peut exploiter des allocations, des zones de données ou du DMA qui n'apparaissent pas dans un scan brut.

### LCD — adresses documentées dans les derniers audits V29.3/V29.4

| Élément | Adresse / constat |
|---|---|
| Image source / framebuffer LCD Korg (selon audit V29.4) | **`0xC031B710`**, 1 024 octets |
| Shadow / tampon de transmission (selon audit V29.4) | **`0xC031B310`**, 1 024 octets |
| Descripteur LCD / état | **`0xC031BB2C`** |
| Dispatcher LCD | **`0xC0015DD0`** |
| Opcode `2` | Marque le drapeau « rafraîchissement requis » à l'offset `+5` du descripteur, via `0xC0015E60` |
| Opcode `3` | Demande le traitement LCD, via `0xC0015E50` puis `0xC0015FA0` |
| Comparateur Korg d'une page | **`0xC0015AB4`** |
| Appel au comparateur, point d'insertion candidat | **`0xC0016084`** |
| Copie de 128 octets vers le shadow | Vers `0xC0015B38` / `0xC000985C` |
| Rappel LCD Korg original | **`0xC002A71C`** |
| Littéral / pointeur du rappel | **`0xC002A970`** |
| Moteur de rappel et compteurs | **`0xC002A7EC`, `0xC002A818`**, configuration vers `0xC002A8D4` |
| Nombre de pages | **8 × 128 octets** ; une page sale doit réellement être copiée vers le shadow avant l'envoi |

**Remarque sur les documents historiques :** certains rapports V22/V25 utilisaient les termes « source » et « shadow » dans le sens inverse. Le **dernier audit V29.4** identifie les adresses comme ci-dessus et vérifie leurs littéraux ARM. La prochaine conversation doit **recontrôler le sens exact des copies et l'instant de consommation par le pilote SPI** avant toute modification du firmware ; le fait que les deux buffers existent ne prouve pas à lui seul l'ordre effectif des opérations matérielles.

**Chemin envisagé, mais PAS installé :**

```
Rappel natif LCD Korg (pointeur depuis 0xC002A970)
   -> relais ARM md30_callback_bridge
        -> md30_callback_visit (cadence, rendu Mercury, opcode 2 si nécessaire)
        -> retour inconditionnel au rappel Korg 0xC002A71C
             -> opcode 3 du dispatcher LCD Korg
                -> appel de comparaison 0xC0016084
                   -> relais md31_compare_veneer
                      -> Mercury si autorisé, comparateur Korg sinon
                         -> shadow 8 × 128 octets -> pilote LCD Korg
```

L'idée est de **réutiliser le pilote LCD natif et le comparateur de pages**, et de ne jamais inventer un deuxième pilote SPI. Le code garde l'original accessible en mode OFF. Le relais et le comparateur doivent être intégrés uniquement dans le **contexte de tâche LCD réellement vérifié**, sans hypothèse de réentrance sûre.

**Horloge :** le rappel utilise un compteur/rechargement avec une valeur `20` analysée en V26. C'est un **nombre d'appels** dans un mécanisme de scheduler, **pas une mesure de 20 ms**. La source candidate d'horloge du séquenceur (`0xC068FC80`, vue dans des analyses antérieures) n'est pas matériellement validée. La porte de rafraîchissement du moteur est à **40 ms** (~25 FPS **dans la simulation**), avec arrêt de sécurité après un trou **>250 ms**.

### Placement ARM de la branche V29.4 A

- Cœur ARM926EJ-S lié à **`0xC01D0000`**, fin exclusive **`0xC01D8028`** (32 808 octets dans ce build).
- Relais de callback lié à **`0xC01E0000..0xC01E0014`** (20 octets).
- Relais du comparateur `md31_compare_veneer` lié dans le cœur à **`0xC01D5C14`** dans le rapport d'audit ; ce n'est pas une routine installée sur l'appareil.
- Réservation auditée contre les pointeurs statiques : **`0xC01D0000..0xC01E1000`**. Elle contient uniquement `FF` dans les **deux images VSB** étudiées ; **aucun mot 32 bits aligné du fichier** ne prend une valeur dans cette plage.
- Le build freestanding ARM rapporte **0 symbole non résolu**, **pas de section `.bss`**, état préalloué dans l'image. Ces conditions restent **insuffisantes pour prouver une bonne initialisation depuis Korg**.
- Le scan initial du placement V29.3 `0xC01A2100` avait **10 mots ressemblant à des pointeurs** ; ils n'étaient pas prouvés réels, mais l'emplacement a été écarté par prudence.

### Panneau de boutons

Pistes du désassemblage : réception/décodage vers **`0xC002814C`**, diffusion vers **`0xC0028208`** et **`0xC00839F0`**. `src/md20_keys.c`, `src/md23_panel_gateway.c`, `src/mercury_keys.c` et `src/md17_panel.c` fournissent un acheminement logiciel simulé de l'appui + relâchement, sans avoir encore branché et vérifié les codes des touches physiques sur la machine.

## 5. Inventaire des principaux fichiers de code source

**À ne pas réécrire de zéro :**

- `src/mercury_live.c/.h` : rendu procédural et primitives du moteur visuel.
- `src/mercury_glitch.c/.h` : transformations et effets glitch.
- `src/mercury_events.c/.h`, `src/md16_runtime.c/.h` : pont d'événements / dynamique ; source réelle des notes et de l'horloge pas encore validée.
- `src/md21_v14_profiles.c/.h` : profils et variantes C hérités, à confronter à la référence V30.
- `src/mercury_keys.c/.h`, `src/mercury_menu.c/.h` : **8 presets, 12 réglages globaux, menus et boutons** ; `global_only` (depuis V28) masque la page PISTES sans perdre ses valeurs.
- `src/md17_panel.c/.h`, `src/md20_keys.c/.h`, `src/md23_panel_gateway.c/.h` : passerelle de boutons, transmission Korg, gestion appui/relâchement.
- `src/lcd_source_mux.c/.h`, `src/md18_lcd_abi.c/.h`, `src/md23_lcd_shadow.c/.h`, `src/md31_lcd_comparator.c/.h` : sélection de source LCD, comparaison et restauration.
- `src/md24_refresh_gate.c/.h`, `src/md24_visual_service.c/.h` : cadence et rendu/rétablissement.
- `src/md25_visual_boot.c/.h` : état du moteur préalloué, garde-fous de démarrage et arrêt en cas de retard.
- `src/md30_lcd_callback.S`, `src/md30_lcd_gate.c/.h` : **relais callback et logique d'armement/désarmement** ; relay OFF par défaut.
- `src/md31_compare_veneer.S` : relais ARM du comparateur.
- `src/md30_lab_layout.ld` : placement théorique du module ARM en RAM.
- `src/mini_lfo4.c/.h`, `src/md23_modulation_bridge.c/.h` : anciennes recherches pour 4 LFO **au total**, non prioritaires et NON raccordées au moteur de modulation matériel.

Important : une simulation peut appeler `md30_arm_for_verified_lab(...)` avec **des validations fournies artificiellement**. **Ne jamais simuler des preuves en mettant tous les drapeaux à 1 sur un véritable firmware.** Le succès des tests hôte ne certifie ni l'ABI ni la sécurité d'un hook réel.

## 6. Résultats de validation et ce qu'ils signifient

- V24 : **64 frames animées non vides** dans le test complet hôte ; restauration de l'image Korg, simulation de pages LCD.
- V25 : ARM statique compile, état préalloué ; **14/14 contrôles** des deux VSB ; 25 mises à jour visuelles en simulation.
- V26 : **37/37 assertions** sur chacun des deux VSB ; **10/10 mutations** repérées par les tests.
- V28 : pages globales conservées, page PISTES masquée, tests des valeurs et navigation.
- V29.1 : relais ARM lié à la fonction C, retour au callback Korg ; correction d'une dépendance `__aeabi_uidivmod`.
- V29.2 : tests ON/OFF, SHIFT+HPF, EXIT, relâchements, affichage/restauration Korg ; **11/11** audits de points LCD par VSB.
- V29.3 : **26/26** assertions binaires par VSB ; **12/12** mutations ; 1 024 octets Korg restaurés en simulation.
- V29.4 A : **28/28** vérifications par VSB ; **14/14** mutations ; aucune référence statique détectée vers la nouvelle plage du fichier ; tests de timeout/restauration. Audit enregistré dans `rapport_audit.json`.
- V29.4 B : **26/26** par VSB, plus scénarios de corruption des deux sentinelles et fallback Korg ; tests **distincts** de la branche A.

**Absence de validation :** aucune mesure de consommation CPU ou de stabilité audio réelle, aucun test de vrais boutons, aucune preuve RAM au runtime, aucune instrumentation du SPI, aucun boot hook implanté, aucun VSB utilisateur modifié, **aucune démonstration sur l'Electribe**. Une restauration simulée de 1 024 octets n'est pas une garantie matérielle de retour écran.

## 7. Risques et lacunes exacts avant un premier essai réel

1. **Point d'initialisation non prouvé** : où le firmware original doit-il appeler `md25_begin`/le relais pour initialiser une seule fois l'état, avec les bonnes adresses et le bon contexte ? La simple édition de liens ne lance pas le code.
2. **Disponibilité mémoire en situation** : espace `FF` + 0 référence statique ne prouvent pas que `0xC01D0000..` restera libre pendant lecture, effets IFX, samples, DMA, heap ou séquenceur.
3. **Point d'insertion du callback** : le pointeur `0xC002A970` est un candidat dans l'image Korg, mais son contrat d'appel, son contexte IRQ/tâche, sa cadence en lecture et les conditions exactes de modification ne sont pas validés sur l'instrument.
4. **Concurrence LCD / SPI** : le comparateur et le transfert des 8 pages doivent rester sérialisés. Pas d'écriture directe vers le SPI depuis une autre tâche.
5. **Touches réelles** : confirmer physiquement les codes SHIFT/LPF/HPF/BPF/EXIT et l'existence d'un endroit réversible pour y intercepter les événements ; OFF doit être disponible même dans les réglages.
6. **Restauration après panne** : tester le cas où le callback arrête de se déclencher, où l'état mémoire est corrompu ou où une touche reste enfoncée ; les deux protections V29.4 restent à fusionner, puis à retester.
7. **Portage artistique / paramètres** : les 8 profils existent en C mais la silhouette et les 12 influences ne sont pas encore toutes vérifiées conformes à la V30 HTML.
8. **Chemin de récupération** : sans JTAG sur cette Electribe, une mise à jour qui empêche le démarrage peut nécessiter des moyens absents. La carte SD et une sauvegarde du firmware **ne sont pas** une garantie de débrickage.

**Conclusion : aucun fichier « prêt à flasher » ni téléchargement garanti « sans risque matériel » ne doit être annoncé.** Les sources de laboratoire, elles, peuvent être conservées/partagées sans solliciter la procédure de flash.

## 8. Feuille de route ciblée (éviter de recommencer le projet)

**Priorité 1 — fusion/revue des deux branches V29.4 :** importer `md25_state_intact`, le repli comparateur Korg et les tests de corruptions de la branche B dans la branche A qui utilise `0xC01D0000`, sans perdre les 28/28 audits ni les 14/14 tests de mutation. Ne pas considérer la fusion comme acquise avant compilation et tests complets.

**Priorité 2 — contrat matériel réel :** vérifier exactement comment et quand Korg remplit les deux buffers, compare/copie la page, puis lance le transfert SPI ; vérifier l'ABI du callback et du comparateur, et identifier un vrai point de démarrage. Faire une revue statique qui prouve que **le mécanisme choisi ne suffit pas à inventer une occupation RAM**.

**Priorité 3 — première démonstration réversible :** afficher quelque chose qui **bouge** sur l'écran de la vraie Electribe **en conservant déjà les 8 presets, 12 paramètres globaux et ON/OFF**. Même si le premier rendu est simple, ne pas supprimer les réglages globaux. Le retour Korg par SHIFT+BPF/EXIT doit être prévu et audité.

**Priorité 4 — seulement après** : mesurer charge CPU et stabilité audio/SPI en lecture, puis brancher événements du séquenceur et effets par piste ; LFO ensuite, et toujours quatre au total au début.

**Condition indispensable :** trouver une méthode d'essai et de récupération réellement défendable **avant** de générer un `SYSTEM.VSB` destiné à la carte SD. Ne pas promettre qu'une sauvegarde PC suffira.

## 9. Exécuter les tests existants (PC/WSL, lecture seule pour les VSB)

Sous Linux/WSL, avec Python 3, `clang`, `ld.lld`, `nm`, `readelf` disponibles :

```bash
# Décompresser la branche V29.4 A sur un PC, dans son dossier :
bash tests/run_v29_3.sh /chemin/user_custom.VSB /chemin/user_backup.VSB

# Les scripts compilent les sources locales et n'écrivent pas dans les VSB.
# NE JAMAIS renommer un ELF/BIN de recherche en SYSTEM.VSB.
```

Pour savoir exactement ce qui a été vérifié, lire le JSON `rapport_audit.json`, puis les fichiers `tests/`, `tools/`, `reports/` du ZIP de la branche correspondante. Les scripts sont destinés à un environnement de développement ; ne pas les exécuter depuis la carte SD de l'Electribe.

## 10. Liste des documents importants à préserver

**Indispensables** :

- Le présent document `MERCURY_DUST_PASSATION_COMPLETE_2026-10-31.md` ; `01_PROMPT_A_COLLER.md` ; `00_LISEZ_MOI.txt`.
- `references/Mercury_Dust_V30_Groove_CORRIGE.html` — **SHA-256 `57d0d2d49377f690fe2561b5f7eb53ebf0fcd6c703f7c27d9a3899685204165d`**, référence artistique officielle.
- `02_SOURCE_V29_4_CAVE_ET_RESTAURATION.zip` — branche V29.4 A, emplacement mémoire `0xC01D0000` et tests récents.
- `03_SOURCE_V29_4_SENTINELLES_FAILSAFE.zip` — branche V29.4 B, protections en cas de corruption, non fusionnée.
- `documents/historique/V21_RAPPORT_FR.md`, `V22_RAPPORT_FR.md`, `V23_RAPPORT_FR.md`, `V24_README_FR.md`, `V25_RAPPORT_FR.md`, `V26_RAPPORT_FR.md`, `V28_RAPPORT_FR.md`.
- `documents/historique/V29_1_README_FR.md`, `V29_2_README_FR.md`, `V29_3_README_FR.md`, `V29_4_PLACEMENT_FR.md`, `V29_4_SENTINELLES_FR.md`.
- `documents/technique/V29_4_AUDIT_PLACEMENT.json`, `V29_4_RESULTATS_FAILSAFE.txt`, `V21_CONTRAT_HOOKS.md`.

**Secondaires / pour contexte** : référence V14, image de huit presets V21, documentation V27 MIDI (projet mis de côté), anciens ZIP V21–V26 si une comparaison historique de code est nécessaire.

**Fichiers utilisateur à fournir séparément à la nouvelle conversation pour réauditer le firmware** : `user_custom.VSB` et `user_backup.VSB` (identifiables par les SHA-256 en section 4). Ne jamais les remplacer par les binaires `.elf`/`.bin` de laboratoire, ni inclure à tort les `.VSB` dans un patch sans confirmation explicite.

## 11. Rappel de sécurité pour tout nouveau développement

- Une ZIP de sources **n'est pas** une image de flash. **Ne rien installer sur l'Electribe depuis cette passation.**
- Les liens de téléchargement et signatures SHA-256 attestent seulement d'un contenu donné ; ils ne prouvent pas qu'un code serait sûr pour une machine réelle.
- **Ne pas présenter des assertions statiques comme une mesure matérielle.**
- Préserver les sauvegardes de samples/patterns/IFX et firmwares ; les IFX personnalisés ne doivent pas être écrasés.
- Ne pas demander à l'utilisateur de démonter sa machine ni d'exécuter un flash de test non récupérable. Sans JTAG, travailler en statique/revue jusqu'à disposer d'un chemin d'essai/récupération raisonnable.

---

**FIN DE PASSATION.** La nouvelle conversation peut commencer par lire le prompt court et les deux ZIP de sources V29.4, puis travailler directement sur les lacunes exactes. **Ne pas recommencer la création des paramètres, menus ou presets.**
