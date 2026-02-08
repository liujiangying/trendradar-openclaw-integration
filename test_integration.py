#!/usr/bin/env python3
"""
简单测试脚本 - 验证 TrendRadar 集成功能
"""

import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """测试模块导入"""
    print("=" * 60)
    print("测试 1: 模块导入")
    print("=" * 60)
    
    try:
        from mcp_client import SyncMCPClient
        print("✅ mcp_client 导入成功")
    except Exception as e:
        print(f"❌ mcp_client 导入失败: {e}")
        return False
    
    try:
        from data_processor import DataProcessor
        print("✅ data_processor 导入成功")
    except Exception as e:
        print(f"❌ data_processor 导入失败: {e}")
        return False
    
    try:
        from formatter import MessageFormatter
        print("✅ formatter 导入成功")
    except Exception as e:
        print(f"❌ formatter 导入失败: {e}")
        return False
    
    try:
        from pusher import Pusher
        print("✅ pusher 导入成功")
    except Exception as e:
        print(f"❌ pusher 导入失败: {e}")
        return False
    
    print("\n所有模块导入成功！\n")
    return True


def test_config():
    """测试配置加载"""
    print("=" * 60)
    print("测试 2: 配置文件加载")
    print("=" * 60)
    
    try:
        import yaml
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print("✅ 配置文件加载成功")
        print(f"   - TrendRadar 路径: {config['trendradar']['root_path']}")
        print(f"   - 推送渠道: {config['push']['channel']}")
        print(f"   - 推送目标: {config['push']['target']}")
        print(f"   - 关键词组数: {len(config['keywords']['groups'])}")
        
        return True, config
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        return False, None


def test_trendradar_path(config):
    """测试 TrendRadar 路径"""
    print("=" * 60)
    print("测试 3: TrendRadar 路径检查")
    print("=" * 60)
    
    trendradar_root = config['trendradar']['root_path']
    
    if not os.path.exists(trendradar_root):
        print(f"❌ TrendRadar 路径不存在: {trendradar_root}")
        return False
    
    print(f"✅ TrendRadar 路径存在: {trendradar_root}")
    
    # 检查关键文件
    key_paths = [
        'mcp_server/server.py',
        'config/config.yaml',
        'output'
    ]
    
    for path in key_paths:
        full_path = os.path.join(trendradar_root, path)
        if os.path.exists(full_path):
            print(f"✅ {path} 存在")
        else:
            print(f"⚠️  {path} 不存在")
    
    return True


def test_data_processor(config):
    """测试数据处理器"""
    print("=" * 60)
    print("测试 4: 数据处理器")
    print("=" * 60)
    
    try:
        from data_processor import DataProcessor
        
        processor = DataProcessor(config)
        print("✅ 数据处理器初始化成功")
        
        # 测试数据
        test_news = [
            {
                'title': 'ChatGPT 推出新功能',
                'rank': 1,
                'source': 'zhihu',
                'hot': '100000'
            },
            {
                'title': '数据质量管理新方法',
                'rank': 2,
                'source': 'toutiao',
                'hot': '50000'
            },
            {
                'title': '广告：不看后悔',
                'rank': 3,
                'source': 'weibo',
                'hot': '30000'
            }
        ]
        
        # 测试过滤
        filtered = processor.filter_by_exclude_keywords(test_news)
        print(f"✅ 排除关键词过滤: {len(test_news)} -> {len(filtered)}")
        
        # 测试关键词分组
        grouped = processor.filter_by_keywords(filtered)
        print(f"✅ 关键词分组: {len(grouped)} 组")
        for keyword, news_list in grouped.items():
            print(f"   - {keyword}: {len(news_list)} 条")
        
        return True
    except Exception as e:
        print(f"❌ 数据处理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_formatter(config):
    """测试消息格式化"""
    print("=" * 60)
    print("测试 5: 消息格式化器")
    print("=" * 60)
    
    try:
        from formatter import MessageFormatter
        
        formatter = MessageFormatter(config)
        print("✅ 消息格式化器初始化成功")
        
        # 测试数据
        grouped_news = {
            'AI': [
                {
                    'title': 'ChatGPT 推出新功能',
                    'rank': 1,
                    'source': 'zhihu',
                    'url': 'https://example.com/1'
                }
            ],
            '数据质量': [
                {
                    'title': '数据质量管理新方法',
                    'rank': 2,
                    'source': 'toutiao',
                    'url': 'https://example.com/2'
                }
            ]
        }
        
        # 格式化消息
        message = formatter.format_news_push(grouped_news)
        print("✅ 消息格式化成功")
        print(f"   消息长度: {len(message)} 字符")
        
        print("\n--- 消息预览 ---")
        print(message[:500])
        print("...\n")
        
        return True
    except Exception as e:
        print(f"❌ 消息格式化测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("TrendRadar + OpenClaw 集成测试")
    print("=" * 60 + "\n")
    
    # 测试 1: 导入
    if not test_imports():
        print("\n测试失败：模块导入出错")
        return False
    
    # 测试 2: 配置
    success, config = test_config()
    if not success:
        print("\n测试失败：配置文件加载出错")
        return False
    
    # 测试 3: TrendRadar 路径
    if not test_trendradar_path(config):
        print("\n测试失败：TrendRadar 路径有问题")
        return False
    
    # 测试 4: 数据处理
    if not test_data_processor(config):
        print("\n测试失败：数据处理器有问题")
        return False
    
    # 测试 5: 消息格式化
    if not test_formatter(config):
        print("\n测试失败：消息格式化器有问题")
        return False
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)
    print("\n下一步:")
    print("1. 配置 config.yaml 中的 push.target（企业微信群名称）")
    print("2. 运行 TrendRadar 获取数据:")
    print("   cd TrendRadar && python3 -m trendradar")
    print("3. 测试推送（dry-run）:")
    print("   python3 src/main.py --mode news --dry-run")
    print("4. 实际推送测试:")
    print("   python3 src/main.py --test")
    print("\n")
    
    return True


if __name__ == '__main__':
    os.chdir('/root/.openclaw/workspace/trendradar-integration')
    success = main()
    sys.exit(0 if success else 1)
