"use client";

import { FormEvent, useState } from "react";
import { askMaple } from "@/lib/api";

const suggestedQuestions = [
  "Why is this anime trending?",
  "Is it worth watching?",
  "Who would enjoy this anime?",
  "What does the Maple Score mean?",
  "What's the story about?",
  "Who animated this?",
  "How many episodes are there?",
  "Is it finished airing?",
  "Any recent news?",
];

type Message = {
  role: "user" | "maple";
  text: string;
};

export function AskMaplePanel({ animeId }: { animeId: string | number }) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "maple",
      text: "Hi! I'm Maple. Ask me about trends, scores, recommendations, or news for this anime.",
    },
  ]);
  const [loading, setLoading] = useState(false);

  async function submitQuestion(nextQuestion: string) {
    const trimmed = nextQuestion.trim();

    if (!trimmed || loading) return;

    setLoading(true);
    setQuestion("");
    setMessages((current) => [
      ...current,
      { role: "user", text: trimmed },
    ]);

    const response = await askMaple(String(animeId), trimmed);
    const answer = response?.answer?.trim();

    setMessages((current) => [
      ...current,
      {
        role: "maple",
        text:
          answer ||
          "Maple could not answer that yet. Try asking about trends, scores, recommendations, or news.",
      },
    ]);
    setLoading(false);
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    submitQuestion(question);
  }

  return (
    <section className="mt-10 rounded-3xl border border-pink-300/20 bg-gradient-to-r from-pink-500/10 via-purple-500/10 to-cyan-500/10 p-6">
      <div>
        <h2 className="text-xl font-black">🍁 Ask Maple</h2>
        <p className="mt-2 text-sm text-purple-200">
          Ask questions about this anime.
        </p>
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
        {messages.map((message, index) => (
          <div
            key={`${message.role}-${index}`}
            className={
              message.role === "user"
                ? "ml-auto max-w-[92%] rounded-2xl bg-white/10 p-4 text-purple-100"
                : "max-w-[92%] rounded-2xl border border-pink-300/20 bg-pink-500/10 p-4 text-purple-100"
            }
          >
            <p className="text-xs font-black uppercase tracking-widest text-pink-300">
              {message.role === "user" ? "You" : "Maple"}
            </p>

            <p className="mt-2 leading-relaxed">{message.text}</p>
          </div>
        ))}

        {loading && (
          <div className="max-w-[92%] rounded-2xl border border-pink-300/20 bg-pink-500/10 p-4 text-purple-100">
            <p className="text-xs font-black uppercase tracking-widest text-pink-300">
              Maple
            </p>
            <div className="mt-3 flex items-center gap-2" aria-label="Maple is thinking">
              <span className="h-2 w-2 animate-bounce rounded-full bg-pink-300" />
              <span
                className="h-2 w-2 animate-bounce rounded-full bg-purple-300"
                style={{ animationDelay: "120ms" }}
              />
              <span
                className="h-2 w-2 animate-bounce rounded-full bg-cyan-300"
                style={{ animationDelay: "240ms" }}
              />
            </div>
          </div>
        )}
      </div>

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
