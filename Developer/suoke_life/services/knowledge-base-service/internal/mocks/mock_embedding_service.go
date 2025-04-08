package mocks

import (
	"context"

	"github.com/stretchr/testify/mock"
)

// MockEmbeddingService 模拟嵌入服务
type MockEmbeddingService struct {
	mock.Mock
}

// GetEmbedding 获取文本嵌入向量
func (m *MockEmbeddingService) GetEmbedding(ctx context.Context, text string) ([]float32, error) {
	args := m.Called(ctx, text)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).([]float32), args.Error(1)
}

// GetBatchEmbeddings 批量获取文本嵌入向量
func (m *MockEmbeddingService) GetBatchEmbeddings(ctx context.Context, texts []string) ([][]float32, error) {
	args := m.Called(ctx, texts)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).([][]float32), args.Error(1)
}
