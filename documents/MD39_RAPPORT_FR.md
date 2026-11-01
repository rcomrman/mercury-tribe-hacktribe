# Mercury Dust — MD39 : protection des codes de touches (SANS FLASH)

31 octobre 2026. Base: **MD38**; aucun changement visuel V30 Groove, menu, preset, paramètre global, fonctionnalité de piste, mini-LFO ou IFX.

## Pourquoi cette modification

Lors de `md25_begin`, la branche MD38 acceptait une `md17_keymap` dans laquelle deux touches physiques recevaient **le même identifiant décodé**. La passerelle de boutons teste SHIFT et EXIT avant LPF/HPF/BPF, de sorte que cette collision peut rendre impossible la fonction attendue d'une touche et brouiller la propriété de l'appui et de son relâchement. Ce risque est important tant que l'identifiant physique EXIT n'est pas confirmé.

**Reproduction avant correction :** un test hôte ajouté à la base MD38 plante sur la première collision (assertion : la branche autorise un armement qu'elle devrait refuser). Aucun firmware Korg n'a été modifié pour le test.

## Correction

- `src/md17_panel.c/.h` : fonction `md17_keymap_distinct` ; vérifie que les cinq identifiants SHIFT, LPF, HPF, BPF, EXIT sont distincts (10 paires).
- `src/md25_visual_boot.c` : refuse l'initialisation si une collision est détectée. La voie d'échec conserve le comportement existant de désarmement.
- `tests/test_md39_keymap.c` : nouveau test hôte, 10 collisions refusées, carte valide acceptée, routage SHIFT+BPF et désarmement.
- `tests/build_v29_2.sh` : intègre ce test à la suite normale.

**Attention** : l'unicité des codes est une condition nécessaire mais **ne prouve absolument pas** qu'il s'agit des codes réels du panneau Korg. Ce test n'installe aucune interception physique.

## Résultats vérifiés

Exécution : `bash tests/run_merged_v29_4.sh user_custom.VSB user_backup.VSB` depuis la copie MD39, avec les deux firmwares fournis **en lecture seule**.

- Tous les cinq programmes de test hôte passent, dont MD39 : les 10 collisions sont rejetées, la carte sans collision autorisée.
- Compilation et édition des liens ARM freestanding réussies ; `md30_callback_bridge` reste à `0xC01E0000`, sans `.bss` ni symbole non résolu.
- Régression hôte des sentinelles, watchdog 250 ms, des touches et de la restauration LCD simulée : réussie.
- Audits binaires historiques : 28/28 sur chaque VSB, 14/14 mutations de copies en mémoire. Ces nombres sont des tests de la *base*, pas des preuves de validation matérielle MD39.
- Les SHA-256 d'entrée contrôlés restent :
  - personnalisé : `81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03` ;
  - sauvegarde : `06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052`.

### Correction d'une hypothèse écartée

Un soupçon initial de désalignement de pile dans `md30_callback_bridge` et `md20_key_veneer` était **faux** : les six registres sauvegardés occupent 24 octets, multiple de 8. Ces deux relais **n'ont pas été modifiés**. L'alignement initial réel de la pile à l'entrée Korg demeure, lui, non démontré.

## Ce qui reste bloquant

1. Disponibilité de la zone `0xC01D0000..0xC01E1000` sous charge audio : inconnue ; le remplissage FF du VSB n'est pas une preuve de RAM libre.
2. Point de démarrage et contrat du rappel LCD : chemins statiques étudiés, branchement pas encore installé ni validé.
3. Code réel de EXIT, contexte appui/relâchement : non prouvés sur instrument.
4. Récupération sans JTAG si le firmware ne démarre plus : aucune méthode sûre établie.

**Décision : pas d'image installable, pas de `SYSTEM.VSB`, aucun flash.** La SD et les VSB restent inchangés. L'objectif MD39 est une correction défensive ciblée, pas un jalon de déploiement.
