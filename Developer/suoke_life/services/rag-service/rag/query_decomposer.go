package rag

import (
	"context"
	"fmt"
	"strings"
	"sync"

	"github.com/suoke/suoke_life/services/rag-service/internal/models"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils"
)

// SubQuery 子查询结构
type SubQuery struct {
	// 子查询ID
	ID string `json:"id"`
	
	// 子查询文本
	Text string `json:"text"`
	
	// 原始查询中的起始位置
	StartPosition int `json:"start_position"`
	
	// 原始查询中的结束位置
	EndPosition int `json:"end_position"`
	
	// 子查询权重
	Weight float64 `json:"weight"`
	
	// 子查询领域
	Domain string `json:"domain"`
	
	// 子查询类型
	Type string `json:"type"`
	
	// 子查询上下文
	Context string `json:"context,omitempty"`
	
	// 其他元数据
	Metadata map[string]interface{} `json:"metadata,omitempty"`
}

// DecomposedQuery 分解后的查询
type DecomposedQuery struct {
	// 原始查询
	OriginalQuery string `json:"original_query"`
	
	// 子查询列表
	SubQueries []SubQuery `json:"sub_queries"`
	
	// 查询关系图（用于表示子查询之间的关系）
	// 格式: map[子查询ID][]相关子查询ID
	QueryGraph map[string][]string `json:"query_graph,omitempty"`
	
	// 全局上下文
	GlobalContext string `json:"global_context,omitempty"`
	
	// 全局约束
	GlobalConstraints map[string]interface{} `json:"global_constraints,omitempty"`
}

// QueryDecomposer 查询分解器接口
type QueryDecomposer interface {
	// DecomposeQuery 将复杂查询分解为多个子查询
	DecomposeQuery(ctx context.Context, query string, options map[string]interface{}) (*DecomposedQuery, error)
	
	// Name 返回分解器名称
	Name() string
	
	// Initialize 初始化分解器
	Initialize(ctx context.Context) error
	
	// Close 关闭分解器
	Close() error
}

// TCMQueryDecomposer 中医领域查询分解器
type TCMQueryDecomposer struct {
	// 日志器
	logger utils.Logger
	
	// 中医术语处理器
	terminologyProcessor *utils.TCMTerminologyProcessor
	
	// LLM服务
	llmService utils.LLMService
	
	// 分解模板
	decompositionTemplates map[string]string
	
	// 查询模式检测器
	patternDetector *utils.QueryPatternDetector
	
	// 缓存
	cache utils.Cache
}

// NewTCMQueryDecomposer 创建中医领域查询分解器
func NewTCMQueryDecomposer(llmService utils.LLMService, terminologyProcessor *utils.TCMTerminologyProcessor, logger utils.Logger) *TCMQueryDecomposer {
	if logger == nil {
		logger = utils.NewNoopLogger()
	}
	
	return &TCMQueryDecomposer{
		logger:                logger,
		terminologyProcessor:  terminologyProcessor,
		llmService:            llmService,
		decompositionTemplates: make(map[string]string),
		patternDetector:       utils.NewQueryPatternDetector(),
		cache:                 utils.NewLRUCache(1000),
	}
}

// Name 返回分解器名称
func (d *TCMQueryDecomposer) Name() string {
	return "tcm-query-decomposer"
}

// Initialize 初始化分解器
func (d *TCMQueryDecomposer) Initialize(ctx context.Context) error {
	// 初始化模板
	d.initDecompositionTemplates()
	
	// 初始化查询模式检测器
	if err := d.patternDetector.Initialize(); err != nil {
		return fmt.Errorf("初始化查询模式检测器失败: %w", err)
	}
	
	d.logger.Info("初始化中医查询分解器完成")
	return nil
}

// Close 关闭分解器
func (d *TCMQueryDecomposer) Close() error {
	return nil
}

