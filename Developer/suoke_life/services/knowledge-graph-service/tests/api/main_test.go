package api

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"testing"
	"time"
)

const (
	// API服务的基础URL，可以通过环境变量配置
	baseURL = "http://localhost:8080/api/v1"
)

// TestMain 在所有测试之前运行，用于测试准备和清理
func TestMain(m *testing.M) {
	// 检查API服务是否在运行
	if !isAPIServiceRunning() {
		log.Printf("警告: API服务似乎未运行在 %s，测试可能会失败", baseURL)
		log.Println("请确保知识图谱服务已启动，然后再运行测试")
		log.Println("启动服务的命令: cd ../../cmd/server && go run main.go")
		// 不立即退出，让测试继续尝试运行，以便显示具体错误
	}

	// 运行测试套件
	exitCode := m.Run()

	// 如果需要，这里可以添加测试后的清理代码
	
	// 退出测试
	os.Exit(exitCode)
}

// 检查API服务是否在运行
func isAPIServiceRunning() bool {
	client := &http.Client{
		Timeout: 3 * time.Second,
	}
	resp, err := client.Get(fmt.Sprintf("%s/health", baseURL))
	if err != nil {
		return false
	}
	defer resp.Body.Close()
	return resp.StatusCode == http.StatusOK
}

// 辅助函数：创建测试节点
func createTestNode(t *testing.T) string {
	// 创建随机节点名称
	nodeName := fmt.Sprintf("测试节点_%d", time.Now().UnixNano())
	
	// 创建节点数据
	nodeData := map[string]interface{}{
		"name":       nodeName,
		"category":   "TEST",
		"properties": map[string]interface{}{
			"created_for_test": true,
			"test_time":        time.Now().Format(time.RFC3339),
		},
	}

	// 将数据转换为JSON
	jsonData, err := json.Marshal(nodeData)
	if err != nil {
		t.Fatalf("转换节点数据为JSON失败: %v", err)
	}

	// 发送POST请求
	resp, err := http.Post(fmt.Sprintf("%s/nodes", baseURL), "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		t.Fatalf("创建测试节点失败: %v", err)
	}

	// 解析响应
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		t.Fatalf("读取响应失败: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusCreated {
		t.Fatalf("创建节点返回状态码: %d, 响应: %s", resp.StatusCode, string(body))
	}

	var response map[string]interface{}
	if err := json.Unmarshal(body, &response); err != nil {
		t.Fatalf("解析响应JSON失败: %v", err)
	}

	// 返回创建的节点ID
	nodeID, ok := response["id"].(string)
	if !ok {
		t.Fatalf("响应中未包含有效的节点ID")
	}
	return nodeID
}

// 辅助函数：删除测试节点
func deleteTestNode(t *testing.T, nodeID string) {
	// 创建DELETE请求
	req, err := http.NewRequest(http.MethodDelete, fmt.Sprintf("%s/nodes/%s", baseURL, nodeID), nil)
	if err != nil {
		t.Logf("创建删除请求失败: %v", err)
		return
	}

	// 发送请求
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		t.Logf("删除节点失败: %v", err)
		return
	}
	defer resp.Body.Close()

	// 如果状态码不是200，记录但不失败
	if resp.StatusCode != http.StatusOK {
		t.Logf("删除节点失败，状态码: %d", resp.StatusCode)
	}
} 