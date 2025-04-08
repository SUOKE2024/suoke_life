package rag

import (
	"context"
	"encoding/json"
	"fmt"
	"sort"
	"strings"
	"time"

	"github.com/suoke/suoke_life/services/rag-service/internal/models"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils"
)

// 节点类型
type NodeType string

const (
	// 概念节点
	NodeConcept NodeType = "concept"
	
	// 实体节点
	NodeEntity NodeType = "entity"
	
	// 属性节点
	NodeAttribute NodeType = "attribute"
	
	// 关系节点
	NodeRelation NodeType = "relation"
)

// 关系类型
type RelationType string

const (
	// 是一种（继承关系）
	RelationIsA RelationType = "is_a"
	
	// 部分关系
	RelationPartOf RelationType = "part_of"
	
	// 属性关系
	RelationHasProperty RelationType = "has_property"
	
	// 因果关系
	RelationCauses RelationType = "causes"
	
	// 治疗关系
	RelationTreats RelationType = "treats"
	
	// 相关关系
	RelationRelatedTo RelationType = "related_to"
	
	// 被...预防
	RelationPreventedBy RelationType = "prevented_by"
	
	// 被...治疗
	RelationTreatedBy RelationType = "treated_by"
	
	// 是...的症状
	RelationSymptomOf RelationType = "symptom_of"
	
	// 与...禁忌
	RelationContraindicatedWith RelationType = "contraindicated_with"
	
	// 与...相似
	RelationSimilarTo RelationType = "similar_to"
	
	// 通过...诊断
	RelationDiagnosedBy RelationType = "diagnosed_by"
)

// KnowledgeGraphNode 知识图谱节点
type KnowledgeGraphNode struct {
	// 节点ID
	ID string `json:"id"`
	
	// 节点类型
	Type NodeType `json:"type"`
	
	// 节点名称
	Name string `json:"name"`
	
	// 节点描述
	Description string `json:"description,omitempty"`
	
	// 节点属性
	Properties map[string]interface{} `json:"properties,omitempty"`
	
	// 节点嵌入向量
	Embedding []float32 `json:"-"`
	
	// 创建时间
	CreatedAt time.Time `json:"created_at"`
	
	// 更新时间
	UpdatedAt time.Time `json:"updated_at"`
}

// KnowledgeGraphEdge 知识图谱边
type KnowledgeGraphEdge struct {
	// 边ID
	ID string `json:"id"`
	
	// 边类型
	Type RelationType `json:"type"`
	
	// 源节点ID
	SourceID string `json:"source_id"`
	
	// 目标节点ID
	TargetID string `json:"target_id"`
	
	// 边属性
	Properties map[string]interface{} `json:"properties,omitempty"`
	
	// 置信度
	Confidence float64 `json:"confidence"`
	
	// 创建时间
	CreatedAt time.Time `json:"created_at"`
	
	// 更新时间
	UpdatedAt time.Time `json:"updated_at"`
}

// KnowledgeGraphPath 知识图谱路径
type KnowledgeGraphPath struct {
	// 路径节点
	Nodes []KnowledgeGraphNode `json:"nodes"`
	
	// 路径边
	Edges []KnowledgeGraphEdge `json:"edges"`
	
	// 路径相关性分数
	RelevanceScore float64 `json:"relevance_score"`
}

// ReasoningSubgraph 推理子图
type ReasoningSubgraph struct {
	// 子图节点
	Nodes []KnowledgeGraphNode `json:"nodes"`
	
	// 子图边
	Edges []KnowledgeGraphEdge `json:"edges"`
	
	// 子图中心节点
	CentralNodeIDs []string `json:"central_node_ids"`
	
	// 子图相关性分数
	RelevanceScore float64 `json:"relevance_score"`
	
	// 节点特征
	Features map[string]interface{} `json:"features,omitempty"`
}

// KnowledgeGraphQuery 知识图谱查询
type KnowledgeGraphQuery struct {
	// 查询文本
	Text string `json:"text"`
	
	// 起始节点ID
	StartNodeIDs []string `json:"start_node_ids,omitempty"`
	
	// 结束节点ID
	EndNodeIDs []string `json:"end_node_ids,omitempty"`
	
	// 关系类型过滤
	RelationTypes []RelationType `json:"relation_types,omitempty"`
	
	// 最大路径长度
	MaxPathLength int `json:"max_path_length,omitempty"`
	
	// 最大结果数
	MaxResults int `json:"max_results,omitempty"`
	
	// 相关性阈值
	RelevanceThreshold float64 `json:"relevance_threshold,omitempty"`
	
	// 是否使用节点嵌入
	UseEmbedding bool `json:"use_embedding,omitempty"`
	
	// 额外约束
	Constraints map[string]interface{} `json:"constraints,omitempty"`
}

