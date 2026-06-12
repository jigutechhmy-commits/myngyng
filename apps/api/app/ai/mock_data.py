"""MockProvider가 반환하는 노트북 카테고리 샘플 데이터."""

LAPTOP_SPEC_SHEET = {
    "summary": "Fusion360 설계와 코딩을 병행하는 휴대성 중시 사용자를 위한 사양",
    "fields": [
        {"key": "cpu", "label_ko": "CPU", "value": "8코어 이상 (Ryzen 7 / Core Ultra 7 / M4 급)"},
        {"key": "ram_gb", "label_ko": "RAM", "value": "32GB 권장 (최소 16GB)"},
        {"key": "storage_gb", "label_ko": "저장장치", "value": "NVMe SSD 1TB"},
        {"key": "weight_kg", "label_ko": "무게", "value": "1.5kg 이하"},
        {"key": "battery_hours", "label_ko": "배터리", "value": "실사용 8시간 이상"},
        {
            "key": "required_features",
            "label_ko": "필수 기능",
            "value": "전용 GPU 또는 강력한 iGPU, 밝기 400nit 이상 디스플레이",
        },
    ],
    "rationale": "Fusion360은 CPU 단일코어 성능과 GPU 가속이 모두 중요하며, 현장 사용을 위해 무게/배터리 기준을 강화했다.",
}

LAPTOP_CANDIDATES = {
    "candidates": [
        {
            "name": "MacBook Pro 14 (M4 Pro)",
            "brand": "Apple",
            "price": 2890000,
            "specs": {"cpu": "M4 Pro 12코어", "ram_gb": 24, "storage_gb": 512, "weight_kg": 1.55, "battery_hours": 14},
        },
        {
            "name": "ThinkPad X1 Carbon Gen 13",
            "brand": "Lenovo",
            "price": 2450000,
            "specs": {"cpu": "Core Ultra 7 258V", "ram_gb": 32, "storage_gb": 1024, "weight_kg": 1.09, "battery_hours": 11},
        },
        {
            "name": "Galaxy Book5 Pro",
            "brand": "Samsung",
            "price": 2150000,
            "specs": {"cpu": "Core Ultra 7 256V", "ram_gb": 32, "storage_gb": 1024, "weight_kg": 1.23, "battery_hours": 12},
        },
        {
            "name": "Surface Laptop 7",
            "brand": "Microsoft",
            "price": 2290000,
            "specs": {"cpu": "Snapdragon X Elite", "ram_gb": 32, "storage_gb": 1024, "weight_kg": 1.34, "battery_hours": 15},
        },
        {
            "name": "Zenbook S 14",
            "brand": "ASUS",
            "price": 1990000,
            "specs": {"cpu": "Core Ultra 7 258V", "ram_gb": 32, "storage_gb": 1024, "weight_kg": 1.20, "battery_hours": 13},
        },
        {
            "name": "Gram Pro 16",
            "brand": "LG",
            "price": 2390000,
            "specs": {"cpu": "Core Ultra 7 255H", "ram_gb": 32, "storage_gb": 1024, "weight_kg": 1.39, "battery_hours": 10},
        },
        {
            "name": "XPS 13 (9350)",
            "brand": "Dell",
            "price": 2550000,
            "specs": {"cpu": "Core Ultra 7 256V", "ram_gb": 32, "storage_gb": 1024, "weight_kg": 1.19, "battery_hours": 12},
        },
        {
            "name": "ROG Zephyrus G14",
            "brand": "ASUS",
            "price": 2750000,
            "specs": {"cpu": "Ryzen AI 9 HX 370 + RTX 4060", "ram_gb": 32, "storage_gb": 1024, "weight_kg": 1.50, "battery_hours": 8},
        },
        {
            "name": "Surface Pro 11",
            "brand": "Microsoft",
            "price": 2090000,
            "specs": {"cpu": "Snapdragon X Elite", "ram_gb": 16, "storage_gb": 512, "weight_kg": 0.89, "battery_hours": 14},
        },
        {
            "name": "Swift Go 14 AI",
            "brand": "Acer",
            "price": 1690000,
            "specs": {"cpu": "Core Ultra 7 256V", "ram_gb": 32, "storage_gb": 1024, "weight_kg": 1.25, "battery_hours": 11},
        },
    ]
}

