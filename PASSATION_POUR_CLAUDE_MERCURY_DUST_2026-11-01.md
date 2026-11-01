# MERCURY DUST — PASSATION COMPLÈTE POUR CLAUDE

**État technique : 1er novembre 2026, après MD44.**  
**Plateforme cible : Korg Electribe 2 Sampler, firmware Hacktribe personnalisé.**  
**Statut : laboratoire PC / analyse statique ARM. Aucun firmware Mercury installable, aucun flash ni essai sur l'instrument.**

> **Règle essentielle** — Dans ce dossier, « test réussi » signifie simulation / test sur ordinateur, édition de liens ARM ou audit binaire statique, JAMAIS confirmation de sûreté matérielle. La présence de code assemblé aux adresses supposées ne constitue PAS son injection ou son exécution sur la vraie Electribe. Le propriétaire n'a pas de JTAG et sa SD / sauvegarde VSB ne constituent PAS une méthode de débrickage garantie.

## 1. But et demandes du propriétaire

Mercury Dust est un visualiseur **procédural monochrome 128 × 64 pixels**, intégré à l'écran de l'Electribe sans ordinateur, qui réagit à la musique jouée sur la machine. La **référence artistique immuable** est `reference/Mercury_Dust_V30_Groove_CORRIGE_Reference.html` ; SHA-256 :

`57d0d2d49377f690fe2561b5f7eb53ebf0fcd6c703f7c27d9a3899685204165d`

Direction : mercure liquide/chrome monochrome, rubans et cordes, cavités noires, gouttes, coulures, poussières, réaction lisible au kick/snare, glitch, fluidité de la lo-fi/jungle à la techno dure. La V31 graphique a été rejetée. Ne pas la remplacer. Les rendus C/ARM hérités **ne sont pas démontrés pixel-à-pixel fidèles à V30** ; ne pas déclarer ce portage artistique terminé.

### Contraintes verrouillées

- **Huit presets** : `FLOW`, `SILK`, `HYPNOSE`, `ACID`, `HARD TEK`, `LOFI`, `JUNGLE`, `COLLAPSE`.
- **Douze contrôles globaux, trois pages** :
  - AMBIANCE : PRESET (0–7), INTENSITÉ (0–100), CORDES (1–8), RÉACTION (0–100).
  - MOUVEMENT : RATE (`1/1`, `1/2`, `1/4`, `1/8`, `1/16`, `1/32`), FLUIDITÉ, ONDULATION, CHAOS (0–100 pour les trois derniers).
  - GLITCH : GLITCH, COULURE, PERTE DATA, IMAGE FIGÉE (0–100).
- **Page PISTES masquée seulement** : IMPACT, SENSIBILITÉ, CORDE, RÔLE pour chacune des 16 pistes ; conserver leurs valeurs/structures et la possibilité de la réactiver ultérieurement.
- **Mini-LFO gelés** : quand repris, **4 LFO AU TOTAL**, jamais 4 par piste ni 64 instances. Aucune modulation DSP réelle à brancher maintenant.
- **Boutons souhaités** : `SHIFT+BPF` = ON/OFF universel depuis toutes les vues ; `SHIFT+HPF` = réglages et navigation des trois pages ; `BPF` en réglages = édition ; `LPF/HPF` = navigation/valeurs ; `EXIT` = retour Korg. `SHIFT+LPF` a historiquement été réservé aux LFO, mais pas à intégrer maintenant.
- Un bouton capturé par Mercury doit garder son **appui et son relâchement** dans le même gestionnaire ; éviter les touches « orphelines » côté Korg. En mode Korg, ne pas modifier le comportement normal des filtres.
- Pas de second pilote SPI, de modifications IFX/DSP/audio, de samples/patterns, de MIDI externe obligatoire, de nouvelles fonctionnalités UI ni de flash expérimental.

## 2. Inventaire des artefacts à transmettre

**Source à reprendre :** archive `MERCURY_DUST_MD44_SOURCES_ET_PASSATION_SANS_FLASH.zip` (ce dossier), **pas** un ancien ZIP V29.4. Son contenu conserve les sources C/ARM V29.4 fusionnées, les corrections MD38–MD41, l'audit de limitation MD42, la couche portable MD43 et la correction MD44.

