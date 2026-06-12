"use client"

import { useEffect, useMemo, useState } from "react"
import { useRouter } from "next/navigation"

import {
  CategoryDetail,
  CategorySummary,
  createSession,
  getCategory,
  listCategories,
} from "@/lib/api"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Textarea } from "@/components/ui/textarea"

const STEPS = [
  { no: 1, title: "카테고리 선택", description: "어떤 것을 고르고 있나요?" },
  { no: 2, title: "예산 입력", description: "목표 예산과 허용 오차를 알려주세요." },
  { no: 3, title: "용도 입력", description: "어떤 용도로 사용할 예정인가요? 자유롭게 적어주세요." },
  { no: 4, title: "우선순위", description: "가장 중요한 기준을 순서대로 최대 3개 선택하세요." },
  { no: 5, title: "토너먼트 규모", description: "몇 강으로 비교할까요?" },
] as const

const TOURNAMENT_OPTIONS = [
  { value: 2, label: "2강" },
  { value: 4, label: "4강" },
  { value: 8, label: "8강" },
  { value: 16, label: "16강" },
  { value: 0, label: "Auto" },
] as const

export default function StartPage() {
  const router = useRouter()

  const [step, setStep] = useState(1)
  const [categories, setCategories] = useState<CategorySummary[]>([])
  const [categoryDetail, setCategoryDetail] = useState<CategoryDetail | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  // 입력 상태 (STEP 1~5)
  const [categoryId, setCategoryId] = useState<string | null>(null)
  const [budget, setBudget] = useState("")
  const [tolerance, setTolerance] = useState("10")
  const [usageText, setUsageText] = useState("")
  const [priorities, setPriorities] = useState<string[]>([])
  const [tournamentSize, setTournamentSize] = useState<number | null>(null)

  useEffect(() => {
    listCategories()
      .then((data) => setCategories(data.categories))
      .catch(() => setLoadError("카테고리를 불러오지 못했습니다. API 서버 상태를 확인해주세요."))
  }, [])

  useEffect(() => {
    if (!categoryId) return
    getCategory(categoryId)
      .then(setCategoryDetail)
      .catch(() => setLoadError("카테고리 정보를 불러오지 못했습니다."))
  }, [categoryId])

  const budgetValue = Number(budget)
  const toleranceValue = Number(tolerance)

  const canNext = useMemo(() => {
    switch (step) {
      case 1:
        return categoryId !== null
      case 2:
        return budgetValue > 0 && toleranceValue >= 0 && toleranceValue <= 50
      case 3:
        return usageText.trim().length > 0
      case 4:
        return priorities.length >= 1
      case 5:
        return tournamentSize !== null
      default:
        return false
    }
  }, [step, categoryId, budgetValue, toleranceValue, usageText, priorities, tournamentSize])

  function togglePriority(key: string) {
    setPriorities((prev) => {
      if (prev.includes(key)) return prev.filter((p) => p !== key)
      if (prev.length >= 3) return prev
      return [...prev, key]
    })
  }

  async function handleSubmit() {
    if (!categoryId || tournamentSize === null) return
    setSubmitting(true)
    setLoadError(null)
    try {
      const session = await createSession({
        category_id: categoryId,
        budget: budgetValue,
        budget_tolerance_pct: toleranceValue,
        usage_text: usageText.trim(),
        priorities,
        tournament_size: tournamentSize,
      })
      router.push(`/session/${session.id}`)
    } catch {
      setLoadError("세션 생성에 실패했습니다. 잠시 후 다시 시도해주세요.")
      setSubmitting(false)
    }
  }

  const current = STEPS[step - 1]

  return (
    <main className="mx-auto flex w-full max-w-xl flex-1 flex-col justify-center gap-6 px-6 py-10">
      <div className="space-y-2">
        <div className="text-muted-foreground flex justify-between text-xs">
          <span>
            STEP {current.no} / {STEPS.length}
          </span>
          <span>{current.title}</span>
        </div>
        <Progress value={(step / STEPS.length) * 100} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{current.title}</CardTitle>
          <CardDescription>{current.description}</CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          {step === 1 && (
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              {categories.map((c) => (
                <Button
                  key={c.id}
                  variant={categoryId === c.id ? "default" : "outline"}
                  disabled={!c.enabled}
                  onClick={() => setCategoryId(c.id)}
                  className="h-16 flex-col gap-1"
                >
                  <span>{c.name_ko}</span>
                  {!c.enabled && (
                    <span className="text-muted-foreground text-[10px]">준비 중</span>
                  )}
                </Button>
              ))}
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="budget">목표 예산 (원)</Label>
                <Input
                  id="budget"
                  type="number"
                  inputMode="numeric"
                  placeholder="예: 2500000"
                  value={budget}
                  onChange={(e) => setBudget(e.target.value)}
                />
                {budgetValue > 0 && (
                  <p className="text-muted-foreground text-xs">
                    {budgetValue.toLocaleString()}원
                    {toleranceValue > 0 && ` ±${toleranceValue}%`}
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="tolerance">허용 오차 (%)</Label>
                <Input
                  id="tolerance"
                  type="number"
                  inputMode="numeric"
                  min={0}
                  max={50}
                  value={tolerance}
                  onChange={(e) => setTolerance(e.target.value)}
                />
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-2">
              <Label htmlFor="usage">용도</Label>
              <Textarea
                id="usage"
                rows={5}
                placeholder={"예: Fusion360 설계, 소규모 바이브코딩,\n프레젠테이션, 휴대성, 현장 사용"}
                value={usageText}
                onChange={(e) => setUsageText(e.target.value)}
              />
            </div>
          )}

          {step === 4 && (
            <div className="space-y-3">
              <div className="flex flex-wrap gap-2">
                {(categoryDetail?.priority_options ?? []).map((opt) => {
                  const rank = priorities.indexOf(opt.key)
                  const selected = rank >= 0
                  return (
                    <Button
                      key={opt.key}
                      size="sm"
                      variant={selected ? "default" : "outline"}
                      onClick={() => togglePriority(opt.key)}
                    >
                      {selected && (
                        <Badge variant="secondary" className="px-1.5">
                          {rank + 1}순위
                        </Badge>
                      )}
                      {opt.label_ko}
                    </Button>
                  )
                })}
              </div>
              <p className="text-muted-foreground text-xs">
                클릭한 순서대로 1~3순위가 지정됩니다. 다시 클릭하면 해제됩니다.
              </p>
            </div>
          )}

          {step === 5 && (
            <RadioGroup
              value={tournamentSize === null ? undefined : String(tournamentSize)}
              onValueChange={(v: string) => setTournamentSize(Number(v))}
              className="grid grid-cols-2 gap-3 sm:grid-cols-5"
            >
              {TOURNAMENT_OPTIONS.map((opt) => (
                <Label
                  key={opt.value}
                  className={
                    "border-input flex cursor-pointer items-center justify-center gap-2 rounded-md border p-3 " +
                    (tournamentSize === opt.value ? "border-primary bg-accent" : "")
                  }
                >
                  <RadioGroupItem value={String(opt.value)} />
                  {opt.label}
                </Label>
              ))}
            </RadioGroup>
          )}

          {loadError && <p className="text-destructive text-sm">{loadError}</p>}
        </CardContent>

        <CardFooter className="justify-between">
          <Button
            variant="ghost"
            disabled={step === 1 || submitting}
            onClick={() => setStep((s) => Math.max(1, s - 1))}
          >
            이전
          </Button>
          {step < STEPS.length ? (
            <Button disabled={!canNext} onClick={() => setStep((s) => s + 1)}>
              다음
            </Button>
          ) : (
            <Button disabled={!canNext || submitting} onClick={handleSubmit}>
              {submitting ? "생성 중..." : "비교 시작"}
            </Button>
          )}
        </CardFooter>
      </Card>
    </main>
  )
}
