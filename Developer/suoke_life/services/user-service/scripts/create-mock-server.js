#!/usr/bin/env node

/**
 * 这个脚本用于生成一个模拟用户服务的 mock-server.js 文件
 * 生成的文件可以作为独立服务运行，不依赖数据库
 */

const fs = require('fs');
const path = require('path');

// 生成用户数据
const generateUsers = () => {
  return [
    {
      id: '11111111-1111-1111-1111-111111111111',
      username: 'admin',
      email: 'admin@suoke.life',
      role: 'admin',
      status: 'active',
      createdAt: '2023-01-01T00:00:00Z',
      updatedAt: '2023-01-01T00:00:00Z',
      profile: {
        id: '22222222-2222-2222-2222-222222222222',
        userId: '11111111-1111-1111-1111-111111111111',
        fullName: '管理员',
        avatar: '/avatars/admin.png',
        phone: '13900000000',
        address: '北京市朝阳区',
        bio: '系统管理员',
        dateOfBirth: '1980-01-01',
        gender: 'prefer_not_to_say',
        createdAt: '2023-01-01T00:00:00Z',
        updatedAt: '2023-01-01T00:00:00Z',
      }
    },
    {
      id: '33333333-3333-3333-3333-333333333333',
      username: 'user1',
      email: 'user1@example.com',
      role: 'user',
      status: 'active',
      createdAt: '2023-01-02T00:00:00Z',
      updatedAt: '2023-01-02T00:00:00Z',
      profile: {
        id: '44444444-4444-4444-4444-444444444444',
        userId: '33333333-3333-3333-3333-333333333333',
        fullName: '张三',
        avatar: '/avatars/default.png',
        phone: '13800138000',
        address: '北京市海淀区中关村',
        bio: '我是一名健康生活爱好者',
        dateOfBirth: '1985-05-15',
        gender: 'male',
        createdAt: '2023-01-02T00:00:00Z',
        updatedAt: '2023-01-02T00:00:00Z',
      }
    },
    {
      id: '55555555-5555-5555-5555-555555555555',
      username: 'user2',
      email: 'user2@example.com',
      role: 'user',
      status: 'active',
      createdAt: '2023-01-03T00:00:00Z',
      updatedAt: '2023-01-03T00:00:00Z',
      profile: {
        id: '66666666-6666-6666-6666-666666666666',
        userId: '55555555-5555-5555-5555-555555555555',
        fullName: '李四',
        avatar: '/avatars/default.png',
        phone: '13900001111',
        address: '上海市浦东新区',
        bio: '健康养生爱好者',
        dateOfBirth: '1990-03-20',
        gender: 'female',
        createdAt: '2023-01-03T00:00:00Z',
        updatedAt: '2023-01-03T00:00:00Z',
      }
    }
  ];
};

// 生成用户知识偏好数据
const generatePreferences = () => {
  return [
    {
      id: '77777777-7777-7777-7777-777777777777',
      userId: '33333333-3333-3333-3333-333333333333',
      domainPreferences: {
        tcm: 0.9,
        nutrition: 0.8,
        wellness: 0.7
      },
      contentTypePreferences: {
        article: 0.8, 
        video: 0.6, 
        infographic: 0.9
      },
      difficultyLevel: 'intermediate',
      createdAt: '2023-01-02T00:00:00Z',
      updatedAt: '2023-01-02T00:00:00Z'
    },
    {
      id: '88888888-8888-8888-8888-888888888888',
      userId: '55555555-5555-5555-5555-555555555555',
      domainPreferences: {
        tcm: 0.6,
        nutrition: 0.9,
        wellness: 0.8
      },
      contentTypePreferences: {
        article: 0.7, 
        video: 0.9, 
        infographic: 0.6
      },
      difficultyLevel: 'beginner',
      createdAt: '2023-01-03T00:00:00Z',
      updatedAt: '2023-01-03T00:00:00Z'
    }
  ];
};

