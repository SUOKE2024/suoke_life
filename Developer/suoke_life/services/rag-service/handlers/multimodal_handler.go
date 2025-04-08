package handlers

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/suoke/suoke_life/services/rag-service/factory"
	"github.com/suoke/suoke_life/services/rag-service/internal/models"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils"
)

// MultimodalHandler 多模态处理器
type MultimodalHandler struct {
	// 组件工厂
	factory *factory.ComponentFactory
	
	// 日志器
	logger utils.Logger
	
	// 缓存管理器
	cacheManager utils.CacheManager
	
	// 临时文件目录
	tempDir string
	
	// 超时时间
	timeout time.Duration
}

// ImageSearchRequest 图像搜索请求
type ImageSearchRequest struct {
	// 图片Base64或URL
	ImageData string `json:"image_data,omitempty"`
	
	// 图片URL
	ImageURL string `json:"image_url,omitempty"`
	
	// 返回结果数量
	TopK int `json:"top_k,omitempty"`
	
	// 图像类型 (舌诊、面诊等)
	Type string `json:"type,omitempty"`
	
	// 用户ID
	UserID string `json:"user_id,omitempty"`
	
	// 附加文本
	Text string `json:"text,omitempty"`
	
	// 是否进行中医特征分析
	AnalyzeTCM bool `json:"analyze_tcm,omitempty"`
	
	// 是否应用重排序
	UseRerank bool `json:"use_rerank,omitempty"`
	
	// 是否使用缓存
	UseCache bool `json:"use_cache,omitempty"`
	
	// 额外选项
	ExtraOptions map[string]interface{} `json:"extra_options,omitempty"`
}

// AudioSearchRequest 音频搜索请求
type AudioSearchRequest struct {
	// 音频Base64或URL
	AudioData string `json:"audio_data,omitempty"`
	
	// 音频URL
	AudioURL string `json:"audio_url,omitempty"`
	
	// 返回结果数量
	TopK int `json:"top_k,omitempty"`
	
	// 音频类型 (方言、脉诊等)
	Type string `json:"type,omitempty"`
	
	// 用户ID
	UserID string `json:"user_id,omitempty"`
	
	// 附加文本
	Text string `json:"text,omitempty"`
	
	// 是否转录音频
	Transcribe bool `json:"transcribe,omitempty"`
	
	// 是否应用重排序
	UseRerank bool `json:"use_rerank,omitempty"`
	
	// 是否使用缓存
	UseCache bool `json:"use_cache,omitempty"`
	
	// 额外选项
	ExtraOptions map[string]interface{} `json:"extra_options,omitempty"`
}

// MultimodalSearchResponse 多模态搜索响应
type MultimodalSearchResponse struct {
	// 检索结果
	Results []SearchResult `json:"results"`
	
	// 分析结果
	Analysis map[string]interface{} `json:"analysis,omitempty"`
	
	// 搜索统计信息
	Stats SearchStats `json:"stats"`
	
	// 错误信息
	Error string `json:"error,omitempty"`
}

// NewMultimodalHandler 创建多模态处理器
func NewMultimodalHandler(factoryInstance *factory.ComponentFactory, logger utils.Logger, cacheManager utils.CacheManager) *MultimodalHandler {
	if logger == nil {
		logger = utils.NewNoopLogger()
	}
	
	if cacheManager == nil {
		cacheManager = utils.NewNoopCacheManager()
	}
	
	// 创建临时目录
	tempDir := filepath.Join(os.TempDir(), "suoke_rag_multimodal")
	if err := os.MkdirAll(tempDir, 0755); err != nil {
		logger.Error("创建临时目录失败", "error", err)
	}
	
	return &MultimodalHandler{
		factory:      factoryInstance,
		logger:       logger,
		cacheManager: cacheManager,
		tempDir:      tempDir,
		timeout:      30 * time.Second,
	}
}

