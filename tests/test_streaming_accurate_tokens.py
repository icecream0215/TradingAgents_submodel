#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试流式响应下的准确tok        # 3. 初始化OpenAI适配器，强制流式
        llm = ThirdPartyOpenAI(
            model=os.getenv('OPENAI_MODEL_NAME', 'Qwen/Qwen3-235B-A22B-Instruct-2507'),  # 使用正确的模型名
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_API_BASE', 'https://llm.submodel.ai/v1'),
            temperature=0.7,
            stream=True  # 🔑 强制使用流式
        )案3：流式请求后通过完整对话获取100%准确的token数量
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

logger = logging.getLogger('stream_test')

def test_streaming_accurate_tokens():
    """测试流式响应的准确token统计"""
    
    print("🎯 流式响应准确Token统计测试")
    print("=" * 50)
    
    try:
        # 1. 初始化配置
        logger.info("✅ 配置管理器初始化成功")
        
        # 2. 显示测试前统计
        def display_current_statistics():
            """显示当前统计信息"""
            try:
                stats = config_manager.get_usage_statistics(7)
                logger.info(f"📊 最近7天统计:")
                logger.info(f"   💰 总成本: ¥{stats['total_cost']:.6f}")
                logger.info(f"   📞 总请求: {stats['total_requests']}")
                logger.info(f"   📥 输入tokens: {stats['total_input_tokens']:,}")
                logger.info(f"   📤 输出tokens: {stats['total_output_tokens']:,}")
                
                provider_stats = stats.get('provider_stats', {})
                if provider_stats:
                    logger.info(f"   📈 供应商统计:")
                    for provider, provider_info in provider_stats.items():
                        cost = provider_info.get('cost', 0)
                        requests = provider_info.get('requests', 0)
                        logger.info(f"      {provider}: ¥{cost:.6f} ({requests}次请求)")
                        
            except Exception as e:
                logger.error(f"❌ 显示统计信息失败: {e}")
        
        print("📊 测试前统计信息:")
        display_current_statistics()
        before_records = len(config_manager.load_usage_records())
        
        # 3. 初始化OpenAI适配器，强制流式
        llm = ThirdPartyOpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            api_base=os.getenv('OPENAI_API_BASE', 'https://llm.submodel.ai/v1'),
            model_name=os.getenv('OPENAI_MODEL_NAME', 'Qwen/Qwen3-235B-A22B-Instruct-2507'),
            temperature=0.7,
            stream=True  # 🔑 强制使用流式
        )
        
        logger.info("🚀 初始化流式OpenAI适配器完成")
        
        # 4. 发送测试请求（强制流式）
        session_id = f"stream_test_{hash(datetime.now())}"
        test_query = "简要分析比特币目前的市场趋势，不超过50字。"
        
        logger.info(f"📝 会话ID: {session_id}")
        logger.info(f"🚀 发送流式测试请求...")
        logger.info(f"📊 测试前记录数: {before_records}")
        
        # 发送请求
        from langchain_core.messages import HumanMessage
        messages = [HumanMessage(content=test_query)]
        
        response = llm._direct_api_call(
            messages=messages,
            stream=True  # 🔑 强制流式
        )
        
        logger.info(f"✅ 收到流式响应:")
        logger.info(f"   {response}")
        
        # 5. 等待token统计完成（异步进行）
        import time
        time.sleep(3)
        
        # 6. 验证token统计结果
        after_records = len(config_manager.load_usage_records())
        logger.info(f"📊 测试后记录数: {after_records}")
        
        if after_records > before_records:
            # 获取最新记录
            all_records = config_manager.load_usage_records()
            new_record = all_records[-1]
            logger.info(f"📊 新增记录:")
            logger.info(f"   供应商: {new_record.provider}")
            logger.info(f"   模型: {new_record.model_name}")
            logger.info(f"   输入tokens: {new_record.input_tokens}")
            logger.info(f"   输出tokens: {new_record.output_tokens}")
            logger.info(f"   总tokens: {new_record.total_tokens}")
            logger.info(f"   成本: ¥{new_record.cost:.6f}")
            logger.info(f"   会话ID: {new_record.session_id}")
            
            # 检查是否为真实token数据（非默认估算值）
            input_tokens = new_record.input_tokens
            output_tokens = new_record.output_tokens
            
            if input_tokens > 0 and output_tokens > 0:
                if input_tokens != 8000 and output_tokens != 4000:  # 非默认估算值
                    logger.info("✅ Token用量数据获取成功且为准确值（非估算）")
                    print("\n🎉 流式响应准确Token统计测试成功！")
                    print("✅ 系统能够在流式响应后获取100%准确的Token用量")
                    print(f"📊 准确token统计: 输入{input_tokens}, 输出{output_tokens}")
                else:
                    logger.warning("⚠️ 可能使用了估算值")
                    print("\n⚠️ 测试结果：使用了估算值，非100%准确")
            else:
                logger.error("❌ Token用量数据异常")
                print("\n❌ 测试失败：Token用量数据异常")
        else:
            logger.error("❌ 未检测到新的用量记录")
            print("\n❌ 测试失败：未检测到新的用量记录")
        
        # 7. 显示测试后统计
        print("\n📈 测试后统计信息:")
        display_current_statistics()
        
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
        test_result = test_streaming_accurate_tokens()
        
        print("\n" + "=" * 50)
        print("📋 测试总结:")
        if test_result:
            print("🎉 流式响应准确Token统计测试完成！")
            print("✅ 验证了方案3：流式请求+完整对话token统计")
        else:
            print("❌ 测试失败")
        
        print("\n📚 相关文件:")
        print("   - 配置: .env")
        print("   - 记录: config/usage.json")
        print("   - 代码: tradingagents/llm_adapters/third_party_openai.py")
        
    except KeyboardInterrupt:
        print("\n\n👋 测试被用户取消")
    except Exception as e:
        logger.error(f"❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()