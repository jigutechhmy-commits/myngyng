"use client"

import { use, useCallback, useEffect, useState } from "react"

import {
  CandidateOut,
  getSession,
  listCandidates,
  runPlan,
  runResearch,
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
  plan: "PLAN — 요구사항 분석 완료",
  research: "RESEARCH — 시장 조사 완료",
  review_scan: "REVIEW SCAN — 후기 수집",
  list_up: "LIST UP — 후보 압축",
  digging: "DIGGING — 세계관 조사",
  final_entry: "FINAL ENTRY — 최종 카드",
  choice: "CHOICE — 월드컵",
  done: "완료",
}

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
    if (["research", "review_scan", "list_up", "digging", "final_entry", "choice", "done"].includes(s.engine_phase)) {
      setCandidates(await listCandidates(id))
    }
  }, [id])

  useEffect(() => {
    refresh().catch(() => setError("세션을 불러오지 못했습니다."))
  }, [refresh])

  async function runEngine() {
    setError(null)
    try {
      if (session?.engine_phase === "created") {
        setRunning("PLAN — 요구사항을 분석하는 중...")
        await runPlan(id)
        await refresh()
      }
      setRunning("RESEARCH — 시장 후보를 수집하는 중...")
      await runResearch(id)
      await refresh()
    } catch {
      setError("엔진 실행에 실패했습니다. 잠시 후 다시 시도해주세요.")
    } finally {
      setRunning(null)
    }
  }

  const phase = session?.engine_phase ?? "created"
  const canRun = phase === "created" || phase === "plan"

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
          {running && <p className="text-muted-foreground text-sm">{running}</p>}
          {canRun && !running && (
            <Button onClick={runEngine}>
              {phase === "created" ? "분석 시작" : "시장 조사 실행"}
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

      {candidates.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>후보군 ({candidates.length})</CardTitle>
            <CardDescription>
              시장 조사로 수집된 1차 후보입니다. 다음 단계(REVIEW SCAN)는 M3에서
              구현됩니다.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="divide-y text-sm">
              {candidates.map((c) => (
                <li key={c.id} className="flex items-center justify-between gap-2 py-2">
                  <div>
                    <span className="font-medium">{c.name}</span>{" "}
                    <span className="text-muted-foreground text-xs">{c.brand}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span>{c.price.toLocaleString()}원</span>
                    {c.source === "ai" && (
                      <Badge variant="outline" className="text-[10px]">
                        AI 추정
                      </Badge>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </main>
  )
}
