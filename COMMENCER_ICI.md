# MERCURY DUST MD44 — DOSSIER CLAUDE / AUTRE ASSISTANT

**Lecture recommandée :**

1. `PASSATION_POUR_CLAUDE_MERCURY_DUST_2026-11-01.md` (contexte complet).
2. `CLAUDE_PROMPT_A_COPIER.md` (mission précise pour Claude).
3. `MD44_RAPPORT_FR.md` (correction la plus récente, test rouge/vert).
4. `MD43_RAPPORT_FR.md` et `MD42_RAPPORT_FR.md` (portage simulé et limite SPI non résolue).
5. `src/` et `tests/` (sources et tests).

État du 1er novembre 2026. **Source de laboratoire seulement.** Aucun `.VSB`, `.ELF`, `.BIN` installable, ni patch de flash. Ne rien installer sur l'Electribe.

Le moteur V30 Groove n'a pas été remplacé ; huit presets, douze paramètres globaux, page PISTES masquée, quatre mini-LFO gelés.

Reproduire sous Linux / WSL avec Clang + Python 3 :

```bash
bash tests/run_md44_host.sh
bash tests/run_md43_host.sh
bash tests/build_v29_2.sh
```

Les deux firmwares d'origine n'appartiennent pas à cette archive ; leurs SHA-256 et les commandes d'audit en lecture seule se trouvent dans la passation.
