#!/usr/bin/env python3
"""
分析500错误的具体原因
既然服务器正常，500错误很可能是参数不兼容导致的
"""

import json
import sys
sys.path.append('/root/TradingAgents')

from tradingagents.llm_adapters.specialized_model_adapters import (
    create_specialized_adapter,
    get_model_parameter_compatibility
)
from tradingagents.utils.logging_manager import get_logger

logger = get_logger('error_analysis')


def analyze_gpt_oss_parameters():
    """分析GPT-OSS模型的参数问题"""
    logger.info("🔍 分析 GPT-OSS 120B 模型参数问题")
    logger.info("=" * 50)
    
    # 从日志中可以看到使用的是 openai/gpt-oss-120b 模型
    model_name = "gpt-oss"
    
    try:
        adapter = create_specialized_adapter(model_name)
        
        # 获取模型信息
        model_info = adapter.get_model_info()
        logger.info(f"目标模型: {model_info['name']}")
        logger.info(f"模型ID: {model_info['model_id']}")
        
        # 检查参数兼容性
        compatibility = get_model_parameter_compatibility()
        gpt_oss_compat = compatibility.get(model_name, {})
        
        logger.info(f"\n📋 GPT-OSS 参数兼容性:")
        supported = [k for k, v in gpt_oss_compat.items() if v]
        unsupported = [k for k, v in gpt_oss_compat.items() if not v]
        
        logger.info(f"✅ 支持的参数: {supported}")
        logger.info(f"❌ 不支持的参数: {unsupported}")
        
        return adapter, gpt_oss_compat
        
    except Exception as e:
        logger.error(f"❌ 创建适配器失败: {e}")
        return None, {}


def test_problematic_parameters():
    """测试可能导致500错误的参数组合"""
    logger.info("\n🧪 测试可能导致500错误的参数组合")
    logger.info("=" * 45)
    
    adapter, compat = analyze_gpt_oss_parameters()
    if not adapter:
        return
    
    # 模拟可能导致500错误的参数
    problematic_scenarios = [
        {
            'name': '场景1: 包含function_call',
            'params': {
                'temperature': 0.7,
                'max_tokens': 1000,
                'function_call': 'auto',  # GPT-OSS可能不完全支持
                'functions': [{'name': 'test'}]
            }
        },
        {
            'name': '场景2: 复杂的logit_bias',
            'params': {
                'temperature': 0.7,
                'max_tokens': 1000,
                'logit_bias': {
                    '123': 0.5,
                    '456': -0.3,
                    '789': 1.0
                }
            }
        },
        {
            'name': '场景3: 混合多种可能问题参数',
            'params': {
                'temperature': 0.7,
                'max_tokens': 1000,
                'top_p': 0.9,
                'frequency_penalty': 0.1,
                'presence_penalty': 0.2,
                'stop': ['END', 'STOP'],
                'function_call': 'none',
                'logit_bias': {'50256': -100}  # 常见的EOS token
            }
        },
        {
            'name': '场景4: 可能的数值范围问题',
            'params': {
                'temperature': 2.0,  # 较高的温度值
                'max_tokens': 4096,  # 较大的token数
                'top_p': 1.0,
                'frequency_penalty': 2.0,  # 较高的penalty
                'presence_penalty': 2.0
            }
        }
    ]
    
    for scenario in problematic_scenarios:
        logger.info(f"\n🔬 {scenario['name']}")
        logger.info(f"   原始参数: {list(scenario['params'].keys())}")
        
        try:
            # 使用适配器过滤参数
            filtered_params = adapter._filter_model_specific_params(scenario['params'])
            logger.info(f"   过滤后参数: {list(filtered_params.keys())}")
            
            # 检查被过滤的参数
            removed = set(scenario['params'].keys()) - set(filtered_params.keys())
            if removed:
                logger.info(f"   🛡️ 已过滤: {list(removed)}")
            
            # 检查参数值是否在合理范围内
            warnings = []
            for key, value in filtered_params.items():
                if key == 'temperature' and (value < 0 or value > 2):
                    warnings.append(f"temperature={value} 超出推荐范围[0,2]")
                elif key == 'top_p' and (value < 0 or value > 1):
                    warnings.append(f"top_p={value} 超出有效范围[0,1]")
                elif key in ['frequency_penalty', 'presence_penalty'] and (value < -2 or value > 2):
                    warnings.append(f"{key}={value} 超出推荐范围[-2,2]")
            
            if warnings:
                logger.warning(f"   ⚠️ 参数范围警告: {'; '.join(warnings)}")
            else:
                logger.info(f"   ✅ 参数值在合理范围内")
                
        except Exception as e:
            logger.error(f"   ❌ 参数处理失败: {e}")


