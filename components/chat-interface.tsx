"use client"

import { useState } from "react"

type Message = {
  role: "user" | "assistant" | "system"
  content: string
}

export default function ChatInterface({
  hasUploadedFile,
  documentId,
}: {
  hasUploadedFile: boolean
  documentId: string | null
}) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const BACKEND_URL =
    process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:5000"

  async function askQuestion() {
    if (!input.trim() || !hasUploadedFile || !documentId) return

    const question = input.trim()
    setInput("")
    setIsLoading(true)

    // 1️⃣ Show user question
    setMessages(prev => [...prev, { role: "user", content: question }])

    // 2️⃣ Show system thinking message
    setMessages(prev => [
      ...prev,
      {
        role: "system",
        content: "Reading document and thinking…",
      },
    ])

    try {
      const res = await fetch(`${BACKEND_URL}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          document_id: documentId,
        }),
      })

      const data = await res.json()

      // 3️⃣ Replace thinking message with real answer
      setMessages(prev =>
        prev
          .filter(m => m.role !== "system")
          .concat({
            role: "assistant",
            content:
              data.answer?.trim() ||
              "No relevant answer found in the document.",
          })
      )
    } catch (err) {
      setMessages(prev =>
        prev
          .filter(m => m.role !== "system")
          .concat({
            role: "assistant",
            content: "Error while reading the document.",
          })
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Chat Window */}
      <div className="flex-1 overflow-y-auto space-y-4 p-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`max-w-[80%] px-4 py-2 rounded-lg text-sm ${
              msg.role === "user"
                ? "ml-auto bg-blue-600 text-white"
                : msg.role === "assistant"
                ? "mr-auto bg-white/70 backdrop-blur-md text-black"
                : "mr-auto italic text-gray-600"
            }`}
          >
            {msg.content}
          </div>
        ))}
      </div>

      {/* Input */}
      <div className="p-3 flex gap-2">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder={
            hasUploadedFile
              ? "Ask a question about your document..."
              : "Upload a PDF first"
          }
          disabled={!hasUploadedFile || isLoading}
          className="flex-1 px-3 py-2 rounded border bg-white/70 backdrop-blur-md"
        />

        <button
          onClick={askQuestion}
          disabled={!hasUploadedFile || isLoading}
          className="px-4 py-2 bg-black text-white rounded disabled:opacity-50"
        >
          {isLoading ? "Thinking…" : "Ask"}
        </button>
      </div>
    </div>
  )
}
