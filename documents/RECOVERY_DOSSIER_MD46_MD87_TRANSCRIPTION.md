# Dossier de récupération Mercury Dust — état de la session

**Je n’ai actuellement accès ni aux fichiers de l’ancien environnement, ni à Git, ni aux commits locaux.** J’ai réessayé : l’environnement répond comme indisponible et la connexion est hors ligne. Je ne peux donc pas vérifier l’existence actuelle du commit `4c1ec01`, créer une archive ZIP fidèle, produire un Git bundle ou publier une branche GitHub.

Le dernier commit annoncé dans cette conversation est **`4c1ec01`**, sur la branche locale **`experiment/md53-triple-buffer`**. Cela indique ce qui avait été enregistré avant la panne, mais ne prouve pas que le stockage est définitivement perdu.

**Priorité de récupération recommandée : demander la restauration ou l’export du volume de l’ancien environnement avant de le remplacer ou de le supprimer.** Les identifiants utiles sont :

- Dépôt : `rcomrman/mercury-tribe-hacktribe`
- Branche locale : `experiment/md53-triple-buffer`
- Dernier commit local annoncé : `4c1ec01`
- Dernier commit annoncé sur GitHub : `ac7c739`, MD45 — information fournie dans votre demande, non vérifiée ici.
- Environnement : `ccarenv_b64_Y2NhcmVudl84NmUzMjA4ZjhhNTg4MTkxYjM1ZWVjZTUwNTcwMzU1Yw`

Si le volume est récupéré, il faudra conserver **tout le répertoire du dépôt, y compris `.git`**, puis créer le ZIP et le bundle depuis cette copie. Ne pas relancer une réinitialisation qui écraserait le volume avant cette tentative.

Les informations ci-dessous proviennent de la conversation et des comptes rendus précédents. Elles ne remplacent pas les fichiers originaux. Les noms de fichiers et résultats sont restitués lorsqu’ils sont visibles ; une mention « non retrouvé » signifie **non accessible dans cette session**, pas nécessairement détruit.

---

## 1. Historique disponible de MD46 à MD87

