OpenAI.md

OpenAI开源了！深夜发Agent四大利器，预告创意写作模型
编译 | 云鹏
编辑 | 心缘
智东西3月12日消息，刚刚，OpenAI放出打造AI智能体的新大招——推出一套专为简化AI agent应用开发的全新工具包，包括新Responses API、其首个开源Agents SDK、多款内置工具、可观察性工具。
简单来说，这个API集成度更高、更简洁、更好用，它融合了Chat Completions API的简洁性和Assistants API的工具使用能力。
OpenAI CEO萨姆·阿尔特曼（Sam Altman）亲自发文称，这是“有史以来设计最完善、最实用的API之一。”
值得一提的是，阿尔特曼今天还发文预告了OpenAI即将发布的新创意写作模型，他提到这是他第一次被AI所写的内容打动。
这些新工具有什么用？它们可以简化核心agent的逻辑、编排及交互流程，降低开发者构建agent的入门门槛。
今天OpenAI发布的是这套新工具的首套构建模块，后续他们还会发布更多新工具。
首批公布的新的API包括4个主要升级：
1、全新的Responses API⁠，融合了Chat Completions API的简洁性和Assistants API的工具使用能力，专为构建agent而设计。
2、内置工具包括网络搜索⁠、文件搜索⁠和计算机使用（compute use）。
3、全新Agents SDK⁠，用于编排单agent及多agent工作流程。
4、集成的可观测性工具⁠（observability tools），用于追踪和检查agent工作流执行情况。
一、一次调用就能解决复杂AI任务，API不会单独收费
在OpenAI看来，随着模型能力的持续进化，Responses API会为开发者构建agent应用提供更灵活的基础。通过一次Responses API调用，开发者就可以借助多种工具和模型轮转，解决日益复杂的任务。
首先，Responses API支持新的内置工具，比如网络搜索、文件搜索和计算机使用。这些工具可以协同工作，将模型与现实世界连接起来，使其在完成任务时更加实用。
1、网络搜索
开发者现在能够通过网页搜索工具获取快速、最新的答案，并附有清晰且相关的引用。在Responses API中，当开发者使用gpt-4o和gpt-4o-mini时，网页搜索会作为一项工具可供使用，并可与其他工具或函数调用相结合。
开发者可以利用网络搜索构建多种应用场景，比如购物agent、研究agent和旅行预订agent。
API中的网络搜索功能采用了与ChatGPT搜索相同的模型。在SimpleQA这一评估大型语言模型回答简短事实性问题准确性的基准测试中，GPT-4o搜索预览版和GPT-4o mini搜索预览版分别取得了90%和88%的得分。
网络搜索工具向所有开发者开放预览，集成于Responses API中。
此外，OpenAI通过Chat Completions API为开发者提供了直接访问精调搜索模型的机会，包括gpt-4o-search-preview和gpt-4o-mini-search-preview，以下是产品定价：
网络搜索文档链接：
https://platform.openai.com/docs/guides/tools-web-search
2、文件搜索
文件搜索工具可以从大量文档中检索相关信息。该工具支持多种文件类型，具备查询优化、元数据过滤及自定义重排序功能，能够提供快速而准确的搜索结果。借助Responses API，该工具仅需几行代码即可实现集成。
文件搜索工具可应用于多种现实场景，比如帮助客服人员便捷获取常见问题解答，协助法律助理快速查阅过往案例以供专业参考，以及支持编程人员查询技术文档。
该工具已面向所有开发者开放于Responses API中，使用费用按每千次查询 2.50美元及文件存储每日每GB 0.10美元计费，首GB免费：
文件搜索文档链接：
https://platform.openai.com/docs/guides/tools-file-search
3、计算机使用
开发者现在可以使用Responses API中的计算机使用工具来构建能够在计算机上高效完成任务的智能体。
计算机使用工具使用了跟Operator相同的Computer Use Agent（CUA）模型。该模型此前在多个测试中都创下了新的记录。
计算机使用工具能捕捉模型生成的鼠标和键盘操作，让开发者能够通过将这些动作直接翻译为环境中的可执行命令，实现计算机使用任务的自动化。
为了应对通过API中的CUA扩展Operator能力至本地操作系统所带来的风险，OpenAI进行了额外的安全评估和红队测试。测试结果表明该模型在自动化操作系统任务方面尚未高度可靠。
价格方面，计算机使用工具已向使用层级3至5的选定开发者开放于Responses API中。
▲OpenAI开发者选定层级一览
该工具使用费用定为100万输入token/3美元、100万输出token/12美元。
计算机使用工具文档链接：
https://platform.openai.com/docs/guides/tools-computer-use
此外，Responses API还进行了多项可用性改进，包括统一的项目化设计、更简洁的多态性、直观的流式事件，以及SDK辅助功能。
OpenAI提到，Responses API可以简化将OpenAI模型及内置工具集成至应用程序的过程，开发者不需要整合多个API或外部供应商。该API还便于在OpenAI上存储数据，让开发者能够利用追踪和评估等功能来评估agent性能。
OpenAI特别提到，默认情况下，他们不会利用存储在OpenAI上的业务数据来训练模型。
Responses API今天起向所有开发者开放，不单独收费——tokens和工具的使用将按照定价页面上的标准费率计费。
值得一提的是，OpenAI计划在2026年年中正式终止Assistants API的使用，Assistants API的能力直接迁移到Responses API中，OpenAI认为Responses API代表了他们构建AI agents的未来方向。
二、开源Agents SDK，改进多智能体协调
除了发布让开发者能更高效构建智能体的一系列新API、新工具，OpenAI在协调多智能体方面发布了新的开源Agents SDK。
Agents SDK适用于多种现实世界应用场景，包括客户支持自动化、多步骤研究、内容生成、代码审查以及销售线索挖掘。
其核心改进主要在以下4个方面：
1、智能体（Agents）：易于配置的大语言模型，配备明确指令与内置工具。
2、交接控制（Handoffs）：智能地在agent之间转移控制权。
3、护栏（Guardrails）：可配置的安全检查，用于输入和输出的验证。
4、追踪与可观测性（Tracing & Observability）：可视化agent执行轨迹，以调试并优化性能。
智能体、交接控制、护栏、追踪与可观测性SDK具体介绍文档：https://platform.openai.com/docs/guides/agents-sdk
Agents SDK开源项目链接：
https://github.com/openai/openai-agents-python?tab=readme-ov-file
结语：AI智能体大战愈发焦灼
OpenAI此前发布了旗下首个“AI智能体”Operater，此次新API和工具的升级进一步降低了开发者开发智能体、将AI智能体集成在应用中的难度。
当下AI智能体成为AI赛道的热门概念和技术焦点，近期Manus的火爆也让更多人开始关注AI智能体。
今天微软也同期发布了AI智能体构建方面的相关新API和工具，正如OpenAI所说，AI智能体很快会融入各行各业提升生产效率，如何高效构建可以实际落地的AI智能体成为各家努力的重点方向。
来源：OpenAI官网