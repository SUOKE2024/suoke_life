/**
 * 团队寻宝冲突解决机制
 * 处理多团队同时争夺宝藏或资源时的冲突情况
 */

const { EventEmitter } = require('events');
const { v4: uuidv4 } = require('uuid');
const { logger } = require('../../utils/logger');
const { calculateDistance } = require('../../utils/geoUtils');

// 冲突类型枚举
const CONFLICT_TYPE = {
  TREASURE: 'TREASURE_CONFLICT', // 宝藏争夺冲突
  RESOURCE: 'RESOURCE_CONFLICT', // 资源争夺冲突
  TERRITORY: 'TERRITORY_CONFLICT', // 领地争夺冲突
  PATH: 'PATH_CONFLICT' // 路径冲突
};

// 冲突状态枚举
const CONFLICT_STATUS = {
  PENDING: 'PENDING', // 待解决
  RESOLVING: 'RESOLVING', // 解决中
  RESOLVED: 'RESOLVED', // 已解决
  ABANDONED: 'ABANDONED' // 已放弃
};

// 争端解决方式枚举
const RESOLUTION_TYPE = {
  FIRST_COME: 'FIRST_COME_FIRST_SERVED', // 先到先得
  MINI_GAME: 'MINI_GAME', // 小游戏决定
  COLLABORATIVE: 'COLLABORATIVE', // 协作解决
  KNOWLEDGE_CONTEST: 'KNOWLEDGE_CONTEST', // 知识竞赛
  RANDOM: 'RANDOM_ASSIGNMENT', // 随机分配
  SPLIT: 'SPLIT_RESOURCES' // 资源分割
};

/**
 * 冲突解决服务类
 */
class ConflictResolutionService extends EventEmitter {
  constructor() {
    super();
    this.activeConflicts = new Map(); // 活跃冲突列表
    this.resolvedConflicts = []; // 已解决冲突历史
    this.resolutionStrategies = new Map(); // 解决策略映射
    
    // 初始化解决策略
    this._initResolutionStrategies();
  }
  
  /**
   * 初始化解决策略
   * @private
   */
  _initResolutionStrategies() {
    // 宝藏冲突策略
    this.resolutionStrategies.set(CONFLICT_TYPE.TREASURE, [
      {
        type: RESOLUTION_TYPE.FIRST_COME,
        priority: 1,
        condition: (conflict) => conflict.teams.length <= 3, // 3个队伍以内使用先到先得
        resolver: this._resolveByFirstCome.bind(this)
      },
      {
        type: RESOLUTION_TYPE.MINI_GAME,
        priority: 2,
        condition: (conflict) => conflict.teams.length <= 5, // 5个队伍以内使用小游戏
        resolver: this._resolveByMiniGame.bind(this)
      },
      {
        type: RESOLUTION_TYPE.KNOWLEDGE_CONTEST,
        priority: 3,
        condition: () => true, // 默认使用知识竞赛
        resolver: this._resolveByKnowledgeContest.bind(this)
      }
    ]);
    
    // 资源冲突策略
    this.resolutionStrategies.set(CONFLICT_TYPE.RESOURCE, [
      {
        type: RESOLUTION_TYPE.SPLIT,
        priority: 1,
        condition: (conflict) => conflict.resource.isSplittable === true, // 可分割资源
        resolver: this._resolveBySplitResources.bind(this)
      },
      {
        type: RESOLUTION_TYPE.COLLABORATIVE,
        priority: 2,
        condition: (conflict) => conflict.resource.requiresCollaboration === true, // 需要协作资源
        resolver: this._resolveByCollaboration.bind(this)
      },
      {
        type: RESOLUTION_TYPE.RANDOM,
        priority: 3,
        condition: () => true, // 默认随机分配
        resolver: this._resolveByRandom.bind(this)
      }
    ]);
    
    // 领地冲突策略
    this.resolutionStrategies.set(CONFLICT_TYPE.TERRITORY, [
      {
        type: RESOLUTION_TYPE.FIRST_COME,
        priority: 1,
        condition: () => true, // 领地始终先到先得
        resolver: this._resolveByFirstCome.bind(this)
      }
    ]);
    
    // 路径冲突策略
    this.resolutionStrategies.set(CONFLICT_TYPE.PATH, [
      {
        type: RESOLUTION_TYPE.COLLABORATIVE,
        priority: 1,
        condition: () => true, // 路径冲突始终协作解决
        resolver: this._resolveByPathRedirection.bind(this)
      }
    ]);
  }
  
