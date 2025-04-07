package logger

import (
	"fmt"
	"log"
	"os"
)

// Logger 定义日志接口
type Logger interface {
	Debug(msg string, keysAndValues ...interface{})
	Info(msg string, keysAndValues ...interface{})
	Warn(msg string, keysAndValues ...interface{})
	Error(msg string, keysAndValues ...interface{})
	Fatal(msg string, keysAndValues ...interface{})
}

// StructuredLogger 结构化日志实现
type StructuredLogger struct {
	debugLogger *log.Logger
	infoLogger  *log.Logger
	warnLogger  *log.Logger
	errorLogger *log.Logger
	fatalLogger *log.Logger
}

// NewStructuredLogger 创建新的结构化日志记录器
func NewStructuredLogger() Logger {
	return &StructuredLogger{
		debugLogger: log.New(os.Stdout, "DEBUG: ", log.Ldate|log.Ltime|log.Lshortfile),
		infoLogger:  log.New(os.Stdout, "INFO: ", log.Ldate|log.Ltime|log.Lshortfile),
		warnLogger:  log.New(os.Stdout, "WARN: ", log.Ldate|log.Ltime|log.Lshortfile),
		errorLogger: log.New(os.Stderr, "ERROR: ", log.Ldate|log.Ltime|log.Lshortfile),
		fatalLogger: log.New(os.Stderr, "FATAL: ", log.Ldate|log.Ltime|log.Lshortfile),
	}
}

// formatKeyValues 格式化键值对
func formatKeyValues(keysAndValues ...interface{}) string {
	if len(keysAndValues) == 0 {
		return ""
	}
	
	result := " "
	for i := 0; i < len(keysAndValues); i += 2 {
		key := keysAndValues[i]
		
		var value interface{} = "MISSING"
		if i+1 < len(keysAndValues) {
			value = keysAndValues[i+1]
		}
		
		result += key.(string) + "=" + formatValue(value) + " "
	}
	
	return result
}

// formatValue 格式化值
func formatValue(value interface{}) string {
	if value == nil {
		return "nil"
	}
	
	switch v := value.(type) {
	case string:
		return `"` + v + `"`
	case error:
		return `"` + v.Error() + `"`
	default:
		return fmt.Sprintf("%v", v)
	}
}

// Debug 输出调试级别日志
func (l *StructuredLogger) Debug(msg string, keysAndValues ...interface{}) {
	l.debugLogger.Println(msg + formatKeyValues(keysAndValues...))
}

// Info 输出信息级别日志
func (l *StructuredLogger) Info(msg string, keysAndValues ...interface{}) {
	l.infoLogger.Println(msg + formatKeyValues(keysAndValues...))
}

// Warn 输出警告级别日志
func (l *StructuredLogger) Warn(msg string, keysAndValues ...interface{}) {
	l.warnLogger.Println(msg + formatKeyValues(keysAndValues...))
}

// Error 输出错误级别日志
func (l *StructuredLogger) Error(msg string, keysAndValues ...interface{}) {
	l.errorLogger.Println(msg + formatKeyValues(keysAndValues...))
}

// Fatal 输出致命错误级别日志并退出程序
func (l *StructuredLogger) Fatal(msg string, keysAndValues ...interface{}) {
	l.fatalLogger.Fatalln(msg + formatKeyValues(keysAndValues...))
} 