_REVIEW = {
    "MacBook Pro 14 (M4 Pro)": {
        "summary": "성능과 디스플레이는 동급 최강이라는 평이 지배적. 다만 Fusion360 일부 기능의 macOS 호환성 이슈가 커뮤니티에서 반복적으로 언급된다.",
        "sources": ["Reddit r/Fusion360", "전문 리뷰(Notebookcheck)", "쇼핑몰 리뷰"],
        "fit_score": 4, "budget_score": 2, "satisfaction_score": 5,
        "missing_required": False, "critical_flaw": None,
    },
    "ThinkPad X1 Carbon Gen 13": {
        "summary": "키보드와 내구성, 가벼운 무게로 출장/현장 사용자 만족도가 높다. iGPU라 무거운 3D 어셈블리에서는 한계가 있다는 후기가 있다.",
        "sources": ["Reddit r/thinkpad", "Lenovo 포럼", "전문 리뷰"],
        "fit_score": 4, "budget_score": 4, "satisfaction_score": 5,
        "missing_required": False, "critical_flaw": None,
    },
    "Galaxy Book5 Pro": {
        "summary": "가볍고 화면이 좋다는 평. 삼성 생태계 연동 만족도가 높으나 AS 외 글로벌 커뮤니티 정보가 적다.",
        "sources": ["커뮤니티(클리앙)", "쇼핑몰 리뷰", "Youtube"],
        "fit_score": 4, "budget_score": 4, "satisfaction_score": 4,
        "missing_required": False, "critical_flaw": None,
    },
    "Surface Laptop 7": {
        "summary": "배터리와 빌드 품질 호평. 그러나 ARM(Snapdragon) 기반이라 Fusion360 네이티브 미지원으로 에뮬레이션 성능 저하가 보고된다.",
        "sources": ["Reddit r/Surface", "Microsoft 포럼"],
        "fit_score": 2, "budget_score": 4, "satisfaction_score": 4,
        "missing_required": True, "critical_flaw": "Fusion360 ARM 네이티브 미지원 — 에뮬레이션 성능 저하",
    },
    "Zenbook S 14": {
        "summary": "휴대성과 디스플레이 대비 가격이 좋다는 평. 발열 시 스로틀링 후기가 일부 있으나 일반 작업에는 무난하다.",
        "sources": ["Reddit r/Zenbook", "전문 리뷰", "쇼핑몰 리뷰"],
        "fit_score": 4, "budget_score": 5, "satisfaction_score": 4,
        "missing_required": False, "critical_flaw": None,
    },
    "Gram Pro 16": {
        "summary": "큰 화면 대비 가벼운 무게가 강점. 다만 섀시 강성과 스피커에 대한 불만 후기가 반복된다.",
        "sources": ["커뮤니티(퀘이사존)", "쇼핑몰 리뷰"],
        "fit_score": 4, "budget_score": 4, "satisfaction_score": 4,
        "missing_required": False, "critical_flaw": None,
    },
    "XPS 13 (9350)": {
        "summary": "디자인/디스플레이 호평. 그러나 보이지 않는 터치 펑션열과 키보드 적응 문제, 발열 관련 불만이 많다.",
        "sources": ["Reddit r/Dell", "전문 리뷰"],
        "fit_score": 3, "budget_score": 3, "satisfaction_score": 3,
        "missing_required": False, "critical_flaw": None,
    },
    "ROG Zephyrus G14": {
        "summary": "전용 GPU(RTX 4060)로 Fusion360 렌더링/시뮬레이션 성능이 가장 좋다. 무게와 배터리는 울트라북 대비 손해.",
        "sources": ["Reddit r/ZephyrusG14", "Youtube", "전문 리뷰"],
        "fit_score": 5, "budget_score": 3, "satisfaction_score": 5,
        "missing_required": False, "critical_flaw": None,
    },
    "Surface Pro 11": {
        "summary": "태블릿 겸용 휴대성은 최고. 그러나 ARM 기반 Fusion360 제약과 RAM 16GB 한계로 설계 용도로는 부적합하다는 후기가 많다.",
        "sources": ["Reddit r/Surface", "Microsoft 포럼"],
        "fit_score": 2, "budget_score": 5, "satisfaction_score": 3,
        "missing_required": True, "critical_flaw": "Fusion360 ARM 미지원 + RAM 16GB로 사양서 미달",
    },
    "Swift Go 14 AI": {
        "summary": "가성비는 좋으나 디스플레이 품질 편차와 빌드 마감에 대한 불만이 많고, 장기 사용 만족도가 낮게 보고된다.",
        "sources": ["쇼핑몰 리뷰", "커뮤니티"],
        "fit_score": 3, "budget_score": 5, "satisfaction_score": 2,
        "missing_required": False, "critical_flaw": None,
    },
}

