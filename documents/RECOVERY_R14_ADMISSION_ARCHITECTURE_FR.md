# R14 — admission de domaines exclusifs et confinement conditionnel

RESEARCH_ONLY. Aucun code installé ; contrats R12/R13 conservés tels quels. `tests/recovery_r14/admission.h` est une extension de laboratoire, C séquentiel, dont chaque appel nécessite une sérialisation extérieure et une couverture de tous les accès. Ni IRQ mask, ni atomique ARMv7, ni sémaphore global ne sont inventés.

## Contrat et responsabilités

La structure embarque le gate R13 de32 octets ; huit champs u32 ajoutent32 octets : propriétaire logique, ticket monotone, source complète, pages terminées, fermeture, demande CRITICAL, suspicion et progression logique. Taille ARM mesurée **64 octets**, soit **3176 octets avec le pool R12 de3112**, contre3144 pour gate R13+pool. Cela exclut piles, fixtures, snapshots et autres structures ; aucune RAM instrument libre n'est prouvée.

| Interface | Préconditions et résultat | Limite / responsabilité extérieure |
|---|---|---|
| DRAW begin | IDLE sans fermeture/suspicion, owner non nul, tickets/epoch non épuisés, ni READ demandé ni CRITICAL réservé ; acquire R12 réussit | Ticket retourné signifie admission du banc uniquement ; aucun appel natif exécuté à ce stade |
| COPY / DRAW done | Propriétaire+ticket+handle R12 courants ; copie séquentielle jusqu'à1024 ; fin seulement complète | Ordre composition Korg/Mercury reste à qualifier ; aucun accès non participant détecté |
| Request READ | Mémorise une demande ; n'appelle pas le LCD | Plusieurs demandes fusionnent ; pas de comptage ni accusé physique |
| READ begin | IDLE complet, demande présente, pas CRITICAL réservé ; retient le domaine pour tout le scan | Les lecteurs ne peuvent être réduits à une page protégée |
| Page ready/done | Owner+ticket, page attendue0..7 ; compteur n'avance qu'après retour du comparateur | API de comptabilité ; ne prouve pas qu'un appelant n'a pas menti ou qu'un lecteur caché a fini |
| READ done | Les huit pages sont comptées ; fin réelle des lecteurs requise | `prepared_epoch` suit source ; aucune génération reçue par LCD n'est ajoutée |
| Request CRITICAL | Mémorise une intention bornée, sans arguments ni allocation | Ce bit n'est pas une queue de commandes natives ni un retour natif de réussite |
| CRITICAL begin | IDLE complet, sans emprunt lecteur/écrivain privé, sans fermeture/suspicion ; bloque nouvelles compositions/lectures | Enveloppe l'opération Korg entière ; admission au point extérieur à prouver |
| CRITICAL returned | Owner/ticket courant et vrai retour natif avec source complète prouvée par le contrat de l'appel | Ne doit jamais être appelé après faute/timeout ; aucune détection automatique de fin ou rollback |
| CLOSE | Rejette nouvelles admissions, ferme le pool ; permet de terminer l'opération déjà admise | Libérable seulement à IDLE sans owner et pool fermé ; pending READ peut subsister sans accusé |
| Observer stall | Compare ticket/progression échantillonnés et pose suspicion ; conserve phase, owner, emprunt | Observateur injecté, pas une horloge ni un watchdog natif. Faux positif possible ; aucune annulation/restauration |

Les valeurs d'identité sont des jetons de fixture, pas des identités de tâches authentifiées. Une nouvelle session ne peut réinitialiser arbitrairement ticket/pool et accepter d'anciens pointeurs. Les générations R12 ne sont pas remplacées par le ticket de domaine. Les épuisements refusent l'admission, sans wrap supposé sûr.

READ demandé empêche un nouveau DRAW, et CRITICAL réservé empêche READ/DRAW. Cela évite une classe de famine par nouvelles compositions dans le modèle borné, mais ne prouve aucune équité : des CRITICAL répétés ou un lecteur qui ne retourne jamais peuvent tout bloquer. Une fermeture ou suspicion n'autorise aucun vol d'emprunt.

## Appels synchrones et modes UI

L'admission doit précéder le dispatch complet du domaine : wrapper UI C002D030, transaction de service C002D684, démarrage exclusif et callback worker sont des frontières distinctes candidates. Une opération refusée reste **non exécutée** ; on ne renvoie jamais une valeur de succès Korg inventée. Un adaptateur réel doit préserver les arguments, objets, durées de vie et la sémantique d'attente/refus de son appelant avant d'être envisageable.

Le corps CRITICAL appelle une seule opération native complète, sans réacquérir une garde non récursive autour de chacun de ses appels LCD internes. Toute réentrée de domaine, y compris du même owner, est refusée. Le cas de progression réel garde CRITICAL jusqu'à la faute GPIO. Le cas avec LCD inactif montre un retour natif sans préparation/réception : ce contrôle négatif ne valide aucun affichage.

Le banc exerce la voie UI alternative native et un widget de fixture sous admission. La voie principale et les pages secondaires restent conditionnelles aux preuves antérieures, non rejouées. Une protection seulement dans le widget Mercury laisserait les autres widgets et destructions hors domaine.

## Architectures comparées

| Option | Apport | Obstacle restant |
|---|---|---|
| Admission distribuée par domaines | Contrats explicites, refus, durée de vie et fin de scan vérifiables dans le banc | Couverture extérieure et sérialisation natives absentes |
| Propriétaire unique avec file de commandes | Peut ordonner l'ensemble des accès et borner les commandes nouvelles | Déplacer des appels synchrones modifie leurs contextes, piles, attentes et résultats ; aucun équivalent démontré |
| Sémaphore partagé par les adaptateurs | Sérialiserait les participants | Accès natifs non participants, ID disponible, inversion, réentrée et blocage non borné |
| Priorité/plafond ou masque IRQ | Peut limiter certaines préemptions qualifiées | Ne couvre ni toutes attentes, FIQ/DMA, réentrée, ni latence audio ; pas installé |
| Snapshot privé du lecteur / comparateur substitué | Isolerait les publications privées | Le comparateur original lit la source fixe ; sa substitution serait une autre architecture, non installée |

Aucune option ne fournit à elle seule détection indépendante, annulation et restauration.

## Frontière de récupération

La suspicion contient uniquement les **participants coopératifs**. Le cas ARM avec observateur injecté conserve READ/CRITICAL et refuse la fermeture effective ; les accès directs Korg peuvent toujours passer. Ne pas représenter ce résultat comme arrêt du worker.

Détection exige une source de temps/progression et un contexte encore exécutable ; confinement exige une autorité sur tous les auteurs/lecteurs ; annulation exige preuve que le worker, IRQ/DMA et services n'accéderont plus aux ressources ; restauration exige un état source/transport/Korg connu et une voie qui fonctionne malgré le LCD en panne. Aucun de ces quatre maillons n'est acquis comme chaîne native complète.

Une expiration d'attente noyau peut rendre une tâche prête et écrire un statut ; cela ne prouve ni qu'elle a repris, ni que le propriétaire d'un verrou a été interrompu, ni qu'un transfert a été annulé. Le diagnostic fatal appelle encore le LCD et peut masquer IRQ. NO GO récupération indépendante et sûreté instrument.
