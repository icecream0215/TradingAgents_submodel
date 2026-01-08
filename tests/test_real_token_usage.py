#!/usr/bin/env python3
"""
真实Token使用量测试脚本
测试在实际应用程序运行过程中，Token用量数据能否正确获取
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
from tradingagents.config.config_manager import config_manager, token_tracker
from tradingagents.utils.logging_manager import get_logger

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

def test_real_analysis():
    """测试真实分析过程中的Token使用量"""
    logger.info("🧪 测试真实分析过程中的Token使用量...")
    
    try:
        # 导入必要的模块
        from web.utils.analysis_runner import run_stock_analysis
        
        # 记录测试前的使用记录数量
        initial_records = config_manager.load_usage_records()
        initial_count = len(initial_records)
        logger.info(f"📊 测试前记录数: {initial_count}")
        
        # 执行一个简单的分析
        results = run_stock_analysis(
            stock_symbol="000001",
            analysis_date="2025-09-08",
            analysts=["market"],
            research_depth=1,
            llm_provider="openai",
            llm_model="Qwen/Qwen3-235B-A22B-Instruct-2507",
            market_type="A股"
        )
        
        if results['success']:
            logger.info("✅ 分析执行成功")
            session_id = results.get('session_id')
            if session_id:
                logger.info(f"📝 会话ID: {session_id}")
                
                # 查看会话成本
                session_cost = token_tracker.get_session_cost(session_id)
                logger.info(f"💰 本次分析成本: ¥{session_cost:.6f}")
            else:
                logger.warning("⚠️ 未获取到会话ID")
        else:
            logger.error(f"❌ 分析执行失败: {results.get('error', 'Unknown error')}")
            return False
            
        # 等待记录保存
        time.sleep(2)
        
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
                    if record.input_tokens != 8000 and record.output_tokens != 4000:
                        logger.info(f"✅ Token用量数据获取成功且真实（非8000:4000）")
                        return True
                    else:
                        logger.warning(f"⚠️ Token用量数据为8000:4000，可能不是真实数据")
                        return False
                else:
                    logger.warning(f"⚠️ Token用量数据为0，可能不是真实数据")
                    return False
        else:
            logger.error(f"❌ 未找到新增的会话记录")
            return False
            
    except Exception as e:
        logger.error(f"❌ 真实分析测试失败: {e}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False

def main():
    """主测试函数"""
    logger.info("🎯 真实Token使用量测试")
    logger.info("=" * 50)
    
    # 1. 加载环境配置
    load_env_config()
    
    # 2. 显示当前统计
    display_current_statistics()
    
    # 3. 测试真实分析过程中的Token使用量
    api_test_result = test_real_analysis()
    
    # 4. 显示更新后的统计
    logger.info("\n" + "=" * 50)
    logger.info("📈 测试后统计信息:")
    display_current_statistics()
    
    # 5. 总结
    logger.info("\n" + "=" * 50)
    logger.info("📋 测试总结:")
    
    if api_test_result:
        logger.info("🎉 真实分析过程中的Token使用量测试成功！")
        logger.info("✅ 系统能够在实际运行时正确获取和记录真实的Token用量数据")
    else:
        logger.error("❌ 真实分析过程中的Token使用量测试失败")
        logger.info("💡 可能的原因:")
        logger.info("   1. API密钥配置不正确")
        logger.info("   2. 网络连接问题")
        logger.info("   3. 第三方服务端未返回token用量信息")
        logger.info("   4. Token跟踪功能配置问题")
    
    logger.info("\n📚 相关文件:")
    logger.info("   - 配置: .env")
    logger.info("   - 记录: config/usage.json")

if __name__ == "__main__":
    main()
