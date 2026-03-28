"""
解析 import 語句，提供套件說明（Import 百科）。
第 3 輪完整實作。

ImportInfo = {
    "raw":          str,       # 原始 import 語句
    "package":      str,       # 主套件名稱（頂層）
    "display_name": str,       # 顯示用名稱
    "from_module":  str|None,  # from X import ...
    "aliases":      List[str], # as 別名
    "info":         dict|None, # KNOWN_PACKAGES 資訊
}
"""
import ast
import re

# ── 套件知識庫（30+ 常見套件）─────────────────────────
KNOWN_PACKAGES: dict = {
    # 標準函式庫 ─────────────────────────────────────────
    "os": {
        "description": "作業系統介面操作工具",
        "guide":       "🖥️ 像電腦的遙控器，可以讀寫檔案、查資料夾、操作路徑",
        "url":         "https://docs.python.org/3/library/os.html",
        "category":    "標準函式庫",
        "icon":        "🖥️",
    },
    "sys": {
        "description": "Python 直譯器系統參數存取",
        "guide":       "⚙️ 像 Python 的後台控制台，可查版本、強制退出、控制路徑搜尋",
        "url":         "https://docs.python.org/3/library/sys.html",
        "category":    "標準函式庫",
        "icon":        "⚙️",
    },
    "re": {
        "description": "正規表示式文字比對與搜尋",
        "guide":       "🔍 像超強版的 Ctrl+F，用符號描述複雜字串規則來搜尋資料",
        "url":         "https://docs.python.org/3/library/re.html",
        "category":    "標準函式庫",
        "icon":        "🔍",
    },
    "json": {
        "description": "JSON 格式資料讀寫轉換",
        "guide":       "📄 像字典和字串的翻譯官，讓 Python 物件和 JSON 文字互相轉換",
        "url":         "https://docs.python.org/3/library/json.html",
        "category":    "標準函式庫",
        "icon":        "📄",
    },
    "datetime": {
        "description": "日期時間操作與計算工具",
        "guide":       "📅 像超精準的日曆和時鐘，可以計算時間差、格式化日期",
        "url":         "https://docs.python.org/3/library/datetime.html",
        "category":    "標準函式庫",
        "icon":        "📅",
    },
    "pathlib": {
        "description": "物件導向的檔案路徑操作",
        "guide":       "📁 像智慧路徑管理員，用點點點的方式操作資料夾和檔案路徑",
        "url":         "https://docs.python.org/3/library/pathlib.html",
        "category":    "標準函式庫",
        "icon":        "📁",
    },
    "collections": {
        "description": "特殊容器型別（計數器、有序字典等）",
        "guide":       "🗂️ 像加強版的字典和清單，提供計數器、預設字典等實用容器",
        "url":         "https://docs.python.org/3/library/collections.html",
        "category":    "標準函式庫",
        "icon":        "🗂️",
    },
    "itertools": {
        "description": "高效率迭代器工具集",
        "guide":       "🔄 像迴圈的魔法工具箱，提供組合、排列、鏈結等進階迴圈操作",
        "url":         "https://docs.python.org/3/library/itertools.html",
        "category":    "標準函式庫",
        "icon":        "🔄",
    },
    "typing": {
        "description": "型別提示與標注工具",
        "guide":       "🏷️ 像程式碼的說明標籤，告訴別人和工具這個變數應該是什麼型別",
        "url":         "https://docs.python.org/3/library/typing.html",
        "category":    "標準函式庫",
        "icon":        "🏷️",
    },
    "asyncio": {
        "description": "非同步 I/O 並行程式框架",
        "guide":       "⚡ 像多工處理大師，讓程式能同時等待多個耗時操作而不卡住",
        "url":         "https://docs.python.org/3/library/asyncio.html",
        "category":    "標準函式庫",
        "icon":        "⚡",
    },
    "hashlib": {
        "description": "密碼學雜湊函式工具",
        "guide":       "🔐 像指紋產生器，把任意資料轉換成固定長度的獨特識別碼",
        "url":         "https://docs.python.org/3/library/hashlib.html",
        "category":    "標準函式庫",
        "icon":        "🔐",
    },
    "logging": {
        "description": "程式執行日誌記錄系統",
        "guide":       "📝 像飛機的黑盒子，把程式執行過程中的重要訊息記錄下來備查",
        "url":         "https://docs.python.org/3/library/logging.html",
        "category":    "標準函式庫",
        "icon":        "📝",
    },
    "csv": {
        "description": "CSV 格式表格資料讀寫",
        "guide":       "📊 像 Excel 的簡化版讀寫工具，專門處理逗號分隔的表格資料",
        "url":         "https://docs.python.org/3/library/csv.html",
        "category":    "標準函式庫",
        "icon":        "📊",
    },
    "subprocess": {
        "description": "執行外部命令與子程序",
        "guide":       "💻 像 Python 的終端機遙控器，可以在程式內執行系統指令",
        "url":         "https://docs.python.org/3/library/subprocess.html",
        "category":    "標準函式庫",
        "icon":        "💻",
    },
    "functools": {
        "description": "高階函數與可呼叫物件工具",
        "guide":       "🛠️ 像函數增強工具箱，提供快取、偏函數等讓函數更強大的工具",
        "url":         "https://docs.python.org/3/library/functools.html",
        "category":    "標準函式庫",
        "icon":        "🛠️",
    },
    "abc": {
        "description": "抽象基底類別定義工具",
        "guide":       "📐 像建築藍圖工具，定義所有子類別都必須實作的介面規範",
        "url":         "https://docs.python.org/3/library/abc.html",
        "category":    "標準函式庫",
        "icon":        "📐",
    },
    "math": {
        "description": "數學函式與常數計算工具",
        "guide":       "🔢 像袖珍計算機，提供平方根、三角函數、π 等各種數學工具",
        "url":         "https://docs.python.org/3/library/math.html",
        "category":    "標準函式庫",
        "icon":        "🔢",
    },
    "time": {
        "description": "時間存取與延遲工具",
        "guide":       "⏱️ 像精準的碼錶，可以暫停程式、計算執行時間",
        "url":         "https://docs.python.org/3/library/time.html",
        "category":    "標準函式庫",
        "icon":        "⏱️",
    },
    "dataclasses": {
        "description": "簡潔定義資料類別的標準工具",
        "guide":       "📋 像自動填表機，用 @dataclass 幫你省去寫 __init__ 的麻煩",
        "url":         "https://docs.python.org/3/library/dataclasses.html",
        "category":    "標準函式庫",
        "icon":        "📋",
    },
    "ast": {
        "description": "Python 抽象語法樹解析工具",
        "guide":       "🌳 像程式碼的解剖工具，把 Python 程式碼拆解成可操作的樹狀結構",
        "url":         "https://docs.python.org/3/library/ast.html",
        "category":    "標準函式庫",
        "icon":        "🌳",
    },
    "textwrap": {
        "description": "文字換行與縮排處理工具",
        "guide":       "📝 像文字的排版助手，自動處理長文字換行、去除縮排等格式問題",
        "url":         "https://docs.python.org/3/library/textwrap.html",
        "category":    "標準函式庫",
        "icon":        "📝",
    },
    # 第三方套件 ──────────────────────────────────────────
    "pandas": {
        "description": "資料分析與處理的瑞士刀",
        "guide":       "🐼 想像 Excel 的超強化版，可以用程式操作大型表格、篩選、彙總",
        "url":         "https://pandas.pydata.org",
        "category":    "資料處理",
        "icon":        "🐼",
    },
    "numpy": {
        "description": "高效能數值計算陣列工具",
        "guide":       "🔢 像超快的計算機，能同時對一整排數字做數學運算，比列表快百倍",
        "url":         "https://numpy.org",
        "category":    "數值計算",
        "icon":        "🔢",
    },
    "matplotlib": {
        "description": "Python 標準繪圖視覺化函式庫",
        "guide":       "📈 像電子白板，把數字轉成折線圖、長條圖、散點圖等各種圖表",
        "url":         "https://matplotlib.org",
        "category":    "視覺化",
        "icon":        "📈",
    },
    "seaborn": {
        "description": "統計資料視覺化美化工具",
        "guide":       "🎨 像 matplotlib 的美妝師，讓統計圖表自動變得更漂亮、更專業",
        "url":         "https://seaborn.pydata.org",
        "category":    "視覺化",
        "icon":        "🎨",
    },
    "plotly": {
        "description": "互動式網頁圖表視覺化",
        "guide":       "📊 像會動的圖表，可以縮放、點擊的互動式視覺化，適合網頁展示",
        "url":         "https://plotly.com/python",
        "category":    "視覺化",
        "icon":        "📊",
    },
    "requests": {
        "description": "簡潔的 HTTP 網路請求工具",
        "guide":       "🌐 像 Python 的瀏覽器，可以向網站發送請求、抓取資料",
        "url":         "https://requests.readthedocs.io",
        "category":    "網路請求",
        "icon":        "🌐",
    },
    "httpx": {
        "description": "支援非同步的現代 HTTP 客戶端",
        "guide":       "⚡ 像升級版的 requests，支援非同步請求，速度更快效率更高",
        "url":         "https://www.python-httpx.org",
        "category":    "網路請求",
        "icon":        "⚡",
    },
    "aiohttp": {
        "description": "非同步 HTTP 客戶端與伺服器框架",
        "guide":       "🚀 像非同步版的 requests，同時發多個請求而不互相等待",
        "url":         "https://docs.aiohttp.org",
        "category":    "網路請求",
        "icon":        "🚀",
    },
    "flask": {
        "description": "輕量級 Python Web 應用框架",
        "guide":       "🍶 像搭積木蓋網站，用很少的程式碼就能建立 API 或網頁服務",
        "url":         "https://flask.palletsprojects.com",
        "category":    "Web 框架",
        "icon":        "🍶",
    },
    "fastapi": {
        "description": "高效能現代 Python API 框架",
        "guide":       "🚀 像 Flask 的超跑版，自動產生文件、速度極快，適合建立 REST API",
        "url":         "https://fastapi.tiangolo.com",
        "category":    "Web 框架",
        "icon":        "🚀",
    },
    "django": {
        "description": "功能完整的大型 Web 開發框架",
        "guide":       "🏗️ 像整棟大樓的建築套件，內建資料庫、後台管理、認證等全套功能",
        "url":         "https://www.djangoproject.com",
        "category":    "Web 框架",
        "icon":        "🏗️",
    },
    "streamlit": {
        "description": "快速建立資料應用的 Web 框架",
        "guide":       "🎈 像把 Python 腳本變成網頁 App 的魔法棒，幾行程式碼就有互動介面",
        "url":         "https://streamlit.io",
        "category":    "Web 框架",
        "icon":        "🎈",
    },
    "selenium": {
        "description": "自動化瀏覽器操作測試工具",
        "guide":       "🤖 像機器人操控瀏覽器，自動點按鈕、填表單、抓動態網頁資料",
        "url":         "https://selenium-python.readthedocs.io",
        "category":    "自動化",
        "icon":        "🤖",
    },
    "playwright": {
        "description": "現代瀏覽器自動化測試框架",
        "guide":       "🎭 像更強大的 Selenium，支援 Chrome/Firefox/Safari 的自動化操作",
        "url":         "https://playwright.dev/python",
        "category":    "自動化",
        "icon":        "🎭",
    },
    "openpyxl": {
        "description": "Excel 檔案讀寫操作工具",
        "guide":       "📑 像 Python 的 Excel 助手，可以讀取、修改、創建 .xlsx 試算表",
        "url":         "https://openpyxl.readthedocs.io",
        "category":    "檔案處理",
        "icon":        "📑",
    },
    "bs4": {
        "description": "HTML/XML 網頁解析工具（BeautifulSoup）",
        "guide":       "🕷️ 像網頁的 X 光機，把 HTML 標籤變成可以程式操作的樹狀結構",
        "url":         "https://www.crummy.com/software/BeautifulSoup",
        "category":    "網頁解析",
        "icon":        "🕷️",
    },
    "beautifulsoup4": {
        "description": "HTML/XML 網頁解析工具",
        "guide":       "🕷️ 像網頁的 X 光機，把 HTML 標籤變成可以程式操作的樹狀結構",
        "url":         "https://www.crummy.com/software/BeautifulSoup",
        "category":    "網頁解析",
        "icon":        "🕷️",
    },
    "sklearn": {
        "description": "機器學習演算法完整工具包（scikit-learn）",
        "guide":       "🤖 像 AI 的工具箱，內建分類、迴歸、聚類等各種機器學習算法",
        "url":         "https://scikit-learn.org",
        "category":    "機器學習",
        "icon":        "🧠",
    },
    "tensorflow": {
        "description": "Google 深度學習框架",
        "guide":       "🧠 像神經網路建造機，讓你用積木方式搭建和訓練深度學習模型",
        "url":         "https://www.tensorflow.org",
        "category":    "深度學習",
        "icon":        "🧠",
    },
    "torch": {
        "description": "PyTorch 深度學習研究框架",
        "guide":       "🔥 像 NumPy 的 AI 進化版，Facebook 出品的靈活深度學習框架",
        "url":         "https://pytorch.org",
        "category":    "深度學習",
        "icon":        "🔥",
    },
    "openai": {
        "description": "OpenAI API 官方 Python 客戶端",
        "guide":       "🤖 像通往 GPT 的橋樑，讓 Python 程式輕鬆呼叫 ChatGPT 等 AI 服務",
        "url":         "https://github.com/openai/openai-python",
        "category":    "AI / LLM",
        "icon":        "🤖",
    },
    "anthropic": {
        "description": "Anthropic Claude API 官方客戶端",
        "guide":       "🐙 像通往 Claude 的大門，讓 Python 程式呼叫 Claude AI 進行對話",
        "url":         "https://github.com/anthropics/anthropic-sdk-python",
        "category":    "AI / LLM",
        "icon":        "🐙",
    },
    "sqlalchemy": {
        "description": "Python 資料庫 ORM 框架",
        "guide":       "🗄️ 像資料庫的翻譯官，用 Python 物件操作 SQL 資料庫，不必寫 SQL",
        "url":         "https://www.sqlalchemy.org",
        "category":    "資料庫",
        "icon":        "🗄️",
    },
    "pydantic": {
        "description": "資料驗證與序列化工具",
        "guide":       "✅ 像資料的品管員，自動檢查、轉換、驗證輸入資料是否符合規格",
        "url":         "https://docs.pydantic.dev",
        "category":    "資料驗證",
        "icon":        "✅",
    },
    "pytest": {
        "description": "Python 自動化測試框架",
        "guide":       "🧪 像程式碼的健康檢查工具，自動跑各種測試確認程式邏輯正確",
        "url":         "https://pytest.org",
        "category":    "測試",
        "icon":        "🧪",
    },
    "PIL": {
        "description": "Python 圖像處理函式庫（Pillow）",
        "guide":       "🖼️ 像 Photoshop 的輕量版，可裁切、縮放、轉檔、加濾鏡等圖片處理",
        "url":         "https://pillow.readthedocs.io",
        "category":    "圖像處理",
        "icon":        "🖼️",
    },
    "dotenv": {
        "description": "從 .env 檔載入環境變數",
        "guide":       "🔒 像密碼保險箱，把 API Key 等敏感資訊存在 .env 檔安全管理",
        "url":         "https://github.com/theskumar/python-dotenv",
        "category":    "設定管理",
        "icon":        "🔒",
    },
    "yaml": {
        "description": "YAML 格式設定檔讀寫工具",
        "guide":       "📋 像人類友善的設定檔格式，比 JSON 更易讀，常用於設定和配置管理",
        "url":         "https://pyyaml.org",
        "category":    "檔案處理",
        "icon":        "📋",
    },
    "rich": {
        "description": "終端機彩色文字美化工具",
        "guide":       "🎨 像終端機的化妝師，讓 print 輸出有顏色、有表格、有進度條",
        "url":         "https://rich.readthedocs.io",
        "category":    "終端機工具",
        "icon":        "🎨",
    },
    "click": {
        "description": "命令列介面建立工具",
        "guide":       "⌨️ 像命令列的積木，用裝飾器輕鬆把 Python 函數變成 CLI 命令",
        "url":         "https://click.palletsprojects.com",
        "category":    "命令列工具",
        "icon":        "⌨️",
    },
    "scipy": {
        "description": "科學計算與工程數學函式庫",
        "guide":       "🔬 像工程師的數學工具箱，提供積分、微分方程、信號處理等高級計算",
        "url":         "https://scipy.org",
        "category":    "科學計算",
        "icon":        "🔬",
    },
    "boto3": {
        "description": "AWS 雲端服務 Python SDK",
        "guide":       "☁️ 像 AWS 的遙控器，讓 Python 操作 S3、EC2、Lambda 等雲端服務",
        "url":         "https://boto3.amazonaws.com/v1/documentation/api/latest",
        "category":    "雲端服務",
        "icon":        "☁️",
    },
    "win32com": {
        "description": "Windows COM 物件操作介面",
        "guide":       "🪟 像 Windows 的後台遙控器，可自動操作 Outlook、Excel 等 Office 軟體",
        "url":         "https://github.com/mhammond/pywin32",
        "category":    "Windows 自動化",
        "icon":        "🪟",
    },
    "google": {
        "description": "Google 服務 API 客戶端工具",
        "guide":       "🔍 像 Google 服務的橋樑，可連接 Drive、Sheets、Gmail 等服務",
        "url":         "https://github.com/googleapis/google-api-python-client",
        "category":    "雲端服務",
        "icon":        "🔍",
    },
    "genai": {
        "description": "Google Gemini AI API 客戶端",
        "guide":       "✨ 像通往 Gemini 的橋樑，讓 Python 程式呼叫 Google AI 生成式模型",
        "url":         "https://ai.google.dev/gemini-api/docs",
        "category":    "AI / LLM",
        "icon":        "✨",
    },
    "pydub": {
        "description": "音訊檔案操作與處理工具",
        "guide":       "🎵 像音訊的剪輯工具，可以剪切、合併、轉換各種音訊格式",
        "url":         "https://github.com/jiaaro/pydub",
        "category":    "多媒體",
        "icon":        "🎵",
    },
    "cryptography": {
        "description": "加密解密安全演算法工具",
        "guide":       "🔐 像程式裡的金鑰管理員，提供 AES、RSA 等各種加密和驗證工具",
        "url":         "https://cryptography.io",
        "category":    "資安",
        "icon":        "🔐",
    },
}

