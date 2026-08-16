import SwiftUI

/// Connection setup shared by macOS, iPhone and iPad. The URL is normal app
/// configuration; the bearer token is persisted in the system Keychain.
struct ConnectionSettingsView: View {
    @EnvironmentObject private var api: APIClient
    @Environment(\.dismiss) private var dismiss

    @State private var serverURL = ""
    @State private var token = ""
    @State private var status: Status = .idle

    private enum Status: Equatable {
        case idle, testing, success, failure(String)
    }

    var body: some View {
        Form {
            Section("Coach-Server") {
                TextField("http://192.168.1.20:8766", text: $serverURL)
                    .autocorrectionDisabled()
                SecureField("IRONMAN_MOBILE_TOKEN", text: $token)
                    .autocorrectionDisabled()

                Text("Für iPhone/iPad: Adresse des Macs im lokalen Netz und Port 8766. Für einen öffentlichen Server ausschließlich HTTPS verwenden.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }

            Section("Verbindung") {
                HStack {
                    Circle()
                        .fill(statusColor)
                        .frame(width: 9, height: 9)
                    Text(statusText)
                    Spacer()
                    if status == .testing { ProgressView() }
                }

                Button("Speichern und testen") {
                    Task { await saveAndTest() }
                }
                .disabled(status == .testing)
            }

            Section {
                Text("Der Token wird im Apple-Schlüsselbund gespeichert und nicht in das GitHub-Projekt oder die App-Dateien geschrieben.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }
        }
        .navigationTitle("Backend-Verbindung")
        .toolbar {
            ToolbarItem(placement: .confirmationAction) {
                Button("Fertig") { dismiss() }
            }
        }
        .onAppear {
            serverURL = api.serverURLString
            token = api.savedToken
            status = api.healthy ? .success : .idle
        }
    }

    @MainActor
    private func saveAndTest() async {
        guard api.configureServer(url: serverURL, token: token) else {
            status = .failure("Bitte eine vollständige HTTP- oder HTTPS-Adresse eingeben.")
            return
        }
        serverURL = api.serverURLString
        status = .testing
        await api.waitUntilHealthy(timeout: 5)
        status = api.healthy ? .success : .failure("Server nicht erreichbar oder Token ungültig.")
    }

    private var statusColor: Color {
        switch status {
        case .success: return Theme.ok
        case .testing: return Theme.warn
        case .failure: return Theme.arc
        case .idle: return Theme.inkDim
        }
    }

    private var statusText: String {
        switch status {
        case .idle: return "Noch nicht getestet"
        case .testing: return "Verbindung wird getestet …"
        case .success: return "Coach-Server erreichbar"
        case .failure(let message): return message
        }
    }
}
