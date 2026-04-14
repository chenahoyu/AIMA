#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版 Streamlit 应用 - 直接测试 OSC 发送
"""

import streamlit as st
from src.osc.osc_client import create_gma3_client

st.set_page_config(page_title="MA3 OSC 测试", layout="wide")

st.title("🎭 MA3 OSC 简化测试")

# 初始化会话状态
if "osc_client" not in st.session_state:
    st.session_state.osc_client = None
if "connection_status" not in st.session_state:
    st.session_state.connection_status = "未连接"

# 侧边栏
with st.sidebar:
    st.header("🔌 连接控制")
    
    host = st.text_input("OSC Host", value="127.0.0.1")
    port = st.number_input("OSC Port", value=8000, min_value=1, max_value=65535)
    
    if st.button("🔄 连接"):
        with st.spinner("正在连接..."):
            try:
                client = create_gma3_client(host=host, port=port)
                st.session_state.osc_client = client
                
                # 测试连接
                success, message = client.send_command(["ClearAll"])
                
                if success:
                    st.session_state.connection_status = "已连接"
                    st.success("✅ 连接成功！")
                    print(f"DEBUG: 连接成功 - {message}")
                else:
                    st.session_state.connection_status = "未连接"
                    st.error(f"❌ 连接失败：{message}")
                    print(f"DEBUG: 连接失败 - {message}")
                    
            except Exception as e:
                st.session_state.connection_status = "未连接"
                st.error(f"❌ 连接错误：{e}")
                print(f"DEBUG: 连接错误 - {e}")
    
    st.info(f"状态：{st.session_state.connection_status}")

# 主界面
st.subheader("📤 发送测试命令")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("ClearAll", use_container_width=True):
        if st.session_state.osc_client:
            with st.spinner("发送中..."):
                success, message = st.session_state.osc_client.send_command("ClearAll")
                if success:
                    st.success(f"✅ {message}")
                    print(f"DEBUG: ClearAll 发送成功 - {message}")
                else:
                    st.error(f"❌ {message}")
                    print(f"DEBUG: ClearAll 发送失败 - {message}")
        else:
            st.error("❌ 请先连接")

with col2:
    if st.button("Fixture 1 At 100", use_container_width=True):
        if st.session_state.osc_client:
            with st.spinner("发送中..."):
                success, message = st.session_state.osc_client.send_command("Fixture 1 At 100")
                if success:
                    st.success(f"✅ {message}")
                    print(f"DEBUG: Fixture 1 At 100 发送成功 - {message}")
                else:
                    st.error(f"❌ {message}")
                    print(f"DEBUG: Fixture 1 At 100 发送失败 - {message}")
        else:
            st.error("❌ 请先连接")

with col3:
    if st.button('Fixture 1 At Preset "Color"."Yellow"', use_container_width=True):
        if st.session_state.osc_client:
            with st.spinner("发送中..."):
                success, message = st.session_state.osc_client.send_command('Fixture 1 At Preset "Color"."Yellow"')
                if success:
                    st.success(f"✅ {message}")
                    print(f"DEBUG: Fixture 1 Yellow 发送成功 - {message}")
                else:
                    st.error(f"❌ {message}")
                    print(f"DEBUG: Fixture 1 Yellow 发送失败 - {message}")
        else:
            st.error("❌ 请先连接")

# 自定义命令
st.subheader("🔧 自定义命令")
custom_cmd = st.text_input("输入命令", value="ClearAll")

if st.button("📤 发送自定义命令"):
    if st.session_state.osc_client:
        with st.spinner("发送中..."):
            success, message = st.session_state.osc_client.send_command(custom_cmd)
            if success:
                st.success(f"✅ {message}")
                print(f"DEBUG: 自定义命令发送成功 - {message}")
            else:
                st.error(f"❌ {message}")
                print(f"DEBUG: 自定义命令发送失败 - {message}")
    else:
        st.error("❌ 请先连接")

# 显示客户端状态
st.subheader("📊 客户端状态")
if st.session_state.osc_client:
    st.json({
        "host": st.session_state.osc_client.host,
        "port": st.session_state.osc_client.port,
        "connected": st.session_state.osc_client.connected,
        "commands_sent": st.session_state.osc_client.stats["commands_sent"],
        "commands_failed": st.session_state.osc_client.stats["commands_failed"]
    })
else:
    st.warning("❌ 未连接")
