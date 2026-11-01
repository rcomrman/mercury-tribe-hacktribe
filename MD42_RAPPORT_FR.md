# Mercury Dust MD42 — audit de la chaîne d’envoi LCD (sans flash)

**Objet** : identifier l’origine du blocage matériel et vérifier si l’accusé MD41 prouve la livraison réelle des pixels. **Non** : il prouve uniquement leur convergence dans les tampons.

## Découverte vérifiée dans les deux VSB originaux

Le traitement LCD Korg part de la comparaison de huit pages. Si le comparateur `0xC0015AB4` renvoie « changé », l’appelant situé à `0xC00160A0` appelle `0xC001613C` pour envoyer la page. Ce dernier utilise notamment `0xC00160C4`, qui appelle la fonction I/O `0xC00183CC`. Cette fonction contient une boucle d’attente bornée à **1 000 itérations** et renvoie un état. La fonction `0xC00160C4` ignore cet état et retourne directement ; l’appel de niveau supérieur ne reçoit donc pas d’acquittement du matériel.

Cette conclusion est **statique**. Elle ne confirme ni que tous les échecs de transport sont détectables à `0xC00183CC`, ni que l’envoi est synchrone, ni que le LCD a fini d’afficher les données. Un délai de 1 000 itérations n’est pas une durée mesurée en millisecondes.

## Test de panne MD42

`tests/test_md42_spi_failure_gap.c` exécute le vrai code MD41 compilé pour PC, avec un comparateur Korg simulé qui copie bien les 1 024 octets mais dont le transfert matériel simulé échoue. Le test **démontre que MD41 peut lever le verrou et accepter un réarmement malgré l’échec simulé**. C’est un **test reproduisant une limite connue**, pas un test qui démontre la résolution du problème. Il n’essaie pas de simuler à tort une validation de transfert SPI réel.

## Décision technique

- Conserver MD41 comme garde sur **la cohérence des tampons**, pas comme preuve d’affichage physique.
- Ne pas ajouter de faux acquittement (temporisation arbitraire, second callback, lecture de shadow) : aucun de ces indices ne peut prouver à lui seul la fin de l’envoi.
- Pour progresser vers un firmware installable, identifier une garantie réelle de livraison (API native documentée, retour de pilote validé, ou mesure matérielle non invasive) et une récupération fiable sans JTAG. À défaut, ne pas flasher.
- La mémoire libre et l’absence de perturbation audio restent également non démontrées.

## Reproduire sur ordinateur

Après extraction, avec Clang et Python 3 :

```bash
bash tests/build_v29_2.sh
python3 tools/md42_audit_native_send_readonly.py '/chemin/user_custom.VSB' '/chemin/user_backup.VSB'
```

Ces commandes ne modifient jamais les VSB. Les binaires générés sont **des exécutables de laboratoire sur PC et un ELF ARM de recherche**, pas un SYSTEM.VSB. Ne rien installer sur l’Electribe.

**Rien n’a été modifié** concernant le moteur visuel V30, les huit presets, les douze paramètres globaux, les boutons, les paramètres par piste masqués ou les quatre mini-LFO gelés.
