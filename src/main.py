"""
TrendRadar + OpenClaw 集成主程序

定时获取热点新闻并推送到企业微信
"""

import argparse
import logging
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

from mcp_client import SyncMCPClient
from data_processor import DataProcessor
from formatter import MessageFormatter
from pusher import Pusher


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/root/.openclaw/workspace/trendradar-integration/trendradar.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class TrendRadarIntegration:
    """TrendRadar + OpenClaw 集成服务"""
    
    def __init__(self, config_path: str):
        """
        初始化集成服务
        
        Args:
            config_path: 配置文件路径
        """
        logger.info("=" * 60)
        logger.info("TrendRadar + OpenClaw 集成服务启动")
        logger.info("=" * 60)
        
        # 加载配置
        self.config = self._load_config(config_path)
        
        # 初始化组件
        trendradar_root = self.config['trendradar']['root_path']
        self.mcp_client = SyncMCPClient(trendradar_root)
        self.data_processor = DataProcessor(self.config)
        self.formatter = MessageFormatter(self.config)
        self.pusher = Pusher(self.config)
        
        logger.info("所有组件初始化完成")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置字典
        """
        logger.info(f"加载配置文件: {config_path}")
        
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        logger.info("配置文件加载成功")
        return config
    
    def run(self, mode: str = 'news', dry_run: bool = False):
        """
        运行集成服务
        
        Args:
            mode: 运行模式，可选 'news', 'topics', 'rss', 'all'
            dry_run: 是否为测试模式（不实际推送）
        """
        logger.info(f"运行模式: {mode}, 测试模式: {dry_run}")
        
        try:
            if mode == 'news':
                self._run_news_push(dry_run)
            elif mode == 'topics':
                self._run_topics_push(dry_run)
            elif mode == 'rss':
                self._run_rss_push(dry_run)
            elif mode == 'all':
                self._run_all_push(dry_run)
            else:
                logger.error(f"未知的运行模式: {mode}")
                return
            
            logger.info("运行完成")
            
        except Exception as e:
            logger.error(f"运行失败: {e}", exc_info=True)
            
            # 发送错误通知
            if not dry_run:
                error_message = self.formatter.format_error_message(str(e))
                self.pusher.push(error_message)
    
    def _run_news_push(self, dry_run: bool = False):
        """
        运行新闻推送
        
        Args:
            dry_run: 是否为测试模式
        """
        logger.info("开始新闻推送流程")
        
        # 1. 获取最新新闻
        platforms = self.config.get('sources', {}).get('platforms')
        result = self.mcp_client.get_latest_news(
            platforms=platforms,
            limit=100,
            include_url=self.formatter.format_config.get('show_url', False)
        )
        
        if not result.get('success'):
            raise Exception(f"获取新闻失败: {result.get('error')}")
        
        news_list = result.get('data', {}).get('news', [])
        logger.info(f"获取到 {len(news_list)} 条新闻")
        
        if not news_list:
            logger.info("无新闻数据，跳过推送")
            return
        
        # 2. 处理新闻
        processed_news = self.data_processor.process_news(news_list)
        
        # 3. 按关键词分组
        grouped_news = self.data_processor.filter_by_keywords(processed_news)
        
        if not grouped_news:
            logger.info("无匹配关键词的新闻，跳过推送")
            return
        
        # 4. 限制每组数量
        grouped_news = self.data_processor.limit_items_per_group(grouped_news)
        
        # 5. 获取热门话题（可选）
        trending_topics = None
        if self.config.get('keywords', {}).get('show_trending', False):
            topics_result = self.mcp_client.get_trending_topics(top_n=5)
            if topics_result.get('success'):
                trending_topics = topics_result.get('data', {}).get('topics', [])
        
        # 6. 格式化消息
        message = self.formatter.format_news_push(
            grouped_news=grouped_news,
            trending_topics=trending_topics
        )
        
        # 截断过长消息
        message = self.formatter.truncate_message(message)
        
        # 7. 推送消息
        success = self.pusher.push(message, dry_run=dry_run)
        
        if success:
            logger.info("新闻推送成功")
        else:
            logger.error("新闻推送失败")
    
    def _run_topics_push(self, dry_run: bool = False):
        """
        运行热门话题推送
        
        Args:
            dry_run: 是否为测试模式
        """
        logger.info("开始热门话题推送流程")
        
        # 1. 获取热门话题
        platforms = self.config.get('sources', {}).get('platforms')
        result = self.mcp_client.get_trending_topics(
            platforms=platforms,
            top_n=20
        )
        
        if not result.get('success'):
            raise Exception(f"获取热门话题失败: {result.get('error')}")
        
        topics = result.get('data', {}).get('topics', [])
        logger.info(f"获取到 {len(topics)} 个热门话题")
        
        if not topics:
            logger.info("无热门话题数据，跳过推送")
            return
        
        # 2. 格式化消息
        message = self.formatter.format_trending_topics_only(topics, top_n=10)
        
        # 3. 推送消息
        success = self.pusher.push(message, dry_run=dry_run)
        
        if success:
            logger.info("热门话题推送成功")
        else:
            logger.error("热门话题推送失败")
    
    def _run_rss_push(self, dry_run: bool = False):
        """
        运行 RSS 推送
        
        Args:
            dry_run: 是否为测试模式
        """
        logger.info("开始 RSS 推送流程")
        
        # 1. 获取最新 RSS
        feeds = self.config.get('sources', {}).get('rss_feeds')
        result = self.mcp_client.get_latest_rss(
            feeds=feeds,
            limit=20,
            include_url=True
        )
        
        if not result.get('success'):
            raise Exception(f"获取 RSS 失败: {result.get('error')}")
        
        articles = result.get('data', {}).get('articles', [])
        logger.info(f"获取到 {len(articles)} 篇 RSS 文章")
        
        if not articles:
            logger.info("无 RSS 数据，跳过推送")
            return
        
        # 2. 格式化消息
        message = self.formatter.format_rss_push(articles, max_items=10)
        
        # 3. 推送消息
        success = self.pusher.push(message, dry_run=dry_run)
        
        if success:
            logger.info("RSS 推送成功")
        else:
            logger.error("RSS 推送失败")
    
    def _run_all_push(self, dry_run: bool = False):
        """
        运行所有推送（新闻 + RSS）
        
        Args:
            dry_run: 是否为测试模式
        """
        logger.info("开始全量推送流程")
        
        try:
            self._run_news_push(dry_run)
        except Exception as e:
            logger.error(f"新闻推送失败: {e}", exc_info=True)
        
        try:
            self._run_rss_push(dry_run)
        except Exception as e:
            logger.error(f"RSS 推送失败: {e}", exc_info=True)
    
    def test(self):
        """测试连接和配置"""
        logger.info("开始测试")
        
        # 测试 MCP 连接
        logger.info("测试 MCP 连接...")
        try:
            result = self.mcp_client.get_latest_news(limit=1)
            if result.get('success'):
                logger.info("✅ MCP 连接正常")
            else:
                logger.error(f"❌ MCP 连接失败: {result.get('error')}")
        except Exception as e:
            logger.error(f"❌ MCP 连接异常: {e}")
        
        # 测试推送连接
        logger.info("测试推送连接...")
        if self.pusher.test_connection():
            logger.info("✅ 推送连接正常")
        else:
            logger.error("❌ 推送连接失败")
        
        logger.info("测试完成")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='TrendRadar + OpenClaw 集成服务'
    )
    parser.add_argument(
        '--config',
        default='/root/.openclaw/workspace/trendradar-integration/config.yaml',
        help='配置文件路径'
    )
    parser.add_argument(
        '--mode',
        choices=['news', 'topics', 'rss', 'all'],
        default='news',
        help='运行模式'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='测试模式（不实际推送）'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='运行测试'
    )
    
    args = parser.parse_args()
    
    try:
        integration = TrendRadarIntegration(args.config)
        
        if args.test:
            integration.test()
        else:
            integration.run(mode=args.mode, dry_run=args.dry_run)
    
    except Exception as e:
        logger.error(f"程序运行失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
