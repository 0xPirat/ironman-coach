import SwiftUI
import Charts

/// Key metrics + charts: PMC (CTL/ATL/TSB), HRV trend, RHR, sleep, Body Battery,
/// Training Readiness. Uses Swift Charts. Renders cleanly with no data.
struct DashboardView: View {
    @EnvironmentObject var api: APIClient
    @State private var metrics: [DailyMetric] = []
    @State private var weather: WeatherSummary?
    @State private var ringsShown = false

    /// The backend caches for 30 min; polling every 15 min keeps the view
    /// at most ~45 min behind the Open-Meteo model — effectively always fresh.
    private static let weatherRefreshSeconds: UInt64 = 15 * 60

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                HUDHeader(eyebrow: "Telemetrie", title: "Dashboard", code: "SYS.01")

                WeatherCard(weather: weather)

                if metrics.isEmpty {
                    emptyState
                } else {
                    reactorHero
                    loadCards
                    pmcChart
                    LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 14) {
                        hrvChart
                        rhrChart
                        sleepChart
                        readinessChart
                    }
                }
            }
            .padding(20)
        }
        .task(id: api.dataVersion) { metrics = await api.metrics() }
        .task {
            while !Task.isCancelled {
                weather = await api.weather()
                try? await Task.sleep(nanoseconds: Self.weatherRefreshSeconds * 1_000_000_000)
            }
        }
    }

    private var latest: DailyMetric? { metrics.last }

    /// Newest day that actually carries a value for this field, plus its date.
    ///
    /// The sync writes a row for every day — `recompute_pmc` fills ctl/atl/tsb
    /// unconditionally — so the newest row is routinely blank in the wellness
    /// columns whenever the watch hasn't uploaded yet. Reading `metrics.last`
    /// per field would then show nothing at all; falling back keeps the last
    /// real reading on screen, dated.
    private func recent<T>(_ key: KeyPath<DailyMetric, T?>) -> (value: T, date: String)? {
        for m in metrics.reversed() {
            if let v = m[keyPath: key] { return (v, m.date) }
        }
        return nil
    }

    private static let isoDay: DateFormatter = {
        let f = DateFormatter()
        f.locale = Locale(identifier: "de_DE")
        f.dateFormat = "yyyy-MM-dd"
        return f
    }()

    private static let shortDay: DateFormatter = {
        let f = DateFormatter()
        f.locale = Locale(identifier: "de_DE")
        f.dateFormat = "dd.MM."
        return f
    }()

    /// "Stand 14.08." for a reading that isn't from today, nil when it's current.
    private func stamp(_ date: String?) -> String? {
        guard let date, date != Self.isoDay.string(from: Date()),
              let d = Self.isoDay.date(from: date) else { return nil }
        return "Stand \(Self.shortDay.string(from: d))"
    }

    private var emptyState: some View {
        VStack(spacing: 14) {
            ArcReactor(size: 120, coreColor: Theme.arcBlue, spinning: false, intensity: 0.12)
            Text("Reaktor offline")
                .font(.system(size: 16, weight: .bold, design: .rounded))
                .foregroundStyle(Theme.ink)
            TechLabel("Starte „Garmin Sync“ unten links, um Telemetrie zu laden")
        }
        .frame(maxWidth: .infinity, minHeight: 280)
        .hudPanel(brackets: false)
    }

    // MARK: Reactor hero — the arc reactor as status gauge, metrics as
    // blueprint callouts with leader lines pointing at the core.

    private var reactorHero: some View {
        VStack(spacing: 8) {
            HStack {
                TechLabel("// Reaktorstatus", color: Theme.arc)
                Spacer()
                TechLabel("SYS.CORE", color: Theme.gold, size: 8)
            }
            HStack(spacing: 16) {
                VStack(alignment: .trailing, spacing: 26) {
                    CalloutMetric(label: "HRV", value: fmt(recent(\.hrv)?.value), unit: "ms",
                                  accent: Theme.arcBlue, side: .leading, delay: 0.10,
                                  stamp: stamp(recent(\.hrv)?.date))
                    CalloutMetric(label: "Ruhepuls", value: recent(\.rhr).map { String($0.value) }, unit: "bpm",
                                  accent: Theme.arc, side: .leading, delay: 0.22,
                                  stamp: stamp(recent(\.rhr)?.date))
                }
                .frame(maxWidth: .infinity, alignment: .trailing)

                reactorGauge

                VStack(alignment: .leading, spacing: 26) {
                    CalloutMetric(label: "Readiness", value: recent(\.training_readiness).map { String($0.value) }, unit: "/100",
                                  accent: Theme.gold, side: .trailing, delay: 0.16,
                                  stamp: stamp(recent(\.training_readiness)?.date))
                    CalloutMetric(label: "Body Battery", value: recent(\.body_battery).map { String($0.value) }, unit: "/100",
                                  accent: Theme.ok, side: .trailing, delay: 0.28,
                                  stamp: stamp(recent(\.body_battery)?.date))
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            TechLabel(systemStatus.0, color: systemStatus.1, size: 9)
                .padding(.top, 2)
        }
        .padding(18)
        .hudPanel()
    }

    private var reactorGauge: some View {
        ZStack {
            ArcReactor(size: 172)
            // Readiness as the gold outer ring, Body Battery as the green inner ring.
            gaugeRing(value: recent(\.training_readiness).map { Double($0.value) },
                      color: Theme.gold, diameter: 148)
            gaugeRing(value: recent(\.body_battery).map { Double($0.value) },
                      color: Theme.ok, diameter: 128)
        }
        .onAppear {
            withAnimation(.easeOut(duration: 1.1).delay(0.25)) { ringsShown = true }
        }
    }

    private func gaugeRing(value: Double?, color: Color, diameter: CGFloat) -> some View {
        Circle()
            .trim(from: 0, to: ringsShown ? (value ?? 0) / 100 : 0)
            .stroke(color.opacity(0.85), style: StrokeStyle(lineWidth: 2.5, lineCap: .round))
            .rotationEffect(.degrees(-90))
            .frame(width: diameter, height: diameter)
            .arcGlow(color, radius: 4)
    }

    /// Playful HUD status line derived from training readiness — but a stale
    /// reading names the actual cause instead of grading two-day-old numbers.
    private var systemStatus: (String, Color) {
        guard let r = recent(\.training_readiness) else {
            return ("// Standby — keine Daten", Theme.inkDim)
        }
        if stamp(r.date) != nil, let d = Self.isoDay.date(from: r.date) {
            return ("// Letzte Telemetrie \(Self.shortDay.string(from: d)) — Uhr nicht synchronisiert", Theme.warn)
        }
        switch r.value {
        case 66...: return ("// Alle Systeme bereit", Theme.ok)
        case 33..<66: return ("// Systeme nominal", Theme.gold)
        default: return ("// Energie niedrig — Recovery empfohlen", Theme.warn)
        }
    }

    private var loadCards: some View {
        LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 4), spacing: 12) {
            MetricCard(title: "CTL · Fitness", value: fmt(recent(\.ctl)?.value), unit: "", symbol: "arrow.up.right", accent: Theme.gold)
            MetricCard(title: "ATL · Fatigue", value: fmt(recent(\.atl)?.value), unit: "", symbol: "flame.fill", accent: Theme.arc)
            MetricCard(title: "TSB · Form", value: fmt(recent(\.tsb)?.value), unit: "", symbol: "scalemass", accent: Theme.arcBlue)
            MetricCard(title: "VO₂max", value: fmt(recent(\.vo2max)?.value), unit: "", symbol: "lungs.fill", accent: Theme.ok)
        }
    }

    // MARK: Charts

    private var pmcChart: some View {
        ChartCard(title: "Performance Management", code: "PMC // CTL·ATL·TSB") {
            Chart {
                ForEach(metrics) { m in
                    if let ctl = m.ctl {
                        LineMark(x: .value("Datum", m.date), y: .value("CTL", ctl))
                            .foregroundStyle(by: .value("Serie", "CTL (Fitness)"))
                            .lineStyle(StrokeStyle(lineWidth: 2))
                    }
                    if let atl = m.atl {
                        LineMark(x: .value("Datum", m.date), y: .value("ATL", atl))
                            .foregroundStyle(by: .value("Serie", "ATL (Fatigue)"))
                            .lineStyle(StrokeStyle(lineWidth: 1.5))
                    }
                    if let tsb = m.tsb {
                        AreaMark(x: .value("Datum", m.date), y: .value("TSB", tsb))
                            .foregroundStyle(by: .value("Serie", "TSB (Form)"))
                            .opacity(0.22)
                    }
                }
            }
            .chartForegroundStyleScale([
                "CTL (Fitness)": Theme.gold,
                "ATL (Fatigue)": Theme.arc,
                "TSB (Form)": Theme.arcBlue,
            ])
            .hudChartStyle()
            .frame(height: 220)
        }
    }

    private var hrvChart: some View {
        ChartCard(title: "HRV-Trend", code: "BIO.HRV") {
            Chart(metrics) { m in
                if let v = m.hrv {
                    LineMark(x: .value("Datum", m.date), y: .value("HRV", v))
                        .foregroundStyle(Theme.arcBlue)
                        .lineStyle(StrokeStyle(lineWidth: 1.5))
                    PointMark(x: .value("Datum", m.date), y: .value("HRV", v))
                        .foregroundStyle(Theme.arcBlue).symbolSize(18)
                }
            }
            .hudChartStyle()
            .frame(height: 150)
        }
    }

    private var rhrChart: some View {
        ChartCard(title: "Ruhepuls", code: "BIO.RHR") {
            Chart(metrics) { m in
                if let v = m.rhr {
                    LineMark(x: .value("Datum", m.date), y: .value("RHR", v))
                        .foregroundStyle(Theme.arc)
                        .lineStyle(StrokeStyle(lineWidth: 1.5))
                }
            }
            .hudChartStyle()
            .frame(height: 150)
        }
    }

    private var sleepChart: some View {
        ChartCard(title: "Schlaf", code: "BIO.SLP // H") {
            Chart(metrics) { m in
                if let v = m.sleep_hours {
                    BarMark(x: .value("Datum", m.date), y: .value("Schlaf", v))
                        .foregroundStyle(Theme.arcBlue.opacity(0.7))
                }
            }
            .hudChartStyle()
            .frame(height: 150)
        }
    }

    private var readinessChart: some View {
        ChartCard(title: "Readiness & Body Battery", code: "SYS.PWR") {
            Chart {
                ForEach(metrics) { m in
                    if let r = m.training_readiness {
                        LineMark(x: .value("Datum", m.date), y: .value("Readiness", r))
                            .foregroundStyle(by: .value("Serie", "Readiness"))
                    }
                    if let b = m.body_battery {
                        LineMark(x: .value("Datum", m.date), y: .value("Body Battery", b))
                            .foregroundStyle(by: .value("Serie", "Body Battery"))
                    }
                }
            }
            .chartForegroundStyleScale(["Readiness": Theme.gold, "Body Battery": Theme.ok])
            .hudChartStyle()
            .frame(height: 150)
        }
    }

    private func fmt(_ v: Double?) -> String? {
        guard let v else { return nil }
        return String(format: "%.0f", v)
    }
}

