package mocks

import (
	"context"
	"github.com/stretchr/testify/mock"
)

// MockEmbeddingService 是 EmbeddingService 接口的模拟实现
type MockEmbeddingService struct {
	mock.Mock
}

// GetEmbedding 模拟获取单个文本的嵌入向量
func (m *MockEmbeddingService) GetEmbedding(ctx context.Context, text string) ([]float32, error) {
	args := m.Called(ctx, text)

	// 如果返回值是 nil，则直接返回 nil
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}

	// 否则转换为预期的类型
	return args.Get(0).([]float32), args.Error(1)
}

// GetBatchEmbeddings 模拟批量获取多个文本的嵌入向量
func (m *MockEmbeddingService) GetBatchEmbeddings(ctx context.Context, texts []string) ([][]float32, error) {
	args := m.Called(ctx, texts)

	// 如果返回值是 nil，则直接返回 nil
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}

	// 否则转换为预期的类型
	return args.Get(0).([][]float32), args.Error(1)
}
