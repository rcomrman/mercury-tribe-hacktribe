# Mercury Dust — Comparaison visuelle V30 / BLECHTRIBE (10 novembre 2026)

## Référence de vérité

`reference/Mercury_Dust_V30_Groove_CORRIGE_Reference.html` reste **la V30 à préserver**. Je l'ai exécutée dans Chromium avec **DÉMO SILENCIEUSE**, en capturant son canvas monochrome 128 × 64.

Les grands critères observés **dans les images produites**, et pas seulement déduits du code :

1. La matière s'enroule en **grandes boucles non symétriques**, parfois repliées en arrière dans l'axe X. Ce ne sont pas des bandes `y = sin(x)`.
2. La **lame blanche et ses bords fins** entourent des **cavités noires profondes** ; les parties du ruban se masquent et se croisent.
3. Plusieurs **filaments délicats** suivent les mêmes chemins que la masse blanche ; les reflets ne forment pas un champ d'étoiles aléatoire.
4. La largeur de la matière **respire, se dilate puis retombe** selon la vie des notes et du kick.
5. Le rendu d'origine est génératif (path 94 segments, polygones, courbes, plusieurs rubans, post-process), pas une boucle de GIF.

## Ce que nous avons vraiment dans BLECHTRIBE

| Variante | Géométrie | État |
|---|---|---|
| R2.1 `mercury_v30_lab.js` | 1–2 bandes suivant des ondes, largeur 4/8px | Test VM ✅ ; trop rigide |
| R3 `mercury_r3_bitmap_lab.js` | Ruban ondulé, bitmap 2px/32×64, 4 tranches par image | Test VM ✅ ; trop sinusoïdal |
| R4 `mercury_r4_braid_lab.js` | **Deux rubans tressés**, creux noirs mobiles, domaine spatial déformé | Test VM ✅ ; conserve l'apparence de longues ondes |
| R5 `mercury_r5_coils_lab.js` | **Deux boucles creuses** asymétriques, lames blanches, reflets intérieurs, pulsation géométrique sur step/pad | Test VM ✅ ; géométrie plus proche des boucles V30, mais trop régulière |

### Validation R5 — simulation, pas matériel

- Compilateur officiel `kuhlers-gelumpe` (script API 6), 8 modes, tests d'édition et sauvegarde, valeurs extrêmes, essais de mouvement.
- R5 actuel : **5 076 octets** de bytecode, **620 variables VM**, coût `frame` observé au plus à **17 301 unités**, sous la limite VM de 20 000. [Exécution GitHub Actions](https://github.com/rcomrman/mercury-tribe-hacktribe/actions/runs/42884053001).
- `render-motion-r5.mjs` enregistre **48 vraies images du simulateur**, toutes distinctes, issues d'une simulation d'événements musicaux.
- La technique par tuiles dessine **32×64** pixels par rappel et couvre les **128×64** en quatre rappels de 40 ms (environ **6,25 images complètes/s**), insuffisant pour la fluidité 25 fps de la V30 originale.
- **Aucune preuve de durée réelle de 5 ms ARM, aucune intégration au signal audio du DSP, aucun essai sur l'Electribe, aucun firmware flashé.** Les effets musicalement synchronisés sont des impulsions synthétiques sur les événements de steps/pads.

## Ce qui manque objectivement à R5

- De véritables **courbes paramétriques repliées** (`x(u), y(u)`, normales et épaisseur), comme dans `buildRibbon` et `drawTube`. R5 n'est encore qu'une approximation par arcs et un raccord central.
- La multiplicité des filaments, fissures, coulures épaisses et reflets intérieurs à l'écran.
- Une cadence visuelle appropriée au live et des **déformations battues en temps réel**, pas seulement le changement de phase à chaque image complète.
- L'édition **par piste** des 24 paramètres, les huit presets artistiques exacts et la véritable réactivité aux événements par piste.
- L'audio DSP n'est pas accessible par cette API de plugin : **ne pas promettre de détection de kick depuis la sortie audio**.

## Décision de conception

Garder R3, R4 et R5 **tous séparés** dans cette branche. La réussite des tests du simulateur ne rend pas R5 artistiquement validée.

Deux pistes raisonnables :

- **Plugin JS** : poursuivre l'exploration de la géométrie des enroulements, optimiser les masques et démontrer une cadence acceptable dans les 20 000 unités de la VM ; conserver ses contrôles, huit variations, steps/pads et menus.
- **Rendu C natif** : utiliser `src/mercury_live.c` comme base fixe pour une migration plus fidèle de `buildRibbon`, mais les points d'injection ARM/écran ainsi que la sécurité mémoire et la récupération matérielle restent **non prouvés**. Aucun patch flashable ne doit être proposé en l'état.

**Objectif artistique** : le mouvement doit sembler tourner autour de lui-même et se déplier, plutôt que faire onduler les mêmes barres en boucle. C'est le critère principal à chaque comparaison à venir.
