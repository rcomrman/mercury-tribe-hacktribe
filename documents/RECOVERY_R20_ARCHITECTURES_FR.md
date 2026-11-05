# R20 — coordination complète et conservation en quarantaine

## Domaine expérimental A

Le prototype `tests/recovery_r20/domain.h` réserve quatre propriétaires et trois
cadres de parcours, sans réemploi d'adresse ni de ticket. Toutes les opérations
supposent une sérialisation extérieure. Il n'implémente aucune primitive ARM926
atomique et n'installe aucun wrapper dans Korg.

Une construction est réservée avant `C0070778`. La fermeture n'efface pas cette
obligation ; seul le vrai retour permet de terminer la réservation. L'admission
des parcours précède les chargements natifs et leur cadre est retenu jusqu'au
retour complet. Le compteur callbacks concerne le thunk expérimental ; un
callback natif direct est retenu par son parcours, pas instrumenté intérieurement.
Un ticket exact et vivant est nécessaire pour terminer un cadre. Saturation et
épuisement des tickets refusent l'admission sans reboucler.

La demande de fermeture est immédiate. L'admission du destructeur exige retour
constructeur, fermeture, absence de constructeur/parcours/callback/destructeur
participant et inventaire local concordant. Le préflight vérifie les tuples
actifs des deux sujets de fixture, leur méthode et les sujets des inverses. Il
refuse le troisième sujet découvert dans le constructeur complet. Cela ne
constitue pas un inventaire des registres CPU, copies externes ou alias indirects.

Après admission, la fixture retire les deux relations avec `C00705DC`, détache
explicitement les champs inverse de leur tableau permanent, puis appelle le
destructeur natif non supprimant avec inverse nul. Le corps revient sans free.
Le tableau inverse n'est pas recyclé. L'état BODY_RETURNED décrit uniquement ce
retour local ; `destroy_allocation` refuse toujours. Ce détachement est une
opération de fixture, pas une autorisation de modifier un inverse Korg réel.

Un gate réel devrait être court, relâché avant constructeur, callback, LCD et
attente. La fermeture intérieure ne doit pas attendre son propre cadre. Un
callback sans retour garde ses obligations : la disponibilité peut être perdue,
sans conversion de timeout en autorisation de destruction.

## Domaine expérimental B

Avec `keep=1`, le protocole refuse les destructeurs, conserve les slots, clés,
inverses et objets. Un ancien appel atteint le thunk permanent ; celui-ci refuse
le travail si son propriétaire est fermé. Ce contrôle est **nouveau code de
fixture** : `C0085078` et `C0085278` ne possèdent pas ce contrôle. Conserver un
abonné Korg brut évite la disparition du stockage, mais n'arrête pas ses effets.

Les inscriptions et modifications de tuples exigent encore une coordination.
Une quarantaine ne protège pas une méthode effacée entre deux chargements ni une
vtable mutable. Les quatre propriétaires peuvent être épuisés ; le cinquième est
refusé, sans réutilisation. Aucun progrès indéfini à mémoire fixe n'est prouvé.

| Critère | A : coordination complète | B : quarantaine |
|---|---|---|
| Fenêtre sélection–entrée | Cadre acquis avant chargements, mutations différées | Adresses conservées ; thunk stable pour refuser le travail |
| Destruction du corps natif | Après drainage et inventaire local, inverse détaché sans free | Refusée |
| Libération réelle | Toujours refusée par le banc | Toujours refusée |
| Réentrée | Cadres distincts, capacité3 ; close sans attente | Même maintien des cadres et refus du travail fermé |
| Constructeur suspendu | Obligation gardée, aucune destruction | Même obligation ; stockage conservé |
| Acteur non participant | Preuve rompue ; alias invisible possible | Ancien thunk peut refuser, callback Korg brut reste actif |
| Coût de durée de vie | Drainage possible sous couverture complète | Stockage monotone, saturation explicite |
| Prérequis natif manquant | Couverture et synchronisation communes | Stabilité, absence de réemploi/mutation, admission des constructions |

## Mémoire mesurée et mémoire non connue

Les tailles proviennent de records ARM, pas d'une estimation hôte :

| Stockage R20 | Octets |
|---|---:|
| Métadonnées domaine, quatre propriétaires, trois cadres |136|
| Quatre abonnés76 avec deux gardes chacun |336|
| Quatre vecteurs préalloués4×4 |64|
| Deux sujets périodiques de fixture904 |1808|
| Modèle natif de fixture788 |788|
| Sous-total de ces tableaux distincts |3132|

Le second sujet904 de fixture n'est **pas** l'objet associé UI1064. Ce dernier
reste étudié statiquement par R19 et l'audit phase1 ; son constructeur n'est pas
rejoué par R20. Le vrai constructeur abonné utilise le modèle788 et son sujet+4.

Les copies de slot, métadonnées de méthodes, états UI de contrôle, clé inconnue,
source/shadow du chargeur, piles et journaux s'ajoutent à3132. La pile GDB8192 est
exclusivement instrumentation. Aucun chiffre n'établit une RAM libre, une marge
de pile ou une durée audio acceptable sur l'instrument. Le coût marginal du
registre est136 ; ce banc spécialisé remplace fonctionnellement certains contrats
R16–R19, sans modifier ni inclure leurs registres et sans revendiquer un adaptateur
général pour toutes les pages et tous les payloads Korg.

## Modèle et portée

Deux propriétaires, deux parcours à usage unique, cinq étapes de construction,
fermeture, sélection, résolution, entrée/retour callback, fin de cadre, admission,
retrait et retour destructeur séparés. Le modèle marque une éventuelle permission
FREE uniquement symboliquement dans une politique négative. Aucun free n'existe
dans les expériences ARM.

| Politique | États | Transitions | Violations |
|---|---:|---:|---|
| Coordination complète |1361|3064|Aucune sous contrat|
| Quarantaine et thunk |1082|2668|Aucune sous contrat|
| Compter seulement les callbacks entrés |4175|10630|Tuple effacé ; accès après retour destructeur|
| Domaine ne recensant qu'un des deux parcours |2569|6410|Même contre-exemple malgré calme local|
| Retour destructeur pris comme certificat |6224|16758|Même accès ; permission de free avec référence vivante|

Total15411 états,39530 transitions. `check_model.py` réexplore chaque politique
avec un interpréteur distinct, sans importer le générateur, et rejoue chaque
témoin négatif. Cela vérifie le modèle borné, pas ses hypothèses sur Korg. Les
transitions sont atomiques par hypothèse ; ni IRQ/FIQ/DMA, ni cache/ordre ARM926,
ni ordonnanceur natif, ni transport LCD ne sont validés. Le modèle n'explore pas
la saturation quatre objets ; celle-ci est testée séparément sur ARM. Le cas de
callback non retournant conserve un état sans transition de retour : absence de
destruction, aucune garantie de vivacité.