| Étape | Ce qui reste identifiable dans la conversation |
|---|---|
| **MD46** | Corrections ARM et tests QEMU antérieurs à MD47. Le détail exact des fichiers et corrections n’est pas suffisamment visible ici. `MD46_RAPPORT_FR.md` et `reports/md46_validation.txt` ont été vus dans le dépôt. |
| **MD47** | Audit du chargement et de la mémoire, notamment `C01D0000` et `C01E0000`, collisions possibles et preuves manquantes. Fichiers connus : `MD47_RAPPORT_FR.md`, `reports/md47_validation.txt`, `reports/md47_stack_frames.tsv`. |
| **MD48** | Étude de faisabilité Hacktribe/OmniTribe, LCD, boutons et concurrence. `MD48_RAPPORT_FR.md`, `reports/md48_validation.txt`. Les conclusions détaillées ne sont pas intégralement visibles. |
| **MD49** | Analyse en lecture seule des deux VSB, empreintes, routines LCD, panneau, mémoire et différences. `MD49_RAPPORT_FR.md`, `reports/md49_original_audit.json`, `reports/md49_selected_disassembly.txt`, `reports/md49_validation.txt`. |
| **MD50** | Analyse du sender LCD, des attentes sans borne, des tâches, files et signalements Korg. `MD50_RAPPORT_FR.md` et plusieurs fichiers `reports/md50_*`. |
| **MD51** | Étude UI4 → LCD2, événements et concurrence. Preuves QEMU d’une image partielle et d’une corruption possible d’événement lors d’une préemption injectée. `MD51_RAPPORT_FR.md`, `tests/arm/md51_native_probe.c`, `tests/run_md51_native.sh`, `research/md51_ui4_adapter.c`. |
| **MD52** | Étude des tampons privés, IRQ, cache, priorités et limites d’un watchdog. `MD52_RAPPORT_FR.md`, `reports/md52_validation.txt`. |
| **MD53** | Triple buffering expérimental, propriété des images et transitions ON/OFF. Fichiers connus : `research/md53_frames.c`, `tests/run_md53.sh`, `MD53_RAPPORT_FR.md`, `reports/md53_validation.txt`. Branche expérimentale citée ci-dessus. |
| **MD54** | Adaptateur expérimental utilisant le worker LCD Korg et une image privée, sous QEMU. `MD54_RAPPORT_FR.md`, `research/md54_scan.c`, `tests/arm/md54_abi.S`. |
| **MD55** | Cartographie des appels LCD et étude de la sérialisation. `MD55_RAPPORT_FR.md`, `tools/md55_prepare.py`. |
| **MD56** | Contrôleur expérimental de propriété graphique exclusive. `MD56_RAPPORT_FR.md`, `research/md56_owner.c`. Les opérations critiques et la réentrée restaient problématiques. |
| **MD57** | Vraies images V30 dans la chaîne expérimentale et le worker Korg sous QEMU. `MD57_RAPPORT_FR.md`, `research/md57_publish.c`, `research/md57_publish.h`, `tests/arm/md57_probe.c`, `tests/run_md57.sh`, `reports/md57_v30_shadow.gif`, `reports/md57_v30_presets.png`. |
| **MD58** | Pont expérimental de notes vers Mercury. `MD58_RAPPORT_FR.md`, `research/md58_note_bridge.c`. Les événements observés ne constituaient pas encore une preuve complète de lecture native d’un pattern. |
| **MD59** | Sidechain visuel expérimental ; une correction ultérieure a établi une différence réelle entre images OFF et ON. Fichiers connus : `MD59_RAPPORT_FR.md`, `MD59_CORRECTION_FR.md`, `research/md59_sidechain.c`, `research/md59_renderer.c`, `tests/run_md59.sh`, `tests/arm/md59_probe.c`, GIF et traces dans `reports/`. |
| **MD60** | Recherche des producteurs d’événements, timing et pont non bloquant. `MD60_RAPPORT_FR.md`. |
| **MD61** | Recherche du moteur de lecture des patterns, notamment `C005F70C`. `MD61_RAPPORT_FR.md`. |
| **MD62** | Chemin candidat pattern → routeur → publication, enveloppes MANUAL/SYNC/AUTO à préciser. `MD62_RAPPORT_FR.md`. |
| **MD63** | Progression native candidate autour de `C005E914`, avec incréments synthétiques. `MD63_RAPPORT_FR.md`. |
| **MD64** | Démonstration visuelle V30 alimentée par des tentatives de messages issues du banc ARM ; événements et temps restaient synthétiques ou collectés dans un modèle. `MD64_RAPPORT_FR.md`, `reports/md64_v30_sequenceur.gif`, `reports/md64_moments.png`, `reports/md64_evenements.csv`. |
| **MD65** | Pipeline de compilation, placement et vérification `RESEARCH_ONLY`. Les noms exacts de tous les scripts ne sont pas visibles. |
| **MD66** | ELF ARM de recherche rassemblant les composants compatibles ; initialisation et chargement réels non établis. `MD66_RAPPORT_FR.md`, `reports/md66_validation.txt`. |
| **MD67** | Payload intégré avec routines LCD originales sous QEMU ; étude de pile et duplication. `MD67_RAPPORT_FR.md`, `reports/md67_memory.json`, `reports/md67_pipeline.json`, `reports/md67_validation.txt`. |
| **MD68** | Test d’une opération critique pendant un transfert : l’arbitrage pouvait refuser un worker nécessaire. `MD68_RAPPORT_FR.md`, `tests/arm/md68_critical.c`, `reports/md68_validation.txt`. |
| **MD69** | Contre-exemple : un comparateur adapté pouvait fournir l’image Mercury à un scan forcé imbriqué au lieu de la source native. `MD69_RAPPORT_FR.md`, `tests/arm/md69_compare.c`, `tests/run_md69.sh`, `reports/md69_validation.txt`. |
| **MD70** | Recherche sur chargeur, mémoire et récupération. Les preuves restaient insuffisantes pour autoriser une installation. `MD70_RAPPORT_FR.md`, `tools/md70_evidence.py`, `reports/md70_evidence.json`. Dernier commit MD70 cité : `f963ece`. |
| **MD71** | Preuve ciblée : remplacer la source graphique modifie l’entrée des dessins Korg suivants. `MD71_RAPPORT_FR.md`, `tests/arm/md71_upstream.c`, `tests/run_md71.sh`, `reports/md71_validation.txt`. Commit : `3f41c1d`. |
| **MD72** | Identification d’objets UI, d’une fabrique de 45 entrées et d’un redessin conditionnel. `MD72_RAPPORT_FR.md`, `tools/md72_ui_audit.py`, `reports/md72_ui_evidence.json`, `reports/md72_ui_disassembly.txt`. Commit : `3eef50b`. |
| **MD73** | Deux objets Korg transitoires identifiés, « Working… » et « Undo! » ; étude des listes et destructeurs. `MD73_RAPPORT_FR.md`, `tools/md73_pages_audit.py`, fichiers `reports/md73_pages_*`. Commit : `f74cb9d`. |
| **MD74** | Un composant de texte Korg authentique dessine sous QEMU ; le texte « PATTERN 01 » est synthétique. `MD74_RAPPORT_FR.md`, `tests/arm/md74_native_ui.c`, `tests/run_md74.sh`, `tools/md74_prepare.py`, `tools/md74_export.py`, `reports/md74_widget_qemu.png`. Commit : `8b7484c`. |
| **MD75** | Quatre services Korg précédemment simulés exécutés nativement ; constructeur UI bloqué sur la file non initialisée `C033E648`. `MD75_RAPPORT_FR.md`, `tests/arm/md75_native_ui.c`, `tests/run_md75.sh`, `tools/md75_export.py`, `reports/md75_native_message.png`. Commit : `2d91ff5`. |
| **MD76** | Initialisation native de `C033E648` par `C0025A84` ; blocage suivant sur `C033E634`. `MD76_RAPPORT_FR.md`, `tests/arm/md76_native_queue.c`, `tests/run_md76.sh`, `reports/md76_validation.txt`. Commit : `26d476c`. |
| **MD77** | Redessin de 32 images V30 par la primitive Korg originale, avec identité des 1 024 octets. `MD77_RAPPORT_FR.md`, `tests/arm/md77_korg_pixels.c`, `tools/md77_frames.py`, `tests/md77_export.py`, `tests/run_md77.sh`, images et GIF `reports/md77_*`. Commit : `10b19a0`. |
| **MD78** | Rendu différentiel Korg : 63 926 appels contre 262 144 sur 32 images, soit 75,61 % d’appels économisés dans le banc. `MD78_RAPPORT_FR.md`, `tests/arm/md78_diff.c`, `tests/md78_report.py`, `tests/run_md78.sh`, `reports/md78_transitions.csv`. Commit : `1c77719`. |
| **MD79** | Entrelacements framebuffer : image mélangée et état différentiel périmé dans des scénarios contrôlés. `MD79_RAPPORT_FR.md`, `tests/arm/md79_interleave.c`, `tests/run_md79.sh`, `reports/md79_validation.txt`. Commit : `e828e6f`. |
| **MD80** | Composant Mercury appelé par une table virtuelle **de fixture**, dessin V30 exact ; pas d’exécution du cycle complet `C006F178`. `MD80_RAPPORT_FR.md`, `tests/arm/md80_widget.c`, `tests/run_md80.sh`, `reports/md80_fixture_v30.png`. Commit : `0356735`. |
| **MD81** | Insertion Mercury par `C00614FC` dans une liste construite par Korg ; appel par les 96 octets originaux `C006F240..C006F29F`, déplacés dans une enveloppe. `MD81_RAPPORT_FR.md`, `tests/arm/md81_list.c`, `tools/md81_iter_asm.py`, `tests/run_md81.sh`, `reports/md81_v30.png`. Commit : `7a05ff3`. |
| **MD82** | Destruction native d’une page contenant seulement deux composants Korg ; aucun retrait individuel Mercury démontré. `MD82_RAPPORT_FR.md`, `tests/arm/md82_cleanup.c`, `tests/run_md82.sh`. Commit : `a75aa8a`. |
| **MD83** | Page de fixture contenant Mercury, dessin et destruction en bloc ; allocateur de laboratoire réutilisant ses blocs. `MD83_RAPPORT_FR.md`, `tests/arm/md83_owned.c`, `tests/run_md83.sh`. Commit : `f2987d4`. |
| **MD84** | Transition native `C006E8BC` page 25 → 29 sous QEMU. `MD84_RAPPORT_FR.md`, `tests/arm/md84_transition.c`, `tests/md84_frames.py`, `tests/run_md84.sh`, `reports/md84_framebuffers.json`, `reports/md84_undo.png`. Commit : `012aae0`. |
| **MD85** | Même transition avec Mercury ; comparaison de deux nettoyages. Sans effacement, 72 pixels supplémentaires subsistaient après le dessin partiel de la page suivante. `MD85_RAPPORT_FR.md`, `tests/arm/md85_transition.c`, `tests/md85_frames.py`, `tests/run_md85.sh`, `reports/md85_*`. Commit : `13911fe`. |
| **MD86** | Événement synthétique de format Korg traversant le publisher, la file et le dispatcher jusqu’à la transition, sans appel direct de `C006E8BC` par le banc. `MD86_RAPPORT_FR.md`, `tests/arm/md86_events.c`, `tests/md86_verify.py`, `tests/run_md86.sh`, `reports/md86_*`. Commit : `d4ebc05`. |
| **MD87** | Producteur Korg `C0083D28` et méthode native de la page 19 menant à une demande de page 21, avec et sans Mercury. `MD87_RAPPORT_FR.md`, `tests/arm/md87_producer.c`, `tests/run_md87.sh`, `reports/md87_validation.txt`. Commit : **`4c1ec01`**. |

