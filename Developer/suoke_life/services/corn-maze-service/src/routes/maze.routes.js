/**
 * 迷宫路由
 */
const express = require('express');
const router = express.Router();

// 导入控制器
// 注意：此处仅为路由定义，控制器实现将在后续开发中完成
const mazeController = {
  getAllMazes: (req, res) => {
    res.json({ message: '获取所有迷宫列表 - 待实现' });
  },
  getMazeById: (req, res) => {
    res.json({ message: `获取迷宫详情 ID: ${req.params.id} - 待实现` });
  },
  createMaze: (req, res) => {
    res.json({ message: '创建新迷宫 - 待实现' });
  },
  updateMaze: (req, res) => {
    res.json({ message: `更新迷宫 ID: ${req.params.id} - 待实现` });
  },
  deleteMaze: (req, res) => {
    res.json({ message: `删除迷宫 ID: ${req.params.id} - 待实现` });
  },
  generateMaze: (req, res) => {
    res.json({ message: '自动生成迷宫 - 待实现' });
  },
  getMazeTreasures: (req, res) => {
    res.json({ message: `获取迷宫宝藏列表 ID: ${req.params.id} - 待实现` });
  },
  addTreasureToMaze: (req, res) => {
    res.json({ 
      message: `向迷宫 ID: ${req.params.id} 添加宝藏 - 待实现` 
    });
  },
  getMazeLeaderboard: (req, res) => {
    res.json({ message: `获取迷宫排行榜 ID: ${req.params.id} - 待实现` });
  }
};

// 公共路由
router.get('/', mazeController.getAllMazes);
router.get('/:id', mazeController.getMazeById);
router.get('/:id/treasures', mazeController.getMazeTreasures);
router.get('/:id/leaderboard', mazeController.getMazeLeaderboard);

// 需要身份验证的路由
router.post('/', mazeController.createMaze);
router.put('/:id', mazeController.updateMaze);
router.delete('/:id', mazeController.deleteMaze);
router.post('/generate', mazeController.generateMaze);
router.post('/:id/treasures', mazeController.addTreasureToMaze);

module.exports = router;
