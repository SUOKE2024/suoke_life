package rag

import "time"

// QueryRequest RAG查询请求
type QueryRequest struct {
	// Query 用户查询
	Query string `json:"query"`

	// CollectionName 集合名称
	CollectionName string `json:"collection_name"`

	// TopK 返回的文档数量
	TopK int `json:"top_k"`

	// ScoreThreshold 相似度分数阈值
	ScoreThreshold float32 `json:"score_threshold"`

	// IncludeContent 是否包含文档内容
	IncludeContent bool `json:"include_content"`

	// Temperature 温度参数
	Temperature float64 `json:"temperature"`

	// MaxTokens 生成的最大令牌数
	MaxTokens int `json:"max_tokens"`

	// Filter 过滤条件
	Filter map[string]interface{} `json:"filter"`
}

// QueryResponse RAG查询响应
type QueryResponse struct {
	// Answer LLM生成的回答
	Answer string `json:"answer"`

	// Sources 来源信息
	Sources []Source `json:"sources"`

	// Metadata 元数据
	Metadata map[string]interface{} `json:"metadata"`
}

// Source 来源信息
type Source struct {
	// ID 文档ID
	ID string `json:"id"`

	// Score 相似度分数
	Score float32 `json:"score"`

	// URL 文档URL
	URL string `json:"url"`

	// Title 文档标题
	Title string `json:"title"`
}

// DocumentUploadRequest 文档上传请求
type DocumentUploadRequest struct {
	// CollectionName 集合名称
	CollectionName string `json:"collection_name"`

	// Files 上传的文件
	Files []FileUpload `json:"files"`

	// ChunkSize 分块大小
	ChunkSize int `json:"chunk_size"`

	// ChunkOverlap 分块重叠大小
	ChunkOverlap int `json:"chunk_overlap"`

	// Metadata 元数据
	Metadata map[string]interface{} `json:"metadata"`
}

// FileUpload 文件上传
type FileUpload struct {
	// Filename 文件名
	Filename string `json:"filename"`

	// Content 文件内容
	Content string `json:"content"`

	// MimeType MIME类型
	MimeType string `json:"mime_type"`

	// Title 文档标题
	Title string `json:"title"`
}

// DocumentUploadResponse 文档上传响应
type DocumentUploadResponse struct {
	// CollectionName 集合名称
	CollectionName string `json:"collection_name"`

	// DocumentCount 文档数量
	DocumentCount int `json:"document_count"`

	// Results 处理结果
	Results []DocumentProcessResult `json:"results"`
}

// DocumentProcessResult 文档处理结果
type DocumentProcessResult struct {
	// Filename 文件名
	Filename string `json:"filename"`

	// ChunkIDs 分块ID列表
	ChunkIDs []string `json:"chunk_ids"`

	// ChunkCount 分块数量
	ChunkCount int `json:"chunk_count"`
}

// CollectionCreateRequest 创建集合请求
type CollectionCreateRequest struct {
	// Name 集合名称
	Name string `json:"name"`

	// Description 集合描述
	Description string `json:"description"`
}

// Collection 集合信息
type Collection struct {
	// Name 集合名称
	Name string `json:"name"`

	// Description 集合描述
	Description string `json:"description"`

	// DocumentCount 文档数量
	DocumentCount int `json:"document_count"`

	// CreatedAt 创建时间
	CreatedAt time.Time `json:"created_at"`
}

// Document 文档信息
type Document struct {
	// ID 文档ID
	ID string `json:"id"`

	// Content 文档内容
	Content string `json:"content"`

	// Score 相似度分数
	Score float32 `json:"score,omitempty"`

	// Metadata 元数据
	Metadata map[string]interface{} `json:"metadata"`
}

// EmbeddingResponse 嵌入响应
type EmbeddingResponse struct {
	// Model 模型名称
	Model string `json:"model"`

	// Embeddings 嵌入向量列表
	Embeddings [][]float32 `json:"embeddings"`
} 