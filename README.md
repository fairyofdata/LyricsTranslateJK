<!-- Source: README_KR.md (Korean is the source; English and Japanese are translations) · synced 2026-11-24 -->

# LyricsTranslateJK

[English](README.md) · [한국어](README_KR.md) · [日本語](README_JP.md)

**A Japanese↔Korean lyric adaptation tool that keeps the sound.**

It looks for lyrics that sound like the original and still make sense as a work. This is adaptation, not translation: the words have to sit on the same melody, so syllable and mora counts are hard constraints.

```
constraint  hard constraint  syllable/mora count fits the slot range   ← if not, it is not a candidate
axis 1      phon             how close to the sound of the original
axis 2      semantic_work    fits the world and theme of the work
knob        adaptation rate  what % is actually moved into the target language
diagnostic  semantic_line    how faithful to that particular line
```

There is no weighted sum and no meaning floor. **The Pareto front and the knob do that job.**

## Status

**Planning stage.** Implementation has not started. A reference corpus of 14 songs (ja2ko 12 · ko2ja 2) is loaded locally (texts are not published, D6), and those twelve songs gave first answers to branch points A and B — [D39](docs/DECISIONS.md).

| Document | Contents |
|---|---|
| [docs/DIGEST.md](docs/DIGEST.md) | **One-page summary** — philosophy, axes, constants, unverified assumptions. Read this first |
| [docs/PLAN.md](docs/PLAN.md) | Philosophy, system structure, evaluation, research questions, data, schedule, risks |
| [docs/SPEC.md](docs/SPEC.md) | Slot representation, transfer tables (batchim, kanji, entering tone), phonology and IPA, metrics, generation, corpus |
| [docs/DECISIONS.md](docs/DECISIONS.md) | 38 settled decisions and 11 reversed ones |
| [docs/INTAKE.md](docs/INTAKE.md) | **Intake format** — how lyrics should be collected |
| [docs/HANDOFF.md](docs/HANDOFF.md) | **Handover** — repository layout, how to grow the corpus, common pitfalls |
| [tools/](tools/) | Loading and aggregation code. No lyrics inside |

Lyrics, audio, melodies and comment texts are not redistributed (D6). What is published: code, rule tables, distance functions, abstract features, hashes and evaluation scripts. The loaded texts stay local in `data/lyrics/`.

(The detailed documents under `docs/` are in Korean.)

## Philosophy

| | Principle |
|---|---|
| 1 | Sound reaches the ear first |
| 2 | **Meaning serves the work, not the line** |
| 3 | Take what is free — where sound and meaning overlap, look it up instead of searching |
| 4 | Do not touch what cannot be replaced |
| 5 | **Do not force a fit** — a bad sound-alike is worse than none |

## Why Japanese↔Korean

The two languages share three resources. **Phonemes** [ɯ]·[ɕ]·[tɕ]·[ɾ]·[ŋ] — the unrounded high vowel [ɯ] (Japanese `ウ`, Korean `ㅡ`) in particular has no counterpart against English or Chinese. **Syllable structure** — final consonants (batchim) and the special morae (ン·ッ·ー) have paths to each other. And **vocabulary** — in Sino-Japanese/Sino-Korean words and Western loanwords, both languages read the same characters with their own sounds.

The third is the key. `残酷` is *zankoku* and *janhok* — **it carries sound and meaning at once.** There is no trade-off there; a dictionary lookup settles it, no search needed.

## Four emission actions

A line is split into word units and each span gets one action. **The combination of assignments is the spectrum.**

| | What it does |
|---|---|
| `keep` | Leave the original word as is — where its symbolism cannot be replaced |
| `sino` | Read the same kanji with the target language's sound |
| `mimic` | Approximate the sound on a phoneme lattice |
| `render` | Generate from meaning and fit it to the slot |

The prior over assignments comes from **morphology**, not prosody — Sino words lean to `sino`·`keep`, native content words to `mimic`·`render`, grammatical morphemes to `render` (each language's grammar forces it).

## Why an LLM cannot simply do this

An LLM cannot "adapt this so it sounds similar". **It cannot measure the phoneme sequence of its own output.** It does not compute IPA while emitting tokens, so it cannot aim at phonetic similarity.

So the order is reversed — instead of translating and then checking the sound, **lay down the sound first and find what makes sense on top of it.** The LLM is used only as the `render` generator and as a corrector.

```
source line + work context + adaptation-rate range
  ├─① phonological analysis → IPA
  ├─② slot template extraction        syllable/mora count range
  ├─③ morphological type → assignment candidates
  ├─④ generation per action           lookup / lattice / LLM samples
  ├─⑤ lattice → word sequence         dictionary lattice + multi-objective beam   ★ the hard part
  ├─⑥ LLM correction → re-check       drop anything that breaks a constraint (closed loop)
  └─⑦ Pareto front + anchors + knee
```

## The output is not a single answer

The two axes really do conflict. Where to compromise depends on the song and the use, which the tool cannot know, so it returns N candidates with their three values.

The coordinate system is set by **computed anchors**, not by a reference — the sound-alike ceiling (the highest possible sound similarity), the MT ceiling (the meaning you get by giving up sound), and keeping the original (adaptation rate 0). They are computed for every line, so they stand even in real use where there is no reference. The default pick is the **knee of the front**, with no hand-set constants.

## No audio needed

The default path works from syllable/mora templates derived from the source lyrics. Audio transcription and synthesis-plus-ASR evaluation are **optional layers**.

## Data

No training data is needed. Nothing is learned from pairs; the search runs on phonological rules, dictionaries and distance functions, and only public pretrained models are used.

The references are **fan covers** — professional adapters have never attempted sound-first adaptation, so their work does not fit the setup. Fan covers are sung over the original audio, so the melody is identical by definition, and one song often has several covers with different aims, giving several points on the spectrum. **Comments that point at a specific correspondence** become human labels for "this correspondence works".

Lyrics, audio, melodies and comment texts are not redistributed. What is published: code, rule tables, distance functions, abstract features, hashes and evaluation scripts.

## License

Code: [MIT](LICENSE). Lyrics and other third-party material quoted in analysis belong to their rights holders and are not covered by this license.
