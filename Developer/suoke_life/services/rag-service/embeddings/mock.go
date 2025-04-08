package embeddings

import (
	"context"
	"math/rand"
	"time"
)

// CostTracker 成本跟踪结构体
type CostTracker struct {
	QueryTokens    int     `json:"query_tokens"`
	DocumentTokens int     `json:"document_tokens"`
	TotalTokens    int     `json:"total_tokens"`
	TotalCost      float64 `json:"total_cost"`
}

// MockEmbedder 模拟嵌入模型，用于测试
type MockEmbedder struct {
	dimensions int
	modelName  string
	batchSize  int
	costs      *CostTracker
}

// NewMockEmbedder 创建一个新的模拟嵌入模型
func NewMockEmbedder(options EmbeddingOptions) (TextEmbedder, error) {
	dimensions := options.Dimensions
	if dimensions <= 0 {
		dimensions = 384 // 默认维度
	}
	
	return &MockEmbedder{
		dimensions: dimensions,
		modelName:  "mock-embedder",
		batchSize:  10,
		costs: &CostTracker{
			QueryTokens:    0,
			DocumentTokens: 0,
			TotalTokens:    0,
			TotalCost:      0,
		},
	}, nil
}

// EmbedQuery 嵌入单个查询文本
func (m *MockEmbedder) EmbedQuery(ctx context.Context, text string) ([]float32, error) {
	// 模拟文本长度作为token数量
	tokenCount := len(text) / 4
	if tokenCount < 1 {
		tokenCount = 1
	}
	
	m.costs.QueryTokens += tokenCount
	m.costs.TotalTokens += tokenCount
	
	// 生成随机向量
	vec := m.generateRandomVector()
	return vec, nil
}

// EmbedDocument 嵌入单个文档文本
func (m *MockEmbedder) EmbedDocument(ctx context.Context, text string) (*EmbeddingResult, error) {
	// 模拟文本长度作为token数量
	tokenCount := len(text) / 4
	if tokenCount < 1 {
		tokenCount = 1
	}
	
	m.costs.DocumentTokens += tokenCount
	m.costs.TotalTokens += tokenCount
	
	// 生成随机向量
	vec := m.generateRandomVector()
	
	return &EmbeddingResult{
		Embedding:  vec,
		TokenCount: tokenCount,
		Model:      m.modelName,
	}, nil
}

// EmbedDocuments 嵌入多个文档文本
func (m *MockEmbedder) EmbedDocuments(ctx context.Context, texts []string) ([][]float32, error) {
	vectors := make([][]float32, len(texts))
	
	for i, text := range texts {
		// 模拟文本长度作为token数量
		tokenCount := len(text) / 4
		if tokenCount < 1 {
			tokenCount = 1
		}
		
		m.costs.DocumentTokens += tokenCount
		m.costs.TotalTokens += tokenCount
		
		// 生成随机向量
		vectors[i] = m.generateRandomVector()
	}
	
	return vectors, nil
}

// GetDimensions 获取嵌入向量的维度
func (m *MockEmbedder) GetDimensions() int {
	return m.dimensions
}

// GetModelName 获取模型名称
func (m *MockEmbedder) GetModelName() string {
	return m.modelName
}

// CountTokens 计算文本的token数量
func (m *MockEmbedder) CountTokens(text string) int {
	// 简单的模拟计算，实际应使用分词器
	return len(text) / 4
}

// BatchSize 获取批处理大小
func (m *MockEmbedder) BatchSize() int {
	return m.batchSize
}

// Close 关闭嵌入模型
func (m *MockEmbedder) Close() error {
	return nil
}

// 生成随机向量
func (m *MockEmbedder) generateRandomVector() []float32 {
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