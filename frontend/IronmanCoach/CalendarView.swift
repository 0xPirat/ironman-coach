import SwiftUI

/// Weekly + monthly calendar showing planned + completed sessions per sport,
/// color-coded by HR zone. Loads real data from the sidecar; renders empty
/// cleanly until data exists.
struct CalendarView: View {
    @EnvironmentObject var api: APIClient
    @State private var mode: Mode = .week
    @State private var anchor = Date()
    @State private var workouts: [PlannedWorkout] = []
    @State private var activities: [Activity] = []

    enum Mode: String, CaseIterable { case week = "Woche", month = "Monat" }

    private let cal = Calendar.current
    private let iso: DateFormatter = {
        let f = DateFormatter(); f.dateFormat = "yyyy-MM-dd"; return f
    }()

    var body: some View {
        VStack(spacing: 0) {
            toolbar
            Rectangle().fill(Theme.line).frame(height: 1)
            ScrollView {
                if mode == .week { weekGrid } else { monthGrid }
            }
        }
        .task(id: rangeKey) { await load() }
    }

    // Adaptive toolbar: single row when there is room, legend drops to a
    // second row in narrow windows instead of crushing the controls.
    private var toolbar: some View {
        ViewThatFits(in: .horizontal) {
            HStack(spacing: 12) {
                pickerAndNav
                Spacer()
                zoneLegend
            }
            VStack(alignment: .leading, spacing: 8) {
                pickerAndNav
                zoneLegend
            }
        }
        .padding(12)
    }

    private var pickerAndNav: some View {
        HStack(spacing: 12) {
            HUDSegmentedPicker(selection: $mode, options: [
                (.week, "Woche"), (.month, "Monat"),
            ])
            Button { shift(-1) } label: { Image(systemName: "chevron.left") }
                .buttonStyle(HUDButtonStyle())
            Text(rangeTitle)
                .font(.system(size: 13, weight: .semibold, design: .monospaced))
                .foregroundStyle(Theme.ink)
                .lineLimit(1)
                .fixedSize()
            Button { shift(1) } label: { Image(systemName: "chevron.right") }
                .buttonStyle(HUDButtonStyle())
            Button("Heute") { anchor = Date() }
                .buttonStyle(HUDButtonStyle())
        }
    }

    private var zoneLegend: some View {
        HStack(spacing: 8) {
            ForEach(HRZone.allCases, id: \.self) { z in
                HStack(spacing: 3) {
                    RoundedRectangle(cornerRadius: 2).fill(z.color).frame(width: 9, height: 9)
                        .arcGlow(z.color, radius: 3)
                    TechLabel(z.rawValue, size: 8)
                }
            }
        }
        .fixedSize()
    }

    // MARK: Week

    private var weekGrid: some View {
        let days = weekDays
        return LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 8), count: 7), spacing: 8) {
            ForEach(days, id: \.self) { day in
                DayColumn(date: day,
                          workouts: workouts.filter { $0.date == iso.string(from: day) },
                          activities: activities.filter { $0.date == iso.string(from: day) },
                          formatter: weekdayFormatter,
                          isToday: cal.isDateInToday(day))
            }
        }
        .padding(12)
    }

    // MARK: Month

    private var monthGrid: some View {
        let days = monthDays
        return LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 6), count: 7), spacing: 6) {
            ForEach(["Mo","Di","Mi","Do","Fr","Sa","So"], id: \.self) {
                TechLabel($0, size: 9)
            }
            ForEach(days, id: \.self) { day in
                if let day {
                    DayCell(date: day,
                            workouts: workouts.filter { $0.date == iso.string(from: day) },
                            isToday: cal.isDateInToday(day))
                } else {
                    Color.clear.frame(height: 70)
                }
            }
        }
        .padding(12)
    }

    // MARK: Data + range helpers

    private var rangeKey: String { "\(mode.rawValue)-\(iso.string(from: anchor))" }

    private func load() async {
        let (s, e) = currentRange
        async let w = api.plan(start: iso.string(from: s), end: iso.string(from: e))
        async let a = api.activities(start: iso.string(from: s), end: iso.string(from: e))
        workouts = await w
        activities = await a
    }

    private func shift(_ dir: Int) {
        let comp: Calendar.Component = mode == .week ? .weekOfYear : .month
        anchor = cal.date(byAdding: comp, value: dir, to: anchor) ?? anchor
    }

    private var currentRange: (Date, Date) {
        if mode == .week {
            let days = weekDays
            return (days.first ?? anchor, days.last ?? anchor)
        } else {
            let comps = cal.dateComponents([.year, .month], from: anchor)
            let start = cal.date(from: comps)!
            let end = cal.date(byAdding: DateComponents(month: 1, day: -1), to: start)!
            return (start, end)
        }
    }

    private var weekDays: [Date] {
        let weekday = cal.component(.weekday, from: anchor)
        // Monday-based
        let delta = (weekday + 5) % 7
        let monday = cal.date(byAdding: .day, value: -delta, to: cal.startOfDay(for: anchor))!
        return (0..<7).compactMap { cal.date(byAdding: .day, value: $0, to: monday) }
    }

    private var monthDays: [Date?] {
        let comps = cal.dateComponents([.year, .month], from: anchor)
        let first = cal.date(from: comps)!
        let range = cal.range(of: .day, in: .month, for: first)!
        let firstWeekday = (cal.component(.weekday, from: first) + 5) % 7  // 0 = Monday
        var cells: [Date?] = Array(repeating: nil, count: firstWeekday)
        for d in range { cells.append(cal.date(byAdding: .day, value: d - 1, to: first)) }
        return cells
    }

    private var rangeTitle: String {
        let f = DateFormatter(); f.locale = Locale(identifier: "de_DE")
        f.dateFormat = mode == .week ? "d. MMM yyyy" : "MMMM yyyy"
        if mode == .week {
            let days = weekDays
            return "\(f.string(from: days.first!)) – \(f.string(from: days.last!))"
        }
        return f.string(from: anchor)
    }

    private var weekdayFormatter: DateFormatter {
        let f = DateFormatter(); f.locale = Locale(identifier: "de_DE"); f.dateFormat = "EEE d."; return f
    }
}

