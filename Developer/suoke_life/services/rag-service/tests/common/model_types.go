package common

// SearchResult 表示单个搜索结果
type SearchResult struct {
	ID       string                 `json:"id"`
	Content  string                 `json:"content"`
	Source   string                 `json:"source,omitempty"`
	Score    float64                `json:"score"`
	Metadata map[string]interface{} `json:"metadata,omitempty"`
}

// KGTriple 表示知识图谱中的三元组
type KGTriple struct {
	Subject   string                 `json:"subject"`
	Predicate string                 `json:"predicate"`
	Object    string                 `json:"object"`
	Weight    float64                `json:"weight,omitempty"`
	Metadata  map[string]interface{} `json:"metadata,omitempty"`
}

// KGSubgraph 表示知识图谱子图
type KGSubgraph struct {
	Nodes      []KGNode  `json:"nodes"`
	Edges      []KGEdge  `json:"edges"`
	CentralNode string   `json:"central_node,omitempty"`
	NodeTypes  []string  `json:"node_types,omitempty"`
	EdgeTypes  []string  `json:"edge_types,omitempty"`
}

// KGNode 表示知识图谱节点
type KGNode struct {
	ID       string                 `json:"id"`
	Type     string                 `json:"type,omitempty"`
	Label    string                 `json:"label"`
	Weight   float64                `json:"weight,omitempty"`
	Metadata map[string]interface{} `json:"metadata,omitempty"`
}

// KGEdge 表示知识图谱边
type KGEdge struct {
	Source    string                 `json:"source"`
	Target    string                 `json:"target"`
	Type      string                 `json:"type"`
	Label     string                 `json:"label"`
	Weight    float64                `json:"weight,omitempty"`
	Metadata  map[string]interface{} `json:"metadata,omitempty"`
}

// PathReasoning 表示路径推理结果
type PathReasoning struct {
	Query    string    `json:"query"`
	Paths    []KGPath  `json:"paths"`
	Evidence []KGTriple `json:"evidence,omitempty"`
}

// KGPath 表示知识图谱中的路径
type KGPath struct {
	Nodes     []string  `json:"nodes"`
	Edges     []string  `json:"edges"`
	Score     float64   `json:"score"`
	Reasoning string    `json:"reasoning,omitempty"`
}

// ReasoningRequest 表示推理请求
type ReasoningRequest struct {
	Query             string                 `json:"query"`
	UserID            string                 `json:"user_id,omitempty"`
	Domain            string                 `json:"domain,omitempty"`
	Context           string                 `json:"context,omitempty"`
	MaxPaths          int                    `json:"max_paths,omitempty"`
	MaxDepth          int                    `json:"max_depth,omitempty"`
	MaxBreadth        int                    `json:"max_breadth,omitempty"`
	Threshold         float64                `json:"threshold,omitempty"`
	Mode              string                 `json:"mode,omitempty"`
	TCMOptions        map[string]bool        `json:"tcm_options,omitempty"`
	ExtraOptions      map[string]interface{} `json:"extra_options,omitempty"`
}

// ReasoningResponse 表示推理响应
type ReasoningResponse struct {
	Success        bool                   `json:"success"`
	Query          string                 `json:"query"`
	Reasoning      string                 `json:"reasoning,omitempty"`
	Paths          []KGPath               `json:"paths,omitempty"`
	Subgraph       *KGSubgraph            `json:"subgraph,omitempty"`
	Evidence       []KGTriple             `json:"evidence,omitempty"`
	Sources        []SearchResult         `json:"sources,omitempty"`
	TotalLatencyMs int                    `json:"total_latency_ms,omitempty"`
	Statistics     map[string]interface{} `json:"statistics,omitempty"`
	Error          string                 `json:"error,omitempty"`
}

// 多模态分析相关类型定义

// TCMImageFeatures 表示中医图像特征
type TCMImageFeatures struct {
	TongueColor     string                 `json:"tongue_color,omitempty"`
	TongueCoating   string                 `json:"tongue_coating,omitempty"`
	TongueShape     string                 `json:"tongue_shape,omitempty"`
	TongueMoisture  string                 `json:"tongue_moisture,omitempty"`
	FaceColor       string                 `json:"face_color,omitempty"`
	FaceTexture     string                 `json:"face_texture,omitempty"`
	FacialFeatures  map[string]interface{} `json:"facial_features,omitempty"`
	DetectedObjects []DetectedObject       `json:"detected_objects,omitempty"`
	Metadata        map[string]interface{} `json:"metadata,omitempty"`
}

// DetectedObject 表示检测到的对象
type DetectedObject struct {
	Label       string    `json:"label"`
	Confidence  float64   `json:"confidence"`
	BoundingBox []float64 `json:"bounding_box,omitempty"`
}

