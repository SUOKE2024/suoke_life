package ai

import (
	"context"
)

// EmbeddingService 文本嵌入服务接口
// 负责生成文本的向量表示
type EmbeddingService interface {
	// GetEmbedding 为文本生成嵌入向量
	// ctx: 上下文
	// text: 需要嵌入的文本
	// 返回嵌入向量（浮点数数组）和可能的错误
	GetEmbedding(ctx context.Context, text string) ([]float32, error)
	
	// GetBatchEmbeddings 批量生成嵌入向量
	// ctx: 上下文
	// texts: 需要嵌入的文本列表
	// 返回嵌入向量列表和可能的错误
	GetBatchEmbeddings(ctx context.Context, texts []string) ([][]float32, error)
} 