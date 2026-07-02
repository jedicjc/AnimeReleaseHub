"use client";

import { useState } from "react";

import { API_URL } from "@/lib/config";

export default function ChatPage() {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState("");
  const userId = "user-1";

  const send = async () => {
    setResponse("");

    const res = await fetch(`${API_URL}/maple/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        user_id: userId,
      }),
    });

    const reader = res.body?.getReader();
    const decoder = new TextDecoder();

    let fullText = "";

    if (!reader) return;

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      fullText += chunk;
      setResponse(fullText);
    }
  };

  return (
    <main className="min-h-screen bg-[#120d1c] p-10 text-white">
      <h1 className="text-2xl font-black">Ask Maple</h1>

      <div className="mt-6 flex gap-2">
        <input
          className="w-full rounded bg-white/10 p-2"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />

        <button onClick={send} className="rounded bg-pink-500 px-4 py-2">
          Ask
        </button>
      </div>

      {response && (
        <div className="mt-6 rounded-xl border border-white/10 bg-white/5 p-4">
          <p className="whitespace-pre-wrap text-purple-200">
            {response}
          </p>
        </div>
      )}
    </main>
  );
}
