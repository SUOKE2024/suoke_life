package rag

import (
	"context"
	"strings"
	"unicode/utf8"

	"github.com/suoke/suoke_life/services/rag-service/internal/utils"
)

// QueryDomain 查询领域
type QueryDomain string

const (
	// DomainGeneral 通用领域
	DomainGeneral QueryDomain = "general"
	
	// DomainTCM 中医领域
	DomainTCM QueryDomain = "tcm"
	
	// DomainNutrition 营养领域
	DomainNutrition QueryDomain = "nutrition"
	
	// DomainMedicine 医学领域
	DomainMedicine QueryDomain = "medicine"
	
	// DomainAgriculture 农业领域
	DomainAgriculture QueryDomain = "agriculture"
)

// QueryType 查询类型
type QueryType string

const (
	// TypeKeyword 关键词查询
	TypeKeyword QueryType = "keyword"
	
	// TypeSemantic 语义查询
	TypeSemantic QueryType = "semantic"
	
	// TypeFactual 事实查询
	TypeFactual QueryType = "factual"
	
	// TypeConversational 对话查询
	TypeConversational QueryType = "conversational"
)

// QueryAnalysisResult 查询分析结果
type QueryAnalysisResult struct {
	// 查询类型
	Type QueryType
	
	// 查询领域
	Domain QueryDomain
	
	// 提取的关键词
	Keywords []string
	
	// 语义向量搜索推荐权重
	VectorWeight float64
	
	// 关键词搜索推荐权重
	KeywordWeight float64
	
	// 其他元数据
	Metadata map[string]interface{}
}

// QueryAnalyzer 查询分析器接口
type QueryAnalyzer interface {
	// Analyze 分析查询
	Analyze(ctx context.Context, query string) (*QueryAnalysisResult, error)
	
	// Initialize 初始化
	Initialize(ctx context.Context) error
	
	// Close 关闭分析器
	Close() error
}

// SimpleQueryAnalyzer 简单查询分析器
type SimpleQueryAnalyzer struct {
	// 中医术语列表
	tcmTerms []string
	
	// 停用词列表
	stopwords []string
	
	// 领域关键词
	domainKeywords map[QueryDomain][]string
	
	// 领域检测阈值
	domainThreshold float64
	
	// 简短查询长度阈值
	shortQueryThreshold int
}

// NewSimpleQueryAnalyzer 创建简单查询分析器
func NewSimpleQueryAnalyzer(tcmTerms, stopwords []string) *SimpleQueryAnalyzer {
	analyzer := &SimpleQueryAnalyzer{
		tcmTerms:           tcmTerms,
		stopwords:          stopwords,
		domainKeywords:     make(map[QueryDomain][]string),
		domainThreshold:    0.2,
		shortQueryThreshold: 5,
	}
	
	// 初始化默认领域关键词
	analyzer.initializeDefaultDomainKeywords()
	
	return analyzer
}

// Initialize 初始化分析器
func (a *SimpleQueryAnalyzer) Initialize(ctx context.Context) error {
	// 简单分析器不需要额外初始化
	return nil
}

// Close 关闭分析器
func (a *SimpleQueryAnalyzer) Close() error {
	// 简单分析器不需要额外清理
	return nil
}

// Analyze 分析查询
func (a *SimpleQueryAnalyzer) Analyze(ctx context.Context, query string) (*QueryAnalysisResult, error) {
	result := &QueryAnalysisResult{
		Type:          TypeSemantic,
		Domain:        DomainGeneral,
		Keywords:      make([]string, 0),
		VectorWeight:  0.7,
		KeywordWeight: 0.3,
		Metadata:      make(map[string]interface{}),
	}
	
	// 提取关键词
	keywords := a.extractKeywords(query)
	result.Keywords = keywords
	
	// 检测查询类型
	result.Type = a.detectQueryType(query, keywords)
	
	// 检测领域
	result.Domain = a.detectDomain(query, keywords)
	
	// 根据查询类型和领域调整权重
	a.adjustWeights(result, query)
	
	// 添加元数据
	result.Metadata["query_length"] = utf8.RuneCountInString(query)
	result.Metadata["keyword_count"] = len(keywords)
	
	return result, nil
}

