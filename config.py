"""
全域設定檔 — AI Python Code Tutor
支援 Claude API 與 Gemini API 雙模式
"""
import os

# ── Claude API 設定 ───────────────────────────────────
CLAUDE_MODELS: list[str] = [
    "claude-sonnet-4-20250514",
    "claude-haiku-4-5-20251001",
    "claude-opus-4-20250514",
]

# ── Gemini API 設定 ───────────────────────────────────
GEMINI_MODELS: list[str] = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]

# 預設
DEFAULT_PROVIDER: str = "claude"
DEFAULT_MODEL: str    = "claude-sonnet-4-20250514"

# ── 快取設定 ─────────────────────────────────────────
CACHE_DIR: str      = os.path.join(os.path.dirname(__file__), "cache")
CACHE_TTL_DAYS: int = 7

# ── UI 常數 ──────────────────────────────────────────
APP_TITLE: str   = "AI Python Code Tutor"
APP_ICON: str    = "🐍"
APP_VERSION: str = "0.5.0-round5"

# ── 費用估算（每 1000 tokens，USD）────────────────────
COST_PER_1K: dict = {
    "claude-sonnet-4-20250514":  {"input": 0.003,   "output": 0.015},
    "claude-haiku-4-5-20251001": {"input": 0.00025, "output": 0.00125},
    "claude-opus-4-20250514":    {"input": 0.015,   "output": 0.075},
    "gemini-2.0-flash":          {"input": 0.000075,"output": 0.0003},
    "gemini-1.5-flash":          {"input": 0.000075,"output": 0.0003},
    "gemini-1.5-pro":            {"input": 0.00125, "output": 0.005},
}

# ── 範例程式碼 ────────────────────────────────────────
SAMPLE_CODE = '''import pandas as pd
import matplotlib.pyplot as plt

def load_data(filepath):
    """從 CSV 檔案讀取資料"""
    df = pd.read_csv(filepath)
    return df

def clean_data(df):
    """移除空值與重複資料"""
    df = df.dropna()
    df = df.drop_duplicates()
    return df

def calculate_summary(df, column):
    """計算指定欄位的統計摘要"""
    mean_val = df[column].mean()
    max_val  = df[column].max()
    min_val  = df[column].min()
    return {"mean": mean_val, "max": max_val, "min": min_val}

def plot_chart(df, x_col, y_col):
    """繪製折線圖"""
    plt.figure(figsize=(10, 6))
    plt.plot(df[x_col], df[y_col])
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.title(f"{y_col} vs {x_col}")
    plt.savefig("output.png")

def main():
    """主程式流程"""
    data  = load_data("sales.csv")
    data  = clean_data(data)
    stats = calculate_summary(data, "revenue")
    print(stats)
    plot_chart(data, "month", "revenue")

if __name__ == "__main__":
    main()
'''


SAMPLE_CODE_CLASS = '''from dataclasses import dataclass
from typing import List, Optional
import json

@dataclass
class Config:
    """應用程式設定類別"""
    host: str = "localhost"
    port: int = 8080
    debug: bool = False


class DataProcessor:
    """負責資料清洗和轉換的處理器"""

    MAX_ROWS = 10000

    def __init__(self, config: Config):
        """初始化處理器"""
        self.config = config
        self._cache = {}

    def load(self, filepath: str) -> list:
        """從 JSON 讀取資料"""
        with open(filepath) as f:
            return json.load(f)

    def clean(self, data: list) -> list:
        """移除空值與重複項目"""
        seen = set()
        result = []
        for item in data:
            if item and str(item) not in seen:
                seen.add(str(item))
                result.append(item)
        return result

    def process(self, data: list) -> dict:
        """主要資料處理流程"""
        cleaned = self.clean(data)
        summary = self._summarize(cleaned)
        return summary

    def _summarize(self, data: list) -> dict:
        """計算摘要統計"""
        return {"count": len(data), "items": data[:5]}


class ProcessingError(Exception):
    """資料處理失敗時拋出的例外"""
    pass


def run_pipeline(filepath: str) -> dict:
    """執行完整資料處理流程"""
    cfg       = Config(debug=True)
    processor = DataProcessor(cfg)
    data      = processor.load(filepath)
    return processor.process(data)
'''