  /**
   * 检测团队间的潜在冲突
   * @param {Array} teams - 团队列表
   * @param {Array} treasures - 宝藏列表
   * @param {Array} resources - 资源列表
   * @returns {Array} - 检测到的冲突列表
   */
  detectConflicts(teams, treasures, resources) {
    const newConflicts = [];
    
    // 检测宝藏冲突 - 当多个团队接近同一宝藏时
    treasures.forEach(treasure => {
      // 获取接近该宝藏的团队（距离小于5米）
      const approachingTeams = teams.filter(team => {
        const distance = calculateDistance(
          treasure.position.latitude, treasure.position.longitude,
          team.currentPosition.latitude, team.currentPosition.longitude
        );
        return distance < 5; // 5米范围内
      });
      
      // 如果多个团队接近同一宝藏，创建冲突
      if (approachingTeams.length > 1) {
        const conflictId = `treasure-${treasure.id}-${Date.now()}`;
        
        // 检查是否已经存在该冲突
        const existingConflict = [...this.activeConflicts.values()].find(
          c => c.type === CONFLICT_TYPE.TREASURE && c.targetId === treasure.id
        );
        
        if (!existingConflict) {
          const conflict = this._createConflict(
            conflictId,
            CONFLICT_TYPE.TREASURE,
            approachingTeams,
            treasure.id,
            { treasure }
          );
          
          this.activeConflicts.set(conflictId, conflict);
          newConflicts.push(conflict);
          
          // 发出冲突检测事件
          this.emit('conflict:detected', conflict);
        }
      }
    });
    
    // 检测资源冲突
    resources.forEach(resource => {
      // 获取接近该资源的团队（距离小于3米）
      const approachingTeams = teams.filter(team => {
        const distance = calculateDistance(
          resource.position.latitude, resource.position.longitude,
          team.currentPosition.latitude, team.currentPosition.longitude
        );
        return distance < 3; // 3米范围内
      });
      
      // 如果多个团队接近同一资源，创建冲突
      if (approachingTeams.length > 1) {
        const conflictId = `resource-${resource.id}-${Date.now()}`;
        
        // 检查是否已经存在该冲突
        const existingConflict = [...this.activeConflicts.values()].find(
          c => c.type === CONFLICT_TYPE.RESOURCE && c.targetId === resource.id
        );
        
        if (!existingConflict) {
          const conflict = this._createConflict(
            conflictId,
            CONFLICT_TYPE.RESOURCE,
            approachingTeams,
            resource.id,
            { resource }
          );
          
          this.activeConflicts.set(conflictId, conflict);
          newConflicts.push(conflict);
          
          // 发出冲突检测事件
          this.emit('conflict:detected', conflict);
        }
      }
    });
    
    // 检测路径冲突 - 当多个团队路径重叠且方向相对时
    for (let i = 0; i < teams.length; i++) {
      for (let j = i + 1; j < teams.length; j++) {
        const teamA = teams[i];
        const teamB = teams[j];
        
        // 如果两队距离很近
        const distance = calculateDistance(
          teamA.currentPosition.latitude, teamA.currentPosition.longitude,
          teamB.currentPosition.latitude, teamB.currentPosition.longitude
        );
        
        if (distance < 10) { // 10米范围内
          // 检查两队是否方向相对
          const isOppositeDirection = this._checkOppositeDirection(teamA, teamB);
          
          if (isOppositeDirection) {
            const conflictId = `path-${teamA.id}-${teamB.id}-${Date.now()}`;
            
            // 检查是否已经存在该冲突
            const existingConflict = [...this.activeConflicts.values()].find(
              c => c.type === CONFLICT_TYPE.PATH && 
                   c.teams.some(t => t.id === teamA.id) && 
                   c.teams.some(t => t.id === teamB.id)
            );
            
            if (!existingConflict) {
              const conflict = this._createConflict(
                conflictId,
                CONFLICT_TYPE.PATH,
                [teamA, teamB],
                `${teamA.id}-${teamB.id}`,
                { 
                  pathA: teamA.currentPath,
                  pathB: teamB.currentPath
                }
              );
              
              this.activeConflicts.set(conflictId, conflict);
              newConflicts.push(conflict);
              
              // 发出冲突检测事件
              this.emit('conflict:detected', conflict);
            }
          }
        }
      }
    }
    
    return newConflicts;
  }
  
