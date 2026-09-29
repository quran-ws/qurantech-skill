### FILE answer.md
# Offline Quran ayah recognition from microphone in React Native

Written from my own knowledge (no web research this session). Verify library versions and model licences before committing.

## Recommendation

Use a **two-stage pipeline**, all on-device:

1. **Offline speech-to-text (ASR) on Arabic** → produces a rough transcript.
2. **Fuzzy matching against a bundled Quran text index** → returns the surah:ayah.

The ASR does not need to be perfect. The matching step corrects for its errors, because the search space is small (6,236 ayahs) and known.

### Stage 1: ASR options

| Option | Notes |
|---|---|
| **whisper.rn** (whisper.cpp binding for RN) | Most practical choice. Works offline on iOS and Android. Use a multilingual `tiny`/`base`/`small` model, language `ar`. Bigger models are more accurate but slower and heavier. |
| **sherpa-onnx** (RN/native bindings) | Streaming ASR, so you get live results while the user recites. Needs an Arabic model, and you must check that one exists and is good enough. |
| **Fine-tuned Quran Whisper model** (community models on Hugging Face) | Much better on tajweed-style recitation than stock Whisper. You would convert to ggml for whisper.cpp. Check the licence and quality yourself. |
| Platform speech APIs (iOS `SFSpeechRecognizer`, Android `SpeechRecognizer`) | Offline Arabic support is inconsistent by device and OS version, and the quality on recitation is poor. Not recommended as the main path. |

Stock Whisper handles Quranic recitation only moderately well. Expect diacritics to be dropped or wrong, and melodic or elongated recitation to hurt accuracy. A Quran-fine-tuned model is worth the effort.

### Stage 2: Matching

- Bundle the Quran text (e.g. Tanzil, Uthmani or simple-clean) in SQLite or a JSON file.
- **Normalise** both sides: strip diacritics/tashkeel, unify alef, ya and ta marbuta variants, remove tatweel, and drop small Quranic marks.
- Match with **character n-gram / token overlap or edit distance** (e.g. an inverted index of word trigrams, then Levenshtein re-rank on the top candidates).
- Also consider **sliding windows over consecutive ayahs**. Users often recite a fragment, or several ayahs, and short ayahs are ambiguous alone (e.g. "الرحمن", "ألم").
- Return the top-N candidates with confidence scores rather than a single answer.

## Architecture in React Native

- Capture audio as 16 kHz mono PCM (e.g. `react-native-audio-record` or a similar library).
- Run Whisper on chunks or on the finished recording, off the JS thread (whisper.rn does this natively).
- Run matching in JS or a native module; 6k ayahs is small enough for JS.
- Ship models with the app or download them once on first launch. Afterwards everything works offline.
- Needs a **dev build / bare workflow**, not Expo Go, because of native modules.

## Limits and risks

- **Model size**: Whisper tiny ≈ 75 MB, base ≈ 140 MB, small ≈ 470 MB (fp16; quantised versions are smaller). This affects app size and RAM on low-end phones.
- **Latency**: `tiny`/`base` are near real-time on modern phones. `small` and above can be slow on older or mid-range devices. Whisper is not natively streaming; real-time behaviour comes from chunking, which is clunkier than a true streaming model.
- **Accuracy on recitation**: tajweed, madd (elongation), qira'at differences, background noise and different reciters all reduce accuracy. Children and non-native speakers are harder still.
- **Similar ayahs (mutashabihat)**: many ayahs repeat or nearly repeat across the Quran. Audio alone can be genuinely ambiguous. Show several candidates and let the user confirm, or use more context (longer recitation).
- **Very short recitations** (one or two words) cannot be identified reliably.
- **Battery and thermals** under continuous inference.
- **Licensing**: check the licence for the Whisper model you use, especially community fine-tunes, and for the Quran text source.
- **Correctness/sensitivity**: this is scripture. Do not present the ASR output itself as Quran text; display the matched ayah from your verified text source. Do not claim it verifies recitation correctness unless you build that separately.

## Alternative: audio fingerprinting/embedding approach

Instead of ASR, match against reference recordings (audio fingerprinting or embeddings). This is less flexible: it works only for reciters you have recordings of, and needs a large audio bundle. It is not recommended unless you are restricting to specific reciters.

## Suggested path

1. Prototype with whisper.rn + `base` multilingual, Arabic, and a normalised n-gram matcher, then measure top-1/top-5 accuracy on real user recordings.
2. If accuracy is too low, swap in a Quran-fine-tuned Whisper model (converted to ggml, quantised).
3. Add a candidate-list UI for ambiguous results.
4. Test on low-end devices to decide the model size to ship.


### FINAL MESSAGE
I wrote the answer to `answer.md`. It comes from my own knowledge, with no web research, so check library versions and model licences before you commit to anything.

**Recommendation:** use a two-stage pipeline, all on the device.
1. **Offline Arabic speech-to-text.** Use `whisper.rn`, ideally with a Quran-fine-tuned Whisper model, because stock Whisper only handles recitation moderately well.
2. **Fuzzy matching against a bundled Quran text.** Normalise away the diacritics, then match with n-gram overlap plus edit-distance re-ranking. Show several candidate ayahs rather than one answer.

**Main limits:**
- **Model size and speed:** the Whisper models range from about 75 MB to 470 MB, and the larger ones run slowly on older phones. Whisper isn't natively streaming, so live results need chunking.
- **Recitation accuracy:** melodic or elongated recitation, background noise, and different reciters all reduce it.
- **Repeated ayahs:** many ayahs repeat or nearly repeat across the Quran, and one- or two-word recitations are effectively unidentifiable. Longer input or a user confirmation step helps.
- **Build setup:** it needs a dev build or bare workflow, so it won't run in Expo Go.
- **Displaying results:** show the matched ayah from your verified text source, never the raw speech-to-text output.

The file also covers the platform speech APIs, `sherpa-onnx`, an audio-fingerprinting alternative, and a suggested prototyping path.