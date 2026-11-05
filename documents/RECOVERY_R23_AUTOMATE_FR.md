# R23 — automate d'autorité proposé et contrats absents

`KORG_ACTIVE → TRANSITION_TO_MERCURY → MERCURY_ACTIVE → TRANSITION_TO_KORG →
KORG_ACTIVE`, avec `FAULT` depuis toute transition. Une demande EXIT ne fait
qu'entrer dans `TRANSITION_TO_KORG`.

Chaque transition exige un gel de tous les nouveaux producteurs, un compteur
fiable de transferts engagés, un ACK réel à zéro transfert, l'absence d'auteur
échappé, puis un changement atomique de propriétaire. Le retour exige en plus
une invalidation autorisée du shadow et une frame Korg complète acquittée.

Ces primitives et contrats ne sont pas identifiés dans les VSB. Le modèle R23
explore 4 096 séquences et place en faute toute prise/restitution avec transfert
actif, réentrée ou auteur échappé. Il conserve les 64 états R22 et leurs 21
témoins de shadow mensonger. Cet automate est une spécification négative, pas
une implémentation native.
