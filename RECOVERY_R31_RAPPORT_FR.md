# R31 — frontière de contrôle LCD

## Décision

**Aucune frontière suffisamment complète pour un module natif sûr n'est
démontrée.** Un arbitre est viable dans une fixture où tous les participants
coopèrent ; il reste vulnérable à un seul auteur qui le contourne. La meilleure
voie à conserver est le rendu privé et une intégration en laboratoire à
propriété explicite, avec suspension lors d'une demande Korg. L'exclusivité et
l'installation dans Hacktribe restent non autorisées.

## Graphe et points candidats

La [carte des chemins et matrice](documents/RECOVERY_R31_COUVERTURE_FR.md)
reprend les domaines R13 et R30. Les chemins identifiés comprennent la tâche UI,
le worker périodique, progression, initialisation, diagnostic, comparateur
direct, contrôle LCD, primitives de lecture et d'écriture. Les contextes,
callbacks, appels indirects et adresses calculées ne sont pas tous résolus.

Dans un graphe borné de **12 chemins sélectionnés**, une énumération complète
trouve huit ensembles minimaux de six points. C'est un minimum mathématique du
modèle de listes : il n'établit ni dominance globale, ni prise de possession,
ni couverture d'une transaction entière. En particulier une garde au
comparateur intervient après les modifications de source de certains chemins.
La preuve et les ensembles sont dans `reports/recovery_r31/coverage.json`.

## Prototype et contre-exemple

Le prototype hôte réutilise sans modification le coordinateur séquentiel R13
et le triple buffer R12. Une demande Korg et une lecture arrivant pendant une
composition sont différées ; une réentrée est refusée ; la lecture admise voit
la frame complète. Une écriture non participante pendant une lecture modifie
néanmoins l'image : le test la détecte. Ces entrelacements sont simulés
séquentiellement ; il n'y a ni atomique, ni ordonnanceur natif, ni synchronisation
IRQ/FIQ/DMA, ni installation de hook.

Une variante sans exclusivité globale suspend les nouvelles compositions
Mercury dès qu'un propriétaire Korg est demandé, puis attend la fin des emprunts
avant de restituer l'image. Elle réduit les exigences de cohabitation visuelle,
mais nécessite encore notification fiable, arbitrage des accès en cours et
absence de chemins non participants. Ces préconditions restent à démontrer.

## EXIT et architectures

Le vérificateur R31 relit les captures R29 : EXIT différé suivi d'une
restauration de huit pages passe dans les 14 scénarios validés ; deux arrêts
de faute restent bloqués. Ces preuves sont celles de R29, sans nouveau rejeu
ARM. Un worker bloqué dans l'attente SPI peut empêcher le retour ; aucun timeout
ou mécanisme d'annulation natif sûr n'est prouvé.

| Architecture | Décision | Raison |
|---|---|---|
| Rendu privé, aucun accès LCD natif | conserver | faible couplage ; aucun affichage réel encore |
| Fenêtre coopérative avec reprise Korg | poursuivre en laboratoire | testable, mais autorité globale et notification non démontrées |
| Plusieurs contrôles candidats | recherche statique uniquement | minimum borné, non dominance ni couverture des aliases |
| Exclusivité déclarée sans médiation des non-participants | rejeter | contre-exemple d'écriture pendant lecture |

Pour continuer : caractériser les auteurs réels et leurs intervalles, prouver
la notification de reprise Korg, inventorier IRQ/FIQ/DMA et disposer d'une
primitive de drain avec restauration vérifiable. Si ces contrats ne peuvent
pas être établis, conserver la sortie privée ou rechercher une interface
graphique officiellement autorisée. L'absence de preuve ne démontre pas qu'une
solution physique est impossible.

## Reproduction

`bash tests/run_recovery_r31.sh` calcule le minimum du graphe, compile et
exécute le prototype hôte, vérifie indépendamment la minimalité puis relit les
captures R29. Les deux VSB ne sont ni nécessaires ni modifiés pour ce rejeu.
Aucun flash, firmware installable ou essai matériel.
