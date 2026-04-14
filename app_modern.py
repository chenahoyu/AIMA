#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MA3 OSC 语义编程助手 - Modern AI Agent UI 版
采用对话流布局，类似 ChatGPT 的简洁界面
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
import time

# 必须在最前面调用
st.set_page_config(
    page_title="MA3 OSC 语义编程助手",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    
    /* 次要按钮 */
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
    
    /* 聊天气泡样式 */
    [data-testid="stChatMessage"] {
        background-color: #1E1E1E;
        border-radius: 12px;
        margin-bottom: 1rem;
        border: 1px solid #2A2A2A;
        padding: 1rem;
    }
    
    /* MA3 终端样式 */
    .ma3-terminal {
        background-color: #000000;
        border: 2px solid #00FF00;
        border-radius: 8px;
        padding: 1rem;
        font-family: 'Consolas', 'Monaco', 'Source Code Pro', monospace;
        color: #00FF00;
        font-size: 0.9rem;
        line-height: 1.6;
        position: relative;
        margin: 1rem 0;
    }
    
    .ma3-terminal::before {
        content: "MA3 TERMINAL";
        position: absolute;
        top: -12px;
        right: 10px;
        background-color: #00FF00;
        color: #000000;
        padding: 2px 8px;
        font-size: 0.7rem;
        font-weight: 700;
        border-radius: 4px;
    }
    
    .ma3-command {
        margin: 0.5rem 0;
        padding-left: 1rem;
    }
    
    .ma3-confirm-btn {
        position: absolute;
        bottom: -40px;
        right: 0;
        background-color: #00FF00 !important;
        color: #000000 !important;
        border: none;
        font-weight: 700;
        padding: 0.5rem 1rem !important;
        border-radius: 4px !important;
        font-size: 0.8rem !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        box-shadow: 0 2px 4px rgba(0, 255, 0, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .ma3-confirm-btn:hover {
        background-color: #00FF66 !important;
        box-shadow: 0 4px 8px rgba(0, 255, 0, 0.4) !important;
        transform: translateY(-1px) !important;
    }
    
    /* 解析思路样式 */
    .thinking-process {
        background-color: #1A1A1A;
        border-left: 3px solid #FFB300;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
        font-size: 0.9rem;
        color: #CCCCCC;
    }
    
    .thinking-title {
        color: #FFB300;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    /* 折叠面板样式 */
    .stExpander {
        background-color: #1A1A1A;
        border: 1px solid #333333;
        border-radius: 8px;
        padding: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .stExpander[aria-expanded="true"] {
        background-color: #1A1A1A;
        border: 1px solid #FFB300;
    }
    
    /* 聊天气泡对齐样式 */
    [data-testid="stChatMessage"][data-chat-align="right"] {
        background-color: #2A4A2A;
        border: 1px solid #00FF00;
        margin-left: auto;
        margin-right: 0;
        max-width: 80%;
    }
    
    [data-testid="stChatMessage"][data-chat-align="left"] {
        background-color: #1E1E1E;
        border: 1px solid #2A2A2A;
        margin-right: auto;
        margin-left: 0;
        max-width: 80%;
    }
    
    /* 连接状态呼吸灯 */
    .connection-status-dot {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        animation: breathing 2s ease-in-out infinite;
    }
    
    .connection-status-dot.connected {
        background-color: #00FF00;
        box-shadow: 0 0 10px #00FF00, 0 0 20px #00FF00, 0 0 30px #00FF00;
        animation: breathing-green 2s ease-in-out infinite;
    }
    
    .connection-status-dot.disconnected {
        background-color: #FF0000;
        box-shadow: 0 0 10px #FF0000, 0 0 20px #FF0000, 0 0 30px #FF0000;
        animation: breathing-red 2s ease-in-out infinite;
    }
    
    @keyframes breathing-green {
        0%, 100% { opacity: 1; box-shadow: 0 0 10px #00FF00, 0 0 20px #00FF00, 0 0 30px #00FF00; }
        50% { opacity: 0.6; box-shadow: 0 0 5px #00FF00, 0 0 10px #00FF00, 0 0 15px #00FF00; }
    }
    
    @keyframes breathing-red {
        0%, 100% { opacity: 1; box-shadow: 0 0 10px #FF0000, 0 0 20px #FF0000, 0 0 30px #FF0000; }
        50% { opacity: 0.6; box-shadow: 0 0 5px #FF0000, 0 0 10px #FF0000, 0 0 15px #FF0000; }
    }
    
    /* 终端字符跳动动画 */
    .typing-effect {
        display: inline-block;
        overflow: hidden;
        border-right: 2px solid #00FF00;
        white-space: nowrap;
        animation: typing-blink 0.75s step-end infinite;
    }
    
    @keyframes typing-blink {
        50% { border-color: transparent; }
    }
    
    .command-feedback {
        font-family: 'Consolas', 'Monaco', 'Source Code Pro', monospace;
        color: #00FF00;
        font-size: 0.9rem;
        line-height: 1.8;
        position: relative;
        overflow: hidden;
    }
    
    .command-feedback::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 255, 0, 0.1), transparent);
        animation: scan-line 2s linear infinite;
    }
    
    @keyframes scan-line {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    /* 内嵌式工具卡片 */
    .tool-card {
        background-color: #1A1A1A;
        border: 1px solid #333333;
        border-radius: 8px;
        margin: 1rem 0;
        overflow: hidden;
    }
    
    .tool-card-header {
        background-color: #2A2A2A;
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #333333;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .tool-card-title {
        color: #FFB300;
        font-weight: 700;
        font-size: 0.9rem;
        letter-spacing: 0.5px;
    }
    
    .tool-card-body {
        padding: 1rem;
    }
    
    .tool-card-actions {
        display: flex;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }
    
    .tool-card-actions button {
        flex: 1;
        font-size: 0.8rem;
        padding: 0.5rem 1rem !important;
    }
    
    /* JSON 代码块样式 */
    .json-code {
        background-color: #000000;
        border: 1px solid #333333;
        border-radius: 4px;
        padding: 1rem;
        font-family: 'Consolas', 'Monaco', 'Source Code Pro', monospace;
        font-size: 0.85rem;
        color: #00FF00;
        overflow-x: auto;
        margin: 0.5rem 0;
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
    
    /* 自动滚动容器 */
    .chat-container {
        max-height: 70vh;
        overflow-y: auto;
        padding: 1rem 0;
    }
    
    /* 分隔线 */
    hr {
        border: 0;
        border-top: 1px solid #333333;
        margin: 1.5rem 0;
    }
    
    /* 信息提示 */
    .stAlert {
        background-color: #1E1E1E;
        border: 1px solid #333333;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

# 应用 MA3 主题
apply_ma3_theme()

# 自定义 MA3 终端渲染函数
def render_ma3_terminal(commands: list, confirm_key: str = "confirm"):
    """
    渲染 MA3 终端界面
    
    Args:
        commands: OSC 命令列表
        confirm_key: 确认按钮的 session_state key
    """
    # 创建终端容器
    st.markdown("""
    <div class="ma3-terminal">
    """, unsafe_allow_html=True)
    
    # 显示每条命令（带字符跳动动画）
    for i, cmd in enumerate(commands, 1):
        st.markdown(f'<div class="command-feedback"><span class="typing-effect">{i}. {cmd}</span></div>', unsafe_allow_html=True)
    
    # 关闭终端容器
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 显示确认按钮
    if st.button("CONFIRM", key=confirm_key, use_container_width=True, type="primary"):
        return True
    return False

# 自动滚动到底部函数
def auto_scroll_to_bottom():
    """自动滚动到页面底部"""
    js_code = """
    <script>
        window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)

# 构建 OSC 命令列表
def build_osc_command(command) -> list:
    """
    构建 OSC 指令列表
    
    根据 GMA3Command 对象构建最终的 OSC 指令列表。
    严格遵守 grandMA3 OSC 核心语法指南。
    
    Args:
        command: GMA3Command 对象
        
    Returns:
        list: OSC 指令列表
    """
    # 1. 先发送 ClearAll（归位与清空）
    commands = ["ClearAll"]
    
    # 2. 遍历 actions 列表
    for action in command.actions:
        parts = []
        
        # 3. 灯具 ID
        if action.fixture_ids:
            if len(action.fixture_ids) == 1:
                parts.append(f"Fixture {action.fixture_ids[0]}")
            else:
                fixture_ids_str = " + ".join(str(fid) for fid in action.fixture_ids)
                parts.append(f"Fixture {fixture_ids_str}")
        
        # 4. 属性
        if action.attributes:
            attr_parts = []
            
            # Dimmer
            if "Dimmer" in action.attributes:
                dimmer_value = action.attributes["Dimmer"]
                attr_parts.append(f"At {dimmer_value}")
            
            # Color
            if "Color" in action.attributes:
                color_name = action.attributes["Color"]
                attr_parts.append(f'At Preset "Color"."{color_name}"')
            
            # RGB 兼容
            color_attrs = {}
            for attr, value in action.attributes.items():
                if attr.startswith("ColorRGB_"):
                    color_attrs[attr] = value
            
            if color_attrs:
                color_name = rgb_to_color_name(color_attrs)
                if color_name:
                    attr_parts.append(f'At Preset "Color"."{color_name}"')
            
            if attr_parts:
                parts.append(" ".join(attr_parts))
        
        # 5. 合并命令
        if parts:
            commands.append(" ".join(parts))
    
    return commands

# RGB 转颜色名称
def rgb_to_color_name(rgb_attrs: dict) -> str:
    """将 RGB 属性转换为颜色名称"""
    r = rgb_attrs.get("ColorRGB_R", 0)
    g = rgb_attrs.get("ColorRGB_G", 0)
    b = rgb_attrs.get("ColorRGB_B", 0)
    
    color_map = {
        (255, 0, 0): "Red",
        (0, 255, 0): "Green",
        (0, 0, 255): "Blue",
        (128, 0, 128): "Purple",
        (255, 255, 0): "Yellow",
        (255, 255, 255): "White",
        (0, 100, 200): "SadBlue",
    }
    
    for (cr, cg, cb), name in color_map.items():
        if r == cr and g == cg and b == cb:
            return name
    
    return "White"

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
if "conv_manager" not in st.session_state:
    st.session_state.conv_manager = ConversationManager()
if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None
if "conversation_list" not in st.session_state:
    st.session_state.conversation_list = []
# 新增：功能开关
if "show_thinking" not in st.session_state:
    st.session_state.show_thinking = True  # 是否显示解析思路
if "auto_send" not in st.session_state:
    st.session_state.auto_send = False  # 是否自动发送

# 初始化对话
if not st.session_state.current_conversation_id:
    st.session_state.conversation_list = list_conversations(limit=50)
    if st.session_state.conversation_list:
        st.session_state.current_conversation_id = st.session_state.conversation_list[0]["id"]
    else:
        st.session_state.current_conversation_id = st.session_state.conv_manager.create_conversation("新对话")
        st.session_state.conversation_list = list_conversations(limit=50)

# 侧边栏
with st.sidebar:
    st.title("🎭 MA3 OSC 助手")
    st.divider()
    
    # 🔌 OSC 配置折叠面板
    with st.expander("🔌 OSC 配置", expanded=False):
        st.text_input("OSC Host", value="127.0.0.1", key="osc_host")
        st.number_input("OSC Port", value=8000, min_value=1, max_value=65535, key="osc_port")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 连接", use_container_width=True):
                with st.spinner("正在连接..."):
                    try:
                        client = create_gma3_client(
                            host=st.session_state.osc_host,
                            port=st.session_state.osc_port
                        )
                        st.session_state.osc_client = client
                        
                        success, message = client.send_command(["ClearAll"])
                        
                        if success:
                            st.session_state.connection_status = "已连接"
                            st.success("✅ 连接成功！")
                        else:
                            st.session_state.connection_status = "未连接"
                            st.error(f"❌ 连接失败：{message}")
                            
                    except Exception as e:
                        st.session_state.connection_status = "未连接"
                        st.error(f"❌ 连接错误：{e}")
        
        with col2:
            if st.button("❌ 断开", use_container_width=True):
                if st.session_state.osc_client:
                    try:
                        st.session_state.osc_client.disconnect()
                        st.session_state.osc_client = None
                        st.session_state.connection_status = "未连接"
                        st.info("❌ 已断开连接")
                    except Exception as e:
                        st.error(f"❌ 断开错误：{e}")
        
        # 显示连接状态（带呼吸灯效果）
        status_dot_class = "connected" if st.session_state.connection_status == "已连接" else "disconnected"
        status_color = "#00FF00" if st.session_state.connection_status == "已连接" else "#FF0000"
        status_text = "✅ 已连接" if st.session_state.connection_status == "已连接" else "❌ 未连接"
        
        st.markdown(f'''
        <div style="display: flex; align-items: center; margin-top: 0.5rem;">
            <span class="connection-status-dot {status_dot_class}"></span>
            <span style="color: {status_color}; font-weight: 600;">{status_text}</span>
        </div>
        ''', unsafe_allow_html=True)
    
    st.divider()
    
    # 🤖 API 配置折叠面板
    with st.expander("🤖 API 配置", expanded=False):
        cached_api_key = get_cached_api_key("api_key")
        cached_api_base_url = get_cached_api_key("api_base_url")
        cached_model_id = get_cached_api_key("model_id")
        
        api_key = st.text_input("API Key", type="password", value=cached_api_key, key="api_key_input")
        api_base_url = st.text_input("API Base URL", value=cached_api_base_url, key="api_base_url_input")
        model_id = st.text_input("Model ID", value=cached_model_id, key="model_id_input")
        
        if cached_api_key or cached_api_base_url or cached_model_id:
            st.success("✅ 已加载缓存的 API 配置")
        
        if api_key and api_base_url and model_id:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 保存 API 配置", use_container_width=True):
                    save_api_key("api_key", api_key)
                    save_api_key("api_base_url", api_base_url)
                    save_api_key("model_id", model_id)
                    st.success("✅ API 配置已缓存")
            
            with col2:
                if st.button("🗑️ 清除缓存", use_container_width=True):
                    clear_all_api_keys()
                    st.rerun()
        
        if st.button("🔌 测试 API", use_container_width=True):
            test_api_key = api_key if api_key else get_cached_api_key("api_key")
            test_api_base_url = api_base_url if api_base_url else get_cached_api_key("api_base_url")
            test_model_id = model_id if model_id else get_cached_api_key("model_id")
            
            if test_api_key and test_api_base_url and test_model_id:
                with st.spinner("正在测试 API..."):
                    try:
                        translator = create_translator(
                            api_key=test_api_key,
                            base_url=test_api_base_url,
                            model_id=test_model_id
                        )
                        st.session_state.translator = translator
                        st.session_state.api_status = "已连接"
                        st.success("✅ API 连接成功！")
                    except Exception as e:
                        st.session_state.translator = None
                        st.session_state.api_status = "未连接"
                        st.error(f"❌ API 连接失败：{e}")
            else:
                st.error("❌ 请先配置 API 信息")
        
        st.info(f"🤖 状态：{st.session_state.api_status}")
    
    st.divider()
    
    # 💬 对话管理折叠面板
    with st.expander("💬 对话管理", expanded=False):
        if st.button("➕ 新建对话", use_container_width=True):
            new_id = st.session_state.conv_manager.create_conversation("新对话")
            st.session_state.current_conversation_id = new_id
            st.session_state.conversation_list = list_conversations(limit=50)
            st.rerun()
        
        # 批量删除功能
        st.subheader("批量操作")
        deleted_ids = st.session_state.get("deleted_conversations", [])
        
        # 显示已删除的对话
        if deleted_ids:
            st.info(f"🗑️ 已删除 {len(deleted_ids)} 条对话记录")
            if st.button("🔄 清空删除记录", key="restore_deleted", use_container_width=True):
                st.session_state["deleted_conversations"] = []
                st.rerun()
        
        # 删除所有非当前对话
        if st.button("🗑️ 删除所有历史对话", use_container_width=True, type="secondary"):
            current_id = st.session_state.current_conversation_id
            all_convs = list_conversations(limit=100)
            deleted_list = []
            for conv in all_convs:
                if conv["id"] != current_id:
                    st.session_state.conv_manager.delete_conversation(conv["id"])
                    deleted_list.append(conv["id"])
            st.session_state.conversation_list = list_conversations(limit=50)
            st.session_state["deleted_conversations"] = deleted_list
            st.session_state["selected_conversations"] = []
            st.rerun()
        
        st.divider()
        st.subheader("对话列表")
        
        # 多选框实现批量删除
        selected_conv_ids = st.session_state.get("selected_conversations", [])
        
        # 更新对话列表
        st.session_state.conversation_list = list_conversations(limit=50)
        
        for conv in st.session_state.conversation_list:
            is_current = conv["id"] == st.session_state.current_conversation_id
            
            # 多选框
            checkbox_key = f"chk_{conv['id']}"
            is_selected = conv["id"] in selected_conv_ids
            
            col1, col2, col3 = st.columns([0.3, 4, 1])
            with col1:
                # 添加 label 避免空标签警告
                st.checkbox(
                    "select",
                    key=checkbox_key,
                    value=is_selected,
                    label_visibility="collapsed"
                )
            with col2:
                if st.button(
                    f"{'✅ ' if is_current else ''}{conv['title'][:20]}...",
                    key=f"conv_{conv['id']}",
                    use_container_width=True
                ):
                    st.session_state.current_conversation_id = conv["id"]
                    st.rerun()
            with col3:
                if st.button("🗑️", key=f"del_{conv['id']}", use_container_width=True):
                    if conv["id"] != st.session_state.current_conversation_id:
                        st.session_state.conv_manager.delete_conversation(conv["id"])
                        # 从选中列表中移除
                        if conv["id"] in selected_conv_ids:
                            selected_conv_ids.remove(conv["id"])
                        st.session_state["selected_conversations"] = selected_conv_ids
                        st.session_state.conversation_list = list_conversations(limit=50)
                        st.rerun()
                    else:
                        st.error("❌ 不能删除当前对话")
        
        # 批量删除按钮
        selected_conv_ids = st.session_state.get("selected_conversations", [])
        if selected_conv_ids:
            if st.button(f"🗑️ 删除选中的 {len(selected_conv_ids)} 条对话", use_container_width=True, type="secondary"):
                deleted_list = []
                for conv_id in selected_conv_ids:
                    if conv_id != st.session_state.current_conversation_id:
                        st.session_state.conv_manager.delete_conversation(conv_id)
                        deleted_list.append(conv_id)
                st.session_state.conversation_list = list_conversations(limit=50)
                st.session_state["deleted_conversations"] = st.session_state.get("deleted_conversations", []) + deleted_list
                st.session_state["selected_conversations"] = []
                st.rerun()
        
        # 保存选中的对话 ID
        st.session_state["selected_conversations"] = selected_conv_ids
    
    st.divider()
    
    # 🐛 Debug 和 功能开关
    with st.expander("🐛 Debug 和功能开关", expanded=False):
        # 显示解析思路开关
        st.checkbox(
            "🧠 显示解析思路",
            value=st.session_state.show_thinking,
            key="show_thinking",
            help="控制是否在 AI 回复中显示解析思路"
        )
        
        # 自动发送开关
        st.checkbox(
            "🚀 自动发送 OSC 命令",
            value=st.session_state.auto_send,
            key="auto_send",
            help="开启后点击 CONFIRM 按钮会自动发送 OSC 命令，关闭后需要手动确认"
        )
        
        st.divider()
        
        # Debug 选项
        debug_enabled = st.checkbox("🔍 显示原始 JSON", value=st.session_state.get("debug_enabled", False), key="debug_enabled")
    
    st.divider()
    
    # 📖 使用说明
    with st.expander("📖 使用说明", expanded=False):
        st.markdown("""
        **自然语言输入示例：**
        - "1 号灯变黄"
        - "把 101 到 105 号灯亮度调到 50%"
        - "清空所有选中"
        
        **操作流程：**
        1. 配置 OSC 连接
        2. 配置 API（可选）
        3. 输入自然语言指令
        4. 点击"CONFIRM"按钮
        """)

# 主界面
st.title("🎭 MA3 OSC 语义编程助手")
st.divider()

# 显示对话历史
chat_container = st.container()
with chat_container:
    if st.session_state.current_conversation_id:
        messages = st.session_state.conv_manager.get_messages(st.session_state.current_conversation_id)
        
        if messages:
            for msg in messages:
                role = "user" if msg["role"] == "user" else "assistant"
                align = "right" if role == "user" else "left"
                
                # 使用 HTML 实现聊天气泡对齐
                st.markdown(f'''
                <div style="margin-bottom: 1rem;">
                    <div style="background-color: {'#2A4A2A' if role == 'user' else '#1E1E1E'}; border: 1px solid {'#00FF00' if role == 'user' else '#2A2A2A'}; border-radius: 12px; padding: 1rem; max-width: 80%; {'margin-left: auto; margin-right: 0;' if role == 'user' else 'margin-right: auto; margin-left: 0;'};">
                        <div style="color: #CCCCCC; font-size: 0.95rem;">{msg['content']}</div>
                        {f'<div style="color: #666666; font-size: 0.8rem; margin-top: 0.5rem;">⏰ {msg["timestamp"]}</div>' if msg.get('timestamp') else ''}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("💬 暂无对话记录。开始输入指令吧！")
    else:
        st.info("💬 请先创建或选择对话")

# 自动滚动到底部
auto_scroll_to_bottom()

# 输入框（固定在底部）
user_input = st.chat_input("输入自然语言指令...")

if user_input:
    # 保存用户输入
    add_message(st.session_state.current_conversation_id, "user", user_input)
    
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # AI 解析
    if st.session_state.translator:
        with st.chat_message("assistant"):
            with st.spinner("🤖 AI 正在解析指令..."):
                try:
                    result = st.session_state.translator.translate(user_input)
                    
                    if not result.success:
                        # 保存错误
                        add_message(st.session_state.current_conversation_id, "assistant", f"❌ 解析失败：{result.error}")
                        st.markdown(f"❌ 解析失败：{result.error}")
                    else:
                        # 显示解析思路（根据开关控制）
                        if st.session_state.show_thinking:
                            st.markdown(f'<div class="thinking-process"><div class="thinking-title">🧠 解析思路</div>{result.command.explanation}</div>', unsafe_allow_html=True)
                        
                        # 构建 OSC 命令
                        osc_commands = build_osc_command(result.command)
                        
                        # 显示 MA3 终端
                        st.markdown("```")
                        render_ma3_terminal(osc_commands, confirm_key=f"confirm_{len(st.session_state.command_history)}")
                        st.markdown("```")
                        
                        # 显示原始 JSON（如果开启 Debug）
                        if st.session_state.debug_enabled:
                            with st.expander("🔍 查看原始 JSON"):
                                st.json(result.command.model_dump())
                        
                        # 保存 AI 响应
                        response_content = f"✅ 解析成功：{result.command.explanation}\n\n```OSC 命令:\n" + "\n".join(f"{i+1}. {cmd}" for i, cmd in enumerate(osc_commands)) + "\n```"
                        add_message(st.session_state.current_conversation_id, "assistant", response_content)
                        
                        # 检查确认按钮
                        confirm_key = f"confirm_{len(st.session_state.command_history)}"
                        if st.session_state.get(confirm_key, False):
                            # 如果开启自动发送，直接发送；否则显示提示
                            if st.session_state.auto_send:
                                # 发送 OSC 命令
                                with st.spinner("📡 正在发送 OSC 命令..."):
                                    if st.session_state.osc_client:
                                        print(f"DEBUG: 开始发送命令，osc_commands={osc_commands}")
                                        
                                        success, message = st.session_state.osc_client.send_command(osc_commands)
                                        
                                        print(f"DEBUG: 发送完成，success={success}, message={message}")
                                        
                                        if success:
                                            st.success(f"✅ 执行成功：{message}")
                                            st.session_state.command_history.append({
                                                "input": user_input,
                                                "parsed": result.command.model_dump(),
                                                "osc_commands": osc_commands,
                                                "status": "成功",
                                                "error": None
                                            })
                                        else:
                                            st.error(f"❌ 执行失败：{message}")
                                            st.session_state.command_history.append({
                                                "input": user_input,
                                                "parsed": result.command.model_dump(),
                                                "osc_commands": osc_commands,
                                                "status": "失败",
                                                "error": message
                                            })
                                    else:
                                        st.error("❌ OSC 客户端未初始化")
                            else:
                                # 关闭自动发送模式，显示提示
                                st.info("💡 已关闭自动发送。请手动点击 CONFIRM 按钮执行命令。")
                                        
                except Exception as e:
                    st.error(f"❌ 解析错误：{e}")
                    print(f"DEBUG: 解析错误 - {e}")
                    import traceback
                    traceback.print_exc()
    else:
        st.markdown("<div style='color: #FFA500;'>⚠️ 请先配置并连接 API</div>", unsafe_allow_html=True)

# 自动连接和测试（页面加载时）
if "auto_connected" not in st.session_state:
    st.session_state.auto_connected = False

if not st.session_state.auto_connected:
    with st.sidebar:
        if st.session_state.connection_status == "未连接" and st.session_state.osc_host == "127.0.0.1" and st.session_state.osc_port == 8000:
            with st.spinner("🔄 自动连接 MA3..."):
                try:
                    client = create_gma3_client(host="127.0.0.1", port=8000)
                    success, message = client.send_command(["ClearAll"])
                    
                    if success:
                        st.session_state.osc_client = client
                        st.session_state.connection_status = "已连接"
                        st.session_state.auto_connected = True
                        st.success("✅ 已自动连接 MA3")
                except:
                    pass
        
        if not st.session_state.translator:
            cached_key = get_cached_api_key("api_key")
            cached_url = get_cached_api_key("api_base_url")
            cached_model = get_cached_api_key("model_id")
            
            if cached_key and cached_url and cached_model:
                with st.spinner("🔄 测试 API..."):
                    try:
                        translator = create_translator(
                            api_key=cached_key,
                            base_url=cached_url,
                            model_id=cached_model
                        )
                        st.session_state.translator = translator
                        st.session_state.api_status = "已连接"
                        st.session_state.auto_connected = True
                        st.success("✅ 已连接 API")
                    except:
                        pass
