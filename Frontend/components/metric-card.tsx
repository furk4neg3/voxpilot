"use client"

import { cn } from "@/lib/utils"

interface MetricCardProps {
  label: string
  value: string | number
  suffix?: string
  variant?: "default" | "primary" | "accent" | "warning" | "destructive"
  highlight?: "top" | "none"
}

export function MetricCard({
  label,
  value,
  suffix,
  variant = "default",
  highlight = "none",
}: MetricCardProps) {
  const valueColorClass = {
    default: "text-foreground",
    primary: "text-primary",
    accent: "text-accent",
    warning: "text-[oklch(0.75_0.15_80)]",
    destructive: "text-destructive",
  }[variant]

  const highlightClass = {
    top: "border-t-2 border-t-primary",
    none: "",
  }[highlight]

  return (
    <div
      className={cn(
        "flex flex-col justify-center rounded-lg border border-border bg-card p-5 shadow-lg shadow-black/5 transition-colors hover:border-primary/30",
        highlightClass
      )}
    >
      <p className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
        {label}
      </p>
      <p className={cn("mt-2 text-3xl font-bold", valueColorClass)}>
        {value}
        {suffix && (
          <span className="ml-0.5 text-base font-semibold">{suffix}</span>
        )}
      </p>
    </div>
  )
}
