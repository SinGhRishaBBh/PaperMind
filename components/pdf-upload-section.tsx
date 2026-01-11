"use client"

import { useRef, useState } from "react"

interface Props {
  uploadedFileName: string | null
  onFileUploadSuccess: (fileName: string, docId: string) => void
}

export default function PDFUploadSection({
  uploadedFileName,
  onFileUploadSuccess,
}: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [loading, setLoading] = useState(false)

  const BACKEND_URL =
    process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:5000"

  async function upload(file: File) {
    setLoading(true)
    const formData = new FormData()
    formData.append("file", file)

    try {
      const res = await fetch(`${BACKEND_URL}/upload-pdf`, {
        method: "POST",
        body: formData,
      })

      if (!res.ok) throw new Error()

      const data = await res.json()
      onFileUploadSuccess(file.name, data.document_id)
    } catch {
      alert("PDF upload failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="rounded-xl bg-white/60 backdrop-blur-md border border-black/20 shadow-xl p-6">
      <h2 className="text-lg font-semibold text-black mb-4">Upload PDF</h2>

      <div
        onClick={() => inputRef.current?.click()}
        className="cursor-pointer rounded-lg border-2 border-dashed border-black/30 bg-white/40 hover:bg-white/50 transition p-8 text-center"
      >
        <p className="text-black font-medium">Drag and drop your PDF here</p>
        <p className="text-sm text-black/70">or click to browse</p>

        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          hidden
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) upload(file)
          }}
        />
      </div>

      {loading && (
        <p className="mt-4 text-sm text-black">Uploading…</p>
      )}

      {uploadedFileName && !loading && (
        <div className="mt-4 p-3 rounded-lg bg-white/50 border border-black/20">
          <p className="text-sm text-black break-all">
            {uploadedFileName}
          </p>
        </div>
      )}
    </div>
  )
}
