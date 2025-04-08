package logger

import (
	"context"
	"os"

	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

type contextKey string

const loggerKey contextKey = "logger"

var defaultLogger *zap.SugaredLogger

// 初始化默认日志记录器
func init() {
	// 创建基础生产环境配置
	config := zap.NewProductionConfig()
	config.EncoderConfig.TimeKey = "timestamp"
	config.EncoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder

	// 根据环境变量调整日志级别
	logLevel := os.Getenv("LOG_LEVEL")
	switch logLevel {
	case "debug":
		config.Level = zap.NewAtomicLevelAt(zapcore.DebugLevel)
	case "info":
		config.Level = zap.NewAtomicLevelAt(zapcore.InfoLevel)
	case "warn":
		config.Level = zap.NewAtomicLevelAt(zapcore.WarnLevel)
	case "error":
		config.Level = zap.NewAtomicLevelAt(zapcore.ErrorLevel)
	default:
		config.Level = zap.NewAtomicLevelAt(zapcore.InfoLevel)
	}

	// 构建日志记录器
	logger, err := config.Build(
		zap.AddCallerSkip(1),
		zap.AddStacktrace(zapcore.ErrorLevel),
	)
	if err != nil {
		// 使用控制台输出作为后备
		logger = zap.NewExample()
	}

	defaultLogger = logger.Sugar()
}

// GetLogger 返回默认日志记录器
func GetLogger() *zap.SugaredLogger {
	return defaultLogger
}

// WithContext 将日志记录器添加到上下文
func WithContext(ctx context.Context, logger *zap.SugaredLogger) context.Context {
	return context.WithValue(ctx, loggerKey, logger)
}

// FromContext 从上下文获取日志记录器
func FromContext(ctx context.Context) *zap.SugaredLogger {
	if ctx == nil {
		return defaultLogger
	}
	if logger, ok := ctx.Value(loggerKey).(*zap.SugaredLogger); ok {
		return logger
	}
	return defaultLogger
}

// With 添加字段到日志记录器
func With(fields ...interface{}) *zap.SugaredLogger {
	return defaultLogger.With(fields...)
}

// 标准日志方法，用于独立使用
func Debug(msg string, keysAndValues ...interface{}) {
	defaultLogger.Debugw(msg, keysAndValues...)
}

func Info(msg string, keysAndValues ...interface{}) {
	defaultLogger.Infow(msg, keysAndValues...)
}

func Warn(msg string, keysAndValues ...interface{}) {
	defaultLogger.Warnw(msg, keysAndValues...)
}

func Error(msg string, keysAndValues ...interface{}) {
	defaultLogger.Errorw(msg, keysAndValues...)
}

func Fatal(msg string, keysAndValues ...interface{}) {
	defaultLogger.Fatalw(msg, keysAndValues...)
}

// NewStructuredLogger 创建结构化日志器
func NewStructuredLogger() *zap.SugaredLogger {
	return defaultLogger
}
