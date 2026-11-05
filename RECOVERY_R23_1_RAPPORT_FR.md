# R23.1 — audit critique, résultats partiels

**STATUT : étude ciblée du worker exécutée ; audit général R23.1 encore partiel.**
Les observations ci-dessous corrigent R23 ; aucun verdict matériel positif.

L'étude demandée en priorité est détaillée dans
[`RECOVERY_R23_1_WORKER_FR.md`](documents/RECOVERY_R23_1_WORKER_FR.md).
Elle exécute le code ARM original sur les deux VSB : 12 cas, dont quatre fautes
GPIO attendues, et vérifie indépendamment les records. Suspendre le worker dans
la fixture préserve le shadow sous hypothèse d'absence d'autres auteurs ; le
droit de le suspendre et la restitution physique restent NON DÉMONTRÉS.

Mise à jour : six mutations réelles du code sont désormais détectées par des
oracles, et neuf traces adversariales ciblées ont été exécutées. Le statut
reste inachevé, notamment faute d'une analyse ARM complète et d'une évaluation
indépendante de l'audio et de la fin physique du transfert.

## Corrections établies

Le modèle R23 accepte `to_mercury, korg_begin, korg_end, exit` comme sûr : il
ne conserve pas la violation intermédiaire. Son compteur de 2 983 séquences
rejetées ne prouve donc aucune exclusivité. Il ne modélise pas non plus les
cinq états de transition revendiqués dans le rapport. Les 21 états R22 étaient
comptés, non rejoués. Ces affirmations de R23 sont retirées.

Le scanner R23 ne détecte que `BL` inconditionnel. Le scan R23.1 reconnaît
aussi `B` et les conditions ARM : 12 candidats vers `C0015DD0`, dont quatre
branchements `B` supplémentaires. Celui à `C008370C` est confirmé dans le
désassemblage : après l'appel du cycle, opcode 2 est placé dans r1, puis un
branchement terminal appelle le dispatcher. Les candidats restent à distinguer
du flot réellement atteignable ; données, Thumb et appels indirects demeurent.

Une autre erreur de R23 concerne l'ordre : `C0016084` appelle le comparateur
**depuis** le worker `C0015FA0` ; `C00160A0` appelle ensuite `C001613C` lorsque
la comparaison indique un changement. `C0015B38` appelle la copie de 128 octets
avant le retour du comparateur. Les entrées du dispatcher et du worker ne sont
donc pas systématiquement « trop tard » pour précéder le shadow, contrairement
au tableau R23. Que ces entrées dominent tous les chemins est NON DÉMONTRÉ.
Le désassemblage est conservé dans `reports/recovery_r23_1/lcd-disassembly.txt`.

## Modèle et essais

Le modèle local enregistre les violations au moment des événements, même si
l'état final redevient normal. Les 64 combinaisons R22 sont rejouées selon les
opérations abstraites R22 ; 21 donnent la relation shadow courant/LCD différent.
Il s'agit d'hypothèses abstraites, pas de 21 expériences matérielles.
Soixante-douze ordonnancements synthétiques combinent deux politiques, trois
cadences Korg, deux durées, deux ordres de fin et trois délais de transfert.
Sous ces hypothèses, les collisions vont de 1 à 299 en mode prioritaire ; le retour brutal laisse un
shadow à jour mais un LCD différent dans 20 de 36 cas prioritaires et dans
les 36 cas où les demandes Korg sont ignorées. Ces chiffres dépendent du
modèle et ne prédisent ni plantage ni comportement réel.

Le retour forcé et la fin des transferts restent des hypothèses. Le modèle ne
prouve ni attente infinie native, ni absence d'effet sur le pilote ou l'audio.
Les tests incluent deux mutations ciblées ; ce n'est pas une campagne complète
de mutation ni une vérification indépendante exhaustive.

Six mutants supplémentaires modifient effectivement le source en mémoire :
suppression de violation, transfert Korg sous Mercury, retour avec transfert
actif, assimilation de fin logique à ACK, auteur inconnu et effacement de faute.
Les six sont détectés ; cela ne prouve pas la complétude des oracles. Neuf
traces ciblées illustrent collision, inversion des fins, suppression, EXIT avec
transfert, faute et retour tardif, réentrée, auteur externe, faux ACK et
rétablissement simulé. Un transfert commencé sans ACK peut rester en attente
dans le modèle ; une attente infinie du vrai pilote est NON DÉMONTRÉE.

Le rejeu R22 reconstruit ses six opérations abstraites ; les historiques réels,
identités de transferts et ordres d'interruption n'ont pas été enregistrés par
R22 et ne peuvent pas être reconstitués. Les expériences ne prouvent aucune
conséquence sur l'audio. Un ordre « late » dans les essais périodiques change
uniquement l'ordre des fins simultanées ; les durées testées sont 1, 2 et 11 ticks.
Les traces ciblées complètent cette variation sans constituer un modèle matériel.

## Comparaison provisoire

| Voie | Atout | Condition non démontrée |
|---|---|---|
| Avant shadow | évite l'avance prématurée | domination de tous les auteurs |
| Après shadow | préserve le chemin Korg | invalidation et restauration acquittées |
| Pilote natif Mercury | réutilise une voie existante | propriété, ordre et ACK physique |
| Pilote indépendant simulé | permet d'explorer des politiques | accès matériel et coexistence inconnus |
| Image privée | faible couplage | aucun affichage physique |

Seule l'image privée est démontrée en laboratoire R21. Les autres options sont
NON DÉMONTRÉES sur instrument ; cette absence de preuve ne démontre pas leur
impossibilité technique.

## Travaux non exécutés

Cartographie ARM exhaustive et analyse complète du flot de contrôle ; résolution
des IRQ/FIQ, DMA, tables et alias calculés ; confrontation systématique aux
traces ARM ; scénario C autonome avec récupération et faute ; mesures ARM ;
comparaison complète des cinq architectures ; vérificateur indépendant et
audit complet R20–R23 : **NON EXÉCUTÉS**. La mission n'est pas close et aucun
rapport de réussite ou publication finale ne doit être déduit de ces essais.
