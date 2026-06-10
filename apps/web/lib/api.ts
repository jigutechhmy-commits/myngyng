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

export interface SessionOut extends SessionCreatePayload {
  id: string
  engine_phase: string
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
