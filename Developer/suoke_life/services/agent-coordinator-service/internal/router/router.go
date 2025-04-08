package router

import (
	"github.com/gin-gonic/gin"
	"github.com/suoke-life/agent-coordinator-service/internal/config"
)

// SetupRouter 设置并返回Gin路由器
func SetupRouter(cfg *config.Config) *gin.Engine {
	// 根据配置设置Gin模式
	if cfg.Environment == "production" {
		gin.SetMode(gin.ReleaseMode)
	} else {
		gin.SetMode(gin.DebugMode)
	}

	// 创建默认路由
	r := gin.Default()

	return r
} 