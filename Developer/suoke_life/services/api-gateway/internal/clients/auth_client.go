package clients

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"time"

	"github.com/suoke-life/api-gateway/internal/logger"
)

// AuthResponse 表示从认证服务接收的响应
type AuthResponse struct {
	Valid    bool   `json:"valid"`
	UserID   string `json:"user_id,omitempty"`
	Username string `json:"username,omitempty"`
	Email    string `json:"email,omitempty"`
	Role     string `json:"role,omitempty"`
	Error    string `json:"error,omitempty"`
}

// TokenClaims 表示令牌中包含的声明
type TokenClaims struct {
	UserID   string `json:"user_id"`
	Username string `json:"username"`
	Email    string `json:"email"`
	Role     string `json:"role"`
}

// AuthClient 认证服务客户端
type AuthClient struct {
	baseURL    string
	client     *http.Client
	logger     logger.Logger
}

// NewAuthClient 创建新的认证服务客户端
func NewAuthClient(baseURL string, timeout time.Duration, logger logger.Logger) *AuthClient {
	return &AuthClient{
		baseURL: baseURL,
		client: &http.Client{
			Timeout: timeout,
		},
		logger: logger,
	}
}

// ValidateToken 通过认证服务验证令牌
func (c *AuthClient) ValidateToken(token string) (*TokenClaims, error) {
	c.logger.Info("正在向认证服务验证令牌")
	
	reqBody, err := json.Marshal(map[string]string{
		"token": token,
	})
	if err != nil {
		return nil, fmt.Errorf("序列化请求体失败: %w", err)
	}

	req, err := http.NewRequest("POST", fmt.Sprintf("%s/auth/validate", c.baseURL), bytes.NewBuffer(reqBody))
	if err != nil {
		return nil, fmt.Errorf("创建请求失败: %w", err)
	}
	
	req.Header.Set("Content-Type", "application/json")
	
	resp, err := c.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("发送请求失败: %w", err)
	}
	defer resp.Body.Close()
	
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("读取响应体失败: %w", err)
	}
	
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("认证服务返回错误: %s, 状态码: %d", string(body), resp.StatusCode)
	}
	
	var authResp AuthResponse
	if err := json.Unmarshal(body, &authResp); err != nil {
		return nil, fmt.Errorf("解析响应失败: %w", err)
	}
	
	if !authResp.Valid {
		return nil, fmt.Errorf("令牌无效: %s", authResp.Error)
	}
	
	return &TokenClaims{
		UserID:   authResp.UserID,
		Username: authResp.Username,
		Email:    authResp.Email,
		Role:     authResp.Role,
	}, nil
}