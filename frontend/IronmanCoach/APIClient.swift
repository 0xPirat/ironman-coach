import Foundation
import Combine
import Security

/// Talks to the Python backend. On macOS the default is the local sidecar;
/// iPhone and iPad users configure the Mac/LAN or HTTPS endpoint in the app.
@MainActor
final class APIClient: ObservableObject {
    @Published var healthy = false

    /// Kept outside the app bundle so the same open-source build can connect to
    /// different self-hosted backends. The bearer token itself lives in Keychain.
    @Published private(set) var serverURLString: String

    /// Bumped after every successful Garmin sync. Views key their reload on it
    /// so fresh rows reach the screen without the user navigating away and back.
    @Published var dataVersion = 0

    private let session = URLSession(configuration: .default)

    private static let serverURLDefaultsKey = "coach.backendURL"
    private static let tokenService = "com.johannesbenedict.ironmancoach.backend"
    private static let tokenAccount = "bearer-token"

    init() {
        if let saved = UserDefaults.standard.string(forKey: Self.serverURLDefaultsKey),
           !saved.isEmpty {
            serverURLString = saved
        } else {
            #if os(macOS)
            serverURLString = "http://\(SidecarManager.host):\(SidecarManager.port)"
            #else
            serverURLString = ""
            #endif
        }
    }

    var hasServerConfiguration: Bool { endpoint("health") != nil }

    var savedToken: String {
        SecureTokenStore.read(service: Self.tokenService, account: Self.tokenAccount) ?? ""
    }

    /// Validates and persists a backend endpoint. HTTP is accepted for a trusted
    /// local LAN; public/remote deployments should always use HTTPS.
    @discardableResult
    func configureServer(url rawURL: String, token: String) -> Bool {
        let trimmed = rawURL.trimmingCharacters(in: .whitespacesAndNewlines)
            .trimmingCharacters(in: CharacterSet(charactersIn: "/"))
        guard let components = URLComponents(string: trimmed),
              ["http", "https"].contains(components.scheme?.lowercased() ?? ""),
              components.host != nil else { return false }

        serverURLString = trimmed
        UserDefaults.standard.set(trimmed, forKey: Self.serverURLDefaultsKey)
        SecureTokenStore.write(token.trimmingCharacters(in: .whitespacesAndNewlines),
                               service: Self.tokenService,
                               account: Self.tokenAccount)
        healthy = false
        return true
    }

    private func endpoint(_ path: String) -> URL? {
        guard !serverURLString.isEmpty,
              let base = URL(string: serverURLString) else { return nil }
        return base.appendingPathComponent(path)
    }

