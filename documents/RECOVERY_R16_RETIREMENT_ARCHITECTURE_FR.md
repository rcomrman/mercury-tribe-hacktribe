# R16 — registre expérimental et fermeture conditionnelle

RESEARCH_ONLY. Le code `tests/recovery_r16/registry.h` ne libère aucune allocation, ne patche aucun accès et n'installe aucun retrait dans Korg. Il est séquentiel ; chaque transition et consultation exige une sérialisation extérieure encore non qualifiée sur ARM926.

## Objets et emprunts nommés

Deux objets décrits par adresse, génération, propriétaire logique, état, masque de producteurs connus, classe CPU/périphérique et ticket de retraite. Huit fiches d'emprunt contiennent chacune vivant/objet/génération/détenteur/type/numéro de série. Le token de16 octets doit correspondre exactement à une fiche vivante et à la génération courante de l'objet. Le numéro de série ne reboucle pas ; génération maximale refuse le réemploi.

Les types distinguent QUEUE, WRAPPER, SERVICE, CALLBACK, PAGE et CONTINUATION. Les propriétaires/détenteurs sont des identifiants de fixture, pas une authentification de tâche Korg. Un token copié volontairement reste un token porteur ; le registre n'est pas une défense contre un appelant mensonger ou une corruption mémoire.

| Transition | Contrat et responsabilité |
|---|---|
| Bind neuf | Métadonnées neuves, aucun ancien token possible ; propriétaire/adresse non nuls |
| Acquire | Objet LIVE, producteur connu toujours actif, capacité et numéro disponibles ; fiche individuelle créée |
| Retire | Propriétaire/génération exacts ; interdit les nouvelles acquisitions externes |
| Detach | Retrait explicite d'une source connue, par son propriétaire ; pas une preuve que les racines natives ont été retirées |
| Derive | Parent vivant exact ; produit un emprunt fils, même pendant RETIRING, pour finir une commande déjà retenue |
| Release | Token/détenteur/génération/série exacts, vrai dernier accès de ce détenteur déjà achevé ; ne libère pas les fils |
| Local quiet | RETIRING, tous producteurs recensés retirés et aucune fiche vivante ; résultat local sous hypothèse de couverture |
| Fixture rebind | Métadonnées seulement, local quiet et objet CPU privé, génération incrémentée ; aucun free réel ni réemploi de ressource LCD |

Derive pendant la retraite est volontaire : arrêter les nouvelles admissions ne doit pas rendre impossible le drainage des commandes déjà acceptées. Une commande retenue garde sa cible jusqu'à réponse/ACK. Son callback intérieur possède sa propre fiche ; retirer le parent ne masque donc pas un fils actif. La réentrée crée deux fiches distinctes au lieu d'un booléen actif ambigu.

Les producteurs sont un masque de sources **connues** ; un bit retiré n'est ni un join noyau ni une inspection exhaustive de toutes les racines. Une mise à jour de génération refuse les anciens tokens, mais un pointeur brut peut encore désigner la même adresse réutilisée. Le réemploi de fixture conserve l'objet alloué pendant tous les tests : aucun UAF réel n'est provoqué.

## Séquence de fermeture à établir sur Korg

1. Arrêter atomiquement les nouvelles admissions et le changement non contrôlé des cibles.
2. Retirer tous les producteurs : queues/publications, wrappers/racines, observateurs natifs, timer et pages concernés. Chaque site nécessite une preuve de durée de vie et de visibilité.
3. Drainer ou refuser avant effets les anciennes commandes, sans perdre leurs réponses/ACK ; conserver les cibles et les sorties pendant l'attente.
4. Attendre la vraie fin de tous les callbacks, cadres réentrants et continuations CPU. Le retrait d'un slot d'observateur ne termine pas un callback déjà entré.
5. Établir l'absence d'alias CPU cachés, notamment clé/contexte de fermeture distincts et vecteurs inverses.
6. Obtenir séparément une preuve d'absence d'accès périphérique/DMA, état des verrous et du transport connu.
7. Alors seulement définir une autorisation de destruction/restauration. **Aucune fonction R16 ne délivre cette autorisation sur l'instrument.**

La source/shadow égale et un retour setter ne satisfont pas6. Les contrôles LCD7 et le worker accèdent eux-mêmes à GPIO/SPI ; aucune autorité d'annulation indépendante n'a été identifiée dans les chemins inspectés. Le registre classe les ressources natives LCD comme périphériques et interdit leur rebind de fixture ; cela ne constitue pas une annulation matérielle.

## Fenêtre entre résolution native et emprunt

Pour certifier une notification réelle, l'emprunt doit être acquis **avant** qu'un producteur charge/résolve le pointeur natif qu'il pourra appeler plus tard. Un comptage ajouté seulement à l'entrée du callback peut arriver trop tard : le retrait peut avoir effacé le slot et libéré sa référence d'inscription alors que le contexte/méthode est déjà chargé dans un cadre CPU. R16 instrumente des callbacks de fixture, mais n'installe pas cette acquisition dans le parcours natif. La sérialisation de cette fenêtre, son contexte IRQ et un éventuel join demeurent non prouvés. Le contrôle d'alias non participant conserve ce NO GO.

## Cas prouvés et limites

Les tests ARM exercent double retrait, mauvais détenteur/propriétaire, fils restant après retrait du parent, profondeur réentrante, transition de cible, ancien token après nouvelle génération et saturation. Des alias bruts et des inscriptions natives volontairement omis du registre appellent encore la cible alors que `local_quiet` est vrai. Ce contre-exemple conserve explicitement NO GO global.

Le contraste a une entrée possédée d'un octet et un emprunt de descripteur. Le cas6 garde ce dernier après retour natif jusqu'à ACK de la file R15. Les trois enveloppes réservées ne constituent pas un multiplexeur général de tous les services Korg ; un seul report de contraste est éprouvé de bout en bout ici.

Mesures ARM : registre256 octets, token16, enveloppe24 ; trois enveloppes72 ; file R15=128 ; admission R14+pool R12=3176. Total des structures distinctes réservées : **3632 octets**, hors objets natifs, listes, copies profondes supplémentaires, piles et diagnostics. Ce n'est pas de la RAM libre ni une borne temporelle/audio. Les snapshots et structures de sujet772 octets sont des fixtures supplémentaires.

Le modèle borné vérifie un graphe fermé de producteurs/emprunts avec un octet capturé, une commande, deux générations et capacité2. Il suppose la fidélité des déclarations, la fin réelle avant Release et les opérations atomiques. Un retrait prématuré ou un alias omis casse cette hypothèse ; le modèle ne transforme pas le registre C en algorithme multitâche natif. **GO registre/codec de laboratoire sous contrat ; NO GO cessation CPU globale, transport arrêté et récupération indépendante.**