// KnowledgeGraphService 知识图谱服务接口
type KnowledgeGraphService interface {
	// 查询节点
	QueryNodes(ctx context.Context, query string, options map[string]interface{}) ([]KnowledgeGraphNode, error)
	
	// 获取路径
	GetPaths(ctx context.Context, query KnowledgeGraphQuery) ([]KnowledgeGraphPath, error)
	
	// 获取子图
	GetSubgraph(ctx context.Context, query KnowledgeGraphQuery) (*ReasoningSubgraph, error)
	
	// 获取相关实体
	GetRelatedEntities(ctx context.Context, nodeID string, options map[string]interface{}) ([]KnowledgeGraphNode, error)
	
	// 添加节点
	AddNode(ctx context.Context, node KnowledgeGraphNode) (string, error)
	
	// 添加边
	AddEdge(ctx context.Context, edge KnowledgeGraphEdge) (string, error)
	
	// 删除节点
	DeleteNode(ctx context.Context, nodeID string) error
	
	// 删除边
	DeleteEdge(ctx context.Context, edgeID string) error
	
	// 更新节点
	UpdateNode(ctx context.Context, node KnowledgeGraphNode) error
	
	// 更新边
	UpdateEdge(ctx context.Context, edge KnowledgeGraphEdge) error
}

// KGReasoningResult 知识图谱推理结果
type KGReasoningResult struct {
	// 推理结论
	Conclusion string `json:"conclusion"`
	
	// 关键实体
	KeyEntities []KnowledgeGraphNode `json:"key_entities,omitempty"`
	
	// 推理路径
	Paths []KnowledgeGraphPath `json:"paths,omitempty"`
	
	// 推理子图
	Subgraph *ReasoningSubgraph `json:"subgraph,omitempty"`
	
	// 置信度
	Confidence float64 `json:"confidence"`
	
	// 辅助检索结果
	SupportingDocuments []models.SearchResult `json:"supporting_documents,omitempty"`
	
	// 推理过程
	ReasoningProcess string `json:"reasoning_process,omitempty"`
}

// KGReasoningOptions 知识图谱推理选项
type KGReasoningOptions struct {
	// 是否启用路径推理
	EnablePathReasoning bool `json:"enable_path_reasoning"`
	
	// 是否启用子图推理
	EnableSubgraphReasoning bool `json:"enable_subgraph_reasoning"`
	
	// 最大路径长度
	MaxPathLength int `json:"max_path_length"`
	
	// 最大路径数量
	MaxPaths int `json:"max_paths"`
	
	// 子图最大节点数
	MaxSubgraphNodes int `json:"max_subgraph_nodes"`
	
	// 是否包含推理过程
	IncludeReasoningProcess bool `json:"include_reasoning_process"`
	
	// 子图相关性阈值
	SubgraphRelevanceThreshold float64 `json:"subgraph_relevance_threshold"`
	
	// 是否启用证据增强
	EnableEvidenceEnhancement bool `json:"enable_evidence_enhancement"`
	
	// 支持文档最大数量
	MaxSupportingDocuments int `json:"max_supporting_documents"`
	
	// 额外选项
	ExtraOptions map[string]interface{} `json:"extra_options,omitempty"`
}

// LanguageModelService LLM服务接口
type LanguageModelService interface {
	// GenerateText 生成文本
	GenerateText(ctx context.Context, prompt string, options map[string]interface{}) (string, error)
	
	// GetEmbedding 获取向量
	GetEmbedding(ctx context.Context, text string) ([]float64, error)
}

// KGReasoner 知识图谱推理器
type KGReasoner struct {
	// 知识图谱服务
	kgService KnowledgeGraphService
	
	// 检索器
	retriever Retriever
	
	// LLM服务
	llmService LanguageModelService
	
	// 日志器
	logger utils.Logger
	
	// 默认选项
	defaultOptions KGReasoningOptions
}

