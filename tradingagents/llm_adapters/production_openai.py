#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产环境优化的OpenAI适配器
直接使用最佳实现，避免LangChain流式问题
"""

from tradingagents.llm_adapters.third_party_openai import ThirdPartyOpenAI
from tradingagents.config.config_manager import token_tracker, TOKEN_TRACKING_ENABLED
from tradingagents.utils.logging_manager import get_logger
from datetime import datetime

logger = get_logger("production_adapter")

class ProductionOpenAI(ThirdPartyOpenAI):
    """
    生产环境优化的OpenAI适配器
    - 直接使用最佳实现，不再"试错"
    - 默认非流式模式，更稳定
    - 保持准确的token统计
    """
    
    def __init__(self, *args, **kwargs):
        # 强制设置为非流式模式（更稳定）
        kwargs['streaming'] = kwargs.get('streaming', False)
        super().__init__(*args, **kwargs)
        
        # 标记这是优化版本
        self.is_optimized = True
        logger.info("🚀 初始化生产环境优化适配器")
    
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        """
        生产环境优化的生成方法
        """
        # 保存自定义参数
        session_id = kwargs.pop('session_id', None)
        analysis_type = kwargs.pop('analysis_type', 'stock_analysis')
        
        try:
            # 🎯 核心优化：直接使用_direct_api_call
            # 避免LangChain的"试错"机制
            
            # 根据配置选择流式模式
            use_streaming = kwargs.get('stream', getattr(self, 'streaming', False))
            
            logger.debug(f"🔄 直接API调用 (stream={use_streaming})")
            
            # 直接调用最佳实现
            result = self._direct_api_call(messages, stream=use_streaming)
            
            # Token跟踪
            self._track_production_usage(session_id, analysis_type)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 生产适配器调用失败: {e}")
            return self._create_error_response(f"API调用失败: {str(e)}")
    
    def _track_production_usage(self, session_id, analysis_type):
        """生产环境token使用跟踪"""
        try:
            if hasattr(self, '_last_api_usage') and self._last_api_usage:
                usage = self._last_api_usage
                input_tokens = usage.get('prompt_tokens', 0)
                output_tokens = usage.get('completion_tokens', 0)
                
                if (input_tokens > 0 or output_tokens > 0) and TOKEN_TRACKING_ENABLED:
                    effective_session_id = (
                        session_id or 
                        getattr(self, 'session_id', None) or 
                        f"prod_{hash(datetime.now())%10000}"
                    )
                    
                    token_tracker.track_usage(
                        provider="production_openai",
                        model_name=getattr(self, 'model_name', 'unknown'),
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        session_id=effective_session_id,
                        analysis_type=analysis_type
                    )
                    
                    logger.debug(f"📊 token记录: {input_tokens}+{output_tokens}")
                    
        except Exception as e:
            logger.warning(f"⚠️ Token跟踪失败: {e}")
