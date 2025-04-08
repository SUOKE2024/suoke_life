package entities

import (
	"time"
)

// TCMNodeType 中医节点类型
type TCMNodeType string

const (
	// TCMNodeHerb 中药材
	TCMNodeHerb TCMNodeType = "herb"
	// TCMNodeFormula 方剂
	TCMNodeFormula TCMNodeType = "formula"
	// TCMNodeSymptom 症状
	TCMNodeSymptom TCMNodeType = "symptom"
	// TCMNodeSyndrome 证型
	TCMNodeSyndrome TCMNodeType = "syndrome"
	// TCMNodeTreatment 治法
	TCMNodeTreatment TCMNodeType = "treatment"
	// TCMNodeMeridian 经络
	TCMNodeMeridian TCMNodeType = "meridian"
	// TCMNodeDisease 疾病
	TCMNodeDisease TCMNodeType = "disease"
)

// TCMProperties 中医节点特定属性
type TCMProperties struct {
	SubType        TCMNodeType `json:"sub_type"`            // 子类型
	Classification string      `json:"classification"`      // 分类
	Nature         []string    `json:"nature,omitempty"`    // 性质 (寒/热/温/凉/平)
	Flavor         []string    `json:"flavor,omitempty"`    // 味道 (酸/苦/甘/辛/咸)
	ChannelTropism []string    `json:"channels,omitempty"`  // 归经
	Functions      []string    `json:"functions,omitempty"` // 功效
	Applications   []string    `json:"applications,omitempty"` // 主治
	Dosage         string      `json:"dosage,omitempty"`    // 用量
	Contraindications []string `json:"contraindications,omitempty"` // 禁忌
	Source         string      `json:"source,omitempty"`    // 出处
}

// TCMNode 中医节点
type TCMNode struct {
	*Node
	tcmProperties *TCMProperties
}

// TCMNodeOption TCM节点选项
type TCMNodeOption func(*TCMNode)

// WithDescription 设置描述
func WithDescription(desc string) TCMNodeOption {
	return func(n *TCMNode) {
		n.SetProperty("description", desc)
	}
}

// WithSource 设置来源
func WithSource(source string) TCMNodeOption {
	return func(n *TCMNode) {
		n.SetProperty("source", source)
	}
}

// NewTCMNode 创建新的TCM节点
func NewTCMNode(name string, subType TCMNodeType, opts ...TCMNodeOption) *TCMNode {
	baseNode := NewNode([]string{"tcm"}, WithProperties(map[string]interface{}{
		"name":      name,
		"category":  "tcm",
		"sub_type":  string(subType),
		"created_at": time.Now(),
	}))
	
	tcmNode := &TCMNode{
		Node: baseNode,
		tcmProperties: &TCMProperties{
			SubType: subType,
		},
	}
	
	for _, opt := range opts {
		opt(tcmNode)
	}
	
	return tcmNode
}

// SetTCMProperties 设置TCM属性
func (n *TCMNode) SetTCMProperties(props *TCMProperties) {
	n.tcmProperties = props
	// 同步更新到基础属性
	n.SetProperty("sub_type", string(props.SubType))
	if props.Classification != "" {
		n.SetProperty("classification", props.Classification)
	}
	if len(props.Nature) > 0 {
		n.SetProperty("nature", props.Nature)
	}
	if len(props.Flavor) > 0 {
		n.SetProperty("flavor", props.Flavor)
	}
}

// GetTCMProperties 获取TCM属性
func (n *TCMNode) GetTCMProperties() *TCMProperties {
	return n.tcmProperties
}

// GetName 获取名称
func (n *TCMNode) GetName() string {
	if name, ok := n.GetProperty("name"); ok {
		if nameStr, isString := name.(string); isString {
			return nameStr
		}
	}
	return ""
}

// GetCategory 获取分类
func (n *TCMNode) GetCategory() string {
	if category, ok := n.GetProperty("category"); ok {
		if categoryStr, isString := category.(string); isString {
			return categoryStr
		}
	}
	return "tcm"
}

// GetDescription 获取描述
func (n *TCMNode) GetDescription() string {
	if desc, ok := n.GetProperty("description"); ok {
		if descStr, isString := desc.(string); isString {
			return descStr
		}
	}
	return ""
}

// GetSource 获取来源
func (n *TCMNode) GetSource() string {
	if source, ok := n.GetProperty("source"); ok {
		if sourceStr, isString := source.(string); isString {
			return sourceStr
		}
	}
	return ""
} 