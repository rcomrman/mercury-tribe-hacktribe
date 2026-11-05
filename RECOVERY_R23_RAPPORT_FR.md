# MERCURY DUST — RAPPORT R23

## Conclusion

La réponse à la question centrale est **non démontrée et actuellement NO GO**.
Une frontière logique existe avant la copie du shadow, mais aucun point natif
unique ne domine tous les producteurs, transferts engagés et acquittements. On
ne peut donc transférer puis restituer l'autorité LCD sans incohérence prouvée.

## Chemin vérifié

La carte directe identique des deux VSB recense 1 appelant de `C0015AB4`, 8 de
`C0015DD0` et 2 de `C0015FA0`. La comparaison copie chaque page modifiée de la
source fixe vers le shadow avant le chemin worker. L'opcode 2 marque une demande
et l'opcode 3 entre dans le worker ; les handles, le pilote bas, le MMIO et la
fin physique viennent ensuite. Aucun code de retour étudié ne prouve que le LCD
a terminé. Le scan direct ne ferme pas les appels indirects, IRQ/FIQ, DMA,
diagnostics ou alias calculés.

## Frontières candidates

| Frontière | Limite | Verdict |
|---|---|---|
| avant chaque `C0015AB4` | tous les demandeurs/alias non dominés | NO GO |
| `C0015DD0` opcode 2 | shadow peut déjà être avancé | trop tard |
| entrée `C0015FA0` | demande et shadow déjà modifiés, deux appelants | trop tard |
| pilote bas | transfert engagé, ACK inconnu | trop tard |

## Automate et tests

L'automate spécifie `KORG_ACTIVE`, `TRANSITION_TO_MERCURY`, `MERCURY_ACTIVE`,
`TRANSITION_TO_KORG` et `FAULT`. EXIT est une demande, jamais une restitution
immédiate. Les 64 états R22 et 21 incohérences sont conservés. R23 explore 4 096
séquences de demandes Korg/Mercury, fins, EXIT, faute, réentrée et auteur échappé.
Toute transition avec transfert actif ou auteur échappé est rejetée.

V30 reste inchangé : empreinte fixe R21, triple buffer, huit presets, douze
paramètres, quatre mini-LFO et cible 10 FPS. Dix FPS réduit les calculs et
demandes Mercury ; cela ne change aucun contrat LCD ni l'activité musicale entre
deux frames. Les contrôles R21 et leur manifeste passent intégralement.

## Verdicts

- Frontière commune : **NO GO**, domination incomplète.
- Exclusivité de l'affichage : **NO GO**.
- Drain : **NO GO**, aucun compteur/ACK global qualifié.
- Restauration EXIT : **NO GO**, invalidation et refresh complet non autorisés.
- Pilote natif pour Mercury : **NO GO**, protocole de fin incomplet.
- Intégration matérielle : **NO GO**.

## R24 recommandée

R24 doit auditer le contrat du descripteur et la fin de transfert en descendant
de `C0015FA0` jusqu'au premier MMIO : états, handles, retours, attente, IRQ et
DMA. Elle doit aussi remonter `C0016084` pour recenser tous les chemins vers la
comparaison. L'objectif est de prouver ou réfuter un compteur fiable « transfert
engagé/terminé » et une invalidation complète du shadow. Sans ces deux contrats,
R24 devra clore la piste d'exclusivité via le pilote natif. Aucun hook, flash ou
essai matériel n'est autorisé.
