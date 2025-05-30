/**
 * 健康算法测试
 * 测试健康相关的计算算法
 */

describe("健康算法测试", () => {
  describe("BMI计算", () => {
    it("应该正确计算BMI", () => {
      const calculateBMI = (weight: number, height: number) => {
        const heightInMeters = height / 100;
        return weight / (heightInMeters * heightInMeters);
      };

      expect(calculateBMI(70, 175)).toBeCloseTo(22.86, 2);
      expect(calculateBMI(60, 160)).toBeCloseTo(23.44, 2);
      expect(calculateBMI(80, 180)).toBeCloseTo(24.69, 2);
    });

    it("应该正确分类BMI等级", () => {
      const classifyBMI = (bmi: number) => {
        if (bmi < 18.5) {
          return "偏瘦";
        }
        if (bmi < 24) {
          return "正常";
        }
        if (bmi < 28) {
          return "超重";
        }
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
      const classifyHeartRate = (heartRate: number, age: number) => {
        const maxHeartRate = 220 - age;
        const percentage = (heartRate / maxHeartRate) * 100;

        if (percentage < 50) {
          return "休息";
        }
        if (percentage < 60) {
          return "轻度";
        }
        if (percentage < 70) {
          return "中度";
        }
        if (percentage < 85) {
          return "高强度";
        }
        return "最大强度";
      };

      expect(classifyHeartRate(60, 30)).toBe("休息"); // 60/(220-30) = 31.6%
      expect(classifyHeartRate(100, 30)).toBe("轻度"); // 100/190 = 52.6%
      expect(classifyHeartRate(130, 30)).toBe("中度"); // 130/190 = 68.4%
      expect(classifyHeartRate(160, 30)).toBe("高强度"); // 160/190 = 84.2%
    });

    it("应该计算目标心率区间", () => {
      const calculateTargetHeartRate = (
        age: number,
        intensity: "low" | "moderate" | "high"
      ) => {
        const maxHeartRate = 220 - age;
        const restingHeartRate = 60; // 假设静息心率

        let lowerPercent, upperPercent;
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
        }

        const lower =
          restingHeartRate + (maxHeartRate - restingHeartRate) * lowerPercent;
        const upper =
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
      const classifyBloodPressure = (systolic: number, diastolic: number) => {
        if (systolic < 120 && diastolic < 80) {
          return "正常";
        }
        if (systolic < 130 && diastolic < 80) {
          return "血压升高";
        }
        if (systolic < 140 || diastolic < 90) {
          return "高血压1期";
        }
        if (systolic < 180 || diastolic < 120) {
          return "高血压2期";
        }
        return "高血压危象";
      };

      expect(classifyBloodPressure(110, 70)).toBe("正常");
      expect(classifyBloodPressure(125, 75)).toBe("血压升高");
      expect(classifyBloodPressure(135, 85)).toBe("高血压1期");
      expect(classifyBloodPressure(150, 95)).toBe("高血压2期");
      expect(classifyBloodPressure(190, 125)).toBe("高血压危象");
    });

    it("应该计算平均动脉压", () => {
      const calculateMAP = (systolic: number, diastolic: number) => {
        return diastolic + (systolic - diastolic) / 3;
      };

      expect(calculateMAP(120, 80)).toBeCloseTo(93.33, 2);
      expect(calculateMAP(140, 90)).toBeCloseTo(106.67, 2);
    });
  });

  describe("睡眠分析", () => {
    it("应该分析睡眠质量", () => {
      const analyzeSleepQuality = (
        duration: number,
        deepSleepPercent: number,
        efficiency: number
      ) => {
        let score = 0;

        // 睡眠时长评分 (7-9小时最佳)
        if (duration >= 7 && duration <= 9) {
          score += 40;
        } else if (duration >= 6 && duration <= 10) {
          score += 30;
        } else {
          score += 10;
        }

        // 深睡眠比例评分 (15-25%最佳)
        if (deepSleepPercent >= 15 && deepSleepPercent <= 25) {
          score += 30;
        } else if (deepSleepPercent >= 10 && deepSleepPercent <= 30) {
          score += 20;
        } else {
          score += 10;
        }

        // 睡眠效率评分 (85%以上最佳)
        if (efficiency >= 85) {
          score += 30;
        } else if (efficiency >= 75) {
          score += 20;
        } else {
          score += 10;
        }

        if (score >= 90) {
          return "优秀";
        }
        if (score >= 70) {
          return "良好";
        }
        if (score >= 50) {
          return "一般";
        }
        return "较差";
      };

      expect(analyzeSleepQuality(8, 20, 90)).toBe("优秀");
      expect(analyzeSleepQuality(7.5, 18, 80)).toBe("优秀");
      expect(analyzeSleepQuality(6, 12, 70)).toBe("一般");
      expect(analyzeSleepQuality(5, 8, 60)).toBe("较差");
    });

    it("应该计算睡眠债务", () => {
      const calculateSleepDebt = (actualSleep: number[], targetSleep = 8) => {
        const totalActual = actualSleep.reduce((sum, sleep) => sum + sleep, 0);
        const totalTarget = targetSleep * actualSleep.length;
        return Math.max(0, totalTarget - totalActual);
      };

      expect(calculateSleepDebt([7, 6, 8, 7, 6, 7, 8])).toBe(7); // 49实际 vs 56目标
      expect(calculateSleepDebt([8, 8, 8, 8, 8, 8, 8])).toBe(0); // 无睡眠债务
    });
  });

  describe("运动分析", () => {
    it("应该计算卡路里消耗", () => {
      const calculateCaloriesBurned = (
        activity: string,
        duration: number, // 分钟
        weight: number // 公斤
      ) => {
        const metValues: Record<string, number> = {
          走路: 3.5,
          跑步: 8.0,
          骑车: 6.0,
          游泳: 7.0,
          瑜伽: 2.5,
        };

        const met = metValues[activity] || 3.0;
        return Math.round((met * weight * duration) / 60);
      };

      expect(calculateCaloriesBurned("跑步", 30, 70)).toBe(280);
      expect(calculateCaloriesBurned("走路", 60, 70)).toBe(245);
      expect(calculateCaloriesBurned("游泳", 45, 70)).toBe(368);
    });

    it("应该分析运动强度", () => {
      const analyzeExerciseIntensity = (heartRate: number, age: number) => {
        const maxHeartRate = 220 - age;
        const percentage = (heartRate / maxHeartRate) * 100;

        if (percentage < 50) {
          return { intensity: "很轻", zone: 1 };
        }
        if (percentage < 60) {
          return { intensity: "轻度", zone: 2 };
        }
        if (percentage < 70) {
          return { intensity: "中度", zone: 3 };
        }
        if (percentage < 80) {
          return { intensity: "高强度", zone: 4 };
        }
        return { intensity: "最大强度", zone: 5 };
      };

      expect(analyzeExerciseIntensity(90, 30)).toEqual({
        intensity: "很轻",
        zone: 1,
      });
      expect(analyzeExerciseIntensity(130, 30)).toEqual({
        intensity: "中度",
        zone: 3,
      });
      expect(analyzeExerciseIntensity(170, 30)).toEqual({
        intensity: "最大强度",
        zone: 5,
      });
    });
  });

  describe("营养分析", () => {
    it("应该计算基础代谢率", () => {
      const calculateBMR = (
        weight: number,
        height: number,
        age: number,
        gender: "male" | "female"
      ) => {
        if (gender === "male") {
          return 88.362 + 13.397 * weight + 4.799 * height - 5.677 * age;
        } else {
          return 447.593 + 9.247 * weight + 3.098 * height - 4.33 * age;
        }
      };

      expect(calculateBMR(70, 175, 30, "male")).toBeCloseTo(1696, 0);
      expect(calculateBMR(60, 165, 25, "female")).toBeCloseTo(1405, 0);
    });

    it("应该计算每日总能量消耗", () => {
      const calculateTDEE = (bmr: number, activityLevel: string) => {
        const activityMultipliers: Record<string, number> = {
          久坐: 1.2,
          轻度活动: 1.375,
          中度活动: 1.55,
          高度活动: 1.725,
          极高活动: 1.9,
        };

        return Math.round(bmr * (activityMultipliers[activityLevel] || 1.2));
      };

      expect(calculateTDEE(1700, "久坐")).toBe(2040);
      expect(calculateTDEE(1700, "中度活动")).toBe(2635);
    });
  });

  describe("健康风险评估", () => {
    it("应该评估心血管风险", () => {
      const assessCardiovascularRisk = (
        age: number,
        systolic: number,
        cholesterol: number,
        smoking: boolean,
        diabetes: boolean
      ) => {
        let risk = 0;

        // 年龄风险
        if (age > 65) {
          risk += 3;
        } else if (age > 55) {
          risk += 2;
        } else if (age > 45) {
          risk += 1;
        }

        // 血压风险
        if (systolic > 160) {
          risk += 3;
        } else if (systolic > 140) {
          risk += 2;
        } else if (systolic > 120) {
          risk += 1;
        }

        // 胆固醇风险
        if (cholesterol > 240) {
          risk += 2;
        } else if (cholesterol > 200) {
          risk += 1;
        }

        // 生活方式风险
        if (smoking) {
          risk += 2;
        }
        if (diabetes) {
          risk += 2;
        }

        if (risk >= 8) {
          return "高风险";
        }
        if (risk >= 5) {
          return "中等风险";
        }
        if (risk >= 2) {
          return "低风险";
        }
        return "很低风险";
      };

      expect(assessCardiovascularRisk(70, 170, 250, true, true)).toBe("高风险");
      expect(assessCardiovascularRisk(50, 130, 180, false, false)).toBe(
        "低风险"
      );
      expect(assessCardiovascularRisk(30, 110, 160, false, false)).toBe(
        "很低风险"
      );
    });

    it("应该计算健康评分", () => {
      const calculateHealthScore = (metrics: {
        bmi: number;
        bloodPressure: { systolic: number; diastolic: number };
        heartRate: number;
        sleepHours: number;
        exerciseMinutes: number;
        smoking: boolean;
      }) => {
        let score = 100;

        // BMI评分
        if (metrics.bmi < 18.5 || metrics.bmi > 30) {
          score -= 20;
        } else if (metrics.bmi > 25) {
          score -= 10;
        }

        // 血压评分
        if (
          metrics.bloodPressure.systolic > 140 ||
          metrics.bloodPressure.diastolic > 90
        ) {
          score -= 20;
        } else if (metrics.bloodPressure.systolic > 120) {
          score -= 5;
        }

        // 心率评分
        if (metrics.heartRate > 100 || metrics.heartRate < 50) {
          score -= 10;
        }

        // 睡眠评分
        if (metrics.sleepHours < 6 || metrics.sleepHours > 10) {
          score -= 15;
        } else if (metrics.sleepHours < 7 || metrics.sleepHours > 9) {
          score -= 5;
        }

        // 运动评分
        if (metrics.exerciseMinutes < 150) {
          score -= 15;
        } // WHO推荐每周150分钟

        // 吸烟评分
        if (metrics.smoking) {
          score -= 25;
        }

        return Math.max(0, score);
      };

      const healthyPerson = {
        bmi: 22,
        bloodPressure: { systolic: 115, diastolic: 75 },
        heartRate: 70,
        sleepHours: 8,
        exerciseMinutes: 200,
        smoking: false,
      };

      const unhealthyPerson = {
        bmi: 32,
        bloodPressure: { systolic: 150, diastolic: 95 },
        heartRate: 110,
        sleepHours: 5,
        exerciseMinutes: 50,
        smoking: true,
      };

      expect(calculateHealthScore(healthyPerson)).toBe(100);
      expect(calculateHealthScore(unhealthyPerson)).toBe(0); // 修正期望值，因为最小值是0
    });
  });
});
