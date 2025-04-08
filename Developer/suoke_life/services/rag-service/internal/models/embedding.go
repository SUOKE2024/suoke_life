package models

// EmbeddingRequest 嵌入请求模型
type EmbeddingRequest struct {
	// Text 需要嵌入的文本
	Text string `json:"text"`

	// Texts 需要批量嵌入的文本列表
	Texts []string `json:"texts,omitempty"`

	// ModelName 模型名称（可选）
	ModelName string `json:"model_name,omitempty"`
}

// EmbeddingResponse 嵌入响应模型
type EmbeddingResponse struct {
	// Embedding 嵌入向量
	Embedding []float32 `json:"embedding,omitempty"`

	// Embeddings 批量嵌入向量
	Embeddings [][]float32 `json:"embeddings,omitempty"`

	// Dimensions 向量维度
	Dimensions int `json:"dimensions"`

	// ModelName 使用的模型名称
	ModelName string `json:"model_name"`

	// TokenCount 处理的token数量
	TokenCount int `json:"token_count,omitempty"`
}

// EmbeddingMetadata 嵌入元数据
type EmbeddingMetadata struct {
	// ModelName 模型名称
	ModelName string `json:"model_name"`

	// Dimensions 向量维度
	Dimensions int `json:"dimensions"`

	// TokenCount token数量
	TokenCount int `json:"token_count,omitempty"`

	// ProcessingTime 处理时间（毫秒）
	ProcessingTime int64 `json:"processing_time,omitempty"`

	// Error 错误信息
	Error string `json:"error,omitempty"`
}

// EmbeddingStats 嵌入统计信息
type EmbeddingStats struct {
	// TotalRequests 总请求数
	TotalRequests int64 `json:"total_requests"`

	// SuccessfulRequests 成功请求数
	SuccessfulRequests int64 `json:"successful_requests"`

	// FailedRequests 失败请求数
	FailedRequests int64 `json:"failed_requests"`

	// TotalTokens 总token数
	TotalTokens int64 `json:"total_tokens"`

	// AverageProcessingTime 平均处理时间（毫秒）
	AverageProcessingTime float64 `json:"average_processing_time"`

	// ModelStats 各模型统计
	ModelStats map[string]ModelStat `json:"model_stats,omitempty"`
}

// ModelStat 模型统计信息
type ModelStat struct {
	// Requests 请求数
	Requests int64 `json:"requests"`

	// Tokens token数
	Tokens int64 `json:"tokens"`

	// AverageProcessingTime 平均处理时间（毫秒）
	AverageProcessingTime float64 `json:"average_processing_time"`
} 