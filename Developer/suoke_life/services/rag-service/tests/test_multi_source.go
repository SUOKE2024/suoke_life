package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/olekukonko/tablewriter"
	"github.com/suoke_life/services/rag-service/tests/common"
)

// 多源检索请求结构
type MultiSourceRequest struct {
	Query         string            `json:"query"`
	UserID        string            `json:"user_id,omitempty"`
	Domain        string            `json:"domain,omitempty"`
	MaxResults    int               `json:"max_results,omitempty"`
	UseCache      bool              `json:"use_cache,omitempty"`
	Sources       []string          `json:"sources,omitempty"`
	Filters       map[string]string `json:"filters,omitempty"`
	TCMOptions    map[string]bool   `json:"tcm_options,omitempty"`
	ExtraOptions  map[string]any    `json:"extra_options,omitempty"`
	SearchDepth   int               `json:"search_depth,omitempty"`
	SearchBreadth int               `json:"search_breadth,omitempty"`
}

// 多源检索结果结构
type MultiSourceResponse struct {
	Status     string               `json:"status"`
	Query      string               `json:"query"`
	Results    []SourceResultGroup  `json:"results,omitempty"`
	Statistics map[string]any       `json:"statistics,omitempty"`
	Metadata   map[string]any       `json:"metadata,omitempty"`
	Error      string               `json:"error,omitempty"`
}

// 数据源组结果
type SourceResultGroup struct {
	Source      string                 `json:"source"`
	Results     []common.SearchResult  `json:"results"`
	Reliability float64                `json:"reliability"`
	Metadata    map[string]interface{} `json:"metadata,omitempty"`
}

// 预定义查询集
var predefinedQueries = []struct {
	Query  string
	Domain string
}{
	{"中医如何治疗感冒", "tcm"},
	{"人参的药用价值和主要功效", "tcm"},
	{"脾虚湿盛的表现和调理方法", "tcm"},
	{"阴虚火旺是什么体质", "tcm"},
	{"肝郁脾虚的症状和调理", "tcm"},
	{"中医养生的基本原则", "tcm"},
	{"针灸对慢性疼痛有什么效果", "tcm"},
	{"艾灸的适应症和禁忌", "tcm"},
	{"太极拳的养生功效", "tcm"},
	{"夏季如何预防中暑", "health"},
}

// 全局变量
var mockMode bool

// 测试批量查询
func testBatchQueries(serviceURL string, outputFile string, verbose bool) {
	fmt.Println("=== 开始批量测试多源检索功能 ===")
	
	results := make([]MultiSourceResponse, 0)
	
	for i, query := range predefinedQueries {
		fmt.Printf("[%d/%d] 测试查询: %s (领域: %s)\n", i+1, len(predefinedQueries), query.Query, query.Domain)
		
		// 构建请求
		req := MultiSourceRequest{
			Query:      query.Query,
			Domain:     query.Domain,
			UserID:     "test_user",
			MaxResults: 5,
			UseCache:   true,
			Sources:    []string{"internal", "kg", "web"},
		}
		
		// 发送请求
		result, err := sendMultiSourceRequest(serviceURL, req, verbose)
		if err != nil {
			fmt.Printf("错误: %v\n", err)
			continue
		}
		
		// 添加到结果集
		results = append(results, result)
		
		// 简要显示结果
		fmt.Printf("  状态: %s\n", result.Status)
		for _, group := range result.Results {
			fmt.Printf("  来源: %s (可靠性: %.2f%%)\n", group.Source, group.Reliability*100)
			fmt.Printf("  结果数量: %d\n", len(group.Results))
		}
		fmt.Println()
		
		// 如果详细模式，显示更多信息
		if verbose {
			printDetailedResults(result)
		}
		
		// 避免请求过快
		time.Sleep(500 * time.Millisecond)
	}
	
	// 保存结果
	if outputFile != "" {
		saveResults(results, outputFile)
		fmt.Printf("结果已保存到: %s\n", outputFile)
	}
	
	fmt.Println("=== 批量测试完成 ===")
}

