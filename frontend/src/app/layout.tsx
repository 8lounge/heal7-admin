import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Toaster } from 'sonner'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'HEAL7 관리자 대시보드',
  description: 'HEAL7 명리학 및 시스템 관리 대시보드',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <body className={inter.className}>
        <div className="min-h-screen bg-background">
          {children}
          <Toaster richColors position="top-right" />
        </div>
      </body>
    </html>
  )
}