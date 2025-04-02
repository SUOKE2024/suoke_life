import { Router } from 'express';
import * as dialectController from '../../controllers/dialect/dialect.controller';

export default function(): Router {
  const router = Router();
  
  // 方言信息相关路由
  router.get('/supported', dialectController.getSupportedDialects);
  
  // 用户方言偏好相关路由
  router.get('/preference/:userId', dialectController.getUserDialectPreference);
  router.put('/preference/:userId', dialectController.updateUserDialectPreference);
  router.get('/history/:userId', dialectController.getUserDialectHistory);
  
  // 方言识别相关路由
  router.post('/recognize', dialectController.recognizeDialect);
  router.post('/translate', dialectController.translateToMandarin);
  
  // 方言语音合成相关路由
  router.get('/voices', dialectController.getAllDialectVoices);
  router.get('/voices/:dialect', dialectController.getDialectVoices);
  router.post('/synthesize', dialectController.synthesizeDialectSpeech);
  router.get('/synthesis/history/:userId', dialectController.getUserSynthesisHistory);
  
  return router;
}