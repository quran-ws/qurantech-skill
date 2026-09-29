### FILE answer.md
# Offline "which ayah did I recite?" in React Native

## Recommendation

Use **Tilawa** (`@tilawa/core`, github.com/yazinsai/tilawa) with **`onnxruntime-react-native`**.

- It is pure TypeScript with no native code of its own. You inject the ONNX runtime for your platform.
- It takes 16 kHz mono audio and returns `surah:ayah` fully on-device, with no network at inference time.
- Output is structured: `{surah, ayah, ayah_end, score}`, not a transcript.
- Two engines ship:

| | Zipformer (default) | FastConformer |
|---|---|---|
| Use for | Live, streaming recitation (300 ms chunks) | One-shot / after-the-fact identification |
| Model size | 66 MB int8 (+5.5 MB corpus JSON) | 88 MB (+ vocab/token JSON) |
| Licence | **NPL-1.2 (non-commercial, share-alike)** | **CC-BY-4.0** |

Install:

```bash
npm i @tilawa/core onnxruntime-react-native
```

Then follow the RN walkthrough at `packages/core/examples/react-native.md` in the repo.

React Native specifics:

- ORT-RN cannot take the model as an `ArrayBuffer`.
- Bundle or download the `.onnx`, copy it to the documents directory, and call `ort.InferenceSession.create(modelPath)`.
- Pass the session and `ort.Tensor` into `createZipformerSession`.
- Load `zipformer_quran.json` (corpus) and optionally `quran.json` (display text).

```ts
import * as ort from "onnxruntime-react-native";
import { createZipformerSession } from "@tilawa/core";

const session = await createZipformerSession({
  session: await ort.InferenceSession.create(modelPath),
  Tensor: ort.Tensor,
  corpus: () => loadJsonAsset("zipformer_quran.json"),
  quran: () => loadJsonAsset("quran.json"),
});
// feed ~300 ms chunks of 16 kHz mono PCM, then stop() to flush the tail
```

Mic capture is your job. Use any RN audio-stream library that gives 16 kHz mono PCM float, or resample yourself, and feed `Float32Array` chunks of about 300 ms.

Around the model, use the Quran.ws blocks rather than ad hoc code:

- **`quran-text`:** verified text and plain/search keys for matching and display. Never hand-type Quranic text.
- **`qiraat-ayah-map`:** converts the result to your app's riwayah or counting system. Splits and merges yield ranges.
- **`quran-svg`, or `quran-engine` on native:** highlight or scroll to the matched ayah on the mushaf page.

## Limits

**Licence (the biggest one)**
- The default Zipformer model and phoneme corpus are **NPL-1.2: non-commercial and share-alike**. A paid or commercial app cannot ship it as is.
- The commercially usable path is **FastConformer (CC-BY-4.0, NVIDIA), with attribution**. It is batch, not streaming.
- The package code itself is MIT. Read the repo's `NOTICE.md` for the exact model you ship.

**Accuracy**
- Figures come from the repo's own small benchmarks, read 2026-09-29. They are not independent, and they change between releases.
  - Zipformer: 100% on v1 (53 samples) and v2 (43), 248/256 on v3.
  - FastConformer: 98% on v1, or 100% with speed test-time augmentation.
- These are small corpora and studio-ish or crowd audio. Test on your users' real phone audio with background noise.
- Textually identical or near-identical ayahs (for example 55:13 vs 55:53) are the main remaining errors. It cannot always tell them apart.
  - Show candidates from `verse_candidate` and ask for more audio when confidence is low.
  - Tune a confidence threshold on your own audio. Low-confidence matches are usually wrong.
- ONNX inference is not fully deterministic. Small benchmark differences are noise.

**Scope**
- It identifies which ayah(s). It does not grade tajweed or correctness, and it is not a mistake detector.
- It matches against the whole Quran. For hifz checking, "did they recite the expected verse" is a different, easier problem than open identification.
- Multi-ayah spans are supported (`final_sequence`), but very short fragments are more ambiguous.
- Riwayah: the counting system is that of the reference text it was matched against. Never assume Hafs numbering; store `{surah, ayah, counting}`. Recitation in other riwayat may lower accuracy. I did not find published numbers, so test it.
- Streaming quality is best with the Zipformer engine. The wav2vec2 phoneme models are batch only.

**Size and performance**
- The model is 66 to 88 MB. Download it on first launch with progress instead of bundling it, so you stay under store size limits.
- Latency is about 0.7 to 0.8 s per sample on the benchmark harness. That is not measured on RN. Real-device speed depends on the phone, so benchmark low-end Android.
- `onnxruntime-react-native` needs native modules. It works in a bare or dev-client build, not Expo Go.
- Web is not affected here, but WASM threading needs COOP/COEP headers if you add a web target.

**Maturity**
- `@tilawa/core` is v0.3.x, so pin the version and the release assets.
- It is a third-party project outside the Quran.ws blocks. Treat the API as able to change.

## Adab and app-level rules
- The mic is user-initiated. Do not record or auto-play without intent.
- Do not log recitation text. Log `surah:ayah` references only.
- Show identified text from a verified source (`quran-text`) with a Quranic font, never the raw model transcript.
- Keep audio on-device, and say so in your privacy policy.

## Alternatives
- **Cloud ASR (Whisper or other):** not offline, so it is out.
- **Stock Whisper-small:** 73% on the repo's v1 corpus, at 461 MB. Not competitive.
- **Custom fine-tuned CTC (phoneme or text):** possible, but the lab results show this is significant research work. Matching quality and phoneme CTC matter more than model size. Only pursue it if the NPL licence blocks you and FastConformer's batch mode is not enough.

## Suggested plan
1. Prototype with Zipformer to validate UX. Non-commercial use only.
2. Decide the commercial path: FastConformer (CC-BY-4.0), or get a licence from the Tilawa author for the Zipformer assets.
3. Build a test set of your own users' recordings, including noisy phone audio and multiple riwayat if relevant.
4. Add a confidence threshold plus a candidates UI for ambiguous ayahs.


### FINAL MESSAGE
I've written the answer to `/tmp/eval10-with_skill-sjqiimb3/answer.md`. I haven't run anything. It's based on the QuranTech skill's verse-recognition notes, which cite the Tilawa repo's own benchmarks as read on 2026-09-29.

**What to use:** Tilawa (`@tilawa/core`) with `onnxruntime-react-native`. It takes 16 kHz mono audio and returns the surah and ayah fully on-device. The default Zipformer engine streams live recitation (66 MB model). The alternative FastConformer engine is batch-only (88 MB model). Around it, use `quran-text` for verified text, `qiraat-ayah-map` to convert to your riwayah's numbering, and `quran-svg` or `quran-engine` to highlight the ayah.

**Main limits:**
- **Licence:** the default Zipformer model is NPL-1.2, which is non-commercial and share-alike. For a commercial app, FastConformer (CC-BY-4.0) is the usable engine, but it isn't streaming.
- **Accuracy:** the benchmarks are the repo's own small test sets. They show 98 to 100% on those, with the remaining errors on near-identical ayahs such as 55:13 and 55:53. Show candidates and use a confidence threshold, and test on real noisy phone audio.
- **Scope:** it identifies which ayah was recited. It doesn't grade tajweed or catch mistakes, and I found no published accuracy numbers for riwayat other than Hafs.
- **Size and setup:** download the model on first launch instead of bundling it. It needs a dev-client or bare build, not Expo Go. Latency is about 0.7 to 0.8 s per sample in the repo's benchmarks, not measured on React Native, so benchmark low-end Android yourself.
- **Maturity:** the package is v0.3.x and third-party, so pin the version.