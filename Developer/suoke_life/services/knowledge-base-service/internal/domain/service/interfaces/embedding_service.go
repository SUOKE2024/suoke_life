package interfaces

import (
	"context"
)

// EmbeddingService 嵌入服务接口
type EmbeddingService interface {
	// GetEmbedding 获取单个文本的嵌入向量
	GetEmbedding(ctx context.Context, text string) ([]float32, error)
	
	// GetBatchEmbeddings 批量获取多个文本的嵌入向量
	GetBatchEmbeddings(ctx context.Context, texts []string) ([][]float32, error)
} 