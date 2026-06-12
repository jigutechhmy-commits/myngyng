import Link from "next/link"

import { Button } from "@/components/ui/button"

export default function Home() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-8 px-6 text-center">
      <div className="space-y-4">
        <h1 className="text-5xl font-bold tracking-tight">GOOD CHOICE</h1>
        <p className="text-muted-foreground text-lg">
          비교는 AI가, 결정은 당신이.
        </p>
      </div>
      <p className="text-muted-foreground max-w-md text-sm leading-relaxed">
        최고의 제품은 존재하지 않습니다. 가장 나에게 맞는 제품만 존재합니다.
        GOOD CHOICE는 당신이 자신의 선택에 확신을 가질 수 있도록 돕는 AI
        의사결정 플랫폼입니다.
      </p>
      <Button asChild size="lg">
        <Link href="/start">시작하기</Link>
      </Button>
    </main>
  )
}
