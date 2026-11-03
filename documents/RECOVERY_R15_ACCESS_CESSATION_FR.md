# R15 — cessation des accès et récupération

RESEARCH_ONLY. Cette étude n'autorise aucune libération forcée. Une demande d'arrêt et une preuve de cessation sont des objets différents.

| Observation | Preuve obtenue | Preuve encore nécessaire |
|---|---|---|
| Demande d'arrêt | C002D88C appelle slot+0x14 ; corps commun C002DE78 écrit objet+0x19=1 | Lecture effective du drapeau, abandon de tous les accès et accusé de cessation |
| Timeout/suspicion | Un observateur peut constater une absence de progrès ou refuser des participants | Contexte indépendant fiable, absence de faux positif, annulation des opérations actives |
| Changement de tâche | Réveil natif rend un TCB prêt ; effacement d'un réveil mémorisé retourne1 | Tâche effectivement exécutée, sortie de son callback et de ses références |
| Retour du callback intérieur | Le cadre intérieur a fini | Cadres extérieurs encore actifs, autres callbacks enregistrés/alias |
| Profondeur locale zéro | Plus de callback recensé actif | Retrait de tous producteurs/enregistrements, queues, alias et continuations CPU |
| Retrait + compteurs locaux zéro | Cessation du sous-graphe fermé supposé par le banc | Exhaustivité de ce sous-graphe sur Korg ; barrières de publication/retrait |
| Cessation CPU globale | Aucune preuve générale R15 | Absence d'accès périphérique/DMA encore en vol |
| Absence de transport en vol | Aucune preuve native établie | État périphérique connu, verrous et objets non empruntés avant destruction/restauration |

## Observations ARM nouvelles

- Cas13 : C002D030 entre dans un callback de fixture ; celui-ci demande l'arrêt natif C002DE78 puis écrit encore la source avant de sortir. Le drapeau n'a donc pas le pouvoir intrinsèque d'interrompre le CPU appelant.
- Cas28 : le wrapper natif de demande d'arrêt C002D88C/slot+0x14 est exercé, puis un autre appel natif au wrapper UI peut encore atteindre le callback de fixture. Aucun retrait de callback n'est effectué par ce corps d'arrêt.
- Cas12 : réentrée de C002D030 ; après le retour intérieur, profondeur extérieure1 et nouvelle écriture encore à venir. La fin intérieure ne permet pas de libérer les ressources extérieures.
- Cas26 : réveil natif d'un TCB en attente, remis prêt, mais le sélectionné de rang supérieur reste distinct et aucun callback n'est exécuté. Une commande RUNNING/autorité CRITICAL et sa référence restent conservées. Aucun changement de contexte n'est simulé.
- Cas19 : C0000ACC consomme le bit de réveil mémorisé ; le callback/autorité de fixture peut continuer à écrire. Cette fonction n'est pas une primitive d'annulation.
- Cas14 : retour local mais enregistrement conservé, fermeture locale non achevée. Cas20 : les références de file empêchent une conclusion de calme local tant qu'elles restent présentes.
- Cas27 : le registre local affirme zéro référence après retrait déclaré, mais un alias brut de wrapper volontairement omis permet encore un callback. **Même un compteur local correct ne prouve pas une fermeture de tous les accès CPU.** L'objet reste alloué dans le banc ; aucune utilisation réelle de mémoire libérée n'est provoquée.
- Cas17/18 : le callback périodique réel rejoint le worker, prépare la première page puis faute GPIO01E260BC. La seconde expérience garde commande RUNNING, fermeture demandée et référence active. Le handler Linux observe et termine ; il ne reprend pas Korg.

Le banc ne fabrique aucun registre SPI occupé pour obtenir une attente ou une sortie choisie. Le worker matériel bloqué sans retour est modélisé comme autorité retenue indéfiniment ; sous QEMU sans MMIO il atteint la faute avant cette validation matérielle. La différence est explicite.

## Ce qui manque dans les mécanismes natifs

C002D684 remet objet+0x19 à0 au début de chaque dispatch. Une demande d'arrêt sans génération/accusé ne peut pas être réutilisée comme certificat durable pour un nouvel appel. Le busy manager+0x10 et son service courant+0xC ne recensent pas toutes les références des pages, queues ou périphériques.

Les handles du service sont détruits au retour de C002D684 via C002D5B0 ; un destructeur appelé ne prouve pas que personne n'a gardé un alias. Le banc exerce le chemin virtuel avec un destructeur de fixture, pas l'allocateur/désallocateur et tous les objets réels.

La sortie de tâche C000066C→C0001A24 retire le courant et peut traiter une activation différée. Elle ne fournit pas un join de toutes les tâches/observateurs, un unwind graphique ou une annulation du périphérique. Le masquage IRQ n'est ni FIQ/DMA ni libération des continuations. Le diagnostic natif utilise toujours le LCD et peut masquer IRQ ; il n'est pas une restauration indépendante.

## Certificat de cessation proposé — non fourni nativement

Il faudrait réunir : identité/génération du domaine retiré ; interdiction atomique de toute entrée future ; files drainées ou refusées avec réponses conservées ; aucune continuation/callback/alias CPU restant ; fin réelle des accès périphérique/DMA prouvée ; restauration cohérente des verrous/objets Korg. Les acquittements de ces étapes ne sont pas interchangeables avec ACK de réponse de commande ou égalité shadow/source.

Le helper `r15_local_cpu_quiet` compte seulement les références explicitement enregistrées dans une fixture. Il ne libère rien et ne certifie jamais le matériel. Le résultat exploitable R15 est un **refus de destruction tant que la preuve globale manque**, pas une récupération validée. **NO GO cessation globale, récupération indépendante et libération de ressources LCD réelles.** Aucun watchdog/reset n'est inventé ni déclaré absent dans tout le firmware.
