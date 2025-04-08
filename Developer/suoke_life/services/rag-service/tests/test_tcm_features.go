package main

import (
	"bytes"
	"encoding/base64"
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// AnalysisRequest 定义分析请求结构
type AnalysisRequest struct {
	FeatureType string            `json:"feature_type"`
	UserID      string            `json:"user_id,omitempty"`
	InputData   string            `json:"input_data,omitempty"`
	InputPath   string            `json:"input_path,omitempty"`
	Options     map[string]bool   `json:"options,omitempty"`
	Extra       map[string]interface{} `json:"extra,omitempty"`
}

// AnalysisResponse 定义分析响应结构
type AnalysisResponse struct {
	Status    string                 `json:"status"`
	Features  map[string]interface{} `json:"features,omitempty"`
	Metadata  map[string]interface{} `json:"metadata,omitempty"`
	Error     string                 `json:"error,omitempty"`
}

// 批量测试配置
type TCMTestCase struct {
	Name        string
	FeatureType string
	InputFile   string
	Options     map[string]bool
}

// 定义批量测试案例
var tcmTestCases = []TCMTestCase{
	{
		Name:        "舌诊分析",
		FeatureType: "tongue",
		InputFile:   "./test_data/images/tongue_sample.jpg",
		Options: map[string]bool{
			"detailed": true,
		},
	},
	{
		Name:        "面诊分析",
		FeatureType: "face",
		InputFile:   "./test_data/images/face_sample.jpg",
		Options: map[string]bool{
			"detailed": true,
		},
	},
	{
		Name:        "脉诊分析",
		FeatureType: "pulse",
		InputFile:   "./test_data/audio/pulse_sample.mp3",
		Options: map[string]bool{
			"detailed": true,
		},
	},
	{
		Name:        "声音分析",
		FeatureType: "voice",
		InputFile:   "./test_data/audio/voice_sample.mp3",
		Options: map[string]bool{
			"detailed": true,
		},
	},
	{
		Name:        "体质辨识",
		FeatureType: "constitution",
		InputFile:   "",
		Options: map[string]bool{
			"detailed": true,
		},
	},
}

// 在全局变量部分添加mockMode
var mockMode bool

// 在sendAnalysisRequest函数中添加mock模式
func sendAnalysisRequest(url string, req AnalysisRequest, verbose bool) (AnalysisResponse, error) {
	// 如果是模拟模式，返回模拟数据
	if mockMode {
		return generateMockResponse(req)
	}
	
	jsonData, err := json.Marshal(req)
	if err != nil {
		return AnalysisResponse{}, fmt.Errorf("JSON编码错误: %v", err)
	}
	
	if verbose {
		fmt.Printf("发送请求到: %s\n", url)
		fmt.Printf("请求数据: %s\n", string(jsonData))
	}
	
	// 发送HTTP请求
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return AnalysisResponse{}, fmt.Errorf("HTTP请求错误: %v", err)
	}
	defer resp.Body.Close()
	
	// 读取响应
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return AnalysisResponse{}, fmt.Errorf("读取响应错误: %v", err)
	}
	
	if verbose {
		fmt.Printf("响应状态码: %d\n", resp.StatusCode)
		fmt.Printf("响应数据: %s\n", string(body))
	}
	
	// 解析响应
	var result AnalysisResponse
	if err := json.Unmarshal(body, &result); err != nil {
		return AnalysisResponse{}, fmt.Errorf("JSON解析错误: %v", err)
	}
	
	return result, nil
}

