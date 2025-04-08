package rag

import (
	"context"
	"fmt"
	"math"
	"sort"
	"strings"

	"github.com/suoke/suoke_life/services/rag-service/internal/models"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils"
)

// MergedResult 合并结果
type MergedResult struct {
	// 分数
	Score float64 `json:"score"`
	
	// 搜索结果
	Result models.SearchResult `json:"result"`
	
	// 来源子查询
	SourceQueries []string `json:"source_queries"`
	
	// 相关性分数
	RelevanceScores map[string]float64 `json:"relevance_scores,omitempty"`
}

// ResultMerger 结果合并器接口
type ResultMerger interface {
	// MergeResults 合并多个子查询的结果
	MergeResults(ctx context.Context, decomposedQuery *DecomposedQuery, subQueryResults map[string][]models.SearchResult, options map[string]interface{}) ([]models.SearchResult, error)
	
	// Name 返回合并器名称
	Name() string
	
	// Initialize 初始化合并器
	Initialize(ctx context.Context) error
	
	// Close 关闭合并器
	Close() error
}

// WeightedResultMerger 加权结果合并器
type WeightedResultMerger struct {
	// 日志器
	logger utils.Logger
	
	// 去重阈值
	deduplicationThreshold float64
	
	// LLM服务
	llmService utils.LLMService
	
	// 是否使用LLM进行结果重新排序
	useLLMReranking bool
}

// NewWeightedResultMerger 创建加权结果合并器
func NewWeightedResultMerger(llmService utils.LLMService, logger utils.Logger) *WeightedResultMerger {
	if logger == nil {
		logger = utils.NewNoopLogger()
	}
	
	return &WeightedResultMerger{
		logger:                 logger,
		deduplicationThreshold: 0.85, // 默认去重阈值
		llmService:             llmService,
		useLLMReranking:        llmService != nil,
	}
}

// Name 返回合并器名称
func (m *WeightedResultMerger) Name() string {
	return "weighted-result-merger"
}

// Initialize 初始化合并器
func (m *WeightedResultMerger) Initialize(ctx context.Context) error {
	m.logger.Info("初始化加权结果合并器完成")
	return nil
}

// Close 关闭合并器
func (m *WeightedResultMerger) Close() error {
	return nil
}

// MergeResults 合并多个子查询的结果
func (m *WeightedResultMerger) MergeResults(ctx context.Context, decomposedQuery *DecomposedQuery, subQueryResults map[string][]models.SearchResult, options map[string]interface{}) ([]models.SearchResult, error) {
	// 提取选项
	topK := 10
	if k, ok := options["top_k"].(int); ok && k > 0 {
		topK = k
	}
	
	dedupeThreshold := m.deduplicationThreshold
	if t, ok := options["deduplication_threshold"].(float64); ok && t > 0 {
		dedupeThreshold = t
	}
	
	// 1. 合并所有结果
	mergedResults := make(map[string]*MergedResult)
	
	for queryID, results := range subQueryResults {
		// 获取子查询权重
		var queryWeight float64 = 1.0
		for _, subQuery := range decomposedQuery.SubQueries {
			if subQuery.ID == queryID {
				queryWeight = subQuery.Weight
				break
			}
		}
		
		// 处理每个结果
		for _, result := range results {
			resultID := result.ID
			
			// 如果是新结果，创建新条目
			if _, exists := mergedResults[resultID]; !exists {
				mergedResults[resultID] = &MergedResult{
					Score:           result.Score * queryWeight,
					Result:          result,
					SourceQueries:   []string{queryID},
					RelevanceScores: map[string]float64{queryID: result.Score},
				}
			} else {
				// 如果已存在，更新分数和来源
				mergedResults[resultID].Score += result.Score * queryWeight
				mergedResults[resultID].SourceQueries = append(mergedResults[resultID].SourceQueries, queryID)
				mergedResults[resultID].RelevanceScores[queryID] = result.Score
			}
		}
	}
	
	// 2. 去重（合并相似结果）
	deduplicatedResults := m.deduplicateResults(mergedResults, dedupeThreshold)
	
	// 3. 转换为SearchResult数组并排序
	finalResults := make([]models.SearchResult, 0, len(deduplicatedResults))
	for _, merged := range deduplicatedResults {
		result := merged.Result
		result.Score = merged.Score
		
		// 增强元数据
		if result.Metadata.Properties == nil {
			result.Metadata.Properties = make(map[string]interface{})
		}
		result.Metadata.Properties["source_queries"] = merged.SourceQueries
		result.Metadata.Properties["relevance_scores"] = merged.RelevanceScores
		
		finalResults = append(finalResults, result)
	}
	
	// 4. 排序结果
	sort.Slice(finalResults, func(i, j int) bool {
		return finalResults[i].Score > finalResults[j].Score
	})
	
	// 5. 使用LLM重新排序（如果启用）
	if m.useLLMReranking {
		llmRankedResults, err := m.rerankWithLLM(ctx, decomposedQuery.OriginalQuery, finalResults)
		if err != nil {
			m.logger.Warn("LLM重排序失败，使用原始排序", "error", err)
		} else {
			finalResults = llmRankedResults
		}
	}
	
	// 6. 截取前topK个结果
	if len(finalResults) > topK {
		finalResults = finalResults[:topK]
	}
	
	// 7. 增强摘要和内容
	m.enhanceResults(ctx, decomposedQuery, finalResults)
	
	return finalResults, nil
}

