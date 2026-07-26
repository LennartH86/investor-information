# Investor Radar – Run 3/3 | Prüfung + HTML-Build + E-Mail

## Rahmenbedingungen
- Repo: `/home/user/investor-information`
- Default Branch: automatisch ermitteln
- Voraussetzung: Run 1 und Run 2 abgeschlossen und gemerged
- Dieser Run prüft Vollständigkeit, holt Fehlendes nach, baut die Website und verschickt die E-Mail

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

**Ergebnis:** Vollständige alphabetisch sortierte Liste aller erwarteten Unternehmen.

Zusätzlich für Nachholungen: Dividenden-Daten und Gesamtportfolio-Wert abrufen.

---

## Schritt 1 – Vollständigkeitsprüfung

```bash
REPO=/home/user/investor-information
DEFAULT=$(git -C $REPO symbolic-ref refs/remotes/origin/HEAD \
          | sed 's@^refs/remotes/origin/@@')
git -C $REPO checkout $DEFAULT && git -C $REPO pull origin $DEFAULT
```

Die Parqet-Unternehmensliste mit den vorhandenen `results/[0-9][0-9]_*.md` Dateien abgleichen.
Jede fehlende Datei melden.

---

## Schritt 2 – Fehlende Dateien nachholen (nur falls nötig)

Für jede fehlende Datei einen Agent mit dem Agent-Template starten (max. 6 parallel).
Die Parqet-Daten für das jeweilige Unternehmen an den Agent übergeben.

Nach Fertigstellung aller Agents:

```bash
REPO=/home/user/investor-information
DEFAULT=$(git -C $REPO symbolic-ref refs/remotes/origin/HEAD \
          | sed 's@^refs/remotes/origin/@@')
BRANCH=$(git -C $REPO rev-parse --abbrev-ref HEAD)

git -C $REPO checkout $DEFAULT
git -C $REPO pull origin $DEFAULT
git -C $REPO merge --no-ff $BRANCH -m "Run 3: Nachholung fehlender Dateien"
git -C $REPO push origin $DEFAULT
```

Wenn nichts fehlt: direkt zu Schritt 3.

---

## Schritt 3 – Website bauen

```bash
REPO=/home/user/investor-information
DEFAULT=$(git -C $REPO symbolic-ref refs/remotes/origin/HEAD \
          | sed 's@^refs/remotes/origin/@@')
git -C $REPO checkout $DEFAULT && git -C $REPO pull origin $DEFAULT

python $REPO/scripts/build_site.py

git -C $REPO add index.html
git -C $REPO commit -m "Build: Investor Radar KW$(grep '^KW:' $REPO/results/_meta.md | awk '{print $2}')"
git -C $REPO push origin $DEFAULT
```

---

## Schritt 4 – Gmail-Entwurf erstellen

Metadaten einlesen:
```bash
REPO=/home/user/investor-information
KW=$(grep   '^KW:'            $REPO/results/_meta.md | awk '{print $2}')
JAHR=$(grep '^JAHR:'          $REPO/results/_meta.md | awk '{print $2}')
VON=$(grep  '^ZEITRAUM_VON:'  $REPO/results/_meta.md | awk '{print $2}')
BIS=$(grep  '^ZEITRAUM_BIS:'  $REPO/results/_meta.md | awk '{print $2}')
WERT=$(grep '^PORTFOLIO_WERT:' $REPO/results/_meta.md | awk '{print $2}')
POS=$(grep  '^POSITIONEN:'    $REPO/results/_meta.md | awk '{print $2}')
```

Tool: `mcp__Gmail__create_draft`
**An:** `lennart.heuckendorf@gmail.com`
**Betreff:** `📊 Investor Radar KW[KW] ist online`

```
Hallo,

der wöchentliche Investor Radar für KW[KW] / [JAHR] ist fertig.

🌐 Website:
https://LennartH86.github.io/investor-information/

📁 Repository (Rohdaten):
https://github.com/LennartH86/investor-information/tree/[DEFAULT_BRANCH]/results

Recherchezeitraum: [VON] – [BIS]
Unternehmen: [POS] (dynamisch aus Parqet-Portfolio)
Portfoliowert: [WERT] EUR

Neu in dieser Version:
- Unternehmensauswahl automatisch aus deinem Parqet-Portfolio
- Portfolio-Analyse pro Unternehmen (Position, G/V, Bewertung)

Viele Grüße,
Dein Claude Code Agent
```

---

## Agent-Template (für Schritt 2 Nachholungen)

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
## Management
## Finanzielles
## Strategie & Ausblick
## Quellen

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
