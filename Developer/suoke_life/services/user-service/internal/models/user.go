package models

import (
	"encoding/json"
	"time"

	"github.com/google/uuid"
)

// User 用户模型
type User struct {
	ID          string          `json:"id" db:"id"`
	Username    string          `json:"username" db:"username"`
	Email       string          `json:"email" db:"email"`
	Phone       string          `json:"phone" db:"phone"`
	DisplayName string          `json:"display_name" db:"display_name"`
	Avatar      string          `json:"avatar" db:"avatar"`
	Bio         string          `json:"bio" db:"bio"`
	Preferences json.RawMessage `json:"-" db:"preferences"`
	CreatedAt   time.Time       `json:"created_at" db:"created_at"`
	UpdatedAt   time.Time       `json:"updated_at" db:"updated_at"`
	LastSeen    time.Time       `json:"last_seen" db:"last_seen"`
	
	// 解析后的偏好设置
	UserPrefs UserPrefs `json:"preferences" db:"-"`
}

// UserPrefs 用户偏好设置
type UserPrefs struct {
	Theme            string            `json:"theme,omitempty"`
	Language         string            `json:"language,omitempty"`
	Notifications    bool              `json:"notifications,omitempty"`
	EmailFrequency   string            `json:"email_frequency,omitempty"`
	HealthGoals      []string          `json:"health_goals,omitempty"`
	DietPreferences  []string          `json:"diet_preferences,omitempty"`
	ActivityLevel    string            `json:"activity_level,omitempty"`
	SleepHours       int               `json:"sleep_hours,omitempty"`
	TCMConstitution  string            `json:"tcm_constitution,omitempty"`
	CustomSettings   map[string]string `json:"custom_settings,omitempty"`
}

// PrivacySettings 隐私设置
type PrivacySettings struct {
	ProfileVisibility string `json:"profile_visibility"` // public, friends, private
	ShowHealthData    bool   `json:"show_health_data"`
	ShowActivities    bool   `json:"show_activities"`
}

// BodyMeasurements 身体测量
type BodyMeasurements struct {
	Height         float64 `json:"height"`         // 身高(cm)
	Weight         float64 `json:"weight"`         // 体重(kg)
	Age            int     `json:"age"`            // 年龄
	Gender         string  `json:"gender"`         // 性别
	ActivityLevel  string  `json:"activity_level"` // 活动水平: sedentary, light, moderate, active, very_active
	BodyFatPercent float64 `json:"body_fat_percent,omitempty"`
	WaistCirc      float64 `json:"waist_circ,omitempty"` // 腰围(cm)
	HipCirc        float64 `json:"hip_circ,omitempty"`   // 臀围(cm)
}

// UserProfile 用户公开资料
type UserProfile struct {
	ID          string    `json:"id"`
	Username    string    `json:"username"`
	DisplayName string    `json:"display_name"`
	Avatar      string    `json:"avatar,omitempty"`
	Bio         string    `json:"bio,omitempty"`
	CreatedAt   time.Time `json:"created_at"`
	LastSeen    time.Time `json:"last_seen"`
	OnlineStatus string   `json:"online_status"`
}

// UserFilter 用户筛选条件
type UserFilter struct {
	Username    string `json:"username,omitempty"`
	Email       string `json:"email,omitempty"`
	DisplayName string `json:"display_name,omitempty"`
	SortBy      string `json:"sort_by,omitempty"`     // 排序字段
	SortOrder   string `json:"sort_order,omitempty"`  // 排序顺序：asc 或 desc
	Limit       int    `json:"limit,omitempty"`       // 默认50
	Offset      int    `json:"offset,omitempty"`      // 默认0
}

// UserUpdate 用户更新结构
type UserUpdate struct {
	DisplayName *string `json:"display_name,omitempty"`
	Avatar      *string `json:"avatar,omitempty"`
	Bio         *string `json:"bio,omitempty"`
	Email       *string `json:"email,omitempty"`
	Phone       *string `json:"phone,omitempty"`
}

// IsEmpty 检查更新结构是否为空
func (u *UserUpdate) IsEmpty() bool {
	return u.DisplayName == nil && u.Avatar == nil && u.Bio == nil && u.Email == nil && u.Phone == nil
}

// PrepareUserPrefs 准备用户偏好设置
func (u *User) PrepareUserPrefs() error {
	if len(u.Preferences) > 0 {
		if err := json.Unmarshal(u.Preferences, &u.UserPrefs); err != nil {
			return err
		}
	} else {
		// 设置默认值
		u.UserPrefs = UserPrefs{
			Theme:          "system",
			Language:       "zh-CN",
			Notifications:  true,
			EmailFrequency: "weekly",
		}
	}
	return nil
}

// SaveUserPrefs 保存用户偏好设置
func (u *User) SaveUserPrefs() error {
	prefs, err := json.Marshal(u.UserPrefs)
	if err != nil {
		return err
	}
	u.Preferences = prefs
	return nil
}

// ToProfile 转换为用户资料
func (u *User) ToProfile() *UserProfile {
	// 计算在线状态
	onlineStatus := "offline"
	if time.Since(u.LastSeen) < 5*time.Minute {
		onlineStatus = "online"
	} else if time.Since(u.LastSeen) < 30*time.Minute {
		onlineStatus = "away"
	}
	
	return &UserProfile{
		ID:           u.ID,
		Username:     u.Username,
		DisplayName:  u.DisplayName,
		Avatar:       u.Avatar,
		Bio:          u.Bio,
		CreatedAt:    u.CreatedAt,
		LastSeen:     u.LastSeen,
		OnlineStatus: onlineStatus,
	}
}

// Validate 验证用户数据
func (u *User) Validate() []string {
	var errors []string
	
	if u.Username == "" {
		errors = append(errors, "用户名不能为空")
	}
	
	if len(u.Username) < 3 {
		errors = append(errors, "用户名长度必须至少为3个字符")
	}
	
	if u.Email == "" {
		errors = append(errors, "邮箱不能为空")
	}
	
	// 更多验证规则可以在这里添加
	
	return errors
}

// NewUser 创建新用户
func NewUser(username, email string) *User {
	now := time.Now()
	return &User{
		ID:          GenerateUniqueID(),
		Username:    username,
		Email:       email,
		DisplayName: username, // 默认使用用户名作为显示名
		Preferences: DefaultUserPrefs(),
		CreatedAt:   now,
		UpdatedAt:   now,
		LastSeen:    now,
	}
}

// DefaultUserPrefs 返回默认用户偏好
func DefaultUserPrefs() json.RawMessage {
	prefs := UserPrefs{
		Theme:          "system",
		Language:       "zh-CN",
		Notifications:  true,
		EmailFrequency: "weekly",
	}
	prefsJSON, _ := json.Marshal(prefs)
	return prefsJSON
}

// GenerateUniqueID 生成唯一ID
func GenerateUniqueID() string {
	return uuid.New().String()
} 