Ordre de lecture suggéré :

1. **Ce fichier**, puis `CLAUDE_PROMPT_A_COPIER.md` et `MD44_RAPPORT_FR.md`.
2. `MD43_RAPPORT_FR.md` et `MD42_RAPPORT_FR.md` : architecture portable, limitation de transport LCD.
3. `documents/MD41_RAPPORT_FR.md`, `documents/MD40_RAPPORT_FR.md`, `documents/MD39_RAPPORT_FR.md`, `documents/MD38_RAPPORT_FR.md` : modifications successives et preuves de test.
4. `src/md43_platform_port.{h,c}`, `src/md30_lcd_gate.{h,c}`, `src/md31_lcd_comparator.{h,c}`, `src/md25_visual_boot.{h,c}`, `src/md20_veneer.S`, `src/md30_lcd_callback.S`, `src/md31_compare_veneer.S`.
5. `tests/test_md44_native_pending_reentry.c` et `tests/test_md42_spi_failure_gap.c` **avant** de suggérer un nouveau hook.
6. `documents/MERCURY_DUST_PASSATION_COMPLETE_2026-10-31.md` pour l'historique initial.

**Firmwares Korg/Hacktribe appartenant à l'utilisateur, non inclus dans l'archive à transmettre :**

| Origine | Taille | SHA-256 |
|---|---:|---|
| `user_custom.VSB` | 2 097 408 octets | `81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03` |
| `user_backup.VSB` | 2 097 408 octets | `06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052` |

Les deux hashes ont été revérifiés le 1er novembre 2026 dans le conteneur, avant et après les tests en lecture seule. Ils sont **différents** : les analyses historiques signalent 142 octets différents dans les zones d'effets personnalisés, mais il ne faut pas remplacer les IFX personnels. Si Claude veut vérifier un site ARM dans un original, demander au propriétaire de fournir ces fichiers **séparément** et vérifier leurs hashes avant toute analyse. **Ne pas produire ni recommander d'image SYSTEM.VSB installable.**

## 3. Architecture logicielle et états

### Moteur indépendant des adresses Korg

- `src/mercury_live.c/.h`, `mercury_glitch.c/.h` : rendu/procédural/glitch 1 bit.
- `src/mercury_keys.c/.h`, `mercury_menu.c/.h` : UI, huit presets et contrôles conservés ; `md_set_global_only(...,1)` cache les paramètres par piste.
- `src/md15_bridge.c/.h`, `md16_runtime.c/.h`, `mercury_events.c/.h` : moteur de rendu, gestion des événements normalisés, rendu 1 024 octets.
- `src/md21_v14_profiles.c/.h` : profils graphiques C hérités ; V30 HTML fait foi si divergence visuelle.
- `src/mini_lfo4.c/.h`, `md23_modulation_bridge.c/.h` : recherches anciennes en sommeil, pas d'écriture de paramètres matériels.

### Couche Korg / Hacktribe étudiée mais NON raccordée physiquement

- `src/md17_korg_adapter.c/.h`, `md17_lcd_page.c/.h`, `md18_lcd_abi.c/.h`, `lcd_source_mux.c/.h`, `md23_lcd_shadow.c/.h` : interface à la source et aux pages LCD.
- `src/md17_panel.c/.h`, `md20_keys.c/.h`, `md20_veneer.S`, `md23_panel_gateway.c/.h` : événements de touches décodées, collision de codes, propriété des relâchements.
- `src/md24_visual_service.c/.h`, `md24_refresh_gate.c/.h` : service visuel, garde de cadence de 40 ms dans la simulation (~25 FPS cible), repli et timeout.
- `src/md25_visual_boot.c/.h` : état préalloué, sentinelles `magic`/`tail_guard`, `md25_state_intact`, preuves externes. La simple existence des sentinelles ne prouve pas l'intégrité du reste de la RAM.
- `src/md30_lcd_callback.S`, `md30_lcd_gate.c/.h` : relais ARM candidat qui appelle `md30_callback_visit` avant de passer **inconditionnellement** au callback LCD Korg original. OFF par défaut. Aucune injection dans les deux VSB.
- `src/md31_compare_veneer.S`, `md31_lcd_comparator.c/.h` : relais C/ARM du comparateur de pages, retourne normalement au comparateur Korg.
- `src/md30_lab_layout.ld` : **placement théorique de laboratoire**, pas preuve d'espace mémoire libre.

