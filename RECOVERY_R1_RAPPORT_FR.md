# Mercury Dust — récupération R1

Date : 2 novembre 2026. Branche : `recovery/mercury-dust`, base MD45 `ac7c7399cf12f59634125beee89e9b375797ec10`.

## Résultat réellement obtenu

Les fondations des expériences de rendu intégral et différentiel sont reconstruites et exécutées sous QEMU ARM926 sur les deux VSB originaux. Ce sont de nouveaux bancs R1, pas les fichiers originaux MD77–MD78 récupérés. MD88 n'est pas commencé.

Le répertoire `src/` et la référence HTML restent inchangés. Le générateur réutilise `md15_bridge`, `md21_v14_profiles`, `mercury_live`, `mercury_events`, `mercury_glitch` et `lcd_source_mux`. Il produit quatre images pour chacun des huit profils existants, avec notes et horloge explicitement synthétiques : ticks 0, 24, 48, 72 ; temps tick×20 ms ; intensité 85 ; huit notes de hauteur 36+c×5 et vélocité 100+c×3 ; avancement d'image 40 ms. Ce choix est une nouvelle fixture déterministe, pas une lecture native de pattern.

Aucune modification des douze commandes globales, des quatre mini-LFO, des profils ou des IFX. La préservation des IFX est assurée par l'absence de toute écriture des VSB ; leur coexistence matérielle n'est pas testée. L'identité artistique avec les anciennes captures MD77 n'est pas démontrable sans leurs fichiers.

## Vérifications et résultats

- MD43 et MD44 hôte : réussite, avec AddressSanitizer et UndefinedBehaviorSanitizer.
- Suite `run_merged_v29_4.sh` : réussite des tests hôte, construction ARM et audits statiques ; 28/28 contrôles par VSB ; 14/14 corruptions statiques détectées en mémoire.
- Audit MD31 complémentaire : 6/6 mutations rejetées en mémoire. Son test accepte désormais un chemin VSB explicite, car son ancien chemin `/mnt/data` aurait provoqué un saut du test.
- Préaudit ABI MD45 : 30/30 contrôles, deux VSB compris. Il reste statique.
- R1 : génération des 32 images avec sanitizers, 32 images distinctes.
- Rendu intégral : 32 × 8 192 = **262 144 appels** à la primitive native par VSB.
- Rendu différentiel : **59 793 appels**, soit **77,19 %** d'appels économisés sur cette fixture (pas une mesure de temps CPU).
- **70 enregistrements par VSB**, chacun contenant les compteurs et les 1 024 octets effectivement obtenus : 32 intégrales, 32 différentielles et six contrôles supplémentaires.
- Le code ARM contrôle tous les octets et les deux sentinelles entourant le framebuffer après chaque rendu. Python contrôle indépendamment les dumps, les compteurs et les différences attendues.
- Les sorties binaires ARM des deux VSB sont strictement identiques.

Les sorties détaillées sont dans `reports/recovery_r1/results.json`, les journaux de validation et `presets.png`. La planche représente les nouvelles images d'entrée vérifiées, pas une capture de LCD physique.

La compilation actuelle de la base produit une section texte de 0x6BD8 octets contre 0x6BF4 dans le rapport historique, avec des adresses internes décalées. Les sources restent identiques et les contrôles ABI passent ; aucune identité binaire historique n’est revendiquée. Les trois rapports ARM historiques ont été conservés inchangés ; les nouveaux sont archivés sous `reports/recovery_r1/baseline_*`.

## Primitive Korg et environnement reconstruit

Le banc Linux ARM charge en mémoire privée les 0x200000 octets d'application du VSB, après son en-tête de 0x100 octets, à `0xC0000000`. Après copie, cette zone est protégée en lecture/exécution. Une page RAM anonyme et initialement nulle est créée à `0xC031B000` ; le framebuffer est à `0xC031B310`, entouré des sentinelles 0x39 et 0xC5. Les pointeurs x, y, valeur sont des entiers 32 bits ; la pile du point d'entrée est alignée sur huit octets.

Les appels de pixel vont à **`0xC0015824`**, sans remplacement ni patch. Ses appels originaux à `0xC0015B50` (bit), `0xC001531C` (zone modifiée), `0xC00153C8` et `0xC0015428` sont exécutés également. La trace QEMU de blocs d'instructions confirme ces cinq entrées pour chacun des VSB. Les traces complètes restent dans `build/recovery_r1/*_trace.log`, régénérables et exclues de Git.

