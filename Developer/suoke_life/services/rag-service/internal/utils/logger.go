package utils

import (
	"fmt"
	"log"
	"os"
)

// Logger 日志接口
type Logger interface {
	// Debug 调试日志
	Debug(msg string, keysAndValues ...interface{})
	
	// Info 信息日志
	Info(msg string, keysAndValues ...interface{})
	
	// Warn 警告日志
	Warn(msg string, keysAndValues ...interface{})
	
	// Error 错误日志
	Error(msg string, keysAndValues ...interface{})
}

// LogLevel 日志级别
type LogLevel int

const (
	// DebugLevel 调试级别
	DebugLevel LogLevel = iota
	
	// InfoLevel 信息级别
	InfoLevel
	
	// WarnLevel 警告级别
	WarnLevel
	
	// ErrorLevel 错误级别
	ErrorLevel
)

// StandardLogger 标准日志器
type StandardLogger struct {
	// 日志级别
	level LogLevel
	
	// 日志记录器
	logger *log.Logger
}

// NewNoopLogger 创建空日志器
func NewNoopLogger() Logger {
	return &StandardLogger{
		level:  ErrorLevel,
		logger: log.New(os.Stderr, "", 0),
	}
}

// NewStandardLogger 创建标准日志器
func NewStandardLogger(level string) (Logger, error) {
	var logLevel LogLevel
	
	switch level {
	case "debug":
		logLevel = DebugLevel
	case "info", "":
		logLevel = InfoLevel
	case "warn":
		logLevel = WarnLevel
	case "error":
		logLevel = ErrorLevel
	default:
		return nil, fmt.Errorf("无效的日志级别: %s", level)
	}
	
	return &StandardLogger{
		level:  logLevel,
		logger: log.New(os.Stdout, "", log.LstdFlags),
	}, nil
}

// Debug 调试日志
func (l *StandardLogger) Debug(msg string, keysAndValues ...interface{}) {
	if l.level <= DebugLevel {
		l.log("DEBUG", msg, keysAndValues...)
	}
}

// Info 信息日志
func (l *StandardLogger) Info(msg string, keysAndValues ...interface{}) {
	if l.level <= InfoLevel {
		l.log("INFO", msg, keysAndValues...)
	}
}

// Warn 警告日志
func (l *StandardLogger) Warn(msg string, keysAndValues ...interface{}) {
	if l.level <= WarnLevel {
		l.log("WARN", msg, keysAndValues...)
	}
}

// Error 错误日志
func (l *StandardLogger) Error(msg string, keysAndValues ...interface{}) {
	if l.level <= ErrorLevel {
		l.log("ERROR", msg, keysAndValues...)
	}
}

// 记录日志
func (l *StandardLogger) log(level, msg string, keysAndValues ...interface{}) {
	// 构建日志消息
	logMsg := fmt.Sprintf("[%s] %s", level, msg)
	
	// 添加键值对
	if len(keysAndValues) > 0 {
		logMsg += " {"
		for i := 0; i < len(keysAndValues); i += 2 {
			key := keysAndValues[i]
			var value interface{} = "MISSING"
			if i+1 < len(keysAndValues) {
				value = keysAndValues[i+1]
			}
			logMsg += fmt.Sprintf(" %v=%v", key, value)
		}
		logMsg += " }"
	}
	
	l.logger.Println(logMsg)
}