# Mercury Dust — MD45, revue du retour de Claude et préaudit ABI ARM

**Date : 1 novembre 2026. Lecture seule / sources de laboratoire. Aucun firmware installable.**

## Conclusion

Le retour de Claude identifie des angles morts importants : absence de sauvegarde complète de flash, tests ARM de bout en bout non réalisés, méconnaissance du chargeur secondaire, risque du patch en l'absence de récupération. Le code MD44 reste non branché matériellement.

Cette revue ne constitue PAS une version MD45 du moteur. Aucun fichier C/ARM Mercury n'a été modifié, aucun .VSB n'a été écrit.

## Contrôles réalisés directement sur les fichiers utilisateur

- Les deux VSB font **2 097 408 octets** (0x100 + 0x200000).
- SHA256 user_custom : `81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03`.
- SHA256 user_backup : `06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052`.
- Les **256 octets d'en-tête sont identiques**. Cela ne démontre PAS que l'en-tête ne comporte aucun mécanisme de validation ; la validation exacte reste à comprendre.
- Seulement **142 octets de l'application diffèrent** entre ces fichiers. Ils ne sont pas équivalents au dump de l'intégralité de la flash.

## Vérification statique des 3 relais ARM de MD44

Analyse directe de `md31_RESEARCH_ONLY.elf` compilé par Clang en ARMv5TE / ARM926EJ-S : `30/30` vérifications ciblées réussies (voir JSON), comprenant les opcodes de sauvegarde/restauration, les destinations BL et les littéraux originaux.

- `md30_callback_bridge` : sauvegarde `r0-r3,r12,lr` (24 octets), appelle `md30_callback_visit`, restaure ces registres et saute en **ARM** vers `0xC002A71C`.
- `md20_key_veneer` : sauvegarde les mêmes six registres, appelle `md23_route_key`, teste son retour, restaure les entrées et transfère soit vers `0xC00839F0`, soit vers `BX LR`.
- `md31_compare_veneer` : sauvegarde `r4,lr` (8 octets), appelle `md31_compare_visit`, restaure `r4` et retourne via `pc`.
- Avec une **pile initialement alignée sur 8 octets**, ces sauvegardes conservent l'alignement au moment des appels C. Contrairement à une ancienne hypothèse, 24 est bien divisible par 8.

**Attention :** ce sont des observations d'opcodes et de conventions supposées. Cela ne valide ni le mode d'entrée ARM/Thumb depuis Korg, ni l'état de SP à l'entrée, ni l'ABI réelle des appels, ni les effets d'un contexte IRQ, ni les sauvegardes dynamiques de `r4-r11` par tous les appels en C. QEMU n'est pas installé dans cet environnement ; aucun test d'exécution ARM n'a été revendiqué.

Pour reproduire ce préaudit à partir de l'ELF généré par MD44 :

```bash
python3 md45_static_abi_audit.py chemin/vers/md31_RESEARCH_ONLY.elf --output resultat.json
```

Avec les deux VSB optionnels :

```bash
python3 md45_static_abi_audit.py chemin/vers/md31_RESEARCH_ONLY.elf --custom chemin/user_custom.VSB --backup chemin/user_backup.VSB --output resultat.json
```

## Comparaison raisonnée avec les propositions de Claude

### Récupération sans JTAG

La page *Debrick* de bangcorrupt documente une récupération par accès direct à la mémoire flash, distincte du JTAG, mais décrit aussi des difficultés de fiabilité et de corruption du bootloader. Ce n'est donc ni une récupération garantie, ni un geste sûr à faire sans équipement/compétences. Dans le projet, une démarche encadrée par un spécialiste reste nécessaire avant un premier flash expérimental.

Source : https://github-wiki-see.page/m/bangcorrupt/hacktribe/wiki/Debrick

### Chargement de l'application

Le boot ROM lance un SBL en RAM interne `0x80000000`, et le SBL charge l'application en RAM externe à `0xC0000000`. **La taille réelle de la copie et les usages heap/DMA de `0xC01D0000..0xC01E1000` ne sont pas démontrés.** Une absence de référence statique ne prouve pas une absence d'écriture à l'exécution.

### Pointeur callback LCD

La modification d'un littéral dans une image de firmware est une hypothèse plausible. Mais elle ne suffit pas : l'initialisation peut avoir copié la valeur, et le contrat de tâche, l'IRQ, l'alignement, la durée d'exécution et la présence mémoire de Mercury restent à vérifier. Aucun patch VSB n'a été créé.

### ACK LCD/SPI

Il est raisonnable de distinguer fiabilité visuelle pragmatique et vraie confirmation physique SPI. La réparation d'un écran perdu par répétition des trames peut être acceptable dans un prototype, mais **ne prouve pas l'innocuité du hook ni la restauration à chaque transition**. MD42 reproduit explicitement le défaut d'acquittement de MD41.

### OmniTribe

Le site `https://omnitribe.org/` annonce un noyau à modules chargés depuis SD, des hooks sur les notes/ticks et des pages de menu. C'est une **déclaration du porteur du projet**, pas un SDK exécutable vérifié par notre équipe. Le site distingue prototypes mesurés, simulations et éléments à venir ; aucune API Mercury compatible n'a été démontrée. La couche MD43 est uniquement un simulateur.

## Priorités à remettre à Claude

1. Fournir un harnais **QEMU ARM926EJ-S réellement exécuté**, avec stubs C et test des registres `r4-r11`, `SP`, `LR`, arguments et retour des trois relais, y compris cas pris et non pris du bouton.
2. Examiner la routine de chargement du SBL et la représentation effective de l'application, avant d'attribuer une zone RAM libre ; différencier chargement et disponibilité durable.
3. Vérifier le format d'en-tête VSB et ses contraintes de validité à partir des scripts officiels Hacktribe, en lecture seule.
4. Définir une méthode de récupération matériellement réaliste avec expertise et sans suppositions. **Pas de canari ni de hook à flasher à ce stade.**
5. Pour OmniTribe, obtenir une SDK ou documentation de module effective et la faire tourner dans un environnement de développement, avant toute affirmation de compatibilité.

## À communiquer sans ambiguïté

- **Dernière version du code Mercury : MD44**, pas MD45.
- MD45 est un audit indépendant/statique et une préparation de questions pour Claude.
- Aucun test sur l'instrument, aucun QEMU dans cet environnement, aucune garantie de mémoire libre et aucun débrickage prouvé.
- Préserver la V30 Groove, les 8 presets, les 12 paramètres globaux, les raccourcis et les IFX personnalisés. Les quatre mini-LFO restent gelés.
