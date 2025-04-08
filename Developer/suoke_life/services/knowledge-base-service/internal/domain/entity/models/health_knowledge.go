package models

import (
	"time"

	"github.com/google/uuid"
)

// 基础知识结构
type BaseKnowledge struct {
	ID          uuid.UUID  `json:"id"`
	Title       string     `json:"title"`
	Description string     `json:"description"`
	Content     string     `json:"content"`
	AuthorID    uuid.UUID  `json:"author_id"`
	CategoryID  uuid.UUID  `json:"category_id"`
	Tags        []string   `json:"tags"`
	Status      string     `json:"status"`
	Version     string     `json:"version"`
	ReviewCount int        `json:"review_count"`
	Metadata    []Metadata `json:"metadata"`
	CreatedAt   time.Time  `json:"created_at"`
	UpdatedAt   time.Time  `json:"updated_at"`
}

// 元数据
type Metadata struct {
	Key   string      `json:"key"`
	Value interface{} `json:"value"`
}

// 传统中医知识
type TraditionalChineseMedicineKnowledge struct {
	BaseKnowledge
	Origin            string   `json:"origin"`             // 起源/出处
	ClassicalText     string   `json:"classical_text"`     // 经典著作
	MeridianSystem    []string `json:"meridian_system"`    // 相关经络
	FiveElements      []string `json:"five_elements"`      // 五行属性
	HerbalMedicines   []string `json:"herbal_medicines"`   // 关联中药
	Acupoints         []string `json:"acupoints"`          // 关联穴位
	ConstitutionTypes []string `json:"constitution_types"` // 相关体质类型
	Contraindications string   `json:"contraindications"`  // 禁忌
}

// 现代医学知识
type ModernMedicineKnowledge struct {
	BaseKnowledge
	ScientificBasis   string   `json:"scientific_basis"`   // 科学依据
	ResearchPapers    []string `json:"research_papers"`    // 研究论文
	ClinicalEvidence  string   `json:"clinical_evidence"`  // 临床证据
	HealthStandards   []string `json:"health_standards"`   // 健康标准
	RiskFactors       []string `json:"risk_factors"`       // 风险因素
	PreventionMethods []string `json:"prevention_methods"` // 预防方法
	DiagnosticMethods []string `json:"diagnostic_methods"` // 诊断方法
	TreatmentOptions  []string `json:"treatment_options"`  // 治疗选择
}

// 精准医学
type PrecisionMedicineKnowledge struct {
	BaseKnowledge
	GeneticMarkers           []string `json:"genetic_markers"`           // 遗传标记
	Biomarkers               []string `json:"biomarkers"`                // 生物标记物
	PersonalizedFactors      []string `json:"personalized_factors"`      // 个性化因素
	EnvironmentalFactors     []string `json:"environmental_factors"`     // 环境因素
	LifestyleRecommendations []string `json:"lifestyle_recommendations"` // 生活方式建议
	NutritionRecommendations []string `json:"nutrition_recommendations"` // 营养建议
	EffectivePopulation      string   `json:"effective_population"`      // 适用人群
}

// 可穿戴设备数据
type WearableDeviceData struct {
	BaseKnowledge
	DeviceTypes           []string `json:"device_types"`           // 设备类型
	MeasurementMetrics    []string `json:"measurement_metrics"`    // 测量指标
	DataInterpretation    string   `json:"data_interpretation"`    // 数据解读
	NormalRanges          string   `json:"normal_ranges"`          // 正常范围
	AbnormalIndications   string   `json:"abnormal_indications"`   // 异常指示
	ActionableSuggestions string   `json:"actionable_suggestions"` // 可行建议
	AccuracyLevel         string   `json:"accuracy_level"`         // 准确度级别
}

