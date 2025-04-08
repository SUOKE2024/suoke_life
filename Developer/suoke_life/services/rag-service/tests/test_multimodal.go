package main

import (
	"bytes"
	"encoding/base64"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// 定义常量
const (
	serviceURL       = "http://localhost:8080/api/search/multimodal"
	tongueAnalysisURL = "http://localhost:8080/api/analyze/tongue"
	faceAnalysisURL   = "http://localhost:8080/api/analyze/face"
	audioAnalysisURL  = "http://localhost:8080/api/analyze/audio"
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

// 读取文件并转换为base64
func fileToBase64(filePath string) (string, error) {
	// 读取文件
	data, err := ioutil.ReadFile(filePath)
	if err != nil {
		return "", fmt.Errorf("读取文件失败: %v", err)
	}

	// 转换为base64
	encoded := base64.StdEncoding.EncodeToString(data)
	return encoded, nil
}

// 发送HTTP请求
func sendRequest(url string, data interface{}) ([]byte, error) {
	// 将数据转换为JSON
	jsonData, err := json.Marshal(data)
	if err != nil {
		return nil, fmt.Errorf("JSON编码失败: %v", err)
	}

	// 创建请求
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("创建请求失败: %v", err)
	}
	req.Header.Set("Content-Type", "application/json")

	// 发送请求
	client := &http.Client{Timeout: 30 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("发送请求失败: %v", err)
	}
	defer resp.Body.Close()

	// 读取响应
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("读取响应失败: %v", err)
	}

	// 检查状态码
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("请求失败，状态码: %d, 响应: %s", resp.StatusCode, body)
	}

	return body, nil
}

// 分析图像
func analyzeImage(imageData string, imageType string) (map[string]interface{}, error) {
	var url string
	if strings.Contains(strings.ToLower(imageType), "tongue") {
		url = tongueAnalysisURL
	} else if strings.Contains(strings.ToLower(imageType), "face") {
		url = faceAnalysisURL
	} else {
		return nil, fmt.Errorf("不支持的图像类型: %s", imageType)
	}

	// 构建请求数据
	reqData := map[string]string{
		"imageData": imageData,
	}

	// 发送请求
	resp, err := sendRequest(url, reqData)
	if err != nil {
		return nil, err
	}

	// 解析响应
	var result map[string]interface{}
	if err := json.Unmarshal(resp, &result); err != nil {
		return nil, fmt.Errorf("解析响应失败: %v", err)
	}

	return result, nil
}

// 分析音频
func analyzeAudio(audioData string, audioType string) (map[string]interface{}, error) {
	// 构建请求数据
	reqData := map[string]string{
		"audioData": audioData,
		"audioType": audioType,
	}

	// 发送请求
	resp, err := sendRequest(audioAnalysisURL, reqData)
	if err != nil {
		return nil, err
	}

	// 解析响应
	var result map[string]interface{}
	if err := json.Unmarshal(resp, &result); err != nil {
		return nil, fmt.Errorf("解析响应失败: %v", err)
	}

	return result, nil
}

// 执行多模态搜索
func multimodalSearch(req MultimodalSearchRequest) (*AnalysisResult, error) {
	// 发送请求
	resp, err := sendRequest(serviceURL, req)
	if err != nil {
		return nil, err
	}

	// 解析响应
	var result AnalysisResult
	if err := json.Unmarshal(resp, &result); err != nil {
		return nil, fmt.Errorf("解析响应失败: %v", err)
	}

	return &result, nil
}

// 打印搜索结果
func printSearchResults(result *AnalysisResult, verbose bool) {
	fmt.Println("=== 搜索结果 ===")
	fmt.Printf("处理时间: %d ms\n", result.ProcessTime)
	fmt.Printf("特征: %s\n", strings.Join(result.Features, ", "))
	fmt.Printf("结果数量: %d\n", len(result.Results))

	if verbose {
		fmt.Println("\n元数据:")
		metadataJSON, _ := json.MarshalIndent(result.Metadata, "", "  ")
		fmt.Println(string(metadataJSON))

		fmt.Println("\n统计信息:")
		statsJSON, _ := json.MarshalIndent(result.Stats, "", "  ")
		fmt.Println(string(statsJSON))
	}

	fmt.Println("\n搜索结果:")
	for i, item := range result.Results {
		fmt.Printf("\n--- 结果 #%d ---\n", i+1)
		fmt.Printf("来源: %s\n", item.Source)
		fmt.Printf("分数: %.2f\n", item.Score)
		fmt.Printf("内容: %s\n", item.Content)
		
		if verbose {
			fmt.Println("元数据:")
			itemMetadataJSON, _ := json.MarshalIndent(item.Metadata, "", "  ")
			fmt.Println(string(itemMetadataJSON))
		}
	}
}

