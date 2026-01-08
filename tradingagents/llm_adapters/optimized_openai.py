#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化的OpenAI适配器 - 解决500错误和"试错"问题
直接使用最佳实现，避免LangChain流式处理问题
"""

from tradingagents.llm_adapters.third_party_openai import ThirdPartyOpenAI
from tradingagents.utils.logging_manager import get_logger
from datetime import datetime

logger = get_logger("optimized_openai")

class OptimizedOpenAI(ThirdPartyOpenAI):
    """
    优化的OpenAI适配器 - 解决关键问题：
    1. 避免500错误：不再使用LangChain的"试错"机制
    2. 节省时间：直接使用最佳实现
    3. 更稳定：默认非流式模式
    4. 准确统计：保持token统计功能
    """
    
    def __init__(self, *args, **kwargs):
        """初始化优化适配器，默认使用更稳定的非流式模式"""
        # 默认设为非流式模式（更稳定，避免500错误）
        kwargs.setdefault('streaming', False)
        
        super().__init__(*args, **kwargs)
        logger.info("✅ 优化OpenAI适配器初始化完成")
    
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        """
        🎯 核心优化：直接使用最佳实现
        
        原来的流程（有问题）：
        1. 尝试 super()._generate() [LangChain标准方法]
        2. 失败 → 500错误
        3. 切换到 self._direct_api_call() [我们的最佳实现]
        
        优化后的流程：
        1. 直接使用 self._direct_api_call() [最佳实现]
        2. 成功 ✅
        """
        
        # 保存会话信息用于token跟踪
        session_id = kwargs.pop('session_id', None)
        analysis_type = kwargs.pop('analysis_type', 'stock_analysis')
        
        try:
            # 🎯 核心改进：直接使用我们的_direct_api_call方法
            # 避免LangChain标准方法的500错误问题
            
            stream_mode = kwargs.get('stream', getattr(self, 'streaming', False))
            
            logger.info(f"🚀 直接API调用 (stream={stream_mode}, 跳过LangChain试错)")
            
            # 直接调用最佳实现，无需"试错"
            result = self._direct_api_call(messages, stream=stream_mode)
            
            # Token跟踪（使用现有机制）
            self._track_optimized_usage(session_id, analysis_type)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 优化适配器调用失败: {e}")
            return self._create_error_response(f"API调用失败: {str(e)}")
    
    def _track_optimized_usage(self, session_id, analysis_type):
        """优化的token使用跟踪"""
        try:
            if hasattr(self, '_last_api_usage') and self._last_api_usage:
                usage = self._last_api_usage
                input_tokens = usage.get('prompt_tokens', 0)
                output_tokens = usage.get('completion_tokens', 0)
                
                if input_tokens > 0 or output_tokens > 0:
                    # 使用现有的token跟踪机制
                    effective_session_id = (
                        session_id or 
                        getattr(self, 'session_id', None) or 
                        f"opt_{hash(datetime.now())%10000}"
                    )
                    
                    from tradingagents.config.config_manager import token_tracker
                    
                    token_tracker.track_usage(
                        provider="optimized_openai",
                        model_name=getattr(self, 'model_name', 'unknown'),
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        session_id=effective_session_id,
                        analysis_type=analysis_type
                    )
                    
                    logger.info(f"📊 Token统计: {input_tokens}+{output_tokens}={input_tokens+output_tokens}")
                    
        except Exception as e:
            logger.warning(f"⚠️ Token跟踪异常: {e}")

# 便捷创建函数
def create_optimized_llm(**kwargs):
    """
    创建优化的LLM实例的便捷函数
    
    使用示例：
    llm = create_optimized_llm(
        model_name='Qwen/Qwen3-235B-A22B-Instruct-2507',
        temperature=0.7,
        streaming=False  # 推荐：非流式更稳定
    )
    """
    import os
    
    defaults = {
        'api_key': os.getenv('OPENAI_API_KEY'),
        'base_url': os.getenv('OPENAI_API_BASE', 'https://llm.submodel.ai/v1'),
        'model': kwargs.pop('model_name', os.getenv('OPENAI_MODEL_NAME', 'Qwen/Qwen3-235B-A22B-Instruct-2507')),
        'temperature': 0.7,
        'streaming': False,  # 默认非流式，更稳定
        'max_tokens': 2000
    }
    
    defaults.update(kwargs)
    
    return OptimizedOpenAI(**defaults)

if __name__ == "__main__":
    """简单测试优化适配器"""
    import os
    from dotenv import load_dotenv
    from langchain_core.messages import HumanMessage
    
    load_dotenv()
    
    print("🎯 测试优化OpenAI适配器")
    
    # 创建优化的LLM实例
    llm = create_optimized_llm(streaming=False)
    
    # 测试调用
    messages = [HumanMessage(content="简要分析比特币趋势，不超过20字")]
    
    start_time = datetime.now()
    result = llm._generate(messages)
    duration = (datetime.now() - start_time).total_seconds()
    
    if result and result.generations:
        response = result.generations[0].message.content
        print(f"✅ 优化适配器成功 ({duration:.2f}秒)")
        print(f"📄 响应: {response}")
    else:
        print("❌ 测试失败")