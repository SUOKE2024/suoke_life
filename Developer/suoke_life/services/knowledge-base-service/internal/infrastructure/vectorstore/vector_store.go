package vectorstore

import (
	"context"
)

// VectorStore 向量存储接口
// 定义了向量存储所需的核心功能
type VectorStore interface {
	// StoreVector 存储向量
	// docID: 文档ID，用于关联存储的向量
	// vector: 向量数据，通常是由嵌入模型生成的浮点数数组
	// 返回: 向量ID和可能的错误
	StoreVector(ctx context.Context, docID string, vector []float32) (string, error)

	// SearchVector 搜索向量
	// vector: 查询向量
	// limit: 限制返回结果数量
	// 返回: 匹配的文档ID列表，相似度分数，和可能的错误
	SearchVector(ctx context.Context, vector []float32, limit int) ([]string, []float32, error)

	// DeleteVector 删除向量
	// vectorID: 要删除的向量ID
	// 返回: 可能的错误
	DeleteVector(ctx context.Context, vectorID string) error

	// Close 关闭向量存储连接
	// 返回: 可能的错误
	Close() error

	// Ping 检查向量存储是否可用
	// 返回: 可能的错误
	Ping(ctx context.Context) error
}
