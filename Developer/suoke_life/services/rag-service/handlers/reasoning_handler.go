package handlers

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/suoke/suoke_life/services/rag-service/factory"
	"github.com/suoke/suoke_life/services/rag-service/internal/models"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils"
	"github.com/suoke/suoke_life/services/rag-service/rag"
)

// ReasoningRequest 推理请求
type ReasoningRequest struct {
	// 查询文本
	Query string `json:"query" binding:"required"`
	
	// 用户ID
	UserID string `json:"user_id,omitempty"`
	
	// 查询领域
	Domain string `json:"domain,omitempty"`
	
	// 是否使用复杂查询分解
	UseDecomposition bool `json:"use_decomposition,omitempty"`
	
	// 最大检索结果数量
	MaxResults int `json:"max_results,omitempty"`
	
	// 最大推理次数
	MaxReasoningSteps int `json:"max_reasoning_steps,omitempty"`
	
	// 是否使用缓存
	UseCache bool `json:"use_cache,omitempty"`
	
	// 中医专用查询选项
	TCMOptions *TCMReasoningOptions `json:"tcm_options,omitempty"`
	
	// 多模态选项
	MultimodalOptions *MultimodalOptions `json:"multimodal_options,omitempty"`
	
	// 额外选项
	ExtraOptions map[string]interface{} `json:"extra_options,omitempty"`
}

// TCMReasoningOptions 中医推理选项
type TCMReasoningOptions struct {
	// 辨证要求
	PatternDifferentiationRequirements []string `json:"pattern_differentiation_requirements,omitempty"`
	
	// 方剂推荐要求
	PrescriptionRequirements []string `json:"prescription_requirements,omitempty"`
	
	// 包含四诊数据
	IncludeFourDiagnosticData bool `json:"include_four_diagnostic_data,omitempty"`
	
	// 四诊数据
	FourDiagnosticData map[string]interface{} `json:"four_diagnostic_data,omitempty"`
	
	// 是否包含推理过程
	IncludeReasoningProcess bool `json:"include_reasoning_process,omitempty"`
}

// ReasoningStep 推理步骤
type ReasoningStep struct {
	// 步骤名称
	Name string `json:"name"`
	
	// 推理问题
	Question string `json:"question"`
	
	// 检索结果
	RetrievedResults []models.SearchResult `json:"retrieved_results,omitempty"`
	
	// 推理过程
	ReasoningProcess string `json:"reasoning_process,omitempty"`
	
	// 中间结论
	Conclusion string `json:"conclusion"`
	
	// 置信度
	Confidence float64 `json:"confidence"`
	
	// 持续时间
	Duration time.Duration `json:"duration,omitempty"`
}

// ReasoningResponse 推理响应
type ReasoningResponse struct {
	// 最终回答
	Answer string `json:"answer"`
	
	// 推理步骤
	Steps []ReasoningStep `json:"steps,omitempty"`
	
	// 引用的资料
	References []models.SearchResult `json:"references,omitempty"`
	
	// 置信度
	Confidence float64 `json:"confidence"`
	
	// 统计信息
	Stats map[string]interface{} `json:"stats,omitempty"`
	
	// 错误信息
	Error string `json:"error,omitempty"`
}

// ReasoningHandler 推理处理器
type ReasoningHandler struct {
	// 组件工厂
	factory *factory.ComponentFactory
	
	// 日志器
	logger utils.Logger
	
	// 缓存管理器
	cacheManager utils.CacheManager
	
	// LLM服务
	llmService utils.LLMService
	
	// 超时时间
	timeout time.Duration
}

// NewReasoningHandler 创建推理处理器
func NewReasoningHandler(factoryInstance *factory.ComponentFactory, llmService utils.LLMService, logger utils.Logger, cacheManager utils.CacheManager) *ReasoningHandler {
	if logger == nil {
		logger = utils.NewNoopLogger()
	}
	
	if cacheManager == nil {
		cacheManager = utils.NewNoopCacheManager()
	}
	
	return &ReasoningHandler{
		factory:      factoryInstance,
		llmService:   llmService,
		logger:       logger,
		cacheManager: cacheManager,
		timeout:      60 * time.Second,
	}
}

