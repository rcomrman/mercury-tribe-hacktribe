# R18 — coordination native : NON PROUVÉ

Les plages exactes sont publiées dans `native-contexts.txt.gz`. L'analyse ne modifie pas les primitives natives et ne simule pas un noyau ordonnançant les tâches dans QEMU user-mode.

## Faits locaux

C0000040 lit CPSR, pose I=0x80 et écrit CPSR_c ; C0000050 restaure le bit I à partir de l'état fourni. F=0x40 n'est pas posé par cette séquence. Cela peut établir une exclusion locale contre certains IRQ, mais ne démontre pas une exclusion FIQ/DMA ni la participation des appelants indirects.

C0000D80 teste notamment un état global à C06A2894, le bit I et le contexte courant C06A2928. Il peut renvoyer−25 pour un contexte interdit et−18 pour un identifiant invalide. Avec un compteur disponible, il le décrémente ; sinon il inscrit une attente via C0001D14 puis appelle le dispatcher C0001760. C0000CA8 peut libérer/réveiller un attendant et également appeler le dispatcher. Ignorer leurs retours ou attendre alors que les IRQ sont déjà masqués ne constitue pas un verrou sûr.

Les corps de notification/invocation/retrait ne consultent aucun gate Mercury. C0070778 publie plusieurs champs puis l'octet actif avant la mise à jour de l'inverse. Le chemin de croissance C00706C8 appelle allocation, copie et libération. C0041B74 parcourt et libère le vecteur inverse. Leur cohérence ne découle donc ni d'un mot d'état Mercury ni d'un slot déjà actif.

## Exigences d'un gate éventuel

Il devrait couvrir admission, visibilité du tuple/vtable, construction de l'inverse, fermeture des propriétaires, publication de page et décisions de destruction. Il devrait fonctionner dans tous les contextes réellement participants. L'inventaire R18 comporte encore des appels virtuels non résolus et des propriétaires UNKNOWN ; aucune dominance globale n'est démontrée.

Le gate serait relâché avant le callback, toute attente et toute opération LCD. Les emprunts conserveraient ensuite les ressources nécessaires, et les mutations incompatibles seraient différées. La fermeture depuis un callback doit revenir sans attendre son propre retour. Les appels réentrants exigent des emprunts distincts, sans reprendre un mutex non réentrant conservé par le cadre extérieur.

Les écritures C ordinaires, `volatile`, le hash d'ancre et un compteur nul ne prouvent ni atomicité composée ni ordre mémoire ARM926. ARM926 n'offre pas le protocole d'exclusives ARMv6 à supposer implicitement ; un éventuel mécanisme SWP/masquage ou drain de write buffer doit être qualifié dans le contexte MMU/cache et noyau réel. Aucun de ces mécanismes n'est installé ou déclaré validé ici. Les délais de préemption, l'audio et les périphériques restent hors du banc.

## Conclusion

**NON PROUVÉ pour une primitive commune aux tâches Korg et à tous les observateurs.** Les scénarios ARM/GDB reproduisent des intercalations choisies avec restauration de registres ; ils ne démontrent pas une exclusion réelle sous IRQ/FIQ. Le prototype suppose une sérialisation extérieure de ses transitions. Aucune expérience ne conserve un verrou pendant le worker LCD.

Détection, confinement, annulation et restauration périphériques restent quatre obligations distinctes. Une faute Linux ou un timeout hôte ne satisfait pas ces obligations sur l'Electribe. Aucun watchdog, réponse GPIO/SPI, acquittement LCD ni retour sûr à Korg n'est fabriqué.
