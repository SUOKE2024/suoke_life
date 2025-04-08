package embeddings

import (
	"context"
	"fmt"
	"math/rand"
	"time"
)

// OpenAIEmbedder OpenAI嵌入模型
type OpenAIEmbedder struct {
	dimensions int
	modelName  string
	batchSize  int
	apiKey     string
	endpoint   string
}

// NewOpenAIEmbedder 创建一个新的OpenAI嵌入模型
func NewOpenAIEmbedder(options EmbeddingOptions) (TextEmbedder, error) {
	if options.APIKey == "" {
		return nil, fmt.Errorf("OpenAI API密钥不能为空")
	}

	dimensions := options.Dimensions
	if dimensions <= 0 {
		dimensions = 1536 // 默认维度
	}

	modelName := "text-embedding-3-small"
	if options.Model == "openai-large" {
		modelName = "text-embedding-3-large"
		dimensions = 3072
	} else if options.Model == "openai-ada" {
		modelName = "text-embedding-ada-002"
		dimensions = 1536
	}

	batchSize := options.BatchSize
	if batchSize <= 0 {
		batchSize = 16 // 默认批处理大小
	}

	endpoint := options.Endpoint
	if endpoint == "" {
		endpoint = "https://api.openai.com/v1/embeddings"
	}

	return &OpenAIEmbedder{
		dimensions: dimensions,
		modelName:  modelName,
		batchSize:  batchSize,
		apiKey:     options.APIKey,
		endpoint:   endpoint,
	}, nil
}

// EmbedQuery 嵌入单个查询文本
func (m *OpenAIEmbedder) EmbedQuery(ctx context.Context, text string) ([]float32, error) {
	// 实际实现中，这里应该调用OpenAI API进行嵌入
	// 在模拟实现中，我们使用随机向量
	return m.generateRandomVector(), nil
}

// EmbedDocument 嵌入单个文档文本
func (m *OpenAIEmbedder) EmbedDocument(ctx context.Context, text string) (*EmbeddingResult, error) {
	// 实际实现中，这里应该调用OpenAI API进行嵌入
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
func (m *OpenAIEmbedder) EmbedDocuments(ctx context.Context, texts []string) ([][]float32, error) {
	vectors := make([][]float32, len(texts))

	// 实际实现中，这里应该调用OpenAI API进行嵌入
	// 在模拟实现中，我们使用随机向量
	for i := range texts {
		vectors[i] = m.generateRandomVector()
	}

	return vectors, nil
}

// GetDimensions 获取嵌入向量的维度
func (m *OpenAIEmbedder) GetDimensions() int {
	return m.dimensions
}

// GetModelName 获取模型名称
func (m *OpenAIEmbedder) GetModelName() string {
	return m.modelName
}

// CountTokens 计算文本的token数量
func (m *OpenAIEmbedder) CountTokens(text string) int {
	// 简单的模拟计算，实际应使用tiktoken
	return len(text) / 4
}

// BatchSize 获取批处理大小
func (m *OpenAIEmbedder) BatchSize() int {
	return m.batchSize
}

// Close 关闭嵌入模型
func (m *OpenAIEmbedder) Close() error {
	// 无需释放资源
	return nil
}

// 生成随机向量（仅测试用）
func (m *OpenAIEmbedder) generateRandomVector() []float32 {
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