### Couche portable MD43/MD44 (indépendante et simulée)

`src/md43_platform_port.{h,c}` expose :

```c
int md43_init(md43_port *p, const uint8_t native_snapshot[1024], md43_platform_api api);
int md43_key_event(md43_port *p, md43_normalized_key key, uint8_t down);
int md43_ui_tick(md43_port *p, uint32_t monotonic_ms);
int md43_step(md43_port *p, uint8_t step, uint16_t part_mask);
int md43_clock(md43_port *p, uint32_t tick, uint32_t ms, uint16_t ppqn);
```

L'API injectée comporte `offer_frame(user, 1024 bytes)` et `request_native(user)`. Leurs retours 1 veulent dire **demande acceptée**, pas livraison physique des pixels. Les plateformes « Hacktribe » et « OmniTribe » du test sont **deux faux adaptateurs PC**. Ils démontrent seulement la séparation du moteur C d'avec ses dépendances ; **aucun plugin, SDK ou appel OmniTribe réel n'est intégré**. Cette couche n'est pas un remplacement matériel prouvé du relais Korg `md30`/`md31`.

## 4. Découvertes ARM sur les deux firmwares (statiques)

### Format firmware

- Fichiers `.VSB` : en-tête `0x100` octets, image applicative d'environ **2 Mio** analysée à la base virtuelle ARM `0xC0000000`.
- CPU ciblé par le code de recherche : **ARM926EJ-S / ARMv5TE**, compilation freestanding, convention d'appel AAPCS à vérifier en contexte réel.
- Les rapports historiques trouvent un intervalle entièrement `FF` dans les VSB ; ce n'est pas la preuve d'une allocation RAM libre ni du chargement de nos propres octets.

### Piste mémoire candidate, toujours non validée matériellement

| Élément | Adresse |
|---|---|
| Placement théorique cœur Mercury | `0xC01D0000` |
| Fin exclusive après compilation **MD44** | `0xC01D88CC` |
| Relais callback (`md30_callback_bridge`) | `0xC01E0000..0xC01E0014` |
| Réservation testée | `0xC01D0000..0xC01E1000` |
| Image applicative présumée | `0xC0000000..0xC0200000` |

L'analyse statique historique : 0 mot 32 bits aligné du fichier pointant dans la réservation, 10 régions de piles documentées ne la chevauchent pas. Mais les données chargées, allocations, autres adresses non alignées, overlaps dynamiques, cache, DMA, mixage audio, SPI, interruptions, relocation ou overlays ne sont PAS suffisamment cartographiés. La disponibilité mémoire **en situation audio** reste à démontrer. Il n'existe aucune preuve d'allocation officielle pour Mercury.

### Démarrage et tâches Korg

Les adresses observées dans MD35–MD37 comprennent :

- `0xC0000110` → `0xC00000F4` → `0xC00002B4` : chemin menant au code qui parcourt dix descripteurs de tâches.
- `0xC00003B0` et `0xC00003D8` : initialisation de structures et préparation conditionnelle de tâches. Des régions de piles sont décrites à partir de `0xC0200000` ; les flags descripteurs n'impliquent pas dix tâches immédiatement lancées.
- `0xC002AB7C` (tâche initiale) → `0xC002B044` (chargement ID de tâche 2) → `0xC002B048` (appel `0xC00005A0`) ; ce mécanisme peut activer la deuxième tâche. Les autres ID suivent.
- Vers `0xC002AA34` / `0xC002A978` / `0xC002A8D4` : chemin initialisation du scheduler/rappels LCD.

**Important :** ce sont des cheminements d'instructions dans le désassemblage, pas la mesure du contexte d'exécution. L'initialiseur du scheduler utilise un compteur de **20 appels**, **pas une période prouvée de 20 ms**. Aucun point de boot Mercury matériellement sûr n'est identifié.

### LCD Korg natif

