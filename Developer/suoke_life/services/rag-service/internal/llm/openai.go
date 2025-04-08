package llm

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"

	"github.com/pkoukk/tiktoken-go"
	"github.com/tiktoken-go/tokenizer"
)

// OpenAIService 实现基于OpenAI API的LLM服务
type OpenAIService struct {
	client        *http.Client
	endpoint      string
	apiKey        string
	modelName     string
	temperature   float64
	maxTokens     int
	topP          float64
	presencePenalty  float64
	frequencyPenalty float64
	tokenizer     *tiktoken.Tiktoken
}

// NewOpenAIService 创建新的OpenAI服务
func NewOpenAIService(options LLMOptions) (*OpenAIService, error) {
	// 校验API密钥
	if options.APIKey == "" {
		return nil, ErrAPIKeyMissing
	}

	// 设置默认端点
	endpoint := "https://api.openai.com/v1/chat/completions"
	if options.Endpoint != "" {
		endpoint = options.Endpoint
	}

	// 设置默认模型
	modelName := "gpt-3.5-turbo"
	if options.ModelName != "" && options.ModelName != "openai" {
		modelName = options.ModelName
	}

	// 创建HTTP客户端
	client := &http.Client{
		Timeout: 60 * time.Second,
	}

	// 创建tokenizer
	tk, err := tokenizer.ForModel(modelName)
	if err != nil {
		// 如果特定模型的分词器不可用，使用默认分词器
		tk, err = tokenizer.ForModel("gpt-3.5-turbo")
		if err != nil {
			return nil, fmt.Errorf("初始化tokenizer失败: %w", err)
		}
	}

	// 设置默认参数
	temperature := 0.7
	if options.Temperature > 0 {
		temperature = options.Temperature
	}

	maxTokens := 2048
	if options.MaxTokens > 0 {
		maxTokens = options.MaxTokens
	}

	topP := 1.0
	if options.TopP > 0 {
		topP = options.TopP
	}

	presencePenalty := 0.0
	if options.PresencePenalty != 0 {
		presencePenalty = options.PresencePenalty
	}

	frequencyPenalty := 0.0
	if options.FrequencyPenalty != 0 {
		frequencyPenalty = options.FrequencyPenalty
	}

	service := &OpenAIService{
		client:        client,
		endpoint:      endpoint,
		apiKey:        options.APIKey,
		modelName:     modelName,
		temperature:   temperature,
		maxTokens:     maxTokens,
		topP:          topP,
		presencePenalty: presencePenalty,
		frequencyPenalty: frequencyPenalty,
		tokenizer:     tk,
	}

	return service, nil
}

// Generate 生成文本响应
func (s *OpenAIService) Generate(ctx context.Context, prompt string, options map[string]interface{}) (string, error) {
	// 准备请求体
	requestBody := map[string]interface{}{
		"model":       s.modelName,
		"messages": []map[string]interface{}{
			{
				"role":    "system",
				"content": "您是一个专业的AI助手，擅长根据提供的信息回答问题。请基于给定的上下文信息回答问题，如果无法从上下文中找到答案，请明确说明。",
			},
			{
				"role":    "user",
				"content": prompt,
			},
		},
		"temperature":      s.temperature,
		"max_tokens":       s.maxTokens,
		"top_p":            s.topP,
		"presence_penalty": s.presencePenalty,
		"frequency_penalty": s.frequencyPenalty,
	}

	// 应用自定义选项
	if options != nil {
		if system, ok := options["system"].(string); ok && system != "" {
			requestBody["messages"].([]map[string]interface{})[0]["content"] = system
		}
		if temp, ok := options["temperature"].(float64); ok {
			requestBody["temperature"] = temp
		}
		if maxTok, ok := options["max_tokens"].(int); ok {
			requestBody["max_tokens"] = maxTok
		}
	}

	// 序列化请求体
	jsonData, err := json.Marshal(requestBody)
	if err != nil {
		return "", fmt.Errorf("序列化请求失败: %w", err)
	}

	// 创建HTTP请求
	req, err := http.NewRequestWithContext(ctx, "POST", s.endpoint, strings.NewReader(string(jsonData)))
	if err != nil {
		return "", fmt.Errorf("创建HTTP请求失败: %w", err)
	}

	// 设置请求头
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+s.apiKey)

	// 发送请求
	resp, err := s.client.Do(req)
	if err != nil {
		return "", fmt.Errorf("发送请求失败: %w", err)
	}
	defer resp.Body.Close()

	// 读取响应
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("读取响应失败: %w", err)
	}

	// 检查HTTP状态码
	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("API请求失败，状态码: %d, 响应: %s", resp.StatusCode, string(body))
	}

	// 解析响应
	var response struct {
		Choices []struct {
			Message struct {
				Content string `json:"content"`
			} `json:"message"`
		} `json:"choices"`
	}

	if err := json.Unmarshal(body, &response); err != nil {
		return "", fmt.Errorf("解析响应失败: %w", err)
	}

	// 检查是否有响应内容
	if len(response.Choices) == 0 {
		return "", fmt.Errorf("API返回了空响应")
	}

	return response.Choices[0].Message.Content, nil
}

