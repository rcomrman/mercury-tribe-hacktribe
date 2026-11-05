# R23.2 — autorité du worker LCD et restitution Korg

**Décision : intégration matérielle NO GO ; transfert temporaire d'autorité NON
DÉMONTRÉ.** Suspendre un appel du worker avant son exécution préserve le shadow
dans la fixture sous absence d'autres auteurs. Ce résultat n'établit ni une
frontière native exclusive, ni la fin des transferts, ni le retour physique à
Korg. L'audio et le séquenceur n'ont pas été testés sur instrument.

## Chemins et degré de certitude

Dans les deux images, `C0015E58` et `C0015F38` sont des appels directs ARM vers
`C0015FA0`. `C0016084` appelle `C0015AB4` dans le worker ; `C00160A0` appelle
`C001613C` lorsque le résultat du comparateur est non nul. Le scan R23.1 trouve
12 candidats `B` ou `BL` vers `C0015DD0`, dont le branchement terminal
`C008370C` après le tick UI ; ce comptage ne ferme ni les appels indirects, ni
Thumb, ni les pointeurs calculés. Les plages critiques désassemblées sont
identiques entre les deux VSB ; les instructions sont conservées dans
`reports/recovery_r23_1/lcd-disassembly.txt`.

`C0015AB4` compare puis appelle la copie à `C0015B38`, avant le sender. Les
accès directs, tables virtuelles, IRQ/FIQ, DMA et autres auteurs du shadow ne
sont pas exhaustivement cartographiés : **couverture complète NON DÉMONTRÉE**.
Les traces R9 et R23.1 montrent des chemins exécutés, pas tous les chemins.

## Suspension et demandes

Le worker sort si descripteur +4 n'est pas égal à 1. Un paramètre +12 en attente
est traité avant le test de la demande graphique +5. Le scan des huit pages
requiert +5=1 ou force=1 ; une fois entré, le comparateur traite toute force non
nulle comme un forçage. Le worker ne remet pas +5 à zéro dans son corps.

| Option | Ce qu'elle peut obtenir en fixture | Blocage réel |
|---|---|---|
| A — avant dispatcher | empêcher certaines demandes | autres appels et auteurs non dominés |
| B — avant worker | éviter cette comparaison tant qu'il n'entre pas | worker déjà engagé, appels et transfert concurrents |
| C — début worker | frontière avant scan sur chemin étudié | paramètre +12 et contrôle natif non autorisé |
| D — garder les demandes | +5 demeure à 1 | quatre demandes deviennent une seule valeur ; ordre et nombre perdus |

La suspension du cas 0 est l'omission explicite d'un appel **dans le banc**,
pas un hook ni une primitive Korg. Elle ne prouve aucune cessation globale.

## Descente vers le matériel

`C001613C` utilise les handles du descripteur +0x18 (GPIO), +0x1c (SPI) et
+0x14 (contexte de délai). `C0016160` appelle `C0016C18`, première frontière
GPIO du chemin ; avec le handle de fixture nul, la faute observée est `0xBC`.
R9 obtient la base native 0x01E26000 et observe la faute 0x01E260BC en absence
de périphérique émulé. La fonction envoie les commandes par `C00160C4`, attend
par `C0015CDC`, obtient le shadow via `C0015A60`, puis `C0016100` appelle
`C001851C` avec le handle SPI et 128 octets. Elle attend de nouveau et appelle
un délai. `C0015CDC` boucle sur `C00117C8`, qui lit le mot SPI +0x10 et teste
0x200. Le sens matériel complet de ce bit, la réception effective LCD, les
interruptions et le DMA ne sont pas établis. Un retour de fonction ou du
dispatcher n'est pas un ACK physique. Aucun compteur global fiable de drain
n'est démontré ; les chemins d'erreur peuvent eux-mêmes solliciter le LCD (R9).

## Nouvelles expériences ARM

Quatre scénarios par VSB, code original RX, mémoires anonymes isolées et aucune
réponse MMIO inventée. Tous les records sont identiques entre VSB et un second
vérificateur relit les octets de source et shadow.

| Cas | Observation |
|---|---|
| Demande avant suspension | opcode 2 laisse +5=1 ; source modifiée et shadow ancien tant que le banc omet le worker |
| Quatre demandes | +5 vaut toujours 1 : indicateur coalescé, pas quatre entrées comptées |
| Deux pages modifiées | page 1 copiée puis faute 0xBC ; page 3 encore ancienne dans le shadow |
| Comparaison répétée | la première copie une page et retourne 1, la seconde retourne 0 sans preuve de transmission |

Huit exécutions, dont deux fautes attendues, plus régression des douze cas
R23.1. Les retours tardifs et EXIT en transfert sont étudiés dans les traces
abstraites R23.1 ; **aucun transfert physique achevé n'a été exécuté**. La
restauration d'un LCD réel et une faute pendant transfert physique sont NON
EXÉCUTÉES. Le modèle ne permet pas d'affirmer qu'un défaut est seulement visuel.

## Automate et architectures

`KORG_ACTIVE → TRANSITION_TO_MERCURY → MERCURY_ACTIVE →
TRANSITION_TO_KORG → KORG_ACTIVE`, avec `FAULT`. Chaque changement d'autorité
exige le blocage de tous les nouveaux auteurs et la fin démontrée de tous les
transferts. EXIT demande la transition ; il ne rend pas immédiatement le LCD.
Le retour exige image Korg complète, cohérence shadow et ACK de son transfert.
Aucune primitive native de drain, invalidation et ACK complet n'a été établie.

| Architecture | Avantage | Risque et condition nécessaire |
|---|---|---|
| A — suspension worker, voie Mercury séparée | évite son scan dans la fixture | autres auteurs et transfert engagé ; voie Mercury et drain à démontrer |
| B — arbitre commun, propriétaire explicite | peut sérialiser les demandes dans un modèle fermé | tous les producteurs doivent participer ; file, ACK et restauration à établir |

Ni A ni B n'est actuellement sélectionnable pour l'instrument. Les 10 FPS
réduisent la fréquence des demandes Mercury, sans établir l'exclusivité ni
libérer la preuve de non-perturbation audio.

## Verdicts et reprise

Couverture des auteurs, suspension effective, drain, autorité Mercury et
restauration EXIT : **NON DÉMONTRÉS**. Intégration matérielle : **NO GO**.
Le prochain travail utile est de qualifier les auteurs et le contrat du bit SPI
et du chemin d'erreur, puis de prouver une invalidation et un transfert complet
acquitté. Un tel travail n'autorise pas en lui-même un essai matériel.

Reproduction : `PATH=/workspace/mercury-tools/bin:$PATH bash
tests/run_recovery_r23_2.sh custom.VSB backup.VSB`. Aucun VSB modifié, firmware
installable, hook, flash ou essai sur l'Electribe.
