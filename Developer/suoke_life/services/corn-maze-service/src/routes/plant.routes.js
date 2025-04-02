/**
 * 玉米植物路由
 */
const express = require('express');
const router = express.Router();

// 导入控制器
// 注意：此处仅为路由定义，控制器实现将在后续开发中完成
const plantController = {
  getAllPlants: (req, res) => {
    res.json({ message: '获取所有植物列表 - 待实现' });
  },
  getPlantById: (req, res) => {
    res.json({ message: `获取植物详情 ID: ${req.params.id} - 待实现` });
  },
  createPlant: (req, res) => {
    res.json({ message: '创建新植物 - 待实现' });
  },
  updatePlant: (req, res) => {
    res.json({ message: `更新植物 ID: ${req.params.id} - 待实现` });
  },
  deletePlant: (req, res) => {
    res.json({ message: `删除植物 ID: ${req.params.id} - 待实现` });
  },
  waterPlant: (req, res) => {
    res.json({ message: `给植物浇水 ID: ${req.params.id} - 待实现` });
  },
  fertilizePlant: (req, res) => {
    res.json({ message: `给植物施肥 ID: ${req.params.id} - 待实现` });
  },
  harvestPlant: (req, res) => {
    res.json({ message: `收获植物 ID: ${req.params.id} - 待实现` });
  },
  getPlantGrowthHistory: (req, res) => {
    res.json({ message: `获取植物生长历史 ID: ${req.params.id} - 待实现` });
  },
  getUserPlants: (req, res) => {
    res.json({ message: '获取用户的植物列表 - 待实现' });
  }
};

// 公共路由
router.get('/', plantController.getAllPlants);
router.get('/:id', plantController.getPlantById);
router.get('/:id/history', plantController.getPlantGrowthHistory);

// 需要身份验证的路由
router.post('/', plantController.createPlant);
router.put('/:id', plantController.updatePlant);
router.delete('/:id', plantController.deletePlant);
router.post('/:id/water', plantController.waterPlant);
router.post('/:id/fertilize', plantController.fertilizePlant);
router.post('/:id/harvest', plantController.harvestPlant);
router.get('/user/plants', plantController.getUserPlants);

module.exports = router;