// HandleReasoning 处理推理请求
func (h *ReasoningHandler) HandleReasoning(c *gin.Context) {
	var request ReasoningRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": fmt.Sprintf("无效的请求参数: %v", err)})
		return
	}
	
	// 设置默认值
	if request.MaxResults <= 0 {
		request.MaxResults = 10
	}
	
	if request.MaxReasoningSteps <= 0 {
		request.MaxReasoningSteps = 3
	}
	
	if request.ExtraOptions == nil {
		request.ExtraOptions = make(map[string]interface{})
	}
	
	// 生成缓存键
	cacheKey := h.generateCacheKey(request)
	
	// 检查缓存
	if request.UseCache {
		if cachedData, found := h.cacheManager.Get(cacheKey); found {
			var response ReasoningResponse
			if err := json.Unmarshal([]byte(cachedData), &response); err == nil {
				c.JSON(http.StatusOK, response)
				return
			}
		}
	}
	
	// 创建上下文
	ctx, cancel := context.WithTimeout(context.Background(), h.timeout)
	defer cancel()
	
	// 执行推理
	response, err := h.performReasoning(ctx, request)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("推理失败: %v", err)})
		return
	}
	
	// 缓存结果
	if request.UseCache {
		if respData, err := json.Marshal(response); err == nil {
			h.cacheManager.Set(cacheKey, string(respData), 30*time.Minute)
		}
	}
	
	c.JSON(http.StatusOK, response)
}

// performReasoning 执行推理
func (h *ReasoningHandler) performReasoning(ctx context.Context, request ReasoningRequest) (*ReasoningResponse, error) {
	startTime := time.Now()
	
	// 创建响应
	response := &ReasoningResponse{
		Steps:      make([]ReasoningStep, 0),
		References: make([]models.SearchResult, 0),
		Stats:      make(map[string]interface{}),
	}
	
	// 检查是否需要进行查询分解
	var decomposedQuery *rag.DecomposedQuery
	var err error
	
	if request.UseDecomposition {
		// 获取查询分解器
		decomposer, err := h.factory.GetQueryDecomposer("tcm")
		if err != nil {
			h.logger.Warn("获取查询分解器失败，将使用原始查询", "error", err)
		} else {
			// 执行查询分解
			decomposedQuery, err = decomposer.DecomposeQuery(ctx, request.Query, map[string]interface{}{
				"domain":  request.Domain,
				"user_id": request.UserID,
			})
			
			if err != nil {
				h.logger.Warn("查询分解失败，将使用原始查询", "error", err)
			} else {
				response.Stats["sub_queries_count"] = len(decomposedQuery.SubQueries)
				h.logger.Info("查询已分解", "original", request.Query, "count", len(decomposedQuery.SubQueries))
			}
		}
	}
	
	if decomposedQuery == nil {
		// 如果没有分解，创建一个包含原始查询的分解
		decomposedQuery = &rag.DecomposedQuery{
			OriginalQuery: request.Query,
			SubQueries: []rag.SubQuery{
				{
					ID:            "q1",
					Text:          request.Query,
					StartPosition: 0,
					EndPosition:   len(request.Query),
					Weight:        1.0,
					Domain:        request.Domain,
					Type:          "general",
				},
			},
			QueryGraph: map[string][]string{"q1": {}},
		}
	}
	
	// 针对分解的每个子查询进行推理
	subQueryResults := make(map[string][]models.SearchResult)
	
	// 对每个子查询执行检索
	for _, subQuery := range decomposedQuery.SubQueries {
		step := ReasoningStep{
			Name:      fmt.Sprintf("检索子查询: %s", subQuery.ID),
			Question:  subQuery.Text,
			Confidence: 0.0,
		}
		
		stepStart := time.Now()
		
		// 执行检索
		results, err := h.retrieveForSubQuery(ctx, subQuery, request)
		
		step.Duration = time.Since(stepStart)
		
		if err != nil {
			h.logger.Warn("子查询检索失败", "subQuery", subQuery.Text, "error", err)
			step.Conclusion = fmt.Sprintf("检索失败: %v", err)
			step.Confidence = 0.0
		} else {
			step.RetrievedResults = results
			step.Conclusion = fmt.Sprintf("检索到%d条相关信息", len(results))
			step.Confidence = h.calculateResultsConfidence(results)
			
			// 保存子查询结果
			subQueryResults[subQuery.ID] = results
		}
		
		response.Steps = append(response.Steps, step)
	}
	
	// 合并检索结果
	var mergedResults []models.SearchResult
	
	if len(subQueryResults) > 0 {
		// 获取结果合并器
		resultMerger, err := h.factory.GetResultMerger("weighted")
		if err != nil {
			return nil, fmt.Errorf("获取结果合并器失败: %w", err)
		}
		
		// 执行结果合并
		mergedResults, err = resultMerger.MergeResults(ctx, decomposedQuery, subQueryResults, map[string]interface{}{
			"top_k":                   request.MaxResults,
			"user_id":                 request.UserID,
			"deduplication_threshold": 0.85,
		})
		
		if err != nil {
			return nil, fmt.Errorf("结果合并失败: %w", err)
		}
		
		response.Stats["merged_results_count"] = len(mergedResults)
	}
	
	// 使用合并后的结果进行推理
	reasoningStep := ReasoningStep{
		Name:     "基于检索结果的推理",
		Question: request.Query,
	}
	
	reasoningStart := time.Now()
	
	// 执行推理
	answer, reasoning, confidence, err := h.reasonWithRetrievedResults(ctx, request.Query, mergedResults, request)
	
	reasoningStep.Duration = time.Since(reasoningStart)
	
	if err != nil {
		reasoningStep.Conclusion = fmt.Sprintf("推理失败: %v", err)
		reasoningStep.Confidence = 0.0
	} else {
		reasoningStep.ReasoningProcess = reasoning
		reasoningStep.Conclusion = answer
		reasoningStep.Confidence = confidence
	}
	
	response.Steps = append(response.Steps, reasoningStep)
	
	// 设置最终答案
	response.Answer = answer
	response.Confidence = confidence
	
	// 添加引用
	response.References = h.selectTopReferences(mergedResults, 5)
	
	// 添加统计信息
	response.Stats["total_duration"] = time.Since(startTime).String()
	response.Stats["steps_count"] = len(response.Steps)
	
	return response, nil
}

