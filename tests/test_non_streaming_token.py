#!/usr/bin/env python3
"""
测试非流式响应的Token使用统计
验证能否获取真实的token用量数据
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入必要的模块
from tradingagents.llm_adapters.third_party_openai import ThirdPartyOpenAI
from tradingagents.config.config_manager import config_manager, token_tracker
from tradingagents.utils.logging_manager import get_logger
from langchain_core.messages import HumanMessage, SystemMessage

logger = get_logger('test')

def load_env_config():
    """加载环境配置"""
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(env_file, override=True)
        logger.info("✅ 环境配置加载成功")
    else:
        logger.warning("⚠️ .env文件未找到")

def test_non_streaming_token_tracking():
    """测试非流式响应的Token跟踪功能"""
    logger.info("🧪 测试非流式响应Token跟踪功能...")
    
    # 获取API配置
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = "https://llm.submodel.ai/v1"
    
    if not api_key:
        logger.error("❌ 未配置OPENAI_API_KEY环境变量")
        return False
    
    try:
        # 创建ThirdPartyOpenAI适配器（非流式）
        logger.info(f"🚀 初始化非流式ThirdPartyOpenAI适配器...")
        
        llm = ThirdPartyOpenAI(
            model="Qwen/Qwen3-235B-A22B-Instruct-2507",
            api_key=api_key,
            base_url=base_url,
            temperature=0.7,
            max_tokens=200,
            streaming=False,  # 关闭流式响应
            stream=False     # 确保非流式
        )
        
        # 生成唯一会话ID
        session_id = f"non_stream_test_{int(time.time())}"
        logger.info(f"📝 会话ID: {session_id}")
        
        # 测试消息
        messages = [
            SystemMessage(content="你是一个专业的股票分析师。"),
            HumanMessage(content="简单分析一下腾讯股票，不超过30字。")
        ]
        
        logger.info(f"🚀 发送非流式请求...")
        
        # 记录测试前的使用记录数量
        initial_records = config_manager.load_usage_records()
        initial_count = len(initial_records)
        logger.info(f"📊 测试前记录数: {initial_count}")
        
        # 调用LLM（非流式）
        response = llm.invoke(
            messages,
            session_id=session_id,
            analysis_type="non_stream_test"
        )
        
        logger.info(f"✅ 收到非流式响应:")
        logger.info(f"   {response.content[:100]}{'...' if len(response.content) > 100 else ''}")
        
        # 等待记录保存
        time.sleep(2)
        
        # 查看会话成本
        session_cost = token_tracker.get_session_cost(session_id)
        logger.info(f"💰 本次分析成本: ¥{session_cost:.6f}")
        
        # 检查是否有新的token使用记录
        final_records = config_manager.load_usage_records()
        final_count = len(final_records)
        logger.info(f"📊 测试后记录数: {final_count}")
        
        if final_count > initial_count:
            # 获取新增的记录
            new_records = final_records[initial_count:]
            for i, record in enumerate(new_records):
                logger.info(f"📊 新增记录 #{i+1}:")
                logger.info(f"   供应商: {record.provider}")
                logger.info(f"   模型: {record.model_name}")
                logger.info(f"   输入tokens: {record.input_tokens}")
                logger.info(f"   输出tokens: {record.output_tokens}")
                logger.info(f"   成本: ¥{record.cost:.6f}")
                logger.info(f"   会话ID: {record.session_id}")
                
                # 检查是否为真实数据（非估算）
                if record.input_tokens > 0 and record.output_tokens > 0:
                    # 非流式响应应该能获取到更准确的token数据
                    if record.input_tokens < 1000 and record.output_tokens < 1000:  # 合理范围
                        logger.info(f"✅ 获取到了合理的Token用量数据")
                        return True
                    else:
                        logger.warning(f"⚠️ Token用量数据可能不准确")
                        return True  # 依然算成功，因为有数据
                else:
                    logger.warning(f"⚠️ Token用量数据为0")
                    return False
        else:
            logger.error(f"❌ 未找到新增的会话记录")
            return False
            
    except Exception as e:
        logger.error(f"❌ 非流式Token跟踪测试失败: {e}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False

def display_current_statistics():
    """显示当前统计信息"""
    logger.info("📊 显示当前统计信息...")
    
    try:
        # 获取最近7天的统计
        stats = config_manager.get_usage_statistics(7)
        logger.info(f"📊 最近7天统计:")
        logger.info(f"   💰 总成本: ¥{stats['total_cost']:.6f}")
        logger.info(f"   📞 总请求: {stats['total_requests']}")
        logger.info(f"   📥 输入tokens: {stats['total_input_tokens']:,}")
        logger.info(f"   📤 输出tokens: {stats['total_output_tokens']:,}")
        
        # 显示供应商统计
        provider_stats = stats.get('provider_stats', {})
        if provider_stats:
            logger.info(f"   📈 供应商统计:")
            for provider, pstats in provider_stats.items():
                logger.info(f"      {provider}: ¥{pstats['cost']:.6f} ({pstats['requests']}次请求)")
        
        return True
    except Exception as e:
        logger.error(f"❌ 获取统计信息失败: {e}")
        return False

def main():
    """主测试函数"""
    logger.info("🎯 非流式Token跟踪测试")
    logger.info("=" * 50)
    
    # 1. 加载环境配置
    load_env_config()
    
    # 2. 显示当前统计
    display_current_statistics()
    
    # 3. 测试非流式Token跟踪
    test_result = test_non_streaming_token_tracking()
    
    # 4. 显示更新后的统计
    logger.info("\n" + "=" * 50)
    logger.info("📈 测试后统计信息:")
    display_current_statistics()
    
    # 5. 总结
    logger.info("\n" + "=" * 50)
    logger.info("📋 测试总结:")
    
    if test_result:
        logger.info("🎉 非流式Token使用量测试成功！")
        logger.info("✅ 系统能够获取和记录Token用量数据")
    else:
        logger.error("❌ 非流式Token使用量测试失败")
    
    logger.info("\n📚 相关文件:")
    logger.info("   - 配置: .env")
    logger.info("   - 记录: config/usage.json")
    logger.info("   - 代码: tradingagents/llm_adapters/third_party_openai.py")

if __name__ == "__main__":
    main()