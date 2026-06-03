// API Types for VoxPilot TTS Studio

export interface Voice {
  id: string
  name: string
  language: string
  gender?: string
  description?: string
}

export interface HealthResponse {
  status: string
  engine: string
  model_loaded: boolean
  version: string
  timestamp: string
}

export interface VoicesResponse {
  voices: Voice[]
  engine: string
}

export interface SynthesizeResponse {
  success: boolean
  run_id: string
  audio_path: string
  audio_url: string
  latency_ms: number
  audio_duration_seconds: number
  real_time_factor?: number
  cache_hit: boolean
  engine: string
  voice: string
  language: string
  error?: string
}

export interface MetricsResponse {
  total_requests: number
  successful_requests: number
  failed_requests: number
  average_latency_ms: number
  p95_latency_ms?: number
  cache_hit_count: number
  cache_hit_rate?: number
  most_used_voice?: string
  engine: string
  feedback_count: number
  average_rating?: number
  average_naturalness?: number
  average_clarity?: number
  latency_acceptability_rate?: number
}

export interface RunRecord {
  id?: number
  run_id: string
  text: string
  language: string
  voice: string
  engine: string
  latency_ms: number
  audio_duration_seconds: number
  real_time_factor?: number
  cache_hit: boolean
  success: boolean
  error?: string
  text_length: number
  created_at: string
}

export interface FeedbackRequest {
  run_id: string
  rating: number
  naturalness?: number
  clarity?: number
  latency_acceptability?: boolean
  comment?: string
}

export interface FeedbackResponse {
  success: boolean
  feedback_id: number
  run_id: string
  rating: number
  naturalness?: number
  clarity?: number
  latency_acceptability?: boolean
  comment?: string
  created_at: string
}
