"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Mic2, History, BarChart3, Radio } from "lucide-react"

const navigation = [
  { name: "Generate", href: "/", icon: Mic2 },
  { name: "History", href: "/history", icon: History },
  { name: "Metrics", href: "/metrics", icon: BarChart3 },
]

interface AppLayoutProps {
  children: React.ReactNode
  status?: {
    isOnline: boolean
    engine?: string
    version?: string
  }
}

export function AppLayout({ children, status }: AppLayoutProps) {
  const pathname = usePathname()

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          {/* Logo and Nav */}
          <div className="flex items-center gap-8">
            <Link href="/" className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
                <Radio className="h-5 w-5 text-primary-foreground" />
              </div>
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-primary">
                  VoxPilot
                </span>
                <h1 className="text-lg font-bold leading-none text-foreground">
                  TTS Studio
                </h1>
              </div>
            </Link>

            <nav className="hidden md:flex">
              <div className="flex items-center gap-1 rounded-lg bg-secondary p-1">
                {navigation.map((item) => {
                  const isActive = pathname === item.href
                  return (
                    <Link
                      key={item.name}
                      href={item.href}
                      className={cn(
                        "flex items-center gap-2 rounded-md px-4 py-2 text-sm font-semibold transition-all",
                        isActive
                          ? "bg-card text-foreground shadow-sm"
                          : "text-muted-foreground hover:text-foreground"
                      )}
                    >
                      <item.icon className="h-4 w-4" />
                      {item.name}
                    </Link>
                  )
                })}
              </div>
            </nav>
          </div>

          {/* Status Badges */}
          <div className="flex items-center gap-2">
            {status?.isOnline ? (
              <>
                <div className="flex items-center gap-2 rounded-full border border-[oklch(0.65_0.18_145/0.3)] bg-[oklch(0.65_0.18_145/0.1)] px-3 py-1.5 text-xs font-semibold text-[oklch(0.65_0.18_145)]">
                  <span className="h-2 w-2 rounded-full bg-current" />
                  Connected
                </div>
                {status.engine && (
                  <div className="hidden rounded-full border border-border bg-secondary px-3 py-1.5 text-xs font-semibold text-muted-foreground sm:block">
                    {status.engine}
                  </div>
                )}
                {status.version && (
                  <div className="hidden rounded-full border border-border bg-secondary px-3 py-1.5 text-xs font-semibold text-muted-foreground sm:block">
                    v{status.version}
                  </div>
                )}
              </>
            ) : (
              <div className="flex items-center gap-2 rounded-full border border-destructive/30 bg-destructive/10 px-3 py-1.5 text-xs font-semibold text-destructive">
                <span className="h-2 w-2 rounded-full bg-current" />
                Disconnected
              </div>
            )}
          </div>
        </div>

        {/* Mobile Nav */}
        <nav className="border-t border-border px-4 py-2 md:hidden">
          <div className="flex items-center gap-1 rounded-lg bg-secondary p-1">
            {navigation.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex flex-1 items-center justify-center gap-2 rounded-md px-3 py-2 text-sm font-semibold transition-all",
                    isActive
                      ? "bg-card text-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  <item.icon className="h-4 w-4" />
                  <span className="hidden sm:inline">{item.name}</span>
                </Link>
              )
            })}
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-border py-8 text-center">
        <p className="text-sm text-muted-foreground">
          Built for TTS product infrastructure, evaluation, and observability
        </p>
        <p className="text-xs text-muted-foreground/70">
          VoxPilot v1.0.0
        </p>
      </footer>
    </div>
  )
}
