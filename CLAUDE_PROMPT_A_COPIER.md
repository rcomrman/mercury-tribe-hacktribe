# Message à envoyer à Claude avec les sources

Je développe **Mercury Dust** pour une **Korg Electribe 2 Sampler avec Hacktribe**. Je joins `MERCURY_DUST_MD44_SOURCES_ET_PASSATION_SANS_FLASH.zip` et je te demande de lire **en priorité** `PASSATION_POUR_CLAUDE_MERCURY_DUST_2026-11-01.md`, puis `MD44_RAPPORT_FR.md`, `MD43_RAPPORT_FR.md`, et les sources `src/` / tests `tests/`.

**Ne recommence surtout pas** les visuels (référence V30 Groove corrigée), les 8 presets, les 12 paramètres globaux ou les menus. Les paramètres par piste sont seulement masqués, les quatre mini-LFO au total sont gelés. Tous les tests actuels sont sur ordinateur ; aucun firmware Mercury n'a été installé.

Je voudrais une **revue technique indépendante** avec des résultats vérifiables, par ordre :

1. Examiner `md30_lcd_gate.c`, `md31_lcd_comparator.c`, `md25_visual_boot.c` et les relais assembleur : identifier une faille concrète de concurrence, d'ABI ou de restauration, avec reproduction si possible. Ne pas prétendre connaître le contexte IRQ/tâche réel.
2. Proposer une démarche **lecture seule / hors appareil** pour clarifier la carte mémoire, le chargement ARM et la coexistence avec l'audio. Ne pas considérer des octets `FF` du `.VSB` comme une preuve de RAM disponible.
3. Réévaluer la chaîne LCD native et le défaut MD42 : le statut d'I/O de bas niveau n'est pas remonté ; distinguer copie des tampons, mise en file, transmission et affichage réel. N'invente pas d'ACK SPI.
4. Examiner le chemin des boutons physiques, leurs appuis/relâchements et le verrou MD44. Les codes des touches ne sont PAS confirmés sur l'instrument.
5. Évaluer si une future API officielle OmniTribe pourrait offrir des points d'entrée documentés, **sans inventer de SDK**, et distinguer Omni-ROMs et noyau OmniTribe.
6. Suggérer un **premier essai réellement récupérable**, ou expliquer précisément pourquoi ce n'est pas encore possible **sans JTAG**.

Je n'ai pas de connaissances en assembleur et je n'ai pas de JTAG ; je possède une SD Hacktribe et deux fichiers VSB de sauvegarde (empreintes dans la passation). **Ne produis aucun fichier flashable, ne touche pas aux VSB originaux et ne propose pas de flash expérimental tant que la récupération n'est pas démontrée.**

Pour chaque proposition, sépare : (a) fait établi par le code ou les binaires, (b) hypothèse, (c) preuve manquante, (d) test reproductible. Si tu trouves un bug, écris le test qui échoue avant correction puis réussit après, plutôt que multiplier les audits de signatures.
