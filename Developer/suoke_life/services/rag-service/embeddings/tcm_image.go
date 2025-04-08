package embeddings

import (
	"context"
	"fmt"
	"path/filepath"
	"strings"

	"github.com/suoke/suoke_life/services/rag-service/internal/models"
	"github.com/suoke/suoke_life/services/rag-service/internal/utils"
)

// TCMImageType 中医图像类型
type TCMImageType string

const (
	// ImageTypeTongue 舌诊图像
	ImageTypeTongue TCMImageType = "tongue"
	
	// ImageTypeFace 面诊图像
	ImageTypeFace TCMImageType = "face"
	
	// ImageTypePulse 脉诊图像
	ImageTypePulse TCMImageType = "pulse"
	
	// ImageTypeHerb 中药图像
	ImageTypeHerb TCMImageType = "herb"
	
	// ImageTypeUnknown 未知类型
	ImageTypeUnknown TCMImageType = "unknown"
)

// TCMImageFeatures 中医图像特征
type TCMImageFeatures struct {
	// 图像类型
	ImageType TCMImageType `json:"image_type"`
	
	// 颜色特征
	ColorFeatures map[string]float32 `json:"color_features,omitempty"`
	
	// 纹理特征
	TextureFeatures map[string]float32 `json:"texture_features,omitempty"`
	
	// 形状特征
	ShapeFeatures map[string]float32 `json:"shape_features,omitempty"`
	
	// 关键点特征
	KeypointFeatures map[string][]float32 `json:"keypoint_features,omitempty"`
	
	// 舌象特征 (舌诊特有)
	TongueFeatures *TongueFeatures `json:"tongue_features,omitempty"`
	
	// 面色特征 (面诊特有)
	FaceFeatures *FaceFeatures `json:"face_features,omitempty"`
}

// TongueFeatures 舌象特征
type TongueFeatures struct {
	// 舌质颜色 (淡白、淡红、红、绛)
	TongueColor string `json:"tongue_color"`
	
	// 舌质颜色RGB值
	TongueColorRGB [3]uint8 `json:"tongue_color_rgb"`
	
	// 舌苔颜色 (白、黄、灰黑)
	CoatingColor string `json:"coating_color"`
	
	// 舌苔颜色RGB值
	CoatingColorRGB [3]uint8 `json:"coating_color_rgb"`
	
	// 舌形 (胖大、瘦薄、齿痕、点刺、裂纹)
	TongueShape []string `json:"tongue_shape"`
	
	// 舌苔厚度 (薄、厚)
	CoatingThickness string `json:"coating_thickness"`
	
	// 舌苔性质 (腻、燥、腐、剥落)
	CoatingNature []string `json:"coating_nature"`
	
	// 舌体湿度 (0-1, 0为干燥, 1为湿润)
	Moisture float32 `json:"moisture"`
}

// FaceFeatures 面色特征
type FaceFeatures struct {
	// 面色 (萎黄、晄白、潮红、暗黑)
	FaceColor string `json:"face_color"`
	
	// 面色RGB值
	FaceColorRGB [3]uint8 `json:"face_color_rgb"`
	
	// 五官特征
	FacialFeatures map[string]string `json:"facial_features"`
	
	// 面部区域与脏腑对应
	OrganMapping map[string]float32 `json:"organ_mapping"`
}

// TCMImageEmbedder 中医图像嵌入器
type TCMImageEmbedder struct {
	// 基础图像嵌入器
	baseEmbedder ImageEmbedder
	
	// 图像处理器
	processor *TCMImageProcessor
	
	// 日志器
	logger utils.Logger
	
	// 嵌入向量维度
	dimensions int
	
	// 模型名称
	modelName string
	
	// 模型路径
	modelPath string
}

// TCMImageProcessor 中医图像处理器
type TCMImageProcessor struct {
	// 舌诊处理器
	tongueProcessor *TongueProcessor
	
	// 面诊处理器
	faceProcessor *FaceProcessor
	
	// 图像分类器
	classifier *TCMImageClassifier
	
	// 模型路径
	modelPath string
}

