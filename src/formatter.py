"""
消息格式化模块

将处理后的数据格式化为企业微信消息
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MessageFormatter:
    """消息格式化器"""
    
    # Emoji 映射
    PLATFORM_EMOJI = {
        'zhihu': '📚',
        'weibo': '🔍',
        'toutiao': '📰',
        'baidu': '🔎',
        'douyin': '📱',
        'bilibili': '📺',
        'tieba': '💬',
        'thepaper': '📄',
        'ifeng': '🦅',
        'wallstreetcn': '💼',
        'cls': '💹',
    }
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化格式化器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.format_config = config.get('push', {}).get('format', {})
        
        logger.info("初始化消息格式化器")
    
    def format_news_push(
        self,
        grouped_news: Dict[str, List[Dict[str, Any]]],
        trending_topics: Optional[List[Dict[str, Any]]] = None,
        title: Optional[str] = None
    ) -> str:
        """
        格式化新闻推送消息
        
        Args:
            grouped_news: 按关键词分组的新闻
            trending_topics: 热门话题列表
            title: 自定义标题
            
        Returns:
            格式化后的 Markdown 消息
        """
        logger.info(f"开始格式化消息，关键词组数: {len(grouped_news)}")
        
        # 构建消息
        lines = []
        
        # 1. 标题
        if title is None:
            now = datetime.now().strftime('%Y-%m-%d %H:%M')
            title = f"📰 热点新闻推送 ({now})"
        lines.append(title)
        lines.append("")
        
        # 2. 热门话题（如果有）
        if trending_topics:
            lines.append("🔥 热门话题 TOP 5")
            lines.append("━━━━━━━━━━━━━━━━━━")
            for i, topic in enumerate(trending_topics[:5], 1):
                topic_name = topic.get('keyword', '未知')
                frequency = topic.get('frequency', 0)
                platforms = topic.get('platforms', [])
                
                platform_str = " | ".join([
                    f"{self._get_platform_emoji(p['platform'])} {p['platform']} #{p['min_rank']}"
                    for p in platforms[:2]  # 只显示前2个平台
                ])
                
                lines.append(f"{i}. [{topic_name}] (热度: {frequency})")
                if platform_str:
                    lines.append(f"   {platform_str}")
                lines.append("")
            
            lines.append("━━━━━━━━━━━━━━━━━━")
        
        # 3. 关键词匹配新闻
        if grouped_news:
            # 统计总数
            total_count = sum(len(news_list) for news_list in grouped_news.values())
            keyword_list = ", ".join(grouped_news.keys())
            
            lines.append(f"🎯 关键词匹配: {keyword_list}")
            lines.append(f"📊 共 {total_count} 条新闻")
            lines.append("━━━━━━━━━━━━━━━━━━")
            lines.append("")
            
            # 按关键词分组显示
            for keyword, news_list in grouped_news.items():
                lines.append(f"📌 {keyword} 相关 ({len(news_list)}条)")
                
                for news in news_list:
                    lines.append(self._format_news_item(news))
                
                lines.append("")  # 组间空行
        
        # 4. 页脚
        lines.append("━━━━━━━━━━━━━━━━━━")
        lines.append("✨ Powered by TrendRadar + OpenClaw")
        
        message = "\n".join(lines)
        
        logger.info(f"消息格式化完成，长度: {len(message)} 字符")
        return message
    
    def format_trending_topics_only(
        self,
        topics: List[Dict[str, Any]],
        title: Optional[str] = None,
        top_n: int = 10
    ) -> str:
        """
        仅格式化热门话题消息
        
        Args:
            topics: 热门话题列表
            title: 自定义标题
            top_n: 显示前 N 个话题
            
        Returns:
            格式化后的 Markdown 消息
        """
        logger.info(f"格式化热门话题消息，话题数: {len(topics)}")
        
        lines = []
        
        # 标题
        if title is None:
            now = datetime.now().strftime('%Y-%m-%d %H:%M')
            title = f"🔥 热门话题榜 ({now})"
        lines.append(title)
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━")
        
        # 话题列表
        for i, topic in enumerate(topics[:top_n], 1):
            keyword = topic.get('keyword', '未知')
            frequency = topic.get('frequency', 0)
            platforms = topic.get('platforms', [])
            
            # 话题行
            lines.append(f"{i}. **{keyword}** (热度: {frequency})")
            
            # 平台信息
            if platforms:
                platform_lines = []
                for p in platforms[:3]:  # 最多显示3个平台
                    emoji = self._get_platform_emoji(p['platform'])
                    rank = p['min_rank']
                    platform_lines.append(f"{emoji} {p['platform']} #{rank}")
                
                lines.append(f"   {' | '.join(platform_lines)}")
            
            lines.append("")
        
        lines.append("━━━━━━━━━━━━━━━━━━")
        lines.append("✨ Powered by TrendRadar + OpenClaw")
        
        message = "\n".join(lines)
        
        logger.info(f"热门话题消息格式化完成")
        return message
    
    def _format_news_item(self, news: Dict[str, Any]) -> str:
        """
        格式化单条新闻
        
        Args:
            news: 新闻数据
            
        Returns:
            格式化后的新闻条目
        """
        title = news.get('title', '无标题')
        rank = news.get('rank', '')
        platform = news.get('source', '')
        url = news.get('url', '')
        
        # 构建基本信息
        parts = []
        
        # 排名（如果配置显示且存在）
        show_ranking = self.format_config.get('show_ranking', True)
        if show_ranking and rank:
            parts.append(f"#{rank}")
        
        # 平台（如果配置显示）
        show_platform = self.format_config.get('show_platform', True)
        if show_platform and platform:
            emoji = self._get_platform_emoji(platform)
            parts.append(f"{emoji} {platform}")
        
        # 组装信息行
        info = " | ".join(parts) if parts else ""
        
        # 标题行
        show_url = self.format_config.get('show_url', False)
        if show_url and url:
            title_line = f"• [{title}]({url})"
        else:
            title_line = f"• {title}"
        
        # 组合
        if info:
            return f"{title_line}\n  {info}"
        else:
            return title_line
    
    def _get_platform_emoji(self, platform: str) -> str:
        """
        获取平台 Emoji
        
        Args:
            platform: 平台标识
            
        Returns:
            Emoji 字符
        """
        # 将平台名转为小写并移除特殊字符
        platform_key = platform.lower().replace('-', '').replace('_', '')
        
        # 尝试匹配
        for key, emoji in self.PLATFORM_EMOJI.items():
            if key in platform_key or platform_key in key:
                return emoji
        
        return '📱'  # 默认 emoji
    
    def format_rss_push(
        self,
        articles: List[Dict[str, Any]],
        title: Optional[str] = None,
        max_items: int = 10
    ) -> str:
        """
        格式化 RSS 推送消息
        
        Args:
            articles: RSS 文章列表
            title: 自定义标题
            max_items: 最多显示条数
            
        Returns:
            格式化后的 Markdown 消息
        """
        logger.info(f"格式化 RSS 消息，文章数: {len(articles)}")
        
        lines = []
        
        # 标题
        if title is None:
            now = datetime.now().strftime('%Y-%m-%d %H:%M')
            title = f"📚 RSS 订阅更新 ({now})"
        lines.append(title)
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━")
        
        # 文章列表
        for article in articles[:max_items]:
            article_title = article.get('title', '无标题')
            source = article.get('source', '未知来源')
            url = article.get('url', '')
            pub_date = article.get('pub_date', '')
            
            # 标题行
            if url:
                lines.append(f"• [{article_title}]({url})")
            else:
                lines.append(f"• {article_title}")
            
            # 来源和时间
            info_parts = []
            if source:
                info_parts.append(f"📰 {source}")
            if pub_date:
                # 格式化日期（如果是 ISO 格式）
                try:
                    dt = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                    formatted_date = dt.strftime('%m-%d %H:%M')
                    info_parts.append(f"🕐 {formatted_date}")
                except:
                    info_parts.append(f"🕐 {pub_date}")
            
            if info_parts:
                lines.append(f"  {' | '.join(info_parts)}")
            
            lines.append("")
        
        # 提示（如果有更多文章）
        if len(articles) > max_items:
            lines.append(f"... 还有 {len(articles) - max_items} 篇文章未显示")
            lines.append("")
        
        lines.append("━━━━━━━━━━━━━━━━━━")
        lines.append("✨ Powered by TrendRadar + OpenClaw")
        
        message = "\n".join(lines)
        
        logger.info(f"RSS 消息格式化完成")
        return message
    
    def format_error_message(self, error: str) -> str:
        """
        格式化错误消息
        
        Args:
            error: 错误信息
            
        Returns:
            格式化后的错误消息
        """
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        return f"""⚠️ TrendRadar 推送失败 ({now})

发生错误: {error}

请检查日志文件或联系管理员。

━━━━━━━━━━━━━━━━━━
TrendRadar + OpenClaw"""
    
    def truncate_message(self, message: str, max_length: int = 4000) -> str:
        """
        截断过长的消息
        
        Args:
            message: 原始消息
            max_length: 最大长度
            
        Returns:
            截断后的消息
        """
        if len(message) <= max_length:
            return message
        
        logger.warning(f"消息过长 ({len(message)} > {max_length})，进行截断")
        
        # 保留前面内容 + 截断提示
        truncated = message[:max_length - 100]
        truncated += "\n\n... (消息过长，已截断)\n\n━━━━━━━━━━━━━━━━━━\n✨ Powered by TrendRadar + OpenClaw"
        
        return truncated
