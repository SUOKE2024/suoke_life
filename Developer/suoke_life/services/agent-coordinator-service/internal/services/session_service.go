package services

import (
	"errors"
	"log"
	"time"

	"github.com/google/uuid"
	"github.com/suoke-life/agent-coordinator-service/internal/models"
)

// 定义可能的错误
var (
	ErrSessionNotFound    = errors.New("会话不存在")
	ErrInvalidSessionData = errors.New("无效的会话数据")
	ErrDatabaseOperation  = errors.New("数据库操作失败")
)

// SessionService 会话服务接口
type SessionService interface {
	CreateSession(req models.CreateSessionRequest) (*models.Session, error)
	GetSessionByID(sessionID string) (*models.Session, error)
	GetSessionsByUserID(userID string) ([]models.Session, error)
	UpdateSession(sessionID string, req models.UpdateSessionRequest) (*models.Session, error)
	DeleteSession(sessionID string) error
	AddMessage(sessionID string, req models.AddMessageRequest) (*models.Message, error)
	GetSessionMessages(sessionID string) ([]models.Message, error)
}

// InMemorySessionService 内存会话服务实现
// 注意：此实现仅用于开发和测试，生产环境应使用数据库实现
type InMemorySessionService struct {
	sessions map[string]models.Session
	messages map[string][]models.Message
}

// NewInMemorySessionService 创建内存会话服务
func NewInMemorySessionService() *InMemorySessionService {
	return &InMemorySessionService{
		sessions: make(map[string]models.Session),
		messages: make(map[string][]models.Message),
	}
}

// CreateSession 创建新会话
func (s *InMemorySessionService) CreateSession(req models.CreateSessionRequest) (*models.Session, error) {
	// 日志记录
	log.Printf("创建会话请求: userID=%s, title=%s", req.UserID, req.Title)

	// 验证请求数据
	if req.UserID == "" || req.Title == "" {
		log.Printf("创建会话失败: 无效的请求数据 userID=%s, title=%s", req.UserID, req.Title)
		return nil, ErrInvalidSessionData
	}

	now := time.Now()
	sessionID := uuid.New().String()

	session := models.Session{
		ID:        sessionID,
		UserID:    req.UserID,
		Title:     req.Title,
		Status:    "ACTIVE",
		Metadata:  req.Metadata,
		CreatedAt: now,
		UpdatedAt: now,
	}

	// 存储会话
	s.sessions[sessionID] = session
	s.messages[sessionID] = []models.Message{}

	log.Printf("会话创建成功: sessionID=%s", sessionID)
	return &session, nil
}

// GetSessionByID 通过ID获取会话
func (s *InMemorySessionService) GetSessionByID(sessionID string) (*models.Session, error) {
	log.Printf("获取会话: sessionID=%s", sessionID)

	session, exists := s.sessions[sessionID]
	if !exists {
		log.Printf("会话不存在: sessionID=%s", sessionID)
		return nil, ErrSessionNotFound
	}

	return &session, nil
}

// GetSessionsByUserID 获取用户的所有会话
func (s *InMemorySessionService) GetSessionsByUserID(userID string) ([]models.Session, error) {
	log.Printf("获取用户会话列表: userID=%s", userID)

	var userSessions []models.Session
	for _, session := range s.sessions {
		if session.UserID == userID {
			userSessions = append(userSessions, session)
		}
	}

	log.Printf("找到会话数量: %d", len(userSessions))
	return userSessions, nil
}

// UpdateSession 更新会话
func (s *InMemorySessionService) UpdateSession(sessionID string, req models.UpdateSessionRequest) (*models.Session, error) {
	log.Printf("更新会话: sessionID=%s", sessionID)

	session, exists := s.sessions[sessionID]
	if !exists {
		log.Printf("会话不存在: sessionID=%s", sessionID)
		return nil, ErrSessionNotFound
	}

	// 更新字段
	if req.Title != "" {
		session.Title = req.Title
	}
	if req.Status != "" {
		session.Status = req.Status
	}
	if req.Metadata != nil {
		session.Metadata = req.Metadata
	}
	session.UpdatedAt = time.Now()

	// 保存更新
	s.sessions[sessionID] = session

	log.Printf("会话更新成功: sessionID=%s", sessionID)
	return &session, nil
}

// DeleteSession 删除会话
func (s *InMemorySessionService) DeleteSession(sessionID string) error {
	log.Printf("删除会话: sessionID=%s", sessionID)

	if _, exists := s.sessions[sessionID]; !exists {
		log.Printf("会话不存在: sessionID=%s", sessionID)
		return ErrSessionNotFound
	}

	// 删除会话和相关消息
	delete(s.sessions, sessionID)
	delete(s.messages, sessionID)

	log.Printf("会话删除成功: sessionID=%s", sessionID)
	return nil
}

// AddMessage 添加消息到会话
func (s *InMemorySessionService) AddMessage(sessionID string, req models.AddMessageRequest) (*models.Message, error) {
	log.Printf("添加消息: sessionID=%s, role=%s", sessionID, req.Role)

	session, exists := s.sessions[sessionID]
	if !exists {
		log.Printf("会话不存在: sessionID=%s", sessionID)
		return nil, ErrSessionNotFound
	}

	now := time.Now()
	message := models.Message{
		ID:          uuid.New().String(),
		SessionID:   sessionID,
		Role:        req.Role,
		Content:     req.Content,
		ContentType: req.ContentType,
		Metadata:    req.Metadata,
		CreatedAt:   now,
	}

	// 添加消息到会话
	s.messages[sessionID] = append(s.messages[sessionID], message)

	// 更新会话的最后消息时间
	session.LastMessage = &now
	session.UpdatedAt = now
	s.sessions[sessionID] = session

	log.Printf("消息添加成功: messageID=%s", message.ID)
	return &message, nil
}

// GetSessionMessages 获取会话的所有消息
func (s *InMemorySessionService) GetSessionMessages(sessionID string) ([]models.Message, error) {
	log.Printf("获取会话消息: sessionID=%s", sessionID)

	if _, exists := s.sessions[sessionID]; !exists {
		log.Printf("会话不存在: sessionID=%s", sessionID)
		return nil, ErrSessionNotFound
	}

	messages := s.messages[sessionID]
	log.Printf("找到消息数量: %d", len(messages))
	return messages, nil
}