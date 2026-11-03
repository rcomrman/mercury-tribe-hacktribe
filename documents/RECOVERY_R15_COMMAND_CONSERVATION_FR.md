# R15 — conservation de commandes, sans substitution d'ABI native

RESEARCH_ONLY. Modèle scalaire borné utilisant **sans modification** pool R12, gate R13 et admission R14. Aucun raccordement installé. Les trois frontières natives ne deviennent pas participantes par simple inclusion de leurs adresses.

## États et résultats

La file de fixture contient trois entrées32 octets et32 octets de métadonnées, soit **128 octets ARM**. Une entrée porte ID, génération de cible, quatre mots copiés, état et résultat. Le codec du banc n'admet que des valeurs scalaires déclarées telles : un cast de pointeur en u32 ne prouve pas sa propriété. Les payloads déclarés pointeurs sont refusés ; aucun pointeur natif générique n'est recopié profondément.

| État / opération | Sens exact | Ce qu'il ne signifie pas |
|---|---|---|
| ACCEPTED1 | Copie dans la file, admissibilité initiale annoncée | Pas d'entrée ni de résultat Korg |
| WAITING2 | Acceptée et conservée, domaine/ordre empêchant l'entrée | Pas de succès natif et pas de commande exécutée |
| REFUSED5 à submit | Saturation, fermeture, ID invalide/ancien, génération nulle ou codec non supporté | Pas d'effet natif ; l'appelant doit traiter un vrai refus du modèle |
| RUNNING3 | Domaine réservé par admission R14 ; entrée du corps natif encore à observer | Ni instruction native déjà exécutée ni résultat acquis ; le corps peut ne jamais être appelé/retourner |
| DONE4 | Vrai retour natif observé, résultat stocké | Pas d'absence de DMA/périphérique ni d'affichage reçu |
| REFUSED5 avant entrée | Génération de cible devenue périmée | Pas une annulation d'une opération exécutée |
| ACK terminal | Le destinataire a consommé DONE ou le refus préalable ; slot réutilisable pour la file | Ne libère aucun objet matériel et ne confirme pas le LCD |
| ANNULÉE | Aucune API d'annulation implémentée ni preuve native | Ne pas renommer timeout/stop/refus en annulation |

Le compteur `admitted` compte les réservations de domaine, pas les effets natifs. RUNNING seul ne certifie aucune instruction native ; les marqueurs de vrai retour et les chemins ARM apportent cette preuve séparément.

`result` n'est disponible qu'en DONE avec l'ID demandé exact. La valeur sentinelle n'est jamais un retour Korg. La tête DONE/REFUSED reste comptée dans la capacité jusqu'à ACK. Elle ne peut ni être réexécutée ni écrasée par une acceptation ultérieure. Une absence d'ACK peut donc saturer volontairement la file plutôt que perdre une réponse.

Les IDs sont strictement croissants pour les commandes acceptées dans cette session. Doublons et IDs inférieurs au dernier accepté sont refusés avant/après terminaison. Un ID refusé pour saturation n'est pas consommé et peut être réessayé après place libérée. Pas de wrap ni de réinitialisation pendant que d'anciens handles/réponses existent. Ce n'est pas un journal distribué persistant ni un algorithme multiproducteur atomique.

## Ordre, réentrée, fermeture

FIFO sans dépassement de la tête bloquée. Les arguments scalaires sont copiés à submit et restent invariants même si le tableau de l'appelant change. Le registre de cible/génération est une **précondition de fixture**, pas un registre natif Korg prouvé. Une transition de page peut invalider une cible : la commande est explicitement refusée avant exécution et sa réponse attend ACK ; pas d'exécution sur un objet de remplacement ni de suppression silencieuse.

Le même owner ne peut réentrer une admission active. Une soumission depuis un callback peut être conservée, mais sa tentative d'exécution attend la fin extérieure. La fermeture de file refuse les nouvelles soumissions, conserve les anciennes et permet leur drainage réel. L'admission R14 ne doit être fermée qu'au moment approprié : la fermer pendant une opération active bloque toute nouvelle admission et peut empêcher définitivement le drainage. Aucun délai ne vole l'autorité en cours.

Les exécuteurs du banc construisent un message scalaire par C003B7FC et appellent réellement la commande LCD2 (demande seulement). Ils stockent le **retour réellement obtenu**. Ils ne prétendent pas reproduire les services17/34 complets ni servir de codec générique à C002D684.

## Compatibilité avec les services synchrones

| Stratégie | Condition nécessaire | Résultat R15 |
|---|---|---|
| Différer avant appel et retenir la continuation de l'appelant | Arguments/objets vivants, contexte/pile conservés, attente qui n'empêche pas de libérer DRAW/READ | Non démontré nativement ; auto-attente si l'appelant conserve le domaine requis |
| Retourner WAIT à la place du résultat natif | Contrat explicite de l'appelant pour un résultat futur | Aucun tel contrat trouvé aux frontières étudiées ; incompatible comme remplacement transparent |
| Refuser avant effets | L'appelant sait traiter cette erreur, sans dépendre d'outputs non produits | Propriété du modèle seulement ; pas un code d'erreur Korg à inventer |
| Reporter après entrée du service | Retenir les handles temporaires de pile et leurs pointees, préserver effets déjà réalisés | Incompatible sans preuve de continuation/propriété profonde ; destructeurs au retour |
| Mettre toutes commandes sous propriétaire unique | Conserver contexte, résultats, notifications, ordre et nettoyage | Candidat de recherche ; déplacement de contexte non équivalent démontré |
| Différer le wrapper UI entier | Tolérer les messages ajoutés et le changement de manager avant consommation | Pas une conservation exacte d'une commande/page déterminée |

**Aucune stratégie n'est déclarée transparente pour l'ensemble des services natifs synchrones.** R15 donne un protocole de conversation propre au laboratoire, pas une nouvelle valeur de retour à placer dans une routine Korg.

## Coût et hypothèses

Admission R14+pool =3176 octets ; plus file128 =**3304 octets**. Le registre local diagnostique de références mesure20 octets, total de ces structures **3324 octets**. Les objets cibles, registres de génération, copies profondes éventuelles, réponses externes, piles, code, source/shadow et fixtures ne sont pas inclus. Aucune marge RAM/temps instrument n'est prouvée.

Les métadonnées sont séquentielles et supposées sérialisées. ARM926/ARMv5TE ne permet pas de supposer les atomiques ARMv7. Aucune sûreté IRQ/FIQ/DMA, cohérence cache/MMU ou équité n'est déduite du FIFO. Les modèles bornés ont capacité2/trois requêtes, et les essais C capacité3 ; la différence de bornes est explicite.
