package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/olekukonko/tablewriter"
	
	"github.com/suoke_life/services/rag-service/tests/common"
)

const (
	defaultServiceURL = "http://localhost:8080/api/reason"
)

var (
	query                = flag.String("query", "", "推理查询")
	userID               = flag.String("user", "test_user", "用户ID")
	domain               = flag.String("domain", "tcm", "领域")
	startEntities        = flag.String("start", "", "起始实体(逗号分隔)")
	endEntities          = flag.String("end", "", "目标实体(逗号分隔)")
	maxDepth             = flag.Int("depth", 3, "最大路径深度")
	maxPaths             = flag.Int("paths", 5, "最大路径数量")
	maxNodes             = flag.Int("nodes", 20, "最大节点数量")
	includeDocuments     = flag.Bool("docs", true, "包含支持文档")
	maxDocuments         = flag.Int("max_docs", 3, "最大文档数量")
	includeProcess       = flag.Bool("process", true, "包含推理过程")
	relevanceThreshold   = flag.Float64("threshold", 0.6, "子图相关性阈值")
	outputDir            = flag.String("output_dir", "", "输出目录")
	serviceURLFlag       = flag.String("url", defaultServiceURL, "服务URL")
	verbose              = flag.Bool("verbose", false, "详细日志")
	predefinedQueries    = flag.Bool("predefined", false, "使用预定义查询集")
)

// 预定义的中医领域查询
var tcmQueries = []string{
	"人参和黄芪有什么关系？二者可以一起服用吗？",
	"糖尿病患者适合服用哪些中药？有哪些需要注意的？",
	"桂枝汤和白虎汤的适应症有哪些不同？",
	"什么是六淫？它们与疾病发生有什么关系？",
	"肝肾阴虚的人适合吃什么中药调理？",
}

func main() {
	flag.Parse()
	
	// 检查必要参数
	if *query == "" && !*predefinedQueries {
		fmt.Println("错误: 必须提供查询参数 (-query) 或使用预定义查询 (-predefined)")
		flag.Usage()
		os.Exit(1)
	}
	
	// 创建HTTP客户端
	client := common.NewHTTPClient(*serviceURLFlag, 30*time.Second)
	client.Verbose = *verbose
	
	// 创建输出目录
	outDir := *outputDir
	if outDir == "" {
		var err error
		outDir, err = common.CreateTestOutputDirectory("kg_reasoning")
		if err != nil {
			fmt.Printf("创建输出目录失败: %v\n", err)
			os.Exit(1)
		}
	} else {
		if err := os.MkdirAll(outDir, 0755); err != nil {
			fmt.Printf("创建指定输出目录失败: %v\n", err)
			os.Exit(1)
		}
	}
	
	fmt.Printf("测试结果将保存到: %s\n\n", outDir)
	
	// 根据模式执行测试
	if *predefinedQueries {
		// 创建结果表格
		table := tablewriter.NewWriter(os.Stdout)
		table.SetHeader([]string{"查询", "结论", "置信度", "耗时(ms)", "状态"})
		table.SetBorder(false)
		table.SetColumnSeparator("|")
		
		// 执行预定义查询
		fmt.Println("执行预定义查询测试...")
		
		for i, q := range tcmQueries {
			fmt.Printf("\n[%d/%d] 测试查询: %s\n", i+1, len(tcmQueries), q)
			
			result, err := executeReasoning(client, q, outDir)
			
			status := "成功"
			if err != nil {
				status = fmt.Sprintf("失败: %v", err)
			} else if !result.Success {
				status = fmt.Sprintf("服务错误: %s", result.Error)
			}
			
			// 添加到表格
			shortConclusion := result.Conclusion
			if len(shortConclusion) > 50 {
				shortConclusion = shortConclusion[:47] + "..."
			}
			
			table.Append([]string{
				q,
				shortConclusion,
				fmt.Sprintf("%.2f", result.Confidence),
				fmt.Sprintf("%d", result.ProcessingTimeMs),
				status,
			})
		}
		
		// 输出结果表格
		fmt.Println("\n推理测试结果汇总:")
		table.Render()
		
	} else {
		// 单次推理测试
		fmt.Printf("执行知识图谱推理测试: %s\n\n", *query)
		result, err := executeReasoning(client, *query, outDir)
		if err != nil {
			fmt.Printf("推理失败: %v\n", err)
			os.Exit(1)
		}
		
		// 详细输出结果
		if result.Success {
			fmt.Println("\n===== 推理结果 =====")
			fmt.Printf("结论: %s\n", result.Conclusion)
			fmt.Printf("置信度: %.2f\n", result.Confidence)
			fmt.Printf("处理时间: %d ms\n", result.ProcessingTimeMs)
			
			// 输出关键实体
			if len(result.KeyEntities) > 0 {
				fmt.Printf("\n关键实体 (%d个):\n", len(result.KeyEntities))
				for i, entity := range result.KeyEntities {
					fmt.Printf("[%d] %s (类型: %s)\n", i+1, entity.Name, entity.Type)
				}
			}
			
			// 输出推理路径
			if len(result.Paths) > 0 {
				fmt.Printf("\n推理路径 (%d条):\n", len(result.Paths))
				for i, path := range result.Paths {
					fmt.Printf("[%d] 相关度: %.4f\n", i+1, path.Score)
					printPath(path)
					fmt.Println()
				}
			}
			
			// 输出支持文档
			if len(result.SupportingDocuments) > 0 {
				fmt.Printf("\n支持文档 (%d个):\n", len(result.SupportingDocuments))
				for i, doc := range result.SupportingDocuments {
					fmt.Printf("[%d] 相关度: %.4f\n", i+1, doc.Score)
					fmt.Printf("    %s\n", doc.Content)
					if doc.Source != "" {
						fmt.Printf("    来源: %s\n", doc.Source)
					}
					fmt.Println()
				}
			}
			
			// 输出推理过程
			if result.ReasoningProcess != "" {
				fmt.Println("\n推理过程:")
				fmt.Println(result.ReasoningProcess)
			}
		} else {
			fmt.Printf("推理失败: %s\n", result.Error)
		}
	}
}

