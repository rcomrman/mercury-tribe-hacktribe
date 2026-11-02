# Mercury Dust — R4 : événements, file native et producteur de navigation

## Objectif et résultat

Le périmètre fonctionnel MD86–MD87 est redémontré sous QEMU, avec des preuves indépendantes : **publication → file Korg → dépilement → dispatcher → transition native**, puis **page 19 native, entrée virtuelle +0x14 → C006BC88 → C0083D28 → même chaîne → page 21**. Les deux chemins existent avec et sans Mercury.

Seize scénarios par VSB ont les issues attendues, dont un échec de dépendance conservé. Les deux flux d'événements ARM et les snapshots sont identiques. La page cible est construite et l'ancienne détruite ; le rendu complet de la page 21 n'est pas validé. R3 reste la preuve de restauration graphique 25 → 29.

## Architecture identifiée

| Fonction | Rôle vérifié |
|---|---|
| C00775EC | Construction des 256 emplacements de message du ring |
| C0070AF0 | Message de 16 octets : vptr +0, type octet +4, arguments u32 +8/+12 |
| C0083FE8 | Publisher : pointeur global C0691378, gestionnaire actif à +112, queue à +12 |
| C00709C0 / C0070978 | Méthode virtuelle d'ajout et corps d'écriture du ring |
| C0070B10 | Extraction ; méthodes virtuelles de disponibilité, lecture et avancement |
| C0083848 | Vidange si gestionnaire actif ; appel virtuel +0x10 pour chaque événement |
| C00834FC | Dispatcher ; type 8 → entrée virtuelle +0x1C du gestionnaire |
| C0083714 | Gestionnaire graphique situé à this+16 ; transmet +8/+12 à C006E8BC |
| C006C030 / C006BED0 | Fabrique et constructeur de la page 19 |
| C00E3B80 | Table native de page 19 ; entrée +0x14 = C006BC88 |
| C006BC88 | Demande la page 21 avec argument nul, via C0083D28 |
| C0083D28 | Contrôles natifs avant publication d'un type 8 |

Le manager UI de fixture possède la table native C00E4C50. Le sous-gestionnaire graphique commence à +16 ; sa page est donc à +32 du manager UI et son identifiant à +44. Aucun dispatcher ni publisher n'est remplacé.

La queue contient un sous-objet à +4, initialisé par C00775EC. Sa table extérieure native est C00E40C8, exactement celle assignée par C0083920. Les indices d'écriture/lecture sont à +8/+12 du conteneur, les éléments à +16, par pas de 16 octets. Les méthodes de verrouillage sélectionnées par cette table sont des retours immédiats : aucune exclusion réelle entre threads n'est établie.

## Hypothèses et expériences

| Cas | Expérience | Résultat par VSB |
|---:|---|---|
| 0 | Message de fixture type 8, page 29 depuis 25 | Publié, consommé, transition native |
| 1 | Idem avec Mercury sortant | Transition et destruction Mercury, sortie/suppression appelées |
| 2 | Publisher avec manager inactif | Aucun message, aucune transition |
| 3 | Type 127 | Message consommé, dispatcher l'ignore, page 25 conservée |
| 4 | Blocage global C0345EC4 actif | Producteur refuse avant publication |
| 5 | Producteur natif demande 29 | Transition après dépilement |
| 6 | Page 19 construite nativement ; appel de son entrée +0x14 | Entrée vérifiée C006BC88 ; événement publié ; page 21 construite |
| 7 | Même chaîne, Mercury ajouté à la page 19 | Mercury dessiné avant demande, puis détruit par la transition |
| 8 | État service +0x308 = 8 | Producteur refuse ; l'état 9 est également bloqué par le code, mais non testé ici |
| 9 | État settings +0x341 non nul | Producteur refuse |
| 10 | Cible égale à la page courante | Producteur refuse |
| 11 | Producteur accepté, publisher inactif | Indicateur UI +40 passe à 1 mais message absent ; page inchangée |
| 12 | 32 allers-retours 25 ↔ 29 par messages | 64 transitions et vérifications des identifiants et indices |
| 13 | 255 messages ignorés puis vidange, puis un message | Vidange et rebouclage des indices réussis |
| 14 | 256 messages sans vidange | Écriture reboucle à zéro ; indices égaux ; la file paraît vide et les demandes deviennent invisibles au consommateur |
| 15 | Page 19 sans région de chaîne vide | SIGSEGV attendu ; dépendance de fixture identifiée, pas contournement de constructeur |

Le cas 11 reproduit la limite MD87 : l'indicateur est écrit avant l'appel au publisher, lequel peut refuser. Cela décrit l'ordre des instructions dans une fixture ; ce n'est pas une preuve de défaut matériel.

