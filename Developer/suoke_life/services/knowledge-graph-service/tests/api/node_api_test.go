package api

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

const (
	// API基础URL
	baseURL = "http://localhost:8080/api/v1"
)

// TestMain 在运行测试之前设置测试环境
func TestMain(m *testing.M) {
	// 检查API服务是否运行
	resp, err := http.Get(fmt.Sprintf("%s/health", baseURL))
	if err != nil || resp.StatusCode != http.StatusOK {
		fmt.Printf("警告: API服务未运行在 %s\n", baseURL)
		fmt.Println("请先启动服务再运行API测试")
		os.Exit(1)
	}

	// 运行测试
	exitCode := m.Run()

	// 退出
	os.Exit(exitCode)
}

// 测试创建节点
func TestCreateNode(t *testing.T) {
	// 创建测试节点数据
	nodeData := map[string]interface{}{
		"name":        fmt.Sprintf("测试节点_%d", time.Now().Unix()),
		"category":    "测试类别",
		"description": "这是一个用于API测试的节点",
		"attributes": map[string]interface{}{
			"test_key": "test_value",
			"number":   123,
		},
	}

	// 将数据转换为JSON
	jsonData, err := json.Marshal(nodeData)
	assert.NoError(t, err)

	// 发送POST请求
	resp, err := http.Post(fmt.Sprintf("%s/nodes", baseURL), "application/json", bytes.NewBuffer(jsonData))
	assert.NoError(t, err)
	assert.Equal(t, http.StatusCreated, resp.StatusCode)

	// 解析响应
	body, err := io.ReadAll(resp.Body)
	assert.NoError(t, err)
	defer resp.Body.Close()

	var response map[string]interface{}
	err = json.Unmarshal(body, &response)
	assert.NoError(t, err)

	// 验证响应
	assert.NotEmpty(t, response["id"])
	nodeID := response["id"].(string)

	// 清理：删除创建的节点
	t.Cleanup(func() {
		deleteTestNode(t, nodeID)
	})
}

// 测试获取单个节点
func TestGetNodeByID(t *testing.T) {
	// 创建一个测试节点
	nodeID := createTestNode(t)

	// 发送GET请求
	resp, err := http.Get(fmt.Sprintf("%s/nodes/%s", baseURL, nodeID))
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, resp.StatusCode)

	// 解析响应
	body, err := io.ReadAll(resp.Body)
	assert.NoError(t, err)
	defer resp.Body.Close()

	var response map[string]interface{}
	err = json.Unmarshal(body, &response)
	assert.NoError(t, err)

	// 验证响应
	assert.Equal(t, nodeID, response["id"])
	assert.Contains(t, response["name"].(string), "测试节点")
	assert.Equal(t, "测试类别", response["category"])

	// 清理：删除创建的节点
	t.Cleanup(func() {
		deleteTestNode(t, nodeID)
	})
}

// 测试按类别获取节点
func TestGetNodesByCategory(t *testing.T) {
	// 创建几个测试节点
	nodeIDs := make([]string, 3)
	for i := 0; i < 3; i++ {
		nodeIDs[i] = createTestNode(t)
	}

	// 发送GET请求
	resp, err := http.Get(fmt.Sprintf("%s/nodes/category/测试类别?offset=0&limit=10", baseURL))
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, resp.StatusCode)

	// 解析响应
	body, err := io.ReadAll(resp.Body)
	assert.NoError(t, err)
	defer resp.Body.Close()

	var response map[string]interface{}
	err = json.Unmarshal(body, &response)
	assert.NoError(t, err)

	// 验证响应
	assert.NotNil(t, response["nodes"])
	assert.NotNil(t, response["total"])
	assert.GreaterOrEqual(t, int(response["total"].(float64)), 3)

	// 清理：删除创建的节点
	t.Cleanup(func() {
		for _, nodeID := range nodeIDs {
			deleteTestNode(t, nodeID)
		}
	})
}

// 测试更新节点
func TestUpdateNode(t *testing.T) {
	// 创建一个测试节点
	nodeID := createTestNode(t)

	// 更新数据
	updateData := map[string]interface{}{
		"description": "这是更新后的描述",
		"attributes": map[string]interface{}{
			"updated_key": "updated_value",
		},
	}

	// 将数据转换为JSON
	jsonData, err := json.Marshal(updateData)
	assert.NoError(t, err)

	// 创建PUT请求
	req, err := http.NewRequest(http.MethodPut, fmt.Sprintf("%s/nodes/%s", baseURL, nodeID), bytes.NewBuffer(jsonData))
	assert.NoError(t, err)
	req.Header.Set("Content-Type", "application/json")

	// 发送请求
	client := &http.Client{}
	resp, err := client.Do(req)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, resp.StatusCode)
	resp.Body.Close()

	// 获取更新后的节点进行验证
	resp, err = http.Get(fmt.Sprintf("%s/nodes/%s", baseURL, nodeID))
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, resp.StatusCode)

	// 解析响应
	body, err := io.ReadAll(resp.Body)
	assert.NoError(t, err)
	defer resp.Body.Close()

	var response map[string]interface{}
	err = json.Unmarshal(body, &response)
	assert.NoError(t, err)

	// 验证响应中包含更新后的数据
	assert.Equal(t, "这是更新后的描述", response["description"])
	attributes := response["attributes"].(map[string]interface{})
	assert.Equal(t, "updated_value", attributes["updated_key"])

	// 清理：删除创建的节点
	t.Cleanup(func() {
		deleteTestNode(t, nodeID)
	})
}

