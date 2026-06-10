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
