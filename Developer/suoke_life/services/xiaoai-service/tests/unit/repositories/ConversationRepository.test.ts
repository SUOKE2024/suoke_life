import { IConversation } from '../../../src/interfaces/IConversation';
import { ConversationRepository } from '../../../src/repositories/ConversationRepository';
import { createMockModel, clearAllMocks } from '../helpers/mockMongoose';

jest.mock('../../../src/models/Conversation', () => ({
  Conversation: createMockModel()
}));

describe('ConversationRepository', () => {
  const mockConversations: Partial<IConversation>[] = [
    {
      _id: 'conv1',
      userId: 'user1',
      title: '健康咨询对话',
      messages: [
        { role: 'user', content: '我最近感觉很疲劳', timestamp: new Date() },
        { role: 'assistant', content: '请详细描述一下您的症状', timestamp: new Date() }
      ],
      createdAt: new Date(),
      updatedAt: new Date(),
      isArchived: false
    },
    {
      _id: 'conv2',
      userId: 'user1',
      title: '饮食咨询',
      messages: [
        { role: 'user', content: '推荐一些适合我体质的食物', timestamp: new Date() },
        { role: 'assistant', content: '根据您的体质情况...', timestamp: new Date() }
      ],
      createdAt: new Date(),
      updatedAt: new Date(),
      isArchived: false
    },
    {
      _id: 'conv3',
      userId: 'user2',
      title: '睡眠问题咨询',
      messages: [
        { role: 'user', content: '我晚上睡不好', timestamp: new Date() },
        { role: 'assistant', content: '请问您是几点入睡？', timestamp: new Date() }
      ],
      createdAt: new Date(),
      updatedAt: new Date(),
      isArchived: true
    }
  ];

  let repository: ConversationRepository;
  const ConversationModel = require('../../../src/models/Conversation').Conversation;

  beforeEach(() => {
    clearAllMocks();
    repository = new ConversationRepository();
    
    // 设置模拟返回值
    ConversationModel.find.mockImplementation(() => ({
      sort: jest.fn().mockReturnThis(),
      skip: jest.fn().mockReturnThis(),
      limit: jest.fn().mockReturnThis(),
      exec: jest.fn().mockResolvedValue(mockConversations)
    }));

    ConversationModel.findOne.mockImplementation(() => ({
      exec: jest.fn().mockResolvedValue(mockConversations[0])
    }));

    ConversationModel.create.mockResolvedValue(mockConversations[0]);
    
    ConversationModel.updateOne.mockImplementation(() => ({
      exec: jest.fn().mockResolvedValue({ modifiedCount: 1 })
    }));
  });

  describe('findByUserId', () => {
    it('应该根据用户ID查找会话', async () => {
      const userId = 'user1';
      const options = { skip: 0, limit: 10, includeArchived: false };
      
      const result = await repository.findByUserId(userId, options);
      
      expect(ConversationModel.find).toHaveBeenCalledWith({
        userId,
        isArchived: false
      });
      expect(result).toEqual(mockConversations);
    });

    it('应该包含已归档的会话，如果includeArchived为true', async () => {
      const userId = 'user1';
      const options = { skip: 0, limit: 10, includeArchived: true };
      
      await repository.findByUserId(userId, options);
      
      expect(ConversationModel.find).toHaveBeenCalledWith({
        userId
      });
    });

    it('应该使用分页参数', async () => {
      const userId = 'user1';
      const options = { skip: 10, limit: 5, includeArchived: false };
      
      const mockSort = jest.fn().mockReturnThis();
      const mockSkip = jest.fn().mockReturnThis();
      const mockLimit = jest.fn().mockReturnThis();
      const mockExec = jest.fn().mockResolvedValue(mockConversations);
      
      ConversationModel.find.mockImplementation(() => ({
        sort: mockSort,
        skip: mockSkip,
        limit: mockLimit,
        exec: mockExec
      }));
      
      await repository.findByUserId(userId, options);
      
      expect(mockSort).toHaveBeenCalledWith({ updatedAt: -1 });
      expect(mockSkip).toHaveBeenCalledWith(10);
      expect(mockLimit).toHaveBeenCalledWith(5);
    });
  });

  describe('findById', () => {
    it('应该根据ID查找会话', async () => {
      const conversationId = 'conv1';
      
      await repository.findById(conversationId);
      
      expect(ConversationModel.findOne).toHaveBeenCalledWith({
        _id: conversationId
      });
    });
  });

  describe('createConversation', () => {
    it('应该创建新会话', async () => {
      const conversationData: Partial<IConversation> = {
        userId: 'user1',
        title: '新的健康咨询',
        messages: []
      };
      
      await repository.create(conversationData);
      
      expect(ConversationModel.create).toHaveBeenCalledWith(conversationData);
    });
  });

  describe('updateConversation', () => {
    it('应该更新会话标题', async () => {
      const conversationId = 'conv1';
      const updateData = { title: '更新后的标题' };
      
      await repository.updateById(conversationId, updateData);
      
      expect(ConversationModel.updateOne).toHaveBeenCalledWith(
        { _id: conversationId },
        { $set: updateData }
      );
    });
    
    it('应该添加消息到会话', async () => {
      const conversationId = 'conv1';
      const newMessage = { role: 'user', content: '新消息', timestamp: new Date() };
      
      await repository.addMessage(conversationId, newMessage);
      
      expect(ConversationModel.updateOne).toHaveBeenCalledWith(
        { _id: conversationId },
        { $push: { messages: newMessage }, $set: { updatedAt: expect.any(Date) } }
      );
    });
  });

  describe('archiveConversation', () => {
    it('应该将会话标记为已归档', async () => {
      const conversationId = 'conv1';
      
      await repository.archiveConversation(conversationId);
      
      expect(ConversationModel.updateOne).toHaveBeenCalledWith(
        { _id: conversationId },
        { $set: { isArchived: true, updatedAt: expect.any(Date) } }
      );
    });
  });

  describe('unarchiveConversation', () => {
    it('应该将会话标记为未归档', async () => {
      const conversationId = 'conv1';
      
      await repository.unarchiveConversation(conversationId);
      
      expect(ConversationModel.updateOne).toHaveBeenCalledWith(
        { _id: conversationId },
        { $set: { isArchived: false, updatedAt: expect.any(Date) } }
      );
    });
  });

  describe('countUserConversations', () => {
    it('应该计算用户会话数', async () => {
      const userId = 'user1';
      const mockCount = 5;
      
      ConversationModel.countDocuments.mockImplementation(() => ({
        exec: jest.fn().mockResolvedValue(mockCount)
      }));
      
      const result = await repository.countUserConversations(userId);
      
      expect(ConversationModel.countDocuments).toHaveBeenCalledWith({
        userId,
        isArchived: false
      });
      expect(result).toBe(mockCount);
    });
  });

  describe('searchConversations', () => {
    it('应该基于关键词搜索会话', async () => {
      const userId = 'user1';
      const keyword = '疲劳';
      
      await repository.searchConversations(userId, keyword);
      
      expect(ConversationModel.find).toHaveBeenCalledWith({
        userId,
        $or: [
          { title: { $regex: keyword, $options: 'i' } },
          { 'messages.content': { $regex: keyword, $options: 'i' } }
        ],
        isArchived: false
      });
    });
  });
}); 