Pour les étapes où seul le titre ou l’objectif est visible, il ne faut pas déduire que tous les objectifs de la mission ont été atteints.

## 2. Fonctions et adresses utiles identifiées

| Adresse | Rôle établi ou étudié dans les rapports précédents |
|---|---|
| `C031B310` | Source graphique LCD, 1 024 octets. |
| `C031B710` | Shadow LCD, 1 024 octets. |
| `C031BB2C` | Descripteur LCD étudié. |
| `C0015804` | Effacement de la source. |
| `C0015824` | Primitive pixel Korg, lecture/modification/écriture. |
| `C0015900` | Lecture d’un pixel source. |
| `C0015988` | Écriture d’une plage d’octets dans la source. |
| `C0015AB4` | Comparateur et copie source → shadow par page. |
| `C0015DD0` | Dispatcher LCD ; opcode 2 positionne un indicateur, opcode 3 appelle le worker. |
| `C0015FA0` | Worker LCD. |
| `C001613C` | Sender LCD. |
| `C0015CDC → C00117C8` | Attente liée notamment au bit `0x200` du registre `0x01C41010`. |
| `C003F104`, `C003F108` | Retours immédiats `BX LR` dans les VSB étudiés ; pas de verrou démontré. |
| `C006F178` | Cycle graphique principal étudié, **non exécuté intégralement** dans les expériences MD81–MD87. |
| `C006F240..C006F29F` | Portion de 96 octets d’itération graphique exécutée dans une enveloppe de laboratoire. |
| `C006EA10` | Appel de trois composants graphiques supplémentaires. |
| `C006E664` | Fabrique interne d’objets graphiques. |
| `C00F9CD8` | Table des 45 entrées de cette fabrique. |
| `C00614FC` | Ajout d’un pointeur dans le vecteur graphique étudié. |
| `C006144C` | Agrandissement du vecteur. |
| `C0060F10` | Nettoyage/destruction de la liste entière ; boucle si le parcours est marqué actif. |
| `C006E8BC` | Routine native de changement du premier emplacement graphique. |
| `C0083848` | Vidange de la file d’événements UI. |
| `C00834FC` | Dispatcher d’événements UI. |
| `C0083714` | Méthode qui transmet les arguments d’une demande de page à `C006E8BC`. |
| `C0083D28` | Producteur natif d’un événement de changement de page, après contrôles. |
| `C006BC88` | Méthode de la page 19 demandant la page 21 à `C0083D28`. |
| `C033E648` | File dont l’initialisation native a été étudiée en MD76. |
| `C0025A84` | Initialisation native identifiée pour cette file. |
| `C033E634` | Pointeur utilisé par le callback de notification suivant ; son initialisation complète restait ouverte. |
| `C005E914` | Moteur d’avancement du séquenceur étudié en MD63. |
| `C005F70C → C005BA78 → C005AF68 → C005AD44` | Chaîne native étudiée pour les notes, avec services et temps synthétiques dans les bancs. |

