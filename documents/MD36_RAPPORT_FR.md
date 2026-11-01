# Mercury Dust MD36 — consommation de la table des tâches ARM et initialisation LCD

**Date : 31 octobre 2026 · Analyse statique reproductible sur les deux firmwares d'origine · SANS FLASH**

## Périmètre

Suite du MD35. Aucun changement artistique ni fonctionnel de Mercury Dust, aucune modification des 8 presets, 12 réglages globaux, boutons de l'interface simulée ou 4 mini-LFO gelés. Aucune réécriture de firmware `.VSB`, pas de fichier `SYSTEM.VSB`, pas de branchement réel au matériel. Les deux fichiers utilisateurs n'entrent pas dans cette archive. La fusion V29.4 A+B a été **retestée telle quelle**, sans nouveau patch.

## Avancée 1 — code consommateur des dix descripteurs identifié

Les deux firmwares ont exactement la même séquence de branches ARM au démarrage :

```text
C0029874 : B  C0000110        chemin préliminaire de démarrage
C0000124 : BL C00000F4       initialisation du noyau/scheduler
C00000F8 : BL C00002B4       initialiseur de structures de tâches
C0000334 : LDR r3,[r6,#4]!  lit l'ordre de tâches 1..10
C0000340 : LSL r3,r3,#5      index * 0x20
C0000344 : ADD r4,r10,r3     adresse du bloc d'état d'une tâche
C000034C : ADD r3,r8,r3      adresse de son descripteur statique
C0000354 : STR r3,[r4,#8]   mémorise le descripteur dans l'état
C0000360 : BL C00003B0      initialise notamment la priorité
C000036C : TST r3,#2        teste le drapeau de démarrage immédiat
C0000378 : BL C00003D8      prépare conditionnellement une tâche
C0000410 : B  C00018F0      passe au gestionnaire de tâches
```

**Note :** le dernier `BL` est conditionné par le `TST` et une branche `BEQ`; il ne lance pas automatiquement les dix tâches. Seule la première entrée a le bit `2` dans son champ de drapeaux initial; les neuf autres ont zéro dans ce champ. Cela ne démontre pas quand ces neuf tâches sont activées ultérieurement.

## Avancée 2 — structure exacte des entrées affinée depuis MD35

La table commence à **`0xC00A37A8`**, et non au premier pointeur de fonction. Chaque descripteur a **32 octets** :

| Offset | Usage inféré à partir des instructions | Confiance |
|---|---|---|
| `+0x00` | drapeaux contrôlés via `TST #2` | forte, statique |
| `+0x04` | mot de métadonnées sauvegardé près du sommet de pile | observation forte, signification complète inconnue |
| `+0x08` | adresse de la fonction initiale de la tâche | forte, statique |
| `+0x0C` | octet lu puis enregistré comme attribut de tâche, possiblement priorité | lecture certaine, interprétation probable |
| `+0x10` | taille de région utilisée pour calculer son sommet | forte, statique |
| `+0x14` | début de cette région | forte, statique |
| `+0x18/+0x1C` | mots supplémentaires | rôle non élucidé |

L'ancienne adresse `0xC00A37D0` est bien **le pointeur de la fonction `0xC002AA34` de la deuxième entrée**, mais son descripteur commence à `0xC00A37C8`. MD35 décrivait les enregistrements à partir des fonctions, pas de leur début réel.

À `0xC00003E0/03E4`, le gestionnaire charge taille et début. À `0xC00003EC`, il additionne ces valeurs pour obtenir le haut de région; aux instructions `0xC00003F4` et `0xC0000400`, il écrit des éléments du contexte de tâche en fin de région. Cela indique très fortement des **zones de pile/contexte** plutôt qu'un simple inventaire de mémoire générique.

Les dix zones sont contiguës de **`0xC0200000` à `0xC03167A8`**. Le code de démarrage étudié à `0xC00296B0` dispose séparément d'une boucle de mise à zéro utilisant des bornes chargées à `0xC0029878` (`0xC0200000`) et `0xC002987C` (`0xC08A2940`). Cela n'établit pas que toutes les zones sont activement exploitées en même temps.

