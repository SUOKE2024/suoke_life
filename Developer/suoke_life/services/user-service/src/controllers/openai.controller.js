/**
 * OpenAI兼容API控制器
 */
const { openaiService } = require('../services');
const { logger } = require('@suoke/shared').utils;

/**
 * Assistants API
 */
// 获取助手列表
exports.listAssistants = async (req, res) => {
  try {
    const { limit = 20, order = 'desc', after, before } = req.query;
    const result = await openaiService.listAssistants(req.user.id, { limit, order, after, before });
    res.status(200).json(result);
  } catch (error) {
    logger.error('获取助手列表失败', { error: error.message, stack: error.stack });
    res.status(500).json({
      object: 'error',
      message: error.message,
      type: 'server_error',
      param: null,
      code: 'internal_server_error'
    });
  }
};

// 创建助手
exports.createAssistant = async (req, res) => {
  try {
    const assistantData = req.body;
    assistantData.user_id = req.user.id;
    const result = await openaiService.createAssistant(assistantData);
    res.status(201).json(result);
  } catch (error) {
    logger.error('创建助手失败', { error: error.message, stack: error.stack });
    res.status(500).json({
      object: 'error',
      message: error.message,
      type: 'server_error',
      param: null,
      code: 'internal_server_error'
    });
  }
};

// 获取助手详情
exports.getAssistant = async (req, res) => {
  try {
    const { assistant_id } = req.params;
    const result = await openaiService.getAssistant(assistant_id, req.user.id);
    if (!result) {
      return res.status(404).json({
        object: 'error',
        message: '助手不存在',
        type: 'not_found_error',
        param: 'assistant_id',
        code: 'assistant_not_found'
      });
    }
    res.status(200).json(result);
  } catch (error) {
    logger.error('获取助手详情失败', { error: error.message, stack: error.stack, assistant_id: req.params.assistant_id });
    res.status(500).json({
      object: 'error',
      message: error.message,
      type: 'server_error',
      param: null,
      code: 'internal_server_error'
    });
  }
};

// 更新助手
exports.updateAssistant = async (req, res) => {
  try {
    const { assistant_id } = req.params;
    const updateData = req.body;
    const result = await openaiService.updateAssistant(assistant_id, updateData, req.user.id);
    if (!result) {
      return res.status(404).json({
        object: 'error',
        message: '助手不存在',
        type: 'not_found_error',
        param: 'assistant_id',
        code: 'assistant_not_found'
      });
    }
    res.status(200).json(result);
  } catch (error) {
    logger.error('更新助手失败', { error: error.message, stack: error.stack, assistant_id: req.params.assistant_id });
    res.status(500).json({
      object: 'error',
      message: error.message,
      type: 'server_error',
      param: null,
      code: 'internal_server_error'
    });
  }
};

// 删除助手
exports.deleteAssistant = async (req, res) => {
  try {
    const { assistant_id } = req.params;
    const result = await openaiService.deleteAssistant(assistant_id, req.user.id);
    if (!result) {
      return res.status(404).json({
        object: 'error',
        message: '助手不存在',
        type: 'not_found_error',
        param: 'assistant_id',
        code: 'assistant_not_found'
      });
    }
    res.status(200).json({
      id: assistant_id,
      object: 'assistant.deleted',
      deleted: true
    });
  } catch (error) {
    logger.error('删除助手失败', { error: error.message, stack: error.stack, assistant_id: req.params.assistant_id });
    res.status(500).json({
      object: 'error',
      message: error.message,
      type: 'server_error',
      param: null,
      code: 'internal_server_error'
    });
  }
};

/**
 * Threads API
 */
// 创建会话
exports.createThread = async (req, res) => {
  try {
    const threadData = req.body || {};
    threadData.user_id = req.user.id;
    const result = await openaiService.createThread(threadData);
    res.status(201).json(result);
  } catch (error) {
    logger.error('创建会话失败', { error: error.message, stack: error.stack });
    res.status(500).json({
      object: 'error',
      message: error.message,
      type: 'server_error',
      param: null,
      code: 'internal_server_error'
    });
  }
};

// 获取会话详情
exports.getThread = async (req, res) => {
  try {
    const { thread_id } = req.params;
    const result = await openaiService.getThread(thread_id, req.user.id);
    if (!result) {
      return res.status(404).json({
        object: 'error',
        message: '会话不存在',
        type: 'not_found_error',
        param: 'thread_id',
        code: 'thread_not_found'
      });
    }
    res.status(200).json(result);
  } catch (error) {
    logger.error('获取会话详情失败', { error: error.message, stack: error.stack, thread_id: req.params.thread_id });
    res.status(500).json({
      object: 'error',
      message: error.message,
      type: 'server_error',
      param: null,
      code: 'internal_server_error'
    });
  }
};

