"use client"

import { useState } from "react"
import PDFUploadSection from "@/components/pdf-upload-section"
import ChatSection from "@/components/chat-interface"

export default function Page() {
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null)
  const [documentId, setDocumentId] = useState<string | null>(null)

  return (
    <main
      className="min-h-screen bg-cover bg-center bg-no-repeat"
      style={{ backgroundImage: "url('/background.jpeg')" }}
    >
      {/* Header */}
      <header className="px-10 pt-8 pb-6">
        <h1 className="text-3xl font-semibold text-white">PaperMind</h1>
        <p className="text-white/80 text-sm">
          Ask questions from your uploaded documents
        </p>
      </header>

      {/* Content */}
      <section className="px-10 pb-10">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
          <PDFUploadSection
            uploadedFileName={uploadedFileName}
            onFileUploadSuccess={(fileName: string, docId: string) => {
              setUploadedFileName(fileName)
              setDocumentId(docId)
            }}
          />

          <ChatSection
            documentId={documentId}
            hasUploadedFile={!!uploadedFileName}
          />
        </div>
      </section>
    </main>
  )
}
