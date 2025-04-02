import { Router } from 'express';
import * as iotController from '../controllers/iot.controller';

export default function(): Router {
  const router = Router();
  
  router.post('/sensor-data', iotController.receiveSensorDataAPI);
  router.get('/environment/:productId', iotController.getEnvironmentData);
  
  return router;
}