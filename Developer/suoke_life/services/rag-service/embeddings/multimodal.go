package embeddings

import (
	"context"
	"fmt"
	"strings"
	"time"

	"github.com/suoke/suoke_life/services/rag-service/internal/models"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils"
)

// MultiModalEmbedder 多模态嵌入接口
type MultiModalEmbedder interface {
	// Name 返回嵌入模型名称
	Name() string
	
	// Type 返回嵌入类型
	Type() string
	
	// EmbedText 对文本进行嵌入
	EmbedText(ctx context.Context, texts []string) ([][]float32, error)
	
	// EmbedImage 对图像进行嵌入
	EmbedImage(ctx context.Context, imagePaths []string) ([][]float32, error)
	
	// EmbedAudio 对音频进行嵌入
	EmbedAudio(ctx context.Context, audioPaths []string) ([][]float32, error)
	
	// EmbedMultiModal 对多模态内容进行嵌入
	EmbedMultiModal(ctx context.Context, request models.EmbeddingRequest) (*models.EmbeddingResponse, error)
	
	// Dimensions 返回嵌入向量维度
	Dimensions() int
	
	// Initialize 初始化嵌入模型
	Initialize(ctx context.Context) error
	
	// Close 关闭嵌入模型
	Close() error
}

// MultiModalEmbedding 多模态嵌入实现
type MultiModalEmbedding struct {
	// 支持的嵌入类型
	supportedTypes map[string]bool
	
	// 文本嵌入模型
	textEmbedder Embedder
	
	// 图像嵌入模型
	imageEmbedder ImageEmbedder
	
	// 音频嵌入模型
	audioEmbedder AudioEmbedder
	
	// 嵌入向量维度
	dimensions map[string]int
	
	// 日志器
	logger utils.Logger
	
	// 模型名称
	modelName string
	
	// 中医知识增强
	tcmEnhancer TCMEmbeddingEnhancer
}

// ImageEmbedder 图像嵌入接口
type ImageEmbedder interface {
	// Name 返回嵌入模型名称
	Name() string
	
	// EmbedImage 对图像进行嵌入
	EmbedImage(ctx context.Context, imagePaths []string) ([][]float32, error)
	
	// Dimensions 返回嵌入向量维度
	Dimensions() int
	
	// Initialize 初始化嵌入模型
	Initialize(ctx context.Context) error
	
	// Close 关闭嵌入模型
	Close() error
}

// AudioEmbedder 音频嵌入接口
type AudioEmbedder interface {
	// Name 返回嵌入模型名称
	Name() string
	
	// EmbedAudio 对音频进行嵌入
	EmbedAudio(ctx context.Context, audioPaths []string) ([][]float32, error)
	
	// Dimensions 返回嵌入向量维度
	Dimensions() int
	
	// Initialize 初始化嵌入模型
	Initialize(ctx context.Context) error
	
	// Close 关闭嵌入模型
	Close() error
}

// TCMEmbeddingEnhancer 中医嵌入增强接口
type TCMEmbeddingEnhancer interface {
	// EnhanceText 增强文本嵌入
	EnhanceText(ctx context.Context, text string) string
	
	// EnhanceImageEmbedding 增强图像嵌入（如舌诊、面诊图像）
	EnhanceImageEmbedding(ctx context.Context, embedding []float32, imageType string) []float32
	
	// EnhanceAudioEmbedding 增强音频嵌入（如脉诊音频）
	EnhanceAudioEmbedding(ctx context.Context, embedding []float32, audioType string) []float32
	
	// Initialize 初始化增强器
	Initialize(ctx context.Context) error
}

// NewMultiModalEmbedding 创建多模态嵌入
func NewMultiModalEmbedding(
	textEmbedder Embedder,
	imageEmbedder ImageEmbedder,
	audioEmbedder AudioEmbedder,
	tcmEnhancer TCMEmbeddingEnhancer,
	logger utils.Logger,
) *MultiModalEmbedding {
	if logger == nil {
		logger = utils.NewNoopLogger()
	}
	
	supportedTypes := make(map[string]bool)
	dimensions := make(map[string]int)
	
	if textEmbedder != nil {
		supportedTypes["text"] = true
		dimensions["text"] = textEmbedder.Dimensions()
	}
	
	if imageEmbedder != nil {
		supportedTypes["image"] = true
		dimensions["image"] = imageEmbedder.Dimensions()
	}
	
	if audioEmbedder != nil {
		supportedTypes["audio"] = true
		dimensions["audio"] = audioEmbedder.Dimensions()
	}
	
	// 生成模型名称
	modelName := "multimodal"
	if textEmbedder != nil {
		modelName += "-" + textEmbedder.Name()
	}
	if imageEmbedder != nil {
		modelName += "-" + imageEmbedder.Name()
	}
	if audioEmbedder != nil {
		modelName += "-" + audioEmbedder.Name()
	}
	
	return &MultiModalEmbedding{
		supportedTypes: supportedTypes,
		textEmbedder:   textEmbedder,
		imageEmbedder:  imageEmbedder,
		audioEmbedder:  audioEmbedder,
		dimensions:     dimensions,
		logger:         logger,
		modelName:      modelName,
		tcmEnhancer:    tcmEnhancer,
	}
}

