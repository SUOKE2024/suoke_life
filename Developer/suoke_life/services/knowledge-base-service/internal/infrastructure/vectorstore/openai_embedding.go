package vectorstore

import (
	"context"
	"fmt"
	"math/rand"

	"knowledge-base-service/internal/interfaces/ai"
)

// OpenAIEmbeddingService 是一个OpenAI嵌入服务的简化实现
// 这是为了测试目的，实际上应该调用OpenAI API
type OpenAIEmbeddingService struct {
	apiKey      string
	dimension   int
	mockVectors bool // 是否使用模拟的向量
}

// 确保实现了EmbeddingService接口
var _ ai.EmbeddingService = (*OpenAIEmbeddingService)(nil)

// NewOpenAIEmbeddingService 创建新的OpenAI嵌入服务
func NewOpenAIEmbeddingService(apiKey string) *OpenAIEmbeddingService {
	useMock := apiKey == ""

	return &OpenAIEmbeddingService{
		apiKey:      apiKey,
		dimension:   1536, // OpenAI嵌入模型的默认维度
		mockVectors: useMock,
	}
}

// GetEmbedding 获取单个文本的嵌入向量
func (s *OpenAIEmbeddingService) GetEmbedding(ctx context.Context, text string) ([]float32, error) {
	if s.mockVectors || s.apiKey == "" {
		return s.generateMockVector(), nil
	}

	// 实际实现应该调用OpenAI API
	// 这里简化为返回一个随机向量
	return s.generateMockVector(), nil
}

// GetBatchEmbeddings 批量获取文本的嵌入向量
func (s *OpenAIEmbeddingService) GetBatchEmbeddings(ctx context.Context, texts []string) ([][]float32, error) {
	if len(texts) == 0 {
		return nil, fmt.Errorf("文本列表不能为空")
	}

	vectors := make([][]float32, len(texts))

	// 如果是模拟模式或没有API密钥，生成模拟向量
	if s.mockVectors || s.apiKey == "" {
		for i := range texts {
			vectors[i] = s.generateMockVector()
		}
		return vectors, nil
	}

	// 实际实现应该批量调用OpenAI API
	// 这里简化为返回随机向量
	for i := range texts {
		vectors[i] = s.generateMockVector()
	}

	return vectors, nil
}

// 生成模拟向量，用于测试
func (s *OpenAIEmbeddingService) generateMockVector() []float32 {
	vector := make([]float32, s.dimension)
	for i := 0; i < s.dimension; i++ {
		vector[i] = rand.Float32()*2 - 1 // 生成-1到1之间的随机值
	}
	return normalizeVector(vector)
}

// 归一化向量，使其长度为1
func normalizeVector(vector []float32) []float32 {
	// 计算平方和
	var sumSquares float32
	for _, v := range vector {
		sumSquares += v * v
	}

	// 如果向量为零向量，返回原向量
	if sumSquares == 0 {
		return vector
	}

	// 计算向量长度
	length := float32(sumSquares)

	// 归一化
	for i, v := range vector {
		vector[i] = v / length
	}

	return vector
}
