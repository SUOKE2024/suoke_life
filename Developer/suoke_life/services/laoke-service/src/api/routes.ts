/**
 * 老克服务API路由
 * 对外提供HTTP接口，供其他服务和客户端调用
 */

import express, { Request, Response, Router } from 'express';
import { logger } from '../utils/logger';
import laokeService from '../laoke-service';

// 创建路由
const router: Router = express.Router();

// 服务状态路由
router.get('/status', (req: Request, res: Response) => {
  try {
    const status = laokeService.getServiceStatus();
    res.json({
      success: true,
      data: status
    });
  } catch (error) {
    logger.error('获取服务状态失败', {
      error: error instanceof Error ? error.message : String(error)
    });
    
    res.status(500).json({
      success: false,
      message: '获取服务状态失败',
      error: error instanceof Error ? error.message : String(error)
    });
  }
});

// 无障碍功能路由
router.get('/accessibility/voices', async (req: Request, res: Response) => {
  try {
    const voiceOptions = await laokeService.getAccessibilityService().getAvailableVoices();
    res.json({
      success: true,
      data: voiceOptions
    });
  } catch (error) {
    logger.error('获取语音选项失败', {
      error: error instanceof Error ? error.message : String(error)
    });
    
    res.status(500).json({
      success: false,
      message: '获取语音选项失败',
      error: error instanceof Error ? error.message : String(error)
    });
  }
});

router.post('/accessibility/text-to-speech', async (req: Request, res: Response) => {
  try {
    const { text, voiceId, pitch, rate, volume } = req.body;
    
    if (!text) {
      return res.status(400).json({
        success: false,
        message: '缺少text参数'
      });
    }
    
    const audioData = await laokeService.getAccessibilityService().textToSpeech(
      text,
      voiceId,
      { pitch, rate, volume }
    );
    
    res.json({
      success: true,
      data: {
        audioData
      }
    });
  } catch (error) {
    logger.error('文字转语音失败', {
      error: error instanceof Error ? error.message : String(error)
    });
    
    res.status(500).json({
      success: false,
      message: '文字转语音失败',
      error: error instanceof Error ? error.message : String(error)
    });
  }
});

// 知识传播路由
router.get('/knowledge/categories', async (req: Request, res: Response) => {
  try {
    const categories = await laokeService.getKnowledgeDisseminationService().getKnowledgeCategories();
    res.json({
      success: true,
      data: categories
    });
  } catch (error) {
    logger.error('获取知识分类失败', {
      error: error instanceof Error ? error.message : String(error)
    });
    
    res.status(500).json({
      success: false,
      message: '获取知识分类失败',
      error: error instanceof Error ? error.message : String(error)
    });
  }
});

router.get('/knowledge/articles', async (req: Request, res: Response) => {
  try {
    const { categoryId, page = 1, limit = 10 } = req.query;
    
    const articles = await laokeService.getKnowledgeDisseminationService().getKnowledgeArticles(
      categoryId as string | undefined,
      Number(page),
      Number(limit)
    );
    
    res.json({
      success: true,
      data: articles
    });
  } catch (error) {
    logger.error('获取知识文章失败', {
      error: error instanceof Error ? error.message : String(error),
      query: req.query
    });
    
    res.status(500).json({
      success: false,
      message: '获取知识文章失败',
      error: error instanceof Error ? error.message : String(error)
    });
  }
});

router.get('/knowledge/articles/:id', async (req: Request, res: Response) => {
  try {
    const article = await laokeService.getKnowledgeDisseminationService().getKnowledgeArticleById(
      req.params.id
    );
    
    if (!article) {
      return res.status(404).json({
        success: false,
        message: '文章不存在'
      });
    }
    
    res.json({
      success: true,
      data: article
    });
  } catch (error) {
    logger.error('获取知识文章详情失败', {
      error: error instanceof Error ? error.message : String(error),
      articleId: req.params.id
    });
    
    res.status(500).json({
      success: false,
      message: '获取知识文章详情失败',
      error: error instanceof Error ? error.message : String(error)
    });
  }
});