// Name 返回嵌入模型名称
func (e *MultiModalEmbedding) Name() string {
	return e.modelName
}

// Type 返回嵌入类型
func (e *MultiModalEmbedding) Type() string {
	return "multimodal"
}

// EmbedText 对文本进行嵌入
func (e *MultiModalEmbedding) EmbedText(ctx context.Context, texts []string) ([][]float32, error) {
	if e.textEmbedder == nil {
		return nil, fmt.Errorf("文本嵌入模型未配置")
	}
	
	// 如果配置了中医增强器，对文本进行增强
	if e.tcmEnhancer != nil {
		enhancedTexts := make([]string, len(texts))
		for i, text := range texts {
			enhancedTexts[i] = e.tcmEnhancer.EnhanceText(ctx, text)
		}
		texts = enhancedTexts
	}
	
	return e.textEmbedder.Embed(ctx, texts)
}

// EmbedImage 对图像进行嵌入
func (e *MultiModalEmbedding) EmbedImage(ctx context.Context, imagePaths []string) ([][]float32, error) {
	if e.imageEmbedder == nil {
		return nil, fmt.Errorf("图像嵌入模型未配置")
	}
	
	embeddings, err := e.imageEmbedder.EmbedImage(ctx, imagePaths)
	if err != nil {
		return nil, err
	}
	
	// 如果配置了中医增强器，对图像嵌入进行增强
	if e.tcmEnhancer != nil {
		for i, embedding := range embeddings {
			// 基于文件路径判断图像类型（舌诊、面诊等）
			imageType := e.inferImageType(imagePaths[i])
			embeddings[i] = e.tcmEnhancer.EnhanceImageEmbedding(ctx, embedding, imageType)
		}
	}
	
	return embeddings, nil
}

// EmbedAudio 对音频进行嵌入
func (e *MultiModalEmbedding) EmbedAudio(ctx context.Context, audioPaths []string) ([][]float32, error) {
	if e.audioEmbedder == nil {
		return nil, fmt.Errorf("音频嵌入模型未配置")
	}
	
	embeddings, err := e.audioEmbedder.EmbedAudio(ctx, audioPaths)
	if err != nil {
		return nil, err
	}
	
	// 如果配置了中医增强器，对音频嵌入进行增强
	if e.tcmEnhancer != nil {
		for i, embedding := range embeddings {
			// 基于文件路径判断音频类型（脉诊等）
			audioType := e.inferAudioType(audioPaths[i])
			embeddings[i] = e.tcmEnhancer.EnhanceAudioEmbedding(ctx, embedding, audioType)
		}
	}
	
	return embeddings, nil
}

// EmbedMultiModal 对多模态内容进行嵌入
func (e *MultiModalEmbedding) EmbedMultiModal(ctx context.Context, request models.EmbeddingRequest) (*models.EmbeddingResponse, error) {
	startTime := time.Now()
	
	// 检查请求类型是否支持
	embeddingType := request.EmbeddingType
	if embeddingType == "" {
		embeddingType = "text" // 默认为文本
	}
	
	if !e.supportedTypes[embeddingType] {
		return nil, fmt.Errorf("不支持的嵌入类型: %s", embeddingType)
	}
	
	var embeddings [][]float32
	var err error
	
	// 根据类型选择嵌入方法
	switch embeddingType {
	case "text":
		embeddings, err = e.EmbedText(ctx, request.Texts)
	case "image":
		embeddings, err = e.EmbedImage(ctx, request.MediaPaths)
	case "audio":
		embeddings, err = e.EmbedAudio(ctx, request.MediaPaths)
	default:
		return nil, fmt.Errorf("未知的嵌入类型: %s", embeddingType)
	}
	
	if err != nil {
		return nil, err
	}
	
	// 构建响应
	response := &models.EmbeddingResponse{
		Embeddings:    embeddings,
		Model:         e.Name(),
		Dimensions:    e.Dimensions(),
		ProcessTime:   time.Since(startTime).Seconds(),
		EmbeddingType: embeddingType,
	}
	
	return response, nil
}

