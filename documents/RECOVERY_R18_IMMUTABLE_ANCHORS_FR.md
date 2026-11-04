# R18 — ancres stables et fermeture sans réutilisation

RESEARCH_ONLY. L'architecture est expérimentée dans un nouveau banc Linux ARM. Aucun accès natif n'est remplacé ; aucune ancienne inscription Korg n'est transformée en ancre. Les callbacks de fixture sont inscrits par C0070778 et invoqués par les routines originales.

## Objet stable et contenu immutable

Une génération possède deux ancres distinctes, une par propriétaire logique, et un payload partagé de32 octets. Chaque ancre fait36 octets : quatre mots de préfixe, puis pointeur de vtable, index de slot, génération de page, bit propriétaire et adresse du payload. Le `this` natif est ajusté de16 octets vers le sous-objet contenant ces cinq derniers mots. Le cas virtuel utilise ajustement encodé33, le cas direct32.

Après création, tous les mots des ancres restent inchangés, ainsi que les entrées de leur vtable et le code du thunk. Le payload de démonstration est aussi immutable. Les compteurs de travail et les sorties graphiques sont externes. Les données mutables — propriétaires encore vivants, registre d'emprunts, rejets, statistiques — sont séparées logiquement de l'ancre. Elles ne sont pas séparées par une protection matérielle de page.

Le hash d'intégrité des ancres est une vérification de fixture, pas une primitive de synchronisation, un mécanisme cryptographique ou une protection contre une écriture concurrente. La RAM n'est pas rendue read-only. Si un alias modifie la vtable **avant que le thunk soit choisi**, le mauvais code peut être appelé avant toute vérification du hash. Les cas6/7/8 le démontrent sur un contexte de contrôle mutable conservé en mémoire.

La génération de page vaut index+1 et ne change jamais dans une ancre publiée. Les ressources de chaque registre R16 neuf ont, elles, leur propre génération1. Ces identités ne sont pas confondues : un handle porte index et génération de page, puis deux tokens de ressources R16. Changer de page crée un nouveau slot à une autre adresse ; cela ne retargete pas les ancres précédentes.

## Durée de vie et propriétaires

Une génération conserve deux ressources R16 : bundle des ancres et payload. Deux emprunts racines existent tant qu'au moins un propriétaire est vivant. Le masque de producteurs distingue les propriétaires1 et2. Un callback entrant doit correspondre exactement à l'adresse d'un sous-objet connu ; le thunk valide son bit propriétaire, l'intégrité du cœur et la capacité avant de prendre deux emprunts individuels.

Retirer le propriétaire1 interdit ses nouvelles entrées, mais laisse fonctionner le propriétaire2. Le dernier retrait passe les deux ressources à RETIRING, détache les producteurs et libère les racines ; les callbacks déjà entrés gardent leurs propres tokens. Les trois cadres simultanés maximum proviennent de la capacité de huit leases du registre R16 : deux racines plus trois paires. Une quatrième paire est refusée sans emprunt résiduel. Tickets, numéros de série et tokens sont contrôlés à la sortie ; aucun token porteur ne constitue une authentification de tâche.

L'ancre reste allouée même si aucun emprunt n'est visible : le processeur peut encore détenir son adresse entre sélection et entrée. Le thunk à adresse permanente peut alors refuser le travail sans lire un payload devenu inaccessible. Dans ce prototype, le payload reste lui aussi conservé ; aucune libération n'est faite. Le cas15 conserve volontairement un alias brut vers le payload : il reste lisible après inactivité locale. Cela empêche de transformer le compteur local en autorisation de destruction.

## Retrait logique, slot natif et inverse

Le protocole nominal ne nettoie pas immédiatement les slots natifs. Les inscriptions, clés et vecteurs inverses de fixture demeurent alloués. Une notification ancienne atteint le thunk stable puis reçoit un refus d'admission, sans prétendre que la notification native elle-même a disparu. Le thunk est de type void ; ce refus est une observation locale, pas un retour de succès LCD ou service Korg inventé.

