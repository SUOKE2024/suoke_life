package rag

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"math"
	"sort"
	"strings"
	"sync"
	"time"

	"github.com/suoke/suoke_life/services/rag-service/internal/embeddings"
	"github.com/suoke/suoke_life/services/rag-service/internal/models"
	"github.com/suoke/suoke_life/services/rag-service/internal/storage/vector_store"
)

// DefaultRAGService 是RAG服务的默认实现
type DefaultRAGService struct {
	vectorStore    vector_store.VectorStore
	embedder       embeddings.TextEmbedder
	topK           int
	contextWindow  int
	metricsHandler interface {
		RecordRequest(method, endpoint, status string)
		RecordTokens(model, tokenType string, count int)
		RecordRequestDuration(method, endpoint string, durationSeconds float64)
	}
}

// NewDefaultRAGService 创建新的默认RAG服务
func NewDefaultRAGService(
	vectorStore vector_store.VectorStore,
	embedder embeddings.TextEmbedder,
	topK int,
	contextWindow int,
	metricsHandler interface {
		RecordRequest(method, endpoint, status string)
		RecordTokens(model, tokenType string, count int)
		RecordRequestDuration(method, endpoint string, durationSeconds float64)
	},
) *DefaultRAGService {
	return &DefaultRAGService{
		vectorStore:    vectorStore,
		embedder:       embedder,
		topK:           topK,
		contextWindow:  contextWindow,
		metricsHandler: metricsHandler,
	}
}

// HealthCheck 健康检查
func (s *DefaultRAGService) HealthCheck(ctx context.Context) error {
	// 检查向量存储
	if s.vectorStore != nil {
		// 如果实现了IsHealthy方法则调用，否则假定健康
		if healthChecker, ok := s.vectorStore.(interface{ IsHealthy(context.Context) bool }); ok {
			if !healthChecker.IsHealthy(ctx) {
				return fmt.Errorf("向量存储健康检查失败")
			}
		}
	}
	
	// 检查嵌入模型
	if s.embedder != nil {
		// 如果实现了IsHealthy方法则调用，否则假定健康
		if healthChecker, ok := s.embedder.(interface{ IsHealthy(context.Context) bool }); ok {
			if !healthChecker.IsHealthy(ctx) {
				return fmt.Errorf("嵌入模型健康检查失败")
			}
		}
	}
	
	return nil
}

// Initialize 初始化RAG服务
func (s *DefaultRAGService) Initialize(ctx context.Context) error {
	// 初始化向量存储
	if s.vectorStore != nil {
		if err := s.vectorStore.Initialize(ctx); err != nil {
			return fmt.Errorf("初始化向量存储失败: %w", err)
		}
	}
	
	return nil
}

// Close 关闭RAG服务
func (s *DefaultRAGService) Close() error {
	// 关闭资源
	if s.vectorStore != nil {
		_ = s.vectorStore.Close()
	}
	if s.embedder != nil {
		_ = s.embedder.Close()
	}
	return nil
}

// Query 执行RAG查询
func (s *DefaultRAGService) Query(ctx context.Context, request models.QueryRequest) (*models.QueryResult, error) {
	startTime := time.Now()
	result := &models.QueryResult{
		Query:     request.Query,
		Stream:    request.Stream,
		SessionID: request.SessionID,
		UserId:    request.UserId,
		Timestamp: startTime,
	}
	
	// 记录指标
	defer func() {
		if s.metricsHandler != nil {
			s.metricsHandler.RecordRequestDuration("rag", "query", time.Since(startTime).Seconds())
		}
	}()
	
	// 参数校验和默认值设置
	topK := s.topK
	if request.TopK > 0 {
		topK = request.TopK
	}
	
	collectionNames := request.CollectionNames
	if len(collectionNames) == 0 {
		// 如果未指定集合，则获取所有集合
		collections, err := s.ListCollections(ctx)
	if err != nil {
			return nil, fmt.Errorf("获取集合列表失败: %w", err)
		}
		
		if len(collections) == 0 {
			return nil, fmt.Errorf("未找到可用的集合")
		}
		
		for _, collection := range collections {
			collectionNames = append(collectionNames, collection.Name)
		}
	}
	
	embedStartTime := time.Now()
	
	// 为查询生成嵌入向量
	queryVector, err := s.embedder.EmbedQuery(ctx, request.Query)
	if err != nil {
		return nil, fmt.Errorf("生成查询嵌入向量失败: %w", err)
	}
	
	// 记录嵌入用时
	embedTime := time.Since(embedStartTime).Seconds()
	result.EmbeddingTime = embedTime
	
	vectorDBStartTime := time.Now()
	
	// 在所有指定的集合中搜索
	var allResults []models.Document
	for _, collName := range collectionNames {
		// 检查集合是否存在
		exists, err := s.vectorStore.CollectionExists(ctx, collName)
		if err != nil {
			return nil, fmt.Errorf("检查集合 %s 是否存在失败: %w", collName, err)
		}
		
		if !exists {
			continue
		}
		
		// 执行向量相似度搜索
		docs, err := s.vectorStore.SimilaritySearch(
			ctx,
			collName,
			queryVector,
			topK,
			request.Metadata,
			false, // 不包含向量以减少数据传输
		)
		
		if err != nil {
			return nil, fmt.Errorf("在集合 %s 中搜索失败: %w", collName, err)
		}
		
		allResults = append(allResults, docs...)
	}
	
	// 记录向量数据库用时
	vectorDBTime := time.Since(vectorDBStartTime).Seconds()
	result.VectorDBTime = vectorDBTime
	
	// 如果启用了重排序
	if request.UseReranker && len(allResults) > 0 {
		// 此处应添加重排序逻辑
		// 重排序会根据查询与文档的相关性重新排序结果
		rerankerStartTime := time.Now()
		
		// TODO: 实现重排序逻辑
		
		result.RerankerTime = time.Since(rerankerStartTime).Seconds()
	}
	
	// 如果启用了网络搜索
	if request.EnableWebSearch {
		webSearchStartTime := time.Now()
		
		// TODO: 实现网络搜索逻辑
		// 这里应该调用网络搜索API，并将结果添加到allResults中
		
		result.WebSearchTime = time.Since(webSearchStartTime).Seconds()
	}
	
	// 处理找到的结果
	result.Results = allResults
	
	// 准备上下文，将检索到的文档内容合并
	var context string
	var citations []models.Citation
	
	for i, doc := range allResults {
		// 截断长文档以保持在上下文窗口大小内
		content := doc.Content
		if len(content) > s.contextWindow/len(allResults) {
			content = content[:s.contextWindow/len(allResults)] + "..."
		}
		
		// 添加到上下文
		context += content + "\n\n"
		
		// 添加引用
		citation := models.Citation{
			DocumentID: doc.ID,
			Text:       doc.Content,
			Score:      doc.Score,
			Metadata:   doc.Metadata,
			Collection: doc.Collection,
		}
		
		if source, ok := doc.Metadata["source"].(string); ok {
			citation.Source = source
		}
		
		if url, ok := doc.Metadata["url"].(string); ok {
			citation.URL = url
		}
		
		citations = append(citations, citation)
	}
	
	// 大型语言模型调用
	llmStartTime := time.Now()
	
	// TODO: 这里应该调用实际的LLM服务
	// 临时使用硬编码答案用于演示
	answer := fmt.Sprintf("基于检索到的%d个文档，关于'%s'的回答是：这是一个示例回答，实际实现中将调用LLM生成。", 
		len(allResults), request.Query)
	
	result.LLMTime = time.Since(llmStartTime).Seconds()
	result.Answer = answer
	result.Citations = citations
	
	// 计算总时间
	result.TotalTime = time.Since(startTime).Seconds()
	result.RagTime = result.TotalTime
	
	return result, nil
}

