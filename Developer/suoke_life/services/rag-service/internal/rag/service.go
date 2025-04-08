package rag

import (
	"context"
	"fmt"
	"io"
	"log"
	"sort"
	"strings"
	"time"

	"github.com/google/uuid"
	"github.com/suoke-life/services/rag-service/internal/embeddings"
	"github.com/suoke-life/services/rag-service/internal/llm"
	"github.com/suoke-life/services/rag-service/internal/metrics"
	"github.com/suoke-life/services/rag-service/internal/store"
	"github.com/suoke-life/services/rag-service/internal/vector_store"
	"github.com/suoke/suoke_life/services/rag-service/internal/models"
	"github.com/suoke/suoke_life/services/rag-service/rag"
)

// DefaultRAGService 是默认的RAG服务实现
type DefaultRAGService struct {
	embedModel  embeddings.EmbeddingModel
	vectorStore vector_store.VectorStore
	llmService  llm.LLMService
	metrics     metrics.MetricsCollector
	impl        *rag.DefaultRAGService
}

// NewRAGService 创建一个新的RAG服务
func NewRAGService(
	embedModel embeddings.EmbeddingModel,
	vectorStore vector_store.VectorStore,
	llmService llm.LLMService,
	metrics metrics.MetricsCollector,
) RAGService {
	return &DefaultRAGService{
		embedModel:  embedModel,
		vectorStore: vectorStore,
		llmService:  llmService,
		metrics:     metrics,
	}
}

// Initialize 初始化RAG服务
func (s *DefaultRAGService) Initialize(ctx context.Context) error {
	s.impl = rag.NewDefaultRAGService(nil, nil, 10, 1000, nil)
	return s.impl.Initialize(ctx)
}

// Close 关闭RAG服务
func (s *DefaultRAGService) Close() error {
	return s.impl.Close()
}

// Query 执行RAG查询
func (s *DefaultRAGService) Query(ctx context.Context, req QueryRequest) (*QueryResponse, error) {
	startTime := time.Now()
	queryID := uuid.New().String()

	// 记录指标
	defer func() {
		duration := time.Since(startTime)
		s.metrics.RecordQueryLatency(duration)
	}()

	// 记录查询请求
	log.Printf("RAG查询: ID=%s 问题='%s' 集合='%s'", queryID, req.Query, req.CollectionName)

	// 嵌入查询文本
	embedding, err := s.embedModel.EmbedQuery(req.Query)
	if err != nil {
		return nil, fmt.Errorf("嵌入查询失败: %w", err)
	}

	// 从向量存储中搜索相似文档
	searchResults, err := s.vectorStore.SimilaritySearch(
		req.CollectionName,
		embedding,
		req.TopK,
		req.ScoreThreshold,
		req.IncludeContent,
	)
	if err != nil {
		return nil, fmt.Errorf("相似度搜索失败: %w", err)
	}

	// 记录检索的文档数量
	s.metrics.RecordDocsRetrieved(len(searchResults))
	log.Printf("RAG检索: ID=%s 检索到%d个文档", queryID, len(searchResults))

	// 组装上下文
	context := s.assembleContext(searchResults)

	// 构建系统提示
	systemPrompt := "您是一个专业的AI助手，擅长根据提供的信息回答问题。请基于以下上下文信息回答问题，如果无法从上下文中找到答案，请明确说明。"
	
	// 构建用户提示
	prompt := fmt.Sprintf(`上下文信息：
%s

请根据上述上下文回答以下问题：%s`, context, req.Query)

	// 调用LLM生成回答
	options := map[string]interface{}{
		"system":       systemPrompt,
		"temperature":  req.Temperature,
		"max_tokens":   req.MaxTokens,
	}

	// 检查是否设置了LLM服务
	if s.llmService == nil {
		// 如果没有LLM服务，返回示例回答
		return &QueryResponse{
			Answer: "我是RAG服务的示例回答。此时LLM服务未配置，无法生成真实回答。请在服务配置中添加LLM服务。",
			Sources: s.extractSources(searchResults),
			Metadata: map[string]interface{}{
				"retrieval_time_ms": time.Since(startTime).Milliseconds(),
				"docs_retrieved":    len(searchResults),
				"model":             "none",
			},
		}, nil
	}

	// 实际调用LLM生成回答
	answer, err := s.llmService.Generate(ctx, prompt, options)
	if err != nil {
		log.Printf("LLM生成回答失败: %v", err)
		return nil, fmt.Errorf("生成回答失败: %w", err)
	}

	// 构建响应
	response := &QueryResponse{
		Answer:  answer,
		Sources: s.extractSources(searchResults),
		Metadata: map[string]interface{}{
			"retrieval_time_ms": time.Since(startTime).Milliseconds(),
			"docs_retrieved":    len(searchResults),
			"model":             s.llmService.GetModelName(),
		},
	}

	log.Printf("RAG完成: ID=%s 耗时=%dms", queryID, time.Since(startTime).Milliseconds())
	return response, nil
}

