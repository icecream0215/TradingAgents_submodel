#!/usr/bin/env python3
"""
FinnHub API 连通性测试
测试FinnHub API的各项功能是否正常

支持的数据类型：
- 实时行情数据 (Real-time market data)
- 公司内部人士情绪 (Company insider sentiment)
- 内部人士交易 (Insider trading)
"""

import os
import sys
from pathlib import Path
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class FinnHubAPITester:
    """FinnHub API 测试器"""
    
    def __init__(self):
        self.api_key = os.getenv('FINNHUB_API_KEY')
        self.base_url = "https://finnhub.io/api/v1"
        self.session = requests.Session()
        
    def check_api_key(self) -> bool:
        """检查API密钥是否配置"""
        if not self.api_key:
            print("❌ 未找到 FINNHUB_API_KEY 环境变量")
            print("💡 请在 .env 文件中设置: FINNHUB_API_KEY=your_api_key")
            return False
        print(f"✅ FinnHub API Key: {self.api_key[:10]}...")
        return True
    
    def test_connection(self) -> bool:
        """测试基本连接"""
        print("\n🔍 测试 FinnHub API 基本连接...")
        try:
            url = f"{self.base_url}/stock/symbol"
            params = {
                'exchange': 'US',
                'token': self.api_key
            }
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 连接成功，获取到 {len(data)} 个美股标的")
                return True
            else:
                print(f"❌ 连接失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 连接异常: {e}")
            return False
    
    def test_real_time_quote(self, symbol: str = "AAPL") -> bool:
        """测试实时行情数据"""
        print(f"\n📈 测试实时行情数据 ({symbol})...")
        try:
            url = f"{self.base_url}/quote"
            params = {
                'symbol': symbol,
                'token': self.api_key
            }
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'c' in data and data['c'] > 0:  # 检查当前价格
                    print(f"✅ 获取 {symbol} 实时行情成功")
                    print(f"   当前价格: ${data['c']}")
                    print(f"   开盘价: ${data['o']}")
                    print(f"   最高价: ${data['h']}")
                    print(f"   最低价: ${data['l']}")
                    return True
                else:
                    print(f"❌ 数据异常: {data}")
                    return False
            else:
                print(f"❌ 请求失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False
    
    def test_insider_sentiment(self, symbol: str = "AAPL") -> bool:
        """测试内部人士情绪数据"""
        print(f"\n🧠 测试内部人士情绪数据 ({symbol})...")
        try:
            url = f"{self.base_url}/stock/insider-sentiment"
            # 获取过去3个月的数据
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            params = {
                'symbol': symbol,
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d'),
                'token': self.api_key
            }
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']:
                    print(f"✅ 获取 {symbol} 内部人士情绪数据成功")
                    print(f"   数据条数: {len(data['data'])}")
                    latest = data['data'][0]
                    print(f"   最新变化: {latest.get('change', 'N/A')}")
                    return True
                else:
                    print(f"⚠️ 暂无 {symbol} 内部人士情绪数据")
                    return True  # 无数据也算正常
            else:
                print(f"❌ 请求失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False
    
    def test_insider_trading(self, symbol: str = "AAPL") -> bool:
        """测试内部人士交易数据"""
        print(f"\n💼 测试内部人士交易数据 ({symbol})...")
        try:
            url = f"{self.base_url}/stock/insider-transactions"
            # 获取过去30天的数据
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            params = {
                'symbol': symbol,
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d'),
                'token': self.api_key
            }
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']:
                    print(f"✅ 获取 {symbol} 内部人士交易数据成功")
                    print(f"   交易记录数: {len(data['data'])}")
                    latest = data['data'][0]
                    print(f"   最新交易: {latest.get('name', 'N/A')} - {latest.get('transactionCode', 'N/A')}")
                    return True
                else:
                    print(f"⚠️ 暂无 {symbol} 内部人士交易数据")
                    return True  # 无数据也算正常
            else:
                print(f"❌ 请求失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """运行所有测试"""
        print("🚀 开始 FinnHub API 连通性测试...")
        print("=" * 50)
        
        results = {}
        
        # 1. 检查API密钥
        results['api_key'] = self.check_api_key()
        if not results['api_key']:
            return results
        
        # 2. 测试基本连接
        results['connection'] = self.test_connection()
        
        # 3. 测试实时行情
        results['real_time_quote'] = self.test_real_time_quote()
        
        # 4. 测试内部人士情绪
        results['insider_sentiment'] = self.test_insider_sentiment()
        
        # 5. 测试内部人士交易
        results['insider_trading'] = self.test_insider_trading()
        
        # 输出总结
        print("\n" + "=" * 50)
        print("📊 FinnHub API 测试结果总结:")
        for test_name, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"   {test_name}: {status}")
        
        success_rate = sum(results.values()) / len(results) * 100
        print(f"\n🎯 总体成功率: {success_rate:.1f}%")
        
        return results

def main():
    """主函数"""
    tester = FinnHubAPITester()
    results = tester.run_all_tests()
    
    # 返回退出码
    if all(results.values()):
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("\n⚠️ 部分测试失败，请检查配置和网络连接")
        sys.exit(1)

if __name__ == "__main__":
    main()