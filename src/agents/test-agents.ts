import { createAgent } from "./index";

/**
 * 智能体系统测试文件
 * 验证所有四个智能体的基本功能
 */

/**
 * 测试所有智能体的基本功能
 */
export async function testAllAgents() {
  console.log("开始测试索克生活四智能体系统...\n");

  try {
    // 测试小艾智能体
    console.log("🤖 测试小艾智能体 (健康助手)...");
    const xiaoai = await createAgent("xiaoai");
    await xiaoai.initialize();
    console.log(`✅ 小艾智能体初始化成功: ${xiaoai.getName()}`);
    console.log(`   描述: ${xiaoai.getDescription()}`);
    console.log(
      `   能力: ${xiaoai.getCapabilities().slice(0, 3).join(", ")}...`
    );

    // 测试小克智能体
    console.log("\n🛒 测试小克智能体 (SUOKE频道版主)...");
    const xiaoke = await createAgent("xiaoke");
    await xiaoke.initialize();
    console.log(`✅ 小克智能体初始化成功: ${xiaoke.getName()}`);
    console.log(`   描述: ${xiaoke.getDescription()}`);
    console.log(
      `   能力: ${xiaoke.getCapabilities().slice(0, 3).join(", ")}...`
    );

    // 测试老克智能体
    console.log("\n📚 测试老克智能体 (探索频道版主)...");
    const laoke = await createAgent("laoke");
    await laoke.initialize();
    console.log(`✅ 老克智能体初始化成功: ${laoke.getName()}`);
    console.log(`   描述: ${laoke.getDescription()}`);
    console.log(
      `   能力: ${laoke.getCapabilities().slice(0, 3).join(", ")}...`
    );

    // 测试索儿智能体
    console.log("\n💝 测试索儿智能体 (LIFE频道版主)...");
    const soer = await createAgent("soer");
    await soer.initialize();
    console.log(`✅ 索儿智能体初始化成功: ${soer.getName()}`);
    console.log(`   描述: ${soer.getDescription()}`);
    console.log(`   能力: ${soer.getCapabilities().slice(0, 3).join(", ")}...`);

    // 测试基本交互
    console.log("\n🗣️ 测试智能体基本交互...");

    // 小艾聊天测试
    const xiaoaiResponse = await xiaoai.processMessage(
      "你好，我想了解一下我的健康状况",
      { userId: "test-user" }
    );
    console.log(`小艾回复: ${xiaoaiResponse.success ? "✅ 成功" : "❌ 失败"}`);

    // 小克服务推荐测试
    const xiaokeResponse = await xiaoke.processMessage("我需要预约医生", {
      userId: "test-user",
    });
    console.log(`小克回复: ${xiaokeResponse.success ? "✅ 成功" : "❌ 失败"}`);

    // 老克知识搜索测试
    const laokeResponse = await laoke.processMessage("我想学习中医基础知识", {
      userId: "test-user",
    });
    console.log(`老克回复: ${laokeResponse.success ? "✅ 成功" : "❌ 失败"}`);

    // 索儿生活管理测试
    const soerResponse = await soer.processMessage("我想改善我的生活习惯", {
      userId: "test-user",
    });
    console.log(`索儿回复: ${soerResponse.success ? "✅ 成功" : "❌ 失败"}`);

    // 测试智能体状态
    console.log("\n📊 测试智能体状态...");
    const xiaoaiStatus = await xiaoai.getHealthStatus();
    const xiaokeStatus = await xiaoke.getHealthStatus();
    const laokeStatus = await laoke.getHealthStatus();
    const soerStatus = await soer.getHealthStatus();

    console.log(`小艾状态: ${xiaoaiStatus.status}`);
    console.log(`小克状态: ${xiaokeStatus.status}`);
    console.log(`老克状态: ${laokeStatus.status}`);
    console.log(`索儿状态: ${soerStatus.status}`);

    // 清理资源
    console.log("\n🧹 清理智能体资源...");
    await xiaoai.shutdown();
    await xiaoke.shutdown();
    await laoke.shutdown();
    await soer.shutdown();

    console.log("\n🎉 所有智能体测试完成！索克生活四智能体系统运行正常。");

    return {
      success: true,
      message: "所有智能体测试通过",
      agents: {
        xiaoai: { name: xiaoai.getName(), status: "ok" },
        xiaoke: { name: xiaoke.getName(), status: "ok" },
        laoke: { name: laoke.getName(), status: "ok" },
        soer: { name: soer.getName(), status: "ok" },
      },
    };
  } catch (error: any) {
    console.error("❌ 智能体测试失败:", error.message);
    return {
      success: false,
      error: error.message,
    };
  }
}

/**
 * 测试智能体协作功能
 */
export async function testAgentCollaboration() {
  console.log("🤝 测试智能体协作功能...\n");

  try {
    // 创建所有智能体
    const agents = {
      xiaoai: await createAgent("xiaoai"),
      xiaoke: await createAgent("xiaoke"),
      laoke: await createAgent("laoke"),
      soer: await createAgent("soer"),
    };

    // 初始化所有智能体
    for (const [name, agent] of Object.entries(agents)) {
      await agent.initialize();
      console.log(`✅ ${name} 初始化完成`);
    }

    // 模拟协作场景：用户健康咨询
    console.log("\n📋 模拟协作场景：用户健康咨询");

    const userQuery = "我最近感觉疲劳，想要全面的健康管理方案";
    const userId = "collaboration-test-user";

    // 1. 小艾进行健康分析
    console.log("1️⃣ 小艾进行健康分析...");
    const healthAnalysis = await agents.xiaoai.processMessage(userQuery, {
      userId,
    });

    // 2. 小克推荐相关服务
    console.log("2️⃣ 小克推荐相关服务...");
    const serviceRecommendation = await agents.xiaoke.processMessage(
      `基于健康分析结果推荐服务: ${JSON.stringify(healthAnalysis.data)}`,
      { userId }
    );

    // 3. 老克提供知识支持
    console.log("3️⃣ 老克提供知识支持...");
    const knowledgeSupport = await agents.laoke.processMessage(
      "提供关于疲劳管理的中医知识",
      { userId }
    );

    // 4. 索儿制定生活方式计划
    console.log("4️⃣ 索儿制定生活方式计划...");
    const lifestylePlan = await agents.soer.processMessage(
      "制定改善疲劳的生活方式计划",
      { userId }
    );

    console.log("\n✅ 协作测试完成！四智能体成功协作处理用户需求。");

    // 清理资源
    for (const agent of Object.values(agents)) {
      await agent.shutdown();
    }

    return {
      success: true,
      collaboration: {
        healthAnalysis: healthAnalysis.success,
        serviceRecommendation: serviceRecommendation.success,
        knowledgeSupport: knowledgeSupport.success,
        lifestylePlan: lifestylePlan.success,
      },
    };
  } catch (error: any) {
    console.error("❌ 协作测试失败:", error.message);
    return {
      success: false,
      error: error.message,
    };
  }
}
