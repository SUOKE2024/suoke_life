/**
 * UserRepository单元测试
 */
import { IUser } from '../../../src/models/User';
import { UserRepository } from '../../../src/repositories/UserRepository';
import { createMockModel, clearAllMocks } from '../helpers/mockMongoose';

// 模拟User模型
jest.mock('../../../src/models/User', () => {
  const mockModel = createMockModel<any>();
  return {
    __esModule: true,
    default: mockModel,
    IUser: {}
  };
});

// 导入模拟的模型
import User from '../../../src/models/User';

describe('UserRepository', () => {
  // 测试数据
  const testUsers = [
    {
      _id: 'id1',
      userId: 'user1',
      username: 'testuser1',
      email: 'user1@example.com',
      phoneNumber: '13800000001',
      accessibilityPreferences: {
        needsVoiceGuidance: true,
        needsSimplifiedContent: false,
        needsHighContrast: true,
        hasVisualImpairment: true
      },
      dialectPreferences: {
        primary: 'mandarin',
        secondary: 'cantonese',
        autoDetect: true
      },
      lastLogin: new Date('2023-01-01')
    },
    {
      _id: 'id2',
      userId: 'user2',
      username: 'testuser2',
      email: 'user2@example.com',
      phoneNumber: '13800000002',
      accessibilityPreferences: {
        needsVoiceGuidance: false,
        needsSimplifiedContent: true
      },
      dialectPreferences: {
        primary: 'cantonese',
        autoDetect: false
      },
      lastLogin: new Date('2023-01-02')
    }
  ];
  
  let repository: UserRepository;
  const mockUserModel = User as jest.Mocked<any>;
  
  beforeEach(() => {
    clearAllMocks();
    // 重置模拟数据
    mockUserModel.find.mockImplementation(() => ({
      exec: jest.fn().mockResolvedValue(testUsers)
    }));
    mockUserModel.findOne.mockImplementation((filter) => {
      const user = testUsers.find(u => 
        (filter.userId && u.userId === filter.userId) ||
        (filter.username && u.username === filter.username) ||
        (filter.email && u.email === filter.email) ||
        (filter.phoneNumber && u.phoneNumber === filter.phoneNumber)
      );
      return { exec: jest.fn().mockResolvedValue(user || null) };
    });
    mockUserModel.updateOne.mockImplementation(() => ({
      exec: jest.fn().mockResolvedValue({ modifiedCount: 1 })
    }));
    
    repository = new UserRepository();
  });
  
  describe('findByUserId', () => {
    it('应该通过userId查找用户', async () => {
      await repository.findByUserId('user1');
      expect(mockUserModel.findOne).toHaveBeenCalledWith({ userId: 'user1' });
    });
    
    it('应该返回找到的用户', async () => {
      const result = await repository.findByUserId('user1');
      expect(result).toEqual(testUsers[0]);
    });
  });
  
  describe('findByUsername', () => {
    it('应该通过username查找用户', async () => {
      await repository.findByUsername('testuser1');
      expect(mockUserModel.findOne).toHaveBeenCalledWith({ username: 'testuser1' });
    });
  });
  
  describe('findByEmail', () => {
    it('应该通过email查找用户', async () => {
      await repository.findByEmail('user1@example.com');
      expect(mockUserModel.findOne).toHaveBeenCalledWith({ email: 'user1@example.com' });
    });
  });
  
  describe('findByPhoneNumber', () => {
    it('应该通过phoneNumber查找用户', async () => {
      await repository.findByPhoneNumber('13800000001');
      expect(mockUserModel.findOne).toHaveBeenCalledWith({ phoneNumber: '13800000001' });
    });
  });
  
  describe('findUsersWithAccessibilityNeeds', () => {
    it('应该查找有无障碍需求的用户', async () => {
      await repository.findUsersWithAccessibilityNeeds();
      
      expect(mockUserModel.find).toHaveBeenCalledWith({
        $or: expect.arrayContaining([
          { 'accessibilityPreferences.needsVoiceGuidance': true },
          { 'accessibilityPreferences.needsSimplifiedContent': true },
          { 'accessibilityPreferences.needsHighContrast': true },
          { 'accessibilityPreferences.needsScreenReader': true },
          { 'accessibilityPreferences.hasVisualImpairment': true },
          { 'accessibilityPreferences.hasHearingImpairment': true },
          { 'accessibilityPreferences.hasCognitiveImpairment': true },
          { 'accessibilityPreferences.hasMotorImpairment': true },
        ])
      });
    });
  });
  
  describe('findUsersByDialect', () => {
    it('应该查找使用特定方言的用户', async () => {
      await repository.findUsersByDialect('cantonese');
      
      expect(mockUserModel.find).toHaveBeenCalledWith({
        $or: [
          { 'dialectPreferences.primary': 'cantonese' },
          { 'dialectPreferences.secondary': 'cantonese' }
        ]
      });
    });
  });
  
  describe('updateLastLogin', () => {
    it('应该更新用户的最后登录时间', async () => {
      const now = new Date();
      jest.spyOn(global, 'Date').mockImplementationOnce(() => now as any);
      
      await repository.updateLastLogin('user1');
      
      expect(mockUserModel.updateOne).toHaveBeenCalledWith(
        { userId: 'user1' },
        { $set: { lastLogin: now } }
      );
    });
  });
}); 