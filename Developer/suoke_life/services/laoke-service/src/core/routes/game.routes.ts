import express from 'express';
import * as gameController from '../../services/game/game.controller';
import { authenticate } from '../middleware/auth';
import { validateRequest } from '../middleware/validation';
import { questStepSchema } from '../validation/game.schema';

const router = express.Router();

// 获取任务列表
router.get('/quests', gameController.getQuestList);

// 获取任务详情
router.get('/quests/:id', gameController.getQuestById);

// 接受任务
router.post('/quests/:id/accept', authenticate, gameController.acceptQuest);

// 更新任务步骤
router.post('/quests/:id/steps/:stepIndex', authenticate, validateRequest(questStepSchema), gameController.updateQuestStep);

// 完成任务
router.post('/quests/:id/complete', authenticate, gameController.completeQuest);

// 获取用户进度
router.get('/progress', authenticate, gameController.getUserProgress);

export default router; 