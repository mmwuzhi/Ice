# Release Notes

## Current Release Flow

- GitHub Actions builds the latest app from `main`.
- The workflow publishes an ad-hoc signed zip to the `latest` GitHub Release.
- The release version follows the highest supported macOS version, currently `26.0.1`.
- Automatic updates are disabled for this fork's GitHub releases.

## Signing Security: Temporary Trade-off (No Paid Account)

The release workflow ships **ad-hoc** builds (`CODE_SIGN_IDENTITY=-`, no team), because
this fork has no paid Apple Developer account / Developer ID certificate.

Ad-hoc builds have no team identifier. On **macOS 26+**, the `MenuBarItemService` XPC
connection enforced `.isFromSameTeam()`, which a teamless build can never satisfy — so
source-PID resolution failed, Ice's control items lost their bundle-id namespace, the
item cache stayed empty, and menu bar items hung on "Loading menu bar items…".

To keep ad-hoc releases working, the same-team requirement is currently **disabled** on
both ends:

- `Ice/MenuBar/MenuBarItems/MenuBarItemServiceConnection.swift` — `setPeerRequirement(.isFromSameTeam())` commented out.
- `MenuBarItemService/Listener.swift` — uses `uncheckedActivate()` (no requirement) instead of `uncheckedActivateWithSameTeamRequirement()`.

This **lowers security**: any local process can connect to the XPC service. The service
is read-only and only reports which app owns a given menu bar window (low-sensitivity),
so the trade-off is acceptable for an ad-hoc fork, but it is not the intended posture.

**When a paid Apple Developer account is available, switch to the higher-security setup:**

1. Restore the same-team requirement at both call sites above (search for `TODO: Restore the same-team`).
2. Change the release workflow from ad-hoc to **Developer ID + notarization**:
   - Import a Developer ID Application cert into the CI keychain (base64 p12 in GitHub secrets).
   - Build with `CODE_SIGN_IDENTITY="Developer ID Application"`, `CODE_SIGN_STYLE=Manual`,
     `OTHER_CODE_SIGN_FLAGS=--timestamp` (secure timestamp, not `--timestamp=none`),
     `ENABLE_HARDENED_RUNTIME=YES`.
   - Notarize with `xcrun notarytool submit ... --wait` (App Store Connect API key in
     secrets), then `xcrun stapler staple Ice.app`, then re-zip.
3. Both the app and the embedded XPC helper are then signed with the same real team, so
   `.isFromSameTeam()` passes and users no longer need `xattr -dr com.apple.quarantine`.

Why ad-hoc over a free-account `Apple Development` signature for releases: a free
`Apple Development` cert has a real team (would also satisfy same-team and keep TCC
permissions across updates), but it still cannot be notarized (so Gatekeeper friction
is unchanged) and expires in ~1 year — a signed release would stop launching once the
cert expires. Ad-hoc never expires, so it is the better stopgap until a paid Developer ID.

## Future Auto-Update Work

Add auto-update support when there is a maintained update feed for this fork.

Expected work:

- Reintroduce Sparkle only when this fork has its own appcast.
- Generate and publish an appcast for `mmwuzhi/Ice` releases.
- Use this fork's Sparkle signing key, not the upstream Ice key.
- Point `SUFeedURL` at this fork's appcast.
- Restore the in-app automatic update toggles and update-check UI.
- Update the GitHub release workflow to publish the appcast alongside the zip.

Do not point release builds at the upstream `jordanbaird/Ice` appcast.
