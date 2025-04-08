package rag

import (
	"context"
	"time"

	"github.com/suoke/suoke_life/services/rag-service/internal/utils"
)

// WeightAdjuster 权重调整器接口
type WeightAdjuster interface {
	// AdjustWeights 调整权重
	AdjustWeights(ctx context.Context, query string, analysisResult *QueryAnalysisResult) (float64, float64, error)
	
	// Learn 学习最优权重
	Learn(ctx context.Context, query string, vectorScore, keywordScore, finalScore float64, isRelevant bool) error
	
	// Initialize 初始化
	Initialize(ctx context.Context) error
	
	// Close 关闭
	Close() error
}

// SimpleWeightAdjuster 简单权重调整器
type SimpleWeightAdjuster struct {
	// 默认向量权重
	defaultVectorWeight float64
	
	// 默认关键词权重
	defaultKeywordWeight float64
	
	// 学习记录
	learningRecords map[string]*WeightLearningRecord
	
	// 领域特定权重
	domainWeights map[QueryDomain]struct {
		VectorWeight  float64
		KeywordWeight float64
	}
	
	// 查询类型特定权重
	typeWeights map[QueryType]struct {
		VectorWeight  float64
		KeywordWeight float64
	}
	
	// 学习率
	learningRate float64
	
	// 日志器
	logger utils.Logger
}

// WeightLearningRecord 权重学习记录
type WeightLearningRecord struct {
	// 查询
	Query string
	
	// 向量搜索分数
	VectorScore float64
	
	// 关键词搜索分数
	KeywordScore float64
	
	// 最终分数
	FinalScore float64
	
	// 相关性（用户反馈）
	IsRelevant bool
	
	// 时间戳
	Timestamp time.Time
	
	// 向量权重
	VectorWeight float64
	
	// 关键词权重
	KeywordWeight float64
}

// NewSimpleWeightAdjuster 创建简单权重调整器
func NewSimpleWeightAdjuster() *SimpleWeightAdjuster {
	adjuster := &SimpleWeightAdjuster{
		defaultVectorWeight:  0.7,
		defaultKeywordWeight: 0.3,
		learningRecords:      make(map[string]*WeightLearningRecord),
		domainWeights:        make(map[QueryDomain]struct{VectorWeight float64; KeywordWeight float64}),
		typeWeights:          make(map[QueryType]struct{VectorWeight float64; KeywordWeight float64}),
		learningRate:         0.05,
		logger:               utils.NewNoopLogger(),
	}
	
	// 初始化默认领域权重
	adjuster.initializeDefaultDomainWeights()
	
	// 初始化默认查询类型权重
	adjuster.initializeDefaultTypeWeights()
	
	return adjuster
}

// AdjustWeights 调整权重
func (a *SimpleWeightAdjuster) AdjustWeights(ctx context.Context, query string, analysisResult *QueryAnalysisResult) (float64, float64, error) {
	// 首先使用分析结果中的权重
	vectorWeight := analysisResult.VectorWeight
	keywordWeight := analysisResult.KeywordWeight
	
	// 然后基于领域进行调整
	if domainWeights, ok := a.domainWeights[analysisResult.Domain]; ok {
		// 领域特定权重与分析器权重取平均
		vectorWeight = (vectorWeight + domainWeights.VectorWeight) / 2
		keywordWeight = (keywordWeight + domainWeights.KeywordWeight) / 2
	}
	
	// 然后基于查询类型进行调整
	if typeWeights, ok := a.typeWeights[analysisResult.Type]; ok {
		// 查询类型特定权重与当前权重取平均
		vectorWeight = (vectorWeight + typeWeights.VectorWeight) / 2
		keywordWeight = (keywordWeight + typeWeights.KeywordWeight) / 2
	}
	
	// 确保权重总和为1.0
	total := vectorWeight + keywordWeight
	if total > 0 {
		vectorWeight /= total
		keywordWeight /= total
	} else {
		vectorWeight = a.defaultVectorWeight
		keywordWeight = a.defaultKeywordWeight
	}
	
	return vectorWeight, keywordWeight, nil
}

