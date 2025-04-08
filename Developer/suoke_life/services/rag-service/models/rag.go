package models

import "time"

// QueryRequest 查询请求
type QueryRequest struct {
	Query           string            `json:"query" binding:"required"`
	Stream          bool              `json:"stream"`
	MaxTokens       int               `json:"max_tokens"`
	Temperature     float64           `json:"temperature"`
	TopK            int               `json:"top_k"`
	Metadata        map[string]string `json:"metadata"`
	CollectionNames []string          `json:"collection_names"`
	UseReranker     bool              `json:"use_reranker"`
	RerankerTopK    int               `json:"reranker_top_k"`
	SessionID       string            `json:"session_id"`
	UserId          string            `json:"user_id"`
	EnableWebSearch bool              `json:"enable_web_search"`
	WebSearchLimit  int               `json:"web_search_limit"`
	// 查询改写相关
	UseQueryRewrite  bool   `json:"use_query_rewrite"`
	RewrittenQuery   string `json:"rewritten_query,omitempty"`
	// 检索策略
	RetrievalStrategy string `json:"retrieval_strategy,omitempty"`
	// 混合检索权重 (0-1之间)
	HybridWeight     float64 `json:"hybrid_weight,omitempty"`
}

// QueryResult 查询结果
type QueryResult struct {
	Query          string           `json:"query"`
	Results        []Document       `json:"results"`
	Answer         string           `json:"answer"`
	Citations      []Citation       `json:"citations"`
	Stream         bool             `json:"stream"`
	RagTime        float64          `json:"rag_time"`
	EmbeddingTime  float64          `json:"embedding_time"`
	VectorDBTime   float64          `json:"vectordb_time"`
	RerankerTime   float64          `json:"reranker_time"`
	LLMTime        float64          `json:"llm_time"`
	WebSearchTime  float64          `json:"web_search_time"`
	TotalTime      float64          `json:"total_time"`
	SessionID      string           `json:"session_id"`
	UserId         string           `json:"user_id"`
	Timestamp      time.Time        `json:"timestamp"`
	MetricsDetails *MetricsDetails  `json:"metrics_details,omitempty"`
	WebResults     []WebSearchResult `json:"web_results,omitempty"`
	// 查询改写信息
	OriginalQuery   string           `json:"original_query,omitempty"`
	RewrittenQuery  string           `json:"rewritten_query,omitempty"`
	// 检索策略信息
	RetrievalStrategy string          `json:"retrieval_strategy,omitempty"`
}

// Document 向量数据库文档
type Document struct {
	ID          string                 `json:"id"`
	Content     string                 `json:"content"`
	Metadata    map[string]interface{} `json:"metadata"`
	Score       float64                `json:"score"`
	Vector      []float32              `json:"vector,omitempty"`
	Collection  string                 `json:"collection"`
	ChunkIndex  int                    `json:"chunk_index"`
	Source      string                 `json:"source"`
	CreatedAt   time.Time              `json:"created_at"`
	UpdatedAt   time.Time              `json:"updated_at"`
	RerankerScore float64              `json:"reranker_score,omitempty"`
	// 文档类型
	DocumentType    string              `json:"document_type,omitempty"`
	// 多模态数据路径或链接
	MediaURL        string              `json:"media_url,omitempty"`
	// 关键词检索分数 (用于混合检索)
	KeywordScore    float64             `json:"keyword_score,omitempty"`
}

// SearchResult 搜索结果
type SearchResult struct {
	ID         string                 `json:"id"`
	Content    string                 `json:"content"`
	Metadata   map[string]interface{} `json:"metadata"`
	Score      float64                `json:"score"`
	Collection string                 `json:"collection,omitempty"`
	Source     string                 `json:"source,omitempty"`
	// 文档类型
	DocumentType    string              `json:"document_type,omitempty"`
	// 多模态数据路径或链接
	MediaURL        string              `json:"media_url,omitempty"`
}

// Citation 引用信息
type Citation struct {
	DocumentID  string                 `json:"document_id"`
	Text        string                 `json:"text"`
	Score       float64                `json:"score"`
	Metadata    map[string]interface{} `json:"metadata"`
	StartIndex  int                    `json:"start_index"`
	EndIndex    int                    `json:"end_index"`
	Collection  string                 `json:"collection"`
	Source      string                 `json:"source"`
	URL         string                 `json:"url,omitempty"`
	// 文档类型
	DocumentType string               `json:"document_type,omitempty"`
	// 多模态数据路径或链接
	MediaURL     string               `json:"media_url,omitempty"`
}

