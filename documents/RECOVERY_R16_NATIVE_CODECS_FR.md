# R16 — codecs natifs par famille

Base65d776f. RESEARCH_ONLY. Aucun nouveau codec installé dans Korg.20 plages natives identiques sur les deux VSB. « Reportable explicite » signifie une nouvelle API Mercury de laboratoire dont le destinataire accepte une réponse ultérieure, jamais une substitution transparente au retour natif.

| Famille et entrée | Contexte / arguments / taille | Propriété, durée de vie, sorties | Résultat et report |
|---|---|---|---|
| LCD demande2 : C0015DD0(desc,2,0) | Timer/UI/services ; descripteur fixe C031BB2C, pas de payload | Descripteur natif partagé, durée de vie non transférée ; écrit octet+5 si active=1 | Retour0 même inactif ; ni livraison ni exécution worker. Codec sans payload, report explicite d'intention seulement ; fusion/changement de source non équivalents à un historique d'images |
| LCD contraste4 : C0015DD0(desc,4,&u8)→C0015F44 | Appel synchrone ; entrée pointée **1 octet**, lue seulement si descripteur actif | Pointeur possédé par l'appelant jusqu'à la lecture ; aucun pointeur retenu dans ce corps. Copie dans mot desc+8 et flag octet+0xC ; pas de sortie dans l'entrée | Retour0 actif/inactif. Codec distinct : capture1 octet dans enveloppe propriétaire puis prêt temporaire à l'appel natif ; report explicite selon ordre accepté par Mercury. NON REPORTABLE de manière transparente pour un appelant qui attend l'effet immédiat |
| UI rafraîchissement type0 : C0070AF0(msg,0,0,0), C0083FE8(msg) | Producteurs dont compteur en tâche2 ; consommation tâche4 ; message16 octets | Construction/copie de type+deux mots ; ici mots nuls, aucun pointee. Queue et gestionnaire restent natifs ; manager actif indispensable, durée de vie jusqu'à consommation/retrait à prouver | Constructeur/publisher sans accusé d'exécution. Codec UI type0 exclusivement, pas un codec générique pour type8/16 ou messages à pointeurs ; report explicite d'intention, pas garantie de page/génération physique |
| Progression : C006040C(obj,r1,r2,r3), C006038C(obj,value) | Démarrage et services ; objet16 octets, vtable+trois champs32 ; configuration écrit+4/+8/+C, dessin puis LCD2/LCD3 synchrones | Getter natif C004D598 associé à C0366D5C ; propriété native partagée. Objet et continuation doivent survivre au retour ou blocage. Pas de copie propriétaire générique démontrée | **NON REPORTABLE** dans le périmètre : effets immédiats objet/source, appels LCD synchrones, pas de contrat futur ou refus natif établi |
| Services17/34 via C002D684 | Tâche5, messages16 octets, deux mots transformés en objets/handles temporaires | Les mots peuvent désigner des objets dont les tailles/propriétaires complets restent inconnus ; handles sur pile et nettoyage au retour | **NON REPORTABLE générique** ; pas d'extension du codec scalaire R15 à des pointeurs inconnus |

## Précisions natives

C0015F5C est un `LDRB` ; C0015F68 stocke la valeur dans desc+8 et C0015F74 pose le flag+0xC. Aucun clamp supplémentaire ni longueur de structure ne doivent être inventés : valeur u8 native0..255, validité physique du contraste non démontrée. C0015DD0 retourne0 aussi quand active!=1 et n'a alors pas déréférencé le payload. Le succès de lecture/copie ne garantit pas l'envoi du contraste.

Le worker traite le flag de contraste en entrant dans le transport avant de le remettre à zéro. C0015CDC attend un statut SPI ; aucun délai/annulation dans le corps inspecté. Le codec doit conserver un emprunt du descripteur, et ne peut déclarer sa propriété transférée à Mercury parce que son adresse est fixe.

Le codec de contraste capture la valeur au moment de l'acceptation : l'appelant peut ensuite modifier son octet sans changer la valeur conservée. Cela définit un contrat nouveau et explicite ; ce n'est pas une preuve que tous les appels natifs accepteraient un décalage temporel. Un champ de sortie natif partagé (desc+8/flag) peut être observé entre-temps : l'ordre réel doit être conservé ou le report refusé.

## Raccordement expérimental

Une enveloppe typée contient opcode, valeur possédée et token de référence de cible. Pas de pointeur vers l'octet appelant conservé. La file R15 conserve quatre mots encodés, identité, génération et résultat jusqu'à ACK ; les enveloppes et leurs emprunts restent détenus jusqu'au résultat consommé. Un refus de submit doit rendre immédiatement l'emprunt capturé ; une opération fautive ne le libère pas.

La génération de cible n'est pas un sémaphore ni un compteur de réception. Les enregistrements de cible natifs sont cartographiés séparément ; l'enveloppe ne rend pas le descripteur, le gestionnaire ou la page propriétaires de Mercury. Aucun code WAIT natif n'est ajouté.

Preuves : `tools/recovery_r16/audit.py`, `reports/recovery_r16/audit.json`, `native_disassembly.txt.gz`. Les expériences ARM R16 contrôlent les bornes d'un octet, la copie propriétaire, l'inactivité, le report explicite et ses limites. Toutes les familles non retenues restent inconnues ou NON REPORTABLES jusqu'à qualification de leur contrat.
