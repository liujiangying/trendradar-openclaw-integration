# TrendRadar + OpenClaw 集成部署文档

## 📋 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [系统架构](#系统架构)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [使用指南](#使用指南)
- [定时任务](#定时任务)
- [故障排查](#故障排查)
- [常见问题](#常见问题)

## 项目简介

TrendRadar + OpenClaw 集成方案，通过 OpenClaw 平台定时调用 TrendRadar 的 MCP 服务，获取热点新闻并推送到企业微信群。

### 技术栈

- **TrendRadar**: 热点新闻聚合器，支持多平台数据源和 MCP 协议
- **OpenClaw**: AI 助手平台，提供定时任务和消息推送能力
- **Python**: 集成代码语言
- **企业微信**: 推送渠道

### 项目结构

```
/root/.openclaw/workspace/trendradar-integration/
├── TrendRadar/              # TrendRadar 仓库（git clone）
│   ├── config/              # TrendRadar 配置
│   ├── mcp_server/          # MCP Server 代码
│   ├── trendradar/          # 核心代码
│   └── output/              # 数据存储目录
├── src/                     # 集成代码
│   ├── __init__.py
│   ├── mcp_client.py       # MCP 客户端封装
│   ├── data_processor.py   # 数据处理
│   ├── formatter.py        # 消息格式化
│   ├── pusher.py           # 推送逻辑
│   └── main.py             # 主入口
├── config.yaml             # 集成配置文件
├── requirements.txt        # Python 依赖
├── README.md              # 本文档
├── ARCHITECTURE.md        # 架构设计文档
├── progress.md            # 开发进度
└── trendradar.log         # 运行日志
```

## 功能特性

### ✅ 已实现功能

- [x] **MCP 客户端封装**: 与 TrendRadar MCP Server 通信
- [x] **数据处理**: 关键词过滤、排名筛选、去重排序
- [x] **消息格式化**: Markdown 格式，支持 Emoji 和平台标识
- [x] **企业微信推送**: 通过 OpenClaw 推送到企业微信群
- [x] **定时任务支持**: 基于 OpenClaw cron
- [x] **多种推送模式**: 新闻推送、热门话题、RSS 订阅
- [x] **灵活配置**: YAML 配置文件，易于调整
- [x] **错误处理**: 异常捕获和错误通知
- [x] **测试模式**: 支持 dry-run 预览消息

### 🔮 未来扩展

- [ ] 支持更多推送渠道（钉钉、飞书、Telegram）
- [ ] AI 分析功能（情感分析、趋势预测）
- [ ] Web 控制台
- [ ] 推送成功率监控
- [ ] 本地缓存机制

## 系统架构

详见 [ARCHITECTURE.md](ARCHITECTURE.md)

简要流程：

```
OpenClaw Cron 定时触发
    ↓
启动 TrendRadar MCP Server (stdio)
    ↓
调用 MCP 工具获取数据
    ↓
数据处理与格式化
    ↓
推送到企业微信群
```

## 快速开始

### 前置要求

- ✅ OpenClaw 已安装并配置
- ✅ Python 3.8+
- ✅ 企业微信机器人已配置（openclaw-wecom-bot）
- ✅ TrendRadar 已部署并运行（至少有一次数据）

### 1. 安装依赖

```bash
cd /root/.openclaw/workspace/trendradar-integration

# 安装 Python 依赖
pip install -r requirements.txt
```

### 2. 配置 TrendRadar

编辑 `TrendRadar/config/config.yaml`：

```bash
cd TrendRadar
vim config/config.yaml
```

确保以下配置正确：

- `app.timezone`: 时区设置
- `platforms.sources`: 启用的平台
- `rss.feeds`: RSS 订阅源

配置关键词（可选）：

```bash
vim config/frequency_words.txt
```

### 3. 手动运行一次 TrendRadar

确保 TrendRadar 有数据：

```bash
cd TrendRadar
python -m trendradar
```

等待抓取完成，检查 `output/` 目录是否有数据。

### 4. 配置集成参数

编辑 `config.yaml`：

```bash
cd /root/.openclaw/workspace/trendradar-integration
vim config.yaml
```

**重要配置项**：

```yaml
# 推送目标（必填）
push:
  target: "your-group-name-or-id"  # 修改为你的企业微信群名称或 ID

# 关键词（根据你的兴趣修改）
keywords:
  groups:
    - name: "技术与 AI"
      words: ["AI", "人工智能", "ChatGPT"]
```

### 5. 测试运行

#### 测试 1: 连接测试

```bash
cd /root/.openclaw/workspace/trendradar-integration
python src/main.py --test
```

应该看到：
- ✅ MCP 连接正常
- ✅ 推送连接正常

#### 测试 2: 预览消息（不实际推送）

```bash
python src/main.py --mode news --dry-run
```

会在控制台打印格式化后的消息，检查内容是否符合预期。

#### 测试 3: 实际推送

```bash
python src/main.py --mode news
```

检查企业微信群是否收到消息。

### 6. 配置定时任务

使用 OpenClaw cron 配置定时推送：

```bash
# 每天 9:00, 12:00, 18:00 推送新闻
openclaw cron add "trendradar-news" \
  --schedule "0 9,12,18 * * *" \
  --command "cd /root/.openclaw/workspace/trendradar-integration && python src/main.py --mode news" \
  --timezone "Asia/Shanghai"

# 每天 8:00 推送热门话题
openclaw cron add "trendradar-topics" \
  --schedule "0 8 * * *" \
  --command "cd /root/.openclaw/workspace/trendradar-integration && python src/main.py --mode topics" \
  --timezone "Asia/Shanghai"
```

查看定时任务：

```bash
openclaw cron list
```

## 配置说明

### config.yaml 详解

#### trendradar 配置

```yaml
trendradar:
  root_path: "/root/.openclaw/workspace/trendradar-integration/TrendRadar"
  mcp_mode: "stdio"  # MCP 通信模式
```

#### sources 配置

```yaml
sources:
  platforms:  # 热榜平台列表
    - "zhihu"
    - "weibo"
    # ... 更多平台
  
  rss_feeds:  # RSS 订阅源
    - "hacker-news"
    # ... 更多源
```

留空表示使用 TrendRadar 配置的所有平台/源。

#### keywords 配置

```yaml
keywords:
  enabled: true  # 是否启用关键词过滤
  show_trending: true  # 是否显示热门话题
  
  groups:  # 关键词分组
    - name: "分组名称"
      words: ["关键词1", "关键词2"]
```

**关键词匹配规则**：
- 大小写不敏感
- 支持部分匹配（"AI" 可以匹配 "AI 大模型"）
- 一条新闻只归入一个关键词组（优先匹配第一个）

#### push 配置

```yaml
push:
  enabled: true
  channel: "wecom"  # wecom 或 telegram
  target: "group-name"  # 推送目标
  
  format:
    max_items_per_keyword: 5  # 每组最多显示 5 条
    show_ranking: true  # 显示排名
    show_platform: true  # 显示平台
    show_url: false  # 不显示链接（减少消息长度）
```

**推送目标配置**：
- 企业微信: 群聊名称或群聊 ID
- Telegram: 频道 ID 或用户名（如 `@channelname`）

#### filters 配置

```yaml
filters:
  rank_threshold: 20  # 只推送排名前 20 的新闻
  min_hot_score: 0  # 热度阈值
  exclude_keywords:  # 排除关键词
    - "广告"
    - "营销"
```

## 使用指南

### 命令行参数

```bash
python src/main.py [OPTIONS]
```

**选项**：

- `--config PATH`: 配置文件路径（默认: `config.yaml`）
- `--mode MODE`: 运行模式
  - `news`: 新闻推送（默认）
  - `topics`: 热门话题推送
  - `rss`: RSS 订阅推送
  - `all`: 全部推送（新闻 + RSS）
- `--dry-run`: 测试模式，不实际推送，只预览消息
- `--test`: 运行连接测试

### 运行模式

#### 1. 新闻推送 (news)

基于关键词过滤的热点新闻推送。

```bash
python src/main.py --mode news
```

**消息示例**：

```
📰 热点新闻推送 (2026-02-08 18:00)

🔥 热门话题 TOP 5
━━━━━━━━━━━━━━━━━━
1. [ChatGPT] (热度: 152)
   📚 知乎 #1 | 🔍 微博 #3

━━━━━━━━━━━━━━━━━━
🎯 关键词匹配: AI, 数据质量
📊 共 15 条新闻
━━━━━━━━━━━━━━━━━━

📌 AI 相关 (8条)
• ChatGPT 推出新功能
  #1 | 📚 知乎
• AI 大模型最新进展
  #3 | 🔍 微博

📌 数据质量 相关 (7条)
• 数据质量管理新方法
  #2 | 📰 今日头条

━━━━━━━━━━━━━━━━━━
✨ Powered by TrendRadar + OpenClaw
```

#### 2. 热门话题推送 (topics)

不做关键词过滤，推送当前最热门的话题。

```bash
python src/main.py --mode topics
```

#### 3. RSS 订阅推送 (rss)

推送 RSS 订阅的最新文章。

```bash
python src/main.py --mode rss
```

#### 4. 全部推送 (all)

依次执行新闻推送和 RSS 推送。

```bash
python src/main.py --mode all
```

### 测试模式

使用 `--dry-run` 预览消息而不实际推送：

```bash
python src/main.py --mode news --dry-run
```

消息会打印到控制台，方便调试格式。

### 连接测试

测试 MCP 和推送连接：

```bash
python src/main.py --test
```

## 定时任务

### OpenClaw Cron 语法

```bash
openclaw cron add <task-name> \
  --schedule "<cron-expression>" \
  --command "<command>" \
  --timezone "<timezone>"
```

**Cron 表达式格式**：`分 时 日 月 周`

示例：
- `0 9 * * *`: 每天 9:00
- `0 9,12,18 * * *`: 每天 9:00, 12:00, 18:00
- `*/30 * * * *`: 每 30 分钟
- `0 9 * * 1`: 每周一 9:00

### 推荐定时任务配置

#### 方案 1: 工作日推送

```bash
# 工作日早上 9:00 推送新闻
openclaw cron add "trendradar-morning" \
  --schedule "0 9 * * 1-5" \
  --command "cd /root/.openclaw/workspace/trendradar-integration && python src/main.py --mode news" \
  --timezone "Asia/Shanghai"

# 工作日中午 12:00 推送新闻
openclaw cron add "trendradar-noon" \
  --schedule "0 12 * * 1-5" \
  --command "cd /root/.openclaw/workspace/trendradar-integration && python src/main.py --mode news" \
  --timezone "Asia/Shanghai"

# 工作日晚上 18:00 推送新闻
openclaw cron add "trendradar-evening" \
  --schedule "0 18 * * 1-5" \
  --command "cd /root/.openclaw/workspace/trendradar-integration && python src/main.py --mode news" \
  --timezone "Asia/Shanghai"
```

#### 方案 2: 每天推送

```bash
# 每天 8:00 推送热门话题
openclaw cron add "trendradar-topics-daily" \
  --schedule "0 8 * * *" \
  --command "cd /root/.openclaw/workspace/trendradar-integration && python src/main.py --mode topics" \
  --timezone "Asia/Shanghai"

# 每天 9:00, 15:00, 21:00 推送新闻
openclaw cron add "trendradar-news-daily" \
  --schedule "0 9,15,21 * * *" \
  --command "cd /root/.openclaw/workspace/trendradar-integration && python src/main.py --mode news" \
  --timezone "Asia/Shanghai"
```

#### 方案 3: 高频监控

```bash
# 每小时推送新闻（工作时间 9:00-18:00）
openclaw cron add "trendradar-hourly" \
  --schedule "0 9-18 * * *" \
  --command "cd /root/.openclaw/workspace/trendradar-integration && python src/main.py --mode news" \
  --timezone "Asia/Shanghai"
```

### 管理定时任务

```bash
# 列出所有任务
openclaw cron list

# 删除任务
openclaw cron remove "trendradar-news"

# 查看任务详情
openclaw cron describe "trendradar-news"

# 立即运行任务（测试用）
openclaw cron run "trendradar-news"
```

### TrendRadar 数据更新

TrendRadar 也需要定时抓取数据，建议在推送前 10-15 分钟运行：

```bash
# 每天 8:45, 14:45, 20:45 更新 TrendRadar 数据
openclaw cron add "trendradar-update" \
  --schedule "45 8,14,20 * * *" \
  --command "cd /root/.openclaw/workspace/trendradar-integration/TrendRadar && python -m trendradar" \
  --timezone "Asia/Shanghai"
```

## 故障排查

### 问题 1: MCP 连接失败

**错误信息**：
```
❌ MCP 连接失败: No module named 'mcp_server'
```

**解决方法**：
1. 检查 TrendRadar 路径是否正确
2. 确认 TrendRadar 已安装依赖：`cd TrendRadar && pip install -r requirements.txt`

### 问题 2: 推送失败

**错误信息**：
```
❌ 推送连接失败
```

**解决方法**：
1. 检查 `config.yaml` 中的 `push.target` 是否正确
2. 确认企业微信机器人已配置：`openclaw message list`
3. 测试推送连接：`python src/main.py --test`

### 问题 3: 无匹配新闻

**日志信息**：
```
无匹配关键词的新闻，跳过推送
```

**解决方法**：
1. 检查关键词配置是否合理（`config.yaml` 的 `keywords.groups`）
2. 降低排名阈值（`filters.rank_threshold`）
3. 查看 TrendRadar 原始数据：`ls -la TrendRadar/output/news/$(date +%Y-%m-%d)/`

### 问题 4: 消息过长被截断

**日志信息**：
```
消息过长 (5000 > 4000)，进行截断
```

**解决方法**：
1. 减少每组显示条数：`push.format.max_items_per_keyword: 3`
2. 提高排名阈值：`filters.rank_threshold: 10`
3. 精简关键词列表

### 问题 5: 定时任务未执行

**解决方法**：
1. 检查 cron 表达式是否正确：`openclaw cron describe "task-name"`
2. 查看 OpenClaw 日志：`openclaw logs`
3. 确认时区设置正确
4. 手动运行测试：`openclaw cron run "task-name"`

### 查看日志

集成服务日志：

```bash
tail -f /root/.openclaw/workspace/trendradar-integration/trendradar.log
```

TrendRadar 日志：

```bash
cd TrendRadar
# 查看最近运行记录
ls -lt output/news/
```

## 常见问题

### Q1: 如何调整推送频率？

修改 OpenClaw cron 任务的 schedule 表达式。

### Q2: 如何添加新的关键词？

编辑 `config.yaml`，在 `keywords.groups` 中添加新的关键词组或在现有组中添加词。

### Q3: 如何切换推送渠道？

修改 `config.yaml` 中的 `push.channel` 和 `push.target`。

### Q4: 如何只推送特定平台的新闻？

修改 `config.yaml` 中的 `sources.platforms`，只保留需要的平台 ID。

### Q5: 消息格式如何自定义？

修改 `src/formatter.py` 中的格式化函数，或调整 `config.yaml` 中的 `push.format` 配置。

### Q6: 如何备份配置和数据？

```bash
# 备份配置
cp config.yaml config.yaml.backup

# 备份 TrendRadar 数据
tar -czf trendradar-data-backup.tar.gz TrendRadar/output/
```

### Q7: 如何更新 TrendRadar？

```bash
cd TrendRadar
git pull
pip install -r requirements.txt --upgrade
```

### Q8: 如何禁用推送？

临时禁用：
```bash
openclaw cron pause "trendradar-news"
```

永久禁用：
```yaml
# config.yaml
push:
  enabled: false
```

### Q9: 如何查看推送历史？

查看日志文件：
```bash
grep "推送成功\|推送失败" trendradar.log
```

### Q10: 如何获取技术支持？

1. 查看本文档的故障排查章节
2. 查看日志文件定位问题
3. 查看 [TrendRadar 文档](https://github.com/sansan0/TrendRadar)
4. 联系 OpenClaw 支持团队

## 最佳实践

### 1. 关键词配置建议

- 使用分组管理关键词，便于维护
- 关键词不宜过多（建议每组 5-10 个）
- 使用具体的关键词（如 "ChatGPT" 而不是 "GPT"）
- 定期review和调整关键词

### 2. 推送频率建议

- 工作日: 早中晚各 1 次（9:00, 12:00, 18:00）
- 周末: 减少频率或仅重要话题
- 避免夜间推送打扰

### 3. 消息长度控制

- 每组显示 3-5 条新闻
- 排名阈值设置为 10-20
- 关闭 URL 显示（减少长度）
- 使用热门话题模式（更简洁）

### 4. 监控和维护

- 定期查看日志确认运行正常
- 每周review推送内容质量
- 根据反馈调整关键词和过滤规则
- 定期更新 TrendRadar 到最新版本

### 5. 安全建议

- 不要在配置文件中存储敏感信息
- 使用环境变量管理 API 密钥
- 定期备份配置和数据
- 限制日志文件大小

## 更新日志

### v1.0.0 (2026-02-08)

- ✅ 初始版本发布
- ✅ 实现 MCP 客户端
- ✅ 实现数据处理和消息格式化
- ✅ 实现企业微信推送
- ✅ 支持定时任务
- ✅ 编写完整文档

## 致谢

- **TrendRadar**: 感谢 [sansan0/TrendRadar](https://github.com/sansan0/TrendRadar) 提供优秀的热点聚合服务
- **OpenClaw**: 感谢 OpenClaw 平台提供的定时任务和消息推送能力
- **工蜂 AI x AnyDev**: 感谢提供的 AI 能力和容器基础设施

## 许可证

本项目遵循 GPL-3.0 许可证（与 TrendRadar 保持一致）。

---

**📧 联系方式**：cassieyliu (腾讯数据质量平台)

**🔗 相关链接**：
- [TrendRadar GitHub](https://github.com/sansan0/TrendRadar)
- [OpenClaw 文档](https://openclaw.woa.com/docs)

---

*最后更新: 2026-02-08*
