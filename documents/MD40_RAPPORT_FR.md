# MERCURY DUST — MD40 : barrière de réarmement LCD / touches

**État au 31 octobre 2026. Sources de laboratoire — pas de firmware installable.**

Base : Mercury Dust MD39 avec la DA V30 Groove, les huit presets, les douze réglages globaux et les commandes existantes **inchangés**. Les réglages par piste restent masqués ; les mini-LFO restent gelés.

## Défaut reproduit dans MD39 avant correction

`md30_arm_for_verified_lab(...)` appelait `md30_disarm()`, puis `md25_begin()` sans refuser un nouvel armement alors que :

1. Mercury était déjà actif ; un nouvel armement réinitialisait son état UI sans raison.
2. `pending_native_restore` signalait une restauration LCD Korg en attente ; la réussite de l'armement effaçait ce drapeau, même si les 1 024 octets du shadow contenaient encore l'image Mercury.
3. Une touche (par exemple BPF) avait produit un `DOWN` consommé par Mercury mais n'avait pas encore produit son `UP` : `md25_begin()` réinitialisait le suivi d'appui, risquant de laisser son `UP` être transmis à Korg alors que Korg n'avait jamais reçu le `DOWN`.

Le nouveau programme `tests/test_md40_rearm_barrier.c` a été exécuté **sur MD39 avant correction** et échouait sur `assert(!arm())`, car l'armement pendant une session active était accepté. Ce test valide ensuite les scénarios de retour LCD et de relâchement de touche.

## Correction ciblée

- `src/md23_panel_gateway.c/.h` : expose `md23_panel_pending_mercury_release()` pour détecter une touche encore détenue par Mercury. Une métadonnée de passerelle corrompue provoque un refus conservateur.
- `src/md30_lcd_gate.c` : refuse `md30_arm_for_verified_lab` si la session est active, si la demande native est encore en attente, ou si un `UP` Mercury doit encore être absorbé. En cas d'état sentinelle invalide, désarme sans poursuivre l'initialisation. **Ne supprime pas** la demande de rafraîchissement en attente.
- `tests/test_md40_rearm_barrier.c` : teste le rejet d'armement dans les trois cas, la restauration simulée complète, l'absorption de l'auto-répétition et du `UP`, puis le succès d'un nouvel armement après drainage.
- `tests/build_v29_2.sh` : inclut le test dans la suite normale.

## Résultats reproductibles

Commande exécutée :

```sh
bash tests/run_merged_v29_4.sh '/chemin/user_custom.VSB' '/chemin/user_backup.VSB'
```

- **6/6 programmes de tests hôte réussis**, avec AddressSanitizer et UndefinedBehaviorSanitizer (tests historiques et MD39/MD40).
- **Compilateur/link ARM926EJ-S réussi**, sans `.bss` ni symboles non résolus. Le cœur finit (exclusivement) à `0xC01D836C`, le relais de callback est `0xC01E0000..0xC01E0014`.
- **28/28 assertions binaires historiques par VSB**, **14/14 tests de mutation** ; ils ne valident pas le matériel.
- SHA-256 des originaux inchangés : `user_custom.VSB = 81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03`, `user_backup.VSB = 06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052`.

## Limites explicites

La demande de restauration est considérée comme satisfaite, dans ce code, dès l'acceptation de l'opcode 2 par le dispatcher. Le véritable achèvement du cycle opcode 3 / pages / SPI **n'est pas accusé réception** par Mercury. En théorie, un événement de réarmement pourrait se produire entre la demande et la copie ou le transfert physique. Le prochain travail devra examiner ce contrat d'achèvement ; aucune garantie de restauration LCD réelle ne résulte du test hôte.

Les sentinelles ne détectent pas toute corruption mémoire. L'emplacement `0xC01D0000` n'est **pas démontré libre à l'exécution** ; le callback, les codes réels des boutons, le SPI et la récupération sans JTAG restent sans validation matérielle. Il serait donc dangereux de présenter ce résultat comme un `SYSTEM.VSB` prêt à flasher.

**Aucun VSB n'a été édité, aucun firmware flashable n'a été produit, aucun test sur la vraie Electribe n'a été réalisé.**