// HandleImageSearch 处理图像搜索请求
func (h *MultimodalHandler) HandleImageSearch(c *gin.Context) {
	// 绑定请求参数
	var request ImageSearchRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": fmt.Sprintf("无效的请求参数: %v", err)})
		return
	}
	
	// 设置默认值
	if request.TopK <= 0 {
		request.TopK = 10
	}
	
	if request.ExtraOptions == nil {
		request.ExtraOptions = make(map[string]interface{})
	}
	
	// 检查图像数据是否存在
	if request.ImageData == "" && request.ImageURL == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "必须提供图像数据或URL"})
		return
	}
	
	// 生成缓存键
	var cacheKey string
	if request.UseCache {
		if request.ImageURL != "" {
			cacheKey = fmt.Sprintf("imgsearch:%s:%s:%d:%t", request.ImageURL, request.Type, request.TopK, request.UseRerank)
		} else {
			// 由于ImageData可能很大，使用其哈希值作为缓存键
			cacheKey = fmt.Sprintf("imgsearch:%s:%s:%d:%t", utils.Sha256(request.ImageData), request.Type, request.TopK, request.UseRerank)
		}
		
		// 检查缓存
		if cachedData, found := h.cacheManager.Get(cacheKey); found {
			var response MultimodalSearchResponse
			if err := json.Unmarshal([]byte(cachedData), &response); err == nil {
				response.Stats.CacheHit = true
				c.JSON(http.StatusOK, response)
				return
			}
		}
	}
	
	// 创建上下文
	ctx, cancel := context.WithTimeout(context.Background(), h.timeout)
	defer cancel()
	
	// 执行图像搜索
	response, err := h.performImageSearch(ctx, request)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("图像搜索失败: %v", err)})
		return
	}
	
	// 缓存结果
	if request.UseCache && cacheKey != "" {
		if respData, err := json.Marshal(response); err == nil {
			h.cacheManager.Set(cacheKey, string(respData), 10*time.Minute)
		}
	}
	
	c.JSON(http.StatusOK, response)
}

// HandleAudioSearch 处理音频搜索请求
func (h *MultimodalHandler) HandleAudioSearch(c *gin.Context) {
	// 绑定请求参数
	var request AudioSearchRequest
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": fmt.Sprintf("无效的请求参数: %v", err)})
		return
	}
	
	// 设置默认值
	if request.TopK <= 0 {
		request.TopK = 10
	}
	
	if request.ExtraOptions == nil {
		request.ExtraOptions = make(map[string]interface{})
	}
	
	// 检查音频数据是否存在
	if request.AudioData == "" && request.AudioURL == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "必须提供音频数据或URL"})
		return
	}
	
	// 生成缓存键
	var cacheKey string
	if request.UseCache {
		if request.AudioURL != "" {
			cacheKey = fmt.Sprintf("audiosearch:%s:%s:%d:%t", request.AudioURL, request.Type, request.TopK, request.UseRerank)
		} else {
			// 使用哈希值作为缓存键
			cacheKey = fmt.Sprintf("audiosearch:%s:%s:%d:%t", utils.Sha256(request.AudioData), request.Type, request.TopK, request.UseRerank)
		}
		
		// 检查缓存
		if cachedData, found := h.cacheManager.Get(cacheKey); found {
			var response MultimodalSearchResponse
			if err := json.Unmarshal([]byte(cachedData), &response); err == nil {
				response.Stats.CacheHit = true
				c.JSON(http.StatusOK, response)
				return
			}
		}
	}
	
	// 创建上下文
	ctx, cancel := context.WithTimeout(context.Background(), h.timeout)
	defer cancel()
	
	// 执行音频搜索
	response, err := h.performAudioSearch(ctx, request)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("音频搜索失败: %v", err)})
		return
	}
	
	// 缓存结果
	if request.UseCache && cacheKey != "" {
		if respData, err := json.Marshal(response); err == nil {
			h.cacheManager.Set(cacheKey, string(respData), 10*time.Minute)
		}
	}
	
	c.JSON(http.StatusOK, response)
}