# ── 別名對照（import 名稱 → 套件名） ──────────────────
_ALIASES: dict = {
    "bs4":      "bs4",
    "np":       "numpy",
    "pd":       "pandas",
    "plt":      "matplotlib",
    "tf":       "tensorflow",
    "genai":    "genai",
    "cv2":      "opencv-python",
}

# 標準函式庫集合（快速判斷）
_STDLIB = {
    "os", "sys", "re", "json", "datetime", "pathlib", "collections",
    "itertools", "typing", "asyncio", "hashlib", "logging", "csv",
    "subprocess", "functools", "abc", "math", "time", "ast", "textwrap",
    "copy", "io", "threading", "multiprocessing", "socket", "struct",
    "enum", "dataclasses", "contextlib", "warnings", "traceback",
    "inspect", "importlib", "pkgutil", "platform", "shutil", "glob",
    "tempfile", "zipfile", "tarfile", "gzip", "pickle", "shelve",
    "sqlite3", "urllib", "http", "email", "html", "xml", "string",
    "random", "statistics", "decimal", "fractions", "heapq", "bisect",
    "array", "queue", "pprint", "difflib", "uuid", "base64", "hmac",
    "secrets", "getpass", "argparse", "configparser", "tomllib",
    "unittest", "doctest", "timeit", "cProfile", "gc", "weakref",
    "dataclasses", "contextlib", "io", "copy",
}


