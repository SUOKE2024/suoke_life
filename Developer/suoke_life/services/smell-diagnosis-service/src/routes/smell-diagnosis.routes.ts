import { Router } from 'express';
import multer from 'multer';
import { SmellDiagnosisController } from '../controllers/smell-diagnosis.controller';

const router = Router();
const controller = new SmellDiagnosisController();

// 配置文件上传
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 10 * 1024 * 1024, // 限制10MB
  },
});

// 健康检查
router.get('/health', controller.healthCheck);

// 闻诊分析
router.post('/analyze', upload.single('audioData'), controller.analyze);

// 获取历史分析结果
router.get('/history/:userId', controller.getHistory);

// 获取诊断详情
router.get('/diagnosis/:id', controller.getDiagnosisById);

export default router; 