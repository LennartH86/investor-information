# Investor Radar – Betriebsanleitung für Claude Code

## Kernprinzip
Wenn der Nutzer sagt „führe alle tasks aus" oder „mache weiter" → **direkt durchlaufen, kein Stopp zwischen Tasks**.
„Stoppe hier" in den Task-Beschreibungen ist nur ein Timeout-Schutz für Einzelstarts, kein Halt bei vollständiger Ausführung.

---

## Branch
Alle Änderungen auf Branch `claude/awesome-pasteur-PaRk9` entwickeln und pushen.
Niemals auf `main` pushen ohne explizite Anweisung.

---

## Parallelisierung: Maximal 6 Agents gleichzeitig

**Falsch (zu viele → Rate Limit):**
```
Agent(Task2), Agent(Task3), ..., Agent(Task25)  # 24 auf einmal → ~50% schlagen fehl
```

**Richtig (Batches von 6):**
```
Batch A: Agent(Task2–7)   → warten bis alle fertig
Batch B: Agent(Task8–13)  → warten bis alle fertig
Batch C: Agent(Task14–19) → warten bis alle fertig
Batch D: Agent(Task20–25) → warten bis alle fertig
Task 26: Website + E-Mail
```

---

## Agent-Prompt: Kurzform Git-Push (nicht 10-zeilige Schleife)

In jedem Research-Agent-Prompt statt der langen Schleife:

```bash
cd /home/user/investor-information
git pull --rebase origin claude/awesome-pasteur-PaRk9 2>&1
git add results/XX_name.md
git commit -m "Firma: Recherche KW[XX]-[JAHR]"
for i in 1 2 3 4 5; do
  git push -u origin claude/awesome-pasteur-PaRk9 2>&1 && break
  sleep $((i*5)) && git pull --rebase origin claude/awesome-pasteur-PaRk9 2>&1
done
```

---

## Task 26 – Website: Immer per Skript, nie per Context-Lesen

**Falsch:** alle 25 .md-Dateien per `cat` in den Context laden → 74 KB Speicher verschwendet.

**Richtig:** Python-Skript `/tmp/build_site.py` generiert die HTML direkt aus den Dateien.
Das Skript liegt nicht im Repo – bei Bedarf neu schreiben (es ist kurz, ~100 Zeilen).

Kernlogik:
```python
import os, re
# Alle results/[0-9][0-9]_*.md einlesen
# Sections per Regex extrahieren: ## Aktuelle Meldungen, ## Management, etc.
# Markdown-Listen → <ul><li>, Markdown-Links → <a href>
# HTML-Template mit Dark-Theme befüllen
# → index.html schreiben
```

---

## Ablauf Task 0 (Cleanup)

```bash
git -C /home/user/investor-information pull origin claude/awesome-pasteur-PaRk9 2>&1 || true
rm -f results/*.md results/*.log index.html
mkdir -p results
touch results/.gitkeep  # Leeres Verzeichnis tracken
git -C /home/user/investor-information add -A
git -C /home/user/investor-information commit -m "Cleanup: Starte neue Recherche KW$(date +%V)-$(date +%Y)"
git -C /home/user/investor-information push -u origin claude/awesome-pasteur-PaRk9
```

Dann `results/_meta.md` schreiben und separat committen.

---

## Bekannte Stolperstellen

| Problem | Lösung |
|---|---|
| `git pull` schlägt fehl weil Branch neu | Beim allerersten Run: kein pull, direkt committen |
| Agent meldet „You've hit your limit" | Zu viele parallele Agents → Batch-Größe auf max. 6 reduzieren |
| `24_sto.md` hat doppelten Commit | Hintergrund-Agent lief parallel zu manuellem Commit → immer foreground-Agents nutzen |
| index.html doppelt generiert | Erst alle 25 Agent-Ergebnisse abwarten, dann einmal generieren |
| `cd ~/investor-information` schlägt fehl | Pfad ist `/home/user/investor-information`, nicht `~/investor-information` |

---

## Letzter Run: KW17/2026 (22.04.2026)
- Tasks 1–12: parallel (Batch 1, alle erfolgreich)
- Tasks 13–18: parallel gestartet, Rate Limit → Dateien lokal erstellt, manuell committed
- Tasks 19–25: parallel (Batch 2, alle erfolgreich)
- Task 26: Website per Python-Skript, E-Mail als Gmail-Draft erstellt
- Gesamtcommits: 30
