package api

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
)

// 测试获取单个TCM节点
func TestGetTCMNodeByID(t *testing.T) {
	// 首先创建一个TCM节点用于测试
	tcmNodeID := createTestTCMNode(t, "HERB")

	// 发送GET请求
	resp, err := http.Get(fmt.Sprintf("%s/tcm/nodes/%s", baseURL, tcmNodeID))
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
	assert.Equal(t, tcmNodeID, response["id"])
	assert.Equal(t, "测试TCM节点", response["name"])
	assert.Equal(t, "HERB", response["sub_type"])

	// 清理：删除测试节点
	t.Cleanup(func() {
		deleteTestNode(t, tcmNodeID)
	})
}

// 测试获取TCM节点列表（按子类型）
func TestGetTCMNodesBySubType(t *testing.T) {
	// 创建几个具有相同子类型的测试TCM节点
	tcmNodeID1 := createTestTCMNode(t, "HERB")
	tcmNodeID2 := createTestTCMNode(t, "HERB")
	tcmNodeID3 := createTestTCMNode(t, "FORMULA") // 不同子类型

	// 发送GET请求，获取HERB子类型的节点
	resp, err := http.Get(fmt.Sprintf("%s/tcm/nodes/subtype/HERB?offset=0&limit=10", baseURL))
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
	nodes := response["nodes"].([]interface{})
	assert.GreaterOrEqual(t, len(nodes), 2)

	// 验证返回的节点都是HERB子类型
	for _, node := range nodes {
		nodeMap := node.(map[string]interface{})
		if nodeMap["id"] == tcmNodeID1 || nodeMap["id"] == tcmNodeID2 {
			assert.Equal(t, "HERB", nodeMap["sub_type"])
		}
	}

	// 清理：删除测试节点
	t.Cleanup(func() {
		deleteTestNode(t, tcmNodeID1)
		deleteTestNode(t, tcmNodeID2)
		deleteTestNode(t, tcmNodeID3)
	})
}

// 测试获取TCM节点列表（按子类型和分类）
func TestGetTCMNodesBySubTypeAndClassification(t *testing.T) {
	// 创建具有特定子类型和分类的TCM节点
	tcmNodeID1 := createTestTCMNodeWithClassification(t, "HERB", "温热药")
	tcmNodeID2 := createTestTCMNodeWithClassification(t, "HERB", "寒凉药")

	// 发送GET请求，获取特定子类型和分类的节点
	resp, err := http.Get(fmt.Sprintf("%s/tcm/nodes/subtype/HERB/classification/温热药?offset=0&limit=10", baseURL))
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
	assert.GreaterOrEqual(t, int(response["total"].(float64)), 1)
	nodes := response["nodes"].([]interface{})
	assert.GreaterOrEqual(t, len(nodes), 1)

	// 验证返回的节点都是匹配的子类型和分类
	for _, node := range nodes {
		nodeMap := node.(map[string]interface{})
		if nodeMap["id"] == tcmNodeID1 {
			assert.Equal(t, "HERB", nodeMap["sub_type"])
			assert.Equal(t, "温热药", nodeMap["classification"])
		}
	}

	// 清理：删除测试节点
	t.Cleanup(func() {
		deleteTestNode(t, tcmNodeID1)
		deleteTestNode(t, tcmNodeID2)
	})
}

// 测试搜索TCM节点
func TestSearchTCMNodes(t *testing.T) {
	// 创建几个测试TCM节点
	tcmNodeID1 := createTestTCMNode(t, "HERB")
	tcmNodeID2 := createTestTCMNodeWithName(t, "HERB", "特殊测试名称")

	// 创建搜索请求数据
	searchData := map[string]interface{}{
		"query":    "特殊测试",
		"sub_type": "HERB",
		"offset":   0,
		"limit":    10,
	}

	// 将数据转换为JSON
	jsonData, err := json.Marshal(searchData)
	assert.NoError(t, err)

	// 发送POST请求
	resp, err := http.Post(fmt.Sprintf("%s/tcm/nodes/search", baseURL), "application/json", bytes.NewBuffer(jsonData))
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
	assert.GreaterOrEqual(t, int(response["total"].(float64)), 1)
	nodes := response["nodes"].([]interface{})
	assert.GreaterOrEqual(t, len(nodes), 1)

	// 验证搜索结果包含特定名称的节点
	found := false
	for _, node := range nodes {
		nodeMap := node.(map[string]interface{})
		if nodeMap["name"] == "特殊测试名称" {
			found = true
			break
		}
	}
	assert.True(t, found, "搜索结果应包含特定名称的节点")

	// 清理：删除测试节点
	t.Cleanup(func() {
		deleteTestNode(t, tcmNodeID1)
		deleteTestNode(t, tcmNodeID2)
	})
}

