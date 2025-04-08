package api

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

// 测试创建关系
func TestCreateRelationship(t *testing.T) {
	// 创建两个测试节点作为关系的起点和终点
	fromNodeID := createTestNode(t)
	toNodeID := createTestNode(t)

	// 创建测试关系数据
	relData := map[string]interface{}{
		"from_node_id": fromNodeID,
		"to_node_id":   toNodeID,
		"type":         "TEST_RELATES_TO",
		"properties": map[string]interface{}{
			"test_key": "test_value",
			"weight":   0.75,
		},
	}

	// 将数据转换为JSON
	jsonData, err := json.Marshal(relData)
	assert.NoError(t, err)

	// 发送POST请求
	resp, err := http.Post(fmt.Sprintf("%s/relationships", baseURL), "application/json", bytes.NewBuffer(jsonData))
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
	relID := response["id"].(string)

	// 清理：删除创建的关系和节点
	t.Cleanup(func() {
		deleteTestRelationship(t, relID)
		deleteTestNode(t, fromNodeID)
		deleteTestNode(t, toNodeID)
	})
}

// 测试获取单个关系
func TestGetRelationshipByID(t *testing.T) {
	// 创建测试关系
	fromNodeID := createTestNode(t)
	toNodeID := createTestNode(t)
	relID := createTestRelationship(t, fromNodeID, toNodeID)

	// 发送GET请求
	resp, err := http.Get(fmt.Sprintf("%s/relationships/%s", baseURL, relID))
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
	assert.Equal(t, relID, response["id"])
	assert.Equal(t, "TEST_RELATES_TO", response["type"])
	assert.Equal(t, fromNodeID, response["from_node_id"])
	assert.Equal(t, toNodeID, response["to_node_id"])

	// 清理：删除测试数据
	t.Cleanup(func() {
		deleteTestRelationship(t, relID)
		deleteTestNode(t, fromNodeID)
		deleteTestNode(t, toNodeID)
	})
}

// 测试获取两个节点之间的关系
func TestGetRelationshipsBetweenNodes(t *testing.T) {
	// 创建两个测试节点
	fromNodeID := createTestNode(t)
	toNodeID := createTestNode(t)

	// 创建两个不同类型的关系连接这两个节点
	rel1ID := createTestRelationship(t, fromNodeID, toNodeID)
	
	// 创建第二个关系，不同类型
	relData := map[string]interface{}{
		"from_node_id": fromNodeID,
		"to_node_id":   toNodeID,
		"type":         "TEST_DEPENDS_ON",
	}
	jsonData, err := json.Marshal(relData)
	assert.NoError(t, err)
	resp, err := http.Post(fmt.Sprintf("%s/relationships", baseURL), "application/json", bytes.NewBuffer(jsonData))
	assert.NoError(t, err)
	assert.Equal(t, http.StatusCreated, resp.StatusCode)
	body, err := io.ReadAll(resp.Body)
	assert.NoError(t, err)
	resp.Body.Close()
	var response map[string]interface{}
	err = json.Unmarshal(body, &response)
	assert.NoError(t, err)
	rel2ID := response["id"].(string)

	// 发送GET请求获取两个节点之间的所有关系
	resp, err = http.Get(fmt.Sprintf("%s/relationships/between?from_node_id=%s&to_node_id=%s", baseURL, fromNodeID, toNodeID))
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, resp.StatusCode)

	// 解析响应
	body, err = io.ReadAll(resp.Body)
	assert.NoError(t, err)
	defer resp.Body.Close()

	var betweenResponse map[string]interface{}
	err = json.Unmarshal(body, &betweenResponse)
	assert.NoError(t, err)

	// 验证响应
	assert.Equal(t, float64(2), betweenResponse["total"])
	relationships := betweenResponse["relationships"].([]interface{})
	assert.Len(t, relationships, 2)

	// 清理：删除测试数据
	t.Cleanup(func() {
		deleteTestRelationship(t, rel1ID)
		deleteTestRelationship(t, rel2ID)
		deleteTestNode(t, fromNodeID)
		deleteTestNode(t, toNodeID)
	})
}

