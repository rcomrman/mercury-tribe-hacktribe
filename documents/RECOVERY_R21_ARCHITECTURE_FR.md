# R21 — architecture persistante à empreinte fixe

Le prototype est un objet statique initialisé une seule fois. Il contient le
bridge V30, l'état d'interface avec ses 12 paramètres et ses quatre mini-LFO au
total, ainsi que le triple buffer R12. Il ne possède ni constructeur/destructeur
Korg, ni clé d'observateur, ni pointeur recyclé. Un changement de page modifie
deux entiers ; il ne recrée aucune ressource.

| État | Entrées permises | Effet |
|---|---|---|
| `INIT` | `activate`, changement de page | stockage créé, aucun rendu |
| `ACTIVE` | calcul, commit privé, changement de page | publication dans R12 |
| `INACTIVE` | `activate`, changement de page | callback possible mais refusé |
| `FAULT` | aucune opération graphique | état terminal, stockage conservé |

Le rendu est séparé en calcul et commit. Si l'arrêt logique intervient entre les
deux, le résultat calculé est abandonné et le buffer publié ne change pas. Cela
prouve une règle locale ; l'état `INACTIVE` ne prouve pas la cessation d'un
callback natif, d'un lecteur LCD ou d'un autre auteur du framebuffer.

Le chemin B réutilise `C006EA10`, déjà appelé par `C006F178`. Sur le banc, ses
trois slots pointent vers des composants statiques dont la méthode virtuelle +8
est appelée exactement une fois. Aucun gestionnaire d'événements n'est créé.
Cette exécution ne prouve pas qu'une page réelle autorise l'insertion du pointeur
Mercury, ni que le cycle UI complet constitue une fenêtre de publication.

La copie vers une source dite native est désactivée par défaut. Les expériences
C ne l'autorisent qu'avec un jeton d'autorité de fixture. Une copie partielle
produit volontairement une image mixte ; un auteur non participant peut aussi
modifier l'image après une copie complète. Ces témoins interdisent de présenter
la garde locale comme une synchronisation native.
