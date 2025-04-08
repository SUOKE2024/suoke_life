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
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
	"time"
)

const (
	defaultServiceURL    = "http://localhost:8080"
	defaultQuery         = "中医舌诊健康分析"
	defaultImagePath     = "assets/tongue_sample.jpg"
	defaultAudioPath     = "assets/audio_sample.mp3"
	defaultOutputDir     = "output"
	defaultMaxResults    = 5
	defaultRequestDomain = "TCM"
)

// 多模态搜索请求结构
type MultimodalSearchRequest struct {
	Query       string                 `json:"query"`
	UserID      string                 `json:"userId,omitempty"`
	Domain      string                 `json:"domain,omitempty"`
	MaxResults  int                    `json:"maxResults,omitempty"`
	UseCache    bool                   `json:"useCache,omitempty"`
	ImageData   string                 `json:"imageData,omitempty"`
	ImagePath   string                 `json:"imagePath,omitempty"`
	ImageType   string                 `json:"imageType,omitempty"`
	AudioData   string                 `json:"audioData,omitempty"`
	AudioPath   string                 `json:"audioPath,omitempty"`
	AudioType   string                 `json:"audioType,omitempty"`
	TCMOptions  map[string]interface{} `json:"tcmOptions,omitempty"`
	ExtraParams map[string]interface{} `json:"extraParams,omitempty"`
}

// 分析结果结构
type AnalysisResult struct {
	Status    string                   `json:"status"`
	Features  []string                 `json:"features,omitempty"`
	Metadata  map[string]interface{}   `json:"metadata,omitempty"`
	Results   []map[string]interface{} `json:"results,omitempty"`
	Error     string                   `json:"error,omitempty"`
	Stats     map[string]interface{}   `json:"stats,omitempty"`
	BodyType  string                   `json:"bodyType,omitempty"`
	Analysis  string                   `json:"analysis,omitempty"`
	Processed bool                     `json:"processed,omitempty"`
}

// 搜索结果结构
type SearchResponse struct {
	Status  string         `json:"status"`
	Results []SearchResult `json:"results"`
}

// 搜索结果项
type SearchResult struct {
	Content  string                 `json:"content"`
	Score    float64                `json:"score"`
	Metadata map[string]interface{} `json:"metadata,omitempty"`
}

// 健康检查响应
type HealthResponse struct {
	Status    string    `json:"status"`
	Service   string    `json:"service"`
	Version   string    `json:"version"`
	Timestamp time.Time `json:"time"`
}

// 服务URLs
var (
	serviceURL        = defaultServiceURL + "/api/search/multimodal"
	tongueAnalysisURL = defaultServiceURL + "/api/analyze/tongue"
	faceAnalysisURL   = defaultServiceURL + "/api/analyze/face"
	audioAnalysisURL  = defaultServiceURL + "/api/analyze/audio"
	healthCheckURL    = defaultServiceURL + "/health"
	basicSearchURL    = defaultServiceURL + "/api/search"
)

// 命令行参数
var (
	baseURL     string
	imageFile   string
	audioFile   string
	query       string
	imageType   string
	audioType   string
	domain      string
	outputFile  string
	maxResults  int
	useCache    bool
	verbose     bool
	outputDir   string
	singleTests bool
)

// 初始化命令行参数
func init() {
	flag.StringVar(&baseURL, "server", defaultServiceURL, "服务器基础URL")
	flag.StringVar(&imageFile, "image", defaultImagePath, "图像文件路径")
	flag.StringVar(&audioFile, "audio", defaultAudioPath, "音频文件路径")
	flag.StringVar(&query, "query", defaultQuery, "查询文本")
	flag.StringVar(&imageType, "image-type", "image/jpeg", "图像MIME类型")
	flag.StringVar(&audioType, "audio-type", "audio/mpeg", "音频MIME类型")
	flag.StringVar(&domain, "domain", defaultRequestDomain, "查询领域")
	flag.StringVar(&outputFile, "output", "", "输出JSON文件路径")
	flag.StringVar(&outputDir, "output-dir", defaultOutputDir, "输出目录")
	flag.IntVar(&maxResults, "max-results", defaultMaxResults, "最大结果数量")
	flag.BoolVar(&useCache, "use-cache", true, "使用缓存")
	flag.BoolVar(&verbose, "verbose", false, "详细输出")
	flag.BoolVar(&singleTests, "single-tests", true, "运行单独的测试")
}

