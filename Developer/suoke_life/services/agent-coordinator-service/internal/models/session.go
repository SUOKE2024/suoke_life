package models

import (
	"time"
)

// Session 会话模型
type Session struct {
	ID          string                 `json:"id"`
	UserID      string                 `json:"userId"`
	Title       string                 `json:"title"`
	Status      string                 `json:"status"` // ACTIVE, ARCHIVED, DELETED
	Metadata    map[string]interface{} `json:"metadata,omitempty"`
	LastMessage *time.Time             `json:"lastMessage,omitempty"`
	CreatedAt   time.Time              `json:"createdAt"`
	UpdatedAt   time.Time              `json:"updatedAt"`
}

// Message 消息模型
type Message struct {
	ID          string                 `json:"id"`
	SessionID   string                 `json:"sessionId"`
	Role        string                 `json:"role"` // user, assistant, system
	Content     string                 `json:"content"`
	ContentType string                 `json:"contentType,omitempty"` // text, image, file
	Metadata    map[string]interface{} `json:"metadata,omitempty"`
	CreatedAt   time.Time              `json:"createdAt"`
}

// SessionResponse 会话响应模型（包含消息）
type SessionResponse struct {
	Session  Session   `json:"session"`
	Messages []Message `json:"messages"`
}

// CreateSessionRequest 创建会话请求
type CreateSessionRequest struct {
	UserID   string                 `json:"userId" binding:"required"`
	Title    string                 `json:"title" binding:"required"`
	Metadata map[string]interface{} `json:"metadata,omitempty"`
}

// UpdateSessionRequest 更新会话请求
type UpdateSessionRequest struct {
	Title    string                 `json:"title,omitempty"`
	Status   string                 `json:"status,omitempty"`
	Metadata map[string]interface{} `json:"metadata,omitempty"`
}

// AddMessageRequest 添加消息请求
type AddMessageRequest struct {
	Role        string                 `json:"role" binding:"required"`
	Content     string                 `json:"content" binding:"required"`
	ContentType string                 `json:"contentType,omitempty"`
	Metadata    map[string]interface{} `json:"metadata,omitempty"`
} 