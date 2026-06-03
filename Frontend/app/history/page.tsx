"use client"

import { useState } from "react"
import useSWR from "swr"
import { RefreshCw, CheckCircle2, XCircle, Zap } from "lucide-react"
import { AppLayout } from "@/components/app-layout"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { getHealth, getVoices, getRuns } from "@/lib/api"
import type { RunRecord } from "@/lib/types"
import { cn } from "@/lib/utils"

export default function HistoryPage() {
  const [statusFilter, setStatusFilter] = useState("all")
  const [voiceFilter, setVoiceFilter] = useState("all")
  const [languageFilter, setLanguageFilter] = useState("all")
  const [cacheFilter, setCacheFilter] = useState("all")

  const { data: health } = useSWR("health", getHealth, {
    refreshInterval: 15000,
    onError: () => {},
  })

  const { data: voicesData } = useSWR("voices", getVoices, {
    refreshInterval: 60000,
    onError: () => {},
  })

  const {
    data: runs,
    isLoading,
    mutate,
  } = useSWR(
    ["runs", statusFilter, voiceFilter, languageFilter, cacheFilter],
    () =>
      getRuns({
        limit: 50,
        status: statusFilter,
        voice: voiceFilter,
        language: languageFilter,
        cache_hit: cacheFilter,
      }),
    {
      refreshInterval: 30000,
      onError: () => {},
    }
  )

  const isOnline = !!health && health.status === "healthy"
  const voices = voicesData?.voices || []
  const languages = [...new Set(voices.map((v) => v.language))].sort()
  const voiceIds = voices.map((v) => v.id)

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr)
      return date.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      })
    } catch {
      return dateStr
    }
  }

  const truncateText = (text: string, maxLength = 60) => {
    if (text.length <= maxLength) return text
    return text.slice(0, maxLength) + "..."
  }

  return (
    <AppLayout
      status={{
        isOnline,
        engine: health?.engine,
        version: health?.version,
      }}
    >
      <div className="space-y-6">
        <div>
          <p className="text-xs font-bold uppercase tracking-wider text-primary">
            History
          </p>
          <h2 className="mt-1 text-2xl font-bold text-foreground">
            Generation Runs
          </h2>
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
            Filter persisted synthesis runs by status, voice, language, and cache
            behavior.
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-end gap-4">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-muted-foreground">
              Status
            </label>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-32 bg-input">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All</SelectItem>
                <SelectItem value="success">Success</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-muted-foreground">
              Voice
            </label>
            <Select value={voiceFilter} onValueChange={setVoiceFilter}>
              <SelectTrigger className="w-36 bg-input">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All</SelectItem>
                {voiceIds.map((id) => (
                  <SelectItem key={id} value={id}>
                    {id}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-muted-foreground">
              Language
            </label>
            <Select value={languageFilter} onValueChange={setLanguageFilter}>
              <SelectTrigger className="w-28 bg-input">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All</SelectItem>
                {languages.map((lang) => (
                  <SelectItem key={lang} value={lang}>
                    {lang.toUpperCase()}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-muted-foreground">
              Cache Hit
            </label>
            <Select value={cacheFilter} onValueChange={setCacheFilter}>
              <SelectTrigger className="w-28 bg-input">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All</SelectItem>
                <SelectItem value="true">Hit</SelectItem>
                <SelectItem value="false">Miss</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={() => mutate()}
            disabled={isLoading}
            className="ml-auto"
          >
            <RefreshCw
              className={cn("mr-2 h-4 w-4", isLoading && "animate-spin")}
            />
            Refresh
          </Button>
        </div>

        {/* Table */}
        <div className="rounded-lg border border-border bg-card shadow-lg shadow-black/5">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <TableHead className="font-bold">Time</TableHead>
                <TableHead className="font-bold">Text</TableHead>
                <TableHead className="font-bold">Voice</TableHead>
                <TableHead className="font-bold">Lang</TableHead>
                <TableHead className="font-bold">Engine</TableHead>
                <TableHead className="font-bold text-right">Latency</TableHead>
                <TableHead className="font-bold text-right">Duration</TableHead>
                <TableHead className="font-bold text-center">Cache</TableHead>
                <TableHead className="font-bold text-center">Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {!runs || runs.length === 0 ? (
                <TableRow>
                  <TableCell
                    colSpan={9}
                    className="h-32 text-center text-muted-foreground"
                  >
                    {isLoading
                      ? "Loading runs..."
                      : "No runs found. Generate speech first."}
                  </TableCell>
                </TableRow>
              ) : (
                runs.map((run: RunRecord, index: number) => (
                  <TableRow key={run.run_id || index}>
                    <TableCell className="whitespace-nowrap text-xs text-muted-foreground">
                      {formatDate(run.created_at)}
                    </TableCell>
                    <TableCell
                      className="max-w-[200px] truncate text-sm"
                      title={run.text}
                    >
                      {truncateText(run.text)}
                    </TableCell>
                    <TableCell className="text-xs">{run.voice}</TableCell>
                    <TableCell className="text-xs uppercase">
                      {run.language}
                    </TableCell>
                    <TableCell className="text-xs">{run.engine}</TableCell>
                    <TableCell className="text-right font-mono text-xs">
                      {Math.round(run.latency_ms)} ms
                    </TableCell>
                    <TableCell className="text-right font-mono text-xs">
                      {run.audio_duration_seconds.toFixed(2)} s
                    </TableCell>
                    <TableCell className="text-center">
                      {run.cache_hit ? (
                        <Zap className="mx-auto h-4 w-4 text-accent" />
                      ) : (
                        <span className="text-xs text-muted-foreground">—</span>
                      )}
                    </TableCell>
                    <TableCell className="text-center">
                      {run.success ? (
                        <CheckCircle2 className="mx-auto h-4 w-4 text-[oklch(0.65_0.18_145)]" />
                      ) : (
                        <XCircle className="mx-auto h-4 w-4 text-destructive" />
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>

        {runs && runs.length > 0 && (
          <p className="text-sm text-muted-foreground">
            Showing {runs.length} run(s)
          </p>
        )}
      </div>
    </AppLayout>
  )
}