// TCMAudioFeatures 表示中医音频特征
type TCMAudioFeatures struct {
	PulseType      string                 `json:"pulse_type,omitempty"`
	PulseStrength  string                 `json:"pulse_strength,omitempty"`
	PulseRhythm    string                 `json:"pulse_rhythm,omitempty"`
	PulseRate      int                    `json:"pulse_rate,omitempty"`
	VoiceQuality   string                 `json:"voice_quality,omitempty"`
	VoiceStrength  string                 `json:"voice_strength,omitempty"`
	SpeechRate     string                 `json:"speech_rate,omitempty"`
	AudioFeatures  map[string]float64     `json:"audio_features,omitempty"`
	SpectralData   []float64              `json:"spectral_data,omitempty"`
	Metadata       map[string]interface{} `json:"metadata,omitempty"`
}

// AnalysisResult 表示分析结果
type AnalysisResult struct {
	Success       bool                   `json:"success"`
	ImageFeatures *TCMImageFeatures      `json:"image_features,omitempty"`
	AudioFeatures *TCMAudioFeatures      `json:"audio_features,omitempty"`
	Metadata      map[string]interface{} `json:"metadata,omitempty"`
	Results       []SearchResult         `json:"results,omitempty"`
	Error         string                 `json:"error,omitempty"`
	Statistics    map[string]interface{} `json:"statistics,omitempty"`
}

// 多模态搜索相关类型定义

// MultimodalSearchRequest 表示多模态搜索请求
type MultimodalSearchRequest struct {
	Query        string                 `json:"query,omitempty"`
	UserID       string                 `json:"user_id,omitempty"`
	Domain       string                 `json:"domain,omitempty"`
	MaxResults   int                    `json:"max_results,omitempty"`
	UseCache     bool                   `json:"use_cache,omitempty"`
	ImageData    string                 `json:"image_data,omitempty"`
	ImagePath    string                 `json:"image_path,omitempty"`
	ImageType    string                 `json:"image_type,omitempty"`
	AudioData    string                 `json:"audio_data,omitempty"`
	AudioPath    string                 `json:"audio_path,omitempty"`
	AudioType    string                 `json:"audio_type,omitempty"`
	TCMOptions   map[string]bool        `json:"tcm_options,omitempty"`
	ExtraOptions map[string]interface{} `json:"extra_options,omitempty"`
}

// MultimodalSearchResponse 表示多模态搜索响应
type MultimodalSearchResponse struct {
	Success       bool                   `json:"success"`
	Query         string                 `json:"query"`
	Results       []SearchResult         `json:"results,omitempty"`
	ImageAnalysis *TCMImageFeatures      `json:"image_analysis,omitempty"`
	AudioAnalysis *TCMAudioFeatures      `json:"audio_analysis,omitempty"`
	TotalLatencyMs int                   `json:"total_latency_ms,omitempty"`
	Statistics    map[string]interface{} `json:"statistics,omitempty"`
	Error         string                 `json:"error,omitempty"`
}

// 自适应学习相关类型定义

// FeedbackRequest 表示反馈请求
type FeedbackRequest struct {
	QueryID      string                 `json:"query_id,omitempty"`
	Query        string                 `json:"query"`
	UserID       string                 `json:"user_id,omitempty"`
	Answer       string                 `json:"answer"`
	FeedbackType string                 `json:"feedback_type"`
	Rating       int                    `json:"rating,omitempty"`
	Comment      string                 `json:"comment,omitempty"`
	Sources      []string               `json:"sources,omitempty"`
	ResultIDs    []string               `json:"result_ids,omitempty"`
	Metadata     map[string]interface{} `json:"metadata,omitempty"`
}

// FeedbackResponse 表示反馈响应
type FeedbackResponse struct {
	Success     bool                    `json:"success"`
	FeedbackID  string                  `json:"feedback_id,omitempty"`
	Metrics     *AdaptiveMetrics        `json:"metrics,omitempty"`
	Changes     []ParamChange           `json:"changes,omitempty"`
	Statistics  map[string]interface{}  `json:"statistics,omitempty"`
	Error       string                  `json:"error,omitempty"`
}

// AdaptiveMetrics 表示自适应指标
type AdaptiveMetrics struct {
	UserSatisfaction  float64                `json:"user_satisfaction"`
	SourceReliability map[string]float64     `json:"source_reliability"`
	QuerySuccessRate  float64                `json:"query_success_rate"`
	AdaptiveScore     float64                `json:"adaptive_score"`
	BatchStats        map[string]float64     `json:"batch_stats,omitempty"`
}

// ParamChange 表示参数变化
type ParamChange struct {
	Name     string   `json:"name"`
	OldValue float64  `json:"old_value"`
	NewValue float64  `json:"new_value"`
	Factor   string   `json:"factor,omitempty"`
} 