// Collection 集合信息
type Collection struct {
	Name        string    `json:"name"`
	Description string    `json:"description"`
	Count       int       `json:"count"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
	Dimension   int       `json:"dimension"`
	Status      string    `json:"status"`
	// 集合支持的嵌入类型
	EmbeddingTypes []string `json:"embedding_types,omitempty"`
}

// CollectionCreateRequest 创建集合请求
type CollectionCreateRequest struct {
	Name        string `json:"name" binding:"required"`
	Description string `json:"description"`
	Dimension   int    `json:"dimension"`
	// 是否启用混合检索
	EnableHybridSearch bool     `json:"enable_hybrid_search"`
	// 支持的嵌入类型
	EmbeddingTypes     []string `json:"embedding_types,omitempty"`
}

// MetricsDetails 指标详情
type MetricsDetails struct {
	EmbeddingTokens  int     `json:"embedding_tokens"`
	LLMTokens        int     `json:"llm_tokens"`
	LLMInputTokens   int     `json:"llm_input_tokens"`
	LLMOutputTokens  int     `json:"llm_output_tokens"`
	LLMCost          float64 `json:"llm_cost"`
	EmbeddingCost    float64 `json:"embedding_cost"`
	TotalCost        float64 `json:"total_cost"`
	// 查询改写相关指标
	QueryRewriteTime float64 `json:"query_rewrite_time,omitempty"`
	// 混合检索相关指标
	KeywordSearchTime float64 `json:"keyword_search_time,omitempty"`
	HybridMergeTime   float64 `json:"hybrid_merge_time,omitempty"`
}

// WebSearchResult 网页搜索结果
type WebSearchResult struct {
	Title       string    `json:"title"`
	URL         string    `json:"url"`
	Description string    `json:"description"`
	Content     string    `json:"content,omitempty"`
	Source      string    `json:"source"`
	PublishedAt time.Time `json:"published_at,omitempty"`
	Score       float64   `json:"score,omitempty"`
}

// DocumentUploadRequest 文档上传请求
type DocumentUploadRequest struct {
	CollectionName  string                 `json:"collection_name" binding:"required"`
	Content         string                 `json:"content,omitempty"`
	Metadata        map[string]interface{} `json:"metadata"`
	URL             string                 `json:"url,omitempty"`
	FilePath        string                 `json:"file_path,omitempty"`
	ChunkSize       int                    `json:"chunk_size"`
	ChunkOverlap    int                    `json:"chunk_overlap"`
	SkipEmbedding   bool                   `json:"skip_embedding"`
	// 文档类型 (text, image, audio, video)
	DocumentType    string                 `json:"document_type,omitempty"`
	// 多模态文件路径
	MediaFilePath   string                 `json:"media_file_path,omitempty"`
	// 多模态嵌入模型
	EmbeddingModel  string                 `json:"embedding_model,omitempty"`
}

// DocumentUploadResponse 文档上传响应
type DocumentUploadResponse struct {
	Success       bool     `json:"success"`
	Message       string   `json:"message"`
	DocumentIDs   []string `json:"document_ids"`
	ChunkCount    int      `json:"chunk_count"`
	TotalTokens   int      `json:"total_tokens"`
	ProcessTime   float64  `json:"process_time"`
	CollectionName string  `json:"collection_name"`
	// 文档类型
	DocumentType  string   `json:"document_type,omitempty"`
}

// 流式响应消息类型
const (
	EventStart     = "start"
	EventRunning   = "running"
	EventText      = "text"
	EventCitation  = "citation"
	EventEnd       = "end"
	EventError     = "error"
	EventDocuments = "documents"
)

// StreamMessage 流式响应消息
type StreamMessage struct {
	Event     string              `json:"event"`
	Text      string              `json:"text,omitempty"`
	Citations []Citation          `json:"citations,omitempty"`
	Documents []Document          `json:"documents,omitempty"`
	Error     string              `json:"error,omitempty"`
	Complete  bool                `json:"complete,omitempty"`
	Metrics   *MetricsDetails     `json:"metrics,omitempty"`
	WebResults []WebSearchResult  `json:"web_results,omitempty"`
	// 查询改写信息
	RewrittenQuery string          `json:"rewritten_query,omitempty"`
}

// ErrorResponse 错误响应
type ErrorResponse struct {
	Error   string `json:"error"`
	Code    int    `json:"code"`
	Message string `json:"message"`
}

// EmbeddingRequest 嵌入请求
type EmbeddingRequest struct {
	Texts  []string `json:"texts" binding:"required"`
	Model  string   `json:"model"`
	UserId string   `json:"user_id"`
	// 嵌入类型 (text, image, audio, video)
	EmbeddingType string   `json:"embedding_type,omitempty"`
	// 多模态文件路径
	MediaPaths    []string `json:"media_paths,omitempty"`
}

// EmbeddingResponse 嵌入响应
type EmbeddingResponse struct {
	Embeddings [][]float32 `json:"embeddings"`
	Model      string      `json:"model"`
	Dimensions int         `json:"dimensions"`
	ProcessTime float64    `json:"process_time"`
	// 嵌入类型
	EmbeddingType string    `json:"embedding_type,omitempty"`
}

// SessionInfo 会话信息
type SessionInfo struct {
	SessionID      string            `json:"session_id"`
	UserID         string            `json:"user_id"`
	StartTime      time.Time         `json:"start_time"`
	LastActiveTime time.Time         `json:"last_active_time"`
	QueryCount     int               `json:"query_count"`
	Metadata       map[string]string `json:"metadata"`
	Collections    []string          `json:"collections"`
}

// ChunkingConfig 文本分块配置
type ChunkingConfig struct {
	ChunkSize       int  `json:"chunk_size"`
	ChunkOverlap    int  `json:"chunk_overlap"`
	SkipEmbedding   bool `json:"skip_embedding"`
	IncludeMetadata bool `json:"include_metadata"`
	// 分块策略 (fixed, sentence, paragraph, semantic)
	ChunkStrategy   string `json:"chunk_strategy"`
}

// 相似度计算方法
type Similarity string

const (
	SimilarityCosine     Similarity = "cosine"
	SimilarityDot        Similarity = "dot"
	SimilarityEuclidean  Similarity = "euclidean"
	SimilarityManhattan  Similarity = "manhattan"
)

// 查询类型
type QueryType string

const (
	QueryTypeVector  QueryType = "vector"
	QueryTypeKeyword QueryType = "keyword"
	QueryTypeHybrid  QueryType = "hybrid"
)

// 嵌入类型
type EmbeddingType string

const (
	EmbeddingTypeText  EmbeddingType = "text"
	EmbeddingTypeImage EmbeddingType = "image"
	EmbeddingTypeAudio EmbeddingType = "audio"
	EmbeddingTypeVideo EmbeddingType = "video"
)

// 查询改写请求
type QueryRewriteRequest struct {
	Query      string `json:"query" binding:"required"`
	SessionID  string `json:"session_id,omitempty"`
	UserId     string `json:"user_id,omitempty"`
	Mode       string `json:"mode,omitempty"` // expand, focus, decompose
}

// 查询改写响应
type QueryRewriteResponse struct {
	OriginalQuery  string   `json:"original_query"`
	RewrittenQuery string   `json:"rewritten_query"`
	SubQueries     []string `json:"sub_queries,omitempty"` // 分解查询时使用
	ProcessTime    float64  `json:"process_time"`
}

// 混合检索选项
type HybridSearchOptions struct {
	VectorWeight    float64   `json:"vector_weight"`    // 向量检索权重 (0-1)
	KeywordWeight   float64   `json:"keyword_weight"`   // 关键词检索权重 (0-1)
	TopK            int       `json:"top_k"`            // 总返回结果数
	VectorTopK      int       `json:"vector_top_k"`     // 向量检索返回结果数
	KeywordTopK     int       `json:"keyword_top_k"`    // 关键词检索返回结果数
	RerankerEnabled bool      `json:"reranker_enabled"` // 是否启用重排序
	RerankerTopK    int       `json:"reranker_top_k"`   // 重排序返回结果数
} 