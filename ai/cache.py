"""
快取管理 — AI Python Code Tutor 第 2 輪

策略：
  1. 以函數原始碼 SHA256 hash（前 16 碼）為檔名
  2. 存為 JSON 檔案在 cache/ 資料夾
  3. TTL 預設 7 天，過期自動重查
  4. 提供命中率統計

JSON 結構：
  cache/{hash}.json → {
      "hash": "a1b2c3d4...",
      "func_name": "load_data",
      "explanation": { ... },
      "created_at": "2025-01-01T00:00:00",
      "api_model": "gemini-2.0-flash",
      "token_cost": {"input_chars": 300, "output_chars": 200}
  }
"""

import hashlib
import json
import os
from datetime import datetime, timedelta


# ── 讀取設定（避免循環 import，直接讀環境變數 fallback）──
try:
    from config import CACHE_DIR, CACHE_TTL_DAYS
except ImportError:
    CACHE_DIR     = os.path.join(os.path.dirname(__file__), "..", "cache")
    CACHE_TTL_DAYS = 7


class ExplanationCache:
    """
    以 SHA256 hash 為 key 的 JSON 檔案快取。
    支援 TTL 過期、命中率統計、清除功能。
    """

    def __init__(self, cache_dir: str = CACHE_DIR):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.hits   = 0
        self.misses = 0

    # ── 內部工具 ─────────────────────────────────────

    def _hash(self, code: str) -> str:
        """回傳程式碼字串的 SHA256 前 16 碼。"""
        return hashlib.sha256(code.strip().encode("utf-8")).hexdigest()[:16]

    def _path(self, h: str) -> str:
        return os.path.join(self.cache_dir, f"{h}.json")

    def _load(self, h: str) -> dict | None:
        """從磁碟讀取快取 entry，不存在時回傳 None。"""
        path = self._path(h)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

    def is_expired(self, entry: dict) -> bool:
        """檢查 entry 是否超過 TTL。"""
        try:
            created = datetime.fromisoformat(entry["created_at"])
            return datetime.now() - created > timedelta(days=CACHE_TTL_DAYS)
        except (KeyError, ValueError):
            return True

    # ── 公開 API ──────────────────────────────────────

    def get(self, code: str) -> dict | None:
        """
        查詢快取。
        命中且未過期 → 回傳 explanation dict
        未命中或已過期 → 回傳 None
        """
        h     = self._hash(code)
        entry = self._load(h)

        if entry is None or self.is_expired(entry):
            self.misses += 1
            return None

        self.hits += 1
        return entry.get("explanation")

    def set(
        self,
        code: str,
        func_name: str,
        explanation: dict,
        api_model: str = "gemini-2.0-flash",
        token_cost: dict | None = None,
    ) -> None:
        """將解釋結果寫入快取。"""
        h     = self._hash(code)
        entry = {
            "hash":        h,
            "func_name":   func_name,
            "explanation": explanation,
            "created_at":  datetime.now().isoformat(),
            "api_model":   api_model,
            "token_cost":  token_cost or {},
        }
        try:
            with open(self._path(h), "w", encoding="utf-8") as f:
                json.dump(entry, f, ensure_ascii=False, indent=2)
        except OSError:
            pass  # 快取寫入失敗不影響主流程

    def stats(self) -> dict:
        """回傳本次 session 的快取統計。"""
        total = len([
            f for f in os.listdir(self.cache_dir) if f.endswith(".json")
        ])
        total_requests = self.hits + self.misses
        return {
            "total_cached": total,
            "hits":         self.hits,
            "misses":       self.misses,
            "hit_rate":     round(self.hits / max(1, total_requests), 3),
        }

    def clear(self) -> int:
        """清除所有快取檔案，回傳刪除數量。"""
        count = 0
        for fname in os.listdir(self.cache_dir):
            if fname.endswith(".json"):
                try:
                    os.remove(os.path.join(self.cache_dir, fname))
                    count += 1
                except OSError:
                    pass
        self.hits   = 0
        self.misses = 0
        return count

    def list_entries(self, limit: int = 20) -> list[dict]:
        """列出最近的快取項目（用於 Debug）。"""
        entries = []
        for fname in sorted(os.listdir(self.cache_dir), reverse=True):
            if not fname.endswith(".json"):
                continue
            entry = self._load(fname[:-5])
            if entry:
                entries.append({
                    "hash":      entry.get("hash", fname[:-5]),
                    "func_name": entry.get("func_name", "?"),
                    "model":     entry.get("api_model", "?"),
                    "created":   entry.get("created_at", "?")[:10],
                    "expired":   self.is_expired(entry),
                })
            if len(entries) >= limit:
                break
        return entries