// KGReasonerOptions 知识图谱推理器选项
type KGReasonerOptions struct {
	// 知识图谱服务
	KGService KnowledgeGraphService
	
	// 检索器
	Retriever Retriever
	
	// LLM服务
	LLMService LanguageModelService
	
	// 默认选项
	DefaultOptions KGReasoningOptions
	
	// 推理模板
	ReasoningTemplates map[string]string
	
	// 日志
	Logger utils.Logger
}

// NewKGReasoner 创建知识图谱推理器
func NewKGReasoner(options KGReasonerOptions) (*KGReasoner, error) {
	if options.KGService == nil {
		return nil, fmt.Errorf("知识图谱服务不能为空")
	}
	
	if options.LLMService == nil {
		return nil, fmt.Errorf("语言模型服务不能为空")
	}
	
	// 设置默认选项
	if options.DefaultOptions.MaxPathLength <= 0 {
		options.DefaultOptions.MaxPathLength = 4
	}
	
	if options.DefaultOptions.MaxPaths <= 0 {
		options.DefaultOptions.MaxPaths = 5
	}
	
	if options.DefaultOptions.MaxSubgraphNodes <= 0 {
		options.DefaultOptions.MaxSubgraphNodes = 20
	}
	
	// 设置默认推理模板
	if options.ReasoningTemplates == nil {
		options.ReasoningTemplates = getDefaultReasoningTemplates()
	}
	
	return &KGReasoner{
		kgService:          options.KGService,
		retriever:          options.Retriever,
		llmService:         options.LLMService,
		logger:             options.Logger,
		defaultOptions:     options.DefaultOptions,
	}, nil
}

// Reason 执行知识图谱推理
func (r *KGReasoner) Reason(ctx context.Context, query string, userOptions *KGReasoningOptions) (*KGReasoningResult, error) {
	startTime := time.Now()
	
	// 合并选项
	options := r.mergeOptions(userOptions)
	
	// 创建结果结构
	result := &KGReasoningResult{
		Confidence: 0.0,
		KeyEntities: make([]KnowledgeGraphNode, 0),
		Paths: make([]KnowledgeGraphPath, 0),
	}
	
	// 1. 识别关键实体
	keyEntities, err := r.identifyKeyEntities(ctx, query)
	if err != nil {
		if r.logger != nil {
			r.logger.Error("识别关键实体失败", "error", err)
		}
		return nil, fmt.Errorf("识别关键实体失败: %w", err)
	}
	
	if len(keyEntities) == 0 {
		r.logger.Warn("未找到关键实体", "query", query)
	} else {
		result.KeyEntities = keyEntities
	}
	
	// 2. 路径推理
	if options.EnablePathReasoning && len(keyEntities) >= 2 {
		paths, err := r.performPathReasoning(ctx, query, keyEntities, options)
		if err != nil {
			r.logger.Warn("路径推理失败", "error", err)
		} else if len(paths) > 0 {
			result.Paths = paths
			
			// 更新置信度
			pathConfidence := calculatePathsConfidence(paths)
			result.Confidence = max(result.Confidence, pathConfidence)
		}
	}
	
	// 3. 子图推理
	if options.EnableSubgraphReasoning {
		subgraph, err := r.performSubgraphReasoning(ctx, query, keyEntities, options)
		if err != nil {
			r.logger.Warn("子图推理失败", "error", err)
		} else if subgraph != nil {
			result.Subgraph = subgraph
			
			// 更新置信度
			subgraphConfidence := subgraph.RelevanceScore
			result.Confidence = max(result.Confidence, subgraphConfidence)
		}
	}
	
	// 4. 证据增强
	if options.EnableEvidenceEnhancement {
		supportingDocs, err := r.enhanceWithEvidence(ctx, query, result, options)
		if err != nil {
			r.logger.Warn("证据增强失败", "error", err)
		} else {
			result.SupportingDocuments = supportingDocs
		}
	}
	
	// 5. 生成推理结论
	conclusion, reasoningProcess, err := r.generateConclusion(ctx, query, result, options)
	if err != nil {
		r.logger.Warn("生成结论失败", "error", err)
		result.Conclusion = "无法生成推理结论"
	} else {
		result.Conclusion = conclusion
		
		if options.IncludeReasoningProcess {
			result.ReasoningProcess = reasoningProcess
		}
	}
	
	result.ExecutionTime = time.Since(startTime).Milliseconds()
	return result, nil
}

