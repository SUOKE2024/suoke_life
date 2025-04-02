const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const helmet = require('helmet');

/**
 * 创建一个用于测试的Mock应用
 * @returns {Express.Application} 用于测试的Express应用
 */
function createMockApp() {
  const app = express();
  
  // 基础中间件
  app.use(helmet());
  app.use(cors());
  app.use(bodyParser.json());
  app.use(bodyParser.urlencoded({ extended: true }));
  
  // 模拟代理协调器路由
  app.use('/api/v1/agents/coordinator', (req, res, next) => {
    if (req.path === '/health') {
      return res.json({ status: 'ok' });
    }
    
    if (req.path === '/agents/available') {
      return res.json({ 
        agents: [
          { id: 'xiaoke', name: '小克', status: 'active' },
          { id: 'xiaoai', name: '小艾', status: 'active' }
        ]
      });
    }
    
    next();
  });
  
  // 错误处理中间件
  app.use((err, req, res, next) => {
    res.status(err.status || 500).json({
      success: false,
      message: err.message,
      error: process.env.NODE_ENV === 'development' ? err : {}
    });
  });
  
  return app;
}

module.exports = { createMockApp };