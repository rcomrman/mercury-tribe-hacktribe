# R19 — transaction expérimentale inscription / fermeture

RESEARCH_ONLY. `tests/recovery_r19/transaction.h` réutilise les ancres R18 et les leases R16 sans modifier leurs sources. Aucun wrapper n'est installé dans Korg. Toutes les transitions de métadonnées supposent une sérialisation extérieure ; sa primitive native reste NON PROUVÉE.

## États et responsabilités

| État / obligation | Entrée | Sortie et limite |
|---|---|---|
| Préparé | Sujet, clé, contexte et inverse possédés/conservés ; ancre immutable | Cette durée de vie n'est pas inférée de la proximité des pointeurs |
| BUILDING | Réservation avant C0070778 ; clé unique recensée ; aucun autre constructeur ni parcours participant sur le sujet | Deux leases CONTINUATION retiennent ancres/payload ; sujet/clé/inverse sont des tableaux permanents dans cette fixture |
| Publié, inverse absent | Fait natif observé pendant BUILDING | Ne change pas l'obligation de construction ; travail du thunk non admis |
| Inverse présent, retour absent | Fait natif avant POP/retour | Ne libère pas le constructeur ni ses références |
| LIVE | Vrai appel revenu ; slot et tuple exacts plus inverse concordants ; fermeture non demandée | Nouvelle notification participante admise ; fermeture devient CLOSING |
| FAILED | Vrai appel revenu mais slot, tuple ou inverse non concordant | Aucun succès d'inscription ; pas de nettoyage d'une relation mal attribuée |
| CLOSING | Propriétaire retiré logiquement ; nouvelles entrées de travail refusées | Les cadres déjà admis conservent leurs propres emprunts |
| DETACHED local | Constructeur revenu, aucun constructeur/parcours/callback recensé, tuple connu et retrait natif effectué, inverse de cette relation compacté | Seulement retrait d'un lien recensé ; aucune libération ou cessation globale |

`r19_complete` accuse la fin de l'obligation et la restitution des tokens ; sa valeur de retour ne signifie pas succès du service natif. La relation porte séparément LIVE/FAILED/CLOSING. Le banc contrôle cet état, notamment quand les32 slots sont occupés ou quand un autre contexte a gagné la clé.

La fixture est spécialisée : méthode virtuelle à offset0, ajustement33, période1, this=ancre de propriétaire. Les inscriptions natives arbitraires, leurs méthodes et pointeurs profonds demandent d'autres codecs/contrats. Les valeurs10 et les sous-objets à +0x38 du véritable abonné audité ne sont pas transformés par cette fixture.

## Réservation courte, sans verrou pendant les appels

La réservation atomique supposée vérifie ouverture, capacité, ticket, absence d'autre construction/parcours et absence de clé déjà recensée ou présente. Elle retient les deux ressources R18 avant l'entrée native. La réservation logique reste en cours pendant l'appel ; un mutex physique ne doit pas rester détenu. Les notifications participantes reçoivent un refus/différé **avant leur appel natif**. L'appelant doit conserver son événement puis réessayer ou l'acquitter comme refus ; aucune queue générale ni livraison native fictive n'est ajoutée.

Le thunk refuse BUILDING, FAILED, CLOSING et DETACHED. Un appel natif de contrôle peut donc atteindre ce thunk sans faire du travail avant validation. Cela repose sur le maintien permanent de l'ancre, de sa vtable et de son code, pas sur un succès d'exclusion natif.

Un parcours admis incrémente son obligation avant C0070688 ou C0082728, donc avant sélection/résolution. Son compteur reste retenu jusqu'au retour complet du parcours, y compris après un callback refusé. Chaque callback de travail possède aussi sa paire de leases ; les entrées réentrantes sont individuelles. Aucun gate n'est conservé pendant le callback, le worker LCD ou une attente.

## Fermeture et retrait physique conditionnel

