#!/usr/bin/env python3
"""
测试Token使用统计功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入必要的模块
from web.utils.analysis_runner import get_session_token_usage
from tradingagents.config.config_manager import config_manager
import json

def test_get_session_token_usage():
    """测试get_session_token_usage函数"""
    
    print("=== 测试get_session_token_usage函数 ===")
    
    # 1. 测试一个存在的session_id
    existing_session_id = "analysis_d6990214_20250908_174101"
    print(f"\n1. 测试存在的session_id: {existing_session_id}")
    
    # 检查usage.json文件
    usage_file = Path("config/usage.json")
    if usage_file.exists():
        with open(usage_file, 'r', encoding='utf-8') as f:
            usage_data = json.load(f)
            print(f"   usage.json中记录总数: {len(usage_data)}")
            
            # 查找匹配的记录
            matching_records = [record for record in usage_data if record.get('session_id') == existing_session_id]
            print(f"   匹配的记录数: {len(matching_records)}")
            
            if matching_records:
                total_input = sum(record['input_tokens'] for record in matching_records)
                total_output = sum(record['output_tokens'] for record in matching_records)
                total_cost = sum(record['cost'] for record in matching_records)
                print(f"   总输入tokens: {total_input}")
                print(f"   总输出tokens: {total_output}")
                print(f"   总成本: {total_cost:.6f}")
    else:
        print("   usage.json文件不存在")
    
    # 调用get_session_token_usage函数
    result = get_session_token_usage(existing_session_id)
    print(f"   get_session_token_usage返回结果: {result}")
    
    # 2. 测试一个不存在的session_id
    non_existing_session_id = "analysis_nonexistent_20250908_123456"
    print(f"\n2. 测试不存在的session_id: {non_existing_session_id}")
    
    result = get_session_token_usage(non_existing_session_id)
    print(f"   get_session_token_usage返回结果: {result}")
    
    # 3. 测试None session_id
    print(f"\n3. 测试None session_id")
    result = get_session_token_usage(None)
    print(f"   get_session_token_usage返回结果: {result}")
    
    # 4. 检查定价配置
    print(f"\n4. 检查定价配置")
    pricing_config = Path("config/pricing_config.json")
    if pricing_config.exists():
        with open(pricing_config, 'r', encoding='utf-8') as f:
            pricing_data = json.load(f)
            print(f"   pricing_config.json内容: {pricing_data}")
    else:
        print("   pricing_config.json文件不存在")
    
    # 5. 检查config manager中的记录
    print(f"\n5. 检查config manager中的记录")
    records = config_manager.load_usage_records()
    print(f"   config_manager加载的记录数: {len(records)}")
    
    if records:
        # 显示前几个记录的session_id
        print("   前5个记录的session_id:")
        for i, record in enumerate(records[:5]):
            print(f"     {i+1}. {record.session_id}")

if __name__ == "__main__":
    test_get_session_token_usage()
