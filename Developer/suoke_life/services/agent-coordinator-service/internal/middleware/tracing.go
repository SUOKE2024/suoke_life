package middleware

import (
	"context"
	"fmt"
	"log"

	"github.com/gin-gonic/gin"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
	"go.opentelemetry.io/otel/exporters/stdout/stdouttrace"
	"go.opentelemetry.io/otel/propagation"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.12.0"
	"go.opentelemetry.io/otel/trace"
)

// TracingConfig 表示追踪配置
type TracingConfig struct {
	ServiceName    string
	ServiceVersion string
	Environment    string
	Endpoint       string
	Enabled        bool
	UseStdout      bool
}

var (
	tracer trace.Tracer
)

// InitTracing 初始化OpenTelemetry追踪器
func InitTracing(cfg *TracingConfig) (func(), error) {
	if !cfg.Enabled {
		log.Println("追踪功能未启用")
		return func() {}, nil
	}

	if cfg.ServiceName == "" {
		cfg.ServiceName = "agent-coordinator-service"
	}

	if cfg.ServiceVersion == "" {
		cfg.ServiceVersion = "unknown"
	}

	if cfg.Environment == "" {
		cfg.Environment = "production"
	}

	// 创建资源
	res, err := resource.New(context.Background(),
		resource.WithAttributes(
			semconv.ServiceNameKey.String(cfg.ServiceName),
			semconv.ServiceVersionKey.String(cfg.ServiceVersion),
			attribute.String("environment", cfg.Environment),
		),
	)
	if err != nil {
		return nil, fmt.Errorf("创建资源失败: %w", err)
	}

	// 选择导出器
	var exporter sdktrace.SpanExporter
	var cleanupFunc func()

	if cfg.UseStdout {
		// 使用标准输出导出器（仅用于开发环境）
		exporter, err = stdouttrace.New(stdouttrace.WithPrettyPrint())
		cleanupFunc = func() {}
	} else {
		// 使用OTLP导出器（用于生产环境）
		ctx := context.Background()
		opts := []otlptracegrpc.Option{
			otlptracegrpc.WithEndpoint(cfg.Endpoint),
			otlptracegrpc.WithInsecure(),
		}
		client := otlptracegrpc.NewClient(opts...)
		exporter, err = otlptrace.New(ctx, client)
		cleanupFunc = func() {
			if err := exporter.Shutdown(ctx); err != nil {
				log.Printf("关闭追踪导出器失败: %v", err)
			}
		}
	}

	if err != nil {
		return nil, fmt.Errorf("创建导出器失败: %w", err)
	}

	// 创建TraceProvider
	tp := sdktrace.NewTracerProvider(
		sdktrace.WithSampler(sdktrace.AlwaysSample()),
		sdktrace.WithBatcher(exporter),
		sdktrace.WithResource(res),
	)

	// 设置全局TracerProvider
	otel.SetTracerProvider(tp)

	// 设置全局Propagator
	otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
		propagation.TraceContext{},
		propagation.Baggage{},
	))

	// 获取tracer实例
	tracer = tp.Tracer(cfg.ServiceName)

	return cleanupFunc, nil
}

// TracingMiddleware 创建追踪中间件
func TracingMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		if tracer == nil {
			c.Next()
			return
		}

		// 提取父级span，如果存在的话
		propagator := otel.GetTextMapPropagator()
		ctx := propagator.Extract(c.Request.Context(), propagation.HeaderCarrier(c.Request.Header))

		// 创建新的span
		spanName := fmt.Sprintf("%s %s", c.Request.Method, c.Request.URL.Path)
		ctx, span := tracer.Start(
			ctx,
			spanName,
			trace.WithAttributes(
				semconv.HTTPMethodKey.String(c.Request.Method),
				semconv.HTTPURLKey.String(c.Request.URL.String()),
				semconv.HTTPHostKey.String(c.Request.Host),
				semconv.HTTPUserAgentKey.String(c.Request.UserAgent()),
			),
		)
		defer span.End()

		// 在Gin上下文中保存追踪上下文
		c.Request = c.Request.WithContext(ctx)

		// 处理请求
		c.Next()

		// 添加响应属性
		span.SetAttributes(
			semconv.HTTPStatusCodeKey.Int(c.Writer.Status()),
		)

		// 如果有错误，在span中记录错误
		if len(c.Errors) > 0 {
			span.RecordError(fmt.Errorf("请求处理错误: %v", c.Errors.String()))
		}
	}
}

// StartSpan 在业务代码中开始新的span
func StartSpan(ctx context.Context, name string) (context.Context, trace.Span) {
	if tracer == nil {
		// 如果追踪未初始化，返回空span
		return ctx, trace.SpanFromContext(ctx)
	}
	return tracer.Start(ctx, name)
}

// AddSpanEvent 向当前span添加事件
func AddSpanEvent(ctx context.Context, name string, attributes ...attribute.KeyValue) {
	span := trace.SpanFromContext(ctx)
	span.AddEvent(name, trace.WithAttributes(attributes...))
}

// AddSpanAttributes 向当前span添加属性
func AddSpanAttributes(ctx context.Context, attributes ...attribute.KeyValue) {
	span := trace.SpanFromContext(ctx)
	span.SetAttributes(attributes...)
}

// RecordSpanError 记录span错误
func RecordSpanError(ctx context.Context, err error) {
	if err == nil {
		return
	}
	span := trace.SpanFromContext(ctx)
	span.RecordError(err)
} 