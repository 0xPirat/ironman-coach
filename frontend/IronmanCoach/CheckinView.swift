import SwiftUI

/// Daily subjective check-in form. POSTs to the sidecar so the coach can read it.
struct CheckinView: View {
    @EnvironmentObject var api: APIClient

    @State private var soreness = 1
    @State private var painLocation = ""
    @State private var painLevel = 0
    @State private var motivation = 3
    @State private var mentalEnergy = 3
    @State private var availableTime = 60
    @State private var lifeStress = 2
    @State private var notes = ""
    @State private var saveResult: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                HUDHeader(eyebrow: "Bio-Scan", title: "Daily Check-in", code: "BIO.05")

                CheckinSection(title: "Körper", code: "BIO.BODY") {
                    PowerCellRating(label: "Muskelkater", value: $soreness)
                    HUDTextField(label: "Schmerz-Ort (optional)", text: $painLocation)
                    PowerCellRating(label: "Schmerz-Level", value: $painLevel, range: 0...10)
                }

                CheckinSection(title: "Kopf", code: "BIO.MIND") {
                    PowerCellRating(label: "Motivation", value: $motivation, color: Theme.gold)
                    PowerCellRating(label: "Mentale Energie", value: $mentalEnergy, color: Theme.gold)
                    PowerCellRating(label: "Lebensstress", value: $lifeStress)
                }

                CheckinSection(title: "Heute", code: "SYS.PLAN") {
                    HStack {
                        TechLabel("Verfügbare Zeit", size: 11)
                        Spacer()
                        Stepper(value: $availableTime, in: 0...300, step: 15) {
                            Text("\(availableTime) min")
                                .font(.system(size: 12, weight: .bold, design: .monospaced))
                                .foregroundStyle(Theme.arcBlue)
                        }
                    }
                    HUDTextField(label: "Notizen", text: $notes, multiline: true)
                }

                HStack(spacing: 12) {
                    Button("Check-in speichern") { Task { await save() } }
                        .buttonStyle(HUDButtonStyle(prominent: true))
                        .keyboardShortcut("s", modifiers: .command)
                    if let saveResult {
                        TechLabel(saveResult, color: saveResult.contains("✓") ? Theme.ok : Theme.arc, size: 10)
                    }
                }
            }
            .padding(20)
            .frame(maxWidth: 620, alignment: .leading)
        }
        .frame(maxWidth: .infinity, alignment: .topLeading)
    }

    private func save() async {
        let c = Checkin(
            date: nil,
            soreness: soreness,
            pain_location: painLocation.isEmpty ? nil : painLocation,
            pain_level: painLevel,
            motivation: motivation,
            mental_energy: mentalEnergy,
            available_time: availableTime,
            life_stress: lifeStress,
            notes: notes.isEmpty ? nil : notes
        )
        let ok = await api.saveCheckin(c)
        saveResult = ok ? "Gespeichert ✓ – der Coach kann es jetzt lesen."
                        : "Speichern fehlgeschlagen (Sidecar erreichbar?)."
    }
}

private struct CheckinSection<Content: View>: View {
    let title: String
    var code: String = ""
    @ViewBuilder let content: Content

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text(title)
                    .font(.system(size: 13, weight: .semibold, design: .rounded))
                    .foregroundStyle(Theme.ink)
                Spacer()
                if !code.isEmpty { TechLabel(code, color: Theme.gold, size: 8) }
            }
            content
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .hudPanel(brackets: false)
    }
}

private struct HUDTextField: View {
    let label: String
    @Binding var text: String
    var multiline = false

    var body: some View {
        TextField(label, text: $text, axis: multiline ? .vertical : .horizontal)
            .textFieldStyle(.plain)
            .font(.system(size: 12))
            .foregroundStyle(Theme.ink)
            .lineLimit(multiline ? 2...5 : 1...1)
            .padding(.horizontal, 10)
            .padding(.vertical, 7)
            .background(RoundedRectangle(cornerRadius: 5).fill(Theme.bgRaised))
            .overlay(RoundedRectangle(cornerRadius: 5).strokeBorder(Theme.line, lineWidth: 1))
    }
}
