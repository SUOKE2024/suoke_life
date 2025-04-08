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
}

// SearchResult 搜索结果
type SearchResult struct {
	ID         string                 `json:"id"`
	Content    string                 `json:"content"`
	Metadata   map[string]interface{} `json:"metadata"`
	Score      float64                `json:"score"`
	Collection string                 `json:"collection,omitempty"`
	Source     string                 `json:"source,omitempty"`
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
}

// CollectionCreateRequest 创建集合请求
type CollectionCreateRequest struct {
	Name        string `json:"name" binding:"required"`
	Description string `json:"description"`
	Dimension   int    `json:"dimension"`
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
}

// EmbeddingResponse 嵌入响应
type EmbeddingResponse struct {
	Embeddings [][]float32 `json:"embeddings"`
	Model      string      `json:"model"`
	Dimensions int         `json:"dimensions"`
	ProcessTime float64    `json:"process_time"`
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
}

// Similarity enum for similarity methods
type Similarity string

const (
	SimilarityCosine     Similarity = "cosine"
	SimilarityEuclidean  Similarity = "euclidean"
	SimilarityDotProduct Similarity = "dot_product"
)

// QueryType enum for query types
type QueryType string

const (
	QueryTypeKNN    QueryType = "knn"
	QueryTypeMMR    QueryType = "mmr"
	QueryTypeHybrid QueryType = "hybrid"
	// 相似度查询
	QueryTypeSimilarity QueryType = "similarity"
)

// RAGRequest RAG请求模型
type RAGRequest struct {
	// Query 用户查询
	Query string `json:"query"`

	// CollectionName 集合名称
	CollectionName string `json:"collection_name,omitempty"`

	// TopK 返回结果数量
	TopK int `json:"top_k,omitempty"`

	// Filter 元数据过滤条件
	Filter map[string]interface{} `json:"filter,omitempty"`

	// UseReranker 是否使用重排序
	UseReranker bool `json:"use_reranker,omitempty"`

	// EnableWebSearch 是否启用网络搜索
	EnableWebSearch bool `json:"enable_web_search,omitempty"`

	// ConversationContext 对话上下文
	ConversationContext []Message `json:"conversation_context,omitempty"`

	// MaxTokens 最大token数
	MaxTokens int `json:"max_tokens,omitempty"`
}

// RAGResponse RAG响应模型
type RAGResponse struct {
	// Answer 生成的回答
	Answer string `json:"answer"`

	// Documents 检索到的文档
	Documents []SearchResult `json:"documents,omitempty"`

	// ConversationID 对话ID
	ConversationID string `json:"conversation_id,omitempty"`

	// TokenUsage token使用情况
	TokenUsage TokenUsage `json:"token_usage,omitempty"`

	// Sources 信息来源
	Sources []Source `json:"sources,omitempty"`

	// WebSearchResults 网络搜索结果
	WebSearchResults []WebSearchResult `json:"web_search_results,omitempty"`

	// Debug 调试信息
	Debug map[string]interface{} `json:"debug,omitempty"`
}

// Source 信息来源
type Source struct {
	// Title 标题
	Title string `json:"title,omitempty"`

	// URL 链接
	URL string `json:"url,omitempty"`

	// Content 内容摘要
	Content string `json:"content,omitempty"`

	// DocumentID 文档ID
	DocumentID string `json:"document_id,omitempty"`

	// Metadata 元数据
	Metadata map[string]interface{} `json:"metadata,omitempty"`

	// Score 相关性分数
	Score float32 `json:"score,omitempty"`
}

// Message 对话消息
type Message struct {
	// Role 角色
	Role string `json:"role"`

	// Content 内容
	Content string `json:"content"`
}

// TokenUsage token使用情况
type TokenUsage struct {
	// PromptTokens 提示tokens
	PromptTokens int `json:"prompt_tokens"`

	// CompletionTokens 补全tokens
	CompletionTokens int `json:"completion_tokens"`

	// TotalTokens 总tokens
	TotalTokens int `json:"total_tokens"`
}

// StreamRAGResponse 流式RAG响应
type StreamRAGResponse struct {
	// ID 响应ID
	ID string `json:"id"`

	// Object 对象类型
	Object string `json:"object"`

	// Created 创建时间
	Created int64 `json:"created"`

	// Model 模型名称
	Model string `json:"model"`

	// Choices 选择结果
	Choices []StreamChoice `json:"choices"`
}

// StreamChoice 流式选择
type StreamChoice struct {
	// Delta 增量内容
	Delta StreamDelta `json:"delta"`

	// Index 索引
	Index int `json:"index"`

	// FinishReason 结束原因
	FinishReason string `json:"finish_reason,omitempty"`
}

// StreamDelta 流式增量
type StreamDelta struct {
	// Role 角色
	Role string `json:"role,omitempty"`

	// Content 内容
	Content string `json:"content,omitempty"`
} 