# Mercury Dust MD41 — Barrière de confirmation LCD (sources de laboratoire uniquement)

**Date : 1er novembre 2026. Aucune installation effectuée, aucun SYSTEM.VSB construit.**

## Ce que MD41 change réellement

Dans MD40, `md30_callback_visit()` effaçait `pending_native_restore` dès que l'opcode 2 du dispatcher LCD était *demandé*. Cette requête ne prouvait ni la comparaison des 8 pages Korg, ni leur copie dans le shadow, ni leur transfert physique. Elle pouvait permettre un réarmement prématuré.

MD41 conserve `pending_native_restore` tant que :

1. Le rappel LCD a demandé un rafraîchissement natif à Korg (opcode 2). Les comparaisons antérieures à cette demande ne comptent pas.
2. Le chemin de comparaison natif (fallback `md31_compare_visit`) a invoqué le **comparateur Korg original** et les 8 pages de 128 octets ont chacune été constatées égales `source Korg == shadow` après cet appel.
3. Un **rappel LCD ultérieur** a constaté que les 1 024 octets source/shadow correspondent *encore*. Le verrou est alors levé, pas avant.

Si une page manque, si le comparateur n'a pas effectivement copié une page, si une page devient périmée, ou si les sentinelles sont invalides, le réarmement reste bloqué et une nouvelle demande de rafraîchissement peut être émise. Une indisponibilité du dispatcher ne lève pas le verrou. Le relais ne fait aucun transfert SPI direct.

## Modifications apportées

- `src/md30_lcd_gate.h` : remplace deux octets `reserved` par `restore_issued` et `restore_seen_mask` (sans agrandissement de la structure). Déclare `md30_note_native_page()`.
- `src/md30_lcd_gate.c` : suit la confirmation page par page, refuse la libération anticipée, vérifie de nouveau les 1 024 octets au rappel suivant. Les états de désarmement/corruption réinitialisent correctement le suivi.
- `src/md31_lcd_comparator.c` : après le comparateur **original** sur le chemin Korg, signale la page observée au verrou MD41. Le chemin Mercury reste inchangé.
- `tests/test_md41_restore_ack.c` : test nouveau **rouge sur MD40**, vert sur MD41 : 7 pages sur 8, copie manquée, octet shadow altéré, réussite après copie complète puis rappel suivant.
- `tests/test_md31_buttons_lcd.c`, `tests/test_md32_timeout_restore.c`, `tests/test_md40_rearm_barrier.c` : adaptation explicite à la sémantique d'accusé de copie (les anciens tests supposaient que l'opcode 2 suffisait).
- `tests/build_v29_2.sh` : inclut MD41 dans les régressions ordinaires.

La direction V30 Groove, les 8 presets, les 12 paramètres globaux, les commandes, les 16 valeurs par piste masquées et les mini-LFO gelés **n'ont pas été modifiés**.

## Résultats réellement obtenus

- Exécution du nouveau test contre MD40 : **échec attendu**, sur la suppression trop précoce de `pending_native_restore`.
- Test nouveau après patch : **réussi**, y compris les scénarios de page omise, copie manquée et octet altéré.
- **7 programmes de tests hôte réussis** avec ASan/UBSan (ancienne suite + MD41).
- Compilation et édition de liens **ARM926EJ-S** réussies, sans symbole non résolu, sans section `.bss` d'après le contrôle de build.
- Audits historiques en lecture seule : **28/28 assertions sur chacun des deux VSB, 14/14 mutations artificielles détectées** (assertions préexistantes, pas de validation matérielle nouvelle).
- Les SHA-256 des deux VSB originaux restent inchangés. Ni les VSB ni les fichiers `build/` ne figurent dans l'archive.

Test reproductible après extraction, sur Linux/WSL doté de `clang`, `ld.lld`, `llvm-objdump`, `nm`, `readelf`, `python3` :

```bash
bash tests/run_merged_v29_4.sh '/chemin/user_custom.VSB' '/chemin/user_backup.VSB'
```

## Limites et risque de flash

**MD41 est une confirmation de copie en mémoire, PAS un acquittement matériel SPI/DMA.** Même quand les 8 pages du shadow concordent, le pilote LCD pourrait encore transmettre les données en arrière-plan. La chronologie d'appel réelle, le sens des deux buffers source/shadow et les éventuels accès concurrents restent à établir sur la vraie Electribe.

Le module ne dispose toujours **ni de preuve de RAM libre pendant l'audio, ni de point d'amorçage matériel sûr, ni de codes physiques validés, ni de récupération démontrée sans JTAG**. Toute confirmation `MD25_REQUIRED_PROOF` fournie par les tests est *simulée*. **Il n'existe aucun firmware MD41 installable ; ne pas renommer le ELF de laboratoire en SYSTEM.VSB.**

## Prochain jalon recommandé

Vérifier statiquement le contrat complet d'appel du comparateur (ordre des pages, sémantique de copie vers le shadow, point de transfert), puis établir une stratégie d'observation non invasive et une récupération défendable **avant** toute modification des VSB. Ne pas transformer le nombre de tests en estimation de proximité d'un flash.