// StreamQuery 执行流式RAG查询
func (s *DefaultRAGService) StreamQuery(ctx context.Context, request models.QueryRequest, writer io.Writer) error {
	startTime := time.Now()
	
	// 记录指标
	defer func() {
		if s.metricsHandler != nil {
			s.metricsHandler.RecordRequestDuration("rag", "stream_query", time.Since(startTime).Seconds())
		}
	}()
	
	// 参数校验和默认值设置
	topK := s.topK
	if request.TopK > 0 {
		topK = request.TopK
	}
	
	collectionNames := request.CollectionNames
	if len(collectionNames) == 0 {
		// 如果未指定集合，则获取所有集合
		collections, err := s.ListCollections(ctx)
	if err != nil {
			return fmt.Errorf("获取集合列表失败: %w", err)
		}
		
		if len(collections) == 0 {
			return fmt.Errorf("未找到可用的集合")
		}
		
		for _, collection := range collections {
			collectionNames = append(collectionNames, collection.Name)
		}
	}
	
	// 发送开始事件
	startMessage := models.StreamMessage{
		Event: models.EventStart,
		Text:  "",
	}
	if err := writeStreamMessage(writer, startMessage); err != nil {
		return fmt.Errorf("发送开始事件失败: %w", err)
	}
	
	embedStartTime := time.Now()
	
	// 为查询生成嵌入向量
	queryVector, err := s.embedder.EmbedQuery(ctx, request.Query)
	if err != nil {
		errorMessage := models.StreamMessage{
			Event: models.EventError,
			Error: fmt.Sprintf("生成查询嵌入向量失败: %v", err),
		}
		_ = writeStreamMessage(writer, errorMessage)
		return fmt.Errorf("生成查询嵌入向量失败: %w", err)
	}
	
	// 记录嵌入用时
	embedTime := time.Since(embedStartTime).Seconds()
	
	vectorDBStartTime := time.Now()
	
	// 在所有指定的集合中搜索
	var allResults []models.Document
	for _, collName := range collectionNames {
		// 检查集合是否存在
		exists, err := s.vectorStore.CollectionExists(ctx, collName)
		if err != nil {
			errorMessage := models.StreamMessage{
				Event: models.EventError,
				Error: fmt.Sprintf("检查集合 %s 是否存在失败: %v", collName, err),
			}
			_ = writeStreamMessage(writer, errorMessage)
			return fmt.Errorf("检查集合 %s 是否存在失败: %w", collName, err)
		}
		
		if !exists {
			continue
		}
		
		// 执行向量相似度搜索
		docs, err := s.vectorStore.SimilaritySearch(
			ctx,
			collName,
			queryVector,
			topK,
			request.Metadata,
			false, // 不包含向量以减少数据传输
		)
		
		if err != nil {
			errorMessage := models.StreamMessage{
				Event: models.EventError,
				Error: fmt.Sprintf("在集合 %s 中搜索失败: %v", collName, err),
			}
			_ = writeStreamMessage(writer, errorMessage)
			return fmt.Errorf("在集合 %s 中搜索失败: %w", collName, err)
		}
		
		allResults = append(allResults, docs...)
	}
	
	// 记录向量数据库用时
	vectorDBTime := time.Since(vectorDBStartTime).Seconds()
	
	// 如果启用了重排序
	if request.UseReranker && len(allResults) > 0 {
		// 此处应添加重排序逻辑
		// 重排序会根据查询与文档的相关性重新排序结果
		// TODO: 实现重排序逻辑
	}
	
	// 如果启用了网络搜索
	if request.EnableWebSearch {
		// TODO: 实现网络搜索逻辑
		// 这里应该调用网络搜索API，并将结果添加到allResults中
	}
	
	// 发送文档事件
	documentsMessage := models.StreamMessage{
		Event:     models.EventDocuments,
		Documents: allResults,
	}
	if err := writeStreamMessage(writer, documentsMessage); err != nil {
		return fmt.Errorf("发送文档事件失败: %w", err)
	}
	
	// 准备上下文，将检索到的文档内容合并
	var context string
	var citations []models.Citation
	
	for _, doc := range allResults {
		// 截断长文档以保持在上下文窗口大小内
		content := doc.Content
		if len(content) > s.contextWindow/len(allResults) {
			content = content[:s.contextWindow/len(allResults)] + "..."
		}
		
		// 添加到上下文
		context += content + "\n\n"
		
		// 添加引用
		citation := models.Citation{
			DocumentID: doc.ID,
			Text:       doc.Content,
			Score:      doc.Score,
			Metadata:   doc.Metadata,
			Collection: doc.Collection,
		}
		
		if source, ok := doc.Metadata["source"].(string); ok {
			citation.Source = source
		}
		
		if url, ok := doc.Metadata["url"].(string); ok {
			citation.URL = url
		}
		
		citations = append(citations, citation)
	}
	
	// 发送正在处理的事件
	runningMessage := models.StreamMessage{
		Event: models.EventRunning,
		Text:  "正在处理查询...",
	}
	if err := writeStreamMessage(writer, runningMessage); err != nil {
		return fmt.Errorf("发送正在处理事件失败: %w", err)
	}
	
	// 大型语言模型调用
	// 实际实现中应流式处理LLM的回复
	// 这里简化为几个块
	chunks := []string{
		"基于检索到的文档，",
		"关于'" + request.Query + "'的回答是：",
		"这是一个示例流式回答，",
		"实际实现中将调用LLM生成并流式返回。",
	}
	
	// 模拟流式输出
	for _, chunk := range chunks {
		textMessage := models.StreamMessage{
			Event: models.EventText,
			Text:  chunk,
		}
		if err := writeStreamMessage(writer, textMessage); err != nil {
			return fmt.Errorf("发送文本块失败: %w", err)
		}
		
		// 模拟处理延迟
		time.Sleep(200 * time.Millisecond)
	}
	
	// 发送引用事件
	if len(citations) > 0 {
		citationsMessage := models.StreamMessage{
			Event:     models.EventCitation,
			Citations: citations,
		}
		if err := writeStreamMessage(writer, citationsMessage); err != nil {
			return fmt.Errorf("发送引用事件失败: %w", err)
		}
	}
	
	// 计算指标
	totalTime := time.Since(startTime).Seconds()
	metrics := &models.MetricsDetails{
		EmbeddingTokens: s.embedder.CountTokens(request.Query),
		LLMTokens:       0, // 实际实现中应计算
		LLMInputTokens:  0, // 实际实现中应计算
		LLMOutputTokens: 0, // 实际实现中应计算
	}
	
	// 发送结束事件
	endMessage := models.StreamMessage{
		Event:    models.EventEnd,
		Complete: true,
		Metrics:  metrics,
	}
	if err := writeStreamMessage(writer, endMessage); err != nil {
		return fmt.Errorf("发送结束事件失败: %w", err)
	}
	
	return nil
}

