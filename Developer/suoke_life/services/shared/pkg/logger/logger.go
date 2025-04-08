package logger

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"time"

	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

// Logger 日志记录器接口
type Logger interface {
	Debug(msg string, keysAndValues ...interface{})
	Info(msg string, keysAndValues ...interface{})
	Warn(msg string, keysAndValues ...interface{})
	Error(msg string, keysAndValues ...interface{})
	Fatal(msg string, keysAndValues ...interface{})
	With(keysAndValues ...interface{}) Logger
}

// ZapLogger 基于zap实现的日志记录器
type ZapLogger struct {
	logger *zap.SugaredLogger
}

// 确保ZapLogger实现了Logger接口
var _ Logger = (*ZapLogger)(nil)

// NewLogger 创建新的日志记录器
func NewLogger(serviceName, logLevel, format string) Logger {
	// 解析日志级别
	level := parseLogLevel(logLevel)
	
	// 创建编码器配置
	encoderConfig := zapcore.EncoderConfig{
		TimeKey:        "time",
		LevelKey:       "level",
		NameKey:        "logger",
		CallerKey:      "caller",
		MessageKey:     "msg",
		StacktraceKey:  "stacktrace",
		LineEnding:     zapcore.DefaultLineEnding,
		EncodeLevel:    zapcore.LowercaseLevelEncoder,
		EncodeTime:     zapcore.ISO8601TimeEncoder,
		EncodeDuration: zapcore.SecondsDurationEncoder,
		EncodeCaller:   zapcore.ShortCallerEncoder,
	}

	// 根据格式选择编码器
	var encoder zapcore.Encoder
	if format == "json" {
		encoder = zapcore.NewJSONEncoder(encoderConfig)
	} else {
		encoder = zapcore.NewConsoleEncoder(encoderConfig)
	}

	// 输出位置
	var writer io.Writer
	if logLoc := os.Getenv("LOG_FILE"); logLoc != "" {
		file, err := os.OpenFile(logLoc, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
		if err == nil {
			writer = file
		} else {
			// 如果打开文件失败，回退到标准输出
			fmt.Fprintf(os.Stderr, "Failed to open log file: %v\n", err)
			writer = os.Stdout
		}
	} else {
		writer = os.Stdout
	}

	// 创建核心
	core := zapcore.NewCore(
		encoder,
		zapcore.AddSync(writer),
		level,
	)

	// 创建日志记录器
	zapLogger := zap.New(
		core,
		zap.AddCaller(),
		zap.AddCallerSkip(1),
		zap.AddStacktrace(zapcore.ErrorLevel),
	)

	// 添加服务名称字段
	sugar := zapLogger.Sugar().With("service", serviceName)

	return &ZapLogger{
		logger: sugar,
	}
}

// Debug 记录调试级别日志
func (l *ZapLogger) Debug(msg string, keysAndValues ...interface{}) {
	l.logger.Debugw(msg, keysAndValues...)
}

// Info 记录信息级别日志
func (l *ZapLogger) Info(msg string, keysAndValues ...interface{}) {
	l.logger.Infow(msg, keysAndValues...)
}

// Warn 记录警告级别日志
func (l *ZapLogger) Warn(msg string, keysAndValues ...interface{}) {
	l.logger.Warnw(msg, keysAndValues...)
}

// Error 记录错误级别日志
func (l *ZapLogger) Error(msg string, keysAndValues ...interface{}) {
	l.logger.Errorw(msg, keysAndValues...)
}

// Fatal 记录致命级别日志
func (l *ZapLogger) Fatal(msg string, keysAndValues ...interface{}) {
	l.logger.Fatalw(msg, keysAndValues...)
}

// With 返回带有指定字段的新日志记录器
func (l *ZapLogger) With(keysAndValues ...interface{}) Logger {
	return &ZapLogger{
		logger: l.logger.With(keysAndValues...),
	}
}

// parseLogLevel 解析日志级别字符串
func parseLogLevel(level string) zapcore.Level {
	switch level {
	case "debug":
		return zapcore.DebugLevel
	case "info":
		return zapcore.InfoLevel
	case "warn":
		return zapcore.WarnLevel
	case "error":
		return zapcore.ErrorLevel
	case "fatal":
		return zapcore.FatalLevel
	default:
		return zapcore.InfoLevel
	}
}

// LoggerMiddleware 创建用于HTTP服务的日志中间件
func LoggerMiddleware(logger Logger) func(next http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			start := time.Now()

			// 创建响应记录器
			recorder := &responseRecorder{
				ResponseWriter: w,
				statusCode:     http.StatusOK,
			}

			// 处理请求
			next.ServeHTTP(recorder, r)

			// 计算请求处理时间
			duration := time.Since(start)

			// 记录请求信息
			logger.Info("HTTP请求",
				"method", r.Method,
				"path", r.URL.Path,
				"status", recorder.statusCode,
				"duration", duration,
				"ip", r.RemoteAddr,
				"user_agent", r.UserAgent(),
			)
		})
	}
}

// responseRecorder 包装http.ResponseWriter以记录状态码
type responseRecorder struct {
	http.ResponseWriter
	statusCode int
}

// WriteHeader 重写以捕获状态码
func (r *responseRecorder) WriteHeader(statusCode int) {
	r.statusCode = statusCode
	r.ResponseWriter.WriteHeader(statusCode)
}

// StatusCode 返回记录的状态码
func (r *responseRecorder) StatusCode() int {
	return r.statusCode
} 