// 测试单个查询
func testSingleQuery(serviceURL, query, domain, outputFile string, useCache bool, maxResults int, verbose bool) {
	fmt.Printf("=== 测试多源检索请求 ===\n")
	fmt.Printf("查询: %s\n", query)
	fmt.Printf("领域: %s\n", domain)
	
	// 构建请求
	req := MultiSourceRequest{
		Query:      query,
		Domain:     domain,
		UserID:     "test_user",
		MaxResults: maxResults,
		UseCache:   useCache,
		Sources:    []string{"internal", "kg", "web"},
	}
	
	// 发送请求
	result, err := sendMultiSourceRequest(serviceURL, req, verbose)
	if err != nil {
		fmt.Printf("错误: %v\n", err)
		return
	}
	
	// 显示详细结果
	printDetailedResults(result)
	
	// 保存结果
	if outputFile != "" {
		saveResults([]MultiSourceResponse{result}, outputFile)
		fmt.Printf("结果已保存到: %s\n", outputFile)
	}
}

// 发送多源检索请求
func sendMultiSourceRequest(serviceURL string, req MultiSourceRequest, verbose bool) (MultiSourceResponse, error) {
	// 如果是模拟模式，返回模拟数据
	if mockMode {
		return generateMockResponse(req)
	}
	
	jsonData, err := json.Marshal(req)
	if err != nil {
		return MultiSourceResponse{}, fmt.Errorf("JSON编码错误: %v", err)
	}
	
	if verbose {
		fmt.Printf("发送请求到: %s\n", serviceURL)
		fmt.Printf("请求数据: %s\n", string(jsonData))
	}
	
	// 发送HTTP请求
	resp, err := http.Post(serviceURL, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return MultiSourceResponse{}, fmt.Errorf("HTTP请求错误: %v", err)
	}
	defer resp.Body.Close()
	
	// 读取响应
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return MultiSourceResponse{}, fmt.Errorf("读取响应错误: %v", err)
	}
	
	if verbose {
		fmt.Printf("响应状态码: %d\n", resp.StatusCode)
		fmt.Printf("响应数据: %s\n", string(body))
	}
	
	// 解析响应
	var result MultiSourceResponse
	if err := json.Unmarshal(body, &result); err != nil {
		return MultiSourceResponse{}, fmt.Errorf("JSON解析错误: %v", err)
	}
	
	return result, nil
}

// 生成模拟响应
func generateMockResponse(req MultiSourceRequest) (MultiSourceResponse, error) {
	response := MultiSourceResponse{
		Status: "success",
		Query:  req.Query,
		Results: []SourceResultGroup{
			{
				Source:      "internal",
				Reliability: 0.85,
				Results:     generateMockResults("internal", req.Query, 3),
				Metadata:    map[string]interface{}{"source_type": "internal_db"},
			},
			{
				Source:      "kg",
				Reliability: 0.92,
				Results:     generateMockResults("kg", req.Query, 2),
				Metadata:    map[string]interface{}{"graph_depth": 2},
			},
			{
				Source:      "web",
				Reliability: 0.75,
				Results:     generateMockResults("web", req.Query, 2),
				Metadata:    map[string]interface{}{"freshness": "24h"},
			},
		},
		Statistics: map[string]any{
			"total_results":  7,
			"response_time":  0.125,
			"search_sources": 3,
		},
		Metadata: map[string]any{
			"domain":     req.Domain,
			"timestamp":  time.Now().Format(time.RFC3339),
			"model":      "suoke-rag-v2.5",
			"session_id": "mock-session-" + time.Now().Format("20060102-150405"),
		},
	}
	
	return response, nil
}

// 生成模拟结果
func generateMockResults(source, query string, count int) []common.SearchResult {
	results := make([]common.SearchResult, 0, count)
	
	for i := 0; i < count; i++ {
		result := common.SearchResult{
			ID:      fmt.Sprintf("%s-result-%d", source, i+1),
			Content: fmt.Sprintf("这是来自%s的第%d条关于"%s"的模拟数据。这里包含一些与查询相关的内容，用于测试多源检索功能。", source, i+1, query),
			Source:  fmt.Sprintf("%s-database", source),
			Score:   0.95 - float64(i)*0.05,
			Metadata: map[string]interface{}{
				"type":       "text",
				"category":   source + "_category",
				"confidence": 0.9 - float64(i)*0.1,
			},
		}
		results = append(results, result)
	}
	
	return results
}