// writeStreamMessage 将流消息写入writer
func writeStreamMessage(writer io.Writer, message models.StreamMessage) error {
	data, err := json.Marshal(message)
	if err != nil {
		return err
	}
	
	// 添加换行符以便客户端解析
	data = append(data, '\n')
	
	_, err = writer.Write(data)
	return err
}

// UploadDocument 上传文档
func (s *DefaultRAGService) UploadDocument(ctx context.Context, request models.DocumentUploadRequest) (*models.DocumentUploadResponse, error) {
	startTime := time.Now()
	
	// 检查必要参数
	if request.CollectionName == "" {
		return nil, fmt.Errorf("集合名称不能为空")
	}
	
	if request.Content == "" && request.URL == "" && request.FilePath == "" {
		return nil, fmt.Errorf("文档内容、URL或文件路径至少需要提供一个")
	}
	
	// 检查集合是否存在
	exists, err := s.vectorStore.CollectionExists(ctx, request.CollectionName)
	if err != nil {
		return nil, fmt.Errorf("检查集合是否存在失败: %w", err)
	}
	
	if !exists {
		// 创建集合
		dimensions := 1536 // 默认维度
		if s.embedder != nil {
			dimensions = s.embedder.GetDimensions()
		}
		
		err = s.vectorStore.CreateCollection(ctx, request.CollectionName, dimensions, "自动创建的集合")
		if err != nil {
			return nil, fmt.Errorf("创建集合失败: %w", err)
		}
	}
	
	// 处理分块参数
	chunkSize := 1000
	if request.ChunkSize > 0 {
		chunkSize = request.ChunkSize
	}
	
	chunkOverlap := 200
	if request.ChunkOverlap > 0 {
		chunkOverlap = request.ChunkOverlap
	}
	
	// 获取文档内容
	var content string
	var sourceURL string
	var sourceType string
	
	if request.Content != "" {
		content = request.Content
		sourceType = "text"
	} else if request.URL != "" {
		// TODO: 实现URL内容获取
		sourceURL = request.URL
		sourceType = "url"
		return nil, fmt.Errorf("URL内容获取功能尚未实现")
	} else if request.FilePath != "" {
		// TODO: 实现文件内容获取
		sourceType = "file"
		return nil, fmt.Errorf("文件内容获取功能尚未实现")
	}
	
	// 将文档分块
	chunks := splitTextIntoChunks(content, chunkSize, chunkOverlap)
	
	// 准备metadata
	metadata := request.Metadata
	if metadata == nil {
		metadata = make(map[string]interface{})
	}
	
	// 添加源信息
	if sourceURL != "" {
		metadata["url"] = sourceURL
	}
	metadata["source_type"] = sourceType
	metadata["chunk_size"] = chunkSize
	metadata["chunk_overlap"] = chunkOverlap
	metadata["upload_time"] = time.Now().Format(time.RFC3339)
	
	// 为每个文本块创建嵌入
	var documents []models.Document
	var documentIDs []string
	totalTokens := 0
	
	for i, chunk := range chunks {
		// 如果跳过嵌入，则创建一个没有嵌入向量的文档
		if request.SkipEmbedding {
			doc := models.Document{
				Content:    chunk,
				Metadata:   copyMetadata(metadata),
				Collection: request.CollectionName,
				ChunkIndex: i,
				Source:     sourceType,
				CreatedAt:  time.Now(),
				UpdatedAt:  time.Now(),
			}
			
			// 添加块索引信息
			doc.Metadata["chunk_index"] = i
			
			documents = append(documents, doc)
			continue
		}
		
		// 创建嵌入向量
		embeddingResult, err := s.embedder.EmbedDocument(ctx, chunk)
		if err != nil {
			return nil, fmt.Errorf("为文本块创建嵌入向量失败: %w", err)
		}
		
		// 创建文档
		doc := models.Document{
			Content:    chunk,
			Metadata:   copyMetadata(metadata),
			Vector:     embeddingResult.Embedding,
			Collection: request.CollectionName,
			ChunkIndex: i,
			Source:     sourceType,
			CreatedAt:  time.Now(),
			UpdatedAt:  time.Now(),
		}
		
		// 添加块索引信息
		doc.Metadata["chunk_index"] = i
		doc.Metadata["token_count"] = embeddingResult.TokenCount
		
		documents = append(documents, doc)
		totalTokens += embeddingResult.TokenCount
	}
	
	// 保存文档到向量存储
	ids, err := s.vectorStore.UpsertDocuments(ctx, request.CollectionName, documents)
	if err != nil {
		return nil, fmt.Errorf("将文档保存到向量存储失败: %w", err)
	}
	
	documentIDs = append(documentIDs, ids...)
	
	// 准备响应
	response := &models.DocumentUploadResponse{
		Success:       true,
		Message:       fmt.Sprintf("成功上传%d个分块", len(chunks)),
		DocumentIDs:   documentIDs,
		ChunkCount:    len(chunks),
		TotalTokens:   totalTokens,
		ProcessTime:   time.Since(startTime).Seconds(),
		CollectionName: request.CollectionName,
	}
	
	return response, nil
}