## Dépendance manquante explorée

Le premier constructeur de page 19 échouait dans la chaîne de formatage/chaînes Korg, avec accès à C06A1BA8. Le code C00A2D54 lit le compteur à l'adresse du texte moins quatre ; les références natives utilisent la chaîne vide à C06A1BAC. Cette région est distincte du heap mappé en R2.

Le banc normal fournit une page anonyme nulle C06A1000..C06A2000. L'en-tête et le texte vide sont donc explicitement une fixture RAM, non des données originales récupérées. Aucun formatage, constructeur, méthode de page ou contrôle producteur n'est remplacé. L'omission reste testée par le cas 15. Le constructeur complet de la page 19 et le constructeur de la page 21 peuvent ensuite terminer dans ces états de laboratoire.

Les widgets de page 19 utilisent également des services et des listes d'observateurs. Leurs états initiaux sont détaillés ci-dessous ; leur fonctionnement général n'est pas revendiqué.

## États fournis et limites

Réutilisation de R2 : copie privée application, heap natif, pages de données malloc modifiables, initialisation graphique native. Ajouts explicites :

- Région du pointeur de publisher C0691000..C0692000, C0691378 pointant sur le manager de fixture.
- Manager UI nul de 256 octets, table C00E4C50, queue native, actif +112=1, sous-gestionnaire graphique cohérent avec sa page.
- C03404C0 pointe sur ce manager pour le getter C002D048.
- C03405BC pointe sur un service de fixture nul de 788 octets ; C03487E8 sur un objet settings nul de 848 octets. Les getters originaux retournent ces pointeurs existants. Les constructeurs généraux de ces services ne sont pas validés.
- Tables et message initialisés conformément aux routines natives ; les pointeurs globaux et le flag actif sont fournis par le banc, pas découverts dans un instrument en marche.
- Quatre mots sentinelles après la queue, vérifiés sur les chemins de transition ordinaires ; sentinelles framebuffer du support R2. Pas d'audit exhaustif des références externes ou du heap natif.

La queue reste statique dans le processus ; les pages sont détruites. Les scénarios répétés n'exercent ni concurrence ni scheduler. Le cas 14 montre une limite de cette implémentation de ring dans ces états : aucune politique de backpressure externe n'est connue. Ne pas en déduire qu'un panneau réel produit 256 messages sans consommation.

## Nouvelle découverte bornée : ambiguïté plein/vide

Le corps C0070978 calcule l'écart modulo 256 et refuse seulement un écart supérieur à 255. Avec des indices normalisés sur huit bits, les 256 écritures du cas 14 ramènent les indices à égalité. Le consommateur les interprète comme vide. Le cas 13 montre que le rebouclage fonctionne lorsqu'une vidange a lieu avant saturation.

Cette différence entre rebouclage normal et saturation ne figure pas dans le dossier MD86–MD87 accessible. Il s'agit d'une nouvelle preuve du dépôt reconstruit, pas d'une affirmation sur l'exhaustivité des anciens rapports.

## Preuves et comparaison historique

[Événements, compteurs et empreintes](reports/recovery_r4/results.json), [journal](reports/recovery_r4/validation.log). Les flux compressés contiennent chaque snapshot complet et les traces QEMU montrent les routines natives traversées. Les compteurs d'allocations laboratoire ne représentent pas le heap natif.

MD86 est retrouvé par les cas 0/1 ; MD87 par 6/7 et les contrôles du producteur. Le déclencheur amont reste un appel direct du banc à l'entrée virtuelle de page 19. Ce n'est **pas** une commande physique ni encore l'identification de son appelant réel.

Les captures de cette phase sont des états source avant/après destruction, pas une preuve de dessin final de la page 21. Le rendu, la direction artistique, les huit presets, les douze commandes, les quatre mini-LFO et les IFX n'ont pas été modifiés.

## Reproduction et suite

```bash
export PATH=/workspace/mercury-tools/bin:$PATH
bash tests/run_recovery_r4.sh 'custom.VSB' 'backup.VSB'
```

Le lanceur reconstruit les prérequis R1/R2/R3. L'orchestrateur seul peut réutiliser les entrées générées par R2. Les SHA VSB sont contrôlés avant et après ; seuls des ELF Linux de laboratoire sont produits dans build/, jamais un VSB ou un firmware installable.

R4 autorise une phase R5 bornée : remonter de C006BC88 aux appels virtuels en amont, avec contrôle explicite des types d'événements et sans attribuer de bouton sans preuve. Restent non validés : cycle C006F178 complet, panneau physique, LCD2/transmission LCD, IRQ/FIQ, DMA, cache, chargeur et récupération matérielle.
