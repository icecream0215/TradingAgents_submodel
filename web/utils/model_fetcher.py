"""
简化的LLM模型获取工具
从第三方服务获取可用模型列表
"""

import requests
import logging
import streamlit as st
from typing import List, Optional
import os

logger = logging.getLogger(__name__)

class ModelFetcher:
    """简化的LLM模型获取器"""
    
    def __init__(self):
        self.base_url = "https://llm.submodel.ai/v1"
        self.api_key = os.getenv("OPENAI_API_KEY")
        
    def get_available_models(self) -> List[str]:
        """获取可用模型ID列表"""
        try:
            if not self.api_key:
                logger.error("❌ API密钥未配置")
                return ['deepseek-ai/DeepSeek-V3.1']  # 返回默认模型
            
            # 检查缓存
            if hasattr(st.session_state, 'cached_models') and st.session_state.cached_models:
                logger.debug(f"📋 使用缓存的模型列表，共{len(st.session_state.cached_models)}个模型")
                return st.session_state.cached_models
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            logger.info("🔍 正在获取可用模型列表...")
            response = requests.get(f"{self.base_url}/models", headers=headers, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get('data', [])
                
                # 提取模型ID列表
                model_ids = []
                for model in models:
                    model_id = model.get('id', '')
                    if model_id:  # 确保模型ID不为空
                        model_ids.append(model_id)
                
                # 排序
                model_ids.sort()
                
                # 缓存结果
                st.session_state.cached_models = model_ids
                
                logger.info(f"✅ 成功获取{len(model_ids)}个可用模型")
                return model_ids
            else:
                logger.error(f"❌ 获取模型列表失败: HTTP {response.status_code}")
                return ['deepseek-ai/DeepSeek-V3.1']  # 返回默认模型
                
        except requests.exceptions.Timeout:
            logger.error("⏰ 获取模型列表超时")
            return ['deepseek-ai/DeepSeek-V3.1']
        except requests.exceptions.RequestException as e:
            logger.error(f"🌐 网络请求失败: {e}")
            return ['deepseek-ai/DeepSeek-V3.1']
        except Exception as e:
            logger.error(f"💥 获取模型列表出现异常: {e}")
            return ['deepseek-ai/DeepSeek-V3.1']
    
    def get_default_model(self) -> str:
        """获取默认模型"""
        models = self.get_available_models()
        
        # 优先选择DeepSeek模型
        for model in models:
            if 'deepseek' in model.lower():
                return model
        
        # 如果没有DeepSeek，选择第一个可用模型
        if models:
            return models[0]
        
        # 如果获取失败，使用固定的默认模型
        return 'deepseek-ai/DeepSeek-V3.1'
    
    def refresh_models(self):
        """刷新模型列表（清除缓存）"""
        if hasattr(st.session_state, 'cached_models'):
            del st.session_state.cached_models
        logger.info("🔄 已清除模型列表缓存")

# 创建全局实例
model_fetcher = ModelFetcher()