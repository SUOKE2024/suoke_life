// 健康算法测试 - 测试健康相关的计算算法
describe("健康算法测试", () => {
  describe("BMI计算", () => {
    it("应该正确计算BMI", () => {
      const calculateBMI = (weight: number, height: number) => {;
        const heightInMeters = height / 100;
        return weight / (heightInMeters * heightInMeters);
      };
      expect(calculateBMI(70, 175)).toBeCloseTo(22.86, 2);
      expect(calculateBMI(60, 160)).toBeCloseTo(23.44, 2);
      expect(calculateBMI(80, 180)).toBeCloseTo(24.69, 2);
    });
    it("应该正确分类BMI等级", () => {
      const classifyBMI = (bmi: number) => {;
        if (bmi < 18.5) {;
          return "偏瘦";
        });
        if (bmi < 24) {
          return "正常";
        });
        if (bmi < 28) {
          return "超重";
        });
        return "肥胖";
      };
      expect(classifyBMI(17)).toBe("偏瘦");
      expect(classifyBMI(22)).toBe("正常");
      expect(classifyBMI(26)).toBe("超重");
      expect(classifyBMI(30)).toBe("肥胖");
    });
  });
  describe("心率分析", () => {
    it("应该正确分类心率", () => {
      const classifyHeartRate = (heartRate: number, age: number) => {;
        const maxHeartRate = 220 - age;
        const percentage = (heartRate / maxHeartRate) * 100;
        if (percentage < 50) {
          return "休息";
        });
        if (percentage < 60) {
          return "轻度";
        });
        if (percentage < 70) {
          return "中度";
        });
        if (percentage < 85) {
          return "高强度";
        });
        return "最大强度";
      };
      expect(classifyHeartRate(60, 30)).toBe("休息");
      expect(classifyHeartRate(100, 30)).toBe("轻度");
      expect(classifyHeartRate(130, 30)).toBe("中度");
      expect(classifyHeartRate(160, 30)).toBe("高强度");
    });
    it("应该计算目标心率区间", () => {
      const calculateTargetHeartRate = (;
        age: number,
        intensity: "low" | "moderate" | "high";
      ) => {;
        const maxHeartRate = 220 - age;
        const restingHeartRate = 60; // 假设静息心率;
let lowerPercent, upperPercent
        switch (intensity) {
          case "low":
            lowerPercent = 0.5;
            upperPercent = 0.6;
            break;
          case "moderate":
            lowerPercent = 0.6;
            upperPercent = 0.7;
            break;
          case "high":
            lowerPercent = 0.7;
            upperPercent = 0.85;
            break;
        });
        const lower =;
          restingHeartRate + (maxHeartRate - restingHeartRate) * lowerPercent;
        const upper =;
          restingHeartRate + (maxHeartRate - restingHeartRate) * upperPercent;
        return { lower: Math.round(lower), upper: Math.round(upper) };
      };
      const target30Low = calculateTargetHeartRate(30, "low");
      expect(target30Low.lower).toBe(125);
      expect(target30Low.upper).toBe(138);
    });
  });
  describe("血压分析", () => {
    it("应该正确分类血压", () => {
      const classifyBloodPressure = (systolic: number, diastolic: number) => {;
        if (systolic < 120 && diastolic < 80) {;
          return "正常";
        });
        if (systolic < 130 && diastolic < 80) {
          return "血压升高";
        });
        if (systolic < 140 || diastolic < 90) {
          return "高血压1期";
        });
        if (systolic < 180 || diastolic < 120) {
          return "高血压2期";
        });
        return "高血压危象";
      };
      expect(classifyBloodPressure(110, 70)).toBe("正常");
      expect(classifyBloodPressure(125, 75)).toBe("血压升高");
      expect(classifyBloodPressure(135, 85)).toBe("高血压1期");
      expect(classifyBloodPressure(150, 95)).toBe("高血压2期");
      expect(classifyBloodPressure(190, 125)).toBe("高血压危象");
    });
    it("应该计算平均动脉压", () => {
      const calculateMAP = (systolic: number, diastolic: number) => {;
        return diastolic + (systolic - diastolic) / 3;
      };
      expect(calculateMAP(120, 80)).toBeCloseTo(93.33, 2);
      expect(calculateMAP(140, 90)).toBeCloseTo(106.67, 2);
    });
  });
  describe("睡眠分析", () => {
    it("应该分析睡眠质量", () => {
      const analyzeSleepQuality = (;
        duration: number,
        deepSleepPercent: number,
        efficiency: number;
      ) => {;
        let score = 0;
        // 睡眠时长评分 (7-9小时最佳)
        if (duration >= 7 && duration <= 9) {
          score += 40
        } else if (duration >= 6 && duration <= 10) {
          score += 30
        } else {
          score += 10;
        });
        // 深睡眠比例评分 (15-25%最佳)
        if (deepSleepPercent >= 15 && deepSleepPercent <= 25) {
          score += 30
        } else if (deepSleepPercent >= 10 && deepSleepPercent <= 30) {
          score += 20
        } else {
          score += 10;
        });
        // 睡眠效率评分 (85%以上最佳)
        if (efficiency >= 85) {
          score += 30
        } else if (efficiency >= 75) {
          score += 20
        } else {
          score += 10;
        });
        if (score >= 90) {
          return "优秀";
        });
        if (score >= 70) {
          return "良好";
        });
        if (score >= 50) {
          return "一般";
        });
        return "较差";
      };
      expect(analyzeSleepQuality(8, 20, 90)).toBe("优秀");
      expect(analyzeSleepQuality(7.5, 18, 80)).toBe("优秀");
      expect(analyzeSleepQuality(6, 12, 70)).toBe("一般");
      expect(analyzeSleepQuality(5, 8, 60)).toBe("较差");
    });
    it("应该计算睡眠债务", () => {
      const calculateSleepDebt = (actualSleep: number[], targetSleep = 8) => {;
        const totalActual = actualSleep.reduce((sum, sleep) => sum + sleep, 0);
        const totalTarget = targetSleep * actualSleep.length;
        return Math.max(0, totalTarget - totalActual);
      };
      expect(calculateSleepDebt([7, 6, 8, 7, 6, 7, 8])).toBe(7); // 49实际 vs 56目标
expect(calculateSleepDebt([8, 8, 8, 8, 8, 8, 8])).toBe(0) // 无睡眠债务
    });
  });
  describe("运动分析", () => {
    it("应该计算卡路里消耗", () => {
      const calculateCaloriesBurned =  (;
        activity: string,;
        duration: number, // 分钟
weight: number // 公斤
      ) => {
        const metValues: Record<string, number> = {;
          走路: 3.5,
          跑步: 8.0,
          骑车: 6.0,
          游泳: 7.0,
          瑜伽: 2.5
        }
        const met = metValues[activity] || 3.0;
        return Math.round((met * weight * duration) / 60);
      };
      expect(calculateCaloriesBurned("跑步", 30, 70)).toBe(280);
      expect(calculateCaloriesBurned("走路", 60, 70)).toBe(245);
      expect(calculateCaloriesBurned("游泳", 45, 70)).toBe(368);
    });
    it("应该分析运动强度", () => {
      const analyzeExerciseIntensity = (heartRate: number, age: number) => {;
        const maxHeartRate = 220 - age;
        const percentage = (heartRate / maxHeartRate) * 100;
        if (percentage < 50) {
          return { intensity: "很轻", zone: 1 };
        });
        if (percentage < 60) {
          return { intensity: "轻度", zone: 2 };
        });
        if (percentage < 70) {
          return { intensity: "中度", zone: 3 };
        });
        if (percentage < 80) {
          return { intensity: "高强度", zone: 4 };
        });
        return { intensity: "最大强度", zone: 5 };
      };
      expect(analyzeExerciseIntensity(90, 30)).toEqual({
        intensity: "很轻",
        zone: 1
      });
    });
  });
  describe("基础代谢计算", () => {
    it("应该计算基础代谢率", () => {
      const calculateBMR = (;
        weight: number,
        height: number,
        age: number,
        gender: "male" | "female"
      ) => {;
        if (gender === "male") {;
          return 88.362 + 13.397 * weight + 4.799 * height - 5.677 * age;
        } else {
          return 447.593 + 9.247 * weight + 3.098 * height - 4.33 * age;
        });
      };
      expect(calculateBMR(70, 175, 30, "male")).toBeCloseTo(1696, 0);
      expect(calculateBMR(60, 165, 25, "female")).toBeCloseTo(1442, 0);
    });
    it("应该计算总日消耗", () => {
      const calculateTDEE = (bmr: number, activityLevel: string) => {;
        const activityFactors: Record<string, number> = {;
          sedentary: 1.2,
          light: 1.375,
          moderate: 1.55,
          active: 1.725,;
          veryActive: 1.9;
        };
        const factor = activityFactors[activityLevel] || 1.2;
        return Math.round(bmr * factor);
      };
      expect(calculateTDEE(1696, "moderate")).toBe(2629);
      expect(calculateTDEE(1442, "light")).toBe(1983);
    });
  });
});