// splitTextIntoChunks 将文本分块
func splitTextIntoChunks(text string, chunkSize, chunkOverlap int) []string {
	if len(text) <= chunkSize {
		return []string{text}
	}
	
	var chunks []string
	start := 0
	
	for start < len(text) {
		end := start + chunkSize
		if end > len(text) {
			end = len(text)
		}
		
		// 尝试在句子末尾分割
		if end < len(text) {
			// 向后查找最近的句号、问号或感叹号
			for i := end; i > start+chunkSize-100 && i > start; i-- {
				if text[i] == '.' || text[i] == '?' || text[i] == '!' {
					end = i + 1 // 包含标点符号
					break
				}
			}
		}
		
		chunks = append(chunks, text[start:end])
		start = end - chunkOverlap
		
		// 避免重复添加非常小的块
		if start >= len(text)-chunkOverlap {
			break
		}
	}
	
	return chunks
}

// copyMetadata 复制元数据
func copyMetadata(metadata map[string]interface{}) map[string]interface{} {
	copy := make(map[string]interface{})
	for k, v := range metadata {
		copy[k] = v
	}
	return copy
}

// CreateCollection 创建集合
func (s *DefaultRAGService) CreateCollection(ctx context.Context, request models.CollectionCreateRequest) (*models.Collection, error) {
	// 参数验证
	if request.Name == "" {
		return nil, fmt.Errorf("集合名称不能为空")
	}
	
	// 检查集合是否已存在
	exists, err := s.vectorStore.CollectionExists(ctx, request.Name)
	if err != nil {
		return nil, fmt.Errorf("检查集合是否存在失败: %w", err)
	}
	
	if exists {
		return nil, fmt.Errorf("集合 %s 已存在", request.Name)
	}
	
	// 确定向量维度
	dimension := 1536 // 默认维度
	if request.Dimension > 0 {
		dimension = request.Dimension
	} else if s.embedder != nil {
		dimension = s.embedder.GetDimensions()
	}
	
	// 创建集合
	err = s.vectorStore.CreateCollection(ctx, request.Name, dimension, request.Description)
	if err != nil {
		return nil, fmt.Errorf("创建集合失败: %w", err)
	}
	
	// 获取创建的集合信息
	collection, err := s.vectorStore.GetCollection(ctx, request.Name)
	if err != nil {
		return nil, fmt.Errorf("获取集合信息失败: %w", err)
	}
	
	return collection, nil
}

// DeleteCollection 删除集合
func (s *DefaultRAGService) DeleteCollection(ctx context.Context, name string) error {
	// 参数验证
	if name == "" {
		return fmt.Errorf("集合名称不能为空")
	}
	
	// 检查集合是否存在
	exists, err := s.vectorStore.CollectionExists(ctx, name)
	if err != nil {
		return fmt.Errorf("检查集合是否存在失败: %w", err)
	}
	
	if !exists {
		return fmt.Errorf("集合 %s 不存在", name)
	}
	
	// 删除集合
	err = s.vectorStore.DeleteCollection(ctx, name)
	if err != nil {
		return fmt.Errorf("删除集合失败: %w", err)
	}
	
	return nil
}

// ListCollections 列出所有集合
func (s *DefaultRAGService) ListCollections(ctx context.Context) ([]models.Collection, error) {
	collections, err := s.vectorStore.ListCollections(ctx)
	if err != nil {
		return nil, fmt.Errorf("获取集合列表失败: %w", err)
	}
	
	return collections, nil
}

// GetCollection 获取集合信息
func (s *DefaultRAGService) GetCollection(ctx context.Context, name string) (*models.Collection, error) {
	// 参数验证
	if name == "" {
		return nil, fmt.Errorf("集合名称不能为空")
	}
	
	// 检查集合是否存在
	exists, err := s.vectorStore.CollectionExists(ctx, name)
		if err != nil {
		return nil, fmt.Errorf("检查集合是否存在失败: %w", err)
	}
	
	if !exists {
		return nil, fmt.Errorf("集合 %s 不存在", name)
	}
	
	// 获取集合信息
	collection, err := s.vectorStore.GetCollection(ctx, name)
	if err != nil {
		return nil, fmt.Errorf("获取集合信息失败: %w", err)
	}
	
	return collection, nil
}

// DeleteDocument 删除文档
func (s *DefaultRAGService) DeleteDocument(ctx context.Context, collectionName string, documentID string) error {
	// 参数验证
	if collectionName == "" {
		return fmt.Errorf("集合名称不能为空")
	}
	
	if documentID == "" {
		return fmt.Errorf("文档ID不能为空")
	}
	
	// 检查集合是否存在
	exists, err := s.vectorStore.CollectionExists(ctx, collectionName)
	if err != nil {
		return fmt.Errorf("检查集合是否存在失败: %w", err)
	}
	
	if !exists {
		return fmt.Errorf("集合 %s 不存在", collectionName)
	}
	
	// 删除文档
	err = s.vectorStore.DeleteDocument(ctx, collectionName, documentID)
	if err != nil {
		return fmt.Errorf("删除文档失败: %w", err)
	}
	
	return nil
}

// GetDocument 获取文档
func (s *DefaultRAGService) GetDocument(ctx context.Context, collectionName string, documentID string) (*models.Document, error) {
	// 参数验证
	if collectionName == "" {
		return nil, fmt.Errorf("集合名称不能为空")
	}
	
	if documentID == "" {
		return nil, fmt.Errorf("文档ID不能为空")
	}
	
	// 检查集合是否存在
	exists, err := s.vectorStore.CollectionExists(ctx, collectionName)
	if err != nil {
		return nil, fmt.Errorf("检查集合是否存在失败: %w", err)
	}
	
	if !exists {
		return nil, fmt.Errorf("集合 %s 不存在", collectionName)
	}
	
	// 获取文档
	doc, err := s.vectorStore.GetDocument(ctx, collectionName, documentID)
	if err != nil {
		return nil, fmt.Errorf("获取文档失败: %w", err)
	}
	
	return doc, nil
}

