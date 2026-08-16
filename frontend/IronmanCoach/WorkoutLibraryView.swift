import SwiftUI

/// Workout library + detail. Lists planned or completed workouts; selecting
/// one shows full detail.
struct WorkoutLibraryView: View {
    @EnvironmentObject var api: APIClient
    @State private var mode: Mode = .done
    @State private var workouts: [PlannedWorkout] = []
    @State private var activities: [Activity] = []
    @State private var selectedWorkout: PlannedWorkout?
    @State private var selectedActivity: Activity?

    enum Mode: String, CaseIterable { case done = "Abgeschlossen", planned = "Geplant" }

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                HUDSegmentedPicker(selection: $mode, options: [
                    (.done, "Abgeschlossen"), (.planned, "Geplant"),
                ])
                Spacer()
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 10)

            Rectangle().fill(Theme.line).frame(height: 1)

            libraryContent
        }
        .task { await load() }
        .onChange(of: mode) { _ in Task { await load() } }
    }

    @ViewBuilder
    private var libraryContent: some View {
        #if os(macOS)
        HSplitView {
            workoutList

            Group {
                if mode == .done, let a = selectedActivity {
                    ActivityDetail(activity: a)
                } else if mode == .planned, let w = selectedWorkout {
                    WorkoutDetail(workout: w)
                } else {
                    emptySelection
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
        #else
        NavigationStack {
            Group {
                if mode == .done {
                    List(activities) { activity in
                        NavigationLink {
                            ActivityDetail(activity: activity)
                        } label: {
                            ActivityRow(activity: activity)
                        }
                    }
                } else {
                    List(workouts) { workout in
                        NavigationLink {
                            WorkoutDetail(workout: workout)
                        } label: {
                            WorkoutRow(workout: workout)
                        }
                    }
                }
            }
            .scrollContentBackground(.hidden)
            .background(Theme.bgRaised)
            .navigationTitle("Workouts")
            .navigationBarTitleDisplayMode(.inline)
        }
        #endif
    }

    #if os(macOS)
    private var workoutList: some View {
        Group {
            if mode == .done {
                List(activities, selection: Binding(
                    get: { selectedActivity?.id },
                    set: { id in selectedActivity = activities.first { $0.id == id } }
                )) { a in
                    ActivityRow(activity: a).tag(a.id)
                }
            } else {
                List(workouts, selection: Binding(
                    get: { selectedWorkout?.id },
                    set: { id in selectedWorkout = workouts.first { $0.id == id } }
                )) { w in
                    WorkoutRow(workout: w).tag(w.id)
                }
            }
        }
        .scrollContentBackground(.hidden)
        .background(Theme.bgRaised)
        .frame(minWidth: 280)
    }

    private var emptySelection: some View {
        VStack(spacing: 10) {
            Image(systemName: "list.bullet.rectangle")
                .font(.system(size: 30))
                .foregroundStyle(Theme.inkDim)
            TechLabel(mode == .done ? "Aktivität wählen" : "Workout wählen")
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
    #endif

    private func load() async {
        let cal = Calendar.current
        let f = DateFormatter(); f.dateFormat = "yyyy-MM-dd"
        if mode == .done {
            let start = cal.date(byAdding: .day, value: -60, to: Date())!
            let fetched = await api.activities(start: f.string(from: start), end: f.string(from: Date()))
            // Neueste zuerst: zuletzt absolvierte Aktivität ganz oben.
            activities = fetched.sorted { $0.date > $1.date }
        } else {
            let start = cal.date(byAdding: .day, value: -14, to: Date())!
            let end = cal.date(byAdding: .day, value: 28, to: Date())!
            workouts = await api.plan(start: f.string(from: start), end: f.string(from: end))
        }
    }
}

private struct ActivityRow: View {
    let activity: Activity
    var body: some View {
        HStack(spacing: 10) {
            Image(systemName: activity.sport.symbol)
                .foregroundStyle(activity.sport.color).frame(width: 22)
            VStack(alignment: .leading, spacing: 2) {
                Text(activity.title ?? activity.sport.label)
                    .font(.system(size: 13, weight: .medium))
                    .foregroundStyle(Theme.ink).lineLimit(1)
                HStack(spacing: 6) {
                    Text(activity.date)
                    if let d = activity.duration_min { Text("· \(Int(d))′") }
                    if let km = activity.distance_km { Text(String(format: "· %.1f km", km)) }
                }
                .font(.system(size: 10, design: .monospaced))
                .foregroundStyle(Theme.inkDim)
            }
            Spacer()
            if let hr = activity.avg_hr {
                HStack(spacing: 3) {
                    Image(systemName: "heart.fill").font(.system(size: 8))
                        .foregroundStyle(Theme.arc)
                    Text("\(hr)")
                        .font(.system(size: 10, design: .monospaced))
                        .foregroundStyle(Theme.inkDim)
                }
            }
        }
        .padding(.vertical, 2)
    }
}

private struct ActivityDetail: View {
    let activity: Activity
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                HStack(spacing: 14) {
                    SchematicIcon(symbol: activity.sport.symbol, color: activity.sport.color)
                    VStack(alignment: .leading, spacing: 3) {
                        Text(activity.title ?? activity.sport.label)
                            .font(.system(size: 22, weight: .bold, design: .rounded))
                            .foregroundStyle(Theme.ink)
                        TechLabel("\(activity.sport.label) · \(activity.date)")
                    }
                }

                HStack(spacing: 12) {
                    if let d = activity.duration_min { StatTile(label: "Dauer", value: "\(Int(d))", unit: "min") }
                    if let km = activity.distance_km { StatTile(label: "Distanz", value: String(format: "%.1f", km), unit: "km") }
                    if let hr = activity.avg_hr { StatTile(label: "Ø Puls", value: "\(hr)", unit: "bpm", accent: Theme.arc) }
                    if let load = activity.training_load { StatTile(label: "Load", value: String(format: "%.0f", load), unit: "", accent: Theme.gold) }
                }

                Spacer()
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(20)
        }
    }
}

private struct WorkoutRow: View {
    let workout: PlannedWorkout
    var body: some View {
        HStack(spacing: 10) {
            Image(systemName: workout.sport.symbol)
                .foregroundStyle(workout.sport.color).frame(width: 22)
            VStack(alignment: .leading, spacing: 2) {
                Text(workout.title ?? workout.sport.label)
                    .font(.system(size: 13, weight: .medium))
                    .foregroundStyle(Theme.ink).lineLimit(1)
                HStack(spacing: 6) {
                    Text(workout.date)
                        .font(.system(size: 10, design: .monospaced))
                        .foregroundStyle(Theme.inkDim)
                    if let d = workout.duration_min {
                        Text("· \(d)′")
                            .font(.system(size: 10, design: .monospaced))
                            .foregroundStyle(Theme.inkDim)
                    }
                    if let z = HRZone.from(workout.target_zone) {
                        Text(z.rawValue)
                            .font(.system(size: 8, weight: .bold, design: .monospaced))
                            .foregroundStyle(z.color)
                            .padding(.horizontal, 5).padding(.vertical, 1)
                            .background(Capsule().fill(z.color.opacity(0.15)))
                            .overlay(Capsule().strokeBorder(z.color.opacity(0.4), lineWidth: 0.5))
                    }
                }
            }
            Spacer()
            if let p = workout.priority {
                Text(p)
                    .font(.system(size: 9, weight: .bold, design: .monospaced))
                    .foregroundStyle(Theme.gold)
                    .padding(5)
                    .background(Circle().strokeBorder(Theme.gold.opacity(0.4), lineWidth: 1))
            }
        }
        .padding(.vertical, 2)
    }
}

private struct WorkoutDetail: View {
    let workout: PlannedWorkout
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                HStack(spacing: 14) {
                    SchematicIcon(symbol: workout.sport.symbol, color: workout.sport.color)
                    VStack(alignment: .leading, spacing: 3) {
                        Text(workout.title ?? workout.sport.label)
                            .font(.system(size: 22, weight: .bold, design: .rounded))
                            .foregroundStyle(Theme.ink)
                        TechLabel("\(workout.sport.label) · \(workout.date)")
                    }
                }

                HStack(spacing: 12) {
                    if let d = workout.duration_min { StatTile(label: "Dauer", value: "\(d)", unit: "min") }
                    if let km = workout.distance_km { StatTile(label: "Distanz", value: String(format: "%.1f", km), unit: "km") }
                    if let z = HRZone.from(workout.target_zone) { StatTile(label: "Zone", value: z.rawValue, unit: z.range, accent: z.color) }
                    if let p = workout.priority { StatTile(label: "Priorität", value: p, unit: "", accent: Theme.gold) }
                    if let s = workout.status { StatTile(label: "Status", value: s, unit: "") }
                }

                if let content = workout.content, !content.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        TechLabel("// Briefing", color: Theme.arc)
                        Text(content)
                            .foregroundStyle(Theme.ink)
                            .textSelection(.enabled)
                    }
                    .padding(14)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .hudPanel(brackets: false)
                }
                Spacer()
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(20)
        }
    }
}