// TongueProcessor 舌诊处理器
type TongueProcessor struct {
	// 舌体分割模型
	segmentationModel string
	
	// 舌质颜色分类模型
	tongueColorModel string
	
	// 舌苔颜色分类模型
	coatingColorModel string
	
	// 舌形分析模型
	tongueShapeModel string
}

// FaceProcessor 面诊处理器
type FaceProcessor struct {
	// 面部分割模型
	segmentationModel string
	
	// 面色分类模型
	faceColorModel string
	
	// 五官检测模型
	facialFeaturesModel string
}

// TCMImageClassifier 中医图像分类器
type TCMImageClassifier struct {
	// 分类模型路径
	modelPath string
	
	// 类别列表
	categories []string
}

// NewTCMImageEmbedder 创建中医图像嵌入器
func NewTCMImageEmbedder(baseEmbedder ImageEmbedder, modelPath string, logger utils.Logger) *TCMImageEmbedder {
	if logger == nil {
		logger = utils.NewNoopLogger()
	}
	
	return &TCMImageEmbedder{
		baseEmbedder: baseEmbedder,
		processor:    nil, // 将在Initialize中初始化
		modelPath:    modelPath,
		logger:       logger,
		dimensions:   baseEmbedder.Dimensions(),
		modelName:    fmt.Sprintf("tcm-image-%s", baseEmbedder.Name()),
	}
}

// Initialize 初始化嵌入模型
func (e *TCMImageEmbedder) Initialize(ctx context.Context) error {
	// 初始化基础嵌入器
	if err := e.baseEmbedder.Initialize(ctx); err != nil {
		return fmt.Errorf("初始化基础图像嵌入器失败: %w", err)
	}
	
	// 初始化图像处理器
	processor, err := e.initImageProcessor(ctx)
	if err != nil {
		e.logger.Warn("初始化图像处理器失败，将使用基础嵌入功能", "error", err)
	} else {
		e.processor = processor
	}
	
	e.logger.Info("初始化中医图像嵌入器完成")
	return nil
}

// 初始化图像处理器
func (e *TCMImageEmbedder) initImageProcessor(ctx context.Context) (*TCMImageProcessor, error) {
	processorPath := filepath.Join(e.modelPath, "image_processor")
	
	// 舌诊处理器
	tongueProcessor := &TongueProcessor{
		segmentationModel:  filepath.Join(processorPath, "tongue/segmentation"),
		tongueColorModel:   filepath.Join(processorPath, "tongue/color"),
		coatingColorModel:  filepath.Join(processorPath, "tongue/coating"),
		tongueShapeModel:   filepath.Join(processorPath, "tongue/shape"),
	}
	
	// 面诊处理器
	faceProcessor := &FaceProcessor{
		segmentationModel:   filepath.Join(processorPath, "face/segmentation"),
		faceColorModel:      filepath.Join(processorPath, "face/color"),
		facialFeaturesModel: filepath.Join(processorPath, "face/features"),
	}
	
	// 图像分类器
	classifier := &TCMImageClassifier{
		modelPath:  filepath.Join(processorPath, "classifier"),
		categories: []string{"tongue", "face", "pulse", "herb", "other"},
	}
	
	return &TCMImageProcessor{
		tongueProcessor: tongueProcessor,
		faceProcessor:   faceProcessor,
		classifier:      classifier,
		modelPath:       processorPath,
	}, nil
}

// Name 返回嵌入模型名称
func (e *TCMImageEmbedder) Name() string {
	return e.modelName
}

// Dimensions 返回嵌入向量维度
func (e *TCMImageEmbedder) Dimensions() int {
	return e.dimensions
}

// Close 关闭嵌入模型
func (e *TCMImageEmbedder) Close() error {
	return e.baseEmbedder.Close()
}

