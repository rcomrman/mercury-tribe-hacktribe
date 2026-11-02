# Mercury Dust — R3 : transitions natives et restauration

## Objectif et résultat

Reprendre MD84–MD85 depuis R2, sans modifier les VSB ou le moteur. **La transition native page 25 → 29 fonctionne sur les deux originaux, avec et sans Mercury.** Huit scénarios par VSB ont les issues attendues ; 32 cycles supplémentaires Mercury → Korg sont vérifiés octet par octet sur chacun des deux VSB. Le programme ne produit qu'un ELF Linux/QEMU de recherche.

## Architecture étudiée

`C006E8BC` reçoit r0=gestionnaire graphique, r1=identifiant cible, r2=argument de fabrique. La fixture fournit un gestionnaire nul de 128 octets, avec page sortante à +16 et identifiant courant à +28. Les octets +24, +76 et +93 sont respectivement utilisés pour l'état du premier emplacement, une demande de redessin et un blocage d'entrée.

Le code : teste +93 ; traite les identifiants particuliers affectant +80 ; compare la cible à +28 ; appelle le destructeur virtuel +4 de l'ancienne page (sauf cas particulier identifiant 1) ; vide son pointeur ; appelle `C006E664` ; enregistre la page entrante, son identifiant et +76=1.

Les pages 25 et 29 sont construites par leurs fabriques et constructeurs Korg. La page 29 dessine « Undo! ». Le heap et l'initialisation graphique natifs établis en R2 sont réutilisés. Aucune routine de transition, fabrique, dessin, destruction ou allocation n'est remplacée.

Le dessin utilise toujours les 96 octets originaux du parcours de R2, **pas le cycle complet C006F178**. La mise à 1 de +76 est observée, mais son consommateur complet n'est pas exécuté. Une demande de redessin du gestionnaire ne doit donc pas être assimilée au redessin complet effectif dans ce banc.

## Hypothèses

1. La destruction puis le dessin de la page entrante suffisent à restaurer l'image : faux avec Mercury dans la fixture.
2. Un effacement natif dans la sortie Mercury peut rétablir l'image : confirmé dans les séquences testées.
3. Un effacement natif juste avant le dessin entrant peut faire de même : confirmé.
4. Un changement vers la même page recrée l'objet : faux ; le pointeur reste identique.
5. Le blocage +93 empêche la transition : confirmé.
6. La transition résout une destruction pendant parcours : faux ; la boucle R2 subsiste.

## Méthodologie et tests

Une référence indépendante est obtenue par construction native de la page 29 sur framebuffer effacé, dessin natif, puis sauvegarde des 1 024 octets. Cette référence n'est pas une capture historique ou matérielle.

| Cas | État/expérience | Résultat par VSB |
|---|---|---|
| 0 | Sans Mercury | Transition et image entrante identiques à la référence |
| 1 | Mercury, sortie sans effacement | Transition aboutie ; **91 pixels supplémentaires** par rapport à la référence |
| 2 | Sortie Mercury appelant C0015804 | 1 024 octets identiques à la référence |
| 3 | C0015804 avant dessin entrant | 1 024 octets identiques à la référence |
| 4 | Gestionnaire +93=1, puis déblocage | Première demande ignorée, pointeur/identifiant conservés ; demande suivante acceptée |
| 5 | Cible identique 25, puis 29 | Première demande conserve l'objet ; seconde réalise la transition |
| 6 | Politique d'effacement en sortie, 32 retours Mercury | Chacune des 32 images V30 et des 32 restaurations de page 29 est vérifiée sur les 1 024 octets |
| 7 | Page sortante marquée en parcours actif | Timeout externe à 2 s ; trace de la boucle C0060F3C |

Les canaris du framebuffer restent contrôlés par le support R2. Les callbacks de sortie et suppression Mercury sont natifs quant à leur appel, expérimentaux quant à leur implémentation. Les compteurs du heap laboratoire ne mesurent pas les allocations natives : aucune absence universelle de fuite du heap Korg n'est revendiquée.

## Analyse des échecs et restauration

Le cas sans effacement est conservé, et non corrigé artificiellement dans la référence. La destruction nettoie certaines zones natives mais la nouvelle page ne réécrit pas tout l'écran. Une transition réussie et un pointeur entrant valide ne garantissent donc pas une image identique à un démarrage propre.

L'appel original `C0015804` dans la sortie Mercury efface la source graphique à un moment où l'ancienne liste est détruite, avant la construction/dessin de la page entrante. Cette politique respecte les appels du destructeur et n'en contourne aucun contrôle. L'autre politique efface explicitement avant le parcours entrant. Les deux produisent une restauration exacte ici ; aucune propriété exclusive du framebuffer en concurrence n'est établie.

Le cas actif échoue pour la même raison qu'en R2 : la transition ne rend pas la destruction réentrante. La boucle ne relit pas l'état actif. Aucun patch de cette boucle n'est réalisé.

## Captures et traces

- [Séquence sans restauration](reports/recovery_r3/case1.gif).
- [Effacement en sortie Mercury](reports/recovery_r3/case2.gif).
- [Effacement avant dessin entrant](reports/recovery_r3/case3.gif).
- [Résultats détaillés](reports/recovery_r3/results.json).

Les fichiers `*.records.gz` contiennent les événements ARM et les snapshots complets, au format R2. Les `*.trace.gz` préservent les blocs d'instructions QEMU ; ils ne comptent pas toutes leurs répétitions. Les événements et empreintes de framebuffer sont strictement identiques entre les deux VSB.

## Comparaison historique et apports

MD84 annonçait la transition 25 → 29 ; elle est redémontrée indépendamment. MD85 annonçait 72 pixels supplémentaires : **R3 en mesure 91**, avec une autre image Mercury, une autre séquence et l'initialisation graphique explicite R2. Ce n'est ni une reproduction numérique du vieux résultat ni sa réfutation.

L'apport est la comparaison de deux politiques de restauration et leur exercice répété, avec un oracle complet de l'image entrante, plutôt que la seule réussite de la transition.

## Reproduction et limites

```bash
export PATH=/workspace/mercury-tools/bin:$PATH # adapter si outils système
bash tests/run_recovery_r3.sh 'custom.VSB' 'backup.VSB'
```

Le lanceur rejoue R2 et ses prérequis avant R3. Pour les seuls essais R3, les fichiers d'entrée vérifiés générés par R2 doivent exister ; utiliser `python3 tools/recovery_r3/run.py` avec les mêmes arguments.

Les VSB sont ouverts en lecture et leurs SHA vérifiés avant/après. Les sources R1/R2 sont réutilisées sans modification. Les états RAM, le gestionnaire et la musique restent des fixtures. Aucun LCD2, ordonnanceur, IRQ/FIQ, DMA, cache physique, chargement matériel ou récupération n'est validé. Le framebuffer inspecté n'est pas une confirmation de transmission au LCD.

Prochaine étape : R4, publier et dépiler une demande de transition par les routines de file et de dispatch Korg, puis étudier le producteur MD87.
