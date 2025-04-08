package controllers

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/suoke-life/shared/pkg/logger"
	"github.com/suoke-life/user-service/internal/models"
	"github.com/suoke-life/user-service/internal/services"
)

// UserController 用户控制器
type UserController struct {
	userService services.UserService
	logger      logger.Logger
}

// NewUserController 创建用户控制器
func NewUserController(userService services.UserService, log logger.Logger) *UserController {
	return &UserController{
		userService: userService,
		logger:      log.With("component", "user_controller"),
	}
}

// CreateUser 创建用户处理函数
func (c *UserController) CreateUser(ctx *gin.Context) {
	var request struct {
		Username string `json:"username" binding:"required,min=3,max=50"`
		Email    string `json:"email" binding:"required,email,max=100"`
	}

	if err := ctx.ShouldBindJSON(&request); err != nil {
		c.logger.Error("无效的创建用户请求", "error", err)
		ctx.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的请求",
			"details": err.Error(),
		})
		return
	}

	user, err := c.userService.CreateUser(ctx, request.Username, request.Email)
	if err != nil {
		c.logger.Error("创建用户失败", "error", err)
		
		// 检查常见错误
		switch {
		case err.Error() == "用户名已存在: "+request.Username:
			ctx.JSON(http.StatusConflict, gin.H{
				"error": "用户名已存在",
			})
		case err.Error() == "邮箱已存在: "+request.Email:
			ctx.JSON(http.StatusConflict, gin.H{
				"error": "邮箱已存在",
			})
		default:
			ctx.JSON(http.StatusInternalServerError, gin.H{
				"error": "创建用户失败",
				"details": err.Error(),
			})
		}
		return
	}

	ctx.JSON(http.StatusCreated, gin.H{
		"message": "用户创建成功",
		"user": user.ToProfile(),
	})
}

// GetUser 获取用户处理函数
func (c *UserController) GetUser(ctx *gin.Context) {
	id := ctx.Param("id")
	if id == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{
			"error": "用户ID不能为空",
		})
		return
	}

	user, err := c.userService.GetUserByID(ctx, id)
	if err != nil {
		c.logger.Error("获取用户失败", "error", err, "id", id)
		
		if err.Error() == "用户不存在: "+id {
			ctx.JSON(http.StatusNotFound, gin.H{
				"error": "用户不存在",
			})
			return
		}
		
		ctx.JSON(http.StatusInternalServerError, gin.H{
			"error": "获取用户失败",
			"details": err.Error(),
		})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{
		"user": user.ToProfile(),
	})
}

// GetUserByUsername 通过用户名获取用户
func (c *UserController) GetUserByUsername(ctx *gin.Context) {
	username := ctx.Param("username")
	if username == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{
			"error": "用户名不能为空",
		})
		return
	}

	user, err := c.userService.GetUserByUsername(ctx, username)
	if err != nil {
		c.logger.Error("通过用户名获取用户失败", "error", err, "username", username)
		
		if err.Error() == "用户不存在: "+username {
			ctx.JSON(http.StatusNotFound, gin.H{
				"error": "用户不存在",
			})
			return
		}
		
		ctx.JSON(http.StatusInternalServerError, gin.H{
			"error": "获取用户失败",
			"details": err.Error(),
		})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{
		"user": user.ToProfile(),
	})
}

// UpdateUser 更新用户处理函数
func (c *UserController) UpdateUser(ctx *gin.Context) {
	id := ctx.Param("id")
	if id == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{
			"error": "用户ID不能为空",
		})
		return
	}

	var update models.UserUpdate
	if err := ctx.ShouldBindJSON(&update); err != nil {
		c.logger.Error("无效的更新用户请求", "error", err)
		ctx.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的请求",
			"details": err.Error(),
		})
		return
	}

	user, err := c.userService.UpdateUser(ctx, id, &update)
	if err != nil {
		c.logger.Error("更新用户失败", "error", err, "id", id)
		
		if err.Error() == "用户不存在: "+id {
			ctx.JSON(http.StatusNotFound, gin.H{
				"error": "用户不存在",
			})
			return
		}
		
		ctx.JSON(http.StatusInternalServerError, gin.H{
			"error": "更新用户失败",
			"details": err.Error(),
		})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{
		"message": "用户更新成功",
		"user": user.ToProfile(),
	})
}

