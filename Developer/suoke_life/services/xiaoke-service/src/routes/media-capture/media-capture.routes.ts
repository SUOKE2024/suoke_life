import { Router } from 'express';
import * as mediaCaptureController from '../../controllers/media-capture/media-capture.controller';

export default function(): Router {
  const router = Router();
  
  // 音频隐私设置相关路由
  router.get('/audio/privacy/:userId', mediaCaptureController.getAudioPrivacySettings);
  router.put('/audio/privacy/:userId', mediaCaptureController.updateAudioPrivacySettings);
  
  // 音频数据相关路由
  router.post('/audio/capture', mediaCaptureController.captureAudioData);
  router.get('/audio/history/:userId', mediaCaptureController.getUserAudioHistory);
  router.delete('/audio/:userId/:audioId', mediaCaptureController.deleteAudioData);
  
  // 视频隐私设置相关路由
  router.get('/video/privacy/:userId', mediaCaptureController.getVideoPrivacySettings);
  router.put('/video/privacy/:userId', mediaCaptureController.updateVideoPrivacySettings);
  
  // 视频数据相关路由
  router.post('/video/capture', mediaCaptureController.captureVideoData);
  router.get('/video/history/:userId', mediaCaptureController.getUserVideoHistory);
  router.delete('/video/:userId/:videoId', mediaCaptureController.deleteVideoData);
  
  return router;
}