## Avancée 3 — initialisation du LCD pendant la tâche de démarrage

La première entrée de la table pointe vers `0xC002AB7C`. Dans cette fonction, les instructions suivantes sont présentes :

```text
C002AC44 : MOV r1,#2
C002AC4C : BL  C0015DD0  ; commande LCD 2, marquage à rafraîchir
C002AC54 : MOV r1,#3
C002AC5C : BL  C0015DD0  ; commande LCD 3, demande de traitement
```

Il s'agit d'un **lien statique vérifié entre la routine de démarrage référencée par la table et le dispatcher LCD**, en plus de la chaîne de callback LCD étudiée en MD34/MD35. Le moment exact de l'exécution, la synchronisation avec le SPI et le contexte IRQ/tâche n'ont **pas** été mesurés sur la vraie machine. Un hook placé au hasard dans ce démarrage pourrait notamment provoquer un rafraîchissement trop précoce.

## Zone mémoire Mercury : ce que nous savons et ignorons

- Zone choisie dans V29.4 A+B : `0xC01D0000..0xC01E1000`.
- Ces octets valent `FF` dans les deux images VSB étudiées, et la zone ne chevauche aucune des dix régions de tâches ci-dessus.
- La zone choisie **se trouve dans l'espace de l'image applicative** (`0xC0000000..0xC0200000`) et non dans les dix régions de tâches identifiées. Les écritures réelles du chargeur, la pile, les allocations dynamiques, l'audio, le DMA, les interruptions et la disponibilité après chargement sont encore inconnues.
- **Aucune preuve de liberté RAM au runtime ou d'absence d'interférence audio** ne découle de ces constats. Aucun point de patch/init sûr n'a été validé.

## Tests exécutés

- VSB personnalisé SHA-256 : `81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03`.
- VSB sauvegarde SHA-256 : `06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052`.
- **52/52 signatures par image** (104/104 vérifications statiques effectuées), incluant branches ARM, accès aux champs, table de 10 tâches, relation au démarrage LCD et zone de fichier.
- **18/18 altérations artificielles détectées**, toutes sur des copies en mémoire Python; les `.VSB` originaux n'ont pas été modifiés.
- Hashes identiques entre les deux images pour le code du consommateur de table et la table des tâches.
- Re-lancement de `tests/run_merged_v29_4.sh` dans le projet fusionné : **PASS** sur les tests hôte du moteur/menus, restauration simulée, relais ARM et audits **28/28 par VSB**, plus les **14/14 mutations** de V29.4. Journal conservé dans `md36_regression_v294.log`.

Les signatures ne prouvent **que les octets et les propriétés spécifiquement vérifiés**. Les mutations ne constituent ni une couverture complète ni un test de comportement sur l'instrument.

## Points ouverts après MD36

1. Relier le démarrage des tâches secondaires à l'exécution réelle de `0xC002AA34` et observer son contexte et sa cadence sur la machine, par une méthode de diagnostic non invasive et défendable.
2. Démontrer la coexistence RAM/CPU avec audio, DMA, heap et périphériques. Les constats de cette table ne suffisent pas à cela.
3. Terminer la recherche des codes physiques (dont EXIT) et de la propriété appui/relâchement, sans perturbation des fonctions Korg normales.
4. Vérifier un chemin de récupération réellement utilisable **sans JTAG** avant d'envisager un firmware expérimental.

**Décision : développement et audit PC uniquement. Ne pas flasher.**

## Reproduction

Python 3, sans paquet externe nécessaire :

```bash
python3 md36_scheduler_readonly.py /chemin/user_custom.VSB /chemin/user_backup.VSB > md36_resultats.json
```

Le script refuse les fichiers qui n'ont pas les SHA-256 attendus et produit uniquement un JSON. Les altérations des 18 tests sont locales en mémoire vive Python; il n'existe aucune écriture vers les entrées `.VSB`.
