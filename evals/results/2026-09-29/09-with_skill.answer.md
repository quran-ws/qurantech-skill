### FILE answer.md
# Daily ayah notification: fixing the ~100-character cut-off

There is no app source in the working directory (it was empty), so I couldn't change your code. Below are the approach and drop-in sample code. The names in the samples (`AyahRef`, `QuranTextRepo`) are placeholders for whatever your app uses.

## Cause

The body is being shortened to about 100 characters and given an ellipsis. Either your code does it, or the OS does it to the collapsed notification. An Arabic ayah with its diacritics is often longer than that.

## Approach

The rule to follow is not to make the truncation smarter. Quran.ws adab says: *never trim the text to fit the layout, and never let an ellipsis stand in Quranic text* (Quranic text 7.1). A fragment is allowed only if it is labelled as a fragment, carries its reference, and links to the full ayah (7.2). Cutting at a word boundary or at N characters can also separate a letter from its marks. So the fix is to change what the collapsed notification shows and where the full text is displayed.

1. **Send a reference, not text.** The push payload carries `{surah, ayah, counting_system}`. The device resolves the text from the pinned, bundled `quran-text` dataset. Nobody hand-types the ayah on the server or in a template. An ayah number alone is not a location, so the counting system travels with it.
2. **Collapsed view: the reference and a label only.** For example "Ayah of the day, 2:255. Tap to read." The system will ellipsize collapsed text if it is long, so no Quranic text goes there and nothing is cut mid-ayah.
3. **Expanded view shows the whole ayah.**
   - Android uses `BigTextStyle`, whose limit is far above 100 characters.
   - iOS uses a Notification Content Extension. It shows the full ayah in a Quranic font, with RTL layout and no fallback font.
4. **Tap opens the ayah in the app.** This is the "link" that 7.2 requires.
5. **If the text can't be resolved** (missing, failed to load, or unexpected), post the reference-only notification. Never post partial text.
6. **No audio in the notification.** Recitation never starts from a notification (Engineering 6.5).
7. **Logging and tests.** Log `2:255`, never the text. Tests compare against a named `quran-text` release, not hand-typed strings.

## Sample code: Android (Kotlin)

```kotlin
data class AyahRef(val surah: Int, val ayah: Int, val counting: String)

fun showDailyAyah(ctx: Context, ref: AyahRef) {
    val label = "${ref.surah}:${ref.ayah}"                 // log and display the reference only
    val text = QuranTextRepo.get(ref)                      // pinned quran-text release; null if unavailable

    val tapIntent = PendingIntent.getActivity(
        ctx, 0,
        Intent(ctx, AyahActivity::class.java)
            .putExtra("surah", ref.surah).putExtra("ayah", ref.ayah)
            .putExtra("counting", ref.counting),
        PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
    )

    val b = NotificationCompat.Builder(ctx, "daily_ayah")
        .setSmallIcon(R.drawable.ic_notification)
        .setContentTitle(ctx.getString(R.string.daily_ayah_title, label))
        .setContentText(ctx.getString(R.string.tap_to_read))   // collapsed: no Quranic text
        .setContentIntent(tapIntent)
        .setAutoCancel(true)

    if (text != null) {
        // Expanded: the complete ayah, unmodified. No substring(), no "...".
        b.setStyle(NotificationCompat.BigTextStyle().bigText(text))
    } // else: reference-only notification; never show partial text

    NotificationManagerCompat.from(ctx).notify(ref.hashCode(), b.build())
}
```

## Sample code: iOS (Swift)

The server sends a mutable-content push whose payload has only the reference.

```json
{ "aps": { "alert": { "title": "Ayah of the day", "body": "Tap to read" },
           "mutable-content": 1, "category": "DAILY_AYAH" },
  "surah": 2, "ayah": 255, "counting": "hafs-kufan" }
```

The Notification Content Extension shows the full ayah when the user expands the notification.

```swift
import UIKit
import UserNotifications
import UserNotificationsUI

final class AyahNotificationViewController: UIViewController, UNNotificationContentExtension {
    @IBOutlet private weak var ayahLabel: UILabel!
    @IBOutlet private weak var refLabel: UILabel!

    func didReceive(_ notification: UNNotification) {
        let info = notification.request.content.userInfo
        guard let surah = info["surah"] as? Int,
              let ayah = info["ayah"] as? Int,
              let counting = info["counting"] as? String else { return }

        refLabel.text = "\(surah):\(ayah)"
        guard let text = QuranTextRepo.shared.ayah(surah: surah, ayah: ayah, counting: counting) else {
            ayahLabel.text = nil          // reference only; never partial text
            return
        }
        ayahLabel.font = QuranFont.uthmani(size: 26)   // Quranic font; no fallback
        ayahLabel.semanticContentAttribute = .forceRightToLeft
        ayahLabel.textAlignment = .right
        ayahLabel.numberOfLines = 0                    // never truncate
        ayahLabel.lineBreakMode = .byWordWrapping
        ayahLabel.text = text                          // unmodified: no trim, no normalize
    }
}
```

In the extension's `Info.plist`, set `UNNotificationExtensionCategory` to `DAILY_AYAH` and `UNNotificationExtensionDefaultContentHidden` to `true`, so the system's own truncated body is hidden.

## Things to avoid

- Don't raise the 100-character limit to something larger. A longer limit still cuts some ayahs, and the OS collapses long bodies anyway.
- Don't cut at a word boundary or add "…". Both put an ellipsis where Quranic text should be.
- Don't call `trim`, `normalize` or whitespace-collapsing on the text.
- Don't put the ayah in server logs, analytics events or push-provider dashboards. Use `surah:ayah`.
- If you must show a fragment (for example on a very old OS with no expandable style), label it as a fragment with its reference and a link. Don't build it by character count.

## Tests

- For each ayah in a pinned `quran-text` release, assert that the expanded content equals the dataset text byte for byte. Include the longest ayah (2:282).
- Assert that the collapsed content contains the reference and no Quranic text.
- Assert that when the text lookup returns null, the notification has only the reference.
- Ayah counts and boundaries differ between counting systems. If you support a riwayah other than Hafs, resolve the reference through `qiraat-ayah-map` first.


### FINAL MESSAGE
I wrote `answer.md` in `/tmp/eval9-with_skill-df_gvb84`. There was no app code in that directory, so I couldn't change your app. `answer.md` has sample Kotlin and Swift code, and I haven't compiled or run either.

The fix is not to raise the 100-character limit, because a longer limit would still cut some ayahs. The Quran.ws adab guidelines (which the QuranTech skill enforces) forbid trimming an ayah to fit the layout or putting an ellipsis in its place. The approach in `answer.md`:

- **Payload:** the push sends only `{surah, ayah, counting_system}`. The app looks up the text from the pinned `quran-text` dataset on the device.
- **Collapsed view:** it shows only the reference and a "tap to read" label, with no Quranic text. That way the system's own ellipsis never lands on an ayah.
- **Expanded view:** it shows the whole ayah, unmodified.
  - On Android, that's `BigTextStyle`.
  - On iOS, it's a Notification Content Extension with a Quranic font, right-to-left layout and no line limit.
- **Failures:** if the text can't be loaded, the notification shows the reference only, never partial text.
- **Other rules:** tapping opens the ayah in the app, and the notification never starts audio.
- **Tests and logs:** the doc also covers logging only `surah:ayah` and tests that compare against a named `quran-text` release, including the longest ayah (2:282).

If you point me at the real notification code, I can apply this there.