  /**
   * 检查两个团队是否方向相对
   * @param {Object} teamA - 第一个团队
   * @param {Object} teamB - 第二个团队
   * @returns {boolean} - 是否方向相对
   * @private
   */
  _checkOppositeDirection(teamA, teamB) {
    // 如果没有路径信息，无法判断
    if (!teamA.heading || !teamB.heading) {
      return false;
    }
    
    // 计算航向差的绝对值
    const headingDiff = Math.abs(teamA.heading - teamB.heading);
    
    // 如果航向差接近180度（±30度），认为是相对方向
    return headingDiff > 150 && headingDiff < 210;
  }
  
  /**
   * 创建新的冲突对象
   * @param {string} id - 冲突ID
   * @param {string} type - 冲突类型
   * @param {Array} teams - 涉及冲突的团队
   * @param {string} targetId - 冲突目标ID
   * @param {Object} metadata - 冲突元数据
   * @returns {Object} - 冲突对象
   * @private
   */
  _createConflict(id, type, teams, targetId, metadata = {}) {
    return {
      id,
      type,
      teams: teams.map(team => ({
        id: team.id,
        name: team.name,
        memberCount: team.members.length,
        currentPosition: team.currentPosition,
        heading: team.heading
      })),
      targetId,
      status: CONFLICT_STATUS.PENDING,
      createdAt: Date.now(),
      resolvedAt: null,
      resolutionType: null,
      winner: null,
      metadata,
      log: []
    };
  }
  
  /**
   * 解决指定冲突
   * @param {string} conflictId - 冲突ID
   * @returns {Promise<Object>} - 解决结果
   */
  async resolveConflict(conflictId) {
    // 获取冲突对象
    const conflict = this.activeConflicts.get(conflictId);
    if (!conflict) {
      throw new Error(`Conflict with ID ${conflictId} not found`);
    }
    
    // 检查冲突状态
    if (conflict.status !== CONFLICT_STATUS.PENDING) {
      throw new Error(`Conflict with ID ${conflictId} is not in PENDING status`);
    }
    
    // 更新冲突状态
    conflict.status = CONFLICT_STATUS.RESOLVING;
    this._logConflictEvent(conflict, '开始解决冲突');
    
    // 获取适用的解决策略
    const strategies = this.resolutionStrategies.get(conflict.type) || [];
    
    // 按优先级排序并找到第一个符合条件的策略
    const strategy = strategies
      .sort((a, b) => a.priority - b.priority)
      .find(s => s.condition(conflict));
    
    if (!strategy) {
      throw new Error(`No resolution strategy found for conflict type ${conflict.type}`);
    }
    
    // 记录所使用的策略
    conflict.resolutionType = strategy.type;
    this._logConflictEvent(conflict, `使用策略: ${strategy.type}`);
    
    try {
      // 执行解决策略
      const result = await strategy.resolver(conflict);
      
      // 更新冲突状态为已解决
      conflict.status = CONFLICT_STATUS.RESOLVED;
      conflict.resolvedAt = Date.now();
      conflict.winner = result.winner;
      
      // 记录解决结果
      this._logConflictEvent(conflict, `冲突已解决: ${JSON.stringify(result)}`);
      
      // 从活跃冲突列表中移除
      this.activeConflicts.delete(conflictId);
      
      // 添加到已解决冲突历史
      this.resolvedConflicts.push(conflict);
      
      // 限制历史记录大小
      if (this.resolvedConflicts.length > 1000) {
        this.resolvedConflicts = this.resolvedConflicts.slice(-1000);
      }
      
      // 发出冲突解决事件
      this.emit('conflict:resolved', conflict, result);
      
      return result;
    } catch (error) {
      // 记录解决失败
      this._logConflictEvent(conflict, `解决失败: ${error.message}`);
      throw error;
    }
  }
  