// 保存结果到文件
func saveResultToFile(result *AnalysisResult, outputFile string) error {
	// 将结果转换为格式化的JSON
	resultJSON, err := json.MarshalIndent(result, "", "  ")
	if err != nil {
		return fmt.Errorf("JSON编码失败: %v", err)
	}

	// 创建目录（如果不存在）
	dir := filepath.Dir(outputFile)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return fmt.Errorf("创建目录失败: %v", err)
	}

	// 写入文件
	if err := ioutil.WriteFile(outputFile, resultJSON, 0644); err != nil {
		return fmt.Errorf("写入文件失败: %v", err)
	}

	fmt.Printf("结果已保存到: %s\n", outputFile)
	return nil
}

func main() {
	// 解析命令行参数
	var (
		imageFile  = flag.String("image", "", "图像文件路径")
		audioFile  = flag.String("audio", "", "音频文件路径")
		query      = flag.String("query", "", "搜索查询")
		imageType  = flag.String("image-type", "tongue", "图像类型: tongue, face")
		audioType  = flag.String("audio-type", "cough", "音频类型: cough, speech")
		domain     = flag.String("domain", "", "搜索域")
		outputFile = flag.String("output", "", "输出文件路径")
		maxResults = flag.Int("max-results", 5, "最大结果数量")
		verbose    = flag.Bool("verbose", false, "显示详细信息")
	)
	flag.Parse()

	// 检查是否至少提供了一种模态
	if *imageFile == "" && *audioFile == "" && *query == "" {
		log.Fatal("错误: 必须至少提供一种模态，例如图像文件、音频文件或文本查询")
	}

	// 处理图像
	var imageData string
	if *imageFile != "" {
		var err error
		imageData, err = fileToBase64(*imageFile)
		if err != nil {
			log.Fatalf("处理图像文件失败: %v", err)
		}

		fmt.Println("图像文件已加载")

		if *verbose {
			// 单独分析图像
			fmt.Println("单独分析图像...")
			imageAnalysis, err := analyzeImage(imageData, *imageType)
			if err != nil {
				log.Printf("警告: 图像分析失败: %v", err)
			} else {
				fmt.Println("图像分析结果:")
				imageAnalysisJSON, _ := json.MarshalIndent(imageAnalysis, "", "  ")
				fmt.Println(string(imageAnalysisJSON))
			}
		}
	}

	// 处理音频
	var audioData string
	if *audioFile != "" {
		var err error
		audioData, err = fileToBase64(*audioFile)
		if err != nil {
			log.Fatalf("处理音频文件失败: %v", err)
		}

		fmt.Println("音频文件已加载")

		if *verbose {
			// 单独分析音频
			fmt.Println("单独分析音频...")
			audioAnalysis, err := analyzeAudio(audioData, *audioType)
			if err != nil {
				log.Printf("警告: 音频分析失败: %v", err)
			} else {
				fmt.Println("音频分析结果:")
				audioAnalysisJSON, _ := json.MarshalIndent(audioAnalysis, "", "  ")
				fmt.Println(string(audioAnalysisJSON))
			}
		}
	}

	// 构建搜索请求
	req := MultimodalSearchRequest{
		Query:        *query,
		UserID:       "test-user",
		Domain:       *domain,
		MaxResults:   *maxResults,
		UseCache:     true,
		ImageData:    imageData,
		ImageType:    *imageType,
		AudioData:    audioData,
		AudioType:    *audioType,
		TCMOptions:   map[string]interface{}{"includeBodyType": true},
		ExtraOptions: map[string]interface{}{"debug": *verbose},
	}

	fmt.Println("执行多模态搜索...")
	start := time.Now()

	// 执行搜索
	result, err := multimodalSearch(req)
	if err != nil {
		log.Fatalf("搜索失败: %v", err)
	}

	fmt.Printf("搜索完成，耗时: %v\n\n", time.Since(start))

	// 打印结果
	printSearchResults(result, *verbose)

	// 保存结果到文件
	if *outputFile != "" {
		if err := saveResultToFile(result, *outputFile); err != nil {
			log.Fatalf("保存结果失败: %v", err)
		}
	}
} 