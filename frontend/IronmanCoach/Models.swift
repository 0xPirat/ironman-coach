import Foundation
import SwiftUI

// Data model mirrors the backend SQLite schema / REST payloads.

enum Sport: String, Codable, CaseIterable, Identifiable {
    case swim, bike, run, strength, brick, triathlon, cycling, hiking, yoga, rowing, rest, other
    var id: String { rawValue }

    var label: String {
        switch self {
        case .swim:      return "Schwimmen"
        case .bike:      return "Rad"
        case .run:       return "Laufen"
        case .strength:  return "Kraft"
        case .brick:     return "Koppel"
        case .triathlon: return "Triathlon"
        case .cycling:   return "Radfahren"
        case .hiking:    return "Wandern"
        case .yoga:      return "Yoga/Mobility"
        case .rowing:    return "Rudern"
        case .rest:      return "Ruhe"
        case .other:     return "Sonstiges"
        }
    }

    var symbol: String {
        switch self {
        case .swim:      return "figure.pool.swim"
        case .bike:      return "figure.outdoor.cycle"
        case .run:       return "figure.run"
        case .strength:  return "dumbbell.fill"
        case .brick:     return "arrow.triangle.2.circlepath"
        case .triathlon: return "trophy.fill"
        case .cycling:   return "bicycle"
        case .hiking:    return "figure.hiking"
        case .yoga:      return "figure.mind.and.body"
        case .rowing:    return "figure.rowing"
        case .rest:      return "bed.double.fill"
        case .other:     return "questionmark.circle"
        }
    }

    // Luminous variants tuned for the dark steel HUD palette (Theme.swift).
    var color: Color {
        switch self {
        case .swim:      return Color(red: 0.38, green: 0.72, blue: 1.00)
        case .bike:      return Color(red: 1.00, green: 0.62, blue: 0.30)
        case .run:       return Color(red: 0.40, green: 0.88, blue: 0.55)
        case .strength:  return Color(red: 0.72, green: 0.55, blue: 1.00)
        case .brick:     return Color(red: 1.00, green: 0.42, blue: 0.60)
        case .triathlon: return Color(red: 0.89, green: 0.71, blue: 0.35)
        case .cycling:   return Color(red: 1.00, green: 0.70, blue: 0.42)
        case .hiking:    return Color(red: 0.80, green: 0.62, blue: 0.44)
        case .yoga:      return Color(red: 0.45, green: 0.90, blue: 0.80)
        case .rowing:    return Color(red: 0.35, green: 0.80, blue: 0.85)
        case .rest:      return Color(red: 0.58, green: 0.64, blue: 0.76)
        case .other:     return .secondary
        }
    }
}

struct AthleteGoal: Codable, Identifiable {
    var id: Int
    var title: String
    var sport: String
    var category: String?
    var event_date: String?
    var description: String?
    var target_metric: String?
    var priority: Int?
    var status: String?

    var priorityLabel: String {
        switch priority ?? 2 {
        case 1: return "⭐ Primär"
        case 3: return "Hintergrund"
        default: return "Sekundär"
        }
    }

    var sportSymbol: String {
        Sport(rawValue: sport)?.symbol ?? "trophy.fill"
    }

    var sportColor: Color {
        Sport(rawValue: sport)?.color ?? .secondary
    }
}

/// HR zone color coding shared across views (matches the user's fixed zones).
enum HRZone: String, CaseIterable {
    case z1 = "Z1", z2 = "Z2", z3 = "Z3", z4 = "Z4", z5 = "Z5"

    var range: String {
        switch self {
        case .z1: return "< 120"
        case .z2: return "120–140"
        case .z3: return "140–160"
        case .z4: return "160–180"
        case .z5: return "180–200"
        }
    }

    // Zone ramp: cool steel → reactor red, matching the HUD palette.
    var color: Color {
        switch self {
        case .z1: return Color(red: 0.58, green: 0.64, blue: 0.76)
        case .z2: return Color(red: 0.38, green: 0.72, blue: 1.00)
        case .z3: return Color(red: 0.40, green: 0.88, blue: 0.55)
        case .z4: return Color(red: 0.89, green: 0.71, blue: 0.35)
        case .z5: return Color(red: 1.00, green: 0.24, blue: 0.37)
        }
    }

