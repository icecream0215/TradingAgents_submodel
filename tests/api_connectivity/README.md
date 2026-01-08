# API连通性测试

本目录包含用于测试TradingAgents项目中各种数据API连通性的测试脚本。

## 测试范围

### 1. 金融数据API

#### FinnHub API (美股数据)
- **测试文件**: `test_finnhub_api.py`
- **数据类型**:
  - 实时行情数据 (Real-time market data)
  - 公司内部人士情绪 (Company insider sentiment)
  - 内部人士交易 (Insider trading)
- **环境变量**: `FINNHUB_API_KEY`

#### AKShare API (A股和港股数据)
- **测试文件**: `test_akshare_api.py`
- **数据类型**:
  - A股实时数据 (A-share real-time data)
  - 港股数据 (Hong Kong stock data)
  - 基本面数据 (Fundamental data)
- **依赖**: `akshare` 库

### 2. 新闻和社交媒体API

#### 新闻数据
- **测试文件**: `test_news_social_api.py`
- **数据源**:
  - Google News (网页爬虫)
  - 其他新闻API (如GNews API)
- **依赖**: `beautifulsoup4`, `requests`

#### 社交媒体数据
- **平台**: Reddit
- **数据类型**: 社交媒体情绪分析
- **环境变量**: 
  - `REDDIT_CLIENT_ID`
  - `REDDIT_CLIENT_SECRET` 
  - `REDDIT_USER_AGENT` (可选)
- **依赖**: `praw` 库

## 快速开始

### 1. 安装依赖

```bash
# 安装基础依赖
pip install requests beautifulsoup4

# 安装AKShare (A股和港股数据)
pip install akshare

# 安装Reddit API库
pip install praw
```

### 2. 配置环境变量

在项目根目录的 `.env` 文件中添加以下配置：

```env
# FinnHub API (美股数据)
FINNHUB_API_KEY=your_finnhub_api_key

# Reddit API (社交媒体数据)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=TradingAgents/1.0

# 可选: 新闻API
GNEWS_API_KEY=your_gnews_api_key
```

### 3. 运行测试

#### 运行单个API测试

```bash
# 测试FinnHub API
python tests/api_connectivity/test_finnhub_api.py

# 测试AKShare API  
python tests/api_connectivity/test_akshare_api.py

# 测试新闻和社交媒体API
python tests/api_connectivity/test_news_social_api.py
```

#### 运行综合测试

```bash
# 运行所有API测试并生成详细报告
python tests/api_connectivity/run_all_tests.py
```

## 测试结果

### 输出信息
每个测试脚本会输出：
- ✅ 成功的测试项目
- ❌ 失败的测试项目  
- ⚠️ 警告信息（如配置缺失但不影响核心功能）
- 📊 成功率统计

### 报告文件
综合测试会生成JSON格式的详细报告，保存在 `data/reports/` 目录下：
- 文件名格式: `api_connectivity_test_YYYYMMDD_HHMMSS.json`
- 包含所有测试的详细结果和汇总信息

## 故障排除

### 常见问题

1. **FinnHub API失败**
   - 检查API密钥是否正确
   - 验证API调用限制是否已达到
   - 确认网络连接正常

2. **AKShare失败**
   - 更新到最新版本: `pip install --upgrade akshare`
   - 某些数据源可能临时不可用
   - 检查网络防火墙设置

3. **Reddit API失败**
   - 验证Reddit应用凭据
   - 检查用户代理字符串格式
   - 确认Reddit API调用限制

4. **新闻爬虫失败**
   - 网站结构可能已变化
   - 检查反爬虫机制
   - 尝试使用备用新闻API

### 配置建议

1. **API密钥管理**
   - 使用 `.env` 文件存储敏感信息
   - 不要在代码中硬编码API密钥
   - 定期轮换API密钥

2. **网络设置**
   - 确保防火墙允许HTTPS出站连接
   - 考虑使用代理服务器（如需要）
   - 设置合适的请求超时时间

3. **依赖管理**
   - 定期更新依赖库
   - 使用虚拟环境隔离依赖
   - 监控弃用警告

## 扩展测试

要添加新的API测试：

1. 在此目录创建新的测试文件
2. 实现测试类，包含各种测试方法
3. 在 `run_all_tests.py` 中集成新测试
4. 更新此README文档

## 注意事项

- 测试脚本会进行实际的API调用，可能消耗API配额
- 某些测试可能因为数据源维护而暂时失败
- 建议在生产环境部署前运行完整的连通性测试
- 定期运行测试以监控API服务状态