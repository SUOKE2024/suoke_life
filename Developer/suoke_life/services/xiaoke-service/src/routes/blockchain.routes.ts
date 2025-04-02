import { Router } from 'express';
import * as blockchainController from '../controllers/blockchain.controller';

export default function(): Router {
  const router = Router();
  
  router.get('/verify/:eventId', blockchainController.verifyEvent);
  router.get('/proof/:productId', blockchainController.getBlockchainProof);
  router.post('/save', blockchainController.saveToBlockchain);
  
  return router;
}