// DeleteUser 删除用户处理函数
func (c *UserController) DeleteUser(ctx *gin.Context) {
	id := ctx.Param("id")
	if id == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{
			"error": "用户ID不能为空",
		})
		return
	}

	if err := c.userService.DeleteUser(ctx, id); err != nil {
		c.logger.Error("删除用户失败", "error", err, "id", id)
		
		if err.Error() == "用户不存在: "+id {
			ctx.JSON(http.StatusNotFound, gin.H{
				"error": "用户不存在",
			})
			return
		}
		
		ctx.JSON(http.StatusInternalServerError, gin.H{
			"error": "删除用户失败",
			"details": err.Error(),
		})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{
		"message": "用户删除成功",
	})
}

// ListUsers 列出用户处理函数
func (c *UserController) ListUsers(ctx *gin.Context) {
	// 解析查询参数
	filter := &models.UserFilter{}
	
	if username := ctx.Query("username"); username != "" {
		filter.Username = username
	}
	
	if email := ctx.Query("email"); email != "" {
		filter.Email = email
	}
	
	if displayName := ctx.Query("display_name"); displayName != "" {
		filter.DisplayName = displayName
	}
	
	if sortBy := ctx.Query("sort_by"); sortBy != "" {
		filter.SortBy = sortBy
	}
	
	if sortOrder := ctx.Query("sort_order"); sortOrder != "" {
		filter.SortOrder = sortOrder
	}
	
	if limitStr := ctx.Query("limit"); limitStr != "" {
		limit, err := strconv.Atoi(limitStr)
		if err == nil && limit > 0 {
			filter.Limit = limit
		}
	}
	
	if offsetStr := ctx.Query("offset"); offsetStr != "" {
		offset, err := strconv.Atoi(offsetStr)
		if err == nil && offset >= 0 {
			filter.Offset = offset
		}
	}
	
	// 获取用户列表
	users, err := c.userService.ListUsers(ctx, filter)
	if err != nil {
		c.logger.Error("列出用户失败", "error", err)
		ctx.JSON(http.StatusInternalServerError, gin.H{
			"error": "列出用户失败",
			"details": err.Error(),
		})
		return
	}
	
	// 转换为资料列表
	profiles := make([]*models.UserProfile, len(users))
	for i, user := range users {
		profiles[i] = user.ToProfile()
	}
	
	// 获取总数
	total, err := c.userService.CountUsers(ctx)
	if err != nil {
		c.logger.Error("获取用户总数失败", "error", err)
		ctx.JSON(http.StatusInternalServerError, gin.H{
			"error": "获取用户总数失败",
			"details": err.Error(),
		})
		return
	}
	
	ctx.JSON(http.StatusOK, gin.H{
		"users": profiles,
		"total": total,
		"limit": filter.Limit,
		"offset": filter.Offset,
	})
}

// UpdateUserPreferences 更新用户偏好设置
func (c *UserController) UpdateUserPreferences(ctx *gin.Context) {
	id := ctx.Param("id")
	if id == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{
			"error": "用户ID不能为空",
		})
		return
	}
	
	var prefs models.UserPrefs
	if err := ctx.ShouldBindJSON(&prefs); err != nil {
		c.logger.Error("无效的偏好设置更新请求", "error", err)
		ctx.JSON(http.StatusBadRequest, gin.H{
			"error": "无效的请求",
			"details": err.Error(),
		})
		return
	}
	
	if err := c.userService.UpdatePreferences(ctx, id, prefs); err != nil {
		c.logger.Error("更新用户偏好设置失败", "error", err, "id", id)
		
		if err.Error() == "用户不存在: "+id {
			ctx.JSON(http.StatusNotFound, gin.H{
				"error": "用户不存在",
			})
			return
		}
		
		ctx.JSON(http.StatusInternalServerError, gin.H{
			"error": "更新用户偏好设置失败",
			"details": err.Error(),
		})
		return
	}
	
	ctx.JSON(http.StatusOK, gin.H{
		"message": "用户偏好设置更新成功",
	})
}

// UpdateLastSeen 更新用户最后在线时间
func (c *UserController) UpdateLastSeen(ctx *gin.Context) {
	id := ctx.Param("id")
	if id == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{
			"error": "用户ID不能为空",
		})
		return
	}
	
	if err := c.userService.UpdateLastSeen(ctx, id); err != nil {
		c.logger.Error("更新用户最后在线时间失败", "error", err, "id", id)
		
		if err.Error() == "用户不存在: "+id {
			ctx.JSON(http.StatusNotFound, gin.H{
				"error": "用户不存在",
			})
			return
		}
		
		ctx.JSON(http.StatusInternalServerError, gin.H{
			"error": "更新用户最后在线时间失败",
			"details": err.Error(),
		})
		return
	}
	
	ctx.JSON(http.StatusOK, gin.H{
		"message": "用户最后在线时间更新成功",
	})
} 