// 打印详细结果
func printDetailedResults(result MultiSourceResponse) {
	fmt.Println("\n=== 详细结果 ===")
	fmt.Printf("查询: %s\n", result.Query)
	fmt.Printf("状态: %s\n", result.Status)
	
	if result.Error != "" {
		fmt.Printf("错误: %s\n", result.Error)
		return
	}
	
	// 输出统计信息
	if len(result.Statistics) > 0 {
		fmt.Println("\n-- 统计信息 --")
		for k, v := range result.Statistics {
			fmt.Printf("%s: %v\n", k, v)
		}
	}
	
	// 遍历每个数据源结果
	for _, group := range result.Results {
		fmt.Printf("\n-- 数据源: %s (可靠性: %.2f%%) --\n", group.Source, group.Reliability*100)
		
		// 创建表格输出搜索结果
		table := tablewriter.NewWriter(os.Stdout)
		table.SetHeader([]string{"ID", "内容", "来源", "分数"})
		table.SetRowLine(true)
		table.SetAlignment(tablewriter.ALIGN_LEFT)
		
		for _, result := range group.Results {
			content := result.Content
			if len(content) > 100 {
				content = content[:97] + "..."
			}
			
			score := fmt.Sprintf("%.3f", result.Score)
			
			table.Append([]string{
				result.ID,
				content,
				result.Source,
				score,
			})
		}
		
		table.Render()
		
		// 输出元数据
		if len(group.Metadata) > 0 {
			fmt.Println("元数据:")
			for k, v := range group.Metadata {
				fmt.Printf("  %s: %v\n", k, v)
			}
		}
	}
}

// 保存结果到文件
func saveResults(results []MultiSourceResponse, outputFile string) error {
	data, err := json.MarshalIndent(results, "", "  ")
	if err != nil {
		return err
	}
	
	// 确保目录存在
	dir := filepath.Dir(outputFile)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return err
	}
	
	return ioutil.WriteFile(outputFile, data, 0644)
}

func main() {
	// 命令行参数
	query := flag.String("query", "", "查询文本")
	domain := flag.String("domain", "tcm", "查询领域")
	serviceURLFlag := flag.String("url", "", "服务地址")
	outputFile := flag.String("output", "", "输出结果到文件")
	batch := flag.Bool("batch", false, "批量测试模式")
	maxResults := flag.Int("max", 5, "每个数据源的最大结果数")
	useCache := flag.Bool("cache", true, "使用缓存")
	verbose := flag.Bool("verbose", false, "详细输出")
	mock := flag.Bool("mock", false, "使用模拟数据")
	
	flag.Parse()
	
	// 设置全局模拟模式
	mockMode = *mock
	
	// 服务URL
	serviceURL := "http://localhost:8080/api/search/multi_source"
	if *serviceURLFlag != "" {
		serviceURL = *serviceURLFlag
	}
	
	// 生成输出文件名
	if *outputFile == "" {
		timestamp := time.Now().Format("20060102_150405")
		if *batch {
			*outputFile = fmt.Sprintf("./test_results/multi_source_batch_%s.json", timestamp)
		} else {
			queryPart := *query
			if len(queryPart) > 20 {
				queryPart = queryPart[:20]
			}
			queryPart = strings.ReplaceAll(queryPart, " ", "_")
			*outputFile = fmt.Sprintf("./test_results/multi_source_%s_%s.json", queryPart, timestamp)
		}
	}
	
	// 批量测试或单个查询测试
	if *batch {
		testBatchQueries(serviceURL, *outputFile, *verbose)
	} else {
		if *query == "" {
			fmt.Println("错误: 必须提供查询文本(-query)或使用批量模式(-batch)")
			flag.Usage()
			os.Exit(1)
		}
		testSingleQuery(serviceURL, *query, *domain, *outputFile, *useCache, *maxResults, *verbose)
	}
} 