// retrieveForSubQuery 执行子查询检索
func (h *ReasoningHandler) retrieveForSubQuery(ctx context.Context, subQuery rag.SubQuery, request ReasoningRequest) ([]models.SearchResult, error) {
	// 检查是否有中医特定需求
	isTCMQuery := false
	var tcmOptions map[string]interface{}
	
	if request.Domain == "tcm" || subQuery.Domain == "tcm" {
		isTCMQuery = true
	}
	
	if request.TCMOptions != nil {
		isTCMQuery = true
		tcmOptions = map[string]interface{}{
			"pattern_requirements":   request.TCMOptions.PatternDifferentiationRequirements,
			"prescription_requirements": request.TCMOptions.PrescriptionRequirements,
			"four_diagnostic_data":   request.TCMOptions.FourDiagnosticData,
		}
	}
	
	// 获取查询分析器
	queryAnalyzer, err := h.factory.GetQueryAnalyzer("simple")
	if err != nil {
		return nil, fmt.Errorf("获取查询分析器失败: %w", err)
	}
	
	// 分析查询
	analysisResult, err := queryAnalyzer.Analyze(ctx, subQuery.Text)
	if err != nil {
		return nil, fmt.Errorf("分析查询失败: %w", err)
	}
	
	// 如果子查询有明确领域，覆盖分析结果
	if subQuery.Domain != "" {
		switch subQuery.Domain {
		case "tcm", "中医":
			analysisResult.Domain = rag.DomainTCM
		case "nutrition", "营养":
			analysisResult.Domain = rag.DomainNutrition
		case "medicine", "医学":
			analysisResult.Domain = rag.DomainMedicine
		case "agriculture", "农业":
			analysisResult.Domain = rag.DomainAgriculture
		}
	}
	
	// 获取混合搜索器
	hybridSearcher, err := h.factory.GetHybridSearcher("adaptive")
	if err != nil {
		return nil, fmt.Errorf("获取混合搜索器失败: %w", err)
	}
	
	// 获取权重调整器
	weightAdjuster, err := h.factory.GetWeightAdjuster("simple")
	if err != nil {
		h.logger.Warn("获取权重调整器失败，将使用默认权重", "error", err)
	}
	
	// 调整权重
	vectorWeight, keywordWeight := analysisResult.VectorWeight, analysisResult.KeywordWeight
	if weightAdjuster != nil {
		vectorWeight, keywordWeight, err = weightAdjuster.AdjustWeights(ctx, subQuery.Text, analysisResult)
		if err != nil {
			h.logger.Warn("调整权重失败，将使用默认权重", "error", err)
		}
	}
	
	// 执行混合搜索
	searchResults, err := hybridSearcher.Search(ctx, subQuery.Text, request.MaxResults, map[string]interface{}{
		"vector_weight":   vectorWeight,
		"keyword_weight":  keywordWeight,
		"domain":          string(analysisResult.Domain),
		"query_type":      string(analysisResult.Type),
		"keywords":        analysisResult.Keywords,
		"user_id":         request.UserID,
		"tcm_specific":    isTCMQuery,
		"tcm_options":     tcmOptions,
		"multimodal_data": request.MultimodalOptions,
	})
	
	if err != nil {
		return nil, fmt.Errorf("混合搜索失败: %w", err)
	}
	
	// 对结果进行重排序
	if len(searchResults) > 0 {
		reranker, err := h.factory.GetReranker("cross-encoder")
		if err != nil {
			h.logger.Warn("获取重排序器失败，将使用原始结果", "error", err)
		} else {
			// 创建重排序选项
			options := map[string]interface{}{
				"top_k":           request.MaxResults,
				"user_id":         request.UserID,
				"domain":          string(analysisResult.Domain),
				"tcm_specific":    isTCMQuery,
				"tcm_options":     tcmOptions,
				"include_metadata": true,
			}
			
			// 执行重排序
			rerankedResults, rerankErr := reranker.Rerank(ctx, subQuery.Text, searchResults, options)
			if rerankErr != nil {
				h.logger.Warn("重排序失败，将使用原始结果", "error", rerankErr)
			} else {
				searchResults = rerankedResults
			}
		}
	}
	
	return searchResults, nil
}

