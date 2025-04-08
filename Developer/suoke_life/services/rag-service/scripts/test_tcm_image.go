package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/suoke/suoke_life/services/rag-service/embeddings"
	"github.com/suoke/suoke_life/services/rag-service/factory"
	"github.com/suoke/suoke_life/services/rag-service/internal/models"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils"
)

// TestResult 测试结果
type TestResult struct {
	// 图像类型
	ImageType string `json:"image_type"`
	
	// 图像路径
	ImagePath string `json:"image_path"`
	
	// 舌诊特征
	TongueFeatures *embeddings.TongueFeatures `json:"tongue_features,omitempty"`
	
	// 面诊特征
	FaceFeatures *embeddings.FaceFeatures `json:"face_features,omitempty"`
	
	// 检索结果
	SearchResults []models.SearchResult `json:"search_results,omitempty"`
	
	// 分析持续时间
	AnalysisDuration time.Duration `json:"analysis_duration"`
	
	// 检索持续时间
	SearchDuration time.Duration `json:"search_duration"`
	
	// 错误信息
	Error string `json:"error,omitempty"`
}

func main() {
	// 命令行参数
	var (
		imagePath     string
		modelPath     string
		imageType     string
		resultPath    string
		topK          int
		useReranker   bool
		testSearch    bool
	)
	
	flag.StringVar(&imagePath, "image", "", "要分析的图像路径")
	flag.StringVar(&modelPath, "model", "./models", "模型目录路径")
	flag.StringVar(&imageType, "type", "tongue", "图像类型 (tongue, face)")
	flag.StringVar(&resultPath, "output", "", "结果输出路径 (JSON)")
	flag.IntVar(&topK, "top", 5, "返回的结果数量")
	flag.BoolVar(&useReranker, "rerank", false, "是否使用重排序")
	flag.BoolVar(&testSearch, "search", true, "是否测试检索功能")
	
	flag.Parse()
	
	if imagePath == "" {
		fmt.Println("请提供图像路径 (-image)")
		flag.Usage()
		os.Exit(1)
	}
	
	// 创建日志器
	logger := utils.NewConsoleLogger()
	
	// 创建结果对象
	result := &TestResult{
		ImageType: imageType,
		ImagePath: imagePath,
	}
	
	// 创建上下文
	ctx := context.Background()
	
	// 创建组件工厂
	factoryInstance, err := factory.NewComponentFactory(modelPath, logger)
	if err != nil {
		fmt.Printf("创建组件工厂失败: %v\n", err)
		os.Exit(1)
	}
	
	// 初始化组件工厂
	if err := factoryInstance.Initialize(ctx); err != nil {
		fmt.Printf("初始化组件工厂失败: %v\n", err)
		os.Exit(1)
	}
	defer factoryInstance.Close()
	
	// 获取TCM图像嵌入器
	embeddingStart := time.Now()
	tcmImageEmbedder, err := factoryInstance.GetImageEmbedder("tcm")
	if err != nil {
		result.Error = fmt.Sprintf("获取TCM图像嵌入器失败: %v", err)
		writeResult(result, resultPath)
		fmt.Println(result.Error)
		os.Exit(1)
	}
	
	// 分析图像
	if imageType == "tongue" {
		// 分析舌诊图像
		start := time.Now()
		features, err := extractTongueFeatures(tcmImageEmbedder.(embeddings.TCMImageEmbedder), imagePath)
		result.AnalysisDuration = time.Since(start)
		
		if err != nil {
			result.Error = fmt.Sprintf("提取舌诊特征失败: %v", err)
		} else {
			result.TongueFeatures = features
			fmt.Println("舌诊分析结果:")
			fmt.Printf("  舌质颜色: %s\n", features.TongueColor)
			fmt.Printf("  舌苔颜色: %s\n", features.CoatingColor)
			fmt.Printf("  舌苔厚度: %s\n", features.CoatingThickness)
			fmt.Printf("  舌体湿度: %.2f\n", features.Moisture)
			fmt.Printf("  舌形特征: %v\n", features.TongueShape)
		}
	} else if imageType == "face" {
		// 分析面诊图像
		start := time.Now()
		features, err := extractFaceFeatures(tcmImageEmbedder.(embeddings.TCMImageEmbedder), imagePath)
		result.AnalysisDuration = time.Since(start)
		
		if err != nil {
			result.Error = fmt.Sprintf("提取面诊特征失败: %v", err)
		} else {
			result.FaceFeatures = features
			fmt.Println("面诊分析结果:")
			fmt.Printf("  面色: %s\n", features.FaceColor)
			fmt.Printf("  五官特征: %v\n", features.FacialFeatures)
			fmt.Printf("  脏腑对应: %v\n", features.OrganMapping)
		}
	}
	
	// 测试检索功能
	if testSearch {
		start := time.Now()
		searchResults, err := performSearch(ctx, factoryInstance, tcmImageEmbedder.(embeddings.TCMImageEmbedder), imagePath, imageType, topK, useReranker)
		result.SearchDuration = time.Since(start)
		
		if err != nil {
			if result.Error == "" {
				result.Error = fmt.Sprintf("检索失败: %v", err)
			} else {
				result.Error += fmt.Sprintf("; 检索失败: %v", err)
			}
		} else {
			result.SearchResults = searchResults
			
			fmt.Println("\n检索结果:")
			for i, sr := range searchResults {
				fmt.Printf("%d. [分数:%.4f] %s\n", i+1, sr.Score, sr.Content)
				if sr.Source != "" {
					fmt.Printf("   来源: %s\n", sr.Source)
				}
				fmt.Println()
			}
		}
	}
	
	// 输出结果
	if resultPath != "" {
		writeResult(result, resultPath)
	}
	
	fmt.Printf("\n分析耗时: %v\n", result.AnalysisDuration)
	if testSearch {
		fmt.Printf("检索耗时: %v\n", result.SearchDuration)
	}
}

