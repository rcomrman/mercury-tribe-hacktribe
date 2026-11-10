# Mercury Dust → BLECHTRIBE (branche laboratoire)

Cette branche **n'écrase pas** la branche `main`, le code C/ARM MD44, les protections MD45, ni la référence artistique V30.

## Fichiers de départ

- `../reference/Mercury_Dust_V30_Groove_CORRIGE_Reference.html` : **référence artistique autoritaire**. Le plugin actuel ne reproduit pas encore ce rendu à l'identique.
- `../src/mercury_live.c`, `../src/mercury_glitch.c`, `../src/mercury_events.c` : algorithmes précédents à adapter.
- `../src/mercury_menu.c` : huit presets et contrôles conservés dans le projet C.
- `../src/mini_lfo4.c` : quatre mini-LFO **en sommeil** ; aucun accès DSP audio établi.
- `plugins/mercury_v30_lab.js` : **premier plugin autonome et expérimental** (pas encore validé sur la machine).
- `tests/check-mercury.mjs` : test du plugin avec le compilateur et le simulateur du dépôt officiel GELUMPE.

## Fonctionnement du premier plugin — V30 Lab / UI3

Cette app s'enregistre sous **BLECH → TOOLS → Mercury V30** et ne dessine que lorsqu'elle est ouverte. EXIT restitue l'écran Korg. PLAY/STOP et l'audio Korg continuent de fonctionner ; le plugin n'écrit pas dans les paramètres des pistes, les données audio ou les patterns.

- Deux rubans de chrome monochromes procéduraux, nervures noires, huit **variantes expérimentales**. Aucun GIF n'est utilisé.
- **12 contrôles globaux sur trois pages**, respectant les noms de la spécification MD44 :
  - AMBIANCE : PRESET (0–7), INTENSITY (0–100), CORDS (1–8), REACTION (0–100) ;
  - MOUVEMENT : RATE (0–5), SMOOTH, WAVE, CHAOS (0–100) ;
  - GLITCH : GLITCH, MELT, DATA LOSS, FRAME SLIP (0–100).
