const Team = require('../models/team.model');
const { AppError } = require('../utils/errorHandler');
const NotificationService = require('./notificationService');
const MazeService = require('./mazeService');

/**
 * 团队服务类
 * 实现玉米迷宫团队相关的所有业务逻辑
 */
class TeamService {
  constructor() {
    this.notificationService = new NotificationService();
    this.mazeService = new MazeService();
  }

  /**
   * 创建新团队
   * @param {Object} teamData - 团队数据
   * @returns {Object} 创建的团队
   */
  async createTeam(teamData) {
    try {
      // 验证用户是否已有团队
      const existingTeam = await Team.findOne({
        'members.userId': teamData.creatorId,
        seasonId: teamData.seasonId,
        isActive: true
      });

      if (existingTeam) {
        throw new AppError('用户在当前赛季已有团队', 'CONFLICT', 409);
      }

      // 创建新团队
      const newTeam = new Team({
        name: teamData.name,
        description: teamData.description || `${teamData.name}的玉米迷宫冒险团队`,
        seasonId: teamData.seasonId,
        members: [{
          userId: teamData.creatorId,
          role: 'leader',
          joinedAt: new Date()
        }],
        maxMembers: teamData.maxMembers || 5,
        isPrivate: teamData.isPrivate || false,
        createdBy: teamData.creatorId
      });

      await newTeam.save();

      // 创建团队迷宫
      await this.mazeService.createTeamMaze(newTeam._id, teamData.seasonId);

      return newTeam;
    } catch (error) {
      throw error;
    }
  }

  /**
   * 获取团队列表
   * @param {Object} filters - 过滤条件
   * @returns {Array} 团队列表
   */
  async getTeams(filters = {}) {
    try {
      const query = { ...filters };
      
      // 默认只显示活跃团队
      if (query.isActive === undefined) {
        query.isActive = true;
      }
      
      return await Team.find(query)
        .sort({ createdAt: -1 })
        .populate('members.userId', 'username avatar level')
        .select('-invitations');
    } catch (error) {
      throw error;
    }
  }

  /**
   * 获取单个团队
   * @param {String} id - 团队ID
   * @returns {Object} 团队
   */
  async getTeamById(id) {
    try {
      return await Team.findById(id)
        .populate('members.userId', 'username avatar level')
        .populate('achievements');
    } catch (error) {
      throw error;
    }
  }

  /**
   * 更新团队
   * @param {String} id - 团队ID
   * @param {Object} updateData - 更新数据
   * @returns {Object} 更新后的团队
   */
  async updateTeam(id, updateData) {
    try {
      // 不允许直接更新的字段
      const protectedFields = ['_id', 'createdBy', 'seasonId', 'createdAt', 'members', 'achievements', 'progress'];
      
      // 过滤掉受保护的字段
      const filteredData = Object.keys(updateData)
        .filter(key => !protectedFields.includes(key))
        .reduce((obj, key) => {
          obj[key] = updateData[key];
          return obj;
        }, {});
      
      // 添加更新时间
      filteredData.updatedAt = new Date();
      
      return await Team.findByIdAndUpdate(
        id,
        { $set: filteredData },
        { new: true, runValidators: true }
      ).populate('members.userId', 'username avatar level');
    } catch (error) {
      throw error;
    }
  }

  /**
   * 解散团队
   * @param {String} id - 团队ID
   * @param {String} userId - 请求用户ID
   * @returns {Object} 结果
   */
  async disbandTeam(id, userId) {
    try {
      const team = await Team.findById(id);
      
      if (!team) {
        return { success: false, message: '未找到指定团队', code: 404 };
      }
      
      // 检查权限
      const isLeader = team.members.some(m => m.userId.toString() === userId && m.role === 'leader');
      
      if (!isLeader) {
        return { success: false, message: '只有团队领导者可以解散团队', code: 403 };
      }
      
      // 发送通知给所有成员
      for (const member of team.members) {
        if (member.userId.toString() !== userId) {
          await this.notificationService.sendNotification({
            userId: member.userId,
            type: 'team_disbanded',
            title: '团队已解散',
            message: `您所在的团队"${team.name}"已被解散`,
            data: { teamId: team._id, teamName: team.name }
          });
        }
      }
      
      // 解散团队
      await Team.findByIdAndUpdate(id, {
        isActive: false,
        disbandedAt: new Date(),
        disbandedBy: userId
      });
      
      return { success: true };
    } catch (error) {
      throw error;
    }
  }