// executeReasoning 执行知识图谱推理
func executeReasoning(client *common.HTTPClient, query string, outDir string) (*common.ReasoningResponse, error) {
	ctx := context.Background()
	
	// 解析实体列表
	var startEntityList, endEntityList []string
	if *startEntities != "" {
		startEntityList = strings.Split(*startEntities, ",")
	}
	if *endEntities != "" {
		endEntityList = strings.Split(*endEntities, ",")
	}
	
	// 构建请求
	request := common.ReasoningRequest{
		Query:                     query,
		UserID:                    *userID,
		Domain:                    *domain,
		StartEntities:             startEntityList,
		EndEntities:               endEntityList,
		MaxDepth:                  *maxDepth,
		MaxPaths:                  *maxPaths,
		MaxNodes:                  *maxNodes,
		IncludeDocuments:          *includeDocuments,
		MaxDocuments:              *maxDocuments,
		IncludeReasoningProcess:   *includeProcess,
		SubgraphRelevanceThreshold: *relevanceThreshold,
		ExtraOptions: map[string]interface{}{
			"test_mode": true,
		},
	}
	
	// 发送请求
	fmt.Println("发送推理请求...")
	startTime := time.Now()
	respData, err := client.PostJSON(ctx, "", request)
	duration := time.Since(startTime)
	
	if err != nil {
		return nil, fmt.Errorf("请求失败: %w", err)
	}
	
	// 解析响应
	var result common.ReasoningResponse
	if err := json.Unmarshal(respData, &result); err != nil {
		return nil, fmt.Errorf("解析响应失败: %w", err)
	}
	
	// 输出基本信息
	fmt.Printf("响应时间: %v\n", duration)
	
	// 保存结果
	if outDir != "" {
		// 为文件名创建简短的查询文本
		queryText := query
		if len(queryText) > 30 {
			queryText = queryText[:27] + "..."
		}
		queryText = strings.ReplaceAll(queryText, " ", "_")
		queryText = strings.ReplaceAll(queryText, "?", "")
		queryText = strings.ReplaceAll(queryText, "！", "")
		
		// 保存完整结果
		resultFile := filepath.Join(outDir, fmt.Sprintf("reasoning_%s.json", queryText))
		if err := common.SaveResultToFile(result, resultFile); err != nil {
			fmt.Printf("保存结果文件失败: %v\n", err)
		} else {
			fmt.Printf("结果已保存至: %s\n", resultFile)
		}
	}
	
	return &result, nil
}

// printPath 打印推理路径
func printPath(path common.KGPath) {
	if len(path.Nodes) == 0 {
		return
	}
	
	// 输出路径
	for i := 0; i < len(path.Nodes); i++ {
		// 打印节点
		fmt.Printf("    %s", path.Nodes[i].Name)
		
		// 如果有下一个边和节点，打印关系
		if i < len(path.Edges) {
			fmt.Printf(" --[%s]--> ", path.Edges[i].Type)
		}
	}
	fmt.Println()
} 