// 初始化分解模板
func (d *TCMQueryDecomposer) initDecompositionTemplates() {
	d.decompositionTemplates["default"] = `
你是一个专业的中医知识查询助手。请将以下复杂查询分解为多个子查询，每个子查询应该专注于一个具体的方面。

原始查询: {{.query}}

请将查询分解为以下几个方面（如适用）：
1. 中医基础理论方面
2. 症状描述与辨识方面
3. 诊断方法方面
4. 治疗方案方面
5. 药方与方剂方面
6. 预防保健方面

输出格式：
[
  {"id": "子查询ID", "text": "子查询文本", "domain": "子查询领域", "type": "子查询类型", "weight": 子查询权重}
]
`

	d.decompositionTemplates["symptom"] = `
你是一个专业的中医症状分析助手。请将以下关于症状的复杂查询分解为多个子查询，每个子查询应该专注于一个具体的症状或症状群。

原始查询: {{.query}}

请将查询分解为不同的症状子查询，并考虑：
1. 每个独立症状的特征
2. 症状之间可能的关联
3. 症状对应的可能病机

输出格式：
[
  {"id": "子查询ID", "text": "子查询文本", "domain": "子查询领域", "type": "子查询类型", "weight": 子查询权重}
]
`

	d.decompositionTemplates["treatment"] = `
你是一个专业的中医治疗方案分析助手。请将以下关于治疗的复杂查询分解为多个子查询，每个子查询应该专注于一个具体的治疗方面。

原始查询: {{.query}}

请将查询分解为不同的治疗子查询，并考虑：
1. 辨证论治方面
2. 具体方剂选用方面
3. 针灸治疗方面
4. 推拿按摩方面
5. 食疗调养方面
6. 生活起居方面

输出格式：
[
  {"id": "子查询ID", "text": "子查询文本", "domain": "子查询领域", "type": "子查询类型", "weight": 子查询权重}
]
`
}

// DecomposeQuery 将复杂查询分解为多个子查询
func (d *TCMQueryDecomposer) DecomposeQuery(ctx context.Context, query string, options map[string]interface{}) (*DecomposedQuery, error) {
	// 检查缓存
	cacheKey := fmt.Sprintf("decomp:%s", utils.MD5(query))
	if cached, found := d.cache.Get(cacheKey); found {
		if decomposed, ok := cached.(*DecomposedQuery); ok {
			return decomposed, nil
		}
	}
	
	// 1. 检测查询复杂度和模式
	isComplex, queryType := d.detectComplexity(query)
	
	// 如果不是复杂查询，则直接返回包含单个子查询的结果
	if !isComplex {
		result := &DecomposedQuery{
			OriginalQuery: query,
			SubQueries: []SubQuery{
				{
					ID:            "q1",
					Text:          query,
					StartPosition: 0,
					EndPosition:   len(query),
					Weight:        1.0,
					Domain:        "tcm",
					Type:          queryType,
				},
			},
			QueryGraph: map[string][]string{"q1": {}},
		}
		
		// 缓存结果
		d.cache.Set(cacheKey, result, 0)
		
		return result, nil
	}
	
	// 2. 根据查询类型选择分解模板
	templateKey := "default"
	if strings.Contains(queryType, "symptom") {
		templateKey = "symptom"
	} else if strings.Contains(queryType, "treatment") {
		templateKey = "treatment"
	}
	
	// 3. 使用LLM服务进行查询分解
	decomposedResult, err := d.decomposeByChatLLM(ctx, query, templateKey)
	if err != nil {
		d.logger.Warn("LLM查询分解失败，回退到规则分解", "error", err)
		// 回退到规则分解
		decomposedResult, err = d.decomposeByRules(query, queryType)
		if err != nil {
			return nil, fmt.Errorf("查询分解失败: %w", err)
		}
	}
	
	// 4. 构建查询关系图
	d.buildQueryGraph(decomposedResult)
	
	// 5. 缓存结果
	d.cache.Set(cacheKey, decomposedResult, 0)
	
	return decomposedResult, nil
}

