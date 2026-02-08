#!/bin/bash
#
# TrendRadar + OpenClaw 集成快速部署脚本
# 

set -e

WORKSPACE="/root/.openclaw/workspace/trendradar-integration"
TRENDRADAR_DIR="$WORKSPACE/TrendRadar"

echo "========================================"
echo "TrendRadar + OpenClaw 快速部署"
echo "========================================"
echo ""

# 1. 检查目录
echo "步骤 1/7: 检查工作目录..."
if [ ! -d "$WORKSPACE" ]; then
    echo "❌ 工作目录不存在: $WORKSPACE"
    exit 1
fi
cd "$WORKSPACE"
echo "✅ 工作目录: $WORKSPACE"
echo ""

# 2. 检查 TrendRadar
echo "步骤 2/7: 检查 TrendRadar..."
if [ ! -d "$TRENDRADAR_DIR" ]; then
    echo "❌ TrendRadar 目录不存在"
    exit 1
fi
echo "✅ TrendRadar 已就绪"
echo ""

# 3. 运行基础测试
echo "步骤 3/7: 运行基础测试..."
python3 test_integration.py
if [ $? -ne 0 ]; then
    echo "❌ 基础测试失败"
    exit 1
fi
echo ""

# 4. 检查配置
echo "步骤 4/7: 检查配置..."
if ! grep -q "your-group-name-or-id" config.yaml; then
    echo "✅ 推送目标已配置"
else
    echo "⚠️  警告: 推送目标尚未配置"
    echo "   请编辑 config.yaml，修改 push.target"
    echo ""
    read -p "是否现在配置？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "请输入企业微信群名称或 ID:"
        read GROUP_TARGET
        sed -i "s/your-group-name-or-id/$GROUP_TARGET/g" config.yaml
        echo "✅ 已配置推送目标: $GROUP_TARGET"
    fi
fi
echo ""

# 5. 运行 TrendRadar 数据采集
echo "步骤 5/7: 采集 TrendRadar 数据..."
echo "这可能需要几分钟时间..."
cd "$TRENDRADAR_DIR"
python3 -m trendradar > /tmp/trendradar-run.log 2>&1 &
TRENDRADAR_PID=$!

# 等待最多 5 分钟
WAIT_TIME=0
MAX_WAIT=300
while [ $WAIT_TIME -lt $MAX_WAIT ]; do
    if ! ps -p $TRENDRADAR_PID > /dev/null; then
        break
    fi
    sleep 10
    WAIT_TIME=$((WAIT_TIME + 10))
    echo "  已等待 ${WAIT_TIME}s..."
done

if ps -p $TRENDRADAR_PID > /dev/null; then
    echo "⚠️  TrendRadar 仍在运行，继续下一步"
    kill $TRENDRADAR_PID 2>/dev/null || true
else
    echo "✅ TrendRadar 数据采集完成"
fi
cd "$WORKSPACE"
echo ""

# 6. 测试推送（dry-run）
echo "步骤 6/7: 测试消息格式（预览模式）..."
python3 src/main.py --mode news --dry-run
echo ""

# 7. 提示下一步
echo "========================================"
echo "✅ 部署完成！"
echo "========================================"
echo ""
echo "📋 下一步操作:"
echo ""
echo "1. 测试实际推送:"
echo "   python3 src/main.py --test"
echo ""
echo "2. 手动推送新闻:"
echo "   python3 src/main.py --mode news"
echo ""
echo "3. 配置定时任务:"
echo "   openclaw cron add \"trendradar-news\" \\"
echo "     --schedule \"0 9,12,18 * * *\" \\"
echo "     --command \"cd $WORKSPACE && python3 src/main.py --mode news\" \\"
echo "     --timezone \"Asia/Shanghai\""
echo ""
echo "4. 查看日志:"
echo "   tail -f trendradar.log"
echo ""
echo "📚 完整文档请参考: README.md"
echo ""