private struct DayColumn: View {
    let date: Date
    let workouts: [PlannedWorkout]
    let activities: [Activity]
    let formatter: DateFormatter
    var isToday = false

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 5) {
                if isToday { GlowDot(color: Theme.arc) }
                TechLabel(formatter.string(from: date),
                          color: isToday ? Theme.arc : Theme.inkDim, size: 9)
            }
            ForEach(workouts) { w in WorkoutChip(workout: w) }
            ForEach(activities) { a in
                HStack(spacing: 4) {
                    Image(systemName: a.sport.symbol).font(.caption2)
                    Text("✓ \(a.sport.label)").font(.caption2)
                }
                .foregroundStyle(Theme.inkDim)
            }
            Spacer(minLength: 0)
        }
        .frame(maxWidth: .infinity, minHeight: 140, alignment: .topLeading)
        .padding(8)
        .hudPanel(accent: Theme.arc, brackets: isToday)
        .opacity(isToday ? 1 : 0.92)
    }
}

private struct WorkoutChip: View {
    let workout: PlannedWorkout
    @State private var hovering = false

    var body: some View {
        let zone = HRZone.from(workout.target_zone)
        return VStack(alignment: .leading, spacing: 2) {
            HStack(spacing: 4) {
                Image(systemName: workout.sport.symbol).font(.caption2)
                    .foregroundStyle(workout.sport.color)
                Text(workout.title ?? workout.sport.label)
                    .font(.caption2).bold().lineLimit(1)
                    .foregroundStyle(Theme.ink)
            }
            HStack(spacing: 4) {
                if let d = workout.duration_min {
                    Text("\(d)′")
                        .font(.system(size: 9, design: .monospaced))
                        .foregroundStyle(Theme.inkDim)
                }
                if let zone {
                    Text(zone.rawValue)
                        .font(.system(size: 8, weight: .bold, design: .monospaced))
                        .foregroundStyle(zone.color)
                        .padding(.horizontal, 4).padding(.vertical, 1)
                        .background(Capsule().fill(zone.color.opacity(0.15)))
                        .overlay(Capsule().strokeBorder(zone.color.opacity(0.4), lineWidth: 0.5))
                }
            }
        }
        .padding(6)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(RoundedRectangle(cornerRadius: 5).fill(workout.sport.color.opacity(hovering ? 0.20 : 0.12)))
        .overlay(RoundedRectangle(cornerRadius: 5).strokeBorder(workout.sport.color.opacity(hovering ? 0.55 : 0.3), lineWidth: 1))
        .arcGlow(hovering ? workout.sport.color : .clear, radius: hovering ? 5 : 0)
        .onHover { h in withAnimation(.easeOut(duration: 0.15)) { hovering = h } }
    }
}

private struct DayCell: View {
    let date: Date
    let workouts: [PlannedWorkout]
    var isToday = false

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text("\(Calendar.current.component(.day, from: date))")
                .font(.system(size: 10, weight: .bold, design: .monospaced))
                .foregroundStyle(isToday ? Theme.arc : Theme.inkDim)
            ForEach(workouts.prefix(3)) { w in
                Circle().fill(w.sport.color).frame(width: 6, height: 6)
                    .arcGlow(w.sport.color, radius: 3)
                    .overlay(alignment: .leading) {
                        Text(w.sport.label).font(.system(size: 8))
                            .foregroundStyle(Theme.inkDim).offset(x: 8)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
        }
        .frame(maxWidth: .infinity, minHeight: 70, alignment: .topLeading)
        .padding(4)
        .hudPanel(accent: Theme.arc, brackets: isToday)
    }
}
