# R22 — interception LCD et mode exclusif

La composition écrit `C031B310`. `C0015AB4` compare par pages et met à jour le
shadow `C031B710`; l'opcode 2 de `C0015DD0` demande un travail, tandis que le
worker `C0015FA0` poursuit vers des handles et le transfert physique. Supprimer
un envoi après la copie du shadow crée un faux état « déjà transmis ». Renvoyer
un succès à ce point n'est donc pas justifié.

| Frontière | Avantage | Contrats manquants | Verdict |
|---|---|---|---|
| demande opcode 2 | avant worker | tous producteurs, valeur de retour, reprise | NO GO |
| worker `C0015FA0` | point commun observé | autres appelants, transfert engagé, IRQ/DMA | NO GO |
| appel SPI/driver bas | proche du LCD | ACK, cache, DMA, erreur et concurrence | NO GO |
| multiplexage avant comparaison | shadow cohérent possible | propriété globale de source et cadence | piste R23 |

À EXIT, une restauration sûre exige : bloquer les nouvelles publications,
drainer ou annuler contractuellement tout transfert engagé, reconstruire une
frame Korg complète, invalider explicitement le shadow, forcer un transfert
complet avec ACK vérifié, puis rendre l'autorité. Les preuves actuelles ne
couvrent aucune séquence atomique de ce type.

À 10 FPS, Mercury calcule et demande au plus dix frames par seconde. Cela réduit
son coût moyen et les conflits qu'il initie. Cela ne réduit ni le nombre des
auteurs Korg, ni une course pendant un transfert, ni IRQ/FIQ/DMA, ni le besoin
d'un ACK et d'une restauration complète.
