package models

import (
	"time"

	"github.com/google/uuid"
	"golang.org/x/crypto/bcrypt"
)

// Role 用户角色
type Role string

const (
	RoleUser      Role = "user"      // 普通用户
	RoleAdmin     Role = "admin"     // 管理员
	RoleSuperUser Role = "superuser" // 超级用户
)

// User 表示用户模型
type User struct {
	ID            string    `json:"id"`
	Username      string    `json:"username"`
	Email         string    `json:"email"`
	PasswordHash  string    `json:"-"` // 不会在JSON中暴露密码哈希
	Role          Role      `json:"role"`
	Active        bool      `json:"active"`
	EmailVerified bool      `json:"email_verified"`
	CreatedAt     time.Time `json:"created_at"`
	UpdatedAt     time.Time `json:"updated_at"`
	LastLoginAt   time.Time `json:"last_login_at"`
}

// UserRegistration 用于用户注册的数据模型
type UserRegistration struct {
	Username string `json:"username" binding:"required,min=3,max=50"`
	Email    string `json:"email" binding:"required,email"`
	Password string `json:"password" binding:"required,min=8"`
}

// UserLogin 用于用户登录的数据模型
type UserLogin struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

// TokenClaims 包含JWT令牌中的自定义声明
type TokenClaims struct {
	UserID   string `json:"user_id"`
	Username string `json:"username"`
	Email    string `json:"email"`
	Role     Role   `json:"role"`
}

// TokenResponse 包含授权令牌响应
type TokenResponse struct {
	AccessToken  string `json:"access_token"`
	RefreshToken string `json:"refresh_token"`
	TokenType    string `json:"token_type"`
	ExpiresIn    int    `json:"expires_in"` // 以秒为单位
}

// PasswordReset 用于密码重置的数据模型
type PasswordReset struct {
	Email       string `json:"email" binding:"required,email"`
	Token       string `json:"token" binding:"required"`
	NewPassword string `json:"new_password" binding:"required,min=8"`
}

// CheckPassword 验证密码是否正确
func (u *User) CheckPassword(password string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(u.PasswordHash), []byte(password))
	return err == nil
}

// SetPassword 设置用户密码（加密）
func (u *User) SetPassword(password string) error {
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return err
	}
	u.PasswordHash = string(hashedPassword)
	return nil
}

// NewUser 创建新用户
func NewUser(username, email, password string) (*User, error) {
	now := time.Now()
	user := &User{
		ID:            generateUUID(), // 实际应该实现生成UUID的函数
		Username:      username,
		Email:         email,
		Role:          RoleUser, // 默认为普通用户
		Active:        true,
		EmailVerified: false, // 需要验证邮箱
		CreatedAt:     now,
		UpdatedAt:     now,
	}
	
	if err := user.SetPassword(password); err != nil {
		return nil, err
	}
	
	return user, nil
}

// generateUUID 生成唯一ID
func generateUUID() string {
	// 简化实现，实际应使用专门的UUID库
	return "user_" + time.Now().Format("20060102150405")
}

// GenerateUniqueID 生成唯一用户ID
func GenerateUniqueID() string {
	return uuid.New().String()
} 