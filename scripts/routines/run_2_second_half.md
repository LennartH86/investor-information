# Investor Radar – Run 2/3 | Zweite Hälfte

## Rahmenbedingungen
- Repo: `/home/user/investor-information`
- Direkt auf Default Branch arbeiten (kein Feature Branch)
- Max. **6 parallele Agents** (Rate-Limit-Schutz)
- Voraussetzung: Run 1 abgeschlossen
- Website aktualisiert sich automatisch (client-side, kein Build nötig)

---

## Schritt 0 – Default Branch auschecken + Parqet-Portfolio abfragen

```bash
REPO=/home/user/investor-information
DEFAULT=$(git -C $REPO remote show origin | grep 'HEAD branch' | awk '{print $NF}')
git -C $REPO checkout "$DEFAULT"
git -C $REPO pull origin "$DEFAULT"
```

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

Zusätzlich Dividenden-Daten und Gesamtportfolio-Wert abrufen:
```
mcp__Parqet__parqet_query_portfolio view: "dividends" portfolioIds: "63c4422082677c2e24f03183"
mcp__Parqet__parqet_query_portfolio view: "overview" portfolioIds: "63c4422082677c2e24f03183"
```

**Ergebnis:** Gleiche alphabetisch sortierte Liste wie Run 1.
Portfolioanteil pro Aktie berechnen: `currentValue / Gesamtportfoliowert * 100`

---

## Schritt 1 – Feststellen welche Dateien fehlen

```bash
REPO=/home/user/investor-information
ls $REPO/results/[0-9][0-9]_*.md
```

Die alphabetisch sortierte Gesamtliste aus Schritt 0 mit den vorhandenen Dateien abgleichen.
Alle Unternehmen ohne Ergebnisdatei müssen in diesem Run recherchiert werden.
(Das sollte die zweite Hälfte der Liste sein, kann aber auch fehlende aus Run 1 enthalten.)

---

## Schritt 2 – Fehlende Unternehmen recherchieren

**Ablauf:**
1. Erstes fehlendes Unternehmen direkt im Hauptkontext recherchieren
2. Dann Batches à 6 Agents parallel starten
3. Warten bis ein Batch fertig ist, dann den nächsten starten

Dateinamen: `results/[NN]_[slug].md` – die Nummern (NN) entsprechen der Position in der alphabetisch sortierten Gesamtliste (gleiche Nummerierung wie Run 1).

Jedem Agent die Parqet-Daten für sein Unternehmen mitgeben.

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
