#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MA3 OSC 语义编程助手 - 完整版
集成 AI 语义解析、对话历史管理、动态配置
MA3 风格 UI 重构版
"""

import streamlit as st
from src.osc.osc_client import create_gma3_client
from src.ai.translator import create_translator
from src.utils.conversation_manager import (
    ConversationManager,
    add_message,
    list_conversations,
    get_conversation_count
)
from src.utils.api_key_cache import (
    get_cached_api_key,
    save_api_key,
    clear_all_api_keys
)
from config import settings
import json

# 必须在最前面调用
st.set_page_config(page_title="MA3 OSC 语义编程助手", layout="wide")

# MA3 风格主题注入
def apply_ma3_theme():
    """注入 MA3 风格 CSS 样式"""
    st.markdown("""
    <style>
    /* 全局背景与字体 */
    .stApp {
        background-color: #0F0F0F;
        color: #CCCCCC;
        font-family: 'Inter', 'Source Code Pro', 'Consolas', monospace;
    }
    
    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background-color: #1E1E1E;
        border-right: 1px solid #333333;
    }
    
    /* 主内容区域 */
    .main > div {
        background-color: #0F0F0F;
    }
    
    /* 按钮美化：MA3 标志性黄色 */
    div.stButton > button:first-child {
        background-color: #FFB300 !important;
        color: black !important;
        border: none;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(255, 179, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    div.stButton > button:first-child:hover {
        background-color: #FFC107 !important;
        box-shadow: 0 4px 8px rgba(255, 179, 0, 0.4);
        transform: translateY(-1px);
    }
    
    /* 次要按钮（清除缓存等） */
    div.stButton > button:nth-child(n+2) {
        background-color: #333333 !important;
        color: #CCCCCC !important;
        border: 1px solid #444444;
        font-weight: 600;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:nth-child(n+2):hover {
        background-color: #444444 !important;
        border-color: #555555 !important;
    }
    
    /* 标题样式 */
    h1, h2, h3, h4, h5, h6 {
        color: #FFB300 !important;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    
    /* 输入框样式 */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #1A1A1A !important;
        border: 1px solid #333333 !important;
        color: #CCCCCC !important;
        border-radius: 4px;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #FFB300 !important;
        box-shadow: 0 0 0 2px rgba(255, 179, 0, 0.2) !important;
    }
    
    /* 卡片/容器样式 */
    .stMetric,
    .stExpander,
    .stTabs {
        background-color: #1E1E1E;
        border: 1px solid #333333;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* JSON 代码块样式 */
    .stCodeBlock,
    pre,
    code {
        background-color: transparent !important;
        border: 1px solid #333333 !important;
        border-radius: 4px;
        font-family: 'Consolas', 'Monaco', 'Source Code Pro', monospace !important;
        font-size: 0.9rem;
        color: #E0E0E0 !important;
    }
    
    /* 聊天气泡样式优化 */
    [data-testid="stChatMessage"] {
        background-color: #1E1E1E;
        border-radius: 8px;
        margin-bottom: 10px;
        border: 1px solid #2A2A2A;
        padding: 1rem;
    }
    
    /* 命令反馈行样式 */
    .command-feedback {
        background-color: #000000;
        border: 1px solid #444444;
        border-radius: 4px;
        padding: 0.75rem;
        font-family: 'Consolas', 'Monaco', 'Source Code Pro', monospace;
        color: #00FF00;
        font-size: 0.85rem;
        line-height: 1.6;
        margin: 0.5rem 0;
    }
    
    /* 分隔线样式 */
    hr {
        border: 0;
        border-top: 1px solid #333333;
        margin: 1.5rem 0;
    }
    
    /* 信息提示框 */
    .stAlert {
        background-color: #1E1E1E;
        border: 1px solid #333333;
        border-radius: 4px;
    }
    
    /* 成功/错误消息 */
    .stSuccess,
    .stError,
    .stInfo {
        background-color: #1E1E1E;
        border: 1px solid #333333;
        border-radius: 4px;
        padding: 0.75rem;
    }
    
    /* 滚动条美化 */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0F0F0F;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #333333;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #444444;
    }
    
    /* 折叠面板样式 */
    .stExpander[aria-expanded="true"] {
        background-color: #1A1A1A;
        border: 1px solid #333333;
        border-radius: 4px;
        padding: 0.5rem;
    }
    
    /* 表格样式 */
    table {
        background-color: #1E1E1E;
        border: 1px solid #333333;
        border-radius: 4px;
    }
    
    th,
    td {
        border: 1px solid #333333;
        padding: 0.5rem;
        text-align: left;
    }
    
    th {
        background-color: #1A1A1A;
        color: #FFB300;
    }
    </style>
    """, unsafe_allow_html=True)

# 应用 MA3 主题
apply_ma3_theme()

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
    - 支持多 actions 列表
    
    Args:
        command: GMA3Command 对象
        
    Returns:
        list: OSC 指令列表（纯净格式，不包含 /cmd 和引号）
    """
    # 1. 先发送 ClearAll（归位与清空）
    commands = ["ClearAll"]
    
    # 2. 遍历 actions 列表
    for action in command.actions:
        parts = []
        
        # 3. 灯具 ID - 使用 "+" 连接所有 ID，防止误选 ID 间隔中的灯具
        if action.fixture_ids:
            if len(action.fixture_ids) == 1:
                parts.append(f"Fixture {action.fixture_ids[0]}")
            else:
                # 使用 + 连接所有 ID，而不是 Thru 范围
                fixture_ids_str = " + ".join(str(fid) for fid in action.fixture_ids)
                parts.append(f"Fixture {fixture_ids_str}")
        
        # 4. 属性 - 根据属性类型使用不同的语法
        if action.attributes:
            attr_parts = []
            
            # 检查是否有 Dimmer 属性
            if "Dimmer" in action.attributes:
                dimmer_value = action.attributes["Dimmer"]
                attr_parts.append(f"At {dimmer_value}")
            
            # 检查是否有颜色属性
            if "Color" in action.attributes:
                color_name = action.attributes["Color"]
                attr_parts.append(f'At Preset "Color"."{color_name}"')
            
            # 检查是否有 RGB 属性（兼容旧格式）
            color_attrs = {}
            for attr, value in action.attributes.items():
                if attr.startswith("ColorRGB_"):
                    color_attrs[attr] = value
            
            if color_attrs:
                # 将 RGB 值转换为颜色名称
                color_name = rgb_to_color_name(color_attrs)
                if color_name:
                    attr_parts.append(f'At Preset "Color"."{color_name}"')
            
            if attr_parts:
                parts.append(" ".join(attr_parts))
        
        # 5. 合并命令
        if parts:
            commands.append(" ".join(parts))
    
    # 6. 返回指令列表
    return commands

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

# 初始化会话状态
if "osc_client" not in st.session_state:
    st.session_state.osc_client = None
if "translator" not in st.session_state:
    st.session_state.translator = None
if "connection_status" not in st.session_state:
    st.session_state.connection_status = "未连接"
if "api_status" not in st.session_state:
    st.session_state.api_status = "未配置"
if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None
if "conversation_list" not in st.session_state:
    st.session_state.conversation_list = []
if "command_history" not in st.session_state:
    st.session_state.command_history = []

# 初始化对话管理器
if "conv_manager" not in st.session_state:
    st.session_state.conv_manager = ConversationManager()

# 初始化对话列表
if not st.session_state.conversation_list:
    st.session_state.conversation_list = list_conversations(limit=50)
    if st.session_state.conversation_list:
        st.session_state.current_conversation_id = st.session_state.conversation_list[0]["id"]
    else:
        # 创建第一个对话
        st.session_state.current_conversation_id = st.session_state.conv_manager.create_conversation("新对话")
        st.session_state.conversation_list = list_conversations(limit=50)

# 加载缓存的 API 配置
if "api_key_cached" not in st.session_state:
    cached_key = get_cached_api_key("api_key")
    st.session_state.api_key_cached = cached_key is not None
if "api_base_url_cached" not in st.session_state:
    cached_url = get_cached_api_key("api_base_url")
    st.session_state.api_base_url_cached = cached_url is not None
if "model_id_cached" not in st.session_state:
    cached_model = get_cached_api_key("model_id")
    st.session_state.model_id_cached = cached_model is not None

# 侧边栏
with st.sidebar:
    st.title("🎭 MA3 OSC 助手")
    
    # 🔌 OSC 配置
    st.header("🔌 OSC 配置")
    osc_host = st.text_input("OSC Host", value="127.0.0.1", key="osc_host")
    osc_port = st.number_input("OSC Port", value=8000, min_value=1, max_value=65535, key="osc_port")
    
    # 🔄 连接控制
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 连接", use_container_width=True):
            with st.spinner("正在连接..."):
                try:
                    client = create_gma3_client(host=osc_host, port=osc_port)
                    st.session_state.osc_client = client
                    
                    # 测试连接
                    success, message = client.send_command(["ClearAll"])
                    
                    if success:
                        st.session_state.connection_status = "已连接"
                        st.success("✅ 连接成功！")
                        print(f"DEBUG: OSC 连接成功 - {message}")
                    else:
                        st.session_state.connection_status = "未连接"
                        st.error(f"❌ 连接失败：{message}")
                        print(f"DEBUG: OSC 连接失败 - {message}")
                        
                except Exception as e:
                    st.session_state.connection_status = "未连接"
                    st.error(f"❌ 连接错误：{e}")
                    print(f"DEBUG: OSC 连接错误 - {e}")
    
    with col2:
        if st.button("❌ 断开", use_container_width=True):
            if st.session_state.osc_client:
                try:
                    st.session_state.osc_client.disconnect()
                    st.session_state.osc_client = None
                    st.session_state.connection_status = "未连接"
                    st.info("❌ 已断开连接")
                    print("DEBUG: OSC 断开连接")
                except Exception as e:
                    st.error(f"❌ 断开错误：{e}")
    
    st.info(f"📡 状态：{st.session_state.connection_status}")
    
    st.divider()
    
    # 🤖 API 配置
    st.header("🤖 API 配置")
    
    # 加载缓存的 API 配置
    cached_api_key = get_cached_api_key("api_key")
    cached_api_base_url = get_cached_api_key("api_base_url")
    cached_model_id = get_cached_api_key("model_id")
    
    api_key = st.text_input("API Key", type="password", value=cached_api_key, key="api_key_input")
    api_base_url = st.text_input("API Base URL", value=cached_api_base_url, key="api_base_url_input")
    model_id = st.text_input("Model ID", value=cached_model_id, key="model_id_input")
    
    # 显示缓存状态
    if cached_api_key or cached_api_base_url or cached_model_id:
        st.success("✅ 已加载缓存的 API 配置")
    
    # 💾 保存 API 配置
    if api_key and api_base_url and model_id:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 保存 API 配置", use_container_width=True):
                # 保存到缓存
                save_api_key("api_key", api_key)
                save_api_key("api_base_url", api_base_url)
                save_api_key("model_id", model_id)
                
                # 更新会话状态
                st.session_state.api_key_cached = True
                st.session_state.api_base_url_cached = True
                st.session_state.model_id_cached = True
                
                st.success("✅ API 配置已保存到本地缓存")
                print(f"DEBUG: API 配置已缓存 - Key: {api_key[:10]}..., URL: {api_base_url}, Model: {model_id}")
        
        with col2:
            if st.button("🗑️ 清除缓存", use_container_width=True):
                clear_all_api_keys()
                st.session_state.api_key_cached = False
                st.session_state.api_base_url_cached = False
                st.session_state.model_id_cached = False
                st.rerun()
    
    # 🔄 测试 API
    if st.button("🔌 测试 API", use_container_width=True):
        # 优先使用输入框的值，如果没有则使用缓存的值
        test_api_key = api_key if api_key else get_cached_api_key("api_key")
        test_api_base_url = api_base_url if api_base_url else get_cached_api_key("api_base_url")
        test_model_id = model_id if model_id else get_cached_api_key("model_id")
        
        if test_api_key and test_api_base_url and test_model_id:
            with st.spinner("正在测试 API..."):
                try:
                    translator = create_translator(api_key=test_api_key, base_url=test_api_base_url, model_id=test_model_id)
                    st.session_state.translator = translator
                    st.session_state.api_status = "已连接"
                    st.success("✅ API 连接成功！")
                    print("DEBUG: API 连接成功")
                except Exception as e:
                    st.session_state.translator = None
                    st.session_state.api_status = "未连接"
                    st.error(f"❌ API 连接失败：{e}")
                    print(f"DEBUG: API 连接失败 - {e}")
        else:
            st.error("❌ 请先配置 API 信息")
    
    st.info(f"🤖 状态：{st.session_state.api_status}")
    
    st.divider()
    
    # 💬 对话管理
    st.header("💬 对话管理")
    
    if st.button("➕ 新建对话", use_container_width=True):
        new_id = st.session_state.conv_manager.create_conversation("新对话")
        st.session_state.current_conversation_id = new_id
        st.session_state.conversation_list = list_conversations(limit=50)
        st.rerun()
    
    # 显示对话列表
    st.subheader("对话列表")
    for conv in st.session_state.conversation_list:
        is_current = conv["id"] == st.session_state.current_conversation_id
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(
                f"{'✅ ' if is_current else ''}{conv['title'][:20]}...",
                key=f"conv_{conv['id']}",
                use_container_width=True
            ):
                st.session_state.current_conversation_id = conv["id"]
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{conv['id']}", use_container_width=True):
                if conv["id"] != st.session_state.current_conversation_id:
                    st.session_state.conv_manager.delete_conversation(conv["id"])
                    st.session_state.conversation_list = list_conversations(limit=50)
                    st.rerun()
                else:
                    st.error("❌ 不能删除当前对话")
    
    st.divider()
    
    # 📖 使用说明（折叠面板）
    with st.expander("📖 使用说明 & 示例指令", expanded=False):
        st.markdown("""
        ### 📝 自然语言输入示例
        
        - `1 号灯变黄`
        - `把 101 到 105 号灯亮度调到 50%`
        - `清空所有选中`
        - `Fixture 1 At 100`
        - `ClearAll`
        
        ### 🎯 操作流程
        
        1. **配置 OSC 连接** - 输入 Host 和 Port
        2. **配置 API**（可选）- 输入 API Key、Base URL、Model ID
        3. **输入自然语言指令** - 在下方输入框输入
        4. **点击"✅ 确认下发"** - 指令将发送到 grandMA3
        
        ### 💡 提示
        
        - 所有 OSC 命令会自动添加 `ClearAll` 前缀
        - 范围选灯使用 `+` 连接（如 `Fixture 1 + 2 + 3`）
        - 颜色使用预设名称（如 `Yellow`, `Red`, `Blue`）
        - 对话历史自动保存，可切换不同对话
        """)

# 主界面
st.title("🎭 grandMA3 语义编程助手")

# 显示当前对话信息
st.markdown(f"<div style='color: #FFB300; font-weight: 700;'>💬 当前对话：{st.session_state.current_conversation_id}</div>", unsafe_allow_html=True)

st.divider()

# 对话历史
st.markdown("<div style='color: #FFB300; font-weight: 700;'>💬 对话历史</div>", unsafe_allow_html=True)

if st.session_state.current_conversation_id:
    messages = st.session_state.conv_manager.get_messages(st.session_state.current_conversation_id)
    
    if messages:
        for msg in messages:
            role = "👤 你" if msg["role"] == "user" else "🤖 AI"
            timestamp = msg.get("timestamp", "")
            
            with st.chat_message(role):
                st.markdown(msg["content"])
                if timestamp:
                    st.caption(f"⏰ {timestamp}")
    else:
        st.info("💬 暂无对话记录")
else:
    st.info("💬 请先创建或选择对话")

st.divider()

# 语义解析输入
st.markdown("<div style='color: #FFB300; font-weight: 700;'>🔍 语义解析</div>", unsafe_allow_html=True)

st.markdown("<div style='color: #999999; font-style: italic;'>💡 输入自然语言指令，AI 会自动解析并转换为 OSC 命令</div>", unsafe_allow_html=True)

# 输入框（固定在底部）
user_input = st.text_input("输入自然语言指令...", key="chat_input", label_visibility="collapsed")

if user_input:
    # 保存用户输入
    add_message(st.session_state.current_conversation_id, "user", user_input)
    
    # 显示用户消息
    st.markdown(f"<div style='color: #CCCCCC;'>👤 **你**: {user_input}</div>", unsafe_allow_html=True)
    
    # AI 解析
    if st.session_state.translator:
        with st.spinner("🤖 AI 正在解析指令..."):
            try:
                result = st.session_state.translator.translate(user_input)
                
                if not result.success:
                    # 保存错误
                    add_message(st.session_state.current_conversation_id, "assistant", f"❌ 解析失败：{result.error}")
                    
                    st.markdown(f"<div style='color: #FF6B6B;'>🤖 **AI**: ❌ 解析失败：{result.error}</div>", unsafe_allow_html=True)
                else:
                    # 保存 AI 响应
                    response_content = f"✅ 解析成功：{result.command.explanation}\n\n```json\n{result.raw_response}\n```"
                    add_message(st.session_state.current_conversation_id, "assistant", response_content)
                    
                    st.markdown(f"<div style='color: #4ECDC4;'>🤖 **AI**: {response_content}</div>", unsafe_allow_html=True)
                    
                    # 显示解析结果
                    st.markdown("<div style='color: #FFB300; font-weight: 700;'>🔍 AI 解析结果</div>", unsafe_allow_html=True)
                    st.json(result.command.model_dump(), expanded=True)
                    
                    # 显示 OSC 命令 - 控制台反馈行样式
                    st.markdown("<div style='color: #FFB300; font-weight: 700;'>📤 即将发送的 OSC 命令</div>", unsafe_allow_html=True)
                    
                    # 构建 OSC 命令列表
                    osc_commands = build_osc_command(result.command)
                    
                    # 控制台反馈行
                    st.markdown("""
                    <div class="command-feedback">
                        <div style='color: #00FF00; font-weight: 700;'>[COMMAND FEEDBACK]</div>
                    """, unsafe_allow_html=True)
                    
                    for i, cmd in enumerate(osc_commands, 1):
                        st.markdown(f"<div style='color: #00FF00;'>  {i}. {cmd}</div>", unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # 保存 OSC 命令到对话记录
                    add_message(
                        st.session_state.current_conversation_id,
                        "assistant",
                        f"📤 OSC 命令：\n```\n" + "\n".join(f"{i+1}. {cmd}" for i, cmd in enumerate(osc_commands)) + "\n```"
                    )
                    
                    # 执行确认
                    st.divider()
                    col1, col2, col3 = st.columns([1, 1, 3])
                    with col1:
                        if st.button("✅ 确认下发", use_container_width=True):
                            # 发送 OSC 命令
                            with st.spinner("📡 正在发送 OSC 命令..."):
                                if st.session_state.osc_client:
                                    print(f"DEBUG: 开始发送命令，osc_commands={osc_commands}")
                                    
                                    # send_command 返回 (success, message) 元组
                                    success, message = st.session_state.osc_client.send_command(osc_commands)
                                    
                                    print(f"DEBUG: 发送完成，success={success}, message={message}")
                                    
                                    if success:
                                        st.success(f"✅ 执行成功：{message}")
                                        
                                        # 添加到历史记录
                                        st.session_state.command_history.append({
                                            "input": user_input,
                                            "parsed": result.command.model_dump(),
                                            "osc_commands": osc_commands,
                                            "status": "成功",
                                            "error": None
                                        })
                                    else:
                                        st.error(f"❌ 执行失败：{message}")
                                        
                                        # 添加到历史记录
                                        st.session_state.command_history.append({
                                            "input": user_input,
                                            "parsed": result.command.model_dump(),
                                            "osc_commands": osc_commands,
                                            "status": "失败",
                                            "error": message
                                        })
                                else:
                                    st.error("❌ OSC 客户端未初始化")
                                    print("DEBUG: osc_client 未初始化")
                    
                    with col2:
                        st.button("❌ 取消", use_container_width=True)
                    
                    with col3:
                        st.markdown("<div style='color: #999999; font-style: italic;'>💡 点击'确认下发'后，指令将保存到历史区</div>", unsafe_allow_html=True)
            
            except Exception as e:
                st.error(f"❌ 解析错误：{e}")
                print(f"DEBUG: 解析错误 - {e}")
                import traceback
                traceback.print_exc()
    else:
        st.markdown("<div style='color: #FFA500;'>⚠️ 请先配置并连接 API</div>", unsafe_allow_html=True)

# 显示客户端状态
st.divider()
st.markdown("<div style='color: #FFB300; font-weight: 700;'>📊 客户端状态</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if st.session_state.osc_client:
        st.markdown("""
        <div style='background-color: #1A1A1A; border: 1px solid #333333; border-radius: 8px; padding: 1rem;'>
            <div style='color: #FFB300; font-weight: 700; margin-bottom: 0.5rem;'>📡 OSC 客户端</div>
            <div style='color: #CCCCCC; font-size: 0.9rem;'>Host: <span style='color: #00FF00;'>{}</span></div>
            <div style='color: #CCCCCC; font-size: 0.9rem;'>Port: <span style='color: #00FF00;'>{}</span></div>
            <div style='color: #CCCCCC; font-size: 0.9rem;'>Status: <span style='color: #00FF00;'>Connected</span></div>
            <div style='color: #CCCCCC; font-size: 0.9rem;'>Commands Sent: <span style='color: #00FF00;'>{}</span></div>
            <div style='color: #CCCCCC; font-size: 0.9rem;'>Commands Failed: <span style='color: #FF6B6B;'>{}</span></div>
        </div>
        """.format(
            st.session_state.osc_client.host,
            st.session_state.osc_client.port,
            st.session_state.osc_client.stats["commands_sent"],
            st.session_state.osc_client.stats["commands_failed"]
        ), unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background-color: #1A1A1A; border: 1px solid #333333; border-radius: 8px; padding: 1rem;'>
            <div style='color: #FF6B6B; font-weight: 700;'>❌ 未连接</div>
        </div>
        """, unsafe_allow_html=True)

with col2:
    if st.session_state.translator:
        st.markdown("""
        <div style='background-color: #1A1A1A; border: 1px solid #333333; border-radius: 8px; padding: 1rem;'>
            <div style='color: #00FF00; font-weight: 700;'>✅ API 已连接</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background-color: #1A1A1A; border: 1px solid #333333; border-radius: 8px; padding: 1rem;'>
            <div style='color: #FFA500; font-weight: 700;'>⚠️ API 未连接</div>
        </div>
        """, unsafe_allow_html=True)

# 显示命令历史
if st.session_state.command_history:
    st.divider()
    st.markdown("<div style='color: #FFB300; font-weight: 700;'>📜 命令历史</div>", unsafe_allow_html=True)
    
    for i, cmd in enumerate(reversed(st.session_state.command_history), 1):
        with st.expander(f"{i}. {cmd['input']} ({cmd['status']})"):
            st.markdown("""
            <div style='background-color: #1A1A1A; border: 1px solid #333333; border-radius: 8px; padding: 1rem;'>
                <div style='color: #FFB300; font-weight: 700; margin-bottom: 0.5rem;'>🔍 解析结果</div>
                <div style='color: #CCCCCC; font-family: monospace; font-size: 0.85rem;'>{}</div>
                <div style='color: #FFB300; font-weight: 700; margin-top: 1rem; margin-bottom: 0.5rem;'>📤 OSC 命令</div>
                <div style='color: #00FF00; font-family: monospace; font-size: 0.85rem;'>{}</div>
                {}{}
            </div>
            """.format(
                json.dumps(cmd["parsed"], ensure_ascii=False, indent=2),
                "\n".join(f"  {j+1}. {c}" for j, c in enumerate(cmd["osc_commands"])),
                "<div style='color: #FF6B6B; margin-top: 0.5rem;'>❌ 错误：{}</div>".format(cmd["error"]) if cmd["error"] else "",
                "<div style='color: #00FF00; margin-top: 0.5rem;'>✅ 执行成功</div>" if not cmd["error"] else ""
            ), unsafe_allow_html=True)
