package utils

import (
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"time"
)

// GenerateUUID 生成一个RFC4122 v4兼容的UUID
func GenerateUUID() string {
	uuid := make([]byte, 16)
	_, err := rand.Read(uuid)
	if err != nil {
		// 如果随机数生成失败，使用时间戳作为后备方案
		return generateTimeBasedID()
	}
	
	// 设置版本位 (4) 和变种位
	uuid[6] = (uuid[6] & 0x0f) | 0x40 // 版本 4
	uuid[8] = (uuid[8] & 0x3f) | 0x80 // 变种 RFC4122
	
	return fmt.Sprintf("%x-%x-%x-%x-%x",
		uuid[0:4],
		uuid[4:6],
		uuid[6:8],
		uuid[8:10],
		uuid[10:16])
}

// GenerateShortUUID 生成一个短UUID，适用于不需要全局唯一性的情况
func GenerateShortUUID() string {
	uuid := make([]byte, 8)
	_, err := rand.Read(uuid)
	if err != nil {
		// 如果随机数生成失败，使用时间戳作为后备方案
		return fmt.Sprintf("%x", time.Now().UnixNano())
	}
	
	return hex.EncodeToString(uuid)
}

// GenerateTimeBasedUUID 生成一个基于时间的UUID
func GenerateTimeBasedUUID() string {
	return generateTimeBasedID()
}

// GenerateSequentialUUID 生成一个基于时间但还包含序列号的UUID
func GenerateSequentialUUID(sequence int) string {
	timestamp := time.Now().UnixNano()
	random := make([]byte, 4)
	_, _ = rand.Read(random)
	
	return fmt.Sprintf("%x-%x-%04x",
		timestamp,
		random,
		sequence%0xFFFF)
}

// 内部使用的基于时间的ID生成器
func generateTimeBasedID() string {
	timestamp := time.Now().UnixNano()
	random := make([]byte, 6)
	_, _ = rand.Read(random)
	
	return fmt.Sprintf("%x-%x",
		timestamp,
		random)
} 