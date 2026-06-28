# Release Notes

## Current Release Flow

- GitHub Actions builds the latest app from `main`.
- The workflow publishes an ad-hoc signed zip to the `latest` GitHub Release.
- The release version follows the highest supported macOS version, currently `26.0.0`.
- Automatic updates are disabled for this fork's GitHub releases.

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
