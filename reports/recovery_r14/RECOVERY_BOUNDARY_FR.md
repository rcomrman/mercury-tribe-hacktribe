# R14 — détection, confinement, annulation, restauration

Recherche bornée, sans preuve de récupération native indépendante. Les nouveaux cas28..31 ne rejouent pas R11 : ils combinent les services noyau originaux avec une autorité READ/CRITICAL R14 active pour vérifier leur effet sur cette autorité. Les TCB/listes/statuts sont des fixtures RAM, pas un ordonnanceur complet.

## Ce que font réellement les mécanismes inspectés

| Mécanisme | Fait natif / expérience | Ce qu'il ne prouve pas |
|---|---|---|
| Attente SPI C0015CDC | Boucle sur C00117C8 jusqu'au bit0x200 du mot périphérique+0x10 ; aucun compteur/délai/sortie d'erreur dans ce corps | Pas de borne, de timeout autonome ni d'annulation du worker. Aucun MMIO mappé pour le faire réussir |
| Échéance C0001C7C | Écrit −50 dans le résultat d'attente, rend éventuellement prêt et demande un dispatch | Pas d'arrêt d'une autre tâche, d'unwind ni de libération d'un objet graphique |
| Nouvelle combinaison cas28/29 | Appel natif d'expiration sur TCB en attente ; résultat−50, état prêt1, sélection TCB et flag de réordonnancement1 ; READ/CRITICAL restent actifs, source/shadow inchangées | Ni reprise effective du TCB, ni interruption d'un worker non retournant, ni annulation du LCD |
| Prise sémaphore C0000D80 | Cas30 : contexte interdit, retour−25 ; domaine READ toujours détenu | Une erreur de prise n'est pas une expiration du propriétaire ni un droit de libérer son emprunt |
| Insertion prête C00018F0 | Cas31 : observateur rang6 n'évince pas sélectionné rang1 ; fixture indépendante rang0 le remplace dans le pointeur de sélection | Ce pointeur n'est pas un changement effectif de contexte ; aucun nouvel observateur natif ni rang libre configuré |
| Cyclique C000143C | Réarme puis appelle callback+8 ; instructions de masquage/démasquage IRQ | Dépend des IRQ, du timer et du contexte ; callback existant réveille2/10, n'implémente pas un surveillant LCD. Non exécuté comme chaîne matérielle ici |
| Diagnostic C00298BC | Masque IRQ, efface/dessine, LCD2/LCD3, GPIO, boucle C00299F4 | N'est ni indépendant du transport ni une restauration sûre ; peut intervenir pendant une composition |
| Sortie/arrêt noyau | R11 conservé ; boucles terminales et sortie courante | Pas de reset matériel, d'annulation des autres accès ni de destruction Mercury démontrés |

Les retours négatifs ne sont pas traités comme des succès d'opérations LCD. Les assertions attendues restent fixes ; les six cas GPIO R14 atteignent01E260BC/signal11. Le handler Linux observe et termine le processus ; il ne reprend pas Korg.

## Confinement proposé, preuves manquantes

L'observateur du modèle compare un ticket et un compteur de progression. S'ils n'ont pas changé, il pose suspicion ; il ne peut déterminer si l'attente est légitime, si l'observateur a été affamé ou si le transport est réellement mort. Les cas12/24/25 injectent cette observation dans un autre contexte logique : ni temps réel écoulé ni exécution parallèle démontrés.

Le résultat utile est limité : après suspicion, les participants n'admettent plus d'opérations et ne libèrent pas l'emprunt/propriétaire actif. Cela évite de convertir une absence de progrès en réutilisation de mémoire. Cela peut bloquer définitivement le banc ; aucun chemin de sortie de suspicion n'est fourni.

Un observateur plus prioritaire n'est qu'une condition envisageable. Il peut lui aussi dépendre d'un timer masqué, de dispatch désactivé ou d'un sémaphore détenu. Le modèle de100 sélections à rangs initiaux montre qu'un observateur moins prioritaire ne peut surveiller une boucle active plus prioritaire ; il ne mesure pas des cycles ou millisecondes.

## Quatre preuves distinctes exigées

1. **Détection** : contexte exécutable malgré le worker bloqué, horloge fiable et observation cohérente/atomique, seuil justifié et gestion des faux positifs. Non démontré nativement.
2. **Confinement** : empêcher tous les accès nouveaux, y compris diagnostic, services, IRQ/FIQ/DMA éventuels. Seulement coopératif dans le banc.
3. **Annulation** : établir que le worker, ses callbacks et le matériel n'accéderont plus aux buffers/objets ; état des verrous, piles et périphériques connu. Aucune preuve.
4. **Restauration** : rétablir une UI/source et un état transport Korg cohérents sans dépendre du LCD en panne. Aucune preuve.

Un état shadow==source ne satisfait aucune preuve de réception ni d'annulation. Un timeout ne justifie pas de débloquer de force READ, CRITICAL, sémaphore ou emprunt. **NO GO récupération indépendante sur instrument.** Le périmètre inspecté n'établit pas l'absence de tout watchdog dans l'ensemble du firmware.