// 测试获取节点的出站关系
func TestGetOutgoingRelationships(t *testing.T) {
	// 创建测试节点
	fromNodeID := createTestNode(t)
	toNodeID1 := createTestNode(t)
	toNodeID2 := createTestNode(t)

	// 创建两个从fromNode出发的关系
	rel1ID := createTestRelationship(t, fromNodeID, toNodeID1)
	rel2ID := createTestRelationship(t, fromNodeID, toNodeID2)

	// 发送GET请求获取出站关系
	resp, err := http.Get(fmt.Sprintf("%s/nodes/%s/outgoing?offset=0&limit=10", baseURL, fromNodeID))
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
	assert.GreaterOrEqual(t, int(response["total"].(float64)), 2)
	relationships := response["relationships"].([]interface{})
	assert.GreaterOrEqual(t, len(relationships), 2)

	// 清理：删除测试数据
	t.Cleanup(func() {
		deleteTestRelationship(t, rel1ID)
		deleteTestRelationship(t, rel2ID)
		deleteTestNode(t, fromNodeID)
		deleteTestNode(t, toNodeID1)
		deleteTestNode(t, toNodeID2)
	})
}

// 测试获取节点的入站关系
func TestGetIncomingRelationships(t *testing.T) {
	// 创建测试节点
	fromNodeID1 := createTestNode(t)
	fromNodeID2 := createTestNode(t)
	toNodeID := createTestNode(t)

	// 创建两个指向toNode的关系
	rel1ID := createTestRelationship(t, fromNodeID1, toNodeID)
	rel2ID := createTestRelationship(t, fromNodeID2, toNodeID)

	// 发送GET请求获取入站关系
	resp, err := http.Get(fmt.Sprintf("%s/nodes/%s/incoming?offset=0&limit=10", baseURL, toNodeID))
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
	assert.GreaterOrEqual(t, int(response["total"].(float64)), 2)
	relationships := response["relationships"].([]interface{})
	assert.GreaterOrEqual(t, len(relationships), 2)

	// 清理：删除测试数据
	t.Cleanup(func() {
		deleteTestRelationship(t, rel1ID)
		deleteTestRelationship(t, rel2ID)
		deleteTestNode(t, fromNodeID1)
		deleteTestNode(t, fromNodeID2)
		deleteTestNode(t, toNodeID)
	})
}

// 测试更新关系
func TestUpdateRelationship(t *testing.T) {
	// 创建测试关系
	fromNodeID := createTestNode(t)
	toNodeID := createTestNode(t)
	relID := createTestRelationship(t, fromNodeID, toNodeID)

	// 更新数据
	updateData := map[string]interface{}{
		"properties": map[string]interface{}{
			"updated_key": "updated_value",
			"weight":      0.9,
		},
	}

	// 将数据转换为JSON
	jsonData, err := json.Marshal(updateData)
	assert.NoError(t, err)

	// 创建PUT请求
	req, err := http.NewRequest(http.MethodPut, fmt.Sprintf("%s/relationships/%s", baseURL, relID), bytes.NewBuffer(jsonData))
	assert.NoError(t, err)
	req.Header.Set("Content-Type", "application/json")

	// 发送请求
	client := &http.Client{}
	resp, err := client.Do(req)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, resp.StatusCode)
	resp.Body.Close()

	// 获取更新后的关系进行验证
	resp, err = http.Get(fmt.Sprintf("%s/relationships/%s", baseURL, relID))
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
	properties := response["properties"].(map[string]interface{})
	assert.Equal(t, "updated_value", properties["updated_key"])
	assert.Equal(t, 0.9, properties["weight"])

	// 清理：删除测试数据
	t.Cleanup(func() {
		deleteTestRelationship(t, relID)
		deleteTestNode(t, fromNodeID)
		deleteTestNode(t, toNodeID)
	})
}