// 识别关键实体
func (r *KGReasoner) identifyKeyEntities(ctx context.Context, query string) ([]KnowledgeGraphNode, error) {
	// 使用知识图谱服务查询节点
	options := map[string]interface{}{
		"relevance_threshold": 0.6,
		"max_results":         10,
		"use_embedding":       true,
	}
	
	nodes, err := r.kgService.QueryNodes(ctx, query, options)
	if err != nil {
		return nil, err
	}
	
	// 过滤和排序
	if len(nodes) > 5 {
		// 这里可以添加更复杂的关键实体筛选逻辑
		nodes = nodes[:5]
	}
	
	return nodes, nil
}

// 执行路径推理
func (r *KGReasoner) performPathReasoning(ctx context.Context, query string, entities []KnowledgeGraphNode, opts KGReasoningOptions) ([]KnowledgeGraphPath, error) {
	// 至少需要两个实体才能找路径
	if len(entities) < 2 {
		return nil, nil
	}
	
	// 获取实体ID
	entityIDs := make([]string, 0, len(entities))
	for _, entity := range entities {
		entityIDs = append(entityIDs, entity.ID)
	}
	
	// 创建知识图谱查询
	kgQuery := KnowledgeGraphQuery{
		Text:               query,
		StartNodeIDs:       entityIDs,
		MaxPathLength:      opts.MaxPathLength,
		MaxResults:         opts.MaxPaths,
		RelevanceThreshold: 0.5,
		UseEmbedding:       true,
	}
	
	// 查询路径
	paths, err := r.kgService.GetPaths(ctx, kgQuery)
	if err != nil {
		return nil, err
	}
	
	// 排序路径（按相关度）
	if len(paths) > 1 {
		sortPaths(paths)
	}
	
	return paths, nil
}

// 执行子图推理
func (r *KGReasoner) performSubgraphReasoning(ctx context.Context, query string, entities []KnowledgeGraphNode, opts KGReasoningOptions) (*ReasoningSubgraph, error) {
	// 获取实体ID
	entityIDs := make([]string, 0, len(entities))
	for _, entity := range entities {
		entityIDs = append(entityIDs, entity.ID)
	}
	
	// 创建知识图谱查询
	kgQuery := KnowledgeGraphQuery{
		Text:               query,
		StartNodeIDs:       entityIDs,
		MaxPathLength:      opts.MaxPathLength,
		RelevanceThreshold: opts.SubgraphRelevanceThreshold,
		UseEmbedding:       true,
		Constraints: map[string]interface{}{
			"max_nodes": opts.MaxSubgraphNodes,
		},
	}
	
	// 查询子图
	subgraph, err := r.kgService.GetSubgraph(ctx, kgQuery)
	if err != nil {
		return nil, err
	}
	
	return subgraph, nil
}

// 使用检索结果增强推理
func (r *KGReasoner) enhanceWithEvidence(ctx context.Context, query string, result *KGReasoningResult, opts KGReasoningOptions) ([]models.SearchResult, error) {
	if r.retriever == nil {
		return nil, fmt.Errorf("检索器未初始化")
	}
	
	// 构建增强查询
	enhancedQuery := query
	
	// 添加关键实体
	if len(result.KeyEntities) > 0 {
		entityNames := make([]string, 0, len(result.KeyEntities))
		for _, entity := range result.KeyEntities {
			entityNames = append(entityNames, entity.Name)
		}
		
		if len(entityNames) > 0 {
			enhancedQuery = fmt.Sprintf("%s (%s)", enhancedQuery, strings.Join(entityNames, " "))
		}
	}
	
	// 添加路径关系
	if len(result.Paths) > 0 {
		relationDescriptions := extractRelationDescriptions(result.Paths[0], 2)
		if len(relationDescriptions) > 0 {
			enhancedQuery = fmt.Sprintf("%s %s", enhancedQuery, strings.Join(relationDescriptions, " "))
		}
	}
	
	// 执行检索
	retrieveOptions := map[string]interface{}{
		"top_k": opts.MaxSupportingDocuments,
	}
	
	results, err := r.retriever.Retrieve(ctx, enhancedQuery, retrieveOptions)
	if err != nil {
		return nil, err
	}
	
	return results, nil
}

// 生成推理结论
func (r *KGReasoner) generateConclusion(ctx context.Context, query string, result *KGReasoningResult, opts KGReasoningOptions) (string, string, error) {
	if r.llmService == nil {
		// 如果没有LLM服务，生成简单的结论
		return r.generateSimpleConclusion(result), "", nil
	}
	
	// 构建提示
	prompt := r.buildConclusionPrompt(query, result)
	
	// 调用LLM
	response, err := r.llmService.GenerateText(ctx, prompt, nil)
	
	if err != nil {
		return "", "", err
	}
	
	// 解析响应
	conclusion, reasoningProcess := r.parseReasoningResponse(response)
	
	return conclusion, reasoningProcess, nil
}