## 3. Architecture et composants Mercury connus

Les éléments suivants avaient été développés ou assemblés en laboratoire :

- **V30 Groove** : moteur graphique monochrome 128 × 64, avec huit presets et douze paramètres à préserver.
- **Sidechain visuel MD59** : enveloppe déclenchée par des notes synthétiques dans le banc, sans modification du traitement audio.
- **Triple buffering MD53** : buffers privé d’écriture, publié et en lecture ; tests hôte/QEMU, sans garantie automatique de compatibilité avec le noyau Korg.
- **Contrôleur et adaptateurs LCD expérimentaux MD54–MD56** : utiles à la recherche, mais des contre-exemples sur les opérations critiques et la réentrée subsistaient.
- **Pont musical expérimental MD58–MD64** : récupération et transfert de champs de notes dans des scénarios ARM contrôlés. Ne pas présenter ces scénarios comme une lecture musicale physique validée.
- **Payload ARM intégré MD66/MD67** : ELF de recherche regroupant des composants compatibles, marqué `RESEARCH_ONLY`.
- **Quatre mini-LFO expérimentaux** : présents dans le payload de recherche selon le rapport MD66, sans preuve d’écriture sûre sur des paramètres Korg.
- **Fracture réactive** et **KNOB REACT** : spécifications futures ; à ne pas confondre avec des fonctionnalités intégrées. Fichiers documentaires vus : `FRACTURE_REACTIVE_SPEC_FR.md` et `KNOB_REACT_SPEC_FR.md`.
- **PSYCH EYE** : en pause dans les dernières instructions visibles.
- **IFX personnalisés** : à préserver ; aucun résultat ne démontre que leur coexistence matérielle avec Mercury est sûre.

