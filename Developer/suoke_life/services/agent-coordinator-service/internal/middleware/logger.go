package middleware

import (
	"fmt"
	"io"
	"os"
	"path/filepath"
	"time"

	"github.com/gin-gonic/gin"
)

// LoggerConfig 日志中间件配置
type LoggerConfig struct {
	// 输出写入器，默认为 gin.DefaultWriter
	Output io.Writer

	// 略过记录的路径，默认为空
	SkipPaths []string

	// 是否记录请求体，默认为 false
	LogRequestBody bool

	// 是否记录响应体，默认为 false
	LogResponseBody bool

	// 日志文件目录，默认为 "logs"
	LogDir string

	// 日志文件名格式，默认为 "access-YYYY-MM-DD.log"
	LogFileName string

	// 是否将日志同时输出到控制台，默认为 true
	AlsoToConsole bool
}

// DefaultLoggerConfig 默认日志配置
var DefaultLoggerConfig = LoggerConfig{
	LogRequestBody:  false,
	LogResponseBody: false,
	LogDir:          "logs",
	LogFileName:     "access-2006-01-02.log", // 使用 Go 的时间格式
	AlsoToConsole:   true,
}

// Logger 返回一个 Gin 日志中间件
func Logger(config ...LoggerConfig) gin.HandlerFunc {
	// 使用默认配置或提供的配置
	cfg := DefaultLoggerConfig
	if len(config) > 0 {
		cfg = config[0]
	}

	// 确保日志目录存在
	if err := os.MkdirAll(cfg.LogDir, 0755); err != nil {
		fmt.Printf("创建日志目录失败: %v\n", err)
	}

	// 配置输出
	var output io.Writer
	if cfg.Output != nil {
		output = cfg.Output
	} else {
		// 获取今天的日志文件
		logFilePath := filepath.Join(cfg.LogDir, time.Now().Format(cfg.LogFileName))
		logFile, err := os.OpenFile(logFilePath, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0644)
		if err != nil {
			fmt.Printf("打开日志文件失败: %v, 使用标准输出\n", err)
			output = os.Stdout
		} else {
			if cfg.AlsoToConsole {
				output = io.MultiWriter(os.Stdout, logFile)
			} else {
				output = logFile
			}
		}
	}

	// 设置 Gin 日志输出
	gin.DefaultWriter = output

	// 跳过的路径
	skipPaths := make(map[string]bool, len(cfg.SkipPaths))
	for _, path := range cfg.SkipPaths {
		skipPaths[path] = true
	}

	// 返回中间件函数
	return func(c *gin.Context) {
		// 如果路径需要跳过，则直接处理请求
		if _, ok := skipPaths[c.Request.URL.Path]; ok {
			c.Next()
			return
		}

		// 开始时间
		start := time.Now()
		path := c.Request.URL.Path
		raw := c.Request.URL.RawQuery
		if raw != "" {
			path = path + "?" + raw
		}

		// 处理请求
		c.Next()

		// 处理时间
		latency := time.Since(start)
		// 客户端 IP
		clientIP := c.ClientIP()
		// HTTP 方法
		method := c.Request.Method
		// HTTP 状态码
		statusCode := c.Writer.Status()
		// 错误信息
		errorMessage := c.Errors.ByType(gin.ErrorTypePrivate).String()

		// 构建日志输出
		timeFormatted := time.Now().Format("2006/01/02 - 15:04:05")
		msg := fmt.Sprintf("[GIN] %v | %3d | %13v | %15s | %-7s %s",
			timeFormatted,
			statusCode,
			latency,
			clientIP,
			method,
			path,
		)

		if errorMessage != "" {
			msg += " | " + errorMessage
		}

		// 根据状态码选择日志级别
		if statusCode >= 500 {
			fmt.Fprintf(output, "[ERROR] %s\n", msg)
		} else if statusCode >= 400 {
			fmt.Fprintf(output, "[WARNING] %s\n", msg)
		} else {
			fmt.Fprintf(output, "[INFO] %s\n", msg)
		}
	}
}

// RequestLogger 请求日志记录
func RequestLogger() gin.HandlerFunc {
	return func(c *gin.Context) {
		// 获取请求信息
		start := time.Now()
		path := c.Request.URL.Path
		method := c.Request.Method
		clientIP := c.ClientIP()
		userAgent := c.Request.UserAgent()
		
		// 调用下一个中间件
		c.Next()
		
		// 记录请求处理时间和状态码
		latency := time.Since(start)
		statusCode := c.Writer.Status()
		
		// 获取请求处理过程中可能产生的错误
		errorMsg := ""
		for _, err := range c.Errors.Errors() {
			errorMsg += err + ";"
		}
		
		// 记录日志
		logEntry := fmt.Sprintf("[%s] %s %s %d %v %s %s %s",
			time.Now().Format("2006/01/02 - 15:04:05"),
			method,
			path,
			statusCode,
			latency,
			clientIP,
			userAgent,
			errorMsg,
		)
		
		// 根据状态码选择日志级别
		if statusCode >= 500 {
			fmt.Println("[ERROR]", logEntry)
		} else if statusCode >= 400 {
			fmt.Println("[WARNING]", logEntry)
		} else {
			fmt.Println("[INFO]", logEntry)
		}
	}
}