// StreamQuery 执行流式RAG查询
func (s *DefaultRAGService) StreamQuery(ctx context.Context, req QueryRequest, writer io.Writer) error {
	startTime := time.Now()
	queryID := uuid.New().String()

	// 记录指标
	defer func() {
		duration := time.Since(startTime)
		s.metrics.RecordQueryLatency(duration)
	}()

	// 记录查询请求
	log.Printf("流式RAG查询: ID=%s 问题='%s' 集合='%s'", queryID, req.Query, req.CollectionName)

	// 嵌入查询文本
	embedding, err := s.embedModel.EmbedQuery(req.Query)
	if err != nil {
		return fmt.Errorf("嵌入查询失败: %w", err)
	}

	// 从向量存储中搜索相似文档
	searchResults, err := s.vectorStore.SimilaritySearch(
		req.CollectionName,
		embedding,
		req.TopK,
		req.ScoreThreshold,
		req.IncludeContent,
	)
	if err != nil {
		return fmt.Errorf("相似度搜索失败: %w", err)
	}

	// 记录检索的文档数量
	s.metrics.RecordDocsRetrieved(len(searchResults))
	log.Printf("RAG检索: ID=%s 检索到%d个文档", queryID, len(searchResults))

	// 组装上下文
	context := s.assembleContext(searchResults)

	// 构建系统提示
	systemPrompt := "您是一个专业的AI助手，擅长根据提供的信息回答问题。请基于以下上下文信息回答问题，如果无法从上下文中找到答案，请明确说明。"
	
	// 构建用户提示
	prompt := fmt.Sprintf(`上下文信息：
%s

请根据上述上下文回答以下问题：%s`, context, req.Query)

	// 调用LLM生成流式回答
	options := map[string]interface{}{
		"system":       systemPrompt,
		"temperature":  req.Temperature,
		"max_tokens":   req.MaxTokens,
	}

	// 检查是否设置了LLM服务
	if s.llmService == nil {
		// 如果没有LLM服务，返回示例回答
		_, err = writer.Write([]byte("我是RAG服务的示例回答。此时LLM服务未配置，无法生成真实回答。请在服务配置中添加LLM服务。"))
		if err != nil {
			return fmt.Errorf("写入响应失败: %w", err)
		}
		return nil
	}

	// 实际调用LLM生成流式回答
	err = s.llmService.GenerateStream(ctx, prompt, writer, options)
	if err != nil {
		log.Printf("LLM流式生成回答失败: %v", err)
		return fmt.Errorf("流式生成回答失败: %w", err)
	}

	log.Printf("流式RAG完成: ID=%s 耗时=%dms", queryID, time.Since(startTime).Milliseconds())
	return nil
}

// UploadDocument 上传文档
func (s *DefaultRAGService) UploadDocument(ctx context.Context, request models.DocumentUploadRequest) (*models.DocumentUploadResponse, error) {
	return s.impl.UploadDocument(ctx, request)
}

// CreateCollection 创建集合
func (s *DefaultRAGService) CreateCollection(ctx context.Context, request models.CollectionCreateRequest) (*models.Collection, error) {
	return s.impl.CreateCollection(ctx, request)
}

// DeleteCollection 删除集合
func (s *DefaultRAGService) DeleteCollection(ctx context.Context, name string) error {
	return s.impl.DeleteCollection(ctx, name)
}

// ListCollections 列出所有集合
func (s *DefaultRAGService) ListCollections(ctx context.Context) ([]models.Collection, error) {
	return s.impl.ListCollections(ctx)
}

// GetCollection 获取集合信息
func (s *DefaultRAGService) GetCollection(ctx context.Context, name string) (*models.Collection, error) {
	return s.impl.GetCollection(ctx, name)
}

// DeleteDocument 删除文档
func (s *DefaultRAGService) DeleteDocument(ctx context.Context, collectionName string, documentID string) error {
	return s.impl.DeleteDocument(ctx, collectionName, documentID)
}

// GetDocument 获取文档
func (s *DefaultRAGService) GetDocument(ctx context.Context, collectionName string, documentID string) (*models.Document, error) {
	return s.impl.GetDocument(ctx, collectionName, documentID)
}

// Search 在集合中搜索
func (s *DefaultRAGService) Search(ctx context.Context, collectionName string, query string, limit int, filter map[string]interface{}) ([]models.Document, error) {
	return s.impl.Search(ctx, collectionName, query, limit, filter)
}

// CreateEmbedding 创建嵌入向量
func (s *DefaultRAGService) CreateEmbedding(ctx context.Context, texts []string, options map[string]interface{}) (*models.EmbeddingResponse, error) {
	return s.impl.CreateEmbedding(ctx, texts, options)
}

// HealthCheck 健康检查
func (s *DefaultRAGService) HealthCheck(ctx context.Context) error {
	return s.impl.HealthCheck(ctx)
}

// assembleContext 组装上下文
func (s *DefaultRAGService) assembleContext(searchResults []vector_store.SearchResult) string {
	// 首先按相关性分数排序
	sort.Slice(searchResults, func(i, j int) bool {
		return searchResults[i].Score > searchResults[j].Score
	})

	var contextBuilder strings.Builder
	
	// 添加每个相关文档
	for i, result := range searchResults {
		contextBuilder.WriteString(fmt.Sprintf("文档[%d] (相关性: %.2f):\n%s\n\n", 
			i+1, result.Score, result.Content))
	}
	
	return contextBuilder.String()
}

// extractSources 从搜索结果中提取来源信息
func (s *DefaultRAGService) extractSources(searchResults []vector_store.SearchResult) []Source {
	sources := make([]Source, 0, len(searchResults))
	
	for _, result := range searchResults {
		source := Source{
			ID:     result.ID,
			Score:  result.Score,
			URL:    result.Metadata["url"],
			Title:  result.Metadata["title"],
		}
		sources = append(sources, source)
	}
	
	return sources
} 