// 更新会话
exports.updateThread = async (req, res) => {
  try {
    const { thread_id } = req.params;
    const updateData = req.body;
    const result = await openaiService.updateThread(thread_id, updateData, req.user.id);
    if (!result) {
      return res.status(404).json({
        object: 'error',
        message: '会话不存在',
        type: 'not_found_error',
        param: 'thread_id',
        code: 'thread_not_found'
      });
    }
    res.status(200).json(result);
  } catch (error) {
    logger.error('更新会话失败', { error: error.message, stack: error.stack, thread_id: req.params.thread_id });
    res.status(500).json({
      object: 'error',
      message: error.message,
      type: 'server_error',
      param: null,
      code: 'internal_server_error'
    });
  }
};

// 删除会话
exports.deleteThread = async (req, res) => {
  try {
    const { thread_id } = req.params;
    const result = await openaiService.deleteThread(thread_id, req.user.id);
    if (!result) {
      return res.status(404).json({
        object: 'error',
        message: '会话不存在',
        type: 'not_found_error',
        param: 'thread_id',
        code: 'thread_not_found'
      });
    }
    res.status(200).json({
      id: thread_id,
      object: 'thread.deleted',
      deleted: true
    });
  } catch (error) {
    logger.error('删除会话失败', { error: error.message, stack: error.stack, thread_id: req.params.thread_id });
    res.status(500).json({
      object: 'error',
      message: error.message,
      type: 'server_error',
      param: null,
      code: 'internal_server_error'
    });
  }
};

/**
 * Messages API
 */
// 获取消息列表
exports.listMessages = async (req, res) => {
  try {
    const { thread_id } = req.params;
    const { limit = 20, order = 'desc', after, before } = req.query;
    const result = await openaiService.listMessages(thread_id, req.user.id, { limit, order, after, before });
    res.status(200).json(result);
  } catch (error) {
    logger.error('获取消息列表失败', { error: error.message, stack: error.stack, thread_id: req.params.thread_id });
    res.status(500).json({
      object: 'error',
      message: error.message,
      type: 'server_error',
      param: null,
      code: 'internal_server_error'
    });
  }
};

// 创建消息
exports.createMessage = async (req, res) => {
  try {
    const { thread_id } = req.params;
    const messageData = req.body;
    messageData.user_id = req.user.id;
    const result = await openaiService.createMessage(thread_id, messageData);
    res.status(201).json(result);
  } catch (error) {
    logger.error('创建消息失败', { error: error.message, stack: error.stack, thread_id: req.params.thread_id });
    res.status(500).json({
      object: 'error',
      message: error.message,
      type: 'server_error',
      param: null,
      code: 'internal_server_error'
    });
  }
};

// 获取消息详情
exports.getMessage = async (req, res) => {
  try {
    const { thread_id, message_id } = req.params;
    const result = await openaiService.getMessage(thread_id, message_id, req.user.id);
    if (!result) {
      return res.status(404).json({
        object: 'error',
        message: '消息不存在',
        type: 'not_found_error',
        param: 'message_id',
        code: 'message_not_found'
      });
    }
    res.status(200).json(result);
  } catch (error) {
    logger.error('获取消息详情失败', { 
      error: error.message, 
      stack: error.stack, 
      thread_id: req.params.thread_id,
      message_id: req.params.message_id
    });
    res.status(500).json({
      object: 'error',
      message: error.message,
      type: 'server_error',
      param: null,
      code: 'internal_server_error'
    });
  }
};

// 更新消息
exports.updateMessage = async (req, res) => {
  try {
    const { thread_id, message_id } = req.params;
    const updateData = req.body;
    const result = await openaiService.updateMessage(thread_id, message_id, updateData, req.user.id);
    if (!result) {
      return res.status(404).json({
        object: 'error',
        message: '消息不存在',
        type: 'not_found_error',
        param: 'message_id',
        code: 'message_not_found'
      });
    }
    res.status(200).json(result);
  } catch (error) {
    logger.error('更新消息失败', { 
      error: error.message, 
      stack: error.stack, 
      thread_id: req.params.thread_id,
      message_id: req.params.message_id
    });
    res.status(500).json({
      object: 'error',
      message: error.message,
      type: 'server_error',
      param: null,
      code: 'internal_server_error'
    });
  }
};

/**
 * Runs API
 */
// 创建运行
exports.createRun = async (req, res) => {
  try {
    const { thread_id } = req.params;
    const runData = req.body;
    runData.user_id = req.user.id;
    const result = await openaiService.createRun(thread_id, runData);
    res.status(201).json(result);
  } catch (error) {
    logger.error('创建运行失败', { error: error.message, stack: error.stack, thread_id: req.params.thread_id });
    res.status(500).json({
      object: 'error',
      message: error.message,
      type: 'server_error',
      param: null,
      code: 'internal_server_error'
    });
  }
};

