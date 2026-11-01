# Mercury Dust — MD37 : activation réelle des tâches, événement bouton et LCD (SANS FLASH)

**31 octobre 2026. Audit binaire statique reproductible sur les deux `.VSB` originaux.** Aucun installateur/`SYSTEM.VSB`, aucune modification de l'Electribe ou des deux originaux. La branche V29.4 fusionnée reste inchangée, avec V30 Groove, 8 presets, 12 paramètres globaux, page par piste masquée et mini-LFO gelés.

## Résultat principal — activation logicielle de la tâche 2

MD36 avait mis en évidence la table des dix descripteurs et la fonction de la deuxième tâche, `0xC002AA34`, mais pas sa demande de démarrage. **MD37 retrouve cette demande explicite** :

1. Première tâche Korg : descripteur `0xC00A37A8`, fonction initiale **`0xC002AB7C`**, drapeau initial `2`.
2. Chemin statique dans cette fonction : à **`0xC002ADA4`**, branche directe vers **`0xC002B038`** (sur un chemin conditionné en amont).
3. À **`0xC002B044`**, `MOV r0,#2` ; à **`0xC002B048`**, `BL 0xC00005A0`. Les paires suivantes font `MOV r0,#3…#10` et appellent la **même** API aux adresses `0xC002B050` à `0xC002B088`.
4. L'API noyau **`0xC00005A0`** utilise l'identifiant de tâche (1..10), l'index `id-1` et la table des états de tâches à **`0xC06A24E4`**. Elle contrôle notamment un indicateur d'état à `+0x0C` et, sous condition, appelle **`0xC00003D8`** à `0xC000062C` pour préparer le contexte. À `0xC00005B4..BC`, elle teste le bit d'interruption IRQ désactivée du registre CPSR et emprunte un chemin de refus si ce bit est actif : **l'API n'est pas un point d'entrée à appeler depuis n'importe quel contexte**.
5. La deuxième entrée de la table pointe vers **`0xC002AA34`**, qui appelle la chaîne d'initialisation des callbacks LCD (`0xC002A978` puis `0xC002A8D4` comme constaté dans MD35).
6. Une **autre** demande de démarrage de la tâche 8 existe déjà à **`0xC002AE38..3C`**. On ne peut donc pas supposer que tous les démarrages ont lieu une seule fois ou qu'ils sont toujours exécutés dans l'ordre linéaire, sans comprendre les conditions préalables.

**Portée :** un mécanisme de **démarrage explicite** des tâches secondaires est maintenant identifié dans les deux images. Cela ne prouve ni le chemin d'exécution effectif dans toutes les conditions, ni le contexte des appels (IRQ, concurrence, moment de la séquence), ni l'existence d'un point sûr pour injecter Mercury. L'API est analysée, **pas appelée**.

## Chaîne matérielle candidate des boutons — progrès sans preuve des codes

Les instructions suivantes sont présentes à l'identique dans les deux VSB :

- `0xC002A4DC` appelle **`0xC002814C`**, répartiteur d'événements décodés.
- Pour le cas de type **0**, ce répartiteur lit **l'identifiant d'événement à `+0x0D`** (`0xC00281FC`) et le **champ d'appui à `+0x0E`** (`0xC00281F4`), normalisé en booléen (`0xC0028204`).
- `0xC0028208` redirige vers **`0xC00839F0`**, qui forme un message de type 1 (`0xC0083A00`) puis l'envoie via **`0xC0083FE8`**.
- Le chemin `0xC0083FE8` récupère un gestionnaire de réception et invoque **indirectement** un callback de sa table virtuelle (`0xC008401C`, `0xC008402C`). C'est un **point de diffusion d'événement**, pas une fonction physique de touche dont le contrat complet est prouvé.

**Important :** ces octets ne suffisent pas à identifier avec certitude `SHIFT=0x0A`, `LPF=0x12`, `HPF=0x14`, `BPF=0x16`, ou **EXIT**. Les numéros de touches et l'ownership des appuis/relâchements restent à valider sur un vrai appareil ou via une méthode de diagnostic non invasive. Le système de capture Mercury ne doit donc pas être branché en aveugle.

## LCD — points natifs confirmés, pas de timing matériel

- Le callback natif `0xC002A71C` prépare l'**opcode LCD 3**, puis saute au dispatcher `0xC0015DD0`.
- Le pointeur de callback est issu du **littéral** `0xC002A970`, chargé à `0xC002A918` et stocké dans un objet pendant l'initialisation (`0xC002A928`) ; il ne s'agit pas d'un emplacement de callback à écraser à chaud.
- Le comparateur appelé depuis `0xC0016084` est **`0xC0015AB4`**. Ses littéraux d'accès désignent la source `0xC031B710` et le shadow `0xC031B310`. Il compare et copie des **pages de 128 octets**, via `0xC00097A8` et `0xC000985C`.
- Le démarrage de la première tâche émet également les opcodes **2 puis 3** aux sites `0xC002AC4C` et `0xC002AC5C`.

