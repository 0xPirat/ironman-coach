import SwiftUI

// MARK: - Stark HUD theme
// Visual language: Iron-Man-style engineering blueprint. Dark steel blue,
// fine schematic grid, glowing arc-reactor red as the primary accent,
// armor gold as the secondary. Technical labels are monospaced uppercase.
// Signature element: the animated arc reactor with blueprint callouts.

enum Theme {
    // Surfaces
    static let bg        = Color(red: 0.10, green: 0.13, blue: 0.20)   // deep steel blue
    static let bgRaised  = Color(red: 0.13, green: 0.17, blue: 0.25)
    static let panel     = Color(red: 0.15, green: 0.19, blue: 0.29)
    static let panelTop  = Color(red: 0.18, green: 0.23, blue: 0.34)

    // Blueprint lines
    static let line      = Color(red: 0.55, green: 0.64, blue: 0.80).opacity(0.16)
    static let lineSoft  = Color(red: 0.55, green: 0.64, blue: 0.80).opacity(0.08)

    // Ink
    static let ink       = Color(red: 0.91, green: 0.93, blue: 0.97)
    static let inkDim    = Color(red: 0.58, green: 0.64, blue: 0.76)

    // Accents
    static let arc       = Color(red: 1.00, green: 0.24, blue: 0.37)   // reactor red
    static let arcSoft   = Color(red: 1.00, green: 0.48, blue: 0.58)
    static let gold      = Color(red: 0.89, green: 0.71, blue: 0.35)   // armor gold
    static let arcBlue   = Color(red: 0.62, green: 0.85, blue: 1.00)   // reactor core blue
    static let corePale  = Color(red: 0.88, green: 0.96, blue: 1.00)   // white-hot core center

    // Status
    static let ok        = Color(red: 0.35, green: 0.85, blue: 0.55)
    static let warn      = Color(red: 0.95, green: 0.75, blue: 0.30)
}

// MARK: - Blueprint grid background

/// Fine schematic grid with sparse crosshair ticks and a faint reactor
/// cross-section in the corner, like a detail view on a technical drawing.
struct BlueprintBackground: View {
    var body: some View {
        ZStack {
            Theme.bg
            Canvas { ctx, size in
                let step: CGFloat = 28
                var grid = Path()
                var x: CGFloat = 0
                while x <= size.width {
                    grid.move(to: CGPoint(x: x, y: 0))
                    grid.addLine(to: CGPoint(x: x, y: size.height))
                    x += step
                }
                var y: CGFloat = 0
                while y <= size.height {
                    grid.move(to: CGPoint(x: 0, y: y))
                    grid.addLine(to: CGPoint(x: size.width, y: y))
                    y += step
                }
                ctx.stroke(grid, with: .color(Theme.lineSoft), lineWidth: 0.5)

                // Sparse crosshairs at fixed grid intersections (every 6th line).
                var marks = Path()
                let cross: CGFloat = 3
                var cx: CGFloat = step * 6
                while cx < size.width {
                    var cy: CGFloat = step * 6
                    while cy < size.height {
                        marks.move(to: CGPoint(x: cx - cross, y: cy))
                        marks.addLine(to: CGPoint(x: cx + cross, y: cy))
                        marks.move(to: CGPoint(x: cx, y: cy - cross))
                        marks.addLine(to: CGPoint(x: cx, y: cy + cross))
                        cy += step * 6
                    }
                    cx += step * 6
                }
                ctx.stroke(marks, with: .color(Theme.line), lineWidth: 0.7)

                // Faint reactor cross-section, bottom-right: concentric rings,
                // radial ticks, crosshair — a schematic "detail A" ornament.
                let c = CGPoint(x: size.width - 150, y: size.height - 140)
                var rings = Path()
                for r: CGFloat in [104, 84, 56, 22] {
                    rings.addEllipse(in: CGRect(x: c.x - r, y: c.y - r, width: 2 * r, height: 2 * r))
                }
                ctx.stroke(rings, with: .color(Theme.lineSoft), lineWidth: 0.8)

                var ticks = Path()
                for i in 0..<36 {
                    let a = CGFloat(i) * .pi / 18
                    ticks.move(to: CGPoint(x: c.x + cos(a) * 96, y: c.y + sin(a) * 96))
                    ticks.addLine(to: CGPoint(x: c.x + cos(a) * 104, y: c.y + sin(a) * 104))
                }
                ctx.stroke(ticks, with: .color(Theme.lineSoft), lineWidth: 0.6)

                var hair = Path()
                hair.move(to: CGPoint(x: c.x - 120, y: c.y))
                hair.addLine(to: CGPoint(x: c.x + 120, y: c.y))
                hair.move(to: CGPoint(x: c.x, y: c.y - 120))
                hair.addLine(to: CGPoint(x: c.x, y: c.y + 120))
                ctx.stroke(hair, with: .color(Theme.lineSoft), lineWidth: 0.5)
            }
            // Depth: a soft cool glow falling in from the top, dark toward the bottom.
            RadialGradient(colors: [Theme.arcBlue.opacity(0.05), .clear],
                           center: .topLeading, startRadius: 0, endRadius: 700)
            LinearGradient(colors: [.clear, Color.black.opacity(0.16)],
                           startPoint: .center, endPoint: .bottom)
        }
        .ignoresSafeArea()
    }
}

