/**
 * 日常活动路由
 * 处理用户日常活动相关的API路由
 */
const DailyActivitiesController = require('../controllers/dailyActivities.controller');
const { AppError, ValidationError, NotFoundError, DatabaseError } = require('../utils/errors');
const { logger } = require('../utils/logger');

/**
 * 注册路由
 * @param {Object} fastify - Fastify实例
 * @param {Object} options - 路由选项
 */
async function routes(fastify, options) {
  // 实例化控制器
  const dailyActivitiesController = new DailyActivitiesController();

  // 错误处理中间件
  const errorHandler = (error, request, reply) => {
    // 记录错误
    logger.error(`API错误: ${error.message}`, { 
      error: error.stack,
      route: request.routeConfig?.url || request.url,
      method: request.method
    });

    // 如果是自定义错误类型，使用其状态码和详情
    if (error instanceof AppError) {
      return reply
        .code(error.statusCode)
        .send(error.toJSON());
    }
    
    // 处理验证错误
    if (error.validation) {
      const validationError = new ValidationError('请求验证失败', {
        validation: error.validation,
        params: error.validationContext
      });
      return reply
        .code(validationError.statusCode)
        .send(validationError.toJSON());
    }

    // 默认服务器错误
    return reply
      .code(500)
      .send({
        error: {
          name: 'ServerError',
          message: '服务器内部错误',
          statusCode: 500,
          errorCode: 'SERVER_ERROR'
        }
      });
  };

  // 获取用户活动摘要
  fastify.get('/api/users/:userId/activities/summary', {
    schema: {
      params: {
        type: 'object',
        required: ['userId'],
        properties: {
          userId: { type: 'string' }
        }
      },
      querystring: {
        type: 'object',
        properties: {
          period: { 
            type: 'string',
            enum: ['day', 'week', 'month'],
            default: 'day'
          }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            userId: { type: 'string' },
            period: { type: 'string' },
            date: { type: 'string', format: 'date-time' },
            totalActivities: { type: 'integer' },
            totalDuration: { type: 'integer' },
            totalDistance: { type: 'number' },
            totalCalories: { type: 'integer' },
            activityBreakdown: { 
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  type: { type: 'string' },
                  typeLabel: { type: 'string' },
                  count: { type: 'integer' },
                  duration: { type: 'integer' }
                }
              }
            },
            lastUpdated: { type: 'string', format: 'date-time' }
          }
        }
      }
    },
    handler: async (request, reply) => {
      try {
        const { userId } = request.params;
        const { period } = request.query;
        
        const summary = await dailyActivitiesController.getActivitySummary(userId, period);
        return reply.send(summary);
      } catch (error) {
        return errorHandler(error, request, reply);
      }
    }
  });

  // 获取活动详情
  fastify.get('/api/users/:userId/activities/:activityId', {
    schema: {
      params: {
        type: 'object',
        required: ['userId', 'activityId'],
        properties: {
          userId: { type: 'string' },
          activityId: { type: 'string' }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            id: { type: 'string' },
            userId: { type: 'string' },
            type: { type: 'string' },
            typeLabel: { type: 'string' },
            description: { type: 'string' },
            duration: { type: 'integer' },
            distance: { type: 'number' },
            calories: { type: 'integer' },
            startTime: { type: 'string', format: 'date-time' },
            endTime: { type: 'string', format: 'date-time' },
            locationName: { type: 'string' },
            locationCoordinates: { 
              type: 'object',
              properties: {
                latitude: { type: 'number' },
                longitude: { type: 'number' }
              }
            },
            heartRate: { 
              type: 'object',
              properties: {
                average: { type: 'integer' },
                max: { type: 'integer' },
                min: { type: 'integer' }
              }
            },
            pace: { 
              type: 'object',
              properties: {
                average: { type: 'string' },
                best: { type: 'string' }
              }
            },
            mood: { type: 'string' },
            notes: { type: 'string' },
            tags: { 
              type: 'array',
              items: { type: 'string' }
            },
            createdAt: { type: 'string', format: 'date-time' },
            updatedAt: { type: 'string', format: 'date-time' }
          }
        },
        404: {
          type: 'object',
          properties: {
            error: {
              type: 'object',
              properties: {
                name: { type: 'string' },
                message: { type: 'string' },
                statusCode: { type: 'integer' },
                errorCode: { type: 'string' },
                details: { type: 'object' }
              }
            }
          }
        }
      }
    },
    handler: async (request, reply) => {
      try {
        const { userId, activityId } = request.params;
        
        const activity = await dailyActivitiesController.getActivityDetail(userId, activityId);
        return reply.send(activity);
      } catch (error) {
        return errorHandler(error, request, reply);
      }
    }
  });

  // 记录新活动
  fastify.post('/api/users/:userId/activities', {
    schema: {
      params: {
        type: 'object',
        required: ['userId'],
        properties: {
          userId: { type: 'string' }
        }
      },
      body: {
        type: 'object',
        required: ['type', 'description', 'duration'],
        properties: {
          type: { 
            type: 'string',
            enum: ['walking', 'running', 'cycling', 'swimming', 'yoga', 'meditation', 'exercise', 'other']
          },
          typeLabel: { type: 'string' },
          description: { type: 'string' },
          duration: { type: 'integer', minimum: 1 },
          distance: { type: 'number' },
          calories: { type: 'integer' },
          startTime: { type: 'string', format: 'date-time' },
          endTime: { type: 'string', format: 'date-time' },
          locationName: { type: 'string' },
          locationCoordinates: { 
            type: 'object',
            properties: {
              latitude: { type: 'number' },
              longitude: { type: 'number' }
            }
          },
          heartRate: { 
            type: 'object',
            properties: {
              average: { type: 'integer' },
              max: { type: 'integer' },
              min: { type: 'integer' }
            }
          },
          pace: { 
            type: 'object',
            properties: {
              average: { type: 'string' },
              best: { type: 'string' }
            }
          },
          mood: { type: 'string' },
          notes: { type: 'string' },
          tags: { 
            type: 'array',
            items: { type: 'string' }
          }
        }
      },
      response: {
        201: {
          type: 'object',
          properties: {
            id: { type: 'string' },
            userId: { type: 'string' },
            type: { type: 'string' },
            description: { type: 'string' },
            duration: { type: 'integer' },
            createdAt: { type: 'string', format: 'date-time' }
          }
        },
        400: {
          type: 'object',
          properties: {
            error: {
              type: 'object',
              properties: {
                name: { type: 'string' },
                message: { type: 'string' },
                statusCode: { type: 'integer' },
                errorCode: { type: 'string' },
                details: { type: 'object' }
              }
            }
          }
        }
      }
    },
    handler: async (request, reply) => {
      try {
        const { userId } = request.params;
        const activityData = request.body;
        
        const activity = await dailyActivitiesController.recordActivity(userId, activityData);
        return reply.code(201).send(activity);
      } catch (error) {
        return errorHandler(error, request, reply);
      }
    }
  });

  // 获取活动建议
  fastify.get('/api/users/:userId/activities/recommendations', {
    schema: {
      params: {
        type: 'object',
        required: ['userId'],
        properties: {
          userId: { type: 'string' }
        }
      },
      response: {
        200: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              id: { type: 'string' },
              type: { type: 'string' },
              title: { type: 'string' },
              description: { type: 'string' },
              durationMinutes: { type: 'integer' },
              caloriesBurned: { type: 'integer' },
              benefits: { 
                type: 'array',
                items: { type: 'string' }
              },
              bestTimeOfDay: { type: 'string' },
              tcmPrinciples: {
                type: 'array',
                items: { type: 'string' }
              }
            }
          }
        }
      }
    },
    handler: async (request, reply) => {
      try {
        const { userId } = request.params;
        
        const recommendations = await dailyActivitiesController.getActivityRecommendations(userId);
        return reply.send(recommendations);
      } catch (error) {
        return errorHandler(error, request, reply);
      }
    }
  });
}

module.exports = routes; 