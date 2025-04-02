import express from 'express';
import knowledgeRoutes from './knowledge.routes';
import trainingRoutes from './training.routes';
import blogRoutes from './blog.routes';
import gameRoutes from './game.routes';
import accessibilityRoutes from './accessibility.routes';
import voiceRoutes from './voice.routes';
import mediaRoutes from './media.routes';
import dialectRoutes from './dialect.routes';
import voiceGuidanceRoutes from './voice-guidance.routes';

const router = express.Router();

// 健康检查路由
router.get('/health', (req, res) => {
  res.status(200).json({
    status: 'ok',
    service: 'laoke-service',
    version: process.env.SERVICE_VERSION || '1.0.0',
    timestamp: new Date().toISOString()
  });
});

// 特性路由
router.use('/knowledge', knowledgeRoutes);
router.use('/training', trainingRoutes);
router.use('/blogs', blogRoutes);
router.use('/game', gameRoutes);
router.use('/accessibility', accessibilityRoutes);
router.use('/voice', voiceRoutes);
router.use('/media', mediaRoutes);
router.use('/dialects', dialectRoutes);
router.use('/voice-guidance', voiceGuidanceRoutes);

export default router; 