// EmbedImages 对图像进行嵌入
func (e *TCMImageEmbedder) EmbedImages(ctx context.Context, imagePaths []string) ([][]float32, error) {
	// 首先使用基础嵌入器生成嵌入向量
	baseEmbeddings, err := e.baseEmbedder.EmbedImages(ctx, imagePaths)
	if err != nil {
		return nil, fmt.Errorf("基础图像嵌入失败: %w", err)
	}
	
	// 如果没有处理器或图像，直接返回基础嵌入
	if e.processor == nil || len(imagePaths) == 0 {
		return baseEmbeddings, nil
	}
	
	// 分类图像并进行专门处理
	tongueImages := make([]int, 0)
	faceImages := make([]int, 0)
	otherImages := make([]int, 0)
	
	for i, path := range imagePaths {
		imageType := e.inferTCMImageType(path)
		
		switch imageType {
		case ImageTypeTongue:
			tongueImages = append(tongueImages, i)
		case ImageTypeFace:
			faceImages = append(faceImages, i)
		default:
			otherImages = append(otherImages, i)
		}
	}
	
	// 处理舌诊图像
	if len(tongueImages) > 0 {
		e.processTongueImages(ctx, tongueImages, imagePaths, baseEmbeddings)
	}
	
	// 处理面诊图像
	if len(faceImages) > 0 {
		e.processFaceImages(ctx, faceImages, imagePaths, baseEmbeddings)
	}
	
	return baseEmbeddings, nil
}

// 处理舌诊图像
func (e *TCMImageEmbedder) processTongueImages(ctx context.Context, indices []int, imagePaths []string, embeddings [][]float32) {
	for _, i := range indices {
		// 提取舌诊特征
		features, err := e.extractTongueFeatures(imagePaths[i])
		if err != nil {
			e.logger.Warn("提取舌诊特征失败", "path", imagePaths[i], "error", err)
			continue
		}
		
		// 根据舌诊特征增强嵌入向量
		e.enhanceTongueEmbedding(embeddings[i], features)
	}
}

// 处理面诊图像
func (e *TCMImageEmbedder) processFaceImages(ctx context.Context, indices []int, imagePaths []string, embeddings [][]float32) {
	for _, i := range indices {
		// 提取面诊特征
		features, err := e.extractFaceFeatures(imagePaths[i])
		if err != nil {
			e.logger.Warn("提取面诊特征失败", "path", imagePaths[i], "error", err)
			continue
		}
		
		// 根据面诊特征增强嵌入向量
		e.enhanceFaceEmbedding(embeddings[i], features)
	}
}

// 提取舌诊特征
func (e *TCMImageEmbedder) extractTongueFeatures(imagePath string) (*TongueFeatures, error) {
	// 默认特征，实际应该调用模型进行识别
	return &TongueFeatures{
		TongueColor:      "淡红",
		TongueColorRGB:   [3]uint8{255, 180, 180},
		CoatingColor:     "薄白",
		CoatingColorRGB:  [3]uint8{240, 240, 240},
		TongueShape:      []string{"正常"},
		CoatingThickness: "薄",
		CoatingNature:    []string{"润"},
		Moisture:         0.7,
	}, nil
}

// 提取面诊特征
func (e *TCMImageEmbedder) extractFaceFeatures(imagePath string) (*FaceFeatures, error) {
	// 默认特征，实际应该调用模型进行识别
	return &FaceFeatures{
		FaceColor:      "正常",
		FaceColorRGB:   [3]uint8{240, 200, 180},
		FacialFeatures: map[string]string{
			"眼": "正常",
			"鼻": "正常",
			"口": "正常",
		},
		OrganMapping: map[string]float32{
			"心": 0.5,
			"肝": 0.5,
			"脾": 0.5,
			"肺": 0.5,
			"肾": 0.5,
		},
	}, nil
}

// 增强舌诊嵌入向量
func (e *TCMImageEmbedder) enhanceTongueEmbedding(embedding []float32, features *TongueFeatures) {
	// 舌色特征增强
	if features.TongueColor == "淡白" {
		// 对应气血亏虚，增强相关维度
		if len(embedding) > 20 {
			embedding[5] *= 1.2
			embedding[8] *= 1.1
		}
	} else if features.TongueColor == "红" || features.TongueColor == "绛" {
		// 对应热症，增强相关维度
		if len(embedding) > 20 {
			embedding[6] *= 1.2
			embedding[9] *= 1.1
		}
	}
	
	// 舌苔特征增强
	if features.CoatingColor == "黄" {
		// 对应湿热，增强相关维度
		if len(embedding) > 20 {
			embedding[7] *= 1.2
			embedding[10] *= 1.1
		}
	} else if features.CoatingColor == "白" && features.CoatingThickness == "厚" {
		// 对应寒湿，增强相关维度
		if len(embedding) > 20 {
			embedding[4] *= 1.2
			embedding[11] *= 1.1
		}
	}
}

