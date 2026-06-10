"use client"

import { use, useCallback, useEffect, useState } from "react"

import {
  CandidateOut,
  CardOut,
  chooseWinner,
  createTournament,
  getSession,
  getTournament,
  listCandidates,
  listCards,
  MatchOut,
  runDigging,
  runFinalEntry,
  runListUp,
  runPlan,
  runResearch,
  runReviewScan,
  SessionOut,
  TournamentOut,
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
import { Textarea } from "@/components/ui/textarea"

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
  { from: "list_up", label: "DIGGING — 제품의 세계관을 조사하는 중...", run: runDigging },
  { from: "digging", label: "FINAL ENTRY — 최종 카드를 만드는 중...", run: runFinalEntry },
]

export default function SessionPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = use(params)
  const [session, setSession] = useState<SessionOut | null>(null)
  const [candidates, setCandidates] = useState<CandidateOut[]>([])
  const [cards, setCards] = useState<CardOut[]>([])
  const [tournament, setTournament] = useState<TournamentOut | null>(null)
  const [running, setRunning] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    const s = await getSession(id)
    setSession(s)
    if (s.engine_phase !== "created" && s.engine_phase !== "plan") {
      setCandidates(await listCandidates(id))
    }
    if (["final_entry", "choice", "done"].includes(s.engine_phase)) {
      setCards(await listCards(id))
    }
    if (["choice", "done"].includes(s.engine_phase)) {
      setTournament(await getTournament(id))
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

      {tournament && (
        <TournamentSection
          sessionId={id}
          tournament={tournament}
          cards={cards}
          onUpdate={setTournament}
        />
      )}

      {!tournament && cards.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">최종 엔트리 ({cards.length})</h2>
            <Button
              onClick={async () => {
                try {
                  setTournament(await createTournament(id))
                  await refresh()
                } catch {
                  setError("토너먼트 생성에 실패했습니다.")
                }
              }}
            >
              월드컵 시작
            </Button>
          </div>
          {cards.map((card) => (
            <FinalCard key={card.candidate_id} card={card} />
          ))}
        </div>
      )}

      {cards.length === 0 && shortlisted.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>1차 통과 후보 ({shortlisted.length})</CardTitle>
            <CardDescription>
              자동 탈락을 통과한 후보입니다. 다음 단계(DIGGING → FINAL ENTRY)를
              실행하세요.
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

function roundLabel(roundNo: number, size: number): string {
  const remaining = size >> (roundNo - 1)
  if (remaining === 2) return "결승"
  return `${remaining}강`
}

function TournamentSection({
  sessionId,
  tournament,
  cards,
  onUpdate,
}: {
  sessionId: string
  tournament: TournamentOut
  cards: CardOut[]
  onUpdate: (t: TournamentOut) => void
}) {
  const [reason, setReason] = useState("")
  const [choosing, setChoosing] = useState(false)
  const cardById = new Map(cards.map((c) => [c.candidate_id, c]))

  const currentMatch: MatchOut | undefined = tournament.matches.find(
    (m) => m.winner_candidate_id === null
  )
  const decidedCount = tournament.matches.filter((m) => m.winner_candidate_id).length
  const totalMatches = tournament.size - 1

  async function pick(match: MatchOut, winnerId: string) {
    setChoosing(true)
    try {
      onUpdate(await chooseWinner(sessionId, match.id, winnerId, reason.trim() || undefined))
      setReason("")
    } finally {
      setChoosing(false)
    }
  }

  if (tournament.status === "done") {
    const winner = tournament.winner_candidate_id
      ? cardById.get(tournament.winner_candidate_id)
      : null
    return (
      <div className="space-y-4">
        <Card className="border-primary">
          <CardHeader>
            <CardTitle>🏆 당신의 선택</CardTitle>
            <CardDescription>
              월드컵이 끝났습니다. Decision Journal 기록은 M6에서 이어집니다.
            </CardDescription>
          </CardHeader>
        </Card>
        {winner && <FinalCard card={winner} />}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">선택 기록</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              {tournament.matches.map((m) => {
                const w = m.winner_candidate_id ? cardById.get(m.winner_candidate_id) : null
                const loserId =
                  m.winner_candidate_id === m.candidate_a_id
                    ? m.candidate_b_id
                    : m.candidate_a_id
                const l = cardById.get(loserId)
                return (
                  <li key={m.id} className="text-muted-foreground">
                    <span className="text-foreground font-medium">
                      [{roundLabel(m.round_no, tournament.size)}]
                    </span>{" "}
                    {w?.name} <span className="text-xs">vs {l?.name}</span>
                    {m.choice_reason && (
                      <span className="block pl-4 text-xs">— {m.choice_reason}</span>
                    )}
                  </li>
                )
              })}
            </ul>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!currentMatch) return null
  const a = cardById.get(currentMatch.candidate_a_id)
  const b = cardById.get(currentMatch.candidate_b_id)
  if (!a || !b) return null

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">
          {roundLabel(currentMatch.round_no, tournament.size)} — 어느 쪽인가요?
        </h2>
        <span className="text-muted-foreground text-xs">
          {decidedCount + 1} / {totalMatches} 경기
        </span>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        {[a, b].map((card) => (
          <div key={card.candidate_id} className="flex flex-col gap-2">
            <FinalCard card={card} />
            <Button
              disabled={choosing}
              onClick={() => pick(currentMatch, card.candidate_id)}
            >
              {card.name} 선택
            </Button>
          </div>
        ))}
      </div>
      <div className="space-y-1">
        <Textarea
          rows={2}
          placeholder="선택 이유를 남기면 Decision Journal에 기록됩니다 (선택)"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
        />
        <p className="text-muted-foreground text-[10px]">
          AI는 정답을 강요하지 않습니다. 결정은 당신의 몫입니다.
        </p>
      </div>
    </div>
  )
}

