package reranker

import (
	"context"

	"github.com/suoke/suoke_life/services/rag-service/internal/models"
)

// Reranker 重排序器接口
type Reranker interface {
	// Name 返回重排序器名称
	Name() string

	// Rerank 对文档进行重排序
	// query: 用户查询
	// docs: 需要重排序的文档
	// options: 重排序选项
	Rerank(ctx context.Context, query string, docs []models.Document, options RerankerOptions) ([]models.Document, error)

	// Initialize 初始化重排序器
	Initialize(ctx context.Context) error

	// Close 关闭重排序器
	Close() error

	// BatchRerank 批量重排序
	BatchRerank(ctx context.Context, query string, docsBatch [][]models.Document, options RerankerOptions) ([][]models.Document, error)
}

// RerankerOptions 重排序选项
type RerankerOptions struct {
	// TopK 返回前K个结果
	TopK int

	// ScoreThreshold 分数阈值，低于该阈值的文档将被过滤
	ScoreThreshold float64

	// UserID 用户ID，用于日志和分析
	UserID string

	// BatchSize 批处理大小
	BatchSize int

	// MaxInputLength 最大输入长度
	MaxInputLength int

	// Domain 领域，用于特定领域的重排序逻辑
	Domain string

	// TCMSpecific 是否使用中医特定的重排序逻辑
	TCMSpecific bool
	
	// RelevanceField 相关性字段，指定哪个字段用于相关性计算
	RelevanceField string
}

// RerankerFactory 重排序器工厂
type RerankerFactory interface {
	// CreateReranker 创建重排序器
	CreateReranker(name string, config map[string]interface{}) (Reranker, error)
}

// RerankerType 重排序器类型
type RerankerType string

const (
	// RerankerTypeCrossEncoder 跨编码器重排序器
	RerankerTypeCrossEncoder RerankerType = "cross-encoder"
	
	// RerankerTypeFusion 融合重排序器
	RerankerTypeFusion RerankerType = "fusion"
	
	// RerankerTypeRule 规则重排序器
	RerankerTypeRule RerankerType = "rule"
	
	// RerankerTypeLLM 大模型重排序器
	RerankerTypeLLM RerankerType = "llm"
) 