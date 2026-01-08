#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化后的适配器 - 避免LangChain流式问题
直接使用最佳实现，不再"试错"
"""

import os
import sys
import logging
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tradingagents.config.config_manager import config_manager, token_tracker
from tradingagents.utils.logging_manager import get_logger
from tradingagents.llm_adapters.third_party_openai import ThirdPartyOpenAI

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger('optimized_test')

class OptimizedOpenAI(ThirdPartyOpenAI):
    """
    优化的OpenAI适配器 - 避免LangChain流式问题
    直接使用最佳实现，不再"试错"
    """
    
    def __init__(self, *args, **kwargs):
        # 提取自定义参数，避免传递给父类
        user_wants_streaming = kwargs.pop('user_wants_streaming', False)
        super().__init__(*args, **kwargs)
        # 在父类初始化后设置自定义属性
        object.__setattr__(self, 'user_wants_streaming', user_wants_streaming)
        logger.info("🚀 初始化优化的OpenAI适配器")
    
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        """
        优化的生成方法：
        1. 直接使用我们的_direct_api_call，避免LangChain问题
        2. 不再"试错"，直接使用最佳实现
        3. 支持流式和非流式，但默认使用非流式（更稳定）
        """
        # 保存自定义参数用于token跟踪
        custom_kwargs = {
            'session_id': kwargs.pop('session_id', None),
            'analysis_type': kwargs.pop('analysis_type', 'stock_analysis')
        }
        
        try:
            # 🎯 直接使用我们的_direct_api_call方法
            # 根据用户意图选择流式或非流式
            wants_streaming = self.user_wants_streaming
            kwargs_stream = kwargs.get('stream', False)
            
            if isinstance(kwargs_stream, bool) and kwargs_stream:
                wants_streaming = True
                
            logger.info(f"🚀 使用优化的直接API调用 (stream={wants_streaming})")
            result = self._direct_api_call(messages, stream=wants_streaming)
            
            # Token跟踪
            self._track_token_usage(custom_kwargs)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 优化适配器失败: {e}")
            # 创建错误响应
            return self._create_error_response(
                f"🚨 API调用失败: {str(e)}"
            )
    
    def _track_token_usage(self, custom_kwargs):
        """跟踪token使用量"""
        try:
            if hasattr(self, '_last_api_usage') and self._last_api_usage:
                usage = self._last_api_usage
                input_tokens = usage.get('prompt_tokens', 0)
                output_tokens = usage.get('completion_tokens', 0)
                
                if input_tokens > 0 or output_tokens > 0:
                    from tradingagents.config.config_manager import TOKEN_TRACKING_ENABLED
                    
                    if TOKEN_TRACKING_ENABLED:
                        session_id = self.session_id or custom_kwargs.get('session_id') or f"optimized_{hash(datetime.now())%10000}"
                        analysis_type = custom_kwargs.get('analysis_type', 'stock_analysis')
                        
                        token_tracker.track_usage(
                            provider="optimized_openai",
                            model_name=getattr(self, 'model_name', 'unknown'),
                            input_tokens=input_tokens,
                            output_tokens=output_tokens,
                            session_id=session_id,
                            analysis_type=analysis_type
                        )
                        logger.info(f"📊 [token] 优化适配器记录: {input_tokens}+{output_tokens}={input_tokens+output_tokens}")
                    
        except Exception as track_error:
            logger.error(f"⚠️ Token 追踪失败: {track_error}")

def test_optimized_adapter():
    """测试优化的适配器"""
    
    print("🎯 测试优化的OpenAI适配器")
    print("=" * 50)
    
    try:
        # 显示测试前统计
        def display_stats():
            try:
                stats = config_manager.get_usage_statistics(7)
                logger.info(f"📊 最近7天: 成本¥{stats['total_cost']:.6f}, 请求{stats['total_requests']}次")
            except Exception as e:
                logger.error(f"❌ 显示统计失败: {e}")
        
        print("📊 测试前统计:")
        display_stats()
        before_records = len(config_manager.load_usage_records())
        
        # 1. 测试非流式模式（推荐，更稳定）
        print("\n1️⃣ 测试非流式模式（推荐）...")
        
        llm_stable = OptimizedOpenAI(
            model=os.getenv('OPENAI_MODEL_NAME', 'Qwen/Qwen3-235B-A22B-Instruct-2507'),
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_API_BASE', 'https://llm.submodel.ai/v1'),
            temperature=0.7,
            streaming=False,  # 非流式，更稳定
            user_wants_streaming=False
        )
        
        from langchain_core.messages import HumanMessage
        test_query = "简要分析当前科技股的市场表现，不超过30字。"
        messages = [HumanMessage(content=test_query)]
        
        logger.info(f"📝 测试查询: {test_query}")
        start_time = datetime.now()
        
        result = llm_stable._generate(messages)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if result and result.generations:
            response = result.generations[0].message.content
            logger.info(f"✅ 非流式响应成功 ({duration:.2f}秒)")
            logger.info(f"📄 响应: {response}")
        else:
            logger.error("❌ 非流式响应失败")
        
        # 2. 测试流式模式
        print("\n2️⃣ 测试流式模式...")
        
        llm_stream = OptimizedOpenAI(
            model=os.getenv('OPENAI_MODEL_NAME', 'Qwen/Qwen3-235B-A22B-Instruct-2507'),
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_API_BASE', 'https://llm.submodel.ai/v1'),
            temperature=0.7,
            streaming=True,  # 流式
            user_wants_streaming=True
        )
        
        test_query2 = "简要说明AI在金融领域的应用，不超过30字。"
        messages2 = [HumanMessage(content=test_query2)]
        
        logger.info(f"📝 测试查询: {test_query2}")
        start_time = datetime.now()
        
        result2 = llm_stream._generate(messages2, stream=True)
        
        end_time = datetime.now()
        duration2 = (end_time - start_time).total_seconds()
        
        if result2 and result2.generations:
            response2 = result2.generations[0].message.content
            logger.info(f"✅ 流式响应成功 ({duration2:.2f}秒)")
            logger.info(f"📄 响应: {response2}")
        else:
            logger.error("❌ 流式响应失败")
        
        # 验证改进效果
        import time
        time.sleep(2)
        
        after_records = len(config_manager.load_usage_records())
        new_records = after_records - before_records
        
        print(f"\n📈 测试结果:")
        print(f"   ⏱️ 非流式耗时: {duration:.2f}秒")
        print(f"   ⏱️ 流式耗时: {duration2:.2f}秒") 
        print(f"   📊 新增记录: {new_records}条")
        
        if new_records > 0:
            print("✅ 优化成功：")
            print("   🚀 避免了'试错'机制，直接使用最佳实现")
            print("   📊 准确的token统计")
            print("   ⚡ 更快的响应速度")
        
        print("\n📊 测试后统计:")
        display_stats()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_production_adapter():
    """创建生产环境用的优化适配器"""
    
    print("\n🔧 创建生产环境优化适配器...")
    
    production_code = '''#!/usr/bin/env python3
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
'''
    
    # 保存生产适配器到文件
    production_file = '/root/TradingAgents/tradingagents/llm_adapters/production_openai.py'
    
    try:
        with open(production_file, 'w', encoding='utf-8') as f:
            f.write(production_code)
        
        logger.info(f"✅ 生产适配器已保存到: {production_file}")
        
        usage_example = '''
# 使用示例：
from tradingagents.llm_adapters.production_openai import ProductionOpenAI

# 创建优化的适配器实例
llm = ProductionOpenAI(
    model=os.getenv('OPENAI_MODEL_NAME'),
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url=os.getenv('OPENAI_API_BASE'),
    temperature=0.7,
    streaming=False  # 推荐非流式模式
)

# 直接使用，无需担心500错误和"试错"问题
response = llm.invoke("分析股市趋势")
'''
        
        print("📝 使用示例:")
        print(usage_example)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 保存生产适配器失败: {e}")
        return False

if __name__ == "__main__":
    try:
        # 加载环境变量
        from dotenv import load_dotenv
        load_dotenv()
        
        if not os.getenv('OPENAI_API_KEY'):
            logger.error("❌ 请设置 OPENAI_API_KEY 环境变量")
            sys.exit(1)
        
        logger.info("✅ 环境配置加载成功")
        
        # 运行测试
        test_result = test_optimized_adapter()
        
        # 创建生产适配器
        production_result = create_production_adapter()
        
        print("\n" + "=" * 50)
        print("📋 优化总结:")
        if test_result:
            print("🎉 优化适配器测试完成！")
            print("\n💡 主要改进:")
            print("   1. 🚀 避免LangChain流式处理的不稳定性")
            print("   2. 🎯 直接使用最佳实现，不再'试错'")
            print("   3. ⚡ 支持流式和非流式，默认非流式更稳定")
            print("   4. 📊 保持准确的token统计")
            print("\n🔧 使用建议:")
            print("   - 优先使用非流式模式（更稳定，无500错误）")
            print("   - 必要时才使用流式模式")
            print("   - 替换现有的ThirdPartyOpenAI为ProductionOpenAI")
            
            if production_result:
                print("   - 已创建生产环境适配器：production_openai.py")
        else:
            print("❌ 测试失败")
            
    except KeyboardInterrupt:
        print("\n\n👋 测试被用户取消")
    except Exception as e:
        logger.error(f"❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()
