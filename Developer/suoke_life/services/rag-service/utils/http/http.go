package http

import (
	"bytes"
	"context"
	"encoding/json"
	"io"
	"net/http"
	"time"

	"github.com/suoke/suoke_life/services/rag-service/internal/utils/logger"
)

const (
	// 默认超时时间
	defaultTimeout = 30 * time.Second
	// 默认重试次数
	defaultRetries = 3
	// 默认重试间隔
	defaultRetryInterval = 1 * time.Second
)

// Client 自定义HTTP客户端
type Client struct {
	client        *http.Client
	retries       int
	retryInterval time.Duration
	headers       map[string]string
}

// NewClient 创建新的HTTP客户端
func NewClient(timeout time.Duration, retries int, retryInterval time.Duration) *Client {
	if timeout <= 0 {
		timeout = defaultTimeout
	}
	if retries <= 0 {
		retries = defaultRetries
	}
	if retryInterval <= 0 {
		retryInterval = defaultRetryInterval
	}

	return &Client{
		client: &http.Client{
			Timeout: timeout,
		},
		retries:       retries,
		retryInterval: retryInterval,
		headers:       make(map[string]string),
	}
}

// SetHeader 设置HTTP请求头
func (c *Client) SetHeader(key, value string) *Client {
	c.headers[key] = value
	return c
}

// SetHeaders 批量设置HTTP请求头
func (c *Client) SetHeaders(headers map[string]string) *Client {
	for k, v := range headers {
		c.headers[k] = v
	}
	return c
}

// Get 发送GET请求
func (c *Client) Get(ctx context.Context, url string) (*http.Response, error) {
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		return nil, err
	}

	// 添加请求头
	for k, v := range c.headers {
		req.Header.Set(k, v)
	}

	return c.do(req)
}

// Post 发送POST请求
func (c *Client) Post(ctx context.Context, url string, body interface{}) (*http.Response, error) {
	var bodyReader io.Reader

	if body != nil {
		jsonBody, err := json.Marshal(body)
		if err != nil {
			return nil, err
		}
		bodyReader = bytes.NewBuffer(jsonBody)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", url, bodyReader)
	if err != nil {
		return nil, err
	}

	// 添加请求头
	for k, v := range c.headers {
		req.Header.Set(k, v)
	}

	// 设置JSON内容类型
	if body != nil && req.Header.Get("Content-Type") == "" {
		req.Header.Set("Content-Type", "application/json")
	}

	return c.do(req)
}

// PostForm 发送表单POST请求
func (c *Client) PostForm(ctx context.Context, url string, formData map[string]string) (*http.Response, error) {
	req, err := http.NewRequestWithContext(ctx, "POST", url, nil)
	if err != nil {
		return nil, err
	}

	// 设置表单内容类型
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")

	// 添加请求头
	for k, v := range c.headers {
		req.Header.Set(k, v)
	}

	// 编码表单数据
	if formData != nil {
		values := req.URL.Query()
		for k, v := range formData {
			values.Add(k, v)
		}
		req.URL.RawQuery = values.Encode()
	}

	return c.do(req)
}

// Put 发送PUT请求
func (c *Client) Put(ctx context.Context, url string, body interface{}) (*http.Response, error) {
	var bodyReader io.Reader

	if body != nil {
		jsonBody, err := json.Marshal(body)
		if err != nil {
			return nil, err
		}
		bodyReader = bytes.NewBuffer(jsonBody)
	}

	req, err := http.NewRequestWithContext(ctx, "PUT", url, bodyReader)
	if err != nil {
		return nil, err
	}

	// 添加请求头
	for k, v := range c.headers {
		req.Header.Set(k, v)
	}

	// 设置JSON内容类型
	if body != nil && req.Header.Get("Content-Type") == "" {
		req.Header.Set("Content-Type", "application/json")
	}

	return c.do(req)
}

// Delete 发送DELETE请求
func (c *Client) Delete(ctx context.Context, url string) (*http.Response, error) {
	req, err := http.NewRequestWithContext(ctx, "DELETE", url, nil)
	if err != nil {
		return nil, err
	}

	// 添加请求头
	for k, v := range c.headers {
		req.Header.Set(k, v)
	}

	return c.do(req)
}

// do 实际执行HTTP请求，支持重试
func (c *Client) do(req *http.Request) (*http.Response, error) {
	var resp *http.Response
	var err error

	for attempt := 0; attempt <= c.retries; attempt++ {
		if attempt > 0 {
			// 如果不是第一次尝试，等待一段时间
			time.Sleep(c.retryInterval)
			
			// 请求重试日志
			logger.Infof("重试请求 [%d/%d]: %s %s", attempt, c.retries, req.Method, req.URL.String())
		}

		resp, err = c.client.Do(req)
		if err == nil {
			// 请求成功，检查状态码
			if resp.StatusCode < 500 {
				// 非服务器错误，不需要重试
				return resp, nil
			}

			// 服务器错误，关闭响应体准备重试
			resp.Body.Close()
			
			// 如果已经达到最大重试次数，返回最后一次响应
			if attempt == c.retries {
				return resp, nil
			}
			
			logger.Warnf("服务器错误: %s %s, 状态码: %d, 正在重试...", req.Method, req.URL.String(), resp.StatusCode)
		} else {
			// 请求失败，检查是否已达到最大重试次数
			if attempt == c.retries {
				return nil, err
			}
			
			logger.Warnf("请求失败: %s %s, 错误: %v, 正在重试...", req.Method, req.URL.String(), err)
		}
	}

	return resp, err
}

// ReadBody 读取响应体并转换为结构体
func ReadBody(resp *http.Response, v interface{}) error {
	defer resp.Body.Close()
	
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return err
	}
	
	return json.Unmarshal(body, v)
}

// ReadBodyAsString 读取响应体并返回字符串
func ReadBodyAsString(resp *http.Response) (string, error) {
	defer resp.Body.Close()
	
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}
	
	return string(body), nil
}

// GetWithParams 发送带查询参数的GET请求
func (c *Client) GetWithParams(ctx context.Context, url string, params map[string]string) (*http.Response, error) {
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		return nil, err
	}

	// 添加查询参数
	if params != nil {
		q := req.URL.Query()
		for k, v := range params {
			q.Add(k, v)
		}
		req.URL.RawQuery = q.Encode()
	}

	// 添加请求头
	for k, v := range c.headers {
		req.Header.Set(k, v)
	}

	return c.do(req)
}

// DownloadFile 下载文件到指定路径
func (c *Client) DownloadFile(ctx context.Context, url, filepath string) error {
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		return err
	}

	// 添加请求头
	for k, v := range c.headers {
		req.Header.Set(k, v)
	}

	resp, err := c.do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	// 创建文件
	out, err := io.CreateTemp("", "download-*")
	if err != nil {
		return err
	}
	defer out.Close()

	// 写入文件
	_, err = io.Copy(out, resp.Body)
	if err != nil {
		return err
	}

	return nil
} 