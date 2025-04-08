package mocks

import (
	"context"

	"github.com/stretchr/testify/mock"
)

// MockEmbeddingService 嵌入服务接口的模拟实现
type MockEmbeddingService struct {
	mock.Mock
}

// EmbedTexts 模拟文本嵌入
func (m *MockEmbeddingService) EmbedTexts(ctx context.Context, texts []string) ([][]float32, error) {
	args := m.Called(ctx, texts)

	if vectors := args.Get(0); vectors != nil {
		return vectors.([][]float32), args.Error(1)
	}

	return nil, args.Error(1)
}

// EmbedText 模拟单个文本嵌入
func (m *MockEmbeddingService) EmbedText(ctx context.Context, text string) ([]float32, error) {
	args := m.Called(ctx, text)

	if vector := args.Get(0); vector != nil {
		return vector.([]float32), args.Error(1)
	}

	return nil, args.Error(1)
}

// GetEmbedding 模拟获取文本嵌入
func (m *MockEmbeddingService) GetEmbedding(ctx context.Context, text string) ([]float32, error) {
	args := m.Called(ctx, text)

	if embeddings := args.Get(0); embeddings != nil {
		return embeddings.([]float32), args.Error(1)
	}

	return nil, args.Error(1)
}

// GetBatchEmbeddings 模拟批量获取文本嵌入
func (m *MockEmbeddingService) GetBatchEmbeddings(ctx context.Context, texts []string) ([][]float32, error) {
	args := m.Called(ctx, texts)

	if embeddings := args.Get(0); embeddings != nil {
		return embeddings.([][]float32), args.Error(1)
	}

	return nil, args.Error(1)
}
