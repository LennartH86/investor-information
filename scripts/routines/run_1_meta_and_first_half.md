# Investor Radar – Run 1/3 | Meta + Portfolio + Erste Hälfte

## Rahmenbedingungen
- Repo: `/home/user/investor-information`
- Branch: wird automatisch von Claude Code vergeben (`claude/...`)
- Max. **6 parallele Agents** (Rate-Limit-Schutz)
- Token-Budget: sparsam planen – Gesamtablauf vorausdenken
- Branch muss im Abschluss auf Default Branch gemerged werden

---

## Schritt 0 – Parqet-Portfolio abfragen

Portfolio-Daten abrufen mit `mcp__Parqet__parqet_query_portfolio`:
```
view: "holdings"
portfolioIds: "63c4422082677c2e24f03183"
assetType: "security"
limit: 100
sortBy: "name"
```

**Filtern – diese Holdings ausschließen:**
- ETFs: Namen die "ETF", "UCITS", "iShares", "SPDR" oder "Fidelity" enthalten
- Tote Positionen: LUKOIL (ADR), Orion Properties

**Ergebnis:** Liste aktiver Einzelaktien, alphabetisch nach Name sortiert.
Den **Gesamtwert** aller Positionen (inkl. ETFs + Cash) merken.

Zusätzlich Dividenden-Daten abrufen:
```
mcp__Parqet__parqet_query_portfolio
view: "dividends"
portfolioIds: "63c4422082677c2e24f03183"
```

Dann: Gesamtportfolio-Wert abfragen:
```
mcp__Parqet__parqet_query_portfolio
view: "overview"
portfolioIds: "63c4422082677c2e24f03183"
```

**Für jede Aktie berechnen:**
- Portfolioanteil = `currentValue / Gesamtportfoliowert * 100`
- Dividenden aus dem Dividenden-Datensatz zuordnen (falls vorhanden)

---

## Schritt 1 – Metadaten schreiben

Datei `results/_meta.md` anlegen:

```
KW: [aktuelle Kalenderwoche]
JAHR: [aktuelles Jahr]
DATUM: [TT.MM.YYYY]
ZEITRAUM_VON: [heute minus 7 Tage, Format TT.MM.YYYY]
ZEITRAUM_BIS: [heute, Format TT.MM.YYYY]
PORTFOLIO_WERT: [Gesamtportfoliowert gerundet, z.B. 152.345]
POSITIONEN: [Anzahl aktiver Einzelaktien nach Filterung]
```

```bash
git add results/_meta.md
git commit -m "Meta: Recherchezeitraum KW[XX]-[JAHR] + Portfolio"
git push
```

---

## Schritt 2 – Alte Ergebnisdateien entfernen

Alle `results/[0-9][0-9]_*.md` Dateien löschen (NICHT `_meta.md`), damit keine veralteten Dateien von der Vorwoche übrig bleiben, falls sich das Portfolio geändert hat.

```bash
find results/ -name '[0-9][0-9]_*.md' -delete
git add -u results/
git commit -m "Clean: Alte Ergebnisse entfernt"
git push
```

---

## Schritt 3 – Erste Hälfte der Unternehmen recherchieren

Die alphabetisch sortierte Unternehmensliste halbieren.
Run 1 bearbeitet die **erste Hälfte** (bei ungerader Zahl die größere Hälfte).

Dateinamen: `results/[NN]_[slug].md` – Nummern (NN) werden global vergeben (01, 02, 03...) über die gesamte alphabetisch sortierte Liste, nicht nur über die Hälfte.

**Ablauf:**
1. Erstes Unternehmen direkt im Hauptkontext recherchieren (spart Agent-Start)
2. Dann Batches à 6 Agents parallel starten
3. Warten bis ein Batch fertig ist, dann den nächsten starten

Jedem Agent die Parqet-Daten für sein Unternehmen mitgeben.

---

## Schritt 4 – Merge in Default Branch

