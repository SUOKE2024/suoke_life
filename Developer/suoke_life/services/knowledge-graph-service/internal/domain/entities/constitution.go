package entities

import (
	"time"
)

// ConstitutionType 中医体质类型
type ConstitutionType string

const (
	// ConstitutionPingHe 平和体质
	ConstitutionPingHe ConstitutionType = "ping_he"
	// ConstitutionQiXu 气虚体质
	ConstitutionQiXu ConstitutionType = "qi_xu"
	// ConstitutionYangXu 阳虚体质
	ConstitutionYangXu ConstitutionType = "yang_xu"
	// ConstitutionYinXu 阴虚体质
	ConstitutionYinXu ConstitutionType = "yin_xu"
	// ConstitutionTanShi 痰湿体质
	ConstitutionTanShi ConstitutionType = "tan_shi"
	// ConstitutionShiRe 湿热体质
	ConstitutionShiRe ConstitutionType = "shi_re"
	// ConstitutionXueYu 血瘀体质
	ConstitutionXueYu ConstitutionType = "xue_yu"
	// ConstitutionQiYu 气郁体质
	ConstitutionQiYu ConstitutionType = "qi_yu"
	// ConstitutionTeQing 特禀体质
	ConstitutionTeQing ConstitutionType = "te_qing"
)

// ConstitutionFeatures 体质特征
type ConstitutionFeatures struct {
	// 形体特征
	BodyFeatures []string `json:"body_features,omitempty"`
	// 常见症状
	CommonSymptoms []string `json:"common_symptoms,omitempty"`
	// 心理特征
	PsychologicalTraits []string `json:"psychological_traits,omitempty"`
	// 发病倾向
	DiseaseTendencies []string `json:"disease_tendencies,omitempty"`
	// 适宜食物
	SuitableFoods []string `json:"suitable_foods,omitempty"`
	// 不适宜食物
	UnsuitableFoods []string `json:"unsuitable_foods,omitempty"`
	// 生活调摄建议
	LifestyleSuggestions []string `json:"lifestyle_suggestions,omitempty"`
}

// ConstitutionNode 体质节点
type ConstitutionNode struct {
	*Node
	constitutionType ConstitutionType
	features         *ConstitutionFeatures
}

// NewConstitutionNode 创建新的体质节点
func NewConstitutionNode(name string, constitutionType ConstitutionType, description string) *ConstitutionNode {
	baseNode := NewNode([]string{"constitution"}, WithProperties(map[string]interface{}{
		"name":        name,
		"category":    "constitution",
		"type":        string(constitutionType),
		"description": description,
		"created_at":  time.Now(),
	}))

	return &ConstitutionNode{
		Node:             baseNode,
		constitutionType: constitutionType,
		features:         &ConstitutionFeatures{},
	}
}

// SetFeatures 设置体质特征
func (c *ConstitutionNode) SetFeatures(features *ConstitutionFeatures) {
	c.features = features
	
	// 同步更新到基础属性
	if len(features.BodyFeatures) > 0 {
		c.SetProperty("body_features", features.BodyFeatures)
	}
	if len(features.CommonSymptoms) > 0 {
		c.SetProperty("common_symptoms", features.CommonSymptoms)
	}
	if len(features.PsychologicalTraits) > 0 {
		c.SetProperty("psychological_traits", features.PsychologicalTraits)
	}
	if len(features.DiseaseTendencies) > 0 {
		c.SetProperty("disease_tendencies", features.DiseaseTendencies)
	}
	if len(features.SuitableFoods) > 0 {
		c.SetProperty("suitable_foods", features.SuitableFoods)
	}
	if len(features.UnsuitableFoods) > 0 {
		c.SetProperty("unsuitable_foods", features.UnsuitableFoods)
	}
	if len(features.LifestyleSuggestions) > 0 {
		c.SetProperty("lifestyle_suggestions", features.LifestyleSuggestions)
	}
}

// GetFeatures 获取体质特征
func (c *ConstitutionNode) GetFeatures() *ConstitutionFeatures {
	return c.features
}

// GetConstitutionType 获取体质类型
func (c *ConstitutionNode) GetConstitutionType() ConstitutionType {
	return c.constitutionType
}

// GetName 获取名称
func (c *ConstitutionNode) GetName() string {
	if name, ok := c.GetProperty("name"); ok {
		if nameStr, isString := name.(string); isString {
			return nameStr
		}
	}
	return ""
}

// GetDescription 获取描述
func (c *ConstitutionNode) GetDescription() string {
	if desc, ok := c.GetProperty("description"); ok {
		if descStr, isString := desc.(string); isString {
			return descStr
		}
	}
	return ""
}

// MarshalJSON 自定义JSON序列化
func (c *ConstitutionNode) MarshalJSON() ([]byte, error) {
	return c.Node.MarshalJSON()
}

// UnmarshalJSON 自定义JSON反序列化
func (c *ConstitutionNode) UnmarshalJSON(data []byte) error {
	return c.Node.UnmarshalJSON(data)
} 