Cette conservation évite d'effacer le tuple pendant sa résolution. **Une ancre ne répare pas un retrait natif concurrent.** Le cas4 appelle réellement C00705DC après le chargement du contexte et avant celui de la méthode ; l'invocation faute à0 malgré l'existence de l'ancre. Un nettoyage physique demanderait donc toujours l'exclusion/join ou le retrait différé de R17.

Le constructeur natif écrit aussi actif à C00707C8 avant d'ajouter la relation inverse. Le cas30 arrête C0070778 à C00707CC : le second slot est déjà sélectionnable, l'inverse de sa clé est vide ; une notification appelle les deux générations. La fermeture logique de la nouvelle génération est ensuite demandée dans l'intercalation. Au retour de l'inscription, la relation inverse est ajoutée vers l'ancre fermée. Tout reste conservé, sans référence libérée. Un destructeur qui se fierait au seul inverse ne couvrirait pas cette fenêtre.

C0041B74 n'est pas exécuté sur ces vecteurs statiques car il les libérerait par l'allocateur natif. Sa capacité à retirer les relations est auditée, mais son emploi concurrent n'est pas qualifié. Une destruction globale doit couvrir également sujet, clé, stockage inverse, slots en construction et toutes les autres racines.

## Changement de page

La fixture prépare une nouvelle génération, inscrit ses ancres, publie son numéro logique, puis retire les propriétaires de l'ancienne. Toutes les anciennes adresses restent distinctes et conservées. Un ancien callback arrivé après fermeture est refusé ; un callback déjà admis garde son payload initial jusqu'à son retour. Aucun pointeur de payload n'est remplacé dans une ancre publiée.

Si la préparation d'une nouvelle génération échoue faute de place, le numéro courant reste inchangé. Ce comportement est testé au passage de la quatrième à la cinquième génération. Il ne qualifie pas une factory/destruction de page Korg réelle ; les transitions complexes et la publication multitâche restent soumises au gate NON PROUVÉ.

## Conditions de destruction

Le prototype n'en délivre **aucune** : `r18_destroy` refuse toujours, même après délai, local_quiet ou retour de tous les callbacks recensés. Il ne contient aucun free ni recyclage de slot.

Pour concevoir une destruction réelle, il faudrait prouver : admissions fermées dans tous les domaines ; fin des inscriptions en construction ; absence de sélection native déjà chargée ; retrait différé sûr de tous slots ; inverse cohérent dans les deux sens ; retour des cadres et commandes ; absence d'alias bruts ou de vtables changeantes ; cessation périphérique indépendante si l'objet y participe. Aucun certificat global de ce type n'est disponible.

## Comparaison avec R17

| Point | Retrait différé R17 | Ancres/quarantaine R18 |
|---|---|---|
| Fenêtre sélection–entrée | Retient avant parcours admis | Garde les adresses de thunk/contexte indéfiniment dans le pool |
| Nouveau travail après fermeture | Nouveau parcours participant refusé ; ancien parcours peut continuer | Ancien parcours atteint encore le thunk, qui refuse l'entrée du propriétaire fermé |
| Tuple natif pendant résolution | Mutations différées jusqu'au retour | Conservation du slot ; retrait brut conserve le même contre-exemple |
| Réentrée | Cadres et emprunts distincts, capacité finie | Emprunts distincts par invocation, trois paires maximum |
| Propriétaires | Sous-graphe R17 à une clé connue | Deux propriétaires de payload, deux clés/contextes stables distincts |
| Inverse | Compaction de fixture après retour | Vecteurs et relations conservés ; aucune destruction globale |
| Mémoire sur durée indéfinie | Drainage possible si tous participent et retournent | Quatre générations puis refus ; pas de progression indéfinie à mémoire fixe |
| Alias non participant | Non couvert | Ancienne ancre sûre sous immutabilité, mais alias brut de payload non couvert |
| Appel LCD bloqué | Cadre gardé, fermeture non terminée | Emprunts et slot gardés ; pas de récupération inventée |
| Statut instrument | NO GO | NO GO |

Ces deux approches sont complémentaires : une ancre évite le retargeting du contexte et une quarantaine maintient sa durée de vie ; retirer réellement ses relations demande toujours une preuve de coordination. La transformation d'une inscription Korg existante en cette architecture reste hors périmètre.