// performImageSearch 执行图像搜索
func (h *MultimodalHandler) performImageSearch(ctx context.Context, request ImageSearchRequest) (*MultimodalSearchResponse, error) {
	startTime := time.Now()
	
	// 创建响应
	response := &MultimodalSearchResponse{
		Results: make([]SearchResult, 0),
		Analysis: make(map[string]interface{}),
		Stats: SearchStats{
			ExtraStats: make(map[string]interface{}),
		},
	}
	
	// 下载或解码图像
	imagePath, err := h.getImageFile(request)
	if err != nil {
		return nil, fmt.Errorf("获取图像文件失败: %w", err)
	}
	defer os.Remove(imagePath) // 清理临时文件
	
	// 获取合适的图像嵌入器
	var embedder interface{} // 可能是ImageEmbedder或MultiModalEmbedder
	var embeddingType string
	
	if request.Type == "tongue" || request.Type == "face" || request.AnalyzeTCM {
		// 使用中医图像嵌入器
		embedder, err = h.factory.GetImageEmbedder("tcm")
		embeddingType = "tcm_image"
	} else {
		// 使用通用图像嵌入器
		embedder, err = h.factory.GetImageEmbedder("default")
		embeddingType = "image"
	}
	
	if err != nil {
		return nil, fmt.Errorf("获取图像嵌入器失败: %w", err)
	}
	
	// 处理附加文本
	var textEmbedding []float32
	var combinedEmbedding []float32
	
	// 创建图像嵌入
	var imageEmbedding []float32
	if embeddingType == "tcm_image" {
		tcmEmbedder := embedder.(TCMImageEmbedder)
		embeddings, err := tcmEmbedder.EmbedImages(ctx, []string{imagePath})
		if err != nil {
			return nil, fmt.Errorf("嵌入图像失败: %w", err)
		}
		
		if len(embeddings) > 0 {
			imageEmbedding = embeddings[0]
		}
		
		// 进行中医图像分析
		metadata := &models.DocumentMetadata{Properties: make(map[string]interface{})}
		tcmEmbedder.EnhanceTCMImageMetadata(ctx, metadata, imagePath)
		
		// 添加分析结果
		response.Analysis["tcm_image_type"] = metadata.Properties["tcm_image_type"]
		response.Analysis["tcm_image_category"] = metadata.Properties["tcm_image_category"]
		
		// 添加具体的舌诊或面诊分析
		if metadata.Properties["tcm_image_category"] == "舌诊图像" {
			if metadata.Properties["tongue_color"] != nil {
				response.Analysis["tongue_color"] = metadata.Properties["tongue_color"]
			}
			if metadata.Properties["coating_color"] != nil {
				response.Analysis["coating_color"] = metadata.Properties["coating_color"]
			}
			if metadata.Properties["tongue_shape"] != nil {
				response.Analysis["tongue_shape"] = metadata.Properties["tongue_shape"]
			}
		} else if metadata.Properties["tcm_image_category"] == "面诊图像" {
			if metadata.Properties["face_color"] != nil {
				response.Analysis["face_color"] = metadata.Properties["face_color"]
			}
		}
	} else {
		// 通用图像嵌入
		stdEmbedder := embedder.(ImageEmbedder)
		embeddings, err := stdEmbedder.EmbedImages(ctx, []string{imagePath})
		if err != nil {
			return nil, fmt.Errorf("嵌入图像失败: %w", err)
		}
		
		if len(embeddings) > 0 {
			imageEmbedding = embeddings[0]
		}
	}
	
	// 如果有附加文本，创建文本嵌入
	if request.Text != "" {
		textEmbedder, err := h.factory.GetEmbedder("default")
		if err != nil {
			h.logger.Warn("获取文本嵌入器失败，将仅使用图像嵌入", "error", err)
		} else {
			textEmbedding, err = textEmbedder.EmbedQuery(ctx, request.Text)
			if err != nil {
				h.logger.Warn("嵌入文本失败，将仅使用图像嵌入", "error", err)
			}
		}
	}
	
	// 如果有文本嵌入，将图像和文本嵌入组合
	if textEmbedding != nil && len(textEmbedding) > 0 {
		// 简单加权平均
		textWeight := 0.3
		imageWeight := 0.7
		
		// 检查维度是否匹配
		if len(textEmbedding) == len(imageEmbedding) {
			combinedEmbedding = make([]float32, len(imageEmbedding))
			for i := 0; i < len(imageEmbedding); i++ {
				combinedEmbedding[i] = float32(imageWeight)*imageEmbedding[i] + float32(textWeight)*textEmbedding[i]
			}
		} else {
			// 如果维度不匹配，仅使用图像嵌入
			combinedEmbedding = imageEmbedding
			h.logger.Warn("文本和图像嵌入维度不匹配，仅使用图像嵌入")
		}
	} else {
		// 仅使用图像嵌入
		combinedEmbedding = imageEmbedding
	}
	
	// 获取向量存储
	vectorStore, err := h.factory.GetVectorStore("default")
	if err != nil {
		return nil, fmt.Errorf("获取向量存储失败: %w", err)
	}
	
	// 过滤器选项
	filterOptions := make(map[string]interface{})
	
	// 如果是中医图像，添加过滤条件
	if embeddingType == "tcm_image" {
		filterOptions["tcm_domain"] = "中医诊断"
		
		if request.Type == "tongue" {
			filterOptions["tcm_image_category"] = "舌诊图像"
		} else if request.Type == "face" {
			filterOptions["tcm_image_category"] = "面诊图像"
		}
	}
	
	// 执行向量搜索
	searchResults, err := vectorStore.Search(ctx, combinedEmbedding, request.TopK, filterOptions)
	if err != nil {
		return nil, fmt.Errorf("向量搜索失败: %w", err)
	}
	
	// 如果需要重排序
	if request.UseRerank && len(searchResults) > 0 && request.Text != "" {
		reranker, err := h.factory.GetReranker("cross-encoder")
		if err != nil {
			h.logger.Warn("获取重排序器失败，将使用原始结果", "error", err)
		} else {
			// 创建重排序选项
			options := map[string]interface{}{
				"top_k":     request.TopK,
				"user_id":   request.UserID,
				"use_cache": request.UseCache,
			}
			
			// 如果是中医领域
			if embeddingType == "tcm_image" {
				options["tcm_specific"] = true
				options["domain"] = "tcm"
			}
			
			// 执行重排序
			rerankedResults, rerankErr := reranker.Rerank(ctx, request.Text, searchResults, options)
			if rerankErr != nil {
				h.logger.Warn("重排序失败，将使用原始结果", "error", rerankErr)
			} else {
				searchResults = rerankedResults
				response.Stats.RerankedResults = len(rerankedResults)
			}
		}
	}
	
	// 转换结果
	for _, result := range searchResults {
		response.Results = append(response.Results, SearchResult{
			ID:       result.ID,
			Content:  result.Content,
			Score:    result.Score,
			Source:   result.Source,
			Metadata: result.Metadata.Properties,
			Snippet:  result.Snippet,
		})
	}
	
	// 计算统计信息
	response.Stats.ElapsedTime = time.Since(startTime)
	
	return response, nil
}