// 获取运行详情
exports.getRun = async (req, res) => {
  try {
    const { thread_id, run_id } = req.params;
    const result = await openaiService.getRun(thread_id, run_id, req.user.id);
    if (!result) {
      return res.status(404).json({
        object: 'error',
        message: '运行不存在',
        type: 'not_found_error',
        param: 'run_id',
        code: 'run_not_found'
      });
    }
    res.status(200).json(result);
  } catch (error) {
    logger.error('获取运行详情失败', { 
      error: error.message, 
      stack: error.stack, 
      thread_id: req.params.thread_id,
      run_id: req.params.run_id
    });
    res.status(500).json({
      object: 'error',
      message: error.message,
      type: 'server_error',
      param: null,
      code: 'internal_server_error'
    });
  }
};

// 更新运行
exports.updateRun = async (req, res) => {
  try {
    const { thread_id, run_id } = req.params;
    const updateData = req.body;
    const result = await openaiService.updateRun(thread_id, run_id, updateData, req.user.id);
    if (!result) {
      return res.status(404).json({
        object: 'error',
        message: '运行不存在',
        type: 'not_found_error',
        param: 'run_id',
        code: 'run_not_found'
      });
    }
    res.status(200).json(result);
  } catch (error) {
    logger.error('更新运行失败', { 
      error: error.message, 
      stack: error.stack, 
      thread_id: req.params.thread_id,
      run_id: req.params.run_id
    });
    res.status(500).json({
      object: 'error',
      message: error.message,
      type: 'server_error',
      param: null,
      code: 'internal_server_error'
    });
  }
};

// 取消运行
exports.cancelRun = async (req, res) => {
  try {
    const { thread_id, run_id } = req.params;
    const result = await openaiService.cancelRun(thread_id, run_id, req.user.id);
    if (!result) {
      return res.status(404).json({
        object: 'error',
        message: '运行不存在',
        type: 'not_found_error',
        param: 'run_id',
        code: 'run_not_found'
      });
    }
    res.status(200).json(result);
  } catch (error) {
    logger.error('取消运行失败', { 
      error: error.message, 
      stack: error.stack, 
      thread_id: req.params.thread_id,
      run_id: req.params.run_id
    });
    res.status(500).json({
      object: 'error',
      message: error.message,
      type: 'server_error',
      param: null,
      code: 'internal_server_error'
    });
  }
};

// 获取运行列表
exports.listRuns = async (req, res) => {
  try {
    const { thread_id } = req.params;
    const { limit = 20, order = 'desc', after, before } = req.query;
    const result = await openaiService.listRuns(thread_id, req.user.id, { limit, order, after, before });
    res.status(200).json(result);
  } catch (error) {
    logger.error('获取运行列表失败', { error: error.message, stack: error.stack, thread_id: req.params.thread_id });
    res.status(500).json({
      object: 'error',
      message: error.message,
      type: 'server_error',
      param: null,
      code: 'internal_server_error'
    });
  }
};

// 提交工具输出
exports.submitToolOutputs = async (req, res) => {
  try {
    const { thread_id, run_id } = req.params;
    const { tool_outputs } = req.body;
    const result = await openaiService.submitToolOutputs(thread_id, run_id, tool_outputs, req.user.id);
    if (!result) {
      return res.status(404).json({
        object: 'error',
        message: '运行不存在',
        type: 'not_found_error',
        param: 'run_id',
        code: 'run_not_found'
      });
    }
    res.status(200).json(result);
  } catch (error) {
    logger.error('提交工具输出失败', { 
      error: error.message, 
      stack: error.stack, 
      thread_id: req.params.thread_id,
      run_id: req.params.run_id
    });
    res.status(500).json({
      object: 'error',
      message: error.message,
      type: 'server_error',
      param: null,
      code: 'internal_server_error'
    });
  }
};

/**
 * Tools API
 */
// 获取工具列表
exports.listTools = async (req, res) => {
  try {
    const result = await openaiService.listTools(req.user.id);
    res.status(200).json(result);
  } catch (error) {
    logger.error('获取工具列表失败', { error: error.message, stack: error.stack });
    res.status(500).json({
      object: 'error',
      message: error.message,
      type: 'server_error',
      param: null,
      code: 'internal_server_error'
    });
  }
};

// 执行工具函数
exports.executeFunction = async (req, res) => {
  try {
    const { name, arguments: args } = req.body;
    const params = typeof args === 'string' ? JSON.parse(args) : args;
    const result = await openaiService.executeFunction(req.user.id, name, params);
    res.status(200).json(result);
  } catch (error) {
    logger.error('执行工具函数失败', { error: error.message, stack: error.stack });
    res.status(500).json({
      object: 'error',
      message: error.message,
      type: 'server_error',
      param: null,
      code: 'internal_server_error'
    });
  }
}; 