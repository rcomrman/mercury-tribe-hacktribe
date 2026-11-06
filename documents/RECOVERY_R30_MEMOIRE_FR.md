# R30 — carte mémoire et limites

| Zone | Occupation observée | Conclusion |
|---|---|---|
| `C0000000..C0200000` | image applicative de 2 MiB chargée depuis VSB | aucun espace code libre, chargeur ou droit d'écriture démontré |
| `C0200000..C03167A8` | réservations de piles tâche 1 à 10, table R11 | réservé ; valeur de pile restante et overlap avec autres usages à vérifier |
| `C031B310..C031B70F` | source graphique, 1 024 octets | partagé, non disponible |
| `C031B710..C031BB0F` | shadow, 1 024 octets | partagé, non disponible |
| `C031BB10..C031BB1F` | rectangle natif | occupé ; ne pas traiter comme canari universel |
| `C031BB2C` et suivants | descripteur LCD et handles | occupé, durée de vie et tous auteurs à établir |
| `C03404AC`, `C03404C0`, `C069...` | heap/globales/gestionnaires identifiés R2–R20 | occupation dynamique et alias non exhaustifs |
| RAM audio, piles IRQ/FIQ, DMA, caches/MMU | zones et attributs non suffisamment caractérisés | **aucune zone libre ou inoffensive démontrée** |

Les réservations exactes des dix piles sont dans
[`RECOVERY_R11_TASK_MAP_FR.md`](RECOVERY_R11_TASK_MAP_FR.md). Les adresses du
banc Linux ne définissent pas le plan physique de l'instrument. `.text` V30
12 512, `.rodata` 732 et `.bss` 5 372 octets dans R26 concernent un ELF de
rendu et sa fixture ; le pool R12 comporte 3 072 octets de frames et 40 octets
de métadonnées. Le bridge possède déjà des buffers : éviter tout double compte.
La pile locale maximale déclarée 328 octets ne borne pas la pile imbriquée.
Code d'adaptation, quatre LFO, UI, piles, alignement et instruments de mesure
ne sont pas tous inclus dans l'ELF de rendu. QEMU ne fournit ni cycles ARM réels
ni réserve mémoire, marge CPU/audio ou temps LCD.
