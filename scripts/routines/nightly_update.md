# Investor Radar – Nightly Update

## Rahmenbedingungen
- Repo: `/home/user/investor-information`
- Direkt auf Default Branch arbeiten
- Max. **6 parallele Agents** (Rate-Limit-Schutz)
- Pro Durchlauf **bis zu 10** Unternehmen aktualisieren (älteste zuerst)
- Website aktualisiert sich automatisch (client-side, kein Build nötig)
- Dateinamen: `results/[slug].md` (kein Nummern-Präfix)

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

**Ergebnis:** Liste aktiver Einzelaktien, alphabetisch nach Name sortiert.

Zusätzlich Dividenden-Daten und Gesamtportfolio-Wert abrufen:
```
mcp__Parqet__parqet_query_portfolio view: "dividends" portfolioIds: "63c4422082677c2e24f03183"
mcp__Parqet__parqet_query_portfolio view: "overview" portfolioIds: "63c4422082677c2e24f03183"
```

**Für jede Aktie berechnen:**
- Portfolioanteil = `currentValue / Gesamtportfoliowert * 100`
- Dividenden aus dem Dividenden-Datensatz zuordnen (falls vorhanden)

**Slug-Erstellung:** Firmenname in Kleinbuchstaben, Leerzeichen → `_`, Sonderzeichen entfernen. Beispiele: "Adidas" → `adidas`, "DHL Group" → `dhl_group`, "GE Vernova" → `ge_vernova`

---

## Schritt 1 – Bestandsabgleich + Aufräumen

Vorhandene `.md` Dateien in `results/` auflisten und deren letztes Änderungsdatum ermitteln:

```bash
REPO=/home/user/investor-information
for f in $REPO/results/*.md; do
  [ -f "$f" ] || continue
  name=$(basename "$f")
  [[ "$name" == _* ]] && continue
  date=$(git -C $REPO log -1 --format="%ci" -- "results/$name" 2>/dev/null || echo "unknown")
  echo "$name $date"
done
```

**Abgleich mit Parqet-Liste:**
- Für jede Datei prüfen: Gehört der Slug zu einem aktiven Parqet-Unternehmen?
- **Dateien ohne Parqet-Zuordnung löschen** (Unternehmen nicht mehr im Portfolio)
- Falls Dateien gelöscht wurden:

```bash
REPO=/home/user/investor-information
git -C $REPO add -u results/
git -C $REPO commit -m "Cleanup: Nicht mehr im Portfolio"
git -C $REPO push origin HEAD
```

**Migrations-Hinweis:** Falls alte Dateien mit Nummern-Präfix existieren (`[0-9][0-9]_*.md`), diese in das neue Format umbenennen (Präfix entfernen) und committen.

---

## Schritt 2 – Zu aktualisierende Unternehmen auswählen

Alle Parqet-Unternehmen nach Priorität sortieren:
1. **Fehlende Dateien** (noch keine `.md` vorhanden) → höchste Priorität
2. **Älteste Dateien** (längster Abstand seit letztem Update) → nach Alter sortiert

Die obersten **10** auswählen.

---

## Schritt 3 – Recherche durchführen

**Ablauf:**
1. Erstes Unternehmen direkt im Hauptkontext recherchieren (spart Agent-Start)
2. Dann Batches à 6 Agents parallel starten
3. Warten bis ein Batch fertig ist, dann den nächsten starten

Jedem Agent die Parqet-Daten für sein Unternehmen mitgeben.

---

## Agent-Template

Jeden Sub-Agent mit diesem Prompt starten – Variablen `[...]` ersetzen:

```
Investor-Radar | [FIRMA] ([TICKER])
Aktualisierung: [DATUM] | Zeitraum: [VON] – [BIS] | Sprache: [LANG]
Datei: /home/user/investor-information/results/[SLUG].md

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
_Aktualisiert: [DATUM] | Zeitraum: [VON] – [BIS]_

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

VARIABLEN:
- [DATUM] = heutiges Datum (TT.MM.YYYY)
- [VON] = heute minus 7 Tage (TT.MM.YYYY)
- [BIS] = heute (TT.MM.YYYY)
- [MONAT] = aktueller Monatsname
- [JAHR] = aktuelles Jahr

GIT PUSH – mit Retry-Logik:
REPO=/home/user/investor-information
git -C $REPO pull --rebase origin HEAD 2>&1
git -C $REPO add results/[SLUG].md
git -C $REPO commit -m "[FIRMA]: Aktualisierung [DATUM]"
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