// reasonWithRetrievedResults 基于检索结果进行推理
func (h *ReasoningHandler) reasonWithRetrievedResults(ctx context.Context, query string, results []models.SearchResult, request ReasoningRequest) (string, string, float64, error) {
	if h.llmService == nil {
		return "", "", 0.0, fmt.Errorf("LLM服务未初始化")
	}
	
	// 构建上下文
	context := h.buildReasoningContext(query, results, request)
	
	// 确定是否需要中医专业推理
	promptTemplate := h.getReasoningPrompt(query, request)
	
	// 调用LLM
	llmRequest := map[string]interface{}{
		"temperature":     0.3,
		"max_tokens":      2000,
		"response_format": "json",
	}
	
	if request.TCMOptions != nil && request.TCMOptions.IncludeReasoningProcess {
		llmRequest["response_format"] = "text"
	}
	
	response, err := h.llmService.Complete(ctx, context+"\n\n"+promptTemplate, llmRequest)
	if err != nil {
		return "", "", 0.0, fmt.Errorf("LLM调用失败: %w", err)
	}
	
	// 解析响应
	if request.TCMOptions != nil && request.TCMOptions.IncludeReasoningProcess {
		// 提取答案和推理过程
		answer, reasoning, confidence := h.extractAnswerAndReasoning(response)
		return answer, reasoning, confidence, nil
	} else {
		// 解析JSON响应
		var responseData struct {
			Answer     string  `json:"answer"`
			Reasoning  string  `json:"reasoning"`
			Confidence float64 `json:"confidence"`
		}
		
		if err := utils.ExtractJSONFromText(response, &responseData); err != nil {
			// 尝试直接返回响应文本
			return response, "", 0.7, nil
		}
		
		return responseData.Answer, responseData.Reasoning, responseData.Confidence, nil
	}
}

