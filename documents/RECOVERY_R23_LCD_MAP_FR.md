# R23 — carte LCD avant shadow

Le scan ARM identique des deux VSB trouve un appel direct de `C0015AB4` depuis
`C0016084`, huit appels de `C0015DD0` depuis `C00298E8`, `C00299B4`,
`C00299C4`, `C002AC4C`, `C002AC5C`, `C0038BC4`, `C00603F0`, `C009A8F0`, et
deux appels de `C0015FA0` depuis `C0015E58` et `C0015F38`.

`C0015AB4` compare une page de 128 octets et copie la source modifiée dans
`C031B710` avant son retour. Le dispatcher `C0015DD0` positionne la demande avec
l'opcode 2 ; l'opcode 3 appelle le worker. Le worker consomme ensuite les
handles du descripteur. Aucun retour observé ne constitue un ACK physique LCD.

La frontière la plus précoce candidate est donc en amont de `C0015AB4`, auprès
de tous ses demandeurs. Elle n'est pas commune démontrée : appels indirects,
diagnostics, accès calculés, IRQ/FIQ et DMA restent hors domination statique.