Une fermeture peut arriver à tout moment : elle ferme l'admission, retire les producteurs du propriétaire et conserve les constructions déjà acceptées. Un constructeur ne s'annule pas parce que la fermeture a été demandée. S'il revient, son wrapper valide puis marque la relation fermée ; sinon ses obligations restent retenues.

Le retrait physique de fixture exige :

1. Demande de fermeture, retour natif effectivement observé et tuple concordant.
2. Aucun constructeur sur le sujet recensé, aucun parcours avant résolution, aucun callback recensé encore actif.
3. Tous les slots actifs du sujet correspondent à des clés et tuples de l'inventaire de fixture.
4. Appel C00705DC puis compaction de la relation inverse correspondante, sans free ni remise en circulation d'adresse.

Le test des32 slots n'est **pas** une preuve que toutes les racines externes sont recensées. Les cas15/16 contournent volontairement le compteur de parcours : l'un obtient une méthode nulle après effacement, l'autre appelle encore la méthode déjà résolue après DETACHED. Ce sont des contrôles négatifs qui interdisent une conclusion de cessation globale.

La compaction conserve les éventuels autres sujets ; DETACHED désigne le lien traité, jamais toute la clé ni le graphe complet. Les clés, inverses, sujets et ancres de ce banc restent alloués. Une inscription native non participante ajoutée pendant un parcours fait aussi échouer le contrôle local de couverture (cas29).

## Propriétaires et générations

Le sujet peut contenir plusieurs clés. Deux ancres/propriétaires distincts peuvent partager un même payload R18. Retirer la première relation n'enlève pas les droits de la seconde. Le dernier propriétaire ferme les deux ressources R18 ; les leases déjà entrés subsistent jusqu'aux vrais retours.

Un changement de page prépare une nouvelle génération à une autre adresse. Un essai de construction pendant une notification participante est refusé ; le changement de fixture est rejoué après retour, puis l'ancien lien fermé. Les copies de slot et les anciens sous-objets continuent de désigner des ancres conservées et sont refusés par le thunk fermé. Aucun destructeur/factory de page Korg complet n'est qualifié ici.

## Comparaison à la quarantaine

| Condition | Réservation avant constructeur + retrait différé | Conservation permanente R18 |
|---|---|---|
| Travail avant fin de l'inscription | Refus/différé avant parcours, et refus du thunk BUILDING | Ancres stables mais un état de construction supplémentaire est nécessaire pour refuser ce travail |
| Fermeture pendant appel | Obligation retenue jusqu'au vrai retour | Conservation du stockage même si le retour ne vient jamais |
| Inverse vide | Ne termine jamais la construction | N'autorise jamais une destruction |
| Nettoyage du slot | Possible seulement dans le graphe participant borné | Évité ; les appels fermés continuent d'atteindre le thunk |
| Appelants natifs non participants | Contre-exemples conservés | Ancre conservée, mais mutation du slot/vtable toujours dangereuse |
| Mémoire / progrès | Métadonnées et emprunts bornés, saturation refusée | Pool monotone et refus après quatre générations |

Les solutions sont complémentaires. Le modèle de quarantaine suppose lui aussi une construction sérialisée par sujet et des slots distincts ; conserver des adresses ne sérialise pas deux constructeurs concurrents choisissant le même slot.

## Synchronisation native et limites

C0000040 pose I sans poser F. C0000D80 peut refuser un contexte ou inscrire une attente et dispatcher ; C0000CA8 peut réveiller un attendant. Aucun de ces chemins n'est un verrou commun démontré pour tous les observateurs, destructeurs et initialisations paresseuses.

La réentrée interdit un mutex non réentrant conservé pendant notification ; attendre son propre callback depuis close créerait un interblocage. L'ordre mémoire/cache et la visibilité ARM926, ainsi que les IRQ/FIQ/DMA, ne sont pas prouvés par les séquences C ou le stub GDB. Une notification et un constructeur non participants peuvent encore contourner la réservation. **NON PROUVÉ pour Korg, NO GO intégration.**