// 多模态健康数据
type MultimodalHealthData struct {
	BaseKnowledge
	DataTypes                []string `json:"data_types"`                // 数据类型
	SensorInformation        string   `json:"sensor_information"`        // 传感器信息
	SamplingFrequency        string   `json:"sampling_frequency"`        // 采样频率
	ProcessingMethods        string   `json:"processing_methods"`        // 处理方法
	FeatureExtraction        string   `json:"feature_extraction"`        // 特征提取
	MachineLearningModels    []string `json:"machine_learning_models"`   // 机器学习模型
	AccuracyMetrics          string   `json:"accuracy_metrics"`          // 准确度指标
	ValidationMethods        string   `json:"validation_methods"`        // 验证方法
	InterpretationGuidelines string   `json:"interpretation_guidelines"` // 解释指南
}

// 循证医学知识
type EvidenceBasedMedicineKnowledge struct {
	BaseKnowledge
	EvidenceLevel          string   `json:"evidence_level"`          // 证据等级
	ResearchMethodology    string   `json:"research_methodology"`    // 研究方法
	SampleSize             int      `json:"sample_size"`             // 样本大小
	StudyDesign            string   `json:"study_design"`            // 研究设计
	OutcomeMeasures        []string `json:"outcome_measures"`        // 结局指标
	StatisticalMethods     []string `json:"statistical_methods"`     // 统计方法
	LimitationsOfEvidence  string   `json:"limitations_of_evidence"` // 证据局限性
	RecommendationStrength string   `json:"recommendation_strength"` // 推荐强度
}

// 跨学科知识
type InterdisciplinaryKnowledge struct {
	BaseKnowledge
	Disciplines           []string `json:"disciplines"`            // 涉及学科
	IntegrationApproach   string   `json:"integration_approach"`   // 整合方法
	SynergyPoints         []string `json:"synergy_points"`         // 协同点
	TheoreticalFramework  string   `json:"theoretical_framework"`  // 理论框架
	PracticalApplications []string `json:"practical_applications"` // 实际应用
	CaseStudies           []string `json:"case_studies"`           // 案例研究
}

// 健康教育知识
type HealthEducationKnowledge struct {
	BaseKnowledge
	TargetAudience         string   `json:"target_audience"`         // 目标受众
	EducationalObjectives  []string `json:"educational_objectives"`  // 教育目标
	DeliveryMethods        []string `json:"delivery_methods"`        // 传递方法
	KeyMessages            []string `json:"key_messages"`            // 关键信息
	VisualAids             []string `json:"visual_aids"`             // 视觉辅助
	AssessmentMethods      []string `json:"assessment_methods"`      // 评估方法
	EffectivenessMetrics   []string `json:"effectiveness_metrics"`   // 有效性指标
	CulturalConsiderations string   `json:"cultural_considerations"` // 文化考虑
}

// 心理健康知识
type PsychologicalHealthKnowledge struct {
	BaseKnowledge
	PsychologicalDomain   string   `json:"psychological_domain"`   // 心理领域
	TherapeuticApproaches []string `json:"therapeutic_approaches"` // 治疗方法
	AssessmentTools       []string `json:"assessment_tools"`       // 评估工具
	CommonSymptoms        []string `json:"common_symptoms"`        // 常见症状
	CopingStrategies      []string `json:"coping_strategies"`      // 应对策略
	SupportResources      []string `json:"support_resources"`      // 支持资源
	PreventionStrategies  []string `json:"prevention_strategies"`  // 预防策略
	RecoveryIndicators    []string `json:"recovery_indicators"`    // 恢复指标
}

// 环境健康知识
type EnvironmentalHealthKnowledge struct {
	BaseKnowledge
	EnvironmentalFactors  []string `json:"environmental_factors"`  // 环境因素
	ExposureRoutes        []string `json:"exposure_routes"`        // 暴露途径
	HealthImpacts         string   `json:"health_impacts"`         // 健康影响
	VulnerablePopulations []string `json:"vulnerable_populations"` // 脆弱人群
	SafetyGuidelines      []string `json:"safety_guidelines"`      // 安全准则
	MitigationStrategies  []string `json:"mitigation_strategies"`  // 缓解策略
	MonitoringApproaches  []string `json:"monitoring_approaches"`  // 监测方法
	RegulatoryStandards   string   `json:"regulatory_standards"`   // 监管标准
}
