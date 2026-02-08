"""
MCP 客户端封装

提供与 TrendRadar MCP Server 的通信接口
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MCPClient:
    """TrendRadar MCP 客户端封装"""
    
    def __init__(self, trendradar_root: str):
        """
        初始化 MCP 客户端
        
        Args:
            trendradar_root: TrendRadar 项目根目录
        """
        self.trendradar_root = Path(trendradar_root)
        if not self.trendradar_root.exists():
            raise ValueError(f"TrendRadar 路径不存在: {trendradar_root}")
        
        # 添加 TrendRadar 到 Python 路径
        if str(self.trendradar_root) not in sys.path:
            sys.path.insert(0, str(self.trendradar_root))
        
        logger.info(f"初始化 MCP 客户端，TrendRadar 路径: {trendradar_root}")
    
    async def get_latest_news(
        self,
        platforms: Optional[List[str]] = None,
        limit: int = 50,
        include_url: bool = False
    ) -> Dict[str, Any]:
        """
        获取最新新闻
        
        Args:
            platforms: 平台列表，None 表示所有平台
            limit: 返回条数限制
            include_url: 是否包含链接
            
        Returns:
            包含新闻列表的字典
        """
        logger.info(f"获取最新新闻: platforms={platforms}, limit={limit}")
        
        try:
            from mcp_server.tools.data_query import DataQueryTools
            
            tools = DataQueryTools(str(self.trendradar_root))
            result = tools.get_latest_news(
                platforms=platforms,
                limit=limit,
                include_url=include_url
            )
            
            logger.info(f"获取新闻成功，返回 {len(result.get('data', {}).get('news', []))} 条")
            return result
            
        except Exception as e:
            logger.error(f"获取最新新闻失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "data": {"news": []}
            }
    
    async def get_trending_topics(
        self,
        date_range: Optional[Dict[str, str]] = None,
        platforms: Optional[List[str]] = None,
        min_frequency: int = 2,
        top_n: int = 20
    ) -> Dict[str, Any]:
        """
        获取热门话题
        
        Args:
            date_range: 日期范围 {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}
            platforms: 平台列表
            min_frequency: 最小出现频率
            top_n: 返回前 N 个话题
            
        Returns:
            包含热门话题的字典
        """
        logger.info(f"获取热门话题: date_range={date_range}, top_n={top_n}")
        
        try:
            from mcp_server.tools.data_query import DataQueryTools
            
            tools = DataQueryTools(str(self.trendradar_root))
            result = tools.get_trending_topics(
                date_range=date_range,
                platforms=platforms,
                min_frequency=min_frequency,
                top_n=top_n
            )
            
            topics = result.get('data', {}).get('topics', [])
            logger.info(f"获取热门话题成功，返回 {len(topics)} 个")
            return result
            
        except Exception as e:
            logger.error(f"获取热门话题失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "data": {"topics": []}
            }
    
    async def search_news(
        self,
        keyword: str,
        search_in_rss: bool = True,
        date_range: Optional[Dict[str, str]] = None,
        platforms: Optional[List[str]] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        搜索新闻
        
        Args:
            keyword: 搜索关键词
            search_in_rss: 是否搜索 RSS
            date_range: 日期范围
            platforms: 平台列表
            limit: 返回条数限制
            
        Returns:
            包含搜索结果的字典
        """
        logger.info(f"搜索新闻: keyword={keyword}, limit={limit}")
        
        try:
            from mcp_server.tools.search_tools import SearchTools
            
            tools = SearchTools(str(self.trendradar_root))
            result = tools.search_news(
                keyword=keyword,
                search_in_rss=search_in_rss,
                date_range=date_range,
                platforms=platforms,
                limit=limit
            )
            
            news = result.get('data', {}).get('news', [])
            logger.info(f"搜索新闻成功，返回 {len(news)} 条")
            return result
            
        except Exception as e:
            logger.error(f"搜索新闻失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "data": {"news": []}
            }
    
    async def resolve_date_range(self, expression: str) -> Dict[str, Any]:
        """
        解析日期范围表达式
        
        Args:
            expression: 日期表达式，如 "今天", "最近7天", "本周" 等
            
        Returns:
            包含日期范围的字典
        """
        logger.info(f"解析日期范围: {expression}")
        
        try:
            from mcp_server.utils.date_parser import DateParser
            from mcp_server.services.data_service import DataService
            
            data_service = DataService(str(self.trendradar_root))
            parser = DateParser(data_service.get_timezone())
            
            result = parser.parse(expression)
            logger.info(f"解析日期范围成功: {result}")
            return result
            
        except Exception as e:
            logger.error(f"解析日期范围失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_latest_rss(
        self,
        feeds: Optional[List[str]] = None,
        limit: int = 50,
        include_url: bool = True
    ) -> Dict[str, Any]:
        """
        获取最新 RSS
        
        Args:
            feeds: RSS 源 ID 列表
            limit: 返回条数限制
            include_url: 是否包含链接
            
        Returns:
            包含 RSS 文章的字典
        """
        logger.info(f"获取最新 RSS: feeds={feeds}, limit={limit}")
        
        try:
            from mcp_server.tools.data_query import DataQueryTools
            
            tools = DataQueryTools(str(self.trendradar_root))
            result = tools.get_latest_rss(
                feeds=feeds,
                limit=limit,
                include_url=include_url
            )
            
            articles = result.get('data', {}).get('articles', [])
            logger.info(f"获取 RSS 成功，返回 {len(articles)} 条")
            return result
            
        except Exception as e:
            logger.error(f"获取 RSS 失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "data": {"articles": []}
            }


# 同步包装器，方便在非异步环境中使用
class SyncMCPClient:
    """同步版本的 MCP 客户端"""
    
    def __init__(self, trendradar_root: str):
        self.client = MCPClient(trendradar_root)
    
    def _run_async(self, coro):
        """运行异步函数"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)
    
    def get_latest_news(self, **kwargs) -> Dict[str, Any]:
        return self._run_async(self.client.get_latest_news(**kwargs))
    
    def get_trending_topics(self, **kwargs) -> Dict[str, Any]:
        return self._run_async(self.client.get_trending_topics(**kwargs))
    
    def search_news(self, **kwargs) -> Dict[str, Any]:
        return self._run_async(self.client.search_news(**kwargs))
    
    def resolve_date_range(self, expression: str) -> Dict[str, Any]:
        return self._run_async(self.client.resolve_date_range(expression))
    
    def get_latest_rss(self, **kwargs) -> Dict[str, Any]:
        return self._run_async(self.client.get_latest_rss(**kwargs))
