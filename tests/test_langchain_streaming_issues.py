#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查LangChain流式支持的潜在问题
比较LangChain标准方法和我们的直接API调用方法
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

logger = get_logger('langchain_test')

def test_langchain_streaming_issues():
    """测试LangChain流式支持的潜在问题"""
    
    print("🔍 LangChain流式支持问题检查")
    print("=" * 60)
    
    try:
        # 1. 测试LangChain标准流式方法
        print("\n1️⃣ 测试LangChain标准流式方法...")
        
        llm_standard = ThirdPartyOpenAI(
            model=os.getenv('OPENAI_MODEL_NAME', 'Qwen/Qwen3-235B-A22B-Instruct-2507'),
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_API_BASE', 'https://llm.submodel.ai/v1'),
            temperature=0.7,
            streaming=False  # 🔑 关闭流式，使用LangChain标准方法
        )
        
        from langchain_core.messages import HumanMessage
        test_query = "简要说明区块链技术优势，不超过20字。"
        messages = [HumanMessage(content=test_query)]
        
        logger.info(f"📝 测试消息: {test_query}")
        logger.info(f"🎯 LangChain标准方法（非流式）...")
        
        before_count = len(config_manager.load_usage_records())
        result1 = llm_standard.generate([messages])
        after_count = len(config_manager.load_usage_records())
        
        logger.info(f"✅ LangChain标准响应: {result1.generations[0][0].text}")
        logger.info(f"📊 新增记录数: {after_count - before_count}")
        
        # 2. 测试我们的直接API调用方法（流式）
        print("\n2️⃣ 测试我们的直接API流式方法...")
        
        llm_direct = ThirdPartyOpenAI(
            model=os.getenv('OPENAI_MODEL_NAME', 'Qwen/Qwen3-235B-A22B-Instruct-2507'),
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_API_BASE', 'https://llm.submodel.ai/v1'),
            temperature=0.7,
            streaming=True  # 🔑 开启流式，使用我们的方法
        )
        
        test_query2 = "简要说明人工智能技术优势，不超过20字。"
        messages2 = [HumanMessage(content=test_query2)]
        
        logger.info(f"📝 测试消息: {test_query2}")
        logger.info(f"🎯 我们的流式方法...")
        
        before_count2 = len(config_manager.load_usage_records())
        result2 = llm_direct.generate([messages2])
        after_count2 = len(config_manager.load_usage_records())
        
        logger.info(f"✅ 我们的流式响应: {result2.generations[0][0].text}")
        logger.info(f"📊 新增记录数: {after_count2 - before_count2}")
        
        # 3. 测试LangChain的流式回调机制
        print("\n3️⃣ 测试LangChain流式回调机制...")
        
        class StreamingHandler:
            def __init__(self):
                self.tokens = []
                self.complete_text = ""
                
            def on_llm_new_token(self, token: str, **kwargs):
                self.tokens.append(token)
                self.complete_text += token
                print(f"🔄 流式Token: {repr(token)}")
        
        handler = StreamingHandler()
        
        try:
            # 测试LangChain的流式回调
            from langchain.callbacks import CallbackManager
            from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
            
            llm_callback = ThirdPartyOpenAI(
                model=os.getenv('OPENAI_MODEL_NAME', 'Qwen/Qwen3-235B-A22B-Instruct-2507'),
                api_key=os.getenv('OPENAI_API_KEY'),
                base_url=os.getenv('OPENAI_API_BASE', 'https://llm.submodel.ai/v1'),
                temperature=0.7,
                streaming=True,
                callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
            )
            
            test_query3 = "简要说明机器学习基本原理，不超过20字。"
            messages3 = [HumanMessage(content=test_query3)]
            
            logger.info(f"📝 测试消息: {test_query3}")
            logger.info(f"🎯 LangChain流式回调...")
            
            before_count3 = len(config_manager.load_usage_records())
            result3 = llm_callback.generate([messages3])
            after_count3 = len(config_manager.load_usage_records())
            
            logger.info(f"✅ 回调流式响应: {result3.generations[0][0].text}")
            logger.info(f"📊 新增记录数: {after_count3 - before_count3}")
            logger.info(f"🔄 捕获的token数: {len(handler.tokens)}")
            
        except Exception as callback_error:
            logger.warning(f"⚠️ LangChain流式回调测试失败: {callback_error}")
        
        # 4. 分析问题
        print("\n4️⃣ 问题分析...")
        
        # 检查最近的记录
        recent_records = config_manager.load_usage_records()[-6:]
        logger.info(f"📊 最近6条记录分析:")
        
        for i, record in enumerate(recent_records[-3:], 1):
            logger.info(f"   记录{i}: 输入={record.input_tokens}, 输出={record.output_tokens}, 模型={record.model_name}")
            logger.info(f"          时间={record.timestamp}, 成本=¥{record.cost:.6f}")
        
        # 5. LangChain版本检查
        print("\n5️⃣ LangChain版本检查...")
        
        try:
            import langchain
            logger.info(f"📦 LangChain版本: {langchain.__version__}")
        except:
            logger.warning("⚠️ 无法获取LangChain版本")
            
        try:
            import langchain_openai
            logger.info(f"📦 LangChain-OpenAI版本: {langchain_openai.__version__}")
        except:
            logger.warning("⚠️ 无法获取LangChain-OpenAI版本")
        
        # 6. 检查流式参数处理
        print("\n6️⃣ 流式参数处理检查...")
        
        # 检查我们的参数处理逻辑
        test_llm = ThirdPartyOpenAI(
            model="test-model",
            streaming=True,
            stream=True  # 同时设置两个参数
        )
        
        logger.info(f"🔍 streaming属性: {getattr(test_llm, 'streaming', 'N/A')}")
        logger.info(f"🔍 stream属性: {getattr(test_llm, 'stream', 'N/A')}")
        
        # 检查可能的冲突
        if hasattr(test_llm, 'streaming') and hasattr(test_llm, 'stream'):
            if test_llm.streaming != test_llm.stream:
                logger.warning(f"⚠️ 流式参数冲突: streaming={test_llm.streaming}, stream={test_llm.stream}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
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
        test_result = test_langchain_streaming_issues()
        
        print("\n" + "=" * 60)
        print("📋 测试总结:")
        
        if test_result:
            print("✅ LangChain流式支持检查完成")
            print("📚 可能的问题点:")
            print("   1. LangChain标准流式 vs 我们的直接API调用")
            print("   2. 流式回调机制的兼容性")
            print("   3. streaming/stream参数冲突")
            print("   4. token统计在不同方法下的表现")
        else:
            print("❌ 检查过程中出现错误")
        
        print(f"\n📚 相关文件:")
        print(f"   - 代码: tradingagents/llm_adapters/third_party_openai.py")
        print(f"   - 记录: config/usage.json")
        
    except KeyboardInterrupt:
        print(f"\n\n👋 测试被用户取消")
    except Exception as e:
        logger.error(f"❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()