Cette mémoire n'est pas une initialisation complète du LCD Korg. Aucun worker LCD, ordonnanceur, IRQ/FIQ, DMA, cache matériel, chargement sur instrument ou cycle C006F178 complet n'est validé.

Le premier essai du nouveau linker échouait avant l'entrée C : des segments ELF de permissions différentes partageaient une page, rendant l'entrée non exécutable sous QEMU. Le linker R1 sépare désormais les segments sur des frontières de 64 Kio. Ce problème de banc a été corrigé avant la validation finale.

## Contrôles essentiels

| Contrôle | Résultat sur chacun des VSB |
|---|---|
| Départ non vide en damier | Rendu intégral et première image différentielle exacts |
| Image inchangée | 0 appel, 1 024 octets exacts |
| Inversion complète | 8 192 appels, allumages et extinctions exacts |
| OFF simulé | Cible synthétique `(i×37+13) mod 256` reconstruite exactement |
| Écriture native indépendante, cache laissé valide | 0 appel ; un octet incorrect attendu et détecté, bit 7 de l'octet 3 |
| Invalidation du cache | 8 192 appels ; réparation exacte des 1 024 octets |
| Image répétée après réparation | 0 appel et framebuffer exact |
| Mutation du banc supprimant les appels pixel | Exécutable rejeté au premier rendu, code de sortie 5 |

La corruption attendue est une démonstration contrôlée de cache périmé ; elle ne constitue pas un défaut matériel observé.

## Entrées originales et substitutions

VSB vérifiés avant et après le test, uniquement ouverts en lecture :

- custom : `81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03` ;
- backup : `06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052`.

Les deux fichiers font 2 097 408 octets. Les scripts refusent une taille ou une empreinte différente. Les copies d'application et les ELF de laboratoire ne sont pas publiés dans Git.

Substitutions explicites : Linux user-mode pour l'environnement d'exécution ; syscalls Linux pour mmap/mprotect/cacheflush/write/exit ; RAM anonyme pour l'état graphique ; notes, temps et cible OFF synthétiques ; algorithme différentiel R1 privé à producteur unique. Le moteur MD45 s'exécute sur l'hôte pour générer les images, puis les octets servent d'oracle au banc ARM. Aucun service Korg appelé par la primitive étudiée n'est remplacé. Aucun verrouillage ou arbitrage matériel n'est simulé comme preuve de sûreté.

## Différences avec les anciens MD77–MD78

| Ancien historique rapporté | R1 reconstruit |
|---|---|
| Scripts MD47/MD74/MD77 et enveloppes originales indisponibles | Nouveau démarrage, linker, générateur et orchestrateur sous `recovery_r1` |
| Images historiques non disponibles | Nouvelle fixture, huit profils × quatre temps, moteur MD45 inchangé |
| MD78 annonçait 63 926 appels / 75,61 % | Nouvelle mesure : 59 793 / 77,19 % ; séquences non identiques, aucune amélioration historique revendiquée |
| 36 enregistrements dans la transcription MD78 | 70 : intégral + différentiel + six contrôles, dumps vérifiés côté hôte |
| Invalidation avec rafraîchissement | Démonstration supplémentaire de l'échec sans invalidation, puis réparation et répétition |
| Anciens fichiers de build et captures | Aucun original retrouvé ; nouveaux résultats avec provenance et empreintes |

## Reproduction

Dépendances : Clang/LLD/LLVM, QEMU user-mode et Python 3 avec Pillow. Versions utilisées : Clang et LLD 19.1.7 ; QEMU 10.0.13. Sur Debian : paquets `clang lld llvm qemu-user python3-pil`. Aucun téléchargement automatique dans le banc.

```bash
# Dans cet environnement seulement, si nécessaire :
export PATH=/workspace/mercury-tools/bin:$PATH
bash tests/run_recovery_r1.sh '/chemin/user_custom (2).VSB' '/chemin/user_backup.VSB'
```

Le lanceur rejoue la base et R1. Il régénère les rapports et les fichiers de laboratoire dans `build/`. Les scripts historiques régénèrent aussi leurs rapports ARM suivis : les comparer avant de les inclure dans un commit. Aucun chemin de flash ou patch VSB n'existe dans les nouveaux scripts.

## Suite proposée

Préserver en priorité la possibilité de restaurer l'ancien volume et ses commits. À défaut, reconstruire ensuite les composants UI/listes et leur cycle de destruction avant les transitions et files MD84–MD87. MD53, MD59, le pont musical, les payloads et les preuves de concurrence restent à retrouver ou à reconstruire. Les résultats R1 ne lèvent pas les limites de propriété du framebuffer ni les inconnues matérielles.
