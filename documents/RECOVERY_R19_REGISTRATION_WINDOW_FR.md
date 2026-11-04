# R19 — fenêtre native de construction d'une inscription

## Ordre des instructions, sans atomicité supposée

| Étape | Instructions / état | Ce qui n'est pas encore établi |
|---|---|---|
| Entrée et recherche | C0070778–07A0 ; compare la clé avant de tester actif,32 slots | Un retour pour clé existante n'actualise pas la fermeture |
| Slot choisi | C00707A4 écrit le mot supplémentaire | Le slot n'est pas réservé atomiquement contre un second constructeur non participant |
| Clé | C00707A8 écrit la clé | Un concurrent peut déjà la trouver alors que actif reste0 |
| Méthode et ajustement | C00707AC–07B8 charge puis écrit les deux mots | Le contexte n'est pas encore publié dans ce slot |
| Contexte | C00707C0 écrit this | L'inverse n'est pas encore traité |
| Publication | C00707C8 écrit actif=1 | Une notification native peut sélectionner immédiatement le tuple |
| Inverse | C00707CC–07EC lit fin/capacité puis append et avance fin | Le constructeur reste actif après cette écriture |
| Croissance | C00707F4–07FC → C00706C8 | Allocation, copie et éventuelle libération de l'ancien stockage ; peut ne pas revenir dans le banc |
| Retour effectif | C0070810 prépare la sortie, C0070814 restaure la pile et retourne | Le retour doit être observé par l'appelant, pas déduit de l'inverse |

L'inscription native retourne void. Un tableau plein peut conduire à un retour sans insertion. Le protocole de fixture conserve donc une distinction entre « appel revenu » et « relation capturée/validée ». Il ne remplace aucun retour Korg par un faux succès.

## Frontières éprouvées

- Avant écriture du tuple : arrêt C00707A4, fermeture demandée, puis reprise native. Le slot peut être publié après la demande ; il reste retenu jusqu'au vrai retour et son travail est refusé.
- Slot actif, inverse vide : arrêt C00707CC ; notification participante différée, ou notification native de contrôle qui atteint un thunk BUILDING et ne fait aucun travail.
- Inverse présent, constructeur encore actif : arrêt C0070810 ; l'obligation de construction est toujours présente et le retrait physique est refusé.
- Retour effectif : le wrapper appelle `r19_complete` seulement après le retour du vrai appel C0070778 ; il vérifie clé/actif, contexte, méthode0, ajustement33, période1 et relation inverse. Ce codec est celui de la fixture, pas une représentation générale des inscriptions natives.
- Conflit après préflight : le cas30 réserve une clé, puis un appel natif non participant enregistre cette même clé avec un autre contexte avant la recherche du constructeur initial. Korg ignore ensuite la nouvelle fermeture. Le contrôle exact constate FAILED malgré slot et inverse présents.

Une garde avant constructeur doit donc couvrir aussi la réservation de clé et de slot, pas seulement le drapeau actif ou un test fait après coup. Deux constructeurs non participants pourraient choisir le même slot libre ; le modèle positif n'en suppose jamais l'exclusion sans son contrat de réservation.

## Destructeur inverse pendant construction : contrôle conservé

Le cas7 initialise un vrai vecteur vide nul, arrête le constructeur après publication, puis exécute C0041B74 sur la clé statique. Le corps natif réécrit sa vtable, constate l'inverse nul et retourne sans appeler le free. La notification peut encore atteindre le slot publié. Le processus de laboratoire termine explicitement avec exit87 pendant que le constructeur d'origine est toujours suspendu.

Ce cas ne reprend pas une inscription dont la clé aurait été libérée, n'installe pas de nouveau vecteur pour lui fabriquer une réussite et ne déclare pas le constructeur terminé. Il ne démontre pas qu'un destructeur réel sur un vecteur non vide serait sûr. Tous les objets restent alloués ; aucun stockage n'est réutilisé. Le record81 contient construction=1 et retour=0.

## Frontière du heap natif

Le cas20 utilise un vecteur inverse nul et laisse réellement emprunter la croissance C00706C8. Le cas24 entre dans le constructeur d'état C006E6EC avec racines S/A déjà fournies, puis atteint son allocation enfant obligatoire. Les deux exécutent l'extension de heap C000A3B0 et fautent au store C000A3C4 vers C06A293C, non mappé dans ce banc.

Aucun allocator n'est remplacé, aucun résultat mémoire n'est inventé. Le cas20 garde la transaction BUILDING, un slot actif et un inverse vide. Le cas24 ne termine pas le constructeur UI : état+0x24 a été affecté mais état+0x2C pas encore. Ces fautes montrent une dépendance du banc ; elles ne prouvent ni OOM ni comportement d'erreur de l'Electribe.