def analyze_request_format():
    """分析请求格式问题"""
    logger.info("\n📝 分析请求格式问题")
    logger.info("=" * 25)
    
    # 从错误日志中提取的信息
    log_info = {
        'model': 'openai/gpt-oss-120b',
        'message_count': 2,
        'message_contents': [
            '你是一位专业的股票技术分析师，与其他分析师协作。使用提供的工具来获取和分析股票数据。如果你无法完全回',
            '600519'
        ]
    }
    
    logger.info(f"📊 错误日志分析:")
    logger.info(f"   模型: {log_info['model']}")
    logger.info(f"   消息数量: {log_info['message_count']}")
    logger.info(f"   消息1长度: {len(log_info['message_contents'][0])} 字符")
    logger.info(f"   消息2: {log_info['message_contents'][1]}")
    
    # 分析可能的问题
    issues = []
    
    # 检查消息格式
    if log_info['message_count'] == 2:
        if len(log_info['message_contents'][0]) > 0 and len(log_info['message_contents'][1]) < 10:
            issues.append("消息格式可能不正确：第一条很长，第二条很短")
    
    # 检查消息内容
    first_msg = log_info['message_contents'][0]
    if first_msg.endswith('如果你无法完全回'):
        issues.append("第一条消息似乎被截断了")
    
    # 检查股票代码格式
    stock_code = log_info['message_contents'][1]
    if stock_code == '600519':
        logger.info("   股票代码: 600519 (茅台) - 格式正确")
    
    if issues:
        logger.warning(f"   ⚠️ 发现的问题:")
        for issue in issues:
            logger.warning(f"     - {issue}")
    else:
        logger.info("   ✅ 消息格式看起来正常")


def suggest_solutions():
    """提供解决方案建议"""
    logger.info("\n💡 解决方案建议")
    logger.info("=" * 20)
    
    solutions = [
        {
            'priority': '高',
            'solution': '使用参数过滤适配器',
            'description': '确保传递给GPT-OSS的参数都是它支持的',
            'action': '在调用前使用 adapter._filter_model_specific_params()'
        },
        {
            'priority': '高', 
            'solution': '检查消息完整性',
            'description': '确保system message和user message都是完整的',
            'action': '验证消息内容没有被意外截断'
        },
        {
            'priority': '中',
            'solution': '参数值范围检查',
            'description': '确保temperature、top_p等参数在有效范围内',
            'action': '添加参数值验证逻辑'
        },
        {
            'priority': '中',
            'solution': '降级到更稳定的模型',
            'description': '如果GPT-OSS不稳定，可以切换到其他模型',
            'action': '使用qwen-instruct或glm-4.5作为备选'
        },
        {
            'priority': '低',
            'solution': '添加重试机制',
            'description': '对500错误实施指数退避重试',
            'action': '在适配器中添加自动重试逻辑'
        }
    ]
    
    for sol in solutions:
        logger.info(f"🔧 [{sol['priority']}优先级] {sol['solution']}")
        logger.info(f"   描述: {sol['description']}")
        logger.info(f"   行动: {sol['action']}\n")


def create_safe_gpt_oss_example():
    """创建安全的GPT-OSS调用示例"""
    logger.info("📋 创建安全的GPT-OSS调用示例")
    logger.info("=" * 35)
    
    try:
        # 创建适配器
        adapter = create_specialized_adapter("gpt-oss")
        
        # 安全参数 - 只使用确定支持的参数
        safe_params = {
            'temperature': 0.7,
            'max_tokens': 1000,
            'top_p': 0.9,
            'frequency_penalty': 0.1,
            'presence_penalty': 0.1,
            'stop': ['END']
        }
        
        # 过滤参数
        filtered_params = adapter._filter_model_specific_params(safe_params)
        
        logger.info(f"✅ 安全参数配置:")
        for key, value in filtered_params.items():
            logger.info(f"   {key}: {value}")
        
        # 示例消息
        from langchain_core.messages import SystemMessage, HumanMessage
        
        messages = [
            SystemMessage(content="你是一位专业的股票技术分析师。"),
            HumanMessage(content="请分析股票代码600519的技术指标。")
        ]
        
        logger.info(f"\n📝 示例消息格式:")
        for i, msg in enumerate(messages):
            logger.info(f"   消息{i+1}: {type(msg).__name__} - {msg.content[:50]}...")
        
        logger.info(f"\n🚀 这样的配置应该能避免500错误")
        
        return filtered_params, messages
        
    except Exception as e:
        logger.error(f"❌ 创建示例失败: {e}")
        return {}, []


def main():
    """主函数"""
    logger.info("🔍 分析500错误的根本原因")
    logger.info("=" * 60)
    logger.info("既然服务器正常，错误很可能是参数不兼容导致的\n")
    
    # 1. 分析GPT-OSS参数兼容性
    analyze_gpt_oss_parameters()
    
    # 2. 测试问题参数
    test_problematic_parameters()
    
    # 3. 分析请求格式
    analyze_request_format()
    
    # 4. 提供解决方案
    suggest_solutions()
    
    # 5. 创建安全示例
    create_safe_gpt_oss_example()
    
    logger.info("\n" + "=" * 60)
    logger.info("🎯 结论: 500错误很可能是由于参数不兼容导致的")
    logger.info("💡 建议: 使用我们重构的专用适配器来自动过滤不兼容参数")


if __name__ == "__main__":
    main()