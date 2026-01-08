from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json

# 导入统一日志系统
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")

# 导入Google工具调用处理器
from tradingagents.agents.utils.google_tool_handler import GoogleToolCallHandler


def _get_company_name_for_china_market(ticker: str, market_info: dict) -> str:
    """
    为中国市场分析师获取公司名称

    Args:
        ticker: 股票代码
        market_info: 市场信息字典

    Returns:
        str: 公司名称
    """
    try:
        if market_info['is_china']:
            # 中国A股：使用统一接口获取股票信息
            from tradingagents.dataflows.interface import get_china_stock_info_unified
            stock_info = get_china_stock_info_unified(ticker)

            # 解析股票名称
            if "股票名称:" in stock_info:
                company_name = stock_info.split("股票名称:")[1].split("\n")[0].strip()
                logger.debug(f"📊 [中国市场分析师] 从统一接口获取中国股票名称: {ticker} -> {company_name}")
                return company_name
            else:
                logger.warning(f"⚠️ [中国市场分析师] 无法从统一接口解析股票名称: {ticker}")
                return f"股票代码{ticker}"

        elif market_info['is_hk']:
            # 港股：使用改进的港股工具
            try:
                from tradingagents.dataflows.improved_hk_utils import get_hk_company_name_improved
                company_name = get_hk_company_name_improved(ticker)
                logger.debug(f"📊 [中国市场分析师] 使用改进港股工具获取名称: {ticker} -> {company_name}")
                return company_name
            except Exception as e:
                logger.debug(f"📊 [中国市场分析师] 改进港股工具获取名称失败: {e}")
                # 降级方案：生成友好的默认名称
                clean_ticker = ticker.replace('.HK', '').replace('.hk', '')
                return f"港股{clean_ticker}"

        elif market_info['is_us']:
            # 美股：使用简单映射或返回代码
            us_stock_names = {
                'AAPL': '苹果公司',
                'TSLA': '特斯拉',
                'NVDA': '英伟达',
                'MSFT': '微软',
                'GOOGL': '谷歌',
                'AMZN': '亚马逊',
                'META': 'Meta',
                'NFLX': '奈飞'
            }

            company_name = us_stock_names.get(ticker.upper(), f"美股{ticker}")
            logger.debug(f"📊 [中国市场分析师] 美股名称映射: {ticker} -> {company_name}")
            return company_name

        else:
            return f"股票{ticker}"

    except Exception as e:
        logger.error(f"❌ [中国市场分析师] 获取公司名称失败: {e}")
        return f"股票{ticker}"