// MARK: - Schematic shapes

/// Radial tick marks around a circle, like the graduation on a gauge.
struct TickRing: Shape {
    var count: Int = 48
    var length: CGFloat = 0.06   // fraction of the radius

    func path(in rect: CGRect) -> Path {
        var p = Path()
        let r = min(rect.width, rect.height) / 2
        let c = CGPoint(x: rect.midX, y: rect.midY)
        for i in 0..<count {
            let a = (CGFloat(i) / CGFloat(count)) * 2 * .pi
            let inner = r * (1 - length)
            p.move(to: CGPoint(x: c.x + cos(a) * inner, y: c.y + sin(a) * inner))
            p.addLine(to: CGPoint(x: c.x + cos(a) * r, y: c.y + sin(a) * r))
        }
        return p
    }
}

/// A ring broken into evenly spaced arc segments — the rotating collar
/// of the arc reactor.
struct SegmentedRing: Shape {
    var segments: Int = 10
    var gapDegrees: Double = 14

    func path(in rect: CGRect) -> Path {
        var p = Path()
        let r = min(rect.width, rect.height) / 2
        let c = CGPoint(x: rect.midX, y: rect.midY)
        let span = 360.0 / Double(segments) - gapDegrees
        for i in 0..<segments {
            let start = Angle.degrees(Double(i) * 360.0 / Double(segments))
            let a = CGFloat(start.radians)
            p.move(to: CGPoint(x: c.x + r * cos(a), y: c.y + r * sin(a)))
            p.addArc(center: c, radius: r, startAngle: start,
                     endAngle: start + .degrees(span), clockwise: false)
        }
        return p
    }
}

/// Horizontal measurement line with end ticks, like a dimension line
/// on an engineering drawing.
struct DimensionLine: Shape {
    var tick: CGFloat = 5

    func path(in rect: CGRect) -> Path {
        var p = Path()
        let y = rect.midY
        p.move(to: CGPoint(x: rect.minX, y: y))
        p.addLine(to: CGPoint(x: rect.maxX, y: y))
        p.move(to: CGPoint(x: rect.minX, y: y - tick))
        p.addLine(to: CGPoint(x: rect.minX, y: y + tick))
        p.move(to: CGPoint(x: rect.maxX, y: y - tick))
        p.addLine(to: CGPoint(x: rect.maxX, y: y + tick))
        return p
    }
}

// MARK: - Arc reactor

/// The signature element: concentric rings, a slowly rotating segment collar,
/// and a glowing core. Scales from a 22 pt avatar to a full dashboard gauge;
/// below 60 pt the fine detail is dropped. `intensity` 0…1 dims the reactor
/// (0 ≈ offline). Rotation stops when Reduce Motion is on.
struct ArcReactor: View {
    var size: CGFloat = 140
    var coreColor: Color = Theme.arcBlue
    var spinning: Bool = true
    var intensity: Double = 1.0

    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var angle: Double = 0

    private var detailed: Bool { size >= 60 }

    var body: some View {
        ZStack {
            Circle().strokeBorder(Theme.line, lineWidth: 1)

            if detailed {
                TickRing(count: 48, length: 0.06)
                    .stroke(Theme.line, lineWidth: 1)
                    .padding(size * 0.02)

                SegmentedRing(segments: 3, gapDegrees: 48)
                    .stroke(Theme.gold.opacity(0.30 + 0.25 * intensity), lineWidth: 1.2)
                    .padding(size * 0.09)
                    .rotationEffect(.degrees(-angle * 0.5))
            }

            SegmentedRing(segments: detailed ? 10 : 6, gapDegrees: detailed ? 14 : 24)
                .stroke(coreColor.opacity(0.25 + 0.5 * intensity),
                        style: StrokeStyle(lineWidth: detailed ? size * 0.05 : 2, lineCap: .butt))
                .padding(detailed ? size * 0.18 : size * 0.20)
                .rotationEffect(.degrees(angle))

            Circle()
                .fill(RadialGradient(colors: [Theme.corePale,
                                              coreColor.opacity(0.9),
                                              coreColor.opacity(0)],
                                     center: .center, startRadius: 0, endRadius: size * 0.19))
                .frame(width: size * 0.38, height: size * 0.38)
                .opacity(0.3 + 0.7 * intensity)
                .arcGlow(coreColor, radius: size * 0.10 * intensity)
        }
        .frame(width: size, height: size)
        .onAppear { startSpin() }
        .onChange(of: spinning) { _ in startSpin() }
    }