// 彩色输出
const (
	colorReset  = "\033[0m"
	colorRed    = "\033[31m"
	colorGreen  = "\033[32m"
	colorYellow = "\033[33m"
	colorBlue   = "\033[34m"
)

// 日志函数
func logInfo(format string, args ...interface{}) {
	fmt.Printf("%s[INFO]%s %s\n", colorYellow, colorReset, fmt.Sprintf(format, args...))
}

func logSuccess(format string, args ...interface{}) {
	fmt.Printf("%s[SUCCESS]%s %s\n", colorGreen, colorReset, fmt.Sprintf(format, args...))
}

func logError(format string, args ...interface{}) {
	fmt.Printf("%s[ERROR]%s %s\n", colorRed, colorReset, fmt.Sprintf(format, args...))
}

func logTest(format string, args ...interface{}) {
	fmt.Printf("%s[TEST]%s %s\n", colorBlue, colorReset, fmt.Sprintf(format, args...))
}

// 主函数
func main() {
	flag.Parse()

	// 更新服务URL
	serviceURL = baseURL + "/api/search/multimodal"
	tongueAnalysisURL = baseURL + "/api/analyze/tongue"
	faceAnalysisURL = baseURL + "/api/analyze/face"
	audioAnalysisURL = baseURL + "/api/analyze/audio"
	healthCheckURL = baseURL + "/health"
	basicSearchURL = baseURL + "/api/search"

	// 创建输出目录
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		logError("创建输出目录失败: %v", err)
		return
	}

	// 检测至少需要一种模态
	if imageFile == "" && audioFile == "" && query == "" {
		logError("错误: 至少需要提供一种模态 (图像文件、音频文件或查询文本)")
		flag.Usage()
		return
	}

	fmt.Println("==========================================================")
	fmt.Println("      索克生活RAG服务多模态搜索测试 (Go版本)")
	fmt.Println("      服务器:", baseURL)
	fmt.Println("      查询:", query)
	fmt.Println("      图像:", imageFile)
	fmt.Println("      音频:", audioFile)
	fmt.Println("      输出目录:", outputDir)
	fmt.Println("==========================================================")

	// 运行健康检查
	if singleTests {
		testHealthCheck()
		testBasicSearch()
	}

	// 检查图像文件
	var imageBase64 string
	if imageFile != "" {
		if _, err := os.Stat(imageFile); os.IsNotExist(err) {
			logError("找不到图像文件: %s", imageFile)
		} else {
			// 读取图像文件并Base64编码
			imageBytes, err := ioutil.ReadFile(imageFile)
			if err != nil {
				logError("读取图像文件失败: %v", err)
			} else {
				imageBase64 = base64.StdEncoding.EncodeToString(imageBytes)
				logInfo("图像文件已读取并编码")

				// 单独测试舌诊分析
				if singleTests {
					testTongueAnalysis(imageBytes)
				}
			}
		}
	}

	// 检查音频文件
	var audioBase64 string
	if audioFile != "" {
		if _, err := os.Stat(audioFile); os.IsNotExist(err) {
			logError("找不到音频文件: %s", audioFile)
		} else {
			// 读取音频文件并Base64编码
			audioBytes, err := ioutil.ReadFile(audioFile)
			if err != nil {
				logError("读取音频文件失败: %v", err)
			} else {
				audioBase64 = base64.StdEncoding.EncodeToString(audioBytes)
				logInfo("音频文件已读取并编码")

				// 单独测试音频分析
				if singleTests {
					testAudioAnalysis(audioBytes)
				}
			}
		}
	}

	// 准备多模态搜索请求
	req := MultimodalSearchRequest{
		Query:      query,
		Domain:     domain,
		MaxResults: maxResults,
		UseCache:   useCache,
	}

	if imageBase64 != "" {
		req.ImageData = imageBase64
		req.ImageType = imageType
	}

	if audioBase64 != "" {
		req.AudioData = audioBase64
		req.AudioType = audioType
	}

	// 设置TCM特定选项
	req.TCMOptions = map[string]interface{}{
		"includeBodyTypes": true,
		"includeAnalysis":  true,
	}

	// 执行多模态搜索
	executeMultimodalSearch(req)
}

