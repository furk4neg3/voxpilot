import type {
  HealthResponse,
  VoicesResponse,
  SynthesizeResponse,
  MetricsResponse,
  RunRecord,
  FeedbackRequest,
  FeedbackResponse,
} from "./types"

// API base URL from environment variable
// In development: http://localhost:8000
// In production: set NEXT_PUBLIC_VOXPILOT_API_URL in your deployment environment
const API_BASE_URL = process.env.NEXT_PUBLIC_VOXPILOT_API_URL || "http://localhost:8000"

export class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message)
    this.name = "ApiError"
  }
}

async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 30000) // 30s timeout

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      signal: controller.signal,
      headers: {
        ...options?.headers,
      },
    })

    clearTimeout(timeoutId)

    if (!response.ok) {
      const errorBody = await response.json().catch(() => null)
      throw new ApiError(
        errorBody?.detail || `Request failed with status ${response.status}`,
        response.status
      )
    }

    return response.json()
  } catch (error) {
    clearTimeout(timeoutId)
    if (error instanceof ApiError) throw error
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError("Request timed out. The backend may be slow or unresponsive.")
    }
    if (error instanceof TypeError) {
      throw new ApiError("Cannot reach backend. Is the server running at " + API_BASE_URL + "?")
    }
    throw new ApiError(error instanceof Error ? error.message : "Unknown error")
  }
}

// Export the base URL for debugging and audio URL construction
export function getApiBaseUrl(): string {
  return API_BASE_URL
}

export async function getHealth(): Promise<HealthResponse> {
  return fetchApi<HealthResponse>("/health")
}

export async function getVoices(): Promise<VoicesResponse> {
  return fetchApi<VoicesResponse>("/voices")
}

export async function synthesize(
  text: string,
  language: string,
  voice: string,
  style?: string
): Promise<SynthesizeResponse> {
  const formData = new FormData()
  formData.append("text", text)
  formData.append("language", language)
  formData.append("voice", voice)
  if (style) formData.append("style", style)

  return fetchApi<SynthesizeResponse>("/synthesize", {
    method: "POST",
    body: formData,
  })
}

export async function getMetrics(): Promise<MetricsResponse> {
  return fetchApi<MetricsResponse>("/metrics")
}

export async function getRuns(params?: {
  limit?: number
  status?: string
  voice?: string
  language?: string
  cache_hit?: string
}): Promise<RunRecord[]> {
  const searchParams = new URLSearchParams()
  if (params?.limit) searchParams.set("limit", params.limit.toString())
  // Backend expects status as "success" or "failed" string
  if (params?.status && params.status !== "all") searchParams.set("status", params.status)
  if (params?.voice && params.voice !== "all") searchParams.set("voice", params.voice)
  if (params?.language && params.language !== "all") searchParams.set("language", params.language)
  // Backend expects cache_hit as boolean query param ("true" or "false")
  if (params?.cache_hit && params.cache_hit !== "all") searchParams.set("cache_hit", params.cache_hit)

  const query = searchParams.toString()
  return fetchApi<RunRecord[]>(`/runs${query ? `?${query}` : ""}`)
}

export async function submitFeedback(
  feedback: FeedbackRequest
): Promise<FeedbackResponse> {
  return fetchApi<FeedbackResponse>("/feedback", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(feedback),
  })
}

export function getAudioUrl(audioUrl: string): string {
  if (audioUrl.startsWith("http")) return audioUrl
  return `${API_BASE_URL}${audioUrl}`
}
