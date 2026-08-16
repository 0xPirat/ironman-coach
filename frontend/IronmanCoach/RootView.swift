import SwiftUI

enum AppSection: String, CaseIterable, Identifiable {
    case dashboard = "Dashboard"
    case goals = "Ziele"
    case calendar = "Kalender"
    case workouts = "Workouts"
    case checkin = "Check-in"
    var id: String { rawValue }

    var symbol: String {
        switch self {
        case .dashboard: return "chart.xyaxis.line"
        case .goals:     return "trophy.fill"
        case .calendar:  return "calendar"
        case .workouts:  return "list.bullet.rectangle"
        case .checkin:   return "checklist"
        }
    }

    /// Module code shown as blueprint annotation next to the nav entry.
    var code: String {
        switch self {
        case .dashboard: return "SYS.01"
        case .goals:     return "TGT.02"
        case .calendar:  return "PLN.03"
        case .workouts:  return "LOG.04"
        case .checkin:   return "BIO.05"
        }
    }
}

struct RootView: View {
    @EnvironmentObject var sidecar: SidecarManager
    @EnvironmentObject var api: APIClient
    @State private var selection: AppSection = .dashboard
    @State private var syncState: SyncState = .idle
    @State private var showingConnectionSettings = false
    @Namespace private var sidebarNS

    enum SyncState {
        case idle, running, done(String), failed(String)
        var isRunning: Bool { if case .running = self { return true }; return false }
    }

    /// Garmin itself only refreshes when the watch uploads, so polling harder
    /// than this buys nothing but Garmin API calls.
    private static let syncIntervalSeconds: UInt64 = 30 * 60

    @ViewBuilder
    var body: some View {
        #if os(iOS)
        mobileBody
        #else
        desktopBody
        #endif
    }

    #if os(macOS)
    private var desktopBody: some View {
        NavigationSplitView {
            sidebar
                .navigationSplitViewColumnWidth(min: 190, ideal: 210)
        } detail: {
            // Main content + persistent chat panel docked on the right.
            HStack(spacing: 0) {
                detailContent
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    .background(BlueprintBackground())
                Rectangle().fill(Theme.line).frame(width: 1)
                ChatPanel()
                    .frame(width: 380)
            }
        }
        .navigationTitle("Sport Coach")
        .background(Theme.bg)
        .task {
            // Sync on launch, then keep syncing while the window is open.
            // Opening the app should be enough to be current, and leaving it
            // open shouldn't mean silently drifting out of date. The sidebar
            // button stays for forcing one in between.
            await api.waitUntilHealthy()
            while !Task.isCancelled {
                if !syncState.isRunning {
                    syncState = .running
                    let result = await api.syncGarmin()
                    syncState = result.hasPrefix("Sync OK") ? .idle : .failed(result)
                }
                try? await Task.sleep(nanoseconds: Self.syncIntervalSeconds * 1_000_000_000)
            }
        }
        .sheet(isPresented: $showingConnectionSettings) {
            NavigationStack {
                ConnectionSettingsView()
                    .environmentObject(api)
            }
            .frame(minWidth: 520, minHeight: 360)
        }
    }
    #else
    private var mobileBody: some View {
        VStack(spacing: 0) {
            mobileConnectionBar
            Rectangle().fill(Theme.line).frame(height: 1)
            TabView {
                DashboardView()
                    .tabItem { Label("Übersicht", systemImage: "chart.xyaxis.line") }
                GoalsView()
                    .tabItem { Label("Ziele", systemImage: "trophy.fill") }
                CalendarView()
                    .tabItem { Label("Kalender", systemImage: "calendar") }
                WorkoutLibraryView()
                    .tabItem { Label("Workouts", systemImage: "list.bullet.rectangle") }
                CheckinView()
                    .tabItem { Label("Check-in", systemImage: "checklist") }
                ChatPanel()
                    .tabItem { Label("Coach", systemImage: "bubble.left.and.bubble.right.fill") }
            }
        }
        .background(Theme.bg)
        .sheet(isPresented: $showingConnectionSettings) {
            NavigationStack {
                ConnectionSettingsView()
                    .environmentObject(api)
            }
        }
        .task {
            if !api.hasServerConfiguration {
                showingConnectionSettings = true
                return
            }
            await api.waitUntilHealthy(timeout: 5)
        }
    }

    private var mobileConnectionBar: some View {
        HStack(spacing: 10) {
            ArcReactor(size: 28, coreColor: Theme.arc, spinning: api.healthy,
                       intensity: api.healthy ? 1 : 0.25)
            VStack(alignment: .leading, spacing: 1) {
                Text("IRONMAN COACH")
                    .font(.system(size: 13, weight: .heavy, design: .rounded))
                    .foregroundStyle(Theme.ink)
                TechLabel(api.healthy ? "Server verbunden" : "Server offline", color: api.healthy ? Theme.ok : Theme.warn, size: 8)
            }
            Spacer()
            Button {
                showingConnectionSettings = true
            } label: {
                Image(systemName: "gearshape.fill")
                    .foregroundStyle(Theme.ink)
                    .padding(8)
                    .background(Circle().fill(Theme.panel))
            }
            .accessibilityLabel("Backend-Verbindung einstellen")
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 8)
        .background(Theme.bgRaised)
    }
    #endif

    // MARK: Sidebar

