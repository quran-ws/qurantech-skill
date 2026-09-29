# Verse Recognition (Audio-to-Ayah Identification)

## Table of Contents
- [Overview](#overview)
- [Mapping Results Through the Blocks](#mapping-results-through-the-blocks)
- [Tilawa](#tilawa)
- [Install and Assets](#install-and-assets)
- [Platform Integration](#platform-integration)
- [Verse Events](#verse-events)
- [Alternate Engine: FastConformer](#alternate-engine-fastconformer)
- [Models and Benchmarks](#models-and-benchmarks)
- [Experiment Landscape](#experiment-landscape)
- [Best Practices](#best-practices)

## Overview

Verse recognition identifies which surah and ayah a person is reciting from audio. The output is structured, not a transcript: `{surah, ayah, ayah_end, score}`. Uses:

- **Mushaf auto-follow:** scroll to the verse being recited
- **Memorization validation:** check that the user recited the expected verse
- **Live verse identification:** show the verse while someone recites nearby
- **Hifz testing:** automated oral examination

## Mapping Results Through the Blocks

Recognition output is a key plus a score. Route it through the Quran.ws blocks ([blocks.md](../blocks.md)) rather than ad hoc code:

- **Matching and normalization: `quran-text`.** Match decoded text against the recognized riwayah's own text. Use its plain and search keys (`plain`, `rasm`, and the word index), not display spellings, as matching keys. Its shared word numbers let you report position at word level and compare across riwayat.
- **Counting system: results carry one.** A result `{surah, ayah, ayah_end}` is only meaningful with the counting system of the reference text it was matched against. Never assume Hafs numbering: store `{surah, ayah, counting}`, and use `qiraat-ayah-map` to convert to the app's active riwayah (splits and merges yield ranges, not one ayah). `quran-text` also ships `data/ayah-map.json` for its seven bundled editions.
- **Highlight: `quran-svg` and `quran-svg-elements`.** Turn the (converted) ayah range into ayah polygons on the page (`quran-svg`) or word keys `surah:ayah:word` (`quran-svg-elements`, Hafs only; `quran-engine` on native).
- **Model and licence are outside the blocks.** Tilawa below is a third-party fallback for the recognition step itself.

## Tilawa

**Repository:** `github.com/yazinsai/tilawa` (formerly `offline-tarteel`; old URLs redirect)
**Supported integration:** `@tilawa/core` (v0.3.x on npm). Pure TypeScript, zero native dependencies; you inject the ONNX runtime for your platform.
**Licences:** package code is MIT. The default Zipformer model and the phoneme corpus are NPL-1.2 (non-commercial, share-alike). FastConformer assets are NVIDIA CC-BY-4.0 (`nvidia/stt_ar_fastconformer_hybrid_large_pcd_v1.0`). Check the licence of the exact model before shipping a commercial app; see the repo `NOTICE.md`.

Give it 16 kHz mono audio and it returns `surah:ayah`, fully on-device (web, Node, React Native), with no network at inference time. Two engines ship:

- **Zipformer (default):** streaming Zipformer2-CTC over a 251-token tajweed-phoneme vocabulary, with a word-level tracker. Use it for live recitation.
- **FastConformer:** text CTC. Use it for one-shot transcription, a raw Arabic transcript, or when you need non-NPL assets.

Pipeline: 16 kHz mono audio, then features and ONNX inference (CTC log-probabilities), then greedy CTC decode, then matching against the whole Quran (phoneme index and alignment for Zipformer; Levenshtein matching for FastConformer). Multi-verse spans are scored as well as single verses.

Figures in this file are from `lab/EXPERIMENTS.md` and the repo README as read on 2026-09-29. Releases change them; re-check before quoting numbers in a design.

## Install and Assets

```bash
npm i @tilawa/core
# plus the runtime for your platform (you own this dependency):
npm i onnxruntime-web            # browser / WASM
npm i onnxruntime-node           # Node
npm i onnxruntime-react-native   # React Native
```

Default-engine assets (release v0.3.0):

```bash
base=https://github.com/yazinsai/tilawa/releases/download/v0.3.0
curl -L -O "$base/zipformer_interp_gentle_a05.int8.onnx"  # 66 MB
curl -L -O "$base/zipformer_quran.json"                    # 5.5 MB, NPL-1.2
# optional: Arabic text on verse_match events (release v0.2.0, 3.19 MB)
curl -L -O https://github.com/yazinsai/tilawa/releases/download/v0.2.0/quran.json
```

The model I/O manifest is bundled (`DEFAULT_ZIPFORMER_IO`). `quran.json` is display text only; matching works without it.

## Platform Integration

### Browser (ONNX Runtime Web)

```ts
import * as ort from "onnxruntime-web";
import { createRecognitionSession } from "@tilawa/core";

// A bundler that does not copy *.wasm files needs:
// ort.env.wasm.wasmPaths = "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.24.2/dist/";

const session = await createRecognitionSession({
  ort,
  model: () => fetch("/zipformer_interp_gentle_a05.int8.onnx").then((r) => r.arrayBuffer()),
  corpus: () => fetch("/zipformer_quran.json").then((r) => r.json()),
  quran: () => fetch("/quran.json").then((r) => r.json()), // optional
  onEvent: (msg) => {
    if (msg.type === "verse_match") console.log(`${msg.surah}:${msg.ayah}`, msg.verse_text);
  },
});

for await (const chunk of micChunks) await session.feed(chunk);
const final = await session.stop();
session.reset();
```

Passing `ort` and `model` selects the provider (`["wasm"]` under onnxruntime-web, `["cpu"]` under onnxruntime-node). On web the library sets `ort.env.wasm.numThreads = 1` unless you set it, because threaded WASM init hangs in workers without COOP/COEP headers.

### Node

```ts
import { readFile } from "node:fs/promises";
import * as ort from "onnxruntime-node";
import { createRecognitionSession } from "@tilawa/core";

const session = await createRecognitionSession({
  ort,
  model: () => readFile("zipformer_interp_gentle_a05.int8.onnx"),
  corpus: async () => JSON.parse(await readFile("zipformer_quran.json", "utf8")),
  quran: async () => JSON.parse(await readFile("quran.json", "utf8")),
  onEvent: (msg) => {
    if (msg.type === "verse_match") console.log(`${msg.surah}:${msg.ayah}`);
  },
});

const CHUNK = Math.round(0.3 * 16000); // 300 ms, the size the benchmarks use
for (let i = 0; i < pcm16k.length; i += CHUNK) {
  await session.feed(pcm16k.subarray(i, i + CHUNK));
}
const final = await session.stop();
session.reset();
```

### React Native

React Native cannot pass the model to ORT as an `ArrayBuffer`. Bundle the `.onnx` as an asset, copy it to the documents directory, create the session from the path, and pass it in with the runtime's `Tensor`:

```ts
import * as ort from "onnxruntime-react-native";
import { createZipformerSession } from "@tilawa/core";

const session = await createZipformerSession({
  session: await ort.InferenceSession.create(modelPath),
  Tensor: ort.Tensor,
  corpus: () => loadJsonAsset("zipformer_quran.json"),
  quran: () => loadJsonAsset("quran.json"),
});
```

Walkthrough: `packages/core/examples/react-native.md` in the repo.

### Python

`@tilawa/core` is the supported integration path. The Python code under `lab/` is a benchmark harness (package name still `offline-tarteel`, `pyproject.toml` in `lab/`), not a published API. For a Python backend, run the ONNX model with `onnxruntime` and port the steps above, or call a Node service.

## Verse Events

Both engines emit the same event union via `onEvent` and as the return value of `feed()` and `stop()`:

| `msg.type` | Meaning | Key fields |
|---|---|---|
| `verse_match` | Confident match for the current verse | `surah`, `ayah`, `verse_text`, `confidence`, `surrounding_verses` |
| `verse_candidate` | Ranked candidates before lock-in | `candidates[]`, `stable`, `final_flush` |
| `word_progress` | Word-level alignment within a verse | `surah`, `ayah`, `word_index`, `total_words`, `matched_indices` |
| `raw_transcript` | Accumulated transcript so far | `text`, `confidence` |
| `final_sequence` | Ordered verse sequence when recitation ends | `verses[]`, `confidence` |

`createZipformerSession` options that matter: `minWordFraction` (default 0.5, share of an ayah's words that must land), `enableFallback` (default true, whole-ayah search when nothing locked), `tailSeconds` (default 2.0, silence appended by `stop()` to flush the CTC tail).

## Alternate Engine: FastConformer

Assets from release v0.2.0: `fastconformer_full_mixed.onnx` (88 MB), `vocab.json`, `quran_ctc_tokens.json`, `quran.json` (3.19 MB). The v0.1.0 models (`fastconformer_ar_ctc_q8.onnx`, `fastconformer_phoneme_q8.onnx`, 131 MB each) are superseded. Preprocessing is inside the graph, so you feed raw 16 kHz audio and need no mel code.

You write a `SessionRunner` that owns `ort`, then pass it to `createTilawaSession`:

```ts
import * as ort from "onnxruntime-web";
import { createTilawaSession, type SessionRunner } from "@tilawa/core";

async function createWebSessionRunner(modelBuffer: ArrayBuffer): Promise<SessionRunner> {
  const session = await ort.InferenceSession.create(modelBuffer, { executionProviders: ["wasm"] });
  return {
    async run(audio) {
      const input = new ort.Tensor("float32", audio, [1, audio.length]);
      const length = new ort.Tensor("int64", BigInt64Array.from([BigInt(audio.length)]), [1]);
      const results = await session.run({ audio_signal: input, length });
      const output = results[session.outputNames[0]];
      const [, timeSteps, vocabSize] = output.dims as number[];
      return { logprobs: output.data as Float32Array, timeSteps, vocabSize };
    },
  };
}

const session = createTilawaSession(await createWebSessionRunner(modelBuffer), {
  vocab,
  quranCtcTokens,
  quran,
});
const pred = await session.transcribe(audioFloat32);
// { surah, ayah, ayah_end, score, transcript }
```

`audio` passed to `SessionRunner.run` is borrowed: treat it as read-only. FastConformer has no `stop()`; it finalizes on trailing silence. Wrap it with `createRecognitionSession({ engine: "fastconformer", runner, assets })` for the same `feed()` / `stop()` / `reset()` surface.

Source files in the repo: `packages/core/src/` holds `text-ctc-decode.ts`, `quran-db.ts`, `normalizer.ts`, and `recitation/` (including `fbank.ts`). The demo worker code is under `web/frontend/src/worker/`. Paths change between releases; verify in the repo.

## Models and Benchmarks

Corpora: **v1** (53 samples: user, EveryAyah, RetaSy crowd), **v2** (43), **v3** (256). Recall is the fraction of expected verses found; ExactSetAcc means the emitted set equals the expected set. Source: `lab/EXPERIMENTS.md`, read 2026-09-29.

| | Zipformer (default) | FastConformer |
|---|---|---|
| File | `zipformer_interp_gentle_a05.int8.onnx` (66 MB) | `fastconformer_full_mixed.onnx` (88 MB) |
| Mode | Streaming, 300 ms chunks | Full-file batch |
| Result | v1 100% (53/53), v2 100% (43/43) recall, precision, and exact-set accuracy; v3 248/256 | v1 100% with test-time augmentation (0.9x/1.1x speed), 98% without |
| Latency | about 0.7 s per sample (Node harness, v3) | 0.84 s (with augmentation), 0.72 s (without) |
| Licence | NPL-1.2 | CC-BY-4.0 |

The v1 and v2 corpora are small; one sample is about 1.9 points on v1. ONNX inference is non-deterministic by 3 to 6 samples per run on v1 for the older streaming models, so treat small differences as noise.

## Experiment Landscape

The repo's `lab/experiments/` has about 25 experiment directories. Historical batch results (full-file, Python harness, v1 recall unless noted) from `lab/EXPERIMENTS.md`:

| Approach | v1 recall | Size | Note |
|---|---|---|---|
| FastConformer `c2c-direct-mixed-tta` | 100% | 88 MB | Best batch model; 0.84 s |
| Zipformer2-CTC (v3.1 base, tracker) | 100% | 73 MB | Streaming; v2 98% in that run |
| w2v-phonemes large (r7) | 100% | 970 MB | 15.2 s per sample; too large to ship |
| w2v-phonemes base (r15) | 96 to 97% (v3 slices) | 388 MB fp32, 118 MB int8 | About 0.9 to 1.1 s on CPU; batch only, cannot stream |
| FastConformer (stock `nvidia-fastconformer`) | 95% | 115 MB | 0.7 s |
| Tadabur Whisper-small | 86% | 461 MB | Fine-tuned |
| Rabah pruned CTC (8 layers, `first_n`, fine-tuned) | 75% | 145 MB | 3.7 s |
| Stock Whisper-small | 73% | 461 MB | Not competitive |
| Contrastive (HuBERT + AraBERT), embedding search | 0% | 397 to 900 MB | English-pretrained encoders give no useful Arabic features |
| Tarteel Whisper-base | not scored | 290 MB | Model loading errors on all samples in the lab run |

Historical streaming baseline before Zipformer (phoneme FastConformer, 131 MB, `RecitationTracker`): 87.9% recall on v2 and 89.3% on v3; precision 68.9% and 73.4%. Full-file single-match on the same model: 84.1% recall (81.1% exact-set accuracy) on v1 and 78.1% on v2.

Key findings from the repo:
- Phoneme CTC with harakat and madd length gives the matcher more discriminative symbols per second than BPE text.
- Matching quality was a bottleneck: multi-pass matching (fragment scoring, span scoring, bismillah stripping) raised one Python batch model from 79% to 90% v1 recall.
- Layer pruning with `first_n` beats `evenly_spaced` by about 20 points at the same depth, and fine-tuning the CTC head is required.
- More crowd (TLOG) data is not better: about 18K samples at filter 0.3 was the best mix; larger mixes regressed.
- Wav2vec2 phoneme models are batch verifiers, not streaming models; chunked inference collapsed (3.9% exact-sequence accuracy).
- Remaining Zipformer errors on v3 are mostly textually identical or near-identical ayahs (for example 55:53 versus 55:13), so an app should show alternatives when confidence is low.

## Best Practices

- **Audio must be 16 kHz mono.** Convert with ffmpeg before processing.
- **Use `@tilawa/core`, not hand-ported DSP.** Feature extraction, decoding, and tracking are inside the package.
- **Feed streaming audio in about 300 ms chunks**, the size the benchmarks use, and call `stop()` at the end so the tail is flushed.
- **Normalize Arabic text before any extra matching.** Match on `quran-text` plain keys, not display text.
- **Handle multi-ayah recitation.** Users often recite several consecutive ayahs; use `final_sequence` for the ordered result.
- **Treat identical or near-identical ayahs as ambiguous.** Ask for more audio or show the candidates from `verse_candidate`.
- **Use confidence.** Show only results above a threshold you tune on your own audio; low-confidence matches are usually wrong.
- **Download the model on first launch, not at install.** 66 MB (Zipformer) is large for an app bundle on some platforms. Show progress.
- **Test with diverse audio.** Studio, phone with background noise, and crowdsourced recordings behave very differently.
- **Run benchmarks more than once.** ONNX Runtime is not fully deterministic; average 3 runs.
- **Check licences per model.** Zipformer is non-commercial share-alike; FastConformer is CC-BY-4.0.
