package logger

import (
	"io"
	"os"
	"path/filepath"

	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

var (
	// Log 全局日志实例
	Log *zap.SugaredLogger
)

func init() {
	// 默认初始化为标准输出的logger，确保在调用任何日志函数前Log不为nil
	consoleEncoder := zapcore.NewConsoleEncoder(zapcore.EncoderConfig{
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
	})
	
	core := zapcore.NewCore(
		consoleEncoder,
		zapcore.AddSync(os.Stdout),
		zapcore.InfoLevel,
	)
	
	logger := zap.New(core, zap.AddCaller(), zap.AddCallerSkip(1))
	Log = logger.Sugar()
}

// Config 日志配置
type Config struct {
	Level      string
	Filename   string
	MaxSize    int
	MaxBackups int
	MaxAge     int
	Compress   bool
	Debug      bool
}

// InitLogger 初始化日志系统
func InitLogger(level string, logPath string, debug bool) error {
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

	// 确保日志目录存在
	if err := os.MkdirAll(filepath.Dir(logPath), 0755); err != nil {
		return err
	}

	// 创建日志文件
	file, err := os.OpenFile(
		logPath,
		os.O_CREATE|os.O_APPEND|os.O_WRONLY,
		0644,
	)
	if err != nil {
		return err
	}

	// 构建编码器配置
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

	// 定义日志输出
	var writers []zapcore.WriteSyncer
	writers = append(writers, zapcore.AddSync(file))
	
	// 开发模式下同时输出到控制台
	if debug {
		writers = append(writers, zapcore.AddSync(os.Stdout))
	}
	
	// 创建多重输出
	multiWriter := zapcore.NewMultiWriteSyncer(writers...)

	// 创建核心
	var core zapcore.Core
	if debug {
		// 开发模式使用控制台编码器
		core = zapcore.NewCore(
			zapcore.NewConsoleEncoder(encoderConfig),
			multiWriter,
			logLevel,
		)
	} else {
		// 生产模式使用JSON编码器
		core = zapcore.NewCore(
			zapcore.NewJSONEncoder(encoderConfig),
			multiWriter,
			logLevel,
		)
	}

	// 创建Logger
	logger := zap.New(
		core,
		zap.AddCaller(),
		zap.AddCallerSkip(1),
		zap.AddStacktrace(zapcore.ErrorLevel),
	)

	// 设置全局实例
	Log = logger.Sugar()
	
	return nil
}

// Close 关闭日志
func Close() {
	if Log != nil {
		_ = Log.Sync()
	}
}

// Debug 调试日志
func Debug(args ...interface{}) {
	if Log != nil {
		Log.Debug(args...)
	}
}

// Debugf 格式化调试日志
func Debugf(format string, args ...interface{}) {
	if Log != nil {
		Log.Debugf(format, args...)
	}
}

// Info 信息日志
func Info(args ...interface{}) {
	if Log != nil {
		Log.Info(args...)
	}
}

// Infof 格式化信息日志
func Infof(format string, args ...interface{}) {
	if Log != nil {
		Log.Infof(format, args...)
	}
}

// Warn 警告日志
func Warn(args ...interface{}) {
	if Log != nil {
		Log.Warn(args...)
	}
}

// Warnf 格式化警告日志
func Warnf(format string, args ...interface{}) {
	if Log != nil {
		Log.Warnf(format, args...)
	}
}

// Error 错误日志
func Error(args ...interface{}) {
	if Log != nil {
		Log.Error(args...)
	}
}

// Errorf 格式化错误日志
func Errorf(format string, args ...interface{}) {
	if Log != nil {
		Log.Errorf(format, args...)
	}
}

// Fatal 致命错误日志
func Fatal(args ...interface{}) {
	if Log != nil {
		Log.Fatal(args...)
	}
}

// Fatalf 格式化致命错误日志
func Fatalf(format string, args ...interface{}) {
	if Log != nil {
		Log.Fatalf(format, args...)
	}
}

// WithFields 添加字段信息
func WithFields(fields map[string]interface{}) *zap.SugaredLogger {
	if Log == nil {
		return nil
	}
	
	args := make([]interface{}, 0, len(fields)*2)
	for k, v := range fields {
		args = append(args, k, v)
	}
	return Log.With(args...)
}

// GetLogWriter 获取日志写入器，与Gin日志集成
func GetLogWriter(logPath string) io.Writer {
	if err := os.MkdirAll(filepath.Dir(logPath), 0755); err != nil {
		Log.Errorf("无法创建日志目录: %v", err)
		return os.Stdout
	}

	file, err := os.OpenFile(
		logPath,
		os.O_CREATE|os.O_APPEND|os.O_WRONLY,
		0644,
	)
	if err != nil {
		Log.Errorf("无法打开日志文件: %v", err)
		return os.Stdout
	}

	return file
} 