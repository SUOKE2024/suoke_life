package middleware

import (
	"os"
	"time"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

// SetupOptimizedLogger 配置高性能日志
// 优化了采样策略、缓冲写入和内存分配
func SetupOptimizedLogger() *zap.Logger {
	// 使用生产配置作为基础
	config := zap.NewProductionConfig()
	
	// 优化采样策略，避免高流量时日志过多
	config.Sampling = &zap.SamplingConfig{
		Initial:    100,  // 每秒前100条日志不采样
		Thereafter: 100,  // 之后每100条取1条
	}
	
	// 优化编码器配置，减少内存分配
	config.EncoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder
	config.EncoderConfig.EncodeDuration = zapcore.MillisDurationEncoder
	config.EncoderConfig.EncodeCaller = zapcore.ShortCallerEncoder
	
	// 配置输出
	var cores []zapcore.Core
	
	// 控制台输出
	consoleEncoder := zapcore.NewConsoleEncoder(config.EncoderConfig)
	consoleLevel := zap.NewAtomicLevelAt(zapcore.InfoLevel)
	consoleCore := zapcore.NewCore(
		consoleEncoder,
		zapcore.Lock(os.Stdout),
		consoleLevel,
	)
	cores = append(cores, consoleCore)
	
	// 文件输出 (如果日志目录存在)
	if _, err := os.Stat("logs"); err == nil {
		// 创建按日期滚动的文件
		today := time.Now().Format("2006-01-02")
		logFile, _ := os.OpenFile(
			"logs/app-"+today+".log",
			os.O_CREATE|os.O_APPEND|os.O_WRONLY,
			0644,
		)
		
		if logFile != nil {
			fileEncoder := zapcore.NewJSONEncoder(config.EncoderConfig)
			fileLevel := zap.NewAtomicLevelAt(zapcore.DebugLevel)
			fileCore := zapcore.NewCore(
				fileEncoder,
				zapcore.Lock(logFile),
				fileLevel,
			)
			cores = append(cores, fileCore)
		}
	}
	
	// 将cores组合到一起
	core := zapcore.NewTee(cores...)
	
	// 创建logger
	logger := zap.New(
		core,
		zap.AddCaller(),          // 记录调用者
		zap.AddStacktrace(zapcore.ErrorLevel), // 只对Error及以上记录堆栈
	)
	
	return logger
}

// CreateBufferedLogger 创建带缓冲的日志器
// 用于高性能场景，定期刷新日志而不是每次写入
func CreateBufferedLogger() *zap.Logger {
	// 基础配置
	encoderConfig := zap.NewProductionEncoderConfig()
	encoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder
	
	// 创建缓冲写入器
	buffer := &BufferedWriteSyncer{
		size: 0,
		max:  1024 * 1024, // 1MB缓冲区
	}
	
	// 周期性刷新日志
	go func() {
		for {
			time.Sleep(5 * time.Second)
			buffer.Sync()
		}
	}()
	
	// 创建核心
	core := zapcore.NewCore(
		zapcore.NewJSONEncoder(encoderConfig),
		zapcore.AddSync(buffer),
		zap.NewAtomicLevelAt(zapcore.InfoLevel),
	)
	
	// 创建logger
	logger := zap.New(core)
	
	return logger
}

// BufferedWriteSyncer 实现缓冲写入的日志同步器
type BufferedWriteSyncer struct {
	buffer []byte
	size   int
	max    int
	file   *os.File
}

// Write 缓冲写入
func (b *BufferedWriteSyncer) Write(p []byte) (n int, err error) {
	if b.file == nil {
		logDir := "logs"
		if _, err := os.Stat(logDir); os.IsNotExist(err) {
			os.Mkdir(logDir, 0755)
		}
		
		today := time.Now().Format("2006-01-02")
		b.file, err = os.OpenFile(
			"logs/buffered-"+today+".log",
			os.O_CREATE|os.O_APPEND|os.O_WRONLY,
			0644,
		)
		if err != nil {
			return 0, err
		}
	}
	
	// 如果缓冲区满了，刷新
	if b.size+len(p) > b.max {
		b.Sync()
	}
	
	// 添加到缓冲区
	b.buffer = append(b.buffer, p...)
	b.size += len(p)
	
	return len(p), nil
}

// Sync 刷新缓冲区
func (b *BufferedWriteSyncer) Sync() error {
	if b.size > 0 && b.file != nil {
		_, err := b.file.Write(b.buffer)
		if err != nil {
			return err
		}
		
		b.buffer = b.buffer[:0]
		b.size = 0
		
		return b.file.Sync()
	}
	return nil
}

// Logger 返回一个用于记录请求日志的Gin中间件
func Logger() gin.HandlerFunc {
	// 使用全局logger
	logger := zap.L()
	
	return func(c *gin.Context) {
		// 开始计时
		start := time.Now()
		
		// 为请求添加跟踪ID
		RequestTracker(logger)(c)
		
		// 处理请求
		c.Next()
		
		// 计算处理时间
		duration := time.Since(start)
		
		// 记录请求日志
		log := FormatRequestLog(c)
		
		// 根据状态码决定日志级别
		status := c.Writer.Status()
		if status >= 500 {
			logger.Error(log,
				zap.String("request_id", GetRequestID(c)),
				zap.Duration("duration", duration),
			)
		} else if status >= 400 {
			logger.Warn(log,
				zap.String("request_id", GetRequestID(c)),
				zap.Duration("duration", duration),
			)
		} else {
			logger.Info(log,
				zap.String("request_id", GetRequestID(c)),
				zap.Duration("duration", duration),
			)
		}
	}
} 