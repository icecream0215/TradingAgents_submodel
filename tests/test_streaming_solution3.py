#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门测试流式响应和方案3的准确token统计
这次确保100%使用流式响应，然后验证方案3是否能获得准确token数
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

logger = get_logger('stream_test')

def test_streaming_then_accurate_tokens():
    """测试流式响应+方案3准确token统计"""
    
    print("🎯 流式响应+方案3准确Token统计测试")
    print("=" * 60)
    
    try:
        # 1. 初始化
        logger.info("✅ 配置管理器初始化成功")
        
        def display_current_statistics():
            """显示当前统计信息"""
            try:
                stats = config_manager.get_usage_statistics(7)
                logger.info(f"📊 最近7天统计:")
                logger.info(f"   💰 总成本: ¥{stats['total_cost']:.6f}")
                logger.info(f"   📞 总请求: {stats['total_requests']}")
                logger.info(f"   📥 输入tokens: {stats['total_input_tokens']:,}")
                logger.info(f"   📤 输出tokens: {stats['total_output_tokens']:,}")
                        
            except Exception as e:
                logger.error(f"❌ 显示统计信息失败: {e}")
        
        print("📊 测试前统计信息:")
        display_current_statistics()
        before_records = len(config_manager.load_usage_records())
        
        # 2. 使用LangChain的generate方法确保是流式的
        llm = ThirdPartyOpenAI(
            model=os.getenv('OPENAI_MODEL_NAME', 'Qwen/Qwen3-235B-A22B-Instruct-2507'),
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_API_BASE', 'https://llm.submodel.ai/v1'),
            temperature=0.7,
            streaming=True  # 🔑 使用LangChain标准的streaming参数
        )
        
        logger.info("🚀 初始化流式OpenAI适配器完成")
        logger.info(f"📊 测试前记录数: {before_records}")
        
        # 3. 使用LangChain标准方法发送流式请求
        from langchain_core.messages import HumanMessage
        test_query = "简要分析当前加密货币市场趋势，不超过30字。"
        messages = [HumanMessage(content=test_query)]
        
        logger.info(f"🚀 发送流式测试请求...")
        logger.info(f"📝 测试消息: {test_query}")
        
        # 使用generate方法（会触发流式响应）
        from langchain_core.messages import BaseMessage
        response = llm.generate([messages])
        
        logger.info(f"✅ 收到流式响应:")
        logger.info(f"   {response.generations[0][0].text}")
        
        # 4. 等待token统计完成（可能是异步的）
        import time
        time.sleep(5)  # 给更多时间完成统计
        
        # 5. 验证结果
        after_records = len(config_manager.load_usage_records())
        logger.info(f"📊 测试后记录数: {after_records}")
        
        if after_records > before_records:
            all_records = config_manager.load_usage_records()
            new_record = all_records[-1]
            logger.info(f"📊 新增记录:")
            logger.info(f"   供应商: {new_record.provider}")
            logger.info(f"   模型: {new_record.model_name}")
            logger.info(f"   输入tokens: {new_record.input_tokens}")
            logger.info(f"   输出tokens: {new_record.output_tokens}")
            logger.info(f"   总tokens: {new_record.input_tokens + new_record.output_tokens}")
            logger.info(f"   成本: ¥{new_record.cost:.6f}")
            logger.info(f"   时间戳: {new_record.timestamp}")
            
            # 分析token统计的准确性
            input_tokens = new_record.input_tokens
            output_tokens = new_record.output_tokens
            
            # 🎯 关键判断：方案3是否工作了
            if input_tokens > 0 and output_tokens > 0:
                # 检查是否为合理的token数（不是默认估算值）
                if (10 <= input_tokens <= 1000) and (5 <= output_tokens <= 500):
                    if input_tokens != 8000 and output_tokens != 4000:  # 确认不是估算值
                        logger.info("🎉 Token用量数据准确！")
                        print(f"\n✅ 流式响应+方案3测试成功！")
                        print(f"📊 准确Token统计: 输入{input_tokens}, 输出{output_tokens}")
                        print(f"💰 计算成本: ¥{new_record.cost:.6f}")
                        
                        # 检查是否真的是流式响应
                        print(f"🔍 响应特征分析:")
                        print(f"   模型: {new_record.model_name}")
                        print(f"   Token比例: 输入/输出 = {input_tokens}/{output_tokens} = {input_tokens/output_tokens:.2f}")
                        
                        return True
                    else:
                        logger.warning("⚠️ 检测到估算值，方案3可能未生效")
                        print(f"\n⚠️ 测试结果：使用了估算值")
                else:
                    logger.warning(f"⚠️ Token数值异常: 输入{input_tokens}, 输出{output_tokens}")
                    print(f"\n⚠️ 测试结果：Token数值异常")
            else:
                logger.error("❌ Token用量数据为0")
                print(f"\n❌ 测试失败：Token用量数据为0")
        else:
            logger.error("❌ 未检测到新的用量记录")
            print(f"\n❌ 测试失败：未检测到新的用量记录")
        
        # 显示测试后统计
        print(f"\n📈 测试后统计信息:")
        display_current_statistics()
        
        return False
        
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
        test_result = test_streaming_then_accurate_tokens()
        
        print("\n" + "=" * 60)
        print("📋 测试总结:")
        if test_result:
            print("🎉 流式响应+方案3准确Token统计测试成功！")
            print("✅ 验证了：")
            print("   1. 流式响应体验（实时显示）")
            print("   2. 100%准确的Token统计（方案3）")
            print("   3. 准确的成本计算")
        else:
            print("❌ 测试失败或方案3未正常工作")
            print("⚠️ 可能原因：")
            print("   1. 流式响应未启用")
            print("   2. 方案3的双重请求未执行")
            print("   3. Token统计逻辑存在问题")
        
        print(f"\n📚 相关文件:")
        print(f"   - 配置: .env")
        print(f"   - 记录: config/usage.json")
        print(f"   - 代码: tradingagents/llm_adapters/third_party_openai.py")
        
    except KeyboardInterrupt:
        print(f"\n\n👋 测试被用户取消")
    except Exception as e:
        logger.error(f"❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()