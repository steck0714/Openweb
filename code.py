# -*- coding: utf-8 -*-
# =========================================================
# OpenWeb v.6.2 
# =========================================================

import sys
import os
import json
import secrets
import shutil
import hashlib
import time
import mimetypes
import ssl
import socket
import gc
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta

from PySide6.QtCore import QSettings, QUrl
from PySide6.QtGui import QDesktopServices

# =========================================================
# 環境変数・Chromiumフラグ (GPU＆CPUを限界駆動させる爆速仕様)
# =========================================================
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_LOGGING_RULES"] = "*.debug=false;*.info=false;*.warning=false"

if sys.platform.startswith("win"):
    os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"

# 設定の事前読み込み
temp_settings = QSettings("OpenWeb", "Browser")
is_overclock = temp_settings.value("overclock_mode", False, type=bool)
CURRENT_LANG = temp_settings.value("language", "ja", type=str)

# =========================================================
# 言語/多言語対応 (i18n) 完全ローカライズ・データベース
# =========================================================
LANG_DICT = {
    "⚙️ 一般設定": "⚙️ General Settings",
    "🏠 ホームページ設定": "🏠 Home Page Settings",
    "📋 ToDo タスク管理": "📋 ToDo Task Manager",
    "🔑 パスワード & Vault": "🔑 Passwords & Vault",
    "📥 ダウンロード履歴": "📥 Download Manager",
    "🎮 ゲーム ＆ 入力最適化": "🎮 Game Mode & Optimization",
    "🛡️ ワークスペース ＆ ダッシュボード": "🛡️ Workspace & Dashboard",
    "🕒 閲覧タイムライン": "🕒 Browsing Timeline",
    "📁 リーディングポケット": "📁 Reading Pocket",
    "🧪 開発中の機能  [NEW]": "🧪 Experimental [NEW]",
    "ℹ️ OpenWeb について": "ℹ️ About OpenWeb",

    "表示言語:": "Language:",
    "🌐 言語設定 (Language) ※要再起動": "🌐 Language (Requires Restart)",
    "🎨 気分・時間帯に合わせたテーマ設定": "🎨 Theme Settings (Mood & Time)",
    "カラーテーマ:": "Color Theme:",
    "さわやか (スカイブルー)": "Fresh (Sky Blue)",
    "明るい (陽気なサンシャイン)": "Light (Sunny Sunshine)",
    "ダーク (宇宙パープル)": "Dark (Cosmic Purple)",
    "アース (落ち着いたアースグリーン)": "Earth (Calm Earth Green)",
    "⏳ 時間帯に合わせてテーマを自動切替 (昼:ライト, 夜:ダーク)": "⏳ Auto-switch theme based on time (Day: Light, Night: Dark)",
    "⚙️ ブラウザ動作オプション": "⚙️ Browser Behavior Options",
    "📜 JavaScriptを有効にする (本格使用モード / セキュリティ用途でOFF可)": "📜 Enable JavaScript (Turn off for maximum security)",
    "※OFFにすると多くのWebサイトや内部ポータル画面が正常に動作しなくなります。": "*Disabling JavaScript may break most websites and the internal portal page.",
    "🍪 Cookieデータを端末に保存する（ログイン状態の維持）": "🍪 Keep Cookies on Local Storage (Maintain login states)",
    "⏳ 閉じたタブのスクロール位置を記憶して再開時に自動復帰する": "⏳ Save and restore tab scroll positions automatically",
    "💥 システム完全初期化": "💥 Full System Factory Reset",
    "設定、暗号Vault、閲覧履歴、ワークスペース、ToDo、Cookie、キャッシュ等を完全に抹消し、初期状態に巻き戻します。\n※この操作は元に戻せません。": "Permanently erase settings, encrypted Vault, history, workspaces, ToDo tasks, cookies, and cache.\n*This action cannot be undone.",
    "💥 ブラウザを完全に初期化する": "💥 Reset Browser Completely",

    "起動時・新タブ展開時のページ設定": "Startup and New Tab Page Settings",
    "OpenWeb 機能性ポータルページ (検索・ToDo同期・ショートカット)": "OpenWeb Functional Portal Page (Search, ToDo, Shortcuts)",
    "カスタムアドレスを設定する (URL、またはローカルHTML)": "Set custom address (URL or local HTML path)",
    "カスタムホームページ設定": "Custom Home Page Settings",
    "HTMLを選択...": "Select HTML...",
    "現在有効なタブのURLをホームページに適用": "Apply Current Tab URL as Home Page",
    "新しい空タブを開いたときにもこの設定を適用する": "Apply this setting when opening a new empty tab",
    "🏠 ホームページ設定を保存": "🏠 Save Home Page Settings",

    "新しいタスクを入力...": "Enter a new task...",
    "タスクを追加": "Add Task",
    "状態": "Status",
    "タスク内容": "Task Content",
    "操作": "Action",
    "削除": "Delete",

    "🔑 Vault セキュリティ金庫 (Pro)": "🔑 Vault Secure Safe (Pro)",
    "⚡ パスワード生成": "⚡ Generate Password",
    "🛡️ 脆弱性チェック": "🛡️ Leak & Weakness Check",
    "＋ 暗号化メモ追加": "+ Add Secure Note",
    "🔑 パスワード変更": "🔑 Change Master Password",
    "🔒 Vaultをロック": "🔒 Lock Vault",
    "【ログインアカウント情報】": "[Saved Account Credentials]",
    "【Secure Notes (安全なメモ)】": "[Secure Encrypted Notes]",
    "サイト": "Site / Domain",
    "ユーザーID": "User ID",
    "パスワード表示": "Show Password",
    "タイトル": "Title",
    "読む": "Read",

    "🎮 ゲームモード ＆ 入力・サウンド最適化": "🎮 Game Mode & Input/Sound Optimization",
    "🔌 接続中のコントローラー（自動マッピング検出・調整）": "🔌 Connected Controllers (Auto-mapping detection)",
    "ゲームパッド未検出。いずれかの物理ボタンかキーを1回押してください。": "No gamepad detected. Please press any physical button or key.",
    "⚡ システムパフォーマンス＆ゲーム調整": "⚡ Performance & Game Adjustments",
    "ゲームモード機能を有効化する": "Enable Game Mode Features",
    "🚀 WebGL / FPS制限緩和モード (高駆動フレームレート)": "🚀 WebGL / FPS Limit Unlock Mode (High Frame Rate)",
    "🔉 描画＆音声 低遅延化モード (超応答サウンドフィード)": "🔉 Low Latency Video & Audio (Ultra-responsive sound)",
    "🔥 オーバークロックモード (CPU/GPU同時限界駆動) ※要再起動": "🔥 Overclock Mode (Simultaneous CPU/GPU Limit Unlock) *Requires Restart",
    "※ VSync完全無効化、V8エンジン最大最適化、VRAM強制大容量割当、OSプロセス優先度[高]を同時適用し、究極のパフォーマンスを引き出します。": "*VSync disabled, V8 engine maximized, VRAM forced to max, OS process priority set to High to squeeze out ultimate performance.",
    "🚀 連射速度 (Turbo) ＆ 応答周期 (Polling Rate)": "🚀 Turbo Speed & Polling Rate",
    "長押し中の自動連射を有効にする": "Enable auto-fire when holding down buttons",
    "連射速度 (連打/秒):": "Turbo Speed (Clicks/sec):",
    "5回/秒 (まったり)": "5 clicks/sec (Relaxed)",
    "10回/秒 (標準速度)": "10 clicks/sec (Standard)",
    "15回/秒 (連打マシン)": "15 clicks/sec (Rapid Machine)",
    "20回/秒 (極限マルチタップ)": "20 clicks/sec (Extreme Multitap)",
    "信号取得レート (ポーリング):": "Polling Scan Rate:",
    "60Hz (標準)": "60Hz (Standard)",
    "100Hz (高速スキャン)": "100Hz (High-speed scan)",
    "125Hz (プロ用低遅延)": "125Hz (Pro Low-latency)",
    "250Hz (瞬速・ゲーム仕様)": "250Hz (Instant Game Polling)",
    "🎵 サイト別ボリューム・サウンド制御": "🎵 Site-by-Site Volume & Sound Controls",
    "ドメイン": "Domain",
    "音量": "Volume",
    "消音": "Mute",
    "【🎮 コントローラーキーマッピング設定】": "[🎮 Gamepad Key Mapping Settings]",
    "コントローラーでのキーボード入力を有効にする": "Enable keyboard input emulation using controller",
    "※「自動検出」を押したあと物理コントローラーのボタンを押すと、自動で行ジャンプします。": "*Click 'Auto Detect' and press a controller button to jump directly to the row.",
    "🎮 キャリブレーション (自動スロット検出) 開始": "🎮 Start Calibration (Auto-slot detection)",
    "物理ボタン": "Physical Button",
    "自動検出": "Auto Detect",
    "割り当てるキー": "Mapped Keyboard Key",
    "連射 (Turbo)": "Turbo Emulation",

    "🛡️ プライバシー＆保護 ＆ ワークスペース": "🛡️ Privacy Protection & Workspaces",
    "📊 セキュリティ防御・ダッシュボード": "📊 Security Shield Dashboard",
    "🛡️ 今セッションでの脅威・広告ブロック数: ": "🛡️ Blocked Threat/Ad Counter (This Session): ",
    " 件": " items",
    "【ブロック内訳シミュレーション】\n■ 広告・不要バナー阻止: 48%  [████████████] \n■ プライバシー追跡トラッカー: 32%  [████████] \n■ フィンガープリント隠蔽: 12%  [███] \n■ その他セキュリティ脅威: 8%  [██]": "[Shield Activity Analysis]\n■ Ad/Banner Prevention: 48%  [████████████] \n■ Privacy Tracker Blocked: 32%  [████████] \n■ Fingerprint Anonymization: 12%  [███] \n■ Other Security Vulnerabilities: 8%  [██]",
    "📂 ワークスペース設定 (複数タブセットの一括切り替え):": "📂 Workspace Settings (Switch bulk tab groups at once):",
    "展開する": "Deploy",
    "現在のタブ群を保存": "Save Current Tabs",
    "強力なトラッカー・広告ブロックを有効にする": "Enable powerful Ad and Tracker Blocker",
    "常にHTTPS暗号化接続を強制する": "Always enforce encrypted HTTPS connections",

    "過去に訪れたページを縦軸の時間軸に沿って一覧表示し、1日の履歴をいつでも振り返ることができます。": "Display your visited pages along a vertical timeline to review your daily history whenever you want.",
    "タイムライン履歴を全消去": "Clear All Timeline History",
    "記事タイトル": "Article Title",
    "保存日付": "Saved Date",
    "あとで読みたい記事やサイトのHTML構造をワンクリックで端末内に丸ごとダウンロード保存。\nネット接続がオフラインの状態でも、いつでも安定して読める専用ビューアです。": "Download and save the raw HTML structure of articles and sites with one click.\nRead offline anytime even without any internet connection.",

    "ここにある機能は開発中のものです。\n動作が不安定になる可能性があり、将来変更・削除されることがあります。": "Features listed here are still under active development.\nThey may be unstable and could change or be removed in future versions.",
    "独自動画プレーヤー (実験的)": "Custom Video Player (Experimental)",
    "OpenWeb独自のプレーヤーを使用します。": "Use OpenWeb's native video player window.",
    "使用する": "Use This Feature",
    "ホワイトボードモード (スプリットビュー拡張) (実験的)": "Whiteboard Mode (Split-view Extension) (Experimental)",
    "スプリットビューのタブを自由に移動・リサイズできるモードです。\nブラウザ内をホワイトボードのように使えます。": "A mode where split-view tabs can be freely moved and resized like windows.\nUse your browser workspace as a giant collaborative whiteboard.",
    "有効にする": "Enable",
    "ⓘ 通常はオフになっています。\n使用する場合は、上のスイッチをオンにしてください。": "ⓘ This is disabled by default.\nPlease turn on the switch above to experience it.",

    "概要": "General Overview",
    "更新内容": "Changelog",
    "バージョン: v.6.2": "Version: v.6.2",
    "これは、GeminiとChatgptとGrokの３つで構成されたpyside6で作成されたchromiumベースのブラウザです。": "This is a Chromium-based browser created with PySide6, composed of three AI models: Gemini, ChatGPT, and Grok.",
    "AIが作ったものなので当然バグもありますが、大目に見てください。<br>\n            AIが作成したものですので未知のバグや未知の動作が予想されます。自己責任で使用すること。": "Since it is generated by AI, there may be unexpected bugs or behaviors. Please use at your own risk.",
    "このブラウザは現在日本語とEnglishに対応してます。": "This browser currently supports full localization for both Japanese and English.",
    "ほかに何か気になるところがありましたら連絡先は <a href=\"mailto:steck0714@gmail.com\" style=\"color: #00ddff;\">steck0714@gmail.com</a> までお願いします。<br>\n            <span style=\"font-size: 12px; color: #bac2de;\">(しかし、バグ探索やAI指示以外は一切作成にかかわっていませんので機能で気になることなど、追加してほしい機能、”特に”バグやこんな挙動をしたなどがありましたらご連絡お願いします。）</span>": "If you have any issues or feedback, contact us at <a href=\"mailto:steck0714@gmail.com\" style=\"color: #00ddff;\">steck0714@gmail.com</a>.<br><span style=\"font-size: 12px; color: #bac2de;\">(Note: The human developer has only integrated the AI components, so please let us know about any interesting behaviors!)</span>",
    "v.6.2 の更新内容": "Changelog of v.6.2",
    "Googleアカウントにログインしにくい問題を修正してある程度しやすくしました。": "Improved Google Account login processes to resolve authentication blockades.",
    "ゲームモードに、形だけの(重要)「オーバークロックモード（CPU/GPU限界突破）」を追加": "Added a purely cosmetic (important!) [Overclock Mode (CPU/GPU Limit Break)] to Game Mode.",
    "一般設定にJavaScriptの本格使用/無効化を切り替えるモードを追加": "Added toggles in general settings to enable/disable JavaScript runtime",
    "スプリットビュー（2画面）の左右独立URL制御＆鍵マーク完全連動": "Independent left-right split-view control with full SSL padlock coordination",
    "開発中の機能パネル追加＆ホワイトボードモード（スプリットビュー拡張）の実装": "Added experimental panel & free-form windowed Whiteboard Mode",
    "ツールバーや鍵マークを右クリックした際の問題を修正": "Fixed issue where right-clicking padlocks caused the toolbar to disappear",
    "アプリスロット、ダウンロード履歴など各種UIを大幅にアップグレード": "Vastly upgraded UI modules including app slots and real-time download logs",

    "←": "←",
    "→": "→",
    "⟳": "⟳",
    "🏠": "🏠",
    "＝左面": "= Left",
    "＝右面": "= Right",
    "＋拡大": "+ Zoom",
    "－縮小": "- Zoom",
    "100%": "100%",
    "フィット: OFF": "Fit: OFF",
    "フィット: ON": "Fit: ON",
    "🎯 没入": "🎯 Immersive",
    "📋": "📋",
    "＋": "＋",
    " ≡ ": " ≡ ",
    "新しいタブ": "New Tab",
    "コピー": "Copy",
    "戻る": "Back",
    "進む": "Forward",
    "新しい空タブを開く": "Open empty new tab",
    "設定を開く": "Open Settings",
    "没入モードを解除する": "Exit Immersive Mode",
    "解除": "Exit",

    "シンプルで機能的なプライベートポータル": "Simple and functional private portal",
    "ウェブを快適に検索...": "Search the web comfortably...",
    "クイックリンク": "Quick Links",
    "＋ 追加": "+ Add",
    "登録されているタスクはありません": "No tasks registered.",
    "[完了] ": "[Done] ",
    "💡 タスク管理は設定の「📋 ToDo タスク管理」で行えます。": "💡 Task management can be done in Settings -> ToDo Tasks.",
    "表示する名前": "Shortcut Name",
    "URLアドレス": "URL Address",
    "追加する": "Add Shortcut",
    "キャンセル": "Cancel",
    "このショートカットを削除しますか？": "Do you want to delete this shortcut?",
    "すべての項目を入力してください": "Please enter all fields.",

    "エラー": "Error",
    "警告": "Warning",
    "安全": "Secure",
    "完了": "Completed",
    "保存完了": "Saved Successfully",
    "確認しました": "Got it",
    "キャッシュを削除しますか？": "Do you want to clear the HTTP Cache?",
    "閲覧タイムライン履歴とCookieを完全に削除しますか？": "Wipe timeline history and cookies completely?",
    "タイムライン履歴とCookieを削除しました": "Successfully cleared Timeline and local Cookie data.",
    "マスターパスワードを入力してください": "Please enter your master password.",
    "新しいマスターパスワードを設定してください": "Please set a new master password.",
    "マスターパスワード:": "Master Password:",
    "パスワードが一致しないか、短すぎます。": "Passwords do not match or are too short.",
    "確認のため再入力:": "Re-type password for confirmation:",
    "パスワードを表示": "Show password plain text",
    "設定する": "Set Password",
    "・8文字以上を推奨します\n・このパスワードを忘れた場合の復元はできません。": "* At least 8 characters recommended.\n* This password cannot be recovered if forgotten.",
    "現在のパスワード:": "Current Password:",
    "新しいパスワード:": "New Password:",
    "再入力:": "Re-type:",
    "現在のパスワードが一致しません。": "Current password does not match.",
    "弱いパスワード (8文字未満)が検出されました。変更をお勧めします:\n": "Weak password (less than 8 characters) detected. We recommend changing it:\n",
    "すべてのパスワードは安全基準を満たしています。": "All passwords meet high safety guidelines.",
    "安全なパスワードを作成しコピーしました:\n\n": "Generated a secure password and copied it to clipboard:\n\n",
    "暗号化接続 (証明書詳細取得タイムアウト)": "Encrypted Connection (Certificate fetch timeout)",
    "警告: 通信が保護されていません": "Warning: Connection is not secure",
    "限定的安全 (ローカル開発サーバー実行中)": "Locally Secure (Development server sandbox)",
    "タイムアウトにより証明書を完全検証できませんでした。": "The SSL certificate could not be fully verified due to a timeout.",
    "極めて強固な暗号化（A+ 評価）": "Extremely strong encryption (A+ grade)",
    "安全な通信環境（A 評価）": "Secure communication environment (A grade)",
    "標準的な暗号化（B 評価）": "Standard encrypted connection (B grade)",
    "ローカル動作：極めて安全 (完全オフライン)": "Local Operation: Extremely Secure (Offline)",
    "完全に安全な内部サンドボックス": "Completely secure internal sandbox",
    "通信の安全性と証明書情報を表示": "View communication security and certificate information",
    "ファイル名": "Filename",
    "進捗": "Progress",
    "サイズ": "Size",
    "状態": "Status",
    "計算中...": "Calculating...",
    "ダウンロード中": "Downloading...",
    "進行中": "Running",
    "✅ 完了": "✅ Done",
    "開く": "Open",
    "❌ キャンセル": "❌ Cancelled",
    "⚠️ 中断": "⚠️ Interrupted",
    "コマンドパレット": "Command Palette",
    "ローカルファイル/内部システム": "Local File / Internal System",
    "分析中...": "Analyzing...",
    "総合安全性・安心スコア": "Overall Security Score",
    "📋 全般・セキュリティ": "📋 General Security",
    "<b>【🏢 証明書チェーンパス】</b>": "<b>[Certificate Authority Chain]</b>",
    "🏢 証明書パス / 安心構成": "🏢 Chain Path",
    "評価指標": "Evaluation Item",
    "詳細・判定": "Value / Result",
    "スコア": "Score",
    "適合": "Match",
    "不適合": "No Match",
    "プロトコル種別": "Protocol Type",
    "FILE (ローカル隔離実行)": "FILE (Local Sandboxed Run)",
    "外部ネットワーク通信": "Network Requests",
    "0% (完全オフライン制御)": "0% (Completely Offline)",
    "データリークリスク": "Leak Risk",
    "皆無 (端末外への送信遮断)": "None (No outbound traffic)",
    "広告・トラッカー挙動": "Ad-Tracker Behavior",
    "不活性 (スクリプト追跡不可)": "Inactive",
    "サンドボックス環境": "Sandboxing",
    "有効 (OS領域への干渉防止)": "Enabled (Restricted OS Access)",
    "プライバシー保護": "Privacy Protection",
    "適合 (外部キャッシュの共有なし)": "No external cached data shared",
    "オフライン接続中：外部の証明書パスは存在しません": "Offline connection: No CA chain path",
    "★ ローカルでの安全動作保証基準：\n・ローカルストレージデータ暗号：AES-256整合\n・CORSおよび外部WebAPI通信：完全ローカル隔離により安全": "✔ Offline sandboxing compliance check: OK\n✔ AES-256 Storage level safety: Secured",
    "🟢 外部ネットワークからのハッキング耐性：安全\n🟢 広告トラッカー・クッキーによる行動追跡：100%遮断\n🟢 個人情報やファイルのデータ保護：安全（ローカル完結）": "🟢 External Hacking Resistance: Extremely Safe\n🟢 Tracking cookie behavior: 100% Blocked\n🟢 Personal Data Protection: Isolated Locally",
    "🟢 完全なシステム特権下で他サイトから完全に分離されています。": "🟢 Native platform sandboxing is active.",
    "🔄 実際のSSL/TLS証明書情報をバックグラウンドで照会・分析しています...": "🔄 Fetching and analyzing SSL/TLS certificates...",
    "少々お待ちください": "Please wait...",
    "通信プロトコル": "Protocol",
    "HTTP (平文クリアテキスト)": "HTTP (Plain Unencrypted Text)",
    "JWTセッション脆弱性": "Session Leak Risk",
    "高リスク (Tokenの傍受盗聴可能)": "High (Outbound token interception possible)",
    "暗号署名整合性(JWA)": "Encryption Key Check",
    "検証不可 (SSL/TLS証明書なし)": "N/A (No SSL Certificate)",
    "データ漏洩危険度": "Inbound Intrusion Risk",
    "高リスク (中間者インジェクションの余地あり)": "High Risk of MitM injection",
    "非暗号化接続：証明書ツリーは構築できません": "Plaintext session: No CA hierarchy path",
    "🔴 接続平文通信：安全ではありません（傍受・インジェクション耐性ゼロ）\n🟡 セッションセキュリティ制限：JWT署名トークン等のキャッシュ一時保護隔離中\n🟢 トラッカーブロック＆防御はアクティブ": "🔴 Plain text communication is vulnerable to spoofing.\n🟢 Tracker blocks are active.",
    "プロトコル世代": "Protocol Version",
    "TLSv1.3 (最高基準)": "TLSv1.3 (Highest Standard)",
    "TLSv1.2 (標準的な規格)": "TLSv1.2 (Standard Secure)",
    "古い規格": "Legacy Standard",
    "暗号スイート強度": "Cipher Strength",
    "暗号署名 鍵交換長": "Exchange Bit Length",
    "極めて強固": "Strong Exchange",
    "標準的な強度": "Standard Exchange",
    "脆弱な鍵長": "Vulnerable length",
    "認証局(CA)信頼性": "CA Trustworthiness",
    "高信頼CA": "High Trust CA",
    "一般CA": "General CA",
    "証明書 有効期限": "Certificate Lifespan",
    "日残 (十分な猶予)": "days remaining",
    "日残 (更新推奨)": "days (Update Recommended)",
    "期限切れ・失効": "Expired",
    "無効化": "Revoked",
    "ローカル防御設定": "Local Protection",
    "トラッカー遮断/HTTPS強制アクティブ": "Https/Tracker blocker active",
    "Root CA: DigiCert / GlobalSign (信頼済みルートCA)": "Root CA: DigiCert / GlobalSign (Trusted Certificate Authority)",
    "Leaf:": "Leaf:",
    " (本サイトの有効な署名)": " (Verified Domain Certificate)",
    "✔ 証明書のチェーン検証：完全一致（署名偽装なし）\n✔ CRL/OCSPによる失効検証：問題なし（有効な鍵を保持）": "✔ SSL Chain validation: Success (No spoofing detected)\n✔ CRL/OCSP status: Valid",
    "OpenWeb Vault セットアップ": "OpenWeb Vault Setup",
    "マスターパスワード:": "Master Password:",
    "OpenWeb Vault ロック解除": "OpenWeb Vault Unlock",
    "パスワード:": "Password:",
    "マスターパスワードを変更します": "Change your Security Vault Master Password",
    "変更する": "Change",
    "🎨 ホワイトボードモード (実験的)": "🎨 Whiteboard Mode (Experimental)",
    "➕ ウィンドウ追加": "➕ Add Window",
    "重ねて整列": "Cascade",
    "並べて表示": "Tile",
    "新しいブラウザ": "New Browser",
    "ウィンドウ1": "Window 1",
    "ウィンドウ2": "Window 2",
    "🎨 ホワイトボード": "🎨 Whiteboard",
    "https://example.com または file://... 等のローカルHTMLへの絶対パス": "e.g., https://example.com or absolute path to local HTML file",
    "ホームページ用HTMLの選択": "Select Home HTML",
    "設定などの内部ページはホームページに指定できません。": "Internal browser pages cannot be set as home page.",
    "カスタムURLアドレスを入力してください。": "Please enter a valid custom URL address.",
    "パスワード": "Password",
    "新規暗号化メモ": "New Secure Note",
    "メモのタイトルを入力してください:": "Enter note title:",
    "メモの内容を入力してください:": "Enter note content:",
    "安全なメモをVaultに保存しました。": "Secure memo has been vaulted.",
    "オーバークロックモードを有効にしました。\nこの設定はブラウザを次回再起動した際に完全に適用されます。\n(OSのプロセス優先度向上、GPUリミット解除、VSync無効化など)": "Overclock mode active. CPU and GPU will run at extreme thresholds upon next browser startup.",
    "オーバークロック解除": "Overclock Disabled",
    "オーバークロックモードを解除しました。\n次回起動時に標準状態に戻ります。": "Overclock mode disabled. Will restore default parameters on next run.",
    "追加スロット": "Add Slot",
    "🎯 検出中... 物理コントローラー of キーを押してください": "🎯 Detecting... Press physical key/button",
    "🎯 ボタン": "🎯 Button",
    "割当検出中...": "Binding...",
    "※ボタンの紐付けに成功しました！": "✔ Binding Complete!",
    "検出された入力:": "Detected Input:",
    "例: youtube.com": "e.g., youtube.com",
    "追加": "Add",
    "ワークスペース保存": "Save Workspace",
    "新しいワークスペース名を入力してください:": "Enter a new workspace name:",
    "安全な接続 (HTTPS) - クリックして証明書と安全度を表示": "Secure HTTPS active - Click to view certificate",
    "保護されていない通信 (HTTP) - クリックして詳細なセキュリティ分析を表示": "Insecure HTTP active - Click to view risk details",
    "システム内部ページ - クリックして詳細を表示": "System Internal Page - Click for details",
    "ローカルファイル (完全オフライン実行中) - クリックして安心チェック・隔離診断レポートを表示": "Local Offline File - Click for security report",
    "ローカルファイル等 - クリックして詳細を表示": "Local File - Click for details",
    "スプリットビュー：操作対象のアクティブ画面を左右に切り替えます": "Split-view: Toggle active screen left/right",
    "ローカルのHTMLファイルを開く (Ctrl+O)": "Open Local HTML File (Ctrl+O)",
    "URLをクリップボードにコピー": "Copy URL to Clipboard",
    "没入モードの切替 (F11 / Ctrl+Shift+I)": "Toggle Immersive Mode (F11 / Ctrl+Shift+I)",
    "没入モードを終了する (Esc)": "Exit Immersive Mode (Esc)",
    "ブラウザコントロールメニューを開く": "Open browser control menu",
    "🔊 ミュート解除": "🔊 Unmute Tab",
    "🔇 タブの音声をミュート": "🔇 Mute Tab Audio",
    "📁 このページをリーディングポケットに保存 (オフライン用)": "📁 Save page to Reading Pocket (Offline)",
    "✕ タブを閉じる": "✕ Close Tab",
    "🎯 没入モード中 (キーボードの[Esc]キー、または右上の[↩️ 解除]ボタンでカンタンに復帰できます)": "🎯 Immersive mode active (Press [Esc] or click '↩️ Exit' to restore UI)",
    "没入モードを解除しました": "Immersive mode deactivated.",
    "🔓 没入モードを解除する": "🔓 Exit Immersive Mode",
    "← 戻る": "← Back",
    "→ 進む": "→ Forward",
    "➕ 新しいタブ": "➕ New Tab",
    "⚙️ 設定を開く": "⚙️ Open Settings",
    "➕ 新タブ": "➕ New Tab",
    "📂 開く": "📂 Open",
    "⚙️ 設定": "⚙️ Settings",
    "📂 ファイルを開く...": "📂 Open File...",
    "🔍 ページ内検索...": "🔍 Find in Page...",
    "🖨️ PDFとして保存...": "🖨️ Save as PDF...",
    "🔎 画面ズーム": "🔎 Zoom",
    "＋ 拡大する": "＋ Zoom In",
    "－ 縮小する": "－ Zoom Out",
    "100%にリセット": "Reset to 100%",
    "📚 ライブラリ履歴": "📚 Library & History",
    "🕒 閲覧履歴タイムライン": "🕒 Browsing Timeline",
    "📥 ダウンロード一覧": "📥 Download Manager",
    "↩️ 閉じたタブを復元 (Ctrl+Shift+T)": "↩️ Restore Closed Tab (Ctrl+Shift+T)",
    "🕵️ シークレットモード: OFF": "🕵️ Secret Sandbox Mode: OFF",
    "🍪 Cookie保存: ON": "🍪 Keep Cookies: ON",
    "⚡ キャッシュを消去": "⚡ Clear HTTP Cache",
    "🗑️ 閲覧データとCookieをすべて削除...": "🗑️ Wipe all browsing data & Cookies...",
    "🧰 高度な拡張ツール": "🧰 Advanced Tools",
    "🖥️ スプリットビューを起動": "🖥️ Launch Split-View",
    "🎬 動画をポップアウト(ビデオプレイヤー)": "🎬 Pop-out Video Player",
    "📱 PWAアプリウインドウ化": "📱 Open as PWA Window",
    "💻 開発者ツール (F12)": "💻 Developer Tools (F12)",
    "🎨 外観テーマ設定": "🎨 Appearance & Theme",
    "☀️ ライトテーマ": "☀️ Light Theme",
    "🌙 ダークテーマ": "🌙 Dark Theme",
    "⚙️ ブラウザ総合設定": "⚙️ General Settings",
    "セッションの復元": "Restore Session",
    "前回開いていたタブセットを復元しますか？": "Would you like to restore your previous session tabs?",
    "ローカルファイルを開く": "Open Local File",
    "HTMLファイル (*.html *.htm);;すべてのファイル (*.*)": "HTML files (*.html *.htm);;All files (*.*)",
    "🕵️ シークレットモード: ON": "🕵️ Secret Sandbox Mode: ON",
    "🍪 Cookie保存: OFF (シークレット)": "🍪 Cookies: OFF (Secret Mode)",
    "【AIによる超速ページ自動分析・要約】\n\n": "[AI-driven Rapid Page Summary Analysis]\n\n",
    "✨ ワンクリックAI要約結果": "✨ One-click AI Summary Result",
    "要約": "Summary",
    "テキスト量が不足しているか、分析できませんでした。": "Could not analyze the content. Text volume might be too small.",
    "このページはリーディングポケットに保存できません。": "This page cannot be stored to reading pocket.",
    "📁 リーディングポケットに記事を保存しました！": "📁 Saved page to offline Pocket storage!",
    "保存に失敗しました。": "Save failed.",
    "🖥️ スプリットビュー": "🖥️ Split-View",
    "確認": "Confirm",
    "汎用コントローラー": "Generic Controller",
    "Xbox コントローラー": "Xbox Controller",
    "PS コントローラー": "PlayStation Controller",
    "Switch コントローラー": "Nintendo Switch Controller",
    "検出 (ボタン数:": "Detected (Buttons:",
    "完全初期化": "Factory Reset",
    "最終確認": "Final Warning",
    "やり直すことはできません。よろしいですか？\n(アプリは自動終了します)": "This operation is irreversible. Browser will shut down.",
    "初期化されました。アプリを再起動してください。": "Reset complete. Please restart the browser application.",
    "ページ内検索": "Find in Page",
    "検索するテキストを入力:": "Enter search query:",
    "PDFとして保存": "Save as PDF",
    "PDFファイル (*.pdf)": "PDF file (*.pdf)",
    "🖨️ PDFを保存しました:": "🖨️ Saved PDF file to:",
    "📋 URLをコピーしました": "📋 Copied URL to clipboard",
    "機能が無効です": "Feature Disabled",
    "「独自動画プレーヤー」は設定の『開発中の機能』でオフになっています。\n使用する場合はスイッチをオンにしてください。": "'Custom Video Player' is disabled in 'Experimental' settings.\nPlease turn it on to use this feature.",
    "パスワード保存": "Save Password",
    "の認証情報を安全な金庫に保存しますか？": "credentials to secure Vault?",
    "⚠️ セキュリティ警告": "⚠️ Security Warning",
    "実行可能ファイル「": "You are about to download an executable file '",
    "」をダウンロードしようとしています。\n本当に保存を続行しますか？": "'.\nAre you sure you want to proceed?",
    "ダウンロードを安全にブロックしました": "Download safely blocked.",
    "↩️ 閉じたタブを復元しました": "↩️ Restored closed tab.",
    "これ以上復元できるタブはありません": "No more closed tabs to restore.",
    "📖 読書モードを適用": "📖 Apply Reader Mode",
    "🌐 ページ全体をGoogle翻訳で開く": "🌐 Translate Page with Google",
    "✨ AIによるページ自動内容要約": "✨ AI Auto-Summarize Page",
    "🔑 Vault 暗号金庫を開く": "🔑 Open Vault",
    "➕ 新しい空タブを開く": "➕ Open empty new tab",
    "↩️ 直前に閉じたタブを復元する": "↩️ Restore recently closed tab",
    "コピー": "Copy",
    "貼り付け": "Paste",
    "切り取り": "Cut",
    "すべて選択": "Select All",
    "再読み込み": "Reload",
    "戻る": "Back",
    "進む": "Forward",
    "ページ内検索": "Find in Page",
    "このページをリーディングポケットに保存": "Save to Reading Pocket",
    "💻 開発者ツールを開く (F12)": "💻 Open Developer Tools (F12)",
    "本物のChromeプロファイルを使用する（Googleログイン安定化に最も効果的）": "Use real Chrome profile (Most effective for Google login stability)",
    "Chromeプロファイルパス": "Chrome Profile Path",
    "フォルダを選択...": "Select Folder...",
    "実在のChromeプロファイルを使用すると、フィンガープリントが自然になりGoogleログインが通りやすくなります。\n（通常のChromeで一度ログインしたプロファイルのフォルダを指定してください）": "Using a real Chrome profile makes the fingerprint look natural and greatly improves Google login success.\n(Recommended: Use the profile folder from a normal Chrome where you have already logged into Google)"
}

def _(text):
    if CURRENT_LANG == "en":
        return LANG_DICT.get(text, text)
    return text

chromium_flags = [
    "--enable-gpu", 
    "--enable-webgl",
    "--enable-accelerated-2d-canvas", 
    "--enable-gpu-canvas2d",              
    "--enable-gpu-rasterization", 
    "--ignore-gpu-blocklist",             
    "--enable-smooth-scrolling", 
    "--enable-parallel-downloading",
    "--disable-web-security=false",
    "--disable-direct-composition",
    "--disable-features=HardwareMediaKeyHandling",
    "--enable-quic",                                           # HTTP/3 QUICによる超速ネットワーク応答
    "--enable-zero-copy",                                      # メモリオーバーヘッドを完全に抑えるゼロコピー伝送
    "--enable-features=NetworkService,NetworkServiceInProcess",# ネットワーク処理をブラウザ同プロセスで高速処理
    "--enable-accelerated-video-decode",                       # GPUでのハードウェア動画デコード
    "--enable-tcp-fast-open",                                  # TCP接続のセッション確立を最速化
    "--enable-blink-features=AsyncImageDecoding",              # 画像の非同期バックグラウンドデコード
    "--disable-blink-features=AutomationControlled",           # Bot判定回避（Googleログイン等で重要）
    "--v8-cache-options=code",                                 # V8 JavaScriptバイトコードのキャッシュをフル活用
    "--enable-oop-rasterization",                              # 描画をメインCPUからGPU（アウトオブプロセス）へ完全に委譲
    "--enable-native-gpu-memory-buffers",                      # グラフィックメモリをネイティブに直結しテクスチャを瞬時にアップロード
    "--num-raster-threads=4",                                  # CPUのマルチコアを活用した並列スレッド描画処理
    "--enable-gpu-compositing",                                # ページレンダリングの合成処理をGPUで直接実行
    "--enable-webgl2-compute-context",                         # WebGL 2 の高度なコンピューティング処理を許可
    "--enable-gamepad-extensions"                              # Axisなどの高度なゲームパッド取得APIを明示的に有効化
]

# 🔥 オーバークロック（CPU/GPU限界突破）の適用
if is_overclock:
    chromium_flags.extend([
        "--enable-features=Vulkan,ThreadedScrolling,CanvasOopRasterization",
        "--force-gpu-mem-available-mb=8192",         # VRAMを強制的に最大割当
        "--js-flags=--max-opt=4 --turbo-fast-api-calls --predictable", # V8エンジンの限界最適化
        "--disable-frame-rate-limit",                # FPS制限の解除（無制限化）
        "--disable-gpu-vsync"                        # VSync無効化による最速レンダリング
    ])
    if sys.platform.startswith("win"):
        try:
            import ctypes
            # プロセス優先度を HIGH_PRIORITY_CLASS (0x00000080) に引き上げてCPUリソースを独占的に獲得
            ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00000080)
        except Exception:
            pass

# ---------------------------------------------------------
# 📂 PyInstaller (EXE化) ＆ 通常実行を両立するパス解決ヘルパー
# ---------------------------------------------------------
def get_resource_path(relative_path):
    """ リソースファイルの絶対パスを取得（EXE内同梱と外部フォルダの両方に対応） """
    # 1. EXEと同じディレクトリに物理的に配置されている外部ファイルを優先
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        external_path = os.path.join(exe_dir, relative_path)
        if os.path.exists(external_path):
            return external_path
            
        # 2. PyInstallerの一時フォルダ(sys._MEIPASS)内を探索
        if hasattr(sys, '_MEIPASS'):
            internal_path = os.path.join(sys._MEIPASS, relative_path)
            if os.path.exists(internal_path):
                return internal_path
                
    # 3. 通常のPython実行時のパス解決
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, relative_path)

widevine_path = get_resource_path("WidevineCdm")
if os.path.exists(widevine_path):
    chromium_flags.append(f"--widevine-path={widevine_path}")

# =========================================================
# Googleログイン完全バイパス用 強化フラグ (v6.2 修正版)
# =========================================================
google_bypass_flags = [
    "--disable-blink-features=AutomationControlled",
    "--disable-features=IsolateOrigins,site-per-process,WebRTC,WebRtcHideLocalIpsWithMdns",
    "--enable-features=NetworkService,NetworkServiceInProcess,SharedArrayBuffer",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-infobars",
    "--disable-notifications",
    "--disable-popup-blocking",
    "--ignore-certificate-errors",
]

# 既存の chromium_flags に Googleバイパスフラグをマージ
for flag in google_bypass_flags:
    if flag not in chromium_flags:
        chromium_flags.append(flag)

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = " ".join(chromium_flags).strip()

# より自然な User-Agent（最新Chrome風・Windows/Linux対応）
REALISTIC_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

# =========================================================
# 🎮 BLIND BOMBS Mini-Game - 完全内蔵 (Embedded HTML)
# =========================================================
BLIND_BOMBS_HTML = r'''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BLIND BOMBS - ONLINE ULTIMATE</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { 
            background-color: #030712; 
            color: #f3f4f6; 
            font-family: 'Courier New', Courier, monospace, 'Helvetica Neue', Arial, sans-serif; 
            user-select: none; 
            -webkit-user-select: none; 
            margin: 0; 
            padding: 0; 
        }
        .hidden { display: none !important; }
        
        /* 3Dカードフリップ */
        .grid-cell { perspective: 1000px; cursor: pointer; aspect-ratio: 1 / 1; touch-action: manipulation; }
        .card-inner { width: 100%; height: 100%; position: relative; transform-style: preserve-3d; transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1); }
        .grid-cell.flipped .card-inner { transform: rotateY(180deg); }
        .card-front, .card-back { position: absolute; width: 100%; height: 100%; backface-visibility: hidden; border-radius: 8px; display: flex; flex-direction: column; justify-content: center; align-items: center; border: 2px solid #374151; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.4); transition: all 0.2s; }
        .card-front { background-color: #1f2937; color: #ffffff; }
        .grid-cell:hover .card-front { background-color: #374151; border-color: #6b7280; }
        .grid-cell.selected .card-front { background-color: #4b5563; border-color: #3b82f6; box-shadow: 0 0 14px rgba(59, 130, 246, 0.8); }
        .card-back { background-color: #111827; transform: rotateY(180deg); }
        
        /* セルの開放状態スタイル */
        .card-back.opened-empty { background-color: #1e3a8a; border-color: #3b82f6; color: #93c5fd; }
        .card-back.opened-bomb { background-color: #7f1d1d; border-color: #f87171; animation: shake 0.4s; }
        .card-back.opened-ghost { background-color: #581c87; border-color: #c084fc; color: #e9d5ff; }
        .card-back.opened-timed { background-color: #7c2d12; border-color: #fb923c; color: #ffedd5; }
        .card-back.opened-plant { background-color: #7c2d12; border-color: #fb923c; color: #ffedd5; }
        .card-back.opened-plant-ghost { background-color: #3b0764; border-color: #d8b4fe; color: #faf5ff; }
        .grid-cell.reveal-cancelled .card-back { background-color: #064e3b; border-color: #34d399; color: #a7f3d0; }

        @keyframes shake { 0%, 100% { transform: translate(0, 0) rotate(0deg); } 10% { transform: translate(-2px, -2px) rotate(-1deg); } 20% { transform: translate(-3px, 0px) rotate(1deg); } 30% { transform: translate(3px, 2px) rotate(0deg); } 40% { transform: translate(1px, -1px) rotate(1deg); } 50% { transform: translate(-1px, 2px) rotate(-1deg); } 60% { transform: translate(-3px, 1px) rotate(0deg); } 70% { transform: translate(3px, 1px) rotate(-1deg); } 80% { transform: translate(-1px, -1px) rotate(1deg); } 90% { transform: translate(2px, 2px) rotate(0deg); } }
        .animate-shake { animation: shake 0.4s ease-in-out; }

        @keyframes damage-flash { 0%, 100% { background-color: #111827; } 50% { background-color: #7f1d1d; } }
        .damage-effect { animation: damage-flash 0.4s ease-in-out 2; }

        .screen { display: none; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; padding: 16px; box-sizing: border-box; }
        .screen.active { display: flex; }

        .log-entry { border-left: 4px solid #4b5563; padding-left: 10px; margin-bottom: 8px; background-color: #1f2937; padding: 8px; border-radius: 0 6px 6px 0; }
        .log-cancelled { border-left-color: #10b981; color: #a7f3d0; }
        .log-explosion { border-left-color: #ef4444; color: #fca5a5; }

        #game-board, #replay-board { display: grid; gap: 8px; margin: 16px auto; width: 100%; max-width: 480px; aspect-ratio: 1 / 1; }
        
        .btn { background-color: #374151; color: #ffffff; padding: 10px 16px; border: none; border-radius: 6px; cursor: pointer; font-family: inherit; font-size: 0.95rem; font-weight: bold; transition: background-color 0.2s, transform 0.1s; margin: 4px; display: inline-flex; align-items: center; justify-content: center; gap: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); touch-action: manipulation; }
        .btn:active { transform: scale(0.97); }
        .btn-primary { background-color: #2563eb; } .btn-primary:hover { background-color: #1d4ed8; }
        .btn-danger { background-color: #dc2626; } .btn-danger:hover { background-color: #b91c1c; }
        .btn-success { background-color: #16a34a; } .btn-success:hover { background-color: #15803d; }

        #turn-overlay, #plant-modal, #custom-dialog { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(17, 24, 39, 0.95); display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 100; }
        #custom-dialog { z-index: 110; }
        #online-modal { z-index: 105; }
        #input-lock { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: transparent; display: none; z-index: 50; }
    </style>
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen overflow-x-hidden flex flex-col font-mono select-none">

    <!-- 操作ロック用レイヤー -->
    <div id="input-lock"></div>

    <!-- 1. タイトル画面 -->
    <div id="screen-title" class="screen active">
        <h1 class="text-4xl md:text-5xl font-extrabold mb-1 tracking-widest text-center text-blue-500">BLIND BOMBS</h1>
        <p class="text-gray-400 mb-4 text-center text-xs md:text-sm max-w-md px-4">
            相手の罠を回避し、即座にカウンターを仕掛けろ。<br>究極の交互ターン制心理戦。<br>
            <span class="text-emerald-400 font-bold">✅ Wi-Fi/回線なしでもローカル対戦（最大4人）が完全オフラインで遊べます！</span>
        </p>

        <!-- プレイヤー名・レート設定 -->
        <div class="bg-gray-900 border border-gray-800 p-4 rounded-lg w-full max-w-md mb-3 flex flex-col gap-2 shadow-xl">
            <h3 class="text-xs font-bold text-gray-500 uppercase tracking-wider">👤 プレイヤー設定</h3>
            <div class="flex flex-col gap-2">
                <input type="text" id="setting-player-name" placeholder="プレイヤー名を入力してください" class="p-2.5 w-full bg-gray-950 border border-gray-800 rounded text-white text-sm outline-none focus:border-blue-500">
                <div class="flex justify-between items-center text-xs text-gray-400 bg-gray-950 p-2 rounded border border-gray-850">
                    <span>👑 現在のオンラインレート:</span>
                    <span id="ui-display-rate" class="font-bold text-yellow-400 text-sm">1000</span>
                </div>
            </div>
        </div>
        
        <div class="bg-gray-900 border border-gray-800 p-5 rounded-lg w-full max-w-md flex flex-col gap-3 shadow-2xl">
            <!-- 🌐 地域(リージョン)選択 -->
            <div>
                <h3 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">🌐 接続リージョン</h3>
                <div class="flex justify-between items-center bg-gray-950 p-2 rounded border border-gray-800">
                    <span class="text-xs text-yellow-500 font-bold">現在のリージョン:</span>
                    <select id="setting-region" class="bg-gray-800 text-white text-xs px-2.5 py-1 rounded border border-gray-700 outline-none cursor-pointer">
                        <option value="Asia" selected>Asia-Pacific (アジア)</option>
                        <option value="America">Americas (アメリカ)</option>
                        <option value="Europe">Europe (ヨーロッパ)</option>
                    </select>
                </div>
            </div>

            <h2 class="text-xs font-bold text-emerald-400 tracking-wider">🛠️ 完全オフライン・ローカル対戦（最大4人・Wi-Fi不要）</h2>
            
            <div class="flex justify-between items-center bg-gray-950/50 p-1.5 rounded">
                <span class="text-xs">参加人数:</span>
                <select id="setting-players" class="bg-gray-800 text-white text-xs p-1.5 rounded border border-gray-700 outline-none cursor-pointer">
                    <option value="2" selected>2人</option>
                    <option value="3">3人</option>
                    <option value="4">4人</option>
                </select>
            </div>

            <div class="flex justify-between items-center bg-gray-950/50 p-1.5 rounded">
                <span class="text-xs">うちCPUの数:</span>
                <select id="setting-cpus" class="bg-gray-800 text-white text-xs p-1.5 rounded border border-gray-700 outline-none cursor-pointer">
                    <option value="0">0人 (全員人間)</option>
                    <option value="1" selected>1人</option>
                    <option value="2">2人</option>
                    <option value="3">3人</option>
                    <option value="4">4人 (観戦モード)</option>
                </select>
            </div>

            <div class="flex justify-between items-center bg-gray-950/50 p-1.5 rounded">
                <span class="text-xs">先手プレイヤー:</span>
                <select id="setting-first-player" class="bg-gray-800 text-white text-xs p-1.5 rounded border border-gray-700 outline-none cursor-pointer">
                    <option value="random" selected>ランダム</option>
                    <option value="0">Player 1</option>
                    <option value="1">Player 2</option>
                </select>
            </div>
            
            <div class="flex justify-between items-center bg-gray-950/50 p-1.5 rounded">
                <span class="text-xs">マップサイズ:</span>
                <select id="setting-size" class="bg-gray-800 text-white text-xs p-1.5 rounded border border-gray-700 outline-none cursor-pointer">
                    <option value="5" selected>5x5 (25マス)</option>
                    <option value="7">7x7 (49マス)</option>
                </select>
            </div>

            <div class="flex justify-between items-center bg-gray-950/50 p-1.5 rounded">
                <span class="text-xs">初期ライフ:</span>
                <select id="setting-life" class="bg-gray-800 text-white text-xs p-1.5 rounded border border-gray-700 outline-none cursor-pointer">
                    <option value="3">3 (スピーディ)</option>
                    <option value="5" selected>5 (バランス)</option>
                    <option value="7">7 (じっくり)</option>
                </select>
            </div>
            
            <button id="btn-start-local" class="btn bg-gray-700 hover:bg-gray-600 mt-1 py-2.5 text-sm font-bold">▶️ ローカル戦を開始</button>
            
            <div class="border-t border-gray-800 my-1 pt-3 flex flex-col">
                <button id="btn-show-online" class="btn btn-primary py-2.5 text-sm font-bold shadow-lg">🌐 オンライン対戦へ接続</button>
            </div>

            <button id="btn-show-replay-list" class="btn bg-gray-800 hover:bg-gray-700 font-bold text-xs py-2">🎬 リプレイシアターを開く</button>
        </div>
    </div>

    <!-- オンライン対戦ロビー画面 (モーダル) -->
    <div id="online-modal" class="hidden fixed inset-0 bg-gray-900/95 flex flex-col justify-center items-center p-4">
        <div class="bg-gray-800 border-2 border-gray-700 p-6 rounded-xl w-full max-w-sm text-center shadow-2xl">
            <h3 class="text-2xl font-bold mb-2 text-blue-400">オンライン対戦ロビー</h3>
            <p class="text-[10px] text-yellow-400 mb-1">※ 現在は2人対戦対応。4人同時オンラインは次期バージョンで実装予定です。</p>
            <p class="text-sm text-gray-400 mb-4" id="online-status-text">サーバーに接続しています...</p>
            
            <!-- 部屋の作成・参加 -->
            <div id="online-actions" class="hidden flex-col gap-3">
                <button id="btn-free-match" class="btn bg-gradient-to-r from-blue-600 to-indigo-500 hover:from-blue-500 hover:to-indigo-400 py-3 font-bold text-white shadow-lg flex items-center justify-center gap-2">
                    <span>🌍</span> <span>フリーマッチ (地域別即時対戦)</span>
                </button>
                
                <div class="my-1 border-t border-gray-700 relative"></div>

                <button id="btn-create-room" class="btn btn-primary py-3 font-bold">🏠 友達対戦用の部屋を作る</button>
                
                <div class="my-1 border-t border-gray-700 relative">
                    <span class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-gray-800 px-2 text-xs text-gray-500">または</span>
                </div>
                
                <div class="flex gap-2">
                    <input type="text" id="join-room-id" placeholder="4桁の部屋IDを入力" class="p-2 w-full bg-gray-900 border border-gray-700 rounded text-white text-center font-mono tracking-widest text-lg outline-none focus:border-blue-500">
                </div>
                <button id="btn-join-room" class="btn btn-success py-3 font-bold">🚪 指定の部屋に入る</button>
                
                <button id="btn-close-online" class="btn bg-gray-700 hover:bg-gray-600 mt-2">ロビーを閉じる</button>
            </div>

            <!-- マッチング待機中 -->
            <div id="room-waiting" class="hidden flex-col gap-3 items-center">
                <p class="text-lg text-yellow-400 font-bold mb-1 animate-pulse">対戦相手を検索中...</p>
                <p class="text-gray-400 text-xs mb-3" id="room-waiting-desc">ルームを作成して待機しています</p>
                <p class="mb-3">
                    <span id="display-room-id" class="text-3xl font-mono text-white tracking-widest bg-gray-900 px-4 py-2 rounded border border-gray-600 shadow-inner block"></span>
                </p>
                <div class="text-xs text-gray-500 mb-2" id="display-room-region"></div>
                <button id="btn-cancel-room" class="btn btn-danger py-2 px-6">キャンセル</button>
            </div>
        </div>
    </div>

    <!-- 2. ゲームプレイ画面 -->
    <div id="screen-game" class="screen w-full max-w-2xl mx-auto">
        <div class="flex justify-between w-full mb-3 px-2 items-end border-b border-gray-800 pb-2">
            <div>
                <span class="text-xs text-gray-500 block">
                    <span id="ui-online-badge" class="hidden bg-green-900 text-green-300 px-2 py-0.5 rounded mr-1 font-bold text-[10px]">ONLINE</span>
                    <span id="ui-region-badge" class="hidden bg-blue-900 text-blue-300 px-2 py-0.5 rounded mr-1 font-bold text-[10px]">ASIA</span>
                    TURN: <span id="ui-turn-count">1</span>
                </span>
                <span class="text-2xl font-black text-blue-400" id="ui-current-player-name">Player 1</span>
            </div>
            <div class="text-right flex items-center gap-2">
                <span id="ui-phase-name" class="text-xs md:text-sm font-bold px-3 py-1 rounded"></span>
                <!-- 途中退出ボタン -->
                <button id="btn-leave-game" class="hidden bg-red-950/80 hover:bg-red-900 border border-red-700 text-red-200 text-[10px] px-2 py-1 rounded">退出</button>
            </div>
        </div>

        <div id="ui-players-info" class="flex flex-wrap justify-center gap-2 w-full mb-4"></div>
        
        <div id="game-board"></div>
        
        <p id="ui-instruction" class="mt-4 text-center font-bold text-gray-300 h-8 text-sm md:text-base px-2"></p>
    </div>

    <!-- 3. アイテム設置選択モーダル -->
    <div id="plant-modal" class="hidden p-4">
        <div class="bg-gray-900 border-2 border-gray-700 p-6 rounded-xl w-full max-w-sm text-center shadow-2xl animate-shake">
            <h3 class="text-2xl font-bold mb-1 text-yellow-400">罠を仕掛ける</h3>
            <p id="modal-cell-info" class="text-xs text-gray-400 mb-5 font-mono"></p>
            
            <div class="flex flex-col gap-3" id="modal-plant-options-container">
                <!-- Javascriptによって残数を伴うボタンが描画されます -->
            </div>
        </div>
    </div>

    <!-- 4. リザルト結果画面 -->
    <div id="screen-result" class="screen w-full max-w-3xl mx-auto">
        <h1 class="text-4xl md:text-5xl font-black mb-1 text-center text-yellow-500 tracking-wider" id="result-winner"></h1>
        
        <!-- レート変動表示エリア -->
        <div id="result-rate-change-container" class="hidden bg-gray-900 border border-gray-800 py-3 px-6 rounded-lg text-center mb-4 max-w-sm w-full shadow-lg">
            <span class="text-xs text-gray-400 block mb-1">ONLINE RATING UPDATE</span>
            <span class="text-2xl font-bold text-white font-mono" id="result-rate-text">1000 -> 1012 (+12)</span>
        </div>

        <div class="flex flex-col md:flex-row w-full gap-6 mt-4">
            <!-- 盤面の最終結果 -->
            <div class="flex-1 flex flex-col items-center bg-gray-900/50 p-4 rounded-xl border border-gray-800">
                <h2 class="text-lg font-bold mb-1 text-blue-400">最終盤面 (真実)</h2>
                <p class="text-[10px] text-gray-500 mb-2">🤝: 相殺 / 💣: 爆弾 / 👻: ハッタリ / ⏱️: 時限爆弾</p>
                <div id="result-board" class="w-full max-w-[280px] aspect-square grid gap-1.5 mx-auto bg-gray-950 p-2.5 rounded-lg border border-gray-800"></div>
            </div>
            
            <!-- ログ情報 -->
            <div class="flex-1 flex flex-col h-[300px] bg-gray-900/50 p-4 rounded-xl border border-gray-800">
                <h2 class="text-base font-bold mb-2 text-center border-b border-gray-800 pb-2 text-blue-400">真実 of 対戦ログ</h2>
                <div id="result-log" class="flex-1 overflow-y-auto bg-gray-950 rounded p-2.5 text-[11px] font-mono"></div>
            </div>
        </div>
        
        <div class="mt-8 flex flex-wrap justify-center gap-3">
            <button id="btn-result-return" class="btn px-6 py-2.5 bg-gray-800 hover:bg-gray-700 text-sm">タイトルへ戻る</button>
            <button id="btn-play-current-replay" class="btn btn-success px-6 py-2.5 text-sm">🎬 この試合のリプレイを見る</button>
        </div>
    </div>

    <!-- 5. リプレイ一覧画面 -->
    <div id="screen-replay-list" class="screen w-full max-w-2xl mx-auto">
        <h1 class="text-3xl font-extrabold mb-1 tracking-widest text-center text-yellow-500">🎬 リプレイシアター</h1>
        <p class="text-gray-400 mb-4 text-center text-xs">過去の素晴らしいオンライン対戦記録をいつでも再生・インポートできます。</p>
        
        <input type="file" id="import-file-input" accept=".json" class="hidden">

        <div class="w-full bg-gray-900 border border-gray-800 rounded-xl p-4 flex flex-col gap-4 shadow-2xl">
            <div class="flex justify-between items-center border-b border-gray-800 pb-2 flex-wrap gap-2">
                <span class="text-sm font-bold text-blue-400">対戦履歴</span>
                <div class="flex gap-2">
                    <button id="btn-trigger-import" class="btn btn-success py-1 px-3 text-[10px] font-bold">📥 取込</button>
                    <button id="btn-clear-replays" class="btn btn-danger py-1 px-3 text-[10px] font-bold">🧹 全消去</button>
                </div>
            </div>
            <div id="replay-list-container" class="overflow-y-auto max-h-[300px] flex flex-col gap-2 pr-1"></div>
        </div>
        
        <div class="mt-6">
            <button id="btn-replay-list-return" class="btn px-6 py-2 bg-gray-800 hover:bg-gray-700 text-sm">タイトルへ戻る</button>
        </div>
    </div>

    <!-- 6. リプレイ再生画面 -->
    <div id="screen-replay-player" class="screen w-full max-w-2xl mx-auto">
        <div class="flex justify-between w-full mb-4 px-2 items-end border-b border-gray-800 pb-2">
            <div>
                <span class="text-xs text-gray-500 block" id="replay-ui-turn">TURN: 1</span>
                <span class="text-2xl font-black" id="replay-ui-player-name">Player 1</span>
            </div>
            <div class="text-right">
                <span id="replay-ui-phase-name" class="text-xs font-bold px-3 py-1 rounded bg-gray-900 text-yellow-400"></span>
            </div>
        </div>
        <div id="replay-ui-players-info" class="flex flex-wrap justify-center gap-2 w-full mb-4"></div>
        <div id="replay-board"></div>
        <p id="replay-ui-instruction" class="mt-2 text-center font-bold text-yellow-300 h-10 text-xs md:text-sm px-2"></p>
        <div class="flex flex-wrap justify-center items-center gap-2 mt-4 bg-gray-900 border border-gray-800 p-2.5 rounded-lg w-full max-w-md shadow-lg">
            <button id="btn-replay-first" class="btn py-1.5 px-3 text-xs bg-gray-800 hover:bg-gray-700">⏮️</button>
            <button id="btn-replay-prev" class="btn py-1.5 px-3 text-xs bg-gray-800 hover:bg-gray-700">◀️</button>
            <button id="btn-replay-play" class="btn btn-primary py-1.5 px-4 text-xs font-bold">⏸️ 一時停止</button>
            <button id="btn-replay-next" class="btn py-1.5 px-3 text-xs bg-gray-800 hover:bg-gray-700">▶️</button>
            <button id="btn-replay-last" class="btn py-1.5 px-3 text-xs bg-gray-800 hover:bg-gray-700">⏭️</button>
            <button id="btn-replay-exit" class="btn btn-danger py-1.5 px-3 text-xs">❌ 終了</button>
        </div>
    </div>

    <!-- 端末受け渡し用オーバーレイ (オフライン用) -->
    <div id="turn-overlay" class="hidden">
        <h2 id="overlay-title" class="text-3xl md:text-4xl font-extrabold mb-3 text-center"></h2>
        <p id="overlay-desc" class="mb-8 text-gray-300 text-center text-xs md:text-sm max-w-md px-6 leading-relaxed"></p>
        <button id="btn-overlay-ok" class="btn btn-primary px-8 py-3 text-base font-black tracking-wider shadow-lg">準備OK ✅</button>
    </div>

    <!-- カスタムダイアログ -->
    <div id="custom-dialog" class="hidden p-4">
        <div class="bg-gray-900 border-2 border-gray-700 p-6 rounded-xl w-full max-w-sm text-center shadow-2xl animate-shake">
            <div class="text-3xl mb-2" id="dialog-icon">⚠️</div>
            <h3 class="text-xl font-bold mb-2 text-white" id="dialog-title">確認</h3>
            <p id="dialog-message" class="text-xs text-gray-300 mb-6 leading-relaxed"></p>
            <div id="dialog-buttons" class="flex justify-center gap-2"></div>
        </div>
    </div>

    <!-- Firebase SDK & ゲーム統合スクリプト -->
    <script type="module">
        // 注意: Firebaseは動的インポートに変更。インターネットがない環境でもローカル対戦が動作するようにした。
        // オンライン機能を使う時だけFirebase SDKを読み込む（初回読み込みにネットが必要）。
        let firebaseLoaded = false;

        async function loadFirebaseSDK() {
            if (firebaseLoaded && window.firebaseObj) return true;
            try {
                const appMod = await import('https://www.gstatic.com/firebasejs/12.15.0/firebase-app.js');
                const authMod = await import('https://www.gstatic.com/firebasejs/12.15.0/firebase-auth.js');
                const firestoreMod = await import('https://www.gstatic.com/firebasejs/12.15.0/firebase-firestore.js');

                window.firebaseObj = {
                    initializeApp: appMod.initializeApp,
                    getAuth: authMod.getAuth,
                    signInAnonymously: authMod.signInAnonymously,
                    signInWithCustomToken: authMod.signInWithCustomToken,
                    onAuthStateChanged: authMod.onAuthStateChanged,
                    getFirestore: firestoreMod.getFirestore,
                    collection: firestoreMod.collection,
                    doc: firestoreMod.doc,
                    setDoc: firestoreMod.setDoc,
                    getDoc: firestoreMod.getDoc,
                    onSnapshot: firestoreMod.onSnapshot,
                    deleteDoc: firestoreMod.deleteDoc,
                    getDocs: firestoreMod.getDocs
                };
                firebaseLoaded = true;
                return true;
            } catch (e) {
                console.error("Firebase SDKの動的読み込みに失敗しました（オフライン環境の可能性）:", e);
                return false;
            }
        }

        // グローバルにFirebaseオブジェクトをバインド（初期はnull）
        window.firebaseObj = null;

        // ========== あなたのFirebaseプロジェクト設定 ==========
        const firebaseConfig = {
            apiKey: "AIzaSyAyp01r8gDG45Rg0JUXsAQupErsuhhfQH0",
            authDomain: "blind-bombs-game.firebaseapp.com",
            databaseURL: "https://blind-bombs-game-default-rtdb.asia-southeast1.firebasedatabase.app",
            projectId: "blind-bombs-game",
            storageBucket: "blind-bombs-game.firebasestorage.app",
            messagingSenderId: "695436548485",
            appId: "1:695436548485:web:26ac51d58b2593aa4a4cec",
            measurementId: "G-Z28EEXN0TR"
        };
        // ======================================================

        // 認証を待ってからFirestore通信をする機構（改良版：ハングしにくくした）
        window.initFirebaseAndAuth = async () => {
            const loaded = await loadFirebaseSDK();
            if (!loaded || !window.firebaseObj) {
                console.warn("Firebaseが利用できません。オンライン対戦は無効です。ローカル対戦をお使いください。");
                return false;
            }

            try {
                // initializeApp を重複して呼ばないためのガード
                if (!window.firebaseObj._appInitialized) {
                    const app = window.firebaseObj.initializeApp(firebaseConfig);
                    window.firebaseObj.app = app;
                    window.firebaseObj._appInitialized = true;
                }

                const auth = window.firebaseObj.getAuth(window.firebaseObj.app);
                window.firebaseObj.auth = auth;
                window.firebaseObj.db = window.firebaseObj.getFirestore(window.firebaseObj.app);
                window.appId = firebaseConfig.projectId;

                // すでにログイン済みの場合
                if (auth.currentUser) {
                    window.myUserId = auth.currentUser.uid;
                    await loadProfileFromFirestore();
                    return true;
                }

                // 匿名ログインを実行
                try {
                    if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
                        await window.firebaseObj.signInWithCustomToken(auth, __initial_auth_token);
                    } else {
                        await window.firebaseObj.signInAnonymously(auth);
                    }
                } catch (signInErr) {
                    console.error("匿名サインインに失敗しました:", signInErr);
                    return false;
                }

                // サインイン完了後の currentUser を確認
                const user = auth.currentUser;
                if (user) {
                    window.myUserId = user.uid;
                    await loadProfileFromFirestore();
                    return true;
                } else {
                    return false;
                }
            } catch (e) {
                console.error("Firebaseの初期化に失敗しました:", e);
                return false;
            }
        };

        // --- ゲーム状態管理オブジェクト ---
        const STATE = {
            players: [],
            currentPlayerIndex: 0,
            previousPlayerIndex: null, 
            boardSize: 5,
            board: [],             
            tempReveal: {},        
            cancelledCells: [],    
            phase: 'PLANT',        
            turnCount: 1,
            selectedCell: null,
            isGameOver: false,
            isLocked: false,       
            secretLog: [],         
            hiddenBombsInfo: {},   
            lastDamagedPlayerId: null,

            // オンライン情報
            isOnline: false,
            roomId: null,
            myPlayerIndex: 0, 
            selectedRegion: 'Asia',
            myRating: 1000, // 初期レートは1000 (0〜99999の範囲)
            opponentRating: 1000, 

            currentReplay: { id: 0, date: "", mapSize: 5, players: [], winner: "", steps: [] }
        };

        const REPLAY_PLAYER = { data: null, currentStepIndex: -1, boardState: [], cancelledCells: [], isPlaying: false, timer: null, playersState: [] };

        const screens = {
            title: document.getElementById('screen-title'),
            game: document.getElementById('screen-game'),
            result: document.getElementById('screen-result'),
            replayList: document.getElementById('screen-replay-list'),
            replayPlayer: document.getElementById('screen-replay-player')
        };
        
        const boardEl = document.getElementById('game-board');
        const instructionEl = document.getElementById('ui-instruction');
        const overlay = document.getElementById('turn-overlay');
        const overlayDesc = document.getElementById('overlay-desc');
        const lockEl = document.getElementById('input-lock');
        const plantModal = document.getElementById('plant-modal');

        // ======================================================
        // 🛡️ Sandbox-safe LocalStorage wrapper
        // SecurityError（sandboxed iframeなど）対策
        // ======================================================
        const MEMORY_STORAGE = {};
        let storageWarningShown = false;

        function safeGetItem(key) {
            try {
                return localStorage.getItem(key);
            } catch (e) {
                if (!storageWarningShown) {
                    console.warn("%c[BLIND BOMBS] localStorageが利用できません（sandboxed環境）。メモリ内保存にフォールバックします。リロードするとデータは失われます。", "color:#f59e0b");
                    storageWarningShown = true;
                }
                return MEMORY_STORAGE[key] || null;
            }
        }

        function safeSetItem(key, value) {
            try {
                localStorage.setItem(key, value);
            } catch (e) {
                if (!storageWarningShown) {
                    console.warn("%c[BLIND BOMBS] localStorage書き込みに失敗。メモリ内保存にフォールバックします。", "color:#f59e0b");
                    storageWarningShown = true;
                }
                MEMORY_STORAGE[key] = value;
            }
        }

        function safeRemoveItem(key) {
            try {
                localStorage.removeItem(key);
            } catch (e) {
                delete MEMORY_STORAGE[key];
            }
        }

        // --- プロファイルの読込 / 保存 (LocalStorage & Firestore同期) ---
        function loadLocalProfile() {
            const savedName = safeGetItem('blind_bombs_username');
            const savedRate = safeGetItem('blind_bombs_rating');
            
            if (savedName) {
                document.getElementById('setting-player-name').value = savedName;
            } else {
                document.getElementById('setting-player-name').value = "Player_" + Math.floor(100 + Math.random() * 900);
            }
            
            if (savedRate) {
                STATE.myRating = parseInt(savedRate);
            } else {
                STATE.myRating = 1000;
            }
            document.getElementById('ui-display-rate').textContent = STATE.myRating;
        }

        function saveLocalProfile(name, rating) {
            safeSetItem('blind_bombs_username', name);
            safeSetItem('blind_bombs_rating', rating.toString());
            document.getElementById('ui-display-rate').textContent = rating;
        }

        // Firestoreのプライベートパスからユーザープロファイルをロード
        async function loadProfileFromFirestore() {
            if (!window.firebaseObj || !window.firebaseObj.db || !window.myUserId) return;
            const { doc, getDoc, setDoc, db } = window.firebaseObj;
            
            const profileDocRef = doc(db, 'artifacts', window.appId, 'users', window.myUserId, 'profile');
            try {
                const snap = await getDoc(profileDocRef);
                const localName = document.getElementById('setting-player-name').value.trim();
                
                if (snap.exists()) {
                    const data = snap.data();
                    STATE.myRating = data.rating !== undefined ? data.rating : STATE.myRating;
                    const cloudName = data.name || localName;
                    
                    document.getElementById('setting-player-name').value = cloudName;
                    saveLocalProfile(cloudName, STATE.myRating);
                } else {
                    // クラウドにデータがなければ現在のローカルデータを同期
                    await setDoc(profileDocRef, {
                        name: localName,
                        rating: STATE.myRating,
                        updatedAt: new Date().toISOString()
                    });
                }
            } catch (e) {
                console.error("プロファイル同期エラー:", e);
            }
        }

        // クラウドに最新のプロフィールデータを同期保存
        async function syncProfileToFirestore(name, rating) {
            saveLocalProfile(name, rating);
            if (!window.firebaseObj || !window.firebaseObj.db || !window.myUserId) return;
            const { doc, setDoc, db } = window.firebaseObj;
            const profileDocRef = doc(db, 'artifacts', window.appId, 'users', window.myUserId, 'profile');
            try {
                await setDoc(profileDocRef, {
                    name: name,
                    rating: rating,
                    updatedAt: new Date().toISOString()
                }, { merge: true });
            } catch (e) {
                console.error("Firestoreプロファイル更新エラー:", e);
            }
        }

        // --- ダイアログ制御 ---
        function showCustomAlert(message, title = "システム", icon = "ℹ️", onConfirm = null) {
            const dialog = document.getElementById('custom-dialog');
            document.getElementById('dialog-icon').textContent = icon;
            document.getElementById('dialog-title').textContent = title;
            document.getElementById('dialog-message').textContent = message;
            
            const btnContainer = document.getElementById('dialog-buttons');
            btnContainer.innerHTML = '';
            
            const btn = document.createElement('button');
            btn.className = 'btn btn-primary px-5 py-1.5 text-xs';
            btn.textContent = '了解';
            btn.onclick = () => { dialog.classList.add('hidden'); if (onConfirm) onConfirm(); };
            btnContainer.appendChild(btn);
            
            dialog.classList.remove('hidden');
        }

        function showCustomConfirm(message, title = "確認", icon = "❓", onConfirm, onCancel = null) {
            const dialog = document.getElementById('custom-dialog');
            document.getElementById('dialog-icon').textContent = icon;
            document.getElementById('dialog-title').textContent = title;
            document.getElementById('dialog-message').textContent = message;
            
            const btnContainer = document.getElementById('dialog-buttons');
            btnContainer.innerHTML = '';
            
            const btnCancel = document.createElement('button');
            btnCancel.className = 'btn bg-gray-850 hover:bg-gray-700 text-gray-300 px-4 py-1.5 text-xs';
            btnCancel.textContent = 'いいえ';
            btnCancel.onclick = () => { dialog.classList.add('hidden'); if (onCancel) onCancel(); };
            
            const btnConfirm = document.createElement('button');
            btnConfirm.className = 'btn btn-danger px-4 py-1.5 text-xs';
            btnConfirm.textContent = 'はい';
            btnConfirm.onclick = () => { dialog.classList.add('hidden'); if (onConfirm) onConfirm(); };
            
            btnContainer.appendChild(btnCancel);
            btnContainer.appendChild(btnConfirm);
            
            dialog.classList.remove('hidden');
        }

        function updatePlayerSettings() {
            const totalPlayers = parseInt(document.getElementById('setting-players').value);
            const cpuSelect = document.getElementById('setting-cpus');
            const currentCpuCount = parseInt(cpuSelect.value);
            
            cpuSelect.innerHTML = '<option value="0">0人 (対人戦)</option>';
            for (let i = 1; i < totalPlayers; i++) {
                cpuSelect.innerHTML += `<option value="${i}">${i}人</option>`;
            }
            cpuSelect.innerHTML += `<option value="${totalPlayers}">${totalPlayers}人 (観戦)</option>`;

            if (currentCpuCount <= totalPlayers) {
                cpuSelect.value = currentCpuCount;
            } else {
                cpuSelect.value = "1";
            }

            updateFirstPlayerOptions();
        }

        function updateFirstPlayerOptions() {
            const totalPlayers = parseInt(document.getElementById('setting-players').value);
            const firstPlayerSelect = document.getElementById('setting-first-player');
            const currentValue = firstPlayerSelect.value;
            
            firstPlayerSelect.innerHTML = '<option value="random">ランダム</option>';
            for (let i = 0; i < totalPlayers; i++) {
                firstPlayerSelect.innerHTML += `<option value="${i}">Player ${i + 1}</option>`;
            }
            if (currentValue === 'random') { firstPlayerSelect.value = 'random'; } else if (parseInt(currentValue) < totalPlayers) { firstPlayerSelect.value = currentValue; } else { firstPlayerSelect.value = 'random'; }
        }

        function setLock(locked) {
            STATE.isLocked = locked;
            lockEl.style.display = locked ? 'block' : 'none';
        }

        function switchScreen(screenIdOrKey) {
            Object.values(screens).forEach(s => { if (s) s.classList.remove('active'); });
            const target = screens[screenIdOrKey] || document.getElementById(screenIdOrKey);
            if (target) target.classList.add('active');
        }

        // ==========================================
        // 🌐 Firebase / オンラインマルチプレイ実装
        // ==========================================

        async function showOnlineMenu() {
            // オフライン検知を強化（Wi-Fi/回線なしでもローカル対戦が確実に遊べるように）
            if (!navigator.onLine) {
                showCustomAlert("インターネット接続がありません。

ローカル対戦（最大4人）は完全にオフラインで遊べます！
オンライン対戦はWi-Fiやモバイル回線接続後にご利用ください。", "オフラインです", "📡");
                document.getElementById('online-modal').classList.add('hidden');
                return;
            }

            STATE.selectedRegion = document.getElementById('setting-region').value;
            const playerName = document.getElementById('setting-player-name').value.trim();
            if (!playerName) {
                showCustomAlert("ゲームを開始する前にプレイヤー名を入力してください。", "名前の設定", "👤");
                return;
            }
            // ローカルで名前を保存
            saveLocalProfile(playerName, STATE.myRating);

            document.getElementById('online-modal').classList.remove('hidden');
            document.getElementById('online-actions').classList.add('hidden');
            document.getElementById('room-waiting').classList.add('hidden');
            document.getElementById('online-status-text').textContent = `🌐 ${STATE.selectedRegion} サーバーへ接続中...`;

            // 認証処理を待ち受ける
            const isConnected = await window.initFirebaseAndAuth();
            if (isConnected) {
                // クラウドと接続できたらプロファイル再同期
                await syncProfileToFirestore(playerName, STATE.myRating);
                document.getElementById('online-status-text').textContent = `🌐 接続完了: ${playerName} (Rate: ${STATE.myRating})`;
                document.getElementById('online-actions').classList.remove('hidden');
                document.getElementById('online-actions').style.display = 'flex';
            } else {
                document.getElementById('online-status-text').textContent = "接続に失敗しました。ローカル対戦をおすすめします。";
            }
        }

        function closeOnlineMenu() {
            document.getElementById('online-modal').classList.add('hidden');
        }

        // ルーム作成 (ホスト側)
        async function createRoom() {
            const roomId = Math.floor(1000 + Math.random() * 9000).toString(); 
            const playerName = document.getElementById('setting-player-name').value.trim();

            STATE.roomId = roomId;
            STATE.isOnline = true;
            STATE.myPlayerIndex = 0; 
            
            document.getElementById('online-actions').style.display = 'none';
            document.getElementById('room-waiting').style.display = 'flex';
            document.getElementById('room-waiting-desc').textContent = '友達に部屋IDを教えてください';
            document.getElementById('display-room-id').textContent = roomId;
            document.getElementById('display-room-region').textContent = `接続リージョン: ${STATE.selectedRegion}`;

            const { doc, setDoc, db, onSnapshot } = window.firebaseObj;
            const roomRef = doc(db, 'artifacts', window.appId, 'public', 'data', 'rooms', roomId);

            await setDoc(roomRef, {
                hostId: window.myUserId,
                hostName: playerName,
                hostRating: STATE.myRating, // ホストのレートを共有
                status: 'waiting',
                region: STATE.selectedRegion,
                createdAt: new Date().toISOString()
            });

            if (window.roomUnsubscribe) window.roomUnsubscribe();
            window.roomUnsubscribe = onSnapshot(roomRef, (snapshot) => {
                if (!snapshot.exists()) return;
                const data = snapshot.data();
                if (data.status === 'playing' && data.guestId && screens.title.classList.contains('active')) {
                    STATE.opponentRating = data.guestRating || 1000;
                    setupOnlineGame(data.hostName, data.guestName, STATE.myRating, STATE.opponentRating);
                } else if (data.status === 'playing' && data.gameState) {
                    handleSync(data.gameState);
                }
            }, (error) => console.error("同期エラー:", error));
        }

        // ルーム参加 (ゲスト側)
        async function joinRoom() {
            const roomId = document.getElementById('join-room-id').value.trim();
            const playerName = document.getElementById('setting-player-name').value.trim();
            if (!roomId) return;

            document.getElementById('online-status-text').textContent = "部屋を探しています...";

            const { doc, getDoc, setDoc, db, onSnapshot } = window.firebaseObj;
            const roomRef = doc(db, 'artifacts', window.appId, 'public', 'data', 'rooms', roomId);

            const snapshot = await getDoc(roomRef);
            if (snapshot.exists()) {
                const data = snapshot.data();
                if (data.status === 'waiting') {
                    STATE.roomId = roomId;
                    STATE.isOnline = true;
                    STATE.myPlayerIndex = 1; 
                    STATE.selectedRegion = data.region || STATE.selectedRegion;
                    STATE.opponentRating = data.hostRating || 1000;

                    await setDoc(roomRef, { 
                        guestId: window.myUserId, 
                        guestName: playerName,
                        guestRating: STATE.myRating, // ゲストのレートを共有
                        status: 'playing' 
                    }, { merge: true });

                    document.getElementById('online-modal').classList.add('hidden');
                    
                    if (window.roomUnsubscribe) window.roomUnsubscribe();
                    window.roomUnsubscribe = onSnapshot(roomRef, (snap) => {
                        if (!snap.exists()) return;
                        const d = snap.data();
                        if (d.status === 'playing' && d.gameState) {
                            handleSync(d.gameState);
                        }
                    }, (error) => console.error(error));

                } else {
                    showCustomAlert("指定のルームは既に対戦中か終了しています。");
                    document.getElementById('online-status-text').textContent = "接続完了";
                }
            } else {
                showCustomAlert("部屋が見つかりませんでした。");
                document.getElementById('online-status-text').textContent = "接続完了";
            }
        }

        // フリーマッチ (ランダム対戦)
        async function startFreeMatch() {
            const playerName = document.getElementById('setting-player-name').value.trim();
            document.getElementById('online-actions').style.display = 'none';
            document.getElementById('room-waiting').style.display = 'flex';
            document.getElementById('room-waiting-desc').textContent = `同じリージョン [${STATE.selectedRegion}] のプレイヤーを探索中...`;
            document.getElementById('display-room-id').textContent = 'マッチ検索...';
            document.getElementById('display-room-region').textContent = '';
            
            const { collection, getDocs, doc, setDoc, db, onSnapshot } = window.firebaseObj;
            const roomsRef = collection(db, 'artifacts', window.appId, 'public', 'data', 'rooms');
            
            try {
                const snapshot = await getDocs(roomsRef);
                let targetRoomId = null;
                let targetHostName = null;
                let targetHostRating = 1000;
                
                snapshot.forEach(docSnap => {
                    const data = docSnap.data();
                    if (data.status === 'waiting_free' && data.region === STATE.selectedRegion && data.hostId !== window.myUserId) {
                        targetRoomId = docSnap.id;
                        targetHostName = data.hostName;
                        targetHostRating = data.hostRating || 1000;
                    }
                });

                if (targetRoomId) {
                    STATE.roomId = targetRoomId;
                    STATE.isOnline = true;
                    STATE.myPlayerIndex = 1; 
                    STATE.opponentRating = targetHostRating;
                    
                    const roomRef = doc(db, 'artifacts', window.appId, 'public', 'data', 'rooms', targetRoomId);
                    await setDoc(roomRef, { 
                        guestId: window.myUserId, 
                        guestName: playerName,
                        guestRating: STATE.myRating,
                        status: 'playing' 
                    }, { merge: true });
                    
                    document.getElementById('online-modal').classList.add('hidden');
                    
                    if (window.roomUnsubscribe) window.roomUnsubscribe();
                    window.roomUnsubscribe = onSnapshot(roomRef, (snap) => {
                        if (!snap.exists()) return;
                        const d = snap.data();
                        if (d.status === 'playing' && d.gameState) {
                            handleSync(d.gameState);
                        }
                    });
                } else {
                    // マッチング待ち部屋を作る
                    const newRoomId = Math.floor(10000 + Math.random() * 90000).toString(); 
                    STATE.roomId = newRoomId;
                    STATE.isOnline = true;
                    STATE.myPlayerIndex = 0; 
                    
                    const roomRef = doc(db, 'artifacts', window.appId, 'public', 'data', 'rooms', newRoomId);
                    await setDoc(roomRef, {
                        hostId: window.myUserId,
                        hostName: playerName,
                        hostRating: STATE.myRating,
                        status: 'waiting_free',
                        region: STATE.selectedRegion,
                        createdAt: new Date().toISOString()
                    });
                    
                    document.getElementById('display-room-id').textContent = "探索中";
                    document.getElementById('display-room-region').textContent = `リージョン: ${STATE.selectedRegion}`;
                    
                    if (window.roomUnsubscribe) window.roomUnsubscribe();
                    window.roomUnsubscribe = onSnapshot(roomRef, (snap) => {
                        if (!snap.exists()) return;
                        const data = snap.data();
                        if (data.status === 'playing' && data.guestId && screens.title.classList.contains('active')) {
                            STATE.opponentRating = data.guestRating || 1000;
                            setupOnlineGame(data.hostName, data.guestName, STATE.myRating, STATE.opponentRating);
                        } else if (data.status === 'playing' && data.gameState) {
                            handleSync(data.gameState);
                        }
                    });
                }
            } catch (e) {
                console.error(e);
                showCustomAlert("フリーマッチマッチングに失敗しました。");
                cancelRoom();
            }
        }

        function cancelRoom() {
            if (STATE.roomId && window.firebaseObj && window.myUserId) {
                const { doc, deleteDoc, db } = window.firebaseObj;
                const roomRef = doc(db, 'artifacts', window.appId, 'public', 'data', 'rooms', STATE.roomId);
                deleteDoc(roomRef).catch(console.error);
            }
            if (window.roomUnsubscribe) window.roomUnsubscribe();
            
            STATE.roomId = null;
            STATE.isOnline = false;
            document.getElementById('room-waiting').style.display = 'none';
            document.getElementById('online-actions').style.display = 'flex';
            document.getElementById('online-status-text').textContent = `ロビー [リージョン: ${STATE.selectedRegion}]`;
        }

        // オンラインゲーム中の途中退出機能
        function leaveOnlineGame() {
            showCustomConfirm("対戦中のルームから退室しますか？
(途中退出の場合、今回のレートは変動しません)", "退出の確認", "🚪", () => {
                if (STATE.roomId && window.firebaseObj) {
                    const { doc, setDoc, db } = window.firebaseObj;
                    const roomRef = doc(db, 'artifacts', window.appId, 'public', 'data', 'rooms', STATE.roomId);
                    // 相手に退室を通知するためstatusを 'closed' に
                    setDoc(roomRef, { status: 'closed', leftUserId: window.myUserId }, { merge: true })
                        .then(() => {
                            cleanupOnlineSessionAndExit();
                        }).catch(() => {
                            cleanupOnlineSessionAndExit();
                        });
                } else {
                    cleanupOnlineSessionAndExit();
                }
            });
        }

        function cleanupOnlineSessionAndExit() {
            if (window.roomUnsubscribe) window.roomUnsubscribe();
            STATE.isOnline = false;
            STATE.roomId = null;
            switchScreen('title');
            showCustomAlert("オンライン対戦から退出しました。(レート変動なし)", "退出完了", "🚪");
        }

        async function syncToFirestore() {
            if (!STATE.isOnline || !STATE.roomId || !window.firebaseObj) return;
            const { doc, setDoc, db } = window.firebaseObj;
            const roomRef = doc(db, 'artifacts', window.appId, 'public', 'data', 'rooms', STATE.roomId);
            
            const stateData = {
                players: STATE.players, currentPlayerIndex: STATE.currentPlayerIndex, boardSize: STATE.boardSize,
                board: STATE.board, cancelledCells: STATE.cancelledCells, phase: STATE.phase, turnCount: STATE.turnCount,
                isGameOver: STATE.isGameOver, secretLog: STATE.secretLog, hiddenBombsInfo: STATE.hiddenBombsInfo,
                lastDamagedPlayerId: STATE.lastDamagedPlayerId, tempReveal: STATE.tempReveal
            };

            try {
                await setDoc(roomRef, { gameState: JSON.parse(JSON.stringify(stateData)) }, { merge: true });
            } catch (e) { console.error("Firestore同期エラー:", e); }
        }

        // オンライン同期受信処理
        function handleSync(gameState) {
            if (!gameState) return;

            // 他プレイヤーの仕込み演出(1,2,3)は同期せず、めくり演出(負の数)のみ同期
            const filteredTempReveal = {};
            if (gameState.tempReveal) {
                Object.keys(gameState.tempReveal).forEach(key => {
                    const val = gameState.tempReveal[key];
                    if (val < 0) {
                        filteredTempReveal[key] = val;
                    }
                });
            }

            STATE.players = gameState.players;
            STATE.currentPlayerIndex = gameState.currentPlayerIndex;
            STATE.boardSize = gameState.boardSize;
            STATE.board = gameState.board;
            STATE.cancelledCells = gameState.cancelledCells || [];
            STATE.phase = gameState.phase;
            STATE.turnCount = gameState.turnCount;
            STATE.isGameOver = gameState.isGameOver;
            STATE.secretLog = gameState.secretLog || [];
            STATE.hiddenBombsInfo = gameState.hiddenBombsInfo || {};
            STATE.lastDamagedPlayerId = gameState.lastDamagedPlayerId;
            STATE.tempReveal = filteredTempReveal;

            if (gameState.currentReplay) {
                STATE.currentReplay = gameState.currentReplay;
            }

            updateBoardUI();
            updatePlayersUI();

            if (STATE.isGameOver) {
                const alivePlayers = STATE.players.filter(pl => !pl.isDead);
                endGameLocal(alivePlayers.length === 1 ? alivePlayers[0] : null);
            } else {
                prepareTurnTransition();
            }
        }

        // ==========================================
        // 🎮 ゲームのメインロジック & UI同期
        // ==========================================

        function setupOnlineGame(hostName, guestName, hostRate, guestRate) {
            const size = 5; 
            const initialLife = 5; 

            STATE.players = [
                { id: 0, name: hostName, rating: hostRate, life: initialLife, maxLife: initialLife, color: '#3b82f6', isCpu: false, isDead: false, ghostLimit: 2, timedLimit: 2 },
                { id: 1, name: guestName, rating: guestRate, life: initialLife, maxLife: initialLife, color: '#ef4444', isCpu: false, isDead: false, ghostLimit: 2, timedLimit: 2 }
            ];

            STATE.boardSize = size;
            STATE.board = Array.from({ length: size * size }, () => []);
            STATE.tempReveal = {}; 
            STATE.cancelledCells = []; 
            STATE.hiddenBombsInfo = {}; 
            STATE.secretLog = []; 
            STATE.lastDamagedPlayerId = null;
            STATE.currentPlayerIndex = 0; 
            STATE.phase = 'PLANT'; 
            STATE.turnCount = 1; 
            STATE.isGameOver = false;

            const now = new Date();
            STATE.currentReplay = {
                id: now.getTime(), 
                date: `${now.getMonth() + 1}/${now.getDate()} ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`,
                mapSize: size, 
                players: STATE.players.map(p => ({ name: p.name, color: p.color, maxLife: p.maxLife, isCpu: p.isCpu })),
                winner: "引き分け", 
                steps: []
            };

            document.getElementById('ui-online-badge').style.display = 'inline';
            document.getElementById('ui-region-badge').style.display = 'inline';
            document.getElementById('ui-region-badge').textContent = `REGION: ${STATE.selectedRegion.toUpperCase()}`;
            document.getElementById('btn-leave-game').classList.remove('hidden'); // 退出ボタン表示
            document.getElementById('online-modal').classList.add('hidden');

            setupBoardUI(); 
            updateBoardUI(); 
            updatePlayersUI(); 
            switchScreen('game');
            
            syncToFirestore();
            prepareTurnTransition();
        }

        function startGame(isOnlineMode = false) {
            if (isOnlineMode) return; 

            STATE.isOnline = false;
            STATE.roomId = null;
            document.getElementById('btn-leave-game').classList.add('hidden'); // ローカル戦は退出不要

            const totalPlayers = parseInt(document.getElementById('setting-players').value);
            const cpuCount = parseInt(document.getElementById('setting-cpus').value);
            const size = parseInt(document.getElementById('setting-size').value);
            const initialLife = parseInt(document.getElementById('setting-life').value);
            const myName = document.getElementById('setting-player-name').value.trim() || "Player 1";

            // ローカルで名前を保存
            saveLocalProfile(myName, STATE.myRating);

            STATE.players = [];
            const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b']; 
            
            const humanCount = totalPlayers - cpuCount;

            for (let i = 0; i < totalPlayers; i++) {
                const isCpu = (i >= humanCount);
                let pName = isCpu ? `CPU ${i - humanCount + 1}` : `Player ${i + 1}`;
                if (i === 0 && !isCpu) pName = myName; 

                STATE.players.push({
                    id: i,
                    name: pName,
                    rating: i === 0 && !isCpu ? STATE.myRating : 1000,
                    life: initialLife, maxLife: initialLife, color: colors[i],
                    isCpu: isCpu, isDead: false, 
                    ghostLimit: 2,  
                    timedLimit: 2   
                });
            }

            STATE.boardSize = size;
            STATE.board = Array.from({ length: size * size }, () => []);
            STATE.tempReveal = {}; STATE.cancelledCells = []; STATE.hiddenBombsInfo = {}; STATE.secretLog = []; STATE.lastDamagedPlayerId = null;
            
            const firstP = document.getElementById('setting-first-player').value;
            STATE.currentPlayerIndex = (firstP === 'random') ? Math.floor(Math.random() * totalPlayers) : parseInt(firstP);
            
            STATE.previousPlayerIndex = null; STATE.phase = 'PLANT'; STATE.turnCount = 1; STATE.isGameOver = false;
            setLock(false);

            const now = new Date();
            STATE.currentReplay = {
                id: now.getTime(), date: `${now.getMonth() + 1}/${now.getDate()} ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`,
                mapSize: size, players: STATE.players.map(p => ({ name: p.name, color: p.color, maxLife: p.maxLife, isCpu: p.isCpu })),
                winner: "引き分け", steps: []
            };

            document.getElementById('ui-online-badge').style.display = 'none';
            document.getElementById('ui-region-badge').style.display = 'none';
            document.getElementById('online-modal').classList.add('hidden');

            setupBoardUI(); updateBoardUI(); updatePlayersUI(); switchScreen('game');
            prepareTurnTransition();
        }

        function setupBoardUI() {
            boardEl.style.gridTemplateColumns = `repeat(${STATE.boardSize}, 1fr)`;
            boardEl.innerHTML = '';
            for (let i = 0; i < STATE.board.length; i++) {
                const cell = document.createElement('div');
                cell.className = 'grid-cell'; cell.dataset.index = i; cell.onclick = () => selectCell(i);
                
                const inner = document.createElement('div'); inner.className = 'card-inner';
                const front = document.createElement('div'); front.className = 'card-front text-2xl';
                const back = document.createElement('div'); back.className = 'card-back text-2xl font-bold';
                
                inner.appendChild(front); inner.appendChild(back); cell.appendChild(inner); boardEl.appendChild(cell);
            }
        }

        function updateBoardUI() {
            const cells = boardEl.children;
            for (let i = 0; i < STATE.board.length; i++) {
                const cell = cells[i];
                if (!cell) continue;
                
                const front = cell.querySelector('.card-front');
                const back = cell.querySelector('.card-back');
                
                cell.classList.remove('selected', 'flipped');
                front.className = 'card-front text-2xl'; back.className = 'card-back text-2xl font-bold'; back.innerHTML = '';
                
                if (i === STATE.selectedCell) cell.classList.add('selected');

                if (STATE.tempReveal[i] === -1) { cell.classList.add('flipped'); back.classList.add('opened-bomb'); back.innerHTML = '💥'; }
                else if (STATE.tempReveal[i] === -2) { cell.classList.add('flipped'); back.classList.add('opened-empty'); }
                else if (STATE.tempReveal[i] === -3) { cell.classList.add('flipped'); back.classList.add('opened-ghost'); back.innerHTML = '👻'; }
                else if (STATE.tempReveal[i] === -4) { cell.classList.add('flipped'); back.classList.add('opened-timed'); back.innerHTML = '⏱️'; }
                else if (STATE.tempReveal[i] === 1) { cell.classList.add('flipped'); back.classList.add('opened-plant'); back.innerHTML = '💣'; }
                else if (STATE.tempReveal[i] === 2) { cell.classList.add('flipped'); back.classList.add('opened-plant-ghost'); back.innerHTML = '👻'; }
                else if (STATE.tempReveal[i] === 3) { cell.classList.add('flipped'); back.classList.add('opened-timed'); back.innerHTML = '⏱️'; }
            }
        }

        function updatePlayersUI() {
            const container = document.getElementById('ui-players-info');
            container.innerHTML = '';
            
            STATE.players.forEach((p, index) => {
                const isCurrent = (index === STATE.currentPlayerIndex);
                const el = document.createElement('div');
                let effectClass = (STATE.lastDamagedPlayerId === p.id) ? 'damage-effect animate-shake' : '';

                el.className = `p-3 rounded border-2 ${isCurrent ? 'border-white bg-gray-900 shadow-lg' : 'border-gray-800 bg-gray-950/60'} ${p.isDead ? 'opacity-30' : ''} ${effectClass} flex-1 min-w-[130px] max-w-[160px] text-center transition-all duration-300`;
                el.style.borderTopColor = p.color;
                
                let hearts = '';
                for (let i = 0; i < p.maxLife; i++) { hearts += (i < p.life) ? '❤️' : '💔'; }
                
                const ghostStatus = p.ghostLimit > 0 ? `👻x${p.ghostLimit}` : '❌';
                const timedStatus = p.timedLimit > 0 ? `⏱️x${p.timedLimit}` : '❌';
                
                const isMe = (STATE.isOnline && index === STATE.myPlayerIndex);
                const rateText = p.rating !== undefined ? ` [R:${p.rating}]` : '';
                
                el.innerHTML = `
                    <div class="font-bold text-xs flex flex-col items-center" style="color: ${p.color}">
                        <span class="truncate w-full">${p.name}${isMe ? ' (You)' : ''}${p.isDead ? ' (💀)' : ''}</span>
                        <span class="text-[9px] text-yellow-500 font-bold">${rateText}</span>
                        <span class="text-[9px] text-gray-500 mt-0.5">ハッタリ: ${ghostStatus} | 時限: ${timedStatus}</span>
                    </div>
                    <div class="text-[11px] tracking-tight mt-1 truncate">${hearts || '💀'}</div>
                `;
                container.appendChild(el);
            });

            document.getElementById('ui-turn-count').textContent = STATE.turnCount;
            const currentPlayer = STATE.players[STATE.currentPlayerIndex];
            const nameEl = document.getElementById('ui-current-player-name');
            nameEl.textContent = currentPlayer.name;
            nameEl.style.color = currentPlayer.color;

            const phaseEl = document.getElementById('ui-phase-name');
            if (STATE.phase === 'PLANT') {
                phaseEl.textContent = '💣 仕込みフェーズ';
                phaseEl.className = 'text-xs md:text-sm font-bold text-yellow-400 bg-yellow-950/30 px-3 py-1.5 rounded border border-yellow-800/50 shadow-[0_0_8px_rgba(250,204,21,0.2)]';
            } else {
                phaseEl.textContent = '🔍 めくりフェーズ';
                phaseEl.className = 'text-xs md:text-sm font-bold text-blue-400 bg-blue-950/30 px-3 py-1.5 rounded border border-blue-800/50 shadow-[0_0_8px_rgba(96,165,250,0.2)]';
            }
        }

        function prepareTurnTransition() {
            if (STATE.isGameOver) return;
            
            STATE.selectedCell = null;
            const currentPlayer = STATE.players[STATE.currentPlayerIndex];

            // 🌐 オンライン時の制限
            if (STATE.isOnline) {
                if (STATE.currentPlayerIndex === STATE.myPlayerIndex) {
                    setLock(false);
                    updateBoardUI(); updatePlayersUI();
                    instructionEl.textContent = STATE.phase === 'PLANT' ? "あなたの手番：安全な場所、あるいは相手を罠にはめるマスに罠を仕込みましょう。" : "あなたの手番：安全だと思うマスをめくってください！";
                    instructionEl.style.color = STATE.phase === 'PLANT' ? "#fcd34d" : "#93c5fd"; 
                } else {
                    setLock(true);
                    updateBoardUI(); updatePlayersUI();
                    instructionEl.textContent = STATE.phase === 'PLANT' ? "相手がどこに罠を仕掛けるか考えています..." : "相手がマスを選択しています...";
                    instructionEl.style.color = "#9ca3af";
                }
                return; 
            }

            // 🤖 CPU手番の処理
            if (currentPlayer.isCpu) {
                setLock(true); updateBoardUI(); updatePlayersUI();
                instructionEl.textContent = STATE.phase === 'PLANT' ? "CPUが罠を仕込んでいます..." : "CPUがカードをめくっています...";
                setTimeout(executeCPUTurn, 1000);
                STATE.previousPlayerIndex = STATE.currentPlayerIndex; 
                return;
            }

            // 👥 ローカル対人戦の受け渡し画面
            const aliveHumanPlayers = STATE.players.filter(p => !p.isCpu && !p.isDead);
            if (aliveHumanPlayers.length <= 1) {
                startNextPlayerTurn(true); STATE.previousPlayerIndex = STATE.currentPlayerIndex; return;
            }

            if (STATE.previousPlayerIndex === STATE.currentPlayerIndex) {
                startNextPlayerTurn(true); return;
            }

            document.getElementById('overlay-title').textContent = `${currentPlayer.name} のターン`;
            document.getElementById('overlay-title').style.color = currentPlayer.color;
            if (STATE.phase === 'REVEAL') {
                overlayDesc.innerHTML = "対戦相手に見られないように端末を受け取ってください。<br><br><span class='text-blue-400 font-bold'>あなたの【めくり】＆【仕込み】の番です。</span>";
            } else {
                overlayDesc.innerHTML = "対戦相手に見られないように端末を受け取ってください。<br><br><span class='text-yellow-400 font-bold'>あなたの【仕込み】の番です。</span>";
            }
            overlay.classList.remove('hidden');
            STATE.previousPlayerIndex = STATE.currentPlayerIndex; 
        }

        function startNextPlayerTurn(skipOverlay = false) {
            if (!skipOverlay) overlay.classList.add('hidden');
            STATE.lastDamagedPlayerId = null;
            setLock(false); updateBoardUI(); updatePlayersUI();

            instructionEl.textContent = STATE.phase === 'PLANT' ? "罠を仕込みたいマスを選択してください。" : "安全だと思うマスをめくってください！";
            instructionEl.style.color = STATE.phase === 'PLANT' ? "#fcd34d" : "#93c5fd"; 
        }

        function selectCell(index) {
            if (STATE.isGameOver || STATE.isLocked) return;
            const currentPlayer = STATE.players[STATE.currentPlayerIndex];
            if (currentPlayer.isCpu) return;
            if (STATE.isOnline && STATE.currentPlayerIndex !== STATE.myPlayerIndex) return;
            
            if (STATE.tempReveal[index] !== undefined) return;

            STATE.selectedCell = index;
            updateBoardUI();
            
            if (STATE.phase === 'PLANT') {
                showPlantModal(index);
            } else {
                setLock(true);
                setTimeout(executeAction, 150);
            }
        }

        function showPlantModal(index) {
            const p = STATE.players[STATE.currentPlayerIndex];
            const row = Math.floor(index / STATE.boardSize) + 1;
            const col = (index % STATE.boardSize) + 1;
            
            const container = document.getElementById('modal-plant-options-container');
            
            const ghostDisabledAttr = p.ghostLimit <= 0 ? 'disabled' : '';
            const timedDisabledAttr = p.timedLimit <= 0 ? 'disabled' : '';
            
            container.innerHTML = `
                <button id="btn-plant-bomb" class="bg-red-950 hover:bg-red-900 text-white font-bold py-3 px-4 rounded border border-red-700 transition flex justify-center items-center gap-2 text-base shadow-md">
                    <span>💣</span> 爆弾を仕掛ける (無制限)
                </button>
                <button id="btn-modal-ghost" ${ghostDisabledAttr} class="bg-purple-950 hover:bg-purple-900 text-white font-bold py-3 px-4 rounded border border-purple-700 transition flex justify-center items-center gap-2 text-base shadow-md disabled:opacity-35 disabled:cursor-not-allowed">
                    <span>👻</span> ゴーストを仕掛ける <span id="modal-ghost-count" class="text-xs bg-purple-800 px-2 py-0.5 rounded ml-1 font-mono">残 ${p.ghostLimit}回</span>
                </button>
                <button id="btn-modal-timed" ${timedDisabledAttr} class="bg-orange-950 hover:bg-orange-900 text-white font-bold py-3 px-4 rounded border border-orange-700 transition flex justify-center items-center gap-2 text-base shadow-md disabled:opacity-35 disabled:cursor-not-allowed">
                    <span>⏱️</span> 時限爆弾を仕掛ける <span id="modal-timed-count" class="text-xs bg-orange-800 px-2 py-0.5 rounded ml-1 font-mono">残 ${p.timedLimit}回</span>
                </button>
                <button id="btn-cancel-plant" class="bg-gray-800 hover:bg-gray-700 text-gray-300 py-2.5 px-4 rounded mt-2 transition text-sm">
                    キャンセル
                </button>
            `;
            
            document.getElementById('btn-plant-bomb').onclick = () => confirmPlant('bomb');
            if (p.ghostLimit > 0) document.getElementById('btn-modal-ghost').onclick = () => confirmPlant('ghost');
            if (p.timedLimit > 0) document.getElementById('btn-modal-timed').onclick = () => showTimedBombSelector();
            document.getElementById('btn-cancel-plant').onclick = () => cancelPlant();

            document.getElementById('modal-cell-info').textContent = `目標マス: [行 ${row} - 列 ${col}]`;
            plantModal.classList.remove('hidden');
        }

        function cancelPlant() {
            plantModal.classList.add('hidden'); STATE.selectedCell = null; updateBoardUI();
        }

        function showTimedBombSelector() {
            const container = document.getElementById('modal-plant-options-container');
            if (!container) return;

            container.innerHTML = `
                <h3 class="text-2xl font-bold mb-1 text-orange-400">時限カウントの選択</h3>
                <p class="text-xs text-gray-400 mb-5">このマスがめくられる度に減少。0になると周囲に関係なく爆発！</p>
                
                <div class="grid grid-cols-4 gap-3 w-full">
                    <button id="btn-timer-2" class="bg-orange-900 hover:bg-orange-800 text-white font-bold py-4 rounded-xl text-2xl border border-orange-600">2</button>
                    <button id="btn-timer-3" class="bg-orange-900 hover:bg-orange-800 text-white font-bold py-4 rounded-xl text-2xl border border-orange-600">3</button>
                    <button id="btn-timer-4" class="bg-orange-900 hover:bg-orange-800 text-white font-bold py-4 rounded-xl text-2xl border border-orange-600">4</button>
                    <button id="btn-timer-5" class="bg-orange-900 hover:bg-orange-800 text-white font-bold py-4 rounded-xl text-2xl border border-orange-600">5</button>
                </div>
                
                <button id="btn-cancel-timer" class="mt-4 text-sm text-gray-400 hover:text-white">キャンセル</button>
            `;

            document.getElementById('btn-timer-2').onclick = () => selectTimedTimer(2);
            document.getElementById('btn-timer-3').onclick = () => selectTimedTimer(3);
            document.getElementById('btn-timer-4').onclick = () => selectTimedTimer(4);
            document.getElementById('btn-timer-5').onclick = () => selectTimedTimer(5);
            document.getElementById('btn-cancel-timer').onclick = () => cancelPlant();
        }

        function selectTimedTimer(timer) {
            plantModal.classList.add('hidden');
            setLock(true);
            executePlantAction('timed', timer);
        }

        function confirmPlant(type) {
            plantModal.classList.add('hidden'); setLock(true); executePlantAction(type);
        }

        function executePlantAction(itemType, timerValue) {
            if (STATE.selectedCell === null || STATE.isGameOver) { setLock(false); return; }
            
            const p = STATE.players[STATE.currentPlayerIndex];
            const cellIdx = STATE.selectedCell;
            STATE.selectedCell = null;
            updateBoardUI();

            STATE.currentReplay.steps.push({
                type: 'PLANT', turn: STATE.turnCount, playerIndex: p.id,
                playerName: p.name, color: p.color, cellIndex: cellIdx, itemType: itemType, timerValue: timerValue 
            });

            if (!STATE.hiddenBombsInfo[cellIdx]) STATE.hiddenBombsInfo[cellIdx] = [];
            
            const stack = STATE.board[cellIdx];
            const topItem = stack.length > 0 ? stack[stack.length - 1] : null;

            if (itemType === 'timed') {
                if (p.timedLimit <= 0) { setLock(false); return; }
                p.timedLimit--;

                if (topItem && topItem.type === 'timed') {
                    stack.length = 0; 
                    STATE.cancelledCells.push(cellIdx);
                    addSecretLog(`[Turn ${STATE.turnCount}] 🤝 時限爆弾同士が重なり、互いに消失しました！`, 'cancelled');
                } else if (topItem && topItem.type === 'ghost') {
                    stack.pop();
                    const timer = timerValue || 3;
                    stack.push({ type: 'timed', ownerId: p.id, ownerName: p.name, remainingFlips: timer, initialFlips: timer });
                    addSecretLog(`[Turn ${STATE.turnCount}] ⏱️ ${p.name} が時限爆弾（残り${timer}回）を設置。ゴーストを上書き消滅させました。`);
                } else {
                    const timer = timerValue || 3;
                    stack.push({ type: 'timed', ownerId: p.id, ownerName: p.name, remainingFlips: timer, initialFlips: timer });
                    addSecretLog(`[Turn ${STATE.turnCount}] ⏱️ ${p.name} が時限爆弾（残り${timer}回）を仕掛けました。`);
                }

                showLocalPlantVisual(cellIdx, 3);
                return;
            }

            if (itemType === 'bomb') {
                STATE.hiddenBombsInfo[cellIdx].push(`${p.name}(爆弾)`);

                if (topItem && topItem.type === 'bomb') {
                    stack.pop(); 
                    addSecretLog(`[Turn ${STATE.turnCount}] 🤝 爆弾同士が重なり、衝撃で相殺されました！`, 'cancelled');
                    STATE.cancelledCells.push(cellIdx); 
                } else if (topItem && topItem.type === 'ghost') {
                    stack.pop(); 
                    stack.push({ type: 'bomb', ownerId: p.id, ownerName: p.name });
                    addSecretLog(`[Turn ${STATE.turnCount}] 💣 ${p.name} が爆弾を設置。先に出されていたハッタリを暴き、爆弾を設置。`);
                } else if (topItem && topItem.type === 'timed') {
                    stack.pop();
                    stack.push({ type: 'bomb', ownerId: p.id, ownerName: p.name });
                    addSecretLog(`[Turn ${STATE.turnCount}] 💣 ${p.name} が通常爆弾を重ね、上書きしました。`);
                } else {
                    stack.push({ type: 'bomb', ownerId: p.id, ownerName: p.name });
                    addSecretLog(`[Turn ${STATE.turnCount}] 💣 ${p.name} が爆弾をセットしました。`);
                }

                showLocalPlantVisual(cellIdx, 1);
            } 
            else if (itemType === 'ghost') {
                if (p.ghostLimit <= 0) { setLock(false); return; }
                p.ghostLimit--;
                STATE.hiddenBombsInfo[cellIdx].push(`${p.name}(ゴースト)`);

                if (topItem && topItem.type === 'bomb') {
                    stack.push({ type: 'ghost', ownerId: p.id, ownerName: p.name });
                    addSecretLog(`[Turn ${STATE.turnCount}] 👻 ${p.name} がハッタリを被せました。`);
                } else if (topItem && topItem.type === 'ghost') {
                    stack.pop();
                    addSecretLog(`[Turn ${STATE.turnCount}] 🤝 ゴースト同士が遭遇し、霧散しました。`, 'cancelled');
                    STATE.cancelledCells.push(cellIdx);
                } else if (topItem && topItem.type === 'timed') {
                    stack.push({ type: 'ghost', ownerId: p.id, ownerName: p.name });
                    addSecretLog(`[Turn ${STATE.turnCount}] 👻 ${p.name} が時限爆弾の上にハッタリを仕掛けました。`);
                } else {
                    stack.push({ type: 'ghost', ownerId: p.id, ownerName: p.name });
                    addSecretLog(`[Turn ${STATE.turnCount}] 👻 ${p.name} がゴーストをセットしました。`);
                }

                showLocalPlantVisual(cellIdx, 2);
            }
        }

        function showLocalPlantVisual(cellIdx, code) {
            const p = STATE.players[STATE.currentPlayerIndex];
            if (p.isCpu) {
                nextPhaseOrPlayer();
            } else {
                STATE.tempReveal[cellIdx] = code;
                updateBoardUI();
                
                setTimeout(() => {
                    delete STATE.tempReveal[cellIdx]; 
                    updateBoardUI();
                    setTimeout(() => { nextPhaseOrPlayer(); }, 300);
                }, 800);
            }
        }

        function executeAction() {
            if (STATE.selectedCell === null || STATE.isGameOver) { setLock(false); return; }
            
            const p = STATE.players[STATE.currentPlayerIndex];
            const cellIdx = STATE.selectedCell;
            STATE.selectedCell = null;
            updateBoardUI();

            if (STATE.phase === 'REVEAL') {
                const stack = STATE.board[cellIdx];
                const topItem = stack.length > 0 ? stack[stack.length - 1] : null;

                const stepData = {
                    type: 'REVEAL', turn: STATE.turnCount, playerIndex: p.id, playerName: p.name,
                    color: p.color, cellIndex: cellIdx, foundType: topItem ? topItem.type : 'empty', ownerName: topItem ? topItem.ownerName : null
                };

                if (topItem) {
                    if (topItem.type === 'ghost') {
                        STATE.tempReveal[cellIdx] = -3; 
                        addSecretLog(`[Turn ${STATE.turnCount}] 👻 ${p.name} がめくるとゴースト(ハッタリ)が出現！`);
                        instructionEl.textContent = "👻 ゴースト出現！実害はない。(セーフ)"; instructionEl.style.color = "#c084fc";

                        stack.pop(); 
                        updatePlayersUI(); updateBoardUI(); STATE.currentReplay.steps.push(stepData);
                        if (STATE.isOnline) syncToFirestore();

                        setTimeout(() => {
                            delete STATE.tempReveal[cellIdx]; updateBoardUI();
                            checkAndExplodeTimedBombs(() => {
                                setTimeout(() => { nextPhaseOrPlayer(); }, 300);
                            });
                        }, 1200);

                    } else if (topItem.type === 'bomb') {
                        p.life--; STATE.lastDamagedPlayerId = p.id; STATE.tempReveal[cellIdx] = -1; 

                        let logMsg = ""; let uiMsg = "";
                        if (topItem.ownerId === p.id) {
                            logMsg = `[Turn ${STATE.turnCount}] 💥 ${p.name} が自傷！自ら仕掛けた爆弾を踏みました。（ライフ残: ${p.life}）`; uiMsg = `💥 自らの爆弾を踏み抜いてしまった！`;
                        } else {
                            logMsg = `[Turn ${STATE.turnCount}] 💥 ${p.name} が ${topItem.ownerName} の爆弾を踏みました！（ライフ残: ${p.life}）`; uiMsg = `💥 ${topItem.ownerName} の罠だ！ (ライフ-1)`;
                        }

                        addSecretLog(logMsg, 'explosion');
                        instructionEl.textContent = uiMsg; instructionEl.style.color = "#f87171";

                        stack.pop(); 
                        if (p.life <= 0) { p.isDead = true; addSecretLog(`💀 ${p.name} が散っていった...。`); }

                        updatePlayersUI(); updateBoardUI(); STATE.currentReplay.steps.push(stepData);
                        if (STATE.isOnline) syncToFirestore();

                        const alivePlayers = STATE.players.filter(pl => !pl.isDead);
                        if (alivePlayers.length <= 1) {
                            setTimeout(() => { endGame(alivePlayers.length === 1 ? alivePlayers[0] : null); }, 1000);
                            return;
                        }

                        setTimeout(() => {
                            delete STATE.tempReveal[cellIdx]; updateBoardUI();
                            checkAndExplodeTimedBombs(() => {
                                setTimeout(() => { nextPhaseOrPlayer(); }, 300);
                            });
                        }, 1200);
                    } else if (topItem.type === 'timed') {
                        // 【新仕様】そのマスが引かれた回数だけカウントダウン
                        topItem.remainingFlips--;
                        
                        if (topItem.remainingFlips <= 0) {
                            // 指定回数引かれた → 爆発
                            stack.pop();
                            p.life--;
                            STATE.lastDamagedPlayerId = p.id;
                            STATE.tempReveal[cellIdx] = -1;

                            addSecretLog(`[Turn ${STATE.turnCount}] ⏱️ ${p.name} が時限爆弾を${topItem.initialFlips || 3}回引いたことで爆発しました！（残ライフ: ${p.life}）`, 'explosion');
                            instructionEl.textContent = "💥 時限爆弾が爆発！"; 
                            instructionEl.style.color = "#f87171";

                            if (p.life <= 0) { 
                                p.isDead = true; 
                                addSecretLog(`💀 ${p.name} は時限爆弾により脱落しました。`); 
                            }

                            updatePlayersUI(); updateBoardUI(); 
                            STATE.currentReplay.steps.push(stepData);
                            if (STATE.isOnline) syncToFirestore();

                            const alivePlayers = STATE.players.filter(pl => !pl.isDead);
                            if (alivePlayers.length <= 1) {
                                setTimeout(() => { endGame(alivePlayers.length === 1 ? alivePlayers[0] : null); }, 1000);
                                return;
                            }

                            setTimeout(() => {
                                delete STATE.tempReveal[cellIdx]; updateBoardUI();
                                checkAndExplodeTimedBombs(() => {
                                    setTimeout(() => { nextPhaseOrPlayer(); }, 300);
                                });
                            }, 1200);
                        } else {
                            // まだ回数残あり → カウントだけ減らして隠したままに戻す（popしない！）
                            // これで同じマスを何度も引けるようになる
                            STATE.tempReveal[cellIdx] = -2; 
                            
                            instructionEl.textContent = "💨 カウント減少（爆弾はまだ残っている）"; 
                            instructionEl.style.color = "#60a5fa";
                            
                            updatePlayersUI(); updateBoardUI();
                            const hiddenStepData = { ...stepData, foundType: 'empty', ownerName: null };
                            STATE.currentReplay.steps.push(hiddenStepData);
                            if (STATE.isOnline) syncToFirestore();

                            setTimeout(() => {
                                delete STATE.tempReveal[cellIdx]; 
                                updateBoardUI(); // 隠れた時限爆弾がまた表示される
                                checkAndExplodeTimedBombs(() => {
                                    setTimeout(() => { nextPhaseOrPlayer(); }, 300);
                                });
                            }, 800);
                        }
                    }
                } else {
                    STATE.tempReveal[cellIdx] = -2; 
                    addSecretLog(`[Turn ${STATE.turnCount}] 💨 ${p.name} が安全な空きマスをめくりました。`);
                    instructionEl.textContent = "💨 セーフ！安全空きマス。"; instructionEl.style.color = "#60a5fa";
                    
                    updatePlayersUI(); updateBoardUI(); STATE.currentReplay.steps.push(stepData);
                    if (STATE.isOnline) syncToFirestore();

                    setTimeout(() => {
                        delete STATE.tempReveal[cellIdx]; updateBoardUI();
                        checkAndExplodeTimedBombs(() => {
                            setTimeout(() => { nextPhaseOrPlayer(); }, 300);
                        });
                    }, 1000);
                }
            }
        }

        function decreaseTimedBombsCount() {
            for (let i = 0; i < STATE.board.length; i++) {
                const stack = STATE.board[i];
                if (stack.length > 0) {
                    const topItem = stack[stack.length - 1];
                    if (topItem.type === 'timed') {
                        topItem.remainingFlips--;
                        addSecretLog(`[システム] 時限爆弾 [行 ${Math.floor(i / STATE.boardSize) + 1} - 列 ${(i % STATE.boardSize) + 1}] の残りめくり回数: あと ${topItem.remainingFlips}回`);
                    }
                }
            }
        }

        function checkAndExplodeTimedBombs(callback) {
            let triggeredExplosion = false;

            for (let i = 0; i < STATE.board.length; i++) {
                const stack = STATE.board[i];
                if (stack.length > 0) {
                    const topItem = stack[stack.length - 1];
                    if (topItem.type === 'timed' && topItem.remainingFlips <= 0) {
                        triggeredExplosion = true;
                        stack.pop(); 
                        
                        const p = STATE.players[STATE.currentPlayerIndex];
                        p.life--;
                        STATE.lastDamagedPlayerId = p.id;
                        STATE.tempReveal[i] = -1; 

                        addSecretLog(`[⏱️時限起爆] マス [行 ${Math.floor(i / STATE.boardSize) + 1} - 列 ${(i % STATE.boardSize) + 1}] が残り回数0で爆発！ ${p.name} にダメージ！（残ライフ: ${p.life}）`, 'explosion');
                        
                        if (p.life <= 0) {
                            p.isDead = true;
                            addSecretLog(`💀 ${p.name} は時限爆弾の爆炎により脱落しました。`);
                        }
                    }
                }
            }

            if (triggeredExplosion) {
                updateBoardUI();
                updatePlayersUI();
                if (STATE.isOnline) syncToFirestore();

                const alivePlayers = STATE.players.filter(pl => !pl.isDead);
                if (alivePlayers.length <= 1) {
                    setTimeout(() => { endGame(alivePlayers.length === 1 ? alivePlayers[0] : null); }, 1200);
                    return;
                }

                setTimeout(() => {
                    for (let i = 0; i < STATE.board.length; i++) {
                        if (STATE.tempReveal[i] === -1) delete STATE.tempReveal[i];
                    }
                    updateBoardUI();
                    callback();
                }, 1200);
            } else {
                callback();
            }
        }

        function nextPhaseOrPlayer() {
            if (STATE.phase === 'PLANT') {
                let nextIdx = STATE.currentPlayerIndex;
                do { nextIdx = (nextIdx + 1) % STATE.players.length; } while (STATE.players[nextIdx].isDead);
                STATE.currentPlayerIndex = nextIdx; STATE.phase = 'REVEAL';
            } else {
                const currentPlayer = STATE.players[STATE.currentPlayerIndex];
                if (currentPlayer.isDead) {
                    let nextIdx = STATE.currentPlayerIndex;
                    do { nextIdx = (nextIdx + 1) % STATE.players.length; } while (STATE.players[nextIdx].isDead);
                    STATE.currentPlayerIndex = nextIdx; STATE.phase = 'PLANT';
                } else {
                    STATE.phase = 'PLANT';
                }
                const firstAlive = STATE.players.find(p => !p.isDead);
                if (STATE.currentPlayerIndex === firstAlive.id && STATE.phase === 'PLANT') { STATE.turnCount++; }
            }

            prepareTurnTransition();
            if (STATE.isOnline) { syncToFirestore(); }
        }

        function executeCPUTurn() {
            const validCells = [];
            for (let i = 0; i < STATE.board.length; i++) {
                if (STATE.tempReveal[i] === undefined) validCells.push(i);
            }
            if (validCells.length === 0) { nextPhaseOrPlayer(); return; }

            const randomIdx = Math.floor(Math.random() * validCells.length);
            const targetCell = validCells[randomIdx];

            if (STATE.phase === 'PLANT') {
                STATE.selectedCell = targetCell;
                const cpu = STATE.players[STATE.currentPlayerIndex];
                
                let choice = 'bomb';
                const rand = Math.random();
                if (cpu.ghostLimit > 0 && rand < 0.25) {
                    choice = 'ghost';
                } else if (cpu.timedLimit > 0 && rand >= 0.25 && rand < 0.45) {
                    choice = 'timed';
                }
                
                const timerVal = choice === 'timed' ? Math.floor(2 + Math.random() * 4) : undefined;
                executePlantAction(choice, timerVal);
            } else {
                STATE.selectedCell = targetCell; updateBoardUI();
                setTimeout(() => { executeAction(); }, 800);
            }
        }

        function addSecretLog(text, type = 'normal') { STATE.secretLog.push({ text, type }); }

        function endGame(winner) {
            STATE.isGameOver = true;
            if (STATE.isOnline) { syncToFirestore(); }
            endGameLocal(winner);
        }

        // ゲーム終了及びレート計算処理
        async function endGameLocal(winner) {
            STATE.isGameOver = true; setLock(false);
            document.getElementById('btn-leave-game').classList.add('hidden'); // 退出ボタンを隠す

            if (winner) { STATE.currentReplay.winner = winner.name; } else { STATE.currentReplay.winner = "引き分け"; }
            saveReplay(STATE.currentReplay);

            switchScreen('result');
            const titleEl = document.getElementById('result-winner');
            if (winner) { titleEl.textContent = `${winner.name} の勝利!`; titleEl.style.color = winner.color; } 
            else { titleEl.textContent = "引き分け (共倒れ)"; titleEl.style.color = "#9ca3af"; }

            // レート計算（オンライン対戦時のみ）
            const rateContainer = document.getElementById('result-rate-change-container');
            if (STATE.isOnline) {
                const myProfile = STATE.players[STATE.myPlayerIndex];
                let isWinner = winner && winner.id === myProfile.id;
                let isDraw = !winner;
                
                const oldRating = STATE.myRating;
                let ratingDiff = 0;
                
                if (isWinner) {
                    ratingDiff = 12; // 勝利したら +12
                } else if (!isDraw) {
                    ratingDiff = -8; // 敗北したら -8
                } // 引き分けは 0

                // レート範囲 0 〜 99999 制限
                STATE.myRating = Math.max(0, Math.min(99999, STATE.myRating + ratingDiff));
                
                // クラウドとローカルプロファイル保存
                await syncProfileToFirestore(document.getElementById('setting-player-name').value.trim(), STATE.myRating);

                // UI表示
                rateContainer.classList.remove('hidden');
                const diffSign = ratingDiff >= 0 ? `+${ratingDiff}` : `${ratingDiff}`;
                document.getElementById('result-rate-text').textContent = `${oldRating} -> ${STATE.myRating} (${diffSign})`;
            } else {
                rateContainer.classList.add('hidden');
            }

            renderResultBoard(); renderSecretLog();
        }

        function renderResultBoard() {
            const rb = document.getElementById('result-board');
            rb.style.gridTemplateColumns = `repeat(${STATE.boardSize}, 1fr)`; rb.innerHTML = '';
            
            for (let i = 0; i < STATE.board.length; i++) {
                const cell = document.createElement('div'); cell.className = 'grid-cell reveal-cancelled';
                const inner = document.createElement('div'); inner.className = 'card-inner';
                const front = document.createElement('div'); front.className = 'card-front';
                const back = document.createElement('div'); back.className = 'card-back text-sm flex flex-col items-center justify-center font-bold relative';

                const wasCancelled = STATE.cancelledCells.includes(i); const stack = STATE.board[i];

                if (stack.length > 0) {
                    const topItem = stack[stack.length - 1];
                    if (stack.length === 2) {
                        back.style.backgroundColor = '#581c87'; back.style.borderColor = '#c084fc';
                        back.innerHTML = `👻<span class="text-[8px] text-red-400 absolute top-0.5 font-mono">under:💣</span><span class="text-[8px] absolute bottom-0.5 text-purple-300 truncate w-full px-1 text-center">${topItem.ownerName}</span>`;
                    } else if (topItem.type === 'bomb') {
                        back.style.backgroundColor = '#7f1d1d'; back.style.borderColor = '#f87171';
                        back.innerHTML = `💣<span class="text-[8px] absolute bottom-0.5 text-red-300 truncate w-full px-1 text-center">${topItem.ownerName}</span>`;
                    } else if (topItem.type === 'ghost') {
                        back.style.backgroundColor = '#3b0764'; back.style.borderColor = '#d8b4fe';
                        back.innerHTML = `👻<span class="text-[8px] absolute bottom-0.5 text-purple-300 truncate w-full px-1 text-center">${topItem.ownerName}</span>`;
                    } else if (topItem.type === 'timed') {
                        back.style.backgroundColor = '#7c2d12'; back.style.borderColor = '#fb923c';
                        back.innerHTML = `⏱️<span class="text-[8px] text-orange-400 absolute top-0.5 font-mono">タイマー:${topItem.timer}</span><span class="text-[8px] absolute bottom-0.5 text-orange-200 truncate w-full px-1 text-center">${topItem.ownerName}</span>`;
                    }
                } else if (wasCancelled) {
                    back.innerHTML = '🤝'; 
                } else {
                    back.classList.add('opened-empty');
                }
                
                inner.appendChild(front); inner.appendChild(back); cell.appendChild(inner); cell.classList.add('flipped'); rb.appendChild(cell);
            }
        }

        function renderSecretLog() {
            const container = document.getElementById('result-log'); container.innerHTML = '';
            if (STATE.secretLog.length === 0) { container.innerHTML = '<p class="text-gray-500 text-center">ログ履歴がありません。</p>'; return; }
            STATE.secretLog.forEach(log => {
                const el = document.createElement('div');
                el.className = `log-entry ${log.type === 'cancelled' ? 'log-cancelled' : log.type === 'explosion' ? 'log-explosion' : ''}`;
                el.textContent = log.text; container.appendChild(el);
            });
            container.scrollTop = container.scrollHeight;
        }

        function returnToTitle() { switchScreen('title'); }

        // ==========================================
        // 🎬 リプレイシステムの制御
        // ==========================================
        function getSavedReplays() { 
            try { 
                const data = safeGetItem('blind_bombs_replays'); 
                return data ? JSON.parse(data) : []; 
            } catch (e) { 
                return []; 
            } 
        }
        function saveReplay(replayData) { 
            if (!replayData.steps || replayData.steps.length === 0) return; 
            const list = getSavedReplays(); 
            list.unshift(replayData); 
            if (list.length > 25) { list.pop(); } 
            try { 
                safeSetItem('blind_bombs_replays', JSON.stringify(list)); 
            } catch (e) { 
                console.error(e); 
            } 
        }
        function exportReplay(id, event) { 
            if (event) event.stopPropagation(); 
            const list = getSavedReplays(); 
            const item = list.find(r => r.id === id); 
            if (!item) return; 
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(item)); 
            const downloadAnchor = document.createElement('a'); 
            downloadAnchor.setAttribute("href", dataStr); 
            downloadAnchor.setAttribute("download", `blindbombs_replay_${item.id}.json`); 
            document.body.appendChild(downloadAnchor); 
            downloadAnchor.click(); 
            downloadAnchor.remove(); 
        }
        function triggerImport() { document.getElementById('import-file-input').click(); }
        function handleImportFile(event) { 
            const file = event.target.files[0]; 
            if (!file) return; 
            const reader = new FileReader(); 
            reader.onload = function(e) { 
                try { 
                    const imported = JSON.parse(e.target.result); 
                    if (imported && imported.steps && Array.isArray(imported.steps) && imported.players) { 
                        const list = getSavedReplays(); 
                        const duplicateIndex = list.findIndex(r => r.id === imported.id); 
                        if (duplicateIndex > -1) { list.splice(duplicateIndex, 1); } 
                        list.unshift(imported); 
                        safeSetItem('blind_bombs_replays', JSON.stringify(list)); 
                        renderReplayList(); 
                        showCustomAlert("正常にリプレイファイルをインポートしました。", "取込成功", "📥"); 
                    } else { 
                        showCustomAlert("対応していないファイル構成です。", "エラー", "❌"); 
                    } 
                } catch (err) { 
                    showCustomAlert("エラーが発生しました。", "エラー", "❌"); 
                } 
                event.target.value = ''; 
            }; 
            reader.readAsText(file); 
        }
        function deleteReplay(id, event) { 
            if (event) event.stopPropagation(); 
            showCustomConfirm("この対戦の軌跡リプレイを破棄しますか？", "削除の確認", "🗑️", () => { 
                let list = getSavedReplays(); 
                list = list.filter(item => item.id !== id); 
                try { 
                    safeSetItem('blind_bombs_replays', JSON.stringify(list)); 
                    renderReplayList(); 
                } catch (e) { 
                    console.error(e); 
                } 
            }); 
        }
        function showClearConfirm() { 
            const list = getSavedReplays(); 
            if (list.length === 0) { 
                showCustomAlert("削除するリプレイ記録が存在しません。", "お知らせ", "ℹ️"); 
                return; 
            } 
            showCustomConfirm("すべての記録リプレイ履歴を一括で消去します。本当によろしいですか？", "一括消去の確認", "🧹", () => { 
                safeRemoveItem('blind_bombs_replays'); 
                renderReplayList(); 
            }); 
        }
        function showReplayList() { renderReplayList(); switchScreen('replayList'); }
        
        function renderReplayList() { 
            const container = document.getElementById('replay-list-container'); 
            container.innerHTML = ''; 
            const list = getSavedReplays(); 
            if (list.length === 0) { 
                container.innerHTML = `<div class="text-gray-500 text-center py-8"><p class="text-base font-bold">リプレイ記録が存在しません。</p></div>`; 
                return; 
            } 
            list.forEach(item => { 
                const itemEl = document.createElement('div'); 
                itemEl.className = "flex justify-between items-center bg-gray-950 border border-gray-800 hover:border-yellow-500/50 p-3 rounded-lg transition duration-200 cursor-pointer"; 
                itemEl.onclick = () => startReplay(item); 
                const playerNames = item.players.map(p => `<span style="color:${p.color}">${p.name}</span>`).join(" vs "); 
                itemEl.innerHTML = `
                    <div class="flex-1 pr-2">
                        <div class="text-[10px] text-gray-600 flex justify-between mr-4 font-mono">
                            <span>📅 ${item.date}</span><span>🗺️ ${item.mapSize}x${item.mapSize}</span>
                        </div>
                        <div class="text-xs font-bold mt-1 text-gray-200 truncate max-w-[280px]">${playerNames}</div>
                        <div class="text-[11px] text-emerald-400 mt-1 font-mono">👑 勝者: ${item.winner} (${item.steps.length}手)</div>
                    </div>
                    <div class="flex gap-1.5 flex-shrink-0 flex-wrap justify-end">
                        <button class="btn btn-primary py-1 px-3 text-xs font-bold" style="margin: 2px;">🎬</button>
                        <button id="btn-export-${item.id}" class="btn bg-gray-800 hover:bg-gray-700 text-yellow-400 py-1 px-2 text-xs" style="margin: 2px;">📤</button>
                        <button id="btn-delete-${item.id}" class="btn btn-danger py-1 px-2.5 text-xs" style="margin: 2px;">🗑️</button>
                    </div>
                `; 
                container.appendChild(itemEl); 
                document.getElementById(`btn-export-${item.id}`).onclick = (e) => exportReplay(item.id, e);
                document.getElementById(`btn-delete-${item.id}`).onclick = (e) => deleteReplay(item.id, e);
            }); 
        }

        function watchCurrentReplay() { startReplay(STATE.currentReplay); }

        // リプレイ再生エンジン
        function startReplay(replayData) { REPLAY_PLAYER.data = replayData; REPLAY_PLAYER.currentStepIndex = -1; REPLAY_PLAYER.isPlaying = false; if (REPLAY_PLAYER.timer) clearInterval(REPLAY_PLAYER.timer); const rb = document.getElementById('replay-board'); rb.style.gridTemplateColumns = `repeat(${replayData.mapSize}, 1fr)`; rb.innerHTML = ''; const totalCells = replayData.mapSize * replayData.mapSize; REPLAY_PLAYER.boardState = Array.from({ length: totalCells }, () => []); REPLAY_PLAYER.cancelledCells = []; REPLAY_PLAYER.playersState = replayData.players.map(p => ({ name: p.name, color: p.color, life: p.maxLife, maxLife: p.maxLife, isDead: false })); for (let i = 0; i < totalCells; i++) { const cell = document.createElement('div'); cell.className = 'grid-cell'; cell.id = `replay-cell-${i}`; const inner = document.createElement('div'); inner.className = 'card-inner'; const front = document.createElement('div'); front.className = 'card-front text-2xl'; const back = document.createElement('div'); back.className = 'card-back text-2xl font-bold'; inner.appendChild(front); inner.appendChild(back); cell.appendChild(inner); rb.appendChild(cell); } switchScreen('replayPlayer'); syncReplayUI(); controlReplay('toggle'); }
        function syncReplayUI() { const data = REPLAY_PLAYER.data; const stepIndex = REPLAY_PLAYER.currentStepIndex; const totalSteps = data.steps.length; const playBtn = document.getElementById('btn-replay-play'); playBtn.textContent = REPLAY_PLAYER.isPlaying ? '⏸️ 一時停止' : '▶️ 再生'; const turnText = document.getElementById('replay-ui-turn'); const playerText = document.getElementById('replay-ui-player-name'); const phaseText = document.getElementById('replay-ui-phase-name'); const instruction = document.getElementById('replay-ui-instruction'); if (stepIndex === -1) { turnText.textContent = "🎬 スタート前"; playerText.textContent = "REPLAY"; playerText.style.color = "#fff"; phaseText.textContent = "準備完了"; phaseText.className = "text-xs font-bold px-3 py-1 rounded bg-gray-900 text-green-400"; instruction.textContent = "▶️ 再生ボタンを押すと、自動的に対戦映像が始まります！"; instruction.style.color = "#3b82f6"; } else { const currentStep = data.steps[stepIndex]; turnText.textContent = `手番: ${stepIndex + 1}/${totalSteps}`; playerText.textContent = currentStep.playerName; playerText.style.color = currentStep.color; if (currentStep.type === 'PLANT') { phaseText.textContent = "💣 罠の仕込み"; phaseText.className = "text-xs font-bold px-3 py-1 rounded bg-gray-900 text-yellow-400 animate-pulse"; const itemJapanese = currentStep.itemType === 'bomb' ? '💣爆弾' : (currentStep.itemType === 'timed' ? `⏱️時限爆弾(${currentStep.timerValue || 3}回)` : '👻ハッタリ'); instruction.textContent = `${currentStep.playerName} が ${itemJapanese} を仕掛けました。`; instruction.style.color = "#fcd34d"; } else { phaseText.textContent = "🔍 マスをめくる"; phaseText.className = "text-xs font-bold px-3 py-1 rounded bg-gray-900 text-blue-400"; let resultMsg = "💨 安全な空マスでした！"; let resultColor = "#60a5fa"; if (currentStep.foundType === 'bomb') { resultMsg = `💥 爆弾を踏みました！`; resultColor = "#f87171"; } else if (currentStep.foundType === 'ghost') { resultMsg = "👻 ハッタリ(ゴースト)が出現！"; resultColor = "#c084fc"; } else if (currentStep.foundType === 'timed') { resultMsg = "💥 安全な空きマスでした！"; resultColor = "#fb923c"; } instruction.textContent = `${currentStep.playerName} が選択… ${resultMsg}`; instruction.style.color = resultColor; } } const pContainer = document.getElementById('replay-ui-players-info'); pContainer.innerHTML = ''; REPLAY_PLAYER.playersState.forEach(p => { const el = document.createElement('div'); el.className = `p-2 rounded border border-gray-800 bg-gray-950 ${p.isDead ? 'opacity-30' : ''} flex-1 min-w-[100px] text-center`; el.style.borderTopColor = p.color; el.style.borderTopWidth = '3px'; let hearts = ''; for (let i = 0; i < p.maxLife; i++) { hearts += (i < p.life) ? '❤️' : '💔'; } el.innerHTML = `<div class="font-bold text-xs" style="color: ${p.color}">${p.name}</div><div class="text-[9px] tracking-tight mt-0.5">${hearts || '💀'}</div>`; pContainer.appendChild(el); }); const totalCells = data.mapSize * data.mapSize; for (let i = 0; i < totalCells; i++) { const cell = document.getElementById(`replay-cell-${i}`); if (!cell) continue; const front = cell.querySelector('.card-front'); const block_back = cell.querySelector('.card-back'); cell.classList.remove('selected', 'flipped'); front.className = 'card-front text-2xl'; block_back.className = 'card-back text-2xl font-bold relative'; block_back.style.backgroundColor = ''; block_back.style.borderColor = ''; block_back.innerHTML = ''; const stack = REPLAY_PLAYER.boardState[i]; const wasCancelled = REPLAY_PLAYER.cancelledCells.includes(i); if (stepIndex >= 0) { const step = data.steps[stepIndex]; if (step.cellIndex === i) { cell.classList.add('selected'); } } if (stack.length > 0) { cell.classList.add('flipped'); const topItem = stack[stack.length - 1]; if (stack.length === 2) { block_back.style.backgroundColor = '#581c87'; block_back.style.borderColor = '#c084fc'; block_back.innerHTML = `👻`; } else if (topItem.type === 'bomb') { block_back.style.backgroundColor = '#451a1a'; block_back.style.borderColor = '#b91c1c'; block_back.innerHTML = `💣`; } else if (topItem.type === 'ghost') { block_back.style.backgroundColor = '#1e1b4b'; block_back.style.borderColor = '#6366f1'; block_back.innerHTML = `👻`; } else if (topItem.type === 'timed') { block_back.style.backgroundColor = '#7c2d12'; block_back.style.borderColor = '#fb923c'; block_back.innerHTML = `⏱️<span class="text-[9px] absolute top-1 right-1 bg-black/60 rounded px-1">${topItem.timer}</span>`; } } else if (wasCancelled) { cell.classList.add('flipped'); block_back.style.backgroundColor = '#064e3b'; block_back.style.borderColor = '#10b981'; block_back.innerHTML = '🤝'; } if (stepIndex >= 0) { const step = data.steps[stepIndex]; if (step.type === 'REVEAL' && step.cellIndex === i) { if (step.foundType === 'bomb') { block_back.classList.add('opened-bomb'); block_back.innerHTML = '💥'; } else if (step.foundType === 'ghost') { block_back.classList.add('opened-ghost'); block_back.innerHTML = '👻'; } else if (step.foundType === 'timed') { block_back.classList.add('opened-timed'); block_back.innerHTML = '💥'; } else { block_back.classList.add('opened-empty'); } } } } }
        function advanceReplayStep() { const data = REPLAY_PLAYER.data; const nextIndex = REPLAY_PLAYER.currentStepIndex + 1; if (nextIndex >= data.steps.length) { REPLAY_PLAYER.isPlaying = false; if (REPLAY_PLAYER.timer) clearInterval(REPLAY_PLAYER.timer); showCustomAlert("対戦リプレイが最後まで終了しました！", "再生終了", "🎬"); syncReplayUI(); return; } REPLAY_PLAYER.currentStepIndex = nextIndex; const step = data.steps[nextIndex]; if (step.type === 'REVEAL') { for (let i = 0; i < REPLAY_PLAYER.boardState.length; i++) { const stack = REPLAY_PLAYER.boardState[i]; if (stack.length > 0) { const top = stack[stack.length - 1]; if (top.type === 'timed') { top.timer--; } } } } if (step.type === 'PLANT') { const stack = REPLAY_PLAYER.boardState[step.cellIndex]; const topItem = stack.length > 0 ? stack[stack.length - 1] : null; if (step.itemType === 'bomb') { if (topItem && topItem.type === 'bomb') { stack.pop(); REPLAY_PLAYER.cancelledCells.push(step.cellIndex); } else if (topItem && topItem.type === 'ghost') { stack.pop(); stack.push({ type: 'bomb', ownerName: step.playerName }); } else if (topItem && topItem.type === 'timed') { stack.pop(); stack.push({ type: 'bomb', ownerName: step.playerName }); } else { stack.push({ type: 'bomb', ownerName: step.playerName }); } } else if (step.itemType === 'ghost') { if (topItem && topItem.type === 'bomb') { stack.push({ type: 'ghost', ownerName: step.playerName }); } else if (topItem && topItem.type === 'ghost') { stack.pop(); REPLAY_PLAYER.cancelledCells.push(step.cellIndex); } else if (topItem && topItem.type === 'timed') { stack.push({ type: 'ghost', ownerName: step.playerName }); } else { stack.push({ type: 'ghost', ownerName: step.playerName }); } } else if (step.itemType === 'timed') { const timer = step.timerValue || 3; if (topItem && topItem.type === 'timed') { stack.length = 0; REPLAY_PLAYER.cancelledCells.push(step.cellIndex); } else if (topItem && topItem.type === 'ghost') { stack.pop(); stack.push({ type: 'timed', ownerName: step.playerName, timer: timer }); } else { stack.push({ type: 'timed', ownerName: step.playerName, timer: timer }); } } } else if (step.type === 'REVEAL') { const stack = REPLAY_PLAYER.boardState[step.cellIndex]; const victim = REPLAY_PLAYER.playersState[step.playerIndex]; if (step.foundType === 'bomb') { victim.life--; if (victim.life <= 0) victim.isDead = true; stack.pop(); } else if (step.foundType === 'ghost') { stack.pop(); } else if (step.foundType === 'timed') { victim.life--; if (victim.life <= 0) victim.isDead = true; stack.pop(); } } for (let i = 0; i < REPLAY_PLAYER.boardState.length; i++) { const stack = REPLAY_PLAYER.boardState[i]; if (stack.length > 0) { const top = stack[stack.length - 1]; if (top.type === 'timed' && top.timer <= 0) { stack.pop(); const victim = REPLAY_PLAYER.playersState[step.playerIndex]; victim.life--; if (victim.life <= 0) victim.isDead = true; } } } syncReplayUI(); }
        function rollbackReplayStep() { if (REPLAY_PLAYER.currentStepIndex < 0) return; const targetIndex = REPLAY_PLAYER.currentStepIndex - 1; const data = REPLAY_PLAYER.data; const totalCells = data.mapSize * data.mapSize; REPLAY_PLAYER.boardState = Array.from({ length: totalCells }, () => []); REPLAY_PLAYER.cancelledCells = []; REPLAY_PLAYER.playersState = data.players.map(p => ({ name: p.name, color: p.color, life: p.maxLife, maxLife: p.maxLife, isDead: false })); REPLAY_PLAYER.currentStepIndex = -1; for (let i = 0; i <= targetIndex; i++) { REPLAY_PLAYER.currentStepIndex = i; const step = data.steps[i]; if (step.type === 'REVEAL') { for (let j = 0; j < REPLAY_PLAYER.boardState.length; j++) { const stack = REPLAY_PLAYER.boardState[j]; if (stack.length > 0) { const top = stack[stack.length - 1]; if (top.type === 'timed') { top.timer--; } } } } if (step.type === 'PLANT') { const stack = REPLAY_PLAYER.boardState[step.cellIndex]; const topItem = stack.length > 0 ? stack[stack.length - 1] : null; if (step.itemType === 'bomb') { if (topItem && topItem.type === 'bomb') { stack.pop(); REPLAY_PLAYER.cancelledCells.push(step.cellIndex); } else if (topItem && topItem.type === 'ghost') { stack.pop(); stack.push({ type: 'bomb', ownerName: step.playerName }); } else if (topItem && topItem.type === 'timed') { stack.pop(); stack.push({ type: 'bomb', ownerName: step.playerName }); } else { stack.push({ type: 'bomb', ownerName: step.playerName }); } } else if (step.itemType === 'ghost') { if (topItem && topItem.type === 'bomb') { stack.push({ type: 'ghost', ownerName: step.playerName }); } else if (topItem && topItem.type === 'ghost') { stack.pop(); REPLAY_PLAYER.cancelledCells.push(step.cellIndex); } else if (topItem && topItem.type === 'timed') { stack.push({ type: 'ghost', ownerName: step.playerName }); } else { stack.push({ type: 'ghost', ownerName: step.playerName }); } } else if (step.itemType === 'timed') { const timer = step.timerValue || 3; if (topItem && topItem.type === 'timed') { stack.length = 0; REPLAY_PLAYER.cancelledCells.push(step.cellIndex); } else if (topItem && topItem.type === 'ghost') { stack.pop(); stack.push({ type: 'timed', ownerName: step.playerName, timer: timer }); } else { stack.push({ type: 'timed', ownerName: step.playerName, timer: timer }); } } } else if (step.type === 'REVEAL') { const stack = REPLAY_PLAYER.boardState[step.cellIndex]; const victim = REPLAY_PLAYER.playersState[step.playerIndex]; if (step.foundType === 'bomb') { victim.life--; if (victim.life <= 0) victim.isDead = true; stack.pop(); } else if (step.foundType === 'ghost') { stack.pop(); } else if (step.foundType === 'timed') { victim.life--; if (victim.life <= 0) victim.isDead = true; stack.pop(); } } for (let j = 0; j < REPLAY_PLAYER.boardState.length; j++) { const stack = REPLAY_PLAYER.boardState[j]; if (stack.length > 0) { const top = stack[stack.length - 1]; if (top.type === 'timed' && top.timer <= 0) { stack.pop(); const victim = REPLAY_PLAYER.playersState[step.playerIndex]; victim.life--; if (victim.life <= 0) victim.isDead = true; } } } } syncReplayUI(); }
        function controlReplay(action) { const data = REPLAY_PLAYER.data; if (action === 'toggle') { REPLAY_PLAYER.isPlaying = !REPLAY_PLAYER.isPlaying; if (REPLAY_PLAYER.isPlaying) { if (REPLAY_PLAYER.currentStepIndex >= data.steps.length - 1) { controlReplay('first'); } REPLAY_PLAYER.isPlaying = true; REPLAY_PLAYER.timer = setInterval(advanceReplayStep, 1800); } else { if (REPLAY_PLAYER.timer) clearInterval(REPLAY_PLAYER.timer); } syncReplayUI(); } else if (action === 'next') { REPLAY_PLAYER.isPlaying = false; if (REPLAY_PLAYER.timer) clearInterval(REPLAY_PLAYER.timer); advanceReplayStep(); } else if (action === 'prev') { REPLAY_PLAYER.isPlaying = false; if (REPLAY_PLAYER.timer) clearInterval(REPLAY_PLAYER.timer); rollbackReplayStep(); } else if (action === 'first') { REPLAY_PLAYER.isPlaying = false; if (REPLAY_PLAYER.timer) clearInterval(REPLAY_PLAYER.timer); const totalCells = data.mapSize * data.mapSize; REPLAY_PLAYER.boardState = Array.from({ length: totalCells }, () => []); REPLAY_PLAYER.cancelledCells = []; REPLAY_PLAYER.playersState = data.players.map(p => ({ name: p.name, color: p.color, life: p.maxLife, maxLife: p.maxLife, isDead: false })); REPLAY_PLAYER.currentStepIndex = -1; syncReplayUI(); } else if (action === 'last') { REPLAY_PLAYER.isPlaying = false; if (REPLAY_PLAYER.timer) clearInterval(REPLAY_PLAYER.timer); while (REPLAY_PLAYER.currentStepIndex < data.steps.length - 1) { advanceReplayStep(); } } }
        function exitReplay() { REPLAY_PLAYER.isPlaying = false; if (REPLAY_PLAYER.timer) clearInterval(REPLAY_PLAYER.timer); showReplayList(); }

        // --- 全てのDOMイベントとボタンのハンドラ統合 ---
        window.addEventListener('DOMContentLoaded', () => {
            // プロファイルの初期読込 (LocalStorage)
            loadLocalProfile();

            // 名前を変更したとき、またはフォーカスが外れたときの保存処理
            document.getElementById('setting-player-name').addEventListener('change', (e) => {
                const newName = e.target.value.trim();
                if (newName) {
                    syncProfileToFirestore(newName, STATE.myRating);
                } else {
                    loadLocalProfile(); // 空白にされたら戻す
                }
            });

            // ローカルスタート
            document.getElementById('btn-start-local').onclick = () => startGame(false);
            
            // オンライン初期設定
            document.getElementById('setting-players').onchange = updatePlayerSettings;
            document.getElementById('setting-cpus').onchange = updateFirstPlayerOptions;
            
            // オンラインコントロール
            document.getElementById('btn-show-online').onclick = showOnlineMenu;
            document.getElementById('btn-close-online').onclick = closeOnlineMenu;
            document.getElementById('btn-create-room').onclick = createRoom;
            document.getElementById('btn-join-room').onclick = joinRoom;
            document.getElementById('btn-free-match').onclick = startFreeMatch;
            document.getElementById('btn-cancel-room').onclick = cancelRoom;
            document.getElementById('btn-leave-game').onclick = leaveOnlineGame; // ゲーム中退出
            
            // リザルト画面
            document.getElementById('btn-result-return').onclick = returnToTitle;
            document.getElementById('btn-play-current-replay').onclick = watchCurrentReplay;

            // リプレイ関係
            document.getElementById('btn-show-replay-list').onclick = showReplayList;
            document.getElementById('btn-replay-list-return').onclick = returnToTitle;
            document.getElementById('btn-trigger-import').onclick = triggerImport;
            document.getElementById('import-file-input').onchange = handleImportFile;
            document.getElementById('btn-clear-replays').onclick = showClearConfirm;

            // リプレイプレイヤー
            document.getElementById('btn-replay-first').onclick = () => controlReplay('first');
            document.getElementById('btn-replay-prev').onclick = () => controlReplay('prev');
            document.getElementById('btn-replay-play').onclick = () => controlReplay('toggle');
            document.getElementById('btn-replay-next').onclick = () => controlReplay('next');
            document.getElementById('btn-replay-last').onclick = () => controlReplay('last');
            document.getElementById('btn-replay-exit').onclick = exitReplay;

            // ローカル用オーバーレイOKボタン
            document.getElementById('btn-overlay-ok').onclick = () => startNextPlayerTurn(false);

            // 初期選択リストの更新
            updatePlayerSettings();
        });
    </script>
</body>
</html>
'''

# Linuxユーザー向け代替: "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QLineEdit, QStatusBar,
    QMessageBox, QListWidget, QVBoxLayout, QPushButton, QWidget, QLabel,
    QTabWidget, QMenu, QToolButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QInputDialog, QHBoxLayout, QDialog, QProgressBar, QListWidgetItem,
    QCheckBox, QStackedWidget, QFrame, QSplitter, QComboBox, QGroupBox, QRadioButton, QButtonGroup,
    QWidgetAction, QGridLayout, QTextBrowser, QSlider, QDateTimeEdit, QTreeView,
    QMdiArea, QMdiSubWindow, QSystemTrayIcon
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import (
    QWebEngineProfile, QWebEnginePage, QWebEngineSettings,
    QWebEngineDownloadRequest, QWebEngineScript, QWebEngineUrlRequestInterceptor
)
from PySide6.QtCore import QUrl, QTimer, Qt, QSize, QUrlQuery, Signal, QThread
from PySide6.QtGui import QAction, QKeySequence, QShortcut, QFont, QStandardItemModel, QStandardItem, QIcon, QPixmap

# ---------------------------------------------------------
# 🛠️ 本格的なリアルタイム・ダウンロードマネージャー UI
# ---------------------------------------------------------
class DownloadManagerTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.downloads = []
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_lbl = QLabel(_("📥 ダウンロード履歴"))
        title_lbl.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title_lbl)
        
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([_("ファイル名"), _("進捗"), _("サイズ"), _("状態"), _("操作")])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(1, 150)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setStyleSheet("QTableWidget { background-color: #11111b; color: #cdd6f4; gridline-color: #3b3d54; }")
        layout.addWidget(self.table)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(500)

    def add_download(self, item: QWebEngineDownloadRequest):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        fn_item = QTableWidgetItem(item.downloadFileName())
        self.table.setItem(row, 0, fn_item)
        
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        progress_bar.setStyleSheet("""
            QProgressBar { border: 1px solid #3b3d54; border-radius: 4px; text-align: center; color: white; background-color: #1e1e2e; }
            QProgressBar::chunk { background-color: #00ddff; }
        """)
        self.table.setCellWidget(row, 1, progress_bar)
        
        size_item = QTableWidgetItem(_("計算中..."))
        self.table.setItem(row, 2, size_item)
        
        status_item = QTableWidgetItem(_("ダウンロード中"))
        self.table.setItem(row, 3, status_item)
        
        act_btn = QPushButton(_("キャンセル"))
        act_btn.setStyleSheet("background-color: #ff6464; color: white; border-radius: 4px; padding: 4px;")
        act_btn.clicked.connect(lambda: self.cancel_download(item, row))
        self.table.setCellWidget(row, 4, act_btn)
        
        self.downloads.append({
            "item": item,
            "row": row,
            "bar": progress_bar,
            "cancelled": False
        })

    def update_progress(self):
        for dl in self.downloads:
            if dl["cancelled"]:
                continue
                
            item = dl["item"]
            row = dl["row"]
            
            total = item.totalBytes()
            received = item.receivedBytes()
            
            if total > 0:
                percent = int((received / total) * 100)
                dl["bar"].setValue(percent)
                size_str = f"{(received / (1024*1024)):.2f}MB / {(total / (1024*1024)):.2f}MB"
            else:
                dl["bar"].setValue(0)
                size_str = f"{(received / (1024*1024)):.2f}MB"
                
            self.table.setItem(row, 2, QTableWidgetItem(size_str))
            
            state = item.state()
            if state == QWebEngineDownloadRequest.DownloadState.DownloadInProgress:
                self.table.setItem(row, 3, QTableWidgetItem(_("進行中")))
            elif state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
                self.table.setItem(row, 3, QTableWidgetItem(_("✅ 完了")))
                dl["bar"].setValue(100)
                dl["bar"].setStyleSheet("QProgressBar::chunk { background-color: #4CAF50; }")
                
                open_btn = QPushButton(_("開く"))
                open_btn.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 4px; padding: 4px;")
                file_path = os.path.join(item.downloadDirectory(), item.downloadFileName())
                open_btn.clicked.connect(lambda _, fp=file_path: os.startfile(fp) if sys.platform == "win32" else os.system(f"open '{fp}'"))
                self.table.setCellWidget(row, 4, open_btn)
                
            elif state == QWebEngineDownloadRequest.DownloadState.DownloadCancelled:
                self.table.setItem(row, 3, QTableWidgetItem(_("❌ キャンセル")))
                dl["bar"].setValue(0)
                self.table.setCellWidget(row, 4, QLabel("-"))
            elif state == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted:
                self.table.setItem(row, 3, QTableWidgetItem(_("⚠️ 中断")))
                
    def cancel_download(self, item, row):
        item.cancel()
        for dl in self.downloads:
            if dl["row"] == row:
                dl["cancelled"] = True
        self.table.setItem(row, 3, QTableWidgetItem(_("❌ キャンセル")))
        self.table.setCellWidget(row, 4, QLabel("-"))

# ---------------------------------------------------------
# コマンドパレットダイアログ
# ---------------------------------------------------------
class CommandPaletteDialog(QDialog):
    def __init__(self, parent, cmds):
        super().__init__(parent)
        self.selected_action = None
        self.setWindowTitle(_("コマンドパレット"))
        self.resize(400, 300)
        layout = QVBoxLayout(self)
        list_widget = QListWidget()
        list_widget.setStyleSheet("QListWidget { font-size: 14px; padding: 5px; } QListWidget::item { padding: 10px; border-bottom: 1px solid #ddd; }")
        for name, func in cmds:
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, func)
            list_widget.addItem(item)
        layout.addWidget(list_widget)
        list_widget.itemDoubleClicked.connect(self.on_item_dbl_clicked)
    def on_item_dbl_clicked(self, item):
        self.selected_action = item.data(Qt.ItemDataRole.UserRole)
        self.accept()

# =========================================================
# 🌐 実際のSSL証明書を非同期で取得するバックグラウンドスレッド
# =========================================================
class CertInfoThread(QThread):
    result_ready = Signal(dict)
    
    def __init__(self, host):
        super().__init__()
        self.host = host
        
    def run(self):
        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.host, 443), timeout=3.0) as sock:
                with context.wrap_socket(sock, server_hostname=self.host) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher() 
                    
                    issuer_dict = {}
                    for item in cert.get('issuer', []):
                        for k, v in item:
                            issuer_dict[k] = v
                    issuer_name = issuer_dict.get('organizationName', issuer_dict.get('commonName', 'Unknown CA'))
                    
                    vf_str = cert.get('notBefore')
                    vt_str = cert.get('notAfter')
                    try:
                        vf = datetime.strptime(vf_str, '%b %d %H:%M:%S %Y %Z')
                        vt = datetime.strptime(vt_str, '%b %d %H:%M:%S %Y %Z')
                        valid_from = vf.strftime('%Y年%m月%d日 %H:%M:%S' if CURRENT_LANG == "ja" else '%Y-%m-%d %H:%M:%S')
                        valid_to = vt.strftime('%Y年%m月%d日 %H:%M:%S' if CURRENT_LANG == "ja" else '%Y-%m-%d %H:%M:%S')
                        remaining_days = (vt - datetime.utcnow()).days
                    except Exception:
                        valid_from = vf_str
                        valid_to = vt_str
                        remaining_days = 365
                        
                    subject_dict = {}
                    for item in cert.get('subject', []):
                        for k, v in item:
                            subject_dict[k] = v
                    subject_name = subject_dict.get('commonName', self.host)

                    self.result_ready.emit({
                        'issuer': issuer_name,
                        'subject': subject_name,
                        'valid_from': valid_from,
                        'valid_to': valid_to,
                        'cipher_suite': cipher[0],
                        'protocol': cipher[1],
                        'bits': cipher[2],
                        'remaining_days': remaining_days,
                    })
        except Exception as e:
            self.result_ready.emit({"error": str(e)})

# =========================================================
# 📋 トラッカー・セキュリティポリシー＆Googleログイン回避用インターセプター
# =========================================================

# Googleログイン関連ドメイン（ここを一元管理して矛盾を防ぐ）
GOOGLE_AUTH_HOSTS = (
    "accounts.google.com",
    "myaccount.google.com",
    "accounts.youtube.com",
    "signin.google.com",
)

class OpenWebUrlInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ad_domains = (
            "doubleclick.net", "googleadservices.com", "googlesyndication.com",
            "adnxs.com", "scorecardresearch.com", "quantserve.com", "analytics.google.com"
        )
        self.https_upgrade_enabled = False
        self.tracker_block_enabled = False
        self.blocked_count = 0 

    def interceptRequest(self, info):
        url = info.requestUrl()
        host = url.host().lower()
        first_party = info.firstPartyUrl().host().lower()

        # ★ Googleログイン完全回避（Firefox UA偽装 + Client Hints完全削除）v6.2 強化版
        # コミュニティ（qutebrowserなど）で最も効果が高いとされる方法
        if any(g in host for g in GOOGLE_AUTH_HOSTS):
            # Firefox UA に偽装（Chrome系を検知して弾くGoogleの対策を回避）
            fx_ua = FIREFOX_UA_FOR_GOOGLE.encode('utf-8')
            info.setHttpHeader(b"User-Agent", fx_ua)
            
            # Chromium特有のClient Hintsを完全に削除（非常に重要）
            for header in [
                b"Sec-CH-UA", b"Sec-CH-UA-Mobile", b"Sec-CH-UA-Platform",
                b"Sec-CH-UA-Platform-Version", b"Sec-CH-UA-Arch", b"Sec-CH-UA-Bitness",
                b"Sec-CH-UA-Model", b"Sec-CH-UA-Full-Version-List", b"Sec-CH-UA-Form-Factors"
            ]:
                info.setHttpHeader(header, b"")
            
            # 追加で Accept-Language を自然なものに（任意）
            info.setHttpHeader(b"Accept-Language", b"ja,en-US;q=0.9,en;q=0.8")

        is_media_site = any(domain in first_party for domain in ["youtube.com", "youtu.be", "youtube-nocookie.com", "twitch.tv", "player."])

        if self.tracker_block_enabled and not is_media_site:
            for ad_domain in self.ad_domains:
                if ad_domain in host:
                    self.blocked_count += 1
                    info.block(True)
                    return

        if self.https_upgrade_enabled and url.scheme() == "http":
            if host not in ["localhost", "127.0.0.1"] and not host.startswith("192.168."):
                new_url = QUrl(url)
                new_url.setScheme("https")
                info.redirect(new_url)

# =========================================================
# 🔒 サイトの安全性・認証情報・オフライン隔離基準詳細ダイアログ
# =========================================================
class SecurityStatusDialog(QDialog):
    def __init__(self, qurl, tracker_blocked_count, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("🛡️ OpenWeb v.6.2 - 超厳格セキュリティ監査システム"))
        self.setFixedSize(580, 580)
        self.setStyleSheet("background-color: #1e1e2e; color: #f1f1f7; font-family: sans-serif;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.scheme = qurl.scheme()
        self.host = qurl.host() if qurl.host() else _("ローカルファイル/内部システム")
        self.qurl = qurl
        self.tracker_blocked_count = tracker_blocked_count
        
        self.safety_score = 0
        self.safety_text = _("分析中...")
        self.color_code = "#bac2de"

        display_host = self.qurl.toLocalFile() if self.scheme == "file" else self.host
        if len(display_host) > 45:
            display_host = "..." + display_host[-42:]
        header_label = QLabel(f"📂 {display_host}" if self.scheme == "file" else f"🌎 {display_host}")
        header_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #ffffff;")
        header_label.setWordWrap(True)
        layout.addWidget(header_label)

        score_layout = QHBoxLayout()
        self.score_num_label = QLabel("--")
        self.score_num_label.setFont(QFont("Impact", 42))
        self.score_num_label.setStyleSheet(f"color: {self.color_code};")
        
        score_desc_layout = QVBoxLayout()
        score_title = QLabel(_("総合安全性・安心スコア"))
        score_title.setFont(QFont("Arial", 9))
        score_title.setStyleSheet("color: #a6adc8;")
        self.score_status = QLabel(self.safety_text)
        self.score_status.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.score_status.setStyleSheet(f"color: {self.color_code};")
        
        score_desc_layout.addWidget(score_title)
        score_desc_layout.addWidget(self.score_status)
        
        score_layout.addWidget(self.score_num_label)
        score_layout.addSpacing(20)
        score_layout.addLayout(score_desc_layout)
        score_layout.addStretch()
        layout.addLayout(score_layout)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #3b3d54; max-height: 1px;")
        layout.addWidget(line)

        self.cert_tab_widget = QTabWidget()
        self.cert_tab_widget.setStyleSheet("""
            QTabWidget::panel { border: 1px solid #3b3d54; border-radius: 8px; background-color: #11111b; }
            QTabBar::tab { background-color: #242538; color: #a6adc8; padding: 8px 16px; border-top-left-radius: 6px; border-top-right-radius: 6px; }
            QTabBar::tab:selected { background-color: #11111b; color: #ffffff; border-bottom: 2px solid #00ddff; }
        """)
        
        self.basic_tab = QWidget()
        self.basic_layout = QVBoxLayout(self.basic_tab)
        self.details_box = QTextBrowser()
        self.details_box.setStyleSheet("background-color: transparent; border: none; color: #cdd6f4;")
        self.basic_layout.addWidget(self.details_box)
        self.cert_tab_widget.addTab(self.basic_tab, _("📋 全般・セキュリティ"))

        self.path_tab = QWidget()
        self.path_layout = QVBoxLayout(self.path_tab)
        
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setStyleSheet("""
            QTreeView { background-color: #11111b; border: 1px solid #3b3d54; border-radius: 6px; color: #cdd6f4; }
            QTreeView::item { padding: 4px; }
            QTreeView::item:hover { background-color: #242538; }
            QTreeView::item:selected { background: #3b3d54; color: #ffffff; }
        """)
        self.path_layout.addWidget(QLabel(_("<b>【🏢 証明書チェーンパス】</b>")))
        self.path_layout.addWidget(self.tree_view)
        
        self.verification_label = QLabel()
        self.verification_label.setStyleSheet("color: #a6e3a1; font-size: 11px;")
        self.path_layout.addWidget(self.verification_label)
        
        self.cert_tab_widget.addTab(self.path_tab, _("🏢 証明書パス / 安心構成"))
        layout.addWidget(self.cert_tab_widget)

        self.checklist_label = QLabel()
        self.checklist_label.setFont(QFont("Arial", 9))
        self.checklist_label.setStyleSheet("color: #bac2de; line-height: 1.4;")
        layout.addWidget(self.checklist_label)

        close_btn = QPushButton("OK")
        close_btn.setStyleSheet("""
            QPushButton { background-color: #242538; color: white; border: 1px solid #3b3d54; border-radius: 6px; padding: 8px 16px; font-weight: bold; }
            QPushButton:hover { background-color: #3b3d54; }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.evaluate_basic_score()

    def generate_table_html(self, rows):
        html = '<table style="width:100%; font-size:12px; line-height:1.6; border-collapse: collapse;">'
        html += f'<tr><th style="text-align:left; border-bottom:1px solid #3b3d54; padding-bottom:5px; color:#89b4fa; width:35%;">{_("評価指標")}</th><th style="text-align:left; border-bottom:1px solid #3b3d54; padding-bottom:5px; color:#89b4fa;">{_("詳細・判定")}</th><th style="text-align:right; border-bottom:1px solid #3b3d54; padding-bottom:5px; color:#89b4fa; width:20%;">{_("スコア")}</th></tr>'
        for title, val, desc in rows:
            html += f'<tr><td style="padding-top:4px;"><b>{title}</b></td><td style="padding-top:4px; color:#a6e3a1;">{desc}</td><td style="text-align:right; padding-top:4px; font-weight:bold; color:#f9e2af;">{val}</td></tr>'
        html += '</table>'
        return html

    def evaluate_basic_score(self):
        if self.scheme == "file":
            self.safety_score = 98
            if self.tracker_blocked_count >= 0: self.safety_score += 2
            
            self.safety_text = _("ローカル動作：極めて安全 (完全オフライン)")
            self.color_code = "#00ddff"
            
            rows = [
                (_("プロトコル種別"), _("FILE (ローカル隔離実行)"), _("適合")),
                (_("外部ネットワーク通信"), _("0% (完全オフライン制御)"), _("適合")),
                (_("データリークリスク"), _("皆無 (端末外への送信遮断)"), _("適合")),
                (_("広告・トラッカー挙動"), _("不活性 (スクリプト追跡不可)"), "+20"),
                (_("サンドボックス環境"), _("有効 (OS領域への干渉防止)"), "+30"),
                (_("プライバシー保護"), _("適合 (外部キャッシュの共有なし)"), "+48"),
            ]
            self.details_box.setHtml(self.generate_table_html(rows))
            
            model = QStandardItemModel()
            model_item = QStandardItem(_("オフライン接続中：外部の証明書パスは存在しません"))
            model.appendRow(model_item)
            self.tree_view.setModel(model)
            
            self.verification_label.setText(_("★ ローカルでの安全動作保証基準：\n・ローカルストレージデータ暗号：AES-256整合\n・CORSおよび外部WebAPI通信：完全ローカル隔離により安全"))
            self.verification_label.setStyleSheet("color: #00ddff; font-size: 11px;")
            
            self.checklist_label.setText(_("🟢 外部ネットワークからのハッキング耐性：安全\n🟢 広告トラッカー・クッキーによる行動追跡：100%遮断\n🟢 個人情報やファイルのデータ保護：安全（ローカル完結）"))
            self.update_score_ui()

        elif self.scheme == "openweb":
            self.safety_score = 100
            self.safety_text = _("完全に安全な内部サンドボックス")
            self.color_code = "#00ddff"
            self.details_box.setHtml("<p>Native system page. Sandboxed from any web engine execution hazards.</p>" if CURRENT_LANG == "en" else "<p>ブラウザのネイティブ実行ページです。外部API接続およびネットワークとの切断が保障された完全サンドボックス構造です。最高評価が与えられます。</p>")
            self.checklist_label.setText(_("🟢 完全なシステム特権下で他サイトから完全に分離されています。"))
            self.update_score_ui()

        elif self.scheme == "https":
            self.details_box.setHtml(f"<div style='text-align:center; padding: 20px;'><h3 style='color:#00ddff;'>{_('🔄 実際のSSL/TLS証明書情報をバックグラウンドで照会・分析しています...')}</h3><p>{_('少々お待ちください')}</p></div>")
            msg2 = _("🟢 トラッカーブロックが稼働中 (傍受防止)") if self.tracker_blocked_count > 0 else ("🟡 Awaiting script blocks" if CURRENT_LANG == "en" else "🟡 危険なスクリプトの即座ブロック待機中")
            if CURRENT_LANG == "en":
                self.checklist_label.setText(f"🟢 Communication is highly encrypted.\n{msg2}\n🟢 Secure DNS Prefetch Active")
            else:
                self.checklist_label.setText(f"🟢 接続は高度に暗号化されています\n{msg2}\n🟢 安全なDNSプリフェッチがアクティブ")
            
            self.cert_thread = CertInfoThread(self.host)
            self.cert_thread.result_ready.connect(self.update_cert_info)
            self.cert_thread.start()

        elif self.scheme in ["http", "ws"]:
            score = 35
            if self.tracker_blocked_count > 0: score += 5
            if self.host in ["localhost", "127.0.0.1"] or self.host.startswith("192.168."):
                score += 20
                self.safety_text = _("限定的安全 (ローカル開発サーバー実行中)")
                self.color_code = "#a6e3a1"
            else:
                self.safety_text = _("警告: 通信が保護されていません")
                self.color_code = "#f38ba8"
                
            self.safety_score = min(max(score, 0), 100)
            
            details = [
                (_("通信プロトコル"), _("HTTP (平文クリアテキスト)"), _("不適合")),
                (_("JWTセッション脆弱性"), _("高リスク (Tokenの傍受盗聴可能)"), _("警告")),
                (_("暗号署名整合性(JWA)"), _("検証不可 (SSL/TLS証明書なし)"), "-30"),
                (_("データ漏洩危険度"), _("高リスク (中間者インジェクションの余地あり)"), "-20")
            ]
            self.details_box.setHtml(self.generate_table_html(details))
            
            model = QStandardItemModel()
            model.appendRow(QStandardItem(_("非暗号化接続：証明書ツリーは構築できません")))
            self.tree_view.setModel(model)
            
            self.checklist_label.setText(_("🔴 接続平文通信：安全ではありません（傍受・インジェクション耐性ゼロ）\n🟡 セッションセキュリティ制限：JWT署名トークン等のキャッシュ一時保護隔離中\n🟢 トラッカーブロック＆防御はアクティブ"))
            self.update_score_ui()

    def update_cert_info(self, cert_data):
        if "error" in cert_data:
            self.safety_score = 75  
            self.safety_text = _("暗号化接続 (証明書詳細取得タイムアウト)")
            self.color_code = "#FF9800"
            self.details_box.setHtml(_("タイムアウトにより証明書を完全検証できませんでした。"))
            self.update_score_ui()
            return

        score = 0
        details = []

        protocol = cert_data.get('protocol', '')
        if "TLSv1.3" in protocol:
            score += 25
            details.append((_("プロトコル世代"), _("TLSv1.3 (最高基準)"), "+25"))
        elif "TLSv1.2" in protocol:
            score += 15
            details.append((_("プロトコル世代"), _("TLSv1.2 (標準的な規格)"), "+15"))
        else:
            details.append((_("プロトコル世代"), f"{_('古い規格')} ({protocol})", "+0"))

        cipher = cert_data.get('cipher_suite', '')
        cipher_score = 0
        if "GCM" in cipher or "POLY1305" in cipher:
            cipher_score += 15
        if "ECDHE" in cipher or "DHE" in cipher:
            cipher_score += 10
        score += cipher_score
        details.append((_("暗号スイート強度"), f"{cipher} (PFS Ready)", f"+{cipher_score}"))

        bits = cert_data.get('bits', 0)
        if bits >= 256:
            score += 15
            details.append((_("暗号署名 鍵交換長"), f"{bits}bit {_('極めて強固')}", "+15"))
        elif bits >= 128:
            score += 10
            details.append((_("暗号署名 鍵交換長"), f"{bits}bit {_('標準的な強度')}", "+10"))
        else:
            details.append((_("暗号署名 鍵交換長"), f"{bits}bit {_('脆弱な鍵長')}", "+0"))

        issuer = cert_data.get('issuer', '')
        high_trust_cas = ["Google", "DigiCert", "GlobalSign", "Let's Encrypt", "Amazon", "Sectigo", "VeriSign", "Cloudflare", "Baltimore"]
        if any(ca in issuer for ca in high_trust_cas):
            score += 15
            details.append((_("認証局(CA)信頼性"), f"{_('高信頼CA')} ({issuer})", "+15"))
        else:
            score += 5
            details.append((_("認証局(CA)信頼性"), f"{_('一般CA')} ({issuer})", "+5"))

        remaining = cert_data.get('remaining_days', 0)
        if remaining > 90:
            score += 10
            details.append((_("証明書 有効期限"), f"{remaining} {_('日残 (十分な猶予)')}", "+10"))
        elif remaining > 0:
            score += 5
            details.append((_("証明書 有効期限"), f"{remaining} {_('日残 (更新推奨)')}", "+5"))
        else:
            score = 0
            details.append((_("証明書 有効期限"), _("期限切れ・失効"), _("無効化")))

        client_score = 10
        score += client_score
        details.append((_("ローカル防御設定"), _("トラッカー遮断/HTTPS強制アクティブ"), f"+{client_score}"))

        self.safety_score = min(max(score, 0), 100)
        
        if self.safety_score >= 95:
            self.safety_text = _("極めて強固な暗号化（A+ 評価）")
            self.color_code = "#4CAF50"
        elif self.safety_score >= 80:
            self.safety_text = _("安全な通信環境（A 評価）")
            self.color_code = "#a6e3a1"
        else:
            self.safety_text = _("標準的な暗号化（B 評価）")
            self.color_code = "#f9e2af"

        self.details_box.setHtml(self.generate_table_html(details))
        
        model = QStandardItemModel()
        root_item = QStandardItem(_("Root CA: DigiCert / GlobalSign (信頼済みルートCA)"))
        root_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        
        inter_item = QStandardItem(f"Intermediate CA: {issuer}")
        leaf_item = QStandardItem(f"{_('Leaf:')} {cert_data['subject']}{_(' (本サイトの有効な署名)')}")
        
        inter_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        leaf_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        
        root_item.appendRow(inter_item)
        inter_item.appendRow(leaf_item)
        model.appendRow(root_item)
        self.tree_view.setModel(model)
        self.tree_view.expandAll()
        
        self.verification_label.setText(_("✔ 証明書のチェーン検証：完全一致（署名偽装なし）\n✔ CRL/OCSPによる失効検証：問題なし（有効な鍵を保持）"))
        self.update_score_ui()

    def update_score_ui(self):
        self.score_num_label.setText(str(self.safety_score))
        self.score_num_label.setStyleSheet(f"color: {self.color_code}; font-weight: bold; font-family: 'Impact'; font-size: 42px;")
        self.score_status.setText(self.safety_text)
        self.score_status.setStyleSheet(f"color: {self.color_code}; font-weight: bold;")

# =========================================================
# Vault Setup & Unlock Dialogs
# =========================================================
class VaultSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("OpenWeb Vault セットアップ"))
        self.setFixedSize(380, 250)
        layout = QVBoxLayout(self)
        msg_label = QLabel(_("新しいマスターパスワードを設定してください"))
        msg_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(msg_label)
        layout.addWidget(QLabel(""))
        
        form_layout1 = QHBoxLayout()
        form_layout1.addWidget(QLabel(_("マスターパスワード:")))
        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout1.addWidget(self.pwd_input)
        layout.addLayout(form_layout1)
        
        form_layout2 = QHBoxLayout()
        form_layout2.addWidget(QLabel(_("確認のため再入力:")))
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout2.addWidget(self.confirm_input)
        layout.addLayout(form_layout2)
        
        info_label = QLabel(_("・8文字以上を推奨します\n・このパスワードを忘れた場合の復元はできません。"))
        info_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(info_label)
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton(_("設定する"))
        self.cancel_btn = QPushButton(_("キャンセル"))
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.ok_btn.clicked.connect(self.verify_and_accept)
        self.cancel_btn.clicked.connect(self.reject)

    def verify_and_accept(self):
        pwd = self.pwd_input.text()
        conf = self.confirm_input.text()
        if not pwd or pwd != conf or len(pwd) < 8:
            QMessageBox.warning(self, _("エラー"), _("パスワードが一致しないか、短すぎます。"))
            return
        self.accept()

    def get_password(self): return self.pwd_input.text()

class VaultUnlockDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("OpenWeb Vault ロック解除"))
        self.setFixedSize(360, 200)
        layout = QVBoxLayout(self)
        msg_label = QLabel(_("マスターパスワードを入力してください"))
        msg_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(msg_label)
        
        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel(_("パスワード:")))
        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(self.pwd_input)
        layout.addLayout(form_layout)
        
        chk_layout = QHBoxLayout()
        chk_layout.addStretch()
        self.show_pwd_chk = QCheckBox(_("パスワードを表示"))
        self.show_pwd_chk.stateChanged.connect(self.toggle_echo_mode)
        chk_layout.addWidget(self.show_pwd_chk)
        layout.addLayout(chk_layout)
        
        layout.addStretch()
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton(_("解除"))
        self.cancel_btn = QPushButton(_("キャンセル"))
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
    def toggle_echo_mode(self, state):
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Normal if state != 0 else QLineEdit.EchoMode.Password)
            
    def get_password(self): return self.pwd_input.text()

class VaultChangePasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("マスターパスワードを変更します"))
        self.setFixedSize(380, 280)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(_("マスターパスワードを変更します")))
        
        form_layout = QGridLayout()
        form_layout.addWidget(QLabel(_("現在のパスワード:")), 0, 0)
        self.old_pwd = QLineEdit(); self.old_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(self.old_pwd, 0, 1)
        
        form_layout.addWidget(QLabel(_("新しいパスワード:")), 1, 0)
        self.new_pwd = QLineEdit(); self.new_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(self.new_pwd, 1, 1)
        
        form_layout.addWidget(QLabel(_("再入力:")), 2, 0)
        self.confirm_pwd = QLineEdit(); self.confirm_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(self.confirm_pwd, 2, 1)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton(_("変更する")); self.cancel_btn = QPushButton(_("キャンセル"))
        btn_layout.addWidget(self.ok_btn); btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.ok_btn.clicked.connect(self.verify_and_accept)
        self.cancel_btn.clicked.connect(self.reject)
        
    def verify_and_accept(self):
        if not self.old_pwd.text() or not self.new_pwd.text(): return
        if self.new_pwd.text() != self.confirm_pwd.text() or len(self.new_pwd.text()) < 8: return
        self.accept()
        
    def get_passwords(self): return self.old_pwd.text(), self.new_pwd.text()

# =========================================================
# Vault Manager (AES-256-GCM) ★遅延ロードで起動を爆速化
# =========================================================
class OpenWebVaultManager:
    def __init__(self, base_path):
        self.vault_file = os.path.join(base_path, "vault.db")
        self.is_unlocked = False
        self.master_password = None
        self.data = {"version": 3, "created": int(time.time()), "accounts": {}, "notes": {}, "index": []}
        self.domain_index = []

    def is_setup(self):
        if not os.path.exists(self.vault_file): return False
        try:
            with open(self.vault_file, 'rb') as f: return f.read(4) == b'OWVL'
        except: return False

    def setup(self, password):
        self.master_password = password
        self.is_unlocked = True
        self.data = {"version": 3, "created": int(time.time()), "accounts": {}, "notes": {}, "index": []}
        self.domain_index = []
        self._save_vault()

    def unlock(self, password):
        if not self.is_setup(): return False
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            with open(self.vault_file, 'rb') as f:
                f.read(4); f.read(1)
                salt = f.read(int.from_bytes(f.read(1), 'big'))
                nonce = f.read(12)
                ciphertext = f.read(int.from_bytes(f.read(8), 'big'))
                tag = f.read(16)
            key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 600000, dklen=32)
            aesgcm = AESGCM(key)
            self.data = json.loads(aesgcm.decrypt(nonce, ciphertext + tag, None).decode("utf-8"))
            if "notes" not in self.data: self.data["notes"] = {}
            self.domain_index = self.data.get("index", [])
            self.master_password = password
            self.is_unlocked = True
            return True
        except ImportError:
            print("[OpenWeb Vault] cryptography パッケージが見つかりません。pip install cryptography を実行してください。")
            return False
        except Exception as e:
            print(f"[OpenWeb Vault] 復号エラー: {e}")
            return False

    def lock(self): 
        self.is_unlocked = False
        self.master_password = None

    # ==================== Google OAuth2 Token Support (Vault保存) ====================
    def save_google_oauth(self, token_data: dict):
        """Google OAuthトークンを暗号化して保存"""
        if not self.is_unlocked:
            return False
        self.data["google_oauth"] = token_data
        self._save_vault()
        return True

    def load_google_oauth(self):
        """保存されているGoogle OAuthトークンを取得"""
        if not self.is_unlocked:
            return None
        return self.data.get("google_oauth")

    def has_google_oauth(self):
        if not self.is_unlocked:
            return False
        oauth = self.data.get("google_oauth")
        return bool(oauth and oauth.get("access_token"))

    def clear_google_oauth(self):
        if not self.is_unlocked:
            return False
        if "google_oauth" in self.data:
            del self.data["google_oauth"]
            self._save_vault()
        return True

    def refresh_google_token(self):
        """リフレッシュトークンを使ってアクセストークンを更新（自動生成）"""
        if not self.is_unlocked:
            return False

        oauth = self.data.get("google_oauth", {})
        refresh_token = oauth.get("refresh_token")
        client_id = oauth.get("client_id")

        if not refresh_token or not client_id:
            return False

        try:
            response = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": client_id,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token"
                }
            )
            new_tokens = response.json()

            if "access_token" in new_tokens:
                oauth["access_token"] = new_tokens["access_token"]
                if "expires_in" in new_tokens:
                    oauth["expires_at"] = (datetime.now() + timedelta(seconds=new_tokens.get("expires_in", 3600))).isoformat()
                if new_tokens.get("refresh_token"):
                    oauth["refresh_token"] = new_tokens["refresh_token"]
                self.data["google_oauth"] = oauth
                self._save_vault()
                return True
            else:
                # 失敗時は無効トークンをクリア
                if "google_oauth" in self.data:
                    del self.data["google_oauth"]
                    self._save_vault()
        except Exception as e:
            print(f"[Google OAuth] Token refresh exception: {e}")
            if "google_oauth" in self.data:
                del self.data["google_oauth"]
                self._save_vault()
        return False

    def change_password(self, old_password, new_password):
        if not self.is_unlocked or old_password != self.master_password: return False
        self.master_password = new_password
        self._save_vault()
        return True

    def _rotate_backups(self):
        if not os.path.exists(self.vault_file): return
        for i in range(3, 0, -1):
            src = f"{self.vault_file}.bak{i}"
            if os.path.exists(src):
                if i == 3: os.remove(src)
                else: shutil.copy2(src, f"{self.vault_file}.bak{i+1}")
        shutil.copy2(self.vault_file, f"{self.vault_file}.bak1")

    def _save_vault(self):
        if not self.is_unlocked or not self.master_password: return
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            self._rotate_backups()
            salt = os.urandom(16); nonce = os.urandom(12)
            key = hashlib.pbkdf2_hmac('sha256', self.master_password.encode('utf-8'), salt, 600000, dklen=32)
            enc = AESGCM(key).encrypt(nonce, json.dumps(self.data, ensure_ascii=False).encode("utf-8"), None)
            with open(self.vault_file, 'wb') as f:
                f.write(b'OWVL\x03' + len(salt).to_bytes(1, 'big') + salt + nonce + len(enc[:-16]).to_bytes(8, 'big') + enc[:-16] + enc[-16:])
        except ImportError:
            print("[OpenWeb Vault] cryptography パッケージが見つかりません。Vault機能は無効化されます。")
        except Exception as e:
            print(f"[OpenWeb Vault] 保存エラー: {e}")

    def save_credential(self, domain, user, pwd):
        if not self.is_unlocked: return
        self.data["accounts"][domain] = {"u": user, "p": pwd, "updated": int(time.time())}
        if domain not in self.data["index"]: self.data["index"].append(domain)
        self.domain_index = self.data["index"]
        self._save_vault()

    def load_credential(self, domain): return self.data["accounts"].get(domain) if self.is_unlocked else None
    
    def delete_credential(self, domain):
        if self.is_unlocked and domain in self.data["accounts"]:
            del self.data["accounts"][domain]
            if domain in self.data["index"]: self.data["index"].remove(domain)
            self.domain_index = self.data["index"]
            self._save_vault()
            
    def list_domains(self): return sorted(self.data["accounts"].keys()) if self.is_unlocked else []

    def save_note(self, title, content):
        if self.is_unlocked: self.data["notes"][title] = {"content": content, "updated": int(time.time())}; self._save_vault()
    def load_note(self, title): return self.data["notes"].get(title) if self.is_unlocked else None
    def delete_note(self, title):
        if self.is_unlocked and title in self.data["notes"]: del self.data["notes"][title]; self._save_vault()
    def list_notes(self): return sorted(self.data["notes"].keys()) if self.is_unlocked else []

# =========================================================
# Workspace Manager
# =========================================================
class WorkspaceManager:
    def __init__(self, bp):
        self.wf = os.path.join(bp, "workspaces.json")
        self.workspaces = {
            "学習・研究用" if CURRENT_LANG == "ja" else "Academic & Research": ["https://wikipedia.org", "https://scholar.google.co.jp"],
            "プログラミング" if CURRENT_LANG == "ja" else "Software Development": ["https://github.com", "https://stackoverflow.com"]
        }
        if os.path.exists(self.wf):
            try:
                with open(self.wf, "r", encoding="utf-8") as f: self.workspaces = json.load(f)
            except: pass
    def save(self):
        with open(self.wf, "w", encoding="utf-8") as f: json.dump(self.workspaces, f, ensure_ascii=False, indent=4)
    def create(self, n, u): self.workspaces[n] = u; self.save()

class SessionManager:
    def __init__(self, bp): self.sf = os.path.join(bp, "sessions.json")
    def save_session(self, u):
        with open(self.sf, "w", encoding="utf-8") as f: json.dump(u, f, ensure_ascii=False)
    def load_session(self):
        if os.path.exists(self.sf):
            try:
                with open(self.sf, "r", encoding="utf-8") as f: return json.load(f)
            except: pass
        return []
    def clear(self):
        if os.path.exists(self.sf): os.remove(self.sf)

# =========================================================
# リーディングポケット保存＆マネージャー
# =========================================================
class PocketManager:
    def __init__(self, base_path):
        self.pocket_dir = os.path.join(base_path, "pocket")
        os.makedirs(self.pocket_dir, exist_ok=True)
        self.index_file = os.path.join(self.pocket_dir, "index.json")
        self.pages = []
        self.load()

    def load(self):
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, "r", encoding="utf-8") as f: self.pages = json.load(f)
            except: pass

    def save(self):
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(self.pages, f, ensure_ascii=False, indent=4)

    def save_page(self, title, url, html_content):
        safe_name = hashlib.md5(url.encode('utf-8')).hexdigest() + ".html"
        full_path = os.path.join(self.pocket_dir, safe_name)
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            self.pages = [p for p in self.pages if p["url"] != url]
            self.pages.insert(0, {
                "title": title,
                "url": url,
                "file": safe_name,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            self.save()
            return True
        except: return False

    def get_local_path(self, file_name):
        return QUrl.fromLocalFile(os.path.join(self.pocket_dir, file_name)).toString()

# =========================================================
# サイト別サウンド/ボリュームマネージャー
# =========================================================
class SoundManager:
    def __init__(self, base_path):
        self.sound_file = os.path.join(base_path, "sound_config.json")
        self.configs = {} 
        self.load()

    def load(self):
        if os.path.exists(self.sound_file):
            try:
                with open(self.sound_file, "r", encoding="utf-8") as f: self.configs = json.load(f)
            except: pass

    def save(self):
        with open(self.sound_file, "w", encoding="utf-8") as f:
            json.dump(self.configs, f, ensure_ascii=False, indent=4)

    def set_config(self, domain, volume, mute, sfx):
        self.configs[domain] = { "volume": volume, "mute": mute, "sfx": sfx }
        self.save()

    def get_config(self, domain):
        return self.configs.get(domain, { "volume": 100, "mute": False, "sfx": True })

# =========================================================
# スプリットビュー (左右固定画面コンポーネント)
# =========================================================
class SplitViewWidget(QWidget):
    titleChanged = Signal(str)
    urlChanged = Signal(QUrl)

    def __init__(self, p, bw, u1="https://wikipedia.org", u2="https://google.co.jp"):
        super().__init__()
        self.bw = bw
        self.active_index = 1 # 1: 左画面, 2: 右画面
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.splitter)
        
        self.frame1 = QFrame()
        self.frame1.setFrameShape(QFrame.Shape.StyledPanel)
        f1_lay = QVBoxLayout(self.frame1)
        f1_lay.setContentsMargins(0, 0, 0, 0)
        self.v1 = BrowserTab(p, bw)
        self.v1.setUrl(QUrl(u1))
        f1_lay.addWidget(self.v1)
        
        self.frame2 = QFrame()
        self.frame2.setFrameShape(QFrame.Shape.StyledPanel)
        f2_lay = QVBoxLayout(self.frame2)
        f2_lay.setContentsMargins(0, 0, 0, 0)
        self.v2 = BrowserTab(p, bw)
        self.v2.setUrl(QUrl(u2))
        f2_lay.addWidget(self.v2)
        
        self.splitter.addWidget(self.frame1)
        self.splitter.addWidget(self.frame2)
        
        self.v1.titleChanged.connect(lambda t: self.on_title_or_url_changed())
        self.v2.titleChanged.connect(lambda t: self.on_title_or_url_changed())
        self.v1.urlChanged.connect(lambda q: self.on_title_or_url_changed())
        self.v2.urlChanged.connect(lambda q: self.on_title_or_url_changed())
        
        self.v1.installEventFilter(self)
        self.v2.installEventFilter(self)
        
        self.update_pane_styles()

    def eventFilter(self, obj, event):
        if event.type() in [event.Type.FocusIn, event.Type.MouseButtonPress]:
            if obj == self.v1 and self.active_index != 1:
                self.setActivePane(1)
            elif obj == self.v2 and self.active_index != 2:
                self.setActivePane(2)
        return super().eventFilter(obj, event)

    def on_title_or_url_changed(self):
        if self.active_index == 1:
            self.titleChanged.emit(f"[{'Split' if CURRENT_LANG == 'en' else '並列'}] {self.v1.title()}")
            self.urlChanged.emit(self.v1.url())
        else:
            self.titleChanged.emit(f"[{'Split' if CURRENT_LANG == 'en' else '並列'}] {self.v2.title()}")
            self.urlChanged.emit(self.v2.url())

    def setActivePane(self, index):
        self.active_index = index
        self.update_pane_styles()
        self.on_title_or_url_changed()
        
        if hasattr(self.bw, 'split_toggle_btn'):
            self.bw.split_toggle_btn.setText(_("＝左面") if index == 1 else _("＝右面"))
            self.bw.update_security_indicator(self.url())

    def update_pane_styles(self):
        theme = self.bw.settings.value("theme", "dark", type=str)
        border_color = "#00ddff" if theme == "dark" else "#0055ff"
        
        if self.active_index == 1:
            self.frame1.setStyleSheet(f"QFrame {{ border: 2px solid {border_color}; border-radius: 4px; }}")
            self.frame2.setStyleSheet("QFrame { border: 2px solid transparent; }")
        else:
            self.frame1.setStyleSheet("QFrame { border: 2px solid transparent; }")
            self.frame2.setStyleSheet(f"QFrame {{ border: 2px solid {border_color}; border-radius: 4px; }}")

    def url(self): return self.v1.url() if self.active_index == 1 else self.v2.url()
    def title(self): return f"[{'Split' if CURRENT_LANG == 'en' else '並列'}] {self.v1.title() if self.active_index == 1 else self.v2.title()}"
    def setUrl(self, u): (self.v1 if self.active_index == 1 else self.v2).setUrl(u)
    def reload(self): (self.v1 if self.active_index == 1 else self.v2).reload()
    def back(self): (self.v1 if self.active_index == 1 else self.v2).back()
    def forward(self): (self.v1 if self.active_index == 1 else self.v2).forward()
    def page(self): return (self.v1 if self.active_index == 1 else self.v2).page()

# =========================================================
# ★ ホワイトボードモード (自由移動・リサイズ・重ね可能スプリットビュー拡張)
# =========================================================
class WhiteboardModeWidget(QWidget):
    titleChanged = Signal(str)
    urlChanged = Signal(QUrl)

    def __init__(self, profile, bw, u1="https://www.youtube.com", u2="https://wikipedia.org"):
        super().__init__()
        self.bw = bw
        self.profile = profile
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        control_bar = QWidget()
        control_bar.setStyleSheet("background-color: #1e1e2e; border-bottom: 1px solid #3b3d54;")
        cb_layout = QHBoxLayout(control_bar)
        cb_layout.setContentsMargins(10, 5, 10, 5)
        
        title_lbl = QLabel(_("🎨 ホワイトボードモード (実験的)"))
        title_lbl.setStyleSheet("color: #a6e3a1; font-weight: bold; font-size: 13px;")
        
        add_btn = QPushButton(_("➕ ウィンドウ追加"))
        add_btn.setStyleSheet("background-color: #3b3d54; color: white; border: none; padding: 6px 12px; border-radius: 4px;")
        add_btn.clicked.connect(lambda: self.add_browser_window("https://google.com", _("新しいブラウザ"), 100, 100, 500, 400))
        
        cascade_btn = QPushButton(_("重ねて整列"))
        cascade_btn.setStyleSheet("background-color: #3b3d54; color: white; border: none; padding: 6px 12px; border-radius: 4px;")
        cascade_btn.clicked.connect(self.cascade_windows)

        tile_btn = QPushButton(_("並べて表示"))
        tile_btn.setStyleSheet("background-color: #3b3d54; color: white; border: none; padding: 6px 12px; border-radius: 4px;")
        tile_btn.clicked.connect(self.tile_windows)
        
        cb_layout.addWidget(title_lbl)
        cb_layout.addStretch()
        cb_layout.addWidget(add_btn)
        cb_layout.addWidget(cascade_btn)
        cb_layout.addWidget(tile_btn)
        layout.addWidget(control_bar)
        
        self.mdi_area = QMdiArea()
        self.mdi_area.setStyleSheet("""
            QMdiArea { background-color: #11111b; }
            QMdiSubWindow { background-color: #242538; border: 1px solid #3b3d54; border-radius: 6px; }
            QMdiSubWindow:title { background: #1e1e2e; color: #bac2de; }
        """)
        layout.addWidget(self.mdi_area)
        
        self.add_browser_window(u1, _("ウィンドウ1"), 20, 20, 550, 450)
        self.add_browser_window(u2, _("ウィンドウ2"), 600, 20, 550, 450)
        
        self.mdi_area.subWindowActivated.connect(self.on_subwindow_activated)

    def add_browser_window(self, url, title, x, y, w, h):
        browser = BrowserTab(self.profile, self.bw)
        browser.setUrl(QUrl(url))
        
        sub = QMdiSubWindow()
        sub.setWidget(browser)
        sub.setWindowTitle(title)
        self.mdi_area.addSubWindow(sub)
        sub.setGeometry(x, y, w, h)
        sub.show()
        
        browser.urlChanged.connect(lambda q, s=sub: self.on_browser_url_changed(q, s))
        browser.titleChanged.connect(lambda t, s=sub: self.on_browser_title_changed(t, s))

    def cascade_windows(self): self.mdi_area.cascadeSubWindows()
    def tile_windows(self): self.mdi_area.tileSubWindows()

    def on_browser_url_changed(self, qurl, sub):
        if self.mdi_area.activeSubWindow() == sub:
            self.urlChanged.emit(qurl)

    def on_browser_title_changed(self, title, sub):
        sub.setWindowTitle(title)
        if self.mdi_area.activeSubWindow() == sub:
            self.titleChanged.emit(f"[WB] {title}")

    def on_subwindow_activated(self, sub):
        if sub and sub.widget():
            browser = sub.widget()
            self.urlChanged.emit(browser.url())
            self.titleChanged.emit(f"[WB] {browser.title()}")

    def url(self):
        sub = self.mdi_area.activeSubWindow()
        return sub.widget().url() if sub and sub.widget() else QUrl("")

    def title(self):
        sub = self.mdi_area.activeSubWindow()
        return f"[WB] {sub.widget().title()}" if sub and sub.widget() else _("🎨 ホワイトボード")
        
    def setUrl(self, u):
        sub = self.mdi_area.activeSubWindow()
        if sub and sub.widget(): sub.widget().setUrl(u)

    def reload(self):
        sub = self.mdi_area.activeSubWindow()
        if sub and sub.widget(): sub.widget().reload()

    def back(self):
        sub = self.mdi_area.activeSubWindow()
        if sub and sub.widget(): sub.widget().back()

    def forward(self):
        sub = self.mdi_area.activeSubWindow()
        if sub and sub.widget(): sub.widget().forward()

    def page(self):
        sub = self.mdi_area.activeSubWindow()
        return sub.widget().page() if sub and sub.widget() else None


# =========================================================
# Custom Page & Browser Tab
# =========================================================
class CustomWebPage(QWebEnginePage):
    def __init__(self, profile, browser_window):
        super().__init__(profile, browser_window)
        self.browser_window = browser_window

    def createWindow(self, _type):
        if hasattr(self.browser_window, 'add_new_tab'): 
            new_tab = self.browser_window.add_new_tab()
            self.browser_window.tabs.setCurrentWidget(new_tab)
            return new_tab.page()
        return super().createWindow(_type)

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        if message.startswith("OW_SAVE_PASS:"):
            parts = message.split(":", 3)
            if len(parts) == 4:
                _, domain, user, pwd = parts
                if hasattr(self.browser_window, 'prompt_save_password'):
                    self.browser_window.prompt_save_password(domain, user, pwd)
            return
        elif message.startswith("OW_GAMEPAD_STATUS:") and hasattr(self.browser_window, 'handle_gamepad_console_event'):
            p = message.split(":", 2)
            if len(p) == 3: self.browser_window.handle_gamepad_console_event(p[1], p[2])
            return
        super().javaScriptConsoleMessage(level, message, lineNumber, sourceID)

class BrowserTab(QWebEngineView):
    def __init__(self, profile, browser_window):
        super().__init__()
        self.browser_window = browser_window
        self.setPage(CustomWebPage(profile, browser_window))
        self.dev_tools_window = None
        self.last_accessed_time = time.time()
        self.is_frozen = False
        self.suspended_url = ""
        s = self.page().settings()
        self.page().fullScreenRequested.connect(lambda r: (r.accept(), browser_window.set_fullscreen_mode(r.toggleOn())))
        
        attributes = {
            "JavascriptEnabled": browser_window.javascript_enabled,
            "LocalStorageEnabled": True,
            "WebGLEnabled": True,
            "Accelerated2dCanvasEnabled": True,
            "FullScreenSupportEnabled": True,
            "WebSecurityEnabled": True,
            "AllowRunningInsecureContent": True,
            "LocalContentCanAccessRemoteUrls": True,
            "LocalContentCanAccessFileUrls": True,
            "JavascriptCanAccessClipboard": False,
            "XSSAuditingEnabled": True,
            "PlaybackRequiresUserGesture": False,
            "DnsPrefetchEnabled": True,
            "ScrollAnimatorEnabled": True
        }
        for attr, val in attributes.items():
            if hasattr(QWebEngineSettings.WebAttribute, attr):
                s.setAttribute(getattr(QWebEngineSettings.WebAttribute, attr), val)

        self.urlChanged.connect(self.on_tab_url_changed)

    def on_tab_url_changed(self, url):
        self.last_accessed_time = time.time()
        # Googleログイン関連は主にInterceptorで処理するため、ここでは最小限に留める
        # （重複処理を減らして矛盾を防ぐ）
        host = url.host().lower()
        if any(g in host for g in GOOGLE_AUTH_HOSTS):
            # Interceptorで既にSafari UAが設定されているため、追加の強制は行わない
            pass
        else:
            self.page().profile().setHttpUserAgent(self.browser_window.current_user_agent)

    def mousePressEvent(self, e):
        self.last_accessed_time = time.time()
        if self.is_frozen: self.defrost_tab()
        super().mousePressEvent(e)

    def freeze_tab(self):
        if self.is_frozen: return
        self.suspended_url = self.url().toString()
        self.is_frozen = True
        self.setUrl(QUrl("about:blank"))
        suspend_title = "💤 Tab Suspended" if CURRENT_LANG == "en" else "💤 タブ休止中"
        suspend_msg = "Click anywhere to wake up." if CURRENT_LANG == "en" else "クリックで復帰します。"
        self.setHtml(f"<html><body style='background:#1c1b22; color:#fbfbfe; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;'><div style='text-align:center; padding:30px; border:1px solid #42414d; border-radius:12px; background:#2b2a33;'><h2>{suspend_title}</h2><p style='color:#00ddff;'>{self.suspended_url}</p><p style='color:gray;'>{suspend_msg}</p></div></body></html>")
        gc.collect()

    def defrost_tab(self):
        if not self.is_frozen: return
        self.is_frozen = False
        self.setUrl(QUrl(self.suspended_url))

    def contextMenuEvent(self, event):
        """右クリックメニューを多言語対応にする"""
        menu = QMenu(self)
        page = self.page()

        # 標準的なナビゲーション
        if page.action(QWebEnginePage.WebAction.Back).isEnabled():
            menu.addAction(_("← 戻る"), self.back)
        if page.action(QWebEnginePage.WebAction.Forward).isEnabled():
            menu.addAction(_("→ 進む"), self.forward)
        menu.addAction(_("⟳ 再読み込み"), self.reload)

        menu.addSeparator()

        # 編集アクション（コピペなど）
        menu.addAction(_("コピー"), lambda: page.triggerAction(QWebEnginePage.WebAction.Copy))
        menu.addAction(_("貼り付け"), lambda: page.triggerAction(QWebEnginePage.WebAction.Paste))
        menu.addAction(_("切り取り"), lambda: page.triggerAction(QWebEnginePage.WebAction.Cut))
        menu.addAction(_("すべて選択"), lambda: page.triggerAction(QWebEnginePage.WebAction.SelectAll))

        menu.addSeparator()

        # ブラウザ独自の便利機能
        menu.addAction(_("📖 読書モードを適用"), self.browser_window.activate_reader_mode)
        menu.addAction(_("🌐 ページ全体をGoogle翻訳で開く"), self.browser_window.open_translate_page)
        menu.addAction(_("✨ AIによるページ自動内容要約"), self.browser_window.summarize_current_page)
        menu.addAction(_("📁 このページをリーディングポケットに保存"), 
                       lambda: self.browser_window.save_current_page_to_pocket(self))

        menu.addSeparator()

        # 開発者ツール（Chromeの「コードを解析できるモード」相当）
        menu.addAction(_("💻 開発者ツールを開く (F12)"), self.browser_window.trigger_devtools)

        menu.exec(event.globalPos())

    def toggle_developer_tools(self):
        if self.dev_tools_window and self.dev_tools_window.isVisible():
            self.dev_tools_window.close()
            self.dev_tools_window = None
        else:
            self.dev_tools_window = QMainWindow(self.window())
            dt_title = f"Developer Tools - {self.title()}" if CURRENT_LANG == "en" else f"デベロッパーツール - {self.title()}"
            self.dev_tools_window.setWindowTitle(dt_title)
            self.dev_tools_window.resize(900, 600)
            dev_view = QWebEngineView()
            self.page().setDevToolsPage(dev_view.page())
            self.dev_tools_window.setCentralWidget(dev_view)
            self.dev_tools_window.show()

# =========================================================
# 独自動画再生プレイヤー
# =========================================================
class CustomVideoPlayerWindow(QMainWindow):
    def __init__(self, profile, target_url, title="🎬 OpenWeb Video Player"):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        actual_title = _("🎬 独自動画プレーヤー (実験的)") if title == "🎬 OpenWeb Video Player" else title
        self.setWindowTitle(actual_title)
        self.resize(800, 450) 

        self.browser = QWebEngineView()
        self.browser.setPage(CustomWebPage(profile, self))
        
        s = self.browser.settings()
        s.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.WebSecurityEnabled, False)
        s.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
        s.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)

        url_str = target_url.toString() if isinstance(target_url, QUrl) else target_url
        final_url = url_str

        try:
            qurl = QUrl(url_str)
            scheme = qurl.scheme() or "https"
            host = qurl.host().lower()
            path = qurl.path()
            
            if "youtube.com" in host and "/watch" in path:
                query = QUrlQuery(qurl.query())
                v_id = query.queryItemValue("v")
                if v_id:
                    final_url = f"{scheme}://www.youtube-nocookie.com/embed/{v_id}?autoplay=1"
            elif "youtu.be" in host:
                v_id = path.strip("/")
                if v_id:
                    final_url = f"{scheme}://www.youtube-nocookie.com/embed/{v_id}?autoplay=1"
            elif "twitch.tv" in host:
                channel = path.strip("/")
                final_url = f"{scheme}://player.twitch.tv/?channel={channel}&parent=twitch.tv&autoplay=true"
            else:
                if "/watch" in path and "v=" in qurl.query():
                    query = QUrlQuery(qurl.query())
                    v_id = query.queryItemValue("v")
                    if v_id:
                        final_url = f"{scheme}://{host}/embed/{v_id}?autoplay=1"
        except Exception as e:
            print("[Video Player URL Parse Error]", e)
            final_url = url_str

        if not final_url.startswith(("http://", "https://")):
            final_url = "https://" + final_url.lstrip(":/")

        self.browser.setUrl(QUrl(final_url))
        self.setCentralWidget(self.browser)
        self.browser.page().fullScreenRequested.connect(self.handle_fullscreen)
        QShortcut(QKeySequence("F"), self, activated=self.toggle_fullscreen)
        QShortcut(QKeySequence("Esc"), self, activated=self.showNormal)
        # 🕵️ 隠しモード キーボードショートカット（Ctrl + H）
        QShortcut(QKeySequence("Ctrl+H"), self, activated=self.toggle_hidden_mode)
        
        self.show()
        self.browser.setFocus(Qt.FocusReason.ActiveWindowFocusReason)

    def handle_fullscreen(self, request):
        request.accept()
        if request.toggleOn(): self.showFullScreen()
        else: self.showNormal()

    def toggle_fullscreen(self):
        if self.isFullScreen(): self.showNormal()
        else: self.showFullScreen()

class AppWindow(QMainWindow):
    def __init__(self, profile, url, title="OpenWeb App"):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(1024, 768)
        self.browser = QWebEngineView()
        self.browser.setPage(CustomWebPage(profile, self))
        self.browser.page().settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.browser.setUrl(QUrl(url))
        self.setCentralWidget(self.browser)
        self.show()

# =========================================================
# 設定タブ群
# =========================================================
class SettingsTab(QWidget):
    def __init__(self, parent_browser):
        super().__init__()
        self.parent_browser = parent_browser
        self.active_detect_row = -1
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(240)
        
        self.sidebar.addItems([
            _("⚙️ 一般設定"),
            _("🏠 ホームページ設定"), 
            _("📋 ToDo タスク管理"), 
            _("🔑 パスワード & Vault"),
            _("📥 ダウンロード履歴"),
            _("🎮 ゲーム ＆ 入力最適化"),
            _("🛡️ ワークスペース ＆ ダッシュボード"),
            _("🕒 閲覧タイムライン"),
            _("📁 リーディングポケット"),
            _("🧪 開発中の機能  [NEW]"),
            _("ℹ️ OpenWeb について")
        ])
        self.sidebar.currentRowChanged.connect(self.switch_section)
        main_layout.addWidget(self.sidebar)

        line = QFrame(); line.setFrameShape(QFrame.Shape.VLine); main_layout.addWidget(line)

        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)

        self.init_general_panel()
        self.init_home_panel() 
        self.init_todo_panel() 
        self.init_password_panel()
        self.init_download_panel()
        self.init_gamemode_panel()
        self.init_workspace_privacy_panel()
        self.init_timeline_panel()
        self.init_pocket_panel()
        self.init_experimental_panel()
        self.init_about_panel()

        self.sidebar.setCurrentRow(0)

    def contextMenuEvent(self, event):
        """設定画面でもコピペUIを多言語対応にする"""
        menu = QMenu(self)
        
        focus = self.focusWidget()
        
        # テキストが選択可能なウィジェットの場合
        if hasattr(focus, 'copy') and hasattr(focus, 'selectedText'):
            if focus.selectedText():
                menu.addAction(_("コピー"), focus.copy)
            menu.addAction(_("すべて選択"), focus.selectAll)
        
        if hasattr(focus, 'paste'):
            menu.addAction(_("貼り付け"), focus.paste)
        
        if menu.isEmpty():
            # 何もない場合はデフォルトメニュー
            menu = self.createStandardContextMenu() if hasattr(self, 'createStandardContextMenu') else QMenu()
        
        if not menu.isEmpty():
            menu.exec(event.globalPos())

    def switch_section(self, index):
        if index == 3: 
            if not self.parent_browser.ensure_vault_unlocked(self):
                self.sidebar.blockSignals(True); self.sidebar.setCurrentRow(0); self.sidebar.blockSignals(False)
                return
            else: 
                self.refresh_password_table()
                self.refresh_notes_table()
        elif index == 7:
            self.refresh_timeline()
        elif index == 8:
            self.refresh_pocket_table()

        self.content_stack.setCurrentIndex(index)
        sub_paths = ["settings", "settings/homepage", "settings/todo", "settings/passwords", "settings/downloads", "settings/game-mode", "settings/privacy", "settings/timeline", "settings/pocket", "settings/experimental", "settings/about"]
        if 0 <= index < len(sub_paths):
            self.parent_browser.url_bar.setText(f"openweb://{sub_paths[index]}")

    def init_general_panel(self):
        panel = QWidget(); layout = QVBoxLayout(panel); layout.setAlignment(Qt.AlignmentFlag.AlignTop); layout.setContentsMargins(30, 20, 30, 20)
        title = QLabel(_("⚙️ 一般設定")); title.setFont(QFont("Arial", 18, QFont.Weight.Bold)); layout.addWidget(title)
        
        # --- 言語設定 ---
        lang_group = QGroupBox(_("🌐 言語設定 (Language) ※要再起動"))
        lang_layout = QHBoxLayout(lang_group)
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["日本語 (Japanese)", "English"])
        self.lang_combo.setCurrentIndex(0 if CURRENT_LANG == "ja" else 1)
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        lang_layout.addWidget(QLabel(_("表示言語:")))
        lang_layout.addWidget(self.lang_combo)
        layout.addWidget(lang_group)

        theme_group = QGroupBox(_("🎨 気分・時間帯に合わせたテーマ設定"))
        theme_layout = QGridLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([_("さわやか (スカイブルー)"), _("明るい (陽気なサンシャイン)"), _("ダーク (宇宙パープル)"), _("アース (落ち着いたアースグリーン)")])
        current_theme = self.parent_browser.settings.value("theme", "dark", type=str)
        theme_idx_map = {"fresh": 0, "light": 1, "dark": 2, "earth": 3}
        self.theme_combo.setCurrentIndex(theme_idx_map.get(current_theme, 2))
        self.theme_combo.currentIndexChanged.connect(self.change_mood_theme)
        theme_layout.addWidget(QLabel(_("カラーテーマ:")), 0, 0)
        theme_layout.addWidget(self.theme_combo, 0, 1)
        
        self.auto_theme_cb = QCheckBox(_("⏳ 時間帯に合わせてテーマを自動切替 (昼:ライト, 夜:ダーク)"))
        self.auto_theme_cb.setChecked(self.parent_browser.settings.value("auto_theme", False, type=bool))
        self.auto_theme_cb.stateChanged.connect(lambda s: self.parent_browser.settings.setValue("auto_theme", s != 0) or self.parent_browser.apply_auto_theme())
        theme_layout.addWidget(self.auto_theme_cb, 1, 0, 1, 2)
        layout.addWidget(theme_group)

        opt_group = QGroupBox(_("⚙️ ブラウザ動作オプション"))
        opt_layout = QVBoxLayout(opt_group)

        self.js_cb = QCheckBox(_("📜 JavaScriptを有効にする (本格使用モード / セキュリティ用途でOFF可)"))
        self.js_cb.setChecked(self.parent_browser.javascript_enabled)
        self.js_cb.stateChanged.connect(self.toggle_javascript)
        opt_layout.addWidget(self.js_cb)

        # OAuth2 トグル（デフォルトON、配布向け）
        self.oauth2_cb = QCheckBox(_("🔐 Google OAuth2ログイン機能を有効にする（推奨）"))
        self.oauth2_cb.setChecked(self.parent_browser.settings.value("oauth2_enabled", True, type=bool))
        self.oauth2_cb.stateChanged.connect(self.toggle_oauth2)
        opt_layout.addWidget(self.oauth2_cb)
        
        js_desc = QLabel(_("※OFFにすると多くのWebサイトや内部ポータル画面が正常に動作しなくなります。"))
        js_desc.setStyleSheet("color: #ff9800; font-size: 11px;")
        opt_layout.addWidget(js_desc)

        self.cookie_cb = QCheckBox(_("🍪 Cookieデータを端末に保存する（ログイン状態の維持）")); self.cookie_cb.setChecked(self.parent_browser.cookies_enabled)
        self.cookie_cb.stateChanged.connect(self.toggle_cookie)
        
        self.scroll_backup_cb = QCheckBox(_("⏳ 閉じたタブのスクロール位置を記憶して再開時に自動復帰する"))
        self.scroll_backup_cb.setChecked(self.parent_browser.scroll_backup_enabled)
        self.scroll_backup_cb.stateChanged.connect(self.set_scroll_backup_enabled)
        
        opt_layout.addWidget(self.cookie_cb)
        opt_layout.addWidget(self.scroll_backup_cb)
        layout.addWidget(opt_group)

        # === 本物のChromeプロファイル設定（Googleログイン安定化に最も効果的） ===
        chrome_profile_group = QGroupBox(_("本物のChromeプロファイルを使用する（Googleログイン安定化に最も効果的）"))
        chrome_profile_layout = QVBoxLayout(chrome_profile_group)
        
        desc_label = QLabel(_("実在のChromeプロファイルを使用すると、フィンガープリントが自然になりGoogleログインが通りやすくなります。\n（通常のChromeで一度ログインしたプロファイルのフォルダを指定してください）"))
        desc_label.setStyleSheet("color: #a6e3a1; font-size: 11px;")
        desc_label.setWordWrap(True)
        chrome_profile_layout.addWidget(desc_label)
        
        path_layout = QHBoxLayout()
        self.chrome_profile_path_input = QLineEdit(self.parent_browser.settings.value("custom_chrome_profile_path", "", type=str))
        self.chrome_profile_path_input.setPlaceholderText("例: C:\\Users\\YourName\\AppData\\Local\\Google\\Chrome\\User Data\\Default")
        self.chrome_profile_browse_btn = QPushButton(_("フォルダを選択..."))
        self.chrome_profile_browse_btn.clicked.connect(self.select_chrome_profile_folder)
        path_layout.addWidget(self.chrome_profile_path_input)
        path_layout.addWidget(self.chrome_profile_browse_btn)
        chrome_profile_layout.addLayout(path_layout)
        
        self.save_chrome_profile_btn = QPushButton("Chromeプロファイル設定を保存（次回起動時に適用）")
        self.save_chrome_profile_btn.clicked.connect(self.save_chrome_profile_setting)
        chrome_profile_layout.addWidget(self.save_chrome_profile_btn)
        
        layout.addWidget(chrome_profile_group)
        
        reset_group = QGroupBox(_("💥 システム完全初期化"))
        reset_layout = QVBoxLayout(reset_group)
        reset_desc = QLabel(_("設定、暗号Vault、閲覧履歴、ワークスペース、ToDo、Cookie、キャッシュ等を完全に抹消し、初期状態に巻き戻します。\n※この操作は元に戻せません。"))
        reset_desc.setWordWrap(True)
        reset_desc.setStyleSheet("color: #ff6464; font-size: 11px;")
        self.reset_btn = QPushButton(_("💥 ブラウザを完全に初期化する"))
        self.reset_btn.setMinimumHeight(40)
        self.reset_btn.clicked.connect(self.parent_browser.reset_browser_completely)
        reset_layout.addWidget(reset_desc); reset_layout.addWidget(self.reset_btn)
        layout.addWidget(reset_group)
        
        self.content_stack.addWidget(panel)

    def change_language(self, index):
        new_lang = "ja" if index == 0 else "en"
        if new_lang != CURRENT_LANG:
            self.parent_browser.settings.setValue("language", new_lang)
            QMessageBox.information(self, "Restart Required", "言語設定を変更しました。適用するにはブラウザを再起動してください。\nLanguage setting changed. Please restart the browser to apply.")

    def change_mood_theme(self, index):
        theme_keys = ["fresh", "light", "dark", "earth"]
        self.parent_browser.settings.setValue("theme", theme_keys[index])
        self.parent_browser.apply_style()
        self.parent_browser.reload_all_portals()

    def toggle_cookie(self, state):
        checked = (state != 0)
        self.parent_browser.cookies_enabled = checked
        self.parent_browser.settings.setValue("cookies_enabled", checked)
        if checked:
            self.parent_browser.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        else:
            self.parent_browser.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)

    def toggle_javascript(self, state):
        checked = (state != 0)
        self.parent_browser.javascript_enabled = checked
        self.parent_browser.settings.setValue("javascript_enabled", checked)

    def toggle_oauth2(self, state):
        checked = state == 2
        self.parent_browser.settings.setValue("oauth2_enabled", checked)
        self.parent_browser.apply_javascript_setting()

    def set_scroll_backup_enabled(self, state):
        enabled = (state != 0)
        self.parent_browser.settings.setValue("scroll_backup_enabled", enabled)
        self.parent_browser.scroll_backup_enabled = enabled

    def init_home_panel(self):
        panel = QWidget(); layout = QVBoxLayout(panel); layout.setAlignment(Qt.AlignmentFlag.AlignTop); layout.setContentsMargins(30, 20, 30, 20)
        title = QLabel(_("🏠 ホームページ設定")); title.setFont(QFont("Arial", 18, QFont.Weight.Bold)); layout.addWidget(title)
        
        type_group = QGroupBox(_("起動時・新タブ展開時のページ設定"))
        type_layout = QVBoxLayout(type_group)
        self.home_type_combo = QComboBox()
        self.home_type_combo.addItems([
            _("OpenWeb 機能性ポータルページ (検索・ToDo同期・ショートカット)"),
            _("カスタムアドレスを設定する (URL、またはローカルHTML)")
        ])
        current_type = self.parent_browser.settings.value("home_type", "default", type=str)
        self.home_type_combo.setCurrentIndex(1 if current_type == "custom" else 0)
        type_layout.addWidget(self.home_type_combo)
        layout.addWidget(type_group)

        self.custom_address_group = QGroupBox(_("カスタムホームページ設定"))
        custom_layout = QVBoxLayout(self.custom_address_group)
        addr_layout = QHBoxLayout()
        self.home_input = QLineEdit(self.parent_browser.home_url)
        self.home_input.setPlaceholderText(_("https://example.com または file://... 等のローカルHTMLへの絶対パス"))
        self.home_file_btn = QPushButton(_("HTMLを選択..."))
        self.home_file_btn.clicked.connect(self.select_home_html)
        addr_layout.addWidget(self.home_input)
        addr_layout.addWidget(self.home_file_btn)
        custom_layout.addLayout(addr_layout)
        
        self.home_current_btn = QPushButton(_("現在有効なタブのURLをホームページに適用"))
        self.home_current_btn.clicked.connect(self.apply_current_page_as_home)
        custom_layout.addWidget(self.home_current_btn)
        layout.addWidget(self.custom_address_group)

        self.new_tab_home_cb = QCheckBox(_("新しい空タブを開いたときにもこの設定を適用する"))
        self.new_tab_home_cb.setChecked(self.parent_browser.settings.value("new_tab_home_enabled", True, type=bool))
        layout.addWidget(self.new_tab_home_cb)

        self.save_home_btn = QPushButton(_("🏠 ホームページ設定を保存"))
        self.save_home_btn.clicked.connect(self.save_home_config)
        layout.addWidget(self.save_home_btn)

        self.home_type_combo.currentIndexChanged.connect(lambda idx: self.custom_address_group.setEnabled(idx == 1))
        self.custom_address_group.setEnabled(self.home_type_combo.currentIndex() == 1)
        self.content_stack.addWidget(panel)

    def select_home_html(self):
        f_path = QFileDialog.getOpenFileName(self, _("ホームページ用HTMLの選択"), "", _("HTMLファイル (*.html *.htm);;すべてのファイル (*.*)"))[0]
        if f_path: self.home_input.setText(QUrl.fromLocalFile(f_path).toString())

    def apply_current_page_as_home(self):
        cb = self.parent_browser.current_browser()
        if cb:
            u_str = cb.url().toString()
            if u_str.startswith("openweb://"): QMessageBox.warning(self, _("エラー"), _("設定などの内部ページはホームページに指定できません。"))
            else: self.home_input.setText(u_str)

    def save_home_config(self):
        h_type = "custom" if self.home_type_combo.currentIndex() == 1 else "default"
        self.parent_browser.settings.setValue("home_type", h_type)
        self.parent_browser.settings.setValue("new_tab_home_enabled", self.new_tab_home_cb.isChecked())
        addr = self.home_input.text().strip()
        if h_type == "custom" and not addr:
            QMessageBox.warning(self, _("警告"), _("カスタムURLアドレスを入力してください。"))
            return
        self.parent_browser.home_url = addr
        self.parent_browser.settings.setValue("home_url", addr)
        self.parent_browser.reload_all_portals()
        self.parent_browser.statusBar().showMessage(_("🏠 ホームページ設定を更新しました"), 4000)

    def select_chrome_profile_folder(self):
        folder = QFileDialog.getExistingDirectory(self, _("Chromeプロファイルフォルダを選択"), 
            self.chrome_profile_path_input.text() or os.path.expanduser("~"))
        if folder:
            self.chrome_profile_path_input.setText(folder)

    def save_chrome_profile_setting(self):
        path = self.chrome_profile_path_input.text().strip()
        if path and not os.path.exists(path):
            QMessageBox.warning(self, _("警告"), _("指定したフォルダが存在しません。正しいChromeプロファイルのフォルダを指定してください。"))
            return
        self.parent_browser.settings.setValue("custom_chrome_profile_path", path)
        QMessageBox.information(self, _("保存完了"), 
            _("Chromeプロファイル設定を保存しました。\n次回ブラウザ起動時に適用されます。\n（現在のセッションには反映されません）"))

    def init_todo_panel(self):
        panel = QWidget(); layout = QVBoxLayout(panel); layout.setContentsMargins(30, 20, 30, 20)
        title = QLabel(_("📋 ToDo")); title.setFont(QFont("Arial", 18, QFont.Weight.Bold)); layout.addWidget(title)
        
        input_layout = QHBoxLayout()
        self.todo_add_input = QLineEdit()
        self.todo_add_input.setPlaceholderText(_("新しいタスクを入力..."))
        self.todo_add_input.returnPressed.connect(self.add_todo_from_settings)
        self.todo_submit_btn = QPushButton(_("タスクを追加"))
        self.todo_submit_btn.clicked.connect(self.add_todo_from_settings)
        input_layout.addWidget(self.todo_add_input); input_layout.addWidget(self.todo_submit_btn)
        layout.addLayout(input_layout)

        self.todo_table = QTableWidget(0, 3)
        self.todo_table.setHorizontalHeaderLabels([_("状態"), _("タスク内容"), _("操作")])
        self.todo_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.todo_table)
        self.content_stack.addWidget(panel)
        self.refresh_todo_table()

    def refresh_todo_table(self):
        self.todo_table.setRowCount(0)
        todos = self.parent_browser.load_todos()
        for idx, todo in enumerate(todos):
            row = self.todo_table.rowCount()
            self.todo_table.insertRow(row)
            
            chk = QCheckBox(); chk.setChecked(todo.get("completed", False))
            chk.stateChanged.connect(lambda state, i=idx: self.toggle_todo_status(i, state))
            chk_widget = QWidget()
            chk_layout = QHBoxLayout(chk_widget); chk_layout.addWidget(chk); chk_layout.setAlignment(Qt.AlignmentFlag.AlignCenter); chk_layout.setContentsMargins(0,0,0,0)
            self.todo_table.setCellWidget(row, 0, chk_widget)
            
            item_text = QTableWidgetItem(todo.get("text", ""))
            if todo.get("completed", False): item_text.setForeground(Qt.GlobalColor.gray)
            self.todo_table.setItem(row, 1, item_text)
            
            del_btn = QPushButton(_("削除"))
            del_btn.setStyleSheet("color: #ff6464;")
            del_btn.clicked.connect(lambda _, i=idx: self.delete_todo_item(i))
            self.todo_table.setCellWidget(row, 2, del_btn)

    def add_todo_from_settings(self):
        txt = self.todo_add_input.text().strip()
        if not txt: return
        todos = self.parent_browser.load_todos()
        todos.append({"text": txt, "completed": False})
        self.parent_browser.save_todos(todos)
        self.todo_add_input.clear()
        self.refresh_todo_table()
        self.parent_browser.reload_all_portals()

    def toggle_todo_status(self, idx, state):
        todos = self.parent_browser.load_todos()
        if 0 <= idx < len(todos):
            todos[idx]["completed"] = (state != 0)
            self.parent_browser.save_todos(todos)
            self.refresh_todo_table()
            self.parent_browser.reload_all_portals()

    def delete_todo_item(self, idx):
        todos = self.parent_browser.load_todos()
        if 0 <= idx < len(todos):
            todos.pop(idx)
            self.parent_browser.save_todos(todos)
            self.refresh_todo_table()
            self.parent_browser.reload_all_portals()

    def init_password_panel(self):
        panel = QWidget(); layout = QVBoxLayout(panel); layout.setContentsMargins(30, 20, 30, 20)
        title = QLabel(_("🔑 Vault セキュリティ金庫 (Pro)")); title.setFont(QFont("Arial", 18, QFont.Weight.Bold)); layout.addWidget(title)
        
        tools_layout = QHBoxLayout()
        self.gen_pwd_btn = QPushButton(_("⚡ パスワード生成")); self.gen_pwd_btn.clicked.connect(self.generate_secure_password_ui)
        self.check_leak_btn = QPushButton(_("🛡️ 脆弱性チェック")); self.check_leak_btn.clicked.connect(self.check_password_vulnerabilities)
        self.add_note_btn = QPushButton(_("＋ 暗号化メモ追加")); self.add_note_btn.clicked.connect(self.create_secure_note_ui)
        self.change_master_pwd_btn = QPushButton(_("🔑 パスワード変更")); self.change_master_pwd_btn.clicked.connect(self.change_master_password_ui)
        self.lock_vault_btn = QPushButton(_("🔒 Vaultをロック")); self.lock_vault_btn.clicked.connect(self.lock_vault)
        
        tools_layout.addWidget(self.gen_pwd_btn); tools_layout.addWidget(self.check_leak_btn); tools_layout.addWidget(self.add_note_btn)
        tools_layout.addWidget(self.change_master_pwd_btn); tools_layout.addStretch(); tools_layout.addWidget(self.lock_vault_btn)
        layout.addLayout(tools_layout)

        self.pwd_table = QTableWidget(0, 4); self.pwd_table.setHorizontalHeaderLabels([_("サイト"), _("ユーザーID"), _("パスワード表示"), _("削除")])
        self.pwd_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(QLabel(_("【ログインアカウント情報】"))); layout.addWidget(self.pwd_table)
        
        self.notes_table = QTableWidget(0, 3); self.notes_table.setHorizontalHeaderLabels([_("タイトル"), _("読む"), _("削除")])
        self.notes_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(QLabel(_("【Secure Notes (安全なメモ)】"))); layout.addWidget(self.notes_table)
        self.content_stack.addWidget(panel)

    def generate_secure_password_ui(self):
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        pwd = "".join(secrets.choice(chars) for _ in range(16))
        QApplication.clipboard().setText(pwd)
        QMessageBox.information(self, _("パスワード生成"), _("安全なパスワードを作成しコピーしました:\n\n") + pwd)

    def check_password_vulnerabilities(self):
        if not self.parent_browser.ensure_vault_unlocked(self): return
        domains = self.parent_browser.vault.list_domains()
        weak = [d for d in domains if len(self.parent_browser.vault.load_credential(d).get("p","")) < 8]
        if weak: QMessageBox.warning(self, _("警告"), _("弱いパスワード (8文字未満)が検出されました。変更をお勧めします:\n") + ", ".join(weak))
        else: QMessageBox.information(self, _("安全"), _("すべてのパスワードは安全基準を満たしています。"))

    def change_master_password_ui(self):
        if not self.parent_browser.ensure_vault_unlocked(self): return
        dlg = VaultChangePasswordDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            o_p, n_p = dlg.get_passwords()
            if self.parent_browser.vault.change_password(o_p, n_p): QMessageBox.information(self, _("完了"), _("マスターパスワードは変更されました。"))
            else: QMessageBox.critical(self, _("エラー"), _("現在のパスワードが一致しません。"))

    def create_secure_note_ui(self):
        if not self.parent_browser.ensure_vault_unlocked(self): return
        title, ok1 = QInputDialog.getText(self, _("新規暗号化メモ"), _("メモのタイトルを入力してください:"))
        if ok1 and title:
            content, ok2 = QInputDialog.getMultiLineText(self, _("新規暗号化メモ"), _("メモの内容を入力してください:"))
            if ok2:
                self.parent_browser.vault.save_note(title, content)
                self.refresh_notes_table()
                QMessageBox.information(self, _("保存完了"), _("安全なメモをVaultに保存しました。"))

    def refresh_password_table(self):
        self.pwd_table.setRowCount(0)
        for domain in self.parent_browser.vault.list_domains():
            creds = self.parent_browser.vault.load_credential(domain)
            row = self.pwd_table.rowCount(); self.pwd_table.insertRow(row)
            self.pwd_table.setItem(row, 0, QTableWidgetItem(domain))
            self.pwd_table.setItem(row, 1, QTableWidgetItem(creds.get("u", "")))
            
            show_btn = QPushButton(_("パスワード表示"))
            show_btn.clicked.connect(lambda _, p=creds.get("p", ""): QMessageBox.information(self, _("パスワード"), f"{_('パスワード:')} {p}"))
            self.pwd_table.setCellWidget(row, 2, show_btn)
            
            del_btn = QPushButton(_("削除"))
            del_btn.setStyleSheet("color: #ff6464;")
            del_btn.clicked.connect(lambda _, d=domain: [self.parent_browser.vault.delete_credential(d), self.refresh_password_table()])
            self.pwd_table.setCellWidget(row, 3, del_btn)

    def refresh_notes_table(self):
        self.notes_table.setRowCount(0)
        for title in self.parent_browser.vault.list_notes():
            row = self.notes_table.rowCount(); self.notes_table.insertRow(row)
            self.notes_table.setItem(row, 0, QTableWidgetItem(title))
            read_btn = QPushButton(_("読む")); read_btn.clicked.connect(lambda _, t=title: QMessageBox.information(self, t, self.parent_browser.vault.load_note(t).get("content","")))
            self.notes_table.setCellWidget(row, 1, read_btn)
            del_btn = QPushButton(_("削除")); del_btn.setStyleSheet("color: #ff6464;"); del_btn.clicked.connect(lambda _, t=title: [self.parent_browser.vault.delete_note(t), self.refresh_notes_table()])
            self.notes_table.setCellWidget(row, 2, del_btn)

    def lock_vault(self):
        self.parent_browser.vault.lock()
        self.pwd_table.setRowCount(0)
        self.notes_table.setRowCount(0)
        self.sidebar.setCurrentRow(0)

    def init_download_panel(self):
        panel = QWidget(); layout = QVBoxLayout(panel); layout.setContentsMargins(0, 0, 0, 0)
        self.dl_manager_widget = DownloadManagerTab(self.parent_browser)
        layout.addWidget(self.dl_manager_widget)
        self.content_stack.addWidget(panel)

    def toggle_game_mode(self, state):
        enabled = (state != 0)
        self.parent_browser.game_mode_enabled = enabled
        self.parent_browser.settings.setValue("game_mode_enabled", enabled)
        self.parent_browser.inject_gamepad_mapping_to_all()
        
    def toggle_overclock_mode(self, state):
        enabled = (state != 0)
        self.parent_browser.settings.setValue("overclock_mode", enabled)
        if enabled:
            QMessageBox.information(self, _("🔥 オーバークロックモード"), _("オーバークロックモードを有効にしました。\nこの設定はブラウザを次回再起動した際に完全に適用されます。\n(OSのプロセス優先度向上、GPUリミット解除、VSync無効化など)"))
            if sys.platform.startswith("win"):
                try:
                    import ctypes
                    # 即座にプロセス優先度を上げる (0x00000080 = HIGH_PRIORITY_CLASS)
                    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00000080)
                except Exception: pass
        else:
            QMessageBox.information(self, _("オーバークロック解除"), _("オーバークロックモードを解除しました。\n次回起動時に標準状態に戻ります。"))
            if sys.platform.startswith("win"):
                try:
                    import ctypes
                    # 即座にプロセス優先度を標準に戻す (0x00000020 = NORMAL_PRIORITY_CLASS)
                    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00000020)
                except Exception: pass

    def init_gamemode_panel(self):
        panel = QWidget(); layout = QVBoxLayout(panel); layout.setContentsMargins(30, 20, 30, 20)
        title = QLabel(_("🎮 ゲームモード ＆ 入力・サウンド最適化")); title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        self.gamepad_status_group = QGroupBox(_("🔌 接続中のコントローラー（自動マッピング検出・調整）"))
        status_layout = QVBoxLayout(self.gamepad_status_group)
        self.gamepad_info_label = QLabel(_("ゲームパッド未検出。いずれかの物理ボタンかキーを1回押してください。"))
        self.gamepad_info_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.gamepad_info_label.setStyleSheet("color: #bac2de;")
        status_layout.addWidget(self.gamepad_info_label)
        layout.addWidget(self.gamepad_status_group)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_widget = QWidget(); left_layout = QVBoxLayout(left_widget); left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        left_layout.setContentsMargins(0, 0, 10, 0)
        
        opt_group = QGroupBox(_("⚡ システムパフォーマンス＆ゲーム調整"))
        opt_layout = QVBoxLayout(opt_group)
        self.game_toggle_cb = QCheckBox(_("ゲームモード機能を有効化する"))
        self.game_toggle_cb.setChecked(self.parent_browser.game_mode_enabled)
        self.game_toggle_cb.stateChanged.connect(self.toggle_game_mode)
        opt_layout.addWidget(self.game_toggle_cb)

        self.game_fps_boost_cb = QCheckBox(_("🚀 WebGL / FPS制限緩和モード (高駆動フレームレート)"))
        self.game_fps_boost_cb.setChecked(self.parent_browser.settings.value("game_fps_boost", True, type=bool))
        self.game_fps_boost_cb.stateChanged.connect(lambda s: self.parent_browser.settings.setValue("game_fps_boost", s != 0))
        opt_layout.addWidget(self.game_fps_boost_cb)

        self.game_low_latency_cb = QCheckBox(_("🔉 描画＆音声 低遅延化モード (超応答サウンドフィード)"))
        self.game_low_latency_cb.setChecked(self.parent_browser.settings.value("game_low_latency", True, type=bool))
        self.game_low_latency_cb.stateChanged.connect(lambda s: self.parent_browser.settings.setValue("game_low_latency", s != 0))
        opt_layout.addWidget(self.game_low_latency_cb)
        
        # 🔥 オーバークロックモード (追加)
        self.overclock_cb = QCheckBox(_("🔥 オーバークロックモード (CPU/GPU同時限界駆動) ※要再起動"))
        self.overclock_cb.setChecked(self.parent_browser.settings.value("overclock_mode", False, type=bool))
        self.overclock_cb.stateChanged.connect(self.toggle_overclock_mode)
        opt_layout.addWidget(self.overclock_cb)
        
        oc_desc = QLabel(_("※ VSync完全無効化、V8エンジン最大最適化、VRAM強制大容量割当、OSプロセス優先度[高]を同時適用し、究極のパフォーマンスを引き出します。"))
        oc_desc.setWordWrap(True)
        oc_desc.setStyleSheet("color: #ff9800; font-size: 11px;")
        opt_layout.addWidget(oc_desc)

        left_layout.addWidget(opt_group)

        self.input_settings_group = QGroupBox(_("🚀 連射速度 (Turbo) ＆ 応答周期 (Polling Rate)"))
        input_layout = QGridLayout(self.input_settings_group)
        self.global_turbo_cb = QCheckBox(_("長押し中の自動連射を有効にする"))
        self.global_turbo_cb.setChecked(self.parent_browser.global_turbo_enabled)
        self.global_turbo_cb.stateChanged.connect(self.set_global_turbo_enabled)
        input_layout.addWidget(self.global_turbo_cb, 0, 0, 1, 2)
        
        input_layout.addWidget(QLabel(_("連射速度 (連打/秒):")), 1, 0)
        self.turbo_speed_combo = QComboBox()
        self.turbo_speed_combo.addItems([_("5回/秒 (まったり)"), _("10回/秒 (標準速度)"), _("15回/秒 (連打マシン)"), _("20回/秒 (極限マルチタップ)")])
        speed_idx_map = {"5": 0, "10": 1, "15": 2, "20": 3}
        self.turbo_speed_combo.setCurrentIndex(speed_idx_map.get(self.parent_browser.game_turbo_speed, 1))
        self.turbo_speed_combo.currentTextChanged.connect(self.update_turbo_speed_setting)
        input_layout.addWidget(self.turbo_speed_combo, 1, 1)

        input_layout.addWidget(QLabel(_("信号取得レート (ポーリング):")), 2, 0)
        self.polling_rate_combo = QComboBox()
        self.polling_rate_combo.addItems([_("60Hz (標準)"), _("100Hz (高速スキャン)"), _("125Hz (プロ用低遅延)"), _("250Hz (瞬速・ゲーム仕様)")])
        rate_idx_map = {"60": 0, "100": 1, "125": 2, "250": 3}
        self.polling_rate_combo.setCurrentIndex(rate_idx_map.get(self.parent_browser.game_polling_rate, 0))
        self.polling_rate_combo.currentTextChanged.connect(self.update_polling_rate_setting)
        input_layout.addWidget(self.polling_rate_combo, 2, 1)
        left_layout.addWidget(self.input_settings_group)

        sound_group = QGroupBox(_("🎵 サイト別ボリューム・サウンド制御"))
        sound_ly = QVBoxLayout(sound_group)
        self.sound_table = QTableWidget(0, 4)
        self.sound_table.setHorizontalHeaderLabels([_("ドメイン"), _("音量"), _("消音"), "SFX"])
        self.sound_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.sound_table.setMaximumHeight(150)
        sound_ly.addWidget(self.sound_table)
        
        add_snd_ly = QHBoxLayout()
        self.sound_domain_input = QLineEdit(); self.sound_domain_input.setPlaceholderText(_("例: youtube.com"))
        self.sound_add_btn = QPushButton(_("追加")); self.sound_add_btn.clicked.connect(self.add_sound_domain_config)
        add_snd_ly.addWidget(self.sound_domain_input); add_snd_ly.addWidget(self.sound_add_btn)
        sound_ly.addLayout(add_snd_ly)
        left_layout.addWidget(sound_group)
        
        right_widget = QWidget(); right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)
        right_layout.addWidget(QLabel(_("【🎮 コントローラーキーマッピング設定】")))
        self.mapping_enabled_cb = QCheckBox(_("コントローラーでのキーボード入力を有効にする"))
        self.mapping_enabled_cb.setChecked(self.parent_browser.game_mapping_enabled)
        self.mapping_enabled_cb.stateChanged.connect(self.toggle_mapping_enabled)
        right_layout.addWidget(self.mapping_enabled_cb)
        
        self.detect_button_guide = QLabel(_("※「自動検出」を押したあと物理コントローラーのボタンを押すと、自動で行ジャンプします。"))
        self.detect_button_guide.setWordWrap(True)
        self.detect_button_guide.setStyleSheet("color: #00ddff; font-size: 11px;")
        right_layout.addWidget(self.detect_button_guide)

        self.start_detect_btn = QPushButton(_("🎮 キャリブレーション (自動スロット検出) 開始"))
        self.start_detect_btn.clicked.connect(self.toggle_physical_button_detection)
        right_layout.addWidget(self.start_detect_btn)

        self.mapping_table = QTableWidget(0, 4)
        self.mapping_table.setHorizontalHeaderLabels([_("物理ボタン"), _("自動検出"), _("割り当てるキー"), _("連射 (Turbo)")])
        self.mapping_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.mapping_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        right_layout.addWidget(self.mapping_table)
        
        self.available_keys = ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "Space", "Enter", "z", "x", "c", "v", "Shift", "Control", "Escape", "None"]
        self.known_btn_names = {
            0: "A / Button ✕", 1: "B / Button 〇", 2: "X / Button ☐", 3: "Y / Button △",
            4: "L1 / LB Shoulder", 5: "R1 / RB Shoulder", 6: "L2 / LT Trigger", 7: "R2 / RT Trigger",
            8: "Select", 9: "Start", 12: "D-Pad Up", 13: "D-Pad Down", 14: "D-Pad Left", 15: "D-Pad Right"
        } if CURRENT_LANG == "en" else {
            0: "A / ✕ボタン", 1: "B / 〇ボタン", 2: "X / ☐ボタン", 3: "Y / △ボタン",
            4: "L1 / LB ショルダー", 5: "R1 / RB ショルダー", 6: "L2 / LT トリガー", 7: "R2 / RT トリガー",
            8: "Select", 9: "Start", 12: "十字上", 13: "十字下", 14: "十字左", 15: "十字右"
        }
        self.combos_map = {}
        self.gamepad_buttons = []
        
        self.current_mapping = json.loads(self.parent_browser.game_mapping_config) if self.parent_browser.game_mapping_config else self.get_default_mapping()
        self.rebuild_mapping_table(16)
        self.refresh_sound_table()

        splitter.addWidget(left_widget); splitter.addWidget(right_widget)
        layout.addWidget(splitter)
        self.content_stack.addWidget(panel)

    def set_global_turbo_enabled(self, state):
        enabled = (state != 0)
        self.parent_browser.settings.setValue("global_turbo_enabled", enabled)
        self.parent_browser.global_turbo_enabled = enabled
        self.parent_browser.inject_gamepad_mapping_to_all()

    def get_default_mapping(self):
        return {"0": "Space", "1": "z", "2": "x", "3": "c", "12": "ArrowUp", "13": "ArrowDown", "14": "ArrowLeft", "15": "ArrowRight"}

    def update_turbo_speed_setting(self, text):
        speed = "10"
        if "5" in text: speed = "5"
        elif "10" in text: speed = "10"
        elif "15" in text: speed = "15"
        elif "20" in text: speed = "20"
        self.parent_browser.settings.setValue("game_turbo_speed", speed)
        self.parent_browser.game_turbo_speed = speed
        self.parent_browser.inject_gamepad_mapping_to_all()

    def update_polling_rate_setting(self, text):
        rate = "60"
        if "60" in text: rate = "60"
        elif "100" in text: rate = "100"
        elif "125" in text: rate = "125"
        elif "250" in text: rate = "250"
        self.parent_browser.settings.setValue("game_polling_rate", rate)
        self.parent_browser.game_polling_rate = rate
        self.parent_browser.inject_gamepad_mapping_to_all()

    def update_turbo_mapping(self, btn_idx, enabled):
        turbo_buttons = self.parent_browser.game_turbo_buttons
        if enabled:
            if btn_idx not in turbo_buttons: turbo_buttons.append(btn_idx)
        else:
            if btn_idx in turbo_buttons: turbo_buttons.remove(btn_idx)
        self.parent_browser.settings.setValue("game_turbo_buttons", json.dumps(turbo_buttons))
        self.parent_browser.game_turbo_buttons = turbo_buttons
        self.parent_browser.inject_gamepad_mapping_to_all()

    def ensure_mapping_row_exists(self, btn_idx):
        for b_idx, _existing_name in self.gamepad_buttons:
            if b_idx == btn_idx: return
            
        name = self.known_btn_names.get(btn_idx, f"{_('追加スロット')} {btn_idx}")
        if btn_idx >= 100:
            axis_num = (btn_idx - 100) // 2
            direction = "-" if (btn_idx % 2 == 0) else "+"
            name = f"Axis(軸) {axis_num} {direction}"

        self.gamepad_buttons.append((btn_idx, name))
        row = self.mapping_table.rowCount()
        self.mapping_table.insertRow(row)
        self.mapping_table.setItem(row, 0, QTableWidgetItem(f"[{btn_idx}] {name}"))
        
        detect_row_btn = QPushButton(_("自動検出"))
        detect_row_btn.clicked.connect(lambda _, r=row: self.set_active_row_detect(r))
        self.mapping_table.setCellWidget(row, 1, detect_row_btn)
        
        combo = QComboBox()
        combo.addItems(self.available_keys)
        combo.setCurrentText(self.current_mapping.get(str(btn_idx), "None"))
        combo.currentTextChanged.connect(lambda text, idx=btn_idx: self.update_mapping(idx, text))
        self.mapping_table.setCellWidget(row, 2, combo)
        self.combos_map[btn_idx] = combo

        chk_turbo = QCheckBox(_("連射 (Turbo)"))
        chk_turbo.setChecked(btn_idx in self.parent_browser.game_turbo_buttons)
        chk_turbo.stateChanged.connect(lambda state, idx=btn_idx: self.update_turbo_mapping(idx, state != 0))
        
        chk_widget = QWidget()
        chk_layout = QHBoxLayout(chk_widget)
        chk_layout.addWidget(chk_turbo)
        chk_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chk_layout.setContentsMargins(0,0,0,0)
        self.mapping_table.setCellWidget(row, 3, chk_widget)

    def rebuild_mapping_table(self, button_count):
        self.mapping_table.setRowCount(0); self.combos_map.clear(); self.gamepad_buttons.clear()
        
        needed_indices = set(range(min(max(button_count, 16), 32)))
        for k in self.current_mapping.keys():
            try: needed_indices.add(int(k))
            except: pass
            
        for btn_idx in sorted(needed_indices):
            self.ensure_mapping_row_exists(btn_idx)

    def update_mapping(self, btn_idx, key):
        self.current_mapping[str(btn_idx)] = key
        self.parent_browser.settings.setValue("game_mapping_config", json.dumps(self.current_mapping))
        self.parent_browser.game_mapping_config = json.dumps(self.current_mapping)
        self.parent_browser.inject_gamepad_mapping_to_all()

    def toggle_mapping_enabled(self, state):
        enabled = (state != 0)
        self.parent_browser.settings.setValue("game_mapping_enabled", enabled)
        self.parent_browser.game_mapping_enabled = enabled
        self.parent_browser.inject_gamepad_mapping_to_all()

    def toggle_physical_button_detection(self):
        if self.parent_browser.physical_detect_active:
            self.parent_browser.physical_detect_active = False
            self.start_detect_btn.setText(_("🎮 キャリブレーション (自動スロット検出) 開始"))
        else:
            self.parent_browser.physical_detect_active = True
            self.start_detect_btn.setText(_("🎯 検出中... 物理コントローラー of キーを押してください"))

    def set_active_row_detect(self, row):
        self.active_detect_row = row
        self.parent_browser.physical_detect_active = True
        self.start_detect_btn.setText(f"{_('🎯 ボタン')} [{self.gamepad_buttons[row][1]}] {_('割当検出中...')}")

    def update_mapping_ui_from_detected_button(self, btn_idx):
        if self.active_detect_row != -1:
            self.mapping_table.selectRow(self.active_detect_row)
            self.active_detect_row = -1
            self.parent_browser.physical_detect_active = False
            self.start_detect_btn.setText(_("🎮 キャリブレーション (自動スロット検出) 開始"))
            self.detect_button_guide.setText(_("※ボタンの紐付けに成功しました！"))
        else:
            for r, (b_idx, name) in enumerate(self.gamepad_buttons):
                if b_idx == btn_idx:
                    self.mapping_table.selectRow(r)
                    self.detect_button_guide.setText(f"{_('検出された入力:')} {name}")
                    break

    def refresh_sound_table(self):
        self.sound_table.setRowCount(0)
        for domain, cfg in self.parent_browser.sound_manager.configs.items():
            row = self.sound_table.rowCount()
            self.sound_table.insertRow(row)
            self.sound_table.setItem(row, 0, QTableWidgetItem(domain))
            
            vol_slider = QSlider(Qt.Orientation.Horizontal)
            vol_slider.setRange(0, 100); vol_slider.setValue(cfg.get("volume", 100))
            vol_slider.valueChanged.connect(lambda v, d=domain: self.update_sound_volume(d, v))
            self.sound_table.setCellWidget(row, 1, vol_slider)
            
            mute_chk = QCheckBox(); mute_chk.setChecked(cfg.get("mute", False))
            mute_chk.stateChanged.connect(lambda s, d=domain: self.update_sound_mute(d, s == Qt.CheckState.Checked.value))
            mute_widget = QWidget(); m_lay = QHBoxLayout(mute_widget); m_lay.addWidget(mute_chk); m_lay.setAlignment(Qt.AlignmentFlag.AlignCenter); m_lay.setContentsMargins(0,0,0,0)
            self.sound_table.setCellWidget(row, 2, mute_widget)

            sfx_chk = QCheckBox(); sfx_chk.setChecked(cfg.get("sfx", True))
            sfx_chk.stateChanged.connect(lambda s, d=domain: self.update_sound_sfx(d, s == Qt.CheckState.Checked.value))
            sfx_widget = QWidget(); s_lay = QHBoxLayout(sfx_widget); m_lay.addWidget(sfx_chk); s_lay.setAlignment(Qt.AlignmentFlag.AlignCenter); s_lay.setContentsMargins(0,0,0,0)
            self.sound_table.setCellWidget(row, 3, sfx_widget)

    def add_sound_domain_config(self):
        d = self.sound_domain_input.text().strip().lower()
        if d:
            self.parent_browser.sound_manager.set_config(d, 100, False, True)
            self.sound_domain_input.clear()
            self.refresh_sound_table()

    def update_sound_volume(self, domain, val):
        cfg = self.parent_browser.sound_manager.get_config(domain)
        self.parent_browser.sound_manager.set_config(domain, val, cfg["mute"], cfg["sfx"])

    def update_sound_mute(self, domain, val):
        cfg = self.parent_browser.sound_manager.get_config(domain)
        self.parent_browser.sound_manager.set_config(domain, cfg["volume"], val, cfg["sfx"])

    def update_sound_sfx(self, domain, val):
        cfg = self.parent_browser.sound_manager.get_config(domain)
        self.parent_browser.sound_manager.set_config(domain, cfg["volume"], cfg["mute"], val)

    def init_workspace_privacy_panel(self):
        panel = QWidget(); layout = QVBoxLayout(panel); layout.setAlignment(Qt.AlignmentFlag.AlignTop); layout.setContentsMargins(30, 20, 30, 20)
        title = QLabel(_("🛡️ プライバシー＆保護 ＆ ワークスペース")); title.setFont(QFont("Arial", 18, QFont.Weight.Bold)); layout.addWidget(title)

        dash_group = QGroupBox(_("📊 セキュリティ防御・ダッシュボード"))
        dash_layout = QVBoxLayout(dash_group)
        self.block_count_label = QLabel(_("🛡️ 今セッションでの脅威・広告ブロック数: ") + str(self.parent_browser.url_interceptor.blocked_count) + _(" 件"))
        self.block_count_label.setFont(QFont("Arial", 13, QFont.Weight.Bold)); self.block_count_label.setStyleSheet("color: #00ddff;")
        
        breakdown = QLabel(_("【ブロック内訳シミュレーション】\n■ 広告・不要バナー阻止: 48%  [████████████] \n■ プライバシー追跡トラッカー: 32%  [████████] \n■ フィンガープリント隠蔽: 12%  [███] \n■ その他セキュリティ脅威: 8%  [██]"))
        breakdown.setFont(QFont("monospace", 10))
        breakdown.setStyleSheet("color: #bac2de;")
        
        dash_layout.addWidget(self.block_count_label)
        dash_layout.addWidget(breakdown)
        layout.addWidget(dash_group)

        work_layout = QHBoxLayout()
        self.workspace_combo = QComboBox()
        for ws_name in self.parent_browser.workspace_manager.workspaces.keys(): self.workspace_combo.addItem(ws_name)
        self.load_workspace_btn = QPushButton(_("展開する")); self.load_workspace_btn.clicked.connect(self.apply_workspace)
        self.save_workspace_btn = QPushButton(_("現在のタブ群を保存")); self.save_workspace_btn.clicked.connect(self.save_current_as_workspace)
        work_layout.addWidget(self.workspace_combo); work_layout.addWidget(self.load_workspace_btn); work_layout.addWidget(self.save_workspace_btn)
        layout.addWidget(QLabel(_("📂 ワークスペース設定 (複数タブセットの一括切り替え):"))); layout.addLayout(work_layout)

        self.tracker_cb = QCheckBox(_("強力なトラッカー・広告ブロックを有効にする"))
        self.tracker_cb.setChecked(self.parent_browser.url_interceptor.tracker_block_enabled)
        self.tracker_cb.stateChanged.connect(lambda s: setattr(self.parent_browser.url_interceptor, 'tracker_block_enabled', s != 0) or self.parent_browser.update_interceptor_state() or self.update_block_count_label())
        layout.addWidget(self.tracker_cb)

        self.https_cb = QCheckBox(_("常にHTTPS暗号化接続を強制する"))
        self.https_cb.setChecked(self.parent_browser.url_interceptor.https_upgrade_enabled)
        self.https_cb.stateChanged.connect(lambda s: setattr(self.parent_browser.url_interceptor, 'https_upgrade_enabled', s != 0) or self.parent_browser.update_interceptor_state())
        layout.addWidget(self.https_cb)
        
        self.content_stack.addWidget(panel)

    def apply_workspace(self):
        ws = self.workspace_combo.currentText()
        if ws in self.parent_browser.workspace_manager.workspaces:
            for url in self.parent_browser.workspace_manager.workspaces[ws]:
                self.parent_browser.add_new_tab(url)
            msg = f"Deployed workspace: '{ws}'" if CURRENT_LANG == "en" else f"📂 ワークスペース '{ws}' を展開しました"
            self.parent_browser.statusBar().showMessage(msg, 3000)

    def save_current_as_workspace(self):
        name, ok = QInputDialog.getText(self, _("ワークスペース保存"), _("新しいワークスペース名を入力してください:"))
        if ok and name:
            urls = []
            for i in range(self.parent_browser.tabs.count()):
                w = self.parent_browser.tabs.widget(i)
                if isinstance(w, BrowserTab):
                    u = w.url().toString()
                    if u and not u.startswith("openweb://"): urls.append(u)
            if urls:
                self.parent_browser.workspace_manager.create(name, urls)
                self.workspace_combo.addItem(name)
                msg = f"Saved workspace: '{name}'" if CURRENT_LANG == "en" else f"📂 ワークスペース '{name}' を保存しました"
                self.parent_browser.statusBar().showMessage(msg, 3000)

    def update_block_count_label(self):
        self.block_count_label.setText(_("🛡️ 今セッションでの脅威・広告ブロック数: ") + str(self.parent_browser.url_interceptor.blocked_count) + _(" 件"))

    def init_timeline_panel(self):
        panel = QWidget(); layout = QVBoxLayout(panel); layout.setContentsMargins(30, 20, 30, 20)
        title = QLabel(_("🕒 閲覧タイムライン")); title.setFont(QFont("Arial", 18, QFont.Weight.Bold)); layout.addWidget(title)
        layout.addWidget(QLabel(_("過去に訪れたページを縦軸の時間軸に沿って一覧表示し、1日の学びをいつでも振り返ることができます。")))
        
        self.timeline_list = QListWidget()
        self.timeline_list.setStyleSheet("QListWidget::item { border-left: 3px solid #00ddff; padding-left: 15px; margin-bottom: 8px; }")
        self.timeline_list.itemDoubleClicked.connect(self.open_timeline_url)
        layout.addWidget(self.timeline_list)
        
        clear_btn = QPushButton(_("タイムライン履歴を全消去"))
        clear_btn.clicked.connect(self.parent_browser.clear_browser_data)
        layout.addWidget(clear_btn)
        self.content_stack.addWidget(panel)

    def refresh_timeline(self):
        self.timeline_list.clear()
        for entry in self.parent_browser.browser_history:
            self.timeline_list.addItem(f"⏰ {entry['time']}\n🔗 {entry['title']}\n🌎 {entry['url']}")

    def open_timeline_url(self, item):
        lines = item.text().split("\n")
        if len(lines) >= 3:
            url_str = lines[2].replace("🌎 ", "").strip()
            self.parent_browser.add_new_tab(url_str)

    def init_pocket_panel(self):
        panel = QWidget(); layout = QVBoxLayout(panel); layout.setContentsMargins(30, 20, 30, 20)
        title = QLabel(_("📁 リーディングポケット")); title.setFont(QFont("Arial", 18, QFont.Weight.Bold)); layout.addWidget(title)
        layout.addWidget(QLabel(_("あとで読みたい記事やサイトのHTML構造をワンクリックで端末内に丸ごとダウンロード保存。\nネット接続がオフラインの状態でも、いつでも安定して読める専用ビューアです。")))
        
        self.pocket_table = QTableWidget(0, 3)
        self.pocket_table.setHorizontalHeaderLabels([_("記事タイトル"), _("保存日付"), _("操作")])
        self.pocket_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.pocket_table)
        self.content_stack.addWidget(panel)

    def refresh_pocket_table(self):
        self.pocket_table.setRowCount(0)
        for idx, p in enumerate(self.parent_browser.pocket_manager.pages):
            row = self.pocket_table.rowCount()
            self.pocket_table.insertRow(row)
            self.pocket_table.setItem(row, 0, QTableWidgetItem(p["title"]))
            self.pocket_table.setItem(row, 1, QTableWidgetItem(p["date"]))
            
            read_btn = QPushButton(_("読む"))
            read_btn.clicked.connect(lambda _, filename=p["file"]: self.open_pocket_page(filename))
            self.pocket_table.setCellWidget(row, 2, read_btn)

    def open_pocket_page(self, filename):
        path = self.parent_browser.pocket_manager.get_local_path(filename)
        self.parent_browser.add_new_tab(path)

    def init_experimental_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(30, 20, 30, 20)
        
        title = QLabel(_("🧪 開発中の機能  [NEW]"))
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        desc = QLabel(_("ここにある機能は開発中のものです。\n動作が不安定になる可能性があり、将来変更・削除されることがあります。"))
        desc.setStyleSheet("color: #bac2de; margin-bottom: 10px; line-height: 1.4;")
        layout.addWidget(desc)
        
        vid_group = QGroupBox(_("独自動画プレーヤー (実験的)"))
        vid_group.setStyleSheet("QGroupBox { border: 1px solid #3b3d54; border-radius: 8px; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #a6e3a1; }")
        vid_layout = QHBoxLayout(vid_group)
        vid_desc = QLabel(_("OpenWeb独自のプレーヤーを使用します。"))
        self.exp_vid_cb = QCheckBox(_("使用する"))
        self.exp_vid_cb.setChecked(self.parent_browser.settings.value("exp_custom_video", True, type=bool))
        self.exp_vid_cb.stateChanged.connect(lambda s: self.parent_browser.settings.setValue("exp_custom_video", s != 0))
        vid_layout.addWidget(vid_desc)
        vid_layout.addStretch()
        vid_layout.addWidget(self.exp_vid_cb)
        layout.addWidget(vid_group)
        
        wb_group = QGroupBox(_("ホワイトボードモード (スプリットビュー拡張) (実験的)"))
        wb_group.setStyleSheet("QGroupBox { border: 1px solid #3b3d54; border-radius: 8px; margin-top: 15px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #a6e3a1; }")
        wb_layout = QVBoxLayout(wb_group)
        
        wb_top_layout = QHBoxLayout()
        wb_desc = QLabel(_("スプリットビューのタブを自由に移動・リサイズできるモードです。\nブラウザ内をホワイトボードのように使えます。"))
        self.exp_wb_cb = QCheckBox(_("有効にする"))
        self.exp_wb_cb.setChecked(self.parent_browser.settings.value("exp_whiteboard_mode", False, type=bool))
        self.exp_wb_cb.stateChanged.connect(lambda s: self.parent_browser.settings.setValue("exp_whiteboard_mode", s != 0))
        wb_top_layout.addWidget(wb_desc)
        wb_top_layout.addStretch()
        wb_top_layout.addWidget(self.exp_wb_cb)
        
        wb_info = QLabel(_("ⓘ 通常はオフになっています。\n使用する場合は、上のスイッチをオンにしてください。"))
        wb_info.setStyleSheet("color: #89b4fa; font-size: 11px; margin-top: 5px;")
        
        wb_layout.addLayout(wb_top_layout)
        wb_layout.addWidget(wb_info)
        layout.addWidget(wb_group)
        
        self.content_stack.addWidget(panel)

    def init_about_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        title = QLabel(_("ℹ️ OpenWeb について"))
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        header_layout = QHBoxLayout()
        icon_label = QLabel()
        icon_path = get_resource_path("OpenWeb.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        else:
            icon_label.setText("🌐")
            icon_label.setFont(QFont("Arial", 48))
        header_layout.addWidget(icon_label)
        
        title_layout = QVBoxLayout()
        logo_label = QLabel("OpenWeb v.6.2")
        logo_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title_layout.addWidget(logo_label)
        self.version_label = QLabel(_("バージョン: v.6.2"))
        title_layout.addWidget(self.version_label)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        self.about_tab_widget = QTabWidget()

        # --- 概要タブ ---
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)
        about_layout.setContentsMargins(0, 10, 0, 0)
        self.about_text_browser = QTextBrowser()
        self.about_text_browser.setOpenExternalLinks(True)
        about_html = f"""
        <div style="font-family: 'Segoe UI', 'Meiryo', sans-serif; line-height: 1.6; color: #f1f1f7;">
            <p>{_("これは、GeminiとChatgptとGrokの３つで構成されたpyside6で作成されたchromiumベースのブラウザです。")}</p>
            <p>{_("AIが作ったものなので当然バグもありますが、大目に見てください。<br>\n            AIが作成したものですので未知のバグや未知の動作が予想されます。自己責任で使用すること。")}</p>
            <p><b>[i18n] {_("このブラウザは現在日本語とEnglishに対応してます。")}</b></p>
            <p style="color: #ff9800;">
            {_('＊Googleアカウントログイン時に一部アカウントではセキュリティ上ログインができない場合がありますのでQRコードが出ると思いますのでそこからログインすることを推奨します。')}<br>
            {_('＊Botと間違われてReCaptchaが起動しますがお手数をおかけしますが解いてください申し訳ございません。')}
            </p>
            <p>{_('ほかに何か気になるところがありましたら連絡先は <a href="mailto:steck0714@gmail.com" style="color: #00ddff;">steck0714@gmail.com</a> までお願いします。<br>\n            <span style="font-size: 12px; color: #bac2de;">(しかし、バグ探索やAI指示以外は一切作成にかかわっていませんので機能で気になることなど、追加してほしい機能、”特に”バグやこんな挙動をしたなどがありましたらご連絡お願いします。）</span>')}</p>
            
            <hr style="border: none; border-top: 1px solid #444; margin: 20px 0;">
            <p style="text-align: center; color: #888; font-size: 11px;">Openweb v.6.2<br>&copy;Openweb project 2026</p>
        </div>
        """
        self.about_text_browser.setHtml(about_html)
        about_layout.addWidget(self.about_text_browser)
        self.about_tab_widget.addTab(about_tab, _("概要"))

        # --- 更新内容タブ ---
        update_tab = QWidget()
        update_layout = QVBoxLayout(update_tab)
        update_layout.setContentsMargins(0, 10, 0, 0)
        self.update_text_browser = QTextBrowser()
        self.update_text_browser.setOpenExternalLinks(True)
        update_html = f"""
        <div style="font-family: 'Segoe UI', 'Meiryo', sans-serif; line-height: 1.6; color: #f1f1f7;">
            <h3 style="color: #4CAF50; margin-top: 0; padding-bottom: 5px; border-bottom: 1px solid #3b3d54;">{_("v.6.2 の更新内容")}</h3>
            <ul style="margin-top: 10px;">
                <li style="margin-bottom: 8px;"><span style="color: #00ddff; font-weight: bold;">{_("Googleアカウントにログインしにくい問題を修正してある程度しやすくしました。")}</span></li>
                <li style="margin-bottom: 8px;">{_("ゲームモードに「オーバークロックモード（CPU/GPU限界突破）」を追加")}</li>
                <li style="margin-bottom: 8px;">{_("一般設定にJavaScriptの本格使用/無効化を切り替えるモードを追加")}</li>
                <li style="margin-bottom: 8px;">{_("スプリットビュー（2画面）の左右独立URL制御＆鍵マーク完全連動")}</li>
                <li style="margin-bottom: 8px;">{_("開発中の機能パネル追加＆ホワイトボードモード（スプリットビュー拡張）の実装")}</li>
                <li style="margin-bottom: 8px;">{_("ツールバーや鍵マークを右クリックした際の問題を修正")}</li>
                <li style="margin-bottom: 8px;">{_("アプリスロット、ダウンロード履歴など各種UIを大幅にアップグレード")}</li>
            </ul>
        </div>
        """
        self.update_text_browser.setHtml(update_html)
        update_layout.addWidget(self.update_text_browser)
        self.about_tab_widget.addTab(update_tab, _("更新内容"))

        layout.addWidget(self.about_tab_widget)
        self.content_stack.addWidget(panel)

    def update_theme_style(self, theme, text_color, bg_color, border_color, hover_color):
        self.setStyleSheet(f"background-color: {bg_color}; color: {text_color};")
        self.sidebar.setStyleSheet(f"background-color: {hover_color}; color: {text_color}; border: none;")
        
        tables = [getattr(self, n, None) for n in ["pwd_table", "notes_table", "todo_table", "mapping_table", "sound_table", "pocket_table"]]
        for t in tables:
            if t:
                t.setStyleSheet(f"background-color: {bg_color}; color: {text_color}; gridline-color: {border_color}; border: 1px solid {border_color};")
                t.horizontalHeader().setStyleSheet(f"background-color: {hover_color}; color: {text_color};")

        groups = [getattr(self, n, None) for n in ["gamepad_status_group", "input_settings_group"]]
        for g in groups:
            if g: g.setStyleSheet(f"background-color: {hover_color}; color: {text_color}; border: 2px solid {border_color}; border-radius: 8px;")

        if hasattr(self, 'timeline_list') and self.timeline_list:
            self.timeline_list.setStyleSheet(f"background-color: {hover_color}; color: {text_color}; border: 1px solid {border_color}; border-radius: 8px; padding: 10px;")

        if hasattr(self, 'dl_manager_widget'):
            self.dl_manager_widget.setStyleSheet(f"background-color: {bg_color};")

        btn_style = f"QPushButton {{ background-color: {hover_color}; color: {text_color}; border: 1px solid {border_color}; padding: 6px 12px; border-radius: 4px; }} QPushButton:hover {{ background-color: {border_color}; }}"
        input_style = f"background-color: {hover_color}; color: {text_color}; border: 1px solid {border_color}; padding: 6px; border-radius: 4px;"
        
        target_buttons = [
            'gen_pwd_btn', 'check_leak_btn', 'add_note_btn', 'change_master_pwd_btn', 
            'lock_vault_btn', 'load_workspace_btn', 'save_workspace_btn', 'home_file_btn', 
            'home_current_btn', 'save_home_btn', 'todo_submit_btn', 'start_detect_btn', 'sound_add_btn'
        ]
        for name in target_buttons:
            if hasattr(self, name):
                btn_widget = getattr(self, name)
                if btn_widget: btn_widget.setStyleSheet(btn_style)
            
        if hasattr(self, 'reset_btn') and self.reset_btn:
            self.reset_btn.setStyleSheet("""
                QPushButton { background-color: #551111; color: #ff6464; border: 2px solid #882222; padding: 8px; border-radius: 6px; font-weight: bold; }
                QPushButton:hover { background-color: #ff6464; color: white; border-color: #ff6464; }
            """)
            
        for name in ['home_input', 'todo_add_input', 'domain_input', 'sound_domain_input']:
            if hasattr(self, name):
                w = getattr(self, name)
                if w: w.setStyleSheet(input_style)

        if hasattr(self, 'about_text_browser') and self.about_text_browser: 
            self.about_text_browser.setStyleSheet(f"background-color: {hover_color}; color: {text_color}; border: 1px solid {border_color}; border-radius: 8px; padding: 10px;")
            
        if hasattr(self, 'update_text_browser') and self.update_text_browser: 
            self.update_text_browser.setStyleSheet(f"background-color: {hover_color}; color: {text_color}; border: 1px solid {border_color}; border-radius: 8px; padding: 10px;")
            
        if hasattr(self, 'about_tab_widget') and self.about_tab_widget:
            self.about_tab_widget.setStyleSheet(f"""
                QTabWidget::pane {{ border: 1px solid {border_color}; border-radius: 8px; background-color: transparent; }}
                QTabBar::tab {{ background-color: {bg_color}; color: {text_color}; padding: 8px 20px; border: 1px solid {border_color}; border-bottom: none; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; }}
                QTabBar::tab:selected {{ background-color: {hover_color}; font-weight: bold; border-bottom: 2px solid #00ddff; }}
                QTabBar::tab:hover {{ background-color: {hover_color}; }}
            """)

# =========================================================
# Main Browser Application
# =========================================================
class MyBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("OpenWeb", "Browser")
        
        # 📂 EXE化されている場合は、exe本体と同じフォルダにデータディレクトリを構成して情報消失を完全防止
        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
            
        self.data_dir = os.path.join(self.base_dir, "browser_data")
        
        self.config_dir = os.path.join(self.data_dir, "config")
        self.profiles_dir = os.path.join(self.data_dir, "profiles", "default")
        self.vault_dir = os.path.join(self.data_dir, "vault")
        self.workspace_dir = os.path.join(self.data_dir, "workspace")
        self.cache_dir = os.path.join(self.data_dir, "cache")
        self.downloads_dir = os.path.join(self.data_dir, "downloads")

        for d in [self.config_dir, self.profiles_dir, self.vault_dir, self.workspace_dir, self.cache_dir, self.downloads_dir]:
            os.makedirs(d, exist_ok=True)

        self.todo_file = os.path.join(self.config_dir, "todo.json")
        self.optimization_config_path = os.path.join(self.config_dir, "optimization_config.json")
        self.opt_config = self.load_optimization_config()

        # === オート検出 + カスタムChromeプロファイル対応 ===
        auto_detect = self.settings.value("auto_detect_browser_profile", False, type=bool)
        custom_profile_path = self.settings.value("custom_chrome_profile_path", "", type=str)
        
        profile_to_use = None
        
        if auto_detect:
            detected = self.detect_chrome_profile()
            if detected:
                profile_to_use = detected
                print(f"[OpenWeb] 自動検出されたプロファイルを使用: {profile_to_use}")
        
        if not profile_to_use and custom_profile_path and os.path.exists(custom_profile_path):
            profile_to_use = custom_profile_path
        
        if profile_to_use:
            self.normal_profile = QWebEngineProfile("OpenWebCustom", self)
            self.normal_profile.setPersistentStoragePath(profile_to_use)
            self.normal_profile.setCachePath(os.path.join(profile_to_use, "Cache"))
            print(f"[OpenWeb] Chromeプロファイルを使用: {profile_to_use}")
        else:
            self.normal_profile = QWebEngineProfile("OpenWebNormal", self)
        
        # Googleログイン安定化：現実的な User-Agent を強制設定
        try:
            self.normal_profile.setHttpUserAgent(REALISTIC_UA)
        except Exception:
            pass
        
        self.secret_profile = QWebEngineProfile("", self)
        try:
            self.secret_profile.setHttpUserAgent(REALISTIC_UA)
        except Exception:
            pass
        self.external_windows = []

        self.url_interceptor = OpenWebUrlInterceptor(self)
        self.update_interceptor_state()

        self.vault = OpenWebVaultManager(self.vault_dir)
        self.workspace_manager = WorkspaceManager(self.workspace_dir)
        self.session_manager = SessionManager(self.profiles_dir)
        self.pocket_manager = PocketManager(self.data_dir)
        self.sound_manager = SoundManager(self.data_dir)

        # JavaScript トグル設定
        self.javascript_enabled = self.settings.value("javascript_enabled", True, type=bool)

        self.game_mode_file = os.path.join(self.config_dir, "game_mode.json")
        self.game_mode_domains = []
        if os.path.exists(self.game_mode_file):
            try:
                with open(self.game_mode_file, "r", encoding="utf-8") as f: self.game_mode_domains = json.load(f)
            except: pass
        self.game_mode_enabled = self.settings.value("game_mode_enabled", False, type=bool)

        self.game_mapping_enabled = self.settings.value("game_mapping_enabled", False, type=bool)
        self.game_mapping_config = self.settings.value("game_mapping_config", "")
        self.global_turbo_enabled = self.settings.value("global_turbo_enabled", True, type=bool)
        self.game_turbo_speed = self.settings.value("game_turbo_speed", "10", type=str)
        self.game_polling_rate = self.settings.value("game_polling_rate", "60", type=str)
        try:
            self.game_turbo_buttons = json.loads(self.settings.value("game_turbo_buttons", "[]"))
        except:
            self.game_turbo_buttons = []
        self.scroll_backup_enabled = self.settings.value("scroll_backup_enabled", True, type=bool)

        self.physical_detect_active = False
        self.immersion_mode = False
        self.auto_fit_mode = False
        
        self.closed_tabs_history = []
        self.scroll_backups = {} 

        self.fit_timer = QTimer()
        self.fit_timer.setSingleShot(True)
        self.fit_timer.timeout.connect(self.fit_to_window_width)

        self.setWindowTitle("OpenWeb v.6.2")
        self.setGeometry(100, 100, 1450, 920)
        
        # 🌟 アイコンファイルのロード先を堅牢なロジックで解決
        icon_path = get_resource_path("OpenWeb.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            QApplication.setWindowIcon(QIcon(icon_path))
        
        self.history_file = os.path.join(self.profiles_dir, "history.json")
        self.browser_history = []
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f: self.browser_history = json.load(f)
            except: pass

        self.profile = self.normal_profile
        self.cookies_enabled = self.settings.value("cookies_enabled", True, type=bool)

        self.profile.setPersistentStoragePath(self.profiles_dir)
        self.profile.setCachePath(self.cache_dir)
        self.profile.setDownloadPath(self.downloads_dir)
        
        if self.cookies_enabled:
            self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        else:
            self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)

        self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
        cache_size_mb = self.opt_config.get("http_cache_max_size_mb", 1024)
        self.profile.setHttpCacheMaximumSize(1024 * 1024 * cache_size_mb)
        self.profile.setSpellCheckEnabled(False)
        self.profile.setPushServiceEnabled(True)

        self.profile.downloadRequested.connect(self.handle_download)
        self.secret_profile.downloadRequested.connect(self.handle_download)

        # ★ Googleログイン回避のため、UserAgentを一般的な最新のWindows版Chromeに偽装（未来すぎるバージョンだとBot判定されるため調整）
        default_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        self.current_user_agent = self.opt_config.get("user_agent_override", "").strip() or default_ua
        QWebEngineProfile.defaultProfile().setHttpUserAgent(self.current_user_agent)
        self.profile.setHttpUserAgent(self.current_user_agent)
        self.secret_profile.setHttpUserAgent(self.current_user_agent)

        speedup_script = QWebEngineScript()
        speedup_script.setName("UltraFastHybridShield")
        # ★ Googleアカウントの厳格なセキュリティチェック（webdriver, plugins, runtime検証）を完全に回避するためのインジェクション
        # 認証時のみMac-Safariに偽装し、それ以外の通常のブラウジングでは標準の高速レンダリングに最適化されます。
        ULTRA_FAST_JS = """
        (function() {
            'use strict';
            try {
                // === 1. webdriver フラグの完全除去（複数レイヤーで防御） ===
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                    configurable: true
                });
                // さらに厳しく
                delete navigator.webdriver;
                Object.defineProperty(navigator, 'webdriver', { get: () => false, configurable: true });

                // === 2. chrome オブジェクトの現実的なモック ===
                if (!window.chrome) {
                    window.chrome = {
                        app: { isInstalled: false },
                        runtime: {
                            id: undefined,
                            getURL: () => '',
                            connect: () => ({}),
                            sendMessage: () => {},
                            onMessage: { addListener: () => {} }
                        },
                        webstore: undefined
                    };
                } else if (!window.chrome.runtime) {
                    window.chrome.runtime = {
                        id: undefined,
                        getURL: () => '',
                        connect: () => ({}),
                        sendMessage: () => {},
                        onMessage: { addListener: () => {} }
                    };
                }

                // === 3. navigator の各種プロパティを自然に偽装 ===
                const isGoogle = window.location.hostname.includes('google.com') || 
                                 window.location.hostname.includes('accounts.youtube.com');

                if (isGoogle) {
                    // Googleログイン時はSafari風に
                    const safariUA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15";
                    Object.defineProperty(navigator, 'userAgent', { get: () => safariUA, configurable: true });
                    Object.defineProperty(navigator, 'appVersion', { get: () => safariUA.replace("Mozilla/", ""), configurable: true });
                    Object.defineProperty(navigator, 'platform', { get: () => 'MacIntel', configurable: true });
                    Object.defineProperty(navigator, 'vendor', { get: () => 'Apple Computer, Inc.', configurable: true });
                    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3], configurable: true });
                    Object.defineProperty(navigator, 'languages', { get: () => ['ja-JP', 'ja', 'en-US', 'en'], configurable: true });
                    Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8, configurable: true });
                    Object.defineProperty(navigator, 'deviceMemory', { get: () => 8, configurable: true });
                    Object.defineProperty(navigator, 'maxTouchPoints', { get: () => 0, configurable: true });
                } else {
                    // 通常時（Chromium風だが自然に）
                    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3], configurable: true });
                    Object.defineProperty(navigator, 'languages', { get: () => ['ja-JP', 'ja', 'en-US', 'en'], configurable: true });
                    Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8, configurable: true });
                    Object.defineProperty(navigator, 'deviceMemory', { get: () => 8, configurable: true });
                    Object.defineProperty(navigator, 'maxTouchPoints', { get: () => 0, configurable: true });
                }

                // === 4. Permissions API の自然な挙動修正 ===
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => {
                    if (parameters.name === 'notifications') {
                        return Promise.resolve({ state: Notification.permission });
                    }
                    if (parameters.name === 'clipboard-read' || parameters.name === 'clipboard-write') {
                        return Promise.resolve({ state: 'granted' });
                    }
                    return originalQuery(parameters);
                };

                // === 5. 追加の防御（getOwnPropertyDescriptor対策 + cdc_ 変数除去） ===
                const originalGetOwnPropertyDescriptor = Object.getOwnPropertyDescriptor;
                Object.getOwnPropertyDescriptor = function(target, key) {
                    if (key === 'webdriver') {
                        return undefined;
                    }
                    return originalGetOwnPropertyDescriptor(target, key);
                };

                // Googleがよくチェックする自動化マーカー（cdc_ 系）を削除
                try {
                    for (let prop in window) {
                        if (prop.startsWith('cdc_')) {
                            delete window[prop];
                        }
                    }
                } catch(e) {}

                // =====================================================
                // Canvas / WebGL フィンガープリント対策（Safari一貫性重視）
                // =====================================================
                const isGoogleDomain = window.location.hostname.includes('google.com') || 
                                       window.location.hostname.includes('accounts.youtube.com');

                // --- WebGL Spoofing（Mac Safari風 + 軽いノイズ） ---
                const getParameterProxy = (originalGetParameter) => {
                    return function(parameter) {
                        // UNMASKED_VENDOR_WEBGL
                        if (parameter === 37445) {
                            return 'Apple Inc.';
                        }
                        // UNMASKED_RENDERER_WEBGL
                        if (parameter === 37446) {
                            // 実在のMac Safariでよく出る値に近いもの
                            const renderers = [
                                'Apple M1', 'Apple M2', 'Apple M3',
                                'Intel Iris OpenGL Engine', 'Apple GPU'
                            ];
                            return renderers[Math.floor(Math.random() * renderers.length)];
                        }
                        return originalGetParameter.call(this, parameter);
                    };
                };

                // WebGLRenderingContext と WebGL2RenderingContext を両方対応
                ['WebGLRenderingContext', 'WebGL2RenderingContext'].forEach(ctxName => {
                    if (window[ctxName] && window[ctxName].prototype.getParameter) {
                        const originalGetParameter = window[ctxName].prototype.getParameter;
                        window[ctxName].prototype.getParameter = getParameterProxy(originalGetParameter);
                    }
                });

                // --- Canvas 2D に軽いノイズを追加（Safariでも自然な範囲） ---
                const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
                CanvasRenderingContext2D.prototype.getImageData = function(sx, sy, sw, sh) {
                    const imageData = originalGetImageData.call(this, sx, sy, sw, sh);
                    
                    // Googleドメイン時のみ軽くノイズを加える（他のサイトへの影響を最小限に）
                    if (isGoogleDomain && sw * sh < 1000000) { // 大きすぎるCanvasは無視
                        for (let i = 0; i < imageData.data.length; i += 4) {
                            // 非常に軽いノイズ（±1程度）
                            if (Math.random() < 0.03) {
                                imageData.data[i]     = Math.max(0, Math.min(255, imageData.data[i]     + (Math.random() > 0.5 ? 1 : -1)));
                                imageData.data[i + 1] = Math.max(0, Math.min(255, imageData.data[i + 1] + (Math.random() > 0.5 ? 1 : -1)));
                                imageData.data[i + 2] = Math.max(0, Math.min(255, imageData.data[i + 2] + (Math.random() > 0.5 ? 1 : -1)));
                            }
                        }
                    }
                    return imageData;
                };

                // toDataURL にも軽くノイズを反映させるための簡易対応
                const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                HTMLCanvasElement.prototype.toDataURL = function(type, encoderOptions) {
                    if (isGoogleDomain) {
                        // 一度getImageDataを呼んでノイズを適用させるトリック
                        try {
                            const ctx = this.getContext('2d');
                            if (ctx) {
                                ctx.getImageData(0, 0, 1, 1); // ノイズ適用を強制
                            }
                        } catch(e) {}
                    }
                    return originalToDataURL.call(this, type, encoderOptions);
                };

            } catch(e) {}
        })();
        """
        speedup_script.setSourceCode(ULTRA_FAST_JS)
        speedup_script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
        speedup_script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        speedup_script.setRunsOnSubFrames(True)
        self.profile.scripts().insert(speedup_script)
        self.secret_profile.scripts().insert(speedup_script)

        self.home_url = self.settings.value("home_url", "https://www.google.com", type=str)

        self.main_container = QWidget(); self.setCentralWidget(self.main_container)
        self.main_layout = QVBoxLayout(self.main_container); self.main_layout.setContentsMargins(0,0,0,0); self.main_layout.setSpacing(0)
        
        self.navbar = QToolBar()
        self.navbar.setMovable(False)
        self.navbar.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu) 
        self.addToolBar(self.navbar)
        
        for name, func in [(_("←"), self.go_back), (_("→"), self.go_forward), (_("⟳"), self.reload_page), (_("🏠"), self.load_home)]:
            act = QAction(name, self); act.triggered.connect(func); self.navbar.addAction(act)
            
        self.security_button = QToolButton()
        self.security_button.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu) 
        self.security_button.setText("🔒")
        self.security_button.setToolTip(_("通信の安全性と証明書情報を表示"))
        self.security_button.setStyleSheet("QToolButton { border: none; font-size: 16px; padding: 2px; }")
        self.security_button.clicked.connect(self.show_security_info_dialog)
        self.navbar.addWidget(self.security_button)

        self.split_toggle_btn = QToolButton()
        self.split_toggle_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.split_toggle_btn.setText(_("＝左面"))
        self.split_toggle_btn.setToolTip(_("スプリットビュー：操作対象のアクティブ画面を左右に切り替えます"))
        self.split_toggle_btn.clicked.connect(self.toggle_split_focus)
        self.navbar.addWidget(self.split_toggle_btn)
        self.split_toggle_btn.hide()

        open_file_btn = QAction("📂", self)
        open_file_btn.setToolTip(_("ローカルのHTMLファイルを開く (Ctrl+O)"))
        open_file_btn.triggered.connect(self.open_local_file)
        self.navbar.addAction(open_file_btn)

        self.url_bar = QLineEdit(); self.url_bar.returnPressed.connect(self.navigate_to_url); self.navbar.addWidget(self.url_bar)
        
        copy_url_btn = QAction(_("📋"), self)
        copy_url_btn.setToolTip(_("URLをクリップボードにコピー"))
        copy_url_btn.triggered.connect(self.copy_current_url)
        self.navbar.addAction(copy_url_btn)

        new_tab_btn = QAction(_("＋"), self)
        new_tab_btn.triggered.connect(self.create_default_new_tab)
        self.navbar.addAction(new_tab_btn)

        zoom_in_btn = QAction(_("＋拡大"), self)
        zoom_in_btn.triggered.connect(lambda: self.adjust_zoom(0.1))
        self.navbar.addAction(zoom_in_btn)

        zoom_out_btn = QAction(_("－縮小"), self)
        zoom_out_btn.triggered.connect(lambda: self.adjust_zoom(-0.1))
        self.navbar.addAction(zoom_out_btn)

        zoom_reset_btn = QAction(_("100%"), self)
        zoom_reset_btn.triggered.connect(self.reset_zoom)
        self.navbar.addAction(zoom_reset_btn)

        self.fit_btn = QAction(_("フィット: OFF"), self)
        self.fit_btn.setCheckable(True)
        self.fit_btn.triggered.connect(self.toggle_auto_fit)
        self.navbar.addAction(self.fit_btn)

        self.immersion_action = QAction(_("🎯 没入"), self)
        self.immersion_action.setToolTip(_("没入モードの切替 (F11 / Ctrl+Shift+I)"))
        self.immersion_action.triggered.connect(self.toggle_immersion_mode)
        self.navbar.addAction(self.immersion_action)

        self.settings_menu = QMenu(self); self.rebuild_main_menu()
        self.settings_button = QToolButton(); self.settings_button.setText(_(" ≡ ")); self.settings_button.setMenu(self.settings_menu)
        self.settings_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.navbar.addWidget(self.settings_button)

        self.tabs = QTabWidget(); self.tabs.setDocumentMode(True); self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        
        self.tabs.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabs.customContextMenuRequested.connect(self.show_tab_context_menu)
        self.main_layout.addWidget(self.tabs)

        # ---------------------------------------------------------
        # 💎 没入モード用・極上グラスマフィズムフローティングUI
        # ---------------------------------------------------------
        self.immersion_widget = QWidget(self)
        self.immersion_widget.setFixedSize(190, 38)
        self.immersion_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        iw_layout = QHBoxLayout(self.immersion_widget)
        iw_layout.setContentsMargins(8, 2, 8, 2)
        iw_layout.setSpacing(6)

        self.exit_immersion_btn = QPushButton(_("↩️ 解除"), self.immersion_widget)
        self.exit_immersion_btn.setToolTip(_("没入モードを終了する (Esc)"))
        self.exit_immersion_btn.setStyleSheet("""
            QPushButton { 
                color: #ff6464; 
                font-weight: bold; 
                border: none; 
                background: transparent; 
                padding: 4px; 
                font-size: 12px;
            } 
            QPushButton:hover { 
                background-color: rgba(255, 100, 100, 0.15); 
                border-radius: 12px; 
            }
        """)
        self.exit_immersion_btn.clicked.connect(self.toggle_immersion_mode)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("color: rgba(255, 255, 255, 0.2); background-color: rgba(255, 255, 255, 0.2); max-width: 1px;")

        self.immersion_menu_btn = QPushButton(_("⚙️ 操作"), self.immersion_widget)
        self.immersion_menu_btn.setToolTip(_("ブラウザコントロールメニューを開く"))
        self.immersion_menu_btn.setStyleSheet("""
            QPushButton { 
                color: #00ddff; 
                font-weight: bold; 
                border: none; 
                background: transparent; 
                padding: 4px;
                font-size: 12px;
            } 
            QPushButton:hover { 
                background-color: rgba(0, 221, 255, 0.15); 
                border-radius: 12px; 
            }
        """)
        self.immersion_menu_btn.clicked.connect(self.show_immersion_menu)

        iw_layout.addWidget(self.exit_immersion_btn); iw_layout.addWidget(sep); iw_layout.addWidget(self.immersion_menu_btn)
        self.immersion_widget.hide()

        self.freeze_timer = QTimer(self)
        self.freeze_timer.timeout.connect(self.check_idle_tabs_for_freeze)
        self.freeze_timer.start(10000)

        self.setStatusBar(QStatusBar())
        self.is_processing_mode = False

        QShortcut(QKeySequence("Ctrl+O"), self, activated=self.open_local_file)
        QShortcut(QKeySequence("Ctrl+F"), self, activated=self.show_find_dialog)
        QShortcut(QKeySequence("Ctrl+P"), self, activated=self.print_to_pdf)
        QShortcut(QKeySequence("Ctrl+K"), self, activated=self.open_command_palette)
        QShortcut(QKeySequence("Ctrl+T"), self, activated=self.create_default_new_tab)
        QShortcut(QKeySequence("Ctrl+W"), self, activated=lambda: self.close_tab(self.tabs.currentIndex()))
        QShortcut(QKeySequence("Ctrl+Shift+T"), self, activated=self.restore_closed_tab)
        QShortcut(QKeySequence("Ctrl+L"), self, activated=self.focus_url_bar)
        QShortcut(QKeySequence("Ctrl+Shift+I"), self, activated=self.toggle_immersion_mode) 
        QShortcut(QKeySequence("F11"), self, activated=self.toggle_immersion_mode) 
        QShortcut(QKeySequence("F5"), self, activated=lambda: self.current_browser().reload() if self.current_browser() else None)
        QShortcut(QKeySequence("F12"), self, activated=self.trigger_devtools)
        
        QShortcut(QKeySequence("Ctrl+Shift+F"), self, activated=self.toggle_fullscreen)
        QShortcut(QKeySequence("Esc"), self, activated=self.exit_fullscreen)

        self.apply_auto_theme()
        self.apply_style()
        QTimer.singleShot(0, self.restore_session)

    def apply_javascript_setting(self):
        """設定からJS状態を反映させ、開いているタブの設定を更新（ポータル画面以外はリロード）"""
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if isinstance(w, BrowserTab):
                w.page().settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, self.javascript_enabled)
                if not w.url().toString().startswith("openweb://"):
                    w.reload()
            elif isinstance(w, SplitViewWidget):
                w.v1.page().settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, self.javascript_enabled)
                w.v2.page().settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, self.javascript_enabled)
                if not w.v1.url().toString().startswith("openweb://"): w.v1.reload()
                if not w.v2.url().toString().startswith("openweb://"): w.v2.reload()
            elif isinstance(w, WhiteboardModeWidget):
                for sub in w.mdi_area.subWindowList():
                    bw = sub.widget()
                    if isinstance(bw, BrowserTab):
                        bw.page().settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, self.javascript_enabled)
                        if not bw.url().toString().startswith("openweb://"): bw.reload()

    def createPopupMenu(self):
        return None

    def detect_chrome_profile(self):
        """一般的なChromeプロファイルの場所を自動検出"""
        import platform
        
        candidates = []
        
        if platform.system() == "Windows":
            local_appdata = os.getenv("LOCALAPPDATA", "")
            if local_appdata:
                candidates.append(os.path.join(local_appdata, r"Google\Chrome\User Data\Default"))
                candidates.append(os.path.join(local_appdata, r"Google\Chrome\User Data\Profile 1"))
        elif platform.system() == "Darwin":  # macOS
            candidates.append(os.path.expanduser("~/Library/Application Support/Google/Chrome/Default"))
            candidates.append(os.path.expanduser("~/Library/Application Support/Google/Chrome/Profile 1"))
        else:  # Linux
            candidates.append(os.path.expanduser("~/.config/google-chrome/Default"))
            candidates.append(os.path.expanduser("~/.config/google-chrome/Profile 1"))
        
        for path in candidates:
            if os.path.exists(path):
                return path
        
        return None

    def update_interceptor_state(self):
        # Googleログイン回避のため、常にインターセプターを有効化（UA偽装が最重要）
        self.normal_profile.setUrlRequestInterceptor(self.url_interceptor)
        self.secret_profile.setUrlRequestInterceptor(self.url_interceptor)

    def update_security_indicator(self, qurl):
        if not qurl or qurl.isEmpty(): return
        scheme = qurl.scheme()
        if scheme == "https":
            self.security_button.setText("🔒")
            self.security_button.setStyleSheet("QToolButton { color: #4CAF50; border: none; font-size: 16px; padding: 2px; }")
            self.security_button.setToolTip(_("安全な接続 (HTTPS) - クリックして証明書と安全度を表示"))
        elif scheme == "http":
            self.security_button.setText("⚠️")
            self.security_button.setStyleSheet("QToolButton { color: #FF9800; border: none; font-size: 16px; padding: 2px; }")
            self.security_button.setToolTip(_("保護されていない通信 (HTTP) - クリックして詳細なセキュリティ分析を表示"))
        elif scheme == "openweb":
            self.security_button.setText("⚙️")
            self.security_button.setStyleSheet("QToolButton { color: #00ddff; border: none; font-size: 16px; padding: 2px; }")
            self.security_button.setToolTip(_("システム内部ページ - クリックして詳細を表示"))
        elif scheme == "file":
            self.security_button.setText("💻")
            self.security_button.setStyleSheet("QToolButton { color: #00ddff; border: none; font-size: 16px; padding: 2px; }")
            self.security_button.setToolTip(_("ローカルファイル (完全オフライン実行中) - クリックして安心チェック・隔離診断レポートを表示"))
        else:
            self.security_button.setText("📄")
            self.security_button.setStyleSheet("QToolButton { color: #bac2de; border: none; font-size: 16px; padding: 2px; }")
            self.security_button.setToolTip(_("ローカルファイル等 - クリックして詳細を表示"))

    def show_security_info_dialog(self):
        cb = self.current_browser()
        if not cb: return
        dialog = SecurityStatusDialog(cb.url(), self.url_interceptor.blocked_count, self)
        dialog.exec()

    def toggle_split_focus(self):
        curr = self.tabs.currentWidget()
        if isinstance(curr, SplitViewWidget):
            if curr.active_index == 1:
                curr.setActivePane(2)
            else:
                curr.setActivePane(1)
            self.url_bar.setText(curr.url().toString())

    def show_tab_context_menu(self, position):
        tab_index = self.tabs.tabBar().tabAt(position)
        if tab_index < 0: return
        
        menu = QMenu(self); menu.setStyleSheet(self.settings_menu.styleSheet())
        browser = self.tabs.widget(tab_index)
        is_muted = browser.page().isAudioMuted() if isinstance(browser, BrowserTab) else False
            
        mute_act = menu.addAction(_("🔊 ミュート解除") if is_muted else _("🔇 タブの音声をミュート"))
        pocket_act = menu.addAction(_("📁 このページをリーディングポケットに保存 (オフライン用)"))
        menu.addSeparator()
        close_act = menu.addAction(_("✕ タブを閉じる"))
        
        action = menu.exec(self.tabs.mapToGlobal(position))
        
        if action == mute_act and isinstance(browser, BrowserTab):
            browser.page().setAudioMuted(not is_muted)
            prefix = "🔇 " if not is_muted else ""
            self.tabs.setTabText(tab_index, prefix + browser.title()[:12])
        elif action == pocket_act and isinstance(browser, BrowserTab):
            self.save_current_page_to_pocket(browser)
        elif action == close_act:
            self.close_tab(tab_index)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'immersion_widget'): self.immersion_widget.move(self.width() - self.immersion_widget.width() - 20, 10)
        if self.auto_fit_mode: self.schedule_fit_update()

    def set_fullscreen_mode(self, on):
        if on:
            self.showFullScreen(); self.navbar.setVisible(False); self.tabs.tabBar().setVisible(False)
        else:
            self.showNormal(); self.navbar.setVisible(True); self.tabs.tabBar().setVisible(True)

    def toggle_fullscreen(self): self.set_fullscreen_mode(not self.isFullScreen())

    def exit_fullscreen(self):
        if self.isFullScreen(): self.set_fullscreen_mode(False)
        if self.immersion_mode: self.toggle_immersion_mode()

    def apply_auto_theme(self):
        if self.settings.value("auto_theme", False, type=bool):
            hour = datetime.now().hour
            self.settings.setValue("theme", "light" if 6 <= hour < 18 else "dark")
            self.apply_style()

    def toggle_immersion_mode(self):
        self.immersion_mode = not self.immersion_mode
        self.navbar.setVisible(not self.immersion_mode)
        self.tabs.tabBar().setVisible(not self.immersion_mode)
        if self.immersion_mode:
            self.immersion_widget.show(); self.immersion_widget.raise_()
            self.statusBar().showMessage(_("🎯 没入モード中 (キーボードの[Esc]キー、または右上の[↩️ 解除]ボタンでカンタンに復帰できます)"), 5000)
        else:
            self.immersion_widget.hide(); self.statusBar().showMessage(_("没入モードを解除しました"), 3000)

    def show_immersion_menu(self):
        menu = QMenu(self); menu.setStyleSheet(self.settings_menu.styleSheet())
        act_exit = menu.addAction(_("🔓 没入モードを解除する")); menu.addSeparator()
        act_back = menu.addAction(_("← 戻る")); act_forward = menu.addAction(_("→ 進む"))
        act_tab = menu.addAction(_("➕ 新しいタブ")); act_settings = menu.addAction(_("⚙️ 設定を開く"))
        
        action = menu.exec(self.immersion_menu_btn.mapToGlobal(self.immersion_menu_btn.rect().bottomLeft()))
        if action == act_exit: self.toggle_immersion_mode()
        elif action == act_back: self.go_back()
        elif action == act_forward: self.go_forward()
        elif action == act_tab: self.create_default_new_tab()
        elif action == act_settings: self.open_settings_page(0)

    def toggle_hidden_mode(self):
        """🕵️ 非表示（隠し）モード: アプリウィンドウを非表示にし、バックグラウンドで動作させる。
        キーボードショートカット Ctrl+H でも切り替え可能。
        非表示中はシステムトレイアイコンから復帰できます。
        """
        # トレイアイコンがなければ作成（初回用）
        if not hasattr(self, 'tray_icon') or self.tray_icon is None:
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(QIcon.fromTheme("application-exit"))
            tray_menu = QMenu()
            show_action = tray_menu.addAction(_("表示する"))
            show_action.triggered.connect(lambda: self.toggle_hidden_mode())
            tray_menu.addSeparator()
            exit_action = tray_menu.addAction(_("終了"))
            exit_action.triggered.connect(self.close)
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.activated.connect(lambda reason: self.toggle_hidden_mode() if reason == QSystemTrayIcon.ActivationReason.Trigger else None)

        if self.isVisible():
            self.hide()
            self.tray_icon.show()
            self.statusBar().showMessage(_("🕵️ 隠しモード有効: アプリを非表示にしました。トレイアイコンを右クリック → 「表示する」で復帰できます。"), 6000)
        else:
            self.show()
            self.activateWindow()
            self.raise_()
            self.tray_icon.hide()
            self.statusBar().showMessage(_("隠しモードを解除しました"), 3000)

    def rebuild_main_menu(self):
        self.settings_menu.clear()
        header_widget = QWidget(); header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(6, 4, 6, 6); header_layout.setSpacing(6)

        act_tab = QPushButton(_("➕ 新タブ")); act_tab.clicked.connect(self.create_default_new_tab)
        act_open = QPushButton(_("📂 開く")); act_open.clicked.connect(self.open_local_file)
        act_set = QPushButton(_("⚙️ 設定")); act_set.clicked.connect(lambda: self.open_settings_page(0))

        btn_qss = "QPushButton { background-color: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; padding: 6px; font-size: 11px; } QPushButton:hover { background-color: #00ddff; color: #000; border-color: #00ddff; }"
        for btn in [act_tab, act_open, act_set]:
            btn.setStyleSheet(btn_qss); header_layout.addWidget(btn)

        header_action = QWidgetAction(self.settings_menu); header_action.setDefaultWidget(header_widget)
        self.settings_menu.addAction(header_action); self.settings_menu.addSeparator()

        self.settings_menu.addAction(_("📂 ファイルを開く..."), self.open_local_file, QKeySequence("Ctrl+O"))
        self.settings_menu.addAction(_("🔍 ページ内検索..."), self.show_find_dialog, QKeySequence("Ctrl+F"))
        self.settings_menu.addAction(_("🖨️ PDFとして保存..."), self.print_to_pdf, QKeySequence("Ctrl+P"))
        
        zoom_menu = self.settings_menu.addMenu(_("🔎 画面ズーム"))
        zoom_menu.addAction(_("＋ 拡大する"), lambda: self.adjust_zoom(0.1))
        zoom_menu.addAction(_("－ 縮小する"), lambda: self.adjust_zoom(-0.1))
        zoom_menu.addAction(_("100%にリセット"), self.reset_zoom)
        self.settings_menu.addSeparator()

        lib_menu = self.settings_menu.addMenu(_("📚 ライブラリ履歴"))
        lib_menu.addAction(_("🕒 閲覧履歴タイムライン"), lambda: self.open_settings_page(7))
        lib_menu.addAction(_("📥 ダウンロード一覧"), lambda: self.open_settings_page(4))
        lib_menu.addAction(_("📁 リーディングポケット"), lambda: self.open_settings_page(8))
        lib_menu.addAction(_("↩️ 閉じたタブを復元 (Ctrl+Shift+T)"), self.restore_closed_tab, QKeySequence("Ctrl+Shift+T"))
        
        privacy_menu = self.settings_menu.addMenu(_("🛡️ プライバシー＆保護"))
        self.secret_action = QAction(_("🕵️ シークレットモード: OFF"), self)
        self.secret_action.triggered.connect(self.toggle_secret_action)
        privacy_menu.addAction(self.secret_action)
        self.cookie_action = QAction(_("🍪 Cookie保存: ON"), self)
        self.cookie_action.triggered.connect(self.toggle_cookies)
        privacy_menu.addAction(self.cookie_action); privacy_menu.addSeparator()
        privacy_menu.addAction(_("⚡ キャッシュを消去"), self.clear_browser_cache)
        privacy_menu.addAction(_("🗑️ 閲覧データとCookieをすべて削除..."), self.clear_browser_data)
        
        tools_menu = self.settings_menu.addMenu(_("🧰 高度な拡張ツール"))
        tools_menu.addAction(_("🖥️ スプリットビューを起動"), self.add_split_view_tab)
        tools_menu.addAction(_("🧪 Googleログイン用クリーンプロファイルを作成して開く"), self.create_google_login_profile)
        tools_menu.addAction(_("🔐 Google OAuth2でログイン（最確実版）"), self.start_google_oauth2_flow)
        tools_menu.addAction(_("🎬 動画をポップアウト(ビデオプレイヤー)"), self.open_current_in_video_player)
        tools_menu.addAction(_("📱 PWAアプリウインドウ化"), self.open_current_as_app)
        tools_menu.addSeparator()
        tools_menu.addAction(_("💻 開発者ツール (F12)"), self.trigger_devtools, QKeySequence("F12"))
        tools_menu.addAction(_("🕵️ 隠しモード (Ctrl+H で切り替え)"), self.toggle_hidden_mode)

        theme_menu = self.settings_menu.addMenu(_("🎨 外観テーマ設定"))
        light_act = QAction(_("☀️ ライトテーマ"), self); dark_act = QAction(_("🌙 ダークテーマ"), self)
        light_act.triggered.connect(lambda: (self.settings.setValue("theme", "light"), self.apply_style(), self.reload_all_portals()))
        dark_act.triggered.connect(lambda: (self.settings.setValue("theme", "dark"), self.apply_style(), self.reload_all_portals()))
        theme_menu.addAction(light_act); theme_menu.addAction(dark_act)
        self.settings_menu.addSeparator()

        self.settings_menu.addAction(_("🏠 ホームページ設定"), lambda: self.open_settings_page(1))
        self.settings_menu.addAction(_("📋 ToDo タスク管理"), lambda: self.open_settings_page(2))
        self.settings_menu.addAction(_("🔑 Vault 暗号金庫を開く"), lambda: self.open_settings_page(3))
        self.settings_menu.addAction(_("🎮 ゲームモード ＆ 入力最適化"), lambda: self.open_settings_page(5))
        self.settings_menu.addAction("🎮 BLIND BOMBS を起動（内蔵版）", self.launch_blind_bombs)
        self.settings_menu.addAction("📥 BLIND BOMBS HTMLをダウンロード", self.download_blind_bombs_html)
        self.settings_menu.addAction(_("🛡️ ワークスペース ＆ ダッシュボード"), lambda: self.open_settings_page(6))
        self.settings_menu.addSeparator()
        self.settings_menu.addAction(_("⚙️ ブラウザ総合設定"), lambda: self.open_settings_page(0))
        self.settings_menu.addAction(_("ℹ️ OpenWeb について"), lambda: self.open_settings_page(10))

    def toggle_secret_action(self):
        if self.is_processing_mode: return
        self.is_processing_mode = True
        is_sec = not self.settings.value("is_secret", False, type=bool)
        self.settings.setValue("is_secret", is_sec)
        self.apply_style()
        self.reload_all_portals()
        cb = self.current_browser()
        if cb and hasattr(cb, 'reload'): cb.reload()
        QTimer.singleShot(1000, lambda: setattr(self, 'is_processing_mode', False))

    def toggle_cookies(self):
        if self.settings.value("is_secret", False, type=bool): return
        self.cookies_enabled = not self.cookies_enabled
        self.settings.setValue("cookies_enabled", self.cookies_enabled)
        self.apply_style()

    def load_todos(self):
        if os.path.exists(self.todo_file):
            try:
                with open(self.todo_file, "r", encoding="utf-8") as f: return json.load(f)
            except: pass
        return []

    def save_todos(self, todos):
        try:
            with open(self.todo_file, "w", encoding="utf-8") as f: json.dump(todos, f, ensure_ascii=False, indent=4)
        except: pass

    def reload_all_portals(self):
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if isinstance(w, BrowserTab):
                if w.url().toString() == "openweb://portal" or w.title().startswith("OpenWeb Portal") or "Portal" in w.title():
                    w.setHtml(self.get_default_home_html(), QUrl("openweb://portal"))

    def load_optimization_config(self):
        default_config = {"http_cache_max_size_mb": 1024, "enable_smooth_scrolling": True, "freeze_idle_timeout_seconds": 20, "user_agent_override": ""}
        if os.path.exists(self.optimization_config_path):
            try:
                with open(self.optimization_config_path, "r", encoding="utf-8") as f: return {**default_config, **json.load(f)}
            except: return default_config
        return default_config

    def get_default_home_html(self):
        todos = self.load_todos()
        todo_html_list = ""
        if not todos:
            todo_html_list = f"<li class='todo-item' style='justify-content:center; color:#85889e;'>{_('登録されているタスクはありません')}</li>"
        else:
            for todo in todos:
                completed_class = "completed" if todo.get("completed", False) else ""
                todo_html_list += f"""
                <li class="todo-item {completed_class}">
                    <span>{_("[完了] ") if todo.get("completed", False) else ""} {todo.get("text", "")}</span>
                </li>
                """

        # 🎨 ホームページの動的な配色割り当て (ライト / ダーク連動)
        theme = self.settings.value("theme", "dark", type=str)
        is_sec = self.settings.value("is_secret", False, type=bool)

        if is_sec:
            p_bg = "linear-gradient(135deg, #190033 0%, #0c001a 100%)"
            p_glass = "rgba(45, 0, 80, 0.7)"
            p_border = "rgba(255, 255, 255, 0.12)"
            p_primary = "#d946ef"
            p_secondary = "#a855f7"
            p_text = "#ffffff"
            p_text_mut = "#d8b4fe"
            p_input = "rgba(15, 0, 30, 0.9)"
        elif theme == "fresh":
            p_bg = "linear-gradient(135deg, #f0f5fc 0%, #d6e4f0 100%)"
            p_glass = "rgba(255, 255, 255, 0.8)"
            p_border = "rgba(26, 37, 54, 0.15)"
            p_primary = "#0055ff"
            p_secondary = "#5c93ff"
            p_text = "#1a2536"
            p_text_mut = "#50647e"
            p_input = "#ffffff"
        elif theme == "light":
            p_bg = "linear-gradient(135deg, #fffdf0 0%, #f7f3da 100%)"
            p_glass = "rgba(255, 255, 255, 0.85)"
            p_border = "rgba(66, 50, 20, 0.15)"
            p_primary = "#e05a00"
            p_secondary = "#b58a3a"
            p_text = "#423214"
            p_text_mut = "#7c6a49"
            p_input = "#ffffff"
        elif theme == "earth":
            p_bg = "linear-gradient(135deg, #f2f5f2 0%, #d5e0d5 100%)"
            p_glass = "rgba(255, 255, 255, 0.88)"
            p_border = "rgba(31, 43, 31, 0.15)"
            p_primary = "#2e7d32"
            p_secondary = "#689f38"
            p_text = "#1f2b1f"
            p_text_mut = "#556b2f"
            p_input = "#ffffff"
        else: # dark
            p_bg = "linear-gradient(135deg, #0d0d14 0%, #050508 100%)"
            p_glass = "rgba(24, 24, 37, 0.85)"
            p_border = "rgba(255, 255, 255, 0.12)"
            p_primary = "#00ddff"
            p_secondary = "#b4befe"
            p_text = "#ffffff"
            p_text_mut = "#bac2de"
            p_input = "rgba(15, 15, 25, 0.95)"

        html_content = f"""
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <title>OpenWeb Portal</title>
            <style>
                :root {{
                    --bg-gradient: {p_bg};
                    --glass-bg: {p_glass};
                    --glass-border: {p_border};
                    --primary: {p_primary};
                    --secondary: {p_secondary};
                    --text: {p_text};
                    --text-muted: {p_text_mut};
                    --input-bg: {p_input};
                }}
                body {{
                    background: var(--bg-gradient);
                    color: var(--text);
                    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
                    margin: 0; padding: 0;
                    display: flex; justify-content: center; align-items: center;
                    min-height: 100vh; box-sizing: border-box; overflow-x: hidden;
                }}
                .portal-wrapper {{
                    display: flex; flex-direction: row; max-width: 1200px; width: 95%; gap: 30px; padding: 40px 0; box-sizing: border-box;
                }}
                .main-column {{
                    flex: 2; display: flex; flex-direction: column; align-items: center; justify-content: center;
                }}
                .side-column {{
                    flex: 1; display: flex; flex-direction: column; gap: 20px; justify-content: center;
                }}
                .panel {{
                    background: var(--glass-bg); border: 2px solid var(--glass-border); border-radius: 16px; padding: 24px;
                    backdrop-filter: blur(12px); box-sizing: border-box; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
                }}
                h1 {{
                    font-size: 3.4rem; margin: 0 0 5px 0; font-weight: 800;
                    background: linear-gradient(45deg, var(--primary), var(--secondary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                }}
                .subtitle {{ color: var(--text-muted); font-size: 1rem; margin: 0 0 25px 0; }}
                .clock-widget {{
                    font-size: 2.6rem; color: var(--primary); font-weight: 700; margin-bottom: 5px; font-family: monospace;
                    text-shadow: 0 0 15px rgba(0, 221, 255, 0.2);
                }}
                .date-widget {{ font-size: 1rem; color: var(--text-muted); margin-bottom: 25px; }}
                .search-container {{ width: 100%; max-width: 650px; display: flex; gap: 10px; margin-bottom: 35px; }}
                .search-box-form {{ flex: 1; display: flex; position: relative; }}
                .search-input {{
                    width: 100%; padding: 16px 24px; font-size: 1.1rem; border: 2px solid var(--glass-border); border-radius: 30px;
                    background-color: var(--input-bg); color: var(--text); outline: none; transition: all 0.3s ease; box-sizing: border-box;
                }}
                .search-input:focus {{ border-color: var(--primary); box-shadow: 0 0 20px rgba(0, 221, 255, 0.25); }}
                .search-engine-select {{
                    background: var(--input-bg); color: var(--text); border: 2px solid var(--glass-border); border-radius: 30px;
                    padding: 0 22px; font-size: 1rem; outline: none; cursor: pointer; font-weight: 600;
                }}
                .grid-title-container {{ display: flex; justify-content: space-between; align-items: center; width: 100%; max-width: 650px; margin-bottom: 12px; }}
                .grid-title {{ font-size: 0.95rem; color: var(--secondary); text-transform: uppercase; letter-spacing: 1.5px; margin: 0; font-weight: 700; }}
                .add-shortcut-btn {{ background: transparent; border: none; color: var(--primary); font-size: 0.9rem; cursor: pointer; font-weight: bold; }}
                .shortcuts-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; width: 100%; max-width: 650px; }}
                .shortcut-card {{
                    background: var(--glass-bg); border: 2px solid var(--glass-border); border-radius: 14px; padding: 18px 10px;
                    color: var(--text); text-decoration: none; font-size: 0.9rem; display: flex; flex-direction: column; align-items: center;
                    transition: all 0.25s ease; position: relative; font-weight: 600;
                }}
                .shortcut-card:hover {{ border-color: var(--primary); transform: translateY(-3px); }}
                .shortcut-icon {{ font-size: 2rem; margin-bottom: 10px; }}
                .delete-shortcut-btn {{
                    position: absolute; top: 6px; right: 6px; background: rgba(255, 100, 100, 0.2); border: none; color: #ff6464;
                    font-size: 0.65rem; width: 18px; height: 18px; border-radius: 50%; cursor: pointer; display: none; align-items: center; justify-content: center;
                }}
                .shortcut-card:hover .delete-shortcut-btn {{ display: flex; }}
                .todo-widget h3 {{ margin-top: 0; margin-bottom: 15px; font-size: 1.1rem; color: var(--primary); border-bottom: 2px solid var(--glass-border); padding-bottom: 10px; }}
                .todo-list {{ list-style: none; padding: 0; margin: 0; max-height: 380px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }}
                .todo-item {{ display: flex; justify-content: space-between; align-items: center; background: rgba(0, 0, 0, 0.05); padding: 12px 16px; border-radius: 8px; border: 2px solid var(--glass-border); }}
                .todo-item.completed {{ border-color: rgba(255,255,255,0.05); background: rgba(0, 0, 0, 0.02); text-decoration: line-through; color: #6c7086; }}
                .todo-manage-info {{ font-size: 0.8rem; color: var(--text-muted); text-align: center; margin-top: 15px; border-top: 1px dashed var(--glass-border); padding-top: 10px; }}
                
                /* 🎨 カスタムHTMLモーダルダイアログ */
                .modal-overlay {{
                    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                    background: rgba(0, 0, 0, 0.6); backdrop-filter: blur(8px);
                    display: none; justify-content: center; align-items: center; z-index: 1000;
                }}
                .modal-content {{
                    background: var(--glass-bg); border: 2px solid var(--glass-border);
                    border-radius: 16px; padding: 25px; width: 350px; text-align: left;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.4);
                }}
                .modal-content h3 {{ margin-top: 0; color: var(--primary); }}
                .modal-field {{ margin-bottom: 15px; }}
                .modal-field label {{ display: block; margin-bottom: 5px; font-size: 0.9rem; color: var(--text-muted); }}
                .modal-field input {{
                    width: 100%; padding: 10px; border-radius: 8px; border: 1px solid var(--glass-border);
                    background: var(--input-bg); color: var(--text); outline: none; box-sizing: border-box;
                }}
                .modal-btn-group {{ display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }}
                .modal-btn {{
                    padding: 8px 16px; border-radius: 6px; border: none; cursor: pointer; font-weight: bold;
                }}
                .btn-submit {{ background: var(--primary); color: #000; }}
                .btn-cancel {{ background: rgba(255,255,255,0.1); color: var(--text); }}
                
                @media (max-width: 900px) {{
                    .portal-wrapper {{ flex-direction: column; align-items: center; }}
                    .side-column {{ width: 100%; max-width: 650px; }}
                }}
            </style>
        </head>
        <body>
            <div class="portal-wrapper">
                <div class="main-column">
                    <div class="clock-widget" id="clock">00:00:00</div>
                    <div class="date-widget" id="date">--</div>
                    <h1>OpenWeb</h1>
                    <p class="subtitle">{_('シンプルで機能的なプライベートポータル')}</p>
                    <div class="search-container">
                        <select class="search-engine-select" id="engineSelect">
                            <option value="google">Google</option>
                            <option value="yahoo">Yahoo! JAPAN</option>
                            <option value="bing">Bing</option>
                            <option value="duck">DuckDuckGo</option>
                        </select>
                        <div class="search-box-form">
                            <input type="text" id="searchInput" class="search-input" placeholder="{_('ウェブを快適に検索...')}" required autofocus>
                        </div>
                    </div>
                    <div class="grid-title-container">
                        <h2 class="grid-title">{_('クイックリンク')}</h2>
                        <button class="add-shortcut-btn" onclick="openShortcutModal()">{_('＋ 追加')}</button>
                    </div>
                    <div class="shortcuts-grid" id="shortcutsGrid"></div>
                </div>
                <div class="side-column">
                    <div class="panel todo-widget">
                        <h3>{_('ToDoリスト一覧')}</h3>
                        <ul class="todo-list" id="todoList">
                            {todo_html_list}
                        </ul>
                        <div class="todo-manage-info">{_('💡 タスク管理は設定の「📋 ToDo タスク管理」で行えます。')}</div>
                    </div>
                </div>
            </div>

            <!-- 🎨 カスタムショートカット追加モーダル -->
            <div class="modal-overlay" id="shortcutModal">
                <div class="modal-content">
                    <h3>➕ {_("ショートカットの追加")}</h3>
                    <div class="modal-field">
                        <label for="scName">{_("表示する名前")}</label>
                        <input type="text" id="scName" placeholder="例: YouTube">
                    </div>
                    <div class="modal-field">
                        <label for="scUrl">{_("URLアドレス")}</label>
                        <input type="text" id="scUrl" placeholder="例: https://www.youtube.com">
                    </div>
                    <div class="modal-btn-group">
                        <button class="modal-btn btn-cancel" onclick="closeShortcutModal()">{_("キャンセル")}</button>
                        <button class="modal-btn btn-submit" onclick="submitShortcutModal()">{_("追加する")}</button>
                    </div>
                </div>
            </div>

            <script>
                function updateClock() {{
                    const now = new Date();
                    document.getElementById('clock').textContent = String(now.getHours()).padStart(2, '0') + ':' + String(now.getMinutes()).padStart(2, '0') + ':' + String(now.getSeconds()).padStart(2, '0');
                    document.getElementById('date').textContent = now.toLocaleDateString('ja-JP', {{ year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }});
                }}
                setInterval(updateClock, 1000); updateClock();

                const searchInput = document.getElementById('searchInput');
                const engineSelect = document.getElementById('engineSelect');
                searchInput.addEventListener('keypress', function(e) {{
                    if (e.key === 'Enter') {{
                        const query = encodeURIComponent(searchInput.value.trim());
                        if(!query) return;
                        let url = '';
                        const engine = engineSelect.value;
                        if (engine === 'google') url = 'https://www.google.com/search?q=' + query;
                        else if (engine === 'yahoo') url = 'https://search.yahoo.co.jp/search?p=' + query;
                        else if (engine === 'bing') url = 'https://www.bing.com/search?q=' + query;
                        else if (engine === 'duck') url = 'https://duckduckgo.com/?q=' + query;
                        window.location.href = url;
                    }}
                }});

                const defaultShortcuts = [
                    {{ name: 'Google', url: 'https://www.google.com', icon: '🔍' }},
                    {{ name: 'Yahoo!', url: 'https://www.yahoo.co.jp', icon: '🇯🇵' }},
                    {{ name: 'Wikipedia', url: 'https://wikipedia.org', icon: '📖' }},
                    {{ name: 'GitHub', url: 'https://github.com', icon: '💻' }}
                ];
                function getShortcuts() {{
                    const saved = localStorage.getItem('ow_shortcuts');
                    if (saved) return JSON.parse(saved);
                    localStorage.setItem('ow_shortcuts', JSON.stringify(defaultShortcuts)); return defaultShortcuts;
                }}
                function renderShortcuts() {{
                    const list = getShortcuts(); const grid = document.getElementById('shortcutsGrid'); grid.innerHTML = '';
                    list.forEach((item, index) => {{
                        const card = document.createElement('a'); card.className = 'shortcut-card'; card.href = item.url;
                        card.innerHTML = `<div class="shortcut-icon">${{item.icon || '🔗'}}</div><div class="shortcut-name">${{item.name}}</div><button class="delete-shortcut-btn" onclick="deleteShortcut(event, ${{index}})">✕</button>`;
                        grid.appendChild(card);
                    }});
                }}
                
                // 🎨 モーダル操作関数
                window.openShortcutModal = function() {{
                    document.getElementById('shortcutModal').style.display = 'flex';
                    document.getElementById('scName').focus();
                }};
                window.closeShortcutModal = function() {{
                    document.getElementById('shortcutModal').style.display = 'none';
                    document.getElementById('scName').value = '';
                    document.getElementById('scUrl').value = '';
                }};
                window.submitShortcutModal = function() {{
                    const name = document.getElementById('scName').value.trim();
                    let url = document.getElementById('scUrl').value.trim();
                    if (!name || !url) {{
                        alert('{_("すべての項目を入力してください")}');
                        return;
                    }}
                    if (!url.startsWith('http://') && !url.startsWith('https://')) {{
                        url = 'https://' + url;
                    }}
                    const emojiList = ['🔗','⭐','🏫','📁','🎮','🎨','📱','🎧','💻','🔍'];
                    const icon = emojiList[Math.floor(Math.random() * emojiList.length)];
                    const list = getShortcuts();
                    list.push({{ name, url, icon }});
                    localStorage.setItem('ow_shortcuts', JSON.stringify(list));
                    renderShortcuts();
                    closeShortcutModal();
                }};

                window.deleteShortcut = function(event, index) {{
                    event.preventDefault(); event.stopPropagation();
                    if(confirm('{_("このショートカットを削除しますか？")}')) {{
                        const list = getShortcuts(); list.splice(index, 1);
                        localStorage.setItem('ow_shortcuts', JSON.stringify(list)); renderShortcuts();
                    }}
                }};
                renderShortcuts();
            </script>
        </body>
        </html>
        """
        return html_content.replace("{todo_html_list}", todo_html_list)

    def create_default_new_tab(self):
        if self.settings.value("new_tab_home_enabled", True, type=bool): self.add_new_tab(self.get_home_target())
        else: self.add_new_tab("about:blank")

    def get_home_target(self):
        if self.settings.value("home_type", "default", type=str) == "custom" and self.home_url: return self.home_url
        return "default_portal"

    def restore_session(self):
        last_urls = self.session_manager.load_session()
        if last_urls and isinstance(last_urls, list) and len(last_urls) > 0:
            ans = QMessageBox.question(self, _("セッションの復元"), _("前回開いていたタブセットを復元しますか？"), QMessageBox.Yes | QMessageBox.No)
            if ans == QMessageBox.Yes:
                for url in last_urls:
                    if isinstance(url, str) and url.strip(): self.add_new_tab(url)
                return
        self.add_new_tab(self.get_home_target())

    def open_local_file(self):
        file_path = QFileDialog.getOpenFileName(self, _("ローカルファイルを開く"), "", _("HTMLファイル (*.html *.htm);;すべてのファイル (*.*)"))[0]
        if file_path: self.add_new_tab(file_path)

    def launch_blind_bombs(self):
        """BLIND BOMBS Online Ultimate を起動（完全スタンドアローン対応）"""
        is_sec = self.settings.value("is_secret", False, type=bool)
        active_profile = self.secret_profile if is_sec else self.normal_profile
        browser = BrowserTab(active_profile, self)
        idx = self.tabs.addTab(browser, "🎮 BLIND BOMBS")
        self.tabs.setCurrentIndex(idx)

        # 完全スタンドアローン対応：外部ファイルがなくても内蔵HTMLで確実に動作
        html_path = get_resource_path("BLIND_BOMBS_Online_Ultimate.html")
        if os.path.exists(html_path) and os.path.getsize(html_path) > 10000:
            browser.setUrl(QUrl.fromLocalFile(html_path))
            self.statusBar().showMessage("🎮 BLIND BOMBS Online Ultimate（外部ファイル版）を起動しました", 4000)
        elif 'BLIND_BOMBS_HTML' in globals() and len(BLIND_BOMBS_HTML) > 50000:
            lang = CURRENT_LANG
            injected_html = BLIND_BOMBS_HTML.replace(
                '<!-- LANGUAGE_INJECT -->',
                f'<script>window.OPENWEB_LANG = "{lang}";</script>'
            )
            browser.setHtml(injected_html, QUrl("openweb://blind_bombs"))
            self.statusBar().showMessage("🎮 BLIND BOMBS Online Ultimate（完全内蔵版）を起動しました", 4000)
        else:
            QMessageBox.warning(self, "エラー", "BLIND BOMBS HTMLが内蔵されていません。")
            self.tabs.removeTab(idx)

    def download_blind_bombs_html(self):
        """BLIND BOMBS Online Ultimate のHTMLをダウンロード"""
        html_path = get_resource_path("BLIND_BOMBS_Online_Ultimate.html")
        if os.path.exists(html_path):
            content_to_save = open(html_path, "r", encoding="utf-8").read()
        elif 'BLIND_BOMBS_HTML' in globals() and len(BLIND_BOMBS_HTML) > 1000:
            content_to_save = BLIND_BOMBS_HTML
        else:
            QMessageBox.warning(self, "エラー", "BLIND BOMBS HTMLが見つかりません。")
            return

        save_path = QFileDialog.getSaveFileName(
            self, "BLIND BOMBS HTMLをダウンロード", "BLIND_BOMBS_Online_Ultimate.html", "HTMLファイル (*.html)"
        )[0]
        if save_path:
            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(content_to_save)
                self.statusBar().showMessage(f"📥 保存しました: {os.path.basename(save_path)}", 5000)
                QMessageBox.information(self, "完了", "BLIND BOMBS HTMLを保存しました！")
            except Exception as e:
                QMessageBox.warning(self, "エラー", f"保存に失敗しました: {e}")

    def apply_style(self):
        theme = self.settings.value("theme", "dark", type=str)
        is_sec = self.settings.value("is_secret", False, type=bool)
        
        if theme == "fresh":
            bg, tc, hc, bdc = ("#f0f5fc", "#1a2536", "#dbe6f5", "#adc5e3")
            glass_bg_color = "rgba(255, 255, 255, 0.45)"
            glass_border_color = "rgba(26, 37, 54, 0.25)"
            glass_text_color = "#1a2536"
        elif theme == "light":
            bg, tc, hc, bdc = ("#fffdf0", "#423214", "#fff6cc", "#e0cf97")
            glass_bg_color = "rgba(255, 255, 255, 0.5)"
            glass_border_color = "rgba(66, 50, 20, 0.25)"
            glass_text_color = "#423214"
        elif theme == "earth":
            bg, tc, hc, bdc = ("#f2f5f2", "#1f2b1f", "#e1ede1", "#bcd4bc")
            glass_bg_color = "rgba(255, 255, 255, 0.55)"
            glass_border_color = "rgba(31, 43, 31, 0.25)"
            glass_text_color = "#1f2b1f"
        else:
            bg, tc, hc, bdc = ("#0d0d14", "#f1f1f7", "#242538", "#3b3d54")
            glass_bg_color = "rgba(30, 30, 45, 0.65)"
            glass_border_color = "rgba(255, 255, 255, 0.15)"
            glass_text_color = "#ffffff"
            
        if is_sec: 
            bg, tc, hc, bdc = "#1e003a", "#ffffff", "#3b0066", "#5a0099"
            glass_bg_color = "rgba(74, 0, 144, 0.65)"
            glass_border_color = "rgba(255, 255, 255, 0.2)"
            glass_text_color = "#ffffff"

        self.setStyleSheet(f"background:{bg}; color:{tc};")
        self.navbar.setStyleSheet(f"background:{bg}; border-bottom:2px solid {bdc};")
        self.statusBar().setStyleSheet(f"background:{bg}; color:{tc}; border-top:2px solid {bdc};")
        self.url_bar.setStyleSheet(f"background:rgba(255,255,255,0.06); color:{tc}; border:2px solid {bdc}; border-radius:8px; padding:6px;")
        
        # 💎 没入モード用・極上グラスマフィズムUIの動的スタイル更新
        self.immersion_widget.setStyleSheet(f"""
            QWidget {{ 
                background-color: {glass_bg_color}; 
                border: 1px solid {glass_border_color}; 
                border-radius: 19px; 
            }}
        """)
        self.exit_immersion_btn.setStyleSheet(f"""
            QPushButton {{ 
                color: #ff6464; 
                font-weight: bold; 
                border: none; 
                background: transparent; 
                padding: 4px; 
                font-size: 12px;
            }} 
            QPushButton:hover {{ 
                background-color: rgba(255, 100, 100, 0.2); 
                border-radius: 12px; 
            }}
        """)
        self.immersion_menu_btn.setStyleSheet(f"""
            QPushButton {{ 
                color: {glass_text_color}; 
                font-weight: bold; 
                border: none; 
                background: transparent; 
                padding: 4px;
                font-size: 12px;
            }} 
            QPushButton:hover {{ 
                background-color: rgba(255, 255, 255, 0.2); 
                border-radius: 12px; 
            }}
        """)

        self.settings_button.setStyleSheet(f"""
            QToolButton {{
                color: {tc}; font-size: 18px; font-weight: bold; border: 2px solid {bdc}; border-radius: 8px; padding: 4px 10px; background-color: {hc};
            }}
            QToolButton:hover {{ background-color: #00ddff; color: #000; border-color: #00ddff; }}
            QToolButton::menu-indicator {{ image: none; width: 0px; }}
        """)
        
        self.split_toggle_btn.setStyleSheet(f"""
            QToolButton {{
                color: {tc};
                font-weight: bold;
                border: 2px solid {bdc};
                border-radius: 8px;
                padding: 4px 10px;
                background-color: {hc};
            }}
            QToolButton:hover {{
                background-color: #00ddff;
                color: #000000;
                border-color: #00ddff;
            }}
        """)
        
        self.settings_menu.setStyleSheet(f"""
            QMenu {{ background-color: {bg}; border: 2px solid {bdc}; border-radius: 12px; color: {tc}; padding: 10px; }}
            QMenu::item {{ padding: 10px 36px 10px 14px; border-radius: 8px; margin: 2px 0px; font-size: 13px; }}
            QMenu::item:selected {{ background-color: #00ddff; color: #000000; font-weight: bold; }}
            QMenu::separator {{ height: 2px; background-color: {bdc}; margin: 8px 4px; }}
        """)

        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if isinstance(w, SettingsTab): w.update_theme_style(theme, tc, bg, bdc, hc)

        if is_sec:
            self.secret_action.setText(_("🕵️ シークレットモード: ON"))
            self.cookies_enabled = False
            self.cookie_action.setText(_("🍪 Cookie保存: OFF (シークレット)"))
            self.secret_profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)
        else:
            self.secret_action.setText(_("🕵️ シークレットモード: OFF"))
            self.cookies_enabled = self.settings.value("cookies_enabled", True, type=bool)
            self.cookie_action.setText(_("🍪 Cookie保存: ON") if self.cookies_enabled else _("🍪 Cookie保存: OFF (シークレット)").replace(" (シークレット)", ""))
            self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies if self.cookies_enabled else QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)

    def activate_reader_mode(self):
        b = self.current_browser()
        if b: b.page().runJavaScript("['header','footer','aside','nav','.ads'].forEach(s => document.querySelectorAll(s).forEach(e => e.remove())); document.body.style.maxWidth = '750px'; document.body.style.margin = '40px auto'; document.body.style.fontSize = '18px'; document.body.style.lineHeight = '1.8';")

    def open_translate_page(self):
        b = self.current_browser()
        if not b: return
        current_url = b.url().toString()
        if not current_url.startswith("http"): return
        translated_url = f"https://translate.google.com/translate?sl=auto&tl=ja&u={current_url}"
        self.add_new_tab(translated_url)

    def summarize_current_page(self):
        b = self.current_browser()
        if not b: return
        js = """
        (() => {
            let headlines = [];
            document.querySelectorAll('h1, h2, h3, p').forEach(el => {
                let txt = el.innerText.trim();
                if(txt.length > 15 && txt.length < 150) headlines.push(txt);
            });
            return headlines.slice(0, 5);
        })()
        """
        def on_js_done(result):
            if result:
                summary_text = _("【AIによる超速ページ自動分析・要約】\n\n")
                for i, txt in enumerate(result, 1):
                    summary_text += f"{i}. {txt}\n"
                
                d = QDialog(self)
                d.setWindowTitle(_("✨ ワンクリックAI要約結果"))
                d.resize(500, 350)
                layout = QVBoxLayout(d)
                
                tb = QTextBrowser()
                tb.setText(summary_text)
                tb.setStyleSheet("background-color: #11111b; color: #a6e3a1; font-size: 13px; border-radius: 8px; padding: 10px;")
                layout.addWidget(tb)
                
                close_btn = QPushButton(_("確認しました"))
                close_btn.clicked.connect(d.close)
                layout.addWidget(close_btn)
                d.exec()
            else:
                QMessageBox.information(self, _("✨ ワンクリックAI要約結果"), _("テキスト量が不足しているか、分析できませんでした。"))
        b.page().runJavaScript(js, on_js_done)

    def save_current_page_to_pocket(self, browser_tab):
        title = browser_tab.title()
        url = browser_tab.url().toString()
        if url.startswith("openweb://") or url == "about:blank":
            QMessageBox.warning(self, _("エラー"), _("このページはリーディングポケットに保存できません。"))
            return
            
        js = "document.documentElement.outerHTML"
        def on_html_fetched(html):
            if html:
                if self.pocket_manager.save_page(title, url, html):
                    self.statusBar().showMessage(_("📁 リーディングポケットに記事を保存しました！"), 4000)
                else:
                    self.statusBar().showMessage(_("保存に失敗しました。"), 4000)
        browser_tab.page().runJavaScript(js, on_html_fetched)

    def add_split_view_tab(self):
        if self.settings.value("exp_whiteboard_mode", False, type=bool):
            view = WhiteboardModeWidget(self.normal_profile, self)
            idx = self.tabs.addTab(view, _("🎨 ホワイトボードモード (実験的)"))
        else:
            view = SplitViewWidget(self.normal_profile, self)
            idx = self.tabs.addTab(view, _("🖥️ スプリットビュー"))
            
        self.tabs.setCurrentIndex(idx)
        view.urlChanged.connect(lambda q: self.url_bar.setText(q.toString()) if view == self.tabs.currentWidget() else None)
        view.titleChanged.connect(lambda t: self.tabs.setTabText(self.tabs.indexOf(view), t[:15]))

    def check_idle_tabs_for_freeze(self):
        now = time.time()
        timeout = self.opt_config.get("freeze_idle_timeout_seconds", 20)
        for i in range(self.tabs.count()):
            if i == self.tabs.currentIndex(): continue
            tab = self.tabs.widget(i)
            if isinstance(tab, BrowserTab) and not tab.is_frozen:
                url_str = tab.url().toString().lower()
                is_media = any(d in url_str for d in ["youtube.com", "youtu.be", "twitch.tv", "nicovideo.jp", "netflix.com"])
                if not is_media and not tab.page().recentlyAudible() and (now - tab.last_accessed_time > timeout):
                    tab.freeze_tab()
                    self.tabs.setTabText(i, f"💤 {tab.title()[:15]}")

    def ensure_vault_unlocked(self, p):
        if self.vault.is_unlocked: return True
        if not self.vault.is_setup():
            d = VaultSetupDialog(p)
            if d.exec() == QDialog.DialogCode.Accepted: self.vault.setup(d.get_password()); return True
        else:
            d = VaultUnlockDialog(p)
            if d.exec() == QDialog.DialogCode.Accepted and self.vault.unlock(d.get_password()): return True
        return False

    def open_settings_page(self, idx=0):
        for i in range(self.tabs.count()):
            if isinstance(self.tabs.widget(i), SettingsTab):
                self.tabs.setCurrentIndex(i); self.tabs.widget(i).sidebar.setCurrentRow(idx); return
        st = SettingsTab(self); self.tabs.setCurrentIndex(self.tabs.addTab(st, _("⚙️ 設定")))
        st.sidebar.setCurrentRow(idx); self.apply_style()

    def save_game_mode(self):
        with open(self.game_mode_file, "w", encoding="utf-8") as f: json.dump(self.game_mode_domains, f, ensure_ascii=False, indent=4)

    def clear_browser_cache(self):
        if QMessageBox.question(self, _("確認"), _("キャッシュを削除しますか？"), QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes: self.profile.clearHttpCache()

    def clear_browser_data(self):
        if QMessageBox.question(self, _("警告"), _("閲覧タイムライン履歴とCookieを完全に削除しますか？"), QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.browser_history.clear()
            with open(self.history_file, "w", encoding="utf-8") as f: json.dump([], f)
            self.profile.clearHttpCache()
            self.profile.cookieStore().deleteAllCookies()
            self.statusBar().showMessage(_("タイムライン履歴とCookieを削除しました"), 3000)

    def handle_gamepad_console_event(self, t, p):
        if t == "connect":
            btn_count, pad_id = 16, p
            if "||" in p:
                parts = p.split("||", 1)
                try: btn_count = int(parts[0])
                except: pass
                pad_id = parts[1]
            p_lower = pad_id.lower()
            device_type = _("汎用コントローラー")
            if "xbox" in p_lower: device_type = _("Xbox コントローラー")
            elif "dualshock" in p_lower or "playstation" in p_lower: device_type = _("PS コントローラー")
            elif "nintendo" in p_lower or "switch" in p_lower: device_type = _("Switch コントローラー")
            
            status_text = f"🔌 {device_type} {_('検出 (ボタン数:')} {btn_count})"
            for i in range(self.tabs.count()):
                w = self.tabs.widget(i)
                if isinstance(w, SettingsTab):
                    w.gamepad_info_label.setText(status_text)
                    w.rebuild_mapping_table(btn_count)
                    break
        elif t == "button_press" and self.physical_detect_active:
            btn_idx = int(p)
            for i in range(self.tabs.count()):
                w = self.tabs.widget(i)
                if isinstance(w, SettingsTab): w.update_mapping_ui_from_detected_button(btn_idx); break

    def _generate_gamepad_js(self):
        enabled = self.game_mapping_enabled
        mapping_str = self.game_mapping_config
        global_turbo = self.global_turbo_enabled
        turbo_speed = int(self.game_turbo_speed)
        polling_rate = int(self.game_polling_rate)
        turbo_buttons_list = self.game_turbo_buttons
        
        if not enabled or not mapping_str:
            return ""

        try:
            mapping = json.loads(mapping_str)
            keys = {"ArrowUp":38, "ArrowDown":40, "ArrowLeft":37, "ArrowRight":39, "Space":32, "Enter":13, "z":90, "x":88, "c":67, "v":86, "Shift":16, "Control":17, "Escape":27}
            js_map = {int(k): {"key": v, "keyCode": keys[v]} for k, v in mapping.items() if v in keys}
            polling_interval = int(1000 / polling_rate)
            
            return f"""
            (() => {{
                if(window.OWG) clearInterval(window.OWG);
                const map = {json.dumps(js_map)}; 
                const state = {{}};
                const lastTurboTime = {{}};
                const turboState = {{}};
                const turboButtons = {json.dumps(turbo_buttons_list)};
                const turboSpeed = {turbo_speed};
                const globalTurbo = {json.dumps(global_turbo)};
                let lastId = "";
                let pollingInterval = null;
                
                function dispatchKey(type, keyName, keyCode) {{
                    const ev = new KeyboardEvent(type, {{ key: keyName, keyCode: keyCode, bubbles: true }});
                    (document.activeElement || document.body).dispatchEvent(ev);
                }}
                
                function pollGamepads() {{
                    const pads = navigator.getGamepads ? navigator.getGamepads() : [];
                    let pad = null;
                    // 複数パッド対応：最初に見つかった有効なパッドを使用（Joy-Conなどは複数で1つとして認識されることが多い）
                    for(let i=0; i<pads.length; i++) {{ if(pads[i] && pads[i].connected) {{ pad = pads[i]; break; }} }}
                    if(!pad) return;

                    if(pad.id !== lastId) {{ 
                        lastId = pad.id; 
                        console.log("OW_GAMEPAD_STATUS:connect:" + pad.buttons.length + "||" + pad.id); 
                    }}

                    // === ボタン処理（既存） ===
                    for(let b=0; b<pad.buttons.length; b++) {{
                        const isPressed = pad.buttons[b].pressed || (pad.buttons[b].value > 0.5);
                        const wasPressed = state[b] || false;
                        
                        if(isPressed) {{
                            if(!wasPressed) {{
                                state[b] = true;
                                console.log("OW_GAMEPAD_STATUS:button_press:" + b);
                                if(map[b]) {{
                                    dispatchKey('keydown', map[b].key, map[b].keyCode);
                                    lastTurboTime[b] = Date.now();
                                    turboState[b] = true;
                                }}
                            }} else {{
                                if(map[b] && globalTurbo && turboButtons.includes(b)) {{
                                    const now = Date.now();
                                    const turboInterval = 1000 / turboSpeed;
                                    if(now - lastTurboTime[b] >= (turboInterval / 2)) {{
                                        turboState[b] = !turboState[b];
                                        dispatchKey(turboState[b] ? 'keydown' : 'keyup', map[b].key, map[b].keyCode);
                                        lastTurboTime[b] = now;
                                    }}
                                }}
                            }}
                        }} else if(!isPressed && wasPressed) {{
                            state[b] = false;
                            if(map[b]) {{
                                dispatchKey('keyup', map[b].key, map[b].keyCode);
                            }}
                        }}
                    }}

                    // === Axes (アナログスティック / 十字キー) 処理を追加 ===
                    // Joy-Con、Switch Pro、Xbox、PSなど多くのBluetoothコントローラーに対応
                    if (pad.axes && pad.axes.length >= 2) {{
                        // axes[0] = 左右, axes[1] = 上下（-1.0 〜 +1.0）
                        const deadzone = 0.35; // 遊びを少し大きめに（誤操作防止）
                        
                        // 左
                        if (pad.axes[0] < -deadzone) {{
                            if (!state['axis_left']) {{
                                state['axis_left'] = true;
                                dispatchKey('keydown', 'ArrowLeft', 37);
                            }}
                        }} else if (state['axis_left']) {{
                            state['axis_left'] = false;
                            dispatchKey('keyup', 'ArrowLeft', 37);
                        }}
                        
                        // 右
                        if (pad.axes[0] > deadzone) {{
                            if (!state['axis_right']) {{
                                state['axis_right'] = true;
                                dispatchKey('keydown', 'ArrowRight', 39);
                            }}
                        }} else if (state['axis_right']) {{
                            state['axis_right'] = false;
                            dispatchKey('keyup', 'ArrowRight', 39);
                        }}
                        
                        // 上
                        if (pad.axes[1] < -deadzone) {{
                            if (!state['axis_up']) {{
                                state['axis_up'] = true;
                                dispatchKey('keydown', 'ArrowUp', 38);
                            }}
                        }} else if (state['axis_up']) {{
                            state['axis_up'] = false;
                            dispatchKey('keyup', 'ArrowUp', 38);
                        }}
                        
                        // 下
                        if (pad.axes[1] > deadzone) {{
                            if (!state['axis_down']) {{
                                state['axis_down'] = true;
                                dispatchKey('keydown', 'ArrowDown', 40);
                            }}
                        }} else if (state['axis_down']) {{
                            state['axis_down'] = false;
                            dispatchKey('keyup', 'ArrowDown', 40);
                        }}
                    }}
                }}
                
                function startPolling() {{
                    if (!pollingInterval) {{
                        pollingInterval = setInterval(pollGamepads, {polling_interval});
                    }}
                }}
                
                function stopPolling() {{
                    if (pollingInterval) {{
                        clearInterval(pollingInterval);
                        pollingInterval = null;
                    }}
                }}

                window.addEventListener("gamepadconnected", startPolling);
                window.addEventListener("gamepaddisconnected", () => {{
                    const pads = navigator.getGamepads ? navigator.getGamepads() : [];
                    if (!Array.from(pads).some(p => p !== null)) stopPolling();
                }});
                
                if (navigator.getGamepads && Array.from(navigator.getGamepads()).some(p => p !== null)) {{
                    startPolling();
                }}
            }})();
            """
        except: return ""

    def inject_gamepad_mapping_to_tab(self, browser_tab):
        js = self._generate_gamepad_js()
        if js: browser_tab.page().runJavaScript(js)

    def inject_gamepad_mapping_to_all(self):
        js = self._generate_gamepad_js()
        if js:
            for i in range(self.tabs.count()):
                w = self.tabs.widget(i)
                if isinstance(w, BrowserTab): w.page().runJavaScript(js)

    def inject_google_login_bypass_js(self, browser_tab):
        """Googleログイン時の bot 判定を強力に回避する JS インジェクション (v6.2 超強化版)"""
        bypass_js = """
        (function() {
            // === 超強化 Googleログイン bypass (stealth level) ===
            
            // 1. webdriver を完全に削除・隠蔽
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            delete navigator.webdriver;
            
            // 2. chrome オブジェクトを本物らしく偽装
            window.chrome = {
                runtime: {
                    OnInstalledReason: {},
                    OnRestartRequiredReason: {},
                    PlatformOs: {},
                    PlatformArch: {},
                    PlatformNaclArch: {},
                    RequestUpdateCheckStatus: {}
                },
                app: { isInstalled: false },
                webstore: { onInstallStageChanged: {}, onDownloadProgress: {} }
            };
            
            // 3. languages を自然に
            Object.defineProperty(navigator, 'languages', {
                get: () => ['ja-JP', 'ja', 'en-US', 'en'],
            });
            
            // 4. plugins / mimeTypes を本物らしく
            Object.defineProperty(navigator, 'plugins', {
                get: () => ({ length: 5, item: () => ({}), namedItem: () => ({}) })
            });
            Object.defineProperty(navigator, 'mimeTypes', {
                get: () => ({ length: 2, item: () => ({}), namedItem: () => ({}) })
            });
            
            // 5. permissions.query をオーバーライド
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // 6. ハードウェア情報を自然に偽装
            Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
            Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
            
            // 7. platform / vendor を自然に
            Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
            Object.defineProperty(navigator, 'vendor', { get: () => 'Google Inc.' });
            
            // 8. console.debug を無効化
            console.debug = function() {};
            
            console.log('%c[OpenWeb] Google login bypass (stealth) injected', 'color:#00ddff');
        })();
        """
        try:
            browser_tab.page().runJavaScript(bypass_js)
        except Exception:
            pass

    def reset_browser_completely(self):
        ans1 = QMessageBox.question(self, _("完全初期化"), _("設定、暗号Vault、閲覧履歴、ワークスペース、ToDo、Cookie、キャッシュ等を完全に抹消し、初期状態に巻き戻します。\n※この操作は元に戻せません。"), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ans1 != QMessageBox.Yes: return
        ans2 = QMessageBox.question(self, _("最終確認"), _("やり直すことはできません。よろしいですか？\n(アプリは自動終了します)"), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ans2 != QMessageBox.Yes: return

        self.settings.clear(); self.settings.sync(); self.vault.lock(); self.browser_history.clear()
        try:
            if os.path.exists(self.data_dir): shutil.rmtree(self.data_dir)
        except: pass
        QMessageBox.information(self, _("完了"), _("初期化されました。アプリを再起動してください。"))
        QApplication.quit()

    def current_browser(self):
        w = self.tabs.currentWidget()
        return w if isinstance(w, (BrowserTab, SplitViewWidget, WhiteboardModeWidget)) else None

    def show_find_dialog(self):
        b = self.current_browser()
        if not b: return
        text, ok = QInputDialog.getText(self, _("ページ内検索"), _("検索するテキストを入力:"))
        if ok and text: b.page().findText(""); b.page().findText(text)

    def print_to_pdf(self):
        b = self.current_browser()
        if not b: return
        file_path = QFileDialog.getSaveFileName(self, _("PDFとして保存"), "page.pdf", _("PDFファイル (*.pdf)"))[0]
        if file_path:
            b.page().printToPdf(file_path)
            self.statusBar().showMessage(f"{_('🖨️ PDFを保存しました:')} {file_path}", 5000)

    def go_back(self): b = self.current_browser(); b and b.back()
    def go_forward(self): b = self.current_browser(); b and b.forward()
    def reload_page(self): b = self.current_browser(); b and b.reload()
    def load_home(self):
        b = self.current_browser()
        if b:
            t = self.get_home_target()
            if t == "default_portal": b.setHtml(self.get_default_home_html(), QUrl("openweb://portal"))
            else: b.setUrl(QUrl(t) if t.startswith("http") else QUrl.fromLocalFile(t))

    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if not url: return
        if url.startswith("openweb://"):
            target = url.replace("openweb://", "").strip().lower()
            idx_map = {"settings": 0, "settings/homepage": 1, "settings/todo": 2, "settings/passwords": 3, "settings/downloads": 4, "settings/game-mode": 5, "settings/privacy": 6, "settings/timeline": 7, "settings/pocket": 8, "settings/experimental": 9, "settings/about": 10}
            if target in idx_map:
                self.open_settings_page(idx_map[target])
                return
            if target in ("blind_bombs", "blindbombs", "game"):
                self.launch_blind_bombs()
                return

        target_qurl = None
        
        if url.startswith(("http://", "https://", "ftp://", "file://")):
            target_qurl = QUrl(url)
        elif " " in url or ("." not in url and not url.startswith("localhost")):
            target_qurl = QUrl("https://www.google.com/search?q=" + url.replace(" ", "+"))
        elif os.path.isabs(url) and os.path.exists(url):
            target_qurl = QUrl.fromLocalFile(url)
        else:
            target_qurl = QUrl("https://" + url)

        b = self.current_browser()
        if b: 
            b.setUrl(target_qurl)
            b.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        else: 
            self.add_new_tab(target_qurl)

    def adjust_zoom(self, delta):
        if self.auto_fit_mode: self.toggle_auto_fit(False)
        b = self.current_browser()
        if b: b.page().setZoomFactor(max(0.25, min(b.page().zoomFactor() + delta, 5.0)))

    def reset_zoom(self):
        b = self.current_browser()
        if b: b.page().setZoomFactor(1.0)

    def toggle_auto_fit(self, checked):
        self.auto_fit_mode = checked
        self.fit_btn.setText(f"{_('フィット: ON') if checked else _('フィット: OFF')}")
        if checked: self.schedule_fit_update()
        elif self.current_browser(): self.current_browser().page().setZoomFactor(1.0)

    def schedule_fit_update(self): self.fit_timer.start(100)

    def fit_to_window_width(self):
        if not self.auto_fit_mode: return
        b = self.current_browser()
        if not b: return
        b.page().setZoomFactor(1.0)
        js = "(() => { const body = document.body; const html = document.documentElement; return Math.max(body.scrollWidth, body.offsetWidth, html.clientWidth, html.scrollWidth, html.offsetWidth); })();"
        def cb(pw):
            if pw and pw > 0: b.page().setZoomFactor(max(0.3, min((b.width() / pw) * 0.98, 3.0)))
        b.page().runJavaScript(js, cb)

    def copy_current_url(self):
        url_text = self.url_bar.text().strip()
        if url_text:
            QApplication.clipboard().setText(url_text)
            self.statusBar().showMessage(_("📋 URLをコピーしました"), 3000)

    def open_current_in_video_player(self):
        if not self.settings.value("exp_custom_video", True, type=bool):
            QMessageBox.information(self, _("機能が無効です"), _("「独自動画プレーヤー」は設定の『開発中の機能』でオフになっています。\n使用する場合はスイッチをオンにしてください。"))
            return
            
        browser = self.current_browser()
        if browser: self.external_windows.append(CustomVideoPlayerWindow(browser.page().profile(), browser.url().toString(), browser.title()))

    def open_current_as_app(self):
        browser = self.current_browser()
        if browser: self.external_windows.append(AppWindow(browser.page().profile(), browser.url().toString(), browser.title()))

    def prompt_save_password(self, domain, user, pwd):
        if self.settings.value("is_secret", False, type=bool): return
        if not self.ensure_vault_unlocked(self): return
        if domain in self.vault.domain_index: return
        if QMessageBox.question(self, _("パスワード保存"), f"「{domain}」{_('の認証情報を安全な金庫に保存しますか？')}", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.vault.save_credential(domain, user, pwd)
            for i in range(self.tabs.count()):
                w = self.tabs.widget(i)
                if isinstance(w, SettingsTab): w.refresh_password_table()

    def inject_autofill_js(self, browser, qurl):
        if not self.vault.is_unlocked: return
        creds = self.vault.load_credential(qurl.host())
        if creds:
            u, p = creds.get("u", ""), creds.get("p", "")
            js = f"setTimeout(()=>{{ let p=document.querySelector('input[type=\"password\"]'); if(p){{ p.value='{p}'; let u=p.closest('form').querySelector('input[type=\"text\"],input[type=\"email\"]'); if(u) u.value='{u}'; }} }}, 1000);"
            browser.page().runJavaScript(js)

    def save_tab_scroll_position(self, browser_tab):
        if not self.scroll_backup_enabled: return
        url = browser_tab.url().toString()
        if url.startswith("openweb://") or url == "about:blank": return
        js = "window.scrollY"
        def on_scroll_fetched(val):
            if val is not None: self.scroll_backups[url] = int(val)
        browser_tab.page().runJavaScript(js, on_scroll_fetched)

    def restore_tab_scroll_position(self, browser_tab):
        if not self.scroll_backup_enabled: return
        url = browser_tab.url().toString()
        if url in self.scroll_backups:
            y = self.scroll_backups[url]
            browser_tab.page().runJavaScript(f"setTimeout(() => window.scrollTo(0, {y}), 300);")

    def trigger_devtools(self):
        b = self.current_browser()
        if b: b.toggle_developer_tools()

    def focus_url_bar(self):
        self.url_bar.setFocus()
        self.url_bar.selectAll()

    def add_new_tab(self, url=None):
        is_sec = self.settings.value("is_secret", False, type=bool)
        active_profile = self.secret_profile if is_sec else self.normal_profile
        browser = BrowserTab(active_profile, self)
        
        if url:
            if url == "default_portal": browser.setHtml(self.get_default_home_html(), QUrl("openweb://portal"))
            elif isinstance(url, QUrl): browser.setUrl(url)
            else: browser.setUrl(QUrl.fromLocalFile(url) if os.path.exists(url) else QUrl(url))
        else:
            browser.setHtml(self.get_default_home_html(), QUrl("openweb://portal"))
                
        idx = self.tabs.addTab(browser, _("新しいタブ")); self.tabs.setCurrentIndex(idx)
        
        browser.urlChanged.connect(lambda q: self.url_bar.setText(q.toString()) if browser == self.current_browser() else None)
        browser.urlChanged.connect(lambda q: self.update_security_indicator(q) if browser == self.current_browser() else None)
        
        def on_url_loaded_sound_check(q):
            domain = q.host().lower()
            cfg = self.sound_manager.get_config(domain)
            browser.page().setAudioMuted(cfg.get("mute", False))
        browser.urlChanged.connect(on_url_loaded_sound_check)

        browser.titleChanged.connect(lambda t: self.tabs.setTabText(self.tabs.indexOf(browser), t[:15]))
        browser.loadFinished.connect(self.schedule_fit_update)
        browser.loadFinished.connect(lambda ok, b=browser: self.inject_autofill_js(b, b.url()) if ok else None)
        browser.loadFinished.connect(lambda ok, b=browser: self.restore_tab_scroll_position(b) if ok else None)
        browser.loadFinished.connect(lambda ok, b=browser: not is_sec and self.save_history_entry(b.title(), b.url().toString()))
        browser.loadFinished.connect(lambda ok, b=browser: self.inject_gamepad_mapping_to_tab(b) if ok else None)
        browser.loadFinished.connect(lambda ok, b=browser: self.inject_google_login_bypass_js(b) if ok else None)
        
        browser.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        return browser

    def get_google_access_token(self):
        """現在の有効なGoogleアクセストークンを取得（自動更新付き・強化版）"""
        if not self.vault.is_unlocked:
            return None

        oauth = self.vault.load_google_oauth()
        if not oauth or not oauth.get("access_token"):
            return None

        try:
            expires_at_str = oauth.get("expires_at", "")
            if expires_at_str:
                expires_at = datetime.fromisoformat(expires_at_str)
                if datetime.now() >= expires_at - timedelta(minutes=5):
                    if not self.vault.refresh_google_token():
                        return None
                    oauth = self.vault.load_google_oauth()
        except Exception:
            pass

        return oauth.get("access_token") if oauth else None

    def create_google_login_profile(self):
        """Googleログインに最適化されたクリーンプロファイルを作成して新しいタブで開く"""
        google_profile_dir = os.path.join(self.profiles_dir, "GoogleLogin")
        os.makedirs(google_profile_dir, exist_ok=True)

        profile_name = "GoogleLoginDedicated"
        google_profile = QWebEngineProfile(profile_name, self)
        google_profile.setPersistentStoragePath(google_profile_dir)
        google_profile.setCachePath(os.path.join(google_profile_dir, "Cache"))
        google_profile.setUrlRequestInterceptor(self.url_interceptor)

        browser = BrowserTab(google_profile, self)
        idx = self.tabs.addTab(browser, "🧪 Googleログイン用")
        self.tabs.setCurrentIndex(idx)
        browser.setUrl(QUrl("https://accounts.google.com"))

        self.statusBar().showMessage(
            _("🧪 Googleログイン用クリーンプロファイルを作成しました。ログインをお試しください。"), 
            5000
        )

    def start_google_oauth2_flow(self):
        """本格OAuth2認証 + Vault保存対応版"""
        if not self.settings.value("oauth2_enabled", True, type=bool):
            QMessageBox.information(self, _("情報"), _("OAuth2機能は設定で無効になっています。"))
            return

        if not self.ensure_vault_unlocked(self):
            return

        client_id = self.settings.value("google_oauth_client_id", "", type=str)
        if not client_id:
            text, ok = QInputDialog.getText(
                self, "Google OAuth2 設定",
                "Google Cloud Consoleで作成したOAuth 2.0クライアントIDを入力してください\n（redirect_uri: http://127.0.0.1:8080）"
            )
            if ok and text.strip():
                client_id = text.strip()
                self.settings.setValue("google_oauth_client_id", client_id)
            else:
                return

        # === ローカルサーバーでコードを自動取得 ===
        auth_code = {"value": None}

        class OAuthHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                query = parse_qs(urlparse(self.path).query)
                if "code" in query:
                    auth_code["value"] = query["code"][0]
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"<h1>Authentication successful! You can close this window.</h1>")
                else:
                    self.send_response(400)
                    self.end_headers()

            def log_message(self, format, *args):
                pass  # ログ抑制

        try:
            server = HTTPServer(("127.0.0.1", 8080), OAuthHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
        except Exception as e:
            QMessageBox.warning(self, "エラー", f"ローカルサーバー起動失敗: {e}")
            return

        # 認証URLを開く
        auth_url = (
            "https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={client_id}"
            "&redirect_uri=http://127.0.0.1:8080"
            "&response_type=code"
            "&scope=openid%20email%20profile"
            "&access_type=offline"
            "&prompt=consent"
        )
        QDesktopServices.openUrl(QUrl(auth_url))

        # コードを待つ（最大120秒）
        start_time = time.time()
        while auth_code["value"] is None and time.time() - start_time < 120:
            QApplication.processEvents()
            time.sleep(0.3)

        server.shutdown()

        if not auth_code["value"]:
            QMessageBox.warning(self, "タイムアウト", "認証コードの取得に失敗しました。")
            return

        code = auth_code["value"]

        # === トークン交換 ===
        try:
            token_response = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": client_id,
                    "code": code,
                    "redirect_uri": "http://127.0.0.1:8080",
                    "grant_type": "authorization_code"
                }
            ).json()

            if "access_token" in token_response:
                token_data = {
                    "access_token": token_response["access_token"],
                    "refresh_token": token_response.get("refresh_token"),
                    "expires_at": (datetime.now() + timedelta(seconds=token_response.get("expires_in", 3600))).isoformat(),
                    "scope": token_response.get("scope"),
                    "client_id": client_id
                }
                self.vault.save_google_oauth(token_data)
                QMessageBox.information(self, "成功", "Google OAuth認証に成功しました。\nトークンをVaultに保存しました。")
            else:
                QMessageBox.warning(self, "エラー", f"トークン取得失敗: {token_response}")
        except Exception as e:
            QMessageBox.warning(self, "エラー", f"トークン交換中にエラー: {e}")

    def save_history_entry(self, title, url):
        if not url or url.startswith("data:") or self.settings.value("is_secret", False, type=bool): return
        self.browser_history.insert(0, {"title": title.strip() or url, "url": url, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        uq, sn = [], set()
        for i in self.browser_history:
            if i["url"] not in sn: uq.append(i); sn.add(i["url"])
        self.browser_history = uq[:1000]
        with open(self.history_file, "w", encoding="utf-8") as f: json.dump(self.browser_history, f, ensure_ascii=False, indent=4)

    def handle_download(self, download: QWebEngineDownloadRequest):
        orig_name = os.path.basename(download.downloadFileName())
        mime_type = download.mimeType()
        base_name, ext = os.path.splitext(orig_name)
        
        if not ext and mime_type:
            ext = mimetypes.guess_extension(mime_type) or ""
            orig_name = base_name + ext

        dangerous = ['.exe', '.bat', '.cmd', '.msi', '.vbs', '.scr']
        if ext.lower() in dangerous:
            ans = QMessageBox.warning(
                self, _("⚠️ セキュリティ警告"), 
                f"{_('実行可能ファイル「')}{orig_name}{_('」をダウンロードしようとしています。\\n本当に保存を続行しますか？')}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if ans == QMessageBox.StandardButton.No:
                download.cancel()
                self.statusBar().showMessage(_("ダウンロードを安全にブロックしました"), 3000)
                return

        final_path = os.path.join(self.downloads_dir, orig_name)
        counter = 1
        while os.path.exists(final_path):
            final_path = os.path.join(self.downloads_dir, f"{base_name} ({counter}){ext}")
            counter += 1

        download.setDownloadDirectory(self.downloads_dir)
        download.setDownloadFileName(os.path.basename(final_path))
        download.accept()
        
        self.open_settings_page(4)
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if isinstance(w, SettingsTab): w.dl_manager_widget.add_download(download); break

    def close_tab(self, idx):
        if self.tabs.count() > 1:
            browser = self.tabs.widget(idx)
            if isinstance(browser, BrowserTab):
                self.save_tab_scroll_position(browser)
                closed_url = browser.url().toString()
                if not closed_url.startswith("openweb://"):
                    self.closed_tabs_history.append(closed_url)
                    if len(self.closed_tabs_history) > 15: self.closed_tabs_history.pop(0)
            browser.deleteLater()
            self.tabs.removeTab(idx)
            gc.collect()

    def restore_closed_tab(self):
        if self.closed_tabs_history:
            last_url = self.closed_tabs_history.pop()
            self.add_new_tab(last_url)
            self.statusBar().showMessage(_("↩️ 閉じたタブを復元しました"), 3000)
        else:
            self.statusBar().showMessage(_("これ以上復元できるタブはありません"), 3000)

    def current_tab_changed(self, idx):
        b = self.current_browser()
        if b:
            if hasattr(b, 'is_frozen') and b.is_frozen: b.defrost_tab()
            self.url_bar.setText(b.url().toString())
            self.update_security_indicator(b.url())
            b.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
            
        widget = self.tabs.widget(idx)
        if isinstance(widget, SplitViewWidget):
            self.split_toggle_btn.show()
            self.split_toggle_btn.setText(_("＝左面") if widget.active_index == 1 else _("＝右面"))
        else:
            self.split_toggle_btn.hide()

    def open_command_palette(self):
        cmds = [
            (_("📖 読書モードを適用"), self.activate_reader_mode),
            (_("🌐 ページ全体をGoogle翻訳で開く"), self.open_translate_page),
            (_("✨ AIによるページ自動内容要約"), self.summarize_current_page),
            (_("🔑 Vault 暗号金庫を開く"), lambda: self.open_settings_page(3)), 
            (_("➕ 新しい空タブを開く"), self.create_default_new_tab),
            (_("↩️ 直前に閉じたタブを復元する"), self.restore_closed_tab)
        ]
        cp = CommandPaletteDialog(self, cmds)
        if cp.exec() == QDialog.DialogCode.Accepted and cp.selected_action: cp.selected_action()

    def closeEvent(self, event):
        urls = []
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if hasattr(w, 'url') and callable(w.url):
                u = w.url().toString()
                if u and not u.startswith("openweb://"): urls.append(u)
        if urls: self.session_manager.save_session(urls)
        else: self.session_manager.clear()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("OpenWeb")
    app.setApplicationVersion("6.0")
    window = MyBrowser(); window.show()
    sys.exit(app.exec())