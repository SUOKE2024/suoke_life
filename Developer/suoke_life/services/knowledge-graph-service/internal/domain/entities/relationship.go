package entities

import (
	"time"
)

// Relationship 表示知识图谱中的关系
type Relationship struct {
	ID         string                 `json:"id"`
	SourceID   string                 `json:"source_id"`
	TargetID   string                 `json:"target_id"`
	Type       string                 `json:"type"`
	Properties map[string]interface{} `json:"properties"`
	CreatedAt  time.Time              `json:"created_at"`
	UpdatedAt  time.Time              `json:"updated_at"`
}

// RelationshipOption 关系选项函数
type RelationshipOption func(*Relationship)

// WithRelationshipProperties 设置关系属性
func WithRelationshipProperties(props map[string]interface{}) RelationshipOption {
	return func(r *Relationship) {
		r.Properties = props
	}
}

// WithRelationshipID 设置关系ID
func WithRelationshipID(id string) RelationshipOption {
	return func(r *Relationship) {
		r.ID = id
	}
}

// WithRelationshipCreatedAt 设置创建时间
func WithRelationshipCreatedAt(t time.Time) RelationshipOption {
	return func(r *Relationship) {
		r.CreatedAt = t
	}
}

// NewRelationship 创建新的关系
func NewRelationship(sourceID, targetID, relType string, opts ...RelationshipOption) *Relationship {
	now := time.Now()
	relationship := &Relationship{
		SourceID:   sourceID,
		TargetID:   targetID,
		Type:       relType,
		Properties: make(map[string]interface{}),
		CreatedAt:  now,
		UpdatedAt:  now,
	}

	for _, opt := range opts {
		opt(relationship)
	}

	return relationship
}

// SetProperty 设置关系属性
func (r *Relationship) SetProperty(key string, value interface{}) {
	r.Properties[key] = value
	r.UpdatedAt = time.Now()
}

// GetProperty 获取关系属性
func (r *Relationship) GetProperty(key string) (interface{}, bool) {
	value, exists := r.Properties[key]
	return value, exists
}

// RemoveProperty 删除关系属性
func (r *Relationship) RemoveProperty(key string) {
	delete(r.Properties, key)
	r.UpdatedAt = time.Now()
} 