| Élément / rôle supposé | Adresse / observation |
|---|---|
| Source native LCD (dernier audit) | `0xC031B710` |
| Tampon shadow/transmission | `0xC031B310` |
| Descripteur LCD | `0xC031BB2C` |
| Dispatcher d'ordres LCD | `0xC0015DD0` |
| Opcode 2 | marque « rafraîchissement requis », flag `+5` |
| Opcode 3 | lance le chemin de rafraîchissement natif |
| Comparateur d'une page | `0xC0015AB4` |
| Site d'appel candidat comparateur | `0xC0016084` |
| Callback LCD original | `0xC002A71C` |
| Littéral du callback original | `0xC002A970` |
| Transmission/page | `0xC001613C` → `0xC00160C4` → `0xC00183CC` |

Le callback est chargé depuis un **littéral** au démarrage puis enregistré dans un objet : le littéral `0xC002A970` n'est pas à traiter comme un pointeur de callback « modifiable à chaud ». Une image est composée de **8 pages × 128 octets = 1024 octets**, pas de RGB ni de framebuffer 8 bpp. Les anciens rapports inversaient parfois les noms source/shadow : recontrôler le sens exact des copies avant tout raccordement.

**Limitation centrale MD42 :** le bas niveau `0xC00183CC` retourne un statut après une attente bornée à 1000 itérations ; `0xC00160C4` ne propage pas ce statut au niveau supérieur dans les deux VSB étudiés. Des tampons convergents peuvent donc coexister avec une transmission échouée. Une demande d'actualisation ou l'égalité de `source == shadow` **ne prouve pas** la fin SPI ni l'affichage réel. MD41 ne prétend valider que la **copie en mémoire**.

### Panneau et boutons

Chemin analysé par MD37 : `0xC002A4DC` → `0xC002814C` (décodage) ; événements de type 0 : code à `+0x0D` et état appui à `+0x0E` ; diffusion via `0xC0028208` → `0xC00839F0` → `0xC0083FE8` puis callback indirect. Cela ne constitue pas une interception de touches réellement intégrée.

Codes proposés historiquement mais **NON vérifiés physiquement** : `SHIFT=0x0A`, `LPF=0x12`, `HPF=0x14`, `BPF=0x16`. EXIT n'a pas de code prouvé. L'unicité des codes (MD39) ne prouve pas leur exactitude.

## 5. Historique condensé (ce qui change vraiment)

| Étape | Changement prouvé / portée | Ce qui reste inconnu |
|---|---|---|
| V21–V28 | Moteur C 1 bit, animations/menus, UI globale, 4 LFO au total dans les recherches, page pistes masquée | Fidélité V30 finale, firmware réel |
| V29.1–V29.4 A | Relais LCD/comparateur de recherche, emplacement `0xC01D0000`, restauration Korg simulée | Task hook réel, RAM runtime, SPI |
| V29.4 B puis fusion A+B | Sentinelles et fallback vers Korg; prévention de l'accès à certains états corrompus; compilations et tests | Sécurité de la zone mémoire en réel |
| MD35–MD37 | Table de tâches et chemin de démarrage, décodage événementiel, adresses LCD approfondis | ABI/concurrence et identité physique des touches |
| MD38 | N'appelle plus inutilement le service visuel au repos en écran Korg ; évite faux timeout après longue inactivité | Consommation CPU réelle |
| MD39 | Refuse dix collisions possibles entre cinq codes de touches | Correspondance des codes réels |
| MD40 | Refuse le réarmement lorsque session active, restauration en attente ou relâchement Mercury non absorbé | Fin effective du SPI |
| MD41 | Attente de huit copies de pages Korg + rappel suivant + comparaison complète avant déverrouillage logiciel | Accusé matériel SPI/DMA |
| MD42 | Test reproduisant la **limitation** : copies en mémoire réussies malgré envois simulés échoués | Faute non corrigée ; ACK à trouver |
| MD43 | Interface indépendante pour deux plateformes factices : mêmes trames et événements PC, refus/réessai du dépôt d'image | Pas de plugin/SDK OmniTribe ni raccordement matériel |
| **MD44** | **Nouveau défaut reproduit et corrigé** : une demande native refusée n'autorise plus `SHIFT+BPF` / `SHIFT+HPF` à réentrer avant acceptation ; propriété des relâchements conservée | Une acceptation n'est toujours PAS un acquittement LCD réel |

