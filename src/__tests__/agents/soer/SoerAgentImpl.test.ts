import { SoerAgentImpl } from "../../../agents/soer/SoerAgentImpl";

/**
 * 索儿智能体实现测试
 * 索克生活APP - 完整的智能体功能测试
 */

describe("SoerAgentImpl", () => {
  let soerAgent: SoerAgentImpl;

  beforeEach(() => {
    soerAgent = new SoerAgentImpl();
  });

  afterEach(async () => {
    await soerAgent.shutdown();
  });

  // 基础功能测试
  describe("基础功能", () => {
    it("应该正确初始化智能体", () => {
      expect(soerAgent).toBeDefined();
      expect(soerAgent).toBeInstanceOf(SoerAgentImpl);
    });

    it("应该返回正确的智能体信息", () => {
      expect(soerAgent.getId()).toBe("soer");
      expect(soerAgent.getName()).toBe("索儿");
      expect(soerAgent.getDescription()).toBe(
        "LIFE频道版主，专注于生活健康管理、陪伴服务和数据整合分析"
      );
      expect(soerAgent.getStatus()).toBe("active");
    });

    it("应该返回正确的能力列表", () => {
      const capabilities = soerAgent.getCapabilities();
      expect(Array.isArray(capabilities)).toBe(true);
      expect(capabilities.length).toBeGreaterThan(0);

      const expectedCapabilities = [
        "lifestyle_management",
        "emotional_support",
        "habit_tracking",
        "environmental_sensing",
        "wellness_planning",
        "behavior_intervention",
        "multi_device_integration",
        "stress_management",
        "companionship",
        "crisis_support",
      ];

      expectedCapabilities.forEach((capability) => {
        expect(capabilities).toContain(capability);
      });
    });
  });

  // 初始化和关闭测试
  describe("生命周期管理", () => {
    it("应该成功初始化", async () => {
      await expect(soerAgent.initialize()).resolves.not.toThrow();
    });

    it("应该成功关闭", async () => {
      await soerAgent.initialize();
      await expect(soerAgent.shutdown()).resolves.not.toThrow();
    });

    it("应该返回健康状态", async () => {
      const healthStatus = await soerAgent.getHealthStatus();

      expect(healthStatus).toBeDefined();
      expect(healthStatus.agentId).toBe("soer");
      expect(healthStatus.status).toBe("healthy");
      expect(healthStatus.lastHealthCheck).toBeInstanceOf(Date);
      expect(typeof healthStatus.uptime).toBe("number");
      expect(typeof healthStatus.memoryUsage).toBe("number");
      expect(typeof healthStatus.cpuUsage).toBe("number");
      expect(typeof healthStatus.responseTime).toBe("number");
      expect(typeof healthStatus.errorRate).toBe("number");
      expect(typeof healthStatus.throughput).toBe("number");

      expect(healthStatus.metrics).toBeDefined();
      expect(typeof healthStatus.metrics.tasksProcessed).toBe("number");
      expect(typeof healthStatus.metrics.successRate).toBe("number");
      expect(typeof healthStatus.metrics.averageResponseTime).toBe("number");
      expect(healthStatus.metrics.lastActive).toBeInstanceOf(Date);
    });
  });

  // 消息处理测试
  describe("消息处理", () => {
    beforeEach(async () => {
      await soerAgent.initialize();
    });

    it("应该成功处理健康咨询消息", async () => {
      const message = "我想了解一下我的健康状况";
      const context = { userId: "test_user_123" };

      const result = await soerAgent.processMessage(message, context);

      expect(result.success).toBe(true);
      expect(result.agentId).toBe("soer");
      expect(result.timestamp).toBeInstanceOf(Date);
      expect(result.data).toBeDefined();
      expect(result.data.response).toBeDefined();
      expect(typeof result.data.response).toBe("string");
      expect(result.data.response.length).toBeGreaterThan(0);
      expect(result.data.emotionalTone).toBeDefined();
      expect(Array.isArray(result.data.recommendations)).toBe(true);
      expect(Array.isArray(result.data.followUpSuggestions)).toBe(true);
    });

    it("应该成功处理情感支持消息", async () => {
      const message = "我今天感觉很难过，压力很大";
      const context = { userId: "test_user_123" };

      const result = await soerAgent.processMessage(message, context);

      expect(result.success).toBe(true);
      expect(result.data.emotionalTone).toBe("supportive");
      expect(result.data.response).toContain("感受");
    });

    it("应该成功处理生活规划消息", async () => {
      const message = "我想制定一个健康的生活计划";
      const context = { userId: "test_user_123" };

      const result = await soerAgent.processMessage(message, context);

      expect(result.success).toBe(true);
      expect(result.data.response).toContain("计划");
    });

    it("应该成功处理习惯跟踪消息", async () => {
      const message = "我想养成早起的习惯";
      const context = { userId: "test_user_123" };

      const result = await soerAgent.processMessage(message, context);

      expect(result.success).toBe(true);
      expect(result.data.response).toContain("习惯");
    });

    it("应该成功处理危机支持消息", async () => {
      const message = "我需要紧急帮助";
      const context = { userId: "test_user_123" };

      const result = await soerAgent.processMessage(message, context);

      expect(result.success).toBe(true);
      expect(result.data.response).toContain("支持");
    });

    it("应该处理无效消息", async () => {
      const message = "";
      const context = { userId: "test_user_123" };

      const result = await soerAgent.processMessage(message, context);

      expect(result.success).toBe(true);
      expect(result.data.response).toBeDefined();
    });
  });

  // 生活方式管理测试
  describe("生活方式管理", () => {
    beforeEach(async () => {
      await soerAgent.initialize();
    });

    it("应该成功创建生活方式计划", async () => {
      const userId = "test_user_123";
      const planData = {
        title: "健康生活计划",
        description: "改善整体健康状况",
        objectives: ["规律作息", "健康饮食", "适量运动"],
        duration: 30,
      };

      // 首先需要创建用户档案
      const userProfile = { id: userId, name: "测试用户" };
      (soerAgent as any).userProfiles.set(userId, userProfile);

      const result = await soerAgent.manageLifestyle(
        userId,
        "create_plan",
        planData
      );

      expect(result).toBeDefined();
      expect(result.id).toBeDefined();
      expect(result.userId).toBe(userId);
      expect(result.title).toBe(planData.title);
      expect(result.status).toBe("active");
      expect(result.createdAt).toBeInstanceOf(Date);
    });

    it("应该处理不存在的用户", async () => {
      const userId = "non_existent_user";

      await expect(
        soerAgent.manageLifestyle(userId, "create_plan")
      ).rejects.toThrow("用户档案不存在");
    });

    it("应该处理无效的操作", async () => {
      const userId = "test_user_123";
      const userProfile = { id: userId, name: "测试用户" };
      (soerAgent as any).userProfiles.set(userId, userProfile);

      await expect(
        soerAgent.manageLifestyle(userId, "invalid_action")
      ).rejects.toThrow("不支持的生活方式管理操作");
    });
  });

  // 情感支持测试
  describe("情感支持", () => {
    beforeEach(async () => {
      await soerAgent.initialize();
    });

    it("应该提供情感支持", async () => {
      const userId = "test_user_123";
      const emotionalState = {
        mood: "sad",
        intensity: 0.7,
        triggers: ["work_stress", "relationship_issues"],
      };

      const result = await soerAgent.provideEmotionalSupport(
        userId,
        emotionalState
      );

      expect(result.success).toBe(true);
      expect(result.agentId).toBe("soer");
      expect(result.timestamp).toBeInstanceOf(Date);
      expect(result.data).toBeDefined();
    });

    it("应该记录情感状态历史", async () => {
      const userId = "test_user_123";
      const emotionalState = {
        mood: "anxious",
        intensity: 0.5,
      };

      await soerAgent.provideEmotionalSupport(userId, emotionalState);

      const userEmotions = (soerAgent as any).emotionalStates.get(userId);
      expect(Array.isArray(userEmotions)).toBe(true);
      expect(userEmotions.length).toBeGreaterThan(0);
      expect(userEmotions[0].mood).toBe("anxious");
      expect(userEmotions[0].timestamp).toBeInstanceOf(Date);
    });
  });

  // 习惯跟踪测试
  describe("习惯跟踪", () => {
    beforeEach(async () => {
      await soerAgent.initialize();
    });

    it("应该成功跟踪习惯", async () => {
      const userId = "test_user_123";
      const habitData = {
        habitType: "exercise",
        completed: true,
        duration: 30,
        notes: "晨跑30分钟",
      };

      const result = await soerAgent.trackHabits(userId, habitData);

      expect(result.success).toBe(true);
      expect(result.habitData).toEqual(habitData);
      expect(result.trends).toBeDefined();
      expect(Array.isArray(result.suggestions)).toBe(true);
      expect(typeof result.streakCount).toBe("number");
      expect(typeof result.nextMilestone).toBe("string");
      expect(result.timestamp).toBeInstanceOf(Date);
    });

    it("应该记录习惯历史", async () => {
      const userId = "test_user_123";
      const habitData = {
        habitType: "meditation",
        completed: true,
        duration: 15,
      };

      await soerAgent.trackHabits(userId, habitData);

      const userHabits = (soerAgent as any).habitTracking.get(userId);
      expect(Array.isArray(userHabits)).toBe(true);
      expect(userHabits.length).toBeGreaterThan(0);
      expect(userHabits[0].habitType).toBe("meditation");
    });
  });

  // 设备协调测试
  describe("设备协调", () => {
    beforeEach(async () => {
      await soerAgent.initialize();
    });

    it("应该成功协调设备", async () => {
      const userId = "test_user_123";
      const devices = [
        { id: "device1", type: "fitness_tracker" },
        { id: "device2", type: "smart_scale" },
      ];
      (soerAgent as any).smartDevices.set(userId, devices);

      const result = await soerAgent.coordinateDevices(userId, "sync_data");

      expect(result.success).toBe(true);
      expect(result.action).toBe("sync_data");
      expect(result.deviceCount).toBe(2);
      expect(Array.isArray(result.results)).toBe(true);
      expect(result.timestamp).toBeInstanceOf(Date);
    });

    it("应该处理无效的设备操作", async () => {
      const userId = "test_user_123";

      const result = await soerAgent.coordinateDevices(
        userId,
        "invalid_action"
      );

      expect(result.success).toBe(false);
      expect(result.error).toContain("不支持的设备协调操作");
    });
  });

  // 压力管理测试
  describe("压力管理", () => {
    beforeEach(async () => {
      await soerAgent.initialize();
    });

    it("应该成功管理压力", async () => {
      const userId = "test_user_123";
      const stressData = {
        level: 7,
        sources: ["work", "family"],
        symptoms: ["headache", "insomnia"],
      };

      const result = await soerAgent.manageStress(userId, stressData);

      expect(result.success).toBe(true);
      expect(result.stressLevel).toBeDefined();
      expect(Array.isArray(result.stressSources)).toBe(true);
      expect(Array.isArray(result.strategies)).toBe(true);
      expect(Array.isArray(result.immediateRelief)).toBe(true);
      expect(result.followUpPlan).toBeDefined();
      expect(result.timestamp).toBeInstanceOf(Date);
    });
  });

  // 危机支持测试
  describe("危机支持", () => {
    beforeEach(async () => {
      await soerAgent.initialize();
    });

    it("应该提供危机支持", async () => {
      const userId = "test_user_123";
      const crisisData = {
        severity: "moderate",
        type: "emotional",
        description: "感到极度焦虑和恐慌",
      };

      const result = await soerAgent.provideCrisisSupport(userId, crisisData);

      expect(result.success).toBe(true);
      expect(result.severityLevel).toBeDefined();
      expect(result.immediateSupport).toBeDefined();
      expect(Array.isArray(result.professionalResources)).toBe(true);
      expect(result.safetyPlan).toBeDefined();
      expect(result.followUpSchedule).toBeDefined();
      expect(Array.isArray(result.emergencyContacts)).toBe(true);
      expect(result.timestamp).toBeInstanceOf(Date);
    });
  });

  // 错误处理测试
  describe("错误处理", () => {
    beforeEach(async () => {
      await soerAgent.initialize();
    });

    it("应该处理消息处理错误", async () => {
      // 模拟错误情况
      const originalMethod = (soerAgent as any).analyzeEmotionalState;
      (soerAgent as any).analyzeEmotionalState = jest
        .fn()
        .mockRejectedValue(new Error("分析失败"));

      const result = await soerAgent.processMessage("测试消息", {});

      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
      expect(result.agentId).toBe("soer");

      // 恢复原方法
      (soerAgent as any).analyzeEmotionalState = originalMethod;
    });

    it("应该处理情感支持错误", async () => {
      const userId = "test_user_123";
      const emotionalState = null; // 无效的情感状态

      const result = await soerAgent.provideEmotionalSupport(
        userId,
        emotionalState
      );

      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
    });

    it("应该处理习惯跟踪错误", async () => {
      const userId = "test_user_123";
      const habitData = null; // 无效的习惯数据

      const result = await soerAgent.trackHabits(userId, habitData);

      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
    });
  });

  // 性能测试
  describe("性能", () => {
    beforeEach(async () => {
      await soerAgent.initialize();
    });

    it("应该快速处理消息", async () => {
      const message = "你好，索儿";
      const context = { userId: "test_user_123" };

      const startTime = Date.now();
      const result = await soerAgent.processMessage(message, context);
      const endTime = Date.now();

      expect(result.success).toBe(true);
      expect(endTime - startTime).toBeLessThan(1000); // 应该在1秒内完成
    });

    it("应该高效处理批量操作", async () => {
      const userId = "test_user_123";
      const userProfile = { id: userId, name: "测试用户" };
      (soerAgent as any).userProfiles.set(userId, userProfile);

      const startTime = Date.now();

      // 批量创建习惯记录
      const promises = Array.from({ length: 10 }, (_, i) =>
        soerAgent.trackHabits(userId, {
          habitType: "exercise",
          completed: true,
          duration: 30,
          notes: `第${i + 1}次运动`,
        })
      );

      const results = await Promise.all(promises);
      const endTime = Date.now();

      expect(results.length).toBe(10);
      expect(results.every((r) => r.success)).toBe(true);
      expect(endTime - startTime).toBeLessThan(2000); // 应该在2秒内完成
    });
  });
});
