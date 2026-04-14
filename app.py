"""
AI-MA Streamlit 交互式控制台

grandMA3 离线语义编程助手的主界面。
"""

import hashlib
import html
import json
import os
import time
from urllib.parse import urlparse

import httpx
import streamlit as st
from streamlit.components.v1 import html as st_html
import sys
from pathlib import Path

# 添加 src 目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from osc.osc_client import GMA3Client, create_gma3_client
from ai.translator import CommandTranslator, create_translator
from config import settings
from utils.api_key_cache import get_cached_api_key, save_api_key, clear_all_api_keys
from utils.conversation_manager import (
    create_conversation, add_message,
    get_messages, clear_messages, delete_conversation,
    list_conversations
)

LANG_ZH = "zh"
LANG_EN = "en"
LANG_JA = "ja"

LANG_LABELS = {
    LANG_ZH: "中文",
    LANG_EN: "English",
    LANG_JA: "日本語",
}

I18N = {
    "app.page_title": {
        LANG_ZH: "AI-MA 灯光控制台",
        LANG_EN: "AI-MA Lighting Console",
        LANG_JA: "AI-MA ライティングコンソール",
    },
    "sidebar.title": {
        LANG_ZH: "AI-MA 控制台",
        LANG_EN: "AI-MA Console",
        LANG_JA: "AI-MA コンソール",
    },
    "sidebar.language": {
        LANG_ZH: "语言",
        LANG_EN: "Language",
        LANG_JA: "言語",
    },
    "conv.manager": {
        LANG_ZH: "💬 对话管理",
        LANG_EN: "💬 Conversations",
        LANG_JA: "💬 会話管理",
    },
    "conv.total": {
        LANG_ZH: "共 {n} 条会话",
        LANG_EN: "{n} sessions",
        LANG_JA: "{n} 件の会話",
    },
    "conv.new": {
        LANG_ZH: "➕ 新建对话",
        LANG_EN: "➕ New chat",
        LANG_JA: "➕ 新しい会話",
    },
    "conv.history": {
        LANG_ZH: "历史会话",
        LANG_EN: "History",
        LANG_JA: "履歴",
    },
    "conv.unnamed": {
        LANG_ZH: "未命名",
        LANG_EN: "Untitled",
        LANG_JA: "無題",
    },
    "conv.switch": {
        LANG_ZH: "切换会话",
        LANG_EN: "Switch",
        LANG_JA: "切り替え",
    },
    "conv.delete": {
        LANG_ZH: "删除会话",
        LANG_EN: "Delete",
        LANG_JA: "削除",
    },
    "conv.none": {
        LANG_ZH: "暂无对话记录",
        LANG_EN: "No conversations yet",
        LANG_JA: "会話がありません",
    },
    "conv.clear_messages": {
        LANG_ZH: "🧹 清空当前会话消息",
        LANG_EN: "🧹 Clear current messages",
        LANG_JA: "🧹 現在の会話をクリア",
    },
    "history.commands": {
        LANG_ZH: "📜 历史指令",
        LANG_EN: "📜 Command history",
        LANG_JA: "📜 コマンド履歴",
    },
    "history.command_n": {
        LANG_ZH: "指令 {n}",
        LANG_EN: "Command {n}",
        LANG_JA: "コマンド {n}",
    },
    "history.ai_parse": {
        LANG_ZH: "AI 解析结果:",
        LANG_EN: "AI parse result:",
        LANG_JA: "AI 解析結果:",
    },
    "history.osc_cmds": {
        LANG_ZH: "OSC 命令:",
        LANG_EN: "OSC commands:",
        LANG_JA: "OSC コマンド:",
    },
    "history.no_osc_cmds": {
        LANG_ZH: "无 OSC 命令记录",
        LANG_EN: "No OSC commands",
        LANG_JA: "OSC コマンドがありません",
    },
    "history.exec_result": {
        LANG_ZH: "执行结果:",
        LANG_EN: "Result:",
        LANG_JA: "実行結果:",
    },
    "history.error": {
        LANG_ZH: "错误：{msg}",
        LANG_EN: "Error: {msg}",
        LANG_JA: "エラー：{msg}",
    },
    "osc.settings": {
        LANG_ZH: "🔌 OSC 设置",
        LANG_EN: "🔌 OSC settings",
        LANG_JA: "🔌 OSC 設定",
    },
    "osc.ip": {
        LANG_ZH: "IP 地址",
        LANG_EN: "IP address",
        LANG_JA: "IP アドレス",
    },
    "osc.ip_help": {
        LANG_ZH: "grandMA3 的 IP 地址或 localhost",
        LANG_EN: "grandMA3 IP address or localhost",
        LANG_JA: "grandMA3 の IP アドレス、または localhost",
    },
    "osc.port": {
        LANG_ZH: "端口",
        LANG_EN: "Port",
        LANG_JA: "ポート",
    },
    "osc.port_help": {
        LANG_ZH: "OSC 端口号，默认 8000",
        LANG_EN: "OSC port (default 8000)",
        LANG_JA: "OSC ポート（既定 8000）",
    },
    "osc.config_updated": {
        LANG_ZH: "✅ 配置已更新：{host}:{port}",
        LANG_EN: "✅ Updated: {host}:{port}",
        LANG_JA: "✅ 更新しました：{host}:{port}",
    },
    "osc.current": {
        LANG_ZH: "当前连接：",
        LANG_EN: "Current:",
        LANG_JA: "現在：",
    },
    "osc.reconnect": {
        LANG_ZH: "🔄 重新连接",
        LANG_EN: "🔄 Reconnect",
        LANG_JA: "🔄 再接続",
    },
    "api.settings": {
        LANG_ZH: "🤖 API 设置",
        LANG_EN: "🤖 API settings",
        LANG_JA: "🤖 API 設定",
    },
    "api.key": {
        LANG_ZH: "API 密钥",
        LANG_EN: "API key",
        LANG_JA: "API キー",
    },
    "api.key_help": {
        LANG_ZH: "OpenAI 兼容 API 密钥（自动保存）",
        LANG_EN: "OpenAI-compatible API key (auto-saved)",
        LANG_JA: "OpenAI 互換 API キー（自動保存）",
    },
    "api.url": {
        LANG_ZH: "API 地址",
        LANG_EN: "API base URL",
        LANG_JA: "API URL",
    },
    "api.url_cached": {
        LANG_ZH: "已缓存",
        LANG_EN: "cached",
        LANG_JA: "保存済み",
    },
    "api.url_not_set": {
        LANG_ZH: "未设置",
        LANG_EN: "not set",
        LANG_JA: "未設定",
    },
    "api.edit": {
        LANG_ZH: "编辑",
        LANG_EN: "Edit",
        LANG_JA: "編集",
    },
    "api.done": {
        LANG_ZH: "完成",
        LANG_EN: "Done",
        LANG_JA: "完了",
    },
    "api.url_help": {
        LANG_ZH: "API 基础 URL（自动保存）",
        LANG_EN: "API base URL (auto-saved)",
        LANG_JA: "API ベースURL（自動保存）",
    },
    "api.select_model": {
        LANG_ZH: "选择模型",
        LANG_EN: "Model",
        LANG_JA: "モデル",
    },
    "api.choose_help": {
        LANG_ZH: "选择预设模型或自定义",
        LANG_EN: "Select preset or custom model",
        LANG_JA: "プリセットまたはカスタムを選択",
    },
    "api.custom_model": {
        LANG_ZH: "自定义模型 ID",
        LANG_EN: "Custom model ID",
        LANG_JA: "カスタムモデル ID",
    },
    "api.custom_model_ph": {
        LANG_ZH: "输入模型 ID",
        LANG_EN: "Enter model ID",
        LANG_JA: "モデル ID を入力",
    },
    "api.config_updated": {
        LANG_ZH: "✅ API 配置已更新",
        LANG_EN: "✅ API settings updated",
        LANG_JA: "✅ API 設定を更新しました",
    },
    "api.current_model": {
        LANG_ZH: "当前模型：",
        LANG_EN: "Model:",
        LANG_JA: "モデル：",
    },
    "api.status": {
        LANG_ZH: "API 状态：",
        LANG_EN: "API:",
        LANG_JA: "API：",
    },
    "api.configured": {
        LANG_ZH: "已配置",
        LANG_EN: "configured",
        LANG_JA: "設定済み",
    },
    "api.not_configured": {
        LANG_ZH: "未配置",
        LANG_EN: "not configured",
        LANG_JA: "未設定",
    },
    "api.network_mode": {
        LANG_ZH: "网络方式（影响 API 调用）",
        LANG_EN: "Network mode (affects API calls)",
        LANG_JA: "ネットワーク方式（API に影響）",
    },
    "api.net.direct": {
        LANG_ZH: "直连（不使用任何代理）",
        LANG_EN: "Direct (no proxy)",
        LANG_JA: "直接（プロキシなし）",
    },
    "api.net.env": {
        LANG_ZH: "使用系统代理（HTTP_PROXY/HTTPS_PROXY/ALL_PROXY）",
        LANG_EN: "Use system proxy (HTTP_PROXY/HTTPS_PROXY/ALL_PROXY)",
        LANG_JA: "システムプロキシを使用（HTTP_PROXY/HTTPS_PROXY/ALL_PROXY）",
    },
    "api.net.env_socks": {
        LANG_ZH: "使用环境 SOCKS5 代理（{val}）",
        LANG_EN: "Use env SOCKS5 proxy ({val})",
        LANG_JA: "環境 SOCKS5 プロキシを使用（{val}）",
    },
    "api.net.none_detected": {
        LANG_ZH: "未检测到",
        LANG_EN: "not detected",
        LANG_JA: "未検出",
    },
    "api.net.custom": {
        LANG_ZH: "自定义代理（http(s):// 或 socks5://）",
        LANG_EN: "Custom proxy (http(s):// or socks5://)",
        LANG_JA: "カスタムプロキシ（http(s):// または socks5://）",
    },
    "api.net.custom_addr": {
        LANG_ZH: "自定义代理地址",
        LANG_EN: "Custom proxy URL",
        LANG_JA: "カスタムプロキシURL",
    },
    "api.net.custom_ph": {
        LANG_ZH: "例如 http://127.0.0.1:57645 或 socks5://127.0.0.1:57644",
        LANG_EN: "e.g. http://127.0.0.1:57645 or socks5://127.0.0.1:57644",
        LANG_JA: "例: http://127.0.0.1:57645 または socks5://127.0.0.1:57644",
    },
    "api.check": {
        LANG_ZH: "✅ 验证 API 可用性",
        LANG_EN: "✅ Check API availability",
        LANG_JA: "✅ API の疎通確認",
    },
    "api.checking": {
        LANG_ZH: "正在验证 API...",
        LANG_EN: "Checking API...",
        LANG_JA: "API を確認中...",
    },
    "api.clear_cached": {
        LANG_ZH: "🗑️ 清除缓存的 API 密钥",
        LANG_EN: "🗑️ Clear cached API keys",
        LANG_JA: "🗑️ キャッシュしたAPIキーを削除",
    },
    "api.check.result": {
        LANG_ZH: "API 验证结果",
        LANG_EN: "API check result",
        LANG_JA: "API 確認結果",
    },
    "api.check.details": {
        LANG_ZH: "显示诊断详情",
        LANG_EN: "Show details",
        LANG_JA: "詳細を表示",
    },
    "automation.title": {
        LANG_ZH: "### ⚙️ 自动化",
        LANG_EN: "### ⚙️ Automation",
        LANG_JA: "### ⚙️ 自動化",
    },
    "automation.auto_connect": {
        LANG_ZH: "开启自动连接 MA",
        LANG_EN: "Auto-connect MA",
        LANG_JA: "MA を自動接続",
    },
    "automation.auto_connect_help": {
        LANG_ZH: "打开后会在需要时自动连接 grandMA3",
        LANG_EN: "Automatically connect to grandMA3 when needed",
        LANG_JA: "必要時に grandMA3 へ自動接続",
    },
    "automation.auto_send": {
        LANG_ZH: "开启自动发送指令",
        LANG_EN: "Auto-send commands",
        LANG_JA: "コマンド自動送信",
    },
    "automation.auto_send_help": {
        LANG_ZH: "打开后解析成功会直接发送，不再手动确认",
        LANG_EN: "Send immediately after a successful parse (no manual confirm)",
        LANG_JA: "解析成功後に自動送信（手動確認なし）",
    },
    "automation.collapse_ai": {
        LANG_ZH: "折叠 AI 结果详情",
        LANG_EN: "Collapse AI details",
        LANG_JA: "AI 詳細を折りたたむ",
    },
    "automation.collapse_ai_help": {
        LANG_ZH: "开启后，包含 JSON/代码块的 AI 消息会默认折叠",
        LANG_EN: "Collapse AI messages that contain JSON/code blocks",
        LANG_JA: "JSON/コードブロックを含む AI メッセージを折りたたむ",
    },
    "help.title": {
        LANG_ZH: "### 📖 使用说明",
        LANG_EN: "### 📖 Guide",
        LANG_JA: "### 📖 使い方",
    },
    "help.body": {
        LANG_ZH: '1. 输入自然语言指令（如："把 101 号灯调成红色"）\n2. AI 自动解析并显示 JSON\n3. 点击"确认下发"发送 OSC 命令\n4. 查看执行结果',
        LANG_EN: '1. Enter a natural-language command (e.g. "Set fixture 101 to red")\n2. AI parses and shows JSON\n3. Click confirm to send OSC commands\n4. View the result',
        LANG_JA: '1. 自然言語コマンドを入力（例：「101番を赤に」）\n2. AI が解析して JSON を表示\n3. 確認して OSC を送信\n4. 実行結果を確認',
    },
    "help.examples_title": {
        LANG_ZH: "### 💡 示例指令",
        LANG_EN: "### 💡 Examples",
        LANG_JA: "### 💡 例",
    },
    "help.examples_body": {
        LANG_ZH: '- "把 101 到 105 号灯调成红色"\n- "把 1 号灯亮度调到 50%"\n- "来个忧郁的蓝色"\n- "把 3 号灯设为紫色"',
        LANG_EN: '- "Set fixtures 101-105 to red"\n- "Set fixture 1 brightness to 50%"\n- "Give me a sad blue"\n- "Set fixture 3 to purple"',
        LANG_JA: '- 「101〜105番を赤に」\n- 「1番の明るさを50%に」\n- 「憂鬱な青にして」\n- 「3番を紫に」',
    },
    "status.connected": {
        LANG_ZH: "已连接",
        LANG_EN: "Connected",
        LANG_JA: "接続済み",
    },
    "status.disconnected": {
        LANG_ZH: "未连接",
        LANG_EN: "Disconnected",
        LANG_JA: "未接続",
    },
    "chat.empty": {
        LANG_ZH: "暂无对话记录，开始对话吧！",
        LANG_EN: "No messages yet. Start chatting!",
        LANG_JA: "メッセージがありません。会話を始めましょう！",
    },
    "chat.user": {
        LANG_ZH: "👤 你 · {ts}",
        LANG_EN: "👤 You · {ts}",
        LANG_JA: "👤 あなた · {ts}",
    },
    "chat.ai": {
        LANG_ZH: "🤖 AI · {ts}",
        LANG_EN: "🤖 AI · {ts}",
        LANG_JA: "🤖 AI · {ts}",
    },
    "chat.view_ai_details": {
        LANG_ZH: "查看 AI 详情：{preview}",
        LANG_EN: "View AI details: {preview}",
        LANG_JA: "AI 詳細を見る：{preview}",
    },
    "composer.placeholder": {
        LANG_ZH: "例如：把 101 到 105 号灯调成红色，亮度 50%",
        LANG_EN: "e.g. Set fixtures 101-105 to red, brightness 50%",
        LANG_JA: "例：101〜105番を赤に、明るさ50%",
    },
    "composer.send": {
        LANG_ZH: "发送",
        LANG_EN: "Send",
        LANG_JA: "送信",
    },
    "spinner.parsing": {
        LANG_ZH: "🤖 AI 正在解析指令...",
        LANG_EN: "🤖 AI is parsing...",
        LANG_JA: "🤖 AI が解析中...",
    },
    "err.translator_not_init": {
        LANG_ZH: "❌ 翻译器未初始化，请重新连接",
        LANG_EN: "❌ Translator not initialized. Please reconnect.",
        LANG_JA: "❌ トランスレーターが未初期化です。再接続してください。",
    },
    "err.parse_failed": {
        LANG_ZH: "❌ 解析失败：{msg}",
        LANG_EN: "❌ Parse failed: {msg}",
        LANG_JA: "❌ 解析に失敗：{msg}",
    },
    "ok.parse_success": {
        LANG_ZH: "✅ 解析成功：{msg}",
        LANG_EN: "✅ Parsed: {msg}",
        LANG_JA: "✅ 解析成功：{msg}",
    },
    "pending.generated": {
        LANG_ZH: "已生成待发送命令，点击下方可查看完整解析与命令详情。",
        LANG_EN: "Commands generated. Expand below to view details.",
        LANG_JA: "送信待ちコマンドを生成しました。下で詳細を確認できます。",
    },
    "pending.preview": {
        LANG_ZH: "预览：",
        LANG_EN: "Preview:",
        LANG_JA: "プレビュー：",
    },
    "pending.more": {
        LANG_ZH: "+{n} 条",
        LANG_EN: "+{n} more",
        LANG_JA: "+{n} 件",
    },
    "pending.view_details": {
        LANG_ZH: "查看待发送详情",
        LANG_EN: "View pending details",
        LANG_JA: "送信待ち詳細を見る",
    },
    "pending.parsed_json": {
        LANG_ZH: "解析 JSON",
        LANG_EN: "Parsed JSON",
        LANG_JA: "解析 JSON",
    },
    "pending.osc_to_send": {
        LANG_ZH: "即将发送的 OSC 命令",
        LANG_EN: "OSC commands to send",
        LANG_JA: "送信する OSC コマンド",
    },
    "pending.already_auto_sent": {
        LANG_ZH: "该待发送指令已自动发送过，等待下一条新指令。",
        LANG_EN: "This pending command was already auto-sent. Waiting for a new one.",
        LANG_JA: "このコマンドは既に自動送信済みです。次を待っています。",
    },
    "pending.auto_sending": {
        LANG_ZH: "📡 自动发送中...",
        LANG_EN: "📡 Auto-sending...",
        LANG_JA: "📡 自動送信中...",
    },
    "pending.sending": {
        LANG_ZH: "📡 正在发送 OSC 命令...",
        LANG_EN: "📡 Sending OSC commands...",
        LANG_JA: "📡 OSC コマンド送信中...",
    },
    "pending.confirm_send": {
        LANG_ZH: "✅ 确认并发送",
        LANG_EN: "✅ Confirm & Send",
        LANG_JA: "✅ 確認して送信",
    },
    "pending.clear": {
        LANG_ZH: "🗑 清除",
        LANG_EN: "🗑 Clear",
        LANG_JA: "🗑 クリア",
    },
    "pending.cancelled": {
        LANG_ZH: "已取消待发送命令",
        LANG_EN: "Pending command cleared",
        LANG_JA: "送信待ちをキャンセルしました",
    },
    "pending.ai_wait_confirm": {
        LANG_ZH: "🤖 AI · 待确认",
        LANG_EN: "🤖 AI · Pending",
        LANG_JA: "🤖 AI · 確認待ち",
    },
    "send.ok": {
        LANG_ZH: "✅ 已发送：{msg}",
        LANG_EN: "✅ Sent: {msg}",
        LANG_JA: "✅ 送信しました：{msg}",
    },
    "send.fail": {
        LANG_ZH: "❌ 发送失败：{msg}",
        LANG_EN: "❌ Send failed: {msg}",
        LANG_JA: "❌ 送信失敗：{msg}",
    },
    "send.auto_ok": {
        LANG_ZH: "✅ 已自动发送：{msg}",
        LANG_EN: "✅ Auto-sent: {msg}",
        LANG_JA: "✅ 自動送信しました：{msg}",
    },
    "send.auto_fail": {
        LANG_ZH: "❌ 自动发送失败：{msg}",
        LANG_EN: "❌ Auto-send failed: {msg}",
        LANG_JA: "❌ 自動送信失敗：{msg}",
    },
    "send.exec_ok": {
        LANG_ZH: "✅ 执行成功：{msg}",
        LANG_EN: "✅ Success: {msg}",
        LANG_JA: "✅ 成功：{msg}",
    },
    "send.exec_fail": {
        LANG_ZH: "❌ 执行失败：{msg}",
        LANG_EN: "❌ Failed: {msg}",
        LANG_JA: "❌ 失敗：{msg}",
    },
    "send.osc_client_not_init": {
        LANG_ZH: "OSC 客户端未初始化",
        LANG_EN: "OSC client not initialized",
        LANG_JA: "OSC クライアントが未初期化です",
    },
    "api_check.no_key": {
        LANG_ZH: "未填写 API 密钥",
        LANG_EN: "API key is empty",
        LANG_JA: "API キーが未入力です",
    },
    "api_check.no_url": {
        LANG_ZH: "未填写 API 地址",
        LANG_EN: "API URL is empty",
        LANG_JA: "API URL が未入力です",
    },
    "api_check.bad_url": {
        LANG_ZH: "API 地址格式不正确",
        LANG_EN: "Invalid API URL format",
        LANG_JA: "API URL の形式が正しくありません",
    },
    "api_check.parse_fail": {
        LANG_ZH: "API 地址解析失败",
        LANG_EN: "Failed to parse API URL",
        LANG_JA: "API URL の解析に失敗しました",
    },
    "api_check.ok": {
        LANG_ZH: "API 可用（请求成功）",
        LANG_EN: "API OK (request succeeded)",
        LANG_JA: "API OK（リクエスト成功）",
    },
    "api_check.auth_fail": {
        LANG_ZH: "鉴权失败（API Key 无效/未生效/权限不足）",
        LANG_EN: "Auth failed (invalid key / no permission)",
        LANG_JA: "認証失敗（キー無効/権限不足）",
    },
    "api_check.not_found": {
        LANG_ZH: "接口路径不存在（API 地址可能需要包含正确版本或路径）",
        LANG_EN: "Endpoint not found (check base URL/path)",
        LANG_JA: "エンドポイントが見つかりません（URL/パス確認）",
    },
    "api_check.rate_limited": {
        LANG_ZH: "请求被限流（429）",
        LANG_EN: "Rate limited (429)",
        LANG_JA: "レート制限（429）",
    },
    "api_check.http_fail": {
        LANG_ZH: "请求失败（HTTP {code}）",
        LANG_EN: "Request failed (HTTP {code})",
        LANG_JA: "失敗（HTTP {code}）",
    },
    "api_check.proxy_error": {
        LANG_ZH: "代理错误（ProxyError）",
        LANG_EN: "Proxy error (ProxyError)",
        LANG_JA: "プロキシエラー（ProxyError）",
    },
    "api_check.connect_error": {
        LANG_ZH: "连接失败（网络/代理/DNS/TLS）",
        LANG_EN: "Connection failed (network/proxy/DNS/TLS)",
        LANG_JA: "接続失敗（ネットワーク/プロキシ/DNS/TLS）",
    },
    "api_check.timeout": {
        LANG_ZH: "请求超时（ReadTimeout）",
        LANG_EN: "Timeout (ReadTimeout)",
        LANG_JA: "タイムアウト（ReadTimeout）",
    },
    "api_check.exception": {
        LANG_ZH: "验证异常",
        LANG_EN: "Check error",
        LANG_JA: "確認エラー",
    },
}