// 健康检查测试
func testHealthCheck() {
	logTest("测试健康检查...")

	resp, err := http.Get(healthCheckURL)
	if err != nil {
		logError("健康检查请求失败: %v", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		logError("健康检查失败，HTTP状态码: %d", resp.StatusCode)
		return
	}

	var result HealthResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		logError("解析健康检查响应失败: %v", err)
		return
	}

	if result.Status == "healthy" {
		logSuccess("健康检查通过")
		if verbose {
			printJSON(result)
		}
		// 保存结果
		saveJSON(result, filepath.Join(outputDir, "health_check_result.json"))
	} else {
		logError("健康检查失败，状态: %s", result.Status)
	}
}

// 基本搜索测试
func testBasicSearch() {
	logTest("测试基本搜索...")

	url := fmt.Sprintf("%s?q=%s", basicSearchURL, query)
	resp, err := http.Get(url)
	if err != nil {
		logError("基本搜索请求失败: %v", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		logError("基本搜索失败，HTTP状态码: %d", resp.StatusCode)
		return
	}

	var result SearchResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		logError("解析基本搜索响应失败: %v", err)
		return
	}

	if result.Status == "success" {
		logSuccess("基本搜索测试通过")
		if verbose {
			printJSON(result)
		}
		// 保存结果
		saveJSON(result, filepath.Join(outputDir, "basic_search_result.json"))
	} else {
		logError("基本搜索测试失败")
	}
}

// 舌诊分析测试
func testTongueAnalysis(imageBytes []byte) {
	logTest("测试舌诊分析...")

	// 创建multipart请求
	var requestBody bytes.Buffer
	writer := multipart.NewWriter(&requestBody)
	part, err := writer.CreateFormFile("image", filepath.Base(imageFile))
	if err != nil {
		logError("创建舌诊分析请求失败: %v", err)
		return
	}

	if _, err := io.Copy(part, bytes.NewReader(imageBytes)); err != nil {
		logError("写入图像数据失败: %v", err)
		return
	}
	writer.Close()

	// 发送请求
	req, err := http.NewRequest("POST", tongueAnalysisURL, &requestBody)
	if err != nil {
		logError("创建舌诊分析HTTP请求失败: %v", err)
		return
	}
	req.Header.Set("Content-Type", writer.FormDataContentType())

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		logError("舌诊分析请求失败: %v", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		logError("舌诊分析失败，HTTP状态码: %d", resp.StatusCode)
		return
	}

	var result AnalysisResult
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		logError("解析舌诊分析响应失败: %v", err)
		return
	}

	if result.Status == "success" {
		logSuccess("舌诊分析测试通过")
		logInfo("体质类型: %s", result.BodyType)
		if verbose {
			printJSON(result)
		}
		// 保存结果
		saveJSON(result, filepath.Join(outputDir, "tongue_analysis_result.json"))
	} else {
		logError("舌诊分析测试失败，状态: %s", result.Status)
	}
}