    private func startSpin() {
        guard spinning, !reduceMotion else { return }
        angle = 0
        withAnimation(.linear(duration: 36).repeatForever(autoreverses: false)) {
            angle = 360
        }
    }
}

// MARK: - HUD panel (card with technical corner brackets)

/// L-shaped brackets at the four corners, like callouts on a schematic.
struct CornerBrackets: Shape {
    var length: CGFloat = 9
    func path(in rect: CGRect) -> Path {
        var p = Path()
        let l = length
        // top-left
        p.move(to: CGPoint(x: rect.minX, y: rect.minY + l))
        p.addLine(to: CGPoint(x: rect.minX, y: rect.minY))
        p.addLine(to: CGPoint(x: rect.minX + l, y: rect.minY))
        // top-right
        p.move(to: CGPoint(x: rect.maxX - l, y: rect.minY))
        p.addLine(to: CGPoint(x: rect.maxX, y: rect.minY))
        p.addLine(to: CGPoint(x: rect.maxX, y: rect.minY + l))
        // bottom-right
        p.move(to: CGPoint(x: rect.maxX, y: rect.maxY - l))
        p.addLine(to: CGPoint(x: rect.maxX, y: rect.maxY))
        p.addLine(to: CGPoint(x: rect.maxX - l, y: rect.maxY))
        // bottom-left
        p.move(to: CGPoint(x: rect.minX + l, y: rect.maxY))
        p.addLine(to: CGPoint(x: rect.minX, y: rect.maxY))
        p.addLine(to: CGPoint(x: rect.minX, y: rect.maxY - l))
        return p
    }
}

struct HUDPanel: ViewModifier {
    var accent: Color = Theme.arc
    var brackets: Bool = true
    var hover: Bool = true

    @State private var hovering = false

    func body(content: Content) -> some View {
        content
            .background(
                RoundedRectangle(cornerRadius: 6)
                    .fill(LinearGradient(colors: [Theme.panelTop, Theme.panel],
                                         startPoint: .top, endPoint: .bottom))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 6)
                    .strokeBorder(hovering ? accent.opacity(0.30) : Theme.line, lineWidth: 1)
            )
            .overlay {
                if brackets {
                    CornerBrackets()
                        .stroke(accent.opacity(hovering ? 0.95 : 0.65),
                                style: StrokeStyle(lineWidth: 1.5, lineCap: .square))
                }
            }
            .shadow(color: .black.opacity(0.25), radius: 7, y: 3)
            .shadow(color: accent.opacity(hovering ? 0.10 : 0), radius: 12)
            .onHover { h in
                guard hover else { return }
                withAnimation(.easeOut(duration: 0.18)) { hovering = h }
            }
    }
}

extension View {
    func hudPanel(accent: Color = Theme.arc, brackets: Bool = true, hover: Bool = true) -> some View {
        modifier(HUDPanel(accent: accent, brackets: brackets, hover: hover))
    }

    /// Arc-reactor glow for key values and indicators.
    func arcGlow(_ color: Color = Theme.arc, radius: CGFloat = 8) -> some View {
        shadow(color: color.opacity(0.55), radius: radius)
    }
}

// MARK: - Type helpers

/// Monospaced uppercase micro-label, like an annotation on a blueprint.
struct TechLabel: View {
    let text: String
    var color: Color = Theme.inkDim
    var size: CGFloat = 10

    init(_ text: String, color: Color = Theme.inkDim, size: CGFloat = 10) {
        self.text = text
        self.color = color
        self.size = size
    }

    var body: some View {
        Text(text.uppercased())
            .font(.system(size: size, weight: .medium, design: .monospaced))
            .kerning(1.2)
            .foregroundStyle(color)
    }
}