LAPTOP_REVIEWS = {
    "reviews": [{"name": name, **review} for name, review in _REVIEW.items()]
}

# 1차 통과(shortlist) 후보 6종에 대한 DIGGING 결과
_NARRATIVE = {
    "ThinkPad X1 Carbon Gen 13": {
        "narrative": "전자제품이 아니라 공구를 만들겠다는 IBM 철학의 후계자",
        "story": "1992년 IBM 도시락에서 영감을 받은 검은 박스로 시작해 레노버 인수 후에도 키보드와 내구성이라는 본질을 지켜왔다. MIL-SPEC 테스트, 빨간 트랙포인트, 개발자와 출장족으로 구성된 강고한 팬덤이 30년 넘게 유지된다. '일하는 도구'라는 정체성에서 벗어난 적이 없는 드문 제품군이다.",
        "digging_scores": {"philosophy": 9, "history": 10, "fandom": 9, "originality": 7, "community": 9, "story": 9},
        "sources": ["Lenovo 공식 헤리티지 페이지", "Reddit r/thinkpad", "IBM 아카이브"],
    },
    "Galaxy Book5 Pro": {
        "narrative": "갤럭시 생태계의 마지막 퍼즐을 자처하는 삼성의 PC 재도전",
        "story": "센스 시절의 실패를 딛고 갤럭시 브랜드로 통합하며 폰-태블릿-노트북 연동을 무기로 삼았다. 자사 OLED 패널을 아낌없이 넣는 디스플레이 우위 전략이 뚜렷하다. 글로벌 팬덤은 얇지만 국내 접근성과 AS는 가장 강력하다.",
        "digging_scores": {"philosophy": 6, "history": 5, "fandom": 5, "originality": 6, "community": 7, "story": 6},
        "sources": ["삼성 뉴스룸", "커뮤니티(클리앙)", "전문 리뷰"],
    },
    "Zenbook S 14": {
        "narrative": "마더보드 회사가 증명한 '얇아도 단단할 수 있다'는 집념",
        "story": "부품 제조사로 출발한 ASUS가 완제품에서도 엔지니어링 우위를 보여주려 만든 라인이 Zenbook이다. 세라루미늄 같은 신소재 실험을 가장 먼저 하는 브랜드이며, 가격 대비 마감에서 평가가 높다. 팬덤보다는 실속파 사용자의 지지를 받는다.",
        "digging_scores": {"philosophy": 7, "history": 6, "fandom": 5, "originality": 8, "community": 7, "story": 6},
        "sources": ["ASUS 공식 디자인 스토리", "Reddit r/Zenbook"],
    },
    "Gram Pro 16": {
        "narrative": "'그램'이라는 이름에 모든 것을 건 경량의 외길",
        "story": "980g 한 가지 숫자로 시장을 연 제품. 무게라는 단일 가치에 집중해 카테고리를 만들었고, 대화면-초경량 조합으로 국내 대학생/직장인 시장을 장악했다. 강성 논란조차 '가벼움의 대가'로 받아들여지는 독특한 포지션이다.",
        "digging_scores": {"philosophy": 7, "history": 7, "fandom": 6, "originality": 8, "community": 7, "story": 7},
        "sources": ["LG전자 공식", "커뮤니티(퀘이사존)"],
    },
    "XPS 13 (9350)": {
        "narrative": "베젤을 지우는 것으로 울트라북의 기준을 다시 쓴 개척자",
        "story": "2015년 인피니티 엣지 디스플레이로 울트라북 디자인의 기준을 바꿨다. 이후 미니멀리즘을 극단까지 밀어붙이며 포트와 키보드까지 지워가는 실험을 계속한다. 혁신과 불편 사이의 긴장이 이 제품의 정체성이다.",
        "digging_scores": {"philosophy": 8, "history": 8, "fandom": 6, "originality": 9, "community": 5, "story": 8},
        "sources": ["Dell 공식", "Reddit r/Dell", "전문 리뷰(The Verge)"],
    },
    "ROG Zephyrus G14": {
        "narrative": "게이밍의 힘을 백팩에 넣겠다는 ROG의 반란",
        "story": "거대한 게이밍 노트북의 공식을 깨고 14인치에 전용 GPU를 욱여넣어 '휴대 가능한 워크스테이션'이라는 새 시장을 열었다. AniMe Matrix 같은 장난기와 진지한 성능이 공존한다. 크리에이터와 게이머 양쪽에서 컬트적 지지를 받는다.",
        "digging_scores": {"philosophy": 7, "history": 6, "fandom": 8, "originality": 9, "community": 8, "story": 8},
        "sources": ["ASUS ROG 공식", "Reddit r/ZephyrusG14", "Youtube"],
    },
}

