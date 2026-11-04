# R17 — cycle de vie des observateurs, audit de phase 2

Base historique : `60eddcdd2cc06dff43b71d5459b147d8c835457f`. Les 167 entrées du manifeste R16 ont été vérifiées, sans rejouer R16.

Les quinze plages de l'audit sont identiques dans les deux VSB originaux. Les adresses ci-dessous sont des faits CPU, pas une preuve d'exclusion entre tâches.

| Référence | Acquisition / utilisation | Retrait / risque résiduel |
|---|---|---|
| Sujet | Tableau de 32 entrées de 24 octets à sujet+4 | Doit survivre au parcours et au vecteur inverse |
| Clé | Entrée+0 ; comparaison dans C0070778 et C00705DC | N'est pas nécessairement le contexte du callback |
| Contexte this | Entrée+4 ; chargé à C007062C | Reste dans r3 même si l'entrée est effacée ensuite |
| Méthode | Entrée+8, ajustement encodé à +12 | Chargement séparé du contexte ; retrait concurrent peut produire un tuple déchiré |
| Ajustement / vtable | Décalage signé ASR 1, bit 0 virtuel ; résolution C007066C–674 | Durée de vie du sous-objet et de la vtable distincte de celle de la clé |
| Argument supplémentaire | Entrée+16 | Utilisé comme diviseur de période par C0082728 ; sens ailleurs non établi |
| Actif | Octet entrée+20 | Effacer cet octet ne retire pas les registres déjà chargés |
| Vecteur inverse | Clé+4 début, +8 fin, +12 capacité ; contient des sujets | C00705DC ne le compacte pas ; C0041B74 le parcourt puis le libère |
| Callback sélectionné | Registres / pile du parcours | À C007067C, r0 et r12 contiennent déjà cible et méthode |
| Racines externes | Pages, autres sujets, copies d'entrée, code/vtable | Inventaire global non établi ; aucune propriété de cessation globale |

C0070778 refuse une clé déjà présente sans remplacer le contexte. Retirer puis réinscrire peut ajouter deux références identiques au vecteur inverse. C00705DC efface la première entrée correspondante, sans attendre le retour d'un callback.

Deux branches directes vers C007061C sont trouvées : C00706B4 depuis C0070688 et C0082770 depuis C0082728. Ce second parcours possède 32 compteurs à sujet+0x308, soit un objet d'au moins 904 octets. Une garde limitée à C0070688 le laisserait passer. Les candidats statiques sont bornés aux mots ARM alignés ; ils ne prouvent pas l'absence d'appels indirects, Thumb, IRQ ou FIQ.

## Frontière critique

Avant C007061C, retirer l'entrée peut empêcher l'invocation. Après C007062C mais avant le chargement de la méthode, effacer l'entrée peut laisser un contexte non nul avec une méthode nulle. Après résolution complète, retirer la mémoire de l'entrée ne retire plus les pointeurs des registres. Ces trois frontières doivent être testées séparément.

Le protocole candidat doit retenir les ressources **et différer les mutations de l'entrée** pendant un parcours admis. Une demande de fermeture effectuée dans le callback doit revenir sans attendre son propre parcours. Un parcours déjà admis peut encore sélectionner les entrées suivantes : arrêter immédiatement chaque sélection demanderait une médiation supplémentaire non démontrée.

Les désassemblages compressés, empreintes et listes de candidats sont dans `reports/recovery_r17/`. Aucun octet natif n'a été modifié pour l'audit.
