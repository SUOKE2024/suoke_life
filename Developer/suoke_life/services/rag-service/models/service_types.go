package models

import "time"

// SearchRequest 搜索请求
type SearchRequest struct {
	Query      string                 `json:"query" binding:"required"`
	Collection string                 `json:"collection" binding:"required"`
	Limit      int                    `json:"limit"`
	Filters    map[string]interface{} `json:"filters"`
}

// SearchResponse 搜索响应
type SearchResponse struct {
	Results        []Document `json:"results"`
	QueryVector    []float32  `json:"query_vector,omitempty"`
	TotalResults   int        `json:"total_results"`
	ProcessingTime int64      `json:"processing_time_ms"`
}

// AddDocumentsRequest 添加文档请求
type AddDocumentsRequest struct {
	Collection string     `json:"collection" binding:"required"`
	Documents  []Document `json:"documents" binding:"required"`
}

// AddDocumentsResponse 添加文档响应
type AddDocumentsResponse struct {
	Status         string `json:"status"`
	DocumentCount  int    `json:"document_count"`
	Collection     string `json:"collection"`
	ProcessingTime int64  `json:"processing_time_ms"`
}

// DeleteDocumentsRequest 删除文档请求
type DeleteDocumentsRequest struct {
	Collection  string   `json:"collection" binding:"required"`
	DocumentIDs []string `json:"document_ids" binding:"required"`
}

// DeleteDocumentsResponse 删除文档响应
type DeleteDocumentsResponse struct {
	Status         string `json:"status"`
	DeletedCount   int    `json:"deleted_count"`
	Collection     string `json:"collection"`
	ProcessingTime int64  `json:"processing_time_ms"`
}

// ListCollectionsResponse 集合列表响应
type ListCollectionsResponse struct {
	Collections    []Collection `json:"collections"`
	TotalCount     int          `json:"total_count"`
	ProcessingTime int64        `json:"processing_time_ms"`
}

// CreateCollectionRequest 创建集合请求
type CreateCollectionRequest struct {
	Name        string `json:"name" binding:"required"`
	Description string `json:"description"`
	Dimension   int    `json:"dimension"`
}

// CreateCollectionResponse 创建集合响应
type CreateCollectionResponse struct {
	Status         string     `json:"status"`
	Collection     Collection `json:"collection"`
	ProcessingTime int64      `json:"processing_time_ms"`
}

// DeleteCollectionRequest 删除集合请求
type DeleteCollectionRequest struct {
	Name string `json:"name" binding:"required"`
}

// DeleteCollectionResponse 删除集合响应
type DeleteCollectionResponse struct {
	Status         string `json:"status"`
	Name           string `json:"name"`
	ProcessingTime int64  `json:"processing_time_ms"`
}

// GetDocumentRequest 获取文档请求
type GetDocumentRequest struct {
	Collection string `json:"collection" binding:"required"`
	DocumentID string `json:"document_id" binding:"required"`
}

// GetDocumentResponse 获取文档响应
type GetDocumentResponse struct {
	Document       Document `json:"document"`
	ProcessingTime int64    `json:"processing_time_ms"`
}

// HealthCheckResponse 健康检查响应
type HealthCheckResponse struct {
	Status    string            `json:"status"`
	Version   string            `json:"version"`
	Timestamp time.Time         `json:"timestamp"`
	Details   map[string]string `json:"details,omitempty"`
} 