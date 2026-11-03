# R15 — frontières de dispatch et couverture

RESEARCH_ONLY, base81d6dcb. Aucun hook ni changement d'instruction.21 plages identiques sur les deux VSB ; appels et pointeurs ARM alignés candidats dans audit.json. « PROUVÉ » qualifie le fait indiqué, pas une protection globale.

## UI : C002D030

r0 pointe un wrapper dont +4 est le gestionnaire. La fonction recharge ce pointeur **au moment de l'appel**, puis appelle gestionnaire.vtable+0xC avec le gestionnaire dans r0. Aucun message n'est fourni à cette frontière : le consommateur virtuel vide sa propre queue. Appel direct identifié C002B1EC dans tâche4 C002B144 ; aucun pointeur aligné vers C002D030 trouvé. Cela n'exclut pas les appels calculés.

Le gestionnaire principal utilise C0083848, l'alternatif C0083428. Le premier consomme des messages16 octets sur sa pile, appelle le slot+0x10 et recommence sans quota. La queue copie les mots, pas les objets pointés qu'ils pourraient désigner. Le publisher C0083FE8 ne fournit pas ici d'accusé fiable de livraison : le gestionnaire absent/inactif peut ignorer le message, et le retour du slot de queue n'est pas exploité par ce wrapper.

Différer **l'invocation** de C002D030 ne signifie pas différer exactement une commande UI. Des messages nouveaux peuvent arriver et wrapper+4 peut changer. Une référence brute au gestionnaire ne prouve ni sa durée de vie ni celle des pages/enfants ; les transitions/destructions doivent être couvertes. Points candidats : avant invocation complète pour la composition, ou avant extraction d'un message si une preuve de conservation est ajoutée. Aucun des deux n'est installé.

## Services : C002D684

r0=gestionnaire de services ; r1=message16 octets : vtable à0, type signé8 bits à+4, mots à+8/+0xC. Appel direct C002D87C dans le consommateur C002D844, depuis tâche5. La publication C002D5D8 crée/copie un message et appelle la queue par slot+8. Le consommateur C003B81C copie type et deux mots, puis retire l'élément.

C002D684 pose manager+0x10=1, choisit l'objet dans C03404C8[type], écrit manager+0xC=type, remet objet+0x19 à0 et appelle slots+0xC, +8 puis +0x10. Il peut émettre des changements UI25/26/28/29, afficher un résultat27 et publier un message UI16 contenant objet+4 et statut+0x18. Il remet manager+0xC à−1 et manager+0x10 à0 avant de nettoyer ses deux handles temporaires.

La table C00A4758 fournit le destructeur+4 C002D434, qui appelle C0028DD4 pour libérer le petit objet lui-même, sans copie profonde du mot+4. Cette route est vérifiée statiquement ; le service complet et son allocateur ne sont pas rejoués.

Les deux mots du message deviennent les champs+4 de petits objets alloués ; leurs adresses sont placées dans deux handles sur **la pile du dispatcher**. Le slot+8 reçoit r1=sp et r2=sp+4. Au retour, C002D5B0 appelle le destructeur virtuel+4 des objets. **Copier ces handles ou conserver leurs adresses au-delà du retour n'est pas une conservation de commande sûre.** Un report doit précéder leur construction, ou disposer de vrais contrats de propriété profonde. Les mots+8/+0xC peuvent être des pointeurs dont la durée de vie n'est pas prolongée par une copie16 octets.

C002D88C appelle le slot+0x14 du service courant, via manager+0xC et C03404C8. C002D8B8 est un accès global à ce wrapper. Plusieurs tables mettent C002DE78 au slot+0x14 ; ce corps écrit seulement octet+0x19=1. Le dispatcher remet ce même drapeau à0 au début de chaque opération. Le drapeau busy+0x10 et le numéro courant sont des observations, pas une exclusion ou preuve de cessation.

Les routes services17/34 et leurs drapeaux de progression établies R14 sont conservées. Les allocations, transformations UI, destructeurs et tous les effets du corps rendent insuffisante une substitution d'un simple retour « en attente ». Le service complet n'est pas requalifié dynamiquement ici ; les sous-frontières sont exercées sans patcher l'allocateur.

## Worker périodique : C002A71C

Cette fonction ignore les arguments entrants, charge r0=C031BB2C, r1=3, r2=0 et branche vers C0015DD0. Son adresse est présente à C002A970, dans la construction du compteur. C002A7EC décrémente compteur+4, recharge depuis+8 à échéance et appelle callback+0xC. Le gestionnaire de mises à jour est en tâche2, priorité initiale1. Le callback appelle le worker **synchronement** : aucune frontière de tâche indépendante n'est créée.

Un wrapper du compteur pourrait différer une intention de scan dans le banc ; fusionner des appels périodiques reste distinct d'une conservation exacte de commandes synchrones. Le descripteur a une adresse fixe mais dépend des objets GPIO/SPI et de l'état de source/shadow. Son retour, surtout inactif/unchangé, n'est pas un accusé de transfert.

## Matrice

| Domaine / fait | Niveau | Portée et limite |
|---|---|---|
| UI wrapper charge manager+4 puis slot+C | PROUVÉ | Instructions et callbacks ARM de fixture ; pas tous gestionnaires/pages |
| UI tâche4 et consommateurs principal/alternatif | PROUVÉ pour routes connues | Autres modes/alias : PARTIEL |
| Report exact d'un message par report du wrapper UI | NON COUVERT | Queue mutable, messages multiples et transitions |
| Services tâche5, format/type/deux mots | PROUVÉ | Routes configurées ; type signé sans validation globale ajoutée |
| Handle de pile/destructeur au retour du service | PROUVÉ | Corps natif ; contrats profonds de chaque service INCONNUS |
| Cessation par drapeau arrêt+0x19 ou busy=0 | NON COUVERT | Drapeau réinitialisable, callbacks et accès différés possibles |
| Callback périodique vers LCD3 | PROUVÉ | Instructions et essais normaux/faute ; source/périphérique pas validés matériellement |
| Protection commune UI/service/timer | PARTIEL | Trois points candidats distincts, aucun dominateur global |
| Progression directe, initialisation forcée, diagnostic, LCD7, comparateur direct | NON COUVERT | Contournent au moins une des trois frontières |
| Lecteurs/écrivains calculés, IRQ/FIQ/DMA et enregistrements cachés | INCONNU | Aucun scan de littéraux ne prouve leur absence |

Preuves : `tools/recovery_r15/audit.py`, `reports/recovery_r15/audit.json`, `native_disassembly.txt.gz`. Les niveaux sont conservateurs : aucune transition de tâche ou fin locale n'est promue en preuve d'absence d'accès matériel.
