package middleware

import (
	"fmt"
	"io"
	"os"
	"path/filepath"
	"time"

	"github.com/gin-gonic/gin"
	rotatelogs "github.com/lestrrat-go/file-rotatelogs"
	"github.com/suoke-life/api-gateway/internal/configs"
	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

// SetupLogger 设置日志记录器
func SetupLogger(config *configs.Config) (*zap.Logger, io.Closer) {
	// 确保日志目录存在
	logPath := config.Logging.FilePath
	if logPath == "" {
		logPath = "/var/log/api-gateway/api-gateway.log"
	}
	
	logDir := filepath.Dir(logPath)
	if _, err := os.Stat(logDir); os.IsNotExist(err) {
		err := os.MkdirAll(logDir, 0755)
		if err != nil {
			fmt.Printf("无法创建日志目录：%v\n", err)
			// 如果无法创建目录，使用临时目录
			logPath = filepath.Join(os.TempDir(), "api-gateway.log")
		}
	}

	// 设置日志轮转
	logRotator, err := rotatelogs.New(
		logPath+".%Y%m%d",
		rotatelogs.WithLinkName(logPath),
		rotatelogs.WithMaxAge(time.Duration(config.Logging.MaxAge)*24*time.Hour),
		rotatelogs.WithRotationTime(24*time.Hour),
		rotatelogs.WithRotationSize(int64(config.Logging.MaxSize)*1024*1024),
	)
	if err != nil {
		fmt.Printf("配置日志轮转失败：%v\n", err)
		return nil, nil
	}

	// 设置日志级别
	var level zapcore.Level
	switch config.Logging.Level {
	case "debug":
		level = zapcore.DebugLevel
	case "info":
		level = zapcore.InfoLevel
	case "warn":
		level = zapcore.WarnLevel
	case "error":
		level = zapcore.ErrorLevel
	default:
		level = zapcore.InfoLevel
	}

	// 设置编码器
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

	// 创建核心
	core := zapcore.NewCore(
		zapcore.NewJSONEncoder(encoderConfig),
		zapcore.AddSync(logRotator),
		level,
	)

	// 创建日志记录器
	logger := zap.New(core, zap.AddCaller(), zap.AddCallerSkip(1))

	// 设置全局日志记录器
	zap.ReplaceGlobals(logger)

	return logger, logRotator
}

// Logger 中间件，使用zap记录HTTP请求
func Logger(logger *zap.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path
		query := c.Request.URL.RawQuery
		method := c.Request.Method
		ip := c.ClientIP()

		// 处理请求
		c.Next()

		// 收集响应信息
		latency := time.Since(start)
		status := c.Writer.Status()
		size := c.Writer.Size()
		userAgent := c.Request.UserAgent()
		referer := c.Request.Referer()
		
		// 生成请求ID（如果没有）
		requestID := c.GetHeader("X-Request-ID")
		if requestID == "" {
			requestID = fmt.Sprintf("%d", time.Now().UnixNano())
			c.Header("X-Request-ID", requestID)
		}

		// 记录访问日志
		if query != "" {
			path = path + "?" + query
		}

		logger.Info("HTTP请求",
			zap.String("request_id", requestID),
			zap.String("method", method),
			zap.String("path", path),
			zap.Int("status", status),
			zap.Int("size", size),
			zap.Duration("latency", latency),
			zap.String("ip", ip),
			zap.String("user_agent", userAgent),
			zap.String("referer", referer),
		)

		// 如果有错误，记录错误信息
		for _, err := range c.Errors {
			logger.Error("请求处理错误",
				zap.String("request_id", requestID),
				zap.String("error", err.Error()),
			)
		}
	}
}