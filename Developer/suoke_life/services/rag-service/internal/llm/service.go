package llm

import (
	"fmt"
	"log"
	"strings"
)

// CreateLLMService 创建LLM服务实例
func CreateLLMService(options LLMOptions) (LLMService, error) {
	// 默认使用OpenAI模型
	modelType := "openai"
	
	// 如果指定了模型名称，解析模型类型
	if options.ModelName != "" {
		modelType = parseModelType(options.ModelName)
	}
	
	log.Printf("创建LLM服务，类型: %s, 模型: %s", modelType, options.ModelName)
	
	// 根据模型类型创建对应的服务
	switch modelType {
	case "openai":
		return NewOpenAIService(options)
	case "local":
		return NewLocalService(options)
	default:
		return nil, fmt.Errorf("%w: %s", ErrUnsupportedModel, modelType)
	}
}

// parseModelType 解析模型类型
func parseModelType(modelName string) string {
	modelName = strings.ToLower(modelName)
	
	// 根据模型名称前缀判断类型
	if strings.HasPrefix(modelName, "gpt") || 
	   strings.Contains(modelName, "openai") || 
	   strings.Contains(modelName, "azure") {
		return "openai"
	}
	
	if strings.HasPrefix(modelName, "local") || 
	   strings.Contains(modelName, "llama") || 
	   strings.Contains(modelName, "gemma") || 
	   strings.Contains(modelName, "mistral") {
		return "local"
	}
	
	// 根据模型全名判断类型
	switch modelName {
	case "local":
		return "local"
	case "openai":
		return "openai"
	default:
		// 默认为OpenAI
		return "openai"
	}
} 