// extractTongueFeatures 提取舌诊特征
func extractTongueFeatures(embedder embeddings.TCMImageEmbedder, imagePath string) (*embeddings.TongueFeatures, error) {
	metadata := &models.DocumentMetadata{Properties: make(map[string]interface{})}
	
	// 调用中医图像元数据增强方法
	ctx := context.Background()
	embedder.EnhanceTCMImageMetadata(ctx, metadata, imagePath)
	
	// 从元数据中提取舌诊特征
	if metadata.Properties["tcm_image_category"] != "舌诊图像" {
		return nil, fmt.Errorf("图像不是舌诊图像")
	}
	
	features := &embeddings.TongueFeatures{
		TongueColor:      metadata.Properties["tongue_color"].(string),
		CoatingColor:     metadata.Properties["coating_color"].(string),
		CoatingThickness: metadata.Properties["coating_thickness"].(string),
	}
	
	// 处理其他可能的属性
	if moisture, ok := metadata.Properties["moisture"].(float32); ok {
		features.Moisture = moisture
	}
	
	if tongueShape, ok := metadata.Properties["tongue_shape"].([]string); ok {
		features.TongueShape = tongueShape
	}
	
	if coatingNature, ok := metadata.Properties["coating_nature"].([]string); ok {
		features.CoatingNature = coatingNature
	}
	
	return features, nil
}

// extractFaceFeatures 提取面诊特征
func extractFaceFeatures(embedder embeddings.TCMImageEmbedder, imagePath string) (*embeddings.FaceFeatures, error) {
	metadata := &models.DocumentMetadata{Properties: make(map[string]interface{})}
	
	// 调用中医图像元数据增强方法
	ctx := context.Background()
	embedder.EnhanceTCMImageMetadata(ctx, metadata, imagePath)
	
	// 从元数据中提取面诊特征
	if metadata.Properties["tcm_image_category"] != "面诊图像" {
		return nil, fmt.Errorf("图像不是面诊图像")
	}
	
	features := &embeddings.FaceFeatures{
		FaceColor: metadata.Properties["face_color"].(string),
	}
	
	// 处理其他可能的属性
	if facialFeatures, ok := metadata.Properties["facial_features"].(map[string]string); ok {
		features.FacialFeatures = facialFeatures
	}
	
	if organMapping, ok := metadata.Properties["organ_mapping"].(map[string]float32); ok {
		features.OrganMapping = organMapping
	}
	
	return features, nil
}