  /**
   * 放弃解决冲突
   * @param {string} conflictId - 冲突ID
   */
  abandonConflict(conflictId) {
    // 获取冲突对象
    const conflict = this.activeConflicts.get(conflictId);
    if (!conflict) {
      throw new Error(`Conflict with ID ${conflictId} not found`);
    }
    
    // 更新冲突状态
    conflict.status = CONFLICT_STATUS.ABANDONED;
    conflict.resolvedAt = Date.now();
    
    // 记录放弃事件
    this._logConflictEvent(conflict, '冲突已放弃解决');
    
    // 从活跃冲突列表中移除
    this.activeConflicts.delete(conflictId);
    
    // 添加到已解决冲突历史
    this.resolvedConflicts.push(conflict);
    
    // 发出冲突放弃事件
    this.emit('conflict:abandoned', conflict);
    
    return conflict;
  }
  
  /**
   * 记录冲突事件
   * @param {Object} conflict - 冲突对象
   * @param {string} message - 事件消息
   * @private
   */
  _logConflictEvent(conflict, message) {
    conflict.log.push({
      timestamp: Date.now(),
      message
    });
    
    logger.info(`[冲突] ${conflict.id} - ${message}`);
  }
  
  /**
   * 先到先得解决策略
   * @param {Object} conflict - 冲突对象
   * @returns {Promise<Object>} - 解决结果
   * @private
   */
  async _resolveByFirstCome(conflict) {
    // 对团队按到达时间排序
    const sortedTeams = [...conflict.teams]
      .sort((a, b) => a.arrivedAt - b.arrivedAt);
    
    // 确定获胜团队（最先到达的）
    const winner = sortedTeams[0];
    
    // 发送结果通知给各团队
    for (const team of conflict.teams) {
      this.emit('team:notification', team.id, {
        type: 'conflict:resolution',
        conflictId: conflict.id,
        resolutionType: RESOLUTION_TYPE.FIRST_COME,
        isWinner: team.id === winner.id,
        message: team.id === winner.id 
          ? '恭喜！你的团队最先到达，获得了资源。'
          : '很遗憾，另一个团队先到达了。'
      });
    }
    
    return {
      strategy: RESOLUTION_TYPE.FIRST_COME,
      winner
    };
  }
  
  /**
   * 小游戏解决策略
   * @param {Object} conflict - 冲突对象
   * @returns {Promise<Object>} - 解决结果
   * @private
   */
  async _resolveByMiniGame(conflict) {
    // 创建小游戏会话
    const gameSession = {
      id: uuidv4(),
      conflictId: conflict.id,
      teamsStatus: conflict.teams.map(team => ({
        teamId: team.id,
        ready: false,
        score: 0
      })),
      startTime: null,
      endTime: null,
      gameType: this._selectMiniGameType(conflict)
    };
    
    // 向团队发送游戏邀请
    for (const team of conflict.teams) {
      this.emit('team:notification', team.id, {
        type: 'minigame:invitation',
        gameSessionId: gameSession.id,
        gameType: gameSession.gameType,
        conflictId: conflict.id,
        message: '与其他团队争夺资源！点击参与小游戏。',
        expiresIn: 60 // 60秒内必须接受
      });
    }
    
    // 等待团队准备
    const readyPromise = new Promise((resolve, reject) => {
      // 设置超时
      const timeout = setTimeout(() => {
        // 如果超时，随机选择一个团队作为获胜者
        const randomTeam = conflict.teams[Math.floor(Math.random() * conflict.teams.length)];
        resolve({
          strategy: RESOLUTION_TYPE.RANDOM,
          winner: randomTeam,
          reason: 'timeout'
        });
      }, 60000); // 60秒超时
      
      // 监听团队准备事件
      const readyHandler = (teamId, sessionId) => {
        if (sessionId === gameSession.id) {
          // 更新团队状态
          const teamStatus = gameSession.teamsStatus.find(ts => ts.teamId === teamId);
          if (teamStatus) {
            teamStatus.ready = true;
          }
          
          // 检查是否所有团队都准备好了
          const allReady = gameSession.teamsStatus.every(ts => ts.ready);
          if (allReady) {
            clearTimeout(timeout);
            this.removeListener('team:ready', readyHandler);
            
            // 开始游戏
            gameSession.startTime = Date.now();
            this._runMiniGame(gameSession)
              .then(resolve)
              .catch(reject);
          }
        }
      };
      
      this.on('team:ready', readyHandler);
    });
    
    return await readyPromise;
  }
  