// 提取关键词
func (a *SimpleQueryAnalyzer) extractKeywords(query string) []string {
	// 分词
	words := strings.Fields(strings.ToLower(query))
	
	// 过滤停用词
	keywords := make([]string, 0)
	for _, word := range words {
		if !a.isStopword(word) {
			keywords = append(keywords, word)
		}
	}
	
	return keywords
}

// 检测查询类型
func (a *SimpleQueryAnalyzer) detectQueryType(query string, keywords []string) QueryType {
	// 简单启发式规则
	
	// 检查是否是对话型查询
	if strings.Contains(query, "?") || strings.Contains(query, "？") {
		return TypeConversational
	}
	
	// 检查是否是事实型查询
	if strings.Contains(query, "何为") || strings.Contains(query, "什么是") || 
	   strings.Contains(query, "定义") || strings.Contains(query, "解释") {
		return TypeFactual
	}
	
	// 如果查询长度短且关键词少，可能是关键词查询
	if len(keywords) <= 3 && utf8.RuneCountInString(query) <= a.shortQueryThreshold {
		return TypeKeyword
	}
	
	// 默认为语义查询
	return TypeSemantic
}

// 检测领域
func (a *SimpleQueryAnalyzer) detectDomain(query string, keywords []string) QueryDomain {
	domainScores := make(map[QueryDomain]float64)
	
	// 对每个领域计算命中分数
	for domain, domainKeywords := range a.domainKeywords {
		domainScores[domain] = a.calculateDomainScore(query, keywords, domainKeywords)
	}
	
	// 找出得分最高的领域
	var bestDomain QueryDomain = DomainGeneral
	var bestScore float64 = 0
	
	for domain, score := range domainScores {
		if score > bestScore && score >= a.domainThreshold {
			bestScore = score
			bestDomain = domain
		}
	}
	
	return bestDomain
}

// 计算领域得分
func (a *SimpleQueryAnalyzer) calculateDomainScore(query string, keywords []string, domainKeywords []string) float64 {
	// 检查关键词匹配
	matchCount := 0
	
	for _, keyword := range keywords {
		for _, domainKeyword := range domainKeywords {
			if strings.Contains(keyword, domainKeyword) || strings.Contains(domainKeyword, keyword) {
				matchCount++
				break
			}
		}
	}
	
	// 直接检查查询中是否包含领域关键词
	directMatchCount := 0
	for _, domainKeyword := range domainKeywords {
		if strings.Contains(query, domainKeyword) {
			directMatchCount++
		}
	}
	
	// 计算总分
	if len(keywords) == 0 {
		return 0
	}
	
	keywordMatchScore := float64(matchCount) / float64(len(keywords))
	directMatchScore := float64(directMatchCount) / float64(len(domainKeywords))
	
	// 组合得分
	return keywordMatchScore*0.6 + directMatchScore*0.4
}

// 调整权重
func (a *SimpleQueryAnalyzer) adjustWeights(result *QueryAnalysisResult, query string) {
	// 根据查询类型调整权重
	switch result.Type {
	case TypeKeyword:
		// 关键词查询更偏向关键词搜索
		result.VectorWeight = 0.3
		result.KeywordWeight = 0.7
	case TypeFactual:
		// 事实查询均衡一点
		result.VectorWeight = 0.5
		result.KeywordWeight = 0.5
	case TypeConversational:
		// 对话查询更偏向语义搜索
		result.VectorWeight = 0.8
		result.KeywordWeight = 0.2
	default:
		// 语义查询默认权重
		result.VectorWeight = 0.7
		result.KeywordWeight = 0.3
	}
	
	// 根据领域调整权重
	switch result.Domain {
	case DomainTCM:
		// 中医领域可能有特殊术语，增加关键词权重
		result.VectorWeight -= 0.1
		result.KeywordWeight += 0.1
	case DomainAgriculture:
		// 农业领域同样有特殊术语
		result.VectorWeight -= 0.05
		result.KeywordWeight += 0.05
	}
	
	// 确保权重总和为1.0
	total := result.VectorWeight + result.KeywordWeight
	if total > 0 {
		result.VectorWeight /= total
		result.KeywordWeight /= total
	}
}

