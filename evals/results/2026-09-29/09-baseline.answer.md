### FILE answer.md
# Daily ayah notification: fixing the truncated body

## Cause

The ~100 characters you see is usually not a limit in your code. It is how the OS renders a *collapsed* notification:

- **Android**: the default style shows one or two lines and ends with an ellipsis. Only `BigTextStyle` shows the full text when the user expands it.
- **iOS**: the banner truncates the body. The full body appears when the user long-presses or pulls down the notification, up to the system limit.

The full text is often already in the payload. The client just never asks the OS to show it expanded. The exception is if the server or app truncates the string itself, for example `body.substring(0, 100) + "…"`, so check for that first.

## Approach

1. **Send the full ayah text** in the payload. APNs and FCM allow about 4 KB, which covers even Ayat al-Kursi and Al-Baqarah 2:282, the longest ayah, with room to spare. Don't truncate on the server.
2. **Android**: apply `NotificationCompat.BigTextStyle` so the notification expands to show the whole ayah.
3. **iOS**: no special style is needed. Put the ayah in `body` and keep the payload under 4 KB. Optionally add a Notification Service Extension (`mutable-content: 1`) to attach the translation or reference.
4. **Fallback for very long text**: put a short reference in the collapsed line, such as "Al-Baqarah 2:282", and open the full ayah screen when the user taps. Set the tap action to deep-link to that screen.
5. If you have to shorten text, cut on a word boundary. Never cut mid-word or mid-Arabic-letter-cluster, and keep the surah:ayah reference.

## Sample code

### Server (Node, firebase-admin)

Send a data message so Android builds the notification itself. Also include a `notification` block for iOS.

```js
const admin = require("firebase-admin");

async function sendDailyAyah(token, ayah) {
  // ayah = { surah: "Al-Baqarah", number: 282, text: "...", translation: "..." }
  const title = `${ayah.surah} ${ayah.number}`;
  const body = ayah.translation
    ? `${ayah.text}\n\n${ayah.translation}`
    : ayah.text;

  await admin.messaging().send({
    token,
    data: {                      // Android reads this in onMessageReceived
      title,
      body,
      ayahId: `${ayah.surah}:${ayah.number}`,
    },
    apns: {                      // iOS shows the full body on expansion
      payload: {
        aps: {
          alert: { title, body },
          "mutable-content": 1,
          sound: "default",
        },
        ayahId: `${ayah.surah}:${ayah.number}`,
      },
    },
    android: { priority: "high" },
  });
}
```

### Android (Kotlin)

```kotlin
class AyahMessagingService : FirebaseMessagingService() {
    override fun onMessageReceived(msg: RemoteMessage) {
        val title = msg.data["title"] ?: return
        val body = msg.data["body"] ?: return
        val ayahId = msg.data["ayahId"]

        val intent = Intent(this, AyahActivity::class.java)
            .putExtra("ayahId", ayahId)
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
        val pending = PendingIntent.getActivity(
            this, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(this, "daily_ayah")
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(body)                              // collapsed view
            .setStyle(NotificationCompat.BigTextStyle().bigText(body)) // expanded: full ayah
            .setContentIntent(pending)
            .setAutoCancel(true)
            .build()

        NotificationManagerCompat.from(this).notify(ayahId.hashCode(), notification)
    }
}
```

The `daily_ayah` channel must exist (Android 8+) and the app needs the `POST_NOTIFICATIONS` permission on Android 13+.

### Word-boundary fallback (if you must shorten)

```js
function shorten(text, max = 180) {
  if (text.length <= max) return text;
  const cut = text.slice(0, max);
  return cut.slice(0, cut.lastIndexOf(" ")) + "…";
}
```

Use it only for the collapsed line. The expanded body and the in-app screen should always show the full ayah.

## Testing

- Test with the longest ayah (2:282) on a real Android device and an iOS device.
- On Android, expand the notification and confirm the full text shows.
- On iOS, long-press the notification and confirm the same.
- Test with Arabic text and RTL layout, and with long translations.
- Test with the app in the foreground, the background and killed. Data-only messages on Android behave differently in each state.

## Note

The project directory was empty, so I couldn't check your actual stack. The samples assume FCM with a Node server and a native Android client. If you use React Native, Flutter or OneSignal, the same ideas apply, but you'll need each library's equivalent of `BigTextStyle`. For example, OneSignal has `big_text`, and `flutter_local_notifications` has `BigTextStyleInformation`. If you share the repo, I can apply the fix directly.


### FINAL MESSAGE
I wrote `answer.md`, but I couldn't change any app code because `/tmp/eval9-baseline-00uq2zg4` was empty. The samples assume FCM with a Node server and a native Android client, and I haven't run any of them.

**Cause:** the 100-character cutoff is most likely how the OS renders a collapsed notification, not a limit in your code. Android needs `BigTextStyle` to show the full text when expanded. iOS shows the full body when the user long-presses. Also check that your server or app isn't trimming the string itself.

**Fix:**
- Send the full ayah in the payload. FCM and APNs allow about 4 KB, which covers the longest ayah (2:282).
- On Android, build the notification client-side with `BigTextStyle`.
- On iOS, put the full ayah in `body`.
- If text has to be shortened, cut on a word boundary. Tapping the notification should open the full ayah screen.

`answer.md` also has the server code, the Android Kotlin service, a word-boundary helper and a testing checklist. If you're on React Native, Flutter or OneSignal, the same approach applies with each library's own big-text option. If you share the repo, I can make the actual change.