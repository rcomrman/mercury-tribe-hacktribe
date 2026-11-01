# Mercury Dust MD44 — verrou de réentrée pendant une restauration native refusée

**Date : 1er novembre 2026. Code de laboratoire uniquement, sans flash.**

## Défaut reproduit dans MD43

Dans `src/md43_platform_port.c`, une transition Mercury -> Korg peut appeler `request_native()` et recevoir `0` (demande refusée, à réessayer). La version MD43 conservait correctement `pending_native_request=1`, mais laissait l'utilisateur réentrer dans Mercury en appuyant sur `SHIFT+BPF`, voire ouvrir les réglages avec `SHIFT+HPF`, **avant même que la demande native soit acceptée**. Cette réentrée contredit l'obligation de terminer le retour à Korg avant une nouvelle session Mercury.

Un nouveau test `tests/test_md44_native_pending_reentry.c` échoue **sur le code MD43 non modifié** lors de l'assertion `screen == MD_KORG` après un `SHIFT+BPF` pendant la demande refusée. Cet échec a été reproduit.

## Modification ciblée

- `src/md43_platform_port.h` : ajout d'un octet `blocked_reentry_down` dans la structure de *portage simulé*, pas dans l'état embarqué `md25_state`.
- `src/md43_platform_port.c` : lorsque `pending_native_request=1` et l'interface est Korg, les combinaisons `SHIFT+LPF/HPF/BPF` sont absorbées, avec suivi du `DOWN/UP`. L'absorption du `UP` persiste même si `request_native()` est acceptée entre le `DOWN` et le `UP`.
- `tests/test_md44_native_pending_reentry.c` : test de deux refus successifs, des raccourcis bloqués, d'une acceptation ultérieure et de la réentrée possible après le relâchement de la touche.
- `tests/build_v29_2.sh` et `tests/run_md44_host.sh` : intégration du test à la suite et exécution ciblée.

La modification concerne seulement le port simulé MD43, pas la chaîne Korg `md30`/`md31`. Aucun nouveau visuel, menu, preset, réglage, LFO ou module DSP.

## Résultats vérifiés dans cette session

- **Rouge avant correctif** : assertion `screen == MD_KORG` échouée sur MD43 d'origine.
- **Vert après correctif** : `MD44 PASS` sous Clang/ASan/UBSan.
- Test de portage MD43 d'origine : `MD43 PASS`, images identiques sur huit presets dans les deux **fausses** plateformes.
- `bash tests/build_v29_2.sh` : neuf programmes fonctionnels hôte passés et compilation/édition de liens ARM freestanding réussie. Les tests incluent MD42, lequel confirme un **défaut connu non réparé**, et non un acquittement SPI.
- Nouveau lien ARM (recherche) : `__md30_core_start=0xC01D0000`, `__md30_core_end=0xC01D88CC`, `md30_callback_bridge=0xC01E0000`, `__md30_bridge_end=0xC01E0014`. Pas de section `.bss` ni de symbole non résolu selon le script de build.
- Audit Korg MD42 en lecture seule réussi sur les deux `.VSB`, 8 assertions ciblées par firmware. La fonction native de transmission ne propage pas l'état de la fonction d'I/O ; aucun acquittement matériel n'est prouvé.
- Empreintes SHA-256 vérifiées sans modification des originaux :
  - custom `81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03`
  - backup `06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052`

## Limites à ne pas gommer

`request_native()` retournant 1 signifie seulement **demande acceptée**, pas « 1024 octets affichés », pas « SPI terminé ». MD44 évite une réentrée lorsque la demande est explicitement refusée. **MD44 ne résout pas le défaut d'acquittement MD42.** La plateforme, son ordonnanceur, ses identifiants de touches réels et son comportement SPI restent simulés.

La zone RAM `0xC01D0000..0xC01E1000` est `FF` dans les firmwares analysés, mais sa disponibilité à l'exécution et pendant l'audio n'est pas démontrée. La méthode de récupération sans JTAG reste inconnue. **Aucune image `SYSTEM.VSB`, aucun patch Korg installable, aucun flash n'a été produit.**

## Reproduire sur Linux / WSL

```bash
bash tests/run_md44_host.sh
bash tests/run_md43_host.sh
bash tests/build_v29_2.sh
python3 tools/md42_audit_native_send_readonly.py '/chemin/user_custom.VSB' '/chemin/user_backup.VSB'
```

Ne jamais renommer `build/arm/md31_RESEARCH_ONLY.elf` en `SYSTEM.VSB`.
