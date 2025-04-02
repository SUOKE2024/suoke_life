/**
 * 数据库集成测试
 * 注意：这些测试需要实际的MongoDB连接
 * 在测试环境中运行时，应使用测试专用数据库
 */
import mongoose from 'mongoose';
import { UserRepository } from '../../../src/repositories/UserRepository';
import { ConversationRepository } from '../../../src/repositories/ConversationRepository';
import { XiaoAiAgentRepository } from '../../../src/repositories/XiaoAiAgentRepository';

// 测试前先设置环境变量
process.env.MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/xiaoai_test';

describe('数据库集成测试', () => {
  // 测试前连接到测试数据库
  beforeAll(async () => {
    await mongoose.connect(process.env.MONGODB_URI);
  });

  // 每个测试后清理集合
  afterEach(async () => {
    // 根据测试情况清理数据
    const collections = mongoose.connection.collections;
    for (const key in collections) {
      await collections[key].deleteMany({});
    }
  });

  // 所有测试完成后断开连接
  afterAll(async () => {
    await mongoose.connection.dropDatabase();
    await mongoose.connection.close();
  });

  describe('UserRepository', () => {
    let userRepository: UserRepository;

    beforeEach(() => {
      userRepository = new UserRepository();
    });

    it('应该创建并检索用户', async () => {
      // 创建用户
      const userData = {
        userId: 'test-user-1',
        username: 'testuser',
        email: 'test@example.com',
        phoneNumber: '13800000000',
        accessibilityPreferences: {
          needsVoiceGuidance: true,
          needsSimplifiedContent: false
        },
        dialectPreferences: {
          primary: 'mandarin',
          autoDetect: true
        }
      };

      const createdUser = await userRepository.create(userData);
      expect(createdUser).toHaveProperty('_id');
      expect(createdUser.userId).toBe('test-user-1');

      // 通过ID检索用户
      const retrievedUser = await userRepository.findByUserId('test-user-1');
      expect(retrievedUser).not.toBeNull();
      expect(retrievedUser?.username).toBe('testuser');
    });

    it('应该更新用户信息', async () => {
      // 创建用户
      const userData = {
        userId: 'test-user-2',
        username: 'updateuser',
        email: 'update@example.com'
      };

      await userRepository.create(userData);

      // 更新用户
      const updateResult = await userRepository.updateOne(
        { userId: 'test-user-2' },
        { $set: { username: 'updatedname' } }
      );

      expect(updateResult).toBeTruthy();

      // 验证更新
      const updatedUser = await userRepository.findByUserId('test-user-2');
      expect(updatedUser?.username).toBe('updatedname');
    });
  });

  describe('ConversationRepository', () => {
    let conversationRepository: ConversationRepository;

    beforeEach(() => {
      conversationRepository = new ConversationRepository();
    });

    it('应该创建并检索会话', async () => {
      // 创建会话
      const conversationData = {
        userId: 'test-user-1',
        title: '测试会话',
        messages: [
          { role: 'user', content: '测试消息', timestamp: new Date() }
        ],
        createdAt: new Date(),
        updatedAt: new Date(),
        isArchived: false
      };

      const createdConversation = await conversationRepository.create(conversationData);
      expect(createdConversation).toHaveProperty('_id');

      // 检索会话
      const conversationId = createdConversation._id.toString();
      const retrievedConversation = await conversationRepository.findById(conversationId);

      expect(retrievedConversation).not.toBeNull();
      expect(retrievedConversation?.title).toBe('测试会话');
      expect(retrievedConversation?.messages).toHaveLength(1);
    });

    it('应该查找用户的所有会话', async () => {
      // 创建多个会话
      await conversationRepository.create({
        userId: 'test-user-3',
        title: '会话1',
        messages: [],
        isArchived: false
      });

      await conversationRepository.create({
        userId: 'test-user-3',
        title: '会话2',
        messages: [],
        isArchived: false
      });

      // 检索用户会话
      const conversations = await conversationRepository.findByUserId('test-user-3');
      expect(conversations).toHaveLength(2);
      expect(conversations[0].title).toMatch(/会话[12]/);
      expect(conversations[1].title).toMatch(/会话[12]/);
    });
  });

  describe('XiaoAiAgentRepository', () => {
    let agentRepository: XiaoAiAgentRepository;

    beforeEach(() => {
      agentRepository = new XiaoAiAgentRepository();
    });

    it('应该创建并检索代理', async () => {
      // 创建代理
      const agentData = {
        name: '测试代理',
        description: '用于测试的代理',
        capabilities: ['测试功能1', '测试功能2'],
        personalityTraits: ['友善', '专业'],
        activeStatus: true,
        version: '1.0.0',
        modelConfig: {
          model: 'gpt-4',
          temperature: 0.7,
          maxTokens: 2000
        }
      };

      const createdAgent = await agentRepository.create(agentData);
      expect(createdAgent).toHaveProperty('_id');

      // 检索代理
      const agentId = createdAgent._id.toString();
      const retrievedAgent = await agentRepository.findById(agentId);

      expect(retrievedAgent).not.toBeNull();
      expect(retrievedAgent?.name).toBe('测试代理');
      expect(retrievedAgent?.capabilities).toContain('测试功能1');
    });

    it('应该更新代理状态', async () => {
      // 创建代理
      const agentData = {
        name: '状态测试代理',
        description: '测试状态更新',
        capabilities: ['状态管理'],
        activeStatus: true,
        version: '1.0.0'
      };

      const createdAgent = await agentRepository.create(agentData);
      const agentId = createdAgent._id.toString();

      // 停用代理
      await agentRepository.updateById(agentId, { activeStatus: false });

      // 验证状态
      const updatedAgent = await agentRepository.findById(agentId);
      expect(updatedAgent?.activeStatus).toBe(false);
    });
  });
}); 