// 测试删除关系
func TestDeleteRelationship(t *testing.T) {
	// 创建测试关系
	fromNodeID := createTestNode(t)
	toNodeID := createTestNode(t)
	relID := createTestRelationship(t, fromNodeID, toNodeID)

	// 创建DELETE请求
	req, err := http.NewRequest(http.MethodDelete, fmt.Sprintf("%s/relationships/%s", baseURL, relID), nil)
	assert.NoError(t, err)

	// 发送请求
	client := &http.Client{}
	resp, err := client.Do(req)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, resp.StatusCode)
	resp.Body.Close()

	// 验证关系已被删除
	resp, err = http.Get(fmt.Sprintf("%s/relationships/%s", baseURL, relID))
	assert.NoError(t, err)
	assert.Equal(t, http.StatusNotFound, resp.StatusCode)
	resp.Body.Close()

	// 清理：删除测试节点
	t.Cleanup(func() {
		deleteTestNode(t, fromNodeID)
		deleteTestNode(t, toNodeID)
	})
}

// 测试删除节点间的关系
func TestDeleteRelationshipsBetweenNodes(t *testing.T) {
	// 创建测试节点
	fromNodeID := createTestNode(t)
	toNodeID := createTestNode(t)

	// 创建两个从fromNode到toNode的关系
	createTestRelationship(t, fromNodeID, toNodeID)
	
	// 创建不同类型的关系
	relData := map[string]interface{}{
		"from_node_id": fromNodeID,
		"to_node_id":   toNodeID,
		"type":         "TEST_DEPENDS_ON",
	}
	jsonData, err := json.Marshal(relData)
	assert.NoError(t, err)
	resp, err := http.Post(fmt.Sprintf("%s/relationships", baseURL), "application/json", bytes.NewBuffer(jsonData))
	assert.NoError(t, err)
	resp.Body.Close()

	// 验证已创建两个关系
	resp, err = http.Get(fmt.Sprintf("%s/relationships/between?from_node_id=%s&to_node_id=%s", baseURL, fromNodeID, toNodeID))
	assert.NoError(t, err)
	body, err := io.ReadAll(resp.Body)
	assert.NoError(t, err)
	resp.Body.Close()
	var beforeResponse map[string]interface{}
	err = json.Unmarshal(body, &beforeResponse)
	assert.NoError(t, err)
	assert.Equal(t, float64(2), beforeResponse["total"])

	// 创建DELETE请求，删除指定类型的关系
	req, err := http.NewRequest(http.MethodDelete, fmt.Sprintf("%s/relationships/between?from_node_id=%s&to_node_id=%s&type=TEST_RELATES_TO", baseURL, fromNodeID, toNodeID), nil)
	assert.NoError(t, err)

	// 发送请求
	client := &http.Client{}
	resp, err = client.Do(req)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, resp.StatusCode)
	resp.Body.Close()

	// 验证TEST_RELATES_TO类型的关系已被删除，但其他类型仍存在
	resp, err = http.Get(fmt.Sprintf("%s/relationships/between?from_node_id=%s&to_node_id=%s", baseURL, fromNodeID, toNodeID))
	assert.NoError(t, err)
	body, err = io.ReadAll(resp.Body)
	assert.NoError(t, err)
	resp.Body.Close()
	var afterResponse map[string]interface{}
	err = json.Unmarshal(body, &afterResponse)
	assert.NoError(t, err)
	assert.Equal(t, float64(1), afterResponse["total"])
	
	// 删除所有剩余关系
	req, err = http.NewRequest(http.MethodDelete, fmt.Sprintf("%s/relationships/between?from_node_id=%s&to_node_id=%s", baseURL, fromNodeID, toNodeID), nil)
	assert.NoError(t, err)
	resp, err = client.Do(req)
	assert.NoError(t, err)
	resp.Body.Close()

	// 清理：删除测试节点
	t.Cleanup(func() {
		deleteTestNode(t, fromNodeID)
		deleteTestNode(t, toNodeID)
	})
}

