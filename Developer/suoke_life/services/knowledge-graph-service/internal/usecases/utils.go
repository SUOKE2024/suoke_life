package usecases

import (
	"time"
)

// currentTimeISO 获取当前时间的ISO 8601格式字符串
func currentTimeISO() string {
	return time.Now().Format(time.RFC3339)
} 