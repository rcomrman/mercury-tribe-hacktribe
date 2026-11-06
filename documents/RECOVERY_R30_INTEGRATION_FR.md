# R30 — carte des points d'intégration candidats

Toutes les adresses concernent les deux VSB de référence. Le scanner R30 lit
32 octets par entrée et recense les branches ARM alignées ; les résultats
incluent potentiellement des données et ne recensent ni Thumb ni les appels
indirects. Le contexte s'appuie sur les missions citées, pas sur un hook posé.

| Besoin / entrée | Appelants et contexte | Contrat visible, risques et preuve |
|---|---|---|
| Boutons `C002814C` | `C002A4DC`, tâche 3 par chaîne R6 | Lit type/code/valeur ; code physique EXIT et validation complète inconnus ; R6 |
| Publication UI `C00839F0` | cinq branches candidates dans l'audit ; plusieurs producteurs R6 | Message copié dans queue, pas ACK d'exécution ; saturation, réentrée et multi-producteurs |
| Timer LCD `C002A71C` | callback indirect du compteur, tâche 2 R10/R11 ; aucun BL direct ne prouve son absence | Appelle dispatcher opcode 3 ; période réelle, IRQ et priorités variables inconnues |
| Cycle UI `C00836E4` | slot virtuel UI +0x18 après type 0 ; tâche 4 R7/R11 | Cycle complet puis opcode 2 ; tâche 2 peut préempter la composition selon R11 |
| Dispatcher `C0015DD0` | 12 branches B/BL candidates ; `C008370C` terminal | r0 descripteur, r1 opcode, r2 argument ; zéro n'est pas un ACK ; contournements init/diagnostic |
| Worker `C0015FA0` | `C0015E58`, `C0015F38` ; voies indirectes inconnues | r0 descripteur, r1 force ; accès LCD et attente non bornée ; R9/R23.1 |
| Transition de page `C006E8BC` | branches candidates `C006EF38`, `C0083724` | r0 gestionnaire, r1 ID page, r2 argument ; destruction possible, aucune touche EXIT physique prouvée |
| Composants annexes `C006EA10` | `C006F1F8` | charge +0x34/+0x38/+0x3c et appelle vtable +8 ; objets possédés, pas de slot libre prouvé R22 |

Aux frontières de fonction, la convention ARM du code et les instructions
effectives doivent être vérifiées, y compris registres préservés, SP aligné,
LR et indicateurs lorsque nécessaires. Aux points internes, les registres et
données vivantes sont propres à l'instruction ; aucune enveloppe universelle
n'est démontrée. IRQ/FIQ/DMA, alias et emprunts restent ouverts à chaque point.

## Source musicale

Les APIs Mercury acceptent `md15_clock`, `md15_note` et `md15_step`. Leur
utilisation R26 est synthétique. Aucun point Korg de BPM, PPQN, notes ou pas
n'est ici identifié avec durée de vie et cadence prouvées. Ne pas substituer
les événements de boutons ou le timer UI aux événements musicaux sans preuve.