// 添加生成模拟响应函数
func generateMockResponse(req AnalysisRequest) (AnalysisResponse, error) {
	response := AnalysisResponse{
		Status: "success",
		Features: map[string]interface{}{
			"analyzed_at": time.Now().Format(time.RFC3339),
			"model":       "suoke-tcm-v2.0",
		},
		Metadata: map[string]interface{}{
			"mode":         "simulation",
			"feature_type": req.FeatureType,
			"options":      req.Options,
		},
	}
	
	// 根据特征类型生成不同的模拟数据
	switch req.FeatureType {
	case "tongue":
		response.Features["tongue_analysis"] = map[string]interface{}{
			"color":    "淡红舌",
			"coating":  "薄白苔",
			"shape":    "正常",
			"moisture": 0.75,
			"cracks": []map[string]interface{}{
				{"position": "center", "size": "小", "depth": "浅"},
			},
			"diagnosis": map[string]string{
				"primary":   "气虚",
				"secondary": "阴虚",
			},
		}
	case "face":
		response.Features["face_analysis"] = map[string]interface{}{
			"color":      "偏黄",
			"complexion": "较暗淡",
			"forehead":   "色暗",
			"cheeks":     "色黄",
			"chin":       "色淡",
			"diagnosis": map[string]string{
				"primary":   "脾虚湿困",
				"secondary": "肝郁",
			},
		}
	case "pulse":
		response.Features["pulse_analysis"] = map[string]interface{}{
			"type":        "弦脉",
			"rate":        78,
			"rhythm":      "规律",
			"strength":    "中等",
			"regularity":  0.9,
			"left_cun":    "弦",
			"left_guan":   "弦细",
			"left_chi":    "细弱",
			"right_cun":   "弦",
			"right_guan":  "弦",
			"right_chi":   "细弱",
			"diagnosis": map[string]string{
				"primary":   "肝郁气滞",
				"secondary": "气血亏虚",
			},
		}
	case "voice":
		response.Features["voice_analysis"] = map[string]interface{}{
			"tone":        "中等",
			"volume":      "偏弱",
			"clarity":     0.8,
			"tremor":      0.2,
			"pitch":       "偏高",
			"speech_rate": "正常",
			"diagnosis": map[string]string{
				"primary":   "肺气不足",
				"secondary": "心神不宁",
			},
		}
	case "constitution":
		response.Features["constitution_analysis"] = map[string]interface{}{
			"primary_type": "气虚质",
			"secondary_type": "阴虚质",
			"scores": map[string]float64{
				"气虚质": 0.75,
				"阴虚质": 0.65,
				"阳虚质": 0.42,
				"痰湿质": 0.38,
				"湿热质": 0.32,
				"血瘀质": 0.28,
				"气郁质": 0.25,
				"特禀质": 0.18,
				"平和质": 0.35,
			},
			"characteristics": []string{
				"易疲劳",
				"气短",
				"自汗",
				"舌淡",
				"脉弱",
			},
			"recommendations": []string{
				"饮食宜温补脾肺",
				"适当运动，避免过度疲劳",
				"情志调养，保持心情舒畅",
				"推荐食疗：人参、黄芪、白术、大枣",
			},
		}
	default:
		response.Status = "error"
		response.Error = "不支持的特征类型"
	}
	
	return response, nil
}