// performAudioSearch 执行音频搜索
func (h *MultimodalHandler) performAudioSearch(ctx context.Context, request AudioSearchRequest) (*MultimodalSearchResponse, error) {
	startTime := time.Now()
	
	// 创建响应
	response := &MultimodalSearchResponse{
		Results: make([]SearchResult, 0),
		Analysis: make(map[string]interface{}),
		Stats: SearchStats{
			ExtraStats: make(map[string]interface{}),
		},
	}
	
	// 下载或解码音频
	audioPath, err := h.getAudioFile(request)
	if err != nil {
		return nil, fmt.Errorf("获取音频文件失败: %w", err)
	}
	defer os.Remove(audioPath) // 清理临时文件
	
	// 获取合适的音频嵌入器
	var embedder interface{} // 可能是AudioEmbedder或MultiModalEmbedder
	var transcription string
	var embeddingType string
	
	if request.Type == "dialect" || request.Type == "pulse" {
		// 使用中医音频嵌入器
		embedder, err = h.factory.GetAudioEmbedder("tcm")
		embeddingType = "tcm_audio"
	} else {
		// 使用通用音频嵌入器
		embedder, err = h.factory.GetAudioEmbedder("default")
		embeddingType = "audio"
	}
	
	if err != nil {
		return nil, fmt.Errorf("获取音频嵌入器失败: %w", err)
	}
	
	// 如果需要转录
	if request.Transcribe {
		h.logger.Info("开始音频转录")
		// TODO: 实现音频转录功能
		transcription = "音频转录功能正在开发中"
		response.Analysis["transcription"] = transcription
	}
	
	// 创建音频嵌入
	var audioEmbedding []float32
	if embeddingType == "tcm_audio" {
		tcmEmbedder := embedder.(TCMAudioEmbedder)
		embeddings, err := tcmEmbedder.EmbedAudio(ctx, []string{audioPath})
		if err != nil {
			return nil, fmt.Errorf("嵌入音频失败: %w", err)
		}
		
		if len(embeddings) > 0 {
			audioEmbedding = embeddings[0]
		}
		
		// 进行中医音频分析
		metadata := &models.DocumentMetadata{Properties: make(map[string]interface{})}
		tcmEmbedder.EnhanceTCMAudioMetadata(ctx, metadata, audioPath)
		
		// 添加分析结果
		response.Analysis["tcm_audio_type"] = metadata.Properties["tcm_audio_type"]
		response.Analysis["tcm_audio_category"] = metadata.Properties["tcm_audio_category"]
		
		// 根据音频类型添加特定分析
		if metadata.Properties["tcm_audio_category"] == "方言音频" {
			// 添加方言分析结果
			response.Analysis["dialect_type"] = metadata.Properties["dialect_type"]
		} else if metadata.Properties["tcm_audio_category"] == "脉象音频" {
			// 添加脉象分析结果
			response.Analysis["pulse_type"] = metadata.Properties["pulse_type"]
		}
	} else {
		// 通用音频嵌入
		stdEmbedder := embedder.(AudioEmbedder)
		embeddings, err := stdEmbedder.EmbedAudio(ctx, []string{audioPath})
		if err != nil {
			return nil, fmt.Errorf("嵌入音频失败: %w", err)
		}
		
		if len(embeddings) > 0 {
			audioEmbedding = embeddings[0]
		}
	}
	
	// 如果有转录或附加文本，创建文本嵌入
	var textEmbedding []float32
	var combinedEmbedding []float32
	var textQuery string
	
	if transcription != "" {
		textQuery = transcription
	}
	
	if request.Text != "" {
		if textQuery != "" {
			textQuery += " " + request.Text
		} else {
			textQuery = request.Text
		}
	}
	
	if textQuery != "" {
		textEmbedder, err := h.factory.GetEmbedder("default")
		if err != nil {
			h.logger.Warn("获取文本嵌入器失败，将仅使用音频嵌入", "error", err)
		} else {
			textEmbedding, err = textEmbedder.EmbedQuery(ctx, textQuery)
			if err != nil {
				h.logger.Warn("嵌入文本失败，将仅使用音频嵌入", "error", err)
			}
		}
	}
	
	// 如果有文本嵌入，将音频和文本嵌入组合
	if textEmbedding != nil && len(textEmbedding) > 0 {
		// 简单加权平均
		textWeight := 0.4
		audioWeight := 0.6
		
		// 检查维度是否匹配
		if len(textEmbedding) == len(audioEmbedding) {
			combinedEmbedding = make([]float32, len(audioEmbedding))
			for i := 0; i < len(audioEmbedding); i++ {
				combinedEmbedding[i] = float32(audioWeight)*audioEmbedding[i] + float32(textWeight)*textEmbedding[i]
			}
		} else {
			// 如果维度不匹配，仅使用音频嵌入
			combinedEmbedding = audioEmbedding
			h.logger.Warn("文本和音频嵌入维度不匹配，仅使用音频嵌入")
		}
	} else {
		// 仅使用音频嵌入
		combinedEmbedding = audioEmbedding
	}
	
	// 获取向量存储
	vectorStore, err := h.factory.GetVectorStore("default")
	if err != nil {
		return nil, fmt.Errorf("获取向量存储失败: %w", err)
	}
	
	// 过滤器选项
	filterOptions := make(map[string]interface{})
	
	// 如果是中医音频，添加过滤条件
	if embeddingType == "tcm_audio" {
		filterOptions["tcm_domain"] = "中医诊断"
		
		if request.Type == "dialect" {
			filterOptions["tcm_audio_category"] = "方言音频"
		} else if request.Type == "pulse" {
			filterOptions["tcm_audio_category"] = "脉象音频"
		}
	}
	
	// 执行向量搜索
	searchResults, err := vectorStore.Search(ctx, combinedEmbedding, request.TopK, filterOptions)
	if err != nil {
		return nil, fmt.Errorf("向量搜索失败: %w", err)
	}
	
	// 如果需要重排序
	if request.UseRerank && len(searchResults) > 0 && textQuery != "" {
		reranker, err := h.factory.GetReranker("cross-encoder")
		if err != nil {
			h.logger.Warn("获取重排序器失败，将使用原始结果", "error", err)
		} else {
			// 创建重排序选项
			options := map[string]interface{}{
				"top_k":     request.TopK,
				"user_id":   request.UserID,
				"use_cache": request.UseCache,
			}
			
			// 如果是中医领域
			if embeddingType == "tcm_audio" {
				options["tcm_specific"] = true
				options["domain"] = "tcm"
			}
			
			// 执行重排序
			rerankedResults, rerankErr := reranker.Rerank(ctx, textQuery, searchResults, options)
			if rerankErr != nil {
				h.logger.Warn("重排序失败，将使用原始结果", "error", rerankErr)
			} else {
				searchResults = rerankedResults
				response.Stats.RerankedResults = len(rerankedResults)
			}
		}
	}
	
	// 转换结果
	for _, result := range searchResults {
		response.Results = append(response.Results, SearchResult{
			ID:       result.ID,
			Content:  result.Content,
			Score:    result.Score,
			Source:   result.Source,
			Metadata: result.Metadata.Properties,
			Snippet:  result.Snippet,
		})
	}
	
	// 计算统计信息
	response.Stats.ElapsedTime = time.Since(startTime)
	
	return response, nil
}

