package models

import (
	"time"
)

// Document 文档对象
type Document struct {
	// ID 文档唯一标识符
	ID string `json:"id"`
	
	// Content 文档内容
	Content string `json:"content"`
	
	// Metadata 文档元数据
	Metadata *DocumentMetadata `json:"metadata,omitempty"`
	
	// VectorScore 向量搜索分数
	VectorScore float64 `json:"vector_score,omitempty"`
	
	// KeywordScore 关键词搜索分数
	KeywordScore float64 `json:"keyword_score,omitempty"`
	
	// RerankerScore 重排序分数
	RerankerScore float64 `json:"reranker_score,omitempty"`
	
	// FinalScore 最终分数
	FinalScore float64 `json:"final_score,omitempty"`
	
	// Vector 文档向量(非JSON)
	Vector []float32 `json:"-"`
}

// DocumentMetadata 文档元数据
type DocumentMetadata struct {
	// Title 标题
	Title string `json:"title,omitempty"`
	
	// Source 来源
	Source string `json:"source,omitempty"`
	
	// URL 链接
	URL string `json:"url,omitempty"`
	
	// Author 作者
	Author string `json:"author,omitempty"`
	
	// CreatedAt 创建时间
	CreatedAt *time.Time `json:"created_at,omitempty"`
	
	// UpdatedAt 更新时间
	UpdatedAt *time.Time `json:"updated_at,omitempty"`
	
	// Language 语言
	Language string `json:"language,omitempty"`
	
	// ContentType 内容类型
	ContentType string `json:"content_type,omitempty"`
	
	// Properties 自定义属性
	Properties map[string]interface{} `json:"properties,omitempty"`
}

// SearchRequest 搜索请求
type SearchRequest struct {
	// Query 查询文本
	Query string `json:"query"`
	
	// TopK 返回结果数量
	TopK int `json:"top_k,omitempty"`
	
	// Filter 过滤条件
	Filter map[string]interface{} `json:"filter,omitempty"`
	
	// Options 搜索选项
	Options map[string]interface{} `json:"options,omitempty"`
}

// SearchResponse 搜索响应
type SearchResponse struct {
	// Documents 文档列表
	Documents []Document `json:"documents"`
	
	// Query 查询文本
	Query string `json:"query"`
	
	// TotalResults 结果总数
	TotalResults int `json:"total_results"`
	
	// SearchTime 搜索耗时(毫秒)
	SearchTime int64 `json:"search_time_ms"`
	
	// Metadata 搜索元数据
	Metadata map[string]interface{} `json:"metadata,omitempty"`
}

// RerankRequest 重排序请求
type RerankRequest struct {
	// Query 查询文本
	Query string `json:"query"`
	
	// Documents 待重排序文档
	Documents []Document `json:"documents"`
	
	// TopK 返回结果数量
	TopK int `json:"top_k,omitempty"`
	
	// Options 重排序选项
	Options map[string]interface{} `json:"options,omitempty"`
}

// RerankResponse 重排序响应
type RerankResponse struct {
	// Documents 重排序后文档
	Documents []Document `json:"documents"`
	
	// RerankTime 重排序耗时(毫秒)
	RerankTime int64 `json:"rerank_time_ms"`
}

// MultimodalEmbedRequest 多模态嵌入请求
type MultimodalEmbedRequest struct {
	// Texts 文本列表
	Texts []string `json:"texts,omitempty"`
	
	// ImagePaths 图像路径列表
	ImagePaths []string `json:"image_paths,omitempty"`
	
	// AudioPaths 音频路径列表
	AudioPaths []string `json:"audio_paths,omitempty"`
	
	// VideoPaths 视频路径列表
	VideoPaths []string `json:"video_paths,omitempty"`
	
	// Options 嵌入选项
	Options map[string]interface{} `json:"options,omitempty"`
}

// MultimodalEmbedResponse 多模态嵌入响应
type MultimodalEmbedResponse struct {
	// Embeddings 嵌入向量
	Embeddings [][]float32 `json:"embeddings"`
	
	// EmbedTime 嵌入耗时(毫秒)
	EmbedTime int64 `json:"embed_time_ms"`
}

// TCMAnalyzeRequest 中医分析请求
type TCMAnalyzeRequest struct {
	// Text 文本
	Text string `json:"text"`
	
	// ImagePaths 图像路径列表(如舌诊、面诊图像)
	ImagePaths []string `json:"image_paths,omitempty"`
	
	// AudioPaths 音频路径列表(如脉象音频)
	AudioPaths []string `json:"audio_paths,omitempty"`
	
	// Options 分析选项
	Options map[string]interface{} `json:"options,omitempty"`
}

// TCMAnalyzeResponse 中医分析响应
type TCMAnalyzeResponse struct {
	// Terms 中医术语
	Terms []TCMTerm `json:"terms"`
	
	// AnalysisTime 分析耗时(毫秒)
	AnalysisTime int64 `json:"analysis_time_ms"`
	
	// Results 分析结果
	Results map[string]interface{} `json:"results"`
}

// TCMTerm 中医术语
type TCMTerm struct {
	// Term 术语
	Term string `json:"term"`
	
	// Category 类别
	Category string `json:"category"`
	
	// Description 描述
	Description string `json:"description,omitempty"`
	
	// Weight 权重
	Weight float64 `json:"weight,omitempty"`
}