package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"time"
)

// ReasoningRequest 推理请求结构体
type ReasoningRequest struct {
	Query            string                 `json:"query"`
	UserID           string                 `json:"user_id,omitempty"`
	Domain           string                 `json:"domain,omitempty"`
	UseDecomposition bool                   `json:"use_decomposition"`
	MaxResults       int                    `json:"max_results"`
	MaxReasoningSteps int                   `json:"max_reasoning_steps"`
	UseCache         bool                   `json:"use_cache"`
	TCMOptions       *TCMReasoningOptions   `json:"tcm_options,omitempty"`
	MultimodalOptions *MultimodalOptions    `json:"multimodal_options,omitempty"`
	ExtraOptions     map[string]interface{} `json:"extra_options,omitempty"`
}

// TCMReasoningOptions 中医推理选项
type TCMReasoningOptions struct {
	PatternDifferentiationRequirements []string               `json:"pattern_differentiation_requirements,omitempty"`
	PrescriptionRequirements           []string               `json:"prescription_requirements,omitempty"`
	IncludeFourDiagnosticData          bool                   `json:"include_four_diagnostic_data,omitempty"`
	FourDiagnosticData                 map[string]interface{} `json:"four_diagnostic_data,omitempty"`
	IncludeReasoningProcess            bool                   `json:"include_reasoning_process,omitempty"`
}

// MultimodalOptions 多模态选项
type MultimodalOptions struct {
	ImageData map[string]string `json:"image_data,omitempty"` // base64编码的图像数据
	AudioData map[string]string `json:"audio_data,omitempty"` // base64编码的音频数据
	ImageType string            `json:"image_type,omitempty"` // tongue, face, pulse, herb
	AudioType string            `json:"audio_type,omitempty"` // pulse, voice
}

// 测试用例结构体
type TestCase struct {
	Name        string
	Request     ReasoningRequest
	Description string
}

// 服务地址
const serviceURL = "http://localhost:8080/api/reasoning"

