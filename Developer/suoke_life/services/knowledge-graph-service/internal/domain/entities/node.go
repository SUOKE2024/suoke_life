package entities

import (
	"time"
)

// Node 表示知识图谱中的节点
type Node struct {
	ID         string                 `json:"id"`
	Labels     []string               `json:"labels"`
	Properties map[string]interface{} `json:"properties"`
	CreatedAt  time.Time              `json:"created_at"`
	UpdatedAt  time.Time              `json:"updated_at"`
}

// NodeOption 节点选项函数
type NodeOption func(*Node)

// WithProperties 设置节点属性
func WithProperties(props map[string]interface{}) NodeOption {
	return func(n *Node) {
		n.Properties = props
	}
}

// WithCreatedAt 设置创建时间
func WithCreatedAt(t time.Time) NodeOption {
	return func(n *Node) {
		n.CreatedAt = t
	}
}

// WithID 设置节点ID
func WithID(id string) NodeOption {
	return func(n *Node) {
		n.ID = id
	}
}

// NewNode 创建一个新的节点
func NewNode(labels []string, opts ...NodeOption) *Node {
	now := time.Now()
	node := &Node{
		Labels:     labels,
		Properties: make(map[string]interface{}),
		CreatedAt:  now,
		UpdatedAt:  now,
	}

	for _, opt := range opts {
		opt(node)
	}

	return node
}

// AddLabel 添加标签
func (n *Node) AddLabel(label string) {
	for _, l := range n.Labels {
		if l == label {
			return
		}
	}
	n.Labels = append(n.Labels, label)
}

// SetProperty 设置属性
func (n *Node) SetProperty(key string, value interface{}) {
	n.Properties[key] = value
	n.UpdatedAt = time.Now()
}

// GetProperty 获取属性
func (n *Node) GetProperty(key string) (interface{}, bool) {
	value, exists := n.Properties[key]
	return value, exists
}

// RemoveProperty 删除属性
func (n *Node) RemoveProperty(key string) {
	delete(n.Properties, key)
	n.UpdatedAt = time.Now()
} 