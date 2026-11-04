# R18 — mémoire et limites d'une quarantaine bornée

## Prototype mesuré sur ARM926 sous QEMU

Pool monotone de quatre slots. Chaque slot est utilisé au plus une fois pendant la vie du processus. Toutes les générations précédentes restent réservées ; la cinquième allocation est refusée. Le numéro de page publié n'est pas modifié par ce refus.

| Composant par génération | Octets |
|---|---:|
| Deux ancres immutables de36 |72|
| Payload de démonstration, huit mots |32|
| Registre R16 inchangé, deux ressources/huit leases |256|
| Deux tokens racines |32|
| Masque propriétaires et hash de fixture |8|
| Slot total |**400**|
| Deux clés natives à16 + deux vecteurs préalloués à8 |48|
| Coût génération avec clés/inverses |**448**|

Pool seul : quatre fois400 +16 octets d'en-tête = **1616**. Un emprunt d'invocation fait48 octets, sur la pile du callback. Le sujet étendu natif persistant fait904 octets. Pool + huit clés/vecteurs + sujet = **2712 octets**, soit920 fixes +448 par génération jusqu'à quatre. La vtable, les compteurs du banc, les piles et les journaux sont en sus. La pile d'injection GDB de8192 octets est exclusivement un instrument du banc.

Ces coûts sont les tailles réellement émises dans les records ARM. Ils ne représentent pas une page Korg réelle ni la quantité de RAM libre. Le payload32 octets borne seulement cette fixture. Un vrai graphe contenant buffers, sous-objets, vecteurs extensibles ou pointeurs profonds nécessite sa propre borne et sa propre preuve de propriété. Le triple buffer R12 n'est ni modifié ni dupliqué par R18.

## Invariants de refus

- Aucune adresse de slot n'est réutilisée, même si le compteur d'emprunts atteint zéro.
- Un délai, y compris après débordement du compteur statistique de ticks, ne libère aucune ressource.
- Une entrée fermée ne redevient pas vivante sous une nouvelle génération.
- Un callback non retournant garde ses tokens ; les autres générations peuvent remplir le pool, puis les suivantes sont refusées.
- La saturation d'emprunts refuse un callback supplémentaire et annule toute acquisition partielle. La saturation de générations refuse une nouvelle page avant publication.
- Le retrait logique et une valeur local_quiet ne font pas disparaître les clés, vecteurs ou alias. `destroy` refuse sans certificat global.

Les tests16/19/26/27/29 exercent transitions successives, délai maximal et débordement, emprunt persistant, saturation et drainage explicite. Le cas18 reste réellement dans une boucle de fixture : l'hôte termine QEMU après son timeout ; aucun mécanisme Korg d'annulation n'est prétendu. Le cas17 se bloque à une frontière GPIO et conserve également ses emprunts.

## Ce qui peut et ne peut pas être borné

**Borne d'espace du prototype : démontrable par construction**, parce que le pool et les tableaux sont fixes et que l'allocation monotone ne dépasse pas quatre générations. Cela ne signifie pas que l'instrument dispose de ces octets.

**Progression illimitée avec mémoire fixe, anciennes références arbitrairement longues et aucune preuve de cessation : impossible pour ce protocole.** Après N générations conservées, garder la génération N+1 exige soit plus de mémoire, soit une réutilisation/libération qui requiert une preuve manquante, soit un refus. R18 choisit le refus. Un callback pouvant ne jamais retourner suffit à invalider toute borne temporelle de drainage.

Une quarantaine à délai seul ne résout pas cette contradiction. Le modèle négatif `timeout_destroy` montre un appel sélectionné encore capable d'utiliser le stockage après expiration. Le modèle `reuse_on_zero_active` montre le retargeting ABA alors que le compteur des callbacks actifs est nul. Ces destructions/recyclages dangereux sont des transitions du **modèle négatif uniquement**, jamais des frees effectués dans le banc ARM.

La conservation des ancres ne couvre pas automatiquement des pointeurs vers l'extérieur. Si leur payload pointe une page libérée ou une vtable mutable, la borne du petit objet « ancre » ne borne pas le sous-graphe nécessaire à son appel. La fixture conserve aussi ses payloads et teste séparément le contre-exemple d'un pointeur de payload changé malgré une adresse de contexte stable.