def create_china_market_analyst(llm, toolkit):
    """创建中国市场分析师"""
    
    def china_market_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        
        # 获取股票市场信息
        from tradingagents.utils.stock_utils import StockUtils
        market_info = StockUtils.get_market_info(ticker)
        
        # 获取公司名称
        company_name = _get_company_name_for_china_market(ticker, market_info)
        logger.info(f"[中国市场分析师] 公司名称: {company_name}")
        
        # 中国股票分析工具
        tools = [
            toolkit.get_china_stock_data,
            toolkit.get_china_market_overview,
            toolkit.get_YFin_data,  # 备用数据源
        ]
        
        system_message = (
            """您是一位专业的中国股市分析师，专门分析A股、港股等中国资本市场。您具备深厚的中国股市知识和丰富的本土投资经验。

您的专业领域包括：
1. **A股市场分析**: 深度理解A股的独特性，包括涨跌停制度、T+1交易、融资融券等
2. **中国经济政策**: 熟悉货币政策、财政政策对股市的影响机制
3. **行业板块轮动**: 掌握中国特色的板块轮动规律和热点切换
4. **监管环境**: 了解证监会政策、退市制度、注册制等监管变化
5. **市场情绪**: 理解中国投资者的行为特征和情绪波动

分析重点：
- **技术面分析**: 使用通达信数据进行精确的技术指标分析
- **基本面分析**: 结合中国会计准则和财报特点进行分析
- **政策面分析**: 评估政策变化对个股和板块的影响
- **资金面分析**: 分析北向资金、融资融券、大宗交易等资金流向
- **市场风格**: 判断当前是成长风格还是价值风格占优

中国股市特色考虑：
- 涨跌停板限制对交易策略的影响
- ST股票的特殊风险和机会
- 科创板、创业板的差异化分析
- 国企改革、混改等主题投资机会
- 中美关系、地缘政治对中概股的影响

请基于Tushare数据接口提供的实时数据和技术指标，结合中国股市的特殊性，撰写专业的中文分析报告。
确保在报告末尾附上Markdown表格总结关键发现和投资建议。"""
        )
        
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "您是一位专业的AI助手，与其他分析师协作进行股票分析。"
                    " 使用提供的工具获取和分析数据。"
                    " 如果您无法完全回答，没关系；其他分析师会补充您的分析。"
                    " 专注于您的专业领域，提供高质量的分析见解。"
                    " 您可以访问以下工具：{tool_names}。\n{system_message}"
                    "当前分析日期：{current_date}，分析标的：{ticker}。请用中文撰写所有分析内容。",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        
        prompt = prompt.partial(system_message=system_message)
        # 安全地获取工具名称，处理函数和工具对象
        tool_names = []
        for tool in tools:
            if hasattr(tool, 'name'):
                tool_names.append(tool.name)
            elif hasattr(tool, '__name__'):
                tool_names.append(tool.__name__)
            else:
                tool_names.append(str(tool))

        prompt = prompt.partial(tool_names=", ".join(tool_names))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)
        
        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])
        
        # 使用统一的Google工具调用处理器
        if GoogleToolCallHandler.is_google_model(llm):
            logger.info(f"📊 [中国市场分析师] 检测到Google模型，使用统一工具调用处理器")
            
            # 创建分析提示词
            analysis_prompt_template = GoogleToolCallHandler.create_analysis_prompt(
                ticker=ticker,
                company_name=company_name,
                analyst_type="中国市场分析",
                specific_requirements="重点关注中国A股市场特点、政策影响、行业发展趋势等。"
            )
            
            # 处理Google模型工具调用
            report, messages = GoogleToolCallHandler.handle_google_tool_calls(
                result=result,
                llm=llm,
                tools=tools,
                state=state,
                analysis_prompt_template=analysis_prompt_template,
                analyst_name="中国市场分析师"
            )
        else:
            # 非Google模型的处理逻辑
            logger.debug(f"📊 [DEBUG] 非Google模型 ({llm.__class__.__name__})，使用标准处理逻辑")
            
            # 处理中国市场分析报告
            if len(result.tool_calls) == 0:
                # 没有工具调用，直接使用LLM的回复
                report = result.content
                logger.info(f"📊 [中国市场分析师] 直接回复，长度: {len(report)}")
            else:
                # 有工具调用，执行工具并生成完整分析报告
                logger.info(f"📊 [中国市场分析师] 工具调用: {[call.get('name', 'unknown') for call in result.tool_calls]}")
                
                try:
                    # 执行工具调用
                    from langchain_core.messages import ToolMessage, HumanMessage

                    tool_messages = []
                    for tool_call in result.tool_calls:
                        tool_name = tool_call.get('name')
                        tool_args = tool_call.get('args', {})
                        tool_id = tool_call.get('id')

                        logger.debug(f"📊 [DEBUG] 执行工具: {tool_name}, 参数: {tool_args}")

                        # 找到对应的工具并执行
                        tool_result = None
                        for tool in tools:
                            # 安全地获取工具名称进行比较
                            current_tool_name = None
                            if hasattr(tool, 'name'):
                                current_tool_name = tool.name
                            elif hasattr(tool, '__name__'):
                                current_tool_name = tool.__name__

                            if current_tool_name == tool_name:
                                try:
                                    tool_result = tool.invoke(tool_args)
                                    logger.debug(f"📊 [DEBUG] 工具执行成功，结果长度: {len(str(tool_result))}")
                                    break
                                except Exception as tool_error:
                                    logger.error(f"❌ [DEBUG] 工具执行失败: {tool_error}")
                                    tool_result = f"工具执行失败: {str(tool_error)}"

                        if tool_result is None:
                            tool_result = f"未找到工具: {tool_name}"

                        # 创建工具消息
                        tool_message = ToolMessage(
                            content=str(tool_result),
                            tool_call_id=tool_id
                        )
                        tool_messages.append(tool_message)

                    # 基于工具结果生成完整分析报告
                    analysis_prompt = f"""现在请基于上述工具获取的数据，生成详细的中国市场分析报告。

要求：
1. 报告必须基于工具返回的真实数据进行分析
2. 结合中国股市特色和政策环境进行分析
3. 提供明确的投资建议和风险提示
4. 报告长度不少于800字
5. 使用中文撰写

请分析股票{ticker}的中国市场情况，包括：
- A股市场特点分析
- 政策影响评估
- 行业发展趋势
- 资金流向分析
- 中国市场投资建议"""

                    # 直接使用HumanMessage包含工具结果和分析请求，避免消息格式错误
                    analysis_with_data = f"""以下是获取到的中国市场数据：

{chr(10).join([f"工具: {tc.get('name', 'unknown')} - 结果: {tm.content[:500]}..." for tc, tm in zip(result.tool_calls, tool_messages)])}

{analysis_prompt}"""
                    
                    # 直接调用LLM，使用单个HumanMessage
                    final_result = llm.invoke([HumanMessage(content=analysis_with_data)])
                    report = final_result.content

                    logger.info(f"📊 [中国市场分析师] 生成完整分析报告，长度: {len(report)}")

                    # 返回包含工具调用和最终分析的完整消息序列
                    return {
                        "messages": [result] + tool_messages + [final_result],
                        "china_market_report": report,
                        "sender": "ChinaMarketAnalyst",
                    }

                except Exception as e:
                    logger.error(f"❌ [中国市场分析师] 工具执行或分析生成失败: {e}")
                    import traceback
                    traceback.print_exc()

                    # 降级处理：返回工具调用信息
                    report = f"中国市场分析师调用了工具但分析生成失败: {[call.get('name', 'unknown') for call in result.tool_calls]}"
                    return {
                        "messages": [result],
                        "china_market_report": report,
                        "sender": "ChinaMarketAnalyst",
                    }
        
        return {
            "messages": [result],
            "china_market_report": report,
            "sender": "ChinaMarketAnalyst",
        }
    
    return china_market_analyst_node