  /**
   * 选择小游戏类型
   * @param {Object} conflict - 冲突对象
   * @returns {string} - 游戏类型
   * @private
   */
  _selectMiniGameType(conflict) {
    // 根据冲突类型选择适合的游戏
    const gameTypes = [
      'quiz', // 知识问答
      'reaction', // 反应速度
      'memory', // 记忆力游戏
      'puzzle' // 拼图
    ];
    
    return gameTypes[Math.floor(Math.random() * gameTypes.length)];
  }
  
  /**
   * 运行小游戏
   * @param {Object} gameSession - 游戏会话
   * @returns {Promise<Object>} - 游戏结果
   * @private
   */
  async _runMiniGame(gameSession) {
    // 向所有团队发送游戏开始通知
    for (const teamStatus of gameSession.teamsStatus) {
      this.emit('team:notification', teamStatus.teamId, {
        type: 'minigame:start',
        gameSessionId: gameSession.id,
        gameType: gameSession.gameType
      });
    }
    
    // 模拟游戏进行过程
    return new Promise((resolve) => {
      // 设置游戏结束时间
      setTimeout(() => {
        // 模拟团队得分
        for (const teamStatus of gameSession.teamsStatus) {
          teamStatus.score = Math.floor(Math.random() * 100);
        }
        
        // 按分数排序
        gameSession.teamsStatus.sort((a, b) => b.score - a.score);
        
        // 确定获胜团队
        const winnerStatus = gameSession.teamsStatus[0];
        const winnerTeam = gameSession.teamsStatus[0].teamId;
        
        // 向所有团队发送游戏结果
        for (const teamStatus of gameSession.teamsStatus) {
          this.emit('team:notification', teamStatus.teamId, {
            type: 'minigame:result',
            gameSessionId: gameSession.id,
            isWinner: teamStatus.teamId === winnerTeam,
            score: teamStatus.score,
            winnerScore: winnerStatus.score,
            message: teamStatus.teamId === winnerTeam 
              ? `恭喜！你的团队获胜，得分: ${teamStatus.score}`
              : `很遗憾，你的团队输了。你的得分: ${teamStatus.score}, 获胜团队得分: ${winnerStatus.score}`
          });
        }
        
        // 返回游戏结果
        resolve({
          strategy: RESOLUTION_TYPE.MINI_GAME,
          winner: { 
            id: winnerTeam 
          },
          gameSessionId: gameSession.id,
          scores: gameSession.teamsStatus.map(ts => ({
            teamId: ts.teamId,
            score: ts.score
          }))
        });
      }, 30000); // 假设游戏持续30秒
    });
  }
  
  /**
   * 知识竞赛解决策略
   * @param {Object} conflict - 冲突对象
   * @returns {Promise<Object>} - 解决结果
   * @private
   */
  async _resolveByKnowledgeContest(conflict) {
    // 实现类似于小游戏，但专注于知识问题
    // ...类似于_resolveByMiniGame的实现...
    
    // 简化实现:
    return {
      strategy: RESOLUTION_TYPE.KNOWLEDGE_CONTEST,
      winner: conflict.teams[Math.floor(Math.random() * conflict.teams.length)]
    };
  }
  
  /**
   * 资源分割解决策略
   * @param {Object} conflict - 冲突对象
   * @returns {Promise<Object>} - 解决结果
   * @private
   */
  async _resolveBySplitResources(conflict) {
    // 计算每个团队应得的份额
    const totalTeams = conflict.teams.length;
    const sharePerTeam = 1 / totalTeams;
    
    // 向每个团队发送份额通知
    for (const team of conflict.teams) {
      this.emit('team:notification', team.id, {
        type: 'resource:split',
        conflictId: conflict.id,
        resourceId: conflict.targetId,
        share: sharePerTeam,
        message: `资源已平分，你的团队获得了${Math.round(sharePerTeam * 100)}%的份额。`
      });
    }
    
    return {
      strategy: RESOLUTION_TYPE.SPLIT,
      noWinner: true, // 没有单一赢家
      shares: conflict.teams.map(team => ({
        teamId: team.id,
        share: sharePerTeam
      }))
    };
  }
  