// Search 在集合中搜索
func (s *DefaultRAGService) Search(ctx context.Context, collectionName string, query string, limit int, filter map[string]interface{}) ([]models.Document, error) {
	// 参数验证
	if collectionName == "" {
		return nil, fmt.Errorf("集合名称不能为空")
	}
	
	if query == "" {
		return nil, fmt.Errorf("查询文本不能为空")
	}
	
	// 设置默认限制数
	if limit <= 0 {
		limit = s.topK
	}
	
	// 检查集合是否存在
	exists, err := s.vectorStore.CollectionExists(ctx, collectionName)
	if err != nil {
		return nil, fmt.Errorf("检查集合是否存在失败: %w", err)
	}
	
	if !exists {
		return nil, fmt.Errorf("集合 %s 不存在", collectionName)
	}
	
	// 为查询生成嵌入向量
	queryVector, err := s.embedder.EmbedQuery(ctx, query)
	if err != nil {
		return nil, fmt.Errorf("生成查询嵌入向量失败: %w", err)
	}
	
	// 执行相似度搜索
	docs, err := s.vectorStore.SimilaritySearch(
		ctx,
		collectionName,
		queryVector,
		limit,
		filter,
		false, // 不包含向量以减少数据传输
	)
	
	if err != nil {
		return nil, fmt.Errorf("执行相似度搜索失败: %w", err)
	}
	
	return docs, nil
}

// CreateEmbedding 创建嵌入向量
func (s *DefaultRAGService) CreateEmbedding(ctx context.Context, texts []string, options map[string]interface{}) (*models.EmbeddingResponse, error) {
	// 参数验证
	if len(texts) == 0 {
		return nil, fmt.Errorf("文本列表不能为空")
	}
	
	startTime := time.Now()
	
	// 获取模型选项
	modelName := s.embedder.GetModelName()
	if options != nil {
		if model, ok := options["model"].(string); ok && model != "" {
			modelName = model
		}
	}
	
	// 批量创建嵌入向量
	embeddings, err := s.embedder.EmbedDocuments(ctx, texts)
	if err != nil {
		return nil, fmt.Errorf("创建嵌入向量失败: %w", err)
	}
	
	// 计算token数
	totalTokens := 0
	for _, text := range texts {
		totalTokens += s.embedder.CountTokens(text)
	}
	
	// 记录指标
	if s.metricsHandler != nil {
		s.metricsHandler.RecordTokens(modelName, "embedding", totalTokens)
	}
	
	// 创建响应
	response := &models.EmbeddingResponse{
		Model:       modelName,
		Dimensions:  s.embedder.GetDimensions(),
		ProcessTime: time.Since(startTime).Seconds(),
		Embeddings:  embeddings,
	}
	
	return response, nil
}

// HybridSearch 混合检索(向量+关键词)
func (s *DefaultRAGService) HybridSearch(ctx context.Context, collectionName string, query string, options models.HybridSearchOptions) ([]models.Document, error) {
	startTime := time.Now()
	
	// 检查集合是否存在
	exists, err := s.vectorStore.CollectionExists(ctx, collectionName)
	if err != nil {
		return nil, fmt.Errorf("检查集合 %s 是否存在失败: %w", collectionName, err)
	}
	
	if !exists {
		return nil, fmt.Errorf("集合 %s 不存在", collectionName)
	}
	
	// 调整默认选项
	if options.TopK <= 0 {
		options.TopK = s.topK
	}
	
	if options.VectorTopK <= 0 {
		options.VectorTopK = options.TopK * 2
	}
	
	if options.KeywordTopK <= 0 {
		options.KeywordTopK = options.TopK * 2
	}
	
	// 权重默认值
	if options.VectorWeight <= 0 && options.KeywordWeight <= 0 {
		options.VectorWeight = 0.7
		options.KeywordWeight = 0.3
	}
	
	// 确保权重和为1
	weightSum := options.VectorWeight + options.KeywordWeight
	if weightSum != 1.0 {
		options.VectorWeight = options.VectorWeight / weightSum
		options.KeywordWeight = options.KeywordWeight / weightSum
	}
	
	// 并行执行向量搜索和关键词搜索
	var (
		vectorResults  []models.Document
		keywordResults []models.Document
		vectorErr      error
		keywordErr     error
		wg             sync.WaitGroup
	)
	
	// 向量搜索
	wg.Add(1)
	go func() {
		defer wg.Done()
		
		// 为查询生成嵌入向量
		queryVector, err := s.embedder.EmbedQuery(ctx, query)
		if err != nil {
			vectorErr = fmt.Errorf("生成查询嵌入向量失败: %w", err)
			return
		}
		
		// 执行向量相似度搜索
		vectorResults, err = s.vectorStore.SimilaritySearch(
			ctx,
			collectionName,
			queryVector,
			options.VectorTopK,
			nil, // 不过滤
			false, // 不包含向量以减少数据传输
		)
		
		if err != nil {
			vectorErr = fmt.Errorf("向量搜索失败: %w", err)
			return
		}
	}()
	
	// 关键词搜索
	wg.Add(1)
	go func() {
		defer wg.Done()
		
		// 检查是否实现了关键词搜索接口
		if keywordSearcher, ok := s.vectorStore.(interface {
			KeywordSearch(ctx context.Context, collectionName string, query string, limit int, filter map[string]interface{}) ([]models.Document, error)
		}); ok {
			// 使用向量存储的关键词搜索实现
			keywordResults, err = keywordSearcher.KeywordSearch(
				ctx,
				collectionName,
				query,
				options.KeywordTopK,
				nil, // 不过滤
			)
			
			if err != nil {
				keywordErr = fmt.Errorf("关键词搜索失败: %w", err)
				return
			}
		} else {
			// 使用简单的关键词搜索回退实现
			keywordResults, err = s.fallbackKeywordSearch(ctx, collectionName, query, options.KeywordTopK)
			if err != nil {
				keywordErr = fmt.Errorf("关键词搜索失败: %w", err)
				return
			}
		}
	}()
	
	// 等待两个搜索完成
	wg.Wait()
	
	// 检查错误
	if vectorErr != nil && keywordErr != nil {
		return nil, fmt.Errorf("混合搜索失败: 向量搜索错误: %v, 关键词搜索错误: %v", vectorErr, keywordErr)
	}
	
	if vectorErr != nil {
		// 如果向量搜索失败，只使用关键词搜索结果
		return keywordResults, nil
	}
	
	if keywordErr != nil {
		// 如果关键词搜索失败，只使用向量搜索结果
		return vectorResults, nil
	}
	
	// 合并和重排结果
	mergedResults := s.mergeSearchResults(vectorResults, keywordResults, options)
	
	// 如果启用了重排序且集成了重排序器
	if options.RerankerEnabled && options.RerankerTopK > 0 {
		// TODO: 实现重排序逻辑
		// 这里可以调用重排序实现
		// mergedResults = s.reranker.Rerank(ctx, query, mergedResults, options.RerankerTopK)
	}
	
	// 记录指标
	if s.metricsHandler != nil {
		s.metricsHandler.RecordRequestDuration("rag", "hybrid_search", time.Since(startTime).Seconds())
	}
	
	return mergedResults, nil
}

