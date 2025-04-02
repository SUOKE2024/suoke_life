import { Router } from 'express';
import * as consumerController from '../controllers/consumer.controller';

export default function(): Router {
  const router = Router();
  
  router.post('/qrcode', consumerController.generateQRCode);
  router.get('/trace/:qrId', consumerController.getProductByQRCode);
  
  return router;
}