func main() {
	// 命令行参数
	var (
		testName  string
		query     string
		domain    string
		decompose bool
		tcm       bool
		verbose   bool
	)
	
	flag.StringVar(&testName, "test", "", "指定测试用例名称")
	flag.StringVar(&query, "query", "", "自定义查询文本")
	flag.StringVar(&domain, "domain", "tcm", "查询领域")
	flag.BoolVar(&decompose, "decompose", true, "启用查询分解")
	flag.BoolVar(&tcm, "tcm", false, "使用中医特定选项")
	flag.BoolVar(&verbose, "v", false, "详细输出")
	flag.Parse()
	
	// 创建测试用例
	testCases := []TestCase{
		{
			Name: "基础推理测试",
			Request: ReasoningRequest{
				Query:            "中医理论中的五行学说是什么？与脏腑有什么关系？",
				Domain:           "tcm",
				UseDecomposition: true,
				MaxResults:       10,
				MaxReasoningSteps: 3,
				UseCache:         false,
			},
			Description: "测试基本的中医理论查询和推理能力",
		},
		{
			Name: "复杂查询分解测试",
			Request: ReasoningRequest{
				Query:            "肝火旺盛会有哪些症状？如何通过食疗进行调理？有没有推荐的中成药？",
				Domain:           "tcm",
				UseDecomposition: true,
				MaxResults:       10,
				MaxReasoningSteps: 3,
				UseCache:         false,
			},
			Description: "测试复杂查询的自动分解和结果合并功能",
		},
		{
			Name: "中医辨证推理测试",
			Request: ReasoningRequest{
				Query:            "我最近感到口干舌燥，容易口渴，尿黄，大便干结，舌头发红，舌苔黄，请进行辨证",
				Domain:           "tcm",
				UseDecomposition: true,
				MaxResults:       15,
				MaxReasoningSteps: 3,
				UseCache:         false,
				TCMOptions: &TCMReasoningOptions{
					IncludeReasoningProcess: true,
					PatternDifferentiationRequirements: []string{"详细分析", "证型诊断"},
					PrescriptionRequirements: []string{"药方推荐", "食疗建议"},
				},
			},
			Description: "测试中医辨证推理功能和详细诊断报告",
		},
		{
			Name: "四诊合参测试",
			Request: ReasoningRequest{
				Query:            "根据以下四诊信息进行辨证",
				Domain:           "tcm",
				UseDecomposition: false,
				MaxResults:       10,
				MaxReasoningSteps: 3,
				UseCache:         false,
				TCMOptions: &TCMReasoningOptions{
					IncludeReasoningProcess: true,
					IncludeFourDiagnosticData: true,
					FourDiagnosticData: map[string]interface{}{
						"tongue": map[string]interface{}{
							"color": "淡红",
							"coating": "薄白",
							"shape": "胖大有齿痕",
							"moisture": "湿润",
						},
						"face": map[string]interface{}{
							"color": "偏白",
							"spirit": "疲倦",
							"features": []string{"眼袋", "面浮"},
						},
						"pulse": map[string]interface{}{
							"left": "沉缓",
							"right": "沉缓",
							"strength": "无力",
						},
					},
					PatternDifferentiationRequirements: []string{"详细分析", "证型诊断"},
				},
			},
			Description: "测试结合四诊信息的辨证功能",
		},
		{
			Name: "跨领域复杂查询",
			Request: ReasoningRequest{
				Query:            "如何从中医和现代营养学角度理解食物的性味与功效？以西红柿为例进行分析。",
				Domain:           "",
				UseDecomposition: true,
				MaxResults:       15,
				MaxReasoningSteps: 4,
				UseCache:         false,
				ExtraOptions: map[string]interface{}{
					"cross_domain": true,
				},
			},
			Description: "测试跨领域知识整合能力，同时考察中医和现代营养学知识",
		},
	}

	// 如果提供了自定义查询，创建自定义测试用例
	if query != "" {
		customTest := TestCase{
			Name: "自定义测试",
			Request: ReasoningRequest{
				Query:            query,
				Domain:           domain,
				UseDecomposition: decompose,
				MaxResults:       15,
				MaxReasoningSteps: 4,
				UseCache:         false,
			},
			Description: "自定义测试查询",
		}
		
		// 如果需要中医特定选项
		if tcm {
			customTest.Request.TCMOptions = &TCMReasoningOptions{
				IncludeReasoningProcess: true,
				PatternDifferentiationRequirements: []string{"详细分析", "证型诊断"},
				PrescriptionRequirements: []string{"药方推荐", "食疗建议"},
			}
		}
		
		// 将自定义测试添加到测试用例列表
		testCases = append(testCases, customTest)
	}
	
	// 执行测试
	casesToRun := testCases
	
	// 如果指定了测试名称，只运行该测试用例
	if testName != "" {
		casesToRun = nil
		for _, tc := range testCases {
			if tc.Name == testName {
				casesToRun = append(casesToRun, tc)
				break
			}
		}
		
		if len(casesToRun) == 0 {
			fmt.Printf("未找到名为 '%s' 的测试用例\n", testName)
			fmt.Println("可用的测试用例:")
			for _, tc := range testCases {
				fmt.Printf("- %s\n", tc.Name)
			}
			os.Exit(1)
		}
	}
	
	// 执行选定的测试用例
	for _, tc := range casesToRun {
		fmt.Printf("\n======= 执行测试: %s =======\n", tc.Name)
		fmt.Printf("描述: %s\n", tc.Description)
		fmt.Printf("查询: %s\n\n", tc.Request.Query)

		// 发送请求
		startTime := time.Now()
		resp, err := sendRequest(tc.Request)
		duration := time.Since(startTime)

		if err != nil {
			fmt.Printf("测试失败: %v\n", err)
			continue
		}

		// 输出结果
		fmt.Printf("响应时间: %v\n\n", duration)
		fmt.Printf("答案:\n%s\n\n", resp["answer"])
		
		// 输出置信度
		if confidence, ok := resp["confidence"].(float64); ok {
			fmt.Printf("置信度: %.2f\n\n", confidence)
		}
		
		// 输出引用数量
		if refs, ok := resp["references"].([]interface{}); ok {
			fmt.Printf("引用数量: %d\n\n", len(refs))
			
			// 如果启用了详细输出，显示引用详情
			if verbose {
				fmt.Println("引用资料:")
				for i, ref := range refs {
					refMap := ref.(map[string]interface{})
					fmt.Printf("  [%d] %s\n", i+1, refMap["content"])
					if source, ok := refMap["source"].(string); ok && source != "" {
						fmt.Printf("      来源: %s\n", source)
					}
					fmt.Println()
				}
			}
		}
		
		// 输出步骤数量
		if steps, ok := resp["steps"].([]interface{}); ok {
			fmt.Printf("推理步骤数: %d\n\n", len(steps))
			
			// 如果启用了详细输出，显示步骤详情
			if verbose {
				fmt.Println("推理步骤:")
				for i, step := range steps {
					stepMap := step.(map[string]interface{})
					fmt.Printf("  步骤 %d: %s\n", i+1, stepMap["name"])
					fmt.Printf("  问题: %s\n", stepMap["question"])
					
					if results, ok := stepMap["retrieved_results"].([]interface{}); ok && len(results) > 0 {
						fmt.Printf("  检索结果数: %d\n", len(results))
					}
					
					if process, ok := stepMap["reasoning_process"].(string); ok && process != "" {
						fmt.Printf("  推理过程: %s\n", truncateText(process, 150))
					}
					
					fmt.Printf("  结论: %s\n", stepMap["conclusion"])
					fmt.Printf("  置信度: %.2f\n\n", stepMap["confidence"])
				}
			}
		}
		
		// 输出统计信息
		if stats, ok := resp["stats"].(map[string]interface{}); ok {
			fmt.Println("统计信息:")
			for k, v := range stats {
				fmt.Printf("  %s: %v\n", k, v)
			}
		}
		
		fmt.Println("\n测试完成")
		fmt.Println("====================================")
	}
}

// 发送请求并返回响应
func sendRequest(req ReasoningRequest) (map[string]interface{}, error) {
	// 序列化请求
	reqData, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("序列化请求失败: %v", err)
	}

	// 发送HTTP请求
	httpResp, err := http.Post(serviceURL, "application/json", bytes.NewBuffer(reqData))
	if err != nil {
		return nil, fmt.Errorf("发送请求失败: %v", err)
	}
	defer httpResp.Body.Close()

	// 读取响应
	respBody, err := ioutil.ReadAll(httpResp.Body)
	if err != nil {
		return nil, fmt.Errorf("读取响应失败: %v", err)
	}

	// 检查HTTP状态码
	if httpResp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("服务器返回错误状态码: %d, 响应: %s", httpResp.StatusCode, string(respBody))
	}

	// 解析JSON响应
	var respData map[string]interface{}
	if err := json.Unmarshal(respBody, &respData); err != nil {
		return nil, fmt.Errorf("解析响应失败: %v", err)
	}

	return respData, nil
}

// 截断文本，添加省略号
func truncateText(text string, maxLen int) string {
	if len(text) <= maxLen {
		return text
	}
	return text[:maxLen] + "..."
} 