// deduplicateResults 去重结果（合并相似结果）
func (m *WeightedResultMerger) deduplicateResults(results map[string]*MergedResult, threshold float64) []*MergedResult {
	// 转换为数组
	resultArray := make([]*MergedResult, 0, len(results))
	for _, result := range results {
		resultArray = append(resultArray, result)
	}
	
	// 按分数排序
	sort.Slice(resultArray, func(i, j int) bool {
		return resultArray[i].Score > resultArray[j].Score
	})
	
	// 标记已合并的结果
	merged := make([]bool, len(resultArray))
	
	// 去重后的结果
	deduplicatedResults := make([]*MergedResult, 0, len(resultArray))
	
	for i := 0; i < len(resultArray); i++ {
		// 如果已经被合并，跳过
		if merged[i] {
			continue
		}
		
		// 将当前结果添加到去重结果中
		deduplicatedResults = append(deduplicatedResults, resultArray[i])
		
		// 查找相似的结果并合并
		for j := i + 1; j < len(resultArray); j++ {
			if merged[j] {
				continue
			}
			
			// 计算内容相似度
			similarity := utils.TextSimilarity(
				resultArray[i].Result.Content,
				resultArray[j].Result.Content,
			)
			
			// 如果相似度高于阈值，合并
			if similarity >= threshold {
				// 合并来源查询和相关性分数
				for _, sourceQuery := range resultArray[j].SourceQueries {
					if !utils.ContainsString(resultArray[i].SourceQueries, sourceQuery) {
						resultArray[i].SourceQueries = append(resultArray[i].SourceQueries, sourceQuery)
					}
				}
				
				for queryID, score := range resultArray[j].RelevanceScores {
					// 如果已存在，取最高分
					if existingScore, exists := resultArray[i].RelevanceScores[queryID]; exists {
						if score > existingScore {
							resultArray[i].RelevanceScores[queryID] = score
						}
					} else {
						resultArray[i].RelevanceScores[queryID] = score
					}
				}
				
				// 如果j的分数更高，更新内容
				if resultArray[j].Score > resultArray[i].Score {
					resultArray[i].Result.Content = resultArray[j].Result.Content
					resultArray[i].Result.Source = resultArray[j].Result.Source
				}
				
				// 更新总分（取两者中的较大值，而不是简单相加）
				resultArray[i].Score = math.Max(resultArray[i].Score, resultArray[j].Score)
				
				// 标记j为已合并
				merged[j] = true
			}
		}
	}
	
	return deduplicatedResults
}

