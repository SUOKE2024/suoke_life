package reranker

// RerankerOptions 重排序器选项
type RerankerOptions struct {
	// TopK 保留的结果数量
	TopK int
	
	// BatchSize 批处理大小
	BatchSize int
	
	// ScoreThreshold 分数阈值，低于此值的结果将被过滤
	ScoreThreshold float64
	
	// MaxInputLength 最大输入长度
	MaxInputLength int
	
	// UserID 用户ID，用于个性化
	UserID string
	
	// Domain 领域，如"医学"、"中医"等
	Domain string
	
	// TCMSpecific 是否启用中医特性
	TCMSpecific bool
	
	// IncludeMetadata 是否在排序时考虑元数据
	IncludeMetadata bool
	
	// UseCache 是否使用缓存
	UseCache bool
	
	// CacheKey 缓存键前缀
	CacheKey string
	
	// ExtraOptions 额外选项
	ExtraOptions map[string]interface{}
}

// NewDefaultRerankerOptions 创建默认重排序选项
func NewDefaultRerankerOptions() RerankerOptions {
	return RerankerOptions{
		TopK:           10,
		BatchSize:      16,
		ScoreThreshold: 0.0,
		MaxInputLength: 512,
		TCMSpecific:    false,
		IncludeMetadata: true,
		UseCache:       true,
		ExtraOptions:   make(map[string]interface{}),
	}
}

// NewTCMRerankerOptions 创建针对中医领域的重排序选项
func NewTCMRerankerOptions() RerankerOptions {
	options := NewDefaultRerankerOptions()
	options.TCMSpecific = true
	options.Domain = "tcm"
	options.ExtraOptions["enhance_tcm_terms"] = true
	options.ExtraOptions["use_tcm_synonyms"] = true
	return options
}

// SetTopK 设置保留的结果数量
func (o *RerankerOptions) SetTopK(topK int) *RerankerOptions {
	o.TopK = topK
	return o
}

// SetBatchSize 设置批处理大小
func (o *RerankerOptions) SetBatchSize(batchSize int) *RerankerOptions {
	o.BatchSize = batchSize
	return o
}

// SetScoreThreshold 设置分数阈值
func (o *RerankerOptions) SetScoreThreshold(threshold float64) *RerankerOptions {
	o.ScoreThreshold = threshold
	return o
}

// SetMaxInputLength 设置最大输入长度
func (o *RerankerOptions) SetMaxInputLength(length int) *RerankerOptions {
	o.MaxInputLength = length
	return o
}

// SetUserID 设置用户ID
func (o *RerankerOptions) SetUserID(userID string) *RerankerOptions {
	o.UserID = userID
	return o
}

// SetDomain 设置领域
func (o *RerankerOptions) SetDomain(domain string) *RerankerOptions {
	o.Domain = domain
	return o
}

// EnableTCMSpecific 启用中医特性
func (o *RerankerOptions) EnableTCMSpecific() *RerankerOptions {
	o.TCMSpecific = true
	o.Domain = "tcm"
	o.ExtraOptions["enhance_tcm_terms"] = true
	o.ExtraOptions["use_tcm_synonyms"] = true
	return o
}

// SetExtraOption 设置额外选项
func (o *RerankerOptions) SetExtraOption(key string, value interface{}) *RerankerOptions {
	o.ExtraOptions[key] = value
	return o
}

// DisableCache 禁用缓存
func (o *RerankerOptions) DisableCache() *RerankerOptions {
	o.UseCache = false
	return o
}

// EnableCache 启用缓存
func (o *RerankerOptions) EnableCache() *RerankerOptions {
	o.UseCache = true
	return o
}

// SetCacheKey 设置缓存键前缀
func (o *RerankerOptions) SetCacheKey(cacheKey string) *RerankerOptions {
	o.CacheKey = cacheKey
	return o
}

// Clone 克隆选项
func (o *RerankerOptions) Clone() RerankerOptions {
	cloned := *o
	cloned.ExtraOptions = make(map[string]interface{})
	for k, v := range o.ExtraOptions {
		cloned.ExtraOptions[k] = v
	}
	return cloned
} 