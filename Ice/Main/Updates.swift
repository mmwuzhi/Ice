//
//  Updates.swift
//  Ice
//

import AppKit
import Combine

/// Manager for app updates.
@MainActor
final class UpdatesManager: NSObject, ObservableObject {
    /// The date of the last update check.
    @Published var lastUpdateCheckDate: Date?

    /// The shared app state.
    private(set) weak var appState: AppState?

    /// The latest release page for this fork.
    private static let latestReleaseURL = URL(string: "https://github.com/mmwuzhi/Ice/releases/latest")

    /// Performs the initial setup of the manager.
    func performSetup(with appState: AppState) {
        self.appState = appState
    }

    /// Checks for app updates.
    @objc func checkForUpdates() {
        guard let latestReleaseURL = Self.latestReleaseURL else {
            return
        }

        if let appState {
            appState.activate(withPolicy: .regular)
        }
        lastUpdateCheckDate = Date()
        NSWorkspace.shared.open(latestReleaseURL)
    }
}
