package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"
)

// 健康检查响应
type HealthResponse struct {
	Status    string    `json:"status"`
	Service   string    `json:"service"`
	Version   string    `json:"version"`
	Timestamp time.Time `json:"time"`
}

// 搜索响应
type SearchResponse struct {
	Status  string         `json:"status"`
	Results []SearchResult `json:"results"`
}

// 搜索结果
type SearchResult struct {
	Content  string                 `json:"content"`
	Score    float64                `json:"score"`
	Metadata map[string]interface{} `json:"metadata,omitempty"`
}

func main() {
	port := "8080"
	if envPort := os.Getenv("PORT"); envPort != "" {
		port = envPort
	}

	// 健康检查端点
	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		response := HealthResponse{
			Status:    "healthy",
			Service:   "rag-minimal",
			Version:   "1.0.0",
			Timestamp: time.Now(),
		}
		
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	})

	// 简单查询端点
	http.HandleFunc("/api/search", func(w http.ResponseWriter, r *http.Request) {
		query := r.URL.Query().Get("q")
		if query == "" {
			query = "未提供查询"
		}
		
		response := SearchResponse{
			Status: "success",
			Results: []SearchResult{
				{
					Content: fmt.Sprintf("索克健康问答: %s", query),
					Score:   1.0,
					Metadata: map[string]interface{}{
						"source": "最小服务响应",
						"type":   "text",
					},
				},
			},
		}
		
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	})

	// 多模态查询端点
	http.HandleFunc("/api/search/multimodal", func(w http.ResponseWriter, r *http.Request) {
		// 仅支持POST
		if r.Method != http.MethodPost {
			http.Error(w, "仅支持POST请求", http.StatusMethodNotAllowed)
			return
		}
		
		response := SearchResponse{
			Status: "success",
			Results: []SearchResult{
				{
					Content: "这是一个多模态测试响应",
					Score:   1.0,
					Metadata: map[string]interface{}{
						"source":    "最小服务响应",
						"type":      "multimodal",
						"processed": true,
					},
				},
			},
		}
		
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)
	})

	// 舌诊分析端点
	http.HandleFunc("/api/analyze/tongue", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "仅支持POST请求", http.StatusMethodNotAllowed)
			return
		}
		
		result := map[string]interface{}{
			"status":   "success",
			"features": []string{"淡红舌", "薄白苔"},
			"analysis": "舌质淡红，苔薄白，提示气血调和，身体状态良好。",
			"bodyType": "平和质",
		}
		
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(result)
	})

	// 面诊分析端点
	http.HandleFunc("/api/analyze/face", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "仅支持POST请求", http.StatusMethodNotAllowed)
			return
		}
		
		result := map[string]interface{}{
			"status":   "success",
			"features": []string{"面色红润", "气色良好"},
			"analysis": "面色红润，精神饱满，提示气血充盈。",
			"bodyType": "阳热质",
		}
		
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(result)
	})

	// 音频分析端点
	http.HandleFunc("/api/analyze/audio", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "仅支持POST请求", http.StatusMethodNotAllowed)
			return
		}
		
		result := map[string]interface{}{
			"status":   "success",
			"features": []string{"声音洪亮", "语速适中"},
			"analysis": "声音洪亮有力，语速适中，提示肺气充足。",
			"bodyType": "气虚质",
		}
		
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(result)
	})

	log.Printf("索克生活RAG服务(最小版本)启动在端口 %s...\n", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatalf("服务启动失败: %v", err)
	}
} 