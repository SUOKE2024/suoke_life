package mocks

import (
	"github.com/stretchr/testify/mock"

	"knowledge-base-service/internal/domain/entity"
)

// MockTextSplitter 文本分割器的模拟实现
type MockTextSplitter struct {
	mock.Mock
}

// SplitText 模拟分割文本
func (m *MockTextSplitter) SplitText(text string, options map[string]interface{}) ([]string, error) {
	args := m.Called(text, options)
	return args.Get(0).([]string), args.Error(1)
}

// Split 模拟分割文本
func (m *MockTextSplitter) Split(text string, metadata map[string]interface{}) ([]entity.Chunk, error) {
	args := m.Called(text, metadata)

	if chunks := args.Get(0); chunks != nil {
		return chunks.([]entity.Chunk), args.Error(1)
	}

	return nil, args.Error(1)
}
