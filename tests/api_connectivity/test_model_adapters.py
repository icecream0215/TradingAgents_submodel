#!/usr/bin/env python3
"""
9大模型适配器请求格式测试工具
检查每个模型适配器的请求格式和实际适配情况
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from tradingagents.utils.logging_manager import get_logger
logger = get_logger('model_test')

class ModelAdapterTester:
    """模型适配器测试器"""
    
    def __init__(self):
        self.test_results = {}
        self.adapters_info = {}
        
    def test_specialized_adapters(self):
        """测试专用适配器"""
        print("🧪 测试专用适配器")
        print("=" * 60)
        
        try:
            from tradingagents.llm_adapters.specialized_model_adapters import (
                SPECIALIZED_ADAPTERS, 
                create_specialized_adapter,
                test_specialized_adapters
            )
            
            print(f"📋 发现 {len(SPECIALIZED_ADAPTERS)} 个专用适配器:")
            
            for i, (model_name, adapter_class) in enumerate(SPECIALIZED_ADAPTERS.items(), 1):
                print(f"   {i}. {model_name}: {adapter_class.__name__}")
                
                # 测试适配器创建
                try:
                    adapter = create_specialized_adapter(model_name)
                    model_info = adapter.get_model_info()
                    
                    self.adapters_info[model_name] = {
                        'class': adapter_class.__name__,
                        'task_type': model_info.get('task_type'),
                        'priority': model_info.get('priority'),
                        'temperature': adapter.temperature,
                        'max_tokens': adapter.max_tokens,
                        'status': '✅ 创建成功'
                    }
                    
                    print(f"      ✅ 创建成功 - 任务类型: {model_info.get('task_type')}")
                    
                except Exception as e:
                    self.adapters_info[model_name] = {
                        'class': adapter_class.__name__,
                        'status': f'❌ 创建失败: {e}',
                        'error': str(e)
                    }
                    print(f"      ❌ 创建失败: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ 专用适配器模块导入失败: {e}")
            return False
    
    def test_third_party_openai(self):
        """测试第三方OpenAI适配器"""
        print(f"\\n🔍 测试第三方OpenAI适配器")
        print("-" * 40)
        
        try:
            from tradingagents.llm_adapters.third_party_openai import ThirdPartyOpenAI
            
            # 测试基础创建
            adapter = ThirdPartyOpenAI(
                model="openai/gpt-oss-120b",
                api_key=os.getenv('OPENAI_API_KEY'),
                base_url="https://llm.submodel.ai/v1"
            )
            
            print(f"✅ ThirdPartyOpenAI适配器创建成功")
            print(f"   模型: {adapter.model_name}")
            print(f"   基础URL: {adapter.openai_api_base}")
            print(f"   温度: {adapter.temperature}")
            print(f"   最大Token: {adapter.max_tokens}")
            
            self.adapters_info['third_party_openai'] = {
                'class': 'ThirdPartyOpenAI',
                'model': adapter.model_name,
                'base_url': adapter.openai_api_base,
                'status': '✅ 正常'
            }
            
            return True
            
        except Exception as e:
            print(f"❌ ThirdPartyOpenAI适配器测试失败: {e}")
            self.adapters_info['third_party_openai'] = {
                'class': 'ThirdPartyOpenAI',
                'status': f'❌ 失败: {e}'
            }
            return False
    
    def test_dashscope_adapter(self):
        """测试阿里百炼适配器"""
        print(f"\\n🔍 测试阿里百炼适配器")
        print("-" * 40)
        
        try:
            from tradingagents.llm_adapters.dashscope_adapter import ChatDashScope
            
            api_key = os.getenv('DASHSCOPE_API_KEY')
            if api_key and api_key != 'your_dashscope_api_key_here':
                adapter = ChatDashScope(
                    model="qwen-turbo",
                    api_key=api_key
                )
                
                print(f"✅ ChatDashScope适配器创建成功")
                print(f"   模型: {adapter.model}")
                print(f"   温度: {adapter.temperature}")
                print(f"   最大Token: {adapter.max_tokens}")
                
                self.adapters_info['dashscope'] = {
                    'class': 'ChatDashScope',
                    'model': adapter.model,
                    'api_key_configured': True,
                    'status': '✅ 正常'
                }
            else:
                print(f"⚠️ DASHSCOPE_API_KEY未配置，跳过实际测试")
                self.adapters_info['dashscope'] = {
                    'class': 'ChatDashScope',
                    'api_key_configured': False,
                    'status': '⚠️ API密钥未配置'
                }
            
            return True
            
        except Exception as e:
            print(f"❌ DashScope适配器测试失败: {e}")
            self.adapters_info['dashscope'] = {
                'class': 'ChatDashScope',
                'status': f'❌ 失败: {e}'
            }
            return False
    
    def test_deepseek_adapter(self):
        """测试DeepSeek适配器"""
        print(f"\\n🔍 测试DeepSeek适配器")
        print("-" * 40)
        
        try:
            from tradingagents.llm_adapters.deepseek_adapter import ChatDeepSeek
            
            api_key = os.getenv('DEEPSEEK_API_KEY')
            if api_key and api_key != 'your_deepseek_api_key_here':
                adapter = ChatDeepSeek(
                    model="deepseek-chat",
                    api_key=api_key
                )
                
                print(f"✅ ChatDeepSeek适配器创建成功")
                print(f"   模型: {adapter.model_name}")
                print(f"   基础URL: {adapter.openai_api_base}")
                print(f"   温度: {adapter.temperature}")
                
                self.adapters_info['deepseek'] = {
                    'class': 'ChatDeepSeek',
                    'model': adapter.model_name,
                    'api_key_configured': True,
                    'status': '✅ 正常'
                }
            else:
                print(f"⚠️ DEEPSEEK_API_KEY未配置，跳过实际测试")
                self.adapters_info['deepseek'] = {
                    'class': 'ChatDeepSeek',
                    'api_key_configured': False,
                    'status': '⚠️ API密钥未配置'
                }
            
            return True
            
        except Exception as e:
            print(f"❌ DeepSeek适配器测试失败: {e}")
            self.adapters_info['deepseek'] = {
                'class': 'ChatDeepSeek',
                'status': f'❌ 失败: {e}'
            }
            return False
    
    def test_google_adapter(self):
        """测试Google适配器"""
        print(f"\\n🔍 测试Google适配器")
        print("-" * 40)
        
        try:
            from tradingagents.llm_adapters.google_openai_adapter import ChatGoogleOpenAI
            
            api_key = os.getenv('GOOGLE_API_KEY')
            if api_key and api_key != 'your_google_api_key_here':
                adapter = ChatGoogleOpenAI(
                    model="gemini-pro",
                    google_api_key=api_key
                )
                
                print(f"✅ ChatGoogleOpenAI适配器创建成功")
                print(f"   模型: {adapter.model}")
                print(f"   温度: {adapter.temperature}")
                
                self.adapters_info['google'] = {
                    'class': 'ChatGoogleOpenAI',
                    'model': adapter.model,
                    'api_key_configured': True,
                    'status': '✅ 正常'
                }
            else:
                print(f"⚠️ GOOGLE_API_KEY未配置，跳过实际测试")
                self.adapters_info['google'] = {
                    'class': 'ChatGoogleOpenAI',
                    'api_key_configured': False,
                    'status': '⚠️ API密钥未配置'
                }
            
            return True
            
        except Exception as e:
            print(f"❌ Google适配器测试失败: {e}")
            self.adapters_info['google'] = {
                'class': 'ChatGoogleOpenAI',
                'status': f'❌ 失败: {e}'
            }
            return False
    
    def check_request_format_compatibility(self):
        """检查请求格式兼容性"""
        print(f"\\n🔧 检查请求格式兼容性")
        print("=" * 60)
        
        compatibility_issues = []
        
        # 检查每个适配器的关键参数
        for adapter_name, info in self.adapters_info.items():
            if '✅' in info.get('status', ''):
                print(f"\\n📝 {adapter_name} 适配器:")
                print(f"   类: {info.get('class')}")
                
                # 检查特定参数
                if 'temperature' in info:
                    temp = info['temperature']
                    if temp < 0 or temp > 2:
                        compatibility_issues.append(f"{adapter_name}: temperature {temp} 超出范围 [0, 2]")
                    print(f"   温度: {temp}")
                
                if 'max_tokens' in info:
                    max_tokens = info['max_tokens']
                    if max_tokens and max_tokens > 8000:
                        compatibility_issues.append(f"{adapter_name}: max_tokens {max_tokens} 可能过大")
                    print(f"   最大Token: {max_tokens}")
                
                if 'model' in info:
                    print(f"   模型: {info['model']}")
                
                if 'task_type' in info:
                    print(f"   任务类型: {info['task_type']}")
        
        return compatibility_issues
    
    def generate_summary_report(self):
        """生成汇总报告"""
        print(f"\\n" + "=" * 60)
        print(f"📊 9大模型适配器测试汇总报告")
        print("=" * 60)
        
        total_adapters = len(self.adapters_info)
        working_adapters = len([info for info in self.adapters_info.values() if '✅' in info.get('status', '')])
        failed_adapters = len([info for info in self.adapters_info.values() if '❌' in info.get('status', '')])
        warning_adapters = len([info for info in self.adapters_info.values() if '⚠️' in info.get('status', '')])
        
        print(f"\\n📈 统计概览:")
        print(f"   总适配器数: {total_adapters}")
        print(f"   正常工作: {working_adapters} ✅")
        print(f"   配置警告: {warning_adapters} ⚠️")
        print(f"   错误失败: {failed_adapters} ❌")
        
        success_rate = (working_adapters / total_adapters * 100) if total_adapters > 0 else 0
        print(f"   成功率: {success_rate:.1f}%")
        
        print(f"\\n📋 详细状态:")
        for adapter_name, info in self.adapters_info.items():
            status = info.get('status', '未知')
            print(f"   {adapter_name}: {status}")
        
        # 检查兼容性问题
        compatibility_issues = self.check_request_format_compatibility()
        
        if compatibility_issues:
            print(f"\\n⚠️ 发现兼容性问题:")
            for issue in compatibility_issues:
                print(f"   - {issue}")
        else:
            print(f"\\n✅ 未发现兼容性问题")
        
        # 总结建议
        print(f"\\n💡 建议:")
        if failed_adapters > 0:
            print(f"   1. 检查失败的适配器依赖库是否正确安装")
        if warning_adapters > 0:
            print(f"   2. 配置缺失API密钥的适配器以获得完整功能")
        if success_rate >= 80:
            print(f"   3. 系统适配器状态良好，可以正常使用")
        else:
            print(f"   3. 需要修复更多适配器以提高系统稳定性")
    
    def run_comprehensive_test(self):
        """运行全面测试"""
        print("🚀 启动9大模型适配器全面测试")
        print("=" * 60)
        
        # 1. 测试专用适配器
        self.test_specialized_adapters()
        
        # 2. 测试第三方OpenAI适配器
        self.test_third_party_openai()
        
        # 3. 测试阿里百炼适配器
        self.test_dashscope_adapter()
        
        # 4. 测试DeepSeek适配器
        self.test_deepseek_adapter()
        
        # 5. 测试Google适配器
        self.test_google_adapter()
        
        # 6. 测试多模型适配器 - 已移除
        # self.test_multi_model_adapter()
        
        # 7. 生成汇总报告
        self.generate_summary_report()

def main():
    """主函数"""
    tester = ModelAdapterTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()