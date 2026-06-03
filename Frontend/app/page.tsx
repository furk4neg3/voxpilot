"use client"

import { useState } from "react"
import useSWR from "swr"
import { AppLayout } from "@/components/app-layout"
import { GenerateSection } from "@/components/generate-section"
import { OutputSection } from "@/components/output-section"
import { getHealth, getVoices } from "@/lib/api"
import type { SynthesizeResponse } from "@/lib/types"

export default function HomePage() {
  const [synthesisResult, setSynthesisResult] = useState<SynthesizeResponse | null>(null)
  const [feedbackSubmitted, setFeedbackSubmitted] = useState<string | null>(null)

  const { data: health } = useSWR("health", getHealth, {
    refreshInterval: 15000,
    onError: () => {},
  })

  const { data: voicesData } = useSWR("voices", getVoices, {
    refreshInterval: 60000,
    onError: () => {},
  })

  const isOnline = !!health && health.status === "healthy"
  const voices = voicesData?.voices || []

  const handleSynthesisComplete = (result: SynthesizeResponse) => {
    setSynthesisResult(result)
    setFeedbackSubmitted(null)
  }

  const handleFeedbackSubmitted = (runId: string) => {
    setFeedbackSubmitted(runId)
  }

  return (
    <AppLayout
      status={{
        isOnline,
        engine: health?.engine,
        version: health?.version,
      }}
    >
      <div className="grid gap-8 lg:grid-cols-2">
        <GenerateSection
          voices={voices}
          isOnline={isOnline}
          onSynthesisComplete={handleSynthesisComplete}
        />
        <OutputSection
          result={synthesisResult}
          feedbackSubmitted={feedbackSubmitted}
          onFeedbackSubmitted={handleFeedbackSubmitted}
        />
      </div>
    </AppLayout>
  )
}
