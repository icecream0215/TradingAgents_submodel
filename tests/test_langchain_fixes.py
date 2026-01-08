#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证LangChain流式支持修复效果
测试修复后的参数处理和流式检测逻辑
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

logger = get_logger('fix_test')

def test_langchain_streaming_fixes():
    """测试LangChain流式支持修复效果"""
    
    print("🔧 LangChain流式支持修复效果验证")
    print("=" * 60)
    
    try:
        # 1. 测试参数冲突修复
        print("\n1️⃣ 测试参数冲突修复...")
        
        # 测试同时设置streaming和stream参数
        llm_conflict = ThirdPartyOpenAI(
            model=os.getenv('OPENAI_MODEL_NAME', 'Qwen/Qwen3-235B-A22B-Instruct-2507'),
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_API_BASE', 'https://llm.submodel.ai/v1'),
            streaming=True,   # LangChain标准参数
            stream=True,      # 可能的冲突参数
            temperature=0.7
        )
        
        logger.info(f"✅ 参数冲突处理完成，无异常")
        logger.info(f"🔍 user_wants_streaming: {getattr(llm_conflict, 'user_wants_streaming', 'N/A')}")
        
        # 2. 测试流式检测逻辑
        print("\n2️⃣ 测试流式检测逻辑...")
        
        from langchain_core.messages import HumanMessage
        test_query = "简要说明云计算核心优势，不超过15字。"
        messages = [HumanMessage(content=test_query)]
        
        logger.info(f"📝 测试消息: {test_query}")
        
        before_count = len(config_manager.load_usage_records())
        result = llm_conflict.generate([messages])
        after_count = len(config_manager.load_usage_records())
        
        logger.info(f"✅ 流式响应: {result.generations[0][0].text}")
        logger.info(f"📊 新增记录数: {after_count - before_count}")
        
        # 检查最新记录
        if after_count > before_count:
            latest_record = config_manager.load_usage_records()[-1]
            logger.info(f"📊 Token统计: 输入={latest_record.input_tokens}, 输出={latest_record.output_tokens}")
            
            # 判断是否使用了方案3（准确统计）
            if latest_record.input_tokens > 0 and latest_record.output_tokens > 0:
                if (10 <= latest_record.input_tokens <= 100) and (5 <= latest_record.output_tokens <= 50):
                    logger.info("✅ 方案3正常工作，获得准确token统计")
                else:
                    logger.warning("⚠️ Token数值异常，可能是估算值")
            else:
                logger.error("❌ Token统计失败")
        
        # 3. 测试非流式模式
        print("\n3️⃣ 测试非流式模式...")
        
        llm_non_stream = ThirdPartyOpenAI(
            model=os.getenv('OPENAI_MODEL_NAME', 'Qwen/Qwen3-235B-A22B-Instruct-2507'),
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_API_BASE', 'https://llm.submodel.ai/v1'),
            streaming=False,  # 明确关闭流式
            temperature=0.7
        )
        
        test_query2 = "简要说明大数据技术价值，不超过15字。"
        messages2 = [HumanMessage(content=test_query2)]
        
        logger.info(f"📝 测试消息: {test_query2}")
        logger.info(f"🔍 user_wants_streaming: {getattr(llm_non_stream, 'user_wants_streaming', 'N/A')}")
        
        before_count2 = len(config_manager.load_usage_records())
        result2 = llm_non_stream.generate([messages2])
        after_count2 = len(config_manager.load_usage_records())
        
        logger.info(f"✅ 非流式响应: {result2.generations[0][0].text}")
        logger.info(f"📊 新增记录数: {after_count2 - before_count2}")
        
        # 4. 测试不同参数组合
        print("\n4️⃣ 测试不同参数组合...")
        
        test_configs = [
            {"streaming": True, "stream": False, "expected": True},
            {"streaming": False, "stream": True, "expected": True}, 
            {"streaming": False, "stream": False, "expected": False},
            {"streaming": True, "expected": True},
            {"stream": True, "expected": True},
            {"expected": False}  # 默认配置
        ]
        
        for i, config in enumerate(test_configs, 1):
            expected = config.pop('expected')
            
            try:
                test_llm = ThirdPartyOpenAI(
                    model="test-model",
                    api_key="test-key",
                    **config
                )
                
                actual = getattr(test_llm, 'user_wants_streaming', False)
                status = "✅" if actual == expected else "❌"
                
                logger.info(f"{status} 配置{i}: {config} → user_wants_streaming={actual} (期望={expected})")
                
            except Exception as e:
                logger.error(f"❌ 配置{i}测试失败: {e}")
        
        # 5. 验证警告消除
        print("\n5️⃣ 验证警告消除...")
        
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            test_llm = ThirdPartyOpenAI(
                model="test-model",
                api_key="test-key",
                streaming=True,
                stream=True
            )
            
            # 检查是否还有stream参数的警告
            stream_warnings = [warning for warning in w if 'stream' in str(warning.message).lower()]
            
            if stream_warnings:
                logger.warning(f"⚠️ 仍有{len(stream_warnings)}个stream相关警告")
                for warning in stream_warnings:
                    logger.warning(f"   {warning.message}")
            else:
                logger.info("✅ 成功消除stream参数警告")
        
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
        test_result = test_langchain_streaming_fixes()
        
        print("\n" + "=" * 60)
        print("📋 修复验证总结:")
        
        if test_result:
            print("✅ LangChain流式支持修复验证完成")
            print("🔧 修复的问题:")
            print("   1. 参数冲突 - streaming vs stream")
            print("   2. 流式检测逻辑优化")
            print("   3. 初始化日志改进")
            print("   4. 警告消息处理")
        else:
            print("❌ 修复验证中出现错误")
        
        print(f"\n📚 相关文件:")
        print(f"   - 代码: tradingagents/llm_adapters/third_party_openai.py")
        
    except KeyboardInterrupt:
        print(f"\n\n👋 测试被用户取消")
    except Exception as e:
        logger.error(f"❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()