// 音频分析测试
func testAudioAnalysis(audioBytes []byte) {
	logTest("测试音频分析...")

	// 创建multipart请求
	var requestBody bytes.Buffer
	writer := multipart.NewWriter(&requestBody)
	part, err := writer.CreateFormFile("audio", filepath.Base(audioFile))
	if err != nil {
		logError("创建音频分析请求失败: %v", err)
		return
	}

	if _, err := io.Copy(part, bytes.NewReader(audioBytes)); err != nil {
		logError("写入音频数据失败: %v", err)
		return
	}
	writer.Close()

	// 发送请求
	req, err := http.NewRequest("POST", audioAnalysisURL, &requestBody)
	if err != nil {
		logError("创建音频分析HTTP请求失败: %v", err)
		return
	}
	req.Header.Set("Content-Type", writer.FormDataContentType())

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		logError("音频分析请求失败: %v", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		logError("音频分析失败，HTTP状态码: %d", resp.StatusCode)
		return
	}

	var result AnalysisResult
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		logError("解析音频分析响应失败: %v", err)
		return
	}

	if result.Status == "success" {
		logSuccess("音频分析测试通过")
		logInfo("体质类型: %s", result.BodyType)
		if verbose {
			printJSON(result)
		}
		// 保存结果
		saveJSON(result, filepath.Join(outputDir, "audio_analysis_result.json"))
	} else {
		logError("音频分析测试失败，状态: %s", result.Status)
	}
}

// 执行多模态搜索
func executeMultimodalSearch(req MultimodalSearchRequest) {
	logTest("测试多模态搜索...")

	// 转换为JSON
	reqBytes, err := json.Marshal(req)
	if err != nil {
		logError("生成多模态搜索请求失败: %v", err)
		return
	}

	if verbose {
		// 简化输出，避免显示大型base64数据
		reqCopy := req
		reqCopy.ImageData = "[图像数据省略]"
		reqCopy.AudioData = "[音频数据省略]"
		prettyJSON, _ := json.MarshalIndent(reqCopy, "", "  ")
		logInfo("多模态搜索请求: %s", string(prettyJSON))
	}

	// 发送请求
	resp, err := http.Post(serviceURL, "application/json", bytes.NewBuffer(reqBytes))
	if err != nil {
		logError("多模态搜索请求失败: %v", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		logError("多模态搜索失败，HTTP状态码: %d", resp.StatusCode)
		bodyBytes, _ := ioutil.ReadAll(resp.Body)
		logError("响应内容: %s", string(bodyBytes))
		return
	}

	var result SearchResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		logError("解析多模态搜索响应失败: %v", err)
		return
	}

	if result.Status == "success" {
		logSuccess("多模态搜索测试通过，找到 %d 个结果", len(result.Results))
		if verbose {
			printJSON(result)
		}
		
		// 保存结果
		outputPath := filepath.Join(outputDir, "multimodal_search_result.json")
		saveJSON(result, outputPath)
		logInfo("结果已保存到: %s", outputPath)
		
		// 如果指定了输出文件，额外保存一份
		if outputFile != "" {
			saveJSON(result, outputFile)
			logInfo("结果已保存到: %s", outputFile)
		}
	} else {
		logError("多模态搜索测试失败")
	}
}

// 打印JSON
func printJSON(v interface{}) {
	prettyJSON, err := json.MarshalIndent(v, "", "  ")
	if err != nil {
		log.Printf("JSON格式化失败: %v", err)
		return
	}
	fmt.Println(string(prettyJSON))
}

// 保存JSON
func saveJSON(v interface{}, filePath string) {
	prettyJSON, err := json.MarshalIndent(v, "", "  ")
	if err != nil {
		logError("JSON格式化失败: %v", err)
		return
	}

	// 确保目录存在
	dir := filepath.Dir(filePath)
	if err := os.MkdirAll(dir, 0755); err != nil {
		logError("创建目录失败: %v", err)
		return
	}

	if err := ioutil.WriteFile(filePath, prettyJSON, 0644); err != nil {
		logError("保存JSON文件失败: %v", err)
	}
} 