// 运行批量测试
func runBatchTests(serviceURLBase string, outputFile string, verbose bool) {
	fmt.Println("=== 开始批量TCM特征测试 ===")
	
	results := []map[string]interface{}{}
	
	for i, testCase := range tcmTestCases {
		fmt.Printf("[%d/%d] 测试: %s\n", i+1, len(tcmTestCases), testCase.Name)
		
		// 构建请求
		req := AnalysisRequest{
			FeatureType: testCase.FeatureType,
			UserID:      "test_user",
			Options:     testCase.Options,
			Extra: map[string]interface{}{
				"test_mode": true,
				"test_case": testCase.Name,
			},
		}
		
		// 读取输入文件（如果有）
		if testCase.InputFile != "" {
			if _, err := os.Stat(testCase.InputFile); os.IsNotExist(err) {
				fmt.Printf("  警告: 输入文件不存在: %s, 将继续测试\n", testCase.InputFile)
			} else if !mockMode { // 只在非模拟模式下实际读取文件
				data, err := ioutil.ReadFile(testCase.InputFile)
				if err != nil {
					fmt.Printf("  错误: 无法读取输入文件: %v\n", err)
				} else {
					req.InputData = base64.StdEncoding.EncodeToString(data)
					fmt.Printf("  已加载输入文件: %s (%d 字节)\n", testCase.InputFile, len(data))
				}
			} else {
				fmt.Printf("  模拟模式: 跳过读取输入文件\n")
			}
		}
		
		// 获取服务URL
		serviceURL := fmt.Sprintf("%s/api/analyze/%s", serviceURLBase, testCase.FeatureType)
		if serviceURLBase == "" {
			serviceURL = fmt.Sprintf("http://localhost:8080/api/analyze/%s", testCase.FeatureType)
		}
		
		// 发送请求
		var result AnalysisResponse
		var err error
		
		// 根据模式选择操作
		if mockMode {
			fmt.Printf("  使用模拟模式生成%s分析结果\n", testCase.FeatureType)
			result, err = generateMockResponse(req)
		} else {
			// 发送分析请求
			fmt.Printf("  发送%s分析请求到服务\n", testCase.FeatureType)
			result, err = sendAnalysisRequest(serviceURL, req, verbose)
		}
		
		if err != nil {
			fmt.Printf("  错误: %v\n", err)
			// 测试失败，但继续测试其他案例
			testResult := map[string]interface{}{
				"test_case": testCase,
				"result": map[string]interface{}{
					"status": "error",
					"error":  err.Error(),
				},
				"timestamp": time.Now().Format(time.RFC3339),
			}
			results = append(results, testResult)
		} else {
			// 保存测试结果
			testResult := map[string]interface{}{
				"test_case": testCase,
				"result":    result,
				"timestamp": time.Now().Format(time.RFC3339),
			}
			results = append(results, testResult)
			
			// 打印简要结果
			fmt.Printf("  分析状态: %v\n", result.Status)
			if result.Status == "success" {
				fmt.Printf("  特征数量: %d\n", len(result.Features))
			} else {
				fmt.Printf("  错误: %s\n", result.Error)
			}
		}
		
		fmt.Println()
	}
	
	// 保存结果到文件
	if outputFile != "" {
		data, err := json.MarshalIndent(results, "", "  ")
		if err != nil {
			fmt.Printf("错误: 无法序列化结果: %v\n", err)
		} else {
			// 确保目录存在
			dir := filepath.Dir(outputFile)
			if err := os.MkdirAll(dir, 0755); err != nil {
				fmt.Printf("错误: 无法创建目录: %v\n", err)
			} else {
				err = ioutil.WriteFile(outputFile, data, 0644)
				if err != nil {
					fmt.Printf("错误: 无法保存结果到文件: %v\n", err)
				} else {
					fmt.Printf("结果已保存到: %s\n", outputFile)
				}
			}
		}
	}
	
	fmt.Println("=== 批量测试完成 ===")
}