// 构建结论提示
func (r *KGReasoner) buildConclusionPrompt(query string, result *KGReasoningResult) string {
	var prompt strings.Builder
	
	prompt.WriteString(fmt.Sprintf("请根据以下信息，回答问题: '%s'\n\n", query))
	
	// 添加关键实体信息
	if len(result.KeyEntities) > 0 {
		prompt.WriteString("相关概念和实体:\n")
		for _, entity := range result.KeyEntities {
			prompt.WriteString(fmt.Sprintf("- %s (%s): %s\n", entity.Name, entity.Type, entity.Description))
		}
		prompt.WriteString("\n")
	}
	
	// 添加路径信息
	if len(result.Paths) > 0 {
		prompt.WriteString("概念间关系:\n")
		for i, path := range result.Paths {
			if i >= 3 {
				break // 最多包含3条路径
			}
			
			pathDescription := describePath(path)
			prompt.WriteString(fmt.Sprintf("- %s\n", pathDescription))
		}
		prompt.WriteString("\n")
	}
	
	// 添加子图信息
	if result.Subgraph != nil && len(result.Subgraph.Nodes) > 0 {
		prompt.WriteString("知识子图特征:\n")
		for key, value := range result.Subgraph.Features {
			prompt.WriteString(fmt.Sprintf("- %s: %v\n", key, value))
		}
		prompt.WriteString("\n")
	}
	
	// 添加支持文档
	if len(result.SupportingDocuments) > 0 {
		prompt.WriteString("相关文档:\n")
		for i, doc := range result.SupportingDocuments {
			if i >= 3 {
				break // 最多包含3个文档
			}
			prompt.WriteString(fmt.Sprintf("- %s\n", doc.Content))
		}
		prompt.WriteString("\n")
	}
	
	// 添加指导
	prompt.WriteString(`请根据上述信息，提供一个全面而准确的回答。回答应基于所提供的知识图谱关系和相关文档，并在可能的情况下建立概念之间的连接。

请以两部分格式给出回答:

推理过程: <详细分析和推理步骤，解释如何从知识图谱和文档得出结论>

结论: <简洁明了的最终回答>`)
	
	return prompt.String()
}

// 解析推理响应
func (r *KGReasoner) parseReasoningResponse(response string) (string, string) {
	// 寻找"结论:"标记
	parts := strings.Split(response, "结论:")
	
	if len(parts) >= 2 {
		// 有标准格式
		reasoningProcess := strings.TrimSpace(parts[0])
		conclusion := strings.TrimSpace(parts[1])
		
		// 移除"推理过程:"前缀
		reasoningProcess = strings.TrimPrefix(reasoningProcess, "推理过程:")
		reasoningProcess = strings.TrimSpace(reasoningProcess)
		
		return conclusion, reasoningProcess
	}
	
	// 没有标准格式，将整个响应作为结论
	return strings.TrimSpace(response), ""
}

// 生成简单结论
func (r *KGReasoner) generateSimpleConclusion(result *KGReasoningResult) string {
	var conclusion strings.Builder
	
	// 如果有路径，使用路径生成简单结论
	if len(result.Paths) > 0 {
		path := result.Paths[0] // 使用相关性最高的路径
		conclusion.WriteString(describePath(path))
	} else if len(result.KeyEntities) > 0 {
		// 否则，使用关键实体生成简单结论
		entityNames := make([]string, 0, len(result.KeyEntities))
		for _, entity := range result.KeyEntities {
			entityNames = append(entityNames, entity.Name)
		}
		
		conclusion.WriteString(fmt.Sprintf("与查询相关的概念包括：%s。", strings.Join(entityNames, "、")))
	} else {
		conclusion.WriteString("知识图谱中未找到相关信息。")
	}
	
	return conclusion.String()
}

