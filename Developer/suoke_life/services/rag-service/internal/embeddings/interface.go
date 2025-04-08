package embeddings

import (
	"context"
	"fmt"
)

// EmbeddingResult 嵌入结果类型
type EmbeddingResult struct {
	Embedding  []float32 // 嵌入向量
	TokenCount int       // 处理的token数量
	Model      string    // 使用的模型名称
}

// TextEmbedder 文本嵌入接口
type TextEmbedder interface {
	// EmbedQuery 为查询文本生成嵌入向量
	EmbedQuery(ctx context.Context, text string) ([]float32, error)

	// EmbedDocument 为单个文档生成嵌入向量
	EmbedDocument(ctx context.Context, text string) (*EmbeddingResult, error)

	// EmbedDocuments 为多个文档生成嵌入向量
	EmbedDocuments(ctx context.Context, texts []string) ([][]float32, error)

	// GetDimensions 获取嵌入向量的维度
	GetDimensions() int

	// GetModelName 获取模型名称
	GetModelName() string

	// CountTokens 计算文本的token数量
	CountTokens(text string) int

	// BatchSize 获取批处理大小
	BatchSize() int

	// Close 关闭嵌入模型
	Close() error
}

// EmbeddingOptions 嵌入选项
type EmbeddingOptions struct {
	// Model 使用的嵌入模型
	Model string

	// Endpoint 嵌入服务端点
	Endpoint string

	// APIKey API密钥
	APIKey string

	// Dimensions 嵌入维度
	Dimensions int

	// BatchSize 批处理大小
	BatchSize int

	// 使用本地模型
	UseLocal bool

	// LocalModelPath 本地模型路径
	LocalModelPath string

	// Threads 线程数
	Threads int

	// UserId 用户ID，用于计量
	UserId string
}

// CostInfo 成本信息
type CostInfo struct {
	// TokenCount 处理的token数量
	TokenCount int

	// Cost 处理成本(美分)
	Cost float64

	// ModelName 模型名称
	ModelName string
}

// CreateEmbedder 创建嵌入模型
func CreateEmbedder(options EmbeddingOptions) (TextEmbedder, error) {
	// 根据选项创建不同的嵌入模型实现
	switch options.Model {
	case "openai":
		return NewOpenAIEmbedder(options)
	case "local":
		return NewLocalEmbedder(options)
	case "mock":
		return NewMockEmbedder(options)
	default:
		// 如果指定的类型不支持，则检查是否为测试
		if options.UseLocal {
			return NewLocalEmbedder(options)
		}
		if options.Model == "test" || options.Model == "" {
			return NewMockEmbedder(options)
		}
		// 默认使用OpenAI
		return nil, fmt.Errorf("不支持的嵌入模型类型: %s", options.Model)
	}
} 