package embeddings

import (
	"context"
	"math/rand"
	"time"
)

// LocalEmbedder 本地嵌入模型
type LocalEmbedder struct {
	dimensions int
	modelName  string
	batchSize  int
	threads    int
	path       string
}

// NewLocalEmbedder 创建一个新的本地嵌入模型
func NewLocalEmbedder(options EmbeddingOptions) (TextEmbedder, error) {
	dimensions := options.Dimensions
	if dimensions <= 0 {
		dimensions = 384 // 默认维度
	}

	batchSize := options.BatchSize
	if batchSize <= 0 {
		batchSize = 8 // 默认批处理大小
	}

	threads := options.Threads
	if threads <= 0 {
		threads = 4 // 默认线程数
	}

	path := options.LocalModelPath
	if path == "" {
		path = "./models/all-MiniLM-L6-v2"
	}

	return &LocalEmbedder{
		dimensions: dimensions,
		modelName:  "local-embedder",
		batchSize:  batchSize,
		threads:    threads,
		path:       path,
	}, nil
}

// EmbedQuery 嵌入单个查询文本
func (m *LocalEmbedder) EmbedQuery(ctx context.Context, text string) ([]float32, error) {
	// 实际实现中，这里应该调用本地模型进行嵌入
	// 在模拟实现中，我们使用随机向量
	return m.generateRandomVector(), nil
}

// EmbedDocument 嵌入单个文档文本
func (m *LocalEmbedder) EmbedDocument(ctx context.Context, text string) (*EmbeddingResult, error) {
	// 实际实现中，这里应该调用本地模型进行嵌入
	// 在模拟实现中，我们使用随机向量
	
	// 简单的token计数
	tokenCount := m.CountTokens(text)
	
	return &EmbeddingResult{
		Embedding:  m.generateRandomVector(),
		TokenCount: tokenCount,
		Model:      m.modelName,
	}, nil
}

// EmbedDocuments 嵌入多个文档文本
func (m *LocalEmbedder) EmbedDocuments(ctx context.Context, texts []string) ([][]float32, error) {
	vectors := make([][]float32, len(texts))

	// 实际实现中，这里应该调用本地模型进行嵌入
	// 在模拟实现中，我们使用随机向量
	for i := range texts {
		vectors[i] = m.generateRandomVector()
	}

	return vectors, nil
}

// GetDimensions 获取嵌入向量的维度
func (m *LocalEmbedder) GetDimensions() int {
	return m.dimensions
}

// GetModelName 获取模型名称
func (m *LocalEmbedder) GetModelName() string {
	return m.modelName
}

// CountTokens 计算文本的token数量
func (m *LocalEmbedder) CountTokens(text string) int {
	// 简单的模拟计算，实际应使用分词器
	return len(text) / 4
}

// BatchSize 获取批处理大小
func (m *LocalEmbedder) BatchSize() int {
	return m.batchSize
}

// Close 关闭嵌入模型
func (m *LocalEmbedder) Close() error {
	// 释放模型资源
	return nil
}

// 生成随机向量（仅测试用）
func (m *LocalEmbedder) generateRandomVector() []float32 {
	r := rand.New(rand.NewSource(time.Now().UnixNano()))
	vector := make([]float32, m.dimensions)

	for i := 0; i < m.dimensions; i++ {
		vector[i] = (r.Float32() * 2) - 1 // 生成-1到1之间的随机数
	}

	// 归一化向量
	var sum float32
	for _, v := range vector {
		sum += v * v
	}

	norm := float32(1.0) / float32(len(vector))
	for i := range vector {
		vector[i] *= norm
	}

	return vector
} 