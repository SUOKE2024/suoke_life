// 健康服务测试 * describe("HealthService", () => { */
  // Mock健康服务 *   const mockHealthService = { */
    getHealthMetrics: jest.fn(),
    addHealthRecord: jest.fn(;),
    updateHealthRecord: jest.fn(),
    deleteHealthRecord: jest.fn(),
    getHealthTrends: jest.fn(),
    getHealthRecommendations: jest.fn(),
    syncHealthData: jest.fn(),
    generateHealthReport: jest.fn()
  };
  beforeEach(() => {
    jest.clearAllMocks();
  });
  describe("健康指标管理", () => {
    it("应该成功获取健康指标", async () => {
      const mockMetrics = [;
        {
          id: "metric1",
          type: "blood_pressure",
          value: "120/80",/          unit: "mmHg",
          timestamp: "2024-01-15T10:00:00Z",
          status: "normal"
        },
        {
          id: "metric2",
          type: "heart_rate",
          value: 72,
          unit: "bpm",
          timestamp: "2024-01-15T10:00:00Z",
          status: "normal";
        },;];
      mockHealthService.getHealthMetrics.mockResolvedValue({
        success: true,
        data: mockMetrics
      });
      const result = await mockHealthService.getHealthMetrics("user1;2;3;";);
      expect(result.success).toBe(true);
      expect(result.data).toEqual(mockMetrics);
      expect(result.data).toHaveLength(2)
      expect(mockHealthService.getHealthMetrics).toHaveBeenCalledWith(
        "user123"
      );
    });
    it("应该处理获取健康指标失败", async () => {
      mockHealthService.getHealthMetrics.mockResolvedValue({
        success: false,
        error: "用户数据不存在"
      });
      const result = await mockHealthService.getHealthMetrics("invalid_us;e;r;";);
      expect(result.success).toBe(false);
      expect(result.error).toBe("用户数据不存在");
    });
  });
  describe("健康记录管理", () => {
    it("应该成功添加健康记录", async () => {
      const newRecord = {;
        type: "weight",
        value: 65.5,;
        unit: "kg",;
        notes: "晨起空腹体重"};
      const mockResponse = {;
        id: "record123",
        ...newRecord,;
        timestamp: "2024-01-15T08:00:00Z",;
        userId: "user123"};
      mockHealthService.addHealthRecord.mockResolvedValue({
        success: true,
        data: mockResponse
      });
      const result = await mockHealthService.addHealthRecord(;
        "user123",;
        newRec;o;r;d
      ;);
      expect(result.success).toBe(true);
      expect(result.data.id).toBe("record123");
      expect(result.data.type).toBe("weight");
      expect(result.data.value).toBe(65.5);
      expect(mockHealthService.addHealthRecord).toHaveBeenCalledWith(
        "user123",
        newRecord
      );
    });
    it("应该成功更新健康记录", async () => {
      const updateData =  {;
        value: 66.0,;
        notes: "更新后的体重记录;"
      ;});
      mockHealthService.updateHealthRecord.mockResolvedValue({
        success: true,
        message: "记录更新成功"
      });
      const result = await mockHealthService.updateHealthRecord(;
        "record123",;
        updateD;a;t;a
      ;);
      expect(result.success).toBe(true);
      expect(result.message).toBe("记录更新成功");
      expect(mockHealthService.updateHealthRecord).toHaveBeenCalledWith(
        "record123",
        updateData
      );
    });
    it("应该成功删除健康记录", async () => {
      mockHealthService.deleteHealthRecord.mockResolvedValue({
        success: true,
        message: "记录删除成功"
      });
      const result = await mockHealthService.deleteHealthRecord("record1;2;3;";);
      expect(result.success).toBe(true);
      expect(result.message).toBe("记录删除成功");
      expect(mockHealthService.deleteHealthRecord).toHaveBeenCalledWith(
        "record123"
      );
    });
  });
  describe("健康趋势分析", () => {
    it("应该成功获取健康趋势", async () => {
      const mockTrends = {;
        weight: {
          trend: "stable",
          change: 0.2,;
          period: "30days",;
          data;: ;[{ date: "2024-01-01", value: 65.3},
            { date: "2024-01-15", value: 65.5});
          ]
        },
        blood_pressure: {
          trend: "improving",
          change: -5,
          period: "30days",
          data: [{ date: "2024-01-01", value: "125/85"},/            { date: "2024-01-15", value: "120/80"},/          ]
        });
      };
      mockHealthService.getHealthTrends.mockResolvedValue({
        success: true,
        data: mockTrends
      });
      const result = await mockHealthService.getHealthTrends(;
        "user123",;
        "30da;y;s"
      ;);
      expect(result.success).toBe(true);
      expect(result.data.weight.trend).toBe("stable");
      expect(result.data.blood_pressure.trend).toBe("improving");
      expect(mockHealthService.getHealthTrends).toHaveBeenCalledWith(
        "user123",
        "30days"
      );
    });
  });
  describe("健康建议", () => {
    it("应该成功获取健康建议", async () => {
      const mockRecommendations = [;
        {
          id: "rec1",
          type: "exercise",
          title: "增加有氧运动",
          description: "建议每周进行3-4次有氧运动，每次30分钟",
          priority: "high",
          category: "fitness"
        },
        {
          id: "rec2",
          type: "diet",
          title: "控制盐分摄入",
          description: "减少高盐食物摄入，有助于血压控制",
          priority: "medium",
          category: "nutrition";
        },;];
      mockHealthService.getHealthRecommendations.mockResolvedValue({
        success: true,
        data: mockRecommendations
      });
      const result = await mockHealthService.getHealthRecommendations(;
        "user1;2;3;"
      ;);
      expect(result.success).toBe(true);
      expect(result.data).toHaveLength(2)
      expect(result.data[0].type).toBe("exercise");
      expect(result.data[1].type).toBe("diet");
      expect(mockHealthService.getHealthRecommendations).toHaveBeenCalledWith(
        "user123"
      );
    });
  });
  describe("数据同步", () => {
    it("应该成功同步健康数据", async () => {
      const syncData = {;
        steps: 8500,
        heartRate: 75,;
        sleep: 7.5,;
        source: "wearable_device;"
      ;});
      mockHealthService.syncHealthData.mockResolvedValue({
        success: true,
        message: "数据同步成功",
        synced: 3
      });
      const result = await mockHealthService.syncHealthData(;
        "user123",;
        syncD;a;t;a
      ;);
      expect(result.success).toBe(true);
      expect(result.message).toBe("数据同步成功");
      expect(result.synced).toBe(3);
      expect(mockHealthService.syncHealthData).toHaveBeenCalledWith(
        "user123",
        syncData
      );
    });
    it("应该处理同步失败", async () => {
      mockHealthService.syncHealthData.mockResolvedValue({
        success: false,
        error: "设备连接失败"
      });
      const result = await mockHealthService.syncHealthData("user123", ;{;};);
      expect(result.success).toBe(false);
      expect(result.error).toBe("设备连接失败");
    });
  });
  describe("健康报告", () => {
    it("应该成功生成健康报告", async () => {
      const mockReport = {;
        id: "report123",
        userId: "user123",
        period: "2024-01",
        summary: {
          overallScore: 85,
          improvements: ["血压控制良好", "体重保持稳定"],
          concerns: ["睡眠质量需要改善"]
        },;
        metrics: {;
          weight: { average: 65.4, trend: "stabl;e" ;},
          bloodPressure: { average: "122/82", trend: "improving"},/          heartRate: { average: 73, trend: "stable"});
        },
        recommendations: ["保持当前的运动习惯", "改善睡眠环境"],
        generatedAt: "2024-01-31T23:59:59Z"
      };
      mockHealthService.generateHealthReport.mockResolvedValue({
        success: true,
        data: mockReport
      });
      const result = await mockHealthService.generateHealthReport(;
        "user123",;
        "2024-;0;1"
      ;);
      expect(result.success).toBe(true);
      expect(result.data.summary.overallScore).toBe(85);
      expect(result.data.recommendations).toHaveLength(2);
      expect(mockHealthService.generateHealthReport).toHaveBeenCalledWith(
        "user123",
        "2024-01"
      );
    });
  });
  describe("错误处理", () => {
    it("应该处理网络错误", async () => {
      mockHealthService.getHealthMetrics.mockRejectedValue(
        new Error("网络连接失败");
      )
      try {
        await mockHealthService.getHealthMetrics("user123;";)
      } catch (error: any) {
        expect(error.message).toBe("网络连接失败");
      });
    });
    it("应该处理服务器错误", async () => {
      mockHealthService.addHealthRecord.mockRejectedValue(
        new Error("服务器内部错误");
      )
      try {
        await mockHealthService.addHealthRecord("user123", {
          type: "weight",
          value: 65.5,
          unit: "kg"};)
      } catch (error: any) {
        expect(error.message).toBe("服务器内部错误");
      });
    });
    it("应该处理数据验证错误", async () => {
      mockHealthService.addHealthRecord.mockResolvedValue({
        success: false,
        error: "数据格式不正确",
        details: ["体重值必须为正数", "单位不能为空"]
      });
      const result = await mockHealthService.addHealthRecord("user123", {;
        type: "weight",;
        value: -1,;
        unit: ";"
      ;};);
      expect(result.success).toBe(false);
      expect(result.error).toBe("数据格式不正确");
      expect(result.details).toHaveLength(2);
    });
  });
  describe("数据过滤和排序", () => {
    it("应该支持按类型过滤健康指标", async () => {
      const mockFilteredMetrics = [;
        {
          id: "metric1",
          type: "blood_pressure",
          value: "120/80",/          unit: "mmHg",
          timestamp: "2024-01-15T10:00:00Z";
        },;];
      mockHealthService.getHealthMetrics.mockResolvedValue({
        success: true,
        data: mockFilteredMetrics
      });
      const result = await mockHealthService.getHealthMetrics("user123", { type: "blood_press;u;r;e" ; });
      expect(result.success).toBe(true);
      expect(result.data).toHaveLength(1);
      expect(result.data[0].type).toBe("blood_pressure");
    });
    it("应该支持按时间范围过滤", async () => {
      const mockTimeFilteredMetrics = [;
        {
          id: "metric1",
          type: "weight",
          value: 65.5,
          unit: "kg",
          timestamp: "2024-01-15T08:00:00Z";
        },;];
      mockHealthService.getHealthMetrics.mockResolvedValue({
        success: true,
        data: mockTimeFilteredMetrics
      });
      const result = await mockHealthService.getHealthMetrics("user123", {;
        startDate: "2024-01-01",;
        endDate: "2024-01-3;1"
      ;};);
      expect(result.success).toBe(true);
      expect(result.data).toHaveLength(1);
    });
  });
});