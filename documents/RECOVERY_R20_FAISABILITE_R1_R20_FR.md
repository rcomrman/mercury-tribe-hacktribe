# R20 — bilan de faisabilité R1–R20 et recommandation R21

## 1. Composants fonctionnels en laboratoire

Le moteur artistique V30, ses huit presets, douze paramètres et quatre mini-LFO
au total existent et sont préservés. Les images sont produites avec notes et
horloges synthétiques ; aucune lecture musicale réelle de l'Electribe n'est
validée par ces fixtures. R1 vérifie32 images128×64 par rendu natif intégral et
différentiel. Le gain77,19% concerne un nombre d'appels sur cette fixture, pas du
temps CPU mesuré. R2–R7 établissent insertion, dessin, certaines transitions et
restauration graphique par le cycle natif complet.

R4–R6 prouvent des chaînes publication/file/dispatcher/navigation sur des entrées
préparées. Elles n'attribuent pas avec certitude les codes à des touches physiques.
R8 conserve les contre-exemples de réentrée et mutation des listes. R9–R11
identifient le transport, les comptes à rebours et les tâches, sans réception LCD
physique ni récupération indépendante. R12–R15 qualifient des pools privés,
publication/admission coopératives et commandes retenues jusqu'à résultat/ACK.
R16–R19 distinguent clé/contexte, emprunts, résolution, ancres et vrai retour du
constructeur. R20 relie ces obligations à un abonné concret et à ses destructeurs.

Ce sont des composants et chaînes de laboratoire validés dans leurs périmètres,
pas un visualiseur intégré de bout en bout. R20 ne rejoue pas les rendus ni les
anciennes missions ; leurs preuves et leurs sources restent identiques.

## 2. Mécanismes natifs suffisamment compris dans un périmètre local

Les primitives pixels, structures de page et certains parcours graphiques,
messages, files et routes UI disposent de contrats et de tests. L'observateur
dispose d'un codec concret : clé distincte de this, méthode directe/virtuelle,
ajustement, publication avant inverse, retour void sans garantie de succès.
Retrait du slot, nettoyage inverse et deux niveaux de free sont distingués.
L'abonné76 s'inscrit sur le périodique et sur le modèle+4 ; ses deux callbacks
accèdent à l'allocation entière, l'un relisant aussi le modèle global.

Cela suffit pour construire et réfuter des contrats locaux. Cela ne suffit pas
pour attribuer tous les appelants, instances, alias, contextes et droits de free.
Une absence de référence dans un scan ARM aligné ne prouve pas l'absence de
référence calculée ou Thumb. Les racines UI et modèle restent partagées.

## 3. Obstacles à l'intégration matérielle

- Aucun domaine commun de synchronisation n'est prouvé couvrir tâches, callbacks,
  destructeurs, initialisations paresseuses et mutations graphiques.
- Des pointeurs déjà sélectionnés ou copiés survivent au retrait. La destruction
  d'une page ne constitue ni join, ni preuve du dernier propriétaire global.
- Mémoire profonde, budget de pile, charge CPU, latence et impact audio/IFX réels
  ne sont pas bornés. Préserver les IFX par absence d'écriture ne valide pas leur
  coexistence temporelle sur instrument.
- Le triple buffer privé ne rend pas atomique la copie vers la source fixe
  partagée `C031B310`, lue aussi par le chemin LCD.
- La shadow est copiée avant transmission ; son égalité ne confirme pas l'écran.
  Détection, confinement, annulation et restauration LCD restent quatre preuves
  séparées, toutes insuffisantes pour une récupération indépendante.
- Les frontières de heap et de périphérique sous QEMU sont des limites du banc,
  sans conclusion sur un échec équivalent de la véritable Electribe.

## 4. Réalisme de la coordination complète

Elle est cohérente et testable pour un graphe fermé, borné, intégralement
participant. Sa généralisation à tous les objets Korg n'est pas démontrée et
demanderait de dominer de nombreux accès indirects, trois racines partagées au
minimum pour ce cas et les durées de vie de commandes/périphériques. Aucun point
d'interception unique déjà qualifié ne remplit ce contrat. R20 ne la déclare ni
impossible ni prête : elle reste une architecture conditionnelle, avec un coût
de preuve élevé et un risque de blocage si un seul participant ne revient pas.

## 5. Architecture moins intrusive à privilégier

Une voie Mercury persistante, à mémoire fixe, sans nouvelles inscriptions
périodiques et sans destruction de sujets Korg paraît une meilleure hypothèse de
travail. Elle réduirait les obligations de construction et destruction que R20
vient de rendre concrètes. La quarantaine seule des objets natifs n'est pas
suffisante : leurs callbacks ignorent close et peuvent continuer à écrire.

Cette préférence est une orientation de recherche, pas une validation. Il faut
encore qualifier la durée de vie du composant de rendu, les changements de page,
les accès à la source fixe et le transfert LCD ; renoncer aux abonnements ne
résout pas automatiquement ces problèmes.

## 6. Preuves minimales avant d'envisager le matériel

1. Définir une voie exacte de rendu/publication et démontrer tous ses acteurs,
   contextes et propriétés, sans supposer une fermeture générale du système.
2. Qualifier admission, visibilité mémoire ARM926 et réentrée pour cette voie,
   y compris sa coexistence avec les lecteurs/écrivains Korg existants.
3. Prouver la conservation ou la cessation de toutes les références nécessaires,
   avant tout changement de cible, destruction ou réemploi.
4. Établir budgets RAM/pile/CPU et latences, avec conservation des IFX et de
   l'audio ; les tailles de fixtures ne suffisent pas.
5. Établir séparément la réception/transmission LCD et une conduite sûre en cas
   de blocage, sans assimiler timeout hôte, shadow ou sortie de tâche à une reprise.
6. Disposer d'une revue explicite de ces preuves et d'une autorisation matérielle
   distincte. Aucune n'est accordée par R20.

Cette liste énonce des prérequis de preuve, pas une procédure d'essai matériel.

## 7. R21 recommandée

**« Voie Mercury persistante à empreinte fixe, sans nouvel abonnement natif ».**

Construire uniquement en laboratoire un composant Mercury conservé, alimenté par
le chemin de dessin déjà étudié, avec données privées de taille fixe et sans
nouveau timer/observateur Korg. Réutiliser V30 et le triple buffer existants.

Livrables attendus : contrat d'entrée/sortie et de durée de vie ; inventaire des
accès graphiques réellement nécessaires ; comparaison avec le candidat à
abonnements ; tests de changement de page, anciennes références, réentrée,
saturation et callback bloqué ; budget mémoire complet et chemin critique CPU.
Établir quels points existants devraient être médiatisés, sans les patcher ni
présumer leur autorisation d'intégration. Refuser toute copie dans une source
partagée dont la fenêtre de lecture n'est pas qualifiée.

Le critère concret est de montrer une réduction vérifiée du graphe et des coûts
sans déplacer les risques vers le LCD. Une nouvelle architecture conditionnelle
sans progrès mesurable de couverture doit être rejetée ou resserrée. R21 ne doit
pas devenir une nouvelle étude de destruction générale du firmware.

**Décision : GO pour cette recherche logicielle ; NO GO intégration matérielle,
flash, destruction globale ou récupération LCD annoncée comme sûre.**
