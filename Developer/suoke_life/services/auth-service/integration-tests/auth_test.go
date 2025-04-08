package integration_tests

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const (
	baseURL = "http://localhost:8081"
)

// 测试用户数据
var testUser = struct {
	Username string `json:"username"`
	Email    string `json:"email"`
	Password string `json:"password"`
}{
	Username: "testuser",
	Email:    "test@example.com",
	Password: "Test@password123",
}

// TestHealthCheck 测试健康检查端点
func TestHealthCheck(t *testing.T) {
	resp, err := http.Get(fmt.Sprintf("%s/health", baseURL))
	require.NoError(t, err)
	defer resp.Body.Close()

	assert.Equal(t, http.StatusOK, resp.StatusCode)

	var result map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&result)
	require.NoError(t, err)

	assert.Equal(t, "ok", result["status"])
	assert.Equal(t, "auth-service", result["service"])
	assert.NotEmpty(t, result["time"])
}

// TestRegistration 测试用户注册
func TestRegistration(t *testing.T) {
	// 创建注册请求
	payload, err := json.Marshal(map[string]string{
		"username": testUser.Username,
		"email":    testUser.Email,
		"password": testUser.Password,
	})
	require.NoError(t, err)

	resp, err := http.Post(
		fmt.Sprintf("%s/auth/register", baseURL),
		"application/json",
		bytes.NewBuffer(payload),
	)
	require.NoError(t, err)
	defer resp.Body.Close()

	// 检查响应状态码
	assert.Equal(t, http.StatusCreated, resp.StatusCode)

	// 解析响应体
	var result map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&result)
	require.NoError(t, err)

	assert.Equal(t, "用户注册成功", result["message"])
	assert.NotNil(t, result["user"])
	assert.NotNil(t, result["token"])

	user := result["user"].(map[string]interface{})
	assert.Equal(t, testUser.Username, user["username"])
	assert.Equal(t, testUser.Email, user["email"])
	assert.NotEmpty(t, user["id"])

	token := result["token"].(map[string]interface{})
	assert.NotEmpty(t, token["access_token"])
	assert.NotEmpty(t, token["refresh_token"])
	assert.Equal(t, "Bearer", token["token_type"])
	assert.Greater(t, token["expires_in"].(float64), float64(0))
}

// TestLogin 测试用户登录
func TestLogin(t *testing.T) {
	// 创建登录请求
	payload, err := json.Marshal(map[string]string{
		"username": testUser.Username,
		"password": testUser.Password,
	})
	require.NoError(t, err)

	resp, err := http.Post(
		fmt.Sprintf("%s/auth/login", baseURL),
		"application/json",
		bytes.NewBuffer(payload),
	)
	require.NoError(t, err)
	defer resp.Body.Close()

	// 检查响应状态码
	assert.Equal(t, http.StatusOK, resp.StatusCode)

	// 解析响应体
	var result map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&result)
	require.NoError(t, err)

	assert.Equal(t, "登录成功", result["message"])
	assert.NotNil(t, result["user"])
	assert.NotNil(t, result["token"])

	user := result["user"].(map[string]interface{})
	assert.Equal(t, testUser.Username, user["username"])
	assert.Equal(t, testUser.Email, user["email"])
	assert.NotEmpty(t, user["id"])

	token := result["token"].(map[string]interface{})
	assert.NotEmpty(t, token["access_token"])
	assert.NotEmpty(t, token["refresh_token"])
	assert.Equal(t, "Bearer", token["token_type"])
	assert.Greater(t, token["expires_in"].(float64), float64(0))
}

// TestRefreshToken 测试刷新令牌
func TestRefreshToken(t *testing.T) {
	// 首先登录获取刷新令牌
	payload, err := json.Marshal(map[string]string{
		"username": testUser.Username,
		"password": testUser.Password,
	})
	require.NoError(t, err)

	resp, err := http.Post(
		fmt.Sprintf("%s/auth/login", baseURL),
		"application/json",
		bytes.NewBuffer(payload),
	)
	require.NoError(t, err)
	defer resp.Body.Close()

	// 解析登录响应获取刷新令牌
	var loginResult map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&loginResult)
	require.NoError(t, err)

	token := loginResult["token"].(map[string]interface{})
	refreshToken := token["refresh_token"].(string)

	// 使用刷新令牌获取新令牌
	refreshPayload, err := json.Marshal(map[string]string{
		"refresh_token": refreshToken,
	})
	require.NoError(t, err)

	refreshResp, err := http.Post(
		fmt.Sprintf("%s/auth/refresh", baseURL),
		"application/json",
		bytes.NewBuffer(refreshPayload),
	)
	require.NoError(t, err)
	defer refreshResp.Body.Close()

	// 检查响应状态码
	assert.Equal(t, http.StatusOK, refreshResp.StatusCode)

	// 解析响应体
	var refreshResult map[string]interface{}
	err = json.NewDecoder(refreshResp.Body).Decode(&refreshResult)
	require.NoError(t, err)

	assert.Equal(t, "令牌刷新成功", refreshResult["message"])
	assert.NotNil(t, refreshResult["token"])

	newToken := refreshResult["token"].(map[string]interface{})
	assert.NotEmpty(t, newToken["access_token"])
	assert.NotEmpty(t, newToken["refresh_token"])
	assert.Equal(t, "Bearer", newToken["token_type"])
	assert.Greater(t, newToken["expires_in"].(float64), float64(0))
}

// TestValidateToken 测试验证令牌
func TestValidateToken(t *testing.T) {
	// 首先登录获取访问令牌
	payload, err := json.Marshal(map[string]string{
		"username": testUser.Username,
		"password": testUser.Password,
	})
	require.NoError(t, err)

	resp, err := http.Post(
		fmt.Sprintf("%s/auth/login", baseURL),
		"application/json",
		bytes.NewBuffer(payload),
	)
	require.NoError(t, err)
	defer resp.Body.Close()

	// 解析登录响应获取访问令牌
	var loginResult map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&loginResult)
	require.NoError(t, err)

	token := loginResult["token"].(map[string]interface{})
	accessToken := token["access_token"].(string)

	// 使用访问令牌验证
	req, err := http.NewRequest("GET", fmt.Sprintf("%s/auth/validate", baseURL), nil)
	require.NoError(t, err)
	req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", accessToken))

	client := &http.Client{Timeout: 10 * time.Second}
	validateResp, err := client.Do(req)
	require.NoError(t, err)
	defer validateResp.Body.Close()

	// 检查响应状态码
	assert.Equal(t, http.StatusOK, validateResp.StatusCode)

	// 解析响应体
	var validateResult map[string]interface{}
	err = json.NewDecoder(validateResp.Body).Decode(&validateResult)
	require.NoError(t, err)

	assert.Equal(t, true, validateResult["valid"])
	assert.NotNil(t, validateResult["user"])

	user := validateResult["user"].(map[string]interface{})
	assert.Equal(t, testUser.Username, user["username"])
	assert.Equal(t, testUser.Email, user["email"])
	assert.NotEmpty(t, user["id"])
} 