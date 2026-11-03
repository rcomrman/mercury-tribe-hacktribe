# R13 — second point de sauvegarde, finalisation encore à publier

3 novembre2026. Base de reprise58bbfba748f499135a44170d170ec36d63023fa4. Cette note et les deux ajouts de diagnostic sont publiés par GitHub API après une nouvelle indisponibilité du terminal. **Ce commit ne clôt pas R13 : les archives complètes et la provenance finale doivent encore être publiées. R14 n'est pas commencée.**

## Travail réellement effectué depuis la reprise

- Le volume original a été retrouvé à la tête locale R12, avec les dossiers R13 non suivis.
- **92 fichiers originaux** ont été conservés avant synchronisation, avec manifesteSHA. Ils sont dans work/r13_original et une copie destinée à Git dans reports/recovery_r13/recovered_original.
- Les C/header/runner originaux étaient identiques octet par octet à58bbfba. Les originaux de audit.py/models.py, plus riches que la retranscription, ont été restaurés localement.
- Les40 archives originales ont été reparsées et validées avant de les rejouer.
- Le lanceur complet sauvegardé a réussi, suivi du vérificateur. Le premier rejeu donne40/40 records bruts identiques aux originaux et40/40 séquences de lignes d'instructions natives identiques. Les traces binaires diffèrent : elles restent toutes conservées séparément.
- La revue a démontré une assertion inaccessible au cas16 : CHECK du diviseur après un appel qui faute avant son retour. La même assertion est déplacée dans l'observateur Linux de faute et émet étape88=1. L'attente GPIO native reste01E260BC ; aucune attente de succès n'est relâchée.
- Le cas18 observe maintenant directement ses32 callbacks et indices32/32 par étape18.
- Les20 cas par VSB ont été recompilés et rejoués après ces ajouts : **40 cas,26 sorties normales,14 fautes attendues,32 images V30/VSB et égalité exacte entre VSB**.
- Un vérificateur autonome local, sans appel aux fonctions decode/validate du runner, a contrôlé les phases, les images complètes, les fautes, les diagnostics, les archives originales et52 records R12. Il a réussi.
- Les records finaux sont bruts identiques pour36/40 cas et identiques pour40/40 après retrait des seuls nouveaux diagnostics16/18 et renumérotation de séquence. Les lignes d'instructions natives correspondent pour40/40.
- Tous les chemins suivis par R12, les VSB et le triple buffer R12 restent intacts.

Dernière sortie du vérificateur lue :
    PASS:40 R13 cases;32 V30 images/VSB;26 normal and14 expected faults;DRAW/READ/CRITICAL/FAULT oracles;52 R12 archives;92 recovered originals intact;R1-R12 unchanged

## Blocage actuel et reprise exacte

Le terminal est devenu indisponible à nouveau pendant la dernière relecture et avant le commit de finalisation. Le rapport final et les preuves sont déjà préparés localement ; ils ne sont pas tous inclus dans ce second commit. Ne pas présenter les statistiques ci-dessus comme un remplacement des archives.

Les fichiers locaux importants comprennent :
- reports/recovery_r13/recovered_original/ et son manifest.json : archives originales, jamais régénérées ;
- records/traces du rejeu final à la racine de reports/recovery_r13/ ;
- recovery_validation.json, baseline_replay_comparison.json, original_final_comparison.json ;
- validation_notes.json, independent_verification.log, launcher_validation.log ;
- access_graph.json, native_disassembly.txt.gz, models.json, results.json, provenance.json ;
- tools/recovery_r13/verify.py autonome, plus complet que celui du premier checkpoint ;
- audit.py/models.py originaux restaurés ;
- rapport et carte/architecture finalisés localement.

Quand l'accès revient : conserver ce volume, synchroniser sans écraser ses changements, comparer les sources avec ce commit, relire les documents, compléter le statut final JSON si absent, exécuter le vérificateur autonome puis publier tous les fichiers et vérifier la tête distante. Ne pas supprimer58bbfba ni ce second checkpoint et ne pas faire de force-push.

Aucune panne ARM d'attente inattendue n'a été constatée pendant cette reprise. La correction concerne la portée de l'assertion du cas16 ; les contre-exemples et fautes natives restent conservés. Aucune réponse GPIO/SPI fabriquée, aucun flash ou firmware installable.

Conclusion technique inchangée : cohérence conditionnelle des acteurs coopératifs dans le banc ; aucun point global sûr ni récupération indépendante démontrés sur instrument. La finalisation logicielle doit encore être durablement publiée avant de déclarer R13 terminée.
