"""
test_multi_model_switching - 索克生活项目模块
"""

    import openai
    import time
import asyncio
import os
import sys

#!/usr/bin/env python3
"""
多模型切换演示脚本
展示如何轻松在不同大模型之间切换
"""


# 添加项目路径
sys.path.append('.')

async def demo_model_switching():
    """演示模型切换功能"""
    print("🚀 多模型切换演示\n")

    # 测试问题
    test_question = "请简单介绍一下中医的基本理论。"

    model_configs = [
        {
            "name": "DeepSeek",
            "api_key": "sk-26ac526b8c3b41c2a39bd80a156aaa68",
            "api_base": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
            "description": "专业的中文大模型,擅长中医知识"
        },
        {
            "name": "OpenAI GPT-4o-mini",
            "api_key": os.environ.get('OPENAI_API_KEY', ''),
            "api_base": "https://api.openai.com/v1",
            "model": "gpt-4o-mini",
            "description": "OpenAI的高效模型"
        },
        {
            "name": "智谱GLM-4",
            "api_key": os.environ.get('ZHIPU_API_KEY', ''),
            "api_base": "https://open.bigmodel.cn/api/paas/v4",
            "model": "glm-4",
            "description": "智谱AI的旗舰模型"
        }
    ]

    results = []

    for config in model_configs:
        print(f"📊 测试模型: {config['name']}")
        print(f"   描述: {config['description']}")

        if not config['api_key']:
            print("   ⚠️  跳过 - 未配置API KEY")
            continue

        try:
            response = await call_model_api(config, test_question)

            results.append({
                "model": config['name'],
                "response": response[:200] + "..." if len(response) > 200 else response,
                "length": len(response),
                "success": True
            })

            print("   ✅ 调用成功")
            print(f"   📝 响应长度: {len(response)}字符")
            print(f"   💬 响应预览: {response[:100]}...")

        except Exception as e:
            print(f"   ❌ 调用失败: {e}")
            results.append({
                "model": config['name'],
                "error": str(e),
                "success": False
            })

        print()

    # 输出对比结果
    print("="*60)
    print("📋 多模型响应对比:")
    print("="*60)

    for result in results:
        if result['success']:
            print(f"🤖 {result['model']}:")
            print(f"   长度: {result['length']}字符")
            print(f"   内容: {result['response']}")
        else:
            print(f"❌ {result['model']}: {result['error']}")
        print()

async def call_model_api(_config, question):
    """调用模型API"""


    client = openai.OpenAI(
        api_key=config['api_key'],
        base_url=config['api_base']
    )

    start_time = time.time()

    response = await asyncio.to_thread(
        client.chat.completions.create,
        model=config['model'],
        messages=[
            {"role": "system", "content": "你是一个专业的中医健康助手。"},
            {"role": "user", "content": question}
        ],
        max_tokens=500,
        temperature=0.7
    )

    processing_time = time.time() - start_time
    content = response.choices[0].message.content

    print(f"   ⏱️  耗时: {processing_time:.2f}秒")

    return content

async def demo_intelligent_model_selection():
    """演示智能模型选择"""
    print("\n🧠 智能模型选择演示")
    print("="*40)

    # 不同类型的任务
    tasks = [
        {
            "type": "中医咨询",
            "question": "我经常失眠,从中医角度应该如何调理?",
            "preferred_model": "deepseek-chat",
            "reason": "DeepSeek在中文和中医知识方面表现优秀"
        },
        {
            "type": "代码生成",
            "question": "请用Python写一个计算斐波那契数列的函数",
            "preferred_model": "deepseek-coder",
            "reason": "DeepSeek Coder专门针对代码生成优化"
        },
        {
            "type": "创意写作",
            "question": "写一首关于春天的诗",
            "preferred_model": "gpt-4",
            "reason": "GPT-4在创意写作方面表现出色"
        },
        {
            "type": "数据分析",
            "question": "分析一下电商行业的发展趋势",
            "preferred_model": "glm-4",
            "reason": "GLM-4在分析任务上表现良好"
        }
    ]

    for task in tasks:
        print(f"📋 任务类型: {task['type']}")
        print(f"❓ 问题: {task['question']}")
        print(f"🎯 推荐模型: {task['preferred_model']}")
        print(f"💡 选择理由: {task['reason']}")
        print()

async def demo_environment_based_switching():
    """演示基于环境的模型切换"""
    print("\n🔄 环境自适应模型切换演示")
    print("="*40)

    environments = [
        {
            "name": "开发环境",
            "config": "mock_services: true",
            "model": "模拟模型",
            "advantage": "快速响应,无API成本"
        },
        {
            "name": "测试环境",
            "config": "primary_model: deepseek-chat",
            "model": "DeepSeek",
            "advantage": "真实API测试,成本较低"
        },
        {
            "name": "生产环境",
            "config": "primary_model: gpt-4, fallback_model: deepseek-chat",
            "model": "GPT-4 + DeepSeek备用",
            "advantage": "最高质量,自动故障转移"
        }
    ]

    for env in environments:
        print(f"🌍 {env['name']}:")
        print(f"   配置: {env['config']}")
        print(f"   模型: {env['model']}")
        print(f"   优势: {env['advantage']}")
        print()

async def demo_simple_api_key_setup():
    """演示简单的API KEY设置"""
    print("\n🔑 简单API KEY设置演示")
    print("="*40)

    setup_examples = [
        {
            "provider": "DeepSeek",
            "method": "环境变量",
            "command": "export DEEPSEEK_API_KEY='your-api-key'",
            "config": "api_key: ${DEEPSEEK_API_KEY}"
        },
        {
            "provider": "OpenAI",
            "method": "直接配置",
            "command": "直接在配置文件中填入",
            "config": "api_key: 'sk-your-openai-key'"
        },
        {
            "provider": "智谱AI",
            "method": "环境变量",
            "command": "export ZHIPU_API_KEY='your-zhipu-key'",
            "config": "api_key: ${ZHIPU_API_KEY}"
        }
    ]

    for example in setup_examples:
        print(f"🔌 {example['provider']}:")
        print(f"   方法: {example['method']}")
        print(f"   命令: {example['command']}")
        print(f"   配置: {example['config']}")
        print()

    print("💡 提示: 只需要在配置文件中添加API KEY,系统会自动检测并使用相应的模型!")

async def main():
    """主演示函数"""
    print("🎯 多模型接入与切换演示")
    print("="*60)

    # 1. 演示多模型切换
    await demo_model_switching()

    # 2. 演示智能模型选择
    await demo_intelligent_model_selection()

    # 3. 演示环境自适应切换
    await demo_environment_based_switching()

    await demo_simple_api_key_setup()

    print("\n" + "="*60)
    print("✨ 总结:")
    print("="*60)
    print("✅ 只需要API KEY即可接入任何大模型")
    print("✅ 支持多模型并存和智能切换")
    print("✅ 自动故障转移和负载均衡")
    print("✅ 环境自适应配置")
    print("✅ 零代码配置,只需修改YAML文件")

    print("\n🚀 使用方法:")
    print("1. 在配置文件中添加API KEY")
    print("2. 设置primary_model指定主要模型")
    print("3. 系统自动处理模型调用和切换")
    print("4. 支持实时切换,无需重启服务")

if __name__ == "__main__":
    asyncio.run(main())