    private func authorizedRequest(url: URL) -> URLRequest {
        var request = URLRequest(url: url)
        let token = savedToken
        if !token.isEmpty {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        return request
    }

    // MARK: - Health

    func waitUntilHealthy(timeout: TimeInterval = 20) async {
        let deadline = Date().addingTimeInterval(timeout)
        while Date() < deadline {
            if await ping() { healthy = true; return }
            try? await Task.sleep(nanoseconds: 500_000_000)
        }
        healthy = false
    }

    func ping() async -> Bool {
        guard let url = endpoint("health") else { return false }
        var req = authorizedRequest(url: url)
        req.timeoutInterval = 2
        guard let (_, resp) = try? await session.data(for: req),
              let http = resp as? HTTPURLResponse, http.statusCode == 200 else { return false }
        return true
    }

    // MARK: - Generic GET

    private func get<T: Decodable>(_ path: String, query: [String: String] = [:]) async throws -> T {
        guard let endpoint = endpoint(path),
              var comps = URLComponents(url: endpoint, resolvingAgainstBaseURL: false) else {
            throw URLError(.badURL)
        }
        if !query.isEmpty { comps.queryItems = query.map { URLQueryItem(name: $0.key, value: $0.value) } }
        guard let url = comps.url else { throw URLError(.badURL) }
        let (data, response) = try await session.data(for: authorizedRequest(url: url))
        guard let http = response as? HTTPURLResponse,
              (200...299).contains(http.statusCode) else { throw URLError(.badServerResponse) }
        return try JSONDecoder().decode(T.self, from: data)
    }

    func plan(start: String? = nil, end: String? = nil) async -> [PlannedWorkout] {
        var q: [String: String] = [:]; if let start { q["start"] = start }; if let end { q["end"] = end }
        return (try? await get("plan", query: q)) ?? []
    }

    func metrics(start: String? = nil, end: String? = nil) async -> [DailyMetric] {
        var q: [String: String] = [:]; if let start { q["start"] = start }; if let end { q["end"] = end }
        return (try? await get("metrics", query: q)) ?? []
    }

    func activities(start: String? = nil, end: String? = nil) async -> [Activity] {
        var q: [String: String] = [:]; if let start { q["start"] = start }; if let end { q["end"] = end }
        return (try? await get("activities", query: q)) ?? []
    }

    func chatHistory(limit: Int = 50) async -> [ChatMessage] {
        struct Row: Codable { let role: String; let content: String }
        let rows: [Row] = (try? await get("chat/history", query: ["limit": "\(limit)"])) ?? []
        return rows.map { ChatMessage(role: .init(rawValue: $0.role) ?? .assistant, content: $0.content) }
    }

    // MARK: - Check-in

    func saveCheckin(_ c: Checkin) async -> Bool {
        guard let body = try? JSONEncoder().encode(c) else { return false }
        guard let url = endpoint("checkin") else { return false }
        var req = authorizedRequest(url: url)
        req.httpMethod = "POST"
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = body
        guard let (_, resp) = try? await session.data(for: req),
              let http = resp as? HTTPURLResponse else { return false }
        return (200...299).contains(http.statusCode)
    }

    // MARK: - Goals

    func goals(status: String = "active") async -> [AthleteGoal] {
        return (try? await get("goals", query: ["status": status])) ?? []
    }

    func createGoal(_ goal: AthleteGoal) async -> Bool {
        struct GoalBody: Encodable {
            var title: String; var sport: String; var category: String?
            var event_date: String?; var description: String?
            var target_metric: String?; var priority: Int?; var status: String?
        }
        let body = GoalBody(title: goal.title, sport: goal.sport,
                            category: goal.category, event_date: goal.event_date,
                            description: goal.description, target_metric: goal.target_metric,
                            priority: goal.priority, status: goal.status)
        guard let data = try? JSONEncoder().encode(body) else { return false }
        guard let url = endpoint("goals") else { return false }
        var req = authorizedRequest(url: url)
        req.httpMethod = "POST"
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = data
        guard let (_, resp) = try? await session.data(for: req),
              let http = resp as? HTTPURLResponse else { return false }
        return (200...299).contains(http.statusCode)
    }

    func updateGoalStatus(id: Int, status: String) async -> Bool {
        guard let body = try? JSONSerialization.data(withJSONObject: ["status": status]) else { return false }
        guard let url = endpoint("goals/\(id)") else { return false }
        var req = authorizedRequest(url: url)
        req.httpMethod = "PATCH"
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = body
        guard let (_, resp) = try? await session.data(for: req),
              let http = resp as? HTTPURLResponse else { return false }
        return (200...299).contains(http.statusCode)
    }

    func deleteGoal(id: Int) async -> Bool {
        guard let url = endpoint("goals/\(id)") else { return false }
        var req = authorizedRequest(url: url)
        req.httpMethod = "DELETE"
        guard let (_, resp) = try? await session.data(for: req),
              let http = resp as? HTTPURLResponse else { return false }
        return (200...299).contains(http.statusCode)
    }

    // MARK: - Weather

    func weather(refresh: Bool = false) async -> WeatherSummary? {
        try? await get("weather", query: refresh ? ["refresh": "true"] : [:])
    }

    // MARK: - Garmin sync

    /// Manual sync covers the last 7 days — the 7:30 daily agent backfills the
    /// rest. A sync is ~10 Garmin calls per day, so the request can run for
    /// minutes; the default 60 s timeout used to abort it mid-flight.
    func syncGarmin(days: Int = 7) async -> String {
        guard let url = endpoint("sync/garmin")?.appending(
            queryItems: [URLQueryItem(name: "days", value: "\(days)")]
        ) else { return "Sync fehlgeschlagen (Backend nicht konfiguriert)." }
        var req = authorizedRequest(url: url)
        req.httpMethod = "POST"
        req.timeoutInterval = 300

        // One retry after a short pause — bridges sidecar restarts and
        // transient network drops so a tap doesn't fail spuriously.
        for attempt in 0..<2 {
            if attempt > 0 { try? await Task.sleep(nanoseconds: 2_000_000_000) }
            guard let (data, resp) = try? await session.data(for: req),
                  let http = resp as? HTTPURLResponse else { continue }
            let body = String(data: data, encoding: .utf8) ?? ""
            if (200...299).contains(http.statusCode) {
                dataVersion += 1
                return "Sync OK: \(body)"
            }
            // 4xx = credentials/config problem; retrying won't change it.
            if (400...499).contains(http.statusCode) { return "Sync-Fehler: \(body)" }
        }
        return "Sync fehlgeschlagen (keine Verbindung zum Sidecar)."
    }

    // MARK: - Streaming chat (SSE)

    /// Streams the coach reply. `onDelta` is called on the main actor per chunk.
    func streamChat(message: String, onDelta: @escaping (String) -> Void) async {
        guard let url = endpoint("chat") else {
            onDelta("\n\n[Bitte zuerst die Backend-Verbindung konfigurieren.]")
            return
        }
        var req = authorizedRequest(url: url)
        req.httpMethod = "POST"
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = try? JSONSerialization.data(withJSONObject: ["message": message])

        do {
            let (bytes, _) = try await session.bytes(for: req)
            for try await line in bytes.lines {
                guard line.hasPrefix("data:") else { continue }
                let json = String(line.dropFirst(5)).trimmingCharacters(in: .whitespaces)
                guard let data = json.data(using: .utf8),
                      let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else { continue }
                if let delta = obj["delta"] as? String { onDelta(delta) }
                if obj["done"] as? Bool == true { break }
            }
        } catch {
            onDelta("\n\n[Verbindungsfehler zum Coach: \(error.localizedDescription)]")
        }
    }
}

private enum SecureTokenStore {
    static func read(service: String, account: String) -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne,
        ]
        var item: CFTypeRef?
        guard SecItemCopyMatching(query as CFDictionary, &item) == errSecSuccess,
              let data = item as? Data else { return nil }
        return String(data: data, encoding: .utf8)
    }

    static func write(_ token: String, service: String, account: String) {
        let identity: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
        ]
        SecItemDelete(identity as CFDictionary)
        guard !token.isEmpty, let data = token.data(using: .utf8) else { return }
        var item = identity
        item[kSecValueData as String] = data
        item[kSecAttrAccessible as String] = kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
        SecItemAdd(item as CFDictionary, nil)
    }
}
