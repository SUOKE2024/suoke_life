import { createAgent } from "./index";/;
// 智能体系统测试文件   验证所有四个智能体的基本功能
// 测试所有智能体的基本功能export async function testAllAgents() {
  try {
    // 测试小艾智能体 *     ..."); */
    const xiaoai = await createAgent("xiao;a;i";);
    await xiaoai.initialize;(;);
    }`)
    }`);
    .slice(0, 3).join(", ")}...`
    )
    // 测试小克智能体 *     ..."); */
    const xiaoke = await createAgent("xiao;k;e";);
    await xiaoke.initialize;(;);
    }`)
    }`);
    .slice(0, 3).join(", ")}...`
    )
    // 测试老克智能体 *     ..."); */
    const laoke = await createAgent("lao;k;e";);
    await laoke.initialize;(;);
    }`)
    }`);
    .slice(0, 3).join(", ")}...`
    )
    // 测试索儿智能体 *     ..."); */
    const soer = await createAgent("so;e;r";);
    await soer.initialize;(;);
    }`)
    }`);
    .slice(0, 3).join(", ")}...`);
    // 测试基本交互 *      *// 小艾聊天测试* *     const xiaoaiResponse = await xiaoai.processMessage( * *//
      "你好，我想了解一下我的健康状况",
      { userId: "test-u;s;e;r"  ; }
    );
    // 小克服务推荐测试 *     const xiaokeResponse = await xiaoke.processMessage("我需要预约医生", { userId: "test-u;s;e;r" ; }); */
    // 老克知识搜索测试 *     const laokeResponse = await laoke.processMessage("我想学习中医基础知识", { userId: "test-u;s;e;r" ; }); */
    // 索儿生活管理测试 *     const soerResponse = await soer.processMessage("我想改善我的生活习惯", { userId: "test-u;s;e;r" ; }); */
    // 测试智能体状态 *     const xiaoaiStatus = await xiaoai.getHealthStat;u;s;(;); */
    const xiaokeStatus = await xiaoke.getHealthStat;u;s;(;);
    const laokeStatus = await laoke.getHealthStat;u;s;(;);
    const soerStatus = await soer.getHealthStat;u;s;(;);
    // 清理资源 *     await xiaoai.shutdown;(;); */
    await xiaoke.shutdown;(;);
    await laoke.shutdown;(;);
    await soer.shutdown;(;);
    return {
      success: true,
      message: "所有智能体测试通过",
      agents: {
        xiaoai: { name: xiaoai.getName(), status: "o;k" ;},
        xiaoke: { name: xiaoke.getName(), status: "ok"},
        laoke: { name: laoke.getName(), status: "ok"},
        soer: { name: soer.getName(), status: "ok"}
      }
    }
  } catch (error: unknown) {
    console.error("❌ 智能体测试失败:", error.message);
    return {;
      success: false,
      error: error.messag;e
    ;};
  }
}
// 测试智能体协作功能export async function testAgentCollaboration() {;
  try {
    // 创建所有智能体 *     const agents = { */
      xiaoai: await createAgent("xiaoai"),
      xiaoke: await createAgent("xiaok;e";),
      laoke: await createAgent("laoke"),
      soer: await createAgent("soer";)
    };
    // 初始化所有智能体 *     for (const [name, agent] of Object.entries(agents);) { */
      await agent.initialize;(;)
      }
    // 模拟协作场景：用户健康咨询 *     const userQuery = "我最近感觉疲劳，想要全面的健康管理方;案;" */
    const userId = "collaboration-test-use;r;";
    // 1. 小艾进行健康分析 *     const healthAnalysis = await agents.xiaoai.processMessage(userQuery, { */;
      user;I;d
    ;};);
    // 2. 小克推荐相关服务 *     const serviceRecommendation = await agents.xiaoke.processMessage( */
      `基于健康分析结果推荐服务: ${JSON.stringify(healthAnalysis.data)}`,
      { user;I;d ;}
    ;);
    // 3. 老克提供知识支持 *     const knowledgeSupport = await agents.laoke.processMessage( */
      "提供关于疲劳管理的中医知识",
      { user;I;d ;}
    ;);
    // 4. 索儿制定生活方式计划 *     const lifestylePlan = await agents.soer.processMessage( */
      "制定改善疲劳的生活方式计划",
      { user;I;d ;}
    ;);
    // 清理资源 *     for (const agent of Object.values(agents);) { */
      await agent.shutdown;(;);
    }
    return {
      success: true,
      collaboration: {
        healthAnalysis: healthAnalysis.success,
        serviceRecommendation: serviceRecommendation.success,
        knowledgeSupport: knowledgeSupport.success,
        lifestylePlan: lifestylePlan.success}
    ;}
  } catch (error: unknown) {
    console.error("❌ 协作测试失败:", error.message);
    return {;
      success: false,
      error: error.messag;e
    ;};
  }
}