"use client"

import useSWR from "swr"
import { RefreshCw } from "lucide-react"
import { AppLayout } from "@/components/app-layout"
import { MetricCard } from "@/components/metric-card"
import { Button } from "@/components/ui/button"
import { getHealth, getMetrics } from "@/lib/api"

export default function MetricsPage() {
  const { data: health } = useSWR("health", getHealth, {
    refreshInterval: 15000,
    onError: () => {},
  })

  const {
    data: metrics,
    isLoading,
    mutate,
  } = useSWR("metrics", getMetrics, {
    refreshInterval: 30000,
    onError: () => {},
  })

  const isOnline = !!health && health.status === "healthy"

  const successRate =
    metrics && metrics.total_requests > 0
      ? ((metrics.successful_requests / metrics.total_requests) * 100).toFixed(1)
      : "0.0"

  const cacheHitRate =
    typeof metrics?.cache_hit_rate === "number"
      ? (metrics.cache_hit_rate * 100).toFixed(1)
      : "0.0"

  return (
    <AppLayout
      status={{
        isOnline,
        engine: health?.engine,
        version: health?.version,
      }}
    >
      <div className="space-y-8">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-wider text-primary">
              Metrics
            </p>
            <h2 className="mt-1 text-2xl font-bold text-foreground">
              System Performance
            </h2>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
              Monitor process-local request counts, latency, cache behavior,
              engine usage, and evaluation feedback.
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => mutate()}
            disabled={isLoading}
          >
            <RefreshCw
              className={`mr-2 h-4 w-4 ${isLoading ? "animate-spin" : ""}`}
            />
            Refresh
          </Button>
        </div>

        {!metrics ? (
          <div className="flex h-64 items-center justify-center rounded-lg border border-dashed border-border bg-card/50">
            <p className="text-muted-foreground">
              {isLoading ? "Loading metrics..." : "Could not fetch metrics"}
            </p>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Request Metrics */}
            <section>
              <h3 className="mb-4 text-sm font-bold uppercase tracking-wider text-muted-foreground">
                Request Statistics
              </h3>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                <MetricCard
                  label="Total Requests"
                  value={metrics.total_requests.toLocaleString()}
                  variant="primary"
                />
                <MetricCard
                  label="Success Rate"
                  value={successRate}
                  suffix="%"
                  variant="accent"
                />
                <MetricCard
                  label="Failed Requests"
                  value={metrics.failed_requests.toLocaleString()}
                  variant={metrics.failed_requests > 0 ? "destructive" : "default"}
                />
              </div>
            </section>

            {/* Latency Metrics */}
            <section>
              <h3 className="mb-4 text-sm font-bold uppercase tracking-wider text-muted-foreground">
                Latency Performance
              </h3>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                <MetricCard
                  label="Avg Latency"
                  value={Math.round(metrics.average_latency_ms)}
                  suffix="ms"
                  variant="primary"
                />
                <MetricCard
                  label="P95 Latency"
                  value={
                    metrics.p95_latency_ms !== undefined
                      ? Math.round(metrics.p95_latency_ms)
                      : "—"
                  }
                  suffix={metrics.p95_latency_ms !== undefined ? "ms" : ""}
                  variant="warning"
                />
                <MetricCard
                  label="Cache Hit Rate"
                  value={cacheHitRate}
                  suffix="%"
                  variant="accent"
                />
              </div>
            </section>

            {/* Engine Info */}
            <section>
              <h3 className="mb-4 text-sm font-bold uppercase tracking-wider text-muted-foreground">
                Engine Information
              </h3>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="rounded-lg border-t-2 border-t-primary border border-border bg-card p-5 shadow-lg shadow-black/5">
                  <p className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                    Most Used Voice
                  </p>
                  <p className="mt-2 text-xl font-bold text-foreground">
                    {metrics.most_used_voice || "—"}
                  </p>
                </div>
                <div className="rounded-lg border-t-2 border-t-accent border border-border bg-card p-5 shadow-lg shadow-black/5">
                  <p className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                    Active Engine
                  </p>
                  <p className="mt-2 text-xl font-bold text-foreground">
                    {metrics.engine || "—"}
                  </p>
                </div>
              </div>
            </section>

            {/* Feedback Metrics */}
            <section>
              <h3 className="mb-4 text-sm font-bold uppercase tracking-wider text-muted-foreground">
                Evaluation Feedback
              </h3>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <MetricCard
                  label="Feedback Count"
                  value={metrics.feedback_count.toLocaleString()}
                  variant="primary"
                />
                <MetricCard
                  label="Avg Rating"
                  value={
                    typeof metrics.average_rating === "number"
                      ? metrics.average_rating.toFixed(2)
                      : "—"
                  }
                  variant="accent"
                />
                <MetricCard
                  label="Avg Naturalness"
                  value={
                    typeof metrics.average_naturalness === "number"
                      ? metrics.average_naturalness.toFixed(2)
                      : "—"
                  }
                />
                <MetricCard
                  label="Avg Clarity"
                  value={
                    typeof metrics.average_clarity === "number"
                      ? metrics.average_clarity.toFixed(2)
                      : "—"
                  }
                />
              </div>
            </section>
          </div>
        )}
      </div>
    </AppLayout>
  )
}
