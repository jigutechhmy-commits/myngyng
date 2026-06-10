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