// 知识培训路由
router.get('/training/courses', async (req: Request, res: Response) => {
  try {
    const { categoryId, level, page = 1, limit = 10 } = req.query;
    
    const courses = await laokeService.getKnowledgeTrainingService().getCourses(
      categoryId as string | undefined,
      level as string | undefined,
      Number(page),
      Number(limit)
    );
    
    res.json({
      success: true,
      data: courses
    });
  } catch (error) {
    logger.error('获取培训课程失败', {
      error: error instanceof Error ? error.message : String(error),
      query: req.query
    });
    
    res.status(500).json({
      success: false,
      message: '获取培训课程失败',
      error: error instanceof Error ? error.message : String(error)
    });
  }
});

router.get('/training/courses/:id', async (req: Request, res: Response) => {
  try {
    const course = await laokeService.getKnowledgeTrainingService().getCourseById(
      req.params.id
    );
    
    if (!course) {
      return res.status(404).json({
        success: false,
        message: '课程不存在'
      });
    }
    
    res.json({
      success: true,
      data: course
    });
  } catch (error) {
    logger.error('获取培训课程详情失败', {
      error: error instanceof Error ? error.message : String(error),
      courseId: req.params.id
    });
    
    res.status(500).json({
      success: false,
      message: '获取培训课程详情失败',
      error: error instanceof Error ? error.message : String(error)
    });
  }
});

// 博客管理路由
router.get('/blog/posts', async (req: Request, res: Response) => {
  try {
    const {
      authorId,
      categoryId,
      tag,
      status,
      page = 1,
      limit = 10
    } = req.query;
    
    const posts = await laokeService.getBlogManagementService().getPosts(
      authorId as string | undefined,
      categoryId as string | undefined,
      tag as string | undefined,
      status as string | undefined,
      Number(page),
      Number(limit)
    );
    
    res.json({
      success: true,
      data: posts
    });
  } catch (error) {
    logger.error('获取博客文章失败', {
      error: error instanceof Error ? error.message : String(error),
      query: req.query
    });
    
    res.status(500).json({
      success: false,
      message: '获取博客文章失败',
      error: error instanceof Error ? error.message : String(error)
    });
  }
});

router.get('/blog/posts/:id', async (req: Request, res: Response) => {
  try {
    const withComments = req.query.withComments === 'true';
    
    const post = await laokeService.getBlogManagementService().getPost(
      req.params.id,
      withComments
    );
    
    if (!post) {
      return res.status(404).json({
        success: false,
        message: '博客文章不存在'
      });
    }
    
    res.json({
      success: true,
      data: post
    });
  } catch (error) {
    logger.error('获取博客文章详情失败', {
      error: error instanceof Error ? error.message : String(error),
      postId: req.params.id
    });
    
    res.status(500).json({
      success: false,
      message: '获取博客文章详情失败',
      error: error instanceof Error ? error.message : String(error)
    });
  }
});

router.post('/blog/posts', async (req: Request, res: Response) => {
  try {
    const { post } = req.body;
    
    if (!post) {
      return res.status(400).json({
        success: false,
        message: '缺少post参数'
      });
    }
    
    const id = await laokeService.getBlogManagementService().createPost(post);
    
    res.status(201).json({
      success: true,
      data: {
        id
      }
    });
  } catch (error) {
    logger.error('创建博客文章失败', {
      error: error instanceof Error ? error.message : String(error),
      body: req.body
    });
    
    res.status(500).json({
      success: false,
      message: '创建博客文章失败',
      error: error instanceof Error ? error.message : String(error)
    });
  }
});

router.put('/blog/posts/:id', async (req: Request, res: Response) => {
  try {
    const { updates } = req.body;
    
    if (!updates) {
      return res.status(400).json({
        success: false,
        message: '缺少updates参数'
      });
    }
    
    const success = await laokeService.getBlogManagementService().updatePost(
      req.params.id,
      updates
    );
    
    if (!success) {
      return res.status(404).json({
        success: false,
        message: '博客文章不存在或更新失败'
      });
    }
    
    res.json({
      success: true
    });
  } catch (error) {
    logger.error('更新博客文章失败', {
      error: error instanceof Error ? error.message : String(error),
      postId: req.params.id,
      updates: req.body.updates
    });
    
    res.status(500).json({
      success: false,
      message: '更新博客文章失败',
      error: error instanceof Error ? error.message : String(error)
    });
  }
});

