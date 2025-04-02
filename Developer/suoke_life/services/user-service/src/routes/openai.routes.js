/**
 * OpenAI兼容API路由
 */
const express = require('express');
const router = express.Router();
const { openaiController } = require('../controllers');
const { authMiddleware } = require('../middlewares');

// Assistants API
router.get('/assistants', authMiddleware.authenticate, openaiController.listAssistants);
router.post('/assistants', authMiddleware.authenticate, openaiController.createAssistant);
router.get('/assistants/:assistant_id', authMiddleware.authenticate, openaiController.getAssistant);
router.post('/assistants/:assistant_id', authMiddleware.authenticate, openaiController.updateAssistant);
router.delete('/assistants/:assistant_id', authMiddleware.authenticate, openaiController.deleteAssistant);

// Threads API
router.post('/threads', authMiddleware.authenticate, openaiController.createThread);
router.get('/threads/:thread_id', authMiddleware.authenticate, openaiController.getThread);
router.post('/threads/:thread_id', authMiddleware.authenticate, openaiController.updateThread);
router.delete('/threads/:thread_id', authMiddleware.authenticate, openaiController.deleteThread);

// Messages API
router.get('/threads/:thread_id/messages', authMiddleware.authenticate, openaiController.listMessages);
router.post('/threads/:thread_id/messages', authMiddleware.authenticate, openaiController.createMessage);
router.get('/threads/:thread_id/messages/:message_id', authMiddleware.authenticate, openaiController.getMessage);
router.post('/threads/:thread_id/messages/:message_id', authMiddleware.authenticate, openaiController.updateMessage);

// Runs API
router.post('/threads/:thread_id/runs', authMiddleware.authenticate, openaiController.createRun);
router.get('/threads/:thread_id/runs/:run_id', authMiddleware.authenticate, openaiController.getRun);
router.post('/threads/:thread_id/runs/:run_id', authMiddleware.authenticate, openaiController.updateRun);
router.post('/threads/:thread_id/runs/:run_id/cancel', authMiddleware.authenticate, openaiController.cancelRun);
router.get('/threads/:thread_id/runs', authMiddleware.authenticate, openaiController.listRuns);
router.post('/threads/:thread_id/runs/:run_id/submit_tool_outputs', authMiddleware.authenticate, openaiController.submitToolOutputs);

// Tools API
router.get('/tools', authMiddleware.authenticate, openaiController.listTools);
router.post('/tools/function', authMiddleware.authenticate, openaiController.executeFunction);

module.exports = router; 