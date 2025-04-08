package utils

import (
	"strings"
	"regexp"
)

// JoinStrings 使用指定的分隔符连接字符串数组
func JoinStrings(strs []string, sep string) string {
	return strings.Join(strs, sep)
}

// TrimSpaceAndQuotes 去除字符串前后的空格和引号
func TrimSpaceAndQuotes(s string) string {
	s = strings.TrimSpace(s)
	if len(s) >= 2 && (s[0] == '"' && s[len(s)-1] == '"' || s[0] == '\'' && s[len(s)-1] == '\'') {
		return s[1 : len(s)-1]
	}
	return s
}

// EscapeQuotes 转义字符串中的引号，用于Neo4j Cypher查询
func EscapeQuotes(s string) string {
	return strings.ReplaceAll(s, "'", "\\'")
}

// SanitizeForNeo4j 净化字符串以安全用于Neo4j查询
func SanitizeForNeo4j(s string) string {
	// 去除可能导致注入的字符
	re := regexp.MustCompile(`[;:'"]`)
	return re.ReplaceAllString(s, "")
}

// Truncate 截断字符串，超出长度部分替换为省略号
func Truncate(s string, maxLength int) string {
	if len(s) <= maxLength {
		return s
	}
	return s[:maxLength-3] + "..."
}

// StripHTMLTags 移除字符串中的HTML标签
func StripHTMLTags(s string) string {
	re := regexp.MustCompile(`<[^>]*>`)
	return re.ReplaceAllString(s, "")
}

// ConvertToLowerCamelCase 将字符串转换为小驼峰命名格式
func ConvertToLowerCamelCase(s string) string {
	// 将下划线转换为空格
	s = strings.ReplaceAll(s, "_", " ")
	// 将连字符转换为空格
	s = strings.ReplaceAll(s, "-", " ")
	
	// 分割为单词
	words := strings.Fields(s)
	if len(words) == 0 {
		return ""
	}
	
	// 第一个单词小写
	result := strings.ToLower(words[0])
	
	// 其余单词首字母大写
	for i := 1; i < len(words); i++ {
		if len(words[i]) > 0 {
			result += strings.ToUpper(words[i][:1]) + strings.ToLower(words[i][1:])
		}
	}
	
	return result
}

// IsNullOrEmpty 检查字符串是否为空或者仅包含空白字符
func IsNullOrEmpty(s string) bool {
	return len(strings.TrimSpace(s)) == 0
}

// SplitAndTrim 分割字符串并去除每部分的前后空格
func SplitAndTrim(s string, sep string) []string {
	parts := strings.Split(s, sep)
	result := make([]string, len(parts))
	
	for i, part := range parts {
		result[i] = strings.TrimSpace(part)
	}
	
	return result
}

// RemoveEmptyStrings 移除字符串数组中的空字符串
func RemoveEmptyStrings(strs []string) []string {
	result := make([]string, 0, len(strs))
	
	for _, s := range strs {
		if !IsNullOrEmpty(s) {
			result = append(result, s)
		}
	}
	
	return result
}