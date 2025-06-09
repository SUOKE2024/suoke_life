import {import {import {import { colors, spacing, typography } from "../../placeholder";../../constants/    theme;
/**
* * 索克生活 - 增强健康仪表板组件
* Enhanced Health Dashboard Component;
//
* 集成中医辨证关联字段和智能体诊断结果
import React, { useState, useEffect, useMemo } from "react";
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Alert,
  { TouchableOpacity } from "../../placeholder";react-native;
  BiomarkerData,
  MCPTimestamp,
  TCMSyndrome,
  AgentDiagnosisResult,
  ComprehensiveHealthData,
  CalculationData,
  { FiveDiagnosesData } from ../../types/    TCM;
  mcpTimestamp,
  formatMCPTimestamp,
  getRelativeTime,
  { validateMCPTimestamp } from "../../utils/    mcpTimestamp";
interface EnhancedHealthDashboardProps {
  userId: string;
  onBiomarkerPress?: (biomarker: BiomarkerData) => void;
  onSyndromePress?: (syndrome: TCMSyndrome) => void;
  onAgentDiagnosisPress?: (diagnosis: AgentDiagnosisResult) => void;
  onCalculationPress?: (calculation: CalculationData) => void;
}
/**
* * 增强健康仪表板组件
export const EnhancedHealthDashboard: React.FC<EnhancedHealthDashboardProps>  = ({
  userId,
  onBiomarkerPress,
  onSyndromePress,onAgentDiagnosisPress,onCalculationPress;
}) => {}
  const [healthData, setHealthData] = useState<ComprehensiveHealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  // 模拟数据加载
const loadHealthData = async() => {}
    try {// 创建示例生物标志物数据
const sampleBiomarkers: BiomarkerData[] = [;
        {
          id: heart-rate-001",
          name: "心率,",
          type: "vital-sign",
          value: 72,
          unit: bpm",
          timestamp: mcpTimestamp.now("device, "millisecond"),"
          referenceRange: {,
  min: 60,
            max: 100,
            optimal: 70;
          },
          device: {,
  id: smartwatch-001",
            name: "Apple Watch Series 8,",
            model: "A2473",
            calibrationDate: mcpTimestamp.fromDate(new Date(Date.now() - 7 * 24 * 60 * 60 * 1000))
          },
          tcmAssociation: {,
  relatedOrgans: [{
              organ: heart",
              state: "normal,",
              score: 85,
              symptoms: [],
              assessedAt: mcpTimestamp.now("server");
            }],
            relatedSyndromes: [],
            tcmInterpretation: 心率正常，心气充足，血脉运行顺畅",
            tcmIndicators: ["心气, "血脉"]"
          },
          quality: {,
  reliability: 0.95,
            isOutlier: false,
            source: device""
          },
          trend: {,
  direction: "stable,",
            rate: 0.02,
            significance: "minimal"
          }
        },
        {
          id: blood-pressure-001",
          name: "血压,",
          type: "vital-sign",
          value: 120, // 收缩压
unit: mmHg",
          timestamp: mcpTimestamp.now("device, "millisecond"),"
          referenceRange: {,
  min: 90,
            max: 140,
            optimal: 120;
          },
          tcmAssociation: {,
  relatedOrgans: [{
              organ: heart",
              state: "normal,",
              score: 88,
              symptoms: [],
              assessedAt: mcpTimestamp.now("server");
            }, {
              organ: liver",
              state: "normal,",
              score: 82,
              symptoms: [],
              assessedAt: mcpTimestamp.now("server");
            }],
            relatedSyndromes: [],
            tcmInterpretation: 血压正常，心肝功能协调，气血运行平稳",
            tcmIndicators: ["心气, "肝气", " 血脉"]
          },
          quality: {,
  reliability: 0.92,
            isOutlier: false,
            source: "device"
          }
        }
      ];
      // 创建示例算诊数据
const sampleCalculation: CalculationData = {,
  id: "calculation-001",
      patientInfo: {,
  birthTime: mcpTimestamp.fromDate(new Date(1990-05-15T08:30:00Z")),"
          gender: "male,",
          birthLocation: {,
  latitude: 39.9042,
            longitude: 116.4074,
            timezone: "Asia/    Shanghai"
          }
        },
        ziwuLiuzhu: {,
  currentHour: {
            earthlyBranch: 巳",
            meridian: "脾经,",
            organ: "脾"
          },
          openingPoints: [
            {
              time: 09:00-11:00",
              point: "太白,",
              meridian: "脾经", "
              function: 健脾益气""
            }
          ],
          optimalTreatmentTime: {,
  start: mcpTimestamp.fromDate(new Date(Date.now() + 2 * 60 * 60 * 1000)),
            end: mcpTimestamp.fromDate(new Date(Date.now() + 4 * 60 * 60 * 1000)),
            reason: "脾经当令，治疗效果最佳"
          },
          recommendations: ["此时宜健脾养胃", " 避免过度思虑", "适量运动]
        },
        constitutionAnalysis: {,
  fourPillars: {
            year: {,
  heavenly: "庚", "
      earthly: 午" },"
            month: { heavenly: "辛, earthly: "巳" },"
            day: { heavenly: 甲", earthly: "子 },
            hour: {,
  heavenly: "己", "
      earthly: 巳" }"
          },
          fiveElements: {,
  wood: 2,
            fire: 3,
            earth: 2,
            metal: 2,
            water: 1;
          },
          constitutionType: "balanced,",
          elementStrength: {,
  strongest: "火", "
            weakest: 水",
            balance: 0.75;
          },
          adjustmentAdvice: {,
  strengthen: ["滋阴养水, "润燥生津"],"
            reduce: [清热降火", "平肝潜阳],
            methods: ["食疗调养", " 作息规律", "情志调节]
          }
        },
        baguaAnalysis: {,
  natalHexagram: {
      name: "乾为天",
      symbol: ☰",
            element: "金,",
            direction: "西北"
          },
          healthAnalysis: {,
  strengths: [意志坚强", "领导能力, "抗压能力强"],
            weaknesses: [易过度劳累", "情绪紧张, "肝气郁结"],
            risks: [心血管疾病", "高血压, "失眠"]
          },
          directionalGuidance: {,
  favorable: [西北方", "正西方],
            unfavorable: ["东南方", " 正南方"],"
            livingAdvice: ["卧室宜在西北, "办公桌面向西北", " 多到西北方活动"]
          }
        },
        wuyunLiuqi: {,
  annualQi: {
            year: 2024,
            mainQi: "太阴湿土,",
            guestQi: "厥阴风木", "
            hostHeaven: 少阳相火",
            hostEarth: "厥阴风木"
          },
          diseasePrediction: {,
  susceptibleDiseases: ["脾胃疾病", " 湿邪困脾", "肝郁脾虚],
            preventionMethods: ["健脾祛湿", " 疏肝理气", "调节情志],
            criticalPeriods: [
              {
      period: "春季",
      risk: medium",
                description: "肝气旺盛，易伤脾胃"
              },
              {
      period: "长夏",
      risk: high",
                description: "湿邪当令，脾胃最易受损"
              }
            ]
          },
          seasonalGuidance: {,
  spring: ["疏肝理气", " 少酸多甘", "适量运动],
            summer: ["清心降火", " 养心安神", "避免贪凉],
            autumn: ["润肺养阴", " 收敛神气", "早睡早起],
            winter: ["温肾助阳", " 藏精纳气", "避寒就温]
          }
        },
        comprehensiveResult: {,
  overallScore: 78,
          primaryRisks: [
            {
      risk: "脾胃虚弱",
      severity: medium",
              probability: 0.65,
              prevention: ["规律饮食, "健脾食疗", " 适量运动"]
            }
          ],
          personalizedPlan: {,
  immediate: ["调整作息, "清淡饮食", " 情志调节"],
            shortTerm: ["健脾益气, "疏肝理气", " 规律运动"],
            longTerm: ["体质调理, "预防保健", " 定期检查"]
          },
          optimalTimings: [
            {
      activity: "服药,",
      timing: "上午9-11点", "
              reason: 脾经当令，吸收最佳""
            },
            {
      activity: "运动,",
      timing: "下午3-5点", "
              reason: 膀胱经当令，利于排毒""
            }
          ]
        },
        confidence: {,
  overall: 0.82,
          ziwuLiuzhu: 0.90,
          constitution: 0.85,
          bagua: 0.75,
          wuyunLiuqi: 0.80;
        },
        timestamp: mcpTimestamp.now("server),"
        practitioner: {,
  id: "tcm-001",
          name: 张仲景AI",
          qualification: "中医算诊专家系统"
        }
      };
      // 创建示例智能体诊断结果
const sampleAgentDiagnoses: AgentDiagnosisResult[] = [;
        {
      agentId: "xiaoai",
      diagnosis: {,
  primarySyndrome: {
              name: 气血平和",
              code: "QX-001,",
              category: "qi-blood",
              severity: mild",
              confidence: 0.85,
              symptoms: ["精神饱满, "面色红润"],"
              diagnosedAt: mcpTimestamp.now(server")"
            },
            secondarySyndromes: [],
            constitution: "balanced,",
            organStates: sampleBiomarkers[0].tcmAssociation.relatedOrgans;
          },
          treatment: {,
  principle: "调和气血，养心安神", "
            lifestyle: {,
  diet: [清淡饮食", "多食新鲜蔬果],
              exercise: ["适量有氧运动", " 太极拳"],"
              sleep: ["规律作息, "晚上11点前入睡"],"
              emotion: [保持心情愉悦", "避免过度紧张]
            }
          },
          confidence: 0.85,
          timestamp: mcpTimestamp.now("server"),
          dataSource: {,
  biomarkers: sampleBiomarkers,
            calculation: sampleCalculation;
          }
        }
      ];
      // 创建五诊数据
const fiveDiagnosesData: FiveDiagnosesData = {inspection: [],
        auscultation: [],
        inquiry: [],
        palpation: [],
        calculation: [sampleCalculation]
      };
      // 创建综合健康数据
const comprehensiveData: ComprehensiveHealthData = {userId,
        timeRange: {,
  start: mcpTimestamp.fromDate(new Date(Date.now() - 24 * 60 * 60 * 1000)),
          end: mcpTimestamp.now(),
          duration: 24 * 60 * 60 * 1000;
        },
        biomarkers: sampleBiomarkers,
        fiveDiagnoses: fiveDiagnosesData,
        agentDiagnoses: sampleAgentDiagnoses,
        completenessScore: 0.85,
        lastUpdated: mcpTimestamp.now(server")"
      };
      setHealthData(comprehensiveData);
    } catch (error) {
      Alert.alert("错误", " 加载健康数据失败，请重试");"
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };
  useEffect() => {
    loadHealthData();
  }, [userId]);
  const handleRefresh = () => {}
    setRefreshing(true);
    loadHealthData();
  };
  // 验证时间戳数据质量
const validateTimestamps = useMemo() => {
    if (!healthData) return { valid: 0, total: 0 };
    let validCount = 0;
    let totalCount = 0;
    // 验证生物标志物时间戳
healthData.biomarkers.forEach(biomarker => {})
      totalCount++;
      if (validateMCPTimestamp(biomarker.timestamp)) {
        validCount++;
      }
    });
    // 验证算诊时间戳
healthData.fiveDiagnoses.calculation.forEach(calculation => {})
      totalCount++;
      if (validateMCPTimestamp(calculation.timestamp)) {
        validCount++;
      }
    });
    return { valid: validCount, total: totalCount };
  }, [healthData]);
  // 渲染生物标志物卡片
const renderBiomarkerCard = (biomarker: BiomarkerData) => {}
    const isNormal = biomarker.value >= biomarker.referenceRange.min && ;
                    biomarker.value <= biomarker.referenceRange.max;
    return (;)
      <TouchableOpacity;
key={biomarker.id}
        style={[styles.biomarkerCard, !isNormal && styles.abnormalCard]}
        onPress={() => onBiomarkerPress?.(biomarker)}
      >
        <View style={styles.cardHeader}>
          <Text style={styles.biomarkerName}>{biomarker.name}</    Text>
          <Text style={styles.biomarkerValue}>
            {biomarker.value} {biomarker.unit}
          </    Text>
        </    View>
        <View style={styles.cardContent}>
          <Text style={styles.timestamp}>
            {getRelativeTime(biomarker.timestamp)}
          </    Text>
          <Text style={styles.tcmInterpretation}>
            {biomarker.tcmAssociation.tcmInterpretation}
          </    Text>
          <View style={styles.qualityIndicator}>
            <Text style={styles.qualityText}>
              可靠性: {Math.round(biomarker.quality.reliability * 100)}%
            </    Text>
            {biomarker.trend  && <Text style={[ ///  >
                styles.trendText,
                biomarker.trend.direction === "increasing && styles.increasingTrend,"
                biomarker.trend.direction === "decreasing" && styles.decreasingTrend;
              ]}}>
                {biomarker.trend.direction === increasing" ? "↗ :
                biomarker.trend.direction === "decreasing" ? ↘" : "→}
              </    Text>
            )}
          </    View>
        </    View>
      </    TouchableOpacity>
    );
  };
  // 渲染算诊结果卡片
const renderCalculationCard = (calculation: CalculationData) => {}
    return (;)
      <TouchableOpacity;
key={calculation.id}
        style={styles.calculationCard}
        onPress={() => onCalculationPress?.(calculation)}
      >
        <View style={styles.cardHeader}>
          <Text style={styles.calculationTitle}>算诊分析</    Text>
          <Text style={styles.calculationScore}>
            {calculation.comprehensiveResult.overallScore}分
          </    Text>
        </    View>
        <View style={styles.cardContent}>
          <Text style={styles.timestamp}>
            {getRelativeTime(calculation.timestamp)}
          </    Text>
          {/* 体质分析 }
          <View style={styles.constitutionSection}>
            <Text style={styles.sectionLabel}>体质类型:</    Text>
            <Text style={styles.constitutionType}>
              {calculation.constitutionAnalysis.constitutionType === "balanced" ? 平和质" : "
              calculation.constitutionAnalysis.constitutionType}
            </    Text>
          </    View>
          {/* 五行分析 }
          <View style={styles.elementsSection}>
            <Text style={styles.sectionLabel}>五行强弱:</    Text>
            <Text style={styles.elementText}>
              最强: {calculation.constitutionAnalysis.elementStrength.strongest} |
              最弱: {calculation.constitutionAnalysis.elementStrength.weakest}
            </    Text>
          </    View>
          {/* 当前时辰经络 }
          <View style={styles.meridianSection}>
            <Text style={styles.sectionLabel}>当前时辰:</    Text>
            <Text style={styles.meridianText}>
              {calculation.ziwuLiuzhu.currentHour.earthlyBranch}时 -
              {calculation.ziwuLiuzhu.currentHour.meridian}当令
            </    Text>
          </    View>
          {/* 主要风险 }
          {calculation.comprehensiveResult.primaryRisks.length > 0  && <View style={styles.riskSection}>
              <Text style={styles.sectionLabel}>主要风险:</    Text>
              <Text style={[ ///  >
                styles.riskText,
                calculation.comprehensiveResult.primaryRisks[0].severity === "high && styles.highRisk,"
                calculation.comprehensiveResult.primaryRisks[0].severity === "medium" && styles.mediumRisk;
              ]}}>
                {calculation.comprehensiveResult.primaryRisks[0].risk}
              </    Text>
            </    View>
          )}
          {/* 置信度 }
          <View style={styles.confidenceSection}>
            <Text style={styles.confidenceText}>
              算诊置信度: {Math.round(calculation.confidence.overall * 100)}%
            </    Text>
          </    View>
        </    View>
      </    TouchableOpacity>
    );
  };
  // 渲染智能体诊断结果
const renderAgentDiagnosis = (diagnosis: AgentDiagnosisResult) => {}
    return (;)
      <TouchableOpacity;
key={`${diagnosis.agentId}-${diagnosis.timestamp.unix}`}
        style={styles.diagnosisCard}
        onPress={() => onAgentDiagnosisPress?.(diagnosis)}
      >
        <View style={styles.diagnosisHeader}>
          <Text style={styles.agentName}>
            {diagnosis.agentId === xiaoai" ? "小艾 :
            diagnosis.agentId === "xiaoke" ? 小克" :"
            diagnosis.agentId === "laoke ? "老克" : 索儿"}
          </    Text>
          <Text style={styles.confidence}>
            置信度: {Math.round(diagnosis.confidence * 100)}%
          </    Text>
        </    View>
        <Text style={styles.syndromeName}>
          {diagnosis.diagnosis.primarySyndrome.name}
        </    Text>
        <Text style={styles.treatmentPrinciple}>
          {diagnosis.treatment.principle}
        </    Text>
        <Text style={styles.diagnosisTime}>
          {formatMCPTimestamp(diagnosis.timestamp, {
      month: "short,",
      day: "numeric",
            hour: 2-digit",
            minute: "2-digit"
          })}
        </    Text>
      </    TouchableOpacity>
    );
  };
  if (loading) {
    return (;)
      <View style={styles.loadingContainer}>;
        <Text style={styles.loadingText}>加载健康数据中...</    Text>;
      </    View>;
    );
  }
  if (!healthData) {
    return (;)
      <View style={styles.errorContainer}>;
        <Text style={styles.errorText}>暂无健康数据</    Text>;
      </    View>;
    );
  }
  return (;)
    <ScrollView;
style={styles.container}
      refreshControl={
        <RefreshControl;
refreshing={refreshing}
          onRefresh={handleRefresh}
          colors={[colors.primary]}
          tintColor={colors.primary}
        /    >
      }
    >
      {/* 数据质量指标 }
      <View style={styles.qualitySection}>
        <Text style={styles.sectionTitle}>数据质量</    Text>
        <View style={styles.qualityStats}>
          <Text style={styles.qualityStatText}>
            时间戳验证: {validateTimestamps.valid}/    {validateTimestamps.total}
          </    Text>
          <Text style={styles.qualityStatText}>
            完整性: {Math.round(healthData.completenessScore * 100)}%
          </    Text>
          <Text style={styles.qualityStatText}>
            五诊完整度: {Object.values(healthData.fiveDiagnoses).filter(arr => arr.length > 0).length}/    5;
          </    Text>
        </    View>
      </    View>
      {/* 生物标志物数据 }
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>生物标志物</    Text>
        {healthData.biomarkers.map(renderBiomarkerCard)}
      </    View>
      {/* 算诊结果 }
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>算诊分析</    Text>
        {healthData.fiveDiagnoses.calculation.map(renderCalculationCard)}
      </    View>
      {/* 智能体诊断结果 }
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>智能体诊断</    Text>
        {healthData.agentDiagnoses.map(renderAgentDiagnosis)}
      </    View>
      {/* 最后更新时间 }
      <View style={styles.footer}>
        <Text style={styles.lastUpdated}>
          最后更新: {formatMCPTimestamp(healthData.lastUpdated)}
        </    Text>
      </    View>
    </    ScrollView>
  );
};
const styles = StyleSheet.create({container: {),
  flex: 1,
    backgroundColor: colors.background;
  },
  loadingContainer: {,
  flex: 1,
    justifyContent: "center",
    alignItems: center""
  },
  loadingText: {
    ...typography.body,
    color: colors.textSecondary;
  },
  errorContainer: {,
  flex: 1,
    justifyContent: "center,",
    alignItems: "center"
  },
  errorText: {
    ...typography.body,
    color: colors.error;
  },
  qualitySection: {,
  padding: spacing.md,
    backgroundColor: colors.surface,
    marginBottom: spacing.sm;
  },
  qualityStats: {,
  flexDirection: row",
    justifyContent: "space-between,",
    marginTop: spacing.sm;
  },
  qualityStatText: {
    ...typography.caption,
    color: colors.textSecondary;
  },
  section: {,
  padding: spacing.md,
    marginBottom: spacing.sm;
  },
  sectionTitle: {
    ...typography.h3,
    color: colors.text,
    marginBottom: spacing.md;
  },
  biomarkerCard: {,
  backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border;
  },
  abnormalCard: {,
  borderColor: colors.warning,
    backgroundColor: colors.warningLight;
  },
  cardHeader: {,
  flexDirection: "row",
    justifyContent: space-between",
    alignItems: "center,",
    marginBottom: spacing.sm;
  },
  biomarkerName: {
    ...typography.h4,
    color: colors.text;
  },
  biomarkerValue: {
    ...typography.h4,
    color: colors.primary,
    fontWeight: "bold"
  },
  cardContent: {,
  gap: spacing.xs;
  },
  timestamp: {
    ...typography.caption,
    color: colors.textSecondary;
  },
  tcmInterpretation: {
    ...typography.body,
    color: colors.text,
    fontStyle: italic""
  },
  qualityIndicator: {,
  flexDirection: "row,",
    justifyContent: "space-between",
    alignItems: center""
  },
  qualityText: {
    ...typography.caption,
    color: colors.textSecondary;
  },
  trendText: {
    ...typography.h4,
    color: colors.textSecondary;
  },
  increasingTrend: {,
  color: colors.success;
  },
  decreasingTrend: {,
  color: colors.error;
  },
  diagnosisCard: {,
  backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.sm,
    borderLeftWidth: 4,
    borderLeftColor: colors.primary;
  },
  diagnosisHeader: {,
  flexDirection: "row,",
    justifyContent: "space-between",
    alignItems: center",
    marginBottom: spacing.sm;
  },
  agentName: {
    ...typography.h4,
    color: colors.primary,
    fontWeight: "bold"
  },
  confidence: {
    ...typography.caption,
    color: colors.textSecondary;
  },
  syndromeName: {
    ...typography.h4,
    color: colors.text,
    marginBottom: spacing.xs;
  },
  treatmentPrinciple: {
    ...typography.body,
    color: colors.text,
    marginBottom: spacing.sm;
  },
  diagnosisTime: {
    ...typography.caption,
    color: colors.textSecondary;
  },
  footer: {,
  padding: spacing.md,
    alignItems: "center"
  },
  lastUpdated: {
    ...typography.caption,
    color: colors.textSecondary;
  },
  calculationCard: {,
  backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.sm,
    borderLeftWidth: 4,
    borderLeftColor: colors.primary;
  },
  calculationTitle: {
    ...typography.h4,
    color: colors.primary,
    fontWeight: bold""
  },
  calculationScore: {
    ...typography.h4,
    color: colors.primary,
    fontWeight: 'bold'
  },
  constitutionSection: {,
  marginBottom: spacing.xs;
  },
  sectionLabel: {
    ...typography.caption,
    color: colors.textSecondary;
  },
  constitutionType: {
    ...typography.body,
    color: colors.text;
  },
  elementsSection: {,
  marginBottom: spacing.xs;
  },
  elementText: {
    ...typography.body,
    color: colors.text;
  },
  meridianSection: {,
  marginBottom: spacing.xs;
  },
  meridianText: {
    ...typography.body,
    color: colors.text;
  },
  riskSection: {,
  marginBottom: spacing.xs;
  },
  riskText: {
    ...typography.body,
    color: colors.text;
  },
  highRisk: {,
  color: colors.error;
  },
  mediumRisk: {,
  color: colors.warning;
  },
  confidenceSection: {,
  marginBottom: spacing.xs;
  },
  confidenceText: {
    ...typography.caption, */
    color: colors.textSecondary; *///
  }; *///
});  */