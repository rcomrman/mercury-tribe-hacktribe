# MERCURY DUST V29.4 — FUSION A + B ET AUDIT ARM (SANS FLASH)

**31 octobre 2026. Aucun firmware utilisateur n'a été créé ni modifié. Aucune installation sur l'Electribe.**

## Fichiers d'origine vérifiés (SHA-256)

- Branche B : `55cf9c393774a1b2201321d85b4e3f83073f37dfb885ce30595fc77075ce152f`
- Firmware personnalisé : `81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03`
- Firmware sauvegarde : `06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052`

Base : branche A « CAVE ET RESTAURATION » de la passation fournie.

## Modifications intégrées (pas de nouvelle fonction artistique)

- Placement A conservé : cœur ARM à `0xC01D0000`, relais callback à `0xC01E0000`.
- Branche B : API `md25_state_intact()` pour vérifier `magic` et `tail_guard`; rejet par comparateur si état non fiable.
- Branche B : `md23_panel_forget_untrusted()` pour abandonner la passerelle des touches sans déréférencer une structure UI suspecte.
- Branche B : coupure du relais `md30` si l'état interne se désarme, notamment après trou d'horloge supérieur à 250 ms.
- Réconciliation A/B : demande de rafraîchissement Korg **au prochain rappel LCD**, avec maintien en attente si le dispatcher n'est pas disponible. La variante B avait effacé la demande même en cas d'échec ; ce comportement n'a **pas** été repris.
- Renforcement supplémentaire : un événement de touche reçu **après désarmement**, lorsque les sentinelles sont corrompues, détache aussi la passerelle sans lire ses pointeurs. Le test couvre ce cas.
- Les 8 presets, 12 paramètres globaux, menus, réglages par piste masqués, mini-LFO gelés et référence V30 n'ont pas été refaits.

## Tests exécutés ici

- Host Clang ASan+UBSan : `test_md30_lab`, `test_v28_global`, `test_md31_buttons_lcd`, `test_md32_timeout_restore` — **tous PASS**.
- Liaison ARM926EJ-S (`armv5te`, soft-float) : **0 symbole non résolu**, **0 `.bss`**, relais callback vers l'original toujours présent.
- Audits statiques : **28/28** pour chaque VSB (56/56 au total, contrôles répétés sur chaque image).
- Mutations statiques sur copies en mémoire : **14/14** détectées (13 substitutions + 1 troncature).
- Audit ARM indépendant ciblé : **17/17 instructions** vérifiées pour chacun des deux VSB.
- Scénarios host de régression : sentinelles `magic` et `tail_guard`, comparateur natif en repli, coupure du relais, restaurations après timeout, défaut temporaire du dispatcher et requête de redessin différée, événement de touche sur état corrompu déjà OFF.

**Ces chiffres n'impliquent pas de sécurité sur l'instrument réel.** Les preuves `MD25_REQUIRED_PROOF` sont injectées par le simulateur : ne jamais les traiter comme une preuve matérielle.

## Nouveaux constats statiques ARM sur les deux VSB

1. L'adresse `0xC002A970` contient **un littéral en lecture seule dans le flux de code**, de valeur `0xC002A71C`, et non le pointeur d'un champ d'objet déjà présent en RAM. À `0xC002A918`, une instruction `LDR r3, [pc,#0x50]` charge le littéral ; `0xC002A928` fait `STR r3, [r0,#0xC]`, inscrivant l'adresse du rappel dans **une structure allouée** pendant l'initialisation `0xC002A8D4`. À `0xC002A80C..0xC002A810`, le mécanisme de tick charge `[r0,#0xC]` puis fait `BLX r3`.
2. La configuration du tick contient `MOV r5,#20` à `0xC002A8F8`. Cette valeur représente un **rechargement de compteur d'appels** ; elle ne garantit aucune période en millisecondes.
3. La routine d'initialisation du scheduler `0xC002A8D4` est appelée directement aux **deux sites candidats `0xC002A984` et `0xC002AA1C`** dans chacune des deux images. Aucun de ces sites n'est déclaré validé comme point d'insertion Mercury : il faut remonter le graphe d'initialisation et les allocations.
4. Le callback Korg `0xC002A71C` prépare opcode 3 avant de sauter au dispatcher LCD `0xC0015DD0`. L'opcode 2 écrit l'indicateur « dirty » à l'offset `+5` du descripteur ; cet ordre est cohérent avec la simulation, **mais le timing et le contexte réel n'ont pas été mesurés**.
5. Le comparateur Korg `0xC0015AB4` détermine la page (`page * 128`), charge l'image LCD source depuis **`0xC031B710`** et le shadow depuis **`0xC031B310`**, compare 128 octets via l'appel à `0xC00097A8` puis **copie 128 octets depuis la source vers le shadow** via `0xC000985C`. Après un retour « changed », la boucle à `0xC00160A0` appelle `0xC001613C`, chemin natif de traitement d'une page. La preuve de la terminaison du transfert SPI physique manque.
6. Décodage panneau : `0xC002814C` est appelé au site `0xC002A4DC` d'après la recherche de branches directes. Ce constat **ne confirme ni SHIFT/BPF/HPF ni le code EXIT**.

## Points bloquants encore ouverts

- **Initialisation ARM** : aucune preuve d'un appel effectif à `md25_begin`/`md30_arm_for_verified_lab` dans Korg ni d'un contexte non-IRQ ; le code de recherche n'est pas amorcé par une véritable tâche de la machine.
- **Mémoire** : `FF` en fichier et zéro pointeur littéral statique dans la réservation ne garantissent pas l'absence d'utilisation par heap, pile, audio, DMA ou chargement du firmware en mémoire.
- **LCD / SPI** : les fonctions et branches natives sont identifiées, pas leur ordonnanceur ou leur caractère non réentrant à l'exécution.
- **Boutons** : codes et appui/relâchement physiques non testés ; le code EXIT réel est inconnu.
- **Récupération** : pas de procédure de débrickage vérifiée pour une Electribe sans JTAG. Une carte SD et une sauvegarde PC n'en constituent pas une.

**Décision : rester sur les sources/tests/forensics. Aucun `SYSTEM.VSB`, aucun patch binaire à appliquer, aucun essai SD ou flash.**

## Reproduction en lecture seule (Linux ou WSL)

```bash
bash tests/run_merged_v29_4.sh /chemin/user_custom.VSB /chemin/user_backup.VSB
python3 tools/md34_arm_inspection_readonly.py /chemin/user_custom.VSB /chemin/user_backup.VSB
```

Le script ne produit que des ELF ARM **de laboratoire** dans `build/arm` et des rapports dans `reports/`. Il n'écrit jamais les VSB originaux. Ne jamais utiliser l'ELF de recherche comme firmware de l'instrument.
