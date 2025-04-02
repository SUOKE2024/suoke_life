/**
 * 数据库初始化脚本
 * 用于创建初始的用户、会话和智能体数据
 */
import dotenv from 'dotenv';
import { initDatabaseConnection, closeDatabaseConnection } from '../config/database';
import User from '../models/User';
import Conversation from '../models/Conversation';
import XiaoAiAgent from '../models/XiaoAiAgent';
import { v4 as uuidv4 } from 'uuid';
import { DialectType } from '../types';

// 加载环境变量
dotenv.config();

/**
 * 创建默认智能体
 */
async function createDefaultAgent() {
  const existingAgent = await XiaoAiAgent.findOne({ name: '小艾' });
  
  if (existingAgent) {
    console.log('默认智能体已存在，跳过创建');
    return;
  }
  
  const xiaoAiAgent = new XiaoAiAgent({
    agentId: uuidv4(),
    name: '小艾',
    version: '1.0.0',
    status: 'active',
    capabilities: [
      'voice-guidance',
      'accessibility',
      'dialect-detection',
      'diagnostic-coordination',
      'medical-knowledge',
      'chat'
    ],
    config: {
      defaultLanguage: 'zh-CN',
      voiceGuidanceEnabled: true,
      dialectDetectionEnabled: true,
      diagnosticCoordinationEnabled: true,
      personalityType: 'helpful',
      responseStyle: 'conversational'
    },
    metrics: {
      conversations: 0,
      messagesProcessed: 0,
      avgResponseTime: 0
    }
  });
  
  await xiaoAiAgent.save();
  console.log('已创建默认智能体：小艾');
}

/**
 * 创建演示用户
 */
async function createDemoUsers() {
  const demoUsers = [
    {
      userId: uuidv4(),
      username: '演示用户1',
      accessibilityPreferences: {
        needsVoiceGuidance: false,
        needsSimplifiedContent: false,
        needsHighContrast: false,
        needsScreenReader: false,
        hasVisualImpairment: false,
        hasHearingImpairment: false,
        hasCognitiveImpairment: false,
        hasMotorImpairment: false,
        guidanceSpeed: 'normal',
        voiceGuidanceVolume: 80,
        textSize: 'medium'
      },
      dialectPreferences: {
        primary: DialectType.MANDARIN,
        autoDetect: true
      }
    },
    {
      userId: uuidv4(),
      username: '无障碍用户',
      accessibilityPreferences: {
        needsVoiceGuidance: true,
        needsSimplifiedContent: true,
        needsHighContrast: true,
        needsScreenReader: false,
        hasVisualImpairment: true,
        hasHearingImpairment: false,
        hasCognitiveImpairment: false,
        hasMotorImpairment: false,
        guidanceSpeed: 'slow',
        voiceGuidanceVolume: 90,
        textSize: 'large'
      },
      dialectPreferences: {
        primary: DialectType.MANDARIN,
        autoDetect: true
      }
    },
    {
      userId: uuidv4(),
      username: '方言用户',
      accessibilityPreferences: {
        needsVoiceGuidance: false,
        needsSimplifiedContent: false,
        needsHighContrast: false,
        needsScreenReader: false,
        hasVisualImpairment: false,
        hasHearingImpairment: false,
        hasCognitiveImpairment: false,
        hasMotorImpairment: false,
        guidanceSpeed: 'normal',
        voiceGuidanceVolume: 80,
        textSize: 'medium'
      },
      dialectPreferences: {
        primary: DialectType.CANTONESE,
        secondary: DialectType.MANDARIN,
        autoDetect: true
      }
    }
  ];
  
  for (const userData of demoUsers) {
    const existingUser = await User.findOne({ username: userData.username });
    
    if (existingUser) {
      console.log(`用户 ${userData.username} 已存在，跳过创建`);
      continue;
    }
    
    const user = new User(userData);
    await user.save();
    console.log(`已创建用户：${userData.username}`);
    
    // 为每个用户创建示例会话
    await createDemoConversation(userData.userId);
  }
}

/**
 * 为用户创建示例会话
 */
async function createDemoConversation(userId: string) {
  const conversationData = {
    conversationId: uuidv4(),
    userId,
    title: '欢迎使用小艾智能体',
    messages: [
      {
        messageId: uuidv4(),
        role: 'assistant',
        content: '您好！我是小艾，索克生活APP的智能助手。我能为您提供四诊健康分析、生活建议和无障碍支持。请问有什么我可以帮助您的吗？',
        contentType: 'text',
        timestamp: new Date()
      }
    ],
    unread: true,
    createdAt: new Date(),
    updatedAt: new Date()
  };
  
  const conversation = new Conversation(conversationData);
  await conversation.save();
  console.log(`已为用户 ${userId} 创建示例会话`);
}

/**
 * 主函数
 */
async function initDatabase() {
  try {
    console.log('开始初始化数据库...');
    
    // 连接数据库
    await initDatabaseConnection();
    
    // 创建默认数据
    await createDefaultAgent();
    await createDemoUsers();
    
    console.log('数据库初始化完成！');
  } catch (error) {
    console.error('数据库初始化失败:', error);
  } finally {
    // 关闭数据库连接
    await closeDatabaseConnection();
  }
}

// 执行初始化
initDatabase(); 