package mocks

import (
	"github.com/stretchr/testify/mock"

	"knowledge-base-service/internal/domain/entity"
)

// MockTextSplitter 是 TextSplitter 接口的模拟实现
type MockTextSplitter struct {
	mock.Mock
}

// Split 模拟文本分割功能
func (m *MockTextSplitter) Split(text string, metadata map[string]interface{}) ([]entity.Chunk, error) {
	args := m.Called(text, metadata)

	// 如果返回值是 nil，则直接返回 nil
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}

	// 否则转换为预期的类型
	return args.Get(0).([]entity.Chunk), args.Error(1)
}
