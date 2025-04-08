package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"math/rand"
	"net/http"
	"os"
	"time"
)

const (
	// 测试服务的默认URL
	serviceURL = "http://localhost:8080/api/feedback"
	
	// 批量测试URL
	batchTestURL = "http://localhost:8080/api/admin/adaptive/test"
	
	// 获取参数URL
	getParametersURL = "http://localhost:8080/api/admin/adaptive/parameters"
	
	// 运行学习循环URL
	runLearningURL = "http://localhost:8080/api/admin/adaptive/learn"
)

// FeedbackRequest 反馈请求结构
type FeedbackRequest struct {
	UserID        string                 `json:"user_id"`
	SessionID     string                 `json:"session_id,omitempty"`
	Query         string                 `json:"query"`
	Answer        string                 `json:"answer"`
	FeedbackType  string                 `json:"feedback_type"`
	FeedbackText  string                 `json:"feedback_text,omitempty"`
	CorrectAnswer string                 `json:"correct_answer,omitempty"`
	RelevanceScore int                   `json:"relevance_score,omitempty"`
	Metadata      map[string]interface{} `json:"metadata,omitempty"`
}

// BatchTestRequest 批量测试请求
type BatchTestRequest struct {
	FeedbackCount     int     `json:"feedback_count"`
	PositiveRatio     float64 `json:"positive_ratio"`
	NegativeRatio     float64 `json:"negative_ratio"`
	CorrectionRatio   float64 `json:"correction_ratio"`
	RelevanceRatio    float64 `json:"relevance_ratio"`
	RandomSeed        int64   `json:"random_seed,omitempty"`
	RunLearningCycle  bool    `json:"run_learning_cycle"`
	ReturnNewParams   bool    `json:"return_new_params"`
}

// TestResult 测试结果
type TestResult struct {
	Success              bool                   `json:"success"`
	Message              string                 `json:"message"`
	FeedbackProcessed    int                    `json:"feedback_processed"`
	OriginalParameters   map[string]interface{} `json:"original_parameters,omitempty"`
	UpdatedParameters    map[string]interface{} `json:"updated_parameters,omitempty"`
	ParameterChanges     map[string]interface{} `json:"parameter_changes,omitempty"`
	ProcessingTimeMs     int64                  `json:"processing_time_ms"`
}

// 命令行参数
var (
	feedbackType  = flag.String("type", "positive", "反馈类型: positive, negative, correction, relevance, missing_context, factual_error, not_complete, too_verbose, too_simplified")
	query         = flag.String("query", "", "用户查询")
	answer        = flag.String("answer", "", "系统回答")
	feedbackText  = flag.String("feedback", "", "反馈文本内容")
	correctAnswer = flag.String("correct", "", "正确答案 (用于correction类型)")
	relevanceScore = flag.Int("score", 0, "相关性评分 (1-5, 用于relevance类型)")
	userID        = flag.String("user", "test_user", "用户ID")
	sessionID     = flag.String("session", "", "会话ID")
	batchMode     = flag.Bool("batch", false, "启用批量测试模式")
	feedbackCount = flag.Int("count", 100, "批量测试的反馈数量")
	positiveRatio = flag.Float64("positive", 0.4, "正面反馈比例")
	negativeRatio = flag.Float64("negative", 0.3, "负面反馈比例")
	correctionRatio = flag.Float64("correction", 0.2, "更正反馈比例")
	relevanceRatio = flag.Float64("relevance", 0.1, "相关性反馈比例")
	randomSeed    = flag.Int64("seed", 0, "随机种子 (0表示使用当前时间)")
	runLearning   = flag.Bool("learn", true, "运行学习循环")
	showParams    = flag.Bool("params", true, "显示参数变化")
	outputFile    = flag.String("output", "", "输出文件")
	serviceURLFlag = flag.String("url", serviceURL, "服务URL")
)