// GenerateStream 流式生成文本响应
func (s *OpenAIService) GenerateStream(ctx context.Context, prompt string, writer io.Writer, options map[string]interface{}) error {
	// 准备请求体
	requestBody := map[string]interface{}{
		"model":       s.modelName,
		"messages": []map[string]interface{}{
			{
				"role":    "system",
				"content": "您是一个专业的AI助手，擅长根据提供的信息回答问题。请基于给定的上下文信息回答问题，如果无法从上下文中找到答案，请明确说明。",
			},
			{
				"role":    "user",
				"content": prompt,
			},
		},
		"temperature":      s.temperature,
		"max_tokens":       s.maxTokens,
		"top_p":            s.topP,
		"presence_penalty": s.presencePenalty,
		"frequency_penalty": s.frequencyPenalty,
		"stream":           true,
	}

	// 应用自定义选项
	if options != nil {
		if system, ok := options["system"].(string); ok && system != "" {
			requestBody["messages"].([]map[string]interface{})[0]["content"] = system
		}
		if temp, ok := options["temperature"].(float64); ok {
			requestBody["temperature"] = temp
		}
		if maxTok, ok := options["max_tokens"].(int); ok {
			requestBody["max_tokens"] = maxTok
		}
	}

	// 序列化请求体
	jsonData, err := json.Marshal(requestBody)
	if err != nil {
		return fmt.Errorf("序列化请求失败: %w", err)
	}

	// 创建HTTP请求
	req, err := http.NewRequestWithContext(ctx, "POST", s.endpoint, strings.NewReader(string(jsonData)))
	if err != nil {
		return fmt.Errorf("创建HTTP请求失败: %w", err)
	}

	// 设置请求头
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+s.apiKey)
	req.Header.Set("Accept", "text/event-stream")

	// 发送请求
	resp, err := s.client.Do(req)
	if err != nil {
		return fmt.Errorf("发送请求失败: %w", err)
	}
	defer resp.Body.Close()

	// 检查HTTP状态码
	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("API请求失败，状态码: %d, 响应: %s", resp.StatusCode, string(body))
	}

	// 处理SSE流
	reader := bufio.NewReader(resp.Body)
	for {
		// 检查上下文是否被取消
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
		}

		// 读取行
		line, err := reader.ReadString('\n')
		if err != nil {
			if err == io.EOF {
				break
			}
			return fmt.Errorf("读取流数据失败: %w", err)
		}

		// 去除前导空格和尾部换行符
		line = strings.TrimSpace(line)

		// 跳过空行和注释
		if line == "" || strings.HasPrefix(line, ":") {
			continue
		}

		// 检查流结束
		if line == "data: [DONE]" {
			break
		}

		// 解析数据
		if strings.HasPrefix(line, "data: ") {
			data := line[6:] // 去除 "data: " 前缀
			var streamResponse struct {
				Choices []struct {
					Delta struct {
						Content string `json:"content"`
					} `json:"delta"`
				} `json:"choices"`
			}

			if err := json.Unmarshal([]byte(data), &streamResponse); err != nil {
				continue // 跳过无法解析的数据
			}

			// 提取内容并写入
			if len(streamResponse.Choices) > 0 {
				content := streamResponse.Choices[0].Delta.Content
				if content != "" {
					_, err = writer.Write([]byte(content))
					if err != nil {
						return fmt.Errorf("写入流数据失败: %w", err)
					}
				}
			}
		}
	}

	return nil
}

// GetModelName 获取模型名称
func (s *OpenAIService) GetModelName() string {
	return s.modelName
}

// CountTokens 计算文本的token数量
func (s *OpenAIService) CountTokens(text string) int {
	if s.tokenizer == nil {
		return 0
	}
	return len(s.tokenizer.Encode(text, nil, nil))
}

// Close 关闭资源
func (s *OpenAIService) Close() error {
	// 无需特殊清理
	return nil
} 