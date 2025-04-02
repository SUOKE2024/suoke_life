/**
 * WebSocket配置
 * 提供实时通信功能
 */
const logger = require('../utils/logger');
const { authenticateToken } = require('../middlewares/auth');

/**
 * 配置Socket.io
 * @param {Object} io - Socket.io实例
 */
module.exports = function(io) {
  // 中间件：认证和连接日志
  io.use(async (socket, next) => {
    try {
      // 获取token
      const token = socket.handshake.auth.token || 
                    socket.handshake.query.token || 
                    socket.handshake.headers.authorization?.split(' ')[1];
      
      if (!token) {
        return next(new Error('认证失败: 缺少token'));
      }
      
      // 验证token
      try {
        const user = await authenticateToken(token);
        socket.user = user;
        logger.info(`用户 ${user.id} 已连接到WebSocket`);
        next();
      } catch (error) {
        return next(new Error('认证失败: 无效token'));
      }
    } catch (error) {
      logger.error('WebSocket连接错误:', error);
      next(new Error('连接失败'));
    }
  });
  
  // 连接处理
  io.on('connection', (socket) => {
    const userId = socket.user?.id || 'unknown';
    
    // 加入用户私人频道
    socket.join(`user:${userId}`);
    
    // 处理加入房间请求
    socket.on('join_room', (data) => {
      try {
        const { roomType, roomId } = data;
        if (!roomType || !roomId) {
          socket.emit('error', { message: '缺少房间类型或ID' });
          return;
        }
        
        const roomKey = `${roomType}:${roomId}`;
        socket.join(roomKey);
        logger.info(`用户 ${userId} 加入房间 ${roomKey}`);
        
        // 通知房间其他成员
        socket.to(roomKey).emit('user_joined', { 
          userId, 
          timestamp: new Date()
        });
        
        // 确认加入成功
        socket.emit('room_joined', { 
          room: roomKey,
          timestamp: new Date()
        });
      } catch (error) {
        logger.error(`加入房间失败: ${error.message}`);
        socket.emit('error', { message: '加入房间失败' });
      }
    });
    
    // 处理离开房间请求
    socket.on('leave_room', (data) => {
      try {
        const { roomType, roomId } = data;
        if (!roomType || !roomId) {
          socket.emit('error', { message: '缺少房间类型或ID' });
          return;
        }
        
        const roomKey = `${roomType}:${roomId}`;
        socket.leave(roomKey);
        logger.info(`用户 ${userId} 离开房间 ${roomKey}`);
        
        // 通知房间其他成员
        socket.to(roomKey).emit('user_left', { 
          userId, 
          timestamp: new Date()
        });
        
        // 确认离开成功
        socket.emit('room_left', { 
          room: roomKey,
          timestamp: new Date()
        });
      } catch (error) {
        logger.error(`离开房间失败: ${error.message}`);
        socket.emit('error', { message: '离开房间失败' });
      }
    });
    
    // 加入团队寻宝会话
    socket.on('join_team_hunt', (data) => {
      try {
        const { sessionId, teamId } = data;
        if (!sessionId) {
          socket.emit('error', { message: '缺少会话ID' });
          return;
        }
        
        // 加入团队寻宝房间
        const roomKey = `hunt:${sessionId}`;
        socket.join(roomKey);
        
        // 如果提供了团队ID，也加入团队房间
        if (teamId) {
          socket.join(`team:${teamId}`);
        }
        
        logger.info(`用户 ${userId} 加入寻宝会话 ${sessionId}`);
        
        // 通知其他会话成员
        socket.to(roomKey).emit('hunt_member_joined', {
          userId,
          sessionId,
          timestamp: new Date()
        });
        
        // 确认加入成功
        socket.emit('hunt_joined', {
          sessionId,
          timestamp: new Date()
        });
      } catch (error) {
        logger.error(`加入团队寻宝会话失败: ${error.message}`);
        socket.emit('error', { message: '加入寻宝会话失败' });
      }
    });
    
    // 宝藏发现广播
    socket.on('treasure_found', (data) => {
      try {
        const { treasureId, treasureName, mazeId, sessionId, teamId } = data;
        
        if (!treasureId || !mazeId) {
          socket.emit('error', { message: '缺少必要参数' });
          return;
        }
        
        logger.info(`用户 ${userId} 在迷宫 ${mazeId} 中发现宝藏 ${treasureId}`);
        
        // 创建广播消息
        const message = {
          type: 'treasure_found',
          userId,
          treasureId,
          treasureName,
          timestamp: new Date()
        };
        
        // 向团队会话广播
        if (sessionId) {
          socket.to(`hunt:${sessionId}`).emit('team_treasure_found', message);
        }
        
        // 向团队广播
        if (teamId) {
          socket.to(`team:${teamId}`).emit('team_treasure_found', message);
        }
        
        // 向迷宫中的所有用户广播
        socket.to(`maze:${mazeId}`).emit('maze_treasure_found', message);
        
        // 确认广播成功
        socket.emit('broadcast_confirmed', {
          type: 'treasure_found',
          timestamp: new Date()
        });
      } catch (error) {
        logger.error(`宝藏发现广播失败: ${error.message}`);
        socket.emit('error', { message: '宝藏广播失败' });
      }
    });
    
    // 地理位置更新
    socket.on('location_update', (data) => {
      try {
        const { latitude, longitude, mazeId, sessionId } = data;
        
        if (!latitude || !longitude) {
          socket.emit('error', { message: '缺少位置信息' });
          return;
        }
        
        // 更新用户位置
        socket.user.location = { latitude, longitude };
        
        // 创建消息
        const message = {
          userId,
          location: { latitude, longitude },
          timestamp: new Date()
        };
        
        // 位置共享房间
        if (sessionId) {
          socket.to(`hunt:${sessionId}`).emit('member_location_update', message);
        }
        
        // 如果在迷宫中，更新迷宫位置
        if (mazeId) {
          socket.to(`maze:${mazeId}`).emit('maze_user_location', message);
        }
      } catch (error) {
        logger.error(`位置更新失败: ${error.message}`);
        socket.emit('error', { message: '位置更新失败' });
      }
    });
    
    // 断开连接处理
    socket.on('disconnect', () => {
      logger.info(`用户 ${userId} 与WebSocket断开连接`);
      
      // 这里可以添加断开连接时的清理逻辑
    });
  });
  
  // 自定义事件发射器
  io.emitToUser = (userId, event, data) => {
    io.to(`user:${userId}`).emit(event, data);
  };
  
  io.emitToTeam = (teamId, event, data) => {
    io.to(`team:${teamId}`).emit(event, data);
  };
  
  io.emitToMaze = (mazeId, event, data) => {
    io.to(`maze:${mazeId}`).emit(event, data);
  };
  
  io.emitToHunt = (sessionId, event, data) => {
    io.to(`hunt:${sessionId}`).emit(event, data);
  };
  
  logger.info('WebSocket服务已配置并初始化');
  
  return io;
}; 