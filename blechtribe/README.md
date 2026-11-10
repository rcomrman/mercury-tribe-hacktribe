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
- Rendu de la scène sur une grille grossière de 16 colonnes par ruban, réactualisée un événement `frame` sur deux (12,5 Hz théoriques). Ce rendu ne remplace **pas** encore les rubans V30 pixel par pixel.

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

**Tests du simulateur : PASS** le 10/11/2026. La première version utilisait 1 648 octets et culminait à 12 605 unités de coût ; la nouvelle version UI3 utilise 3 864 octets, 61 variables, avec un pic de 16 176 unités dans un gestionnaire sur la limite de 20 000 unités de la VM. Ce budget de calcul n'est **pas** une mesure du temps matériel de 5 ms. [Première validation UI3](https://github.com/rcomrman/mercury-tribe-hacktribe/actions/runs/42874080077). Test complémentaire : huit presets, réglages et persistance du stockage.

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
