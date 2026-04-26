# Investor Radar – Claude Code Runbook

## Trigger
Sobald der Nutzer eine dieser Phrasen schreibt, führe sofort **Task 0 → Tasks 1–25 → Task 26** komplett durch, ohne Rückfragen und ohne Zwischenstopps:
- „starte" / „start"
- „führe aus" / „führe claude.md aus"
- „wöchentlicher run" / „weekly run"
- „mache weiter" / „weiter"

## Sofortregeln
- Repo: `/home/user/investor-information` | Branch: `claude/admiring-maxwell-wlJWm`
- „führe alle tasks aus" / „mache weiter" → **ohne Stopp durchlaufen**
- Max **6 parallele Agents** pro Batch (sonst Rate Limit)
- Niemals auf `main` pushen

---

## Task 0 – Cleanup

```bash
REPO=/home/user/investor-information
BRANCH=claude/admiring-maxwell-wlJWm
git -C $REPO pull origin $BRANCH 2>&1 || true
rm -f $REPO/results/*.md $REPO/results/*.log $REPO/index.html
mkdir -p $REPO/results && touch $REPO/results/.gitkeep
git -C $REPO add -A
git -C $REPO commit -m "Cleanup: Starte neue Recherche KW$(date +%V)-$(date +%Y)"
git -C $REPO push -u origin $BRANCH
```

Dann `results/_meta.md` schreiben:
```
KW: [date +%V]
JAHR: [date +%Y]
DATUM: [TT.MM.YYYY]
ZEITRAUM_VON: [heute minus 7 Tage]
ZEITRAUM_BIS: [heute]
```
Committen: `git add results/_meta.md && git commit -m "Meta: Recherchezeitraum gesetzt" && git push`

---

## Tasks 1–25 – Recherche (Batches à 6)

**Ausführungsreihenfolge:**
```
Batch A (parallel): Tasks 2–7   → warten
Batch B (parallel): Tasks 8–13  → warten
Batch C (parallel): Tasks 14–19 → warten
Batch D (parallel): Tasks 20–25 → warten
Task 26: Website + E-Mail
```
*(Task 1 – Adidas – direkt im Hauptcontext erledigen, spart einen Agent-Start)*

### Agent-Prompt-Template

Jeden Agent mit diesem **kompakten Template** starten – nur die 4 Parameter `[FIRMA]`, `[TICKER]`, `[FILE]`, `[LANG]` ersetzen:

```
Investor-Radar-Recherche KW[XX]/[JAHR] | [FIRMA] ([TICKER])
Zeitraum: [VON]–[BIS] | Sprache: [LANG]
Datei: /home/user/investor-information/results/[FILE]

1. Führe genau 5 WebSearches durch:
   - "[FIRMA] News [Monat] [JAHR]"
   - "[FIRMA] Pressemitteilung/press release [Monat] [JAHR]"
   - "[FIRMA] CEO Interview [JAHR]"
   - "[FIRMA] Quartalsergebnis/quarterly results forecast [JAHR]"
   - "[FIRMA] Übernahme/acquisition investment [JAHR]"

2. Schreibe [FILE] mit diesen Abschnitten (Markdown-Bullets):
   # [FIRMA] ([TICKER])
   _KW[XX] / [JAHR] | Zeitraum: [VON] – [BIS]_
   ## Aktuelle Meldungen
   ## Management
   ## Finanzielles
   ## Strategie & Ausblick
   ## Quellen
   Leere Abschnitte: "Keine aktuellen Informationen gefunden."

3. Git push (mit Retry):
   REPO=/home/user/investor-information; B=claude/admiring-maxwell-wlJWm
   git -C $REPO pull --rebase origin $B 2>&1
   git -C $REPO add results/[FILE]
   git -C $REPO commit -m "[FIRMA]: Recherche KW[XX]-[JAHR]"
   for i in 1 2 3 4 5; do git -C $REPO push -u origin $B 2>&1 && break; sleep $((i*5)); git -C $REPO pull --rebase origin $B 2>&1; done
```

### Unternehmensliste