router.delete('/blog/posts/:id', async (req: Request, res: Response) => {
  try {
    const success = await laokeService.getBlogManagementService().deletePost(
      req.params.id
    );
    
    if (!success) {
      return res.status(404).json({
        success: false,
        message: '博客文章不存在或删除失败'
      });
    }
    
    res.json({
      success: true
    });
  } catch (error) {
    logger.error('删除博客文章失败', {
      error: error instanceof Error ? error.message : String(error),
      postId: req.params.id
    });
    
    res.status(500).json({
      success: false,
      message: '删除博客文章失败',
      error: error instanceof Error ? error.message : String(error)
    });
  }
});

// 博客评论路由
router.post('/blog/comments', async (req: Request, res: Response) => {
  try {
    const { comment } = req.body;
    
    if (!comment) {
      return res.status(400).json({
        success: false,
        message: '缺少comment参数'
      });
    }
    
    const id = await laokeService.getBlogInteractionService().createComment(comment);
    
    res.status(201).json({
      success: true,
      data: {
        id
      }
    });
  } catch (error) {
    logger.error('创建评论失败', {
      error: error instanceof Error ? error.message : String(error),
      body: req.body
    });
    
    res.status(500).json({
      success: false,
      message: '创建评论失败',
      error: error instanceof Error ? error.message : String(error)
    });
  }
});

router.get('/blog/posts/:postId/comments', async (req: Request, res: Response) => {
  try {
    const { status, parentId } = req.query;
    
    const comments = await laokeService.getBlogInteractionService().getPostComments(
      req.params.postId,
      status ? (status as string).split(',') as any : undefined,
      parentId as string | undefined
    );
    
    res.json({
      success: true,
      data: comments
    });
  } catch (error) {
    logger.error('获取博客评论失败', {
      error: error instanceof Error ? error.message : String(error),
      postId: req.params.postId,
      query: req.query
    });
    
    res.status(500).json({
      success: false,
      message: '获取博客评论失败',
      error: error instanceof Error ? error.message : String(error)
    });
  }
});

router.post('/blog/interaction', async (req: Request, res: Response) => {
  try {
    const { postId, interaction } = req.body;
    
    if (!postId || !interaction) {
      return res.status(400).json({
        success: false,
        message: '缺少postId或interaction参数'
      });
    }
    
    const success = await laokeService.getBlogInteractionService().recordBlogInteraction(
      postId,
      interaction
    );
    
    if (!success) {
      return res.status(404).json({
        success: false,
        message: '博客文章不存在或记录互动失败'
      });
    }
    
    res.json({
      success: true
    });
  } catch (error) {
    logger.error('记录博客互动失败', {
      error: error instanceof Error ? error.message : String(error),
      body: req.body
    });
    
    res.status(500).json({
      success: false,
      message: '记录博客互动失败',
      error: error instanceof Error ? error.message : String(error)
    });
  }
});

// 游戏NPC路由
router.get('/game/npc/definition', async (req: Request, res: Response) => {
  try {
    const npcDefinition = laokeService.getGameNPCService().getNPCDefinition();
    
    res.json({
      success: true,
      data: npcDefinition
    });
  } catch (error) {
    logger.error('获取NPC定义失败', {
      error: error instanceof Error ? error.message : String(error)
    });
    
    res.status(500).json({
      success: false,
      message: '获取NPC定义失败',
      error: error instanceof Error ? error.message : String(error)
    });
  }
});

router.post('/game/npc/dialog/start', async (req: Request, res: Response) => {
  try {
    const { userId } = req.body;
    
    if (!userId) {
      return res.status(400).json({
        success: false,
        message: '缺少userId参数'
      });
    }
    
    const dialog = laokeService.getGameNPCService().startDialog(userId);
    
    res.json({
      success: true,
      data: dialog
    });
  } catch (error) {
    logger.error('开始对话失败', {
      error: error instanceof Error ? error.message : String(error),
      body: req.body
    });
    
    res.status(500).json({
      success: false,
      message: '开始对话失败',
      error: error instanceof Error ? error.message : String(error)
    });
  }
});

