"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.releaseScheduler = exports.cleanupCompletedTasks = exports.cancelTask = exports.getTaskStatus = exports.addTask = exports.initializeAgentScheduler = void 0;
const logger_1 = require("../../utils/logger");
// 任务队列
const taskQueue = [];
// 是否正在处理任务
let isProcessing = false;
// 最大并发任务数
let maxConcurrentTasks = 2;
// 定期任务ID
const scheduledTasks = {};
/**
 * 初始化智能体任务调度器
 * @param config 智能体配置
 */
const initializeAgentScheduler = async (config) => {
    try {
        logger_1.logger.info('初始化智能体任务调度器...');
        // 从环境变量获取最大并发任务数
        if (process.env.MAX_CONCURRENT_TASKS) {
            maxConcurrentTasks = parseInt(process.env.MAX_CONCURRENT_TASKS, 10);
        }
        // 启动任务处理器
        processNextTask();
        // 设置定期任务
        setupScheduledTasks();
        logger_1.logger.info('智能体任务调度器初始化完成');
    }
    catch (error) {
        logger_1.logger.error('智能体任务调度器初始化失败:', error);
        throw error;
    }
};
exports.initializeAgentScheduler = initializeAgentScheduler;
/**
 * 添加任务到队列
 * @param name 任务名称
 * @param handler 任务处理函数
 * @param priority 任务优先级，默认为0，越大越优先
 */
const addTask = (name, handler, priority = 0) => {
    const taskId = generateTaskId();
    const task = {
        id: taskId,
        name,
        status: 'pending',
        priority,
        createdAt: Date.now(),
        handler
    };
    // 根据优先级插入队列
    let inserted = false;
    for (let i = 0; i < taskQueue.length; i++) {
        if (taskQueue[i].priority < priority) {
            taskQueue.splice(i, 0, task);
            inserted = true;
            break;
        }
    }
    if (!inserted) {
        taskQueue.push(task);
    }
    logger_1.logger.info(`任务已添加到队列: ${name} (ID: ${taskId}, 优先级: ${priority})`);
    // 尝试处理任务
    processNextTask();
    return taskId;
};
exports.addTask = addTask;
/**
 * 处理下一个任务
 */
const processNextTask = async () => {
    // 如果已经在处理任务，或者队列为空，直接返回
    if (isProcessing || taskQueue.length === 0) {
        return;
    }
    isProcessing = true;
    try {
        // 获取当前运行中的任务数
        const runningTasks = taskQueue.filter(t => t.status === 'running').length;
        // 如果当前运行中的任务数小于最大并发任务数，开始新任务
        if (runningTasks < maxConcurrentTasks) {
            // 获取下一个待处理的任务
            const nextTask = taskQueue.find(t => t.status === 'pending');
            if (nextTask) {
                // 更新任务状态
                nextTask.status = 'running';
                nextTask.startedAt = Date.now();
                logger_1.logger.info(`开始执行任务: ${nextTask.name} (ID: ${nextTask.id})`);
                // 异步执行任务
                nextTask.handler()
                    .then(result => {
                    // 任务成功完成
                    nextTask.status = 'completed';
                    nextTask.completedAt = Date.now();
                    nextTask.result = result;
                    logger_1.logger.info(`任务完成: ${nextTask.name} (ID: ${nextTask.id})`);
                })
                    .catch(error => {
                    // 任务执行失败
                    nextTask.status = 'failed';
                    nextTask.completedAt = Date.now();
                    nextTask.error = error;
                    logger_1.logger.error(`任务失败: ${nextTask.name} (ID: ${nextTask.id})`, error);
                })
                    .finally(() => {
                    // 处理下一个任务
                    isProcessing = false;
                    processNextTask();
                });
            }
        }
    }
    catch (error) {
        logger_1.logger.error('处理任务时发生错误:', error);
    }
    finally {
        isProcessing = false;
    }
};
/**
 * 生成唯一的任务ID
 */
const generateTaskId = () => {
    return `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};
/**
 * 获取任务状态
 * @param taskId 任务ID
 */
const getTaskStatus = (taskId) => {
    const task = taskQueue.find(t => t.id === taskId);
    return task || null;
};
exports.getTaskStatus = getTaskStatus;
/**
 * 取消任务
 * @param taskId 任务ID
 */
const cancelTask = (taskId) => {
    const taskIndex = taskQueue.findIndex(t => t.id === taskId);
    if (taskIndex === -1) {
        return false;
    }
    const task = taskQueue[taskIndex];
    // 只有待处理的任务可以取消
    if (task.status === 'pending') {
        taskQueue.splice(taskIndex, 1);
        logger_1.logger.info(`任务已取消: ${task.name} (ID: ${task.id})`);
        return true;
    }
    return false;
};
exports.cancelTask = cancelTask;
/**
 * 设置定期任务
 */
const setupScheduledTasks = () => {
    // 每小时执行一次的任务
    scheduledTasks.hourlyTask = setInterval(() => {
        logger_1.logger.info('执行定期任务: 每小时任务');
        // 添加实际的每小时任务
    }, 60 * 60 * 1000);
    // 每天执行一次的任务
    scheduledTasks.dailyTask = setInterval(() => {
        logger_1.logger.info('执行定期任务: 每天任务');
        // 添加实际的每天任务
    }, 24 * 60 * 60 * 1000);
    // 每周执行一次的任务
    scheduledTasks.weeklyTask = setInterval(() => {
        logger_1.logger.info('执行定期任务: 每周任务');
        // 添加实际的每周任务
    }, 7 * 24 * 60 * 60 * 1000);
    logger_1.logger.info('定期任务已设置');
};
/**
 * 清理已完成的任务
 * @param maxAge 最长保留时间（毫秒），默认为1小时
 */
const cleanupCompletedTasks = (maxAge = 60 * 60 * 1000) => {
    const now = Date.now();
    const initialLength = taskQueue.length;
    // 筛选出需要保留的任务
    const remainingTasks = taskQueue.filter(task => {
        // 只清理已完成或失败的任务
        if (task.status !== 'completed' && task.status !== 'failed') {
            return true;
        }
        const taskAge = now - (task.completedAt || now);
        return taskAge < maxAge;
    });
    // 更新任务队列
    taskQueue.length = 0;
    taskQueue.push(...remainingTasks);
    const removedCount = initialLength - taskQueue.length;
    if (removedCount > 0) {
        logger_1.logger.info(`已清理 ${removedCount} 个已完成的任务`);
    }
};
exports.cleanupCompletedTasks = cleanupCompletedTasks;
/**
 * 释放调度器资源
 */
const releaseScheduler = () => {
    try {
        logger_1.logger.info('释放任务调度器资源...');
        // 清除所有定期任务
        for (const taskId in scheduledTasks) {
            clearInterval(scheduledTasks[taskId]);
            delete scheduledTasks[taskId];
        }
        // 清空任务队列
        taskQueue.length = 0;
        logger_1.logger.info('任务调度器资源已释放');
    }
    catch (error) {
        logger_1.logger.error('释放任务调度器资源失败:', error);
    }
};
exports.releaseScheduler = releaseScheduler;
