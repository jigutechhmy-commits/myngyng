export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"

export interface CategorySummary {
  id: string
  name_ko: string
  enabled: boolean
}

export interface PriorityOption {
  key: string
  label_ko: string
}

export interface CategoryDetail extends CategorySummary {
  spec_schema: {
    fields: {
      key: string
      label_ko: string
      type: string
      unit?: string
      required?: boolean
    }[]
  }
  priority_options: PriorityOption[]
}

export interface SessionCreatePayload {
  category_id: string
  budget: number
  budget_tolerance_pct: number
  usage_text: string
  priorities: string[]
  tournament_size: number
}

export interface SpecSheet {
  summary: string
  fields: { key: string; label_ko: string; value: string }[]
  rationale: string
}

export interface SessionOut extends SessionCreatePayload {
  id: string
  engine_phase: string
  spec_sheet?: SpecSheet | null
}

export interface ReviewOut {
  summary: string
  sources: string[]
  fit_score: number
  budget_score: number
  satisfaction_score: number
  missing_required: boolean
  critical_flaw: string | null
}

export interface CandidateOut {
  id: string
  name: string
  brand: string
  price: number
  specs: Record<string, string | number>
  source: string
  status: string
  elimination_reason: string | null
  review: ReviewOut | null
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  })
  if (!res.ok) {
    const body = await res.text()
    throw new Error(`API ${res.status}: ${body}`)
  }
  return res.json()
}

export function listCategories() {
  return request<{ categories: CategorySummary[] }>("/api/categories")
}

export function getCategory(id: string) {
  return request<CategoryDetail>(`/api/categories/${id}`)
}

export function createSession(payload: SessionCreatePayload) {
  return request<SessionOut>("/api/sessions", {
    method: "POST",
    body: JSON.stringify(payload),
  })
}

export function getSession(id: string) {
  return request<SessionOut>(`/api/sessions/${id}`)
}

export function runPlan(id: string) {
  return request<SessionOut>(`/api/sessions/${id}/plan`, { method: "POST" })
}

export function runResearch(id: string) {
  return request<CandidateOut[]>(`/api/sessions/${id}/research`, {
    method: "POST",
  })
}

export function runReviewScan(id: string) {
  return request<CandidateOut[]>(`/api/sessions/${id}/review-scan`, {
    method: "POST",
  })
}

export function runListUp(id: string) {
  return request<CandidateOut[]>(`/api/sessions/${id}/list-up`, {
    method: "POST",
  })
}

export function listCandidates(id: string) {
  return request<CandidateOut[]>(`/api/sessions/${id}/candidates`)
}

export interface NarrativeOut {
  narrative: string
  story: string
  digging_scores: Record<string, number>
  sources: string[]
  ai_inferred: boolean
}

export interface CardOut {
  candidate_id: string
  name: string
  brand: string
  price: number
  headline: string
  key_specs: string[]
  pros: string[]
  cons: string[]
  review_digest: string
  worldview: string
  recommended_for: string[]
  not_recommended_for: string[]
  narrative: NarrativeOut | null
}

export function runDigging(id: string) {
  return request<CandidateOut[]>(`/api/sessions/${id}/digging`, {
    method: "POST",
  })
}

export function runFinalEntry(id: string) {
  return request<CardOut[]>(`/api/sessions/${id}/final-entry`, {
    method: "POST",
  })
}

export function listCards(id: string) {
  return request<CardOut[]>(`/api/sessions/${id}/cards`)
}