func main() {
	// 命令行参数
	featureTypeFlag := flag.String("type", "", "特征类型 (tongue, face, pulse, voice, constitution)")
	inputFileFlag := flag.String("input", "", "输入文件路径")
	outputFileFlag := flag.String("output", "", "输出结果到文件")
	serviceURLFlag := flag.String("url", "", "服务地址")
	verboseFlag := flag.Bool("verbose", false, "详细输出")
	mockFlag := flag.Bool("mock", false, "使用模拟数据")
	batchFlag := flag.Bool("batch", false, "批量测试模式")
	
	flag.Parse()
	
	// 设置全局模拟模式
	mockMode = *mockFlag
	
	// 检查必要参数
	if *batchFlag {
		runBatchTests(*serviceURLFlag, *outputFileFlag, *verboseFlag)
		return
	}
	
	if *featureTypeFlag == "" {
		fmt.Println("错误: 必须指定特征类型")
		flag.Usage()
		os.Exit(1)
	}
	
	// 验证特征类型
	validTypes := map[string]bool{"tongue": true, "face": true, "pulse": true, "voice": true, "constitution": true}
	if !validTypes[*featureTypeFlag] {
		fmt.Printf("错误: 不支持的特征类型: %s\n", *featureTypeFlag)
		fmt.Println("支持的类型: tongue, face, pulse, voice, constitution")
		os.Exit(1)
	}
	
	// 准备请求
	req := AnalysisRequest{
		FeatureType: *featureTypeFlag,
		UserID:      "test_user",
		Options: map[string]bool{
			"detailed": true,
			"test_mode": true,
		},
	}
	
	// 如果提供了输入文件，读取并处理
	if *inputFileFlag != "" {
		// 检查文件是否存在
		if _, err := os.Stat(*inputFileFlag); os.IsNotExist(err) {
			fmt.Printf("错误: 输入文件不存在: %s\n", *inputFileFlag)
			os.Exit(1)
		}
		
		// 根据文件类型处理
		if strings.HasSuffix(strings.ToLower(*inputFileFlag), ".json") {
			// 读取JSON文件作为请求配置
			data, err := ioutil.ReadFile(*inputFileFlag)
			if err != nil {
				fmt.Printf("错误: 读取文件失败: %v\n", err)
				os.Exit(1)
			}
			
			if err := json.Unmarshal(data, &req); err != nil {
				fmt.Printf("错误: JSON解析失败: %v\n", err)
				os.Exit(1)
			}
			
			if *verboseFlag {
				fmt.Printf("从JSON加载请求配置: %+v\n", req)
			}
		} else {
			// 假设是图像或音频文件，读取并Base64编码
			data, err := ioutil.ReadFile(*inputFileFlag)
			if err != nil {
				fmt.Printf("错误: 读取文件失败: %v\n", err)
				os.Exit(1)
			}
			
			req.InputData = base64.StdEncoding.EncodeToString(data)
			if *verboseFlag {
				fmt.Printf("已加载输入文件: %s (%d字节)\n", *inputFileFlag, len(data))
			}
		}
	}
	
	// 获取服务URL
	var serviceURL string
	if *serviceURLFlag != "" {
		serviceURL = *serviceURLFlag
	} else {
		serviceURL = fmt.Sprintf("http://localhost:8080/api/analyze/%s", *featureTypeFlag)
	}
	
	// 发送请求
	var result AnalysisResponse
	var err error
	
	// 根据模式选择操作
	if mockMode {
		fmt.Println("使用模拟模式...")
		result, err = generateMockResponse(req)
	} else {
		// 发送分析请求
		fmt.Printf("发送%s分析请求...\n", *featureTypeFlag)
		result, err = sendAnalysisRequest(serviceURL, req, *verboseFlag)
	}
	
	if err != nil {
		fmt.Printf("错误: %v\n", err)
		os.Exit(1)
	}
	
	// 输出结果
	if result.Status == "success" {
		fmt.Println("\n分析成功!")
		
		// 输出特征
		fmt.Println("\n特征:")
		for k, v := range result.Features {
			fmt.Printf("  %s: %v\n", k, v)
		}
		
		// 输出元数据（如果在详细模式下）
		if *verboseFlag && len(result.Metadata) > 0 {
			fmt.Println("\n元数据:")
			for k, v := range result.Metadata {
				fmt.Printf("  %s: %v\n", k, v)
			}
		}
	} else {
		fmt.Printf("分析失败: %s\n", result.Error)
	}
	
	// 保存结果到文件（如果指定）
	if *outputFileFlag != "" {
		// 创建目录（如果不存在）
		dir := filepath.Dir(*outputFileFlag)
		if err := os.MkdirAll(dir, 0755); err != nil {
			fmt.Printf("错误: 创建目录失败: %v\n", err)
			return
		}
		
		// 格式化JSON输出
		data, err := json.MarshalIndent(result, "", "  ")
		if err != nil {
			fmt.Printf("错误: JSON序列化失败: %v\n", err)
			return
		}
		
		// 写入文件
		if err := ioutil.WriteFile(*outputFileFlag, data, 0644); err != nil {
			fmt.Printf("错误: 写入文件失败: %v\n", err)
			return
		}
		
		fmt.Printf("结果已保存到: %s\n", *outputFileFlag)
	}
} 