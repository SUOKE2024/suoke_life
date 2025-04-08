package llm

import (
	"context"
	"io"
)

// LLMService 大型语言模型服务接口
type LLMService interface {
	// Generate 生成文本响应
	Generate(ctx context.Context, prompt string, options map[string]interface{}) (string, error)
	
	// GenerateStream 流式生成文本响应
	GenerateStream(ctx context.Context, prompt string, writer io.Writer, options map[string]interface{}) error
	
	// GetModelName 获取模型名称
	GetModelName() string
	
	// CountTokens 计算文本的token数量
	CountTokens(text string) int
	
	// Close 关闭资源
	Close() error
}

// LLMOptions LLM配置选项
type LLMOptions struct {
	// ModelName 模型名称
	ModelName string
	
	// Endpoint 端点URL
	Endpoint string
	
	// APIKey API密钥
	APIKey string
	
	// Temperature 温度参数
	Temperature float64
	
	// MaxTokens 最大生成tokens
	MaxTokens int
	
	// TopP Top-P参数
	TopP float64
	
	// PresencePenalty 存在惩罚
	PresencePenalty float64
	
	// FrequencyPenalty 频率惩罚
	FrequencyPenalty float64
	
	// UseLocal 使用本地模型
	UseLocal bool
	
	// LocalModelPath 本地模型路径
	LocalModelPath string
	
	// PromptTemplate 提示模板
	PromptTemplate string
}

// CreateLLMService 创建LLM服务
func CreateLLMService(options LLMOptions) (LLMService, error) {
	// 根据配置创建不同的LLM服务实现
	switch options.ModelName {
	case "openai", "gpt-4", "gpt-4o", "gpt-3.5-turbo":
		return NewOpenAIService(options)
	case "local":
		if options.UseLocal {
			return NewLocalLLMService(options)
		}
	case "mock":
		return NewMockLLMService(options)
	}
	
	// 默认使用OpenAI
	if options.ModelName == "" {
		options.ModelName = "gpt-3.5-turbo"
		return NewOpenAIService(options)
	}
	
	// 测试模式
	if options.ModelName == "test" {
		return NewMockLLMService(options)
	}
	
	// 无法识别的模型类型
	return nil, ErrUnsupportedModel
} 