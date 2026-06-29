# Ice

Ice is a macOS menu bar management app (hide/show menu bar items, custom menu bar
appearance, hotkeys, the "Ice Bar"). SwiftUI app, macOS 14+, Swift 5.0. This repo is a
fork of `jordanbaird/Ice` with bundle id `com.mmwuzhi.Ice`.

`AGENTS.md` is a symlink to this file.

## Build, run, lint

There is no Makefile or `Package.swift`; the project is an Xcode project with SPM
dependencies resolved through Xcode.

```sh
# Build the app (Debug)
xcodebuild -project Ice.xcodeproj -scheme Ice -configuration Debug build

# Lint exactly as CI does (.github/workflows/lint.yml)
swiftlint --strict
```

- Schemes: `Ice` (the app) and `MenuBarItemService` (the XPC helper). Building `Ice`
  also builds the helper and embeds it under `Contents/XPCServices`.
- `swiftlint` is not installed locally. Install with `brew install swiftlint` before
  relying on lint output. CI runs `--strict`, so any warning fails the build.
- No unit/UI test target exists. Do not assume `xcodebuild test` works.
- Signing is automatic (`DEVELOPMENT_TEAM = JLB7JMH6A9`). The app is unsandboxed and
  uses Accessibility + Screen Recording permissions at runtime.
- Release CI uses ad-hoc signing (`CODE_SIGN_IDENTITY=-`) because this fork ships
  public GitHub release builds without a paid Developer ID certificate.

## Architecture

Entry point and ownership chain:

```
IceApp (@main, SwiftUI App)
  -> AppDelegate (NSApplicationDelegateAdaptor)
     -> AppState (@MainActor, ObservableObject) -- the central hub
```

`AppState` (`Ice/Main/AppState.swift`) owns every long-lived manager and is the single
source of app-wide state. The managers it owns:

- `settings` (`AppSettings`), `permissions` (`AppPermissions`), `navigationState`
- `menuBarManager`, `appearanceManager`, `spacingManager`, `itemManager`, `imageCache`
- `hidEventManager`, `updatesManager`, `userNotificationManager`

Two conventions to follow when touching managers:

1. **`performSetup(with: AppState)`** is the standard init hook. Managers do real wiring
   in `performSetup`, not in `init`. `AppState.setupTask` calls each manager's
   `performSetup` in a fixed order; respect that ordering when adding a new manager.
2. **Managers hold `private weak var appState: AppState?`** captured during
   `performSetup`. Keep the reference weak to avoid retain cycles.

State propagation is Combine-heavy: managers expose `@Published` properties, and
`AppState.configureCancellables()` forwards their `objectWillChange` upward. Prefer the
existing custom Combine operators (`discardMerge`, `replace`, `removeNil`, `mergeMap`,
etc. in `Ice/Utilities` and `Ice/UI`) over re-rolling pipelines.

### Targets and shared code

- **`Ice/`** — the main app. Subsystems live in named folders: `MenuBar/` (items,
  appearance, IceBar, layout, spacing, sections, control item), `Events/`, `Hotkeys/`,
  `Permissions/`, `Settings/` (panes + `Models`), `UI/`, `UserNotifications/`,
  `Utilities/`, `Main/`.
- **`MenuBarItemService/`** — a separate XPC service target. It runs an `XPCListener`
  (`Listener.swift`) and resolves the source process of a menu bar item window via
  `SourcePIDCache`. Only used on **macOS 26+** (`AppState` starts the connection behind
  `if #available(macOS 26.0, *)`). On 26+ the listener requires peers from the same team.
- **`Shared/`** — code compiled into both targets: `Bridging/` (private API wrappers),
  `Services/MenuBarItemService.swift` (the request/response protocol shared by both
  sides), and `Utilities/` (AX helpers, logging, `WindowInfo`).

### Private and bridged APIs

`Shared/Bridging/Bridging.swift` wraps private window-server (`CGS*`) and other system
APIs behind a clean `Bridging` namespace; `Shims.swift` declares the missing
signatures. Route new private-API usage through `Bridging` rather than calling the
symbols directly inline.

## Code conventions (enforced by SwiftLint)

`.swiftlint.yml` is `--strict`, so these are hard requirements, not suggestions:

- **File header is mandatory** and must match exactly:
  ```swift
  //
  //  FileName.swift
  //  Ice          // or `Shared` / `MenuBarItemService`, matching the target
  //
  ```
- **4-space indentation, never tabs** (`prefer_spaces_over_tabs` custom rule).
- **Trailing commas are mandatory** in multiline literals.
- **`force_unwrapping` and `implicitly_unwrapped_optional` are opt-in rules**, i.e.
  flagged. Where a force-unwrap is intentional (e.g. `Constants.swift`), wrap it in
  `// swiftlint:disable force_unwrapping` / `enable` rather than leaving a raw `!`.
- `@objc dynamic` ordering, `modifier_order` (acl, setterACL, override, ...), and
  closure/multiline-bracket rules are enforced. When in doubt, mirror a nearby file.
- Use enum-as-namespace (`enum Constants`, `enum Bridging`) for grouping static members.
- Use `OSLog` via the project `Logger(category:)` helper for logging, with `privacy:`
  annotations on interpolated values.

## Notes

- Releases are built by `.github/workflows/latest-release.yml` on pushes to `main`.
  The workflow publishes `Ice-latest-macos26.zip` to the moving `latest` GitHub
  Release and overrides the app version to the highest supported macOS version
  (`26.0.1` currently).
- Automatic updates are disabled for this fork's GitHub releases. The in-app update
  action opens `https://github.com/mmwuzhi/Ice/releases/latest` instead of using an
  appcast.
- Sparkle has been removed for now. Future auto-update work is tracked in
  `docs/release.md`; do not point release builds at the upstream Ice appcast or reuse
  the upstream Sparkle signing key.
- SPM dependencies: LaunchAtLogin-Modern, AXSwift, CompactSlider, Ifrit (fuzzy search
  for item search), Semaphore.
- `FREQUENT_ISSUES.md` documents user-facing menu bar quirks (items landing in the
  always-hidden section, ordering) that are macOS behavior, not bugs in this code.