    static func from(_ raw: String?) -> HRZone? {
        guard let raw else { return nil }
        return HRZone(rawValue: String(raw.prefix(2)).uppercased())
    }
}

enum DayStatusValue: String, Codable {
    case green, yellow, red

    var label: String {
        switch self {
        case .green: return "Grün"
        case .yellow: return "Gelb"
        case .red: return "Rot"
        }
    }
    var color: Color {
        switch self {
        case .green: return .green
        case .yellow: return .yellow
        case .red: return .red
        }
    }
    var emoji: String {
        switch self {
        case .green: return "🟢"
        case .yellow: return "🟡"
        case .red: return "🔴"
        }
    }
}

struct PlannedWorkout: Codable, Identifiable {
    var id: Int
    var date: String
    var sport: Sport
    var title: String?
    var duration_min: Int?
    var distance_km: Double?
    var target_zone: String?
    var content: String?
    var priority: String?
    var status: String?
}

struct Activity: Codable, Identifiable {
    var id: Int
    var date: String
    var sport: Sport
    var title: String?
    var duration_min: Double?
    var distance_km: Double?
    var avg_hr: Int?
    var training_load: Double?
}

struct DailyMetric: Codable, Identifiable {
    var date: String
    var hrv: Double?
    var rhr: Int?
    var sleep_hours: Double?
    var body_battery: Int?
    var training_readiness: Int?
    var ctl: Double?
    var atl: Double?
    var tsb: Double?
    var vo2max: Double?

    var id: String { date }
}

struct DayStatus: Codable {
    var date: String
    var status: DayStatusValue
    var reason: String?
}

// MARK: - Weather (mirrors backend /weather payload)

struct WeatherCurrent: Codable {
    var temp_c: Double
    var description: String
    var code: Int?
    var wind_kmh: Double
    var precip_mm: Double
}

struct WeatherDay: Codable, Identifiable {
    var date: String
    var weekday: String
    var desc: String
    var code: Int?
    var temp_max: Double
    var temp_min: Double
    var precip_mm: Double
    var precip_prob_pct: Int
    var wind_max_kmh: Double
    var uv_max: Double
    var outdoor_suitable: Bool

    var id: String { date }
}

struct WeatherSummary: Codable {
    var current: WeatherCurrent
    var forecast: [WeatherDay]
    var fetched_at: String?
    var stale: Bool?
}

/// WMO weather code → SF Symbol + accent color for the HUD.
enum WeatherIcon {
    static func symbol(for code: Int?) -> String {
        switch code ?? -1 {
        case 0:          return "sun.max.fill"
        case 1:          return "sun.max"
        case 2:          return "cloud.sun.fill"
        case 3:          return "cloud.fill"
        case 45, 48:     return "cloud.fog.fill"
        case 51...57:    return "cloud.drizzle.fill"
        case 61...67:    return "cloud.rain.fill"
        case 71...77:    return "cloud.snow.fill"
        case 80...82:    return "cloud.heavyrain.fill"
        case 85, 86:     return "cloud.snow.fill"
        case 95...99:    return "cloud.bolt.rain.fill"
        default:         return "questionmark.circle"
        }
    }

    static func color(for code: Int?) -> Color {
        switch code ?? -1 {
        case 0, 1:       return Theme.gold
        case 2, 3:       return Theme.inkDim
        case 45, 48:     return Theme.inkDim
        case 51...67, 80...82: return Theme.arcBlue
        case 71...77, 85, 86:  return Theme.corePale
        case 95...99:    return Theme.arc
        default:         return Theme.inkDim
        }
    }
}

struct ChatMessage: Identifiable, Codable {
    enum Role: String, Codable { case user, assistant, system }
    var id = UUID()
    var role: Role
    var content: String
}

struct Checkin: Codable {
    var date: String?
    var soreness: Int?
    var pain_location: String?
    var pain_level: Int?
    var motivation: Int?
    var mental_energy: Int?
    var available_time: Int?
    var life_stress: Int?
    var notes: String?
}
