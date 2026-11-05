# R23.4 — identification matérielle et restauration forcée

## Conclusion

Le firmware présente une correspondance précise avec le bloc SPI de la famille
Texas Instruments DaVinci/DA8xx, et la carte d'adresses publiée pour DA850
correspond aussi à son GPIO. **Le modèle exact du SoC de l'Electribe, le modèle
de contrôleur LCD et la signification documentaire du bit 0x200 restent NON
IDENTIFIÉS.** Cette correspondance ne prouve pas une identification physique.
Le forçage du comparateur peut demander huit pages même lorsque source et shadow
sont égaux, dans un banc ARM ; il ne prouve pas l'envoi ni la restauration du LCD.

## Sources et identification

1. [Linux v6.12, `da850.dtsi`, lignes 114–119, 620–628 et 741–745](https://github.com/torvalds/linux/blob/v6.12/arch/arm/boot/dts/ti/davinci/da850.dtsi#L114) : le bus DA850 est translaté sur `0x01C00000` ; SPI0 est à l'offset `0x41000` avec `compatible = "ti,da830-spi"`, et GPIO à l'offset `0x226000`. Les adresses résultantes, `0x01C41000` et `0x01E26000`, correspondent aux getters natifs documentés dans [R9](RECOVERY_R9_RAPPORT_FR.md).
2. [Linux v6.12, `spi-davinci.c`, lignes 58–60 et 86–96](https://github.com/torvalds/linux/blob/v6.12/drivers/spi/spi-davinci.c#L58) : le pilote définit `SPIFLG` à +0x10, `SPIDAT1` à +0x3C, `SPIBUF` à +0x40 et un masque `SPIBUF_TXFULL` bit 29. La même organisation d'offsets est observée dans le firmware aux fonctions `C00117C8` et `C001851C`.
3. [U-Boot, pilote DaVinci SPI, lignes 125–130](https://github.com/u-boot/u-boot/blob/master/drivers/spi/davinci_spi.c#L125) : attend l'effacement de `TXFULL` avant écriture. C'est une indication pour **ce pilote**, pas une preuve de la sémantique de `SPIFLG` bit 9 du matériel Korg.

Le `.dtsi` DA850 est une description du DA850, pas une nomenclature de
l'Electribe : elle ne permet pas de trancher entre variantes ni d'attribuer un
marquage exact au composant. Le dépôt consulté ne fournit pas de référence
fabricant identifiable de l'écran. La documentation TI consultable depuis ce
banc est limitée : l'accès à `ti.com` a retourné HTTP 403. Aucune fiche LCD ou
table de registre primaire n'a donc été vérifiée pour l'instrument.

## Cartographie des registres

| Adresse/offset firmware | Instructions | Rapprochement externe | Certitude |
|---|---|---|---|
| SPI `0x01C41000` | getter `C0016654` ; R9 | base SPI0 DA850 ci-dessus | même adresse, modèle exact non prouvé |
| +0x10, masque 0x200 | `C00117DC..17F4`, `C0015CF4..5D08` | offset `SPIFLG` DaVinci | bit 9 testé ; nom/sémantique documentaire inconnus |
| +0x3C | `C001862C` | offset `SPIDAT1` DaVinci | écriture logicielle observée, acceptation matérielle inconnue |
| +0x40 | `C001853C`, `C0018398` | offset `SPIBUF`, bit 29 TXFULL dans Linux | lecture Korg et interprétation Korg ne sont pas automatiquement identiques à Linux |
| GPIO `0x01E26000` | getter `C0016568` | GPIO DA850 calculé ci-dessus | même adresse, montage physique inconnu |

Linux mentionne aussi une activation DMA (`SPIINT_DMA_REQ_EN`, ligne 86), ce
qui établit une capacité du pilote comparé, **pas** l'usage de DMA par Korg ni
l'activité d'un transfert donné. Profondeur de FIFO, drapeau de bus réellement
vide, IRQ/FIQ et politique d'erreur sont non déterminés pour l'instrument.

## Quatre niveaux de fin

La boucle Korg teste `0x200` avant une écriture +0x3C ; une écriture ARM
exécutée ne prouve pas à elle seule l'acceptation par la FIFO. Un retour de
`C0015CDC` prouve seulement qu'une lecture a présenté ce bit à 1 dans le
contexte observé. La vidange FIFO et la fin de transmission sur le bus sont
NON DÉMONTRÉES. Aucun ACK LCD n'a été identifié ; son absence physique est
elle-même NON DÉMONTRÉE sans modèle et câblage de l'écran.

Si une documentation vérifie qu'il n'existe pas d'ACK LCD, la garantie visée
peut être conditionnelle : contrôleur configuré, données acceptées, FIFO et
registre de décalage vides selon leur contrat, temporisations et sélection du
LCD respectées, huit pages complètes transmises, aucune erreur ou concurrence.
Cela reste une **présomption de livraison sous hypothèses électriques**, pas
une confirmation indépendante de l'image effectivement affichée.

## Forçage et restauration

Nouveau test ARM : huit pages source=shadow sont comparées dans l'ordre, sur
chacun des deux VSB. Sans force les huit retours sont 0 ; avec force ils sont
1. Quatre processus QEMU et leurs snapshots sont identiques entre images ; un
vérificateur indépendant relit les records. Le sender n'est pas appelé.
La branche du worker qui exploite ces retours est décrite dans
[R23.1](documents/RECOVERY_R23_1_WORKER_FR.md), et R23.2 conserve le témoin
d'un shadow partiel après faute.

Une restauration fondée sur le shadow comme preuve d'affichage peut manquer
des pages : celui-ci avance avant la transmission. Une source Korg complète,
stable et acquise sous une autorité couvrant tous les auteurs constitue un
meilleur point de départ ; il faut encore forcer les huit pages, gérer une
interruption au milieu, puis attendre les états matériels contractuellement
nécessaires. La force comparateur ne prouve ni droit d'appel, ni atomicité de
la source, ni ACK. En cas de faute ou de transfert interrompu, aucune
réinitialisation ou reprise sûre n'est démontrée.

## Décision architecturale

| Choix | État | Dépendances |
|---|---|---|
| Suspendre le worker, voie Mercury séparée | recherche conditionnelle | couverture de tous les auteurs, drain, autre voie et restitution |
| Arbitre LCD commun | recherche conditionnelle | autorité sur tous les producteurs, file, exclusion et fin matérielle |
| Abandon de la prise de contrôle native | option raisonnable si ces contrats restent inaccessibles | conserver le rendu privé ; pas d'affichage Mercury démontré |

Les inconnues de modèle et de documentation sont potentiellement levables. En
revanche, aucun mécanisme logiciel ne pourra convertir un état de FIFO en ACK
d'écran si le matériel et le protocole ne fournissent pas cette information ;
une garantie conditionnelle de livraison serait alors le plafond justifiable.
La prise de contrôle matérielle reste **NO GO**.

Reproduction : `PATH=/workspace/mercury-tools/bin:$PATH bash
tests/run_recovery_r23_4.sh custom.VSB backup.VSB`. Aucun test physique,
écriture VSB, hook ou flash.
