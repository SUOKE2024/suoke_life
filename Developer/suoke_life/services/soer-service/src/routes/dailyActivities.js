'use strict';

/**
 * 日常活动路由
 * 处理用户日常生活、饮食起居、打卡等功能
 */
module.exports = async function (fastify, opts) {
  // 获取用户日常活动记录
  fastify.get('/user/:userId', {
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
          timeframe: { type: 'string', enum: ['day', 'week', 'month', 'year'] },
          date: { type: 'string', format: 'date' }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            userId: { type: 'string' },
            activities: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  id: { type: 'string' },
                  type: { type: 'string', enum: ['meal', 'sleep', 'exercise', 'medication', 'water', 'mood', 'custom'] },
                  title: { type: 'string' },
                  description: { type: 'string' },
                  timestamp: { type: 'string', format: 'date-time' },
                  value: { type: 'number' },
                  unit: { type: 'string' },
                  metadata: { type: 'object' },
                  images: {
                    type: 'array',
                    items: { type: 'string' }
                  },
                  location: {
                    type: 'object',
                    properties: {
                      latitude: { type: 'number' },
                      longitude: { type: 'number' },
                      name: { type: 'string' }
                    }
                  },
                  tags: {
                    type: 'array',
                    items: { type: 'string' }
                  },
                  completed: { type: 'boolean' }
                }
              }
            },
            insights: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  type: { type: 'string' },
                  title: { type: 'string' },
                  description: { type: 'string' },
                  actionable: { type: 'boolean' },
                  action: { type: 'string' }
                }
              }
            },
            habits: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  id: { type: 'string' },
                  name: { type: 'string' },
                  description: { type: 'string' },
                  streak: { type: 'number' },
                  completion: { type: 'number' },
                  status: { type: 'string', enum: ['active', 'paused', 'completed'] }
                }
              }
            },
            stats: {
              type: 'object',
              properties: {
                completionRate: { type: 'number' },
                consistency: { type: 'number' },
                totalActivities: { type: 'number' }
              }
            },
            generatedAt: { type: 'string', format: 'date-time' }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { userId } = request.params;
    const { timeframe = 'day', date = new Date().toISOString().split('T')[0] } = request.query;
    
    try {
      // 实际实现应该从数据库或其他服务获取用户活动
      const activities = getMockDailyActivities(userId, timeframe, date);
      
      // 分析活动并生成洞察
      const insights = generateActivityInsights(activities, userId);
      
      // 获取用户习惯数据
      const habits = getMockHabits(userId);
      
      // 计算统计数据
      const stats = calculateActivityStats(activities, habits);
      
      return {
        userId,
        activities,
        insights,
        habits,
        stats,
        generatedAt: new Date().toISOString()
      };
    } catch (error) {
      fastify.log.error(`获取用户日常活动失败: ${error.message}`);
      
      return reply.code(500).send({
        error: 'daily_activities_fetch_failed',
        message: '获取用户日常活动失败',
        details: process.env.NODE_ENV === 'production' ? undefined : error.message
      });
    }
  });
  
  // 记录新的日常活动
  fastify.post('/user/:userId', {
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
        required: ['type', 'title'],
        properties: {
          type: { type: 'string', enum: ['meal', 'sleep', 'exercise', 'medication', 'water', 'mood', 'custom'] },
          title: { type: 'string' },
          description: { type: 'string' },
          timestamp: { type: 'string', format: 'date-time' },
          value: { type: 'number' },
          unit: { type: 'string' },
          metadata: { type: 'object' },
          images: {
            type: 'array',
            items: { type: 'string' }
          },
          location: {
            type: 'object',
            properties: {
              latitude: { type: 'number' },
              longitude: { type: 'number' },
              name: { type: 'string' }
            }
          },
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
            title: { type: 'string' },
            timestamp: { type: 'string', format: 'date-time' },
            message: { type: 'string' }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { userId } = request.params;
    const activityData = request.body;
    
    try {
      // 添加时间戳（如果未提供）
      if (!activityData.timestamp) {
        activityData.timestamp = new Date().toISOString();
      }
      
      // 实际实现应该将活动保存到数据库
      const activityId = `act_${Date.now()}_${Math.floor(Math.random() * 1000)}`;
      
      // 记录活动并更新相关习惯
      // ...
      
      // 如果是用户对应的习惯活动，更新习惯状态
      // ...
      
      return reply.code(201).send({
        id: activityId,
        userId,
        type: activityData.type,
        title: activityData.title,
        timestamp: activityData.timestamp,
        message: '活动记录成功'
      });
    } catch (error) {
      fastify.log.error(`记录用户日常活动失败: ${error.message}`);
      
      return reply.code(500).send({
        error: 'daily_activity_record_failed',
        message: '记录用户日常活动失败',
        details: process.env.NODE_ENV === 'production' ? undefined : error.message
      });
    }
  });
  
  // 完成活动打卡
  fastify.post('/user/:userId/checkin/:activityId', {
    schema: {
      params: {
        type: 'object',
        required: ['userId', 'activityId'],
        properties: {
          userId: { type: 'string' },
          activityId: { type: 'string' }
        }
      },
      body: {
        type: 'object',
        properties: {
          note: { type: 'string' },
          rating: { type: 'number', minimum: 1, maximum: 5 },
          photos: { 
            type: 'array',
            items: { type: 'string' }
          },
          mood: { type: 'string' }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            success: { type: 'boolean' },
            message: { type: 'string' },
            timestamp: { type: 'string', format: 'date-time' },
            streak: { type: 'number' }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { userId, activityId } = request.params;
    const checkinData = request.body;
    
    try {
      // 实际实现应该在数据库中更新活动状态
      // ...
      
      // 如果是习惯活动，更新习惯连续打卡次数
      const streak = 5; // 示例值
      
      return {
        success: true,
        message: '打卡成功',
        timestamp: new Date().toISOString(),
        streak
      };
    } catch (error) {
      fastify.log.error(`用户打卡失败: ${error.message}`);
      
      return reply.code(500).send({
        error: 'checkin_failed',
        message: '打卡失败',
        details: process.env.NODE_ENV === 'production' ? undefined : error.message
      });
    }
  });
  
  // 获取用户习惯和目标
  fastify.get('/user/:userId/habits', {
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
          type: 'object',
          properties: {
            userId: { type: 'string' },
            habits: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  id: { type: 'string' },
                  name: { type: 'string' },
                  description: { type: 'string' },
                  category: { type: 'string' },
                  frequency: { type: 'string' },
                  progress: { type: 'number' },
                  streak: { type: 'number' },
                  startDate: { type: 'string', format: 'date' },
                  lastCheckin: { type: 'string', format: 'date-time' },
                  status: { type: 'string' }
                }
              }
            }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { userId } = request.params;
    
    try {
      const habits = getMockHabits(userId);
      
      return {
        userId,
        habits
      };
    } catch (error) {
      fastify.log.error(`获取用户习惯失败: ${error.message}`);
      
      return reply.code(500).send({
        error: 'habits_fetch_failed',
        message: '获取用户习惯失败',
        details: process.env.NODE_ENV === 'production' ? undefined : error.message
      });
    }
  });
  
  // 创建新习惯
  fastify.post('/user/:userId/habits', {
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
        required: ['name', 'frequency'],
        properties: {
          name: { type: 'string' },
          description: { type: 'string' },
          category: { type: 'string' },
          frequency: { type: 'string' },
          reminderTime: { type: 'string' }
        }
      },
      response: {
        201: {
          type: 'object',
          properties: {
            id: { type: 'string' },
            name: { type: 'string' },
            message: { type: 'string' }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { userId } = request.params;
    const habitData = request.body;
    
    try {
      // 实际实现应该将习惯保存到数据库
      const habitId = `habit_${Date.now()}_${Math.floor(Math.random() * 1000)}`;
      
      return reply.code(201).send({
        id: habitId,
        name: habitData.name,
        message: '习惯创建成功'
      });
    } catch (error) {
      fastify.log.error(`创建用户习惯失败: ${error.message}`);
      
      return reply.code(500).send({
        error: 'habit_creation_failed',
        message: '创建用户习惯失败',
        details: process.env.NODE_ENV === 'production' ? undefined : error.message
      });
    }
  });
  
  // 获取用户博客内容
  fastify.get('/user/:userId/blog', {
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
          page: { type: 'number', default: 1 },
          limit: { type: 'number', default: 10 },
          tag: { type: 'string' }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            userId: { type: 'string' },
            posts: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  id: { type: 'string' },
                  title: { type: 'string' },
                  content: { type: 'string' },
                  summary: { type: 'string' },
                  publishedAt: { type: 'string', format: 'date-time' },
                  tags: {
                    type: 'array',
                    items: { type: 'string' }
                  },
                  images: {
                    type: 'array',
                    items: { type: 'string' }
                  },
                  likes: { type: 'number' },
                  comments: { type: 'number' }
                }
              }
            },
            pagination: {
              type: 'object',
              properties: {
                page: { type: 'number' },
                limit: { type: 'number' },
                total: { type: 'number' },
                pages: { type: 'number' }
              }
            }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { userId } = request.params;
    const { page = 1, limit = 10, tag } = request.query;
    
    try {
      // 实际实现应该从数据库获取博客文章
      const blogPosts = getMockBlogPosts(userId, page, limit, tag);
      
      // 模拟分页
      const total = 25; // 示例总数
      const pages = Math.ceil(total / limit);
      
      return {
        userId,
        posts: blogPosts,
        pagination: {
          page,
          limit,
          total,
          pages
        }
      };
    } catch (error) {
      fastify.log.error(`获取用户博客失败: ${error.message}`);
      
      return reply.code(500).send({
        error: 'blog_posts_fetch_failed',
        message: '获取用户博客失败',
        details: process.env.NODE_ENV === 'production' ? undefined : error.message
      });
    }
  });
  
  // 创建新的博客文章
  fastify.post('/user/:userId/blog', {
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
        required: ['title', 'content'],
        properties: {
          title: { type: 'string' },
          content: { type: 'string' },
          summary: { type: 'string' },
          tags: {
            type: 'array',
            items: { type: 'string' }
          },
          images: {
            type: 'array',
            items: { type: 'string' }
          },
          isDraft: { type: 'boolean' }
        }
      },
      response: {
        201: {
          type: 'object',
          properties: {
            id: { type: 'string' },
            title: { type: 'string' },
            publishedAt: { type: 'string', format: 'date-time' },
            message: { type: 'string' }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { userId } = request.params;
    const postData = request.body;
    
    try {
      // 实际实现应该将博客保存到数据库
      const postId = `post_${Date.now()}_${Math.floor(Math.random() * 1000)}`;
      const publishedAt = new Date().toISOString();
      
      return reply.code(201).send({
        id: postId,
        title: postData.title,
        publishedAt,
        message: postData.isDraft ? '草稿保存成功' : '博客发布成功'
      });
    } catch (error) {
      fastify.log.error(`创建用户博客失败: ${error.message}`);
      
      return reply.code(500).send({
        error: 'blog_post_creation_failed',
        message: '创建用户博客失败',
        details: process.env.NODE_ENV === 'production' ? undefined : error.message
      });
    }
  });
  
  // 获取用户健康陪伴服务状态
  fastify.get('/user/:userId/companion', {
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
          type: 'object',
          properties: {
            userId: { type: 'string' },
            activeCompanion: {
              type: 'object',
              properties: {
                id: { type: 'string' },
                name: { type: 'string' },
                type: { type: 'string' },
                level: { type: 'number' },
                mood: { type: 'string' },
                lastInteraction: { type: 'string', format: 'date-time' }
              }
            },
            interactions: {
              type: 'object',
              properties: {
                today: { type: 'number' },
                week: { type: 'number' },
                month: { type: 'number' }
              }
            },
            recommendations: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  type: { type: 'string' },
                  title: { type: 'string' },
                  description: { type: 'string' }
                }
              }
            }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { userId } = request.params;
    
    try {
      // 实际实现应该从数据库获取用户陪伴服务数据
      const companionData = getMockCompanionData(userId);
      
      return companionData;
    } catch (error) {
      fastify.log.error(`获取用户陪伴服务数据失败: ${error.message}`);
      
      return reply.code(500).send({
        error: 'companion_data_fetch_failed',
        message: '获取用户陪伴服务数据失败',
        details: process.env.NODE_ENV === 'production' ? undefined : error.message
      });
    }
  });
  
  // 与陪伴服务互动
  fastify.post('/user/:userId/companion/interact', {
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
        required: ['action'],
        properties: {
          action: { type: 'string', enum: ['chat', 'check', 'guide', 'remind', 'motivate'] },
          message: { type: 'string' },
          context: { type: 'object' }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            response: { type: 'string' },
            mood: { type: 'string' },
            actionTaken: { type: 'boolean' },
            actionDescription: { type: 'string' },
            nextSuggestion: { type: 'string' }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { userId } = request.params;
    const { action, message, context } = request.body;
    
    try {
      // 实际实现应该处理与陪伴服务的互动
      // 这里使用模拟数据
      let response;
      let mood;
      let actionTaken = false;
      let actionDescription = '';
      let nextSuggestion = '';
      
      switch (action) {
        case 'chat':
          response = "我一直在关注你的健康状况。今天你的步数有些低，想一起出去散步吗？";
          mood = "关心";
          nextSuggestion = "设置一个30分钟的散步提醒";
          break;
        case 'check':
          response = "您今天的血压读数看起来很稳定，继续保持良好的作息习惯。";
          mood = "满意";
          actionTaken = true;
          actionDescription = "已更新健康记录";
          nextSuggestion = "记录今天的饮食情况";
          break;
        case 'guide':
          response = "根据您的习惯记录，建议增加一些轻度的伸展运动来缓解久坐带来的不适。";
          mood = "建议";
          nextSuggestion = "查看5分钟办公室伸展运动指南";
          break;
        case 'remind':
          response = "提醒您该喝水了。保持水分摄入对维持体内平衡很重要。";
          mood = "提醒";
          actionTaken = true;
          actionDescription = "已设置2小时后的下次提醒";
          break;
        case 'motivate':
          response = "您已经连续记录饮食习惯7天了，太棒了！这对您的健康目标非常有帮助。";
          mood = "鼓励";
          nextSuggestion = "设定下一个健康目标";
          break;
        default:
          response = "我在这里随时为您提供帮助和支持。";
          mood = "友好";
      }
      
      return {
        response,
        mood,
        actionTaken,
        actionDescription,
        nextSuggestion
      };
    } catch (error) {
      fastify.log.error(`陪伴服务互动失败: ${error.message}`);
      
      return reply.code(500).send({
        error: 'companion_interaction_failed',
        message: '陪伴服务互动失败',
        details: process.env.NODE_ENV === 'production' ? undefined : error.message
      });
    }
  });
  
  // 辅助函数
  function getMockDailyActivities(userId, timeframe, date) {
    // 返回模拟的日常活动数据
    const activities = [
      {
        id: 'act_breakfast',
        type: 'meal',
        title: '早餐',
        description: '全麦面包、鸡蛋和牛奶',
        timestamp: `${date}T07:30:00Z`,
        value: 450,
        unit: '卡路里',
        metadata: {
          nutrition: {
            protein: 15,
            carbs: 45,
            fat: 12
          }
        },
        images: ['url_to_breakfast_image'],
        tags: ['健康', '早餐'],
        completed: true
      },
      {
        id: 'act_lunch',
        type: 'meal',
        title: '午餐',
        description: '米饭、蔬菜和鱼',
        timestamp: `${date}T12:00:00Z`,
        value: 650,
        unit: '卡路里',
        metadata: {
          nutrition: {
            protein: 25,
            carbs: 75,
            fat: 15
          }
        },
        tags: ['午餐', '蛋白质'],
        completed: true
      },
      {
        id: 'act_exercise',
        type: 'exercise',
        title: '步行',
        description: '公园慢跑',
        timestamp: `${date}T18:00:00Z`,
        value: 30,
        unit: '分钟',
        metadata: {
          distance: 2.5,
          caloriesBurned: 200
        },
        location: {
          latitude: 39.9042,
          longitude: 116.4074,
          name: '中央公园'
        },
        tags: ['有氧', '户外'],
        completed: true
      },
      {
        id: 'act_sleep',
        type: 'sleep',
        title: '睡眠',
        description: '夜间睡眠',
        timestamp: `${date}T23:00:00Z`,
        value: 7.5,
        unit: '小时',
        metadata: {
          quality: 'good',
          deepSleep: 2.5,
          remSleep: 1.8
        },
        tags: ['睡眠', '恢复'],
        completed: false
      },
      {
        id: 'act_water',
        type: 'water',
        title: '喝水',
        timestamp: `${date}T15:30:00Z`,
        value: 300,
        unit: '毫升',
        tags: ['水分', '健康'],
        completed: true
      }
    ];
    
    return activities;
  }
  
  function generateActivityInsights(activities, userId) {
    // 根据活动数据生成相关洞察
    return [
      {
        type: 'nutrition',
        title: '蛋白质摄入不足',
        description: '您今天的蛋白质摄入低于推荐水平。考虑在晚餐中添加优质蛋白质来源。',
        actionable: true,
        action: '查看高蛋白食物推荐'
      },
      {
        type: 'activity',
        title: '活动目标接近完成',
        description: '您今天已完成活动目标的75%。再走2000步就能达成目标！',
        actionable: true,
        action: '设置步行提醒'
      },
      {
        type: 'sleep',
        title: '睡眠规律性良好',
        description: '过去一周您的睡眠时间很规律，这有助于提高睡眠质量。',
        actionable: false
      }
    ];
  }
  
  function getMockHabits(userId) {
    // 返回模拟的习惯数据
    return [
      {
        id: 'habit_water',
        name: '每天喝8杯水',
        description: '保持充分水分摄入',
        category: '健康',
        frequency: 'daily',
        progress: 0.75,
        streak: 12,
        startDate: '2023-03-01',
        lastCheckin: '2023-03-27T15:30:00Z',
        status: 'active'
      },
      {
        id: 'habit_walk',
        name: '每天步行30分钟',
        description: '保持基础有氧活动',
        category: '运动',
        frequency: 'daily',
        progress: 1,
        streak: 7,
        startDate: '2023-03-10',
        lastCheckin: '2023-03-27T18:00:00Z',
        status: 'active'
      },
      {
        id: 'habit_meditation',
        name: '冥想10分钟',
        description: '培养专注力和放松',
        category: '心理健康',
        frequency: 'weekdays',
        progress: 0.4,
        streak: 3,
        startDate: '2023-03-15',
        lastCheckin: '2023-03-27T07:00:00Z',
        status: 'active'
      }
    ];
  }
  
  function calculateActivityStats(activities, habits) {
    // 计算活动统计数据
    return {
      completionRate: 0.85,
      consistency: 0.92,
      totalActivities: activities.length
    };
  }
  
  function getMockBlogPosts(userId, page, limit, tag) {
    // 返回模拟的博客文章
    const posts = [
      {
        id: 'post_001',
        title: '我的健康饮食之旅',
        content: '长文内容...',
        summary: '分享如何通过改变饮食习惯改善健康状况',
        publishedAt: '2023-03-25T10:30:00Z',
        tags: ['饮食', '健康', '生活方式'],
        images: ['url_to_image1', 'url_to_image2'],
        likes: 24,
        comments: 5
      },
      {
        id: 'post_002',
        title: '每天30分钟运动的变化',
        content: '长文内容...',
        summary: '记录坚持运动一个月的身体变化',
        publishedAt: '2023-03-20T14:15:00Z',
        tags: ['运动', '坚持', '变化'],
        images: ['url_to_image'],
        likes: 36,
        comments: 8
      },
      {
        id: 'post_003',
        title: '正念冥想体验',
        content: '长文内容...',
        summary: '分享正念冥想如何帮助减轻压力',
        publishedAt: '2023-03-15T09:45:00Z',
        tags: ['冥想', '心理健康', '压力管理'],
        images: [],
        likes: 18,
        comments: 3
      }
    ];
    
    // 如果有标签过滤，应用过滤
    const filteredPosts = tag 
      ? posts.filter(post => post.tags.includes(tag))
      : posts;
    
    return filteredPosts.slice(0, limit);
  }
  
  function getMockCompanionData(userId) {
    // 返回模拟的陪伴服务数据
    return {
      userId,
      activeCompanion: {
        id: 'comp_001',
        name: '小健',
        type: '健康顾问',
        level: 3,
        mood: '友好',
        lastInteraction: new Date().toISOString()
      },
      interactions: {
        today: 5,
        week: 23,
        month: 87
      },
      recommendations: [
        {
          type: 'activity',
          title: '午后伸展运动',
          description: '建议在下午2点进行5分钟的办公室伸展，缓解久坐疲劳'
        },
        {
          type: 'nutrition',
          title: '补充水分',
          description: '您已有2小时未记录饮水，建议补充300ml水分'
        },
        {
          type: 'mental',
          title: '呼吸放松',
          description: '工作一段时间后，试试2分钟的深呼吸放松练习'
        }
      ]
    };
  }
};