// 测试创建TCM节点
func TestCreateTCMNode(t *testing.T) {
	// 创建测试TCM节点数据
	tcmNodeData := map[string]interface{}{
		"name":          "测试创建TCM节点",
		"sub_type":      "HERB",
		"classification": "温热药",
		"properties": map[string]interface{}{
			"nature":     "温",
			"flavor":     "辛",
			"meridians":  []string{"肺", "脾"},
			"usage":      "用于祛风散寒",
			"common_name": "测试中药",
		},
	}

	// 将数据转换为JSON
	jsonData, err := json.Marshal(tcmNodeData)
	assert.NoError(t, err)

	// 发送POST请求
	resp, err := http.Post(fmt.Sprintf("%s/tcm/nodes", baseURL), "application/json", bytes.NewBuffer(jsonData))
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
	tcmNodeID := response["id"].(string)
	assert.Equal(t, "测试创建TCM节点", response["name"])
	assert.Equal(t, "HERB", response["sub_type"])
	assert.Equal(t, "温热药", response["classification"])

	// 清理：删除测试节点
	t.Cleanup(func() {
		deleteTestNode(t, tcmNodeID)
	})
}

// 测试更新TCM节点
func TestUpdateTCMNode(t *testing.T) {
	// 创建测试TCM节点
	tcmNodeID := createTestTCMNode(t, "HERB")

	// 更新数据
	updateData := map[string]interface{}{
		"name":          "更新后的TCM节点",
		"classification": "寒凉药",
		"properties": map[string]interface{}{
			"nature":     "寒",
			"flavor":     "苦",
			"meridians":  []string{"肝", "心"},
			"usage":      "清热解毒",
		},
	}

	// 将数据转换为JSON
	jsonData, err := json.Marshal(updateData)
	assert.NoError(t, err)

	// 创建PUT请求
	req, err := http.NewRequest(http.MethodPut, fmt.Sprintf("%s/tcm/nodes/%s", baseURL, tcmNodeID), bytes.NewBuffer(jsonData))
	assert.NoError(t, err)
	req.Header.Set("Content-Type", "application/json")

	// 发送请求
	client := &http.Client{}
	resp, err := client.Do(req)
	assert.NoError(t, err)
	assert.Equal(t, http.StatusOK, resp.StatusCode)
	resp.Body.Close()

	// 获取更新后的节点进行验证
	resp, err = http.Get(fmt.Sprintf("%s/tcm/nodes/%s", baseURL, tcmNodeID))
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
	assert.Equal(t, "更新后的TCM节点", response["name"])
	assert.Equal(t, "寒凉药", response["classification"])
	properties := response["properties"].(map[string]interface{})
	assert.Equal(t, "寒", properties["nature"])
	assert.Equal(t, "苦", properties["flavor"])

	// 清理：删除测试节点
	t.Cleanup(func() {
		deleteTestNode(t, tcmNodeID)
	})
}

// 测试获取所有TCM子类型
func TestGetAllTCMSubTypes(t *testing.T) {
	// 创建不同子类型的测试TCM节点，确保子类型存在
	tcmNodeID1 := createTestTCMNode(t, "HERB")
	tcmNodeID2 := createTestTCMNode(t, "FORMULA")

	// 发送GET请求
	resp, err := http.Get(fmt.Sprintf("%s/tcm/nodes/subtypes", baseURL))
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
	assert.NotNil(t, response["sub_types"])
	subTypes := response["sub_types"].([]interface{})
	assert.GreaterOrEqual(t, len(subTypes), 2)
	assert.Contains(t, subTypes, "HERB")
	assert.Contains(t, subTypes, "FORMULA")

	// 清理：删除测试节点
	t.Cleanup(func() {
		deleteTestNode(t, tcmNodeID1)
		deleteTestNode(t, tcmNodeID2)
	})
}

// 辅助函数：创建测试TCM节点
func createTestTCMNode(t *testing.T, subType string) string {
	// 创建节点数据
	tcmNodeData := map[string]interface{}{
		"name":       "测试TCM节点",
		"sub_type":    subType,
		"properties": map[string]interface{}{
			"test": true,
		},
	}

	// 将数据转换为JSON
	jsonData, err := json.Marshal(tcmNodeData)
	assert.NoError(t, err)

	// 发送POST请求
	resp, err := http.Post(fmt.Sprintf("%s/tcm/nodes", baseURL), "application/json", bytes.NewBuffer(jsonData))
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

// 辅助函数：创建具有特定分类的测试TCM节点
func createTestTCMNodeWithClassification(t *testing.T, subType string, classification string) string {
	// 创建节点数据
	tcmNodeData := map[string]interface{}{
		"name":          "测试TCM节点",
		"sub_type":       subType,
		"classification": classification,
		"properties": map[string]interface{}{
			"test": true,
		},
	}

	// 将数据转换为JSON
	jsonData, err := json.Marshal(tcmNodeData)
	assert.NoError(t, err)

	// 发送POST请求
	resp, err := http.Post(fmt.Sprintf("%s/tcm/nodes", baseURL), "application/json", bytes.NewBuffer(jsonData))
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

// 辅助函数：创建具有特定名称的测试TCM节点
func createTestTCMNodeWithName(t *testing.T, subType string, name string) string {
	// 创建节点数据
	tcmNodeData := map[string]interface{}{
		"name":       name,
		"sub_type":    subType,
		"properties": map[string]interface{}{
			"test": true,
		},
	}

	// 将数据转换为JSON
	jsonData, err := json.Marshal(tcmNodeData)
	assert.NoError(t, err)

	// 发送POST请求
	resp, err := http.Post(fmt.Sprintf("%s/tcm/nodes", baseURL), "application/json", bytes.NewBuffer(jsonData))
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