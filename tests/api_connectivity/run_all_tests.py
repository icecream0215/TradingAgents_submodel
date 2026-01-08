#!/usr/bin/env python3
"""
综合API连通性测试运行器
运行所有API的连通性测试并生成详细报告

包含的API测试：
1. FinnHub API - 美股数据
2. AKShare API - A股和港股数据  
3. News & Social APIs - 新闻和社交媒体数据
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import json

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from test_finnhub_api import FinnHubAPITester
from test_akshare_api import AKShareAPITester
from test_news_social_api import NewsAndSocialAPITester

class ComprehensiveAPITester:
    """综合API测试器"""
    
    def __init__(self):
        self.test_results = {}
        self.test_timestamp = datetime.now()
        
    def run_all_api_tests(self) -> Dict[str, Any]:
        """运行所有API测试"""
        print("🌟 开始综合API连通性测试")
        print("=" * 60)
        print(f"测试时间: {self.test_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        all_results = {}
        
        # 1. FinnHub API测试
        print("\n📊 第1部分: FinnHub API测试")
        print("-" * 40)
        try:
            finnhub_tester = FinnHubAPITester()
            all_results['finnhub'] = finnhub_tester.run_all_tests()
        except Exception as e:
            print(f"❌ FinnHub测试异常: {e}")
            all_results['finnhub'] = {'error': str(e)}
        
        # 2. AKShare API测试
        print("\n📈 第2部分: AKShare API测试")
        print("-" * 40)
        try:
            akshare_tester = AKShareAPITester()
            all_results['akshare'] = akshare_tester.run_all_tests()
        except Exception as e:
            print(f"❌ AKShare测试异常: {e}")
            all_results['akshare'] = {'error': str(e)}
        
        # 3. 新闻和社交媒体API测试
        print("\n📰 第3部分: 新闻和社交媒体API测试")
        print("-" * 40)
        try:
            news_social_tester = NewsAndSocialAPITester()
            all_results['news_social'] = news_social_tester.run_all_tests()
        except Exception as e:
            print(f"❌ 新闻社交媒体测试异常: {e}")
            all_results['news_social'] = {'error': str(e)}
        
        self.test_results = all_results
        return all_results
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """生成汇总报告"""
        print("\n" + "=" * 60)
        print("📋 综合测试结果汇总报告")
        print("=" * 60)
        
        summary = {
            'timestamp': self.test_timestamp.isoformat(),
            'total_apis_tested': len(self.test_results),
            'api_results': {},
            'overall_status': 'unknown'
        }
        
        total_tests = 0
        total_passed = 0
        
        for api_name, api_results in self.test_results.items():
            if 'error' in api_results:
                # API测试出现异常
                summary['api_results'][api_name] = {
                    'status': 'error',
                    'error': api_results['error'],
                    'tests_passed': 0,
                    'tests_total': 0,
                    'success_rate': 0.0
                }
                print(f"\n🚫 {api_name.upper()} API: 测试异常")
                print(f"   错误: {api_results['error']}")
            else:
                # 正常测试结果
                tests_passed = sum(1 for result in api_results.values() if result)
                tests_total = len(api_results)
                success_rate = (tests_passed / tests_total * 100) if tests_total > 0 else 0
                
                summary['api_results'][api_name] = {
                    'status': 'completed',
                    'tests_passed': tests_passed,
                    'tests_total': tests_total,
                    'success_rate': success_rate,
                    'details': api_results
                }
                
                total_tests += tests_total
                total_passed += tests_passed
                
                status_emoji = "✅" if success_rate == 100 else "⚠️" if success_rate >= 50 else "❌"
                print(f"\n{status_emoji} {api_name.upper()} API: {tests_passed}/{tests_total} 通过 ({success_rate:.1f}%)")
                
                # 显示详细结果
                for test_name, result in api_results.items():
                    status = "✅" if result else "❌"
                    print(f"   {status} {test_name}")
        
        # 计算总体成功率
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        summary['overall_success_rate'] = overall_success_rate
        summary['total_tests_passed'] = total_passed
        summary['total_tests'] = total_tests
        
        # 确定总体状态
        if overall_success_rate == 100:
            summary['overall_status'] = 'excellent'
            status_desc = "🎉 优秀"
        elif overall_success_rate >= 80:
            summary['overall_status'] = 'good'
            status_desc = "✅ 良好"
        elif overall_success_rate >= 50:
            summary['overall_status'] = 'fair'
            status_desc = "⚠️ 一般"
        else:
            summary['overall_status'] = 'poor'
            status_desc = "❌ 较差"
        
        print(f"\n" + "=" * 60)
        print(f"🎯 总体结果: {status_desc}")
        print(f"📊 成功率: {total_passed}/{total_tests} ({overall_success_rate:.1f}%)")
        print(f"📅 测试时间: {self.test_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return summary
    
    def save_report_to_file(self, summary: Dict[str, Any]) -> str:
        """保存报告到文件"""
        try:
            # 创建报告目录
            reports_dir = project_root / "data" / "reports"
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成文件名
            timestamp_str = self.test_timestamp.strftime('%Y%m%d_%H%M%S')
            report_file = reports_dir / f"api_connectivity_test_{timestamp_str}.json"
            
            # 保存详细结果
            full_report = {
                'summary': summary,
                'detailed_results': self.test_results
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(full_report, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 测试报告已保存到: {report_file}")
            return str(report_file)
            
        except Exception as e:
            print(f"⚠️ 保存报告失败: {e}")
            return ""
    
    def print_recommendations(self, summary: Dict[str, Any]):
        """打印建议和下一步操作"""
        print(f"\n📝 建议和下一步操作:")
        print("-" * 40)
        
        # 根据测试结果给出建议
        for api_name, api_result in summary['api_results'].items():
            if api_result['status'] == 'error':
                print(f"\n🚫 {api_name.upper()}:")
                print(f"   - 检查依赖库是否正确安装")
                print(f"   - 检查网络连接")
                print(f"   - 查看错误信息: {api_result['error']}")
            elif api_result['success_rate'] < 100:
                print(f"\n⚠️ {api_name.upper()} (成功率: {api_result['success_rate']:.1f}%):")
                
                if api_name == 'finnhub':
                    if not any('api_key' in detail and detail for detail in api_result['details'].values()):
                        print(f"   - 检查 FINNHUB_API_KEY 环境变量是否正确设置")
                    print(f"   - 验证API密钥是否有效且未过期")
                    print(f"   - 检查API调用限制")
                
                elif api_name == 'akshare':
                    print(f"   - 检查 akshare 库是否为最新版本: pip install --upgrade akshare")
                    print(f"   - 某些数据源可能有访问限制或维护")
                
                elif api_name == 'news_social':
                    print(f"   - 检查 Reddit API 凭据 (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET)")
                    print(f"   - 检查新闻API密钥配置")
                    print(f"   - 网页爬虫可能因网站结构变化而失效")
        
        # 总体建议
        if summary['overall_success_rate'] == 100:
            print(f"\n🎉 所有API连接正常！系统已准备好进行数据分析。")
        else:
            print(f"\n💡 通用建议:")
            print(f"   - 检查网络连接和防火墙设置")
            print(f"   - 确保所有必要的Python包已安装")
            print(f"   - 检查.env文件中的API密钥配置")
            print(f"   - 查看项目文档了解详细配置说明")

def main():
    """主函数"""
    print("🚀 启动TradingAgents API连通性综合测试")
    
    tester = ComprehensiveAPITester()
    
    # 运行所有测试
    results = tester.run_all_api_tests()
    
    # 生成汇总报告
    summary = tester.generate_summary_report()
    
    # 保存报告
    report_file = tester.save_report_to_file(summary)
    
    # 打印建议
    tester.print_recommendations(summary)
    
    # 返回适当的退出码
    if summary['overall_success_rate'] >= 80:
        print(f"\n✅ 测试完成，系统状态良好")
        sys.exit(0)
    else:
        print(f"\n⚠️ 测试完成，发现问题需要处理")
        sys.exit(1)

if __name__ == "__main__":
    main()