| Task | File | Firma | Ticker | Lang |
|------|------|-------|--------|------|
| 1 | 01_adidas.md | Adidas | ADS.DE | DE+EN |
| 2 | 02_allianz.md | Allianz | ALV.DE | DE |
| 3 | 03_basf.md | BASF | BAS.DE | DE |
| 4 | 04_biontech.md | BioNTech | BNTX | DE+EN |
| 5 | 05_daikin.md | Daikin | 6367.T | EN |
| 6 | 06_deutsche_post.md | Deutsche Post / DHL Group | DHL.DE | DE+EN |
| 7 | 07_energiekontor.md | Energiekontor | EKT.DE | DE |
| 8 | 08_equinor.md | Equinor | EQNR | EN |
| 9 | 09_fraport.md | Fraport | FRA.DE | DE |
| 10 | 10_heidelberg_materials.md | Heidelberg Materials | HEIG.DE | DE+EN |
| 11 | 11_hochtief.md | Hochtief | HOT.DE | DE |
| 12 | 12_iberdrola.md | Iberdrola | IBE.MC | EN+ES |
| 13 | 13_ionos.md | Ionos | IOS.DE | DE |
| 14 | 14_italmobiliare.md | Italmobiliare | ITM.MI | EN+IT |
| 15 | 15_jumbo.md | Jumbo | BELA.AT | EN |
| 16 | 16_lvmh.md | LVMH | MC.PA | EN+FR |
| 17 | 17_merck.md | Merck KGaA (nicht US-Merck) | MRK.DE | DE+EN |
| 18 | 18_munich_re.md | Munich Re | MUV2.DE | DE+EN |
| 19 | 19_mutares.md | Mutares | MUX.DE | DE |
| 20 | 20_novo_nordisk.md | Novo Nordisk | NOVO-B.CO | EN |
| 21 | 21_rio_tinto.md | Rio Tinto | RIO.L | EN |
| 22 | 22_shell.md | Shell | SHEL.L | EN |
| 23 | 23_sixt.md | Sixt | SIX2.DE | DE |
| 24 | 24_sto.md | Sto SE & Co. KGaA | STO3.DE | DE |
| 25 | 25_vonovia.md | Vonovia | VNA.DE | DE |

---

## Task 26 – Website + E-Mail

### Website
```bash
python3 /home/user/investor-information/scripts/build_site.py
REPO=/home/user/investor-information; B=claude/awesome-pasteur-PaRk9
git -C $REPO add index.html
git -C $REPO commit -m "Website: Investor Radar KW[XX]-[JAHR]"
git -C $REPO push -u origin claude/admiring-maxwell-wlJWm
```

### E-Mail (Gmail Draft)
An: `lennart.heuckendorf@gmail.com`
Betreff: `📊 Investor Radar KW[XX] ist online`
```
Hallo,

der wöchentliche Investor Radar für KW[XX] / [JAHR] ist fertig.

🌐 Website:
https://LennartH86.github.io/investor-information/

📁 Repository (Rohdaten):
https://github.com/LennartH86/investor-information/tree/main/results

Recherchezeitraum: [VON] – [BIS]
Unternehmen: 25

Viele Grüße,
Dein Claude Code Agent
```
Tool: `mcp__Gmail__create_draft`

---

## Fehlerverhalten

| Fehler | Aktion |
|--------|--------|
| Agent „You've hit your limit" | Datei lokal prüfen (`ls results/`), fehlende manuell nachholen |
| Push rejected | `git pull --rebase` dann erneut pushen |
| Datei lokal da aber ungetrackt | `git add FILE && git commit && git push` |
| `~/investor-information` not found | Pfad ist `/home/user/investor-information` |

---

## Laufprotokoll

| Run | KW | Datum | Commits | Anmerkungen |
|-----|----|-------|---------|-------------|
| 1 | KW17 | 22.04.2026 | 30 | Erstrun; 13 Agents Rate-Limited; Batch-Größe zu groß (24) |
| 2 | KW17 | 26.04.2026 | 29 | Erster automatischer Run; 2× ins 5h-Token-Limit gelaufen; alle 25 Dateien vorhanden |
| 3 | KW17 | 26.04.2026 | 2 | Completion-Run: Task 26 (Website + E-Mail) nachgeholt; Branch auf claude/admiring-maxwell-wlJWm umgestellt |
