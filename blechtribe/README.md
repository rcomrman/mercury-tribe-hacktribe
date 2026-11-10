# Mercury Dust → BLECHTRIBE (branche laboratoire)

Cette branche **n'écrase pas** la branche `main`, le code C/ARM MD44, les protections MD45, ni la référence artistique V30.

## Fichiers de départ

- `../reference/Mercury_Dust_V30_Groove_CORRIGE_Reference.html` : **référence artistique autoritaire**. Le plugin actuel ne reproduit pas encore ce rendu à l'identique.
- `../src/mercury_live.c`, `../src/mercury_glitch.c`, `../src/mercury_events.c` : algorithmes précédents à adapter.
- `../src/mercury_menu.c` : huit presets et contrôles conservés dans le projet C.
- `../src/mini_lfo4.c` : quatre mini-LFO **en sommeil** ; aucun accès DSP audio établi.
- `plugins/mercury_v30_lab.js` : **premier plugin autonome et expérimental** (pas encore validé sur la machine).
- `tests/check-mercury.mjs` : test du plugin avec le compilateur et le simulateur du dépôt officiel GELUMPE.

## Fonctionnement du premier plugin

L'app s'enregistre sous **BLECH → TOOLS → Mercury V30** et ne dessine que lorsqu'elle est ouverte. EXIT restitue l'écran Korg. PLAY/STOP et l'audio Korg continuent de fonctionner ; le plugin ne modifie ni les paramètres des pistes, ni les données audio, ni les patterns.

- Affichage de deux rubans procéduraux noirs et blancs avec cavités.
- Huit variantes **provisoires**, que PART LEFT / PART RIGHT font défiler. Ordre réservé : FLOW, SILK, HYPNOSE, ACID, HARD TEK, LOFI, JUNGLE, COLLAPSE. Ce ne sont **pas encore** les huit presets fidèles à V30.
- `step` provoque un accent **synthétique** tous les quatre steps ; ce n'est **pas** une vraie détection de kick ni une analyse audio.
- `pad` provoque un impact visuel selon la vélocité ; son traitement musical demeure celui de Korg.
- Mouvement du potentiomètre `OSC EDIT` (index 10) pilote aussi une variation visuelle. Attention : ce potentiomètre continue normalement de modifier le son de la piste sélectionnée. Il ne devient pas un réglage indépendant.
- Trame mise à jour une fois tous les deux événements `frame` (~12,5 Hz si la tâche UI tient 25 Hz), afin de réserver du temps CPU.

**Tests du simulateur : PASS** le 10/11/2026 après réduction de 32 à 16 colonnes par ruban. Bytecode : 1648 octets, 28 variables, maximum observé 12 605 unités de calcul pour le handler `frame` sur une limite de 20 000. Ce n'est pas une mesure du temps réel (5 ms). [Exécution CI](https://github.com/rcomrman/mercury-tribe-hacktribe/actions/runs/42873094819).\n\n**Ce prototype n'est pas une version installable garantie.** Il ne constitue pas une validation matériellement sûre de BLECHTRIBE, de son chargeur, ou de la compatibilité avec le firmware personnalisé actuel.

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
| Premier plugin UI procédural | Compilé et exécuté sans erreur dans le simulateur GELUMPE (GitHub Actions, 10/11/2026) |
| Conformité artistique pixel par pixel à V30 | Non obtenue |
| Rendu 128×64 natif via framebuffer `bitmap` | À implémenter, mesurer l'occupation mémoire et CPU |
| 12 paramètres globaux et édition avancée | À porter |
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
