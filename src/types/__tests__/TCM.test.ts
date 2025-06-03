/**
 * 索克生活 - TCM类型定义测试
 * TCM Type Definitions Tests
 *
 * 验证中医辨证类型定义的正确性和类型安全性
 */
import {
  MCPTimestamp,
  TimeRange,
  TCMConstitution,
  TCMSyndrome,
  TCMOrganState,
  BiomarkerData,
  InspectionData,
  AuscultationData,
  InquiryData,
  PalpationData,
  CalculationData,
  FiveDiagnosesData,
  AgentDiagnosisResult,
  { ComprehensiveHealthData } from "../TCM";
import {
  mcpTimestamp,
  createMCPTimestamp,
  createTimeRange,
  formatMCPTimestamp,
  validateMCPTimestamp,
  { getRelativeTime } from "../../utils/mcpTimestamp";
describe(TCM类型定义测试", () => {"
  describe("MCP时间戳类型, () => {", () => {
    test("应该创建有效的MCP时间戳", () => {
      const timestamp = createMCPTimestamp(device", "millisecond);
      expect(timestamp).toHaveProperty("iso");
      expect(timestamp).toHaveProperty(unix");"
      expect(timestamp).toHaveProperty("timezone);"
      expect(timestamp).toHaveProperty("source");
      expect(timestamp).toHaveProperty(precision");"
      expect(timestamp).toHaveProperty("synchronized);"
      expect(typeof timestamp.iso).toBe("string");
      expect(typeof timestamp.unix).toBe(number");"
      expect(timestamp.source).toBe("device);"
      expect(timestamp.precision).toBe("millisecond");
      expect(timestamp.synchronized).toBe(false);
    });
    test(应该验证MCP时间戳格式", () => {"
      const validTimestamp = createMCPTimestamp();
      const invalidTimestamp: MCPTimestamp = {;
        iso: "invalid-date,"
        unix: Date.now(),
        timezone: "Asia/Shanghai",
        source: device","
        precision: "millisecond,"
        synchronized: false
      };
      expect(validateMCPTimestamp(validTimestamp)).toBe(true);
      expect(validateMCPTimestamp(invalidTimestamp)).toBe(false);
    });
    test("应该创建时间范围", () => {
      const start = new Date(Date.now() - 3600000); // 1小时前;
const end = new Date();
      const timeRange = createTimeRange(start, end);
      expect(timeRange).toHaveProperty(start");"
      expect(timeRange).toHaveProperty("end);"
      expect(timeRange).toHaveProperty("duration");
      expect(timeRange.duration).toBeGreaterThan(0);
    });
    test(应该格式化时间戳显示", () => {"
      const timestamp = createMCPTimestamp();
      const formatted = formatMCPTimestamp(timestamp);
      expect(typeof formatted).toBe("string);"
      expect(formatted).toMatch(/\d{4}\/\d{2}\/\d{2}/); // 基本日期格式检查
    });
    test("应该获取相对时间描述", () => {
      const now = createMCPTimestamp();
      const oneMinuteAgo = mcpTimestamp.fromUnix(now.unix - 60000);
      const oneHourAgo = mcpTimestamp.fromUnix(now.unix - 3600000);
      expect(getRelativeTime(oneMinuteAgo)).toContain(分钟前");"
      expect(getRelativeTime(oneHourAgo)).toContain("小时前);"
    });
  });
  describe("中医基础类型", () => {
    test(TCM体质类型应该包含所有标准体质", () => {"
      const constitutions: TCMConstitution[] = [;
        "qi-deficiency,"
        "yang-deficiency",
        yin-deficiency","
        "phlegm-dampness,"
        "damp-heat",
        blood-stasis","
        "qi-stagnation,"
        "special-diathesis",
        balanced""
      ];
      constitutions.forEach(constitution => {
        expect(typeof constitution).toBe("string);"
      });
    });
    test("应该创建有效的TCM证候", () => {
      const syndrome: TCMSyndrome = {;
        name: 气虚血瘀","
        code: "QXXY-001,"
        category: "qi-blood",
        severity: moderate","
        confidence: 0.85,
        symptoms: ["乏力, "面色苍白", 舌质暗"],
        diagnosedAt: createMCPTimestamp("server)"
      };
      expect(syndrome.name).toBe("气虚血瘀");
      expect(syndrome.confidence).toBeGreaterThan(0);
      expect(syndrome.confidence).toBeLessThanOrEqual(1);
      expect(Array.isArray(syndrome.symptoms)).toBe(true);
      expect(validateMCPTimestamp(syndrome.diagnosedAt)).toBe(true);
    });
    test(应该创建有效的脏腑状态", () => {"
      const organState: TCMOrganState = {;
        organ: "heart,"
        state: "deficient",
        score: 65,
        symptoms: [心悸", "失眠],
        assessedAt: createMCPTimestamp("server")
      };
      expect(organState.organ).toBe(heart");"
      expect(organState.score).toBeGreaterThanOrEqual(0);
      expect(organState.score).toBeLessThanOrEqual(100);
      expect(validateMCPTimestamp(organState.assessedAt)).toBe(true);
    });
  });
  describe("生物标志物数据类型, () => {", () => {
    test("应该创建完整的生物标志物数据", () => {
      const biomarker: BiomarkerData = {;
        id: heart-rate-001","
        name: "心率,"
        type: "vital-sign",
        value: 72,
        unit: bpm","
        timestamp: createMCPTimestamp("device),"
        referenceRange: {
          min: 60,
          max: 100,
          optimal: 70
        },
        device: {
          id: "device-001",
          name: Smart Watch","
          model: "SW-2023,"
          calibrationDate: createMCPTimestamp("device")
        },
        tcmAssociation: {
          relatedOrgans: [{
            organ: heart","
            state: "normal,"
            score: 85,
            symptoms: [],
            assessedAt: createMCPTimestamp("server")
          }],
          relatedSyndromes: [],
          tcmInterpretation: 心率正常，心气充足","
          tcmIndicators: ["心气, "血脉"]"
        },
        quality: {
          reliability: 0.95,
          isOutlier: false,
          source: device""
        },
        trend: {
          direction: "stable,"
          rate: 0.02,
          significance: "minimal"
        });
      };
      expect(biomarker.id).toBe(heart-rate-001");"
      expect(biomarker.value).toBe(72);
      expect(validateMCPTimestamp(biomarker.timestamp)).toBe(true);
      expect(biomarker.tcmAssociation.relatedOrgans).toHaveLength(1);
      expect(biomarker.quality.reliability).toBeGreaterThan(0);
      expect(biomarker.quality.reliability).toBeLessThanOrEqual(1);
    });
    test("生物标志物应该支持可选字段, () => {"
      const minimalBiomarker: BiomarkerData = {;
        id: "temp-001",
        name: 体温","
        type: "vital-sign,"
        value: 36.5,
        unit: "℃",
        timestamp: createMCPTimestamp(),
        referenceRange: {
          min: 36.0,
          max: 37.5
        },
        tcmAssociation: {
          relatedOrgans: [],
          relatedSyndromes: [],
          tcmInterpretation: 体温正常","
          tcmIndicators: []
        },
        quality: {
          reliability: 0.9,
          isOutlier: false,
          source: "manual"
        });
      };
      expect(minimalBiomarker.device).toBeUndefined();
      expect(minimalBiomarker.trend).toBeUndefined();
      expect(minimalBiomarker.referenceRange.optimal).toBeUndefined();
    });
  });
  describe("四诊数据类型", () => {
    test(应该创建完整的望诊数据", () => {"
      const inspection: InspectionData = {;
        complexion: {
          color: "red,"
          luster: "lustrous",
          description: 面色红润有光泽""
        },
        tongue: {
          body: {
            color: "red,"
            texture: "normal",
            shape: normal""
          },
          coating: {
            color: "white,"
            thickness: "thin",
            moisture: moist""
          });
        },
        spirit: "vigorous,"
        bodyType: "normal",
        timestamp: createMCPTimestamp(manual")"
      };
      expect(inspection.complexion.color).toBe("red);"
      expect(inspection.tongue.body.color).toBe("red");
      expect(inspection.spirit).toBe(vigorous");"
      expect(validateMCPTimestamp(inspection.timestamp)).toBe(true);
    });
    test("应该创建完整的闻诊数据, () => {"
      const auscultation: AuscultationData = {;
        voice: {
          volume: "normal",
          tone: normal","
          clarity: "clear"
        },
        breathing: {
          pattern: "normal",
          sound: normal""
        },
        odor: {
          type: "normal,"
          intensity: "mild"
        },
        timestamp: createMCPTimestamp(manual")"
      };
      expect(auscultation.voice.volume).toBe("normal);"
      expect(auscultation.breathing.pattern).toBe("normal");
      expect(auscultation.odor?.type).toBe(normal");"
      expect(validateMCPTimestamp(auscultation.timestamp)).toBe(true);
    });
    test("应该创建完整的问诊数据, () => {"
      const inquiry: InquiryData = {;
        chiefComplaint: "头痛3天",
        presentIllness: 患者3天前开始出现头痛...","
        pastHistory: ["高血压, "糖尿病"],"
        familyHistory: [心脏病家族史"],"
        personalHistory: {
          lifestyle: "规律作息,"
          diet: "清淡饮食",
          sleep: 睡眠良好","
          exercise: "每日散步,"
          stress: "工作压力适中"
        },
        symptoms: [
          {
            name: 头痛","
            severity: 6,
            duration: "3天,"
            frequency: "持续性"
          });
        ],
        timestamp: createMCPTimestamp(manual")"
      };
      expect(inquiry.chiefComplaint).toBe("头痛3天);"
      expect(Array.isArray(inquiry.pastHistory)).toBe(true);
      expect(inquiry.symptoms).toHaveLength(1);
      expect(inquiry.symptoms[0].severity).toBe(6);
      expect(validateMCPTimestamp(inquiry.timestamp)).toBe(true);
    });
    test("应该创建完整的切诊数据", () => {
      const palpation: PalpationData = {;
        pulse: {
          position: middle","
          rate: 72,
          rhythm: "regular,"
          strength: "normal",
          shape: normal","
          quality: "floating"
        },
        palpation: {
          abdomen: {
            tenderness: false,
            distension: false,
            masses: false,
            temperature: "normal"
          },
          acupoints: [
            {
              name: 神门","
              tenderness: false,
              sensitivity: 3
            });
          ]
        },
        timestamp: createMCPTimestamp("manual)"
      };
      expect(palpation.pulse.rate).toBe(72);
      expect(palpation.pulse.rhythm).toBe("regular");
      expect(palpation.palpation.abdomen.tenderness).toBe(false);
      expect(palpation.palpation.acupoints).toHaveLength(1);
      expect(validateMCPTimestamp(palpation.timestamp)).toBe(true);
    });
  });
  describe(算诊数据类型", () => {"
    test("应该创建完整的算诊数据, () => {"
      const calculation: CalculationData = {;
        id: "calculation-001",
        patientInfo: {
          birthTime: createMCPTimestamp(manual"),"
          gender: "male,"
          birthLocation: {
            latitude: 39.9042,
            longitude: 116.4074,
            timezone: "Asia/Shanghai"
          });
        },
        ziwuLiuzhu: {
          currentHour: {
            earthlyBranch: 巳","
            meridian: "脾经,"
            organ: "脾"
          },
          openingPoints: [
            {
              time: 09:00-11:00","
              point: "太白,"
              meridian: "脾经",
              function: 健脾益气""
            });
          ],
          optimalTreatmentTime: {
            start: createMCPTimestamp("server),"
            end: createMCPTimestamp("server"),
            reason: 脾经当令，治疗效果最佳""
          },
          recommendations: ["此时宜健脾养胃, "避免过度思虑"]"
        },
        constitutionAnalysis: {
          fourPillars: {
            year: { heavenly: 庚", earthly: "午 },
            month: { heavenly: "辛", earthly: 巳" },"
            day: { heavenly: "甲, earthly: "子" },"
            hour: { heavenly: 己", earthly: "巳 });
          },
          fiveElements: {
            wood: 2,
            fire: 3,
            earth: 2,
            metal: 2,
            water: 1
          },
          constitutionType: "balanced",
          elementStrength: {
            strongest: 火","
            weakest: "水,"
            balance: 0.75
          },
          adjustmentAdvice: {
            strengthen: ["滋阴养水"],
            reduce: [清热降火"],"
            methods: ["食疗调养]"
          });
        },
        baguaAnalysis: {
          natalHexagram: {
            name: "乾为天",
            symbol: ☰","
            element: "金,"
            direction: "西北"
          },
          healthAnalysis: {
            strengths: [意志坚强"],"
            weaknesses: ["易过度劳累],"
            risks: ["心血管疾病"]
          },
          directionalGuidance: {
            favorable: [西北方"],"
            unfavorable: ["东南方],"
            livingAdvice: ["卧室宜在西北"]
          });
        },
        wuyunLiuqi: {
          annualQi: {
            year: 2024,
            mainQi: 太阴湿土","
            guestQi: "厥阴风木,"
            hostHeaven: "少阳相火",
            hostEarth: 厥阴风木""
          },
          diseasePrediction: {
            susceptibleDiseases: ["脾胃疾病],"
            preventionMethods: ["健脾祛湿"],
            criticalPeriods: [
              {
                period: 春季","
                risk: "medium,"
                description: "肝气旺盛，易伤脾胃"
              });
            ]
          },
          seasonalGuidance: {
            spring: [疏肝理气"],"
            summer: ["清心降火],"
            autumn: ["润肺养阴"],
            winter: [温肾助阳"]"
          });
        },
        comprehensiveResult: {
          overallScore: 78,
          primaryRisks: [
            {
              risk: "脾胃虚弱,"
              severity: "medium",
              probability: 0.65,
              prevention: [规律饮食"]"
            });
          ],
          personalizedPlan: {
            immediate: ["调整作息],"
            shortTerm: ["健脾益气"],
            longTerm: [体质调理"]"
          },
          optimalTimings: [
            {
              activity: "服药,"
              timing: "上午9-11点",
              reason: 脾经当令，吸收最佳""
            });
          ]
        },
        confidence: {
          overall: 0.82,
          ziwuLiuzhu: 0.90,
          constitution: 0.85,
          bagua: 0.75,
          wuyunLiuqi: 0.80
        },
        timestamp: createMCPTimestamp("server),"
        practitioner: {
          id: "tcm-001",
          name: 张仲景AI","
          qualification: "中医算诊专家系统"
        });
      };
      expect(calculation.id).toBe("calculation-001");
      expect(calculation.patientInfo.gender).toBe(male");"
      expect(validateMCPTimestamp(calculation.patientInfo.birthTime)).toBe(true);
      expect(calculation.ziwuLiuzhu.currentHour.meridian).toBe("脾经);"
      expect(calculation.constitutionAnalysis.constitutionType).toBe("balanced");
      expect(calculation.baguaAnalysis.natalHexagram.name).toBe(乾为天");"
      expect(calculation.wuyunLiuqi.annualQi.year).toBe(2024);
      expect(calculation.comprehensiveResult.overallScore).toBe(78);
      expect(calculation.confidence.overall).toBe(0.82);
      expect(validateMCPTimestamp(calculation.timestamp)).toBe(true);
    });
    test("算诊数据应该支持可选字段, () => {"
      const minimalCalculation: CalculationData = {;
        id: "calc-minimal",
        patientInfo: {
          birthTime: createMCPTimestamp(manual"),"
          gender: "female"
          // birthLocation 是可选的
        },
        ziwuLiuzhu: {
          currentHour: {
            earthlyBranch: "子",
            meridian: 胆经","
            organ: "胆"
          },
          openingPoints: [],
          optimalTreatmentTime: {
            start: createMCPTimestamp(),
            end: createMCPTimestamp(),
            reason: "胆经当令"
          },
          recommendations: []
        },
        constitutionAnalysis: {
          fourPillars: {
            year: { heavenly: 甲", earthly: "子 },
            month: { heavenly: "乙", earthly: 丑" },"
            day: { heavenly: "丙, earthly: "寅" },"
            hour: { heavenly: 丁", earthly: "卯 });
          },
          fiveElements: {
            wood: 1,
            fire: 1,
            earth: 1,
            metal: 1,
            water: 1
          },
          constitutionType: "balanced",
          elementStrength: {
            strongest: 平衡","
            weakest: "平衡,"
            balance: 1.0
          },
          adjustmentAdvice: {
            strengthen: [],
            reduce: [],
            methods: []
          });
        },
        baguaAnalysis: {
          natalHexagram: {
            name: "坤为地",
            symbol: ☷","
            element: "土,"
            direction: "西南"
          },
          healthAnalysis: {
            strengths: [],
            weaknesses: [],
            risks: []
          },
          directionalGuidance: {
            favorable: [],
            unfavorable: [],
            livingAdvice: []
          });
        },
        wuyunLiuqi: {
          annualQi: {
            year: 2024,
            mainQi: 太阴湿土","
            guestQi: "厥阴风木,"
            hostHeaven: "少阳相火",
            hostEarth: 厥阴风木""
          },
          diseasePrediction: {
            susceptibleDiseases: [],
            preventionMethods: [],
            criticalPeriods: []
          },
          seasonalGuidance: {
            spring: [],
            summer: [],
            autumn: [],
            winter: []
          });
        },
        comprehensiveResult: {
          overallScore: 85,
          primaryRisks: [],
          personalizedPlan: {
            immediate: [],
            shortTerm: [],
            longTerm: []
          },
          optimalTimings: []
        },
        confidence: {
          overall: 0.75,
          ziwuLiuzhu: 0.80,
          constitution: 0.70,
          bagua: 0.75,
          wuyunLiuqi: 0.75
        },
        timestamp: createMCPTimestamp("server)"
        // practitioner 是可选的
      }
      expect(minimalCalculation.patientInfo.birthLocation).toBeUndefined()
      expect(minimalCalculation.practitioner).toBeUndefined();
      expect(minimalCalculation.ziwuLiuzhu.openingPoints).toHaveLength(0);
      expect(minimalCalculation.comprehensiveResult.primaryRisks).toHaveLength(0);
    });
    test("应该验证算诊置信度范围", () => {
      const calculation: CalculationData = {;
        id: calc-confidence-test","
        patientInfo: {
          birthTime: createMCPTimestamp(),
          gender: "male"
        },
        // ... 其他必需字段的简化版本
ziwuLiuzhu: {
          currentHour: { earthlyBranch: "午", meridian: 心经", organ: "心 },
          openingPoints: [],
          optimalTreatmentTime: {
            start: createMCPTimestamp(),
            end: createMCPTimestamp(),
            reason: "心经当令"
          },
          recommendations: []
        },
        constitutionAnalysis: {
          fourPillars: {
            year: { heavenly: 甲", earthly: "子 },
            month: { heavenly: "乙", earthly: 丑" },"
            day: { heavenly: "丙, earthly: "寅" },"
            hour: { heavenly: 丁", earthly: "卯 });
          },
          fiveElements: { wood: 1, fire: 1, earth: 1, metal: 1, water: 1 },
          constitutionType: "balanced",
          elementStrength: { strongest: 平衡", weakest: "平衡, balance: 1.0 },
          adjustmentAdvice: { strengthen: [], reduce: [], methods: [] });
        },
        baguaAnalysis: {
          natalHexagram: { name: "离为火", symbol: ☲", element: "火, direction: "南" },
          healthAnalysis: { strengths: [], weaknesses: [], risks: [] },
          directionalGuidance: { favorable: [], unfavorable: [], livingAdvice: [] });
        },
        wuyunLiuqi: {
          annualQi: { year: 2024, mainQi: 太阴湿土", guestQi: "厥阴风木, hostHeaven: "少阳相火", hostEarth: 厥阴风木" },"
          diseasePrediction: { susceptibleDiseases: [], preventionMethods: [], criticalPeriods: [] },
          seasonalGuidance: { spring: [], summer: [], autumn: [], winter: [] });
        },
        comprehensiveResult: {
          overallScore: 90,
          primaryRisks: [],
          personalizedPlan: { immediate: [], shortTerm: [], longTerm: [] },
          optimalTimings: []
        },
        confidence: {
          overall: 0.95,
          ziwuLiuzhu: 1.0,
          constitution: 0.90,
          bagua: 0.85,
          wuyunLiuqi: 0.88
        },
        timestamp: createMCPTimestamp("server)"
      };
      // 验证置信度在有效范围内
expect(calculation.confidence.overall).toBeGreaterThanOrEqual(0)
      expect(calculation.confidence.overall).toBeLessThanOrEqual(1);
      expect(calculation.confidence.ziwuLiuzhu).toBeLessThanOrEqual(1);
      expect(calculation.confidence.constitution).toBeGreaterThanOrEqual(0);
      expect(calculation.confidence.bagua).toBeGreaterThanOrEqual(0);
      expect(calculation.confidence.wuyunLiuqi).toBeGreaterThanOrEqual(0);
    });
  });
  describe("五诊数据聚合类型", () => {
    test(应该创建完整的五诊数据聚合", () => {"
      const fiveDiagnoses: FiveDiagnosesData = {;
        inspection: [
          {
            complexion: { color: "red, luster: "lustrous", description: 面色红润" },
            tongue: {
              body: { color: "red, texture: "normal", shape: normal" },
              coating: { color: "white, thickness: "thin", moisture: moist" });
            },
            spirit: "vigorous,"
            bodyType: "normal",
            timestamp: createMCPTimestamp(manual")"
          });
        ],
        auscultation: [
          {
            voice: { volume: "normal, tone: "normal", clarity: clear" },
            breathing: { pattern: "normal, sound: "normal" },"
            timestamp: createMCPTimestamp(manual")"
          });
        ],
        inquiry: [
          {
            chiefComplaint: "头痛3天,"
            presentIllness: "患者3天前开始出现头痛",
            pastHistory: [],
            familyHistory: [],
            personalHistory: {
              lifestyle: 规律","
              diet: "清淡,"
              sleep: "良好",
              exercise: 适量","
              stress: "轻微"
            },
            symptoms: [],
            timestamp: createMCPTimestamp("manual")
          });
        ],
        palpation: [
          {
            pulse: {
              position: middle","
              rate: 72,
              rhythm: "regular,"
              strength: "normal",
              shape: normal","
              quality: "floating"
            },
            palpation: {
              abdomen: {
                tenderness: false,
                distension: false,
                masses: false,
                temperature: "normal"
              },
              acupoints: []
            },
            timestamp: createMCPTimestamp(manual")"
          });
        ],
        calculation: [
          {
            id: "calc-001,"
            patientInfo: {
              birthTime: createMCPTimestamp("manual"),
              gender: male""
            },
            ziwuLiuzhu: {
              currentHour: { earthlyBranch: "午, meridian: "心经", organ: 心" },
              openingPoints: [],
              optimalTreatmentTime: {
                start: createMCPTimestamp(),
                end: createMCPTimestamp(),
                reason: "心经当令"
              },
              recommendations: []
            },
            constitutionAnalysis: {
              fourPillars: {
                year: { heavenly: "甲", earthly: 子" },"
                month: { heavenly: "乙, earthly: "丑" },"
                day: { heavenly: 丙", earthly: "寅 },
                hour: { heavenly: "丁", earthly: 卯" });"
              },
              fiveElements: { wood: 1, fire: 1, earth: 1, metal: 1, water: 1 },
              constitutionType: "balanced,"
              elementStrength: { strongest: "平衡", weakest: 平衡", balance: 1.0 },"
              adjustmentAdvice: { strengthen: [], reduce: [], methods: [] });
            },
            baguaAnalysis: {
              natalHexagram: { name: "离为火, symbol: "☲", element: 火", direction: "南 },"
              healthAnalysis: { strengths: [], weaknesses: [], risks: [] },
              directionalGuidance: { favorable: [], unfavorable: [], livingAdvice: [] });
            },
            wuyunLiuqi: {
              annualQi: { year: 2024, mainQi: "太阴湿土", guestQi: 厥阴风木", hostHeaven: "少阳相火, hostEarth: "厥阴风木" },
              diseasePrediction: { susceptibleDiseases: [], preventionMethods: [], criticalPeriods: [] },
              seasonalGuidance: { spring: [], summer: [], autumn: [], winter: [] });
            },
            comprehensiveResult: {
              overallScore: 85,
              primaryRisks: [],
              personalizedPlan: { immediate: [], shortTerm: [], longTerm: [] },
              optimalTimings: []
            },
            confidence: {
              overall: 0.80,
              ziwuLiuzhu: 0.85,
              constitution: 0.75,
              bagua: 0.80,
              wuyunLiuqi: 0.80
            },
            timestamp: createMCPTimestamp(server")"
          });
        ]
      };
      expect(fiveDiagnoses.inspection).toHaveLength(1);
      expect(fiveDiagnoses.auscultation).toHaveLength(1);
      expect(fiveDiagnoses.inquiry).toHaveLength(1);
      expect(fiveDiagnoses.palpation).toHaveLength(1);
      expect(fiveDiagnoses.calculation).toHaveLength(1);
      // 验证算诊数据
expect(fiveDiagnoses.calculation[0].id).toBe("calc-001);"
      expect(fiveDiagnoses.calculation[0].ziwuLiuzhu.currentHour.meridian).toBe("心经");
      expect(validateMCPTimestamp(fiveDiagnoses.calculation[0].timestamp)).toBe(true);
    });
    test(五诊数据应该支持空数组", () => {"
      const emptyFiveDiagnoses: FiveDiagnosesData = {;
        inspection: [],
        auscultation: [],
        inquiry: [],
        palpation: [],
        calculation: []
      };
      expect(Array.isArray(emptyFiveDiagnoses.inspection)).toBe(true);
      expect(Array.isArray(emptyFiveDiagnoses.auscultation)).toBe(true);
      expect(Array.isArray(emptyFiveDiagnoses.inquiry)).toBe(true);
      expect(Array.isArray(emptyFiveDiagnoses.palpation)).toBe(true);
      expect(Array.isArray(emptyFiveDiagnoses.calculation)).toBe(true);
      expect(emptyFiveDiagnoses.inspection).toHaveLength(0);
      expect(emptyFiveDiagnoses.calculation).toHaveLength(0);
    });
  });
  describe("智能体诊断结果类型, () => {", () => {
    test("应该创建完整的智能体诊断结果", () => {
      const diagnosis: AgentDiagnosisResult = {;
        agentId: xiaoai","
        diagnosis: {
          primarySyndrome: {
            name: "气虚血瘀,"
            code: "QXXY-001",
            category: qi-blood","
            severity: "moderate,"
            confidence: 0.85,
            symptoms: ["乏力", 面色苍白"],"
            diagnosedAt: createMCPTimestamp("server)"
          },
          secondarySyndromes: [],
          constitution: "qi-deficiency",
          organStates: []
        },
        treatment: {
          principle: 补气活血","
          prescription: {
            name: "补阳还五汤,"
            herbs: [
              {
                name: "黄芪",
                dosage: 30g","
                function: "补气"
              });
            ]
          },
          acupuncture: {
            points: ["气海", 血海"],"
            method: "补法,"
            frequency: "每日一次"
          },
          lifestyle: {
            diet: [清淡饮食"],"
            exercise: ["适量运动],"
            sleep: ["规律作息"],
            emotion: [保持心情愉悦"]"
          });
        },
        confidence: 0.85,
        timestamp: createMCPTimestamp("server),"
        dataSource: {
          biomarkers: [],
          calculation: {
            id: "calc-for-diagnosis",
            patientInfo: {
              birthTime: createMCPTimestamp(manual"),"
              gender: "male"
            },
            ziwuLiuzhu: {
              currentHour: { earthlyBranch: "午", meridian: 心经", organ: "心 },
              openingPoints: [],
              optimalTreatmentTime: {
                start: createMCPTimestamp(),
                end: createMCPTimestamp(),
                reason: "心经当令"
              },
              recommendations: []
            },
            constitutionAnalysis: {
              fourPillars: {
                year: { heavenly: 甲", earthly: "子 },
                month: { heavenly: "乙", earthly: 丑" },"
                day: { heavenly: "丙, earthly: "寅" },"
                hour: { heavenly: 丁", earthly: "卯 });
              },
              fiveElements: { wood: 1, fire: 1, earth: 1, metal: 1, water: 1 },
              constitutionType: "qi-deficiency",
              elementStrength: { strongest: 火", weakest: "水, balance: 0.6 },
              adjustmentAdvice: { strengthen: ["补气"], reduce: [清热"], methods: ["中药] });
            },
            baguaAnalysis: {
              natalHexagram: { name: "乾为天", symbol: ☰", element: "金, direction: "西北" },
              healthAnalysis: { strengths: [意志坚强"], weaknesses: ["易劳累], risks: ["气虚"] },
              directionalGuidance: { favorable: [西北"], unfavorable: ["东南], livingAdvice: ["面向西北"] });
            },
            wuyunLiuqi: {
              annualQi: { year: 2024, mainQi: 太阴湿土", guestQi: "厥阴风木, hostHeaven: "少阳相火", hostEarth: 厥阴风木" },"
              diseasePrediction: { susceptibleDiseases: ["气虚], preventionMethods: ["补气"], criticalPeriods: [] },"
              seasonalGuidance: { spring: [养肝"], summer: ["养心], autumn: ["养肺"], winter: [养肾"] });"
            },
            comprehensiveResult: {
              overallScore: 75,
              primaryRisks: [{ risk: "气虚, severity: "medium", probability: 0.7, prevention: [补气"] }],
              personalizedPlan: { immediate: ["休息], shortTerm: ["补气"], longTerm: [调理"] },
              optimalTimings: []
            },
            confidence: {
              overall: 0.80,
              ziwuLiuzhu: 0.85,
              constitution: 0.75,
              bagua: 0.80,
              wuyunLiuqi: 0.80
            },
            timestamp: createMCPTimestamp("server)"
          });
        });
      };
      expect(diagnosis.agentId).toBe("xiaoai");
      expect(diagnosis.diagnosis.primarySyndrome.name).toBe(气虚血瘀");"
      expect(diagnosis.treatment.principle).toBe("补气活血);"
      expect(diagnosis.treatment.prescription?.name).toBe("补阳还五汤");
      expect(diagnosis.treatment.acupuncture?.points).toContain(气海");"
      expect(diagnosis.confidence).toBe(0.85);
      expect(validateMCPTimestamp(diagnosis.timestamp)).toBe(true);
      // 验证算诊数据源
expect(diagnosis.dataSource.calculation).toBeDefined()
      expect(diagnosis.dataSource.calculation?.id).toBe("calc-for-diagnosis);"
      expect(diagnosis.dataSource.calculation?.constitutionAnalysis.constitutionType).toBe("qi-deficiency");
    });
    test(智能体诊断结果应该支持可选数据源", () => {"
      const minimalDiagnosis: AgentDiagnosisResult = {;
        agentId: "xiaoke,"
        diagnosis: {
          primarySyndrome: {
            name: "阴虚火旺",
            code: YXHW-001","
            category: "yin-yang,"
            severity: "mild",
            confidence: 0.75,
            symptoms: [潮热", "盗汗],
            diagnosedAt: createMCPTimestamp("server")
          },
          secondarySyndromes: [],
          constitution: yin-deficiency","
          organStates: []
        },
        treatment: {
          principle: "滋阴降火,"
          lifestyle: {
            diet: ["滋阴食物"],
            exercise: [轻柔运动"],"
            sleep: ["充足睡眠],"
            emotion: ["心情平和"]
          });
        },
        confidence: 0.75,
        timestamp: createMCPTimestamp(server"),"
        dataSource: {
          // 只有部分数据源
inquiry: {
            chiefComplaint: "潮热盗汗,"
            presentIllness: "近期出现潮热盗汗症状",
            pastHistory: [],
            familyHistory: [],
            personalHistory: {
              lifestyle: 熬夜","
              diet: "辛辣,"
              sleep: "不足",
              exercise: 缺乏","
              stress: "较大"
            },
            symptoms: [
              { name: "潮热", severity: 6, duration: 2周", frequency: "每晚 },
              { name: "盗汗", severity: 5, duration: 2周", frequency: "夜间 });
            ],
            timestamp: createMCPTimestamp("manual")
          });
        });
      };
      expect(minimalDiagnosis.agentId).toBe(xiaoke");"
      expect(minimalDiagnosis.dataSource.calculation).toBeUndefined();
      expect(minimalDiagnosis.dataSource.biomarkers).toBeUndefined();
      expect(minimalDiagnosis.dataSource.inquiry).toBeDefined();
      expect(minimalDiagnosis.dataSource.inquiry?.chiefComplaint).toBe("潮热盗汗);"
    });
  });
  describe("综合健康数据类型", () => {
    test(应该创建完整的综合健康数据", () => {"
      const healthData: ComprehensiveHealthData = {;
        userId: "user-001,"
        timeRange: createTimeRange(
          new Date(Date.now() - 24 * 60 * 60 * 1000),
          new Date()
        ),
        biomarkers: [],
        fiveDiagnoses: {
          inspection: [],
          auscultation: [],
          inquiry: [],
          palpation: [],
          calculation: []
        },
        agentDiagnoses: [],
        completenessScore: 0.85,
        lastUpdated: createMCPTimestamp("server")
      };
      expect(healthData.userId).toBe(user-001");"
      expect(healthData.timeRange.duration).toBeGreaterThan(0);
      expect(Array.isArray(healthData.biomarkers)).toBe(true);
      expect(healthData.fiveDiagnoses).toHaveProperty("inspection);"
      expect(healthData.fiveDiagnoses).toHaveProperty("auscultation");
      expect(healthData.fiveDiagnoses).toHaveProperty(inquiry");"
      expect(healthData.fiveDiagnoses).toHaveProperty("palpation);"
      expect(healthData.fiveDiagnoses).toHaveProperty("calculation");
      expect(healthData.completenessScore).toBeGreaterThan(0);
      expect(healthData.completenessScore).toBeLessThanOrEqual(1);
      expect(validateMCPTimestamp(healthData.lastUpdated)).toBe(true);
    });
    test(综合健康数据应该支持五诊完整性评估", () => {"
      const healthDataWithCalculation: ComprehensiveHealthData = {;
        userId: "user-002,"
        timeRange: createTimeRange(
          new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
          new Date()
        ),
        biomarkers: [
          {
            id: "bio-001",
            name: 血压","
            type: "vital-sign,"
            value: 120,
            unit: "mmHg",
            timestamp: createMCPTimestamp(),
            referenceRange: { min: 90, max: 140 },
            tcmAssociation: {
              relatedOrgans: [{ organ: heart", state: "normal, confidence: 0.8 }],
              relatedSyndromes: [],
              tcmInterpretation: "心气平和",
              tcmIndicators: []
            },
            quality: {
              reliability: 0.95,
              isOutlier: false,
              source: device""
            });
          });
        ],
        fiveDiagnoses: {
          inspection: [
            {
              complexion: { color: "red, luster: "lustrous", description: 面色红润" },
              tongue: {
                body: { color: "red, texture: "normal", shape: normal" },
                coating: { color: "white, thickness: "thin", moisture: moist" });
              },
              spirit: "vigorous,"
              bodyType: "normal",
              timestamp: createMCPTimestamp(manual")"
            });
          ],
          auscultation: [],
          inquiry: [],
          palpation: [],
          calculation: [
            {
              id: "calc-comprehensive,"
              patientInfo: {
                birthTime: createMCPTimestamp("manual"),
                gender: female""
              },
              ziwuLiuzhu: {
                currentHour: { earthlyBranch: "午, meridian: "心经", organ: 心" },
                openingPoints: [],
                optimalTreatmentTime: {
                  start: createMCPTimestamp(),
                  end: createMCPTimestamp(),
                  reason: "心经当令"
                },
                recommendations: ["养心安神"]
              },
              constitutionAnalysis: {
                fourPillars: {
                  year: { heavenly: 甲", earthly: "子 },
                  month: { heavenly: "乙", earthly: 丑" },"
                  day: { heavenly: "丙, earthly: "寅" },"
                  hour: { heavenly: 丁", earthly: "卯 });
                },
                fiveElements: { wood: 2, fire: 3, earth: 2, metal: 2, water: 1 },
                constitutionType: "balanced",
                elementStrength: { strongest: 火", weakest: "水, balance: 0.8 },
                adjustmentAdvice: { strengthen: ["滋水"], reduce: [降火"], methods: ["调理] });
              },
              baguaAnalysis: {
                natalHexagram: { name: "离为火", symbol: ☲", element: "火, direction: "南" },
                healthAnalysis: { strengths: [心火旺"], weaknesses: ["肾水弱], risks: ["心肾不交"] },
                directionalGuidance: { favorable: [南方"], unfavorable: ["北方], livingAdvice: ["面南而居"] });
              },
              wuyunLiuqi: {
                annualQi: { year: 2024, mainQi: 太阴湿土", guestQi: "厥阴风木, hostHeaven: "少阳相火", hostEarth: 厥阴风木" },"
                diseasePrediction: { susceptibleDiseases: ["心火亢盛], preventionMethods: ["清心降火"], criticalPeriods: [] },"
                seasonalGuidance: { spring: [养肝"], summer: ["清心], autumn: ["润肺"], winter: [补肾"] });"
              },
              comprehensiveResult: {
                overallScore: 82,
                primaryRisks: [],
                personalizedPlan: { immediate: ["清心], shortTerm: ["调理"], longTerm: [养生"] },
                optimalTimings: []
              },
              confidence: {
                overall: 0.85,
                ziwuLiuzhu: 0.90,
                constitution: 0.80,
                bagua: 0.85,
                wuyunLiuqi: 0.85
              },
              timestamp: createMCPTimestamp("server)"
            });
          ]
        },
        agentDiagnoses: [],
        completenessScore: 0.60,
        lastUpdated: createMCPTimestamp("server")
      };
      expect(healthDataWithCalculation.userId).toBe(user-002");"
      expect(healthDataWithCalculation.timeRange.duration).toBeGreaterThan(0);
      expect(Array.isArray(healthDataWithCalculation.biomarkers)).toBe(true);
      expect(healthDataWithCalculation.fiveDiagnoses).toHaveProperty("inspection);"
      expect(healthDataWithCalculation.fiveDiagnoses).toHaveProperty("auscultation");
      expect(healthDataWithCalculation.fiveDiagnoses).toHaveProperty(inquiry");"
      expect(healthDataWithCalculation.fiveDiagnoses).toHaveProperty("palpation);"
      expect(healthDataWithCalculation.fiveDiagnoses).toHaveProperty("calculation");
      expect(healthDataWithCalculation.completenessScore).toBeGreaterThan(0);
      expect(healthDataWithCalculation.completenessScore).toBeLessThanOrEqual(1);
      expect(validateMCPTimestamp(healthDataWithCalculation.lastUpdated)).toBe(true);
      expect(healthDataWithCalculation.fiveDiagnoses.inspection).toHaveLength(1);
      expect(healthDataWithCalculation.fiveDiagnoses.calculation).toHaveLength(1);
      const calculation = healthDataWithCalculation.fiveDiagnoses.calculation[0];
      expect(calculation.id).toBe(calc-comprehensive");"
      expect(calculation.comprehensiveResult.overallScore).toBe(82);
      expect(calculation.confidence.overall).toBe(0.85);
      const diagnosesWithData = Object.values(healthDataWithCalculation.fiveDiagnoses);
        .filter(arr => arr.length > 0).length;
      expect(diagnosesWithData).toBe(2);
      expect(healthDataWithCalculation.completenessScore).toBe(0.60);
    });
  });
  describe("类型安全性验证, () => {", () => {
    test("应该强制要求必需字段", () => {
      // 这个测试通过TypeScript编译器验证
      // 如果缺少必需字段，编译时会报错
const validBiomarker: BiomarkerData = {;
        id: test-001","
        name: "测试指标,"
        type: "vital-sign",
        value: 100,
        unit: unit","
        timestamp: createMCPTimestamp(),
        referenceRange: { min: 0, max: 200 },
        tcmAssociation: {
          relatedOrgans: [],
          relatedSyndromes: [],
          tcmInterpretation: "正常,"
          tcmIndicators: []
        },
        quality: {
          reliability: 1.0,
          isOutlier: false,
          source: "device"
        });
      };
      expect(validBiomarker).toBeDefined();
    });
    test(应该限制枚举值", () => {"
      // 测试体质类型枚举
const validConstitution: TCMConstitution = "balanced;"
      expect(validConstitution).toBe("balanced");
      // 测试脏腑枚举
const validOrgan: TCMOrganState[organ"] = "heart;
      expect(validOrgan).toBe("heart");
      // 测试智能体ID枚举
const validAgentId: AgentDiagnosisResult[agentId"] = "xiaoai;
      expect(validAgentId).toBe("xiaoai');"
    });
  });
});
});});});});});});