**Attention :** les scores historiques tels que `82/82` concernent des assertions limitées à des signatures statiques, pas une couverture fonctionnelle du firmware. Un test « rouge puis vert » sur un cas réel de logiciel est un progrès plus significatif.

## 6. MD44 : correction de code de cette session

**Défaut source MD43 :** `pending_native_request=1` après un `request_native()` refusé n'empêchait pas `md43_key_event()` de rouvrir Mercury via `SHIFT+BPF` ou `SHIFT+HPF`. Cela perdait une frontière de propriété écran dans le port abstrait.

**Preuve :** nouveau `tests/test_md44_native_pending_reentry.c` lancé **sans patch** sur MD43 : assertion `screen == MD_KORG` échouée, donc test initial rouge.

**Correction :** `md43_platform_port` maintient `blocked_reentry_down` pour les raccourcis déclenchés pendant cette attente et consomme leur relâchement même si la demande est acceptée entre deux événements. Tests MD44 verts ; anciens tests MD43 verts. La limite MD42 de l'ACK physique subsiste.

**Compilation ARM actuelle (laboratoire) :** lien réussi, `__md30_core_end = 0xC01D88CC`, aucun `.bss` ni symbole non résolu selon le contrôle du build. Les adresses ne constituent pas un patch réel.

## 7. Statut de tests et reproduction

Sur un environnement Linux/WSL avec `clang`, `ld.lld`, `llvm-objdump`, `readelf`, `nm`, Python 3 :

```bash
# Depuis la racine des sources extraites
bash tests/run_md44_host.sh         # test ciblé MD44, ASan/UBSan
bash tests/run_md43_host.sh         # compatibilité des deux faux adaptateurs
bash tests/build_v29_2.sh          # tests historiques + MD44 + lien ARM recherche

# Audit de code Korg en lecture seule, avec fichiers fournis séparément
python3 tools/md42_audit_native_send_readonly.py \
  '/chemin/user_custom.VSB' '/chemin/user_backup.VSB'

# Audit des emplacements statiques, pas de sécurité RAM réelle
python3 tools/md30_audit_vsbs_readonly.py \
  '/chemin/user_custom.VSB' '/chemin/user_backup.VSB'

# Vérification de l'archive téléchargée
python3 tools/verify_source_archive.py MERCURY_DUST_MD44_SOURCES_ET_PASSATION_SANS_FLASH.zip
```

Résultats déjà vérifiés dans l'environnement de développement : **test MD44 rouge avant patch, vert après ; test MD43 vert ; suite `build_v29_2.sh` verte ; audits statiques MD42 8/8 par VSB ; hashes des VSB intacts**. Les suites utilisent des simulateurs Korg et des sanitizers PC. Aucun protocole matériel n'a été instrumenté.

## 8. Ce qui empêche vraiment la première installation

1. **Résidence mémoire non prouvée** : une plage `FF` du fichier VSB n'est pas une allocation libre. Le code pourrait écraser des structures audio ou être écrasé à l'exécution.
2. **Aucun point d'initialisation ARM validé** : le code ne sera pas lancé parce qu'un linker place une fonction à telle adresse. Le contexte appelant, les registres, l'alignement, le chargement/relocation et la réentrance doivent être démontrés.
3. **LCD/SPI sans acquittement physique** : MD41 assure seulement une convergence de tampons. MD42 a montré l'écart entre « envoyé au gestionnaire » et « affiché ». Éviter toute fausse garantie par simple temporisation arbitraire.
4. **Touches non validées sur appareil** : codes physiques et point de callback à prendre sans interrompre Korg, et propriété de chaque appui/relâchement.
5. **Récupération sans JTAG non garantie** : mise à jour Korg via le menu ne prouve pas un débrickage si le menu ne démarre plus. Posséder une sauvegarde VSB et une SD n'élimine pas le risque.
6. **Coexistence audio et ordonnancement** : aucun test réel du séquenceur, samples, IFX, IRQ, DMA, CPU ni de l'affichage à 25 FPS sur la machine.
7. **Portage V30** : le rendu ARM existant n'est pas nécessairement identique au prototype HTML validé, mais ce n'est pas la priorité tant que la sûreté matérielle est inconnue.

