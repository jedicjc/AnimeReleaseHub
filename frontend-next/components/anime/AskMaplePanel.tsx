"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { askMaple } from "@/lib/api";

const suggestedQuestions = [
  "Why is this anime trending?",
  "Is it worth watching?",
  "Recommend something like this",
  "I loved this anime",
  "This wasn't for me",
  "What should I watch next?",
  "Compare to Frieren",
  "Which has better world building?",
  "Who would enjoy this anime?",
  "Similar anime to this",
  "What does the Maple Score mean?",
  "What's the story about?",
  "Who animated this?",
  "How many episodes are there?",
  "Is it finished airing?",
  "Any recent news?",
];

type ChatMessage = {
  id: string;
  role: "user" | "maple";
  text: string;
};

const initialMessage =
  "Hi! I'm Maple. Ask me about this anime, compare it to another title, or ask for recommendations.";

function createMessage(
  role: ChatMessage["role"],
  text: string,
): ChatMessage {
  return {
    id: crypto.randomUUID(),
    role,
    text,
  };
}

export function AskMaplePanel({ animeId }: { animeId: string | number }) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    createMessage("maple", initialMessage),
  ]);
  const [loading, setLoading] = useState(false);
  const [thinking, setThinking] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  function startNewChat() {
    setMessages([createMessage("maple", initialMessage)]);
    setQuestion("");
  }

  async function copyMessage(text: string) {
    await navigator.clipboard.writeText(text);
  }

  function getPreviousUserQuestion(messageId: string) {
    const index = messages.findIndex((message) => message.id === messageId);

    if (index === -1) return null;

    for (let i = index - 1; i >= 0; i -= 1) {
      if (messages[i].role === "user") {
        return messages[i].text;
      }
    }

    return [...messages]
      .reverse()
      .find((message) => message.role === "user")?.text ?? null;
  }

  async function typeMapleMessage(text: string) {
    let current = "";
    const messageId = crypto.randomUUID();

    setMessages((prev) => [
      ...prev,
      {
        id: messageId,
        role: "maple",
        text: "",
      },
    ]);

    for (const char of text) {
      current += char;

      setMessages((prev) =>
        prev.map((message) =>
          message.id === messageId ? { ...message, text: current } : message,
        ),
      );

      await new Promise((resolve) => setTimeout(resolve, 8));
    }
  }

  async function submitQuestion(nextQuestion: string) {
    const trimmed = nextQuestion.trim();

    if (!trimmed || loading) return;

    setLoading(true);
    setThinking(true);
    setQuestion("");
    setMessages((current) => [...current, createMessage("user", trimmed)]);

    try {
      const response = await askMaple(
        String(animeId),
        trimmed,
        messages.map((message) => ({
          role: message.role,
          content: message.text,
        })),
      );
      const answer = response?.answer?.trim();

      await typeMapleMessage(
        answer ||
          "Maple could not answer that yet. Try asking about trends, scores, recommendations, or news.",
      );
      setThinking(false);
    } catch {
      await typeMapleMessage("Maple had trouble answering that.");
    } finally {
      setLoading(false);
      setThinking(false);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    submitQuestion(question);
  }

  return (
    <section className="mt-10 rounded-3xl border border-pink-300/20 bg-gradient-to-r from-pink-500/10 via-purple-500/10 to-cyan-500/10 p-6">
      <div className="flex items-center justify-between gap-4">
        <h2 className="text-xl font-black">🍁 Ask Maple</h2>
        <div className="min-w-0">
        <p className="mt-2 text-sm text-purple-200">
          Ask questions about this anime.
        </p>
        </div>

        <button
          type="button"
          onClick={startNewChat}
          className="rounded-full border border-[rgba(255,145,77,0.35)] bg-white/10 px-3 py-2 text-sm font-bold text-white transition hover:bg-[rgba(255,145,77,0.18)]"
        >
          New Chat
        </button>
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        {suggestedQuestions.map((prompt) => (
          <button
            key={prompt}
            type="button"
            onClick={() => submitQuestion(prompt)}
            disabled={loading}
            className="rounded-2xl border border-white/10 bg-black/20 p-4 text-left text-sm font-bold text-purple-100 transition hover:border-pink-300/40 hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-60"
          >
            💬 {prompt}
          </button>
        ))}
      </div>

      <div className="mt-6 space-y-4 border-y border-white/10 py-5">
        {messages.map((message) => (
          <div
            key={message.id}
            className={
              message.role === "user"
                ? "ml-auto max-w-[92%] rounded-2xl bg-white/10 p-4 text-purple-100"
                : "max-w-[92%] rounded-2xl border border-pink-300/20 bg-pink-500/10 p-4 text-purple-100"
            }
          >
            <p className="text-xs font-black uppercase tracking-widest text-pink-300">
              {message.role === "user" ? "You" : "Maple"}
            </p>

            <div className="mt-2 prose prose-invert prose-sm max-w-none text-purple-100 prose-p:leading-relaxed prose-headings:text-white prose-strong:text-white prose-a:text-pink-300 prose-li:marker:text-pink-300">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.text}
              </ReactMarkdown>
            </div>

            {message.role === "maple" && message.text && (
              <div className="mt-3 flex flex-wrap gap-2 text-sm text-purple-100 opacity-75">
                <button
                  type="button"
                  onClick={() => void copyMessage(message.text)}
                  className="rounded-lg px-2 py-1 transition hover:bg-white/10"
                >
                  Copy
                </button>
                <button
                  type="button"
                  onClick={() => {
                    const lastUserQuestion = getPreviousUserQuestion(message.id);

                    if (lastUserQuestion) {
                      void submitQuestion(lastUserQuestion);
                    }
                  }}
                  className="rounded-lg px-2 py-1 transition hover:bg-white/10"
                >
                  Retry
                </button>
                <button
                  type="button"
                  className="rounded-lg px-2 py-1 transition hover:bg-white/10"
                  aria-label="Thumbs up"
                >
                  👍
                </button>
                <button
                  type="button"
                  className="rounded-lg px-2 py-1 transition hover:bg-white/10"
                  aria-label="Thumbs down"
                >
                  👎
                </button>
              </div>
            )}
          </div>
        ))}

        <div ref={bottomRef} />
      </div>

      {thinking && (
        <div className="mt-4 flex items-center gap-3 text-purple-100 opacity-90">
          <strong className="text-sm font-black text-pink-300">Maple</strong>
          <div className="flex gap-1.5" aria-label="Maple is thinking">
            <span className="h-2 w-2 animate-bounce rounded-full bg-[#ff9d2f]" />
            <span
              className="h-2 w-2 animate-bounce rounded-full bg-[#ff9d2f]"
              style={{ animationDelay: "0.2s" }}
            />
            <span
              className="h-2 w-2 animate-bounce rounded-full bg-[#ff9d2f]"
              style={{ animationDelay: "0.4s" }}
            />
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="mt-5 flex gap-3">
        <input
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask Maple..."
          className="min-w-0 flex-1 rounded-2xl border border-white/10 bg-black/30 px-4 py-3 text-sm text-white outline-none transition placeholder:text-purple-300 focus:border-pink-300/50"
        />

        <button
          type="submit"
          disabled={loading}
          className="rounded-2xl bg-pink-500 px-5 py-3 text-sm font-black text-white transition hover:bg-pink-400 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "..." : "Send"}
        </button>
      </form>
    </section>
  );
}