## 4. Fichiers et outils nécessaires à rechercher dans une sauvegarde

Le dépôt à récupérer devait notamment contenir :

```text
MD46_RAPPORT_FR.md … MD87_RAPPORT_FR.md
COMMENCER_ICI.md
FRACTURE_REACTIVE_SPEC_FR.md
KNOB_REACT_SPEC_FR.md

src/
research/
tests/
  arm/
tools/
reports/
```

Fichiers particulièrement importants connus :

```text
research/md53_frames.c
research/md54_scan.c
research/md56_owner.c
research/md57_publish.c
research/md57_publish.h
research/md58_note_bridge.c
research/md59_sidechain.c
research/md59_renderer.c

tests/arm/md47_start.S
tests/arm/md47_load_probe.ld
tests/arm/md54_abi.S
tests/arm/md71_upstream.c
tests/arm/md74_native_ui.c
tests/arm/md75_native_ui.c
tests/arm/md76_native_queue.c
tests/arm/md77_korg_pixels.c
tests/arm/md78_diff.c
tests/arm/md79_interleave.c
tests/arm/md80_widget.c
tests/arm/md81_list.c
tests/arm/md82_cleanup.c
tests/arm/md83_owned.c
tests/arm/md84_transition.c
tests/arm/md85_transition.c
tests/arm/md86_events.c
tests/arm/md87_producer.c

tools/cloud_env.sh
tools/md47_korg_memory_readonly.py
tools/md47_prepare_qemu.py
tools/md51_prepare_native_probe.py
tools/md51_audit_readonly.py
tools/md70_evidence.py
tools/md72_ui_audit.py
tools/md73_pages_audit.py
tools/md74_prepare.py
tools/md74_export.py
tools/md75_export.py
tools/md77_frames.py
tools/md81_iter_asm.py

tests/run_md53.sh
tests/run_md57.sh
tests/run_md59.sh
tests/run_md69.sh
tests/run_md71.sh
tests/run_md74.sh
tests/run_md75.sh
tests/run_md76.sh
tests/run_md77.sh
tests/run_md78.sh
tests/run_md79.sh
tests/run_md80.sh
tests/run_md81.sh
tests/run_md82.sh
tests/run_md83.sh
tests/run_md84.sh
tests/run_md85.sh
tests/run_md86.sh
tests/run_md87.sh
```