// 测试删除节点
func TestDeleteNode(t *testing.T) {
	// 创建一个测试节点
	nodeID := createTestNode(t)

	// 创建DELETE请求
	req, err := http.NewRequest(http.MethodDelete, fmt.Sprintf("%s/nodes/%s", baseURL, nodeID), nil)
	assert.NoError(t, err)

	// 发送请求
	client := &http.Client{}
	resp, err := client.Do(req)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, resp.StatusCode)
	resp.Body.Close()

	// 验证节点已被删除
	resp, err = http.Get(fmt.Sprintf("%s/nodes/%s", baseURL, nodeID))
	assert.NoError(t, err)
	assert.Equal(t, http.StatusNotFound, resp.StatusCode)
	resp.Body.Close()
}

// 测试获取所有类别
func TestGetAllCategories(t *testing.T) {
	// 创建一个测试节点以确保有至少一个类别
	nodeID := createTestNode(t)

	// 发送GET请求
	resp, err := http.Get(fmt.Sprintf("%s/nodes/categories", baseURL))
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, resp.StatusCode)

	// 解析响应
	body, err := io.ReadAll(resp.Body)
	assert.NoError(t, err)
	defer resp.Body.Close()

	var response map[string]interface{}
	err = json.Unmarshal(body, &response)
	assert.NoError(t, err)

	// 验证响应
	assert.NotNil(t, response["categories"])
	categories := response["categories"].([]interface{})
	assert.GreaterOrEqual(t, len(categories), 1)
	assert.Contains(t, categories, "测试类别")

	// 清理：删除创建的节点
	t.Cleanup(func() {
		deleteTestNode(t, nodeID)
	})
}

// 测试搜索节点
func TestSearchNodes(t *testing.T) {
	// 创建一个特殊的测试节点用于搜索
	uniqueName := fmt.Sprintf("特殊测试节点_%d", time.Now().Unix())
	nodeData := map[string]interface{}{
		"name":        uniqueName,
		"category":    "测试类别",
		"description": "这是一个用于搜索测试的特殊节点",
	}

	jsonData, err := json.Marshal(nodeData)
	assert.NoError(t, err)

	resp, err := http.Post(fmt.Sprintf("%s/nodes", baseURL), "application/json", bytes.NewBuffer(jsonData))
	assert.NoError(t, err)
	assert.Equal(t, http.StatusCreated, resp.StatusCode)

	body, err := io.ReadAll(resp.Body)
	assert.NoError(t, err)
	resp.Body.Close()

	var createResponse map[string]interface{}
	err = json.Unmarshal(body, &createResponse)
	assert.NoError(t, err)
	nodeID := createResponse["id"].(string)

	// 构造搜索查询
	searchQuery := map[string]interface{}{
		"query": map[string]interface{}{
			"name": uniqueName,
		},
		"limit":  10,
		"offset": 0,
	}

	jsonData, err = json.Marshal(searchQuery)
	assert.NoError(t, err)

	// 发送搜索请求
	resp, err = http.Post(fmt.Sprintf("%s/nodes/search", baseURL), "application/json", bytes.NewBuffer(jsonData))
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, resp.StatusCode)

	// 解析响应
	body, err = io.ReadAll(resp.Body)
	assert.NoError(t, err)
	resp.Body.Close()

	var searchResponse map[string]interface{}
	err = json.Unmarshal(body, &searchResponse)
	assert.NoError(t, err)

	// 验证搜索结果
	assert.NotNil(t, searchResponse["nodes"])
	assert.NotNil(t, searchResponse["total"])
	assert.GreaterOrEqual(t, int(searchResponse["total"].(float64)), 1)

	// 检查是否找到了我们创建的特定节点
	found := false
	nodes := searchResponse["nodes"].([]interface{})
	for _, node := range nodes {
		nodeMap := node.(map[string]interface{})
		if nodeMap["id"] == nodeID {
			found = true
			break
		}
	}
	assert.True(t, found, "未在搜索结果中找到特定节点")

	// 清理：删除创建的节点
	t.Cleanup(func() {
		deleteTestNode(t, nodeID)
	})
}

// 辅助函数: 创建测试节点
func createTestNode(t *testing.T) string {
	// 创建节点数据
	nodeData := map[string]interface{}{
		"name":        fmt.Sprintf("测试节点_%d", time.Now().Unix()),
		"category":    "测试类别",
		"description": "这是一个API测试节点",
	}

	// 将数据转换为JSON
	jsonData, err := json.Marshal(nodeData)
	assert.NoError(t, err)

	// 发送POST请求
	resp, err := http.Post(fmt.Sprintf("%s/nodes", baseURL), "application/json", bytes.NewBuffer(jsonData))
	assert.NoError(t, err)
	assert.Equal(t, http.StatusCreated, resp.StatusCode)

	// 解析响应
	body, err := io.ReadAll(resp.Body)
	assert.NoError(t, err)
	defer resp.Body.Close()

	var response map[string]interface{}
	err = json.Unmarshal(body, &response)
	assert.NoError(t, err)

	// 返回创建的节点ID
	return response["id"].(string)
}

// 辅助函数: 删除测试节点
func deleteTestNode(t *testing.T, nodeID string) {
	// 创建DELETE请求
	req, err := http.NewRequest(http.MethodDelete, fmt.Sprintf("%s/nodes/%s", baseURL, nodeID), nil)
	if err != nil {
		t.Logf("删除节点时出错: %v", err)
		return
	}

	// 发送请求
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		t.Logf("删除节点时出错: %v", err)
		return
	}
	defer resp.Body.Close()

	// 如果状态码不是200，记录但不失败
	if resp.StatusCode != http.StatusOK {
		t.Logf("删除节点失败，状态码: %d", resp.StatusCode)
	}
} 