  /**
   * 添加团队成员
   * @param {String} teamId - 团队ID
   * @param {String} userId - 用户ID
   * @param {String} role - 角色
   * @returns {Object} 结果
   */
  async addMember(teamId, userId, role = 'member') {
    try {
      const team = await Team.findById(teamId);
      
      if (!team) {
        return { success: false, message: '未找到指定团队', code: 404 };
      }
      
      if (!team.isActive) {
        return { success: false, message: '该团队已被解散', code: 400 };
      }
      
      // 检查是否已是成员
      const isAlreadyMember = team.members.some(m => m.userId.toString() === userId);
      
      if (isAlreadyMember) {
        return { success: false, message: '用户已是团队成员', code: 400 };
      }
      
      // 检查是否已达到最大成员数
      if (team.members.length >= team.maxMembers) {
        return { success: false, message: '团队已达到最大成员数', code: 400 };
      }
      
      // 检查用户是否已有团队
      const existingTeam = await Team.findOne({
        'members.userId': userId,
        seasonId: team.seasonId,
        isActive: true,
        _id: { $ne: teamId }
      });
      
      if (existingTeam) {
        return { success: false, message: '用户已加入其他团队', code: 409 };
      }
      
      // 添加新成员
      team.members.push({
        userId,
        role: role || 'member',
        joinedAt: new Date()
      });
      
      // 添加活动记录
      team.activities.push({
        type: 'member_joined',
        userId,
        timestamp: new Date(),
        details: { role }
      });
      
      await team.save();
      
      // 发送通知给团队成员
      for (const member of team.members) {
        if (member.userId.toString() !== userId) {
          await this.notificationService.sendNotification({
            userId: member.userId,
            type: 'new_team_member',
            title: '新成员加入',
            message: `新成员已加入团队"${team.name}"`,
            data: { teamId: team._id, teamName: team.name, newMemberId: userId }
          });
        }
      }
      
      // 发送欢迎通知给新成员
      await this.notificationService.sendNotification({
        userId,
        type: 'team_welcome',
        title: '欢迎加入团队',
        message: `欢迎加入"${team.name}"团队`,
        data: { teamId: team._id, teamName: team.name }
      });
      
      return { success: true, team };
    } catch (error) {
      throw error;
    }
  }

  /**
   * 移除团队成员
   * @param {String} teamId - 团队ID
   * @param {String} memberId - 成员ID
   * @param {String} requesterId - 请求用户ID
   * @returns {Object} 结果
   */
  async removeMember(teamId, memberId, requesterId) {
    try {
      const team = await Team.findById(teamId);
      
      if (!team) {
        return { success: false, message: '未找到指定团队', code: 404 };
      }
      
      if (!team.isActive) {
        return { success: false, message: '该团队已被解散', code: 400 };
      }
      
      // 检查被移除成员是否存在
      const memberIndex = team.members.findIndex(m => m.userId.toString() === memberId);
      
      if (memberIndex === -1) {
        return { success: false, message: '成员不存在', code: 404 };
      }
      
      // 检查权限
      const requesterMember = team.members.find(m => m.userId.toString() === requesterId);
      
      if (!requesterMember) {
        return { success: false, message: '请求者不是团队成员', code: 403 };
      }
      
      // 只有自己或领导者可以移除成员
      const isSelf = memberId === requesterId;
      const isLeader = requesterMember.role === 'leader';
      
      if (!isSelf && !isLeader) {
        return { success: false, message: '没有权限移除成员', code: 403 };
      }
      
      // 如果是领导者要离开，必须先转让领导权
      if (isSelf && requesterMember.role === 'leader' && team.members.length > 1) {
        return { success: false, message: '领导者离开前必须先转让领导权', code: 400 };
      }
      
      // 记录被移除的成员信息
      const removedMember = team.members[memberIndex];
      
      // 移除成员
      team.members.splice(memberIndex, 1);
      
      // 添加活动记录
      team.activities.push({
        type: isSelf ? 'member_left' : 'member_removed',
        userId: requesterId,
        timestamp: new Date(),
        details: { 
          removedMemberId: memberId,
          reason: isSelf ? '主动离开' : '被管理员移除'
        }
      });
      
      await team.save();
      
      // 发送通知
      if (!isSelf) {
        // 发送通知给被移除成员
        await this.notificationService.sendNotification({
          userId: memberId,
          type: 'removed_from_team',
          title: '您已被移出团队',
          message: `您已被移出"${team.name}"团队`,
          data: { teamId: team._id, teamName: team.name }
        });
      }
      
      // 发送通知给其他团队成员
      for (const member of team.members) {
        if (member.userId.toString() !== requesterId) {
          await this.notificationService.sendNotification({
            userId: member.userId,
            type: 'member_left_team',
            title: '团队成员离开',
            message: `一名成员已${isSelf ? '离开' : '被移出'}"${team.name}"团队`,
            data: { teamId: team._id, teamName: team.name, memberId }
          });
        }
      }
      
      return { success: true, team };
    } catch (error) {
      throw error;
    }
  }

