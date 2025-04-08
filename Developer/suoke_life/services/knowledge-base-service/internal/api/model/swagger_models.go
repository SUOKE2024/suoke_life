// Package model 提供API请求和响应的模型定义
package model

// StandardResponse 标准API响应结构
type StandardResponse struct {
	Success bool        `json:"success" example:"true"`
	Code    int         `json:"code" example:"200"`
	Message string      `json:"message" example:"操作成功"`
	Data    interface{} `json:"data,omitempty"`
}

// ErrorResponse 错误响应结构
type ErrorResponse struct {
	Success bool         `json:"success" example:"false"`
	Code    int          `json:"code" example:"400"`
	Message string       `json:"message" example:"请求参数错误"`
	Errors  []FieldError `json:"errors,omitempty"`
}

// FieldError 字段错误
type FieldError struct {
	Field   string `json:"field" example:"title"`
	Message string `json:"message" example:"标题不能为空"`
}

// PaginatedResponse 分页响应结构
type PaginatedResponse struct {
	Total int         `json:"total" example:"100"`
	Page  int         `json:"page" example:"1"`
	Limit int         `json:"limit" example:"20"`
	Items interface{} `json:"items"`
}

// DocumentListItem 文档列表项
type DocumentListItem struct {
	ID        string   `json:"id" example:"doc123"`
	Title     string   `json:"title" example:"中医体质辨识基础"`
	Summary   string   `json:"summary" example:"介绍九种体质的基本特征和辨识方法"`
	Category  string   `json:"category" example:"中医理论"`
	Tags      []string `json:"tags" example:"体质辨识,中医基础"`
	CreatedAt string   `json:"created_at" example:"2024-04-01T08:00:00Z"`
	UpdatedAt string   `json:"updated_at" example:"2024-04-02T10:30:00Z"`
}

// DocumentDetail 文档详情
type DocumentDetail struct {
	ID               string              `json:"id" example:"doc123"`
	Title            string              `json:"title" example:"中医体质辨识基础"`
	Content          string              `json:"content" example:"中医体质学说是中医学对人体生命本质的认识..."`
	Summary          string              `json:"summary" example:"介绍九种体质的基本特征和辨识方法"`
	Category         string              `json:"category" example:"中医理论"`
	Tags             []string            `json:"tags" example:"体质辨识,中医基础"`
	References       []DocumentReference `json:"references,omitempty"`
	RelatedDocuments []string            `json:"related_documents,omitempty" example:"doc456,doc789"`
	Version          int                 `json:"version" example:"2"`
	CreatedAt        string              `json:"created_at" example:"2024-04-01T08:00:00Z"`
	UpdatedAt        string              `json:"updated_at" example:"2024-04-02T10:30:00Z"`
}

// DocumentReference 文档引用
type DocumentReference struct {
	Title  string `json:"title" example:"《中医体质学》"`
	Author string `json:"author,omitempty" example:"王琦"`
	Year   int    `json:"year,omitempty" example:"2005"`
	URL    string `json:"url,omitempty"`
}

// CreateDocumentRequest 创建文档请求
type CreateDocumentRequest struct {
	Title      string              `json:"title" example:"四季养生之春季养生" binding:"required"`
	Content    string              `json:"content" example:"春季养生应当以养肝为主，饮食宜甘少酸..." binding:"required"`
	Summary    string              `json:"summary" example:"介绍春季养生的基本原则和方法" binding:"required"`
	Category   string              `json:"category" example:"养生保健" binding:"required"`
	Tags       []string            `json:"tags" example:"四季养生,春季,养肝"`
	References []DocumentReference `json:"references,omitempty"`
}

// UpdateDocumentRequest 更新文档请求
type UpdateDocumentRequest struct {
	Title      string              `json:"title" example:"四季养生之春季养生指南"`
	Content    string              `json:"content" example:"春季养生应当以养肝为主，饮食宜甘少酸..."`
	Summary    string              `json:"summary" example:"全面介绍春季养生的基本原则和实用方法"`
	Category   string              `json:"category" example:"养生保健"`
	Tags       []string            `json:"tags" example:"四季养生,春季,养肝,实用指南"`
	References []DocumentReference `json:"references,omitempty"`
}

// SearchResult 搜索结果
type SearchResult struct {
	ID         string            `json:"id" example:"doc456"`
	Title      string            `json:"title" example:"四季养生之春季养生指南"`
	Summary    string            `json:"summary" example:"全面介绍春季养生的基本原则和实用方法"`
	Category   string            `json:"category" example:"养生保健"`
	Tags       []string          `json:"tags" example:"四季养生,春季,养肝,实用指南"`
	Highlight  map[string]string `json:"highlight,omitempty"`
	Score      float64           `json:"score,omitempty" example:"0.89"`
	Similarity float64           `json:"similarity,omitempty" example:"0.92"`
}

// CategoryInfo 分类信息
type CategoryInfo struct {
	ID            string `json:"id" example:"cat1"`
	Name          string `json:"name" example:"中医理论"`
	Description   string `json:"description" example:"中医基础理论和概念"`
	DocumentCount int    `json:"document_count" example:"120"`
}

// TagInfo 标签信息
type TagInfo struct {
	ID            string `json:"id" example:"tag1"`
	Name          string `json:"name" example:"四季养生"`
	DocumentCount int    `json:"document_count" example:"45"`
}

// HealthResponse 健康检查响应
type HealthResponse struct {
	Status               string `json:"status" example:"ok"`
	Version              string `json:"version" example:"2024.04.06-abc123"`
	DBConnected          bool   `json:"db_connected" example:"true"`
	VectorStoreConnected bool   `json:"vector_store_connected" example:"true"`
	Uptime               int64  `json:"uptime" example:"1234567"`
}

// SearchQuery 搜索请求
type SearchQuery struct {
	Query    string   `json:"query" example:"春季养生" binding:"required"`
	Page     int      `json:"page" example:"1"`
	Limit    int      `json:"limit" example:"20"`
	Category string   `json:"category,omitempty" example:"养生保健"`
	Tags     []string `json:"tags,omitempty" example:"春季,养肝"`
}

// SemanticSearchQuery 语义搜索请求
type SemanticSearchQuery struct {
	Query     string   `json:"query" example:"如何预防春季肝火旺盛" binding:"required"`
	Page      int      `json:"page" example:"1"`
	Limit     int      `json:"limit" example:"20"`
	Threshold float64  `json:"threshold" example:"0.7"`
	Category  string   `json:"category,omitempty" example:"养生保健"`
	Tags      []string `json:"tags,omitempty" example:"春季,养肝"`
}