Cette liste est **partielle**. Il faut récupérer l’arborescence entière, les fichiers non suivis éventuels et `.git`, plutôt que se limiter à ces noms.

Les bancs vus dans la conversation utilisaient notamment :

- Clang ciblant `arm-none-eabi`, `-mcpu=arm926ej-s -marm`.
- `ld.lld`.
- `qemu-arm -cpu arm926`.
- Python 3 et Pillow pour les captures.
- Deux VSB fournis par vous, lus uniquement.
- Des exécutables Linux/QEMU et fichiers intermédiaires dans `build/`, non destinés au flash.

### Empreintes des VSB utilisées dans les tests

```text
user_custom (2).VSB
81b62467490fd25fd154ffe02298886bfdd6e9cf9bda897cde41ee65201ffd03

user_backup.VSB
06becf76750f0dce7d3e40d476e4a78524a53730ba61b9b9752dfb170745b052
```

Ces fichiers sont vos références de recherche. Leur disponibilité actuelle ne peut pas être vérifiée depuis cette session.

## 5. Problèmes qui n’étaient pas résolus

Les derniers résultats ne permettaient pas de déclarer l’intégration matérielle sûre :

- Chargement réel du payload et occupation de `C01D0000`/`C01E0000`.
- Conflits possibles avec heap, piles, audio, DMA et IFX.
- MMU, cache, IRQ/FIQ et ordre mémoire sur ARM926.
- Propriété du framebuffer entre producteurs Korg, Mercury et LCD2.
- Opérations LCD critiques, réentrance et attente périphérique sans borne.
- Restitution complète de l’interface Korg après Mercury.
- Navigation et correspondance avec les boutons physiques.
- Origine réelle de l’appel à la méthode de la page 19 utilisée en MD87.
- Méthode de récupération indépendante après un démarrage ou un LCD bloqué.
- Comportement réel du heap Korg et des références externes.
- Budget de pile et temps CPU sur l’instrument.

Un succès QEMU ne constitue pas une validation physique.

---

## 6. Code source encore visible dans la conversation

Le contenu ci-dessous est **transcrit depuis les commandes visibles dans cette conversation**, pas extrait à nouveau du dépôt. Il doit être conservé comme copie de secours textuelle et comparé aux originaux si le volume est retrouvé.

### `tools/md81_iter_asm.py`

```python
#!/usr/bin/env python3
"""Embed unchanged bounded Korg iteration instructions in a test wrapper."""
from pathlib import Path
import argparse,hashlib
from md51_prepare_native_probe import read_original
p=argparse.ArgumentParser();p.add_argument('vsb',type=Path);a=p.parse_args()
b,sha=read_original(a.vsb);code=b[0x6f240:0x6f2a0]
if len(code)!=96:raise ValueError('bad excerpt')
path=str(a.vsb.resolve())
if any(c in path for c in ('\n','\r','\0')):raise ValueError('unsupported path')
path=path.replace('\\','\\\\').replace('"','\\"')
s=''' .syntax unified
 .cpu arm926ej-s
 .arm
 .text
 .global md81_original_iteration
 .type md81_original_iteration,%function
md81_original_iteration:
 push {r4-r8,lr}
 sub sp,sp,#8
 mov r5,r0
 mov r3,#1
 strb r3,[r5,#28]
'''
s+=f' .incbin "{path}",0x6f340,96\n'
s+=''' add sp,sp,#8
 pop {r4-r8,pc}
 .section .note.GNU-stack,"",%progbits
'''
out=Path('build/md81/iteration.S')
if out.is_symlink():raise ValueError('output symlink')
out.write_text(s)
print(f'MD81 iteration original SHA256={hashlib.sha256(code).hexdigest()}; VSB {sha}')
```

Cette copie dépend de `md51_prepare_native_probe.py` et des VSB d’origine. Elle ne contient pas les 96 octets Korg : elle les lit dans un VSB vérifié.

### `tests/md78_report.py`

