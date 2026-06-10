"use client"

import { use, useCallback, useEffect, useState } from "react"

import {
  CandidateOut,
  getSession,
  listCandidates,
  runListUp,
  runPlan,
  runResearch,
  runReviewScan,
  SessionOut,
} from "@/lib/api"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

const PHASE_LABELS: Record<string, string> = {
  created: "생성됨",
  plan: "PLAN 완료",
  research: "RESEARCH 완료",
  review_scan: "REVIEW SCAN 완료",
  list_up: "LIST UP 완료",
  digging: "DIGGING 완료",
  final_entry: "FINAL ENTRY 완료",
  choice: "CHOICE 진행 중",
  done: "완료",
}

const ELIMINATION_LABELS: Record<string, string> = {
  budget_exceeded: "예산 초과",
  missing_required: "필수 기능 없음",
  critical_flaw: "치명적 결함",
  low_satisfaction: "낮은 만족도",
  no_review: "후기 없음",
}

// 자동 실행 파이프라인: 현재 phase → 다음 단계
const PIPELINE: { from: string; label: string; run: (id: string) => Promise<unknown> }[] = [
  { from: "created", label: "PLAN — 요구사항을 분석하는 중...", run: runPlan },
  { from: "plan", label: "RESEARCH — 시장 후보를 수집하는 중...", run: runResearch },
  { from: "research", label: "REVIEW SCAN — 실사용 후기를 분석하는 중...", run: runReviewScan },
  { from: "review_scan", label: "LIST UP — 후보를 압축하는 중...", run: runListUp },
]

export default function SessionPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = use(params)
  const [session, setSession] = useState<SessionOut | null>(null)
  const [candidates, setCandidates] = useState<CandidateOut[]>([])
  const [running, setRunning] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    const s = await getSession(id)
    setSession(s)
    if (s.engine_phase !== "created" && s.engine_phase !== "plan") {
      setCandidates(await listCandidates(id))
    }
    return s
  }, [id])

  useEffect(() => {
    refresh().catch(() => setError("세션을 불러오지 못했습니다."))
  }, [refresh])

  async function runEngine() {
    setError(null)
    try {
      let phase = session?.engine_phase ?? "created"
      for (const step of PIPELINE) {
        if (step.from !== phase) continue
        setRunning(step.label)
        await step.run(id)
        phase = (await refresh()).engine_phase
      }
    } catch {
      setError("엔진 실행에 실패했습니다. 잠시 후 다시 시도해주세요.")
    } finally {
      setRunning(null)
    }
  }

  const phase = session?.engine_phase ?? "created"
  const canRun = PIPELINE.some((s) => s.from === phase)
  const shortlisted = candidates.filter((c) => c.status === "shortlisted")
  const eliminated = candidates.filter((c) => c.status === "eliminated")
  const pending = candidates.filter(
    (c) => c.status !== "shortlisted" && c.status !== "eliminated"
  )

  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-6 px-6 py-10">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Good Choice Engine</span>
            <Badge>{PHASE_LABELS[phase] ?? phase}</Badge>
          </CardTitle>
          <CardDescription>
            {session && (
              <>
                {session.budget.toLocaleString()}원 ±{session.budget_tolerance_pct}% ·{" "}
                {session.tournament_size === 0 ? "Auto" : `${session.tournament_size}강`} ·{" "}
                {session.usage_text}
              </>
            )}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {error && <p className="text-destructive text-sm">{error}</p>}
          {running && <p className="text-muted-foreground animate-pulse text-sm">{running}</p>}
          {canRun && !running && (
            <Button onClick={runEngine}>
              {phase === "created" ? "분석 시작" : "다음 단계 실행"}
            </Button>
          )}
        </CardContent>
      </Card>

      {session?.spec_sheet && (
        <Card>
          <CardHeader>
            <CardTitle>최적 사양서</CardTitle>
            <CardDescription>{session.spec_sheet.summary}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <dl className="space-y-2">
              {session.spec_sheet.fields.map((f) => (
                <div key={f.key} className="flex gap-2">
                  <dt className="text-muted-foreground w-24 shrink-0">{f.label_ko}</dt>
                  <dd>{f.value}</dd>
                </div>
              ))}
            </dl>
            <p className="text-muted-foreground border-t pt-3 text-xs leading-relaxed">
              {session.spec_sheet.rationale}
            </p>
          </CardContent>
        </Card>
      )}

      {shortlisted.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>1차 통과 후보 ({shortlisted.length})</CardTitle>
            <CardDescription>
              자동 탈락을 통과한 후보입니다. 다음 단계(DIGGING)는 M4에서 구현됩니다.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="divide-y">
              {shortlisted.map((c) => (
                <CandidateRow key={c.id} candidate={c} />
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {pending.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>후보군 ({pending.length})</CardTitle>
            <CardDescription>
              {phase === "research"
                ? "시장 조사로 수집된 1차 후보입니다."
                : "후기 분석이 완료된 후보입니다. LIST UP을 실행해 압축하세요."}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="divide-y">
              {pending.map((c) => (
                <CandidateRow key={c.id} candidate={c} />
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {eliminated.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-muted-foreground">
              자동 탈락 ({eliminated.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="divide-y opacity-60">
              {eliminated.map((c) => (
                <CandidateRow key={c.id} candidate={c} />
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </main>
  )
}

function CandidateRow({ candidate: c }: { candidate: CandidateOut }) {
  return (
    <li className="space-y-1 py-3 text-sm">
      <div className="flex items-center justify-between gap-2">
        <div>
          <span className="font-medium">{c.name}</span>{" "}
          <span className="text-muted-foreground text-xs">{c.brand}</span>
        </div>
        <div className="flex items-center gap-2">
          <span>{c.price.toLocaleString()}원</span>
          {c.elimination_reason && (
            <Badge variant="destructive" className="text-[10px]">
              {ELIMINATION_LABELS[c.elimination_reason] ?? c.elimination_reason}
            </Badge>
          )}
          {c.source === "ai" && (
            <Badge variant="outline" className="text-[10px]">
              AI 추정
            </Badge>
          )}
        </div>
      </div>
      {c.review && (
        <div className="space-y-1">
          <div className="text-muted-foreground flex gap-3 text-xs">
            <span>적합도 {c.review.fit_score}/5</span>
            <span>예산 {c.review.budget_score}/5</span>
            <span>만족도 {c.review.satisfaction_score}/5</span>
          </div>
          <p className="text-muted-foreground text-xs leading-relaxed">
            {c.review.summary}
          </p>
          {c.review.critical_flaw && (
            <p className="text-destructive text-xs">⚠ {c.review.critical_flaw}</p>
          )}
          <p className="text-muted-foreground text-[10px]">
            출처: {c.review.sources.join(", ")}
          </p>
        </div>
      )}
    </li>
  )
}