// mergeSearchResults 合并向量搜索和关键词搜索结果
func (s *DefaultRAGService) mergeSearchResults(vectorResults, keywordResults []models.Document, options models.HybridSearchOptions) []models.Document {
	// 创建ID到文档的映射
	documentMap := make(map[string]models.Document)
	
	// 记录已有的ID以避免重复
	seenIDs := make(map[string]bool)
	
	// 合并结果集
	var mergedResults []models.Document
	
	// 处理向量结果
	for _, doc := range vectorResults {
		if _, seen := seenIDs[doc.ID]; !seen {
			// 设置向量得分并保存
			doc.Score = doc.Score * options.VectorWeight
			documentMap[doc.ID] = doc
			seenIDs[doc.ID] = true
			mergedResults = append(mergedResults, doc)
		}
	}
	
	// 处理关键词结果
	for _, doc := range keywordResults {
		if existingDoc, seen := documentMap[doc.ID]; seen {
			// 更新已存在文档的分数
			existingDoc.KeywordScore = doc.Score * options.KeywordWeight
			existingDoc.Score = existingDoc.Score + existingDoc.KeywordScore
			documentMap[doc.ID] = existingDoc
		} else {
			// 添加新文档
			doc.KeywordScore = doc.Score * options.KeywordWeight
			doc.Score = doc.KeywordScore
			documentMap[doc.ID] = doc
			mergedResults = append(mergedResults, doc)
		}
	}
	
	// 更新所有结果的分数
	for i, doc := range mergedResults {
		updatedDoc := documentMap[doc.ID]
		mergedResults[i] = updatedDoc
	}
	
	// 重新排序结果
	sort.Slice(mergedResults, func(i, j int) bool {
		return mergedResults[i].Score > mergedResults[j].Score
	})
	
	// 限制结果数量
	if len(mergedResults) > options.TopK {
		mergedResults = mergedResults[:options.TopK]
	}
	
	return mergedResults
}

// fallbackKeywordSearch 备用关键词搜索实现
func (s *DefaultRAGService) fallbackKeywordSearch(ctx context.Context, collectionName string, query string, limit int) ([]models.Document, error) {
	// 简单的关键词匹配实现
	// 获取所有文档
	docs, err := s.vectorStore.GetDocuments(ctx, collectionName, limit*2, nil)
	if err != nil {
		return nil, fmt.Errorf("获取文档失败: %w", err)
	}
	
	// 关键词分词
	keywords := s.extractKeywords(query)
	if len(keywords) == 0 {
		// 没有关键词，返回按时间排序的文档
		sort.Slice(docs, func(i, j int) bool {
			return docs[i].CreatedAt.After(docs[j].CreatedAt)
		})
		
		if len(docs) > limit {
			docs = docs[:limit]
		}
		return docs, nil
	}
	
	// 计算每个文档的关键词匹配得分
	type scoredDoc struct {
		doc   models.Document
		score float64
	}
	
	var scoredDocs []scoredDoc
	for _, doc := range docs {
		score := s.calculateKeywordScore(doc.Content, keywords)
		scoredDocs = append(scoredDocs, scoredDoc{doc: doc, score: score})
	}
	
	// 排序
	sort.Slice(scoredDocs, func(i, j int) bool {
		return scoredDocs[i].score > scoredDocs[j].score
	})
	
	// 转换回文档列表
	var result []models.Document
	for i, sd := range scoredDocs {
		if i >= limit {
			break
		}
		sd.doc.Score = sd.score
		result = append(result, sd.doc)
	}
	
	return result, nil
}

// extractKeywords 从查询中提取关键词
func (s *DefaultRAGService) extractKeywords(query string) []string {
	// 分词
	words := strings.Fields(strings.ToLower(query))
	
	// 移除停用词
	stopwords := map[string]bool{
		"的":   true, "了":   true, "在":   true, "是":   true, "我":   true,
		"有":   true, "和":   true, "就":   true, "不":   true, "人":   true,
		"都":   true, "一":   true, "一个":  true, "上":   true, "也":   true,
		"很":   true, "到":   true, "说":   true, "要":   true, "去":   true,
		"你":   true, "会":   true, "着":   true, "没有":  true, "看":   true,
		"好":   true, "自己":  true, "这":   true, "那":   true, "么":   true,
		"the": true, "a":   true, "an":  true, "of":  true, "to":  true,
		"in":  true, "for": true, "and": true, "or":  true, "but": true,
		"is":  true, "are": true, "was": true, "be":  true, "on":  true,
	}
	
	var keywords []string
	for _, word := range words {
		if len(word) > 1 && !stopwords[word] {
			keywords = append(keywords, word)
		}
	}
	
	return keywords
}

// calculateKeywordScore 计算内容与关键词的匹配得分
func (s *DefaultRAGService) calculateKeywordScore(content string, keywords []string) float64 {
	if len(keywords) == 0 {
		return 0
	}
	
	content = strings.ToLower(content)
	
	// 实现简单的TF-IDF算法
	var totalScore float64
	for _, keyword := range keywords {
		// 词频 (TF)
		count := strings.Count(content, keyword)
		if count > 0 {
			// 考虑词频和关键词长度
			score := float64(count) * math.Log(float64(len(keyword)))
			totalScore += score
		}
	}
	
	// 标准化得分 (0-1之间)
	if totalScore > 0 {
		// 根据内容长度归一化
		contentLength := float64(len(content))
		if contentLength > 0 {
			totalScore = totalScore / math.Sqrt(contentLength)
		}
		
		// 限制最大得分为1
		if totalScore > 1 {
			totalScore = 1
		}
	}
	
	return totalScore
}

