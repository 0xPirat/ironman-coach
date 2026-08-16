import SwiftUI

/// Manage athletic goals — add, edit, mark as achieved, delete.
struct GoalsView: View {
    @EnvironmentObject var api: APIClient
    @State private var goals: [AthleteGoal] = []
    @State private var showAdd = false
    @State private var filterStatus = "active"

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            header
            if goals.isEmpty {
                emptyState
            } else {
                goalList
            }
        }
        .task { await reload() }
        .sheet(isPresented: $showAdd, onDismiss: { Task { await reload() } }) {
            AddGoalSheet(api: api)
        }
    }

    // MARK: - Subviews

    private var header: some View {
        HStack(alignment: .bottom, spacing: 16) {
            HUDHeader(eyebrow: "Missionen", title: "Ziele", code: "TGT.02")
            HUDSegmentedPicker(selection: $filterStatus, options: [
                ("active", "Aktiv"), ("all", "Alle"), ("achieved", "Erreicht"),
            ])
            .onChange(of: filterStatus) { _ in Task { await reload() } }
            Button { showAdd = true } label: {
                Label("Neues Ziel", systemImage: "plus")
            }
            .buttonStyle(HUDButtonStyle(prominent: true))
        }
        .padding(20)
    }

    private var emptyState: some View {
        VStack(spacing: 10) {
            Image(systemName: "trophy")
                .font(.system(size: 34))
                .foregroundStyle(Theme.gold)
                .arcGlow(Theme.gold)
            Text(filterStatus == "active" ? "Keine aktiven Ziele" : "Keine Ziele")
                .font(.system(size: 16, weight: .bold, design: .rounded))
                .foregroundStyle(Theme.ink)
            TechLabel(filterStatus == "active"
                ? "Füge dein erstes Ziel hinzu — der Coach plant darauf hin"
                : "Noch keine Ziele vorhanden")
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    private var goalList: some View {
        ScrollView {
            LazyVStack(spacing: 12) {
                ForEach(goals) { goal in
                    GoalCard(goal: goal, onAchieved: {
                        Task {
                            await api.updateGoalStatus(id: goal.id, status: "achieved")
                            await reload()
                        }
                    }, onDelete: {
                        Task {
                            await api.deleteGoal(id: goal.id)
                            await reload()
                        }
                    })
                }
            }
            .padding(20)
        }
    }

    private func reload() async {
        goals = await api.goals(status: filterStatus)
    }
}

// MARK: - GoalCard

private struct GoalCard: View {
    let goal: AthleteGoal
    let onAchieved: () -> Void
    let onDelete: () -> Void

    private var isPrimary: Bool { (goal.priority ?? 2) == 1 }

    var body: some View {
        HStack(alignment: .top, spacing: 16) {
            // Sport icon in a schematic frame
            ZStack {
                RoundedRectangle(cornerRadius: 8)
                    .fill(goal.sportColor.opacity(0.12))
                    .frame(width: 48, height: 48)
                RoundedRectangle(cornerRadius: 8)
                    .strokeBorder(goal.sportColor.opacity(0.4), lineWidth: 1)
                    .frame(width: 48, height: 48)
                Image(systemName: goal.sportSymbol)
                    .font(.title2)
                    .foregroundStyle(goal.sportColor)
                    .arcGlow(goal.sportColor, radius: 6)
            }

            VStack(alignment: .leading, spacing: 5) {
                HStack {
                    Text(goal.title)
                        .font(.system(size: 14, weight: .bold, design: .rounded))
                        .foregroundStyle(Theme.ink)
                    Spacer()
                    TechLabel(goal.priorityLabel, color: isPrimary ? Theme.gold : Theme.inkDim, size: 9)
                }
                HStack(spacing: 8) {
                    SportBadge(name: Sport(rawValue: goal.sport)?.label ?? goal.sport,
                               color: goal.sportColor)
                    if let metric = goal.target_metric, !metric.isEmpty {
                        TechLabel("Ziel: \(metric)", size: 9)
                    }
                    if let date = goal.event_date {
                        HStack(spacing: 3) {
                            Image(systemName: "calendar").font(.system(size: 8))
                            TechLabel(formatDate(date), color: Theme.gold, size: 9)
                        }
                        .foregroundStyle(Theme.gold)
                    }
                }
                if let desc = goal.description, !desc.isEmpty {
                    Text(desc).font(.callout).foregroundStyle(Theme.inkDim)
                        .lineLimit(2)
                }
            }

            Spacer()

            if goal.status == "active" {
                Menu {
                    Button("Als erreicht markieren ✅", action: onAchieved)
                    Divider()
                    Button("Löschen", role: .destructive, action: onDelete)
                } label: {
                    Image(systemName: "ellipsis.circle")
                        .foregroundStyle(Theme.inkDim)
                }
                .buttonStyle(.borderless)
            } else {
                Text(statusLabel(goal.status ?? ""))
                    .font(.system(size: 10, weight: .semibold, design: .monospaced))
                    .foregroundStyle(statusColor(goal.status ?? ""))
                    .padding(.horizontal, 8).padding(.vertical, 3)
                    .background(Capsule().fill(statusColor(goal.status ?? "").opacity(0.14)))
                    .overlay(Capsule().strokeBorder(statusColor(goal.status ?? "").opacity(0.35), lineWidth: 1))
            }
        }
        .padding(16)
        .hudPanel(accent: isPrimary ? Theme.gold : Theme.arc, brackets: isPrimary)
    }

    private func formatDate(_ iso: String) -> String {
        let df = DateFormatter()
        df.dateFormat = "yyyy-MM-dd"
        guard let d = df.date(from: iso) else { return iso }
        df.dateStyle = .medium; df.dateFormat = nil
        return df.string(from: d)
    }

    private func statusLabel(_ s: String) -> String {
        switch s {
        case "achieved": return "✓ ERREICHT"
        case "paused":   return "⏸ PAUSIERT"
        case "abandoned": return "✕ AUFGEGEBEN"
        default: return s.uppercased()
        }
    }

    private func statusColor(_ s: String) -> Color {
        switch s {
        case "achieved": return Theme.ok
        case "paused":   return Theme.warn
        case "abandoned": return Theme.arc
        default: return Theme.inkDim
        }
    }
}

private struct SportBadge: View {
    let name: String
    let color: Color
    var body: some View {
        Text(name.uppercased())
            .font(.system(size: 9, weight: .bold, design: .monospaced))
            .kerning(0.6)
            .foregroundStyle(color)
            .padding(.horizontal, 8).padding(.vertical, 2)
            .background(Capsule().fill(color.opacity(0.1)))
            .overlay(Capsule().strokeBorder(color.opacity(0.35), lineWidth: 1))
    }
}

// MARK: - AddGoalSheet

struct AddGoalSheet: View {
    let api: APIClient
    @Environment(\.dismiss) var dismiss

    @State private var title = ""
    @State private var sport: Sport = .run
    @State private var category = "endurance"
    @State private var eventDate: Date? = nil
    @State private var hasEventDate = false
    @State private var targetMetric = ""
    @State private var description = ""
    @State private var priority = 2
    @State private var saving = false

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Header
            HStack {
                VStack(alignment: .leading, spacing: 2) {
                    TechLabel("// Neue Mission", color: Theme.arc)
                    Text("Neues Ziel")
                        .font(.system(size: 18, weight: .bold, design: .rounded))
                        .foregroundStyle(Theme.ink)
                }
                Spacer()
                Button("Abbrechen") { dismiss() }.buttonStyle(HUDButtonStyle())
            }
            .padding(20)
            Rectangle().fill(Theme.line).frame(height: 1)

            Form {
                Section("Ziel") {
                    TextField("Titel (z. B. Ironman Frankfurt 2026)", text: $title)
                    Picker("Sportart", selection: $sport) {
                        ForEach(Sport.allCases) { s in
                            Label(s.label, systemImage: s.symbol).tag(s)
                        }
                    }
                    Picker("Priorität", selection: $priority) {
                        Text("⭐ Primärziel").tag(1)
                        Text("Sekundärziel").tag(2)
                        Text("Hintergrundprojekt").tag(3)
                    }
                }
                Section("Details (optional)") {
                    TextField("Ziel-Metrik (z. B. sub-10h, sub-4h Marathon)", text: $targetMetric)
                    Toggle("Event-Datum", isOn: $hasEventDate)
                    if hasEventDate {
                        DatePicker("Datum", selection: Binding(
                            get: { eventDate ?? Date() },
                            set: { eventDate = $0 }
                        ), displayedComponents: .date)
                    }
                    TextField("Beschreibung", text: $description, axis: .vertical)
                        .lineLimit(3...5)
                }
            }
            .formStyle(.grouped)
            .scrollContentBackground(.hidden)
            .background(Theme.bgRaised)

            Rectangle().fill(Theme.line).frame(height: 1)
            HStack {
                Spacer()
                Button("Ziel speichern") {
                    saving = true
                    Task {
                        let df = DateFormatter(); df.dateFormat = "yyyy-MM-dd"
                        let goal = AthleteGoal(
                            id: 0,
                            title: title,
                            sport: sport.rawValue,
                            category: category,
                            event_date: hasEventDate && eventDate != nil ? df.string(from: eventDate!) : nil,
                            description: description.isEmpty ? nil : description,
                            target_metric: targetMetric.isEmpty ? nil : targetMetric,
                            priority: priority,
                            status: "active"
                        )
                        await api.createGoal(goal)
                        saving = false
                        dismiss()
                    }
                }
                .buttonStyle(HUDButtonStyle(prominent: true))
                .disabled(title.isEmpty || saving)
            }
            .padding(20)
        }
        .frame(width: 480)
        .background(Theme.bgRaised)
    }
}
