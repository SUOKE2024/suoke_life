package common

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// FormatJSON 格式化JSON输出
func FormatJSON(data interface{}) string {
	jsonBytes, err := json.MarshalIndent(data, "", "  ")
	if err != nil {
		return fmt.Sprintf("错误: 格式化JSON失败: %v", err)
	}
	return string(jsonBytes)
}

// PrintJSON 打印格式化的JSON
func PrintJSON(data interface{}) {
	fmt.Println(FormatJSON(data))
}

// SaveResultToFile 将结果保存到文件
func SaveResultToFile(data interface{}, filename string) error {
	// 确保目录存在
	dir := filepath.Dir(filename)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return fmt.Errorf("创建目录失败: %w", err)
	}
	
	// 序列化数据
	jsonData, err := json.MarshalIndent(data, "", "  ")
	if err != nil {
		return fmt.Errorf("序列化数据失败: %w", err)
	}
	
	// 写入文件
	if err := os.WriteFile(filename, jsonData, 0644); err != nil {
		return fmt.Errorf("写入文件失败: %w", err)
	}
	
	return nil
}

// LoadJSONFromFile 从文件加载JSON数据
func LoadJSONFromFile(filename string, target interface{}) error {
	data, err := os.ReadFile(filename)
	if err != nil {
		return fmt.Errorf("读取文件失败: %w", err)
	}
	
	if err := json.Unmarshal(data, target); err != nil {
		return fmt.Errorf("解析JSON失败: %w", err)
	}
	
	return nil
}

// PrintMap 打印Map键值对
func PrintMap(m map[string]interface{}, indent string) {
	for k, v := range m {
		valueStr := fmt.Sprintf("%v", v)
		
		// 如果值是嵌套的Map，进行递归打印
		if nestedMap, ok := v.(map[string]interface{}); ok {
			fmt.Printf("%s%s:\n", indent, k)
			PrintMap(nestedMap, indent+"  ")
			continue
		}
		
		// 如果值是数组或切片，格式化输出
		if valueStr[0] == '[' && valueStr[len(valueStr)-1] == ']' {
			valueStr = strings.TrimPrefix(strings.TrimSuffix(valueStr, "]"), "[")
			items := strings.Split(valueStr, " ")
			
			if len(items) > 3 {
				fmt.Printf("%s%s: [%s ... 共%d项]\n", indent, k, strings.Join(items[:3], ", "), len(items))
			} else {
				fmt.Printf("%s%s: [%s]\n", indent, k, valueStr)
			}
			continue
		}
		
		// 如果值太长，进行截断
		if len(valueStr) > 100 {
			valueStr = valueStr[:97] + "..."
		}
		
		fmt.Printf("%s%s: %s\n", indent, k, valueStr)
	}
}

// GetCurrentTimestamp 获取当前时间戳
func GetCurrentTimestamp() string {
	return time.Now().Format("20060102-150405")
}

// MeasureExecutionTime 测量函数执行时间
func MeasureExecutionTime(name string, fn func() error) error {
	fmt.Printf("开始执行 %s...\n", name)
	start := time.Now()
	
	err := fn()
	
	duration := time.Since(start)
	fmt.Printf("执行 %s 完成, 耗时: %v\n", name, duration)
	
	return err
}

// CreateTestOutputDirectory 创建测试输出目录
func CreateTestOutputDirectory(testName string) (string, error) {
	timestamp := GetCurrentTimestamp()
	dirPath := filepath.Join("./test_results", testName, timestamp)
	
	if err := os.MkdirAll(dirPath, 0755); err != nil {
		return "", fmt.Errorf("创建测试输出目录失败: %w", err)
	}
	
	return dirPath, nil
}

// IsValidFile 检查文件是否存在且可读
func IsValidFile(filepath string) bool {
	_, err := os.Stat(filepath)
	return err == nil
}

// GenerateRandomString 生成随机字符串
func GenerateRandomString(length int) string {
	const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	b := make([]byte, length)
	for i := range b {
		b[i] = charset[time.Now().UnixNano()%int64(len(charset))]
		time.Sleep(1 * time.Nanosecond)
	}
	return string(b)
}

// PadString 填充字符串到指定长度
func PadString(str string, length int) string {
	if len(str) >= length {
		return str
	}
	return str + strings.Repeat(" ", length-len(str))
} 