// getImageFile 获取图像文件（下载或解码）
func (h *MultimodalHandler) getImageFile(request ImageSearchRequest) (string, error) {
	// 创建临时文件
	tempFile, err := os.CreateTemp(h.tempDir, "image-*.jpg")
	if err != nil {
		return "", fmt.Errorf("创建临时文件失败: %w", err)
	}
	defer tempFile.Close()
	
	if request.ImageURL != "" {
		// 下载图像
		client := &http.Client{Timeout: 10 * time.Second}
		resp, err := client.Get(request.ImageURL)
		if err != nil {
			return "", fmt.Errorf("下载图像失败: %w", err)
		}
		defer resp.Body.Close()
		
		if resp.StatusCode != http.StatusOK {
			return "", fmt.Errorf("下载图像失败，状态码: %d", resp.StatusCode)
		}
		
		// 保存到临时文件
		_, err = io.Copy(tempFile, resp.Body)
		if err != nil {
			return "", fmt.Errorf("保存图像失败: %w", err)
		}
		
	} else if request.ImageData != "" {
		// 解码Base64
		imageBytes, err := utils.DecodeBase64(request.ImageData)
		if err != nil {
			return "", fmt.Errorf("解码图像数据失败: %w", err)
		}
		
		// 保存到临时文件
		_, err = tempFile.Write(imageBytes)
		if err != nil {
			return "", fmt.Errorf("保存图像失败: %w", err)
		}
	}
	
	return tempFile.Name(), nil
}