    private var sidebar: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Wordmark with a miniature arc reactor
            HStack(spacing: 10) {
                ArcReactor(size: 30, coreColor: Theme.arc)
                VStack(alignment: .leading, spacing: 2) {
                    TechLabel("Mark 01 // Trainer", color: Theme.gold)
                    (Text("IRONMAN")
                        .foregroundStyle(Theme.ink)
                    + Text("COACH")
                        .foregroundStyle(Theme.arc))
                        .font(.system(size: 16, weight: .heavy, design: .rounded))
                        .lineLimit(1)
                        .minimumScaleFactor(0.7)
                }
            }
            .padding(.horizontal, 16)
            .padding(.top, 14)
            .padding(.bottom, 18)

            ForEach(AppSection.allCases) { s in
                SidebarItem(section: s, active: selection == s, ns: sidebarNS) {
                    withAnimation(.spring(response: 0.35, dampingFraction: 0.8)) {
                        selection = s
                    }
                }
            }

            Spacer()
            statusFooter
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .background(Theme.bgRaised)
    }

    @ViewBuilder private var detailContent: some View {
        switch selection {
        case .dashboard: DashboardView()
        case .goals:     GoalsView()
        case .calendar:  CalendarView()
        case .workouts:  WorkoutLibraryView()
        case .checkin:   CheckinView()
        }
    }

    private var statusFooter: some View {
        VStack(alignment: .leading, spacing: 8) {
            Rectangle().fill(Theme.line).frame(height: 1)
            HStack(spacing: 7) {
                GlowDot(color: sidecarColor)
                TechLabel(sidecarLabel, size: 9)
            }
            Button {
                guard !syncState.isRunning else { return }
                syncState = .running
                Task {
                    let result = await api.syncGarmin()
                    if result.hasPrefix("Sync OK") {
                        syncState = .done(result)
                        try? await Task.sleep(nanoseconds: 4_000_000_000)
                    } else {
                        syncState = .failed(result)
                        try? await Task.sleep(nanoseconds: 12_000_000_000)
                    }
                    syncState = .idle
                }
            } label: {
                HStack(spacing: 6) {
                    if syncState.isRunning {
                        ProgressView().controlSize(.mini).scaleEffect(0.7)
                    } else {
                        Image(systemName: "arrow.triangle.2.circlepath")
                            .font(.system(size: 10, weight: .bold))
                    }
                    Text(syncButtonLabel)
                        .font(.system(size: 10, weight: .semibold, design: .monospaced))
                }
                .foregroundStyle(syncForeground)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 6)
                .background(RoundedRectangle(cornerRadius: 5).fill(Theme.panel))
                .overlay(RoundedRectangle(cornerRadius: 5).strokeBorder(Theme.line, lineWidth: 1))
            }
            .buttonStyle(.plain)
            .disabled(syncState.isRunning)

            Button {
                showingConnectionSettings = true
            } label: {
                Label("Verbindung", systemImage: "network")
                    .font(.system(size: 10, weight: .semibold, design: .monospaced))
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 6)
            }
            .buttonStyle(.plain)

            if case .failed(let msg) = syncState {
                TechLabel(String(msg.prefix(120)), color: Theme.warn, size: 8)
                    .lineLimit(3)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .padding(12)
    }

    private var syncButtonLabel: String {
        switch syncState {
        case .idle:         return "GARMIN SYNC"
        case .running:      return "SYNC LÄUFT…"
        case .done:         return "SYNC OK"
        case .failed:       return "SYNC FEHLER"
        }
    }

    private var syncForeground: Color {
        switch syncState {
        case .idle, .running: return Theme.ink
        case .done:           return Theme.ok
        case .failed:         return Theme.arc
        }
    }

    private var sidecarColor: Color {
        switch sidecar.state {
        case .running where api.healthy: return Theme.ok
        case .running, .starting: return Theme.warn
        case .failed: return Theme.arc
        case .idle: return Theme.inkDim
        }
    }

    private var sidecarLabel: String {
        switch sidecar.state {
        case .idle: return "Sidecar: aus"
        case .starting: return "Sidecar: startet…"
        case .running: return api.healthy ? "Coach online" : "Verbinde…"
        case .failed(let m): return "Fehler: \(m)"
        }
    }
}

private struct SidebarItem: View {
    let section: AppSection
    let active: Bool
    let ns: Namespace.ID
    let action: () -> Void
    @State private var hovering = false

    var body: some View {
        Button(action: action) {
            HStack(spacing: 10) {
                ZStack {
                    if active {
                        Rectangle()
                            .fill(Theme.arc)
                            .matchedGeometryEffect(id: "sidebar-indicator", in: ns)
                            .arcGlow(Theme.arc, radius: 4)
                    }
                }
                .frame(width: 2, height: 22)
                Image(systemName: section.symbol)
                    .font(.system(size: 13))
                    .foregroundStyle(active ? Theme.arc : Theme.inkDim)
                    .frame(width: 18)
                Text(section.rawValue)
                    .font(.system(size: 13, weight: active ? .semibold : .regular))
                    .foregroundStyle(active ? Theme.ink : Theme.inkDim)
                Spacer()
                TechLabel(section.code, color: active ? Theme.gold : Theme.inkDim.opacity(0.5), size: 8)
            }
            .padding(.trailing, 12)
            .padding(.vertical, 7)
            .background(
                Rectangle().fill(active ? Theme.arc.opacity(0.08)
                                        : hovering ? Theme.line.opacity(0.5) : Color.clear)
            )
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .onHover { hovering = $0 }
    }
}