// detectComplexity 检测查询的复杂度和类型
func (d *TCMQueryDecomposer) detectComplexity(query string) (bool, string) {
	// 检测查询字数，超过一定长度认为可能是复杂查询
	isComplex := len([]rune(query)) > 30
	
	// 检测是否包含多个问题
	if strings.Count(query, "?") > 1 || strings.Count(query, "？") > 1 {
		isComplex = true
	}
	
	// 检测是否包含连接词，表示多个问题或方面
	connectingWords := []string{"和", "与", "以及", "同时", "另外", "此外", "除了", "还有"}
	for _, word := range connectingWords {
		if strings.Contains(query, word) {
			isComplex = true
			break
		}
	}
	
	// 检测查询类型
	queryType := "general"
	
	// 症状相关查询
	symptomPatterns := []string{"症状", "表现", "感觉", "疼痛", "不适", "问题"}
	for _, pattern := range symptomPatterns {
		if strings.Contains(query, pattern) {
			queryType = "symptom"
			break
		}
	}
	
	// 治疗相关查询
	treatmentPatterns := []string{"治疗", "方法", "调理", "改善", "处理", "缓解", "方剂", "药方"}
	for _, pattern := range treatmentPatterns {
		if strings.Contains(query, pattern) {
			queryType = "treatment"
			break
		}
	}
	
	// 理论相关查询
	theoryPatterns := []string{"理论", "学说", "机制", "原理", "阴阳", "五行", "脏腑"}
	for _, pattern := range theoryPatterns {
		if strings.Contains(query, pattern) {
			queryType = "theory"
			break
		}
	}
	
	// 使用模式检测器进一步精确检测
	if d.patternDetector != nil {
		patternType := d.patternDetector.DetectPattern(query)
		if patternType != "" {
			queryType = patternType
		}
	}
	
	return isComplex, queryType
}

// decomposeByChatLLM 使用ChatLLM进行查询分解
func (d *TCMQueryDecomposer) decomposeByChatLLM(ctx context.Context, query string, templateKey string) (*DecomposedQuery, error) {
	if d.llmService == nil {
		return nil, fmt.Errorf("LLM服务未初始化")
	}
	
	// 获取模板
	template, ok := d.decompositionTemplates[templateKey]
	if !ok {
		template = d.decompositionTemplates["default"]
	}
	
	// 替换模板中的查询
	prompt := strings.ReplaceAll(template, "{{.query}}", query)
	
	// 调用LLM服务
	response, err := d.llmService.Complete(ctx, prompt, map[string]interface{}{
		"temperature":     0.3,
		"max_tokens":      1000,
		"response_format": "json",
	})
	
	if err != nil {
		return nil, fmt.Errorf("LLM调用失败: %w", err)
	}
	
	// 解析响应中的JSON
	var subQueries []SubQuery
	if err := utils.ExtractJSONFromText(response, &subQueries); err != nil {
		return nil, fmt.Errorf("解析LLM响应失败: %w", err)
	}
	
	// 设置子查询的位置信息
	for i := range subQueries {
		// 在原始查询中查找子查询文本的位置
		position := strings.Index(query, subQueries[i].Text)
		if position != -1 {
			subQueries[i].StartPosition = position
			subQueries[i].EndPosition = position + len(subQueries[i].Text)
		} else {
			// 如果找不到精确匹配，则设置为-1
			subQueries[i].StartPosition = -1
			subQueries[i].EndPosition = -1
		}
		
		// 确保ID存在
		if subQueries[i].ID == "" {
			subQueries[i].ID = fmt.Sprintf("q%d", i+1)
		}
		
		// 确保权重存在且有效
		if subQueries[i].Weight <= 0 {
			subQueries[i].Weight = 1.0
		}
	}
	
	return &DecomposedQuery{
		OriginalQuery: query,
		SubQueries:    subQueries,
	}, nil
}