// 生成社交分享数据
const generateShares = () => {
  return [
    {
      id: '99999999-9999-9999-9999-999999999999',
      userId: '33333333-3333-3333-3333-333333333333',
      contentId: 'article-12345',
      contentType: 'article',
      shareType: 'wechat',
      shareStatus: 'active',
      shareLink: 'https://suoke.life/share/s/article-12345',
      shareTitle: '中医养生之道',
      shareDescription: '本文介绍了中医养生的基本原则...',
      shareImage: '/images/articles/tcm-wellness.jpg',
      viewCount: 42,
      createdAt: '2023-02-15T10:30:00Z',
      updatedAt: '2023-02-15T10:30:00Z'
    }
  ];
};

// 生成mock服务器代码
const generateMockServer = () => {
  const users = generateUsers();
  const preferences = generatePreferences();
  const shares = generateShares();
  
  return `
const express = require('express');
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid');

// 创建Express应用
const app = express();
const PORT = process.env.PORT || 3002;

// 中间件
app.use(bodyParser.json());

// 记录请求日志
app.use((req, res, next) => {
  console.log(\`[\${new Date().toISOString()}] \${req.method} \${req.url}\`);
  next();
});

// 模拟数据
let users = ${JSON.stringify(users, null, 2)};
let preferences = ${JSON.stringify(preferences, null, 2)};
let shares = ${JSON.stringify(shares, null, 2)};

// 健康检查端点
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.get('/health/ready', (req, res) => {
  res.status(200).json({ status: 'ready', timestamp: new Date().toISOString() });
});

app.get('/health/startup', (req, res) => {
  res.status(200).json({ status: 'started', timestamp: new Date().toISOString() });
});

// 用户API
app.get('/users', (req, res) => {
  res.json(users);
});

app.get('/users/:id', (req, res) => {
  const user = users.find(u => u.id === req.params.id);
  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }
  res.json(user);
});

app.post('/users', (req, res) => {
  const newUser = {
    id: uuidv4(),
    ...req.body,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };
  users.push(newUser);
  res.status(201).json(newUser);
});

app.put('/users/:id', (req, res) => {
  const index = users.findIndex(u => u.id === req.params.id);
  if (index === -1) {
    return res.status(404).json({ error: 'User not found' });
  }
  
  users[index] = {
    ...users[index],
    ...req.body,
    updatedAt: new Date().toISOString()
  };
  
  res.json(users[index]);
});

app.delete('/users/:id', (req, res) => {
  const index = users.findIndex(u => u.id === req.params.id);
  if (index === -1) {
    return res.status(404).json({ error: 'User not found' });
  }
  
  const deletedUser = users[index];
  users.splice(index, 1);
  
  res.json(deletedUser);
});

// 用户知识偏好API
app.get('/users/:userId/knowledge-preferences', (req, res) => {
  const preference = preferences.find(p => p.userId === req.params.userId);
  if (!preference) {
    return res.status(404).json({ error: 'Preferences not found' });
  }
  res.json(preference);
});

app.put('/users/:userId/knowledge-preferences', (req, res) => {
  let preference = preferences.find(p => p.userId === req.params.userId);
  
  if (preference) {
    const index = preferences.findIndex(p => p.userId === req.params.userId);
    preferences[index] = {
      ...preferences[index],
      ...req.body,
      updatedAt: new Date().toISOString()
    };
    return res.json(preferences[index]);
  }
  
  // 创建新偏好
  preference = {
    id: uuidv4(),
    userId: req.params.userId,
    ...req.body,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };
  
  preferences.push(preference);
  res.status(201).json(preference);
});

// 社交分享API
app.get('/social-shares', (req, res) => {
  const userShares = req.query.userId 
    ? shares.filter(s => s.userId === req.query.userId) 
    : shares;
  res.json(userShares);
});

app.post('/social-shares', (req, res) => {
  const newShare = {
    id: uuidv4(),
    ...req.body,
    viewCount: 0,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };
  
  shares.push(newShare);
  res.status(201).json(newShare);
});

// 错误处理中间件
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Internal server error' });
});

// 启动服务器
app.listen(PORT, () => {
  console.log(\`Mock User Service running on port \${PORT}\`);
});
`;
};

// 写入文件
const mockServerPath = path.join(__dirname, '..', 'mock-server.js');
fs.writeFileSync(mockServerPath, generateMockServer());

console.log(`已成功生成mock-server.js文件: ${mockServerPath}`);
console.log('运行命令启动模拟服务器: node mock-server.js');

// 设置可执行权限
fs.chmodSync(mockServerPath, '755'); 