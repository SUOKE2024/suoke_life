# 测试数据目录

本目录包含SuokeBench评测系统使用的示例测试数据，完整数据集需要单独下载。

## 目录结构

```
data/
├── tcm-4d/              # 中医四诊数据集
│   ├── tongue/          # 舌象图像
│   ├── face/            # 面色视频
│   ├── pulse/           # 脉搏波形
│   └── voice/           # 语音问诊
├── health-plan/         # 健康管理数据集
├── agent-dialogue/      # 智能体对话数据集
└── privacy-zkp/         # 隐私与安全测试数据
```

## 数据集获取

完整数据集可以通过以下命令下载：

```bash
# 安装评测环境并下载示例数据集
make bench.setup
```

或者手动下载并放置到对应目录：

```bash
# 手动下载示例数据
python -m internal.suokebench.setup --download-only
```

## 数据格式说明

详细的数据格式说明请参考每个子目录中的`format.md`文件。 