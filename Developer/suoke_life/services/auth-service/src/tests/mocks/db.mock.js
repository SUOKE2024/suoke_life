/**
 * 数据库模拟文件
 */

// 创建内存存储对象模拟数据库表
const dbStore = {
  users: [
    {
      id: '1',
      username: 'admin',
      email: 'admin@suoke.life',
      password: '$2b$10$6Bnyt0UtJ3xdqE3wTRIAJeBjvxRjK1rY7JgcwOy2s0G6RxJFzXFY.',  // admin123
      role: 'admin',
      bio: '系统管理员',
      is_active: true,
      created_at: new Date(),
      updated_at: new Date()
    },
    {
      id: '2',
      username: 'test_user',
      email: 'test@suoke.life',
      password: '$2b$10$CSRanwtb16HOI4aQFLfLbO7f2N1JEiWR.Xki1r9TfJ6XX3Kfz.HQm',  // password123
      role: 'user',
      bio: '测试用户',
      is_active: true,
      created_at: new Date(),
      updated_at: new Date()
    }
  ],
  refresh_tokens: [],
  oauth_accounts: []
};

// 模拟数据库工具函数
const createQueryBuilder = (tableName) => {
  // 存储查询条件
  let whereConditions = [];
  let orWhereConditions = [];
  let updateData = null;
  let insertData = null;
  let selectedFields = ['*'];
  let limitValue = null;
  
  // 当前查询结果集
  let results = [...dbStore[tableName] || []];
  
  // 查询构建器对象
  const queryBuilder = {
    // 选择字段
    select: (fields) => {
      selectedFields = Array.isArray(fields) ? fields : [fields];
      return queryBuilder;
    },
    
    // 添加WHERE条件
    where: jest.fn((conditions) => {
      if (typeof conditions === 'object') {
        whereConditions.push(conditions);
      }
      return queryBuilder;
    }),
    
    // 添加OR WHERE条件
    orWhere: jest.fn((conditions) => {
      if (typeof conditions === 'object') {
        orWhereConditions.push(conditions);
      }
      return queryBuilder;
    }),
    
    // 限制返回结果数量
    limit: (value) => {
      limitValue = value;
      return queryBuilder;
    },
    
    // 更新数据
    update: jest.fn((data) => {
      updateData = data;
      return queryBuilder;
    }),
    
    // 插入数据
    insert: jest.fn((data) => {
      insertData = data;
      return queryBuilder;
    }),
    
    // 删除数据
    del: jest.fn().mockImplementation(() => {
      return Promise.resolve(1);
    }),
    
    // 执行查询
    then: jest.fn((callback) => {
      const applyWhere = () => {
        if (whereConditions.length === 0) return;
        
        results = results.filter(item => {
          return whereConditions.some(condition => {
            return Object.entries(condition).every(([key, value]) => {
              return item[key] === value;
            });
          });
        });
      };
      
      const applyOrWhere = () => {
        if (orWhereConditions.length === 0) return;
        
        const orResults = dbStore[tableName].filter(item => {
          return orWhereConditions.some(condition => {
            return Object.entries(condition).every(([key, value]) => {
              return item[key] === value;
            });
          });
        });
        
        // 合并结果并去重
        const combinedResults = [...results, ...orResults];
        results = [...new Map(combinedResults.map(item => [item.id, item])).values()];
      };
      
      const applyLimit = () => {
        if (limitValue !== null) {
          results = results.slice(0, limitValue);
        }
      };
      
      // 应用查询条件
      applyWhere();
      applyOrWhere();
      applyLimit();
      
      // 处理更新操作
      if (updateData) {
        results.forEach(item => {
          Object.assign(item, updateData, { updated_at: new Date() });
        });
        
        return Promise.resolve(results.length);
      }
      
      // 处理插入操作
      if (insertData) {
        const newItem = {
          ...insertData,
          created_at: new Date(),
          updated_at: new Date()
        };
        
        // 添加新项到存储
        if (Array.isArray(dbStore[tableName])) {
          dbStore[tableName].push(newItem);
        } else {
          dbStore[tableName] = [newItem];
        }
        
        return Promise.resolve([newItem.id]);
      }
      
      // 执行选择字段映射
      if (selectedFields[0] !== '*') {
        results = results.map(item => {
          const result = {};
          selectedFields.forEach(field => {
            result[field] = item[field];
          });
          return result;
        });
      }
      
      // 返回结果
      return Promise.resolve(results);
    }),
    
    // 获取第一条结果
    first: jest.fn(() => {
      // 应用查询条件
      const applyWhere = () => {
        if (whereConditions.length === 0) return;
        
        results = results.filter(item => {
          return whereConditions.some(condition => {
            return Object.entries(condition).every(([key, value]) => {
              return item[key] === value;
            });
          });
        });
      };
      
      applyWhere();
      
      // 获取第一条结果
      const firstResult = results[0] || null;
      
      // 执行选择字段映射
      if (firstResult && selectedFields[0] !== '*') {
        const mappedResult = {};
        selectedFields.forEach(field => {
          mappedResult[field] = firstResult[field];
        });
        return Promise.resolve(mappedResult);
      }
      
      return Promise.resolve(firstResult);
    })
  };
  
  return queryBuilder;
};

// 模拟数据库客户端
const mockDb = jest.fn((tableName) => {
  return createQueryBuilder(tableName);
});

// 添加事务支持
mockDb.transaction = jest.fn((callback) => {
  return Promise.resolve(callback(mockDb));
});

// 重置所有模拟数据
mockDb.resetMocks = () => {
  Object.keys(dbStore).forEach(key => {
    if (key === 'users') {
      dbStore[key] = [
        {
          id: '1',
          username: 'admin',
          email: 'admin@suoke.life',
          password: '$2b$10$6Bnyt0UtJ3xdqE3wTRIAJeBjvxRjK1rY7JgcwOy2s0G6RxJFzXFY.',
          role: 'admin',
          bio: '系统管理员',
          is_active: true,
          created_at: new Date(),
          updated_at: new Date()
        },
        {
          id: '2',
          username: 'test_user',
          email: 'test@suoke.life',
          password: '$2b$10$CSRanwtb16HOI4aQFLfLbO7f2N1JEiWR.Xki1r9TfJ6XX3Kfz.HQm',
          role: 'user',
          bio: '测试用户',
          is_active: true,
          created_at: new Date(),
          updated_at: new Date()
        }
      ];
    } else {
      dbStore[key] = [];
    }
  });
  
  jest.clearAllMocks();
};

// 导出模拟数据库客户端
module.exports = mockDb; 