  /**
   * 更改成员角色
   * @param {String} teamId - 团队ID
   * @param {String} memberId - 成员ID
   * @param {String} requesterId - 请求用户ID
   * @param {String} newRole - 新角色
   * @returns {Object} 结果
   */
  async changeMemberRole(teamId, memberId, requesterId, newRole) {
    try {
      const team = await Team.findById(teamId);
      
      if (!team) {
        return { success: false, message: '未找到指定团队', code: 404 };
      }
      
      if (!team.isActive) {
        return { success: false, message: '该团队已被解散', code: 400 };
      }
      
      // 检查成员是否存在
      const memberIndex = team.members.findIndex(m => m.userId.toString() === memberId);
      
      if (memberIndex === -1) {
        return { success: false, message: '成员不存在', code: 404 };
      }
      
      // 检查请求者权限
      const requesterIndex = team.members.findIndex(m => m.userId.toString() === requesterId);
      
      if (requesterIndex === -1) {
        return { success: false, message: '请求者不是团队成员', code: 403 };
      }
      
      const isRequesterLeader = team.members[requesterIndex].role === 'leader';
      
      if (!isRequesterLeader) {
        return { success: false, message: '只有领导者可以更改角色', code: 403 };
      }
      
      // 验证角色
      const validRoles = ['leader', 'admin', 'member'];
      
      if (!validRoles.includes(newRole)) {
        return { success: false, message: '无效的角色', code: 400 };
      }
      
      // 如果转让领导权
      if (newRole === 'leader') {
        // 当前领导者降级为管理员
        team.members[requesterIndex].role = 'admin';
      }
      
      // 更新成员角色
      team.members[memberIndex].role = newRole;
      
      // 添加活动记录
      team.activities.push({
        type: 'role_changed',
        userId: requesterId,
        timestamp: new Date(),
        details: { 
          targetMemberId: memberId,
          oldRole: team.members[memberIndex].role,
          newRole
        }
      });
      
      await team.save();
      
      // 发送通知给被更改角色的成员
      await this.notificationService.sendNotification({
        userId: memberId,
        type: 'role_changed',
        title: '您的团队角色已更改',
        message: `您在"${team.name}"团队中的角色已变更为${this.getRoleDisplayName(newRole)}`,
        data: { teamId: team._id, teamName: team.name, newRole }
      });
      
      return { success: true, team };
    } catch (error) {
      throw error;
    }
  }