// 增强面诊嵌入向量
func (e *TCMImageEmbedder) enhanceFaceEmbedding(embedding []float32, features *FaceFeatures) {
	// 面色特征增强
	if features.FaceColor == "萎黄" {
		// 对应脾虚，增强相关维度
		if len(embedding) > 20 {
			embedding[12] *= 1.2
			embedding[15] *= 1.1
		}
	} else if features.FaceColor == "潮红" {
		// 对应阴虚火旺，增强相关维度
		if len(embedding) > 20 {
			embedding[13] *= 1.2
			embedding[16] *= 1.1
		}
	}
}

// 推断中医图像类型
func (e *TCMImageEmbedder) inferTCMImageType(imagePath string) TCMImageType {
	lowerPath := strings.ToLower(imagePath)
	
	// 根据文件路径推断图像类型
	if strings.Contains(lowerPath, "tongue") || strings.Contains(lowerPath, "舌诊") || strings.Contains(lowerPath, "舌象") {
		return ImageTypeTongue
	} else if strings.Contains(lowerPath, "face") || strings.Contains(lowerPath, "面诊") || strings.Contains(lowerPath, "面色") {
		return ImageTypeFace
	} else if strings.Contains(lowerPath, "pulse") || strings.Contains(lowerPath, "脉诊") || strings.Contains(lowerPath, "脉象") {
		return ImageTypePulse
	} else if strings.Contains(lowerPath, "herb") || strings.Contains(lowerPath, "中药") || strings.Contains(lowerPath, "药材") {
		return ImageTypeHerb
	}
	
	// 如果有图像分类器，应该使用分类器进行更准确的分类
	// 这里简化处理
	return ImageTypeUnknown
}

// EnhanceTCMImageMetadata 增强中医图像元数据
func (e *TCMImageEmbedder) EnhanceTCMImageMetadata(ctx context.Context, metadata *models.DocumentMetadata, imagePath string) {
	imageType := e.inferTCMImageType(imagePath)
	
	if metadata.Properties == nil {
		metadata.Properties = make(map[string]interface{})
	}
	
	// 添加中医图像类型
	metadata.Properties["tcm_image_type"] = string(imageType)
	
	// 根据图像类型添加特定信息
	switch imageType {
	case ImageTypeTongue:
		metadata.Properties["tcm_image_category"] = "舌诊图像"
		metadata.Properties["tcm_domain"] = "中医诊断"
		
		// 尝试提取舌诊特征
		if features, err := e.extractTongueFeatures(imagePath); err == nil {
			metadata.Properties["tongue_color"] = features.TongueColor
			metadata.Properties["coating_color"] = features.CoatingColor
			metadata.Properties["tongue_shape"] = features.TongueShape
			metadata.Properties["coating_thickness"] = features.CoatingThickness
			metadata.Properties["moisture"] = features.Moisture
		}
		
	case ImageTypeFace:
		metadata.Properties["tcm_image_category"] = "面诊图像"
		metadata.Properties["tcm_domain"] = "中医诊断"
		
		// 尝试提取面诊特征
		if features, err := e.extractFaceFeatures(imagePath); err == nil {
			metadata.Properties["face_color"] = features.FaceColor
		}
		
	case ImageTypePulse:
		metadata.Properties["tcm_image_category"] = "脉诊图像"
		metadata.Properties["tcm_domain"] = "中医诊断"
		
	case ImageTypeHerb:
		metadata.Properties["tcm_image_category"] = "中药图像"
		metadata.Properties["tcm_domain"] = "中药识别"
		
	default:
		metadata.Properties["tcm_image_category"] = "一般图像"
	}
} 