// RewriteQuery 查询改写
func (s *DefaultRAGService) RewriteQuery(ctx context.Context, request models.QueryRewriteRequest) (*models.QueryRewriteResponse, error) {
	startTime := time.Now()
	
	// 准备响应
	response := &models.QueryRewriteResponse{
		OriginalQuery: request.Query,
		RewrittenQuery: request.Query, // 默认不改写
	}
	
	// 如果未指定模式，默认为扩展模式
	mode := request.Mode
	if mode == "" {
		mode = "expand"
	}
	
	// 检查缓存（如果有缓存模块）
	// TODO: 实现缓存逻辑
	
	// 创建改写提示
	var prompt string
	switch mode {
	case "expand":
		prompt = fmt.Sprintf(`你是一个专业的查询改写助手，专门负责改进用户的搜索查询以获得更好的检索效果。
请对以下搜索查询进行改写，使其更适合进行文档检索。改写应包括：
1. 扩展关键词和同义词
2. 使用更具体和明确的术语
3. 添加可能相关的领域专业术语

原始查询: %s

改写后的查询应保持在一个句子内，不要添加解释。直接给出改写后的查询。`, request.Query)

	case "focus":
		prompt = fmt.Sprintf(`你是一个专业的查询改写助手，专门负责改进用户的搜索查询以获得更聚焦的检索结果。
请对以下搜索查询进行改写，使其更加专注于核心问题，去除不必要的修饰词和模糊表达。改写应当：
1. 提取核心问题或需求
2. 使用更精确的术语
3. 移除无关的修饰词

原始查询: %s

改写后的查询应保持在一个句子内，不要添加解释。直接给出改写后的查询。`, request.Query)

	case "decompose":
		prompt = fmt.Sprintf(`你是一个专业的查询分解助手，专门负责将复杂查询分解为多个简单查询。
请将以下复杂查询分解为2-5个独立的子查询，每个子查询应专注于原始问题的一个方面。

原始复杂查询: %s

请输出一个子查询列表，每行一个，不要有编号或其他格式标记。不要添加任何解释。`, request.Query)
	
	default:
		return nil, fmt.Errorf("不支持的查询改写模式: %s", mode)
	}
	
	// 调用LLM进行查询改写
	// 检查是否有集成LLM客户端
	if s.llmClient == nil {
		return nil, fmt.Errorf("未配置LLM客户端，无法执行查询改写")
	}
	
	// 调用LLM
	llmResponse, err := s.llmClient.Complete(ctx, prompt, map[string]interface{}{
		"temperature": 0.2, // 低温度保持确定性
		"max_tokens": 200,  // 限制输出长度
	})
	
	if err != nil {
		return nil, fmt.Errorf("LLM查询改写失败: %w", err)
	}
	
	// 处理LLM响应
	output := strings.TrimSpace(llmResponse)
	
	if mode == "decompose" {
		// 如果是分解模式，则拆分为多个子查询
		subQueries := strings.Split(output, "\n")
		
		// 清理子查询
		var cleanSubQueries []string
		for _, q := range subQueries {
			q = strings.TrimSpace(q)
			if q != "" {
				cleanSubQueries = append(cleanSubQueries, q)
			}
		}
		
		response.SubQueries = cleanSubQueries
		
		// 如果能够分解出子查询，也设置第一个子查询为改写结果
		if len(cleanSubQueries) > 0 {
			response.RewrittenQuery = cleanSubQueries[0]
		}
	} else {
		// 扩展或聚焦模式，直接使用输出作为改写结果
		response.RewrittenQuery = output
	}
	
	// 设置处理时间
	response.ProcessTime = time.Since(startTime).Seconds()
	
	// 记录指标
	if s.metricsHandler != nil {
		s.metricsHandler.RecordRequestDuration("rag", "query_rewrite", response.ProcessTime)
	}
	
	return response, nil
}

// DecomposeQuery 分解复杂查询为多个子查询
func (s *DefaultRAGService) DecomposeQuery(ctx context.Context, query string, options map[string]interface{}) ([]string, error) {
	// 创建分解查询请求
	request := models.QueryRewriteRequest{
		Query: query,
		Mode:  "decompose",
	}
	
	// 调用查询改写功能
	response, err := s.RewriteQuery(ctx, request)
	if err != nil {
		return nil, fmt.Errorf("分解查询失败: %w", err)
	}
	
	return response.SubQueries, nil
}

// CreateMultiModalEmbedding 创建多模态嵌入向量
func (s *DefaultRAGService) CreateMultiModalEmbedding(ctx context.Context, request models.EmbeddingRequest) (*models.EmbeddingResponse, error) {
	startTime := time.Now()
	
	// 准备响应
	response := &models.EmbeddingResponse{
		Model: "default_multimodal",
		ProcessTime: 0,
	}
	
	// 验证请求参数
	if request.EmbeddingType == "" {
		request.EmbeddingType = string(models.EmbeddingTypeText)
	}
	
	// 根据嵌入类型选择处理逻辑
	switch request.EmbeddingType {
	case string(models.EmbeddingTypeText):
		// 文本嵌入
		if len(request.Texts) == 0 {
			return nil, fmt.Errorf("文本嵌入请求必须包含文本")
		}
		
		// 调用文本嵌入模型
		embeddings, err := s.embedder.BatchEmbedTexts(ctx, request.Texts)
		if err != nil {
			return nil, fmt.Errorf("文本嵌入失败: %w", err)
		}
		
		// 设置响应信息
		response.Embeddings = embeddings
		response.Dimensions = len(embeddings[0])
		
	case string(models.EmbeddingTypeImage):
		// 图像嵌入
		if len(request.MediaPaths) == 0 {
			return nil, fmt.Errorf("图像嵌入请求必须包含图像路径")
		}
		
		// 检查是否有图像嵌入模型
		imageEmbedder, ok := s.embedder.(interface {
			EmbedImages(ctx context.Context, imagePaths []string) ([][]float32, error)
		})
		
		if !ok {
			return nil, fmt.Errorf("当前嵌入模型不支持图像嵌入")
		}
		
		// 调用图像嵌入模型
		embeddings, err := imageEmbedder.EmbedImages(ctx, request.MediaPaths)
		if err != nil {
			return nil, fmt.Errorf("图像嵌入失败: %w", err)
		}
		
		// 设置响应信息
		response.Embeddings = embeddings
		response.Dimensions = len(embeddings[0])
		response.Model = "image_embedder"
		
	case string(models.EmbeddingTypeAudio):
		// 音频嵌入
		if len(request.MediaPaths) == 0 {
			return nil, fmt.Errorf("音频嵌入请求必须包含音频路径")
		}
		
		// 检查是否有音频嵌入模型
		audioEmbedder, ok := s.embedder.(interface {
			EmbedAudio(ctx context.Context, audioPaths []string) ([][]float32, error)
		})
		
		if !ok {
			return nil, fmt.Errorf("当前嵌入模型不支持音频嵌入")
		}
		
		// 调用音频嵌入模型
		embeddings, err := audioEmbedder.EmbedAudio(ctx, request.MediaPaths)
		if err != nil {
			return nil, fmt.Errorf("音频嵌入失败: %w", err)
		}
		
		// 设置响应信息
		response.Embeddings = embeddings
		response.Dimensions = len(embeddings[0])
		response.Model = "audio_embedder"
		
	case string(models.EmbeddingTypeVideo):
		// 视频嵌入
		if len(request.MediaPaths) == 0 {
			return nil, fmt.Errorf("视频嵌入请求必须包含视频路径")
		}
		
		// TODO: 实现视频嵌入
		return nil, fmt.Errorf("视频嵌入功能尚未实现")
		
	default:
		return nil, fmt.Errorf("不支持的嵌入类型: %s", request.EmbeddingType)
	}
	
	// 设置处理时间
	response.ProcessTime = time.Since(startTime).Seconds()
	response.EmbeddingType = request.EmbeddingType
	
	// 记录指标
	if s.metricsHandler != nil {
		s.metricsHandler.RecordRequestDuration("rag", "multimodal_embedding", response.ProcessTime)
	}
	
	return response, nil
} 