// 测试获取所有关系类型
func TestGetAllRelationshipTypes(t *testing.T) {
	// 创建一个具有特定类型的测试关系，确保该类型存在
	fromNodeID := createTestNode(t)
	toNodeID := createTestNode(t)
	relID := createTestRelationship(t, fromNodeID, toNodeID)

	// 发送GET请求
	resp, err := http.Get(fmt.Sprintf("%s/relationships/types", baseURL))
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
	assert.NotNil(t, response["types"])
	types := response["types"].([]interface{})
	assert.GreaterOrEqual(t, len(types), 1)
	assert.Contains(t, types, "TEST_RELATES_TO")

	// 清理：删除测试数据
	t.Cleanup(func() {
		deleteTestRelationship(t, relID)
		deleteTestNode(t, fromNodeID)
		deleteTestNode(t, toNodeID)
	})
}

// 测试查找路径
func TestFindPath(t *testing.T) {
	// 创建一条简单的路径：node1 -> node2 -> node3
	node1ID := createTestNode(t)
	node2ID := createTestNode(t)
	node3ID := createTestNode(t)
	
	rel1ID := createTestRelationship(t, node1ID, node2ID)
	rel2ID := createTestRelationship(t, node2ID, node3ID)

	// 发送GET请求查找从node1到node3的路径
	resp, err := http.Get(fmt.Sprintf("%s/relationships/path?from_node_id=%s&to_node_id=%s&max_depth=3", baseURL, node1ID, node3ID))
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, resp.StatusCode)

	// 解析响应
	body, err := io.ReadAll(resp.Body)
	assert.NoError(t, err)
	defer resp.Body.Close()

	var response map[string]interface{}
	err = json.Unmarshal(body, &response)
	assert.NoError(t, err)

	// 验证找到了路径
	assert.GreaterOrEqual(t, int(response["total_paths"].(float64)), 1)
	paths := response["paths"].([]interface{})
	assert.GreaterOrEqual(t, len(paths), 1)
	
	// 验证路径包含正确的节点
	path := paths[0].(map[string]interface{})
	pathNodes := path["nodes"].([]interface{})
	assert.Contains(t, pathNodes, node1ID)
	assert.Contains(t, pathNodes, node2ID)
	assert.Contains(t, pathNodes, node3ID)

	// 清理：删除测试数据
	t.Cleanup(func() {
		deleteTestRelationship(t, rel1ID)
		deleteTestRelationship(t, rel2ID)
		deleteTestNode(t, node1ID)
		deleteTestNode(t, node2ID)
		deleteTestNode(t, node3ID)
	})
}

// 辅助函数：创建测试关系
func createTestRelationship(t *testing.T, fromNodeID, toNodeID string) string {
	// 创建关系数据
	relData := map[string]interface{}{
		"from_node_id": fromNodeID,
		"to_node_id":   toNodeID,
		"type":         "TEST_RELATES_TO",
		"properties": map[string]interface{}{
			"created_at": time.Now().Format(time.RFC3339),
			"test":       true,
		},
	}

	// 将数据转换为JSON
	jsonData, err := json.Marshal(relData)
	assert.NoError(t, err)

	// 发送POST请求
	resp, err := http.Post(fmt.Sprintf("%s/relationships", baseURL), "application/json", bytes.NewBuffer(jsonData))
	assert.NoError(t, err)
	assert.Equal(t, http.StatusCreated, resp.StatusCode)

	// 解析响应
	body, err := io.ReadAll(resp.Body)
	assert.NoError(t, err)
	defer resp.Body.Close()

	var response map[string]interface{}
	err = json.Unmarshal(body, &response)
	assert.NoError(t, err)

	// 返回创建的关系ID
	return response["id"].(string)
}

// 辅助函数：删除测试关系
func deleteTestRelationship(t *testing.T, relID string) {
	// 创建DELETE请求
	req, err := http.NewRequest(http.MethodDelete, fmt.Sprintf("%s/relationships/%s", baseURL, relID), nil)
	if err != nil {
		t.Logf("删除关系时出错: %v", err)
		return
	}

	// 发送请求
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		t.Logf("删除关系时出错: %v", err)
		return
	}
	defer resp.Body.Close()

	// 如果状态码不是200，记录但不失败
	if resp.StatusCode != http.StatusOK {
		t.Logf("删除关系失败，状态码: %d", resp.StatusCode)
	}
} 