// getAudioFile 获取音频文件（下载或解码）
func (h *MultimodalHandler) getAudioFile(request AudioSearchRequest) (string, error) {
	// 创建临时文件
	tempFile, err := os.CreateTemp(h.tempDir, "audio-*.wav")
	if err != nil {
		return "", fmt.Errorf("创建临时文件失败: %w", err)
	}
	defer tempFile.Close()
	
	if request.AudioURL != "" {
		// 下载音频
		client := &http.Client{Timeout: 10 * time.Second}
		resp, err := client.Get(request.AudioURL)
		if err != nil {
			return "", fmt.Errorf("下载音频失败: %w", err)
		}
		defer resp.Body.Close()
		
		if resp.StatusCode != http.StatusOK {
			return "", fmt.Errorf("下载音频失败，状态码: %d", resp.StatusCode)
		}
		
		// 保存到临时文件
		_, err = io.Copy(tempFile, resp.Body)
		if err != nil {
			return "", fmt.Errorf("保存音频失败: %w", err)
		}
		
	} else if request.AudioData != "" {
		// 解码Base64
		audioBytes, err := utils.DecodeBase64(request.AudioData)
		if err != nil {
			return "", fmt.Errorf("解码音频数据失败: %w", err)
		}
		
		// 保存到临时文件
		_, err = tempFile.Write(audioBytes)
		if err != nil {
			return "", fmt.Errorf("保存音频失败: %w", err)
		}
	}
	
	return tempFile.Name(), nil
}

// RegisterRoutes 注册路由
func (h *MultimodalHandler) RegisterRoutes(router *gin.Engine) {
	router.POST("/api/search/image", h.HandleImageSearch)
	router.POST("/api/search/audio", h.HandleAudioSearch)
} 