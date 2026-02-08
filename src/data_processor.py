"""
数据处理模块

对 TrendRadar 返回的数据进行过滤、排序和处理
"""

import logging
import re
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class DataProcessor:
    """数据处理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化数据处理器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.filters = config.get('filters', {})
        self.keywords_config = config.get('keywords', {})
        
        logger.info("初始化数据处理器")
    
    def filter_by_keywords(
        self,
        news_list: List[Dict[str, Any]],
        keywords: Optional[List[str]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        根据关键词过滤和分组新闻
        
        Args:
            news_list: 新闻列表
            keywords: 关键词列表，None 时使用配置中的关键词
            
        Returns:
            按关键词分组的新闻字典 {keyword: [news_items]}
        """
        if keywords is None:
            # 从配置中获取关键词
            keywords = []
            for group in self.keywords_config.get('groups', []):
                keywords.extend(group.get('words', []))
        
        if not keywords:
            logger.warning("未配置关键词，跳过关键词过滤")
            return {}
        
        logger.info(f"使用关键词过滤: {keywords}")
        
        result = {kw: [] for kw in keywords}
        matched_ids = set()  # 记录已匹配的新闻，避免重复
        
        for news in news_list:
            title = news.get('title', '')
            news_id = news.get('id') or news.get('url') or title
            
            # 跳过已匹配的新闻
            if news_id in matched_ids:
                continue
            
            # 检查每个关键词
            for keyword in keywords:
                if self._match_keyword(title, keyword):
                    result[keyword].append(news)
                    matched_ids.add(news_id)
                    break  # 一条新闻只归入一个关键词组
        
        # 移除空的关键词组
        result = {k: v for k, v in result.items() if v}
        
        logger.info(f"关键词过滤完成，匹配到 {len(matched_ids)} 条新闻，分为 {len(result)} 组")
        return result
    
    def _match_keyword(self, text: str, keyword: str) -> bool:
        """
        匹配关键词（大小写不敏感，支持部分匹配）
        
        Args:
            text: 待匹配文本
            keyword: 关键词
            
        Returns:
            是否匹配
        """
        return keyword.lower() in text.lower()
    
    def filter_by_rank(
        self,
        news_list: List[Dict[str, Any]],
        rank_threshold: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        根据排名过滤新闻
        
        Args:
            news_list: 新闻列表
            rank_threshold: 排名阈值，只保留排名 <= threshold 的新闻
            
        Returns:
            过滤后的新闻列表
        """
        if rank_threshold is None:
            rank_threshold = self.filters.get('rank_threshold', 0)
        
        if rank_threshold <= 0:
            return news_list
        
        logger.info(f"根据排名过滤，阈值: {rank_threshold}")
        
        filtered = []
        for news in news_list:
            rank = news.get('rank', 999)
            if rank <= rank_threshold:
                filtered.append(news)
        
        logger.info(f"排名过滤完成，保留 {len(filtered)}/{len(news_list)} 条")
        return filtered
    
    def filter_by_exclude_keywords(
        self,
        news_list: List[Dict[str, Any]],
        exclude_keywords: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        排除包含特定关键词的新闻
        
        Args:
            news_list: 新闻列表
            exclude_keywords: 排除关键词列表
            
        Returns:
            过滤后的新闻列表
        """
        if exclude_keywords is None:
            exclude_keywords = self.filters.get('exclude_keywords', [])
        
        if not exclude_keywords:
            return news_list
        
        logger.info(f"排除关键词: {exclude_keywords}")
        
        filtered = []
        excluded_count = 0
        
        for news in news_list:
            title = news.get('title', '')
            should_exclude = False
            
            for keyword in exclude_keywords:
                if self._match_keyword(title, keyword):
                    should_exclude = True
                    excluded_count += 1
                    break
            
            if not should_exclude:
                filtered.append(news)
        
        logger.info(f"排除关键词过滤完成，排除 {excluded_count} 条，保留 {len(filtered)} 条")
        return filtered
    
    def deduplicate_news(
        self,
        news_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        去重新闻（基于标题相似度）
        
        Args:
            news_list: 新闻列表
            
        Returns:
            去重后的新闻列表
        """
        if not news_list:
            return []
        
        logger.info(f"开始去重，原始数量: {len(news_list)}")
        
        # 使用标题作为去重依据
        seen_titles = set()
        unique_news = []
        
        for news in news_list:
            title = news.get('title', '').strip().lower()
            
            # 简单的标题归一化（移除空格和标点）
            normalized_title = re.sub(r'[^\w\s]', '', title)
            normalized_title = re.sub(r'\s+', '', normalized_title)
            
            if normalized_title and normalized_title not in seen_titles:
                seen_titles.add(normalized_title)
                unique_news.append(news)
        
        logger.info(f"去重完成，保留 {len(unique_news)}/{len(news_list)} 条")
        return unique_news
    
    def sort_news(
        self,
        news_list: List[Dict[str, Any]],
        sort_by: str = 'rank'
    ) -> List[Dict[str, Any]]:
        """
        排序新闻
        
        Args:
            news_list: 新闻列表
            sort_by: 排序字段，可选 'rank', 'hot', 'time'
            
        Returns:
            排序后的新闻列表
        """
        if not news_list:
            return []
        
        logger.info(f"排序新闻，字段: {sort_by}")
        
        if sort_by == 'rank':
            # 按排名升序（排名越小越靠前）
            sorted_list = sorted(news_list, key=lambda x: x.get('rank', 999))
        elif sort_by == 'hot':
            # 按热度降序（热度越高越靠前）
            sorted_list = sorted(
                news_list,
                key=lambda x: float(x.get('hot', 0)),
                reverse=True
            )
        elif sort_by == 'time':
            # 按时间降序（最新的在前）
            sorted_list = sorted(
                news_list,
                key=lambda x: x.get('timestamp', ''),
                reverse=True
            )
        else:
            logger.warning(f"未知的排序字段: {sort_by}，保持原顺序")
            sorted_list = news_list
        
        return sorted_list
    
    def limit_items_per_group(
        self,
        grouped_news: Dict[str, List[Dict[str, Any]]],
        max_items: Optional[int] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        限制每组的新闻数量
        
        Args:
            grouped_news: 分组的新闻字典
            max_items: 每组最大条数，None 或 0 表示不限制
            
        Returns:
            限制后的分组新闻字典
        """
        if max_items is None:
            max_items = self.config.get('push', {}).get('format', {}).get('max_items_per_keyword', 0)
        
        if not max_items or max_items <= 0:
            return grouped_news
        
        logger.info(f"限制每组新闻数量: {max_items}")
        
        result = {}
        for keyword, news_list in grouped_news.items():
            result[keyword] = news_list[:max_items]
            if len(news_list) > max_items:
                logger.info(f"关键词 '{keyword}' 截断: {len(news_list)} -> {max_items}")
        
        return result
    
    def process_news(
        self,
        news_list: List[Dict[str, Any]],
        apply_filters: bool = True
    ) -> List[Dict[str, Any]]:
        """
        应用所有过滤和处理逻辑
        
        Args:
            news_list: 原始新闻列表
            apply_filters: 是否应用过滤器
            
        Returns:
            处理后的新闻列表
        """
        if not news_list:
            return []
        
        logger.info(f"开始处理新闻，原始数量: {len(news_list)}")
        
        result = news_list
        
        if apply_filters:
            # 1. 排除关键词过滤
            result = self.filter_by_exclude_keywords(result)
            
            # 2. 排名过滤
            result = self.filter_by_rank(result)
            
            # 3. 去重
            result = self.deduplicate_news(result)
            
            # 4. 排序
            result = self.sort_news(result, sort_by='rank')
        
        logger.info(f"新闻处理完成，最终数量: {len(result)}")
        return result
    
    def group_by_platform(
        self,
        news_list: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        按平台分组新闻
        
        Args:
            news_list: 新闻列表
            
        Returns:
            按平台分组的新闻字典
        """
        logger.info(f"按平台分组，新闻数量: {len(news_list)}")
        
        result = {}
        for news in news_list:
            platform = news.get('source', '未知平台')
            if platform not in result:
                result[platform] = []
            result[platform].append(news)
        
        logger.info(f"平台分组完成，共 {len(result)} 个平台")
        return result