private extension View {
    /// Blueprint-style chart chrome: hairline grid, mono axis labels.
    func hudChartStyle() -> some View {
        self
            .chartXAxis {
                AxisMarks { _ in
                    AxisGridLine().foregroundStyle(Theme.line)
                    AxisValueLabel()
                        .font(.system(size: 8, design: .monospaced))
                        .foregroundStyle(Theme.inkDim)
                }
            }
            .chartYAxis {
                AxisMarks { _ in
                    AxisGridLine().foregroundStyle(Theme.line)
                    AxisValueLabel()
                        .font(.system(size: 8, design: .monospaced))
                        .foregroundStyle(Theme.inkDim)
                }
            }
            .chartLegend(position: .top, alignment: .trailing)
    }
}

/// A metric annotated like a blueprint callout: label + value with a leader
/// line ending in a glowing node that points at the reactor.
private struct CalloutMetric: View {
    enum Side { case leading, trailing }   // which side of the reactor it sits on

    let label: String
    let value: String?
    let unit: String
    var accent: Color
    var side: Side
    var delay: Double = 0
    /// Set when the reading isn't from today, e.g. "Stand 14.08.".
    var stamp: String? = nil

    @State private var appeared = false

    var body: some View {
        HStack(spacing: 8) {
            if side == .trailing { leader }
            VStack(alignment: side == .leading ? .trailing : .leading, spacing: 2) {
                TechLabel(label, size: 9)
                HStack(alignment: .firstTextBaseline, spacing: 3) {
                    Text(value ?? "–")
                        .font(.system(size: 22, weight: .bold, design: .rounded))
                        .foregroundStyle(value == nil ? Theme.inkDim : Theme.ink)
                        .arcGlow(value == nil ? .clear : accent, radius: 8)
                    if !unit.isEmpty {
                        Text(unit)
                            .font(.system(size: 9, design: .monospaced))
                            .foregroundStyle(Theme.inkDim)
                    }
                }
                if let stamp, value != nil {
                    Text(stamp)
                        .font(.system(size: 8, design: .monospaced))
                        .foregroundStyle(Theme.warn)
                }
            }
            if side == .leading { leader }
        }
        .opacity(appeared ? 1 : 0)
        .offset(x: appeared ? 0 : (side == .leading ? -10 : 10))
        .onAppear {
            withAnimation(.easeOut(duration: 0.5).delay(delay)) { appeared = true }
        }
    }

