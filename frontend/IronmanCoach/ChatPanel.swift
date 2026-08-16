import SwiftUI

/// The persistent coach chat panel. Wired end-to-end to the streaming /chat SSE.
struct ChatPanel: View {
    @EnvironmentObject var api: APIClient
    @State private var messages: [ChatMessage] = []
    @State private var input: String = ""
    @State private var streaming = false

    var body: some View {
        VStack(spacing: 0) {
            header
            Rectangle().fill(Theme.line).frame(height: 1)
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 10) {
                        if messages.isEmpty {
                            VStack(alignment: .leading, spacing: 6) {
                                TechLabel("// Standby", color: Theme.gold)
                                Text("Frag deinen Coach – z. B. „Wie sieht meine Woche aus?“ oder „Bewerte heute.“")
                                    .font(.callout)
                                    .foregroundStyle(Theme.inkDim)
                            }
                            .padding(14)
                        }
                        ForEach(messages) { msg in
                            MessageBubble(message: msg).id(msg.id)
                        }
                    }
                    .padding(12)
                }
                .onChange(of: messages.count) { _ in
                    if let last = messages.last { withAnimation { proxy.scrollTo(last.id, anchor: .bottom) } }
                }
            }
            Rectangle().fill(Theme.line).frame(height: 1)
            inputBar
        }
        .background(Theme.bgRaised)
        .task { messages = await api.chatHistory() }
    }

    private var header: some View {
        HStack(spacing: 8) {
            // Miniature arc reactor as the coach avatar — glows gold while thinking.
            ArcReactor(size: 24,
                       coreColor: streaming ? Theme.gold : Theme.arc,
                       intensity: streaming ? 1.0 : 0.8)
                .animation(.easeInOut(duration: 0.4), value: streaming)
            VStack(alignment: .leading, spacing: 1) {
                Text("Coach")
                    .font(.system(size: 13, weight: .bold, design: .rounded))
                    .foregroundStyle(Theme.ink)
                TechLabel(streaming ? "Antwortet…" : "Online", color: streaming ? Theme.gold : Theme.inkDim, size: 8)
            }
            Spacer()
            if streaming { ProgressView().controlSize(.small) }
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 10)
    }

    private var inputBar: some View {
        HStack(spacing: 8) {
            TextField("Nachricht an den Coach…", text: $input, axis: .vertical)
                .textFieldStyle(.plain)
                .font(.system(size: 13))
                .foregroundStyle(Theme.ink)
                .lineLimit(1...5)
                .padding(.horizontal, 10)
                .padding(.vertical, 7)
                .background(RoundedRectangle(cornerRadius: 6).fill(Theme.panel))
                .overlay(RoundedRectangle(cornerRadius: 6).strokeBorder(Theme.line, lineWidth: 1))
                .onSubmit(send)
                .disabled(streaming)
            Button(action: send) {
                Image(systemName: "paperplane.fill")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundStyle(.white)
                    .frame(width: 30, height: 30)
                    .background(Circle().fill(sendDisabled ? Theme.panel : Theme.arc))
                    .arcGlow(sendDisabled ? .clear : Theme.arc, radius: 6)
            }
            .buttonStyle(.plain)
            .keyboardShortcut(.return, modifiers: [])
            .disabled(sendDisabled)
        }
        .padding(10)
    }

    private var sendDisabled: Bool {
        input.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || streaming
    }

    private func send() {
        let text = input.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty, !streaming else { return }
        input = ""
        messages.append(ChatMessage(role: .user, content: text))
        let assistant = ChatMessage(role: .assistant, content: "")
        messages.append(assistant)
        let idx = messages.count - 1
        streaming = true

        Task {
            await api.streamChat(message: text) { delta in
                messages[idx].content += delta
            }
            streaming = false
        }
    }
}

private struct MessageBubble: View {
    let message: ChatMessage
    var isUser: Bool { message.role == .user }

    var body: some View {
        HStack {
            if isUser { Spacer(minLength: 30) }
            Text(message.content.isEmpty ? "…" : message.content)
                .font(.system(size: 13))
                .foregroundStyle(Theme.ink)
                .padding(10)
                .background(
                    RoundedRectangle(cornerRadius: 8)
                        .fill(isUser ? Theme.arc.opacity(0.16) : Theme.panel)
                )
                .overlay(
                    RoundedRectangle(cornerRadius: 8)
                        .strokeBorder(isUser ? Theme.arc.opacity(0.35) : Theme.line, lineWidth: 1)
                )
                .overlay(alignment: .leading) {
                    if !isUser {
                        UnevenRoundedRectangle(topLeadingRadius: 8, bottomLeadingRadius: 8)
                            .fill(Theme.gold.opacity(0.7))
                            .frame(width: 2)
                    }
                }
                .frame(maxWidth: .infinity, alignment: isUser ? .trailing : .leading)
            if !isUser { Spacer(minLength: 30) }
        }
    }
}
