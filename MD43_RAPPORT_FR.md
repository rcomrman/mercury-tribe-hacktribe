# Mercury Dust MD43 — première séparation de plateforme (SANS FLASH)

Date : 1er novembre 2026.

## Objet et état

Suite à MD41 (barrière de restauration des tampons) et MD42 (échec d'acquittement physique SPI reproduit), ce jalon construit **une frontière de portage**. Le moteur graphique C V30 hérité, ses huit presets, les douze paramètres globaux, les menus et les contrôles restent inchangés.

Deux cibles **simulées** dans un seul programme PC (étiquetées Hacktribe et OmniTribe) consomment une interface identique. Leurs sorties de 1024 octets sont identiques pour les mêmes événements. Il ne s'agit d'aucun firmware réel ni d'un plugin OmniTribe.

## Fichiers ajoutés

- `src/md43_platform_port.h` / `.c` : interface `md43_init`, `md43_key_event`, `md43_ui_tick`, `md43_clock`, `md43_step`. Aucun accès aux adresses Korg, au DSP, au SPI ou à la flash.
- `tests/test_md43_portability.c` : simulateurs de deux plateformes, 8 scènes exercées, mêmes images, navigation des trois pages globales, propriétés des touches et EXIT, rejet/réessai d'un dépôt d'image, maintien des données pistes masquées.
- `tests/run_md43_host.sh` : compilation et test sur PC avec AddressSanitizer + UndefinedBehaviorSanitizer.

## Contrat d'interface et ses limites

- La plateforme possède un snapshot de l'écran natif, un horodatage monotone, un décodeur de touches en événements normalisés et un contexte UI/LCD sérialisé.
- `offer_frame(1024 bytes)` signifie **accepté pour traitement**, et ne signifie **jamais** affiché ni SPI terminé. Si le dépôt est refusé, une nouvelle tentative sera faite au tick suivant.
- `request_native()` signifie **demande de retour native acceptée**, non la preuve de l'achèvement de l'envoi. La faille identifiée en MD42 demeure.
- `md43_key_event()` suppose des identifiants de touches déjà vérifiés ; les codes physiques de Korg ne sont pas fournis. La page PISTES reste masquée et ses valeurs existent toujours en mémoire.
- Ni l'occupation RAM réelle, ni le contexte IRQ/tâche, ni l'ABI, ni le risque de brick ne sont résolus. Ne pas attacher cette interface directement à une Electribe.

## À propos d'OmniTribe (recherches publiques)

Le site officiel au 27 octobre 2026 annonce :

- Les Omni-ROMs dérivés du firmware Korg, avec une VM de plugins à capacités restreintes, en cours de développement : ces plugins **ne garantissent pas l'exécution d'un module natif ARM/C**.
- Le noyau OmniTribe distinct, annoncé comme démarrant depuis SD et proposant des modules chargeables et des pages propres ; c'est la piste **potentiellement** mieux adaptée au rendu, à confirmer à la publication des sources et de l'API.
- L'installeur et les patchs restent annoncés à venir, sans date publique précise vérifiée.

Sources : https://www.omnitribe.org/ et https://www.omnitribe.org/roms/omnitribe-kernel (déclarations de l'équipe ; indépendamment non validées sur notre machine).

## Commandes de reproduction (sur ordinateur)

```bash
bash tests/run_md43_host.sh
bash tests/build_v29_2.sh
python3 tools/md42_audit_native_send_readonly.py '/chemin/user_custom.VSB' '/chemin/user_backup.VSB'
```

Les deux VSB fournis en conversation ont été contrôlés en lecture seule, avec empreintes :

- custom : `81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03`
- backup : `06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052`

## Prochain jalon significatif

Obtenir une API publique/contractuelle avec les appels LCD et touches du noyau OmniTribe, ou un point documenté de raccordement sans flash, puis vérifier le timing et la mémoire *en conditions réelles*. Avant cela, les deux « plateformes » MD43 ne sont que des mocks de test, utiles pour isoler le code à recompiler.

**Aucun VSB, BIN de flash, patch Korg ou installation n'est produit.**
