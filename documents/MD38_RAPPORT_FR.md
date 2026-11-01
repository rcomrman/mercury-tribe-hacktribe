# Mercury Dust — MD38 : correction ciblée du repos Korg (SANS FLASH)

Date : 31 octobre 2026. Source de départ : Mercury Dust V29.4 fusion A+B. Aucune modification des visuels, menus, presets, paramètres ou IFX.

## Problème vérifié dans les sources

Dans V29.4, lorsque l'interface revient sur Korg après SHIFT+BPF ou EXIT, le relais LCD reste armé pour permettre un retour ultérieur à Mercury. Il continuait cependant à appeler `md25_on_lcd_worker` à chaque callback Korg, alors qu'aucun visuel Mercury n'était affiché. Cela n'est pas une mesure de charge audio réelle : il s'agit d'un parcours de code superflu constaté et reproduit sur PC.

## Correction (3 fichiers)

- `src/md30_lcd_gate.c` : court-circuit du service visuel lorsque l'écran Korg est actif **et** que la restauration native a déjà été demandée. Le code assembleur continue à sauter vers le callback Korg original, indépendamment du court-circuit.
- `src/md25_visual_boot.c` : le watchdog de 250 ms surveille les interruptions d'une **session Mercury active** (`svc.in_custom_view`) et ne déclenche plus une fausse panne à la première image après une longue période d'inactivité sur Korg.
- `tests/test_md31_buttons_lcd.c` : ajout de tests à l'entrée de l'état Korg, après restauration, puis après un repos >250 ms et une nouvelle entrée en vue Mercury.

## Résultats PC

- Avant la modification, le relais appelait toujours le worker pendant Korg/OFF ; avec MD38, 10 callbacks de repos entraînent **0 appel supplémentaire** au worker.
- OFF après animation Mercury : **une** visite du service permet le retour Korg, puis 10 callbacks de repos n'ajoutent **aucune** visite au worker.
- Après 400 ms de repos, SHIFT+BPF et SHIFT+HPF permettent toujours le retour en vue Mercury/SETTINGS dans la simulation.
- Le watchdog reste actif pour un trou >250 ms *pendant que Mercury s'affiche* ; les tests historiques timeout, restauration et sentinelles restent réussis.
- Suite `tests/run_merged_v29_4.sh` : PASS, compilations ARM, contrôle `.bss` vide, audits statiques 28/28 sur les deux VSB et mutations 14/14. Ces derniers audits ne mesurent PAS l'amélioration MD38 : les assertions comportementales du test hôte le font.

## Limites et décisions

**Aucune connexion réelle au firmware n'a été créée.** Les chemins de tâches, la disponibilité RAM, les boutons physiques, l'ordonnancement SPI et la récupération sans JTAG restent à démontrer. Aucun fichier flashable, VSB, ELF ou BIN n'est distribué. Les preuves d'armement du simulateur ne sont pas des preuves matérielles.

La réduction de travail dans la voie Korg/OFF est prouvée uniquement dans le code et par les compteurs du simulateur. Ce n'est pas une mesure de charge CPU, de consommation de batterie ou de stabilité audio sur l'Electribe.

## Reproduction depuis l'archive

Sous Linux/WSL, avec Clang et Python 3 :

```bash
bash tests/run_merged_v29_4.sh /chemin/user_custom.VSB /chemin/user_backup.VSB
```

Les deux VSB utilisateurs ne sont pas inclus et ne sont jamais écrits. La référence artistique V30 Groove reste inchangée.

**Prochaine priorité :** obtenir un vrai contrat d'initialisation et de résidence mémoire. Un nouveau compteur d'assertions ne remplacera pas une preuve d'occupation RAM ni une méthode de récupération.
