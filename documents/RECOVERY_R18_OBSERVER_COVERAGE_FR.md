# R18 — couverture des observateurs Korg

Base : c4fe851. Les142 empreintes R17 passent la vérification, sans rejouer ses expériences. Les autres chemins historiques ne sont pas modifiés.

## Classement de chaque candidat

`reports/recovery_r18/coverage.csv` et `coverage.json` contiennent une ligne par branche candidate : cible, adresse d'appel, B/BL, voisinage natif signé, hint de prologue, racines syntaxiques, statut de tâche, propriétaire et couverture. Les239 candidats inscription/notification sont tous présents ; les retraits/destructeurs et deux chemins d'invocation sont également classés, soit316 lignes. Les239 candidats ne sont pas renommés artificiellement en239 appelants exécutables distincts.

| Cible | Candidats | Atteignables syntaxiquement depuis au moins une tâche connue | Non attribués à une tâche |
|---|---:|---:|---:|
| Inscription C0070778 |119|35|84|
| Notification C0070688 |120|21|99|
| Invocation C007061C |2|voir lignes individuelles|voir lignes individuelles|
| Retrait C00705DC |12|voir lignes individuelles|voir lignes individuelles|
| Destructeur inverse C0041B74 |51|voir lignes individuelles|voir lignes individuelles|
| Notification périodique C0082728 |1|voir ligne individuelle|voir ligne individuelle|
| Reset de compteur C0082788 |11|voir lignes individuelles|voir lignes individuelles|

« Atteignable syntaxiquement » signifie possibilité dans un CFG ARM conservateur, pas appel réellement exécuté ni attribution exclusive. Les instructions conditionnelles ne sont pas résolues ; les appels sont supposés pouvoir retourner ; les retours ne sont pas appariés à leurs appels. Les données indirectes et les fonctions virtuelles ne sont pas résolues. Les limites sont explicites dans le JSON.

Les dix racines de tâches sont lues directement dans les enregistrements Korg déjà identifiés R11. Des racines supplémentaires explicitent IRQ15, le consommateur UI virtuel, le dispatcher de services et la notification périodique ; elles ne sont pas assimilées à des tâches supplémentaires. Les listes de transferts indirects non résolus sont conservées par racine. Le témoin de chaque possibilité est un chemin d'instructions compressé dans `coverage-witnesses.json.gz` ; ses branches et voisinages peuvent être inspectés dans `native-contexts.txt.gz`.

Les tâches2 (mise à jour/compteurs),4 (UI) et5 (services) restent les domaines R15, mais un objet virtuel peut être appelé depuis plusieurs domaines. La présence d'un appel dans une plage graphique n'identifie pas son propriétaire. **Tous les propriétaires d'instances restent UNKNOWN** : le dépôt ne contient pas de symboles/types/contrats autorisant une attribution exhaustive. Les hints « nearest push LR » ne sont pas des frontières de fonction prouvées.

## Routes et obligations

- C0070688 et C0082728 appellent C007061C par deux branches directes différentes. Les contrôles dynamiques R18 doivent exercer les deux.
- C007061C charge séparément clé, this, méthode et ajustement puis résout indirectement une méthode/vtable. La cible indirecte ne peut pas être classée uniquement par un scan de branches.
- C00705DC ne joint pas les callbacks. Le destructeur C0041B74 retire les relations à partir du vecteur inverse puis libère son stockage ; un sujet déjà disparu rend ce parcours dangereux.
- Le pointeur aligné C00C5B50 et les sites de destruction ne constituent pas une preuve que toutes les vtables ou copies de fermeture ont été inventoriées.
- Aucun candidat n'est protégé par les nouvelles fixtures dans le firmware. La couverture installée reste nulle. Un site sans racine trouvée est INCONNU, jamais déclaré inatteignable.

## Synchronisation native

Le désassemblage inclut les corps observateurs, C0000040–0064 et les wrappers de sémaphore C0000CA8–0E98. Le masquage I conserve F ; sa portée est locale, pas une preuve contre IRQ/FIQ/DMA ensemble. Les sémaphores exigent un contexte noyau et des participants au même protocole ; les observateurs inchangés ne consultent pas les métadonnées Mercury.

Aucun verrou commun dominant tous les candidats, appels virtuels et destructeurs n'est démontré. Ordre mémoire, barrière/cache, ordonnancement et contraintes d'interruption ne sont pas qualifiés par QEMU user-mode. Statut de la primitive commune : **NON PROUVÉ**. Aucun verrou ne doit être conservé pendant un callback ou une opération LCD pouvant bloquer.