def _extract_top_package(import_str: str) -> str:
    """從 import 字串提取頂層套件名稱。"""
    # e.g. "import os.path" → "os"
    # e.g. "from collections.abc import ABC" → "collections"
    clean = import_str.strip()
    if clean.startswith("from "):
        # "from X.Y import Z" → "X"
        rest = clean[5:].split()[0]
        return rest.split(".")[0]
    elif clean.startswith("import "):
        # "import X, Y" → "X"（取第一個）
        rest = clean[7:].split(",")[0].strip()
        return rest.split(".")[0].split(" as ")[0].strip()
    return clean.split(".")[0]


def lookup_package(package: str) -> dict | None:
    """查詢套件資訊，回傳 KNOWN_PACKAGES entry 或 None。"""
    name = _ALIASES.get(package, package)
    return KNOWN_PACKAGES.get(name) or KNOWN_PACKAGES.get(name.lower())


def parse_imports_detail(source_code: str) -> list:
    """
    解析原始碼中的 import 語句，回傳詳細 ImportInfo 列表。

    每筆 ImportInfo：
    {
        "raw":          str,       # 原始 import 語句
        "package":      str,       # 頂層套件名稱
        "display_name": str,       # 顯示用名稱
        "is_stdlib":    bool,      # 是否為標準函式庫
        "from_module":  str|None,  # from X 的 X
        "aliases":      List[str], # as 別名
        "info":         dict|None, # KNOWN_PACKAGES 資訊（可能為 None）
    }
    """
    if not source_code.strip():
        return []

    try:
        tree = ast.parse(source_code)
    except Exception:
        return []

    results = []
    seen    = set()  # 去重（同套件只顯示一次）

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            try:
                raw = ast.unparse(node)
            except Exception:
                continue

            package = _extract_top_package(raw)
            if package in seen:
                continue
            seen.add(package)

            # 別名
            aliases = []
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.asname:
                        aliases.append(alias.asname)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.asname:
                        aliases.append(alias.asname)
                    elif alias.name != "*":
                        aliases.append(alias.name)

            from_module = None
            if isinstance(node, ast.ImportFrom) and node.module:
                from_module = node.module

            is_stdlib = package in _STDLIB

            results.append({
                "raw":          raw,
                "package":      package,
                "display_name": package,
                "is_stdlib":    is_stdlib,
                "from_module":  from_module,
                "aliases":      aliases[:5],  # 最多顯示 5 個
                "info":         lookup_package(package),
            })

    return results
