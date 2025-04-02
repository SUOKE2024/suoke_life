/**
 * 宝藏路由
 */
const express = require('express');
const router = express.Router();

// 导入控制器
// 注意：此处仅为路由定义，控制器实现将在后续开发中完成
const treasureController = {
  getAllTreasures: (req, res) => {
    res.json({ message: '获取所有宝藏列表 - 待实现' });
  },
  getTreasureById: (req, res) => {
    res.json({ message: `获取宝藏详情 ID: ${req.params.id} - 待实现` });
  },
  createTreasure: (req, res) => {
    res.json({ message: '创建新宝藏 - 待实现' });
  },
  updateTreasure: (req, res) => {
    res.json({ message: `更新宝藏 ID: ${req.params.id} - 待实现` });
  },
  deleteTreasure: (req, res) => {
    res.json({ message: `删除宝藏 ID: ${req.params.id} - 待实现` });
  },
  scanARMarker: (req, res) => {
    res.json({ message: `扫描AR标记 ID: ${req.params.markerId} - 待实现` });
  },
  collectTreasure: (req, res) => {
    res.json({ message: `收集宝藏 ID: ${req.params.id} - 待实现` });
  },
  getTreasureStats: (req, res) => {
    res.json({ message: '获取宝藏统计信息 - 待实现' });
  },
  getDiscoveredTreasures: (req, res) => {
    res.json({ message: '获取已发现宝藏列表 - 待实现' });
  }
};

// 公共路由
router.get('/', treasureController.getAllTreasures);
router.get('/stats', treasureController.getTreasureStats);
router.get('/:id', treasureController.getTreasureById);

// 需要身份验证的路由
router.post('/', treasureController.createTreasure);
router.put('/:id', treasureController.updateTreasure);
router.delete('/:id', treasureController.deleteTreasure);
router.post('/scan/:markerId', treasureController.scanARMarker);
router.post('/:id/collect', treasureController.collectTreasure);
router.get('/user/discovered', treasureController.getDiscoveredTreasures);

module.exports = router;
