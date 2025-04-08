package logger

import (
	"fmt"
	"log"
	"os"
	"time"
)

// Logger 定义日志接口
type Logger interface {
	Debug(msg string, args ...interface{})
	Info(msg string, args ...interface{})
	Warn(msg string, args ...interface{})
	Error(msg string, args ...interface{})
	Fatal(msg string, args ...interface{})
}

// Level 日志级别
type Level int

const (
	// DebugLevel 调试级别
	DebugLevel Level = iota
	// InfoLevel 信息级别
	InfoLevel
	// WarnLevel 警告级别
	WarnLevel
	// ErrorLevel 错误级别
	ErrorLevel
	// FatalLevel 致命级别
	FatalLevel
)

// String 返回日志级别的字符串表示
func (l Level) String() string {
	switch l {
	case DebugLevel:
		return "DEBUG"
	case InfoLevel:
		return "INFO"
	case WarnLevel:
		return "WARN"
	case ErrorLevel:
		return "ERROR"
	case FatalLevel:
		return "FATAL"
	default:
		return fmt.Sprintf("Level(%d)", l)
	}
}

// Config 日志配置
type Config struct {
	Level     Level
	FilePath  string
	MaxSize   int
	MaxBackup int
	MaxAge    int
}

// DefaultConfig 返回默认日志配置
func DefaultConfig() *Config {
	return &Config{
		Level:     InfoLevel,
		FilePath:  "",
		MaxSize:   100, // MB
		MaxBackup: 5,
		MaxAge:    30, // 天
	}
}

// SimpleLogger 是一个简单的日志实现
type SimpleLogger struct {
	level  Level
	logger *log.Logger
}

// NewLogger 创建新的日志记录器
func NewLogger(cfg *Config) Logger {
	if cfg == nil {
		cfg = DefaultConfig()
	}
	
	// 创建基础logger
	var logger *log.Logger
	if cfg.FilePath != "" {
		// 如果指定了文件路径，记录到文件
		f, err := os.OpenFile(cfg.FilePath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
		if err != nil {
			// 如果打开文件失败，回退到标准输出
			fmt.Printf("无法打开日志文件: %v, 使用标准输出\n", err)
			logger = log.New(os.Stdout, "", 0)
		} else {
			logger = log.New(f, "", 0)
		}
	} else {
		logger = log.New(os.Stdout, "", 0)
	}
	
	return &SimpleLogger{
		level:  cfg.Level,
		logger: logger,
	}
}

// log 通用日志方法
func (l *SimpleLogger) log(level Level, msg string, args ...interface{}) {
	if level < l.level {
		return
	}
	
	timestamp := time.Now().Format("2006-01-02 15:04:05")
	prefix := fmt.Sprintf("[%s] %s ", level.String(), timestamp)
	
	if len(args) > 0 && len(args)%2 == 0 {
		// 以键值对格式打印参数
		format := prefix + msg
		for i := 0; i < len(args); i += 2 {
			format += fmt.Sprintf(" %v=%v", args[i], args[i+1])
		}
		l.logger.Println(format)
	} else {
		// 简单格式
		l.logger.Println(prefix + msg)
		if len(args) > 0 {
			l.logger.Println(args...)
		}
	}
}

// Debug 输出调试级别日志
func (l *SimpleLogger) Debug(msg string, args ...interface{}) {
	l.log(DebugLevel, msg, args...)
}

// Info 输出信息级别日志
func (l *SimpleLogger) Info(msg string, args ...interface{}) {
	l.log(InfoLevel, msg, args...)
}

// Warn 输出警告级别日志
func (l *SimpleLogger) Warn(msg string, args ...interface{}) {
	l.log(WarnLevel, msg, args...)
}

// Error 输出错误级别日志
func (l *SimpleLogger) Error(msg string, args ...interface{}) {
	l.log(ErrorLevel, msg, args...)
}

// Fatal 输出致命级别日志并退出程序
func (l *SimpleLogger) Fatal(msg string, args ...interface{}) {
	l.log(FatalLevel, msg, args...)
	os.Exit(1)
} 