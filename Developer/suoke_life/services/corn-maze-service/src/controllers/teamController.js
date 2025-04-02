const TeamService = require('../services/teamService');
const { handleError } = require('../utils/errorHandler');

/**
 * 团队控制器
 * 实现玉米迷宫团队管理功能
 */
class TeamController {
  /**
   * 创建新团队
   */
  async createTeam(req, res) {
    try {
      const { name, creatorId, description, maxMembers, seasonId } = req.body;
      
      if (!name || !creatorId || !seasonId) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数'
        });
      }
      
      const teamService = new TeamService();
      const newTeam = await teamService.createTeam({
        name,
        description,
        creatorId,
        maxMembers: maxMembers || 5,
        seasonId,
        isPrivate: req.body.isPrivate || false
      });
      
      return res.status(201).json({
        success: true,
        data: newTeam,
        message: '团队创建成功'
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 获取所有团队
   */
  async getAllTeams(req, res) {
    try {
      const filters = {};
      
      // 应用过滤条件
      if (req.query.seasonId) filters.seasonId = req.query.seasonId;
      if (req.query.isActive !== undefined) filters.isActive = req.query.isActive === 'true';
      if (req.query.isPrivate !== undefined) filters.isPrivate = req.query.isPrivate === 'true';
      
      const teamService = new TeamService();
      const teams = await teamService.getTeams(filters);
      
      return res.status(200).json({
        success: true,
        count: teams.length,
        data: teams
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 获取单个团队
   */
  async getTeamById(req, res) {
    try {
      const { id } = req.params;
      const teamService = new TeamService();
      const team = await teamService.getTeamById(id);
      
      if (!team) {
        return res.status(404).json({
          success: false,
          message: '未找到指定团队'
        });
      }
      
      return res.status(200).json({
        success: true,
        data: team
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 更新团队信息
   */
  async updateTeam(req, res) {
    try {
      const { id } = req.params;
      const teamService = new TeamService();
      const team = await teamService.updateTeam(id, req.body);
      
      if (!team) {
        return res.status(404).json({
          success: false,
          message: '未找到指定团队'
        });
      }
      
      return res.status(200).json({
        success: true,
        data: team,
        message: '团队更新成功'
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 解散团队
   */
  async disbandTeam(req, res) {
    try {
      const { id } = req.params;
      const { userId } = req.body;
      
      if (!userId) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数: userId'
        });
      }
      
      const teamService = new TeamService();
      const result = await teamService.disbandTeam(id, userId);
      
      if (!result.success) {
        return res.status(result.code || 400).json({
          success: false,
          message: result.message
        });
      }
      
      return res.status(200).json({
        success: true,
        message: '团队已解散'
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 添加团队成员
   */
  async addTeamMember(req, res) {
    try {
      const { id } = req.params;
      const { userId, role } = req.body;
      
      if (!userId) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数: userId'
        });
      }
      
      const teamService = new TeamService();
      const result = await teamService.addMember(id, userId, role || 'member');
      
      if (!result.success) {
        return res.status(result.code || 400).json({
          success: false,
          message: result.message
        });
      }
      
      return res.status(200).json({
        success: true,
        data: result.team,
        message: '成员添加成功'
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 移除团队成员
   */
  async removeTeamMember(req, res) {
    try {
      const { id, memberId } = req.params;
      const { requesterId } = req.body;
      
      if (!requesterId) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数: requesterId'
        });
      }
      
      const teamService = new TeamService();
      const result = await teamService.removeMember(id, memberId, requesterId);
      
      if (!result.success) {
        return res.status(result.code || 400).json({
          success: false,
          message: result.message
        });
      }
      
      return res.status(200).json({
        success: true,
        data: result.team,
        message: '成员移除成功'
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 更改成员角色
   */
  async changeTeamMemberRole(req, res) {
    try {
      const { id, memberId } = req.params;
      const { requesterId, newRole } = req.body;
      
      if (!requesterId || !newRole) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数: requesterId 或 newRole'
        });
      }
      
      const teamService = new TeamService();
      const result = await teamService.changeMemberRole(id, memberId, requesterId, newRole);
      
      if (!result.success) {
        return res.status(result.code || 400).json({
          success: false,
          message: result.message
        });
      }
      
      return res.status(200).json({
        success: true,
        data: result.team,
        message: '角色更改成功'
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 发送入队邀请
   */
  async sendInvitation(req, res) {
    try {
      const { id } = req.params;
      const { inviterId, inviteeId, message } = req.body;
      
      if (!inviterId || !inviteeId) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数: inviterId 或 inviteeId'
        });
      }
      
      const teamService = new TeamService();
      const result = await teamService.sendInvitation(id, inviterId, inviteeId, message);
      
      if (!result.success) {
        return res.status(result.code || 400).json({
          success: false,
          message: result.message
        });
      }
      
      return res.status(200).json({
        success: true,
        data: result.invitation,
        message: '邀请发送成功'
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 获取用户的团队列表
   */
  async getUserTeams(req, res) {
    try {
      const { userId } = req.params;
      
      if (!userId) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数: userId'
        });
      }
      
      const teamService = new TeamService();
      const teams = await teamService.getUserTeams(userId);
      
      return res.status(200).json({
        success: true,
        count: teams.length,
        data: teams
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 获取团队进度
   */
  async getTeamProgress(req, res) {
    try {
      const { id } = req.params;
      
      const teamService = new TeamService();
      const result = await teamService.getTeamProgress(id);
      
      if (!result.success) {
        return res.status(result.code || 404).json({
          success: false,
          message: result.message
        });
      }
      
      return res.status(200).json({
        success: true,
        data: result.progress
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
}

module.exports = new TeamController();
