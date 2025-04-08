package mocks

import (
	"context"

	"github.com/stretchr/testify/mock"

	"knowledge-base-service/internal/domain/entity"
)

// MockBlockchainClient 模拟区块链客户端
type MockBlockchainClient struct {
	mock.Mock
}

// RegisterDocument 模拟注册文档到区块链
func (m *MockBlockchainClient) RegisterDocument(ctx context.Context, doc *entity.Document) (string, error) {
	args := m.Called(ctx, doc)
	return args.String(0), args.Error(1)
}

// VerifyDocument 模拟验证文档在区块链上的存在
func (m *MockBlockchainClient) VerifyDocument(ctx context.Context, doc *entity.Document) (bool, error) {
	args := m.Called(ctx, doc)
	return args.Bool(0), args.Error(1)
}