router.post('/game/npc/dialog/choose', async (req: Request, res: Response) => {
  try {
    const { userId, optionId } = req.body;
    
    if (!userId || !optionId) {
      return res.status(400).json({
        success: false,
        message: '缺少userId或optionId参数'
      });
    }
    
    const nextDialog = laokeService.getGameNPCService().chooseOption(userId, optionId);
    
    if (!nextDialog) {
      return res.status(404).json({
        success: false,
        message: '对话选项无效或无下一对话'
      });
    }
    
    res.json({
      success: true,
      data: nextDialog
    });
  } catch (error) {
    logger.error('选择对话选项失败', {
      error: error instanceof Error ? error.message : String(error),
      body: req.body
    });
    
    res.status(500).json({
      success: false,
      message: '选择对话选项失败',
      error: error instanceof Error ? error.message : String(error)
    });
  }
});

router.get('/game/npc/tasks', async (req: Request, res: Response) => {
  try {
    const tasks = laokeService.getGameNPCService().getAvailableTasks();
    
    res.json({
      success: true,
      data: tasks
    });
  } catch (error) {
    logger.error('获取可用任务失败', {
      error: error instanceof Error ? error.message : String(error)
    });
    
    res.status(500).json({
      success: false,
      message: '获取可用任务失败',
      error: error instanceof Error ? error.message : String(error)
    });
  }
});

router.get('/game/npc/users/:userId/tasks', async (req: Request, res: Response) => {
  try {
    const { status } = req.query;
    
    const tasks = laokeService.getGameNPCService().getUserTasks(
      req.params.userId,
      status ? (status as string).split(',') as any : undefined
    );
    
    res.json({
      success: true,
      data: tasks
    });
  } catch (error) {
    logger.error('获取用户任务失败', {
      error: error instanceof Error ? error.message : String(error),
      userId: req.params.userId,
      query: req.query
    });
    
    res.status(500).json({
      success: false,
      message: '获取用户任务失败',
      error: error instanceof Error ? error.message : String(error)
    });
  }
});

router.post('/game/npc/tasks/assign', async (req: Request, res: Response) => {
  try {
    const { userId, taskId } = req.body;
    
    if (!userId || !taskId) {
      return res.status(400).json({
        success: false,
        message: '缺少userId或taskId参数'
      });
    }
    
    const task = laokeService.getGameNPCService().assignTask(userId, taskId);
    
    if (!task) {
      return res.status(404).json({
        success: false,
        message: '任务不存在或分配失败'
      });
    }
    
    res.json({
      success: true,
      data: task
    });
  } catch (error) {
    logger.error('分配任务失败', {
      error: error instanceof Error ? error.message : String(error),
      body: req.body
    });
    
    res.status(500).json({
      success: false,
      message: '分配任务失败',
      error: error instanceof Error ? error.message : String(error)
    });
  }
});

router.post('/game/npc/tasks/progress', async (req: Request, res: Response) => {
  try {
    const { userId, taskId, progress } = req.body;
    
    if (!userId || !taskId || progress === undefined) {
      return res.status(400).json({
        success: false,
        message: '缺少userId、taskId或progress参数'
      });
    }
    
    const task = laokeService.getGameNPCService().updateTaskProgress(
      userId,
      taskId,
      progress
    );
    
    if (!task) {
      return res.status(404).json({
        success: false,
        message: '任务不存在或更新进度失败'
      });
    }
    
    res.json({
      success: true,
      data: task
    });
  } catch (error) {
    logger.error('更新任务进度失败', {
      error: error instanceof Error ? error.message : String(error),
      body: req.body
    });
    
    res.status(500).json({
      success: false,
      message: '更新任务进度失败',
      error: error instanceof Error ? error.message : String(error)
    });
  }
});

router.post('/game/npc/tasks/complete', async (req: Request, res: Response) => {
  try {
    const { userId, taskId } = req.body;
    
    if (!userId || !taskId) {
      return res.status(400).json({
        success: false,
        message: '缺少userId或taskId参数'
      });
    }
    
    const rewards = laokeService.getGameNPCService().completeTask(
      userId,
      taskId
    );
    
    if (!rewards) {
      return res.status(404).json({
        success: false,
        message: '任务不存在、未完成或已领取奖励'
      });
    }
    
    res.json({
      success: true,
      data: {
        rewards
      }
    });
  } catch (error) {
    logger.error('完成任务失败', {
      error: error instanceof Error ? error.message : String(error),
      body: req.body
    });
    
    res.status(500).json({
      success: false,
      message: '完成任务失败',
      error: error instanceof Error ? error.message : String(error)
    });
  }
});

export default router;