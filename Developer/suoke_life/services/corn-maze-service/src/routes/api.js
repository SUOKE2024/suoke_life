const express = require('express');
const router = express.Router();

// 控制器
const mazeController = require('../controllers/mazeController');
const teamController = require('../controllers/teamController');
const npcController = require('../controllers/npcController');

// 新增控制器
const recommendationController = require('../controllers/recommendationController');
const i18nController = require('../controllers/i18nController');
const offlineController = require('../controllers/offlineController');

// 中间件
const authMiddleware = require('../middlewares/authMiddleware');
const { i18nMiddleware } = require('../services/i18nService');

// 应用国际化中间件到所有路由
router.use(i18nMiddleware);

// 迷宫相关路由
router.get('/mazes', mazeController.getAllMazes);
router.get('/mazes/:id', mazeController.getMazeById);
router.post('/mazes', authMiddleware(['admin']), mazeController.createMaze);
router.put('/mazes/:id', authMiddleware(['admin']), mazeController.updateMaze);
router.delete('/mazes/:id', authMiddleware(['admin']), mazeController.deleteMaze);
router.get('/mazes/:id/stats', mazeController.getMazeStats);

// 团队相关路由
router.get('/teams', teamController.getAllTeams);
router.get('/teams/:id', teamController.getTeamById);
router.post('/teams', authMiddleware(), teamController.createTeam);
router.put('/teams/:id', authMiddleware(), teamController.updateTeam);
router.delete('/teams/:id', authMiddleware(['admin', 'leader']), teamController.deleteTeam);
router.post('/teams/:id/join', authMiddleware(), teamController.joinTeam);
router.post('/teams/:id/leave', authMiddleware(), teamController.leaveTeam);
router.post('/teams/:id/kick/:userId', authMiddleware(['admin', 'leader']), teamController.kickPlayer);

// NPC相关路由
router.get('/npcs', npcController.getAllNpcs);
router.get('/npcs/:id', npcController.getNpcById);
router.post('/npcs/:id/dialog', authMiddleware(), npcController.talkToNpc);

// 推荐系统路由
router.get('/recommendations/mazes', authMiddleware(), recommendationController.getRecommendedMazes);
router.get('/recommendations/teams', authMiddleware(), recommendationController.getRecommendedTeams);
router.get('/recommendations/teams/:mazeId', authMiddleware(), recommendationController.getRecommendedTeamsForMaze);
router.get('/recommendations/treasures/:mazeId', authMiddleware(), recommendationController.getRecommendedTreasures);
router.get('/user/history', authMiddleware(), recommendationController.getUserHistory);

// 国际化路由
router.get('/i18n/locales', i18nController.getSupportedLocales);
router.get('/i18n/translations/:locale', i18nController.getTranslations);
router.post('/i18n/locale', authMiddleware(), i18nController.setUserLocale);
router.post('/i18n/translations', authMiddleware(['admin']), i18nController.addTranslation);
router.post('/i18n/translations/bulk', authMiddleware(['admin']), i18nController.addBulkTranslations);

// 离线功能路由
router.get('/offline/package/:mazeId', authMiddleware(), offlineController.getOfflinePackage);
router.post('/offline/sync', authMiddleware(), offlineController.syncOfflineChanges);
router.get('/offline/sync/status', authMiddleware(), offlineController.getSyncStatus);
router.post('/offline/check-updates', authMiddleware(), offlineController.checkUpdates);

module.exports = router; 