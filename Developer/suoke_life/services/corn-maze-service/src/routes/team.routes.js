/**
 * 团队路由
 */
const express = require('express');
const router = express.Router();

// 导入控制器
// 注意：此处仅为路由定义，控制器实现将在后续开发中完成
const teamController = {
  getAllTeams: (req, res) => {
    res.json({ message: '获取所有团队列表 - 待实现' });
  },
  getTeamById: (req, res) => {
    res.json({ message: `获取团队详情 ID: ${req.params.id} - 待实现` });
  },
  createTeam: (req, res) => {
    res.json({ message: '创建新团队 - 待实现' });
  },
  updateTeam: (req, res) => {
    res.json({ message: `更新团队 ID: ${req.params.id} - 待实现` });
  },
  deleteTeam: (req, res) => {
    res.json({ message: `删除团队 ID: ${req.params.id} - 待实现` });
  },
  addTeamMember: (req, res) => {
    res.json({ message: `添加团队成员到团队 ID: ${req.params.id} - 待实现` });
  },
  removeTeamMember: (req, res) => {
    res.json({ message: `从团队 ID: ${req.params.id} 移除成员 ID: ${req.params.memberId} - 待实现` });
  },
  changeTeamLeader: (req, res) => {
    res.json({ message: `更改团队 ID: ${req.params.id} 的领导者 - 待实现` });
  },
  getTeamMembers: (req, res) => {
    res.json({ message: `获取团队 ID: ${req.params.id} 的成员列表 - 待实现` });
  },
  getTeamAchievements: (req, res) => {
    res.json({ message: `获取团队 ID: ${req.params.id} 的成就列表 - 待实现` });
  },
  getTeamLeaderboard: (req, res) => {
    res.json({ message: '获取团队排行榜 - 待实现' });
  },
  startMaze: (req, res) => {
    res.json({ message: `团队 ID: ${req.params.id} 开始迷宫 ID: ${req.params.mazeId} - 待实现` });
  },
  completeMaze: (req, res) => {
    res.json({ message: `团队 ID: ${req.params.id} 完成迷宫 ID: ${req.params.mazeId} - 待实现` });
  },
  getUserTeams: (req, res) => {
    res.json({ message: '获取当前用户的团队列表 - 待实现' });
  }
};

// 公共路由
router.get('/', teamController.getAllTeams);
router.get('/leaderboard', teamController.getTeamLeaderboard);
router.get('/:id', teamController.getTeamById);
router.get('/:id/members', teamController.getTeamMembers);
router.get('/:id/achievements', teamController.getTeamAchievements);

// 需要身份验证的路由
router.post('/', teamController.createTeam);
router.put('/:id', teamController.updateTeam);
router.delete('/:id', teamController.deleteTeam);
router.post('/:id/members', teamController.addTeamMember);
router.delete('/:id/members/:memberId', teamController.removeTeamMember);
router.put('/:id/leader', teamController.changeTeamLeader);
router.post('/:id/mazes/:mazeId/start', teamController.startMaze);
router.post('/:id/mazes/:mazeId/complete', teamController.completeMaze);
router.get('/user/teams', teamController.getUserTeams);

module.exports = router;
