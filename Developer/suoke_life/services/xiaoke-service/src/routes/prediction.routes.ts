import { Router } from 'express';
import * as predictionController from '../controllers/prediction.controller';

export default function(): Router {
  const router = Router();
  
  router.get('/risks/:productId', predictionController.predictRisks);
  
  return router;
}