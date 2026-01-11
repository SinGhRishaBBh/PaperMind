import "./globals.css"
import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "PaperMind",
  description: "Ask questions from your uploaded PDFs",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="app-bg">
        {children}
      </body>
    </html>
  )
}