// Learn 学习最优权重
func (a *SimpleWeightAdjuster) Learn(ctx context.Context, query string, vectorScore, keywordScore, finalScore float64, isRelevant bool) error {
	record := &WeightLearningRecord{
		Query:         query,
		VectorScore:   vectorScore,
		KeywordScore:  keywordScore,
		FinalScore:    finalScore,
		IsRelevant:    isRelevant,
		Timestamp:     time.Now(),
		VectorWeight:  a.defaultVectorWeight,
		KeywordWeight: a.defaultKeywordWeight,
	}
	
	// 如果已有记录，则获取之前的权重
	if existingRecord, ok := a.learningRecords[query]; ok {
		record.VectorWeight = existingRecord.VectorWeight
		record.KeywordWeight = existingRecord.KeywordWeight
	}
	
	// 如果用户反馈相关，则调整权重以增加相关性
	if isRelevant {
		// 如果向量分数更高，则增加向量权重
		if vectorScore > keywordScore {
			record.VectorWeight += a.learningRate
			record.KeywordWeight -= a.learningRate
		} else {
			// 否则增加关键词权重
			record.VectorWeight -= a.learningRate
			record.KeywordWeight += a.learningRate
		}
	} else {
		// 如果用户反馈不相关，则减少贡献最多的权重
		if vectorScore > keywordScore {
			record.VectorWeight -= a.learningRate
			record.KeywordWeight += a.learningRate
		} else {
			record.VectorWeight += a.learningRate
			record.KeywordWeight -= a.learningRate
		}
	}
	
	// 确保权重在有效范围内
	if record.VectorWeight < 0 {
		record.VectorWeight = 0
	}
	if record.KeywordWeight < 0 {
		record.KeywordWeight = 0
	}
	
	// 归一化权重
	total := record.VectorWeight + record.KeywordWeight
	if total > 0 {
		record.VectorWeight /= total
		record.KeywordWeight /= total
	} else {
		record.VectorWeight = a.defaultVectorWeight
		record.KeywordWeight = a.defaultKeywordWeight
	}
	
	// 更新记录
	a.learningRecords[query] = record
	
	return nil
}

// Initialize 初始化
func (a *SimpleWeightAdjuster) Initialize(ctx context.Context) error {
	return nil
}

// Close 关闭
func (a *SimpleWeightAdjuster) Close() error {
	return nil
}

// 初始化默认领域权重
func (a *SimpleWeightAdjuster) initializeDefaultDomainWeights() {
	// 中医领域权重
	a.domainWeights[DomainTCM] = struct {
		VectorWeight  float64
		KeywordWeight float64
	}{
		VectorWeight:  0.6, // 中医领域术语较多，增加关键词权重
		KeywordWeight: 0.4,
	}
	
	// 营养领域权重
	a.domainWeights[DomainNutrition] = struct {
		VectorWeight  float64
		KeywordWeight float64
	}{
		VectorWeight:  0.65,
		KeywordWeight: 0.35,
	}
	
	// 医学领域权重
	a.domainWeights[DomainMedicine] = struct {
		VectorWeight  float64
		KeywordWeight float64
	}{
		VectorWeight:  0.65,
		KeywordWeight: 0.35,
	}
	
	// 农业领域权重
	a.domainWeights[DomainAgriculture] = struct {
		VectorWeight  float64
		KeywordWeight float64
	}{
		VectorWeight:  0.6,
		KeywordWeight: 0.4,
	}
}

// 初始化默认查询类型权重
func (a *SimpleWeightAdjuster) initializeDefaultTypeWeights() {
	// 关键词查询权重
	a.typeWeights[TypeKeyword] = struct {
		VectorWeight  float64
		KeywordWeight float64
	}{
		VectorWeight:  0.3, // 关键词查询更适合关键词搜索
		KeywordWeight: 0.7,
	}
	
	// 语义查询权重
	a.typeWeights[TypeSemantic] = struct {
		VectorWeight  float64
		KeywordWeight float64
	}{
		VectorWeight:  0.8, // 语义查询更适合向量搜索
		KeywordWeight: 0.2,
	}
	
	// 事实查询权重
	a.typeWeights[TypeFactual] = struct {
		VectorWeight  float64
		KeywordWeight float64
	}{
		VectorWeight:  0.5, // 事实查询两种方式都可以
		KeywordWeight: 0.5,
	}
	
	// 对话查询权重
	a.typeWeights[TypeConversational] = struct {
		VectorWeight  float64
		KeywordWeight float64
	}{
		VectorWeight:  0.8, // 对话查询通常更适合向量搜索
		KeywordWeight: 0.2,
	}
}

// SetLearningRate 设置学习率
func (a *SimpleWeightAdjuster) SetLearningRate(rate float64) {
	if rate > 0 && rate < 1.0 {
		a.learningRate = rate
	}
}

// SetDefaultWeights 设置默认权重
func (a *SimpleWeightAdjuster) SetDefaultWeights(vectorWeight, keywordWeight float64) {
	total := vectorWeight + keywordWeight
	if total > 0 {
		a.defaultVectorWeight = vectorWeight / total
		a.defaultKeywordWeight = keywordWeight / total
	}
}

// SetLogger 设置日志器
func (a *SimpleWeightAdjuster) SetLogger(logger utils.Logger) {
	if logger != nil {
		a.logger = logger
	}
}

// GetLearningRecords 获取学习记录
func (a *SimpleWeightAdjuster) GetLearningRecords() map[string]*WeightLearningRecord {
	return a.learningRecords
}

// ClearLearningRecords 清空学习记录
func (a *SimpleWeightAdjuster) ClearLearningRecords() {
	a.learningRecords = make(map[string]*WeightLearningRecord)
} 