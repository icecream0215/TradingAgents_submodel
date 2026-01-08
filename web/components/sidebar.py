"""
侧边栏组件
"""

import streamlit as st
import os
import logging
import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from web.utils.persistence import load_model_selection, save_model_selection
from web.utils.model_fetcher import model_fetcher

logger = logging.getLogger(__name__)

def render_sidebar():
    """渲染侧边栏配置"""

    # 添加localStorage支持的JavaScript
    st.markdown("""
    <script>
    // 保存到localStorage
    function saveToLocalStorage(key, value) {
        localStorage.setItem('tradingagents_' + key, value);
        console.log('Saved to localStorage:', key, value);
    }

    // 从localStorage读取
    function loadFromLocalStorage(key, defaultValue) {
        const value = localStorage.getItem('tradingagents_' + key);
        console.log('Loaded from localStorage:', key, value || defaultValue);
        return value || defaultValue;
    }

    // 页面加载时恢复设置
    window.addEventListener('load', function() {
        console.log('Page loaded, restoring settings...');
    });
    </script>
    """, unsafe_allow_html=True)

    # 优化侧边栏样式
    st.markdown("""
    <style>
    /* 优化侧边栏宽度 - 调整为320px */
    section[data-testid="stSidebar"] {
        width: 320px !important;
        min-width: 320px !important;
        max-width: 320px !important;
    }

    /* 优化侧边栏内容容器 */
    section[data-testid="stSidebar"] > div {
        width: 320px !important;
        min-width: 320px !important;
        max-width: 320px !important;
    }

    /* 强制减少侧边栏内边距 - 多种选择器确保生效 */
    section[data-testid="stSidebar"] .block-container,
    section[data-testid="stSidebar"] > div > div,
    .css-1d391kg,
    .css-1lcbmhc,
    .css-1cypcdb {
        padding-top: 0.75rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        padding-bottom: 0.75rem !important;
    }

    /* 侧边栏内所有元素的边距控制 */
    section[data-testid="stSidebar"] * {
        box-sizing: border-box !important;
    }

    /* 优化selectbox容器 */
    section[data-testid="stSidebar"] .stSelectbox {
        margin-bottom: 0.4rem !important;
        width: 100% !important;
    }

    /* 优化selectbox下拉框 - 调整为适合320px */
    section[data-testid="stSidebar"] .stSelectbox > div > div,
    section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] {
        width: 100% !important;
        min-width: 260px !important;
        max-width: 280px !important;
    }

    /* 优化下拉框选项文本 */
    section[data-testid="stSidebar"] .stSelectbox label {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.2rem !important;
    }

    /* 优化文本输入框 */
    section[data-testid="stSidebar"] .stTextInput > div > div > input {
        font-size: 0.8rem !important;
        padding: 0.3rem 0.5rem !important;
        width: 100% !important;
    }

    /* 优化按钮样式 */
    section[data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        font-size: 0.8rem !important;
        padding: 0.3rem 0.5rem !important;
        margin: 0.1rem 0 !important;
        border-radius: 0.3rem !important;
    }

    /* 优化标题样式 */
    section[data-testid="stSidebar"] h3 {
        font-size: 1rem !important;
        margin-bottom: 0.5rem !important;
        margin-top: 0.3rem !important;
        padding: 0 !important;
    }

    /* 优化info框样式 */
    section[data-testid="stSidebar"] .stAlert {
        padding: 0.4rem !important;
        margin: 0.3rem 0 !important;
        font-size: 0.75rem !important;
    }

    /* 优化文本 */
    section[data-testid="stSidebar"] .stMarkdown {
        margin-bottom: 0.3rem !important;
        padding: 0 !important;
    }

    /* 优化分隔线 */
    section[data-testid="stSidebar"] hr {
        margin: 0.75rem 0 !important;
    }

    /* 确保下拉框选项完全可见 - 调整为适合320px */
    .stSelectbox [data-baseweb="select"] {
        min-width: 260px !important;
        max-width: 280px !important;
    }

    /* 优化下拉框选项列表 */
    .stSelectbox [role="listbox"] {
        min-width: 260px !important;
        max-width: 290px !important;
    }

    /* 额外的边距控制 - 确保左右边距减小 */
    .sidebar .element-container {
        padding: 0 !important;
        margin: 0.2rem 0 !important;
    }

    /* 强制覆盖默认样式 */
    .css-1d391kg .element-container {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        # 使用组件来从localStorage读取并初始化session state
        st.markdown("""
        <div id="localStorage-reader" style="display: none;">
            <script>
            // 从localStorage读取设置并发送给Streamlit
            const provider = loadFromLocalStorage('llm_provider', 'dashscope');
            const category = loadFromLocalStorage('model_category', 'openai');
            const model = loadFromLocalStorage('llm_model', '');

            // 通过自定义事件发送数据
            window.parent.postMessage({
                type: 'localStorage_data',
                provider: provider,
                category: category,
                model: model
            }, '*');
            </script>
        </div>
        """, unsafe_allow_html=True)

        # 从持久化存储加载配置
        saved_config = load_model_selection()

        # 初始化session state，优先使用保存的配置
        if 'llm_provider' not in st.session_state:
            st.session_state.llm_provider = saved_config['provider']
            logger.debug(f"🔧 [Persistence] 恢复 llm_provider: {st.session_state.llm_provider}")
        if 'model_category' not in st.session_state:
            st.session_state.model_category = saved_config['category']
            logger.debug(f"🔧 [Persistence] 恢复 model_category: {st.session_state.model_category}")
        if 'llm_model' not in st.session_state:
            st.session_state.llm_model = saved_config['model']
            logger.debug(f"🔧 [Persistence] 恢复 llm_model: {st.session_state.llm_model}")

        # 显示当前session state状态（调试用）
        logger.debug(f"🔍 [Session State] 当前状态 - provider: {st.session_state.llm_provider}, category: {st.session_state.model_category}, model: {st.session_state.llm_model}")

        # AI模型配置（动态选择）
        st.markdown("### 🧠 AI模型配置")
        
        # 设置固定的提供商配置
        st.session_state.llm_provider = 'openai'
        st.session_state.model_category = 'openai'
        
        # 获取可用模型列表
        with st.spinner("正在获取可用模型..."):
            available_models = model_fetcher.get_available_models()
        
        if available_models:
            # 获取默认模型
            default_model = model_fetcher.get_default_model()
            
            # 如果session state中没有模型或模型不在可用列表中，使用默认模型
            if 'llm_model' not in st.session_state or st.session_state.llm_model not in available_models:
                st.session_state.llm_model = default_model
            
            # 模型选择器
            col1, col2 = st.columns([4, 1])
            
            with col1:
                selected_model = st.selectbox(
                    "🚀 选择AI模型",
                    options=available_models,
                    index=available_models.index(st.session_state.llm_model) if st.session_state.llm_model in available_models else 0,
                    key="model_selector",
                    help="从可用模型列表中选择要使用的AI模型"
                )
                
                # 更新session state
                if selected_model != st.session_state.llm_model:
                    st.session_state.llm_model = selected_model
                    logger.info(f"🔄 用户切换模型到: {selected_model}")
                    # 保存配置
                    save_model_selection(st.session_state.llm_provider, st.session_state.model_category, st.session_state.llm_model)
            
            with col2:
                if st.button("🔄", help="刷新模型列表"):
                    model_fetcher.refresh_models()
                    st.rerun()
            
            # 显示当前模型信息
            st.success(f"✅ **当前模型**: {st.session_state.llm_model}")
            
            with st.expander("📋 模型配置详情", expanded=False):
                st.markdown(f"""
                **当前模型配置：**
                - 🎯 **提供商**：第三方OpenAI兼容服务
                - 🚀 **模型**：{st.session_state.llm_model}
                - 🌐 **API端点**：https://llm.submodel.ai/v1
                - 📊 **可用模型数**：{len(available_models)}
                - 💰 **特点**：高性价比，响应快速，多模型选择
                """)
            
            # Token价格配置
            render_token_pricing_config()
        else:
            # 如果获取模型列表失败，回退到固定配置
            st.warning("⚠️ 无法获取模型列表，使用默认配置")
            st.session_state.llm_model = 'deepseek-ai/DeepSeek-V3.1'
            st.info(f"🚀 **默认模型**: {st.session_state.llm_model}")
        
        # 检查API密钥配置状态
        import os
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and api_key.startswith('sk-'):
            # 安全地显示API密钥（处理SecretStr类型）
            if hasattr(api_key, 'get_secret_value'):
                key_display = api_key.get_secret_value()[:20] if api_key.get_secret_value() else 'None'
            else:
                key_display = str(api_key)[:20] if api_key else 'None'
            st.success(f"✅ API密钥已配置：{key_display}...")
        else:
            st.error("❌ 请在.env文件中配置OPENAI_API_KEY")
            st.code("OPENAI_API_KEY=sk-84erLIZj6ljBXra9BPC77mWqfNC7sxI2P7MhbVuiWcEKl4Rq")
        
        # 保存配置到持久化存储（为了兼容性）
        save_model_selection(st.session_state.llm_provider, st.session_state.model_category, st.session_state.llm_model)

        st.markdown("---")
        
        # 系统配置
        st.markdown("**🔧 系统配置**")

        # API密钥状态
        st.markdown("**🔑 API密钥状态**")

        def validate_api_key(key, expected_format):
            """验证API密钥格式"""
            if not key:
                return "未配置", "error"

            if expected_format == "openai" and key.startswith("sk-") and len(key) >= 40:
                return f"{key[:20]}...", "success"
            elif expected_format == "finnhub" and len(key) >= 20:
                return f"{key[:8]}...", "success"
            else:
                return f"{key[:8]}... (格式异常)", "warning"

        # 必需的API密钥
        st.markdown("*必需配置:*")

        # OpenAI API密钥 (用于DeepSeek)
        openai_key = os.getenv("OPENAI_API_KEY")
        status, level = validate_api_key(openai_key, "openai")
        if level == "success":
            st.success(f"✅ OpenAI API (DeepSeek): {status}")
        elif level == "warning":
            st.warning(f"⚠️ OpenAI API (DeepSeek): {status}")
        else:
            st.error("❌ OpenAI API (DeepSeek): 未配置")
            st.code("OPENAI_API_KEY=sk-84erLIZj6ljBXra9BPC77mWqfNC7sxI2P7MhbVuiWcEKl4Rq")

        # FinnHub
        finnhub_key = os.getenv("FINNHUB_API_KEY")
        status, level = validate_api_key(finnhub_key, "finnhub")
        if level == "success":
            st.success(f"✅ FinnHub: {status}")
        elif level == "warning":
            st.warning(f"⚠️ FinnHub: {status}")
        else:
            st.error("❌ FinnHub: 未配置")

        st.markdown("---")

        # 系统信息
        st.markdown("**ℹ️ 系统信息**")
        
        st.info(f"""
        **版本**: cn-0.1.13
        **框架**: Streamlit + LangGraph
        **AI模型**: {st.session_state.llm_provider.upper()} - {st.session_state.llm_model}
        **数据源**: Tushare + FinnHub API
        """)
        
        # 帮助链接
        st.markdown("**📚 帮助资源**")
        
        st.markdown("""
        - [📖 使用文档](https://github.com/TauricResearch/TradingAgents)
        - [🐛 问题反馈](https://github.com/TauricResearch/TradingAgents/issues)
        - [💬 讨论社区](https://github.com/TauricResearch/TradingAgents/discussions)
        - [🔧 API密钥配置](../docs/security/api_keys_security.md)
        """)
    
    # 确保返回session state中的值，而不是局部变量
    final_provider = st.session_state.llm_provider
    final_model = st.session_state.llm_model

    logger.debug(f"🔄 [Session State] 返回配置 - provider: {final_provider}, model: {final_model}")

    # 固定系统配置值
    enable_memory = False  # 简化配置，关闭记忆功能
    enable_debug = False   # 简化配置，关闭调试模式
    max_tokens = 4096      # 默认token限制
    
    return {
        'llm_provider': final_provider,
        'llm_model': final_model,
        'enable_memory': enable_memory,
        'enable_debug': enable_debug,
        'max_tokens': max_tokens
    }


def render_token_pricing_config():
    """渲染简化的Token价格配置"""
    
    st.markdown("**💰 Token价格配置**")
    
    # 加载当前配置
    pricing_config = load_token_pricing_config()
    
    # 创建配置表单
    with st.form("token_pricing_form"):
        st.markdown("*配置Token价格（每1000个token的价格，单位：¥）*")
        
        col1, col2 = st.columns(2)
        with col1:
            input_price = st.number_input(
                "输入价格 (¥/1K tokens)",
                value=pricing_config.get("input_price", 0.002),
                min_value=0.0,
                max_value=1.0,
                step=0.0001,
                format="%.4f",
                key="token_input_price"
            )
        with col2:
            output_price = st.number_input(
                "输出价格 (¥/1K tokens)",
                value=pricing_config.get("output_price", 0.004),
                min_value=0.0,
                max_value=1.0,
                step=0.0001,
                format="%.4f",
                key="token_output_price"
            )
        
        # 保存按钮
        if st.form_submit_button("💾 保存价格配置", type="primary"):
            new_pricing = {
                "input_price": input_price,
                "output_price": output_price
            }
            
            if save_token_pricing_config(new_pricing):
                st.success("✅ Token价格已保存")
                st.rerun()
            else:
                st.error("❌ 保存失败，请检查权限")


def load_token_pricing_config():
    """加载Token价格配置"""
    config_file = Path("config/pricing_config.json")
    
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 如果是旧格式，返回通用配置
                if isinstance(data, dict):
                    # 优先使用openai配置，然后dashscope，最后用默认值
                    for provider in ['openai', 'dashscope', 'deepseek']:
                        if provider in data:
                            return data[provider]
                    # 如果是新的简化格式
                    if 'input_price' in data and 'output_price' in data:
                        return data
        except Exception as e:
            st.warning(f"⚠️ 加载价格配置失败: {e}")
    
    # 返回默认配置
    return {"input_price": 0.002, "output_price": 0.004}


def save_token_pricing_config(pricing_config):
    """保存Token价格配置"""
    config_file = Path("config/pricing_config.json")
    
    try:
        # 确保配置目录存在
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存简化的价格配置，同时为所有provider设置相同价格
        unified_config = {
            "input_price": pricing_config["input_price"],
            "output_price": pricing_config["output_price"],
            # 为兼容性保留各provider配置
            "deepseek": pricing_config,
            "dashscope": pricing_config,
            "openai": pricing_config,
            "google": pricing_config
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(unified_config, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        st.error(f"❌ 保存配置失败: {e}")
        return False
