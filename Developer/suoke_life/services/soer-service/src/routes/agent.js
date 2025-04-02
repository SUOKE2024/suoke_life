'use strict';

/**
 * 智能体路由
 * 处理与智能体交互的API接口
 */
module.exports = async function (fastify, opts) {
  // 获取智能体配置
  fastify.get('/config', {
    schema: {
      response: {
        200: {
          type: 'object',
          properties: {
            name: { type: 'string' },
            id: { type: 'string' },
            version: { type: 'string' },
            description: { type: 'string' },
            avatar: { type: 'string' },
            greeting: { type: 'string' },
            capabilities: { type: 'array', items: { type: 'string' } }
          }
        }
      }
    }
  }, async (request, reply) => {
    // 返回智能体公开配置
    const { agent } = fastify.agentConfig;
    return {
      name: agent.name,
      id: agent.id,
      version: agent.version,
      description: agent.description,
      avatar: agent.avatar,
      greeting: agent.greeting,
      capabilities: agent.capabilities
    };
  });

  // 发送消息给智能体
  fastify.post('/message', {
    schema: {
      body: {
        type: 'object',
        required: ['userId', 'message'],
        properties: {
          userId: { type: 'string' },
          message: { type: 'string' },
          context: { 
            type: 'object',
            properties: {
              location: { type: 'string' },
              deviceType: { type: 'string' },
              referrer: { type: 'string' }
            }
          }
        }
      },
      response: {
        200: {
          type: 'object',
          properties: {
            content: { type: 'string' },
            type: { type: 'string' },
            timestamp: { type: 'string', format: 'date-time' }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { userId, message, context = {} } = request.body;
    
    // 验证用户ID
    if (!userId || userId.length < 3) {
      return reply.code(400).send({
        error: 'invalid_user_id',
        message: '无效的用户ID'
      });
    }
    
    // 验证消息内容
    if (!message || message.trim().length === 0) {
      return reply.code(400).send({
        error: 'empty_message',
        message: '消息内容不能为空'
      });
    }
    
    try {
      // 处理消息
      const response = await fastify.agentService.processMessage(userId, message, context);
      
      // 记录交互
      fastify.log.info({
        userId,
        messageLength: message.length,
        responseType: response.type,
        responseLength: response.content.length
      }, '消息处理完成');
      
      return {
        content: response.content,
        type: response.type,
        timestamp: response.timestamp.toISOString()
      };
    } catch (error) {
      fastify.log.error(`处理消息失败: ${error.message}`);
      
      return reply.code(500).send({
        error: 'message_processing_failed',
        message: '消息处理失败',
        details: process.env.NODE_ENV === 'production' ? undefined : error.message
      });
    }
  });

  // 获取智能体状态
  fastify.get('/status', {
    schema: {
      response: {
        200: {
          type: 'object',
          properties: {
            status: { type: 'string' },
            models: { type: 'object' },
            activeSessions: { type: 'integer' },
            timestamp: { type: 'string', format: 'date-time' }
          }
        }
      }
    }
  }, async (request, reply) => {
    const agentStatus = await fastify.agentService.getStatus();
    
    return {
      status: agentStatus.initialized ? 'active' : 'initializing',
      models: agentStatus.models,
      activeSessions: agentStatus.activeSessions,
      timestamp: new Date().toISOString()
    };
  });

  // 获取会话历史
  fastify.get('/sessions/:userId', {
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
            created: { type: 'string', format: 'date-time' },
            lastActive: { type: 'string', format: 'date-time' },
            history: { 
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  role: { type: 'string', enum: ['user', 'assistant'] },
                  content: { type: 'string' },
                  timestamp: { type: 'string', format: 'date-time' }
                }
              }
            }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { userId } = request.params;
    
    // 验证用户ID
    if (!userId || userId.length < 3) {
      return reply.code(400).send({
        error: 'invalid_user_id',
        message: '无效的用户ID'
      });
    }
    
    // 获取会话数据
    const sessionData = fastify.agentService.sessionData.get(userId);
    
    if (!sessionData) {
      return reply.code(404).send({
        error: 'session_not_found',
        message: '未找到会话数据'
      });
    }
    
    // 格式化日期
    const formattedSession = {
      ...sessionData,
      created: sessionData.created.toISOString(),
      lastActive: sessionData.lastActive.toISOString(),
      history: sessionData.history.map(msg => ({
        ...msg,
        timestamp: msg.timestamp.toISOString()
      }))
    };
    
    return formattedSession;
  });

  // 清除会话历史
  fastify.delete('/sessions/:userId', {
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
            success: { type: 'boolean' },
            message: { type: 'string' }
          }
        }
      }
    }
  }, async (request, reply) => {
    const { userId } = request.params;
    
    // 验证用户ID
    if (!userId || userId.length < 3) {
      return reply.code(400).send({
        error: 'invalid_user_id',
        message: '无效的用户ID'
      });
    }
    
    // 删除会话数据
    const sessionExists = fastify.agentService.sessionData.has(userId);
    
    if (sessionExists) {
      fastify.agentService.sessionData.delete(userId);
      
      // 如果有Redis，同时删除Redis中的会话
      if (fastify.redis) {
        try {
          await fastify.redis.del(`session:${userId}`);
        } catch (error) {
          fastify.log.error(`从Redis删除会话失败: ${error.message}`);
          // 不抛出错误，继续执行
        }
      }
      
      fastify.log.info(`已清除用户会话: ${userId}`);
      
      return {
        success: true,
        message: '会话已清除'
      };
    } else {
      return {
        success: false,
        message: '未找到会话数据'
      };
    }
  });
  
  // 获取智能体协作者
  fastify.get('/collaborators', {
    schema: {
      response: {
        200: {
          type: 'object',
          properties: {
            collaborators: { 
              type: 'array', 
              items: { 
                type: 'object',
                properties: {
                  id: { type: 'string' },
                  name: { type: 'string' },
                  description: { type: 'string' }
                }
              } 
            }
          }
        }
      }
    }
  }, async (request, reply) => {
    // 获取协作者信息
    const { agent, protocols } = fastify.agentConfig;
    const collaboratorIds = agent.collaborators || [];
    
    // 如果有配置协作协议，使用其中的详细信息
    const collaborators = [];
    
    if (protocols?.agent_collaboration?.collaboration_partners) {
      const partners = protocols.agent_collaboration.collaboration_partners;
      
      for (const collaboratorId of collaboratorIds) {
        const partner = partners[collaboratorId];
        collaborators.push({
          id: collaboratorId,
          name: partnerNames[collaboratorId] || collaboratorId,
          description: partnerDescriptions[collaboratorId] || '',
          contexts: partner?.contexts || [],
          delegationRules: partner?.delegation_rules || ''
        });
      }
    } else {
      // 使用基本信息
      for (const collaboratorId of collaboratorIds) {
        collaborators.push({
          id: collaboratorId,
          name: partnerNames[collaboratorId] || collaboratorId,
          description: partnerDescriptions[collaboratorId] || ''
        });
      }
    }
    
    return { collaborators };
  });
};

// 协作伙伴名称映射
const partnerNames = {
  xiaoai: '小爱',
  laoke: '老柯',
  xiaoke: '小柯'
};

// 协作伙伴描述映射
const partnerDescriptions = {
  xiaoai: '索克生活APP的主智能体，擅长通用信息和系统交互',
  laoke: '索克生活APP的医疗顾问智能体，擅长医疗问题诊断和治疗建议',
  xiaoke: '索克生活APP的情感支持智能体，擅长社交和情感互动'
};