func main() {
	flag.Parse()
	
	// 设置随机种子
	if *randomSeed == 0 {
		*randomSeed = time.Now().UnixNano()
	}
	rand.Seed(*randomSeed)
	
	var result interface{}
	var err error
	
	if *batchMode {
		// 批量测试模式
		result, err = runBatchTest()
	} else {
		// 单次反馈测试
		result, err = submitFeedback()
	}
	
	if err != nil {
		fmt.Printf("错误: %v\n", err)
		os.Exit(1)
	}
	
	// 格式化输出结果
	resultJSON, err := json.MarshalIndent(result, "", "  ")
	if err != nil {
		fmt.Printf("格式化结果失败: %v\n", err)
		os.Exit(1)
	}
	
	// 输出结果
	if *outputFile != "" {
		err = os.WriteFile(*outputFile, resultJSON, 0644)
		if err != nil {
			fmt.Printf("写入输出文件失败: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("结果已写入: %s\n", *outputFile)
	} else {
		fmt.Println(string(resultJSON))
	}
}

// submitFeedback 提交单次反馈
func submitFeedback() (map[string]interface{}, error) {
	// 基本验证
	if *query == "" {
		return nil, fmt.Errorf("必须提供查询参数 (-query)")
	}
	
	if *answer == "" {
		return nil, fmt.Errorf("必须提供回答参数 (-answer)")
	}
	
	// 构建反馈请求
	feedbackReq := FeedbackRequest{
		UserID:        *userID,
		SessionID:     *sessionID,
		Query:         *query,
		Answer:        *answer,
		FeedbackType:  *feedbackType,
		FeedbackText:  *feedbackText,
		CorrectAnswer: *correctAnswer,
		RelevanceScore: *relevanceScore,
		Metadata:      map[string]interface{}{
			"test": true,
			"timestamp": time.Now().Format(time.RFC3339),
		},
	}
	
	// 转换为JSON
	jsonData, err := json.Marshal(feedbackReq)
	if err != nil {
		return nil, fmt.Errorf("JSON序列化失败: %v", err)
	}
	
	// 发送请求
	resp, err := http.Post(*serviceURLFlag, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("发送请求失败: %v", err)
	}
	defer resp.Body.Close()
	
	// 读取响应
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("读取响应失败: %v", err)
	}
	
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("服务返回错误: %s - %s", resp.Status, string(body))
	}
	
	// 解析响应
	var result map[string]interface{}
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, fmt.Errorf("解析响应失败: %v", err)
	}
	
	return result, nil
}

// runBatchTest 运行批量测试
func runBatchTest() (*TestResult, error) {
	// 构建批量测试请求
	batchReq := BatchTestRequest{
		FeedbackCount:    *feedbackCount,
		PositiveRatio:    *positiveRatio,
		NegativeRatio:    *negativeRatio,
		CorrectionRatio:  *correctionRatio,
		RelevanceRatio:   *relevanceRatio,
		RandomSeed:       *randomSeed,
		RunLearningCycle: *runLearning,
		ReturnNewParams:  *showParams,
	}
	
	// 转换为JSON
	jsonData, err := json.Marshal(batchReq)
	if err != nil {
		return nil, fmt.Errorf("JSON序列化失败: %v", err)
	}
	
	// 发送请求
	resp, err := http.Post(batchTestURL, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("发送请求失败: %v", err)
	}
	defer resp.Body.Close()
	
	// 读取响应
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("读取响应失败: %v", err)
	}
	
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("服务返回错误: %s - %s", resp.Status, string(body))
	}
	
	// 解析响应
	var result TestResult
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, fmt.Errorf("解析响应失败: %v", err)
	}
	
	return &result, nil
}

// getSystemParameters 获取系统参数
func getSystemParameters() (map[string]interface{}, error) {
	resp, err := http.Get(getParametersURL)
	if err != nil {
		return nil, fmt.Errorf("获取参数失败: %v", err)
	}
	defer resp.Body.Close()
	
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("读取响应失败: %v", err)
	}
	
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("服务返回错误: %s - %s", resp.Status, string(body))
	}
	
	var result map[string]interface{}
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, fmt.Errorf("解析响应失败: %v", err)
	}
	
	return result, nil
}

