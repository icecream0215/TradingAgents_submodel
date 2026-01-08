#!/usr/bin/env python3
"""
测试数据获取工具的可用性
验证所有列出的数据获取工具是否都能正常导入和调用
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入日志模块
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('test')

def test_tool_availability():
    """测试所有数据工具的可用性"""
    print("=" * 60)
    print("数据获取工具可用性测试")
    print("=" * 60)
    
    # 获取当前日期和一周前的日期
    curr_date = datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    # 测试用的股票代码
    test_ticker = "AAPL"  # 苹果公司
    test_china_ticker = "000001"  # 平安银行
    
    # 测试计数器
    total_tests = 0
    passed_tests = 0
    
    # 1. 测试 get_reddit_news (对应 get_reddit_global_news)
    total_tests += 1
    try:
        from tradingagents.dataflows.interface import get_reddit_global_news
        print(f"\n[1/22] 测试 get_reddit_global_news (get_reddit_news)...")
        result = get_reddit_global_news(week_ago, 7, 5)
        print("  ✓ 可用")
        passed_tests += 1
    except Exception as e:
        print(f"  ✗ 不可用: {e}")
    
    # 2. 测试 get_finnhub_news
    total_tests += 1
    try:
        from tradingagents.dataflows.interface import get_finnhub_news
        print(f"\n[2/22] 测试 get_finnhub_news...")
        result = get_finnhub_news(test_ticker, curr_date, 7)
        print("  ✓ 可用")
        passed_tests += 1
    except Exception as e:
        print(f"  ✗ 不可用: {e}")
    
    # 3. 测试 get_reddit_stock_info (对应 get_reddit_company_news)
    total_tests += 1
    try:
        from tradingagents.dataflows.interface import get_reddit_company_news
        print(f"\n[3/22] 测试 get_reddit_company_news (get_reddit_stock_info)...")
        result = get_reddit_company_news(test_ticker, curr_date, 7, 5)
        print("  ✓ 可用")
        passed_tests += 1
    except Exception as e:
        print(f"  ✗ 不可用: {e}")
    
    # 4. 测试 get_chinese_social_sentiment
    total_tests += 1
    try:
        from tradingagents.dataflows.chinese_finance_utils import get_chinese_social_sentiment
        print(f"\n[4/22] 测试 get_chinese_social_sentiment...")
        result = get_chinese_social_sentiment(test_ticker, curr_date)
        print("  ✓ 可用")
        passed_tests += 1
    except Exception as e:
        print(f"  ✗ 不可用: {e}")
    
    # 5. 测试 get_YFin_data
    total_tests += 1
    try:
        from tradingagents.dataflows.interface import get_YFin_data
        print(f"\n[5/22] 测试 get_YFin_data...")
        # 注意：这里可能需要有效的日期范围，使用较早的日期
        result = get_YFin_data(test_ticker, "2023-01-01", "2023-01-31")
        print("  ✓ 可用")
        passed_tests += 1
    except Exception as e:
        print(f"  ✗ 不可用: {e}")
    
    # 6. 测试 get_YFin_data_online
    total_tests += 1
    try:
        from tradingagents.dataflows.interface import get_YFin_data_online
        print(f"\n[6/22] 测试 get_YFin_data_online...")
        result = get_YFin_data_online(test_ticker, week_ago, curr_date)
        print("  ✓ 可用")
        passed_tests += 1
    except Exception as e:
        print(f"  ✗ 不可用: {e}")
    
    # 7. 测试 get_stockstats_indicators_report (离线)
    total_tests += 1
    try:
        from tradingagents.dataflows.interface import get_stock_stats_indicators_window
        print(f"\n[7/22] 测试 get_stockstats_indicators_report (离线)...")
        result = get_stock_stats_indicators_window(test_ticker, "rsi", curr_date, 30, False)
        print("  ✓ 可用")
        passed_tests += 1
    except Exception as e:
        print(f"  ✗ 不可用: {e}")
    
    # 8. 测试 get_stockstats_indicators_report_online
    total_tests += 1
    try:
        from tradingagents.dataflows.interface import get_stock_stats_indicators_window
        print(f"\n[8/22] 测试 get_stockstats_indicators_report_online...")
        result = get_stock_stats_indicators_window(test_ticker, "rsi", curr_date, 30, True)
        print("  ✓ 可用")
        passed_tests += 1
    except Exception as e:
        print(f"  ✗ 不可用: {e}")
    
    # 9. 测试 get_finnhub_company_insider_sentiment
    total_tests += 1
    try:
        from tradingagents.dataflows.interface import get_finnhub_company_insider_sentiment
        print(f"\n[9/22] 测试 get_finnhub_company_insider_sentiment...")
        result = get_finnhub_company_insider_sentiment(test_ticker, curr_date, 30)
        print("  ✓ 可用")
        passed_tests += 1
    except Exception as e:
        print(f"  ✗ 不可用: {e}")
    
    # 10. 测试 get_finnhub_company_insider_transactions
    total_tests += 1
    try:
        from tradingagents.dataflows.interface import get_finnhub_company_insider_transactions
        print(f"\n[10/22] 测试 get_finnhub_company_insider_transactions...")
        result = get_finnhub_company_insider_transactions(test_ticker, curr_date, 30)
        print("  ✓ 可用")
        passed_tests += 1
    except Exception as e:
        print(f"  ✗ 不可用: {e}")
    
    # 11. 测试 get_simfin_balance_sheet
    total_tests += 1
    try:
        from tradingagents.dataflows.interface import get_simfin_balance_sheet
        print(f"\n[11/22] 测试 get_simfin_balance_sheet...")
        result = get_simfin_balance_sheet(test_ticker, "annual", curr_date)
        print("  ✓ 可用")
        passed_tests += 1
    except Exception as e:
        print(f"  ✗ 不可用: {e}")
    
    # 12. 测试 get_simfin_cashflow
    total_tests += 1
    try:
        from tradingagents.dataflows.interface import get_simfin_cashflow
        print(f"\n[12/22] 测试 get_simfin_cashflow...")
        result = get_simfin_cashflow(test_ticker, "annual", curr_date)
        print("  ✓ 可用")
        passed_tests += 1
    except Exception as e:
        print(f"  ✗ 不可用: {e}")
    
    # 13. 测试 get_simfin_income_stmt (对应 get_simfin_income_statements)
    total_tests += 1
    try:
        from tradingagents.dataflows.interface import get_simfin_income_statements
        print(f"\n[13/22] 测试 get_simfin_income_statements (get_simfin_income_stmt)...")
        result = get_simfin_income_statements(test_ticker, "annual", curr_date)
        print("  ✓ 可用")
        passed_tests += 1
    except Exception as e:
        print(f"  ✗ 不可用: {e}")
    
    # 14. 测试 get_google_news
    total_tests += 1
    try:
        from tradingagents.dataflows.interface import get_google_news
        print(f"\n[14/22] 测试 get_google_news...")
        result = get_google_news(test_ticker, curr_date, 7)
        print("  ✓ 可用")
        passed_tests += 1
    except Exception as e:
        print(f"  ✗ 不可用: {e}")
    
    # 15. 测试 get_realtime_stock_news
    total_tests += 1
    try:
        # 这个工具可能在tools目录中，但我们无法读取那些文件
        # 尝试从interface.py导入（如果存在）
        from tradingagents.dataflows.interface import get_realtime_stock_news
        print(f"\n[15/22] 测试 get_realtime_stock_news...")
        result = get_realtime_stock_news(test_ticker, curr_date)
        print("  ✓ 可用")
        passed_tests += 1
    except ImportError:
        print(f"\n[15/22] 测试 get_realtime_stock_news...")
        print("  ? 未找到实现")
    except Exception as e:
        print(f"  ✗ 不可用: {e}")
    
    # 16. 测试 get_stock_news_openai
    total_tests += 1
    try:
        from tradingagents.dataflows.interface import get_stock_news_openai
        print(f"\n[16/22] 测试 get_stock_news_openai...")
        result = get_stock_news_openai(test_ticker, curr_date)
        print("  ✓ 可用")
        passed_tests += 1
    except Exception as e:
        print(f"  ✗ 不可用: {e}")
    
    # 17. 测试 get_global_news_openai
    total_tests += 1
    try:
        from tradingagents.dataflows.interface import get_global_news_openai
        print(f"\n[17/22] 测试 get_global_news_openai...")
        result = get_global_news_openai(curr_date)
        print("  ✓ 可用")
        passed_tests += 1
    except Exception as e:
        print(f"  ✗ 不可用: {e}")
    
    # 18. 测试 get_stock_fundamentals_unified (对应 get_fundamentals_openai)
    total_tests += 1
    try:
        from tradingagents.dataflows.interface import get_fundamentals_openai
        print(f"\n[18/22] 测试 get_fundamentals_openai (get_stock_fundamentals_unified)...")
        result = get_fundamentals_openai(test_ticker, curr_date)
        print("  ✓ 可用")
        passed_tests += 1
    except Exception as e:
        print(f"  ✗ 不可用: {e}")
    
    # 19. 测试 get_stock_market_data_unified (对应 get_stock_data_by_market)
    total_tests += 1
    try:
        from tradingagents.dataflows.interface import get_stock_data_by_market
        print(f"\n[19/22] 测试 get_stock_data_by_market (get_stock_market_data_unified)...")
        result = get_stock_data_by_market(test_ticker, week_ago, curr_date)
        print("  ✓ 可用")
        passed_tests += 1
    except Exception as e:
        print(f"  ✗ 不可用: {e}")
    
    # 20. 测试 get_stock_news_unified
    total_tests += 1
    try:
        from tradingagents.tools.unified_news_tool import create_unified_news_tool
        print(f"\n[20/22] 测试 get_stock_news_unified...")
        # 创建一个模拟的toolkit对象
        class MockToolkit:
            def __init__(self):
                pass
        
        mock_toolkit = MockToolkit()
        unified_news_tool = create_unified_news_tool(mock_toolkit)
        # 注意：我们不实际调用工具，因为需要真实的toolkit对象
        print("  ✓ 工具创建函数可用")
        passed_tests += 1
    except Exception as e:
        print(f"  ✗ 不可用: {e}")
    
    # 21. 测试 get_stock_sentiment_unified
    total_tests += 1
    try:
        # 这个工具可能还没有实现，或者实现在其他地方
        print(f"\n[21/22] 测试 get_stock_sentiment_unified...")
        print("  ? 未找到实现")
    except Exception as e:
        print(f"  ✗ 不可用: {e}")
    
    # 22. 测试 get_china_market_overview
    total_tests += 1
    try:
        # 这个工具可能还没有实现，或者实现在其他地方
        print(f"\n[22/22] 测试 get_china_market_overview...")
        print("  ? 未找到实现")
    except Exception as e:
        print(f"  ✗ 不可用: {e}")
    
    # 输出总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {total_tests - passed_tests}")
    print(f"成功率: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 所有数据工具都可用！")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} 个工具不可用，需要进一步检查。")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = test_tool_availability()
    sys.exit(0 if success else 1)
