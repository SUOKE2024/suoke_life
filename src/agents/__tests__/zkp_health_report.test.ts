import {
  /**
   * 零知识证明健康报告测试
   */

  ProofType,
  zkpHealthReportGenerator,
  batchProofGenerator,
  generateHealthProof,
  verifyHealthProof,
  generateComprehensiveHealthProof,
  verifyComprehensiveHealthProof,
} from "../zkp_health_report";

describe("ZKP Health Report", () => {
  const userId = "test_user_123";

  describe("年龄范围证明", () => {
    it("应该生成有效的年龄范围证明", async () => {
      const proof = await generateHealthProof({
        userId,
        proofType: ProofType.AGE_RANGE,
        privateData: { actualAge: 35 },
        publicAttributes: { minAge: 18, maxAge: 65 },
      });

      expect(proof).toBeDefined();
      expect(proof.type).toBe(ProofType.AGE_RANGE);
      expect(proof.statement).toContain("年龄在 18 到 65 岁之间");
      expect(proof.publicInputs).toEqual([18, 65]);
    });

    it("应该验证有效的年龄证明", async () => {
      const proof = await generateHealthProof({
        userId,
        proofType: ProofType.AGE_RANGE,
        privateData: { actualAge: 35 },
        publicAttributes: { minAge: 18, maxAge: 65 },
      });

      const result = await verifyHealthProof(proof);
      expect(result.valid).toBe(true);
      expect(result.message).toBe("证明验证成功");
    });

    it("应该拒绝超出范围的年龄", async () => {
      const proof = await generateHealthProof({
        userId,
        proofType: ProofType.AGE_RANGE,
        privateData: { actualAge: 70 },
        publicAttributes: { minAge: 18, maxAge: 65 },
      });

      const proofData = JSON.parse(proof.proof);
      expect(proofData.valid).toBe(false);
    });
  });

  describe("健康状态证明", () => {
    it("应该生成健康状态证明", async () => {
      const healthMetrics = {
        bloodPressure: { systolic: 120, diastolic: 80 },
        heartRate: 72,
        bloodSugar: 95,
        bmi: 23.5,
      };

      const proof = await generateHealthProof({
        userId,
        proofType: ProofType.HEALTH_STATUS,
        privateData: { healthMetrics },
        publicAttributes: {
          meetsStandards: true,
          category: "优秀",
        },
      });

      expect(proof.type).toBe(ProofType.HEALTH_STATUS);
      expect(proof.statement).toContain("健康指标符合优秀类别标准");
    });
  });

  describe("生命体征范围证明", () => {
    it("应该验证生命体征在正常范围内", async () => {
      const vitalSigns = {
        temperature: 36.5,
        heartRate: 72,
        bloodPressureSystolic: 120,
        bloodPressureDiastolic: 80,
        respiratoryRate: 16,
      };

      const ranges = [
        { metric: "temperature", min: 36.0, max: 37.5, unit: "℃" },
        { metric: "heartRate", min: 60, max: 100, unit: "bpm" },
        { metric: "bloodPressureSystolic", min: 90, max: 140, unit: "mmHg" },
        { metric: "bloodPressureDiastolic", min: 60, max: 90, unit: "mmHg" },
      ];

      const proof = await generateHealthProof({
        userId,
        proofType: ProofType.VITAL_SIGNS_RANGE,
        privateData: { vitalSigns },
        publicAttributes: { ranges, allInRange: true },
      });

      const result = await verifyHealthProof(proof);
      expect(result.valid).toBe(true);
    });
  });

  describe("体质类型证明", () => {
    it("应该生成体质类型证明", async () => {
      const constitutionData = {
        types: ["平和质", "气虚质"],
        scores: { 平和质: 75, 气虚质: 25 },
      };

      const proof = await generateHealthProof({
        userId,
        proofType: ProofType.CONSTITUTION_TYPE,
        privateData: { constitutionData },
        publicAttributes: {
          hasType: ["平和质"],
          doesNotHaveType: ["阴虚质", "阳虚质"],
          dominantType: "平和质",
        },
      });

      expect(proof.type).toBe(ProofType.CONSTITUTION_TYPE);
      expect(proof.statement).toBe("体质类型验证");
    });
  });

  describe("用药依从性证明", () => {
    it("应该生成用药依从性证明", async () => {
      const medicationRecords = [
        { date: "2024-01-01", taken: true },
        { date: "2024-01-02", taken: true },
        { date: "2024-01-03", taken: true },
        { date: "2024-01-04", taken: false },
        { date: "2024-01-05", taken: true },
      ];

      const proof = await generateHealthProof({
        userId,
        proofType: ProofType.MEDICATION_COMPLIANCE,
        privateData: { medicationRecords },
        publicAttributes: {
          complianceRate: 80,
          period: "2024年1月",
        },
      });

      expect(proof.statement).toContain("2024年1月期间用药依从率达到80%");
    });
  });

  describe("活动水平证明", () => {
    it("应该生成活动水平证明", async () => {
      const activityData = {
        dailySteps: [8000, 10000, 12000, 9000, 11000],
        exerciseMinutes: [30, 45, 60, 40, 50],
        caloriesBurned: [300, 400, 500, 350, 450],
      };

      const proof = await generateHealthProof({
        userId,
        proofType: ProofType.ACTIVITY_LEVEL,
        privateData: { activityData },
        publicAttributes: {
          level: "活跃",
          meetsTarget: true,
        },
      });

      expect(proof.type).toBe(ProofType.ACTIVITY_LEVEL);
      expect(proof.statement).toBe("活动水平达到活跃级别");
    });
  });

  describe("风险评估证明", () => {
    it("应该生成风险评估证明", async () => {
      const riskFactors = [
        { factor: "血压", level: "low" },
        { factor: "血糖", level: "normal" },
        { factor: "体重", level: "normal" },
        { factor: "吸烟", level: "none" },
      ];

      const proof = await generateHealthProof({
        userId,
        proofType: ProofType.RISK_ASSESSMENT,
        privateData: { riskFactors },
        publicAttributes: {
          riskLevel: "低风险",
          belowThreshold: true,
        },
      });

      expect(proof.statement).toBe("健康风险等级为低风险");
    });
  });

  describe("综合健康报告", () => {
    it("应该生成和验证综合健康报告", async () => {
      const healthData = {
        age: 35,
        vitalSigns: {
          temperature: 36.5,
          heartRate: 72,
          bloodPressureSystolic: 120,
          bloodPressureDiastolic: 80,
        },
        constitutionType: ["平和质", "气虚质"],
        activityLevel: "活跃",
        riskFactors: [
          { factor: "血压", level: "normal" },
          { factor: "血糖", level: "normal" },
        ],
      };

      const requirements = {
        ageRange: { min: 18, max: 65 },
        vitalSignsRanges: [
          { metric: "temperature", min: 36.0, max: 37.5, unit: "℃" },
          { metric: "heartRate", min: 60, max: 100, unit: "bpm" },
        ],
        requiredConstitutionTypes: ["平和质"],
        minActivityLevel: "中等",
        maxRiskLevel: "中风险",
      };

      const proofs = await generateComprehensiveHealthProof(
        userId,
        healthData,
        requirements
      );

      expect(proofs).toHaveLength(5);
      expect(proofs.map((p) => p.type)).toContain(ProofType.AGE_RANGE);
      expect(proofs.map((p) => p.type)).toContain(ProofType.VITAL_SIGNS_RANGE);
      expect(proofs.map((p) => p.type)).toContain(ProofType.CONSTITUTION_TYPE);
      expect(proofs.map((p) => p.type)).toContain(ProofType.ACTIVITY_LEVEL);
      expect(proofs.map((p) => p.type)).toContain(ProofType.RISK_ASSESSMENT);

      const verificationResult = await verifyComprehensiveHealthProof(proofs);
      expect(verificationResult.allValid).toBe(true);
      expect(verificationResult.results).toHaveLength(5);
    });
  });

  describe("证明过期验证", () => {
    it("应该拒绝过期的证明", async () => {
      const proof = await generateHealthProof({
        userId,
        proofType: ProofType.AGE_RANGE,
        privateData: { actualAge: 35 },
        publicAttributes: { minAge: 18, maxAge: 65 },
        expirationTime: 1, // 1毫秒后过期
      });

      // 等待证明过期
      await new Promise((resolve) => setTimeout(resolve, 10));

      const result = await verifyHealthProof(proof);
      expect(result.valid).toBe(false);
      expect(result.message).toBe("证明已过期");
    });
  });

  describe("公共输入验证", () => {
    it("应该验证公共输入匹配", async () => {
      const proof = await generateHealthProof({
        userId,
        proofType: ProofType.AGE_RANGE,
        privateData: { actualAge: 35 },
        publicAttributes: { minAge: 18, maxAge: 65 },
      });

      // 使用正确的公共输入
      const result1 = await verifyHealthProof(proof, [18, 65]);
      expect(result1.valid).toBe(true);

      // 使用错误的公共输入
      const result2 = await verifyHealthProof(proof, [20, 60]);
      expect(result2.valid).toBe(false);
      expect(result2.message).toBe("公共输入不匹配");
    });
  });
});