// generateRandomFeedback 生成随机反馈数据
func generateRandomFeedback() FeedbackRequest {
	// 示例查询和回答列表
	queries := []string{
		"黄芪的功效是什么？",
		"如何改善睡眠质量？",
		"舌苔发白是什么原因？",
		"中医如何调理脾胃？",
		"针灸对颈椎病有效吗？",
		"冬季养生的关键点是什么？",
		"如何判断自己的体质类型？",
		"反复感冒怎么调理？",
		"中医怎么看待高血压？",
		"艾灸有什么作用和禁忌？",
	}
	
	answers := []string{
		"黄芪具有补气、升阳、固表、利水、生肌的功效。主要用于气虚乏力、食少便溏、中气下陷、久泻脱肛、表虚自汗、气虚水肿、慢性肾炎蛋白尿、糖尿病、血小板减少及气虚血瘀证等。",
		"改善睡眠质量的方法包括：保持规律作息、睡前放松、创造良好睡眠环境、避免睡前饮食刺激、适量运动、减少电子产品使用等。从中医角度，还可以按摩穴位如内关、安眠等。",
		"舌苔发白主要是脾胃湿热或寒凉所致。如果是厚腻白苔，多为湿邪困脾；薄白苔多为风寒外感或脾胃虚寒。需要根据其他症状综合辨证。",
		"中医调理脾胃主要从饮食调理、情志调理、作息调理、穴位按摩、中药调理等方面入手。关键在于健脾化湿、和胃降逆，适合脾胃虚弱者的食物有山药、莲子、薏米等。",
		"针灸对颈椎病有一定疗效，主要通过疏通经络、调和气血、缓解肌肉痉挛来减轻疼痛。常用穴位包括风池、天柱、大椎等。但需要正规医师操作，效果因人而异。",
	}
	
	feedbackTypes := []string{"positive", "negative", "correction", "relevance", "missing_context", "factual_error", "not_complete", "too_verbose"}
	feedbackTexts := []string{
		"回答很有帮助，谢谢！",
		"这个答案不太准确。",
		"信息不完整，缺少重要内容。",
		"答案太笼统，希望有更详细的解释。",
		"这个回答包含错误信息。",
		"没有回答我的问题要点。",
	}
	
	correctAnswers := []string{
		"黄芪的功效主要有补气固表、利水消肿、生肌止血等，常用于治疗气虚乏力、自汗、水肿等症状。现代研究表明其还具有增强免疫力、降血压、抗衰老等作用。",
		"中医调理脾胃的方法包括饮食调理（少食生冷、定时定量）、情志调理（保持心情舒畅）、穴位按摩（揉足三里、中脘等穴位）以及药膳调理（如山药薏米粥、党参茯苓粥等）。",
		"针灸治疗颈椎病主要通过刺激特定穴位，如风池、天柱、大椎、肩井等，达到疏经通络、行气活血、消肿止痛的效果。临床研究显示对缓解颈部僵硬、疼痛及放射痛有显著效果，但需要规范操作并结合其他治疗方法。",
	}
	
	// 随机生成反馈
	queryIndex := rand.Intn(len(queries))
	query := queries[queryIndex]
	answer := ""
	
	if queryIndex < len(answers) {
		answer = answers[queryIndex]
	} else {
		answer = answers[rand.Intn(len(answers))]
	}
	
	feedbackType := feedbackTypes[rand.Intn(len(feedbackTypes))]
	feedbackText := feedbackTexts[rand.Intn(len(feedbackTexts))]
	
	var correctAnswer string
	if feedbackType == "correction" && len(correctAnswers) > 0 {
		correctAnswer = correctAnswers[rand.Intn(len(correctAnswers))]
	}
	
	var relevanceScore int
	if feedbackType == "relevance" {
		relevanceScore = rand.Intn(5) + 1 // 1-5分
	}
	
	return FeedbackRequest{
		UserID:        fmt.Sprintf("test_user_%d", rand.Intn(10)),
		SessionID:     fmt.Sprintf("test_session_%d", rand.Intn(100)),
		Query:         query,
		Answer:        answer,
		FeedbackType:  feedbackType,
		FeedbackText:  feedbackText,
		CorrectAnswer: correctAnswer,
		RelevanceScore: relevanceScore,
		Metadata: map[string]interface{}{
			"test":      true,
			"timestamp": time.Now().Format(time.RFC3339),
			"test_id":   rand.Intn(1000),
		},
	}
} 