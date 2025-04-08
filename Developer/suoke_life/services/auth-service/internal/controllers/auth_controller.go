package controllers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/suoke-life/auth-service/internal/models"
	"github.com/suoke-life/auth-service/internal/services"
	"github.com/suoke-life/shared/pkg/logger"
)

// AuthController 认证控制器
type AuthController struct {
	logger     logger.Logger
	jwtService *services.JWTService
	authService services.AuthService
}

// NewAuthController 创建认证控制器
func NewAuthController(log logger.Logger, jwtService *services.JWTService, authService services.AuthService) *AuthController {
	return &AuthController{
		logger:     log,
		jwtService: jwtService,
		authService: authService,
	}
}

// VerifyToken 验证令牌并返回声明信息，提供给服务器中间件使用
func (c *AuthController) VerifyToken(tokenString string) (*services.JWTClaims, error) {
	return c.jwtService.ValidateAccessToken(tokenString)
}

// Register 处理用户注册请求
func (c *AuthController) Register(ctx *gin.Context) {
	var registration models.UserRegistration

	if err := ctx.ShouldBindJSON(&registration); err != nil {
		c.logger.Error("无效的注册请求", "error", err)
		ctx.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的注册请求",
			"details": err.Error(),
		})
		return
	}

	// 创建新用户
	user, err := c.authService.Register(ctx, &registration)
	if err != nil {
		c.logger.Error("创建用户失败", "error", err)
		
		// 处理特定错误
		if err == services.ErrEmailExists {
			ctx.JSON(http.StatusConflict, gin.H{
				"error": "邮箱已存在",
			})
			return
		} else if err == services.ErrUsernameExists {
			ctx.JSON(http.StatusConflict, gin.H{
				"error": "用户名已存在",
			})
			return
		}
		
		ctx.JSON(http.StatusInternalServerError, gin.H{
			"error": "无法创建用户",
		})
		return
	}

	// 生成令牌
	tokenResponse, err := c.jwtService.GenerateTokens(user)
	if err != nil {
		c.logger.Error("生成令牌失败", "error", err)
		ctx.JSON(http.StatusInternalServerError, gin.H{
			"error": "无法生成认证令牌",
		})
		return
	}

	ctx.JSON(http.StatusCreated, gin.H{
		"message": "用户注册成功",
		"user": gin.H{
			"id":       user.ID,
			"username": user.Username,
			"email":    user.Email,
			"role":     user.Role,
		},
		"token": tokenResponse,
	})
}

// Login 处理用户登录请求
func (c *AuthController) Login(ctx *gin.Context) {
	var login models.UserLogin

	if err := ctx.ShouldBindJSON(&login); err != nil {
		c.logger.Error("无效的登录请求", "error", err)
		ctx.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的登录请求",
			"details": err.Error(),
		})
		return
	}

	// 登录用户
	user, err := c.authService.Login(ctx, &login)
	if err != nil {
		c.logger.Warn("登录失败", "username", login.Username, "error", err)
		
		if err == services.ErrInvalidCredentials {
			ctx.JSON(http.StatusUnauthorized, gin.H{
				"error": "用户名或密码不正确",
			})
			return
		}
		
		ctx.JSON(http.StatusInternalServerError, gin.H{
			"error": "登录失败",
			"details": err.Error(),
		})
		return
	}

	// 生成令牌
	tokenResponse, err := c.jwtService.GenerateTokens(user)
	if err != nil {
		c.logger.Error("生成令牌失败", "error", err)
		ctx.JSON(http.StatusInternalServerError, gin.H{
			"error": "无法生成认证令牌",
		})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{
		"message": "登录成功",
		"user": gin.H{
			"id":       user.ID,
			"username": user.Username,
			"email":    user.Email,
			"role":     user.Role,
		},
		"token": tokenResponse,
	})
}

// RefreshToken 处理刷新令牌请求
func (c *AuthController) RefreshToken(ctx *gin.Context) {
	var request struct {
		RefreshToken string `json:"refresh_token" binding:"required"`
	}

	if err := ctx.ShouldBindJSON(&request); err != nil {
		c.logger.Error("无效的刷新令牌请求", "error", err)
		ctx.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的刷新令牌请求",
			"details": err.Error(),
		})
		return
	}

	// 验证刷新令牌
	claims, err := c.jwtService.ValidateRefreshToken(request.RefreshToken)
	if err != nil {
		c.logger.Error("无效的刷新令牌", "error", err)
		ctx.JSON(http.StatusUnauthorized, gin.H{
			"error": "无效的刷新令牌",
		})
		return
	}

	// 获取用户
	user, err := c.authService.GetUserByID(ctx, claims.UserID)
	if err != nil {
		c.logger.Error("获取用户失败", "error", err, "user_id", claims.UserID)
		ctx.JSON(http.StatusInternalServerError, gin.H{
			"error": "无法刷新令牌",
		})
		return
	}

	// 生成新令牌
	tokenResponse, err := c.jwtService.GenerateTokens(user)
	if err != nil {
		c.logger.Error("生成新令牌失败", "error", err)
		ctx.JSON(http.StatusInternalServerError, gin.H{
			"error": "无法生成新令牌",
		})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{
		"message": "令牌刷新成功",
		"token": tokenResponse,
	})
}

// ValidateToken 验证令牌有效性
func (c *AuthController) ValidateToken(ctx *gin.Context) {
	authHeader := ctx.GetHeader("Authorization")
	if authHeader == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{
			"error": "未提供认证令牌",
		})
		return
	}

	// 从Authorization头部提取令牌
	// 格式通常是 "Bearer <token>"
	if len(authHeader) < 7 || authHeader[:7] != "Bearer " {
		ctx.JSON(http.StatusBadRequest, gin.H{
			"error": "认证令牌格式不正确",
		})
		return
	}
	tokenString := authHeader[7:]

	// 验证令牌
	claims, err := c.jwtService.ValidateAccessToken(tokenString)
	if err != nil {
		c.logger.Error("令牌验证失败", "error", err)
		ctx.JSON(http.StatusUnauthorized, gin.H{
			"error": "无效的令牌",
			"details": err.Error(),
		})
		return
	}

	// 获取用户
	user, err := c.authService.GetUserByID(ctx, claims.UserID)
	if err != nil {
		c.logger.Error("获取用户失败", "error", err, "user_id", claims.UserID)
		ctx.JSON(http.StatusInternalServerError, gin.H{
			"error": "无法验证令牌",
		})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{
		"valid": true,
		"user": gin.H{
			"id":       user.ID,
			"username": user.Username,
			"email":    user.Email,
			"role":     user.Role,
		},
	})
}

// ValidateTokenForGateway 处理API网关的令牌验证请求
func (c *AuthController) ValidateTokenForGateway(ctx *gin.Context) {
	var request struct {
		Token string `json:"token" binding:"required"`
	}

	if err := ctx.ShouldBindJSON(&request); err != nil {
		c.logger.Error("无效的网关验证请求", "error", err)
		ctx.JSON(http.StatusBadRequest, gin.H{
			"valid": false,
			"error": "无效的验证请求",
		})
		return
	}

	// 验证令牌
	claims, err := c.jwtService.ValidateAccessToken(request.Token)
	if err != nil {
		c.logger.Warn("网关令牌验证失败", "error", err)
		ctx.JSON(http.StatusOK, gin.H{
			"valid": false,
			"error": err.Error(),
		})
		return
	}

	// 成功验证
	ctx.JSON(http.StatusOK, gin.H{
		"valid": true,
		"user_id": claims.UserID,
		"username": claims.Username,
		"email": claims.Email,
		"role": claims.Role,
	})
} 