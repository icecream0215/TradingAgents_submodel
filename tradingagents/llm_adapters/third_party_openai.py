import os
import json
from typing import Any, Dict, List, Optional, Union
from functools import lru_cache
from pydantic import Field

# 延迟导入，避免循环导入问题
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import BaseMessage
    from langchain_core.outputs import ChatResult
    from langchain_core.callbacks import CallbackManagerForLLMRun
except ImportError:
    # 如果导入失败，使用占位符类
    class ChatOpenAI:
        pass

    class BaseMessage:
        pass

    class ChatResult:
        pass

    class CallbackManagerForLLMRun:
        pass

# 导入日志模块
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')

# 导入token跟踪器
try:
    from tradingagents.config.config_manager import token_tracker
    TOKEN_TRACKING_ENABLED = True
    logger.info("✅ Token跟踪功能已启用")
except ImportError:
    TOKEN_TRACKING_ENABLED = False
    logger.warning("⚠️ Token跟踪功能未启用")


class ThirdPartyOpenAI(ChatOpenAI):
    """
    第三方OpenAI服务适配器

    专门处理第三方OpenAI兼容服务的兼容性问题，
    通过过滤和优化请求参数来避免500错误
    """

    # 添加session_id作为Pydantic字段
    session_id: Optional[str] = Field(default=None, description="会话ID用于token跟踪")
    
    # 🔧 添加流式配置字段，解决Pydantic属性问题（不能以下划线开头）
    user_wants_streaming: bool = Field(default=False, description="用户是否需要流式响应")
    user_defined_model: Optional[str] = Field(default=None, description="用户定义的模型名")
    
    # 添加模型参数缓存
    _model_param_cache = {}
    
    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        api_key: Optional[str] = None,
        base_url: str = "https://llm.submodel.ai/v1",
        temperature: float = 0.1,
        max_tokens: Optional[int] = 2000,
        session_id: Optional[str] = None,
        **kwargs
    ):
        """
        初始化第三方OpenAI适配器
        
        Args:
            model: 模型名称
            api_key: API密钥
            base_url: API基础URL
            temperature: 温度参数
            max_tokens: 最大token数
            session_id: 会话ID用于token跟踪
            **kwargs: 其他参数
        """
        
        # 🔧 修复流式参数冲突问题
        # 处理LangChain的stream参数转移问题
        default_streaming = False  # 改为False，优先获取准确token数据
        user_streaming = kwargs.get('streaming', default_streaming)
        
        # 🔑 重要：正确处理stream参数（避免与LangChain的stream方法冲突）
        user_stream = None
        if 'stream' in kwargs:
            user_stream = kwargs.get('stream', default_streaming)
            # 只有当stream是布尔值时才认为是流式参数
            if not isinstance(user_stream, bool):
                user_stream = default_streaming
        else:
            user_stream = default_streaming
        
        # 移除可能冲突的参数（避免传递给父类）
        kwargs.pop('streaming', None)
        kwargs.pop('stream', None)
        
        # 添加session_id作为Pydantic字段
        super().__init__(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=120,
            max_retries=2,
            streaming=user_streaming,  # 使用处理后的流式参数
            # 🔧 重要：不传递stream给父类，避免LangChain警告
            session_id=session_id,
            user_wants_streaming=user_streaming or user_stream,  # 🔧 通过构造函数设置
            user_defined_model=model,  # 🔧 通过构造函数设置
            **kwargs  # 传递其他参数，但已经移除了冲突的参数
        )
        
        # 🔑 重要：强制设置model_name为传入的model参数
        self.model_name = model
        # self.user_defined_model = model  # 已在构造函数中设置
        
        # 🔧 保存用户的流式偏好（避免传递给父类引起警告）
        self._user_stream_setting = user_stream
        
        # 初始化token使用信息临时存储
        self._last_api_usage = None
        
        logger.info(f"✅ 第三方OpenAI适配器初始化成功")
        logger.info(f"   模型: {self.model_name}")  # 显示强制设置后的模型名
        logger.info(f"   端点: {base_url}")
        logger.info(f"   流式模式: {self.user_wants_streaming} (方案3={'启用' if self.user_wants_streaming else '禁用'})")
        # 安全地显示API密钥（处理SecretStr类型）
        if api_key:
            if hasattr(api_key, 'get_secret_value'):
                key_display = api_key.get_secret_value()[:20] if api_key.get_secret_value() else 'None'
            else:
                key_display = str(api_key)[:20] if api_key else 'None'
        else:
            key_display = 'None'
        logger.info(f"   API密钥: {key_display}...")
        if session_id:
            logger.info(f"   会话ID: {session_id}")
    
    def _filter_safe_kwargs(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        不再进行参数过滤，直接返回所有参数
        
        Args:
            kwargs: 原始参数
            
        Returns:
            原始参数（不进行过滤）
        """
        
        # 不再进行参数过滤，直接返回所有参数
        logger.debug(f"🔓 跳过参数过滤，直接使用所有参数: {list(kwargs.keys())}")
        return kwargs
    
    def _get_model_supported_params(self, model_name: str) -> Dict[str, Any]:
        """
        通过API查询模型支持的参数（带缓存）
        
        Args:
            model_name: 模型名称
            
        Returns:
            模型支持的参数字典
        """
        # 检查缓存
        if model_name in self._model_param_cache:
            return self._model_param_cache[model_name]
        
        try:
            # 安全地获取API密钥和基础URL
            api_key = self._get_api_key()
            base_url = self._get_base_url()
            
            # 构造模型信息查询URL
            api_url = f"{base_url}/models/{model_name}" if "openai" in base_url.lower() else f"{base_url}/models"
            
            # 请求头
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
            
            import requests
            response = requests.get(api_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                # 解析模型支持的参数
                supported_params = self._parse_model_params(data, model_name)
                # 缓存结果
                self._model_param_cache[model_name] = supported_params
                logger.debug(f"📥 获取模型 {model_name} 支持的参数: {list(supported_params.keys())}")
                return supported_params
            else:
                logger.warning(f"⚠️ 无法获取模型 {model_name} 信息: {response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ 查询模型参数失败: {e}")
        
        # 返回默认支持的参数
        return self._get_default_supported_params(model_name)
    
    def _parse_model_params(self, model_data: Dict[str, Any], model_name: str) -> Dict[str, Any]:
        """
        解析模型支持的参数
        
        Args:
            model_data: 模型数据
            model_name: 模型名称
            
        Returns:
            支持的参数字典
        """
        # 默认支持的基本参数
        supported = {
            'model', 'messages', 'temperature', 'max_tokens',
            'top_p', 'frequency_penalty', 'presence_penalty'
        }
        
        # 根据模型类型调整支持的参数
        if 'deepseek' in model_name.lower():
            # DeepSeek支持的参数
            supported = {'model', 'messages', 'temperature', 'max_tokens'}
        elif 'gpt' in model_name.lower():
            # OpenAI GPT系列支持更多参数
            supported = {
                'model', 'messages', 'temperature', 'max_tokens',
                'top_p', 'frequency_penalty', 'presence_penalty',
                'stop', 'stream'
            }
        
        return {param: True for param in supported}
    
    def _clean_message_content(self, content: str) -> str:
        """
        清理消息内容，移除可能导致token解析错误的字符和格式
        
        Args:
            content: 原始消息内容
            
        Returns:
            清理后的消息内容
        """
        if not isinstance(content, str):
            content = str(content)
        
        # 移除可能导致token解析问题的特殊字符
        # 1. 移除零宽度字符
        content = content.replace('\u200b', '')  # 零宽度空格
        content = content.replace('\ufeff', '')  # BOM字符
        
        # 2. 规范化换行符
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # 3. 移除过多的连续空白字符
        import re
        content = re.sub(r'\n{3,}', '\n\n', content)  # 最多保留两个连续换行
        content = re.sub(r'[ \t]{3,}', '  ', content)  # 最多保留两个连续空格
        
        # 4. 确保内容不为空
        content = content.strip()
        if not content:
            content = "请提供分析建议。"  # 默认内容
        
        # 5. 限制单个消息的最大长度（避免超长输入）
        max_length = 8000  # 保守的最大长度
        if len(content) > max_length:
            content = content[:max_length] + "...(内容过长已截断)"
            logger.warning(f"⚠️ 消息内容过长，已截断到{max_length}字符")
        
        return content
    
    def _aggressive_clean_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        激进的消息清理，用于处理token解析错误的重试
        
        Args:
            messages: 原始消息列表
            
        Returns:
            激进清理后的消息列表
        """
        cleaned_messages = []
        
        for msg in messages:
            content = msg['content']
            
            # 更激进的清理
            import re
            
            # 1. 移除所有非ASCII字符（保留中文）
            content = re.sub(r'[^\u4e00-\u9fff\u3400-\u4dbf\u0020-\u007E\n]', '', content)
            
            # 2. 移除markdown格式
            content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)  # 粗体
            content = re.sub(r'\*([^*]+)\*', r'\1', content)      # 斜体
            content = re.sub(r'`([^`]+)`', r'\1', content)       # 代码
            content = re.sub(r'#+\s*', '', content)              # 标题
            
            # 3. 简化标点符号
            content = re.sub(r'[。！？]{2,}', '。', content)      # 多个句号
            content = re.sub(r'[，、；：]{2,}', '，', content)     # 多个逗号
            
            # 4. 确保基本内容
            content = content.strip()
            if not content:
                content = "请分析" if msg['role'] == 'user' else "好的"
            
            # 5. 限制长度
            if len(content) > 1000:
                content = content[:1000] + "..."
            
            cleaned_messages.append({
                'role': msg['role'],
                'content': content
            })
        
        return cleaned_messages
    
    def _get_default_supported_params(self, model_name: str) -> Dict[str, Any]:
        """
        获取默认支持的参数（基于模型名称）
        
        Args:
            model_name: 模型名称
            
        Returns:
            默认支持的参数字典
        """
        # 基础参数（所有模型都支持）
        base_params = {'model', 'messages', 'temperature'}
        
        # 根据模型名称确定额外支持的参数
        if 'deepseek' in model_name.lower():
            # DeepSeek模型较为保守
            extra_params = {'max_tokens'}
        elif 'gpt' in model_name.lower() or 'openai' in model_name.lower():
            # OpenAI系列模型支持更多参数
            extra_params = {'max_tokens', 'top_p', 'frequency_penalty', 'presence_penalty'}
        else:
            # 其他模型使用最小化参数集
            extra_params = {'max_tokens'}
        
        all_params = base_params.union(extra_params)
        return {param: True for param in all_params}
    
    def _filter_model_kwargs(self, model_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        不再进行模型参数过滤，直接返回所有参数
        
        Args:
            model_kwargs: 模型关键字参数
            
        Returns:
            原始参数（不进行过滤）
        """
        if not model_kwargs:
            return {}
        
        # 获取模型名称（用于日志）
        model_name = getattr(self, 'model_name', '')
        
        logger.debug(f"� 跳过模型参数过滤: {model_name}")
        logger.debug(f"   直接使用所有参数: {list(model_kwargs.keys())}")
        
        # 直接返回所有参数，不进行过滤
        return model_kwargs
    
    def _filter_model_kwargs_predefined(self, model_kwargs: Dict[str, Any], model_name: str) -> Dict[str, Any]:
        """
        废弃的方法 - 不再进行参数过滤
        为了向后兼容而保留，直接返回所有参数
        
        Args:
            model_kwargs: 模型关键字参数
            model_name: 模型名称
            
        Returns:
            原始参数（不进行过滤）
        """
        logger.debug(f"🔓 废弃的参数过滤方法，直接返回所有参数")
        return model_kwargs
    
    def _get_api_key(self) -> str:
        """
        安全地获取API密钥，处理不同的属性名称和SecretStr类型
        
        Returns:
            str: API密钥
            
        Raises:
            ValueError: 如果无法获取API密钥
        """
        # 尝试不同的可能属性名称
        possible_attrs = ['openai_api_key', 'api_key', '_api_key']
        
        for attr in possible_attrs:
            if hasattr(self, attr):
                api_key = getattr(self, attr)
                if api_key:
                    # 处理SecretStr类型
                    if hasattr(api_key, 'get_secret_value'):
                        return api_key.get_secret_value()
                    return str(api_key)
        
        # 最后尝试从环境变量获取
        import os
        env_key = os.getenv('OPENAI_API_KEY')
        if env_key:
            return env_key
            
        raise ValueError("无法获取API密钥：请检查初始化参数或环境变量OPENAI_API_KEY")
    
    def _get_base_url(self) -> str:
        """
        安全地获取基础URL
        
        Returns:
            str: 基础URL
        """
        # 尝试不同的可能属性名称
        possible_attrs = ['base_url', 'openai_api_base', '_base_url']
        
        for attr in possible_attrs:
            if hasattr(self, attr):
                base_url = getattr(self, attr)
                if base_url:
                    return base_url
                    
        # 默认基础URL
        return "https://llm.submodel.ai/v1"
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        生成聊天响应，使用优化的参数和直接API调用
        
        Args:
            messages: 消息列表
            stop: 停止词
            run_manager: 回调管理器
            **kwargs: 其他参数
            
        Returns:
            聊天结果
        """
        
        # 保存自定义参数用于token跟踪，并从kwargs中移除
        custom_kwargs = {
            'session_id': kwargs.pop('session_id', None),
            'analysis_type': kwargs.pop('analysis_type', 'stock_analysis')
        }
        
        try:
            # 🔑 重要：如果是流式响应，强制使用我们的_direct_api_call以确保方案3生效
            # 使用保存的用户流式意图，避免参数冲突
            wants_streaming = getattr(self, 'user_wants_streaming', False)
            kwargs_stream = kwargs.get('stream', False)
            # 只有当stream是布尔值时才考虑
            if isinstance(kwargs_stream, bool) and kwargs_stream:
                wants_streaming = True
                
            if wants_streaming:
                logger.info(f"🌊 检测到流式模式，使用方案3的_direct_api_call")
                result = self._direct_api_call(messages, stream=True)
            else:
                # 直接使用LangChain标准方法，不进行参数过滤
                logger.debug(f"🔄 第三方适配器：使用标准LangChain调用（无参数过滤）")
                result = super()._generate(messages, stop, run_manager, **kwargs)
        except Exception as e:
            # 特别处理token解析错误
            if "Unexpected token" in str(e) and "while expecting start token" in str(e):
                logger.warning(f"🔧 检测到token解析错误，尝试清理消息后重试: {e}")
                try:
                    # 清理消息内容
                    cleaned_messages = []
                    for msg in messages:
                        cleaned_content = self._clean_message_content(msg.content)
                        # 创建新的消息对象，保持原有类型
                        if hasattr(msg, 'type'):
                            # 使用LangChain的消息类
                            if msg.type == 'human':
                                from langchain_core.messages import HumanMessage
                                cleaned_msg = HumanMessage(content=cleaned_content)
                            else:
                                from langchain_core.messages import AIMessage
                                cleaned_msg = AIMessage(content=cleaned_content)
                        else:
                            # 保持原始消息类型
                            cleaned_msg = type(msg)(content=cleaned_content)
                        cleaned_messages.append(cleaned_msg)
                    
                    # 使用清理后的消息重试
                    logger.info(f"🔄 使用清理后的消息重试标准调用")
                    result = super()._generate(cleaned_messages, stop, run_manager, **kwargs)
                except Exception as retry_error:
                    logger.warning(f"⚠️ 清理后重试仍失败，切换到直接API调用: {retry_error}")
                    result = self._direct_api_call(messages)
            # 如果出现500错误，使用直接API调用方式
            elif "500" in str(e) or "Internal server error" in str(e).lower():
                logger.warning(f"⚠️ 标准调用失败，使用直接API方法: {e}")
                logger.info(f"🔄 切换到直接API调用模式")
                
                try:
                    result = self._direct_api_call(messages)
                except Exception as direct_error:
                    logger.error(f"❌ 直接API调用也失败: {direct_error}")
                    # 记录详细错误信息
                    logger.error(f"   模型: {getattr(self, 'model_name', 'unknown')}")
                    logger.error(f"   消息数量: {len(messages)}")
                    logger.error(f"   消息内容: {[m.content[:50] for m in messages]}")
                    
                    # 优雅地处理失败，返回有意义的错误信息
                    return self._create_error_response(
                        "🚨 API服务暂时不可用，请稍后再试。原因：上游API服务出现错误，同时备用调用机制也失败。"
                    )
            else:
                # 其他错误直接抛出
                raise e
        
        # 追踪 token 使用量
        try:
            # 尝试多种方式获取token使用信息
            input_tokens = 0
            output_tokens = 0
            
            # 方法1：检查LangChain标准的llm_output
            if hasattr(result, 'llm_output') and result.llm_output:
                token_usage = result.llm_output.get('token_usage', {})
                input_tokens = token_usage.get('prompt_tokens', 0)
                output_tokens = token_usage.get('completion_tokens', 0)
                logger.debug(f"🔍 [token] 从llm_output获取: 输入={input_tokens}, 输出={output_tokens}")
            
            # 方法2：检查response_metadata中的token信息（新版LangChain）
            if (input_tokens == 0 and output_tokens == 0 and 
                hasattr(result, 'response_metadata') and result.response_metadata):
                token_usage = result.response_metadata.get('token_usage', {})
                input_tokens = token_usage.get('prompt_tokens', 0)
                output_tokens = token_usage.get('completion_tokens', 0)
                logger.debug(f"🔍 [token] 从response_metadata获取: 输入={input_tokens}, 输出={output_tokens}")
            
            # 方法3：检查usage_metadata（LangChain新属性）
            if (input_tokens == 0 and output_tokens == 0 and 
                hasattr(result, 'usage_metadata') and result.usage_metadata):
                input_tokens = getattr(result.usage_metadata, 'input_tokens', 0)
                output_tokens = getattr(result.usage_metadata, 'output_tokens', 0)
                logger.debug(f"🔍 [token] 从usage_metadata获取: 输入={input_tokens}, 输出={output_tokens}")
            
            # 方法4：如果以上都没有获取到，且这是我们的直接API调用，尝试解析token信息
            if (input_tokens == 0 and output_tokens == 0 and 
                hasattr(self, '_last_api_usage') and self._last_api_usage):
                input_tokens = self._last_api_usage.get('prompt_tokens', 0)
                output_tokens = self._last_api_usage.get('completion_tokens', 0)
                logger.debug(f"🔍 [token] 从_last_api_usage获取: 输入={input_tokens}, 输出={output_tokens}")
                # 清除临时存储
                self._last_api_usage = None
            
            # 方法5：如果还是没有，且消息不为空，使用估算方法（最后手段）
            if input_tokens == 0 and output_tokens == 0 and messages:
                # 简单估算：中文字符约等于1.5个token，英文单词约等于1.3个token
                input_text = " ".join([msg.content for msg in messages])
                output_text = result.content if hasattr(result, 'content') else ""
                
                # 粗略估算
                input_tokens = max(1, int(len(input_text) * 0.75))  # 保守估算
                output_tokens = max(1, int(len(output_text) * 0.75))
                logger.warning(f"⚠️ [token] 使用估算方法: 输入≈{input_tokens}, 输出≈{output_tokens}")
            
            # 记录token使用（只要有任何一个值大于0）
            if input_tokens > 0 or output_tokens > 0:
                # 使用初始化时保存的session_id
                session_id = self.session_id or custom_kwargs.get('session_id') or f"thirdparty_openai_{hash(str(messages))%10000}"
                analysis_type = custom_kwargs.get('analysis_type', 'stock_analysis')
                
                # 使用 TokenTracker 记录使用量
                if TOKEN_TRACKING_ENABLED:
                    logger.info(f"📊 [token] 记录使用量: {input_tokens}+{output_tokens}={input_tokens+output_tokens} tokens")
                    token_tracker.track_usage(
                        provider="custom_openai",
                        model_name=getattr(self, 'model_name', 'unknown'),
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        session_id=session_id,
                        analysis_type=analysis_type
                    )
                else:
                    logger.warning(f"⚠️ [token] Token跟踪未启用")
            else:
                logger.warning(f"⚠️ [token] 无法获取token使用量信息")
                        
        except Exception as track_error:
            # token 追踪失败不应该影响主要功能
            logger.error(f"⚠️ Token 追踪失败: {track_error}")
        
        return result
    
    def _create_error_response(self, error_message: str) -> ChatResult:
        """
        创建错误响应，用于优雅地处理失败
        
        Args:
            error_message: 错误信息
            
        Returns:
            ChatResult: 包含错误信息的响应
        """
        try:
            from langchain_core.outputs import ChatResult, ChatGeneration
            from langchain_core.messages import AIMessage
            
            ai_message = AIMessage(content=error_message)
            generation = ChatGeneration(message=ai_message)
            return ChatResult(generations=[generation])
        except ImportError:
            # 如果导入失败，创建一个简单的响应对象
            class MockChatResult:
                def __init__(self, generations):
                    self.generations = generations
                    
            class MockChatGeneration:
                def __init__(self, message):
                    self.message = message
                    
            class MockAIMessage:
                def __init__(self, content):
                    self.content = content
            
            ai_message = MockAIMessage(content=error_message)
            generation = MockChatGeneration(message=ai_message)
            return MockChatResult(generations=[generation])
    
    def _direct_api_call(self, messages: List[BaseMessage], stream: bool = True) -> ChatResult:
        """
        直接使用requests调用API，支持流式和非流式响应
        增强了错误处理和属性安全性，包括token格式兼容性处理
        
        Args:
            messages: 消息列表
            stream: 是否使用流式响应
            
        Returns:
            聊天结果
            
        Raises:
            Exception: 各种错误情况
        """
        import requests
        try:
            from langchain_core.outputs import ChatResult, ChatGeneration
            from langchain_core.messages import AIMessage
        except ImportError:
            # 如果导入失败，使用占位符
            class ChatResult:
                def __init__(self, generations):
                    self.generations = generations
                    
            class ChatGeneration:
                def __init__(self, message):
                    self.message = message
                    
            class AIMessage:
                def __init__(self, content):
                    self.content = content
        
        try:
            # 安全地获取API密钥和基础URL
            api_key = self._get_api_key()
            base_url = self._get_base_url()
            
            logger.debug(f"🔑 使用API密钥: {api_key[:20] if api_key else 'None'}...")
            logger.debug(f"🌐 使用基础URL: {base_url}")
            
        except ValueError as e:
            logger.error(f"❌ 配置错误: {e}")
            raise Exception(f"配置错误：{e}")
        
        # 转换和清理消息格式
        api_messages = []
        for msg in messages:
            if hasattr(msg, 'role'):
                role = msg.role
            elif hasattr(msg, 'type'):
                role = 'user' if msg.type == 'human' else 'assistant'
            else:
                role = 'user'
            
            # 清理消息内容，处理可能导致token解析错误的字符
            content = self._clean_message_content(msg.content)
            
            api_messages.append({
                'role': role,
                'content': content
            })
        
        # 安全地获取模型参数 - 优先使用用户定义的模型名
        model_name = getattr(self, 'user_defined_model', None) or getattr(self, 'model', getattr(self, 'model_name', 'gpt-3.5-turbo'))
        logger.info(f"🤖 实际使用的模型名: {model_name}")
        logger.info(f"🔍 self.model: {getattr(self, 'model', 'N/A')}")
        logger.info(f"🔍 self.model_name: {getattr(self, 'model_name', 'N/A')}")
        logger.info(f"🔍 self.user_defined_model: {getattr(self, 'user_defined_model', 'N/A')}")
        temperature = getattr(self, 'temperature', 0.1)
        max_tokens = getattr(self, 'max_tokens', 2000)
        request_timeout = getattr(self, 'request_timeout', 120)
        
        # 构建请求数据 - 不进行参数过滤
        request_data = {
            'model': model_name,
            'messages': api_messages,
            'temperature': temperature,
            'stream': stream  # 默认使用流式请求
        }
        
        # 直接添加max_tokens参数，不进行过滤检查
        if max_tokens and max_tokens > 0:
            request_data['max_tokens'] = max_tokens
            
        # 可以添加其他常用参数（不进行兼容性检查）
        # 让服务端自行处理不支持的参数
        logger.debug(f"📋 使用完整参数集，让服务端处理兼容性")
        
        # 请求头
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        api_url = f"{base_url}/chat/completions"
        logger.debug(f"🌐 直接API调用: {api_url}")
        logger.debug(f"📝 请求数据: {request_data}")
        
        try:
            if stream:
                # 流式请求处理
                response = requests.post(
                    api_url,
                    headers=headers,
                    json=request_data,
                    timeout=request_timeout,
                    stream=True
                )
                
                # 检查响应状态
                if response.status_code != 200:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    logger.error(f"❌ 直接API调用失败: {error_msg}")
                    raise Exception(f"API调用失败: {error_msg}")
                
                # 处理流式响应
                full_content = ""
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith('data: '):
                            data_str = decoded_line[6:]  # 移除 'data: ' 前缀
                            if data_str == '[DONE]':
                                break
                            try:
                                import json
                                chunk_data = json.loads(data_str)
                                if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                                    delta = chunk_data['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        full_content += content
                                        # 这里可以添加回调处理，如果需要实时处理每个chunk
                            except json.JSONDecodeError:
                                logger.warning(f"⚠️ 无法解析流式数据: {data_str}")
                
                logger.info(f"✅ 流式API调用成功，响应长度: {len(full_content)}")
                
                # 方案3：通过重新发送完整对话获取100%准确的token统计
                # 将原始输入+AI完整回复作为完整对话，用非流式请求获取精确token计数
                logger.info(f"🔍 [token] 开始执行方案3：完整对话token统计...")
                accurate_usage = self._get_accurate_tokens_via_complete_conversation(api_messages, full_content, headers, api_url, request_timeout)
                
                if accurate_usage:
                    # 使用100%准确的token数据
                    self._last_api_usage = accurate_usage
                    logger.info(f"✅ [token] 获取到100%准确的token统计: 输入={accurate_usage['prompt_tokens']}, 输出={accurate_usage['completion_tokens']}")
                else:
                    # 如果无法获取准确数据，回退到估算
                    logger.warning(f"⚠️ [token] 方案3失败，回退到估算方法")
                    input_text = " ".join([msg['content'] for msg in api_messages])
                    input_tokens = max(1, int(len(input_text) * 0.75))
                    output_tokens = max(1, int(len(full_content) * 0.75))
                    
                    self._last_api_usage = {
                        'prompt_tokens': input_tokens,
                        'completion_tokens': output_tokens,
                        'total_tokens': input_tokens + output_tokens
                    }
                    logger.warning(f"⚠️ [token] 回退到估算方法: 输入≈{input_tokens}, 输出≈{output_tokens}")
                
                # 构造LangChain格式的响应
                ai_message = AIMessage(content=full_content)
                generation = ChatGeneration(message=ai_message)
                return ChatResult(generations=[generation])
            else:
                # 非流式请求处理（保持原有的处理逻辑）
                response = requests.post(
                    api_url,
                    headers=headers,
                    json=request_data,
                    timeout=request_timeout
                )
                
                # 检查响应
                if response.status_code == 200:
                    data = response.json()
                    content = data['choices'][0]['message']['content']
                    
                    # 提取真实的token使用信息
                    if 'usage' in data:
                        usage = data['usage']
                        self._last_api_usage = {
                            'prompt_tokens': usage.get('prompt_tokens', 0),
                            'completion_tokens': usage.get('completion_tokens', 0),
                            'total_tokens': usage.get('total_tokens', 0)
                        }
                        logger.debug(f"🔍 [token] 非流式响应真实token使用: {self._last_api_usage}")
                    else:
                        # 如果没有usage字段，进行估算
                        input_text = " ".join([msg['content'] for msg in api_messages])
                        input_tokens = max(1, int(len(input_text) * 0.75))
                        output_tokens = max(1, int(len(content) * 0.75))
                        self._last_api_usage = {
                            'prompt_tokens': input_tokens,
                            'completion_tokens': output_tokens,
                            'total_tokens': input_tokens + output_tokens
                        }
                        logger.debug(f"🔍 [token] 非流式响应估算token使用: {self._last_api_usage}")
                    
                    logger.info(f"✅ 直接API调用成功，响应长度: {len(content)}")
                    
                    # 构造LangChain格式的响应
                    ai_message = AIMessage(content=content)
                    generation = ChatGeneration(message=ai_message)
                    return ChatResult(generations=[generation])
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    logger.error(f"❌ 直接API调用失败: {error_msg}")
                    
                    # 特别处理token解析错误
                    if "Unexpected token" in response.text and "while expecting start token" in response.text:
                        logger.warning(f"🔧 检测到token解析错误，尝试重新清理消息格式")
                        # 尝试更激进的消息清理
                        cleaned_messages = self._aggressive_clean_messages(api_messages)
                        if cleaned_messages != api_messages:
                            logger.info(f"🔄 使用激进清理后的消息重试")
                            request_data['messages'] = cleaned_messages
                            retry_response = requests.post(
                                api_url,
                                headers=headers,
                                json=request_data,
                                timeout=request_timeout
                            )
                            if retry_response.status_code == 200:
                                data = retry_response.json()
                                content = data['choices'][0]['message']['content']
                                logger.info(f"✅ 重试成功，响应长度: {len(content)}")
                                ai_message = AIMessage(content=content)
                                generation = ChatGeneration(message=ai_message)
                                return ChatResult(generations=[generation])
                    
                    # 根据不同的错误代码提供友好的错误信息
                    if response.status_code == 400:
                        if "Unexpected token" in response.text:
                            raise Exception("输入格式错误：消息包含模型无法解析的特殊字符或格式，请简化输入内容")
                        else:
                            raise Exception(f"请求格式错误：{response.text}")
                    elif response.status_code == 401:
                        raise Exception("身份验证失败：请检查API密钥是否正确")
                    elif response.status_code == 403:
                        raise Exception("访问被拒绝：请检查API密钥权限")
                    elif response.status_code == 429:
                        raise Exception("请求频率超限：请稍后再试")
                    elif response.status_code >= 500:
                        raise Exception(f"服务器错误 ({response.status_code})：上游API服务暂时不可用")
                    else:
                        raise Exception(f"未知错误 ({response.status_code})：{response.text}")
                        
        except requests.exceptions.Timeout:
            raise Exception("请求超时：网络连接问题或服务器响应过慢")
        except requests.exceptions.ConnectionError:
            raise Exception("连接错误：无法连接到API服务器")
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求错误：{str(e)}")
    
    def _get_accurate_tokens_via_complete_conversation(self, original_messages, ai_response_content, headers, api_url, request_timeout):
        """
        方案3：通过重新发送完整对话获取100%准确的token统计
        将原始输入+AI完整回复构建成完整对话，用非流式请求精确计算token数量
        
        Args:
            original_messages: 原始用户输入消息
            ai_response_content: AI的完整流式回复内容
            headers: 请求头
            api_url: API URL
            request_timeout: 超时时间
            
        Returns:
            dict: 包含100%准确token使用信息的字典，如果失败返回None
        """
        import requests  # 确保导入requests
        
        try:
            # 构建完整的对话历史（用户输入 + AI完整回复）
            complete_conversation = []
            
            # 1. 添加原始用户消息
            for msg in original_messages:
                complete_conversation.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
            
            # 2. 添加AI的完整回复
            complete_conversation.append({
                'role': 'assistant',
                'content': ai_response_content
            })
            
            # 3. 构建统计请求：将完整对话作为输入，用极小输出获取token统计
            token_counting_request = {
                'model': getattr(self, 'model', getattr(self, 'model_name', 'gpt-3.5-turbo')),
                'messages': complete_conversation,  # 🔑 关键：完整对话作为输入
                'temperature': 0.1,
                'max_tokens': 1,      # 🔑 最小输出，仅为获取token统计
                'stream': False       # 🔑 非流式获取usage信息
            }
            
            logger.debug(f"🔍 [token] 发送完整对话进行token统计...")
            logger.debug(f"   对话轮次: {len(complete_conversation)}")
            logger.debug(f"   最后AI回复长度: {len(ai_response_content)}字符")
            
            response = requests.post(
                api_url,
                headers=headers,
                json=token_counting_request,
                timeout=min(15, request_timeout)  # 使用适中的超时时间
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'usage' in data:
                    usage = data['usage']
                    total_conversation_tokens = usage.get('prompt_tokens', 0)
                    
                    # 🎯 关键计算：从总token数中分离出原始输入和AI输出的token数
                    # 发送一个只包含原始输入的请求，获取纯输入的token数
                    input_only_usage = self._get_input_only_tokens(original_messages, headers, api_url, request_timeout)
                    
                    if input_only_usage:
                        accurate_input_tokens = input_only_usage.get('prompt_tokens', 0)
                        # AI输出的token数 = 完整对话的输入token数 - 原始输入的token数
                        accurate_output_tokens = total_conversation_tokens - accurate_input_tokens
                        
                        # 验证计算结果的合理性
                        if accurate_output_tokens > 0:
                            result = {
                                'prompt_tokens': accurate_input_tokens,      # 原始用户输入的准确token数
                                'completion_tokens': accurate_output_tokens, # AI输出的准确token数
                                'total_tokens': accurate_input_tokens + accurate_output_tokens
                            }
                            
                            logger.info(f"🎯 [token] 完整对话token分析:")
                            logger.info(f"   完整对话输入tokens: {total_conversation_tokens}")
                            logger.info(f"   原始输入tokens: {accurate_input_tokens}")
                            logger.info(f"   AI输出tokens: {accurate_output_tokens}")
                            logger.info(f"   计算验证: {accurate_input_tokens} + {accurate_output_tokens} = {result['total_tokens']}")
                            
                            return result
                        else:
                            logger.warning(f"⚠️ [token] 计算出的输出token数异常: {accurate_output_tokens}")
                    else:
                        logger.warning(f"⚠️ [token] 无法获取原始输入的token数")
                else:
                    logger.warning(f"⚠️ [token] 完整对话请求未返回usage信息")
            else:
                logger.warning(f"⚠️ [token] 完整对话请求失败: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"⚠️ [token] 完整对话token统计失败: {e}")
        
        return None
    
    def _get_input_only_tokens(self, original_messages, headers, api_url, request_timeout):
        """
        获取纯输入消息的token数量
        
        Args:
            original_messages: 原始用户输入消息
            headers: 请求头
            api_url: API URL
            request_timeout: 超时时间
            
        Returns:
            dict: 包含输入token信息，如果失败返回None
        """
        import requests  # 确保导入requests
        
        try:
            # 构建只包含原始输入的请求
            input_only_request = {
                'model': getattr(self, 'model', getattr(self, 'model_name', 'gpt-3.5-turbo')),
                'messages': original_messages,  # 🔑 只有原始用户输入
                'temperature': 0.1,
                'max_tokens': 1,     # 最小输出
                'stream': False
            }
            
            logger.debug(f"🔍 [token] 计算原始输入token数...")
            
            response = requests.post(
                api_url,
                headers=headers,
                json=input_only_request,
                timeout=min(10, request_timeout)
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'usage' in data:
                    return data['usage']
                    
        except Exception as e:
            logger.warning(f"⚠️ [token] 获取输入token数失败: {e}")
        
        return None
    
    def _get_accurate_usage_for_streaming(self, api_messages, full_content, headers, api_url, request_timeout):
        """
        为流式响应获取准确的token使用统计
        通过发送一个简化的非流式请求来获取准确的token计费信息
        
        Args:
            api_messages: 原始消息
            full_content: 流式响应的完整内容
            headers: 请求头
            api_url: API URL
            request_timeout: 超时时间
            
        Returns:
            dict: 包含准确token使用信息的字典，如果失败返回None
        """
        try:
            # 构建一个简化的非流式请求来获取token使用信息
            # 使用相同的输入和一个简短的输出限制，快速获取准确的输入token数
            simplified_request = {
                'model': getattr(self, 'model_name', 'gpt-3.5-turbo'),
                'messages': api_messages,  # 使用相同的输入
                'temperature': 0.1,  # 降低随机性
                'max_tokens': 1,      # 最小输出，仅为获取token统计
                'stream': False       # 非流式请求
            }
            
            logger.debug(f"🔍 [token] 发送简化请求获取准确token统计...")
            
            response = requests.post(
                api_url,
                headers=headers,
                json=simplified_request,
                timeout=min(10, request_timeout)  # 使用较短的超时
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'usage' in data:
                    usage = data['usage']
                    accurate_input_tokens = usage.get('prompt_tokens', 0)
                    
                    # 对于输出token，我们需要估算实际流式输出的token数
                    # 因为简化请求只输出了1个token，但实际输出更多
                    # 使用更精确的估算方法
                    actual_output_tokens = self._estimate_output_tokens_accurately(full_content)
                    
                    return {
                        'prompt_tokens': accurate_input_tokens,  # 使用API返回的准确输入token数
                        'completion_tokens': actual_output_tokens,  # 使用改进的输出token估算
                        'total_tokens': accurate_input_tokens + actual_output_tokens
                    }
                else:
                    logger.warning(f"⚠️ [token] 简化请求未返回usage信息")
            else:
                logger.warning(f"⚠️ [token] 简化请求失败: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"⚠️ [token] 获取准确token统计失败: {e}")
        
        return None
    
    def _estimate_output_tokens_accurately(self, content):
        """
        更准确地估算输出token数量
        基于改进的算法，考虑中英文混合、标点符号等因素
        
        Args:
            content: 输出内容
            
        Returns:
            int: 估算的token数量
        """
        if not content:
            return 0
        
        # 分别处理中文、英文、数字、标点符号
        import re
        
        # 中文字符（包括中文标点）
        chinese_chars = re.findall(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', content)
        chinese_count = len(chinese_chars)
        
        # 英文单词（连续的字母）
        english_words = re.findall(r'[a-zA-Z]+', content)
        english_word_count = len(english_words)
        
        # 数字
        numbers = re.findall(r'\d+', content)
        number_count = len(numbers)
        
        # 特殊符号和emoji
        emojis = re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', content)
        emoji_count = len(emojis)
        
        # 标点符号
        punctuation = re.findall(r'[^\w\s\u4e00-\u9fff]', content)
        punct_count = len(punctuation) - emoji_count  # 排除emoji
        
        # 根据不同类型内容计算token数
        estimated_tokens = 0
        estimated_tokens += chinese_count * 1.2    # 中文字符，约1.2 token/字符
        estimated_tokens += english_word_count * 1.3  # 英文单词，约1.3 token/词
        estimated_tokens += number_count * 0.8    # 数字，约0.8 token/数字
        estimated_tokens += emoji_count * 1.5     # emoji，约1.5 token/emoji
        estimated_tokens += punct_count * 0.5     # 标点符号，约0.5 token/符号
        
        result = max(1, int(estimated_tokens))
        
        logger.debug(f"🔍 [token] 详细输出估算: 中文{chinese_count}*1.2 + 英文{english_word_count}*1.3 + 数字{number_count}*0.8 + emoji{emoji_count}*1.5 + 标点{punct_count}*0.5 = {result}")
        
        return result


def create_third_party_openai(
    model: str,
    api_key: str,
    base_url: str = "https://llm.submodel.ai/v1",
    temperature: float = 0.1,
    max_tokens: int = 2000,
    session_id: Optional[str] = None
) -> ThirdPartyOpenAI:
    """
    创建第三方OpenAI适配器的便捷函数
    
    Args:
        model: 模型名称
        api_key: API密钥
        base_url: API基础URL
        temperature: 温度参数
        max_tokens: 最大token数
        session_id: 会话ID用于token跟踪
        
    Returns:
        第三方OpenAI适配器实例
    """
    
    return ThirdPartyOpenAI(
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
        max_tokens=max_tokens,
        session_id=session_id
    )


# 为了向后兼容
CompatibleChatOpenAI = ThirdPartyOpenAI
