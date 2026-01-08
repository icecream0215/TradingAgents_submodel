#!/usr/bin/env python3
"""
AI模型请求格式测试工具
测试TradingAgents中配置的各种AI模型的请求格式和连通性
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
import asyncio

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class AIModelTester:
    """AI模型测试器"""
    
    def __init__(self):
        self.test_prompt = "你好，请简单回复一下，测试API连接。"
        self.results = {}
        
    def check_openai_compatible(self, base_url: str, api_key: str, model_name: str, test_name: str) -> Dict[str, Any]:
        """测试OpenAI兼容的API"""
        print(f"\n🔍 测试 {test_name}...")
        print(f"   模型: {model_name}")
        print(f"   接口: {base_url}")
        
        try:
            import requests
            
            # 构建请求
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model_name,
                "messages": [
                    {
                        "role": "user", 
                        "content": self.test_prompt
                    }
                ],
                "max_tokens": 100,
                "temperature": 0.7
            }
            
            print(f"   请求格式: {json.dumps(data, ensure_ascii=False, indent=2)[:200]}...")
            
            response = requests.post(
                base_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                usage = result.get('usage', {})
                
                print(f"   ✅ 请求成功")
                print(f"   响应内容: {content[:100]}...")
                print(f"   Token使用: {usage}")
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response_content": content,
                    "usage": usage,
                    "error": None
                }
            else:
                error_text = response.text
                print(f"   ❌ 请求失败")
                print(f"   错误信息: {error_text[:200]}...")
                
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": error_text[:500],
                    "response_content": None,
                    "usage": None
                }
                
        except Exception as e:
            print(f"   ❌ 测试异常: {e}")
            return {
                "success": False,
                "status_code": None,
                "error": str(e),
                "response_content": None,
                "usage": None
            }
    
    def test_third_party_openai(self) -> Dict[str, Any]:
        """测试第三方OpenAI服务 (当前使用的)"""
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            print("\n⚠️ 未配置 OPENAI_API_KEY，跳过测试")
            return {"success": False, "error": "No API key configured"}
        
        return self.check_openai_compatible(
            base_url="https://llm.submodel.ai/v1/chat/completions",
            api_key=api_key,
            model_name="openai/gpt-oss-120b",
            test_name="第三方OpenAI服务 (llm.submodel.ai)"
        )
    
    def test_deepseek(self) -> Dict[str, Any]:
        """测试DeepSeek API"""
        api_key = os.getenv('DEEPSEEK_API_KEY')
        enabled = os.getenv('DEEPSEEK_ENABLED', 'false').lower() in ['true', '1', 'yes', 'on']
        
        if not api_key or api_key == 'your_deepseek_api_key_here':
            print("\n⚠️ DeepSeek API Key 未配置，跳过测试")
            return {"success": False, "error": "No API key configured"}
        
        if not enabled:
            print("\n⚠️ DeepSeek 未启用 (DEEPSEEK_ENABLED=false)，跳过测试")
            return {"success": False, "error": "Service disabled"}
        
        return self.check_openai_compatible(
            base_url="https://api.deepseek.com/v1/chat/completions",
            api_key=api_key,
            model_name="deepseek-chat",
            test_name="DeepSeek API"
        )
    
    def test_dashscope(self) -> Dict[str, Any]:
        """测试阿里百炼 DashScope API"""
        api_key = os.getenv('DASHSCOPE_API_KEY')
        
        if not api_key or api_key == 'your_dashscope_api_key_here':
            print("\n⚠️ DashScope API Key 未配置，跳过测试")
            return {"success": False, "error": "No API key configured"}
        
        print(f"\n🔍 测试阿里百炼 DashScope API...")
        print(f"   模型: qwen-turbo")
        
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "qwen-turbo",
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": self.test_prompt
                        }
                    ]
                },
                "parameters": {
                    "max_tokens": 100
                }
            }
            
            print(f"   请求格式: {json.dumps(data, ensure_ascii=False, indent=2)[:200]}...")
            
            response = requests.post(
                "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                headers=headers,
                json=data,
                timeout=30
            )
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('output', {}).get('text', '')
                usage = result.get('usage', {})
                
                print(f"   ✅ 请求成功")
                print(f"   响应内容: {content[:100]}...")
                print(f"   Token使用: {usage}")
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response_content": content,
                    "usage": usage,
                    "error": None
                }
            else:
                error_text = response.text
                print(f"   ❌ 请求失败")
                print(f"   错误信息: {error_text[:200]}...")
                
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": error_text[:500],
                    "response_content": None,
                    "usage": None
                }
                
        except Exception as e:
            print(f"   ❌ 测试异常: {e}")
            return {
                "success": False,
                "status_code": None,
                "error": str(e),
                "response_content": None,
                "usage": None
            }
    
    def test_google_gemini(self) -> Dict[str, Any]:
        """测试Google Gemini API"""
        api_key = os.getenv('GOOGLE_API_KEY')
        
        if not api_key or api_key == 'your_google_api_key_here':
            print("\n⚠️ Google API Key 未配置，跳过测试")
            return {"success": False, "error": "No API key configured"}
        
        print(f"\n🔍 测试Google Gemini API...")
        print(f"   模型: gemini-pro")
        
        try:
            import requests
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
            
            data = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": self.test_prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": 100,
                    "temperature": 0.7
                }
            }
            
            print(f"   请求格式: {json.dumps(data, ensure_ascii=False, indent=2)[:200]}...")
            
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=data,
                timeout=30
            )
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                usage = result.get('usageMetadata', {})
                
                print(f"   ✅ 请求成功")
                print(f"   响应内容: {content[:100]}...")
                print(f"   Token使用: {usage}")
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response_content": content,
                    "usage": usage,
                    "error": None
                }
            else:
                error_text = response.text
                print(f"   ❌ 请求失败")
                print(f"   错误信息: {error_text[:200]}...")
                
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": error_text[:500],
                    "response_content": None,
                    "usage": None
                }
                
        except Exception as e:
            print(f"   ❌ 测试异常: {e}")
            return {
                "success": False,
                "status_code": None,
                "error": str(e),
                "response_content": None,
                "usage": None
            }
    
    def test_siliconflow(self) -> Dict[str, Any]:
        """测试硅基流动 API"""
        api_key = os.getenv('SILICONFLOW_API_KEY')
        
        if not api_key or api_key == 'your_siliconflow_api_key_here':
            print("\n⚠️ SiliconFlow API Key 未配置，跳过测试")
            return {"success": False, "error": "No API key configured"}
        
        return self.check_openai_compatible(
            base_url="https://api.siliconflow.cn/v1/chat/completions",
            api_key=api_key,
            model_name="qwen/Qwen2.5-7B-Instruct",
            test_name="硅基流动 SiliconFlow API"
        )
    
    def test_anthropic_claude(self) -> Dict[str, Any]:
        """测试Anthropic Claude API"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not api_key or api_key == 'your_anthropic_api_key_here':
            print("\n⚠️ Anthropic API Key 未配置，跳过测试")
            return {"success": False, "error": "No API key configured"}
        
        print(f"\n🔍 测试Anthropic Claude API...")
        print(f"   模型: claude-3-haiku-20240307")
        
        try:
            import requests
            
            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 100,
                "messages": [
                    {
                        "role": "user",
                        "content": self.test_prompt
                    }
                ]
            }
            
            print(f"   请求格式: {json.dumps(data, ensure_ascii=False, indent=2)[:200]}...")
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=30
            )
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('content', [{}])[0].get('text', '')
                usage = result.get('usage', {})
                
                print(f"   ✅ 请求成功")
                print(f"   响应内容: {content[:100]}...")
                print(f"   Token使用: {usage}")
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response_content": content,
                    "usage": usage,
                    "error": None
                }
            else:
                error_text = response.text
                print(f"   ❌ 请求失败")
                print(f"   错误信息: {error_text[:200]}...")
                
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": error_text[:500],
                    "response_content": None,
                    "usage": None
                }
                
        except Exception as e:
            print(f"   ❌ 测试异常: {e}")
            return {
                "success": False,
                "status_code": None,
                "error": str(e),
                "response_content": None,
                "usage": None
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有AI模型测试"""
        print("🚀 开始AI模型请求格式测试")
        print("=" * 60)
        
        # 测试各种AI模型
        test_methods = [
            ("third_party_openai", self.test_third_party_openai),
            ("deepseek", self.test_deepseek),
            ("dashscope", self.test_dashscope),
            ("google_gemini", self.test_google_gemini),
            ("siliconflow", self.test_siliconflow),
            ("anthropic_claude", self.test_anthropic_claude),
        ]
        
        results = {}
        
        for test_name, test_method in test_methods:
            try:
                result = test_method()
                results[test_name] = result
                time.sleep(1)  # 避免请求过于频繁
            except Exception as e:
                print(f"\n❌ {test_name} 测试出现异常: {e}")
                results[test_name] = {
                    "success": False,
                    "error": f"Test exception: {e}",
                    "status_code": None,
                    "response_content": None,
                    "usage": None
                }
        
        # 生成测试报告
        print("\n" + "=" * 60)
        print("📊 AI模型测试结果汇总")
        print("=" * 60)
        
        success_count = 0
        total_count = len(results)
        
        for test_name, result in results.items():
            status = "✅ 成功" if result["success"] else "❌ 失败"
            print(f"\n{test_name}: {status}")
            
            if result["success"]:
                success_count += 1
                print(f"   状态码: {result.get('status_code')}")
                print(f"   响应长度: {len(result.get('response_content', '')) if result.get('response_content') else 0} 字符")
                if result.get('usage'):
                    print(f"   Token使用: {result['usage']}")
            else:
                print(f"   错误原因: {result.get('error', 'Unknown error')[:100]}...")
        
        success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
        
        print(f"\n🎯 总体结果:")
        print(f"   成功率: {success_count}/{total_count} ({success_rate:.1f}%)")
        print(f"   可用模型数: {success_count}")
        
        # 给出建议
        if success_count == 0:
            print(f"\n⚠️ 建议:")
            print(f"   - 所有AI模型都无法使用")
            print(f"   - 请检查API密钥配置")
            print(f"   - 建议至少配置一个可用的AI服务")
        elif success_count < total_count:
            print(f"\n💡 建议:")
            print(f"   - 部分AI模型可用，系统可以正常工作")
            print(f"   - 建议配置更多备用AI服务提高可靠性")
        else:
            print(f"\n🎉 所有配置的AI模型都可正常使用！")
        
        return {
            "results": results,
            "summary": {
                "total_tested": total_count,
                "successful": success_count,
                "success_rate": success_rate
            }
        }

def main():
    """主函数"""
    tester = AIModelTester()
    results = tester.run_all_tests()
    
    # 保存测试结果
    try:
        import json
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = project_root / "data" / "reports" / f"ai_model_test_{timestamp}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n💾 测试报告已保存到: {report_file}")
        
    except Exception as e:
        print(f"\n⚠️ 保存报告失败: {e}")
    
    # 返回适当的退出码
    if results["summary"]["successful"] > 0:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()