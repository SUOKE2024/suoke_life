package services

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/go-redis/redis/v8"
	"github.com/suoke-life/agent-coordinator-service/internal/models"
)

// RedisConfig 代表Redis配置
type RedisConfig struct {
	Host     string
	Port     string
	Password string
	DB       int
	PoolSize int
}

// RedisService 提供Redis持久化服务
type RedisService struct {
	client  *redis.Client
	config  *RedisConfig
	timeout time.Duration
	ctx     context.Context
}

// NewRedisService 创建新的Redis服务实例
func NewRedisService(config *RedisConfig) (*RedisService, error) {
	if config == nil {
		config = &RedisConfig{
			Host:     "localhost",
			Port:     "6379",
			Password: "",
			DB:       0,
			PoolSize: 10,
		}
	}

	client := redis.NewClient(&redis.Options{
		Addr:         fmt.Sprintf("%s:%s", config.Host, config.Port),
		Password:     config.Password,
		DB:           config.DB,
		PoolSize:     config.PoolSize,
		MinIdleConns: 2,
		MaxRetries:   3,
		DialTimeout:  5 * time.Second,
		ReadTimeout:  3 * time.Second,
		WriteTimeout: 3 * time.Second,
	})

	ctx := context.Background()
	// 验证连接
	_, err := client.Ping(ctx).Result()
	if err != nil {
		return nil, fmt.Errorf("无法连接到Redis: %w", err)
	}

	return &RedisService{
		client:  client,
		config:  config,
		timeout: 30 * time.Minute, // 默认会话超时
		ctx:     ctx,
	}, nil
}

// 会话存储相关方法

// SaveSession 保存会话到Redis
func (rs *RedisService) SaveSession(session *models.Session) error {
	sessionBytes, err := json.Marshal(session)
	if err != nil {
		return fmt.Errorf("序列化会话失败: %w", err)
	}

	key := fmt.Sprintf("session:%s", session.ID)
	err = rs.client.Set(rs.ctx, key, sessionBytes, rs.timeout).Err()
	if err != nil {
		return fmt.Errorf("保存会话到Redis失败: %w", err)
	}

	return nil
}

// GetSession 从Redis获取会话
func (rs *RedisService) GetSession(sessionID string) (*models.Session, error) {
	key := fmt.Sprintf("session:%s", sessionID)
	sessionBytes, err := rs.client.Get(rs.ctx, key).Bytes()
	if err != nil {
		if err == redis.Nil {
			return nil, fmt.Errorf("会话不存在")
		}
		return nil, fmt.Errorf("从Redis获取会话失败: %w", err)
	}

	var session models.Session
	if err := json.Unmarshal(sessionBytes, &session); err != nil {
		return nil, fmt.Errorf("反序列化会话失败: %w", err)
	}

	// 刷新过期时间
	rs.client.Expire(rs.ctx, key, rs.timeout)

	return &session, nil
}

// DeleteSession 从Redis删除会话
func (rs *RedisService) DeleteSession(sessionID string) error {
	key := fmt.Sprintf("session:%s", sessionID)
	err := rs.client.Del(rs.ctx, key).Err()
	if err != nil {
		return fmt.Errorf("从Redis删除会话失败: %w", err)
	}

	return nil
}

// ListSessionIDs 列出所有会话ID
func (rs *RedisService) ListSessionIDs() ([]string, error) {
	pattern := "session:*"
	keys, err := rs.client.Keys(rs.ctx, pattern).Result()
	if err != nil {
		return nil, fmt.Errorf("列出会话失败: %w", err)
	}

	// 从键中提取会话ID
	sessionIDs := make([]string, 0, len(keys))
	for _, key := range keys {
		// 格式: "session:uuid"，我们需要提取uuid部分
		sessionID := key[8:] // 去除前缀"session:"
		sessionIDs = append(sessionIDs, sessionID)
	}

	return sessionIDs, nil
}

// SaveState 保存任意状态数据
func (rs *RedisService) SaveState(key string, value interface{}, expiration time.Duration) error {
	valueBytes, err := json.Marshal(value)
	if err != nil {
		return fmt.Errorf("序列化状态数据失败: %w", err)
	}

	err = rs.client.Set(rs.ctx, key, valueBytes, expiration).Err()
	if err != nil {
		return fmt.Errorf("保存状态到Redis失败: %w", err)
	}

	return nil
}

// GetState 获取状态数据
func (rs *RedisService) GetState(key string, value interface{}) error {
	valueBytes, err := rs.client.Get(rs.ctx, key).Bytes()
	if err != nil {
		if err == redis.Nil {
			return fmt.Errorf("状态数据不存在")
		}
		return fmt.Errorf("从Redis获取状态失败: %w", err)
	}

	if err := json.Unmarshal(valueBytes, value); err != nil {
		return fmt.Errorf("反序列化状态数据失败: %w", err)
	}

	return nil
}

// Close 关闭Redis连接
func (rs *RedisService) Close() error {
	return rs.client.Close()
}

// SetTimeout 设置会话超时时间
func (rs *RedisService) SetTimeout(timeout time.Duration) {
	rs.timeout = timeout
}

// 批量操作方法

// SaveMultiple 批量保存数据
func (rs *RedisService) SaveMultiple(keyValuePairs map[string]interface{}, expiration time.Duration) error {
	pipe := rs.client.Pipeline()
	
	for key, value := range keyValuePairs {
		valueBytes, err := json.Marshal(value)
		if err != nil {
			return fmt.Errorf("序列化数据失败: %w", err)
		}
		pipe.Set(rs.ctx, key, valueBytes, expiration)
	}
	
	_, err := pipe.Exec(rs.ctx)
	if err != nil {
		return fmt.Errorf("批量保存数据到Redis失败: %w", err)
	}
	
	return nil
}

// DeleteMultiple 批量删除数据
func (rs *RedisService) DeleteMultiple(keys []string) error {
	if len(keys) == 0 {
		return nil
	}
	
	err := rs.client.Del(rs.ctx, keys...).Err()
	if err != nil {
		return fmt.Errorf("批量删除数据失败: %w", err)
	}
	
	return nil
}

// Increment 原子递增
func (rs *RedisService) Increment(key string) (int64, error) {
	val, err := rs.client.Incr(rs.ctx, key).Result()
	if err != nil {
		return 0, fmt.Errorf("递增操作失败: %w", err)
	}
	return val, nil
}

// Decrement 原子递减
func (rs *RedisService) Decrement(key string) (int64, error) {
	val, err := rs.client.Decr(rs.ctx, key).Result()
	if err != nil {
		return 0, fmt.Errorf("递减操作失败: %w", err)
	}
	return val, nil
} 