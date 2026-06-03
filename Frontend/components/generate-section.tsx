"use client"

import { useState, useMemo } from "react"
import { Loader2, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { synthesize } from "@/lib/api"
import type { Voice, SynthesizeResponse } from "@/lib/types"
import { cn } from "@/lib/utils"

interface GenerateSectionProps {
  voices: Voice[]
  isOnline: boolean
  onSynthesisComplete: (result: SynthesizeResponse) => void
}

export function GenerateSection({
  voices,
  isOnline,
  onSynthesisComplete,
}: GenerateSectionProps) {
  const [text, setText] = useState("")
  const [selectedLanguage, setSelectedLanguage] = useState("en")
  const [selectedVoice, setSelectedVoice] = useState("default")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const languages = useMemo(() => {
    const langSet = new Set(voices.map((v) => v.language))
    return langSet.size > 0 ? Array.from(langSet).sort() : ["en"]
  }, [voices])

  const filteredVoices = useMemo(() => {
    const filtered = voices.filter((v) => v.language === selectedLanguage)
    return filtered.length > 0 ? filtered : [{ id: "default", name: "Default", language: "en" }]
  }, [voices, selectedLanguage])

  const charCount = text.length
  const charStatus = charCount > 950 ? (charCount > 1000 ? "over" : "warn") : "ok"

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!text.trim()) {
      setError("Please enter some text to synthesize.")
      return
    }
    if (!isOnline) {
      setError("Backend is not reachable. Please start the server first.")
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const result = await synthesize(text.trim(), selectedLanguage, selectedVoice)
      onSynthesisComplete(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Synthesis failed")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-bold uppercase tracking-wider text-primary">
          Compose
        </p>
        <h2 className="mt-1 text-xl font-bold text-foreground">
          Generation Request
        </h2>
        <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
          Enter the script, choose a language and voice preset, then generate
          speech through the active backend service.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="rounded-lg border border-border bg-card p-6 shadow-lg shadow-black/5">
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="text" className="text-sm font-bold text-foreground">
                Text Input
              </Label>
              <Textarea
                id="text"
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="e.g. Welcome to VoxPilot, a TTS Studio for speech generation workflows and latency-aware evaluation."
                className="min-h-[180px] resize-none bg-input text-foreground placeholder:text-muted-foreground"
                maxLength={1000}
              />
              <p
                className={cn(
                  "text-right text-xs font-semibold",
                  charStatus === "ok" && "text-muted-foreground",
                  charStatus === "warn" && "text-[oklch(0.75_0.15_80)]",
                  charStatus === "over" && "text-destructive"
                )}
              >
                {charCount} / 1,000 characters
              </p>
            </div>

            <div className="h-px bg-border" />

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="language" className="text-sm font-bold text-foreground">
                  Language
                </Label>
                <Select
                  value={selectedLanguage}
                  onValueChange={(value) => {
                    setSelectedLanguage(value)
                    setSelectedVoice("default")
                  }}
                >
                  <SelectTrigger id="language" className="bg-input">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {languages.map((lang) => (
                      <SelectItem key={lang} value={lang}>
                        {lang.toUpperCase()}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="voice" className="text-sm font-bold text-foreground">
                  Voice Preset
                </Label>
                <Select value={selectedVoice} onValueChange={setSelectedVoice}>
                  <SelectTrigger id="voice" className="bg-input">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {filteredVoices.map((voice) => (
                      <SelectItem key={voice.id} value={voice.id}>
                        {voice.name}
                        {voice.gender && ` · ${voice.gender}`}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
        </div>

        {error && (
          <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
            {error}
          </div>
        )}

        <Button
          type="submit"
          size="lg"
          disabled={isLoading || !isOnline}
          className="w-full bg-gradient-to-r from-primary to-accent font-bold shadow-lg shadow-primary/20 transition-all hover:shadow-primary/30"
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Sparkles className="mr-2 h-4 w-4" />
              Generate Speech
            </>
          )}
        </Button>
      </form>
    </div>
  )
}