// 检查是否是停用词
func (a *SimpleQueryAnalyzer) isStopword(word string) bool {
	for _, stopword := range a.stopwords {
		if word == stopword {
			return true
		}
	}
	return false
}

// 检查是否包含中医术语
func (a *SimpleQueryAnalyzer) containsTCMTerms(query string) bool {
	for _, term := range a.tcmTerms {
		if strings.Contains(query, term) {
			return true
		}
	}
	return false
}

// 初始化默认领域关键词
func (a *SimpleQueryAnalyzer) initializeDefaultDomainKeywords() {
	// 中医领域关键词
	a.domainKeywords[DomainTCM] = []string{
		"中医", "中药", "针灸", "艾灸", "经络", "穴位", "气血", "阴阳", "五行",
		"脏腑", "辨证", "舌诊", "脉诊", "处方", "汤剂", "丸剂", "膏方", "调理",
		"湿热", "寒湿", "虚实", "补气", "益阴", "温阳", "清热", "利湿", "消导",
	}
	
	// 营养领域关键词
	a.domainKeywords[DomainNutrition] = []string{
		"饮食", "营养", "蛋白质", "脂肪", "碳水", "维生素", "矿物质", "膳食",
		"热量", "能量", "代谢", "消化", "吸收", "减肥", "增重", "健身", "运动",
		"食谱", "菜谱", "食材", "烹饪", "搭配", "食疗", "养生", "健康饮食",
	}
	
	// 医学领域关键词
	a.domainKeywords[DomainMedicine] = []string{
		"医学", "临床", "病症", "疾病", "诊断", "治疗", "药物", "药剂", "西药",
		"抗生素", "手术", "检查", "检验", "CT", "核磁", "超声", "放射", "免疫",
		"基因", "细胞", "病毒", "细菌", "寄生虫", "心脏", "肝脏", "肾脏", "肺",
	}
	
	// 农业领域关键词
	a.domainKeywords[DomainAgriculture] = []string{
		"农业", "种植", "栽培", "养殖", "畜牧", "农作物", "果树", "蔬菜", "粮食",
		"有机", "无机", "肥料", "农药", "灌溉", "收割", "土壤", "种子", "幼苗",
		"病虫害", "防治", "除草", "农机", "农具", "农艺", "农田", "大棚", "温室",
	}
}

// SetTCMTerms 设置中医术语
func (a *SimpleQueryAnalyzer) SetTCMTerms(terms []string) {
	a.tcmTerms = terms
}

// SetStopwords 设置停用词
func (a *SimpleQueryAnalyzer) SetStopwords(stopwords []string) {
	a.stopwords = stopwords
}

// SetDomainKeywords 设置领域关键词
func (a *SimpleQueryAnalyzer) SetDomainKeywords(domain QueryDomain, keywords []string) {
	a.domainKeywords[domain] = keywords
}

// SetDomainThreshold 设置领域检测阈值
func (a *SimpleQueryAnalyzer) SetDomainThreshold(threshold float64) {
	if threshold > 0 && threshold <= 1.0 {
		a.domainThreshold = threshold
	}
}

// SetShortQueryThreshold 设置短查询阈值
func (a *SimpleQueryAnalyzer) SetShortQueryThreshold(threshold int) {
	if threshold > 0 {
		a.shortQueryThreshold = threshold
	}
} 