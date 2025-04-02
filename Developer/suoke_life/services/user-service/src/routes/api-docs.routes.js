/**
 * API文档路由
 * 提供API文档和服务说明
 */
const express = require('express');
const router = express.Router();
const packageInfo = require('../../package.json');

/**
 * @route GET /api-docs
 * @description 获取API文档
 * @access 公开
 */
router.get('/', (req, res) => {
  res.json({
    service: 'user-service',
    version: packageInfo.version,
    description: '索克生活用户服务API',
    endpoints: {
      core: [
        { path: '/health', method: 'GET', description: '健康检查' },
        { path: '/health/ready', method: 'GET', description: '就绪状态检查' },
        { path: '/health/startup', method: 'GET', description: '启动状态检查' },
        { path: '/metrics', method: 'GET', description: 'Prometheus指标' },
        { path: '/api-docs', method: 'GET', description: 'API文档' }
      ],
      users: [
        { path: '/api/users', method: 'GET', description: '获取用户列表' },
        { path: '/api/users/:id', method: 'GET', description: '获取用户详情' },
        { path: '/api/users', method: 'POST', description: '创建用户' },
        { path: '/api/users/:id', method: 'PUT', description: '更新用户信息' },
        { path: '/api/users/:id', method: 'DELETE', description: '删除用户' },
        { path: '/api/users/:id/avatar', method: 'POST', description: '上传用户头像' }
      ],
      profiles: [
        { path: '/api/profiles/:userId', method: 'GET', description: '获取用户档案' },
        { path: '/api/profiles/:userId', method: 'PUT', description: '更新用户档案' }
      ],
      health: [
        { path: '/api/health/:userId/data', method: 'GET', description: '获取用户健康数据' },
        { path: '/api/health/:userId/data', method: 'POST', description: '添加用户健康数据' },
        { path: '/api/health/:userId/metrics', method: 'GET', description: '获取用户健康指标' },
        { path: '/api/health/:userId/recommendations', method: 'GET', description: '获取健康建议' }
      ],
      healthProfiles: [
        { path: '/api/health-profiles/:userId', method: 'GET', description: '获取用户健康档案' },
        { path: '/api/health-profiles/:userId', method: 'POST', description: '创建用户健康档案' },
        { path: '/api/health-profiles/:userId', method: 'PUT', description: '更新用户健康档案' }
      ],
      knowledgePreferences: [
        { path: '/api/knowledge-preferences/:userId', method: 'GET', description: '获取用户知识偏好' },
        { path: '/api/knowledge-preferences/:userId', method: 'PUT', description: '更新用户知识偏好' },
        { path: '/api/knowledge-preferences/:userId/domains', method: 'GET', description: '获取用户感兴趣的知识领域' }
      ],
      recommendations: [
        { path: '/api/recommendations/content/:userId', method: 'GET', description: '获取内容推荐' },
        { path: '/api/recommendations/health/:userId', method: 'GET', description: '获取健康推荐' }
      ],
      socialShares: [
        { path: '/api/social-shares', method: 'POST', description: '创建分享' },
        { path: '/api/social-shares/:shareId', method: 'GET', description: '获取分享详情' },
        { path: '/api/social-shares/:shareId', method: 'PUT', description: '更新分享' },
        { path: '/api/social-shares/:shareId', method: 'DELETE', description: '删除分享' },
        { path: '/api/social-shares/user/:userId', method: 'GET', description: '获取用户分享列表' },
        { path: '/api/social-shares/:shareId/interactions', method: 'POST', description: '记录分享互动' },
        { path: '/api/social-shares/:shareId/interactions', method: 'GET', description: '获取分享互动列表' },
        { path: '/api/social-shares/:shareId/link', method: 'POST', description: '生成分享链接' },
        { path: '/api/social-shares/view/:shareId', method: 'POST', description: '记录分享查看' }
      ],
      userMatches: [
        { path: '/api/user-matches', method: 'POST', description: '创建用户匹配' },
        { path: '/api/user-matches/:matchId', method: 'GET', description: '获取匹配详情' },
        { path: '/api/user-matches/:matchId/status', method: 'PUT', description: '更新匹配状态' },
        { path: '/api/user-matches', method: 'GET', description: '获取用户匹配列表' },
        { path: '/api/user-matches/:matchId', method: 'DELETE', description: '删除匹配记录' },
        { path: '/api/user-matches/interest-vector', method: 'POST', description: '计算用户兴趣向量' },
        { path: '/api/user-matches/potential', method: 'GET', description: '查找潜在匹配用户' },
        { path: '/api/user-matches/connections', method: 'POST', description: '创建用户连接请求' },
        { path: '/api/user-matches/connections/:connectionId/status', method: 'PUT', description: '更新连接状态' },
        { path: '/api/user-matches/connections', method: 'GET', description: '获取用户连接列表' }
      ]
    }
  });
});

module.exports = router;