import Foundation
import Combine

/// Spawns and supervises the Python FastAPI sidecar as a child process on macOS.
/// iOS/iPadOS cannot execute bundled Python processes, so those platforms use
/// the configurable backend endpoint managed by `APIClient` instead.
///
/// Resolution order for how to launch the sidecar:
///  1. A bundled venv inside the .app (Resources/sidecar/venv) — for a shipped app.
///  2. A dev fallback: the repo's `.venv` + `backend.main` (works when running
///     from Xcode during development). Configure via the IRONMAN_REPO env var or
///     the default path below.
@MainActor
final class SidecarManager: ObservableObject {
    @Published var state: State = .idle
    @Published var lastLog: String = ""

    enum State: Equatable { case idle, starting, running, failed(String) }

    static let host = "127.0.0.1"
    static let port = 8765

    #if os(macOS)
    private var process: Process?

    /// Edit this if your repo lives elsewhere. Used only in the dev fallback.
    private let devRepoPath = "\(NSHomeDirectory())/ironman-coach"

    func start() async {
        guard process == nil else { return }
        state = .starting

        // If a healthy sidecar is already listening on the port (an orphan from a
        // previous run, or a manually-started dev instance), adopt it instead of
        // spawning a second uvicorn — a second bind on the same port exits code 1
        // and surfaces a spurious "Sidecar exited" error.
        if await isHealthy() {
            lastLog = "Bestehenden Sidecar auf Port \(Self.port) übernommen."
            state = .running
            return
        }

        let (executableURL, arguments, workingDir, env) = resolveLaunch()
        guard let executableURL else {
            state = .failed("Sidecar interpreter not found. See README / dev fallback path.")
            return
        }

        let proc = Process()
        proc.executableURL = executableURL
        proc.arguments = arguments
        proc.currentDirectoryURL = workingDir
        proc.environment = env

        let pipe = Pipe()
        proc.standardOutput = pipe
        proc.standardError = pipe
        pipe.fileHandleForReading.readabilityHandler = { [weak self] handle in
            let data = handle.availableData
            guard !data.isEmpty, let line = String(data: data, encoding: .utf8) else { return }
            Task { @MainActor in self?.lastLog = line }
        }

        proc.terminationHandler = { [weak self] p in
            Task { @MainActor in
                if p.terminationStatus != 0 {
                    self?.state = .failed("Sidecar exited (code \(p.terminationStatus)).")
                }
                self?.process = nil
            }
        }

        do {
            try proc.run()
            process = proc
            state = .running
        } catch {
            state = .failed("Failed to launch sidecar: \(error.localizedDescription)")
        }
    }

    func stop() {
        process?.terminate()
        process = nil
        state = .idle
    }

    /// Quick probe: is a sidecar already serving /health on the port?
    private func isHealthy() async -> Bool {
        guard let url = URL(string: "http://\(Self.host):\(Self.port)/health") else { return false }
        var req = URLRequest(url: url)
        req.timeoutInterval = 1.5
        do {
            let (data, resp) = try await URLSession.shared.data(for: req)
            guard let http = resp as? HTTPURLResponse, http.statusCode == 200 else { return false }
            return String(data: data, encoding: .utf8)?.contains("ok") ?? true
        } catch {
            return false
        }
    }

    // MARK: - Launch resolution

    private func resolveLaunch() -> (URL?, [String], URL, [String: String]) {
        var env = ProcessInfo.processInfo.environment
        // CRITICAL: force subscription auth — never let a stray API key bill the API.
        env.removeValue(forKey: "ANTHROPIC_API_KEY")

        let args = ["-m", "uvicorn", "backend.main:app",
                    "--host", Self.host, "--port", "\(Self.port)"]

        // 1) Bundled venv inside the .app (shipped layout).
        if let resourceURL = Bundle.main.resourceURL {
            let bundledRepo = resourceURL.appendingPathComponent("sidecar")
            let bundledPython = bundledRepo.appendingPathComponent("venv/bin/python")
            if FileManager.default.fileExists(atPath: bundledPython.path) {
                env["PYTHONPATH"] = bundledRepo.path
                return (bundledPython, args, bundledRepo, env)
            }
        }

        // 2) Dev fallback: repo .venv.
        let repo = ProcessInfo.processInfo.environment["IRONMAN_REPO"] ?? devRepoPath
        let devPython = URL(fileURLWithPath: "\(repo)/.venv/bin/python")
        if FileManager.default.fileExists(atPath: devPython.path) {
            env["PYTHONPATH"] = repo
            return (devPython, args, URL(fileURLWithPath: repo), env)
        }

        return (nil, args, URL(fileURLWithPath: repo), env)
    }
    #else
    func start() async {
        state = .idle
        lastLog = "Auf iPhone und iPad wird ein externer Coach-Server verwendet."
    }

    func stop() {
        state = .idle
    }
    #endif
}
