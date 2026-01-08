#!/usr/bin/env python3
"""
用户指定模型的简单使用示例
演示如何直接选择想要使用的模型
"""

import os
import sys
from langchain_core.messages import HumanMessage

# 添加项目路径
sys.path.append('/root/TradingAgents')

from tradingagents.llm_adapters.specialized_model_adapters import (
    create_specialized_adapter,
    get_adapter_by_name,
    list_available_models,
    SPECIALIZED_ADAPTERS
)
from tradingagents.utils.logging_manager import get_logger

logger = get_logger('user_model_selection')


def show_available_models():
    """显示所有可用的模型"""
    logger.info("📋 可用模型列表:")
    logger.info("=" * 50)
    
    available_models = list_available_models()
    for i, (model_name, description) in enumerate(available_models.items(), 1):
        logger.info(f"{i}. {model_name}")
        logger.info(f"   {description}")
        
        # 显示参数兼容性
        try:
            adapter = create_specialized_adapter(model_name)
            model_info = adapter.get_model_info()
            logger.info(f"   质量评分: {model_info['quality_score']}/10, 速度评分: {model_info['speed_score']}/10")
            logger.info(f"   擅长: {', '.join(model_info['task_strengths'])}")
        except Exception as e:
            logger.warning(f"   无法获取详细信息: {e}")
        
        logger.info("")


def demonstrate_user_choice():
    """演示用户直接选择模型"""
    logger.info("\n🎯 用户直接选择模型示例")
    logger.info("=" * 40)
    
    examples = [
        {
            'scenario': '用户想要代码帮助',
            'user_choice': 'qwen-coder',
            'message': '请帮我写一个快速排序算法',
            'params': {'temperature': 0.1, 'max_tokens': 2000}
        },
        {
            'scenario': '用户需要快速回答',
            'user_choice': 'glm-4.5',
            'message': '北京今天天气如何？',
            'params': {'temperature': 0.8, 'max_tokens': 100}
        },
        {
            'scenario': '用户要求深度分析',
            'user_choice': 'deepseek-r1',
            'message': '分析人工智能对就业市场的影响',
            'params': {'temperature': 0.2, 'max_tokens': 3000}
        },
        {
            'scenario': '用户想要投资建议',
            'user_choice': 'deepseek-v31',
            'message': '评估苹果公司的投资价值',
            'params': {'temperature': 0.2, 'max_tokens': 2500}
        }
    ]
    
    for example in examples:
        logger.info(f"\n💡 场景: {example['scenario']}")
        logger.info(f"👤 用户选择: {example['user_choice']}")
        logger.info(f"📝 用户问题: {example['message']}")
        
        try:
            # 用户直接指定模型
            adapter = get_adapter_by_name(example['user_choice'], **example['params'])
            
            model_info = adapter.get_model_info()
            logger.info(f"🤖 使用模型: {model_info['name']}")
            
            # 模拟参数处理
            filtered_params = adapter._filter_model_specific_params(example['params'])
            logger.info(f"🔧 安全参数: {list(filtered_params.keys())}")
            
            # 模拟消息优化
            message = HumanMessage(content=example['message'])
            optimized = adapter._optimize_messages([message])
            
            logger.info(f"✅ 准备完成，可以安全调用 {example['user_choice']}")
            
        except Exception as e:
            logger.error(f"❌ 处理失败: {e}")


def show_parameter_safety():
    """展示参数安全过滤"""
    logger.info("\n🛡️ 参数安全过滤演示")
    logger.info("=" * 35)
    
    # 模拟用户可能传入的各种参数
    risky_params = {
        'temperature': 0.7,
        'max_tokens': 1500,
        'top_p': 0.9,
        'frequency_penalty': 0.1,
        'presence_penalty': 0.2,
        'logit_bias': {'123': 0.5},      # 很多模型不支持
        'function_call': 'auto',         # 很多模型不支持
        'functions': [{'name': 'test'}], # 很多模型不支持
        'invalid_param': 'test'          # 无效参数
    }
    
    logger.info(f"用户传入参数: {list(risky_params.keys())}")
    
    test_models = ['qwen-coder', 'glm-4.5', 'deepseek-r1']
    
    for model_name in test_models:
        logger.info(f"\n🧪 测试 {model_name}:")
        
        try:
            adapter = create_specialized_adapter(model_name)
            
            # 显示过滤过程
            openai_filtered = adapter._filter_openai_params(risky_params)
            model_filtered = adapter._filter_model_specific_params(risky_params)
            
            removed = set(risky_params.keys()) - set(model_filtered.keys())
            
            logger.info(f"   原始参数: {len(risky_params)} 个")
            logger.info(f"   OpenAI过滤后: {len(openai_filtered)} 个")
            logger.info(f"   模型过滤后: {len(model_filtered)} 个")
            logger.info(f"   安全参数: {list(model_filtered.keys())}")
            if removed:
                logger.info(f"   已移除危险参数: {list(removed)}")
            
        except Exception as e:
            logger.error(f"   ❌ {model_name} 测试失败: {e}")


def interactive_model_selection():
    """交互式模型选择示例"""
    logger.info("\n🎮 交互式模型选择")
    logger.info("=" * 25)
    
    # 模拟用户交互流程
    scenarios = [
        {
            'user_input': '我想写代码',
            'recommended': ['qwen-coder'],
            'reason': '代码专家模型'
        },
        {
            'user_input': '我要快速答案',
            'recommended': ['glm-4.5'],
            'reason': '高速响应模型'
        },
        {
            'user_input': '我需要深度思考',
            'recommended': ['qwen-thinking', 'deepseek-r1'],
            'reason': '思维链和推理专家'
        },
        {
            'user_input': '我想分析股票',
            'recommended': ['deepseek-v31'],
            'reason': '金融分析专家'
        }
    ]
    
    for scenario in scenarios:
        logger.info(f"\n👤 用户说: \"{scenario['user_input']}\"")
        logger.info(f"💡 推荐模型: {', '.join(scenario['recommended'])}")
        logger.info(f"📖 推荐理由: {scenario['reason']}")
        
        # 用户选择第一个推荐模型
        chosen_model = scenario['recommended'][0]
        logger.info(f"✅ 用户选择: {chosen_model}")
        
        try:
            adapter = get_adapter_by_name(chosen_model)
            model_info = adapter.get_model_info()
            logger.info(f"🤖 已准备 {model_info['name']}")
        except Exception as e:
            logger.error(f"❌ 模型准备失败: {e}")


def main():
    """主函数"""
    logger.info("🎯 用户指定模型使用示例")
    logger.info("=" * 60)
    
    # 1. 显示可用模型
    show_available_models()
    
    # 2. 演示用户直接选择
    demonstrate_user_choice()
    
    # 3. 展示参数安全
    show_parameter_safety()
    
    # 4. 交互式选择
    interactive_model_selection()
    
    logger.info("\n" + "=" * 60)
    logger.info("🎉 总结:")
    logger.info("✅ 用户可以直接指定想要使用的模型")
    logger.info("✅ 系统自动处理参数兼容性问题")
    logger.info("✅ 提供完整的模型信息帮助用户选择")
    logger.info("✅ 无需复杂的任务类型映射")
    logger.info("✅ 简单直观的使用方式")


if __name__ == "__main__":
    main()