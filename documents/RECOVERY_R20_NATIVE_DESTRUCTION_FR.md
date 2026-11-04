# R20 — chaîne native et points d'arrêt avant libération

Base dce3fdc. Les150 SHA R19 ont été vérifiés en lecture seule, sans relancer les expériences historiques.

## Références et étapes

| Élément | Fait local prouvé | Limite |
|---|---|---|
| C00852B0 constructeur | Prépare objet et clé inline+0x38 ; inscrit sur sujet global ; méthode C0085078, this=objet, période10 | Dépend d'autres services et du heap ; retour complet non acquis par ce seul audit |
| C0085078 callback | Si octet objet+0x48 non nul, inverse le bit0 de +0x49 et pose +0x14=1 | Aucun test de fermeture, retrait ou vtable dans ce corps |
| C00851B4 destructeur non supprimant | Modifie vtables, appelle C0041B74 avec this+0x38, puis change la vtable extérieure | Peut libérer le vecteur inverse ; « non supprimant » ne signifie pas sans free |
| C0041B74 inverse | Parcourt chaque sujet, appelle C00705DC(sujet,clé), puis free du vecteur à C0041BB4 si non nul | Aucun join des callbacks |
| C00705DC retrait | Efface la première entrée correspondant à la clé | Ne retire pas les registres d'une invocation déjà résolue |
| C00851F4 variante supprimante | Appelle C00851B4 puis free extérieur à C0085204 | Dernier accès extérieur non prouvé |
| C00851EC / C0085210 | Thunks this−0x38 avant non-supprimant / supprimant | Une référence de sous-objet garde besoin de l'allocation entière |

C00E4DA8/+4 contiennent C00851B4/C00851F4 ; C00E4DD0/+4 contiennent les deux thunks. Les deux branches directes candidates vers C00851B4, la branche vers C00851F4 et les pointeurs de vtable sont publiés intégralement dans native-map.json. Ces nombres ne couvrent pas les appels calculés ni toutes les instances. Les transitions de page inspectées appellent virtuellement un slot+4 ; identifier l'instance réelle reste une obligation distincte.

## Deux frontières différentes

1. C0041BB4 : premier free du vecteur inverse, après les retraits de slots.
2. C0085204 : free de l'objet extérieur, après retour du destructeur non supprimant.

Les expériences doivent s'arrêter avant ces instructions sur des ressources statiques. Aucun free natif ne doit être exécuté sur un objet ou un vecteur utilisé par le banc. Un corps non supprimant n'est exécutable jusqu'au retour que si son inverse est réellement nul, ou a été détaché localement sans libérer le stockage permanent de fixture.

Une ancienne méthode C0085078 peut encore modifier le même objet sans consulter sa vtable. La modification des vtables par le destructeur n'est donc pas un mécanisme d'annulation.
