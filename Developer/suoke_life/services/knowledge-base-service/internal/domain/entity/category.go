package entity

import (
	"fmt"
	"time"

	"github.com/google/uuid"
)

// Category 表示文档分类
type Category struct {
	ID          uuid.UUID   `json:"id"`
	Name        string      `json:"name"`
	Description string      `json:"description"`
	ParentID    *uuid.UUID  `json:"parent_id,omitempty"`
	Path        string      `json:"path"` // 存储路径，如 "/中医/经络/"
	Children    []*Category `json:"children,omitempty"`
	CreatedAt   time.Time   `json:"created_at"`
	UpdatedAt   time.Time   `json:"updated_at"`
}

// NewCategory 创建新分类
func NewCategory(name, description string, parentID *uuid.UUID) (*Category, error) {
	if name == "" {
		return nil, fmt.Errorf("分类名称不能为空")
	}

	now := time.Now()

	return &Category{
		ID:          uuid.New(),
		Name:        name,
		Description: description,
		ParentID:    parentID,
		Path:        fmt.Sprintf("/%s/", name), // 默认路径
		Children:    []*Category{},
		CreatedAt:   now,
		UpdatedAt:   now,
	}, nil
}

// AddChild 添加子分类
func (c *Category) AddChild(child *Category) error {
	if child == nil {
		return fmt.Errorf("子分类不能为空")
	}

	// 更新子分类的父ID
	parentID := c.ID
	child.ParentID = &parentID

	// 更新子分类的路径
	child.Path = fmt.Sprintf("%s%s/", c.Path, child.Name)

	// 添加到子分类列表
	c.Children = append(c.Children, child)
	c.UpdatedAt = time.Now()

	return nil
}

// RemoveChild 移除子分类
func (c *Category) RemoveChild(childID uuid.UUID) error {
	for i, child := range c.Children {
		if child.ID == childID {
			c.Children = append(c.Children[:i], c.Children[i+1:]...)
			c.UpdatedAt = time.Now()
			return nil
		}
	}

	return fmt.Errorf("未找到子分类 ID: %s", childID)
}

// Update 更新分类信息
func (c *Category) Update(name, description string) {
	if name != "" {
		c.Name = name
	}

	if description != "" {
		c.Description = description
	}

	c.UpdatedAt = time.Now()

	// 如果名称变更，需要更新路径
	if name != "" {
		c.updatePath()
	}
}

// IsRoot 检查是否为根分类
func (c *Category) IsRoot() bool {
	return c.ParentID == nil
}

// HasChildren 检查是否有子分类
func (c *Category) HasChildren() bool {
	return len(c.Children) > 0
}

// 更新路径（内部方法）
func (c *Category) updatePath() {
	if c.IsRoot() {
		c.Path = fmt.Sprintf("/%s/", c.Name)
	}

	// 递归更新所有子分类的路径
	for _, child := range c.Children {
		child.Path = fmt.Sprintf("%s%s/", c.Path, child.Name)
		child.updatePath()
	}
}