/// Section header: mono eyebrow + big title, followed by a dimension line
/// that runs to the edge and an optional gold module code.
struct HUDHeader: View {
    let eyebrow: String
    let title: String
    var code: String = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            TechLabel("// " + eyebrow, color: Theme.arc)
            HStack(spacing: 12) {
                Text(title)
                    .font(.system(size: 26, weight: .bold, design: .rounded))
                    .foregroundStyle(Theme.ink)
                DimensionLine()
                    .stroke(Theme.line, lineWidth: 1)
                    .frame(height: 12)
                    .frame(maxWidth: .infinity)
                if !code.isEmpty {
                    TechLabel(code, color: Theme.gold, size: 9)
                }
            }
        }
    }
}

// MARK: - Controls

struct HUDButtonStyle: ButtonStyle {
    var prominent = false

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.system(size: 12, weight: .semibold))
            .foregroundStyle(prominent ? Color.white : Theme.ink)
            .padding(.horizontal, 12)
            .padding(.vertical, 6)
            .background(
                RoundedRectangle(cornerRadius: 5)
                    .fill(prominent ? Theme.arc : Theme.panelTop)
            )
            .overlay(
                RoundedRectangle(cornerRadius: 5)
                    .strokeBorder(prominent ? Theme.arcSoft.opacity(0.6) : Theme.line, lineWidth: 1)
            )
            .opacity(configuration.isPressed ? 0.8 : 1)
            .scaleEffect(configuration.isPressed ? 0.97 : 1)
            .animation(.spring(response: 0.2, dampingFraction: 0.7), value: configuration.isPressed)
            .arcGlow(prominent ? Theme.arc : .clear, radius: prominent ? 6 : 0)
    }
}

/// Segmented mode switch in HUD style with a sliding active pill.
struct HUDSegmentedPicker<T: Hashable>: View {
    @Binding var selection: T
    let options: [(T, String)]

    @Namespace private var ns

    var body: some View {
        HStack(spacing: 2) {
            ForEach(options, id: \.0) { value, label in
                let active = selection == value
                Button {
                    withAnimation(.spring(response: 0.3, dampingFraction: 0.8)) { selection = value }
                } label: {
                    Text(label.uppercased())
                        .font(.system(size: 10, weight: active ? .bold : .medium, design: .monospaced))
                        .kerning(0.8)
                        .fixedSize()
                        .foregroundStyle(active ? Color.white : Theme.inkDim)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 5)
                        .background {
                            if active {
                                RoundedRectangle(cornerRadius: 4)
                                    .fill(Theme.arc.opacity(0.85))
                                    .matchedGeometryEffect(id: "hud-seg-pill", in: ns)
                            }
                        }
                }
                .buttonStyle(.plain)
            }
        }
        .padding(3)
        .background(RoundedRectangle(cornerRadius: 6).fill(Theme.bgRaised))
        .overlay(RoundedRectangle(cornerRadius: 6).strokeBorder(Theme.line, lineWidth: 1))
    }
}

/// 1–5 rating as glowing power cells (check-in form).
struct PowerCellRating: View {
    let label: String
    @Binding var value: Int
    var range: ClosedRange<Int> = 1...5
    var color: Color = Theme.arc

    var body: some View {
        HStack {
            TechLabel(label, size: 11)
            Spacer()
            HStack(spacing: 4) {
                ForEach(Array(range), id: \.self) { i in
                    let filled = i <= value
                    Button { value = i } label: {
                        RoundedRectangle(cornerRadius: 2)
                            .fill(filled ? color : Theme.bgRaised)
                            .frame(width: 22, height: 12)
                            .overlay(
                                RoundedRectangle(cornerRadius: 2)
                                    .strokeBorder(filled ? color.opacity(0.8) : Theme.line, lineWidth: 1)
                            )
                            .scaleEffect(filled ? 1 : 0.88)
                            .arcGlow(filled ? color : .clear, radius: filled ? 4 : 0)
                    }
                    .buttonStyle(.plain)
                }
            }
            .animation(.spring(response: 0.28, dampingFraction: 0.6), value: value)
            Text("\(value)")
                .font(.system(size: 12, weight: .bold, design: .monospaced))
                .foregroundStyle(color)
                .arcGlow(color, radius: 4)
                .frame(width: 22, alignment: .trailing)
                .contentTransition(.numericText())
                .animation(.spring(response: 0.28, dampingFraction: 0.7), value: value)
        }
    }
}

/// Status dot with a soft glow halo.
struct GlowDot: View {
    let color: Color
    var body: some View {
        Circle()
            .fill(color)
            .frame(width: 7, height: 7)
            .arcGlow(color, radius: 5)
    }
}
