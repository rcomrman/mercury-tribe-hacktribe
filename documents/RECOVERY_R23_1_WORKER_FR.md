# R23.1 — worker LCD, étude ciblée

Les plages `C0015A60..C0015B50`, `C0015CDC..C00162A8` et
`C00836E4..C0083714` sont identiques octet pour octet dans les deux VSB, lus
après leur en-tête de 256 octets. [Désassemblage](../reports/recovery_r23_1/lcd-disassembly.txt).
Les deux VSB originaux sont vérifiés par SHA avant et après exécution.

| Instruction | Effet directement observé |
|---|---|
| `C0015FB8..5FD0` | charge +4, XOR 1 : tout octet autre que 1 sort, y compris 2 |
| `C0015FD4..6034` | si +12 non nul : GPIO, commande 0x81, valeur +8, attente SPI, puis efface +12 ; une faute antérieure empêche cet effacement |
| `C0016038..6064` | si +5 diffère de 1 **et** octet force diffère de 1, sort ; la branche paramètre a déjà eu lieu |
| `C0016068..60B8` | compteur local 0..7 ; comparateur `C0015AB4` à `C0016084` ; si retour non nul, sender `C001613C` à `C00160A0` |
| `C0015AF0..5B38` | force non nul impose résultat 1 ; sinon comparaison 128 octets ; copie source→shadow inconditionnelle avant retour |
| `C0016150..6200` | GPIO, commandes, attente SPI, délai, résolution du shadow et longueur, puis envoi ; attente et délai suivent encore |
| `C00160BC..60C0` | retour ; pas d'effacement de +5 dans ce corps |

Attention aux conventions : force=2 et demande=0 ne franchissent pas le test
d'entrée ; si +5=1, force=2 est non nul dans le comparateur et force l'envoi.
Les sorties sont des retours sans contrat d'ACK physique. Le sender lit le
shadow, pas directement le buffer privé Mercury.

Le dispatcher à `C0015DD0` admet notamment opcode 2 (demande) et 3 (worker) ;
les appels directs `C0015E58` et `C0015F38` atteignent le worker. Le tick
`C008370C` est un branchement terminal vers le dispatcher. Le scan trouve
douze candidats B/BL vers celui-ci ; appels indirects, données, Thumb et alias
ne sont pas exhaustivement résolus. Le worker appelle le comparateur et le
sender directement ; les chemins IRQ/FIQ/DMA, autres auteurs et états des
tâches n'ont pas été reconstitués complètement.

## Tests ARM nouveaux

Six scénarios par VSB, originaux exécutés sous QEMU avec mappings anonymes
isolés, aucune réponse périphérique simulée. Les records bruts source, shadow
et descripteur sont comparés entre VSB et relus indépendamment.

| Cas | Expérience | Résultat |
|---|---|---|
| 0 | actif, demande, pages égales | retour normal, +5 persiste |
| 1 | pas de demande, source modifiée | aucun scan ; shadow inchangé |
| 2 | suspension par omission de l'appel dans la fixture, image Mercury privée ; comparaison explicite au retour | shadow préservé jusqu'à la comparaison ; comparaison copie la page ; aucune transmission prétendue |
| 3 | demande et page 3 modifiée | shadow mise à jour puis faute GPIO 0xBC, avant envoi confirmé |
| 4 | demande=0, paramètre +12 en attente | faute GPIO 0xBC avant le test de demande |
| 5 | demande=0, force=2, page modifiée | retour sans scan, shadow inchangé |

Total : 8 retours et 4 fautes attendues ; six paires de records strictement
identiques. R9 fournit les cas complémentaires force=1/2, deux appels worker,
faute avec bases GPIO natives et mélange de pages. Le cas 2 ne réalise pas de
publication physique Mercury, et la comparaison explicite ne constitue pas une
restauration LCD.

## Frontière théorique et conditions

Dans la fixture, empêcher l'entrée du worker avant son appel conserve le shadow
tant qu'aucun autre auteur n'y touche. Cela identifie une frontière **théorique
conditionnelle**, non une autorité installable prouvée. Il faudrait notamment
maîtriser tous les appels et accès directs, les paramètres +12, l'état d'un
worker déjà engagé, les périphériques et leur ACK, les IRQ/FIQ/DMA et la
concurrence, puis disposer d'une restauration complète effectivement acquittée.
Une suppression à mi-worker est tardive pour les pages déjà copiées. La faute
du cas 3 montre que shadow à jour ne signifie pas LCD à jour. EXIT doit rester
une demande jusqu'à la fin réelle et à la restauration ; aucune preuve native
de drain ou de récupération n'est obtenue.

Les simulations `adversarial.json` illustrent collision, ordres de fin, faute,
retour tardif, réentrée et faux ACK. Elles ne justifient pas les règles de
synchronisation matérielles ni une absence d'effet sur l'audio. **NO GO pour
intégration matérielle ; faisabilité d'un contrôle à l'entrée NON DÉMONTRÉE.**
