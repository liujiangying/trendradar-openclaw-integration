"""
推送模块

负责将消息推送到企业微信等渠道
"""

import logging
import subprocess
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class Pusher:
    """消息推送器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化推送器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.push_config = config.get('push', {})
        
        self.enabled = self.push_config.get('enabled', True)
        self.channel = self.push_config.get('channel', 'wecom')
        self.target = self.push_config.get('target', '')
        
        logger.info(f"初始化推送器: channel={self.channel}, target={self.target}")
    
    def push(self, message: str, dry_run: bool = False) -> bool:
        """
        推送消息
        
        Args:
            message: 要推送的消息
            dry_run: 是否为测试模式（不实际推送，只打印）
            
        Returns:
            是否推送成功
        """
        if not self.enabled:
            logger.info("推送已禁用，跳过")
            return True
        
        if not self.target:
            logger.error("未配置推送目标（target）")
            return False
        
        if dry_run:
            logger.info("===== 测试模式：消息预览 =====")
            print(message)
            logger.info("===== 测试模式结束 =====")
            return True
        
        logger.info(f"开始推送消息到 {self.channel}: {self.target}")
        
        try:
            if self.channel == 'wecom':
                return self._push_to_wecom(message)
            elif self.channel == 'wechat':
                return self._push_to_wechat(message)
            elif self.channel == 'feishu':
                return self._push_to_feishu(message)
            elif self.channel == 'telegram':
                return self._push_to_telegram(message)
            else:
                logger.error(f"不支持的推送渠道: {self.channel}")
                return False
        except Exception as e:
            logger.error(f"推送失败: {e}", exc_info=True)
            return False
    
    def _push_to_wecom(self, message: str) -> bool:
        """
        推送到企业微信
        
        Args:
            message: 消息内容
            
        Returns:
            是否推送成功
        """
        logger.info("推送到企业微信")
        
        try:
            # 使用 openclaw message send 命令
            cmd = [
                'openclaw', 'message', 'send',
                '--channel', 'openclaw-wecom-bot',
                '--target', self.target,
                '--message', message
            ]
            
            logger.debug(f"执行命令: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info("企业微信推送成功")
                return True
            else:
                logger.error(f"企业微信推送失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("企业微信推送超时")
            return False
        except FileNotFoundError:
            logger.error("未找到 openclaw 命令，请检查安装")
            return False
        except Exception as e:
            logger.error(f"企业微信推送异常: {e}", exc_info=True)
            return False
    
    def _push_to_telegram(self, message: str) -> bool:
        """
        推送到 Telegram
        
        Args:
            message: 消息内容
            
        Returns:
            是否推送成功
        """
        logger.info("推送到 Telegram")
        
        try:
            cmd = [
                'openclaw', 'message', 'send',
                '--channel', 'telegram',
                '--target', self.target,
                '--message', message
            ]
            
            logger.debug(f"执行命令: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info("Telegram 推送成功")
                return True
            else:
                logger.error(f"Telegram 推送失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Telegram 推送异常: {e}", exc_info=True)
            return False
    
    def _push_to_wechat(self, message: str) -> bool:
        """
        推送到微信（个人微信）
        
        使用 OpenClaw 的 imessage 或其他微信渠道
        
        Args:
            message: 消息内容
            
        Returns:
            是否推送成功
        """
        logger.info("推送到微信")
        
        try:
            # 如果配置了微信 bot/webhook
            # 可以通过 OpenClaw 的 message tool 推送
            cmd = [
                'openclaw', 'message', 'send',
                '--channel', 'wechat',  # 需要配置微信渠道
                '--target', self.target,
                '--message', message
            ]
            
            logger.debug(f"执行命令: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info("微信推送成功")
                return True
            else:
                logger.error(f"微信推送失败: {result.stderr}")
                logger.warning("微信推送需要先配置微信渠道，详见文档")
                return False
                
        except Exception as e:
            logger.error(f"微信推送异常: {e}", exc_info=True)
            return False
    
    def _push_to_feishu(self, message: str) -> bool:
        """
        推送到飞书
        
        Args:
            message: 消息内容
            
        Returns:
            是否推送成功
        """
        logger.info("推送到飞书")
        
        try:
            # 使用 OpenClaw message send 推送到飞书
            cmd = [
                'openclaw', 'message', 'send',
                '--channel', 'feishu',  # 需要配置飞书渠道
                '--target', self.target,
                '--message', message
            ]
            
            logger.debug(f"执行命令: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info("飞书推送成功")
                return True
            else:
                logger.error(f"飞书推送失败: {result.stderr}")
                logger.warning("飞书推送需要先配置飞书渠道，详见文档")
                return False
                
        except Exception as e:
            logger.error(f"飞书推送异常: {e}", exc_info=True)
            return False
    
    def test_connection(self) -> bool:
        """
        测试推送连接
        
        Returns:
            连接是否正常
        """
        logger.info("测试推送连接")
        
        test_message = "🔔 TrendRadar 推送测试\n\n这是一条测试消息，如果收到说明配置正确。"
        
        return self.push(test_message)