def get_ui_lang() -> str:
    lang = st.session_state.get("ui_lang") or get_cached_api_key("ui_lang") or LANG_ZH
    return lang if lang in LANG_LABELS else LANG_ZH


def t(key: str, **kwargs) -> str:
    lang = get_ui_lang()
    entry = I18N.get(key)
    if not entry:
        return key.format(**kwargs) if kwargs else key
    text = entry.get(lang) or entry.get(LANG_ZH) or next(iter(entry.values()))
    try:
        return text.format(**kwargs) if kwargs else text
    except Exception:
        return text


def _build_chat_completions_endpoint(base_url: str) -> str:
    """
    将用户输入的 base_url 规范为可用的 /chat/completions endpoint。
    兼容两种输入：
    - https://host/v2
    - https://host/v2/chat/completions
    """
    base_url = (base_url or "").strip()
    if not base_url:
        return ""
    if base_url.endswith("/chat/completions"):
        return base_url
    return base_url.rstrip("/") + "/chat/completions"


def check_api_availability(api_key: str, base_url: str, model_id: str, trust_env: bool = True) -> dict:
    """
    API 可用性验证（OpenAI 兼容 Chat Completions）。
    目标：给用户明确诊断，而不是只看到 Connection error。
    """
    api_key = (api_key or "").strip()
    base_url = (base_url or "").strip()
    model_id = (model_id or "").strip()

    endpoint = _build_chat_completions_endpoint(base_url)
    result = {
        "ok": False,
        "endpoint": endpoint,
        "base_url": base_url,
        "model_id": model_id,
        "proxy_mode": None,
        "proxy_url": None,
        "status_code": None,
        "latency_ms": None,
        "message": "",
        "detail": "",
    }

    if not api_key:
        result["message"] = t("api_check.no_key")
        return result
    if not endpoint:
        result["message"] = t("api_check.no_url")
        return result
    try:
        parsed = urlparse(endpoint)
        if not parsed.scheme or not parsed.netloc:
            result["message"] = t("api_check.bad_url")
            result["detail"] = f"endpoint={endpoint!r}"
            return result
    except Exception as e:
        result["message"] = t("api_check.parse_fail")
        result["detail"] = str(e)
        return result

    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": model_id or "gpt-4",
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 1,
        "temperature": 0,
    }

    t0 = time.time()
    try:
        proxy_mode = st.session_state.get("api_proxy_mode", "env")
        proxy_url = (st.session_state.get("api_custom_proxy_url") or "").strip() or None

        client_kwargs = dict(
            timeout=httpx.Timeout(20.0, connect=8.0),
            follow_redirects=True,
        )

        if proxy_mode == "direct":
            client_kwargs["trust_env"] = False
            client_kwargs["proxies"] = None
        elif proxy_mode == "env_socks":
            # 从环境变量读取 SOCKS5 代理（你这台机器里通常有 SOCKS5_PROXY / SOCKS_PROXY）
            env_proxy = (
                os.environ.get("SOCKS5_PROXY")
                or os.environ.get("socks5_proxy")
                or os.environ.get("SOCKS_PROXY")
                or os.environ.get("socks_proxy")
            )
            env_proxy = (env_proxy or "").strip() or None
            client_kwargs["trust_env"] = False
            client_kwargs["proxies"] = env_proxy
            proxy_url = env_proxy
        elif proxy_mode == "custom":
            # 自定义代理（支持 http(s):// 或 socks5:// / socks5h://）
            p = proxy_url
            client_kwargs["trust_env"] = False
            client_kwargs["proxies"] = p
            proxy_url = p
        else:
            # env：使用系统代理（HTTP_PROXY/HTTPS_PROXY/ALL_PROXY）
            client_kwargs["trust_env"] = bool(trust_env)

        result["proxy_mode"] = proxy_mode
        result["proxy_url"] = proxy_url

        with httpx.Client(
            **client_kwargs,
        ) as client:
            resp = client.post(endpoint, headers=headers, json=payload)
        result["latency_ms"] = int((time.time() - t0) * 1000)
        result["status_code"] = resp.status_code

        # 200：可用
        if 200 <= resp.status_code < 300:
            result["ok"] = True
            result["message"] = t("api_check.ok")
            return result

        # 401/403：鉴权失败（通常是 key/鉴权方式问题）
        if resp.status_code in (401, 403):
            result["message"] = t("api_check.auth_fail")
        # 404：路径不对（base_url 填错常见）
        elif resp.status_code == 404:
            result["message"] = t("api_check.not_found")
        # 429：限流
        elif resp.status_code == 429:
            result["message"] = t("api_check.rate_limited")
        else:
            result["message"] = t("api_check.http_fail", code=resp.status_code)

        body = (resp.text or "").strip()
        result["detail"] = body[:500]
        return result

    except httpx.ProxyError as e:
        result["latency_ms"] = int((time.time() - t0) * 1000)
        result["message"] = t("api_check.proxy_error")
        result["detail"] = str(e)
        return result
    except httpx.ConnectError as e:
        result["latency_ms"] = int((time.time() - t0) * 1000)
        result["message"] = t("api_check.connect_error")
        result["detail"] = str(e)
        return result
    except httpx.ReadTimeout:
        result["latency_ms"] = int((time.time() - t0) * 1000)
        result["message"] = t("api_check.timeout")
        return result
    except Exception as e:
        result["latency_ms"] = int((time.time() - t0) * 1000)
        result["message"] = t("api_check.exception")
        result["detail"] = f"{type(e).__name__}: {e}"
        return result