LAPTOP_NARRATIVES = {
    "narratives": [{"name": name, **n} for name, n in _NARRATIVE.items()]
}

_CARD = {
    "ThinkPad X1 Carbon Gen 13": {
        "headline": "30년을 버틴 도구의 품격, 일하는 사람의 1순위",
        "key_specs": ["Core Ultra 7 258V", "32GB RAM", "1TB SSD", "1.09kg", "배터리 11시간"],
        "pros": ["최고 수준의 키보드", "1.1kg 초경량 + MIL-SPEC 내구성", "출장/현장 최적"],
        "cons": ["iGPU라 무거운 3D 작업엔 한계", "디자인이 보수적"],
        "review_digest": "키보드·내구성·무게로 출장족과 개발자의 만족도가 가장 높다.",
        "worldview": "전자제품이 아니라 공구를 만들겠다는 IBM 철학의 후계자.",
        "recommended_for": ["이동이 잦은 실무자", "키보드를 많이 치는 개발자/작가"],
        "not_recommended_for": ["무거운 3D 렌더링 위주 사용자"],
    },
    "Galaxy Book5 Pro": {
        "headline": "갤럭시를 쓰고 있다면 답은 이미 정해져 있다",
        "key_specs": ["Core Ultra 7 256V", "32GB RAM", "3K AMOLED", "1.23kg"],
        "pros": ["최상급 OLED 디스플레이", "갤럭시 생태계 연동", "국내 AS 최강"],
        "cons": ["글로벌 커뮤니티 정보 부족", "브랜드 정체성이 옅음"],
        "review_digest": "화면과 휴대성, 생태계 연동에서 높은 만족도를 보인다.",
        "worldview": "갤럭시 생태계의 마지막 퍼즐을 자처하는 삼성의 PC 재도전.",
        "recommended_for": ["갤럭시 폰/탭 사용자", "디스플레이 품질 중시자"],
        "not_recommended_for": ["리눅스/개조 친화적 기기를 원하는 사용자"],
    },
    "Zenbook S 14": {
        "headline": "이 가격에 이 마감, 실속파의 합리적 사치",
        "key_specs": ["Core Ultra 7 258V", "32GB RAM", "세라루미늄 바디", "1.20kg"],
        "pros": ["가격 대비 뛰어난 마감", "신소재 경량 바디", "균형 잡힌 성능"],
        "cons": ["고부하 시 스로틀링 보고", "팬덤/커뮤니티가 얇음"],
        "review_digest": "휴대성과 디스플레이 대비 가격 경쟁력이 좋다는 평이 많다.",
        "worldview": "마더보드 회사가 증명한 '얇아도 단단할 수 있다'는 집념.",
        "recommended_for": ["가성비와 마감을 모두 원하는 사용자"],
        "not_recommended_for": ["지속 고부하 작업 위주 사용자"],
    },
    "Gram Pro 16": {
        "headline": "16인치가 1.3kg, 화면도 무게도 포기 못 한다면",
        "key_specs": ["Core Ultra 7 255H", "32GB RAM", "16인치 대화면", "1.39kg"],
        "pros": ["대화면 대비 초경량", "긴 배터리", "국내 AS 용이"],
        "cons": ["섀시 강성 불만", "스피커 품질 아쉬움"],
        "review_digest": "큰 화면을 가볍게 들고 다니고 싶은 사용자의 만족도가 높다.",
        "worldview": "'그램'이라는 이름에 모든 것을 건 경량의 외길.",
        "recommended_for": ["대화면+휴대성 동시 추구자", "학생/사무직"],
        "not_recommended_for": ["견고한 빌드를 중시하는 사용자"],
    },
    "XPS 13 (9350)": {
        "headline": "미니멀리즘의 끝, 디자인이 곧 스펙인 머신",
        "key_specs": ["Core Ultra 7 256V", "32GB RAM", "베젤리스 디스플레이", "1.19kg"],
        "pros": ["압도적인 디자인/디스플레이", "콤팩트한 풋프린트"],
        "cons": ["터치 펑션열 등 급진적 UX", "발열 관리 아쉬움", "포트 부족"],
        "review_digest": "디자인과 화면은 호평이나 급진적 인터페이스에 호불호가 갈린다.",
        "worldview": "베젤을 지우는 것으로 울트라북의 기준을 다시 쓴 개척자.",
        "recommended_for": ["디자인 우선 사용자", "얼리어답터"],
        "not_recommended_for": ["전통적 키보드/포트 구성을 원하는 사용자"],
    },
    "ROG Zephyrus G14": {
        "headline": "백팩에 들어가는 워크스테이션, 성능 타협은 없다",
        "key_specs": ["Ryzen AI 9 HX 370", "RTX 4060", "32GB RAM", "1.50kg"],
        "pros": ["전용 GPU로 3D/렌더링 최강", "14인치 휴대 가능", "크리에이터 팬덤"],
        "cons": ["배터리 짧음(8시간)", "발열/팬소음", "예산 상한 근접"],
        "review_digest": "Fusion360 등 3D 작업 성능에서 후보 중 가장 높은 평가를 받는다.",
        "worldview": "게이밍의 힘을 백팩에 넣겠다는 ROG의 반란.",
        "recommended_for": ["3D 설계/렌더링 비중이 큰 사용자", "겸용 게이머"],
        "not_recommended_for": ["배터리/정숙성이 1순위인 사용자"],
    },
}

LAPTOP_CARDS = {
    "cards": [{"name": name, **c} for name, c in _CARD.items()]
}