    private var leader: some View {
        HStack(spacing: 0) {
            if side == .trailing { node }
            Rectangle().fill(accent.opacity(0.45)).frame(width: 30, height: 1)
            if side == .leading { node }
        }
    }

    private var node: some View {
        Circle().fill(accent).frame(width: 4, height: 4).arcGlow(accent, radius: 4)
    }
}

private struct MetricCard: View {
    let title: String
    let value: String?
    let unit: String
    let symbol: String
    var accent: Color = Theme.arc

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 5) {
                Image(systemName: symbol)
                    .font(.system(size: 9))
                    .foregroundStyle(accent)
                TechLabel(title, size: 9)
            }
            HStack(alignment: .firstTextBaseline, spacing: 3) {
                Text(value ?? "–")
                    .font(.system(size: 24, weight: .bold, design: .rounded))
                    .foregroundStyle(value == nil ? Theme.inkDim : Theme.ink)
                    .arcGlow(value == nil ? .clear : accent, radius: 10)
                if !unit.isEmpty {
                    Text(unit)
                        .font(.system(size: 10, design: .monospaced))
                        .foregroundStyle(Theme.inkDim)
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .hudPanel(accent: accent)
    }
}

// MARK: - Weather

/// Environment panel: current conditions + 7-day forecast for training
/// planning. Days unsuitable for outdoor sessions are flagged.
private struct WeatherCard: View {
    let weather: WeatherSummary?

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                TechLabel("// Umgebung — Rostock", color: Theme.arc)
                Spacer()
                if weather?.stale == true {
                    TechLabel("Offline — letzter Stand", color: Theme.warn, size: 8)
                } else if let at = weather?.fetched_at, at.count >= 16 {
                    TechLabel("Stand \(at.suffix(5))", size: 8)
                }
                TechLabel("ENV.WX", color: Theme.gold, size: 8)
            }

            if let w = weather {
                HStack(alignment: .top, spacing: 18) {
                    currentBlock(w.current)
                    Divider().frame(height: 92).overlay(Theme.line)
                    forecastRow(w.forecast)
                }
            } else {
                TechLabel("Wetterdaten werden geladen …")
                    .frame(maxWidth: .infinity, minHeight: 60)
            }
        }
        .padding(14)
        .hudPanel(accent: Theme.arcBlue)
    }

    private func currentBlock(_ c: WeatherCurrent) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 10) {
                Image(systemName: WeatherIcon.symbol(for: c.code))
                    .font(.system(size: 26))
                    .foregroundStyle(WeatherIcon.color(for: c.code))
                    .arcGlow(WeatherIcon.color(for: c.code), radius: 6)
                Text("\(c.temp_c, specifier: "%.0f")°")
                    .font(.system(size: 34, weight: .bold, design: .rounded))
                    .foregroundStyle(Theme.ink)
            }
            Text(c.description)
                .font(.system(size: 12, weight: .medium))
                .foregroundStyle(Theme.ink)
            HStack(spacing: 10) {
                TechLabel("Wind \(Int(c.wind_kmh)) km/h", size: 9)
                if c.precip_mm > 0 {
                    TechLabel(String(format: "%.1f mm", c.precip_mm), color: Theme.arcBlue, size: 9)
                }
            }
        }
        .frame(width: 150, alignment: .leading)
    }

    private func forecastRow(_ days: [WeatherDay]) -> some View {
        HStack(spacing: 0) {
            ForEach(days) { day in
                VStack(spacing: 5) {
                    TechLabel(day.weekday, size: 9)
                    Image(systemName: WeatherIcon.symbol(for: day.code))
                        .font(.system(size: 15))
                        .foregroundStyle(WeatherIcon.color(for: day.code))
                        .frame(height: 20)
                    Text("\(day.temp_max, specifier: "%.0f")°")
                        .font(.system(size: 13, weight: .bold, design: .rounded))
                        .foregroundStyle(Theme.ink)
                    Text("\(day.temp_min, specifier: "%.0f")°")
                        .font(.system(size: 10, design: .rounded))
                        .foregroundStyle(Theme.inkDim)
                    TechLabel("\(day.precip_prob_pct)%",
                              color: day.precip_prob_pct >= 60 ? Theme.arcBlue : Theme.inkDim,
                              size: 8)
                    GlowDot(color: day.outdoor_suitable ? Theme.ok : Theme.warn)
                        .help(day.outdoor_suitable
                              ? "Outdoor-Training geeignet"
                              : "\(day.desc) — Indoor-Alternative erwägen")
                }
                .frame(maxWidth: .infinity)
            }
        }
    }
}

private struct ChartCard<Content: View>: View {
    let title: String
    var code: String = ""
    @ViewBuilder let content: Content

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text(title)
                    .font(.system(size: 13, weight: .semibold, design: .rounded))
                    .foregroundStyle(Theme.ink)
                Spacer()
                if !code.isEmpty { TechLabel(code, color: Theme.gold, size: 8) }
            }
            content
        }
        .padding(14)
        .hudPanel(brackets: false)
    }
}
