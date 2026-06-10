"use client"

import { use, useEffect, useState } from "react"

import { getSession, SessionOut } from "@/lib/api"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

const PHASE_LABELS: Record<string, string> = {
  created: "생성됨",
  plan: "PLAN — 요구사항 분석",
  research: "RESEARCH — 시장 조사",
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
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getSession(id)
      .then(setSession)
      .catch(() => setError("세션을 불러오지 못했습니다."))
  }, [id])

  return (
    <main className="mx-auto flex w-full max-w-xl flex-1 flex-col justify-center gap-6 px-6 py-10">
      <Card>
        <CardHeader>
          <CardTitle>요청 접수 완료</CardTitle>
          <CardDescription>
            Good Choice Engine이 곧 분석을 시작합니다. (PLAN 단계는 M2에서
            구현됩니다)
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          {error && <p className="text-destructive">{error}</p>}
          {session && (
            <>
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground w-24">진행 상태</span>
                <Badge>{PHASE_LABELS[session.engine_phase] ?? session.engine_phase}</Badge>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground w-24">카테고리</span>
                <span>{session.category_id}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground w-24">예산</span>
                <span>
                  {session.budget.toLocaleString()}원 ±{session.budget_tolerance_pct}%
                </span>
              </div>
              <div className="flex items-start gap-2">
                <span className="text-muted-foreground w-24 shrink-0">용도</span>
                <span className="whitespace-pre-wrap">{session.usage_text}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground w-24">우선순위</span>
                <span className="flex gap-1">
                  {session.priorities.map((p, i) => (
                    <Badge key={p} variant="outline">
                      {i + 1}. {p}
                    </Badge>
                  ))}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground w-24">토너먼트</span>
                <span>
                  {session.tournament_size === 0 ? "Auto" : `${session.tournament_size}강`}
                </span>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </main>
  )
}
