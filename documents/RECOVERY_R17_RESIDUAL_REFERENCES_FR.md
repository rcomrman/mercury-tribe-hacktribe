# R17 — matrice des références et accès résiduels

« Couvert » signifie couvert uniquement par le contrat de la fixture, avec sérialisation extérieure et participants recensés. Les sources natives restent intactes.

| Accès / racine | Fait natif ou observation | Couverture expérimentale | Résidu / preuve manquante |
|---|---|---|---|
| C0070778 inscription | Clé séparée du this ; doublon de clé ignoré | Gardée seulement pour graphe préconstruit et OPEN | 119 branches candidates ; inscription native directe contourne CLOSING, cas18 |
| C0070688 notification | 32 slots, sélection par actif | Garde avant parcours, cinq pins, tuple gelé | 120 branches candidates ; tâches exactes de chaque site non attribuées |
| C007061C invocation | this chargé avant méthode ; BLX après résolution | Fenêtres reproduites à trois PCs par debugger | Entrée directe ou copie de slot peuvent contourner l'admission, cas13 |
| C0082728 notification périodique | Compteur par slot, diviseur+16, appel C007061C | Contournement natif reproduit, cas22 | Aucune garde installée ; domaine distinct à médiatiser |
| C00705DC retrait | Efface première relation sans join ni compaction inverse | Différé jusqu'au dernier retour admis | 12 branches candidates ; retrait direct pendant résolution produit faute, cas6 |
| Clé A, contexte B | Pointeurs différents dans tous les essais ordinaires | Cinq ressources distinctes, contexte jamais déduit de la clé | Autres propriétaires/alias du contexte inconnus |
| Même clé, autre contexte | L'ancienne fermeture reste enregistrée | Cas8 constate l'absence de remplacement | Le producteur ne doit pas croire son nouveau contexte enregistré |
| Vecteur inverse | Doublons après retrait/réinscription | Cas9, compaction de fixture des doublons | Ancienne relation vers un autre sujet bloque le prédicat, cas19 |
| C0041B74 destructeur inverse | Parcourt sujets, appelle retrait, libère vecteur | Audit statique uniquement, stockage du banc jamais libéré | 51 branches +1 pointeur candidat ; destruction concurrente non qualifiée |
| this ajusté / méthode virtuelle | Encodage ASR1, bit virtuel, chargement vtable | Cas20/21 : direct+16 et virtuel+16 | Réécriture concurrente vtable, héritage complexe et propriétaires réels inconnus |
| Cadres sélectionnés | Callback peut survivre au slot effacé | Cas3, quatre registres/PC documentés par arrêt exact | Pas de join natif trouvé |
| Cadres réentrants | Appels imbriqués conservent leurs pins | Cas10/11 ; tickets et emprunts indépendants | Profondeur réelle non bornée ; quatrième admission refusée |
| Changement de page | Nouvelle racine logique, ancien parcours retenu | Cas12/27, changement scalaire de fixture | Destructeurs/page factory Korg complets non rejoués ni protégés |
| Alias brut copié | Callback possible après inactivité locale | Cas13, aucun free réel | Inventaire global des copies de fermeture absent |
| Adresse / génération | Vieux token refusé, pointeur brut encore utilisable | Cas15, réemploi de métadonnées seulement | Aucun allocateur réel ni ABA matériel qualifié |
| Commande retenue | Référence maintenue jusqu'au refus avant effet et ACK | Cas16, file R15 inchangée | Service déjà lancé et pointeurs profonds arbitraires non annulables ici |
| Plusieurs slots / autres clés | Un parcours peut continuer après une fermeture intérieure | Cas26 refus de tuple inconnu, cas28 deux callbacks natifs | Pas de couverture générale des propriétaires d'un sujet partagé |
| Callback bloqué / worker | Le cadre ne retourne pas dans le banc à l'accès MMIO | Cas17 conserve cadre, callback et pins | Détection indépendante, arrêt périphérique, reprise et restauration inconnus |
| IRQ/FIQ/DMA et appels calculés | Aucun inventaire exhaustif | Non couvert | Une recherche de mots ARM alignés n'est pas une preuve d'absence |

Les nombres de candidats sont des résultats du scan ARM aligné, pas un décompte certifié de tous les appels exécutables. Les traces démontrent les parcours exercés seulement. Le banc ne corrige ni une référence cachée ni un appelant qui omet le gate. Une valeur locale zéro, une génération changée et un slot inactif ne constituent jamais une cessation globale.