/// Sport icon inside a graduated schematic ring, like a part detail
/// on a technical drawing.
private struct SchematicIcon: View {
    let symbol: String
    let color: Color

    var body: some View {
        ZStack {
            Circle().strokeBorder(Theme.line, lineWidth: 1)
            TickRing(count: 24, length: 0.10)
                .stroke(Theme.line, lineWidth: 1)
                .padding(3)
            Image(systemName: symbol)
                .font(.system(size: 22))
                .foregroundStyle(color)
                .arcGlow(color, radius: 6)
        }
        .frame(width: 58, height: 58)
    }
}

private struct StatTile: View {
    let label: String
    let value: String
    var unit: String = ""
    var accent: Color = Theme.arcBlue

    var body: some View {
        VStack(alignment: .leading, spacing: 3) {
            TechLabel(label, size: 8)
            HStack(alignment: .firstTextBaseline, spacing: 3) {
                Text(value)
                    .font(.system(size: 16, weight: .bold, design: .rounded))
                    .foregroundStyle(Theme.ink)
                if !unit.isEmpty {
                    Text(unit)
                        .font(.system(size: 9, design: .monospaced))
                        .foregroundStyle(Theme.inkDim)
                }
            }
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .hudPanel(accent: accent, brackets: false)
    }
}
