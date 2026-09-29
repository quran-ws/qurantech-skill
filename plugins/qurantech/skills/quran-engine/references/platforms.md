# quran-engine platforms (sources: repo README and package READMEs, quran.ws/docs/build/platforms)

The site platforms page was written at repo commit a19ee9b (11 Sep 2026) and says nothing is published. The repo READMEs are newer; prefer them and verify on the registry.

| Platform | Package in repo | Install per its README |
|---|---|---|
| Web | `@quran.ws/engine` (package.json 0.3.0; exports `.`, `./lite`, `./lite/passage`, `./qvp.js`, `./qvp_ffi.wasm`) | Root README says "not published — build the wasm, or take it from the release". `npm view` returned 0.3.0. Unresolved conflict. |
| iOS/macOS | `packages/ios/QvpKit`, product `QvpKit` | `.package(url: "https://github.com/quran-ws/quran-engine.git", from: "0.2.2")`; SwiftPM downloads the XCFramework and verifies its checksum. Otherwise build with `scripts/build-engine-ios.sh`. |
| Android | `packages/android/qvp`, Kotlin over JNI, minSdk 24, arm64-v8a, armeabi-v7a, x86_64 | `implementation("ws.quran:qvp-android:0.2.2")` from Maven Central, or the release AAR with SHA-256. |
| Flutter | `packages/flutter/qvp_flutter`, dart:ffi | `qvp_flutter: ^0.2.2`; pub.dev package includes the Android engine. Android only per the site; iOS unverified. |
| React Native | `packages/react-native/qvp-react-native`, `<QvpPageView />` | `npm install @quran.ws/qvp-react-native` (0.3.0 on npm). Android only ("iOS TODO"); include `packages/android/qvp` as a Gradle project; RN >= 0.76. |

Every wrapper takes bytes or a path, never a base URL (the engine is URL-agnostic). No package ships page data.
Build commands (AGENTS.md): `scripts/build-engine-android.sh`, `scripts/build-engine-ios.sh`, `cargo build -p qvp-ffi --release --target wasm32-unknown-unknown`.
Method names are the same across wrappers (`docs/API.md`, `docs/API-PARITY.md`); Flutter/Kotlin/Swift use their own casing.

## CDN layout (docs/CDN.md)
`qvp/<v>/{manifest.json,NNN.qvp,NNN.words.json,atlas.qva,surah-names/...,hafs-kfgqpc.tar.br}`; `engine/wasm|apple|android/<v>/`. `latest.json` sits beside the version folders. Data releases are tagged `data-vX.Y.Z`; engine releases `vX.Y.Z`. `qvp.quran.ws/<v>/` 301-redirects to the CDN.

## Sizes (site /offline)
Page 001 is 37.4 KB as `.qvp`, sidecar 4.2 KB; whole mushaf 26 MB as one bundle (README).

## Unverified
Whether the site's "not published" claims are now out of date for every platform; iOS on Flutter/RN; that lite `hitTestExact` exists at the released version.