Cela confirme des relations dans le **code statique**, pas l'instant de consommation par le contrôleur LCD ni l'absence de concurrence avec audio/SPI/DMA.

## Mémoire / audio — problème non résolu

- La réservation candidate Mercury `0xC01D0000..0xC01E1000` est entièrement `FF` **dans le fichier** des deux VSB ; aucun mot 32 bits aligné du fichier ne contient une adresse dans cette plage.
- Les dix régions de piles décrites dans la table ne chevauchent pas la réservation ; les zones de pile démarrent à `0xC0200000`.
- La réservation **est cependant située dans la plage de l'image de code/application** `0xC0000000..0xC0200000`. Le contenu `FF` et l'absence de pointeur littéral **ne prouvent pas** qu'elle est réellement libre en RAM après le chargement, ni qu'aucune allocation/overlay/DMA/audio ne l'utilise.
- La boucle initiale de mise à zéro observée dans MD36 commence à `0xC0200000`, mais ses bornes ne suffisent pas à cartographier tout l'usage de la mémoire.

**Conclusion mémoire : ne pas déclarer la zone sûre.** La coexistence avec l'audio ne peut pas être prouvée uniquement à partir de ces deux fichiers.

## Récupération sans JTAG — vérification de documentation externe

- La **documentation officielle Korg** présente l'actualisation 2.02 comme une mise à jour système via la carte mémoire, avec une procédure à exécuter sur l'instrument. Elle ne constitue **pas** une garantie de récupération après un blocage du démarrage. Source : https://www.korg.com/us/support/download/software/0/368/2579/
- Le guide de paramètres explique que **SOFTWARE UPDATE** est une fonction du menu de l'instrument ; sans accès au menu, cette procédure n'est pas une solution de récupération démontrée. Source Korg : https://www.korg.com/us/support/download/product/0/368/
- Une discussion de propriétaires rapporte un cas où le démarrage ne se terminait pas et où la carte SD n'était pas prise en compte ; des membres y évoquent **JTAG**. C'est un témoignage, pas une preuve générale que tout appareil bloqué exige JTAG. Source : https://www.korgforums.com/forum/phpBB3/viewtopic.php?t=125862

Sans procédure indépendante de récupération éprouvée, **aucun flash expérimental** n'est justifié.

## Validation MD37

- **82/82 signatures statiques** sur chaque VSB (**164/164** vérifications au total, sur deux images), y compris le démarrage de tâche 2 à 10, le répartiteur des événements, le LCD, le placement mémoire et les descriptions de piles.
- **31/31 altérations** de copies en mémoire détectées par les signatures ; aucun VSB n'a été modifié.
- Séquences de démarrage et de décodage événementiel **identiques** dans les deux images, selon SHA-256 des régions correspondantes.
- Test de régression de la branche **V29.4 A+B** réexécuté : tests hôte, compilations ARM, contrôles **28/28 par VSB**, mutations **14/14**, tous réussis.
- Hashes originaux contrôlés avant/après audit : `user_custom` = `81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03` ; `user_backup` = `06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052`.

**Limite des comptes :** chaque signature confirme un mot ou une propriété précise, pas une couverture complète du firmware. Les tests hôte reposent sur un environnement simulé. Ne pas extrapoler ces résultats à la sûreté physique.

## Suites prioritaires

1. Chercher les conditions et le contrat d'appel réels de la tâche 2 et du gestionnaire événementiel, **sans patch**.
2. Trouver des preuves supplémentaires de disposition mémoire et des scénarios d'usage audio, sans supposer que des `FF` sont de la RAM libre.
3. Identifier les codes de touches, dont EXIT, et vérifier appui/relâchement avant toute capture.
4. Chercher une récupération sans JTAG réellement valable pour le scénario où le menu ne démarre plus.

**Décision MD37 : audit PC uniquement. Aucun code ou binaire installable, aucun flash.**

## Reproduire (PC, Python 3 sans dépendances)

```bash
python3 md37_audit_readonly.py /chemin/user_custom.VSB /chemin/user_backup.VSB > md37_resultats.json
```

Le programme vérifie les SHA-256, effectue des contrôles en lecture seule et n'écrit que sur la sortie standard. Les mutations sont faites sur des copies Python.