## 9. OmniTribe : opportunité sous conditions

Dans la recherche publique consignée dans `MD43_RAPPORT_FR.md` (état **27 octobre 2026**, à revalider si la publication évolue), il faut distinguer :

- **Omni-ROMs** : variantes du firmware Korg avec une VM de plugins encadrée. **Rien ne prouve** qu'elle permette de lancer librement un module C/ARM ou d'accéder au LCD complet.
- **Noyau OmniTribe** : projet distinct, annoncé comme démarrant depuis SD et acceptant des modules et pages personnalisées ; potentiellement plus adapté **si et seulement si** un SDK réel, l'API écran/touches et une méthode de récupération sont publiés et vérifiés.

**L'interface MD43/MD44 est une abstraction inventée pour tester notre code sur PC, PAS une API fournie par OmniTribe.** Ne pas prétendre à une compatibilité réelle sans lecture du SDK/source officiel.

## 10. Mission de revue indépendante demandée à Claude

**Livrable souhaité : des résultats techniques concrets et testables, pas de nouvelle architecture abstraite ou de simples scores d'audit.** Prioriser :

1. Revoir `md30_lcd_gate.c`, `md31_lcd_comparator.c`, les `.S`, `md25_visual_boot.c`, `md23_panel_gateway.c`, `md43_platform_port.c` : localiser **un bug reproductible** ou une hypothèse non fondée ; fournir test avant/après correction.
2. Refaire le raisonnement de sûreté mémoire : identifier les informations manquantes pour démontrer l'absence d'écrasement audio/heap/DMA dans `0xC01D0000..0xC01E1000`, sans conclure que FF=libre. Donner une méthode de validation hors firmware modifié si possible.
3. Analyser le contrat d'initialisation ARM/callback et de comparateur : contexte UI/LCD prouvé ou non, ABI ARMv5TE, registres, pile, préemption, callbacks et gestion d'IRQ. Ne pas appeler une routine supposée sûre sur la vraie machine.
4. Analyser la possibilité d'un signal de transfert LCD **réellement fiable** ; reconnaître si le matériel/driver ne l'expose pas. Faire une distinction explicite entre état DMA/SPI, tampon transmis, écran mis à jour.
5. Relire la propriété des touches, y compris le verrou MD44, les appuis répétés et les retours Korg pendant panne.
6. Chercher le **moyen de récupération documenté** réellement applicable sans JTAG ; ne pas recommander de flash tant que non démontré.
7. Si OmniTribe devient accessible, comparer ses API et contraintes réelles avec les cinq appels de l'interface portable ; proposer un portage uniquement sur preuves.

Pour **chaque** proposition : indiquer (a) fait vérifié, (b) hypothèse, (c) preuve absente, (d) test réplicable et (e) risque de brick/audio. Ne pas changer V30 ni les huit presets, douze contrôles, navigation ni données pistes. Les quatre mini-LFO restent gelés.

## 11. Ce qu'un test réussi ne démontre PAS

- Un build ARM freestanding ne prouve pas le chargement/l'exécution du code en RAM réelle.
- Une image LCD identique dans deux simulateurs ne prouve ni compatibilité Korg ni plugin OmniTribe.
- Un callback LCD natif identifié ne prouve pas que son interception est sans risque.
- Un réarmement logiciel réussi ne prouve pas le transfert physique des 1024 octets.
- La vérification des sentinelles ne prouve ni l'absence de corruption ailleurs ni la disponibilité mémoire.
- Une sauvegarde VSB n'est pas une procédure garantie pour récupérer une Electribe qui ne démarre plus.

**Conclusion actuelle : MD44 est la meilleure base source de laboratoire pour poursuivre. Aucun firmware Mercury n'a été installé. Le chemin le plus utile n'est pas d'ajouter des effets, mais d'obtenir une preuve d'intégration, de mémoire et de récupération — éventuellement via un SDK OmniTribe documenté.**
