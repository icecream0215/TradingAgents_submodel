"""
Token定价配置组件
允许用户配置不同LLM服务的token价格
"""

import streamlit as st
import json
from pathlib import Path
from typing import Dict, Any

def render_pricing_config_sidebar():
    """在侧边栏渲染价格配置"""
    
    with st.sidebar:
        st.markdown("---")
        with st.expander("💰 Token价格配置", expanded=True):
            render_pricing_config()

def render_pricing_config():
    """渲染价格配置界面"""
    
    st.markdown("### 💰 LLM Token价格配置")
    st.markdown("*配置不同LLM服务的输入/输出token价格（每1000个token的价格）*")
    
    # 加载当前配置
    current_pricing = load_pricing_config()
    
    # 创建配置表单
    with st.form("pricing_config_form"):
        st.markdown("#### 常用LLM服务价格")
        
        # DeepSeek配置
        st.markdown("**🤖 DeepSeek**")
        col1, col2 = st.columns(2)
        with col1:
            deepseek_input_price = st.number_input(
                "输入价格 (¥/1K tokens)",
                value=current_pricing.get("deepseek", {}).get("input_price", 0.0014),
                min_value=0.0,
                max_value=1.0,
                step=0.0001,
                format="%.4f",
                key="deepseek_input"
            )
        with col2:
            deepseek_output_price = st.number_input(
                "输出价格 (¥/1K tokens)",
                value=current_pricing.get("deepseek", {}).get("output_price", 0.0028),
                min_value=0.0,
                max_value=1.0,
                step=0.0001,
                format="%.4f",
                key="deepseek_output"
            )
        
        # 阿里百炼配置
        st.markdown("**🇨🇳 阿里百炼 (DashScope)**")
        col3, col4 = st.columns(2)
        with col3:
            dashscope_input_price = st.number_input(
                "输入价格 (¥/1K tokens)",
                value=current_pricing.get("dashscope", {}).get("input_price", 0.0005),
                min_value=0.0,
                max_value=1.0,
                step=0.0001,
                format="%.4f",
                key="dashscope_input"
            )
        with col4:
            dashscope_output_price = st.number_input(
                "输出价格 (¥/1K tokens)",
                value=current_pricing.get("dashscope", {}).get("output_price", 0.002),
                min_value=0.0,
                max_value=1.0,
                step=0.0001,
                format="%.4f",
                key="dashscope_output"
            )
        
        # OpenAI配置
        st.markdown("**🌍 OpenAI**")
        col5, col6 = st.columns(2)
        with col5:
            openai_input_price = st.number_input(
                "输入价格 (¥/1K tokens)",
                value=current_pricing.get("openai", {}).get("input_price", 0.07),
                min_value=0.0,
                max_value=1.0,
                step=0.001,
                format="%.3f",
                key="openai_input"
            )
        with col6:
            openai_output_price = st.number_input(
                "输出价格 (¥/1K tokens)",
                value=current_pricing.get("openai", {}).get("output_price", 0.14),
                min_value=0.0,
                max_value=1.0,
                step=0.001,
                format="%.3f",
                key="openai_output"
            )
        
        # Google配置
        st.markdown("**🔍 Google Gemini**")
        col7, col8 = st.columns(2)
        with col7:
            google_input_price = st.number_input(
                "输入价格 (¥/1K tokens)",
                value=current_pricing.get("google", {}).get("input_price", 0.035),
                min_value=0.0,
                max_value=1.0,
                step=0.001,
                format="%.3f",
                key="google_input"
            )
        with col8:
            google_output_price = st.number_input(
                "输出价格 (¥/1K tokens)",
                value=current_pricing.get("google", {}).get("output_price", 0.105),
                min_value=0.0,
                max_value=1.0,
                step=0.001,
                format="%.3f",
                key="google_output"
            )
        
        # 保存按钮
        if st.form_submit_button("💾 保存价格配置", type="primary"):
            new_pricing = {
                "deepseek": {
                    "input_price": deepseek_input_price,
                    "output_price": deepseek_output_price
                },
                "dashscope": {
                    "input_price": dashscope_input_price,
                    "output_price": dashscope_output_price
                },
                "openai": {
                    "input_price": openai_input_price,
                    "output_price": openai_output_price
                },
                "google": {
                    "input_price": google_input_price,
                    "output_price": google_output_price
                }
            }
            
            if save_pricing_config(new_pricing):
                st.success("✅ 价格配置已保存")
                st.rerun()
            else:
                st.error("❌ 保存失败，请检查权限")

def load_pricing_config() -> Dict[str, Any]:
    """加载价格配置"""
    config_file = Path("config/pricing_config.json")
    
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.warning(f"⚠️ 加载价格配置失败: {e}")
    
    # 返回默认配置
    return {
        "deepseek": {"input_price": 0.0014, "output_price": 0.0028},
        "dashscope": {"input_price": 0.0005, "output_price": 0.002},
        "openai": {"input_price": 0.07, "output_price": 0.14},
        "google": {"input_price": 0.035, "output_price": 0.105}
    }

def save_pricing_config(pricing_config: Dict[str, Any]) -> bool:
    """保存价格配置"""
    config_file = Path("config/pricing_config.json")
    
    try:
        # 确保配置目录存在
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(pricing_config, f, ensure_ascii=False, indent=2)
        
        # 同时更新系统的pricing.json文件
        update_system_pricing_config(pricing_config)
        
        return True
    except Exception as e:
        st.error(f"❌ 保存配置失败: {e}")
        return False

def update_system_pricing_config(pricing_config: Dict[str, Any]):
    """更新系统的pricing.json配置文件"""
    try:
        from tradingagents.config.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        
        # 构建系统格式的价格配置
        system_pricing = []
        
        for provider, prices in pricing_config.items():
            # 根据provider映射模型名称
            model_names = {
                "deepseek": ["deepseek-chat", "deepseek-coder"],
                "dashscope": ["qwen-turbo", "qwen-plus", "qwen-max"],
                "openai": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
                "google": ["gemini-pro", "gemini-1.5-pro"]
            }
            
            for model_name in model_names.get(provider, [provider]):
                system_pricing.append({
                    "provider": provider,
                    "model_name": model_name,
                    "input_price_per_1k": prices["input_price"],
                    "output_price_per_1k": prices["output_price"],
                    "currency": "CNY"
                })
        
        # 保存到系统配置
        config_manager.save_pricing(system_pricing)
        
    except Exception as e:
        st.warning(f"⚠️ 更新系统配置失败: {e}")

def get_provider_price(provider: str, token_type: str) -> float:
    """获取指定provider的价格"""
    pricing_config = load_pricing_config()
    return pricing_config.get(provider, {}).get(f"{token_type}_price", 0.0)