package reranker

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/suoke/suoke_life/services/rag-service/internal/utils"
)

// HuggingFaceClient HuggingFace API客户端
type HuggingFaceClient struct {
	// API令牌
	apiToken string
	
	// API端点
	endpoint string
	
	// HTTP客户端
	httpClient *http.Client
	
	// 日志器
	logger utils.Logger
	
	// 重试次数
	maxRetries int
	
	// 重试间隔基数（毫秒）
	retryBaseIntervalMs int
	
	// 模型名称
	modelName string
}

// RerankerRequest 重排序请求
type RerankerRequest struct {
	// 输入文本对
	Inputs [][]string `json:"inputs"`
	
	// 模型选项
	Options map[string]interface{} `json:"options,omitempty"`
}

// RerankerResponse 重排序响应
type RerankerResponse struct {
	// 相似度分数
	Scores []float64 `json:"scores"`
	
	// 错误信息
	Error string `json:"error,omitempty"`
}

// NewHuggingFaceClient 创建HuggingFace客户端
func NewHuggingFaceClient(modelName, apiToken string, logger utils.Logger) *HuggingFaceClient {
	if logger == nil {
		logger = utils.NewNoopLogger()
	}
	
	return &HuggingFaceClient{
		apiToken:           apiToken,
		endpoint:           fmt.Sprintf("https://api-inference.huggingface.co/models/%s", modelName),
		httpClient:         &http.Client{Timeout: 30 * time.Second},
		logger:             logger,
		maxRetries:         3,
		retryBaseIntervalMs: 500,
		modelName:          modelName,
	}
}

// GetCrossEncoderScores 获取跨编码器分数
func (c *HuggingFaceClient) GetCrossEncoderScores(ctx context.Context, textPairs [][]string) ([]float64, error) {
	request := RerankerRequest{
		Inputs: textPairs,
	}
	
	// 将请求转换为JSON
	requestBody, err := json.Marshal(request)
	if err != nil {
		return nil, fmt.Errorf("序列化请求失败: %w", err)
	}
	
	// 创建HTTP请求
	req, err := http.NewRequestWithContext(ctx, "POST", c.endpoint, bytes.NewBuffer(requestBody))
	if err != nil {
		return nil, fmt.Errorf("创建HTTP请求失败: %w", err)
	}
	
	// 设置请求头
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", c.apiToken))
	
	// 发送请求并获取分数，支持重试
	var response RerankerResponse
	
	// 实现带重试的请求发送
	var lastErr error
	for attempt := 0; attempt <= c.maxRetries; attempt++ {
		if attempt > 0 {
			// 计算重试等待时间（指数退避）
			waitTime := c.retryBaseIntervalMs * (1 << (attempt - 1))
			c.logger.Debug("重试请求", "attempt", attempt, "wait_ms", waitTime)
			time.Sleep(time.Duration(waitTime) * time.Millisecond)
		}
		
		// 发送请求
		resp, err := c.httpClient.Do(req)
		if err != nil {
			lastErr = fmt.Errorf("发送请求失败: %w", err)
			continue
		}
		
		// 延迟关闭响应体
		defer resp.Body.Close()
		
		// 检查响应状态码
		if resp.StatusCode == http.StatusTooManyRequests {
			// 如果遇到限流，等待并重试
			lastErr = fmt.Errorf("API请求过于频繁，状态码: %d", resp.StatusCode)
			continue
		} else if resp.StatusCode != http.StatusOK {
			lastErr = fmt.Errorf("API请求失败，状态码: %d", resp.StatusCode)
			continue
		}
		
		// 解析响应
		if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
			lastErr = fmt.Errorf("解析响应失败: %w", err)
			continue
		}
		
		// 检查响应中是否有错误
		if response.Error != "" {
			lastErr = fmt.Errorf("API返回错误: %s", response.Error)
			continue
		}
		
		// 请求成功，返回分数
		return response.Scores, nil
	}
	
	// 如果所有重试都失败，返回最后一个错误
	return nil, fmt.Errorf("获取重排序分数失败，已重试%d次: %w", c.maxRetries, lastErr)
}

// GetModelInfo 获取模型信息，可用于检查模型是否可用
func (c *HuggingFaceClient) GetModelInfo(ctx context.Context) (map[string]interface{}, error) {
	// 创建HTTP请求
	req, err := http.NewRequestWithContext(ctx, "GET", fmt.Sprintf("https://huggingface.co/api/models/%s", c.modelName), nil)
	if err != nil {
		return nil, fmt.Errorf("创建HTTP请求失败: %w", err)
	}
	
	// 设置请求头
	req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", c.apiToken))
	
	// 发送请求
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("发送请求失败: %w", err)
	}
	defer resp.Body.Close()
	
	// 检查响应状态码
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("获取模型信息失败，状态码: %d", resp.StatusCode)
	}
	
	// 解析响应
	var modelInfo map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&modelInfo); err != nil {
		return nil, fmt.Errorf("解析模型信息失败: %w", err)
	}
	
	return modelInfo, nil
}

// SetTimeout 设置HTTP客户端超时时间
func (c *HuggingFaceClient) SetTimeout(timeout time.Duration) {
	c.httpClient.Timeout = timeout
}

// SetMaxRetries 设置最大重试次数
func (c *HuggingFaceClient) SetMaxRetries(maxRetries int) {
	c.maxRetries = maxRetries
}

// SetRetryBaseInterval 设置重试基础间隔（毫秒）
func (c *HuggingFaceClient) SetRetryBaseInterval(retryBaseIntervalMs int) {
	c.retryBaseIntervalMs = retryBaseIntervalMs
} 