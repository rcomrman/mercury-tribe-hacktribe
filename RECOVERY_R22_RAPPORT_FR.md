# MERCURY DUST — RAPPORT R22

R22 étudie le mode visuel exclusif à 10 FPS, sans flash, patch, hook installé ni
écriture hors fixture. Les deux VSB ont les mêmes contrats étudiés et restent
inchangées.

## Résultat accessible

Le mode exclusif simplifie l'image souhaitée, mais pas l'autorité matérielle.
Les trois champs lus par `C006EA10` sont des widgets annexes possédés et créés
par le gestionnaire, et non trois slots libres de page. Mercury ne peut en
remplacer un sans reprendre une durée de vie et des abonnements non dominés.

L'interception d'une demande Korg après mise à jour du shadow est également
insuffisante : le logiciel peut croire l'image transmise alors que le LCD affiche
Mercury. EXIT peut alors ne rien renvoyer. Un faux succès n'est pas admissible.

## Verdicts

| Sujet | Verdict |
|---|---|
| insertion dans un slot `C006EA10` | **NO GO** : autorité et cessation absentes |
| interception des transferts Korg | **NO GO** : aucun point unique/contrat d'ACK démontré |
| restitution Korg à EXIT | **NO GO** : drain, invalidation et transfert complet non atomiques |
| publication Mercury vers LCD | **NO GO matériel**, GO simulation privée à 10 FPS |
| intégration matérielle | **NO GO** |

## Preuves et séparation

Observé dans les deux images : allocations 76/88/76, constructeurs
`C0084B3C/C0084254/C008C8B4`, écritures à `+0x34/+0x38/+0x3c`, trois lectures
et appels virtuels de `C006EA10`, chaîne framebuffer/shadow/worker. Observé dans
les missions conservées : réentrée R8, faute worker et comparaison par pages.

Simulé en R22 : 64 combinaisons shadow/physique/transfert/faute/restauration.
Une sortie n'est classée sûre que si aucun transfert n'est engagé, aucune faute
n'arrive et une restauration complète forcée réussit. Ce modèle expose les
contre-exemples ; il ne constitue pas une preuve native.

La cible 10 FPS conserve V30, huit presets, douze paramètres, quatre mini-LFO
et le triple buffer R21. Elle borne Mercury à une publication toutes les 100 ms,
mais ne résout aucune propriété, concurrence ou cohérence du shadow. Le BPM et
les événements peuvent continuer à piloter l'état V30 entre deux publications.

## Contrats encore nécessaires

Il manque un inventaire exhaustif des entrées du pilote, un contrat de fin de
transfert et d'ACK, l'état IRQ/FIQ/DMA/cache, une primitive de drain, une
invalidation légitime du shadow, un transfert complet forcé, l'ordre de reprise
après faute, la séparation prouvée des tâches audio et l'autorité de bascule.

## R23 recommandée

R23 doit qualifier en émulation la frontière **avant comparaison shadow** et le
descripteur LCD : recenser tous les appelants de `C0015AB4`, `C0015DD0` et
`C0015FA0`, déterminer quand le shadow est copié, puis établir les états et
retours du driver jusqu'au premier MMIO. Elle devra construire un automate
Korg→Mercury→Korg avec drain et restauration forcée, conserver les transferts
engagés comme témoins négatifs, et conclure NO GO si un ACK ou un auteur échappe
à la frontière. Aucun essai matériel ne doit précéder cette preuve.
