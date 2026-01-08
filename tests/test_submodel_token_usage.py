#!/usr/bin/env python3
"""
Submodel LLM服务Token使用量测试脚本
测试在使用submodel提供的LLM服务时token用量数据能否正确获取
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
from tradingagents.llm_adapters.openai_compatible_base import ChatCustomOpenAI, create_openai_compatible_llm
from tradingagents.config.config_manager import config_manager, token_tracker
from tradingagents.utils.logging_manager import get_logger
from langchain_core.messages import HumanMessage, SystemMessage

logger = get_logger('default')

def load_env_config():
    """加载环境配置"""
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(env_file, override=True)
        logger.info("✅ 环境配置加载成功")
    else:
        logger.warning("⚠️ .env文件未找到")

def test_submodel_openai_endpoint():
    """测试submodel OpenAI端点的token用量获取"""
    logger.info("🧪 测试submodel OpenAI端点...")
    
    # 获取API配置
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = "https://llm.submodel.ai/v1"
    
    if not api_key:
        logger.error("❌ 未配置OPENAI_API_KEY环境变量")
        return False
    
    try:
        # 创建自定义OpenAI适配器
        logger.info(f"🚀 初始化submodel OpenAI适配器...")
        logger.info(f"   API Base: {base_url}")
        
        llm = ChatCustomOpenAI(
            model="Qwen/Qwen3-235B-A22B-Instruct-2507",  # 使用用户实际使用的模型
            api_key=api_key,
            base_url=base_url,
            temperature=0.7,
            max_tokens=200
        )
        
        # 生成唯一会话ID
        session_id = f"submodel_test_{int(time.time())}"
        logger.info(f"📝 会话ID: {session_id}")
        
        # 测试消息
        messages = [
            SystemMessage(content="你是一个专业的股票分析师，请提供简洁准确的分析。"),
            HumanMessage(content="请简单分析一下当前A股市场的整体趋势，不超过50字。")
        ]
        
        logger.info(f"🚀 发送测试请求...")
        
        # 记录测试前的使用记录数量
        initial_records = config_manager.load_usage_records()
        initial_count = len(initial_records)
        logger.info(f"📊 测试前记录数: {initial_count}")
        
        # 调用LLM（自动记录token使用）
        response = llm.invoke(
            messages,
            session_id=session_id,
            analysis_type="market_analysis"
        )
        
        logger.info(f"✅ 收到响应:")
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
                
                # 验证数据是否真实
                if record.input_tokens > 0 and record.output_tokens > 0:
                    logger.info(f"✅ Token用量数据获取成功且真实")
                    return True
                else:
                    logger.warning(f"⚠️ Token用量数据为0，可能不是真实数据")
                    return False
        else:
            logger.error(f"❌ 未找到新增的会话记录")
            return False
            
    except Exception as e:
        logger.error(f"❌ submodel OpenAI测试失败: {e}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False

def test_create_openai_compatible_llm():
    """测试create_openai_compatible_llm工厂函数"""
    logger.info("🔧 测试create_openai_compatible_llm工厂函数...")
    
    try:
        # 获取API配置
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("❌ 未配置OPENAI_API_KEY环境变量")
            return False
        
        # 使用工厂函数创建自定义OpenAI适配器
        llm = create_openai_compatible_llm(
            provider="custom_openai",
            model="Qwen/Qwen3-235B-A22B-Instruct-2507",
            api_key=api_key,
            base_url="https://llm.submodel.ai/v1",
            temperature=0.7,
            max_tokens=100
        )
        
        logger.info(f"✅ 工厂函数创建适配器成功")
        logger.info(f"   供应商: {llm.provider_name}")
        logger.info(f"   模型: {llm.model_name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 工厂函数测试失败: {e}")
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

def check_token_tracking_status():
    """检查token跟踪状态"""
    logger.info("🔍 检查token跟踪状态...")
    
    # 检查配置管理器
    logger.info(f"🔧 配置管理器状态:")
    logger.info(f"   配置目录: {config_manager.config_dir}")
    logger.info(f"   使用记录文件: {config_manager.usage_file.exists()}")
    logger.info(f"   定价配置文件: {config_manager.pricing_file.exists()}")
    
    # 检查token跟踪器
    logger.info(f"📊 Token跟踪器状态:")
    logger.info(f"   启用状态: True")
    
    # 检查定价配置
    try:
        from web.components.pricing_config import load_pricing_config
        pricing_config = load_pricing_config()
        logger.info(f"💰 定价配置:")
        for provider, prices in pricing_config.items():
            if isinstance(prices, dict) and "input_price" in prices:
                logger.info(f"   {provider}: 输入¥{prices['input_price']}/1K, 输出¥{prices['output_price']}/1K")
            else:
                logger.info(f"   {provider}: {prices}")
    except Exception as e:
        logger.error(f"❌ 定价配置检查失败: {e}")

def main():
    """主测试函数"""
    logger.info("🎯 Submodel LLM服务Token使用量测试")
    logger.info("=" * 50)
    
    # 1. 加载环境配置
    load_env_config()
    
    # 2. 检查token跟踪状态
    check_token_tracking_status()
    
    # 3. 显示当前统计
    display_current_statistics()
    
    # 4. 测试工厂函数
    factory_test_result = test_create_openai_compatible_llm()
    
    # 5. 测试submodel OpenAI端点
    api_test_result = test_submodel_openai_endpoint()
    
    # 6. 显示更新后的统计
    logger.info("\n" + "=" * 50)
    logger.info("📈 测试后统计信息:")
    display_current_statistics()
    
    # 7. 总结
    logger.info("\n" + "=" * 50)
    logger.info("📋 测试总结:")
    
    if factory_test_result:
        logger.info("✅ 工厂函数测试成功")
    else:
        logger.error("❌ 工厂函数测试失败")
    
    if api_test_result:
        logger.info("🎉 Submodel LLM服务Token使用量测试成功！")
        logger.info("✅ 系统能够正确获取和记录submodel LLM服务的token用量数据")
    else:
        logger.error("❌ Submodel LLM服务Token使用量测试失败")
        logger.info("💡 可能的原因:")
        logger.info("   1. API密钥配置不正确")
        logger.info("   2. 网络连接问题")
        logger.info("   3. submodel服务端未返回token用量信息")
        logger.info("   4. Token跟踪功能配置问题")
    
    logger.info("\n📚 相关文件:")
    logger.info("   - 配置: .env")
    logger.info("   - 记录: config/usage.json")
    logger.info("   - 代码: tradingagents/llm_adapters/openai_compatible_base.py")

if __name__ == "__main__":
    main()
