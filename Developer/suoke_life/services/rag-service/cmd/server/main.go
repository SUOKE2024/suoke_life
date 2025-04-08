package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// MultimodalSearchRequest 定义多模态搜索请求参数
type MultimodalSearchRequest struct {
	Query        string                 `json:"query"`
	UserID       string                 `json:"userId"`
	Domain       string                 `json:"domain"`
	MaxResults   int                    `json:"maxResults"`
	UseCache     bool                   `json:"useCache"`
	ImageData    string                 `json:"imageData"`
	ImagePath    string                 `json:"imagePath"`
	ImageType    string                 `json:"imageType"`
	AudioData    string                 `json:"audioData"`
	AudioPath    string                 `json:"audioPath"`
	AudioType    string                 `json:"audioType"`
	TCMOptions   map[string]interface{} `json:"tcmOptions"`
	ExtraOptions map[string]interface{} `json:"extraOptions"`
}

// AnalysisResult 定义分析结果
type AnalysisResult struct {
	Success     bool                   `json:"success"`
	Features    []string               `json:"features"`
	Metadata    map[string]interface{} `json:"metadata"`
	Results     []SearchResult         `json:"results"`
	Error       string                 `json:"error,omitempty"`
	Stats       map[string]interface{} `json:"stats,omitempty"`
	ProcessTime int64                  `json:"processTime"`
}

// SearchResult 定义搜索结果项
type SearchResult struct {
	ID       string                 `json:"id"`
	Content  string                 `json:"content"`
	Source   string                 `json:"source"`
	Score    float64                `json:"score"`
	Metadata map[string]interface{} `json:"metadata"`
}

// createDirIfNotExist 创建目录（如果不存在）
func createDirIfNotExist(dir string) error {
	if _, err := os.Stat(dir); os.IsNotExist(err) {
		return os.MkdirAll(dir, 0755)
	}
	return nil
}

// setupLogger 设置日志记录器
func setupLogger() *log.Logger {
	logDir := "logs"
	err := createDirIfNotExist(logDir)
	if err != nil {
		log.Fatalf("无法创建日志目录: %v", err)
	}

	// 创建日志文件，以日期命名
	logFile := filepath.Join(logDir, fmt.Sprintf("rag-service-%s.log", time.Now().Format("2006-01-02")))
	file, err := os.OpenFile(logFile, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
	if err != nil {
		log.Fatalf("无法创建日志文件: %v", err)
	}

	// 设置日志输出到文件和控制台
	logger := log.New(file, "", log.LstdFlags)
	logger.SetOutput(os.Stdout)

	return logger
}

// writeJSONResponse 将JSON响应写入HTTP响应
func writeJSONResponse(w http.ResponseWriter, statusCode int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	json.NewEncoder(w).Encode(data)
}

// handleMultimodalSearch 处理多模态搜索请求
func handleMultimodalSearch(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		writeJSONResponse(w, http.StatusMethodNotAllowed, map[string]string{
			"error": "仅支持POST方法",
		})
		return
	}

	var req MultimodalSearchRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeJSONResponse(w, http.StatusBadRequest, map[string]string{
			"error": fmt.Sprintf("无法解析请求体: %v", err),
		})
		return
	}

	// 记录请求信息
	log.Printf("收到多模态搜索请求: 查询=%s, 域=%s, 最大结果数=%d",
		req.Query, req.Domain, req.MaxResults)

	// 处理时间
	start := time.Now()
	time.Sleep(500 * time.Millisecond) // 模拟处理时间

	// 模拟搜索结果
	results := []SearchResult{
		{
			ID:      "1",
			Content: "春季是发生感冒的常见季节，保持良好的个人卫生和规律作息有助于预防。",
			Source:  "中医基础知识库",
			Score:   0.95,
			Metadata: map[string]interface{}{
				"category": "预防保健",
				"keywords": []string{"感冒", "预防", "个人卫生"},
			},
		},
		{
			ID:      "2",
			Content: "感冒初期可饮用姜汤，有发汗解表之功效，有助于排出体内风寒。",
			Source:  "中医治疗方案",
			Score:   0.87,
			Metadata: map[string]interface{}{
				"category": "治疗方案",
				"keywords": []string{"感冒", "姜汤", "发汗解表"},
			},
		},
	}

	// 判断是否提供了图像数据
	if req.ImageData != "" || req.ImagePath != "" {
		results = append(results, SearchResult{
			ID:      "3",
			Content: "从舌象图像分析，您的舌质偏红，苔薄白，提示有风热感冒的征象。建议清热解表，可服用银翘散等方剂。",
			Source:  "四诊辨证系统-舌诊",
			Score:   0.92,
			Metadata: map[string]interface{}{
				"category": "诊断",
				"keywords": []string{"舌诊", "风热感冒", "苔薄白"},
			},
		})
	}

	// 判断是否提供了音频数据
	if req.AudioData != "" || req.AudioPath != "" {
		results = append(results, SearchResult{
			ID:      "4",
			Content: "从咳嗽声音分析，属于干咳，提示风热犯肺。建议多饮水，可选用杏仁、梨等食材煮水饮用。",
			Source:  "四诊辨证系统-声诊",
			Score:   0.89,
			Metadata: map[string]interface{}{
				"category": "诊断",
				"keywords": []string{"声诊", "干咳", "风热犯肺"},
			},
		})
	}

	// 判断请求是否包含中医选项
	if req.TCMOptions != nil && len(req.TCMOptions) > 0 {
		results = append(results, SearchResult{
			ID:      "5",
			Content: "基于体质分析，您属于阳虚体质，更易感受风寒。平时宜温补阳气，可食用羊肉、韭菜等温阳食物，避免生冷食物。",
			Source:  "中医体质辨识",
			Score:   0.85,
			Metadata: map[string]interface{}{
				"category": "体质分析",
				"keywords": []string{"阳虚体质", "温补阳气", "饮食调理"},
			},
		})
	}

	// 根据请求域过滤结果
	if req.Domain != "" && req.Domain != "all" {
		filteredResults := []SearchResult{}
		for _, result := range results {
			if category, ok := result.Metadata["category"].(string); ok {
				if strings.EqualFold(category, req.Domain) {
					filteredResults = append(filteredResults, result)
				}
			}
		}
		results = filteredResults
	}

	// 限制返回结果数量
	if req.MaxResults > 0 && len(results) > req.MaxResults {
		results = results[:req.MaxResults]
	}

	// 创建响应
	response := AnalysisResult{
		Success:  true,
		Features: []string{"文本分析", "知识图谱检索"},
		Metadata: map[string]interface{}{
			"domain":     req.Domain,
			"queryTime":  time.Now().Format(time.RFC3339),
			"resultSize": len(results),
		},
		Results:     results,
		ProcessTime: time.Since(start).Milliseconds(),
		Stats: map[string]interface{}{
			"tokens": 156,
			"sources": map[string]int{
				"中医基础知识库": 1,
				"中医治疗方案":  1,
			},
		},
	}

	// 如果有图像数据，添加图像分析特征
	if req.ImageData != "" || req.ImagePath != "" {
		response.Features = append(response.Features, "图像分析")
		response.Stats["imageAnalysis"] = true
	}

	// 如果有音频数据，添加音频分析特征
	if req.AudioData != "" || req.AudioPath != "" {
		response.Features = append(response.Features, "声音分析")
		response.Stats["audioAnalysis"] = true
	}

	writeJSONResponse(w, http.StatusOK, response)
}

