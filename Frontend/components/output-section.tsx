"use client"

import { useState } from "react"
import { Check, ChevronDown, ChevronUp, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Slider } from "@/components/ui/slider"
import { Checkbox } from "@/components/ui/checkbox"
import { AudioPlayer } from "@/components/audio-player"
import { MetricCard } from "@/components/metric-card"
import { getAudioUrl, submitFeedback } from "@/lib/api"
import type { SynthesizeResponse } from "@/lib/types"

interface OutputSectionProps {
  result: SynthesizeResponse | null
  feedbackSubmitted: string | null
  onFeedbackSubmitted: (runId: string) => void
}

export function OutputSection({
  result,
  feedbackSubmitted,
  onFeedbackSubmitted,
}: OutputSectionProps) {
  const [showDetails, setShowDetails] = useState(false)
  const [rating, setRating] = useState(4)
  const [naturalness, setNaturalness] = useState(4)
  const [clarity, setClarity] = useState(4)
  const [latencyAcceptable, setLatencyAcceptable] = useState(true)
  const [comment, setComment] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [feedbackError, setFeedbackError] = useState<string | null>(null)

  const handleFeedbackSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!result?.run_id) return

    setIsSubmitting(true)
    setFeedbackError(null)

    try {
      await submitFeedback({
        run_id: result.run_id,
        rating,
        naturalness,
        clarity,
        latency_acceptability: latencyAcceptable,
        comment: comment.trim() || undefined,
      })
      onFeedbackSubmitted(result.run_id)
    } catch (err) {
      setFeedbackError(err instanceof Error ? err.message : "Failed to submit feedback")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-bold uppercase tracking-wider text-primary">
          Output
        </p>
        <h2 className="mt-1 text-xl font-bold text-foreground">
          Latest Generation
        </h2>
        <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
          Playback, inspect run metadata, and collect evaluator feedback after a
          successful request.
        </p>
      </div>

      {!result ? (
        <div className="flex min-h-[300px] flex-col items-center justify-center rounded-lg border border-dashed border-border bg-card/50 p-8 text-center">
          <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-secondary">
            <div className="flex items-end gap-1">
              {[1, 2, 3, 4, 5].map((i) => (
                <div
                  key={i}
                  className="w-1 rounded-full bg-muted-foreground/30"
                  style={{ height: `${12 + Math.sin(i) * 8}px` }}
                />
              ))}
            </div>
          </div>
          <p className="font-semibold text-foreground">No generation yet</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Your latest result will appear here with playback, latency, cache
            status, run details, and feedback controls.
          </p>
        </div>
      ) : result.success ? (
        <div className="space-y-4">
          {/* Audio Player */}
          {result.audio_url && (
            <AudioPlayer
              src={getAudioUrl(result.audio_url)}
              onError={() => console.error("Failed to load audio")}
            />
          )}

          {/* Metrics Grid */}
          <div className="grid grid-cols-2 gap-4">
            <MetricCard
              label="Latency"
              value={Math.round(result.latency_ms)}
              suffix="ms"
              variant="primary"
            />
            <MetricCard
              label="Duration"
              value={result.audio_duration_seconds.toFixed(2)}
              suffix="s"
              variant="accent"
            />
            <MetricCard
              label="Real-Time Factor"
              value={result.real_time_factor?.toFixed(2) ?? "—"}
              suffix="x"
            />
            <MetricCard
              label="Cache"
              value={result.cache_hit ? "Hit" : "Miss"}
              variant={result.cache_hit ? "accent" : "default"}
            />
          </div>

          {/* Run Details */}
          <div className="rounded-lg border border-border bg-card">
            <button
              type="button"
              onClick={() => setShowDetails(!showDetails)}
              className="flex w-full items-center justify-between px-4 py-3 text-left text-sm font-semibold text-foreground hover:bg-secondary/50"
            >
              Run Details
              {showDetails ? (
                <ChevronUp className="h-4 w-4 text-muted-foreground" />
              ) : (
                <ChevronDown className="h-4 w-4 text-muted-foreground" />
              )}
            </button>
            {showDetails && (
              <div className="border-t border-border px-4 py-3">
                <div className="grid gap-2 text-sm sm:grid-cols-2">
                  <div>
                    <span className="text-muted-foreground">Run ID:</span>{" "}
                    <code className="text-xs text-foreground">{result.run_id}</code>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Engine:</span>{" "}
                    <code className="text-xs text-foreground">{result.engine}</code>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Voice:</span>{" "}
                    <code className="text-xs text-foreground">{result.voice}</code>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Language:</span>{" "}
                    <code className="text-xs text-foreground">{result.language}</code>
                  </div>
                  <div className="sm:col-span-2">
                    <span className="text-muted-foreground">Audio Path:</span>{" "}
                    <code className="text-xs text-foreground">{result.audio_path}</code>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Feedback Form */}
          {result.run_id && (
            <div className="rounded-lg border border-border bg-card p-4">
              <h3 className="mb-4 text-sm font-bold text-foreground">Evaluation</h3>

              {feedbackSubmitted === result.run_id ? (
                <div className="flex items-center gap-2 rounded-lg bg-[oklch(0.65_0.18_145/0.1)] px-4 py-3 text-sm font-medium text-[oklch(0.65_0.18_145)]">
                  <Check className="h-4 w-4" />
                  Feedback saved for this generation.
                </div>
              ) : (
                <form onSubmit={handleFeedbackSubmit} className="space-y-4">
                  <div className="grid gap-4 sm:grid-cols-3">
                    <div className="space-y-2">
                      <Label className="text-xs font-semibold text-muted-foreground">
                        Overall Rating: {rating}
                      </Label>
                      <Slider
                        value={[rating]}
                        onValueChange={(v) => setRating(v[0])}
                        min={1}
                        max={5}
                        step={1}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-xs font-semibold text-muted-foreground">
                        Naturalness: {naturalness}
                      </Label>
                      <Slider
                        value={[naturalness]}
                        onValueChange={(v) => setNaturalness(v[0])}
                        min={1}
                        max={5}
                        step={1}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-xs font-semibold text-muted-foreground">
                        Clarity: {clarity}
                      </Label>
                      <Slider
                        value={[clarity]}
                        onValueChange={(v) => setClarity(v[0])}
                        min={1}
                        max={5}
                        step={1}
                      />
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Checkbox
                      id="latency"
                      checked={latencyAcceptable}
                      onCheckedChange={(checked) =>
                        setLatencyAcceptable(checked === true)
                      }
                    />
                    <Label
                      htmlFor="latency"
                      className="text-sm font-medium text-foreground"
                    >
                      Latency felt acceptable
                    </Label>
                  </div>

                  <div className="space-y-2">
                    <Label
                      htmlFor="comment"
                      className="text-xs font-semibold text-muted-foreground"
                    >
                      Comment
                    </Label>
                    <Textarea
                      id="comment"
                      value={comment}
                      onChange={(e) => setComment(e.target.value)}
                      placeholder="Optional notes about output quality, clarity, or workflow fit."
                      className="min-h-[80px] resize-none bg-input"
                      maxLength={2000}
                    />
                  </div>

                  {feedbackError && (
                    <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-2 text-sm text-destructive">
                      {feedbackError}
                    </div>
                  )}

                  <Button
                    type="submit"
                    disabled={isSubmitting}
                    className="w-full font-semibold"
                  >
                    {isSubmitting ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      "Save Feedback"
                    )}
                  </Button>
                </form>
              )}
            </div>
          )}
        </div>
      ) : (
        <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          Generation failed: {result.error || "Unknown error"}
        </div>
      )}
    </div>
  )
}