def create_china_stock_screener(llm, toolkit):
    """创建中国股票筛选器"""
    
    def china_stock_screener_node(state):
        current_date = state["trade_date"]
        
        tools = [
            toolkit.get_china_market_overview,
        ]
        
        system_message = (
            """您是一位专业的中国股票筛选专家，负责从A股市场中筛选出具有投资价值的股票。

筛选维度包括：
1. **基本面筛选**: 
   - 财务指标：ROE、ROA、净利润增长率、营收增长率
   - 估值指标：PE、PB、PEG、PS比率
   - 财务健康：资产负债率、流动比率、速动比率

2. **技术面筛选**:
   - 趋势指标：均线系统、MACD、KDJ
   - 动量指标：RSI、威廉指标、CCI
   - 成交量指标：量价关系、换手率

3. **市场面筛选**:
   - 资金流向：主力资金净流入、北向资金偏好
   - 机构持仓：基金重仓、社保持仓、QFII持仓
   - 市场热度：概念板块活跃度、题材炒作程度

4. **政策面筛选**:
   - 政策受益：国家政策扶持行业
   - 改革红利：国企改革、混改标的
   - 监管影响：监管政策变化的影响

筛选策略：
- **价值投资**: 低估值、高分红、稳定增长
- **成长投资**: 高增长、新兴行业、技术创新
- **主题投资**: 政策驱动、事件催化、概念炒作
- **周期投资**: 经济周期、行业周期、季节性

请基于当前市场环境和政策背景，提供专业的股票筛选建议。"""
        )
        
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system", 
                    "您是一位专业的股票筛选专家。"
                    " 使用提供的工具分析市场概况。"
                    " 您可以访问以下工具：{tool_names}。\n{system_message}"
                    "当前日期：{current_date}。请用中文撰写分析内容。",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        
        prompt = prompt.partial(system_message=system_message)
        # 安全地获取工具名称，处理函数和工具对象
        tool_names = []
        for tool in tools:
            if hasattr(tool, 'name'):
                tool_names.append(tool.name)
            elif hasattr(tool, '__name__'):
                tool_names.append(tool.__name__)
            else:
                tool_names.append(str(tool))

        prompt = prompt.partial(tool_names=", ".join(tool_names))
        prompt = prompt.partial(current_date=current_date)
        
        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])
        
        return {
            "messages": [result],
            "stock_screening_report": result.content,
            "sender": "ChinaStockScreener",
        }
    
    return china_stock_screener_node
