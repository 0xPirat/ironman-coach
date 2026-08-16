import SwiftUI

@main
struct IronmanCoachApp: App {
    // Owns the Python sidecar lifecycle and the shared API client.
    @StateObject private var sidecar = SidecarManager()
    @StateObject private var api = APIClient()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(sidecar)
                .environmentObject(api)
                #if os(macOS)
                .frame(minWidth: 1100, minHeight: 720)
                #endif
                .preferredColorScheme(.dark)
                .tint(Theme.arc)
                .task {
                    // macOS launches/adopts its local sidecar. iOS/iPadOS instead
                    // connect to the server configured in the connection sheet.
                    await sidecar.start()
                    await api.waitUntilHealthy()
                }
        }
        #if os(macOS)
        .windowStyle(.titleBar)
        .windowToolbarStyle(.unified)
        #endif
    }
}