// UploadMultiModalDocument 上传多模态文档
func (s *DefaultRAGService) UploadMultiModalDocument(ctx context.Context, request models.DocumentUploadRequest) (*models.DocumentUploadResponse, error) {
	startTime := time.Now()
	
	// 检查集合是否存在
	exists, err := s.vectorStore.CollectionExists(ctx, request.CollectionName)
	if err != nil {
		return nil, fmt.Errorf("检查集合是否存在失败: %w", err)
	}
	
	if !exists {
		// 创建集合
		_, err = s.CreateCollection(ctx, models.CollectionCreateRequest{
			Name: request.CollectionName,
			Description: "多模态文档集合",
		})
		
		if err != nil {
			return nil, fmt.Errorf("创建集合失败: %w", err)
		}
	}
	
	// 准备响应
	response := &models.DocumentUploadResponse{
		Success:        true,
		Message:        "文档上传成功",
		CollectionName: request.CollectionName,
		DocumentType:   request.DocumentType,
	}
	
	// 验证请求参数
	if request.DocumentType == "" {
		request.DocumentType = string(models.EmbeddingTypeText)
	}
	
	// 根据文档类型处理
	switch request.DocumentType {
	case string(models.EmbeddingTypeText):
		// 文本文档，使用标准上传流程
		return s.UploadDocument(ctx, request)
		
	case string(models.EmbeddingTypeImage):
		// 图像文档
		if request.MediaFilePath == "" && request.URL == "" {
			return nil, fmt.Errorf("图像文档必须提供媒体文件路径或URL")
		}
		
		// 准备嵌入请求
		mediaPath := request.MediaFilePath
		if mediaPath == "" {
			mediaPath = request.URL
		}
		
		embedReq := models.EmbeddingRequest{
			EmbeddingType: request.DocumentType,
			MediaPaths:    []string{mediaPath},
			Model:         request.EmbeddingModel,
		}
		
		// 获取图像嵌入
		embedResp, err := s.CreateMultiModalEmbedding(ctx, embedReq)
		if err != nil {
			return nil, fmt.Errorf("生成图像嵌入失败: %w", err)
		}
		
		// 准备图像文档元数据
		if request.Metadata == nil {
			request.Metadata = make(map[string]interface{})
		}
		
		request.Metadata["document_type"] = request.DocumentType
		request.Metadata["media_path"] = mediaPath
		request.Metadata["dimensions"] = embedResp.Dimensions
		request.Metadata["model"] = embedResp.Model
		
		// 生成文档ID
		docID := generateUUID()
		
		// 存储图像文档
		err = s.vectorStore.UpsertVectors(
			ctx,
			request.CollectionName,
			[]string{docID},
			embedResp.Embeddings,
			[]string{"图像文档: " + mediaPath}, // 简单描述作为内容
			[]map[string]interface{}{request.Metadata},
		)
		
		if err != nil {
			return nil, fmt.Errorf("存储图像文档失败: %w", err)
		}
		
		// 更新响应
		response.DocumentIDs = []string{docID}
		response.ChunkCount = 1
		
	case string(models.EmbeddingTypeAudio):
		// 音频文档
		if request.MediaFilePath == "" && request.URL == "" {
			return nil, fmt.Errorf("音频文档必须提供媒体文件路径或URL")
		}
		
		// 准备嵌入请求
		mediaPath := request.MediaFilePath
		if mediaPath == "" {
			mediaPath = request.URL
		}
		
		embedReq := models.EmbeddingRequest{
			EmbeddingType: request.DocumentType,
			MediaPaths:    []string{mediaPath},
			Model:         request.EmbeddingModel,
		}
		
		// 获取音频嵌入
		embedResp, err := s.CreateMultiModalEmbedding(ctx, embedReq)
		if err != nil {
			return nil, fmt.Errorf("生成音频嵌入失败: %w", err)
		}
		
		// 准备音频文档元数据
		if request.Metadata == nil {
			request.Metadata = make(map[string]interface{})
		}
		
		request.Metadata["document_type"] = request.DocumentType
		request.Metadata["media_path"] = mediaPath
		request.Metadata["dimensions"] = embedResp.Dimensions
		request.Metadata["model"] = embedResp.Model
		
		// 生成文档ID
		docID := generateUUID()
		
		// 存储音频文档
		err = s.vectorStore.UpsertVectors(
			ctx,
			request.CollectionName,
			[]string{docID},
			embedResp.Embeddings,
			[]string{"音频文档: " + mediaPath}, // 简单描述作为内容
			[]map[string]interface{}{request.Metadata},
		)
		
		if err != nil {
			return nil, fmt.Errorf("存储音频文档失败: %w", err)
		}
		
		// 更新响应
		response.DocumentIDs = []string{docID}
		response.ChunkCount = 1
		
	case string(models.EmbeddingTypeVideo):
		// 视频文档
		return nil, fmt.Errorf("视频文档上传功能尚未实现")
		
	default:
		return nil, fmt.Errorf("不支持的文档类型: %s", request.DocumentType)
	}
	
	// 设置处理时间
	response.ProcessTime = time.Since(startTime).Seconds()
	
	// 记录指标
	if s.metricsHandler != nil {
		s.metricsHandler.RecordRequestDuration("rag", "upload_multimodal", response.ProcessTime)
	}
	
	return response, nil
}

// generateUUID 生成UUID
func generateUUID() string {
	return fmt.Sprintf("%d-%s", time.Now().UnixNano(), randomString(8))
}

// randomString 生成随机字符串
func randomString(length int) string {
	const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	result := make([]byte, length)
	for i := range result {
		result[i] = charset[time.Now().UnixNano()%int64(len(charset))]
		// 等待一下，确保纳秒级别的随机性
		time.Sleep(time.Nanosecond)
	}
	return string(result)
} 