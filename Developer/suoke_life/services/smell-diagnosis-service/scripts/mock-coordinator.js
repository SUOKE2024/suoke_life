/**
 * 模拟四诊协调器服务
 * 用于本地开发环境，模拟四诊协调器服务的基本功能
 */

const http = require('http');

const PORT = process.env.PORT || 3050;

// 存储诊断会话数据
const sessions = new Map();

// 创建HTTP服务器
const server = http.createServer((req, res) => {
  // 设置跨域头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  // 处理预检请求
  if (req.method === 'OPTIONS') {
    res.statusCode = 204;
    res.end();
    return;
  }
  
  // 解析URL路径
  const url = new URL(req.url, `http://${req.headers.host}`);
  const path = url.pathname;
  
  // 健康检查端点
  if (path === '/health') {
    res.statusCode = 200;
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify({ status: 'ok', timestamp: new Date().toISOString() }));
    console.log(`[${new Date().toISOString()}] 健康检查请求`);
    return;
  }
  
  // API前缀
  if (path.startsWith('/api/coordinator')) {
    // 创建诊断会话
    if (path === '/api/coordinator/sessions' && req.method === 'POST') {
      let body = '';
      
      req.on('data', chunk => {
        body += chunk.toString();
      });
      
      req.on('end', () => {
        try {
          const data = JSON.parse(body);
          const sessionId = `session-${Date.now()}`;
          
          // 存储会话数据
          sessions.set(sessionId, {
            id: sessionId,
            userId: data.userId || 'anonymous',
            createdAt: new Date().toISOString(),
            status: 'active',
            diagnoses: []
          });
          
          res.statusCode = 201;
          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify({ 
            success: true, 
            data: { sessionId } 
          }));
          
          console.log(`[${new Date().toISOString()}] 创建诊断会话: ${sessionId}`);
        } catch (err) {
          res.statusCode = 400;
          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify({ 
            success: false, 
            error: 'Invalid request body' 
          }));
        }
      });
      return;
    }
    
    // 提交诊断结果
    if (path === '/api/coordinator/diagnoses' && req.method === 'POST') {
      let body = '';
      
      req.on('data', chunk => {
        body += chunk.toString();
      });
      
      req.on('end', () => {
        try {
          const data = JSON.parse(body);
          const { sessionId, diagnosisType, diagnosisData } = data;
          
          if (!sessionId || !diagnosisType || !diagnosisData) {
            throw new Error('Missing required fields');
          }
          
          // 检查会话是否存在
          if (!sessions.has(sessionId)) {
            res.statusCode = 404;
            res.setHeader('Content-Type', 'application/json');
            res.end(JSON.stringify({ 
              success: false, 
              error: 'Session not found' 
            }));
            return;
          }
          
          // 获取会话数据
          const session = sessions.get(sessionId);
          
          // 添加诊断结果
          const diagnosisId = `diag-${Date.now()}`;
          const diagnosis = {
            id: diagnosisId,
            type: diagnosisType,
            timestamp: new Date().toISOString(),
            data: diagnosisData
          };
          
          session.diagnoses.push(diagnosis);
          
          // 更新会话
          sessions.set(sessionId, session);
          
          res.statusCode = 200;
          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify({ 
            success: true, 
            data: { diagnosisId, sessionId } 
          }));
          
          console.log(`[${new Date().toISOString()}] 提交诊断结果: ${diagnosisId} (会话: ${sessionId})`);
        } catch (err) {
          res.statusCode = 400;
          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify({ 
            success: false, 
            error: err.message 
          }));
        }
      });
      return;
    }
    
    // 获取会话信息
    if (path.match(/^\/api\/coordinator\/sessions\/[^/]+$/) && req.method === 'GET') {
      const sessionId = path.split('/').pop();
      
      if (!sessions.has(sessionId)) {
        res.statusCode = 404;
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify({ 
          success: false, 
          error: 'Session not found' 
        }));
        return;
      }
      
      const session = sessions.get(sessionId);
      
      res.statusCode = 200;
      res.setHeader('Content-Type', 'application/json');
      res.end(JSON.stringify({ 
        success: true, 
        data: session 
      }));
      
      console.log(`[${new Date().toISOString()}] 获取会话信息: ${sessionId}`);
      return;
    }
    
    // 获取综合诊断报告
    if (path.match(/^\/api\/coordinator\/sessions\/[^/]+\/report$/) && req.method === 'GET') {
      const sessionId = path.split('/')[3];
      
      if (!sessions.has(sessionId)) {
        res.statusCode = 404;
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify({ 
          success: false, 
          error: 'Session not found' 
        }));
        return;
      }
      
      const session = sessions.get(sessionId);
      
      // 生成模拟报告
      const report = {
        sessionId,
        userId: session.userId,
        timestamp: new Date().toISOString(),
        diagnoses: session.diagnoses,
        constitution: '气虚质',
        confidenceScore: 0.85,
        recommendation: [
          '注意休息，避免劳累',
          '饮食宜清淡，避免辛辣刺激',
          '可适当补充气血的食物'
        ]
      };
      
      res.statusCode = 200;
      res.setHeader('Content-Type', 'application/json');
      res.end(JSON.stringify({ 
        success: true, 
        data: report 
      }));
      
      console.log(`[${new Date().toISOString()}] 生成诊断报告: ${sessionId}`);
      return;
    }
  }
  
  // 未找到对应的路径
  res.statusCode = 404;
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify({ 
    success: false, 
    error: 'Not found' 
  }));
});

// 启动服务器
server.listen(PORT, () => {
  console.log(`[${new Date().toISOString()}] 模拟四诊协调器服务已启动，监听端口: ${PORT}`);
}); 