// 合并选项
func (r *KGReasoner) mergeOptions(userOptions *KGReasoningOptions) KGReasoningOptions {
	options := r.defaultOptions
	
	if userOptions == nil {
		return options
	}
	
	// 合并字段
	if userOptions.MaxPathLength > 0 {
		options.MaxPathLength = userOptions.MaxPathLength
	}
	
	if userOptions.MaxPaths > 0 {
		options.MaxPaths = userOptions.MaxPaths
	}
	
	if userOptions.MaxSubgraphNodes > 0 {
		options.MaxSubgraphNodes = userOptions.MaxSubgraphNodes
	}
	
	if userOptions.SubgraphRelevanceThreshold > 0 {
		options.SubgraphRelevanceThreshold = userOptions.SubgraphRelevanceThreshold
	}
	
	if userOptions.MaxSupportingDocuments > 0 {
		options.MaxSupportingDocuments = userOptions.MaxSupportingDocuments
	}
	
	// 合并额外选项
	if userOptions.ExtraOptions != nil {
		if options.ExtraOptions == nil {
			options.ExtraOptions = make(map[string]interface{})
		}
		
		for k, v := range userOptions.ExtraOptions {
			options.ExtraOptions[k] = v
		}
	}
	
	return options
}

// 辅助函数

// 排序路径
func sortPaths(paths []KnowledgeGraphPath) {
	// 按相关性分数排序
	for i := 0; i < len(paths); i++ {
		for j := i + 1; j < len(paths); j++ {
			if paths[i].RelevanceScore < paths[j].RelevanceScore {
				paths[i], paths[j] = paths[j], paths[i]
			}
		}
	}
}

// 计算路径置信度
func calculatePathsConfidence(paths []KnowledgeGraphPath) float64 {
	if len(paths) == 0 {
		return 0.0
	}
	
	totalConfidence := 0.0
	totalWeight := 0.0
	
	for i, path := range paths {
		weight := 1.0 / float64(i+1) // 路径权重随排名下降
		totalConfidence += path.RelevanceScore * weight
		totalWeight += weight
	}
	
	if totalWeight > 0 {
		return totalConfidence / totalWeight
	}
	
	return 0.0
}

// 描述路径
func describePath(path KnowledgeGraphPath) string {
	if len(path.Nodes) <= 1 || len(path.Edges) == 0 {
		return ""
	}
	
	var description strings.Builder
	
	for i := 0; i < len(path.Edges); i++ {
		if i > 0 {
			description.WriteString(", ")
		}
		
		source := path.Nodes[i]
		target := path.Nodes[i+1]
		edge := path.Edges[i]
		
		relationText := formatRelationType(edge.Type)
		
		description.WriteString(fmt.Sprintf("%s %s %s", source.Name, relationText, target.Name))
	}
	
	return description.String()
}

// 格式化关系类型
func formatRelationType(relationType RelationType) string {
	switch relationType {
	case RelationIsA:
		return "是一种"
	case RelationPartOf:
		return "是...的一部分"
	case RelationHasProperty:
		return "具有属性"
	case RelationCauses:
		return "导致"
	case RelationPreventedBy:
		return "被...预防"
	case RelationTreatedBy:
		return "被...治疗"
	case RelationSymptomOf:
		return "是...的症状"
	case RelationRelatedTo:
		return "与...相关"
	case RelationContraindicatedWith:
		return "与...禁忌"
	case RelationSimilarTo:
		return "与...相似"
	case RelationDiagnosedBy:
		return "通过...诊断"
	default:
		return string(relationType)
	}
}

// 提取关系描述
func extractRelationDescriptions(path KnowledgeGraphPath, maxRelations int) []string {
	if len(path.Edges) == 0 {
		return nil
	}
	
	count := min(len(path.Edges), maxRelations)
	relations := make([]string, 0, count)
	
	for i := 0; i < count; i++ {
		edge := path.Edges[i]
		relations = append(relations, string(edge.Type))
	}
	
	return relations
}

// 获取最大值
func max(a, b float64) float64 {
	if a > b {
		return a
	}
	return b
}

// 获取最小值
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// getDefaultReasoningTemplates 获取默认推理模板
func getDefaultReasoningTemplates() map[string]string {
	return map[string]string{
		"entity_extraction": `
从以下查询中提取关键实体和概念的列表。专注于医学、健康和中医相关的实体。

查询: %s

提取的实体列表:`,

		"conclusion_generation": `
基于以下信息，请提供一个综合性的回答:

%s

请提供一个考虑了所有上述信息的综合性回答。回答应该是准确的、有见解的，并向用户提供有价值的信息。优先考虑基于知识图谱和推理路径的信息，并引用相关文档作为支持。`,
	}
} 