# R16 — détenteurs et retrait des références CPU

RESEARCH_ONLY. Cette carte donne des sites vérifiables et leurs limites ; elle ne prétend pas recenser tous les alias de Korg. Les anciennes preuves R12–R15 restent inchangées.

| Détenteur | Enregistrement / stockage | Consommation / retrait / destruction | Couverture |
|---|---|---|---|
| Messages de service | C002D5D8, constructeur C003B7FC et copie C003B7D4 ; deux mots+8/+C | C003B81C retire la tête ; C002D684 construit des objets temporaires, handles sur pile ; C002D5B0 appelle destructeur+4 C002D434 | PROUVÉ borné ; pointees génériques et continuations complètes INCONNUS |
| Queue UI | C0083FE8 ; copie C0070A80, publication via slot+8 | C0070B10 copie puis retire ; drains C0083848/C0083428 dispatchent sur la pile | PROUVÉ routes connues ; pas d'ACK d'exécution global |
| Wrapper/gestionnaire UI | Wrapper+4, racine C0691378 et gestionnaires C03404C0/BC/B8 connus des audits antérieurs | C002D030 recharge la cible ; transitions changent les cibles et peuvent détruire leurs pages | PARTIEL ; retirer une racine n'efface pas toutes les copies |
| Pages secondaires | C006E9A0 appelle destructeur+4 de l'ancien manager+0x14, met0 puis installe le résultat de fabrique | C006EFD0 détruit+met0 ; reste de la routine dépend d'autres services | PROUVÉ sur instructions ; aucune garde du nouveau registre consultée |
| Vecteur graphique/enfants | C00614FC copie la valeur du pointeur enfant et avance fin+4 ; manager/page possède la liste | Parcours C006F178 et C0083374 appelle slot enfant+8 ; destruction C0060F10 et méthodes enfants | PARTIEL ; thunks/sous-objets et références externes restent à qualifier |
| Inscription observateur | **C0070778**, sujet avec32 entrées de24 octets à+4 ; append du sujet dans vecteur de l'objet clé+4/+8/+C | **C00705DC** recherche la première clé identique, efface entrée/flag actif ; pas le vecteur inverse | PROUVÉ natif et ARM R16 ; retrait d'un seul côté seulement |
| Callback d'observateur | C0070688 parcourt les flags actifs, C007061C invoque la fermeture | Retour de callback ne retire pas toutes les inscriptions ; retrait pendant callback n'annule pas le cadre déjà entré | PROUVÉ borné ; réentrée et cadre extérieur testés |
| Destructeur base observateur | C0041B74 parcourt son vecteur de sujets et appelle C00705DC(sujet,this), puis libère le vecteur | Nettoyage fondé sur les sujets recensés, pas une recherche globale des alias | Statique PROUVÉ ; destructeur complet avec tous services non rejoué |
| Timer LCD | Compteur+0xC=C002A71C, stocké par construction à partir de C002A970 | C002A7EC appelle synchronement ; worker peut ne pas retourner | PARTIEL ; aucun retrait complet/annulation indépendant validé |
| Frames/continuations CPU | Paramètres et variables de pile dans dispatch, parcours et callbacks réentrants | Seulement après vrai retour des cadres correspondants | INCONNU global ; profondeur du banc seulement |
| Lecteurs natifs/périphérique | Source fixe/shadow/descripteur et GPIO/SPI | Comparaison/copie avant transport ; contrôle7 dépend aussi du matériel | NON COUVERT par registre coopératif ; DMA/IRQ/FIQ non exclus |

## Fermeture native d'observateur : deux identités à conserver

Une entrée de sujet commence par une **clé d'inscription** à+0, mais le callback charge son **contexte `this` distinct à+4**. Les mots+8 et+C décrivent méthode/ajustement ; le champ+0x10 reçoit l'argument r2 de registration, dont la sémantique complète reste ouverte ; l'octet+0x14 active l'entrée. Le sujet occupe au moins4+32×24=772 octets dans ce chemin. Ce n'est pas une preuve de taille de toutes ses classes dérivées.

C0070778 reçoit r0=sujet, r1=clé, r2=champ supplémentaire, r3=descripteur de fermeture3 mots (`this`, mot méthode, ajustement encodé). Le callback C007061C utilise une représentation de méthode pouvant charger une entrée virtuelle si l'ajustement est impair. Les tests R16 n'exercent que le cas direct avec ajustement0. Ils ne substituent pas un pointeur de fonction simple à toute représentation C++.

La clé n'est donc pas automatiquement le propriétaire du contexte. **Le cas32 enregistre cléA/contexteB et appelle réellement B.** Le vecteur inverse est ajouté à l'objet cléA ; la durée de vie de B exige une preuve séparée. Un registre qui ne retient que A omettrait un détenteur indispensable.

C0070778 retourne quand la clé existe déjà : le cas33 montre qu'une réinscription avec un autre contexte ne remplace pas le contexte précédent. Celui-ci doit rester vivant. Le cas21 confirme l'idempotence de la registration séquentielle pour cette clé, sans en déduire une atomicité sous préemption.

C00705DC efface le slot du sujet puis retourne ; il ne retire pas le pointeur sujet du vecteur inverse. Après retrait/réinscription, le cas22 observe deux pointeurs de sujet dans ce vecteur. Ce n'est pas deux callbacks actifs pour cette clé : les deux directions doivent être distinguées. Le cas30 confirme que deux retraits natifs sans callback actif sont idempotents sur le slot, tandis qu'un double retrait du token de registre est refusé.

## Frontière de l'exhaustivité

Le registre expérimental ne s'installe pas dans ces sites. Il peut représenter des références de file, wrapper, service, callback, page et continuation **déclarées par le banc**. Il ne découvre ni les adresses brutes ni les contextes cachés dans les fermetures. Les cas15/16/29/32 conservent cette limite comme contrôles négatifs. Aucun succès local ne fait passer la colonne INCONNU à PROUVÉ global.