function FinalCard({ card }: { card: CardOut }) {
  const scores = card.narrative?.digging_scores ?? {}
  const SCORE_LABELS: Record<string, string> = {
    philosophy: "철학",
    history: "역사성",
    fandom: "팬덤",
    originality: "독창성",
    community: "커뮤니티",
    story: "스토리성",
  }
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-start justify-between gap-2">
          <span>
            {card.name}{" "}
            <span className="text-muted-foreground text-xs font-normal">
              {card.brand} · {card.price.toLocaleString()}원
            </span>
          </span>
          {card.narrative?.ai_inferred && (
            <Badge variant="outline" className="shrink-0 text-[10px]">
              AI 추론 포함
            </Badge>
          )}
        </CardTitle>
        <CardDescription className="text-foreground text-base font-medium">
          “{card.headline}”
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4 text-sm">
        {card.narrative && (
          <blockquote className="border-l-2 pl-3 italic">
            {card.narrative.narrative}
          </blockquote>
        )}
        <div className="flex flex-wrap gap-1.5">
          {card.key_specs.map((s) => (
            <Badge key={s} variant="secondary" className="text-[11px]">
              {s}
            </Badge>
          ))}
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          <div>
            <p className="mb-1 font-medium">장점</p>
            <ul className="text-muted-foreground list-disc space-y-0.5 pl-4 text-xs">
              {card.pros.map((p) => (
                <li key={p}>{p}</li>
              ))}
            </ul>
          </div>
          <div>
            <p className="mb-1 font-medium">단점</p>
            <ul className="text-muted-foreground list-disc space-y-0.5 pl-4 text-xs">
              {card.cons.map((c) => (
                <li key={c}>{c}</li>
              ))}
            </ul>
          </div>
        </div>
        <p className="text-muted-foreground text-xs leading-relaxed">
          {card.review_digest}
        </p>
        {card.narrative && (
          <details className="text-xs">
            <summary className="text-muted-foreground cursor-pointer">
              세계관 이야기 · Digging Score
            </summary>
            <div className="mt-2 space-y-2">
              <p className="text-muted-foreground leading-relaxed">
                {card.narrative.story}
              </p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(scores).map(([k, v]) => (
                  <span key={k} className="text-muted-foreground">
                    {SCORE_LABELS[k] ?? k} {v}/10
                  </span>
                ))}
              </div>
              <p className="text-muted-foreground text-[10px]">
                출처: {card.narrative.sources.join(", ")}
              </p>
            </div>
          </details>
        )}
        <div className="grid gap-2 border-t pt-3 sm:grid-cols-2">
          <div className="text-xs">
            <span className="font-medium">추천: </span>
            <span className="text-muted-foreground">
              {card.recommended_for.join(", ")}
            </span>
          </div>
          <div className="text-xs">
            <span className="font-medium">비추천: </span>
            <span className="text-muted-foreground">
              {card.not_recommended_for.join(", ")}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
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
