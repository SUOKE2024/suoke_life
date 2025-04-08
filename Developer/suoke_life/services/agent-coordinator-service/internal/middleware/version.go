package middleware

import (
	"os"
	"runtime"
	"time"

	"github.com/gin-gonic/gin"
)

// VersionInfo 应用版本信息
type VersionInfo struct {
	Version    string `json:"version"`    // 应用版本号
	BuildTime  string `json:"buildTime"`  // 构建时间
	GitCommit  string `json:"gitCommit"`  // Git提交ID
	GoVersion  string `json:"goVersion"`  // Go版本
	OS         string `json:"os"`         // 操作系统
	Arch       string `json:"arch"`       // 系统架构
	StartTime  string `json:"startTime"`  // 服务启动时间
	APIVersion string `json:"apiVersion"` // API版本
	Hostname   string `json:"hostname"`   // 主机名
}

var (
	// 版本信息，构建时注入
	version    = "dev"
	buildTime  = ""
	gitCommit  = ""
	startTime  = time.Now().Format(time.RFC3339)
	apiVersion = "v1"
)

// GetVersionInfo 获取版本信息
func GetVersionInfo() VersionInfo {
	if buildTime == "" {
		buildTime = time.Now().Format(time.RFC3339)
	}

	hostname, _ := os.Hostname()

	return VersionInfo{
		Version:    version,
		BuildTime:  buildTime,
		GitCommit:  gitCommit,
		GoVersion:  runtime.Version(),
		OS:         runtime.GOOS,
		Arch:       runtime.GOARCH,
		StartTime:  startTime,
		APIVersion: apiVersion,
		Hostname:   hostname,
	}
}

// VersionMiddleware 版本信息中间件
func VersionMiddleware() gin.HandlerFunc {
	versionInfo := GetVersionInfo()
	
	return func(c *gin.Context) {
		// 在每个响应中添加版本信息头
		c.Header("X-App-Version", versionInfo.Version)
		c.Header("X-API-Version", versionInfo.APIVersion)
		
		// 将版本信息放入上下文中，以便处理程序可以使用
		c.Set("version_info", versionInfo)
		
		c.Next()
	}
}

// WithVersion 在响应中添加版本信息
func WithVersion(data gin.H) gin.H {
	versionInfo := GetVersionInfo()
	
	// 如果传入的是nil，创建一个新的map
	if data == nil {
		data = gin.H{}
	}
	
	// 添加版本信息
	data["version"] = versionInfo.Version
	data["apiVersion"] = versionInfo.APIVersion
	
	return data
}

// VersionHandler 返回完整版本信息的处理程序
func VersionHandler(c *gin.Context) {
	versionInfo := GetVersionInfo()
	
	c.JSON(200, gin.H{
		"message": "版本信息",
		"data": versionInfo,
	})
}