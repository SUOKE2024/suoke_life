package logger

import (
	"os"
	"sync"

	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

var (
	// 全局日志对象
	log *zap.Logger
	// 确保只初始化一次的互斥锁
	once sync.Once
)

// InitLogger 初始化日志
func InitLogger(level string) {
	once.Do(func() {
		// 设置日志级别
		var logLevel zapcore.Level
		switch level {
		case "debug":
			logLevel = zapcore.DebugLevel
		case "info":
			logLevel = zapcore.InfoLevel
		case "warn":
			logLevel = zapcore.WarnLevel
		case "error":
			logLevel = zapcore.ErrorLevel
		default:
			logLevel = zapcore.InfoLevel
		}

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

		// 创建核心配置
		core := zapcore.NewCore(
			zapcore.NewJSONEncoder(encoderConfig),
			zapcore.NewMultiWriteSyncer(zapcore.AddSync(os.Stdout)),
			logLevel,
		)

		// 创建日志对象
		log = zap.New(core, zap.AddCaller(), zap.AddCallerSkip(1))
	})
}

// Logger 返回全局日志对象
func Logger() *zap.Logger {
	if log == nil {
		InitLogger("info") // 默认使用info级别
	}
	return log
}

// Debug 输出调试级别日志
func Debug(msg string, fields ...zap.Field) {
	Logger().Debug(msg, fields...)
}

// Info 输出信息级别日志
func Info(msg string, fields ...zap.Field) {
	Logger().Info(msg, fields...)
}

// Warn 输出警告级别日志
func Warn(msg string, fields ...zap.Field) {
	Logger().Warn(msg, fields...)
}

// Error 输出错误级别日志
func Error(msg string, fields ...zap.Field) {
	Logger().Error(msg, fields...)
}

// Fatal 输出致命错误级别日志并退出
func Fatal(msg string, fields ...zap.Field) {
	Logger().Fatal(msg, fields...)
}

// WithFields 创建带字段的日志
func WithFields(fields ...zap.Field) *zap.Logger {
	return Logger().With(fields...)
}

// NewLogger 创建一个新的日志记录器实例
func NewLogger(level string, output string) (*zap.Logger, error) {
	// 设置日志级别
	var logLevel zapcore.Level
	switch level {
	case "debug":
		logLevel = zapcore.DebugLevel
	case "info":
		logLevel = zapcore.InfoLevel
	case "warn":
		logLevel = zapcore.WarnLevel
	case "error":
		logLevel = zapcore.ErrorLevel
	default:
		logLevel = zapcore.InfoLevel
	}

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

	// 根据output参数决定输出位置
	var writeSyncer zapcore.WriteSyncer
	switch output {
	case "file":
		// 确保日志目录存在
		if err := os.MkdirAll("logs", 0755); err != nil {
			return nil, err
		}
		// 打开日志文件
		logFile, err := os.OpenFile("logs/app.log", os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0644)
		if err != nil {
			return nil, err
		}
		writeSyncer = zapcore.AddSync(logFile)
	case "console":
		writeSyncer = zapcore.AddSync(os.Stdout)
	default:
		// 默认同时输出到控制台和文件
		fileWriter, err := os.OpenFile("logs/app.log", os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0644)
		if err != nil {
			return nil, err
		}
		writeSyncer = zapcore.NewMultiWriteSyncer(
			zapcore.AddSync(os.Stdout),
			zapcore.AddSync(fileWriter),
		)
	}

	// 创建核心配置
	var encoder zapcore.Encoder
	if output == "console" {
		encoder = zapcore.NewConsoleEncoder(encoderConfig)
	} else {
		encoder = zapcore.NewJSONEncoder(encoderConfig)
	}

	core := zapcore.NewCore(
		encoder,
		writeSyncer,
		logLevel,
	)

	// 创建日志对象
	logger := zap.New(core, zap.AddCaller(), zap.AddCallerSkip(1))
	
	// 设置全局日志对象
	zap.ReplaceGlobals(logger)
	
	return logger, nil
} 