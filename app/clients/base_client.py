"""基础客户端类，定义通用接口"""
from typing import AsyncGenerator, Any
import aiohttp
from app.utils.logger import logger
from abc import ABC, abstractmethod
import os

class BaseClient(ABC):
    def __init__(self, api_key: str, api_url: str):
        """初始化基础客户端
        
        Args:
            api_key: API密钥
            api_url: API地址
        """
        self.api_key = api_key
        self.api_url = api_url
        # 从环境变量获取代理配置
        self.proxy = os.getenv("PROXY")
        
    async def _make_request(self, headers: dict, data: dict) -> AsyncGenerator[bytes, None]:
        """发送请求并处理响应
        
        Args:
            headers: 请求头
            data: 请求数据
            
        Yields:
            bytes: 原始响应数据
        """
        if self.proxy:
            logger.debug(f"使用代理: {self.proxy}")
        
        try:
            async with aiohttp.ClientSession() as session:
                # 构建请求参数
                request_kwargs = {
                    "headers": headers,
                    "json": data
                }
                # 仅在配置了代理时添加 proxy 参数
                if self.proxy:
                    request_kwargs["proxy"] = self.proxy
    
                async with session.post(self.api_url, **request_kwargs) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API 请求失败: {error_text}")
                        return
                        
                    async for chunk in response.content.iter_any():
                        yield chunk
                        
        except Exception as e:
            logger.error(f"请求 API 时发生错误: {e}")
            
    @abstractmethod
    async def stream_chat(self, messages: list, model: str) -> AsyncGenerator[tuple[str, str], None]:
        """流式对话，由子类实现
        
        Args:
            messages: 消息列表
            model: 模型名称
            
        Yields:
            tuple[str, str]: (内容类型, 内容)
        """
        pass
