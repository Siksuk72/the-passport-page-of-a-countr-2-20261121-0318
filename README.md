# The Passport Page of a Country That Isn't There

Entry for make.fun competition
`the-passport-page-of-a-countr-2-20261121-0318`.

## What it is

`main.py` (Python 3.13, Pillow only) renders one invented passport
spread — 1024×1024 PNG, under 1 MiB — to `/output/entry.png`.
Everything is drawn from code with a fixed seed: no network, no clock,
no files outside this repository.

The document is a passport of the **Republic of Valdoria**, a small
landlocked alpine republic (capital Kaldris). The holder is **Elena
Maris Voss**, born 14 MAR 1994 in Kaldris, a licensed mountain guide —
the portrait (drawn in code), the physical description (168 cm, green
eyes, auburn hair) and the occupation all belong to the same person.

- **Left page — data page:** coat of arms, bilingual headings
  (Valdorian / English), photograph, data fields, issue 12 JUN 2024 /
  expiry 11 JUN 2034, holder's signature, observations, and an ICAO
  9303 machine-readable zone with valid check digits
  (passport VD 0417823).
- **Right page — visas:** four oval border stamps in travel order,
  each with its exit stamp where the holder left:
  Ostara entry 28 JUN 2024 / exit 11 JUL, Talyria entry 12 JUL /
  exit 02 AUG, Brennar Free Port entry 03 AUG / exit 19 AUG, and
  re-entry to Valdoria 19 AUG 2024. Every stamp is dated after the
  passport's issue and none contradicts the place of issue.
- **The telling detail:** Condition 7, printed on the visas page and
  stamped "FEE PAID · 40 KORUN · GUIDE PERMIT · 19 AUG 2024" — a
  licensed guide may not take clients above 3,000 m without a second
  licensed guide (Valdorian Alpine Code, §12). That is what kind of
  place Valdoria is: a mountain state that regulates its peaks.

## Run

```sh
python3 main.py   # writes /output/entry.png (0644)
```

Run it twice and the file is byte-identical.

## License

MIT — see `LICENSE`.