  /**
   * 协作解决策略
   * @param {Object} conflict - 冲突对象
   * @returns {Promise<Object>} - 解决结果
   * @private
   */
  async _resolveByCollaboration(conflict) {
    // 向团队发送协作任务
    const collaborationId = uuidv4();
    
    for (const team of conflict.teams) {
      this.emit('team:notification', team.id, {
        type: 'collaboration:request',
        conflictId: conflict.id,
        collaborationId,
        message: '这个任务需要团队协作！请与其他团队一起完成任务。'
      });
    }
    
    // 模拟协作任务完成过程
    return new Promise((resolve) => {
      setTimeout(() => {
        // 所有团队都获得奖励
        resolve({
          strategy: RESOLUTION_TYPE.COLLABORATIVE,
          noWinner: true, // 没有单一赢家
          collaborationId,
          message: '通过协作，所有团队共同完成了任务并获得奖励！'
        });
      }, 30000); // 假设协作持续30秒
    });
  }
  
  /**
   * 随机分配解决策略
   * @param {Object} conflict - 冲突对象
   * @returns {Promise<Object>} - 解决结果
   * @private
   */
  async _resolveByRandom(conflict) {
    // 随机选择一个团队作为获胜者
    const randomTeam = conflict.teams[Math.floor(Math.random() * conflict.teams.length)];
    
    // 向团队发送结果通知
    for (const team of conflict.teams) {
      this.emit('team:notification', team.id, {
        type: 'conflict:resolution',
        conflictId: conflict.id,
        resolutionType: RESOLUTION_TYPE.RANDOM,
        isWinner: team.id === randomTeam.id,
        message: team.id === randomTeam.id 
          ? '恭喜！你的团队被随机选中，获得了资源。'
          : '很遗憾，另一个团队被随机选中了。'
      });
    }
    
    return {
      strategy: RESOLUTION_TYPE.RANDOM,
      winner: randomTeam
    };
  }
  
  /**
   * 路径重定向解决策略
   * @param {Object} conflict - 冲突对象
   * @returns {Promise<Object>} - 解决结果
   * @private
   */
  async _resolveByPathRedirection(conflict) {
    // 为团队计算替代路径
    const teamA = conflict.teams[0];
    const teamB = conflict.teams[1];
    
    // 模拟路径重定向过程
    const alternativePathA = { /* 替代路径数据 */ };
    const alternativePathB = { /* 替代路径数据 */ };
    
    // 向团队发送路径重定向通知
    this.emit('team:notification', teamA.id, {
      type: 'path:redirect',
      conflictId: conflict.id,
      alternativePath: alternativePathA,
      message: '检测到路径冲突，已提供替代路线。'
    });
    
    this.emit('team:notification', teamB.id, {
      type: 'path:redirect',
      conflictId: conflict.id,
      alternativePath: alternativePathB,
      message: '检测到路径冲突，已提供替代路线。'
    });
    
    return {
      strategy: RESOLUTION_TYPE.COLLABORATIVE,
      noWinner: true, // 没有单一赢家
      redirections: [
        { teamId: teamA.id, newPath: alternativePathA },
        { teamId: teamB.id, newPath: alternativePathB }
      ]
    };
  }
  
  /**
   * 获取活跃冲突列表
   * @returns {Array} - 活跃冲突列表
   */
  getActiveConflicts() {
    return Array.from(this.activeConflicts.values());
  }
  
  /**
   * 获取已解决冲突历史
   * @param {number} limit - 限制数量
   * @returns {Array} - 已解决冲突历史
   */
  getResolvedConflictHistory(limit = 100) {
    return this.resolvedConflicts.slice(-limit);
  }
  
  /**
   * 获取团队参与的冲突
   * @param {string} teamId - 团队ID
   * @returns {Array} - 团队参与的活跃冲突
   */
  getTeamConflicts(teamId) {
    return Array.from(this.activeConflicts.values())
      .filter(conflict => conflict.teams.some(team => team.id === teamId));
  }
}

module.exports = {
  ConflictResolutionService: new ConflictResolutionService(),
  CONFLICT_TYPE,
  CONFLICT_STATUS,
  RESOLUTION_TYPE
};