// buildReasoningContext 构建推理上下文
func (h *ReasoningHandler) buildReasoningContext(query string, results []models.SearchResult, request ReasoningRequest) string {
	var context strings.Builder
	
	context.WriteString(fmt.Sprintf("用户查询: %s\n\n", query))
	context.WriteString("检索到的相关知识：\n")
	
	for i, result := range results {
		context.WriteString(fmt.Sprintf("[%d] %s\n", i+1, result.Content))
		if result.Source != "" {
			context.WriteString(fmt.Sprintf("来源: %s\n", result.Source))
		}
		context.WriteString("\n")
	}
	
	// 如果有中医四诊数据，添加到上下文
	if request.TCMOptions != nil && request.TCMOptions.IncludeFourDiagnosticData && request.TCMOptions.FourDiagnosticData != nil {
		context.WriteString("四诊相关信息：\n")
		
		// 根据四诊数据类型添加信息
		if tongue, ok := request.TCMOptions.FourDiagnosticData["tongue"].(map[string]interface{}); ok {
			context.WriteString("舌诊信息：\n")
			for k, v := range tongue {
				context.WriteString(fmt.Sprintf("- %s: %v\n", k, v))
			}
			context.WriteString("\n")
		}
		
		if face, ok := request.TCMOptions.FourDiagnosticData["face"].(map[string]interface{}); ok {
			context.WriteString("面诊信息：\n")
			for k, v := range face {
				context.WriteString(fmt.Sprintf("- %s: %v\n", k, v))
			}
			context.WriteString("\n")
		}
		
		if pulse, ok := request.TCMOptions.FourDiagnosticData["pulse"].(map[string]interface{}); ok {
			context.WriteString("脉诊信息：\n")
			for k, v := range pulse {
				context.WriteString(fmt.Sprintf("- %s: %v\n", k, v))
			}
			context.WriteString("\n")
		}
	}
	
	return context.String()
}

// getReasoningPrompt 获取推理提示
func (h *ReasoningHandler) getReasoningPrompt(query string, request ReasoningRequest) string {
	// 默认提示
	defaultPrompt := `
请基于上述检索到的知识，为用户查询提供准确、有根据的回答。

要求：
1. 回答要基于检索到的知识，尽量不使用自己的知识
2. 如果检索到的知识不足以回答问题，请明确说明
3. 如果检索到的知识有矛盾，请指出矛盾并解释
4. 回答要简洁清晰，重点突出
5. 必须给出推理过程，说明如何从检索知识得出结论

请以JSON格式输出：
{
  "answer": "最终回答",
  "reasoning": "推理过程",
  "confidence": 0.8  // 置信度，0到1之间
}
`

	// 中医专业提示
	tcmPrompt := `
作为中医专业助手，请基于上述检索到的知识和四诊信息，为用户查询提供专业的中医分析和建议。

要求：
1. 回答必须遵循中医理论体系，基于检索到的知识
2. 应用辨证论治方法，分析病机，辨别证型
3. 结合四诊数据进行分析
4. 如有必要，提供具体的方剂推荐或养生建议
5. 解释推理过程和治疗原理

分析步骤：
1. 症状归纳与分析
2. 证型辨别
3. 治疗原则
4. 方剂推荐或调理建议

请输出：
```
【辨证分析】
（详细的辨证过程）

【证型结论】
（明确的证型判断）

【治疗建议】
（具体的治疗或调理建议）

【方剂推荐】
（适用的方剂及其组成、功效）

【信心水平】
（对结论的确信度，1-10分）
```
`

	// 根据请求类型选择提示
	if request.Domain == "tcm" || (request.TCMOptions != nil && request.TCMOptions.IncludeReasoningProcess) {
		return tcmPrompt
	}
	
	return defaultPrompt
}