// Dimensions 返回嵌入向量维度
func (e *MultiModalEmbedding) Dimensions() int {
	// 返回文本嵌入的维度作为默认维度
	if dim, ok := e.dimensions["text"]; ok {
		return dim
	}
	
	// 如果没有文本嵌入，返回其他类型的维度
	for _, dim := range e.dimensions {
		return dim
	}
	
	return 0
}

// Initialize 初始化嵌入模型
func (e *MultiModalEmbedding) Initialize(ctx context.Context) error {
	e.logger.Info("初始化多模态嵌入模型", "model", e.modelName)
	
	// 初始化各个嵌入模型
	if e.textEmbedder != nil {
		if err := e.textEmbedder.Initialize(ctx); err != nil {
			return fmt.Errorf("初始化文本嵌入模型失败: %w", err)
		}
	}
	
	if e.imageEmbedder != nil {
		if err := e.imageEmbedder.Initialize(ctx); err != nil {
			return fmt.Errorf("初始化图像嵌入模型失败: %w", err)
		}
	}
	
	if e.audioEmbedder != nil {
		if err := e.audioEmbedder.Initialize(ctx); err != nil {
			return fmt.Errorf("初始化音频嵌入模型失败: %w", err)
		}
	}
	
	// 初始化中医增强器
	if e.tcmEnhancer != nil {
		if err := e.tcmEnhancer.Initialize(ctx); err != nil {
			return fmt.Errorf("初始化中医增强器失败: %w", err)
		}
	}
	
	return nil
}

// Close 关闭嵌入模型
func (e *MultiModalEmbedding) Close() error {
	// 关闭各个嵌入模型
	if e.textEmbedder != nil {
		if err := e.textEmbedder.Close(); err != nil {
			e.logger.Error("关闭文本嵌入模型失败", "error", err)
		}
	}
	
	if e.imageEmbedder != nil {
		if err := e.imageEmbedder.Close(); err != nil {
			e.logger.Error("关闭图像嵌入模型失败", "error", err)
		}
	}
	
	if e.audioEmbedder != nil {
		if err := e.audioEmbedder.Close(); err != nil {
			e.logger.Error("关闭音频嵌入模型失败", "error", err)
		}
	}
	
	return nil
}

// 推断图像类型
func (e *MultiModalEmbedding) inferImageType(imagePath string) string {
	lowerPath := strings.ToLower(imagePath)
	
	if strings.Contains(lowerPath, "tongue") || strings.Contains(lowerPath, "舌诊") {
		return "tongue" // 舌诊
	} else if strings.Contains(lowerPath, "face") || strings.Contains(lowerPath, "面诊") {
		return "face" // 面诊
	} else if strings.Contains(lowerPath, "pulse") || strings.Contains(lowerPath, "脉诊") {
		return "pulse" // 脉诊图像
	} else if strings.Contains(lowerPath, "skin") || strings.Contains(lowerPath, "皮肤") {
		return "skin" // 皮肤
	} else if strings.Contains(lowerPath, "eye") || strings.Contains(lowerPath, "眼诊") {
		return "eye" // 眼诊
	} else if strings.Contains(lowerPath, "ear") || strings.Contains(lowerPath, "耳诊") {
		return "ear" // 耳诊
	}
	
	return "general" // 默认为通用图像
}

// 推断音频类型
func (e *MultiModalEmbedding) inferAudioType(audioPath string) string {
	lowerPath := strings.ToLower(audioPath)
	
	if strings.Contains(lowerPath, "pulse") || strings.Contains(lowerPath, "脉诊") {
		return "pulse" // 脉诊音频
	} else if strings.Contains(lowerPath, "voice") || strings.Contains(lowerPath, "声诊") {
		return "voice" // 声诊
	} else if strings.Contains(lowerPath, "cough") || strings.Contains(lowerPath, "咳嗽") {
		return "cough" // 咳嗽
	} else if strings.Contains(lowerPath, "breathing") || strings.Contains(lowerPath, "呼吸") {
		return "breathing" // 呼吸
	}
	
	return "general" // 默认为通用音频
}

// SimpleTCMEmbeddingEnhancer 简单中医嵌入增强实现
type SimpleTCMEmbeddingEnhancer struct {
	// 中医术语库
	tcmTerms map[string]bool
	
	// 中医术语增强权重
	termWeights map[string]float32
	
	// 各类型图像增强参数
	imageEnhanceParams map[string]map[string]float32
	
	// 各类型音频增强参数
	audioEnhanceParams map[string]map[string]float32
	
	// 日志器
	logger utils.Logger
}