# 页面配置
st.set_page_config(
    page_title=t("app.page_title"),
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS（深色专业主题）
st.markdown("""
    <style>
    :root {
        --bg-main: #111318;
        --bg-card: #1a1e25;
        --bg-soft: #212733;
        --border: #303847;
        --text-main: #e5e7eb;
        --text-soft: #a5adbb;
        --accent: #1f6feb;
        --brand: #d97706;
        --danger: #ef4444;
        --ok: #22c55e;
        color-scheme: dark;
    }

    /* 永久暗黑：即使系统偏好浅色，也强制 dark 的渲染策略 */
    @media (prefers-color-scheme: light) {
        :root { color-scheme: dark; }
        html, body, .stApp, [data-testid="stAppViewContainer"] {
            background: #0f1115 !important;
            color: var(--text-main) !important;
        }
    }
    html, body {
        background: #0f1115 !important;
        color: var(--text-main) !important;
    }
    .stApp {
        background: #0f1115 !important;
    }
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #0f1115 0%, #131720 100%);
        color: var(--text-main);
    }
    footer {visibility: hidden !important; height: 0 !important;}
    .block-container {
        max-width: 1400px;
        padding-top: 1.1rem;
        padding-bottom: 8rem;
    }
    section.main .block-container {
        padding-top: 2.8rem !important;
    }
    [data-testid="stSidebar"] {
        background: #0f1218;
        border-right: 1px solid #262d3b;
    }
    [data-testid="stSidebarUserContent"] {
        padding-top: 0.2rem !important;
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 0.2rem !important;
    }
    [data-testid="stSidebar"] h1 {
        margin-top: 0.2rem !important;
        padding-top: 0.2rem !important;
        line-height: 1.2 !important;
        text-align: center !important;
        width: 100% !important;
        min-height: 54px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin-bottom: 0.2rem !important;
    }
    [data-testid="stSidebar"] .stButton button,
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stNumberInput input,
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
        border-radius: 10px !important;
    }
    /* 主区表单控件在 Safari 下强制深色 */
    section.main .stTextInput input,
    section.main .stNumberInput input,
    section.main textarea,
    section.main [data-baseweb="select"] > div {
        background: rgba(26, 30, 37, 0.92) !important;
        color: var(--text-main) !important;
        border-color: #2a3342 !important;
    }
    section.main input::placeholder,
    section.main textarea::placeholder {
        color: rgba(165, 173, 187, 0.75) !important;
    }
    /* Safari/Chrome autofill 修正 */
    input:-webkit-autofill,
    textarea:-webkit-autofill,
    select:-webkit-autofill {
        -webkit-text-fill-color: var(--text-main) !important;
        transition: background-color 99999s ease-in-out 0s;
        box-shadow: 0 0 0px 1000px rgba(26, 30, 37, 0.92) inset !important;
        border: 1px solid #2a3342 !important;
    }
    .panel-card {
        background: rgba(26, 30, 37, 0.92);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.9rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .panel-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #cbd5e1;
        letter-spacing: 0.3px;
        margin: 0;
        text-align: center;
    }
    .status-row {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        font-weight: 600;
        margin-bottom: 0.15rem;
        font-size: 0.88rem;
    }
    .status-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
    }
    .status-dot.connected {
        background: var(--ok);
        box-shadow: 0 0 0 rgba(34,197,94,0.8);
        animation: breathe 1.8s infinite;
    }
    .status-dot.disconnected {
        background: var(--danger);
        box-shadow: 0 0 0 rgba(239,68,68,0.6);
    }
    @keyframes breathe {
        0% { box-shadow: 0 0 0 0 rgba(34,197,94,0.7); }
        70% { box-shadow: 0 0 0 10px rgba(34,197,94,0); }
        100% { box-shadow: 0 0 0 0 rgba(34,197,94,0); }
    }
    .dryrun-card {
        background: #10141b;
        border: 1px solid #2a3342;
        border-radius: 12px;
        padding: 0.65rem;
    }
    .stButton button {
        border-radius: 10px !important;
    }
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #d97706, #b45309) !important;
        border: 1px solid #ea580c !important;
        color: #fff !important;
    }
    .stChatMessage {
        background: rgba(26, 30, 37, 0.88);
        border: 1px solid #2e3747;
        border-radius: 12px;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
    }
    .chat-shell {
        width: 100%;
        max-width: 1280px;
        margin: 0 auto;
        padding: 0 2px;
    }
    .chat-row-left,
    .chat-row-right {
        display: flex;
        width: 100%;
        margin-bottom: 0.2rem;
    }
    .chat-row-left {
        justify-content: flex-start;
    }
    .chat-row-right {
        justify-content: flex-end;
    }
    .msg-bubble {
        border-radius: 12px;
        border: 1px solid #2f394a;
        padding: 0.6rem 0.8rem;
        margin-bottom: 0.5rem;
        line-height: 1.45;
        font-size: 0.95rem;
        display: inline-block;
        width: fit-content;
        max-width: min(78%, 900px);
        word-break: break-word;
    }
    .msg-bubble.assistant {
        background: rgba(27, 34, 46, 0.9);
    }
    .msg-bubble.user {
        background: rgba(24, 62, 112, 0.55);
        border-color: #2d6db7;
        margin-left: auto;
    }
    .user-msg-wrap {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        margin-bottom: 0.35rem;
    }
    .user-msg-time {
        font-size: 0.9rem;
        color: #8ea0b5;
        margin-bottom: 0.2rem;
    }
    section.main [data-testid="stExpander"] {
        display: inline-block !important;
        width: fit-content !important;
        max-width: min(78%, 900px) !important;
    }
    section.main [data-testid="stExpander"] details {
        display: inline-block !important;
        width: auto !important;
        max-width: 100% !important;
    }
    section.main [data-testid="stExpander"] summary {
        width: auto !important;
        display: inline-flex !important;
    }
    .input-panel {
        border: 1px solid #2a3342;
        border-radius: 12px;
        padding: 0.8rem;
        background: rgba(15, 19, 28, 0.75);
    }
    .input-title {
        font-weight: 700;
        margin-bottom: 0.45rem;
    }
    .composer-wrap {
        margin-top: 0.2rem;
    }
    .top-title {
        font-size: 1.35rem;
        font-weight: 700;
        margin: 0.2rem 0 0.35rem 0;
        line-height: 1.55;
        min-height: 2.25rem;
        padding-top: 0.2rem;
        overflow: visible;
        display: flex;
        align-items: center;
    }
    .top-subtitle {
        color: var(--text-soft);
        font-size: 0.9rem;
        margin: 0.1rem 0 0.65rem 0;
    }
    div[data-testid="stMetric"] {
        background: rgba(20, 24, 32, 0.75);
        border: 1px solid #2a3342;
        border-radius: 10px;
        padding: 0.5rem 0.7rem;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.72rem !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.15rem !important;
    }
    .status-block {
        margin-bottom: 0.5rem;
    }
    .status-strip {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.7rem;
        background: rgba(16, 21, 30, 0.9);
        border: 1px solid #2a3342;
        border-radius: 10px;
        padding: 0.45rem 0.6rem;
        margin-bottom: 0.55rem;
        min-height: 44px;
    }
    .status-left {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        font-size: 0.86rem;
        color: #d6dbe5;
        white-space: nowrap;
    }
    .status-right {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        flex-wrap: wrap;
        justify-content: flex-end;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        background: rgba(28, 35, 47, 0.9);
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 0.2rem 0.5rem;
        font-size: 0.8rem;
        color: #d6dbe5;
    }
    .status-pill b {
        color: #9aa6b2;
        font-weight: 600;
    }
    .send-feedback {
        width: 100%;
        border-radius: 10px;
        padding: 0.5rem 0.75rem;
        margin-top: 0.45rem;
        font-size: 0.92rem;
        border: 1px solid #355a41;
        background: rgba(27, 94, 54, 0.28);
        color: #d5f6df;
    }
    .send-feedback.error {
        border-color: #6a3a3a;
        background: rgba(120, 38, 38, 0.28);
        color: #ffd8d8;
    }
    .composer-wrap .stButton button[kind="primary"] {
        min-height: 36px !important;
        min-width: 74px !important;
        padding: 0.2rem 0.9rem !important;
        border-radius: 8px !important;
        font-size: 0.88rem !important;
        white-space: nowrap !important;
        line-height: 1.1 !important;
        margin-top: 0 !important;
    }
    .composer-wrap [data-testid="stTextInput"] input {
        min-height: 36px !important;
        height: 36px !important;
        line-height: 1.2 !important;
    }
    .composer-wrap [data-testid="stHorizontalBlock"] {
        align-items: center !important;
    }
    .composer-wrap [data-testid="stColumn"] {
        display: flex !important;
        align-items: center !important;
    }
    section.main div[data-testid="stForm"] {
        position: fixed;
        left: 50%;
        transform: translateX(-50%);
        bottom: max(24px, env(safe-area-inset-bottom));
        z-index: 70;
        background: rgba(10, 14, 22, 0.96);
        border: 1px solid #2a3342;
        border-radius: 12px;
        padding: 0.6rem 0.7rem 0.55rem 0.7rem;
        backdrop-filter: blur(6px);
        box-sizing: border-box;
        width: clamp(360px, 62vw, 860px);
        max-width: calc(100vw - 28px);
    }
    /* 侧边栏弹出/展开时，让底部输入条同步缩窄 */
    [data-testid="stAppViewContainer"]:has([data-testid="stSidebar"][aria-expanded="true"]) section.main div[data-testid="stForm"] {
        width: clamp(420px, 58vw, 860px);
        max-width: calc(100vw - 340px);
        left: calc(50% + 78px);
    }
    @media (max-width: 1100px) {
        section.main div[data-testid="stForm"] {
            left: 50%;
            transform: translateX(-50%);
            width: calc(100vw - 24px);
            bottom: 16px;
        }
        [data-testid="stAppViewContainer"]:has([data-testid="stSidebar"][aria-expanded="true"]) section.main div[data-testid="stForm"] {
            left: 50%;
            width: calc(100vw - 40px);
            max-width: calc(100vw - 40px);
        }
    }
    </style>
""", unsafe_allow_html=True)


def main():
    """主函数"""
    
    # 初始化配置
    config = settings
    
    # 初始化会话状态
    if "osc_client" not in st.session_state:
        st.session_state.osc_client = None
    if "translator" not in st.session_state:
        st.session_state.translator = None
    if "connection_status" not in st.session_state:
        st.session_state.connection_status = "未连接"
    if "api_status" not in st.session_state:
        st.session_state.api_status = "未连接"
    if "command_history" not in st.session_state:
        st.session_state.command_history = []
    if "pending_command" not in st.session_state:
        st.session_state.pending_command = None
    # 自动化开关（从本地缓存恢复）
    if "auto_connect_ma" not in st.session_state:
        st.session_state.auto_connect_ma = (get_cached_api_key("ui_auto_connect_ma") == "1")
    if "auto_send_command" not in st.session_state:
        st.session_state.auto_send_command = (get_cached_api_key("ui_auto_send_command") == "1")
    if "last_auto_sent_signature" not in st.session_state:
        st.session_state.last_auto_sent_signature = ""
    if "collapse_ai_details" not in st.session_state:
        cached = get_cached_api_key("ui_collapse_ai_details")
        st.session_state.collapse_ai_details = True if cached is None else (cached == "1")
    if "pending_feedback_message" not in st.session_state:
        st.session_state.pending_feedback_message = ""
    if "pending_feedback_is_error" not in st.session_state:
        st.session_state.pending_feedback_is_error = False
    if "scroll_nonce" not in st.session_state:
        st.session_state.scroll_nonce = 0
    if "last_message_count_by_conv" not in st.session_state:
        st.session_state.last_message_count_by_conv = {}
    if "ui_edit_api_base_url" not in st.session_state:
        st.session_state.ui_edit_api_base_url = False

    # 全局语言（从本地缓存恢复）
    if "ui_lang" not in st.session_state:
        cached = get_cached_api_key("ui_lang") or LANG_ZH
        st.session_state.ui_lang = cached if cached in LANG_LABELS else LANG_ZH
    
    # 初始化配置（支持动态修改）
    if "osc_host" not in st.session_state:
        st.session_state.osc_host = settings.ma3_osc_host
    if "osc_port" not in st.session_state:
        st.session_state.osc_port = settings.ma3_osc_port
    
    # 加载缓存的 API Key
    cached_api_key = get_cached_api_key("openai_api_key")
    cached_api_base_url = get_cached_api_key("openai_base_url")
    cached_model_id = get_cached_api_key("model_id")
    
    if "api_key" not in st.session_state:
        st.session_state.api_key = cached_api_key or ""
    if "api_base_url" not in st.session_state:
        st.session_state.api_base_url = cached_api_base_url or settings.openai_base_url
    if "model_id" not in st.session_state:
        st.session_state.model_id = cached_model_id or settings.model_id
    
    # 对话管理
    if "current_conversation_id" not in st.session_state:
        # 获取最新的对话
        conversations = list_conversations(1)
        if conversations:
            st.session_state.current_conversation_id = conversations[0]["id"]
        else:
            # 创建新对话
            conv_id = create_conversation("新对话")
            st.session_state.current_conversation_id = conv_id
    
    # 侧边栏
    with st.sidebar:
        # 语言切换（全局）
        current_lang = get_ui_lang()
        lang_codes = list(LANG_LABELS.keys())
        selected_lang = st.selectbox(
            t("sidebar.language"),
            options=lang_codes,
            index=lang_codes.index(current_lang),
            format_func=lambda c: LANG_LABELS.get(c, c),
            key="ui_lang_selector",
        )
        if selected_lang != current_lang:
            st.session_state.ui_lang = selected_lang
            save_api_key("ui_lang", selected_lang)
            st.rerun()

        st.title(t("sidebar.title"))
        
        # 对话管理
        conversations = list_conversations(2000)
        # 处理“下次 rerun 再更新”的选择器变更，避免修改已实例化的 widget key
        pending_next_conv = st.session_state.pop("conversation_selector_pending", None)
        if pending_next_conv:
            st.session_state.current_conversation_id = pending_next_conv
            st.session_state.conversation_selector = pending_next_conv

        current_id = st.session_state.current_conversation_id
        conversation_ids = {c["id"] for c in conversations}
        if current_id not in conversation_ids:
            if conversations:
                st.session_state.current_conversation_id = conversations[0]["id"]
            else:
                st.session_state.current_conversation_id = create_conversation("新对话")
                conversations = list_conversations(2000)

        with st.expander("💬 对话管理", expanded=True):
            st.caption(t("conv.total", n=len(conversations)))

            if st.button(t("conv.new"), use_container_width=True, key="create_conv_btn"):
                conv_id = create_conversation("新对话")
                st.session_state.current_conversation_id = conv_id
                st.session_state.conversation_selector_pending = conv_id
                st.rerun()

            if conversations:
                conv_map = {c["id"]: c for c in conversations}
                conv_ids = list(conv_map.keys())
                default_idx = conv_ids.index(st.session_state.current_conversation_id) if st.session_state.current_conversation_id in conv_ids else 0
                if "conversation_selector" not in st.session_state or st.session_state.conversation_selector not in conv_ids:
                    st.session_state.conversation_selector = conv_ids[default_idx]
                selected_conv_id = st.selectbox(
                    t("conv.history"),
                    options=conv_ids,
                    index=conv_ids.index(st.session_state.conversation_selector),
                    format_func=lambda cid: f"{conv_map[cid].get('title', t('conv.unnamed'))} · {conv_map[cid].get('updated_at', '')[:19]}",
                    label_visibility="collapsed",
                    key="conversation_selector"
                )
                c1, c2 = st.columns(2)
                with c1:
                    if st.button(t("conv.switch"), use_container_width=True, key="switch_selected_conv"):
                        st.session_state.current_conversation_id = selected_conv_id
                        st.rerun()
                with c2:
                    if st.button(t("conv.delete"), use_container_width=True, key="delete_selected_conv"):
                        deleting_current = selected_conv_id == st.session_state.current_conversation_id
                        delete_conversation(selected_conv_id)
                        refreshed = list_conversations(2000)
                        if refreshed:
                            next_id = refreshed[0]["id"]
                        else:
                            next_id = create_conversation("新对话")
                        if deleting_current or selected_conv_id == st.session_state.conversation_selector:
                            st.session_state.current_conversation_id = next_id
                        st.session_state.conversation_selector_pending = next_id
                        st.rerun()
            else:
                st.info(t("conv.none"))

            if st.button(t("conv.clear_messages"), use_container_width=True):
                clear_messages(st.session_state.current_conversation_id)
                st.rerun()

        with st.expander(t("history.commands"), expanded=False):
            if st.session_state.command_history:
                for i, cmd in enumerate(reversed(st.session_state.command_history), 1):
                    st.markdown(f"**{t('history.command_n', n=len(st.session_state.command_history) - i + 1)}**")
                    st.caption(cmd.get("input", ""))
                    st.markdown(f"**{t('history.ai_parse')}**")
                    st.json(cmd["parsed"], expanded=False)
                    st.markdown(f"**{t('history.osc_cmds')}**")
                    osc_commands = cmd.get("osc_commands", [])
                    if osc_commands:
                        st.code("\n".join(f"{idx+1}. {item}" for idx, item in enumerate(osc_commands)), language="text")
                    else:
                        st.caption(t("history.no_osc_cmds"))
                    st.markdown(f"**{t('history.exec_result')}** {cmd['status']}")
                    if cmd["error"]:
                        st.error(t("history.error", msg=cmd["error"]))
                    st.markdown("---")
            else:
                st.caption(t("conv.none"))

        with st.expander(t("osc.settings"), expanded=True):
            new_host = st.text_input(
                t("osc.ip"),
                value=st.session_state.osc_host,
                help=t("osc.ip_help")
            )
            new_port = st.number_input(
                t("osc.port"),
                min_value=1,
                max_value=65535,
                value=st.session_state.osc_port,
                help=t("osc.port_help")
            )
            if new_host != st.session_state.osc_host or new_port != st.session_state.osc_port:
                st.session_state.osc_host = new_host
                st.session_state.osc_port = int(new_port)
                st.info(t("osc.config_updated", host=new_host, port=int(new_port)))
            st.markdown(f"**{t('osc.current')}** `{st.session_state.osc_host}:{st.session_state.osc_port}`")
            if st.button(t("osc.reconnect"), use_container_width=True):
                initialize_connection()

        with st.expander(t("api.settings"), expanded=True):
            new_api_key = st.text_input(
                t("api.key"),
                value=st.session_state.api_key,
                type="password",
                help=t("api.key_help")
            )

            # API 地址：默认不展示明文，只显示“已缓存/未设置”，需要时再点编辑
            api_url_cached = bool((st.session_state.api_base_url or "").strip())
            url_status = t("api.url_cached") if api_url_cached else t("api.url_not_set")
            url_row_l, url_row_r = st.columns([7, 3])
            with url_row_l:
                st.caption(f"{t('api.url')}: {url_status}")
            with url_row_r:
                if not st.session_state.ui_edit_api_base_url:
                    if st.button(t("api.edit"), use_container_width=True, key="edit_api_base_url"):
                        st.session_state.ui_edit_api_base_url = True
                        st.rerun()
                else:
                    if st.button(t("api.done"), use_container_width=True, key="done_api_base_url"):
                        st.session_state.ui_edit_api_base_url = False
                        st.rerun()

            if st.session_state.ui_edit_api_base_url:
                new_api_base_url = st.text_input(
                    t("api.url"),
                    value=st.session_state.api_base_url,
                    help=t("api.url_help"),
                    key="api_base_url_input",
                )
            else:
                new_api_base_url = st.session_state.api_base_url
            preset_models = [
                {"name": "astron-code-latest", "desc": "Astron Code (推荐)"},
                {"name": "gpt-4", "desc": "GPT-4"},
                {"name": "gpt-3.5-turbo", "desc": "GPT-3.5 Turbo"},
                {"name": "claude-3-opus", "desc": "Claude 3 Opus"},
                {"name": "claude-3-sonnet", "desc": "Claude 3 Sonnet"},
                {"name": "custom", "desc": "自定义模型"},
            ]
            model_options = {m["name"]: m["desc"] for m in preset_models}
            selected_model_name = st.selectbox(
                t("api.select_model"),
                options=list(model_options.keys()),
                index=list(model_options.keys()).index(st.session_state.model_id) if st.session_state.model_id in model_options else 0,
                help=t("api.choose_help")
            )
            custom_model = ""
            if selected_model_name == "custom":
                custom_model = st.text_input(
                    t("api.custom_model"),
                    value=st.session_state.model_id,
                    placeholder=t("api.custom_model_ph"),
                )
                if custom_model:
                    selected_model_name = custom_model

            config_changed = (
                new_api_key != st.session_state.api_key or
                new_api_base_url != st.session_state.api_base_url or
                selected_model_name != st.session_state.model_id
            )
            if config_changed:
                st.session_state.api_key = new_api_key
                st.session_state.api_base_url = new_api_base_url
                st.session_state.model_id = selected_model_name
                st.session_state.api_check_result = None
                if new_api_key:
                    save_api_key("openai_api_key", new_api_key)
                if new_api_base_url:
                    save_api_key("openai_base_url", new_api_base_url)
                if selected_model_name:
                    save_api_key("model_id", selected_model_name)
                st.success(t("api.config_updated"))

            st.markdown(f"**{t('api.current_model')}** `{st.session_state.model_id}`")
            st.markdown(
                f"**{t('api.status')}** `{t('api.configured') if st.session_state.api_key else t('api.not_configured')}`"
            )

            if "api_proxy_mode" not in st.session_state:
                st.session_state.api_proxy_mode = "env"
            if "api_custom_proxy_url" not in st.session_state:
                st.session_state.api_custom_proxy_url = ""

            socks_env = (
                os.environ.get("SOCKS5_PROXY")
                or os.environ.get("socks5_proxy")
                or os.environ.get("SOCKS_PROXY")
                or os.environ.get("socks_proxy")
                or ""
            ).strip()

            st.selectbox(
                t("api.network_mode"),
                options=[
                    ("direct", t("api.net.direct")),
                    ("env", t("api.net.env")),
                    ("env_socks", t("api.net.env_socks", val=socks_env or t("api.net.none_detected"))),
                    ("custom", t("api.net.custom")),
                ],
                format_func=lambda x: x[1],
                index=[("direct",""),("env",""),("env_socks",""),("custom","")].index((st.session_state.api_proxy_mode,"")) if st.session_state.api_proxy_mode in ("direct","env","env_socks","custom") else 1,
                key="api_proxy_mode_select",
            )
            # Streamlit selectbox 需要单独映射保存 mode
            st.session_state.api_proxy_mode = st.session_state.api_proxy_mode_select[0]

            if st.session_state.api_proxy_mode == "custom":
                st.text_input(
                    t("api.net.custom_addr"),
                    value=st.session_state.api_custom_proxy_url,
                    placeholder=t("api.net.custom_ph"),
                    key="api_custom_proxy_url",
                )

            c_api_1, c_api_2 = st.columns([1, 1])
            with c_api_1:
                if st.button(t("api.check"), use_container_width=True):
                    with st.spinner(t("api.checking")):  # type: ignore[arg-type]
                        st.session_state.api_check_result = check_api_availability(
                            st.session_state.api_key,
                            st.session_state.api_base_url,
                            st.session_state.model_id,
                            True,
                        )
            with c_api_2:
                if st.button(t("api.clear_cached"), use_container_width=True):
                    clear_all_api_keys()
                    st.session_state.api_key = ""
                    st.session_state.api_check_result = None
                    st.rerun()

            api_check = st.session_state.get("api_check_result")
            if api_check:
                st.markdown(f"**{t('api.check.result')}**")
                if api_check.get("ok"):
                    st.success(
                        f"{api_check.get('message','可用')} · {api_check.get('latency_ms','?')}ms · HTTP {api_check.get('status_code')}"
                    )
                else:
                    sc = api_check.get("status_code")
                    suffix = f" · HTTP {sc}" if sc is not None else ""
                    st.error(f"{api_check.get('message','不可用')}{suffix}")
                show_details = st.checkbox(t("api.check.details"), value=False, key="api_check_show_details")
                if show_details:
                    st.code(json.dumps(api_check, ensure_ascii=False, indent=2), language="json")

        st.markdown("---")
        st.markdown(t("automation.title"))
        auto_connect_ma_new = st.toggle(
            t("automation.auto_connect"),
            value=st.session_state.auto_connect_ma,
            help=t("automation.auto_connect_help")
        )
        auto_send_command_new = st.toggle(
            t("automation.auto_send"),
            value=st.session_state.auto_send_command,
            help=t("automation.auto_send_help")
        )
        collapse_ai_details_new = st.toggle(
            t("automation.collapse_ai"),
            value=st.session_state.collapse_ai_details,
            help=t("automation.collapse_ai_help")
        )

        # 变更即持久化
        if auto_connect_ma_new != st.session_state.auto_connect_ma:
            st.session_state.auto_connect_ma = auto_connect_ma_new
            save_api_key("ui_auto_connect_ma", "1" if auto_connect_ma_new else "0")
        if auto_send_command_new != st.session_state.auto_send_command:
            st.session_state.auto_send_command = auto_send_command_new
            save_api_key("ui_auto_send_command", "1" if auto_send_command_new else "0")
        if collapse_ai_details_new != st.session_state.collapse_ai_details:
            st.session_state.collapse_ai_details = collapse_ai_details_new
            save_api_key("ui_collapse_ai_details", "1" if collapse_ai_details_new else "0")

        st.markdown("---")
        st.markdown(t("help.title"))
        st.markdown(t("help.body"))
        
        # 示例指令
        st.markdown("---")
        st.markdown(t("help.examples_title"))
        st.markdown(t("help.examples_body"))
    
    # 主界面（紧凑且顶部固定）
    
    # 自动连接（按开关触发）
    if st.session_state.auto_connect_ma and st.session_state.connection_status != "已连接":
        initialize_connection()

    # 状态区（顶部固定）
    with st.container():
        connected = st.session_state.connection_status == "已连接"
        dot_class = "connected" if connected else "disconnected"
        label = t("status.connected") if connected else t("status.disconnected")
        api_label = t("api.configured") if st.session_state.api_key else t("api.not_configured")
        st.markdown(
            (
                "<div class='status-strip'>"
                f"<div class='status-left'><span class='status-dot {dot_class}'></span>{label}</div>"
                "<div class='status-right'>"
                f"<span class='status-pill'><b>MA</b>{st.session_state.connection_status}</span>"
                f"<span class='status-pill'><b>API</b>{api_label}</span>"
                f"<span class='status-pill'><b>Model</b>{st.session_state.model_id}</span>"
                "</div>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

    # 对话区
    with st.container():
        st.markdown("<div class='chat-shell'>", unsafe_allow_html=True)
        current_messages = get_messages(st.session_state.current_conversation_id)
        if current_messages:
            for idx, msg in enumerate(current_messages):
                role = msg.get("role", "user")
                ts = msg.get("timestamp", "")[:19]
                content = msg.get("content", "")
                if role == "assistant":
                    row_left, row_right = st.columns([7.2, 4.8])
                    with row_left:
                        st.caption(t("chat.ai", ts=ts))
                        has_code_or_json = ("```" in content) or ('"intent"' in content and "actions" in content)
                        if st.session_state.collapse_ai_details and has_code_or_json:
                            preview = content.replace("```json", " ").replace("```", " ").replace("\n", " ")
                            preview = " ".join(preview.split())
                            if len(preview) > 56:
                                preview = preview[:56] + "..."
                            with st.expander(t("chat.view_ai_details", preview=preview), expanded=False):
                                st.markdown(f"<div class='msg-bubble assistant'>{content}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='msg-bubble assistant'>{content}</div>", unsafe_allow_html=True)

                        is_pending_msg = content.strip().startswith("📤 待发送 OSC 命令")
                        if is_pending_msg and st.session_state.pending_command:
                            if st.button(t("composer.send"), key=f"inline_send_pending_{idx}", type="primary"):
                                pending = st.session_state.pending_command
                                success, message = send_osc_commands(
                                    pending["input"], pending["parsed"], pending["osc_commands"]
                                )
                                if success:
                                    st.success(t("send.ok", msg=message))
                                    st.session_state.pending_command = None
                                    st.rerun()
                                else:
                                    st.error(t("send.fail", msg=message))
                else:
                    row_left, row_right = st.columns([4.2, 7.8])
                    with row_right:
                        safe_content = html.escape(str(content)).replace("\n", "<br>")
                        st.markdown(
                            (
                                "<div class='user-msg-wrap'>"
                                f"<div class='user-msg-time'>{t('chat.user', ts=ts)}</div>"
                                f"<div class='msg-bubble user'>{safe_content}</div>"
                                "</div>"
                            ),
                            unsafe_allow_html=True
                        )
        else:
            st.info(t("chat.empty"))
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 输入区（底部固定 + 小发送按钮）
    st.markdown("<div class='composer-wrap'>", unsafe_allow_html=True)
    user_input = None
    with st.form("chat_input_form", clear_on_submit=True):
        input_col, send_col = st.columns([9, 1.6])
        with input_col:
            input_text = st.text_input(
                "输入内容",
                placeholder=t("composer.placeholder"),
                label_visibility="collapsed",
                key="chat_text_input"
            )
        with send_col:
            submitted = st.form_submit_button(t("composer.send"), type="primary", use_container_width=True)
        if submitted:
            user_input = (input_text or "").strip()
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 处理用户输入
    if user_input:
        st.session_state.scroll_nonce += 1
        # 💾 保存用户输入到对话记录
        add_message(st.session_state.current_conversation_id, "user", user_input)
        
        # 1. 语义解析
        with st.spinner(t("spinner.parsing")):
            if st.session_state.translator:
                result = st.session_state.translator.translate(user_input)
            else:
                st.error(t("err.translator_not_init"))
                st.stop()
        
        if not result.success:
            # 💾 保存错误到对话记录
            add_message(st.session_state.current_conversation_id, "assistant", t("err.parse_failed", msg=result.error))
            st.error(t("err.parse_failed", msg=result.error))
            st.stop()
        
        # 💾 保存 AI 响应到对话记录
        add_message(
            st.session_state.current_conversation_id,
            "assistant",
            t("ok.parse_success", msg=result.command.explanation) + f"\n\n```json\n{result.raw_response}\n```",
        )
        
        parsed_command = result.command.model_dump()
        osc_commands = build_osc_command(result.command)

        # 保存为待发送命令，避免按钮在 rerun 后消失
        signature_raw = user_input + "|" + json.dumps(parsed_command, ensure_ascii=False, sort_keys=True)
        signature = hashlib.sha256(signature_raw.encode("utf-8")).hexdigest()
        st.session_state.pending_command = {
            "input": user_input,
            "parsed": parsed_command,
            "osc_commands": osc_commands,
            "signature": signature,
        }
        add_message(
            st.session_state.current_conversation_id,
            "assistant",
            "📤 待发送 OSC 命令：\n```\n" + "\n".join(f"{i+1}. {cmd}" for i, cmd in enumerate(osc_commands)) + "\n```"
        )

    # 待发送预览（以 AI 对话消息样式展示，不单独成块）
    pending = st.session_state.pending_command
    if pending:
        with st.container():
            st.caption(t("pending.ai_wait_confirm"))
            st.markdown(t("pending.generated"))
            cmd_preview = pending.get("osc_commands", [])
            if cmd_preview:
                more = t("pending.more", n=(len(cmd_preview) - 1)) if len(cmd_preview) > 1 else ""
                st.markdown(f"**{t('pending.preview')}** `{cmd_preview[0]}`" + (f" {more}" if more else ""))
            with st.expander(t("pending.view_details"), expanded=False):
                st.markdown(f"**{t('pending.parsed_json')}**")
                st.code(json.dumps(pending["parsed"], ensure_ascii=False, indent=2), language="json")
                st.markdown(f"**{t('pending.osc_to_send')}**")
                st.code("\n".join(f"{i}. {cmd}" for i, cmd in enumerate(pending.get("osc_commands", []), 1)), language="bash")

        # 自动发送开关开启时，直接发送一次
        if st.session_state.auto_send_command:
            pending_signature = pending.get("signature", "")
            if pending_signature and pending_signature == st.session_state.last_auto_sent_signature:
                st.info(t("pending.already_auto_sent"))
            else:
                with st.spinner(t("pending.auto_sending")):
                    success, message = send_osc_commands(
                        pending["input"], pending["parsed"], pending["osc_commands"]
                    )
                if success:
                    st.session_state.pending_feedback_message = t("send.auto_ok", msg=message)
                    st.session_state.pending_feedback_is_error = False
                else:
                    st.session_state.pending_feedback_message = t("send.auto_fail", msg=message)
                    st.session_state.pending_feedback_is_error = True
                st.session_state.last_auto_sent_signature = pending_signature
                st.session_state.pending_command = None
                st.rerun()

        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            if st.button(t("pending.confirm_send"), use_container_width=True, key="send_pending", type="primary"):
                with st.spinner(t("pending.sending")):
                    success, message = send_osc_commands(
                        pending["input"], pending["parsed"], pending["osc_commands"]
                    )
                if success:
                    st.session_state.pending_feedback_message = t("send.exec_ok", msg=message)
                    st.session_state.pending_feedback_is_error = False
                    st.session_state.pending_command = None
                    st.session_state.scroll_nonce += 1
                else:
                    st.session_state.pending_feedback_message = t("send.exec_fail", msg=message)
                    st.session_state.pending_feedback_is_error = True
        with col2:
            if st.button(t("pending.clear"), use_container_width=True, key="cancel_pending", type="secondary"):
                st.session_state.pending_command = None
                st.info(t("pending.cancelled"))
        with col3:
            st.empty()
        if st.session_state.pending_feedback_message:
            cls = "send-feedback error" if st.session_state.pending_feedback_is_error else "send-feedback"
            st.markdown(
                f"<div class='{cls}'>{st.session_state.pending_feedback_message}</div>",
                unsafe_allow_html=True
            )

    # 智能自动滚动：仅当当前会话有新消息时触发
    current_conv_id = st.session_state.current_conversation_id
    current_message_count = len(current_messages) if "current_messages" in locals() else 0
    last_count = st.session_state.last_message_count_by_conv.get(current_conv_id, 0)
    should_auto_scroll = current_message_count > last_count
    st.session_state.last_message_count_by_conv[current_conv_id] = current_message_count

    if should_auto_scroll:
        anchor_id = f"chat-bottom-anchor-{st.session_state.scroll_nonce}"
        st.markdown(f"<div id='{anchor_id}'></div>", unsafe_allow_html=True)
        scroll_script = """
        <script>
        (function() {{
          const tryScroll = () => {{
            const p = window.parent;
            const doc = p.document;
            const anchor = doc.querySelector('#{anchor_id}');

            // 1) 优先滚到锚点
            if (anchor) {{
              anchor.scrollIntoView({{ behavior: 'smooth', block: 'end', inline: 'nearest' }});
            }}

            // 2) 同时尝试常见滚动容器
            const main = doc.querySelector('section.main');
            const appView = doc.querySelector('[data-testid="stAppViewContainer"]');
            const block = doc.querySelector('.block-container');
            [main, appView, block, doc.scrollingElement, doc.documentElement, doc.body].forEach((el) => {{
              if (!el) return;
              try {{
                el.scrollTop = el.scrollHeight;
              }} catch (e) {{}}
            }});

            // 3) 再兜底 window 滚动
            try {{
              p.scrollTo({{ top: doc.body.scrollHeight, behavior: 'smooth' }});
            }} catch (e) {{
              p.scrollTo(0, doc.body.scrollHeight);
            }}
          }};

          // 连续重试一小段时间，覆盖 Streamlit rerun 后异步渲染
          let count = 0;
          const timer = setInterval(() => {{
            tryScroll();
            count += 1;
            if (count >= 12) clearInterval(timer);
          }}, 120);

          setTimeout(tryScroll, 30);
          setTimeout(tryScroll, 300);
          setTimeout(tryScroll, 700);
          setTimeout(tryScroll, 1200);
        }})();
        </script>
        """.format(anchor_id=anchor_id)
        st_html(scroll_script, height=0)


def send_osc_commands(user_input: str, parsed: dict, osc_commands: list) -> tuple:
    """
    发送 OSC 命令并记录历史
    """
    if st.session_state.auto_connect_ma and (
        st.session_state.osc_client is None or st.session_state.connection_status != "已连接"
    ):
        initialize_connection()

    if not st.session_state.osc_client:
        st.session_state.command_history.append({
            "input": user_input,
            "parsed": parsed,
            "osc_commands": osc_commands,
            "status": "失败",
            "error": t("send.osc_client_not_init")
        })
        return (False, t("send.osc_client_not_init"))

    success, message = st.session_state.osc_client.send_command(osc_commands)
    st.session_state.command_history.append({
        "input": user_input,
        "parsed": parsed,
        "osc_commands": osc_commands,
        "status": "成功" if success else "失败",
        "error": None if success else message
    })
    return (success, message)


def initialize_connection():
    """初始化连接"""
    
    try:
        # 使用会话状态中的动态配置
        host = st.session_state.osc_host
        port = st.session_state.osc_port
        api_key = st.session_state.api_key
        base_url = st.session_state.api_base_url
        model_id = st.session_state.model_id
        proxy_mode = st.session_state.get("api_proxy_mode", "env")
        proxy_url = None
        trust_env = True
        if proxy_mode == "direct":
            trust_env = False
            proxy_url = None
        elif proxy_mode == "env_socks":
            trust_env = False
            proxy_url = (
                os.environ.get("SOCKS5_PROXY")
                or os.environ.get("socks5_proxy")
                or os.environ.get("SOCKS_PROXY")
                or os.environ.get("socks_proxy")
            )
        elif proxy_mode == "custom":
            trust_env = False
            proxy_url = st.session_state.get("api_custom_proxy_url")
        else:
            trust_env = True
            proxy_url = None
        
        # 初始化 OSC 客户端
        st.session_state.osc_client = create_gma3_client(
            host=host,
            port=port
        )
        
        # 测试连接 - 使用更可靠的测试命令
        success, message = st.session_state.osc_client.send_command(["ClearAll"])
        
        # 打印调试信息
        print(f"DEBUG: 连接测试结果 - success={success}, message={message}")
        print(f"DEBUG: osc_client.connected={st.session_state.osc_client.connected}")
        print(f"DEBUG: osc_client.client={st.session_state.osc_client.client}")
        
        if success:
            st.session_state.connection_status = "已连接"
            st.session_state.api_status = "已连接" if (api_key and base_url) else "未配置"
        else:
            st.session_state.connection_status = "未连接"
            st.session_state.api_status = "未配置"
        
        # 初始化翻译器
        if api_key and base_url:
            st.session_state.translator = create_translator(
                api_key=api_key,
                base_url=base_url,
                model_id=model_id,
                trust_env=trust_env,
                proxy_url=proxy_url,
            )
        else:
            st.session_state.translator = None
        
        # 不再显示 st.success/st.error，避免无限循环
        # 状态会在主界面自动更新
        
    except Exception as e:
        st.session_state.connection_status = "未连接"
        st.session_state.api_status = "未连接"
        st.session_state.translator = None


def build_osc_command(command) -> list:
    """
    构建 OSC 指令列表
    
    根据 GMA3Command 对象构建最终的 OSC 指令列表。
    严格遵守 grandMA3 OSC 核心语法指南：
    - 范围选灯：Fixture [ID] + [ID] + ...
    - 亮度赋值：At [数值]
    - 颜色预设：At Preset "Color"."颜色名"（优先使用）
    - 属性控制：Attribute "属性名" At 数值
    - 每次发送前自动添加 ClearAll
    
    Args:
        command: GMA3Command 对象
        
    Returns:
        list: OSC 指令列表（纯净格式，不包含 /cmd 和引号）
    """
    # 1. 先发送 ClearAll（归位与清空）
    commands = ["ClearAll"]

    # 2. 新结构：遍历 actions 生成命令
    actions = getattr(command, "actions", []) or []
    for action in actions:
        fixture_ids = getattr(action, "fixture_ids", []) or []
        attributes = getattr(action, "attributes", {}) or {}
        if not fixture_ids:
            continue

        if len(fixture_ids) == 1:
            fixture_expr = f"Fixture {fixture_ids[0]}"
        else:
            fixture_expr = "Fixture " + " + ".join(str(fid) for fid in fixture_ids)

        # 亮度命令
        if "Dimmer" in attributes:
            commands.append(f"{fixture_expr} At {attributes['Dimmer']}")

        # 颜色命令：优先 Color 名称，其次 RGB 转名称
        color_name = None
        if "Color" in attributes and attributes["Color"]:
            color_name = str(attributes["Color"]).strip()
        else:
            rgb_attrs = {k: v for k, v in attributes.items() if str(k).startswith("ColorRGB_")}
            if rgb_attrs:
                color_name = rgb_to_color_name(rgb_attrs)

        if color_name:
            commands.append(f'{fixture_expr} At Preset "Color"."{normalize_color_name(color_name)}"')

        # 其他属性走 Attribute 语法
        for attr, value in attributes.items():
            if attr in ("Dimmer", "Color"):
                continue
            if str(attr).startswith("ColorRGB_"):
                continue
            commands.append(f'{fixture_expr} Attribute "{attr}" At {value}')

    # 3. 兜底：如果没有任何有效动作，只发送 ClearAll
    return commands


def normalize_color_name(color_name: str) -> str:
    """规范化颜色名称，兼容中英文常见写法。"""
    mapping = {
        "红": "Red",
        "红色": "Red",
        "green": "Green",
        "绿色": "Green",
        "blue": "Blue",
        "蓝": "Blue",
        "蓝色": "Blue",
        "purple": "Purple",
        "紫": "Purple",
        "紫色": "Purple",
        "yellow": "Yellow",
        "黄": "Yellow",
        "黄色": "Yellow",
        "white": "White",
        "白": "White",
        "白色": "White",
        "sadblue": "SadBlue",
        "忧郁蓝": "SadBlue",
        "忧郁的蓝色": "SadBlue",
    }
    key = color_name.strip().lower()
    return mapping.get(key, color_name.strip())


def rgb_to_color_name(rgb_attrs: dict) -> str:
    """
    将 RGB 属性转换为颜色名称
    
    Args:
        rgb_attrs: RGB 属性字典
        
    Returns:
        str: 颜色名称
    """
    # 提取 RGB 值
    r = rgb_attrs.get("ColorRGB_R", 0)
    g = rgb_attrs.get("ColorRGB_G", 0)
    b = rgb_attrs.get("ColorRGB_B", 0)
    
    # 定义颜色映射
    color_map = {
        (255, 0, 0): "Red",
        (0, 255, 0): "Green",
        (0, 0, 255): "Blue",
        (128, 0, 128): "Purple",
        (255, 255, 0): "Yellow",
        (255, 255, 255): "White",
        (0, 100, 200): "SadBlue",
    }
    
    # 查找匹配的颜色
    for (cr, cg, cb), name in color_map.items():
        if r == cr and g == cg and b == cb:
            return name
    
    # 如果没有匹配的颜色，返回默认值
    return "White"


if __name__ == "__main__":
    main()