- Ces réglages sont mémorisés dans **12 slots de korg.store**, sauvegardés en quittant le menu ou l'app. Test de sauvegarde/rechargement réalisé sur le simulateur seulement.
- Les valeurs **CORDS > 2 n'ajoutent pas encore les autres rubans** ; la compatibilité avec les 8 cordes de la V30 de référence n'est pas obtenue. Les valeurs RATE sont ici des vitesses prototypes et non encore les divisions synchronisées de V30.
- `step` crée une pulsation **synthétique tous les quatre steps** ; ce n'est ni une vraie détection de kick, ni une analyse audio.
- `pad` provoque un impact visuel avec vélocité.
- `knob` index **9** = OSC EDIT (corrigé depuis l'ancien index 10) : valeur lue uniquement et utilisée pour influencer la vitesse de l'image. **Ce potentiomètre continue de modifier le son Korg.**
- Rendu du ruban principal sur 32 colonnes de 4 px, ruban secondaire sur 16 colonnes de 8 px, réactualisé un événement `frame` sur deux (12,5 Hz théoriques). Ce rendu ne remplace **pas** encore les rubans V30 pixel par pixel.

### Commandes quand Mercury est ouvert

| Commande | Action |
|---|---|
| MENU | Affiche ou masque le menu Mercury |
| PART LEFT / PART RIGHT, hors menu | Change de preset (0–7) |
| EDIT LEFT / EDIT RIGHT, dans menu | Change de page (trois pages) |
| PART LEFT / PART RIGHT, dans menu | Choisit une des quatre valeurs |
| BAR 1 / BAR 4, dans menu | Valeur −1 / +1 |
| BAR 2 / BAR 3, dans menu | Valeur −10 / +10 |
| EXIT | Quitte Mercury et rend l'écran à Korg |
| PLAY / STOP / REC | Continuent d'atteindre la machine |

Les touches de navigation sont interceptées par l'app ouverte, conformément au comportement officiel des plugins. En dehors de Mercury, elles retrouvent leur fonction d'origine. Le raccourci historique `SHIFT+BPF` n'est **pas** encore implémenté et il faudra vérifier sa compatibilité avec les filtres Korg.

**Tests du simulateur : PASS** le 10/11/2026. La première version utilisait 1 648 octets et culminait à 12 605 unités de coût ; la version UI3 initiale utilisait 3 864 octets, 61 variables. Le rendu sinusoïdal R2 utilise **3 996 octets et 313 variables**, avec un maximum de **18 540 unités** dans les parcours de test, pour une limite de 20 000 unités. Ce budget de calcul n'est **pas** une mesure du temps matériel de 5 ms. [Première validation UI3](https://github.com/rcomrman/mercury-tribe-hacktribe/actions/runs/42874080077). Les tests complémentaires vérifient les huit presets, leur évolution au fil des images, l'échelle 0–255 du potentiomètre OSC EDIT, les réglages et la persistance du stockage. [Exécution R2](https://github.com/rcomrman/mercury-tribe-hacktribe/actions/runs/42876442898). La CI produit une planche SVG des huit variantes, téléchargeable depuis les artefacts du test.

**Ce prototype n'est pas une version installable garantie.** Il ne constitue pas une validation matériellement sûre de BLECHTRIBE, de son chargeur ou de la compatibilité avec le firmware personnalisé actuel.

## Essayer sur ordinateur sans flasher

1. Cloner le dépôt officiel [KuhlerBuhler/kuhlers-gelumpe](https://github.com/KuhlerBuhler/kuhlers-gelumpe) dans un dossier voisin.
2. Vérifier le plugin via le compilateur et le simulateur JS :
   ```bash
   node blechtribe/tests/check-mercury.mjs ../kuhlers-gelumpe
   ```
   Exécuter cette commande depuis la **racine du dépôt Mercury**.
3. Ouvrir la page **Plugins** de GELUMPE, copier le contenu de `plugins/mercury_v30_lab.js` dans son éditeur, compiler et tester dans l'émulateur. Adapter les chemins selon le dossier GELUMPE installé.
4. Examiner le rendu à côté du fichier de référence V30, mesurer les warnings de performance et capturer les anomalies.

**Pas de flash VSB, pas de connexion matérielle obligatoire, pas d'essai sur l'Electribe tant que le simulateur, la compatibilité firmware et une stratégie de récupération ne sont pas validés.**

## Portage restant à faire

| Composant | État |
|---|---|
| Branche séparée de `main` | Créée |
| Premier plugin UI procédural | PASS GELUMPE (CI) : 8 presets parcourus |
| Conformité artistique pixel par pixel à V30 | Non obtenue |
| Rendu 128×64 natif via framebuffer `bitmap` | Toujours à porter ; utilise actuellement les primitives `rect` / `clearRect` |
| 12 paramètres globaux et édition avancée | Interface des 3 pages et persistance simulée : PASS ; comportement V30 incomplet |
| Page PISTES cachée, état par piste | À préserver puis porter |
| Événements step et pad | Utilisés ; pas d'accès audio |
| Réaction au véritable kick | À vérifier (notes/steps par piste, pas signal DSP) |
| Quatre mini-LFO | Gelés ; aucune écriture libre du cutoff/level démontrée |
| Réutilisation des effets IFX existants | Aucun changement dans cette branche |
| Tests de performance sur matériel | Non exécutés |

## Références techniques vérifiables

- [Documentation des plugins BLECHTRIBE](https://github.com/KuhlerBuhler/kuhlers-gelumpe/blob/main/docs/plugins.en.md)
- [Contrat de l'API, fonctions et budget](https://github.com/KuhlerBuhler/kuhlers-gelumpe/blob/main/data/script/contract.mjs)
- [Implémentation du rendu LCD simulé](https://github.com/KuhlerBuhler/kuhlers-gelumpe/blob/main/src/script/display.mjs)
- [Exemples de plugins](https://github.com/KuhlerBuhler/kuhlers-gelumpe/blob/main/data/script/presets.mjs)

**Risques documentés :** VM entière 32 bits sans float, budget commun de 5 ms par cycle, événements `step` quantifiés à 40 ms, rétention limitée, aucun accès audio brut documenté. Les tests sur émulateur ne prouvent pas l'innocuité sur l'appareil.

## Suivi R2 — rendu 4 pixels et optimisation mémoire (10 novembre 2026)

- La géométrie de la bande principale est maintenant calculée tous les **4 pixels** (au lieu de 8). L'autre bande reste sur **8 pixels**, pour tenir le budget VM.
- Un tableau de **256 sinus en format entier décalé** remplace le calcul sinusoïdal approximatif par segment, sans utiliser de flottants dans le plugin. `SINE` coûte 256 slots (1 024 octets) dans la mémoire partagée de la VM.
- Les trous noirs se déplacent avec la bande et restent volontairement très simples : la pleine fidélité V30 demande des cavités plus profondes, des ramifications et des reflets plus complexes.
- L'ancien indice de knob était erroné : `OSC EDIT` est bien le **numéro 9** dans la table `data/panel.mjs` de GELUMPE. La nouvelle mise à l'échelle transforme la valeur matérielle 0–255 en 0–100.
- Test automatisé renforcé : une scène doit **changer visiblement entre deux images** après plusieurs frames, en plus de se compiler et de s'afficher. Les huit variations testées passent.
- Le plafond de calcul est contrôlé dans les tests à **19 500 unités maximum** (seuil interne de prudence inférieur au plafond VM de 20 000). Ce n'est **pas** la mesure de 5 ms CPU réelle, que seul le matériel ou un émulateur temporisé crédible pourra confirmer.

**Risque en suspens** : la compression de largeur à 4/8 px provoque encore des marches d'escalier ; la vraie référence V30 HTML a des contours et des reflets fluides. Le renderer V30 natif C doit rester la source conceptuelle, pas remplacé en production par ce laboratoire graphique. Les anciens hooks LCD ARM ne sont pas intégrés ici.

### R2.1 — Coulures légères (10 novembre 2026)

Deux fines coulures par image peuvent maintenant descendre depuis le ruban principal, selon le réglage **MELT**. Elles se déplacent horizontalement avec la géométrie et ne sont pas des particules indépendantes. Première tentative à quatre coulures : limite de prudence de 19 500 unités dépassée (19 596) ; réduction à deux coulures : **PASS**, maximum observé 19 292 unités dans le simulateur, `frame` 19 183. [Tests officiels sur GitHub](https://github.com/rcomrman/mercury-tribe-hacktribe/actions/runs/42876906013). Les timings 5 ms ARM restent inconnus. Le rendu est toujours une approximation expérimentale de la V30, pas sa reproduction intégrale.

## R3 — moteur de chrome bitmap organique (10 novembre 2026)

La branche conserve la R2.1 dans `plugins/mercury_v30_lab.js`, **sans la remplacer**. La recherche R3 est isolée dans `plugins/mercury_r3_bitmap_lab.js`.

### Ce qui a réellement été codé

- **Dessin en mémoire sur tout l'écran 128×64**, mais par tranches de **32×64 pixels** seulement. Un tableau de **256 slots** contient la tranche courante dans le format exact attendu par `korg.display.bitmap(FB, sweepX, 0, 32)`. La zone affichée est nettoyée avec `clearRect` juste avant le dessin pour ne pas laisser de pixels fantômes.
- **Résolution horizontale 2 pixels par colonne calculée**, au lieu des gros blocs de 4/8 pixels de la R2.1 ; la R3 reste du pixel art, pas un rendu vectoriel antialiasé.
- **Ruban principal aminci aux extrémités**, canal noir intérieur qui suit les sinuosités, largeur qui respire et variation de domaine par réutilisation d'une seconde onde lente. Le calcul utilise la LUT sinusoïdale entière de `src/sine_q7.h`, adaptée à la VM.
- **Réactivité événementielle** conservée (pads, steps, réglage `OSC EDIT` lu sans détournement de sa fonction Korg) ; la réaction aux steps ne constitue **pas** une détection du véritable signal du kick.
- Les **12 réglages globaux** et les trois pages de menu sont réutilisés de la R2.1, avec sauvegarde simulée et retour Korg par EXIT.

### Vérification avec le vrai compilateur GELUMPE et son SimDevice

- `node blechtribe/tests/check-r3.mjs ./kuhlers-gelumpe` teste huit modes, leurs mouvements, le menu, les réglages, la mémoire après redémarrage simulé et **quatre profils extrêmes** dont haute énergie + valeurs à 100.
- `node blechtribe/tests/render-r3.mjs ./kuhlers-gelumpe` crée la planche SVG des huit presets.
- `node blechtribe/tests/render-motion-r3.mjs ./kuhlers-gelumpe` génère **48 images PGM 128×64** distinctes sur 7,68 secondes de simulation, en appliquant des événements musicaux de test ; la CI les publie sous l'artefact `mercury-r3-motion-frames`.
- Dernière vérification R3 poussée : **PASS**, taille du bytecode **4 092 octets**, **579 variables**, coût maximal **19 385 unités** / limite **20 000** sur les cas testés.
- [GitHub Actions R3](https://github.com/rcomrman/mercury-tribe-hacktribe/actions?query=branch%3Amercury-blechtribe) (ouvrir l'exécution la plus récente pour consulter ses artefacts et logs).

### Ce qui manque avant de parler d'une vraie V30

1. **Fidélité visuelle** : la référence HTML reste plus organique ; la R3 a encore **un seul ruban principal**, et non l'entrelacs original. Reflets épais, vraies cavités sculptées, coulures complexes, poussières, fractures et rémanence de la V30 manquent.
2. **Fluidité** : l'écran reçoit une tranche à chaque événement `frame` de 40 ms, donc un tour complet de quatre tranches prend **160 ms** (~6,25 images complètes par seconde). Les parties de l'image ont des âges légèrement différents. Ce compromis n'est **pas** l'objectif de fluidité final.
3. **Synchronisation vraie** : aucun accès DSP au kick ni à l'énergie audio n'est validé ; la pulsation est dérivée de l'événement `step`, et le potentiomètre audio conserve son action normale.
4. **Fidélité des réglages** : CORDS > 1, variations exactes de chaque preset, paramètres par piste et quatre mini-LFO restent à porter ou sont bloqués par les possibilités API documentées.
5. **Matériel** : le budget d'instructions du simulateur **n'est pas une mesure de la limite réelle de 5 ms**. Ne pas installer sur l'Electribe, ni produire un VSB Mercury, sans méthode de récupération adaptée et validation de compatibilité du firmware existant.

**Décision actuelle** : la R3 est une **branche exploratoire testée en simulation**, et la R2.1 demeure le fallback. Le prochain gain visible ne vient plus de la seule augmentation de résolution : il faut une topologie moins sinusoïdale, une deuxième coulée et un champ de reflets propre à la V30, tout en conservant un coût VM et un temps d'exécution raisonnables.

## Nouvelle recherche visuelle R4 / R5 (10 novembre 2026)

La comparaison a été faite **à partir du véritable canvas 128×64 de `reference/Mercury_Dust_V30_Groove_CORRIGE_Reference.html` exécuté dans Chromium**, pas d'une interprétation de captures ni d'une image générée. Voir [audit détaillé V30/R2–R5](V30_VISUAL_GAP.md).

- `plugins/mercury_r4_braid_lab.js` : deuxième variante procédurale, deux rubans qui se tressent, avec creux noirs et déformation spatiale. La R3 reste disponible.
- `plugins/mercury_r5_coils_lab.js` : **nouvelle piste** dessinant des boucles creuses asymétriques de chrome avec lames, fins reflets intérieurs et expansion liée aux steps/pads.
- `tests/check-r4.mjs`, `tests/check-r5.mjs` et leurs scripts d'aperçu : compilation par GELUMPE, tests de huit modes et de profils extrêmes, simulation des contrôles et stockage.
- R5 : **tests GELUMPE PASS**, compilation **5 076 octets**, **620 variables**, budget maximal testé **17 301 / 20 000 unités**. [Dernier test R5 dédié](https://github.com/rcomrman/mercury-tribe-hacktribe/actions/runs/42884053001).
- Les captures de simulation R5 (48 images) sont disponibles dans l'artefact `mercury-r5-v30-coils` des Actions. Ne pas confondre avec des captures de l'Electribe réelle.

⚠️ **L'aspect V30 n'est PAS encore reproduit fidèlement.** Malgré la topologie plus proche des grandes boucles, les R4/R5 restent des études graphiques. Le moteur de la vraie V30 possède des courbes paramétriques repliées et beaucoup plus de détails. Le rendu actuel en quatre tuiles par image impose encore une actualisation complète théorique de **6,25 Hz**. Aucune modification du firmware de la machine, aucune validation de cadence ARM.
