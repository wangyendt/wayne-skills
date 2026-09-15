# Client setup

Python 3.10+; recommended launcher: `uv run /absolute/skill/scripts/publisher.py ...`. Android inspection needs SDK build-tools (`aapt`, `apksigner`) and Java. Standard macOS/Linux/Windows SDK directories are discovered automatically; ANDROID_HOME, ANDROID_SDK_ROOT, AAPT_PATH, APKSIGNER_PATH and JAVA_HOME override discovery. On macOS the helper can use Android Studio's bundled Java. It does not modify Xcode license settings.

In the user's interactive terminal, run `init --url https://HOST:PORT`. Token input is hidden. Initialization verifies authenticated app listing, so the service needs OSS configured first. The default URL is the owner's deployment; other installations must pass their own URL.

Use macOS Keychain, Windows credential storage or a working Linux Secret Service/KWallet backend. Plaintext/fail/chainer keyring backends are rejected. In a headless POSIX environment, explicitly choose `--credential-store file` if a 0600 local credential file is acceptable. Prefer OS storage on Windows instead of relying on POSIX file modes.

Config defaults to the user's `.config/android-app-publisher` directory, not the repository. ANDROID_APP_PUBLISHER_CONFIG overrides it with a private local directory. Config JSON contains only API URL and backend. The keyring entry is scoped by API origin. Reinitialization verifies new credentials before replacing old ones.

`--token-stdin` permits a trusted server-to-client pipe without model-visible plaintext or shell arguments. It is not an invitation to paste tokens into chat. No Notion secret integration is implemented.

## Operations

- `inspect /absolute/app.apk`: offline metadata/signature verification.
- `publish --apk /absolute/app.apk --dry-run`: inspect only, no token/network needed.
- `publish --project /absolute/project --apk-output app/build/outputs/apk/release/app-release.apk --gradle-task assembleRelease`: explicit Gradle build/output. Add tests from project docs. Uses argv, not shell interpolation. Tasks run with --rerun-tasks and the selected APK must be freshly produced; use --apk when intentionally reusing an existing artifact. Build logs are private outside Git since builds can print credentials.
- `apps`, `show com.example.app`: authenticated listing/current version.
- `share com.example.app --output /absolute/download.png`: locally generated QR of the stable APK link.
- `status [UPLOAD_ID]`: last/specified receipt; `complete UPLOAD_ID`: retry finalization after inspecting uncertain status. Superseded/conflicting releases are not silently overwritten.
- `doctor`: credential loading and authenticated listing, without token disclosure.

Latest URLs remain fixed and request cache revalidation. A client ignoring cache headers may still keep an old file; compare actual version/hash when diagnosing. Labels are untrusted text. The skill does not add in-app upgrades, change signing/ABI/minSDK, or edit embedded keys without a separate user instruction.
