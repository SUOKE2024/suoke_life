package helpers

import (
	"crypto/md5"
	"crypto/sha256"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"math/rand"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/google/uuid"
)

func init() {
	rand.Seed(time.Now().UnixNano())
}

// GenerateUUID 生成UUID
func GenerateUUID() string {
	return uuid.New().String()
}

// GenerateShortID 生成短ID
func GenerateShortID() string {
	id := uuid.New().String()
	return strings.ReplaceAll(id, "-", "")[:12]
}

// GenerateRandomString 生成随机字符串
func GenerateRandomString(length int) string {
	const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	b := make([]byte, length)
	for i := range b {
		b[i] = charset[rand.Intn(len(charset))]
	}
	return string(b)
}

// MD5Hash 计算MD5哈希
func MD5Hash(text string) string {
	hash := md5.Sum([]byte(text))
	return hex.EncodeToString(hash[:])
}

// SHA256Hash 计算SHA256哈希
func SHA256Hash(text string) string {
	hash := sha256.Sum256([]byte(text))
	return hex.EncodeToString(hash[:])
}

// Base64Encode Base64编码
func Base64Encode(text string) string {
	return base64.StdEncoding.EncodeToString([]byte(text))
}

// Base64Decode Base64解码
func Base64Decode(encoded string) (string, error) {
	decoded, err := base64.StdEncoding.DecodeString(encoded)
	if err != nil {
		return "", err
	}
	return string(decoded), nil
}

// Truncate 截断字符串
func Truncate(s string, max int) string {
	if len(s) <= max {
		return s
	}
	return s[:max-3] + "..."
}

// StringInSlice 检查字符串是否在切片中
func StringInSlice(a string, list []string) bool {
	for _, b := range list {
		if b == a {
			return true
		}
	}
	return false
}

// MergeSlices 合并两个切片并去重
func MergeSlices(a, b []string) []string {
	check := make(map[string]bool)
	result := []string{}
	
	for _, val := range a {
		if _, exist := check[val]; !exist {
			check[val] = true
			result = append(result, val)
		}
	}
	
	for _, val := range b {
		if _, exist := check[val]; !exist {
			check[val] = true
			result = append(result, val)
		}
	}
	
	return result
}

// CreateDirIfNotExist 创建目录（如果不存在）
func CreateDirIfNotExist(path string) error {
	if _, err := os.Stat(path); os.IsNotExist(err) {
		return os.MkdirAll(path, 0755)
	}
	return nil
}

// FileExists 检查文件是否存在
func FileExists(filename string) bool {
	info, err := os.Stat(filename)
	if os.IsNotExist(err) {
		return false
	}
	return !info.IsDir()
}

// DirExists 检查目录是否存在
func DirExists(path string) bool {
	info, err := os.Stat(path)
	if os.IsNotExist(err) {
		return false
	}
	return info.IsDir()
}

// ToJSON 转换为JSON字符串
func ToJSON(v interface{}) (string, error) {
	bytes, err := json.Marshal(v)
	if err != nil {
		return "", err
	}
	return string(bytes), nil
}

// FromJSON 从JSON字符串解析
func FromJSON(data string, v interface{}) error {
	return json.Unmarshal([]byte(data), v)
}

// PrettyJSON 格式化的JSON字符串
func PrettyJSON(v interface{}) (string, error) {
	bytes, err := json.MarshalIndent(v, "", "  ")
	if err != nil {
		return "", err
	}
	return string(bytes), nil
}

// SanitizeFilename 净化文件名
func SanitizeFilename(filename string) string {
	// 替换不允许在文件名中使用的字符
	invalid := []string{"<", ">", ":", "\"", "/", "\\", "|", "?", "*"}
	result := filename
	
	for _, char := range invalid {
		result = strings.ReplaceAll(result, char, "_")
	}
	
	return result
}

// GetFileExtension 获取文件扩展名
func GetFileExtension(filename string) string {
	return strings.ToLower(filepath.Ext(filename))
}

// FormatByteSize 格式化字节大小
func FormatByteSize(bytes int64) string {
	const unit = 1024
	if bytes < unit {
		return fmt.Sprintf("%d B", bytes)
	}
	div, exp := int64(unit), 0
	for n := bytes / unit; n >= unit; n /= unit {
		div *= unit
		exp++
	}
	return fmt.Sprintf("%.1f %cB", float64(bytes)/float64(div), "KMGTPE"[exp])
}

// ElapsedTime 计算经过的时间
func ElapsedTime(start time.Time) time.Duration {
	return time.Since(start)
}

// ElapsedTimeStr 返回易读的经过时间字符串
func ElapsedTimeStr(start time.Time) string {
	elapsed := time.Since(start)
	
	// 如果小于1秒，显示毫秒
	if elapsed < time.Second {
		return fmt.Sprintf("%d毫秒", elapsed.Milliseconds())
	}
	
	// 如果小于1分钟，显示秒
	if elapsed < time.Minute {
		return fmt.Sprintf("%.2f秒", elapsed.Seconds())
	}
	
	// 如果小于1小时，显示分钟和秒
	if elapsed < time.Hour {
		minutes := int(elapsed.Minutes())
		seconds := int(elapsed.Seconds()) % 60
		return fmt.Sprintf("%d分%d秒", minutes, seconds)
	}
	
	// 显示小时、分钟和秒
	hours := int(elapsed.Hours())
	minutes := int(elapsed.Minutes()) % 60
	seconds := int(elapsed.Seconds()) % 60
	return fmt.Sprintf("%d时%d分%d秒", hours, minutes, seconds)
}

// Retry 重试执行函数
func Retry(attempts int, sleep time.Duration, fn func() error) error {
	if err := fn(); err != nil {
		if attempts--; attempts > 0 {
			time.Sleep(sleep)
			return Retry(attempts, sleep*2, fn)
		}
		return err
	}
	return nil
}

// ChunkSlice 将切片分块
func ChunkSlice(slice []string, chunkSize int) [][]string {
	var chunks [][]string
	for i := 0; i < len(slice); i += chunkSize {
		end := i + chunkSize
		if end > len(slice) {
			end = len(slice)
		}
		chunks = append(chunks, slice[i:end])
	}
	return chunks
}

// ParseBool 安全解析布尔值
func ParseBool(val string) bool {
	switch strings.ToLower(val) {
	case "true", "yes", "1", "on", "y":
		return true
	default:
		return false
	}
}

// MapToStruct 将map转换为结构体
func MapToStruct(m map[string]interface{}, v interface{}) error {
	data, err := json.Marshal(m)
	if err != nil {
		return err
	}
	return json.Unmarshal(data, v)
}

// StructToMap 将结构体转换为map
func StructToMap(v interface{}) (map[string]interface{}, error) {
	data, err := json.Marshal(v)
	if err != nil {
		return nil, err
	}
	
	var result map[string]interface{}
	err = json.Unmarshal(data, &result)
	return result, err
} 