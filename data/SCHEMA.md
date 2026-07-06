# Theory record schema & scoring rubric

Every theory is one object in `data/theories.json`. Fields:

| field | type | notes |
|---|---|---|
| `id` | string | kebab-case slug, unique, stable. |
| `name` | string | Display name. |
| `aliases` | string[] | Other names / spellings. |
| `genre` | enum | One key from `src/taxonomy.json.genres`. |
| `year` | int | Year the theory was **formulated / first popularized** (not the year of the event it concerns). |
| `truth` | int 0–100 | Plausibility / verification. See rubric below. |
| `impact` | int 0–100 | If it were TRUE, how world-altering. See rubric. |
| `notoriety` | int 0–100 | How widely known (drives point size). |
| `summary` | string | 1–3 sentence neutral description of the claim. |
| `evidence_for` | (string \| evidence)[] | Points cited by proponents / genuine anomalies. |
| `evidence_against` | (string \| evidence)[] | Debunkings, refutations, mainstream explanation. |

An `evidence` item links a claim to the source that documents it:
`{"text": "2023 DOJ OIG report found no evidence of foul play", "source": "https://oig.justice.gov/..."}`.
Plain strings are still valid (legacy / no source yet); prefer the object form
whenever a source exists, and the `source` URL should also appear in `sources`.
| `related` | string[] | ids of thematically related theories (undirected). |
| `depends_on` | string[] | ids this theory **requires to be true** (load-bearing, directed). |
| `wikidata` | string? | Q-id if known. |
| `wikipedia` | string? | URL if known. |
| `sources` | source[] | Structured citations, see below. Open-ended — add as many as exist. |
| `research_note` | string? | Free-text provenance note (e.g. "no external coverage found; iceberg-chart lore only"). |

## `sources` entries

```json
{ "title": "Jeffrey Epstein — Wikipedia",
  "url": "https://en.wikipedia.org/wiki/Jeffrey_Epstein",
  "type": "wikipedia",
  "stance": "documents" }
```

- `type`: `wikipedia` | `news` | `academic` | `government` | `debunker` (Snopes, RationalWiki…) | `book` | `archive` | `lore` (fan wikis, iceberg explainers — for entries that exist only as internet folklore).
- `stance`: `documents` (neutral coverage of the theory's existence) | `supports` (presents evidence for the claim) | `debunks`.
- URLs must be real pages that were actually visited/seen in search results — never constructed from memory.

## Research overlays (`data/research/*.json`) — how to contribute

Base records live in `data/theories.seed.json` and `data/enriched/batch_*.json`.
**Don't edit those to add sources.** Instead drop a new file in `data/research/`
containing an array of *partial* records:

```json
[ { "id": "epstein-killed",
    "sources": [ ... ],
    "truth": 55,
    "evidence_against": ["2023 DOJ OIG report found no evidence of foul play"] } ]
```

`build.py` applies overlays on top of the base records: scalar fields
(`truth`, `notoriety`, `summary`, `wikipedia`, …) overwrite; `evidence_for`/
`evidence_against` append (deduplicated, capped at 8); `sources` append
(deduplicated by URL). Later overlay files win over earlier ones
(alphabetical order). One id can appear in many overlay files — that's the
point: research accumulates modularly, and community contributions are just
new overlay files.

## Truth rubric (X axis)
- **0–10 Debunked** — flat earth, moon-landing hoax, reptilians.
- **11–30 Fringe** — no credible evidence (chemtrails, Finland doesn't exist).
- **31–55 Contested** — real open questions / unfalsifiable (JFK second gunman, Epstein death).
- **56–75 Plausible** — strong circumstantial record (CIA & crack, Gary Webb).
- **76–90 Substantiated** — largely borne out (Operation Mockingbird scope).
- **91–100 Confirmed** — proven fact: MKUltra, Tuskegee, COINTELPRO, Gulf of Tonkin, Iran-Contra, NSA mass surveillance (PRISM), Big Tobacco, Business Plot, Operation Northwoods (proposed), Watergate.

## Impact rubric (Y axis) — *if the theory were true*
- **0–20 Trivial/local** — a single celebrity is a body double.
- **21–45 Limited** — one industry lied (still serious, bounded).
- **46–70 National/major** — a government murdered a leader; a war was started on a lie.
- **71–90 Global** — mass covert control of populations; shared history is falsified.
- **91–100 Reality-defining** — the planet, species, or nature of reality is a lie.

## Load-bearing / `depends_on`
A theory is *load-bearing* for others when many theories list it in their `depends_on`.
Example chains: `chemtrails → mass-govt-secrecy`; `qanon → deep-state → ...`.
In-degree over `depends_on` edges = how foundational a theory is (rendered larger/central in the graph view).