```python
#!/usr/bin/env python3
import csv,struct
from pathlib import Path
raw=Path('build/md78/records.bin').read_bytes()
if len(raw)!=36*28:raise ValueError('wrong record length')
rows=list(struct.iter_unpack('<7I',raw))
if rows[0][1]!=8192 or rows[32][1]!=0 or rows[33][1]!=8192 or rows[35][1]!=8192:raise ValueError('incorrect special transition')
if not all(c==on+off for _,c,on,off,_,_,_ in rows):raise ValueError('count mismatch')
if not any(off for _,_,_,off,_,_,_ in rows[1:32]):raise ValueError('no extinguished pixels tested')
with open('reports/md78_transitions.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['transition','appels_korg','pixels_allumes','pixels_eteints','octets_compares','bits_examines','rendu_integral','appels_economises_sur_8192'])
 for i,c,on,off,cmp,bits,full in rows:w.writerow([i,c,on,off,cmp,bits,full,8192-c])
n=sum(r[1] for r in rows[:32]);print(f'32 frames: {n} Korg calls vs {32*8192} full, saved {32*8192-n} ({100*(1-n/(32*8192)):.2f}%)')
print('Special cases: repeated=0, inverted=8192, OFF=fixture target, invalidation=8192; detailed counters in reports/md78_transitions.csv')
```

### `tests/run_md78.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ "$#" -ne 2 ]; then echo 'usage: bash tests/run_md78.sh custom.VSB backup.VSB' >&2; exit 2; fi
mkdir -p build/md78 build/md74
echo 'MD77 reference, both originals:'
bash tests/run_md77.sh "$@"
clang --target=arm-none-eabi -mcpu=arm926ej-s -marm -c tests/arm/md47_start.S -o build/md78/start.o
clang --target=arm-none-eabi -mcpu=arm926ej-s -marm -c build/md77/frames.S -o build/md78/frames.o
clang --target=arm-none-eabi -mcpu=arm926ej-s -marm -O2 -fno-builtin -ffreestanding -Wall -Wextra -Werror -fno-stack-protector -c tests/arm/md78_diff.c -o build/md78/probe.o
index=0
for original in "$@"; do
 python3 tools/md74_prepare.py "$original" build/md74/original.S
 clang --target=arm-none-eabi -mcpu=arm926ej-s -marm -c build/md74/original.S -o build/md78/original.o
 ld.lld -T tests/arm/md47_load_probe.ld build/md78/start.o build/md78/probe.o build/md78/frames.o build/md78/original.o -o build/md78/probe_LINUX_TEST_ONLY.elf
 timeout 60 qemu-arm -cpu arm926 build/md78/probe_LINUX_TEST_ONLY.elf
 if [ "$index" -eq 0 ]; then cp build/md78/records.bin build/md78/records_first.bin; else cmp build/md78/records.bin build/md78/records_first.bin; fi
 python3 tools/md74_prepare.py "$original" build/md74/original.S
 index=$((index+1))
done
python3 tests/md78_report.py
```

### `tests/arm/md78_diff.c`

```c
/* Research-only: private single-producer model, actual Korg pixel routine.
 * No scheduler, LCD worker, ownership or physical framebuffer guarantee. */