// handleTongueAnalysis 处理舌诊分析请求
func handleTongueAnalysis(w http.ResponseWriter, r *http.Request) {
	time.Sleep(200 * time.Millisecond) // 模拟处理时间
	writeJSONResponse(w, http.StatusOK, map[string]interface{}{
		"success": true,
		"analysis": map[string]interface{}{
			"tongueColor": "淡红",
			"coatingColor": "薄白",
			"coatingThickness": "薄",
			"moisture": "适中",
			"shape": "正常",
		},
		"interpretation": "舌质淡红，苔薄白，属正常舌象，提示身体基本健康。",
		"suggestions": []string{
			"保持良好生活习惯",
			"避免过度劳累",
			"注意饮食均衡",
		},
	})
}

// handleFaceAnalysis 处理面诊分析请求
func handleFaceAnalysis(w http.ResponseWriter, r *http.Request) {
	time.Sleep(200 * time.Millisecond) // 模拟处理时间
	writeJSONResponse(w, http.StatusOK, map[string]interface{}{
		"success": true,
		"analysis": map[string]interface{}{
			"complexion": "偏白",
			"facialFeatures": map[string]string{
				"eyes": "明亮",
				"lips": "淡红",
				"cheeks": "略苍白",
			},
		},
		"interpretation": "面色偏白，提示可能有阳虚或气血不足的倾向。",
		"suggestions": []string{
			"适当进行户外活动，增加阳气",
			"可食用黑豆、黑芝麻等黑色食物补肾",
			"保证充足睡眠",
		},
	})
}

// handleAudioAnalysis 处理声音分析请求
func handleAudioAnalysis(w http.ResponseWriter, r *http.Request) {
	time.Sleep(200 * time.Millisecond) // 模拟处理时间
	writeJSONResponse(w, http.StatusOK, map[string]interface{}{
		"success": true,
		"analysis": map[string]interface{}{
			"voiceType": "偏弱",
			"rhythm": "均匀",
			"pitch": "中等",
			"soundFeatures": map[string]string{
				"cough": "干咳",
				"breathing": "轻度急促",
			},
		},
		"interpretation": "声音偏弱，呼吸稍急促，干咳，提示有风热犯肺的迹象。",
		"suggestions": []string{
			"注意保暖，避免受风",
			"多饮水，可饮用梨水、杏仁水等",
			"适当休息，避免劳累",
		},
	})
}

// handleHealthCheck 处理健康检查请求
func handleHealthCheck(w http.ResponseWriter, r *http.Request) {
	writeJSONResponse(w, http.StatusOK, map[string]string{
		"status":  "healthy",
		"version": "1.0.0",
		"time":    time.Now().Format(time.RFC3339),
	})
}

func main() {
	// 设置日志
	logger := setupLogger()
	logger.Println("启动索克生活RAG服务...")

	// 创建必要的目录
	for _, dir := range []string{"data", "logs", "config"} {
		if err := createDirIfNotExist(dir); err != nil {
			logger.Fatalf("无法创建目录 %s: %v", dir, err)
		}
	}

	// 注册路由处理函数
	http.HandleFunc("/api/search/multimodal", handleMultimodalSearch)
	http.HandleFunc("/api/analyze/tongue", handleTongueAnalysis)
	http.HandleFunc("/api/analyze/face", handleFaceAnalysis)
	http.HandleFunc("/api/analyze/audio", handleAudioAnalysis)
	http.HandleFunc("/health", handleHealthCheck)
	http.HandleFunc("/", handleHealthCheck)

	// 设置服务器
	port := "8080"
	if envPort := os.Getenv("PORT"); envPort != "" {
		port = envPort
	}

	// 启动服务器
	logger.Printf("服务器启动在端口 %s...\n", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		logger.Fatalf("服务器启动失败: %v", err)
	}
} 