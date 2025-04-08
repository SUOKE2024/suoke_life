package embeddings

import (
	"context"
	"fmt"

	"github.com/suoke/suoke_life/services/rag-service/internal/models"
)

// EmbeddingResult 嵌入结果类型
type EmbeddingResult struct {
	Embedding  []float32 // 嵌入向量
	TokenCount int       // 处理的token数量
	Model      string    // 使用的模型名称
}

// Embedder 基础嵌入器接口
type Embedder interface {
	// EmbedQuery 对查询文本进行嵌入
	EmbedQuery(ctx context.Context, query string) ([]float32, error)
	
	// EmbedDocuments 对多个文档进行嵌入
	EmbedDocuments(ctx context.Context, documents []string) ([][]float32, error)
	
	// Dimensions 返回嵌入向量维度
	Dimensions() int
	
	// Name 返回嵌入器名称
	Name() string
	
	// Initialize 初始化嵌入器
	Initialize(ctx context.Context) error
	
	// Close 关闭嵌入器
	Close() error
}

// ImageEmbedder 图像嵌入器接口
type ImageEmbedder interface {
	// EmbedImages 对图像进行嵌入
	EmbedImages(ctx context.Context, imagePaths []string) ([][]float32, error)
	
	// Dimensions 返回嵌入向量维度
	Dimensions() int
	
	// Name 返回嵌入器名称
	Name() string
	
	// Initialize 初始化嵌入器
	Initialize(ctx context.Context) error
	
	// Close 关闭嵌入器
	Close() error
}

// TCMImageEmbedder 中医图像嵌入器接口
type TCMImageEmbedder interface {
	// 继承基础图像嵌入器接口
	ImageEmbedder
	
	// EnhanceTCMImageMetadata 增强中医图像元数据
	EnhanceTCMImageMetadata(ctx context.Context, metadata *models.DocumentMetadata, imagePath string)
}

// AudioEmbedder 音频嵌入器接口
type AudioEmbedder interface {
	// EmbedAudio 对音频文件进行嵌入
	EmbedAudio(ctx context.Context, audioPaths []string) ([][]float32, error)
	
	// Dimensions 返回嵌入向量维度
	Dimensions() int
	
	// Name 返回嵌入器名称
	Name() string
	
	// Initialize 初始化嵌入器
	Initialize(ctx context.Context) error
	
	// Close 关闭嵌入器
	Close() error
}

// TCMAudioEmbedder 中医音频嵌入器接口
type TCMAudioEmbedder interface {
	// 继承基础音频嵌入器接口
	AudioEmbedder
	
	// EnhanceTCMAudioMetadata 增强中医音频元数据
	EnhanceTCMAudioMetadata(ctx context.Context, metadata *models.DocumentMetadata, audioPath string)
}

// MultiModalEmbedder 多模态嵌入器接口
type MultiModalEmbedder interface {
	// EmbedText 对文本进行嵌入
	EmbedText(ctx context.Context, text string) ([]float32, error)
	
	// EmbedImage 对图像进行嵌入
	EmbedImage(ctx context.Context, imagePath string) ([]float32, error)
	
	// EmbedAudio 对音频进行嵌入
	EmbedAudio(ctx context.Context, audioPath string) ([]float32, error)
	
	// EmbedMultimodal 对多模态内容进行嵌入
	EmbedMultimodal(ctx context.Context, content *MultiModalContent) ([]float32, error)
	
	// Dimensions 返回嵌入向量维度
	Dimensions() int
	
	// Name 返回嵌入器名称
	Name() string
	
	// Initialize 初始化嵌入器
	Initialize(ctx context.Context) error
	
	// Close 关闭嵌入器
	Close() error
}

// MultiModalContent 多模态内容
type MultiModalContent struct {
	// 文本内容
	Text string
	
	// 图像路径
	ImagePaths []string
	
	// 音频路径
	AudioPaths []string
	
	// 权重
	Weights map[string]float32
}

// EmbeddingOptions 嵌入选项
type EmbeddingOptions struct {
	// 最大输入长度
	MaxInputLength int
	
	// 是否使用缓存
	UseCache bool
	
	// 用户ID，用于个性化
	UserID string
	
	// 额外选项
	ExtraOptions map[string]interface{}
}

// CostInfo 成本信息
type CostInfo struct {
	// TokenCount 处理的token数量
	TokenCount int

	// Cost 处理成本(美分)
	Cost float64

	// ModelName 模型名称
	ModelName string
}

// CreateEmbedder 创建嵌入模型
func CreateEmbedder(options EmbeddingOptions) (TextEmbedder, error) {
	// 根据选项创建不同的嵌入模型实现
	switch options.Model {
	case "openai":
		return NewOpenAIEmbedder(options)
	case "local":
		return NewLocalEmbedder(options)
	case "mock":
		return NewMockEmbedder(options)
	default:
		// 如果指定的类型不支持，则检查是否为测试
		if options.UseLocal {
			return NewLocalEmbedder(options)
		}
		if options.Model == "test" || options.Model == "" {
			return NewMockEmbedder(options)
		}
		// 默认使用OpenAI
		return nil, fmt.Errorf("不支持的嵌入模型类型: %s", options.Model)
	}
} 