```bash
REPO=/home/user/investor-information
BRANCH=$(git -C $REPO rev-parse --abbrev-ref HEAD)
DEFAULT=$(git -C $REPO symbolic-ref refs/remotes/origin/HEAD \
          | sed 's@^refs/remotes/origin/@@')

git -C $REPO checkout "$DEFAULT"
git -C $REPO pull origin "$DEFAULT"
git -C $REPO merge --no-ff "$BRANCH" -m "Run 1: Meta + Erste Hälfte (KW$(date +%V))"
git -C $REPO push origin "$DEFAULT"
```

---

## Agent-Template

Jeden Sub-Agent mit diesem Prompt starten – Variablen `[...]` ersetzen:

```
Investor-Radar KW[XX]/[JAHR] | [FIRMA] ([TICKER])
Zeitraum: [VON] – [BIS] | Sprache: [LANG]
Datei: /home/user/investor-information/results/[FILE]

PORTFOLIO-DATEN für diese Position:
- Position: [SHARES] Aktien
- Kaufkurs (Ø): [PURCHASE_PRICE] EUR
- Aktueller Kurs: [CURRENT_PRICE] EUR
- Marktwert: [MARKET_VALUE] EUR
- Unrealisierter G/V: [UNREALIZED_GAIN] EUR ([UNREALIZED_RETURN]%)
- Portfolioanteil: [ALLOCATION]%
- Erster Kauf: [EARLIEST_ACTIVITY]
- Dividenden erhalten: [DIVIDENDS] EUR (0 falls keine)

RECHERCHE – genau 5 Web-Suchen:
1. "[FIRMA] News [Monat] [JAHR]"
2. "[FIRMA] Pressemitteilung / press release [Monat] [JAHR]"
3. "[FIRMA] CEO Interview [JAHR]"
4. "[FIRMA] Quartalsergebnis / quarterly results [JAHR]"
5. "[FIRMA] Übernahme / acquisition / investment [JAHR]"

DATEI SCHREIBEN – exakt dieses Markdown-Format:

# [FIRMA] ([TICKER])
_KW[XX] / [JAHR] | Zeitraum: [VON] – [BIS]_

## Portfolio-Analyse
- **Position:** [SHARES] Aktien
- **Kaufkurs (Ø):** [PURCHASE_PRICE] EUR
- **Aktueller Kurs:** [CURRENT_PRICE] EUR
- **Marktwert:** [MARKET_VALUE] EUR
- **Unrealisierter G/V:** [+/-GAIN] EUR ([RETURN]%)
- **Portfolioanteil:** [ALLOCATION]%
- **Dividenden erhalten:** [DIVIDENDS] EUR
- **Bewertung:** [1-2 Sätze basierend auf der Recherche: aktuelle Bewertung (KGV/KBV falls verfügbar), Dividendenrendite, Kursentwicklung vs. Kaufkurs, und ob Halten/Aufstocken/Reduzieren sinnvoll erscheint.]

## Aktuelle Meldungen
[Bullet Points mit aktuellen Nachrichten]

## Management
[Bullet Points zu Management-Themen]

## Finanzielles
[Bullet Points zu Finanzkennzahlen]

## Strategie & Ausblick
[Bullet Points zu Strategie und Ausblick]

## Quellen
[Bullet Points mit Links]

Leere Abschnitte mit: "Keine aktuellen Informationen gefunden."

GIT PUSH – mit Retry-Logik:
REPO=/home/user/investor-information
git -C $REPO pull --rebase origin HEAD 2>&1
git -C $REPO add results/[FILE]
git -C $REPO commit -m "[FIRMA]: Recherche + Portfolio KW[XX]-[JAHR]"
for i in 1 2 3 4 5; do
  git -C $REPO push -u origin HEAD 2>&1 && break
  sleep $((i*5))
  git -C $REPO pull --rebase origin HEAD 2>&1
done
```

---

## Sprach-Zuordnung

Sprache pro Unternehmen anhand des Tickers bestimmen:
- `.DE` → DE (deutsch)
- `.PA`, `.MC` → EN + Landessprache
- `.MI` → EN+IT
- `.AT` (Griechenland) → EN
- `.T` (Japan) → EN
- `.CO` (Dänemark) → EN
- `.L` (London) → EN
- US-Ticker (kein Punkt) → EN
- NO-Prefix → EN
- Sonderfälle: BioNTech → DE+EN, DHL Group → DE+EN, Merck KGaA (NICHT US-Merck) → DE+EN