// decomposeByRules 使用规则进行查询分解
func (d *TCMQueryDecomposer) decomposeByRules(query string, queryType string) (*DecomposedQuery, error) {
	var subQueries []SubQuery
	
	// 根据标点符号分割
	parts := utils.SplitByPunctuation(query, []string{"。", "？", "！", "；", "，"})
	
	// 如果没有分隔成多部分，尝试按关键连接词分割
	if len(parts) <= 1 {
		parts = utils.SplitByKeywords(query, []string{"和", "与", "以及", "同时", "另外", "此外", "除了", "还有"})
	}
	
	// 如果仍然没有分隔成多部分，则将整个查询作为一个子查询
	if len(parts) <= 1 {
		subQueries = append(subQueries, SubQuery{
			ID:            "q1",
			Text:          query,
			StartPosition: 0,
			EndPosition:   len(query),
			Weight:        1.0,
			Domain:        "tcm",
			Type:          queryType,
		})
	} else {
		// 将每个部分作为一个子查询
		startPos := 0
		for i, part := range parts {
			// 跳过空部分
			if strings.TrimSpace(part) == "" {
				continue
			}
			
			// 查找部分在原始查询中的位置
			position := strings.Index(query[startPos:], part)
			if position != -1 {
				position += startPos
				startPos = position + len(part)
				
				subQueries = append(subQueries, SubQuery{
					ID:            fmt.Sprintf("q%d", i+1),
					Text:          part,
					StartPosition: position,
					EndPosition:   position + len(part),
					Weight:        1.0,
					Domain:        "tcm",
					Type:          d.inferSubQueryType(part, queryType),
				})
			}
		}
	}
	
	// 调整权重，确保总和为1
	totalWeight := 0.0
	for _, sq := range subQueries {
		totalWeight += sq.Weight
	}
	
	if totalWeight > 0 {
		for i := range subQueries {
			subQueries[i].Weight /= totalWeight
		}
	}
	
	return &DecomposedQuery{
		OriginalQuery: query,
		SubQueries:    subQueries,
	}, nil
}

// inferSubQueryType 推断子查询类型
func (d *TCMQueryDecomposer) inferSubQueryType(text string, parentType string) string {
	// 先检查是否符合特定的类型模式
	symptomPatterns := []string{"症状", "表现", "感觉", "疼痛", "不适", "问题"}
	for _, pattern := range symptomPatterns {
		if strings.Contains(text, pattern) {
			return "symptom"
		}
	}
	
	treatmentPatterns := []string{"治疗", "方法", "调理", "改善", "处理", "缓解", "方剂", "药方"}
	for _, pattern := range treatmentPatterns {
		if strings.Contains(text, pattern) {
			return "treatment"
		}
	}
	
	theoryPatterns := []string{"理论", "学说", "机制", "原理", "阴阳", "五行", "脏腑"}
	for _, pattern := range theoryPatterns {
		if strings.Contains(text, pattern) {
			return "theory"
		}
	}
	
	// 如果找不到特定类型，则继承父查询类型
	return parentType
}

// buildQueryGraph 构建查询关系图
func (d *TCMQueryDecomposer) buildQueryGraph(query *DecomposedQuery) {
	// 初始化关系图
	graph := make(map[string][]string)
	
	// 初始时，每个节点都没有相关节点
	for _, sq := range query.SubQueries {
		graph[sq.ID] = []string{}
	}
	
	// 计算子查询之间的相关性
	for i, sq1 := range query.SubQueries {
		for j, sq2 := range query.SubQueries {
			// 避免自身关联
			if i == j {
				continue
			}
			
			// 检查两个子查询是否相关
			if d.areRelated(sq1, sq2) {
				graph[sq1.ID] = append(graph[sq1.ID], sq2.ID)
			}
		}
	}
	
	query.QueryGraph = graph
}

// areRelated 检查两个子查询是否相关
func (d *TCMQueryDecomposer) areRelated(sq1, sq2 SubQuery) bool {
	// 检查是否有共同的关键词
	sq1Keywords := utils.ExtractKeywords(sq1.Text)
	sq2Keywords := utils.ExtractKeywords(sq2.Text)
	
	commonKeywords := utils.IntersectStrings(sq1Keywords, sq2Keywords)
	
	// 如果有共同关键词，则认为相关
	if len(commonKeywords) > 0 {
		return true
	}
	
	// 如果类型相同，可能相关
	if sq1.Type == sq2.Type && sq1.Type != "general" {
		return true
	}
	
	// 如果位置相邻，可能相关
	if sq1.EndPosition == sq2.StartPosition || sq2.EndPosition == sq1.StartPosition {
		return true
	}
	
	return false
} 