// performSearch 执行检索
func performSearch(ctx context.Context, factoryInstance *factory.ComponentFactory, embedder embeddings.TCMImageEmbedder, imagePath, imageType string, topK int, useReranker bool) ([]models.SearchResult, error) {
	// 嵌入图像
	embeddings, err := embedder.EmbedImages(ctx, []string{imagePath})
	if err != nil {
		return nil, fmt.Errorf("嵌入图像失败: %v", err)
	}
	
	if len(embeddings) == 0 {
		return nil, fmt.Errorf("嵌入图像失败: 没有生成嵌入向量")
	}
	
	// 获取向量存储
	vectorStore, err := factoryInstance.GetVectorStore("default")
	if err != nil {
		return nil, fmt.Errorf("获取向量存储失败: %v", err)
	}
	
	// 设置过滤条件
	filter := map[string]interface{}{
		"tcm_domain": "中医诊断",
	}
	
	if imageType == "tongue" {
		filter["tcm_image_category"] = "舌诊图像"
	} else if imageType == "face" {
		filter["tcm_image_category"] = "面诊图像"
	}
	
	// 执行向量搜索
	results, err := vectorStore.Search(ctx, embeddings[0], topK, filter)
	if err != nil {
		return nil, fmt.Errorf("向量搜索失败: %v", err)
	}
	
	// 如果需要重排序
	if useReranker && len(results) > 0 {
		metadata := &models.DocumentMetadata{Properties: make(map[string]interface{})}
		embedder.EnhanceTCMImageMetadata(ctx, metadata, imagePath)
		
		// 构建伪查询文本
		var queryText string
		if imageType == "tongue" {
			queryText = fmt.Sprintf("舌诊分析 舌色%s 舌苔%s 舌形%s",
				metadata.Properties["tongue_color"],
				metadata.Properties["coating_color"],
				metadata.Properties["tongue_shape"])
		} else if imageType == "face" {
			queryText = fmt.Sprintf("面诊分析 面色%s", metadata.Properties["face_color"])
		}
		
		// 获取重排序器
		reranker, err := factoryInstance.GetReranker("cross-encoder")
		if err != nil {
			fmt.Printf("警告: 获取重排序器失败，将使用原始结果: %v\n", err)
		} else {
			// 执行重排序
			options := map[string]interface{}{
				"top_k":       topK,
				"tcm_specific": true,
				"domain":      "tcm",
			}
			
			rerankedResults, err := reranker.Rerank(ctx, queryText, results, options)
			if err != nil {
				fmt.Printf("警告: 重排序失败，将使用原始结果: %v\n", err)
			} else {
				results = rerankedResults
			}
		}
	}
	
	return results, nil
}

// writeResult 将结果写入文件
func writeResult(result *TestResult, resultPath string) {
	// 如果目录不存在，则创建
	resultDir := filepath.Dir(resultPath)
	if resultDir != "" && resultDir != "." {
		if err := os.MkdirAll(resultDir, 0755); err != nil {
			fmt.Printf("创建结果目录失败: %v\n", err)
			return
		}
	}
	
	// 序列化结果
	resultJSON, err := json.MarshalIndent(result, "", "  ")
	if err != nil {
		fmt.Printf("结果序列化失败: %v\n", err)
		return
	}
	
	// 写入文件
	if err := os.WriteFile(resultPath, resultJSON, 0644); err != nil {
		fmt.Printf("写入结果文件失败: %v\n", err)
		return
	}
	
	fmt.Printf("结果已写入: %s\n", resultPath)
} 