// extractAnswerAndReasoning 从文本响应中提取答案和推理过程
func (h *ReasoningHandler) extractAnswerAndReasoning(text string) (string, string, float64) {
	// 尝试提取结构化信息
	var answer, reasoning string
	var confidence float64 = 0.7
	
	// 提取辨证分析
	reasoningStart := strings.Index(text, "【辨证分析】")
	if reasoningStart != -1 {
		reasoningEnd := strings.Index(text[reasoningStart:], "【证型结论】")
		if reasoningEnd != -1 {
			reasoning = strings.TrimSpace(text[reasoningStart+len("【辨证分析】"):reasoningStart+reasoningEnd])
		}
	}
	
	// 提取证型结论和治疗建议
	conclusionStart := strings.Index(text, "【证型结论】")
	if conclusionStart != -1 {
		conclusionEnd := strings.Index(text[conclusionStart:], "【治疗建议】")
		if conclusionEnd != -1 {
			conclusion := strings.TrimSpace(text[conclusionStart+len("【证型结论】"):conclusionStart+conclusionEnd])
			
			// 提取治疗建议
			treatmentStart := conclusionStart + conclusionEnd
			treatmentEnd := strings.Index(text[treatmentStart:], "【方剂推荐】")
			
			var treatment string
			if treatmentEnd != -1 {
				treatment = strings.TrimSpace(text[treatmentStart+len("【治疗建议】"):treatmentStart+treatmentEnd])
			} else {
				treatment = strings.TrimSpace(text[treatmentStart+len("【治疗建议】"):])
			}
			
			// 组合答案
			answer = fmt.Sprintf("证型：%s\n\n治疗建议：%s", conclusion, treatment)
		}
	}
	
	// 提取信心水平
	confidenceStart := strings.Index(text, "【信心水平】")
	if confidenceStart != -1 {
		confidenceText := text[confidenceStart+len("【信心水平】"):]
		var confidenceValue int
		if _, err := fmt.Sscanf(confidenceText, "%d", &confidenceValue); err == nil {
			if confidenceValue >= 1 && confidenceValue <= 10 {
				confidence = float64(confidenceValue) / 10.0
			}
		}
	}
	
	// 如果没有提取出结构化信息，使用整个文本作为答案
	if answer == "" {
		answer = text
	}
	
	return answer, reasoning, confidence
}

// calculateResultsConfidence 计算检索结果的置信度
func (h *ReasoningHandler) calculateResultsConfidence(results []models.SearchResult) float64 {
	if len(results) == 0 {
		return 0.0
	}
	
	// 基于前三个结果的分数计算置信度
	topCount := 3
	if len(results) < topCount {
		topCount = len(results)
	}
	
	var totalScore float64
	for i := 0; i < topCount; i++ {
		totalScore += results[i].Score
	}
	
	// 计算平均分数并缩放到0-1范围
	averageScore := totalScore / float64(topCount)
	
	// 假设分数范围在0-1之间，如果不是，需要调整
	if averageScore > 1.0 {
		averageScore = 1.0
	}
	
	return averageScore
}

// selectTopReferences 选择最重要的引用
func (h *ReasoningHandler) selectTopReferences(results []models.SearchResult, count int) []models.SearchResult {
	if len(results) <= count {
		return results
	}
	
	// 复制前count个结果
	references := make([]models.SearchResult, count)
	copy(references, results[:count])
	
	// 简化引用内容
	for i := range references {
		references[i].Content = utils.TruncateText(references[i].Content, 300)
	}
	
	return references
}

// generateCacheKey 生成缓存键
func (h *ReasoningHandler) generateCacheKey(request ReasoningRequest) string {
	return fmt.Sprintf("reasoning:%s:%s:%t:%d", 
		request.Query, 
		request.Domain, 
		request.UseDecomposition, 
		request.MaxResults)
}

// RegisterRoutes 注册路由
func (h *ReasoningHandler) RegisterRoutes(router *gin.Engine) {
	router.POST("/api/reasoning", h.HandleReasoning)
}