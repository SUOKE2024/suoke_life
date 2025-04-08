package config

import (
	"io/ioutil"

	"gopkg.in/yaml.v2"
)

// Config 配置结构
type Config struct {
	// 服务器配置
	Server ServerConfig `yaml:"server"`
	
	// 数据库配置
	Database DatabaseConfig `yaml:"database"`
	
	// 组件配置
	Components map[string]interface{} `yaml:"components"`
	
	// 日志配置
	Logging LoggingConfig `yaml:"logging"`
	
	// 重排序配置
	Reranker RerankerConfig `yaml:"reranker"`
	
	// 混合搜索配置
	HybridSearch HybridSearchConfig `yaml:"hybrid_search"`
	
	// 多模态配置
	Multimodal MultimodalConfig `yaml:"multimodal"`
}

// ServerConfig 服务器配置
type ServerConfig struct {
	// 端口
	Port int `yaml:"port"`
	
	// 主机
	Host string `yaml:"host"`
	
	// 请求超时(秒)
	TimeoutSeconds int `yaml:"timeout_seconds"`
	
	// 最大并发请求数
	MaxConcurrentRequests int `yaml:"max_concurrent_requests"`
}

// DatabaseConfig 数据库配置
type DatabaseConfig struct {
	// 向量数据库类型
	VectorDBType string `yaml:"vector_db_type"`
	
	// 向量数据库URL
	VectorDBURL string `yaml:"vector_db_url"`
	
	// 关系数据库类型
	RelationalDBType string `yaml:"relational_db_type"`
	
	// 关系数据库URL
	RelationalDBURL string `yaml:"relational_db_url"`
}

// LoggingConfig 日志配置
type LoggingConfig struct {
	// 级别
	Level string `yaml:"level"`
	
	// 文件路径
	FilePath string `yaml:"file_path"`
	
	// 格式
	Format string `yaml:"format"`
}

// RerankerConfig 重排序配置
type RerankerConfig struct {
	// 启用状态
	Enabled bool `yaml:"enabled"`
	
	// 默认模型
	DefaultModel string `yaml:"default_model"`
	
	// 模型端点
	ModelEndpoint string `yaml:"model_endpoint"`
	
	// API密钥
	APIKey string `yaml:"api_key"`
	
	// 批处理大小
	BatchSize int `yaml:"batch_size"`
	
	// 缓存大小
	CacheSize int `yaml:"cache_size"`
	
	// TCM特性
	TCMSpecific TCMSpecificConfig `yaml:"tcm_specific"`
}

// TCMSpecificConfig TCM特性配置
type TCMSpecificConfig struct {
	// 启用状态
	Enabled bool `yaml:"enabled"`
	
	// 术语库路径
	TermLibraryPath string `yaml:"term_library_path"`
}

// HybridSearchConfig 混合搜索配置
type HybridSearchConfig struct {
	// 启用状态
	Enabled bool `yaml:"enabled"`
	
	// 向量权重
	VectorWeight float64 `yaml:"vector_weight"`
	
	// 关键词权重
	KeywordWeight float64 `yaml:"keyword_weight"`
	
	// 结果数量
	TopK int `yaml:"top_k"`
	
	// 向量结果数量
	VectorTopK int `yaml:"vector_top_k"`
	
	// 关键词结果数量
	KeywordTopK int `yaml:"keyword_top_k"`
	
	// 重排序启用
	RerankerEnabled bool `yaml:"reranker_enabled"`
	
	// 重排序结果数量
	RerankerTopK int `yaml:"reranker_top_k"`
}

// MultimodalConfig 多模态配置
type MultimodalConfig struct {
	// 启用状态
	Enabled bool `yaml:"enabled"`
	
	// 图像模型
	ImageModel string `yaml:"image_model"`
	
	// 音频模型
	AudioModel string `yaml:"audio_model"`
	
	// 视频模型
	VideoModel string `yaml:"video_model"`
	
	// 模型路径
	ModelPath string `yaml:"model_path"`
	
	// 处理线程数
	NumThreads int `yaml:"num_threads"`
}

// LoadConfig 从文件加载配置
func LoadConfig(path string) (*Config, error) {
	data, err := ioutil.ReadFile(path)
	if err != nil {
		return nil, err
	}
	
	var config Config
	if err := yaml.Unmarshal(data, &config); err != nil {
		return nil, err
	}
	
	return &config, nil
} 