// NewSimpleTCMEmbeddingEnhancer 创建简单中医嵌入增强器
func NewSimpleTCMEmbeddingEnhancer(logger utils.Logger) *SimpleTCMEmbeddingEnhancer {
	if logger == nil {
		logger = utils.NewNoopLogger()
	}
	
	return &SimpleTCMEmbeddingEnhancer{
		tcmTerms:          make(map[string]bool),
		termWeights:       make(map[string]float32),
		imageEnhanceParams: make(map[string]map[string]float32),
		audioEnhanceParams: make(map[string]map[string]float32),
		logger:            logger,
	}
}

// EnhanceText 增强文本嵌入
func (e *SimpleTCMEmbeddingEnhancer) EnhanceText(ctx context.Context, text string) string {
	// 简单实现：在中医术语周围添加特殊标记
	// 实际应用中可以使用更复杂的语义增强方法
	
	// 遍历中医术语库，在文本中标记中医术语
	enhancedText := text
	for term := range e.tcmTerms {
		if strings.Contains(text, term) {
			enhancedText = strings.ReplaceAll(enhancedText, term, "[TCM]"+term+"[/TCM]")
		}
	}
	
	return enhancedText
}

// EnhanceImageEmbedding 增强图像嵌入
func (e *SimpleTCMEmbeddingEnhancer) EnhanceImageEmbedding(ctx context.Context, embedding []float32, imageType string) []float32 {
	// 简单实现：根据图像类型调整向量中的某些维度
	// 实际应用中可能需要更复杂的模型进行增强
	
	// 检查是否有该类型的增强参数
	params, ok := e.imageEnhanceParams[imageType]
	if !ok {
		return embedding
	}
	
	// 复制原始嵌入向量
	enhanced := make([]float32, len(embedding))
	copy(enhanced, embedding)
	
	// 根据参数调整嵌入向量
	for dim, weight := range params {
		dimIndex := 0
		fmt.Sscanf(dim, "%d", &dimIndex)
		if dimIndex >= 0 && dimIndex < len(enhanced) {
			enhanced[dimIndex] *= weight
		}
	}
	
	return enhanced
}

// EnhanceAudioEmbedding 增强音频嵌入
func (e *SimpleTCMEmbeddingEnhancer) EnhanceAudioEmbedding(ctx context.Context, embedding []float32, audioType string) []float32 {
	// 简单实现：与图像嵌入增强类似
	
	// 检查是否有该类型的增强参数
	params, ok := e.audioEnhanceParams[audioType]
	if !ok {
		return embedding
	}
	
	// 复制原始嵌入向量
	enhanced := make([]float32, len(embedding))
	copy(enhanced, embedding)
	
	// 根据参数调整嵌入向量
	for dim, weight := range params {
		dimIndex := 0
		fmt.Sscanf(dim, "%d", &dimIndex)
		if dimIndex >= 0 && dimIndex < len(enhanced) {
			enhanced[dimIndex] *= weight
		}
	}
	
	return enhanced
}

// Initialize 初始化增强器
func (e *SimpleTCMEmbeddingEnhancer) Initialize(ctx context.Context) error {
	// 加载中医术语库
	e.loadTCMTerms()
	
	// 加载增强参数
	e.loadEnhanceParams()
	
	return nil
}

// 加载中医术语库
func (e *SimpleTCMEmbeddingEnhancer) loadTCMTerms() {
	// 示例：加载一些基本中医术语
	terms := []string{
		"阴阳", "五行", "气血", "脏腑", "经络", "津液", "精气神",
		"寒热", "虚实", "表里", "阴虚", "阳虚", "气虚", "血虚",
		"风寒", "风热", "湿热", "湿寒", "燥热", "痰湿", "瘀血",
		"舌诊", "脉诊", "面诊", "望闻问切", "辨证论治",
	}
	
	for _, term := range terms {
		e.tcmTerms[term] = true
		e.termWeights[term] = 1.2 // 默认权重
	}
}

// 加载增强参数
func (e *SimpleTCMEmbeddingEnhancer) loadEnhanceParams() {
	// 示例：为不同类型的图像配置增强参数
	e.imageEnhanceParams["tongue"] = map[string]float32{
		"10": 1.5,  // 假设第10维与舌像颜色相关
		"20": 1.3,  // 假设第20维与舌苔特征相关
	}
	
	e.imageEnhanceParams["face"] = map[string]float32{
		"15": 1.4,  // 假设第15维与脸色相关
		"25": 1.2,  // 假设第25维与面部特征相关
	}
	
	// 示例：为不同类型的音频配置增强参数
	e.audioEnhanceParams["pulse"] = map[string]float32{
		"5": 1.6,   // 假设第5维与脉象频率相关
		"15": 1.4,  // 假设第15维与脉象强度相关
	}
	
	e.audioEnhanceParams["voice"] = map[string]float32{
		"8": 1.5,   // 假设第8维与声音特征相关
		"18": 1.3,  // 假设第18维与音调相关
	}
} 