// rerankWithLLM 使用LLM重新排序结果
func (m *WeightedResultMerger) rerankWithLLM(ctx context.Context, query string, results []models.SearchResult) ([]models.SearchResult, error) {
	if m.llmService == nil || len(results) <= 1 {
		return results, nil
	}
	
	// 构建提示
	prompt := fmt.Sprintf(`
作为一个专业的中医知识助手，请对以下搜索结果按照与查询的相关性进行排序，返回排序后的结果ID列表。

查询：%s

搜索结果：
`, query)
	
	for i, result := range results {
		prompt += fmt.Sprintf("%d) ID: %s\n内容: %s\n\n", i+1, result.ID, utils.TruncateText(result.Content, 200))
	}
	
	prompt += `
请按照与查询相关性从高到低的顺序，输出结果ID列表。仅需输出ID列表，格式如：
[ID1, ID2, ID3, ...]
`
	
	// 调用LLM
	response, err := m.llmService.Complete(ctx, prompt, map[string]interface{}{
		"temperature":     0.1,
		"max_tokens":      200,
		"response_format": "json",
	})
	
	if err != nil {
		return results, err
	}
	
	// 解析响应中的ID列表
	var idList []string
	if err := utils.ExtractJSONFromText(response, &idList); err != nil {
		return results, err
	}
	
	// 如果ID列表为空，返回原始结果
	if len(idList) == 0 {
		return results, nil
	}
	
	// 创建ID到索引的映射
	idToIndex := make(map[string]int)
	for i, result := range results {
		idToIndex[result.ID] = i
	}
	
	// 根据LLM排序结果重新排序
	sortedResults := make([]models.SearchResult, 0, len(results))
	
	// 首先添加LLM排序中的结果
	for _, id := range idList {
		if idx, exists := idToIndex[id]; exists {
			sortedResults = append(sortedResults, results[idx])
			// 标记为已处理
			idToIndex[id] = -1
		}
	}
	
	// 添加剩余未被LLM排序的结果
	for id, idx := range idToIndex {
		if idx >= 0 {
			sortedResults = append(sortedResults, results[idx])
		}
	}
	
	return sortedResults, nil
}

// enhanceResults 增强结果摘要和内容
func (m *WeightedResultMerger) enhanceResults(ctx context.Context, decomposedQuery *DecomposedQuery, results []models.SearchResult) {
	// 对每个结果进行增强
	for i := range results {
		// 生成更相关的摘要
		if results[i].Snippet == "" {
			results[i].Snippet = m.generateSnippet(ctx, decomposedQuery.OriginalQuery, results[i].Content)
		}
		
		// 如果有元数据，添加子查询信息
		if results[i].Metadata.Properties != nil {
			// 获取与结果相关的所有子查询文本
			var relevantSubQueries []string
			if sourceQueries, ok := results[i].Metadata.Properties["source_queries"].([]string); ok {
				for _, id := range sourceQueries {
					for _, subQuery := range decomposedQuery.SubQueries {
						if subQuery.ID == id {
							relevantSubQueries = append(relevantSubQueries, subQuery.Text)
							break
						}
					}
				}
			}
			
			if len(relevantSubQueries) > 0 {
				results[i].Metadata.Properties["relevant_subqueries"] = relevantSubQueries
			}
		}
	}
}

// generateSnippet 生成摘要
func (m *WeightedResultMerger) generateSnippet(ctx context.Context, query string, content string) string {
	// 简单摘要生成：提取包含查询关键词的句子
	keywords := utils.ExtractKeywords(query)
	
	if len(keywords) == 0 {
		// 如果没有关键词，返回内容的前200个字符作为摘要
		return utils.TruncateText(content, 200)
	}
	
	// 分割内容为句子
	sentences := utils.SplitToSentences(content)
	
	// 对每个句子评分
	type ScoredSentence struct {
		Sentence string
		Score    int
	}
	
	scoredSentences := make([]ScoredSentence, 0, len(sentences))
	
	for _, sentence := range sentences {
		score := 0
		for _, keyword := range keywords {
			if strings.Contains(sentence, keyword) {
				score++
			}
		}
		
		if score > 0 {
			scoredSentences = append(scoredSentences, ScoredSentence{
				Sentence: sentence,
				Score:    score,
			})
		}
	}
	
	// 按分数排序
	sort.Slice(scoredSentences, func(i, j int) bool {
		return scoredSentences[i].Score > scoredSentences[j].Score
	})
	
	// 提取最高分的句子作为摘要，总长度不超过200个字符
	var snippet strings.Builder
	totalLen := 0
	
	for _, scored := range scoredSentences {
		if totalLen+len([]rune(scored.Sentence)) > 200 {
			break
		}
		
		if snippet.Len() > 0 {
			snippet.WriteString(" ")
		}
		
		snippet.WriteString(scored.Sentence)
		totalLen += len([]rune(scored.Sentence))
	}
	
	// 如果没有找到相关句子，返回内容的前200个字符作为摘要
	if snippet.Len() == 0 {
		return utils.TruncateText(content, 200)
	}
	
	return snippet.String()
} 