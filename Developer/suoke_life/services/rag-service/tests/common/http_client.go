package common

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
	"time"
)

// HTTPClient 封装的HTTP客户端
type HTTPClient struct {
	BaseURL    string
	Client     *http.Client
	Timeout    time.Duration
	UserAgent  string
	Verbose    bool
	LogWriter  io.Writer
}

// NewHTTPClient 创建新的HTTP客户端
func NewHTTPClient(baseURL string, timeout time.Duration) *HTTPClient {
	return &HTTPClient{
		BaseURL:   baseURL,
		Client:    &http.Client{Timeout: timeout},
		Timeout:   timeout,
		UserAgent: "RAG-Testing-Client/1.0",
		LogWriter: os.Stdout,
	}
}

// Get 发送GET请求
func (c *HTTPClient) Get(ctx context.Context, endpoint string, params map[string]string) ([]byte, error) {
	req, err := http.NewRequestWithContext(ctx, "GET", c.BaseURL+endpoint, nil)
	if err != nil {
		return nil, err
	}
	
	// 添加请求头
	req.Header.Set("User-Agent", c.UserAgent)
	
	// 添加查询参数
	q := req.URL.Query()
	for k, v := range params {
		q.Add(k, v)
	}
	req.URL.RawQuery = q.Encode()
	
	if c.Verbose {
		fmt.Fprintf(c.LogWriter, "GET %s\n", req.URL.String())
	}
	
	// 发送请求
	resp, err := c.Client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	
	// 读取响应
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	
	if c.Verbose {
		fmt.Fprintf(c.LogWriter, "响应状态: %s\n", resp.Status)
	}
	
	if resp.StatusCode != http.StatusOK {
		return body, fmt.Errorf("错误状态: %s", resp.Status)
	}
	
	return body, nil
}

// PostJSON 发送JSON POST请求
func (c *HTTPClient) PostJSON(ctx context.Context, endpoint string, data interface{}) ([]byte, error) {
	jsonData, err := json.Marshal(data)
	if err != nil {
		return nil, err
	}
	
	req, err := http.NewRequestWithContext(ctx, "POST", c.BaseURL+endpoint, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, err
	}
	
	// 添加请求头
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("User-Agent", c.UserAgent)
	
	if c.Verbose {
		fmt.Fprintf(c.LogWriter, "POST %s\n", req.URL.String())
		fmt.Fprintf(c.LogWriter, "请求体: %s\n", string(jsonData))
	}
	
	// 发送请求
	resp, err := c.Client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	
	// 读取响应
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	
	if c.Verbose {
		fmt.Fprintf(c.LogWriter, "响应状态: %s\n", resp.Status)
	}
	
	if resp.StatusCode != http.StatusOK {
		return body, fmt.Errorf("错误状态: %s", resp.Status)
	}
	
	return body, nil
}

// UploadFile 上传文件
func (c *HTTPClient) UploadFile(ctx context.Context, endpoint string, filePath string, fieldName string, params map[string]string) ([]byte, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, err
	}
	defer file.Close()
	
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)
	
	// 创建文件表单字段
	part, err := writer.CreateFormFile(fieldName, filepath.Base(filePath))
	if err != nil {
		return nil, err
	}
	
	// 复制文件内容
	_, err = io.Copy(part, file)
	if err != nil {
		return nil, err
	}
	
	// 添加其他表单字段
	for key, val := range params {
		if err := writer.WriteField(key, val); err != nil {
			return nil, err
		}
	}
	
	if err := writer.Close(); err != nil {
		return nil, err
	}
	
	// 创建请求
	req, err := http.NewRequestWithContext(ctx, "POST", c.BaseURL+endpoint, body)
	if err != nil {
		return nil, err
	}
	
	// 设置请求头
	req.Header.Set("Content-Type", writer.FormDataContentType())
	req.Header.Set("User-Agent", c.UserAgent)
	
	if c.Verbose {
		fmt.Fprintf(c.LogWriter, "POST (multipart) %s\n", req.URL.String())
		fmt.Fprintf(c.LogWriter, "上传文件: %s\n", filePath)
	}
	
	// 发送请求
	resp, err := c.Client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	
	// 读取响应
	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	
	if c.Verbose {
		fmt.Fprintf(c.LogWriter, "响应状态: %s\n", resp.Status)
	}
	
	if resp.StatusCode != http.StatusOK {
		return respBody, fmt.Errorf("错误状态: %s", resp.Status)
	}
	
	return respBody, nil
} 