  /**
   * 发送入队邀请
   * @param {String} teamId - 团队ID
   * @param {String} inviterId - 邀请人ID
   * @param {String} inviteeId - 被邀请人ID
   * @param {String} message - 邀请消息
   * @returns {Object} 结果
   */
  async sendInvitation(teamId, inviterId, inviteeId, message = '') {
    try {
      const team = await Team.findById(teamId);
      
      if (!team) {
        return { success: false, message: '未找到指定团队', code: 404 };
      }
      
      if (!team.isActive) {
        return { success: false, message: '该团队已被解散', code: 400 };
      }
      
      // 检查是否已是成员
      const isAlreadyMember = team.members.some(m => m.userId.toString() === inviteeId);
      
      if (isAlreadyMember) {
        return { success: false, message: '用户已是团队成员', code: 400 };
      }
      
      // 检查邀请者权限
      const inviter = team.members.find(m => m.userId.toString() === inviterId);
      
      if (!inviter) {
        return { success: false, message: '邀请者不是团队成员', code: 403 };
      }
      
      const canInvite = ['leader', 'admin'].includes(inviter.role);
      
      if (!canInvite) {
        return { success: false, message: '没有邀请权限', code: 403 };
      }
      
      // 检查是否已达到最大成员数
      if (team.members.length >= team.maxMembers) {
        return { success: false, message: '团队已达到最大成员数', code: 400 };
      }
      
      // 检查是否已有待处理邀请
      const existingInvitation = team.invitations.find(
        inv => inv.inviteeId.toString() === inviteeId && inv.status === 'pending'
      );
      
      if (existingInvitation) {
        return { success: false, message: '已有待处理的邀请', code: 400 };
      }
      
      // 创建邀请
      const invitation = {
        inviterId,
        inviteeId,
        message: message || `邀请您加入"${team.name}"团队`,
        createdAt: new Date(),
        status: 'pending'
      };
      
      team.invitations.push(invitation);
      await team.save();
      
      // 发送通知给被邀请者
      await this.notificationService.sendNotification({
        userId: inviteeId,
        type: 'team_invitation',
        title: '团队邀请',
        message: `您收到来自"${team.name}"团队的邀请`,
        data: { 
          teamId: team._id, 
          teamName: team.name, 
          inviterId,
          invitationId: invitation._id
        },
        actions: [
          { label: '接受', value: 'accept' },
          { label: '拒绝', value: 'decline' }
        ]
      });
      
      return { 
        success: true, 
        invitation,
        message: '邀请已发送'
      };
    } catch (error) {
      throw error;
    }
  }

  /**
   * 获取用户的团队
   * @param {String} userId - 用户ID
   * @returns {Array} 团队列表
   */
  async getUserTeams(userId) {
    try {
      return await Team.find({
        'members.userId': userId,
        isActive: true
      })
      .populate('members.userId', 'username avatar level')
      .sort({ updatedAt: -1 });
    } catch (error) {
      throw error;
    }
  }

  /**
   * 获取团队进度
   * @param {String} teamId - 团队ID
   * @returns {Object} 团队进度
   */
  async getTeamProgress(teamId) {
    try {
      const team = await Team.findById(teamId);
      
      if (!team) {
        return { success: false, message: '未找到指定团队', code: 404 };
      }
      
      // 获取团队迷宫进度
      const mazeProgress = await this.mazeService.getTeamMazeProgress(teamId);
      
      if (!mazeProgress.success) {
        return { success: false, message: mazeProgress.message, code: mazeProgress.code || 404 };
      }
      
      // 获取团队成就
      const achievements = team.achievements || [];
      
      // 计算团队状态
      const memberCount = team.members.length;
      const maxMembers = team.maxMembers;
      const completionRate = mazeProgress.data ? mazeProgress.data.completionRate : 0;
      const treasuresFound = mazeProgress.data ? mazeProgress.data.treasuresFound : 0;
      const totalTreasures = mazeProgress.data ? mazeProgress.data.totalTreasures : 0;
      
      const progress = {
        teamId: team._id,
        teamName: team.name,
        seasonId: team.seasonId,
        memberCount,
        maxMembers,
        mazeProgress: mazeProgress.data,
        completionRate,
        treasuresFound,
        totalTreasures,
        achievements: achievements.map(a => ({
          id: a._id,
          name: a.name,
          description: a.description,
          earnedAt: a.earnedAt
        })),
        activities: team.activities.slice(-10).reverse()
      };
      
      return { success: true, progress };
    } catch (error) {
      throw error;
    }
  }
  
  /**
   * 获取角色显示名称
   * @param {String} role - 角色代码
   * @returns {String} 角色显示名称
   */
  getRoleDisplayName(role) {
    const roleMap = {
      'leader': '队长',
      'admin': '管理员',
      'member': '队员'
    };
    
    return roleMap[role] || '队员';
  }
}

module.exports = TeamService;