#include <stdint.h>
extern unsigned char original[],v30_frames[];
#define FN(t,a) ((t)(uintptr_t)(a))
static uint32_t sys(uint32_t n,uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f){register uint32_t r0 __asm__("r0")=a,r1 __asm__("r1")=b,r2 __asm__("r2")=c,r3 __asm__("r3")=d,r4 __asm__("r4")=e,r5 __asm__("r5")=f,r7 __asm__("r7")=n;__asm__ volatile("svc #0":"+r"(r0):"r"(r1),"r"(r2),"r"(r3),"r"(r4),"r"(r5),"r"(r7):"memory","cc");return r0;}
static void say(const char*s){unsigned n=0;while(s[n])n++;sys(4,1,(uintptr_t)s,n,0,0,0);}
static uint8_t prev[1024],alternate[1024],native_fixture[1024];
static uint8_t *fb=(uint8_t*)0xc031b310;
static void (*pixel)(int*,int*,int*)=FN(void(*)(int*,int*,int*),0xc0015824);
struct record {uint32_t id,calls,on,off,compared_bytes,tested_bits,full;};
static int fd;
static void copy(uint8_t *a,const uint8_t *b){for(unsigned i=0;i<1024;i++)a[i]=b[i];}
static int render(unsigned id,const uint8_t *next,int valid){
 struct record r={id,0,0,0,0,0,(unsigned)!valid};
 for(unsigned i=0;i<1024;i++){
  unsigned mask=valid?(prev[i]^next[i]):255u;
  if(valid)r.compared_bytes++;
  if(!mask)continue;
  for(unsigned bit=0;bit<8;bit++){
   r.tested_bits++;
   if(!(mask&(1u<<bit)))continue;
   int x=(int)(i&127),y=(int)((i>>7)*8+bit),v=(next[i]>>bit)&1;
   pixel(&x,&y,&v);r.calls++;if(v)r.on++;else r.off++;
  }
 }
 for(unsigned i=0;i<1024;i++)if(fb[i]!=next[i])return 0;
 if(fb[-1]!=0x39||fb[1024]!=0xc5)return 0;
 copy(prev,next);
 return sys(4,fd,(uintptr_t)&r,sizeof(r),0,0,0)==sizeof(r);
}
int main(void){
 if(sys(192,0xc0000000,0x200000,7,0x32,-1,0)!=0xc0000000)return 2;
 if(sys(192,0xc031b000,4096,7,0x32,-1,0)!=0xc031b000)return 3;
 for(unsigned i=0;i<0x200000;i++)((uint8_t*)0xc0000000)[i]=original[i];
 sys(0xf0002,0xc0000000,0xc0200000,0,0,0,0);
 fd=sys(5,(uintptr_t)"build/md78/records.bin",577,0644,0,0,0);if(fd<0)return 4;
 fb[-1]=0x39;fb[1024]=0xc5;
 /* Deliberately start from a non-empty checkerboard through native pixels. */
 for(int y=0;y<64;y++)for(int x=0;x<128;x++){int v=(x+y)&1;pixel(&x,&y,&v);}
 for(unsigned i=0;i<32;i++)if(!render(i,v30_frames+1024*i,i!=0))return 5;
 if(!render(32,v30_frames+31*1024,1))return 6; /* unchanged */
 for(unsigned i=0;i<1024;i++)alternate[i]=(uint8_t)~prev[i];
 if(!render(33,alternate,1))return 7; /* all 8192 bits differ */
 for(unsigned i=0;i<1024;i++)native_fixture[i]=(uint8_t)(i*37u+13u);
 if(!render(34,native_fixture,1))return 8; /* OFF: synthetic native target */
 /* Independent native write invalidates the cached source. No fake ownership. */
 {int x=3,y=7,v=((fb[(7>>3)*128+3]>>(7&7))&1)^1;pixel(&x,&y,&v);}
 if(!render(35,v30_frames,0))return 9; /* re-arm with full refresh */
 sys(6,fd,0,0,0,0,0);
 say("PASS: 32 V30 images, repeated frame, inversion, simulated OFF and invalidation; original pixel primitive; every framebuffer byte checked\n");
 return 0;
}
```

Ce fichier est un **banc de recherche**, pas un module à installer sur l’instrument. Il dépend notamment des images MD77, de l’enveloppe de démarrage et des VSB.

## 7. Ce qui manque encore

Je ne peux pas fournir honnêtement une archive contenant :

- Les sources complètes du moteur V30 et des payloads MD46–MD87.
- L’ensemble des scripts et bancs mentionnés plus haut.
- Les images, GIF, traces complètes et fichiers de build originaux.
- Les objets Git, l’historique complet et les éventuels fichiers non commités.
- Les contenus complets de toutes les pièces jointes de ce chat.

Certains extraits ont été visibles dans les messages techniques précédents, mais je ne peux pas garantir qu’ils constituent l’intégralité des fichiers ni les extraire automatiquement dans un dossier depuis cet environnement hors ligne. **Le volume n’est pas déclaré définitivement perdu** : une restauration de l’environnement ou une sauvegarde côté fournisseur reste le moyen prioritaire de récupérer les véritables fichiers et commits.