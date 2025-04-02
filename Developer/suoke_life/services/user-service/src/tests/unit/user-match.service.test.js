/**
 * 用户匹配服务单元测试
 */
const chai = require('chai');
const sinon = require('sinon');
const expect = chai.expect;
const sinonChai = require('sinon-chai');
chai.use(sinonChai);

const userMatchService = require('../../services/user-match.service');
const userMatchRepository = require('../../repositories/user-match.repository');
const userRepository = require('../../repositories/user.repository');
const userPreferenceRepository = require('../../repositories/user-preference.repository');
const knowledgePreferenceRepository = require('../../repositories/knowledge-preference.repository');
const userMatchModel = require('../../models/user-match.model');
const { NotFoundError, BadRequestError, UnauthorizedError } = require('../../utils/errors');

describe('用户匹配服务', () => {
  let sandbox;
  
  beforeEach(() => {
    sandbox = sinon.createSandbox();
  });
  
  afterEach(() => {
    sandbox.restore();
  });
  
  describe('createMatch', () => {
    it('应该成功创建用户匹配', async () => {
      // 准备模拟数据
      const userId = 'user-123';
      const matchedUserId = 'user-456';
      const matchData = {
        matchType: userMatchModel.MATCH_TYPES.INTEREST,
        matchScore: 85,
        matchReason: '兴趣相似',
        matchedInterests: ['健康', '中医']
      };
      
      const user = { id: userId, username: 'testuser' };
      const matchedUser = { id: matchedUserId, username: 'matcheduser' };
      const createdMatch = {
        id: 'match-123',
        userId,
        matchedUserId,
        matchType: matchData.matchType,
        matchScore: matchData.matchScore,
        matchReason: matchData.matchReason,
        matchedInterests: matchData.matchedInterests,
        matchStatus: userMatchModel.MATCH_STATUS.PENDING,
        createdAt: new Date()
      };
      
      // 设置存根
      sandbox.stub(userRepository, 'getUserById')
        .withArgs(userId).resolves(user)
        .withArgs(matchedUserId).resolves(matchedUser);
      sandbox.stub(userMatchRepository, 'createMatch').resolves(createdMatch);
      
      // 执行测试
      const result = await userMatchService.createMatch(userId, matchedUserId, matchData);
      
      // 验证结果
      expect(result).to.deep.equal(createdMatch);
      expect(userRepository.getUserById).to.have.been.calledWith(userId);
      expect(userRepository.getUserById).to.have.been.calledWith(matchedUserId);
      expect(userMatchRepository.createMatch).to.have.been.calledOnce;
    });
    
    it('当用户不存在时应该抛出NotFoundError', async () => {
      // 准备模拟数据
      const userId = 'non-existent-user';
      const matchedUserId = 'user-456';
      const matchData = {
        matchType: userMatchModel.MATCH_TYPES.INTEREST,
        matchScore: 85
      };
      
      // 设置存根
      sandbox.stub(userRepository, 'getUserById').resolves(null);
      
      // 执行测试并验证结果
      try {
        await userMatchService.createMatch(userId, matchedUserId, matchData);
        // 如果没有抛出错误，测试应该失败
        expect.fail('应该抛出NotFoundError');
      } catch (error) {
        expect(error).to.be.instanceOf(NotFoundError);
        expect(error.message).to.equal('用户不存在');
      }
    });
    
    it('当匹配用户不存在时应该抛出NotFoundError', async () => {
      // 准备模拟数据
      const userId = 'user-123';
      const matchedUserId = 'non-existent-user';
      const matchData = {
        matchType: userMatchModel.MATCH_TYPES.INTEREST,
        matchScore: 85
      };
      
      const user = { id: userId, username: 'testuser' };
      
      // 设置存根
      sandbox.stub(userRepository, 'getUserById')
        .withArgs(userId).resolves(user)
        .withArgs(matchedUserId).resolves(null);
      
      // 执行测试并验证结果
      try {
        await userMatchService.createMatch(userId, matchedUserId, matchData);
        // 如果没有抛出错误，测试应该失败
        expect.fail('应该抛出NotFoundError');
      } catch (error) {
        expect(error).to.be.instanceOf(NotFoundError);
        expect(error.message).to.equal('被匹配用户不存在');
      }
    });
    
    it('当匹配类型无效时应该抛出BadRequestError', async () => {
      // 准备模拟数据
      const userId = 'user-123';
      const matchedUserId = 'user-456';
      const matchData = {
        matchType: 'invalid-type',
        matchScore: 85
      };
      
      const user = { id: userId, username: 'testuser' };
      const matchedUser = { id: matchedUserId, username: 'matcheduser' };
      
      // 设置存根
      sandbox.stub(userRepository, 'getUserById')
        .withArgs(userId).resolves(user)
        .withArgs(matchedUserId).resolves(matchedUser);
      
      // 执行测试并验证结果
      try {
        await userMatchService.createMatch(userId, matchedUserId, matchData);
        // 如果没有抛出错误，测试应该失败
        expect.fail('应该抛出BadRequestError');
      } catch (error) {
        expect(error).to.be.instanceOf(BadRequestError);
        expect(error.message).to.equal('无效的匹配类型');
      }
    });
    
    it('当匹配分数超出范围时应该抛出BadRequestError', async () => {
      // 准备模拟数据
      const userId = 'user-123';
      const matchedUserId = 'user-456';
      const matchData = {
        matchType: userMatchModel.MATCH_TYPES.INTEREST,
        matchScore: 150 // 超出范围（应该在0-100之间）
      };
      
      const user = { id: userId, username: 'testuser' };
      const matchedUser = { id: matchedUserId, username: 'matcheduser' };
      
      // 设置存根
      sandbox.stub(userRepository, 'getUserById')
        .withArgs(userId).resolves(user)
        .withArgs(matchedUserId).resolves(matchedUser);
      
      // 执行测试并验证结果
      try {
        await userMatchService.createMatch(userId, matchedUserId, matchData);
        // 如果没有抛出错误，测试应该失败
        expect.fail('应该抛出BadRequestError');
      } catch (error) {
        expect(error).to.be.instanceOf(BadRequestError);
        expect(error.message).to.equal('匹配分数必须在0-100之间');
      }
    });
  });
  
  describe('updateMatchStatus', () => {
    it('应该成功更新匹配状态', async () => {
      // 准备模拟数据
      const matchId = 'match-123';
      const userId = 'user-123';
      const status = userMatchModel.MATCH_STATUS.ACCEPTED;
      
      const existingMatch = {
        id: matchId,
        userId,
        matchedUserId: 'user-456',
        matchType: userMatchModel.MATCH_TYPES.INTEREST,
        matchStatus: userMatchModel.MATCH_STATUS.PENDING
      };
      
      const updatedMatch = {
        ...existingMatch,
        matchStatus: status
      };
      
      // 设置存根
      sandbox.stub(userMatchRepository, 'getMatchById')
        .onFirstCall().resolves(existingMatch)
        .onSecondCall().resolves(updatedMatch);
      sandbox.stub(userMatchRepository, 'updateMatch').resolves(true);
      
      // 执行测试
      const result = await userMatchService.updateMatchStatus(matchId, userId, status);
      
      // 验证结果
      expect(result).to.deep.equal(updatedMatch);
      expect(userMatchRepository.getMatchById).to.have.been.calledWith(matchId);
      expect(userMatchRepository.updateMatch).to.have.been.calledWith(matchId, {
        matchStatus: status
      });
    });
    
    it('当匹配记录不存在时应该抛出NotFoundError', async () => {
      // 准备模拟数据
      const matchId = 'non-existent-match';
      const userId = 'user-123';
      const status = userMatchModel.MATCH_STATUS.ACCEPTED;
      
      // 设置存根
      sandbox.stub(userMatchRepository, 'getMatchById').resolves(null);
      
      // 执行测试并验证结果
      try {
        await userMatchService.updateMatchStatus(matchId, userId, status);
        // 如果没有抛出错误，测试应该失败
        expect.fail('应该抛出NotFoundError');
      } catch (error) {
        expect(error).to.be.instanceOf(NotFoundError);
        expect(error.message).to.equal('匹配记录不存在');
      }
    });
    
    it('当用户不是匹配相关者时应该抛出UnauthorizedError', async () => {
      // 准备模拟数据
      const matchId = 'match-123';
      const userId = 'user-789'; // 非相关用户
      const status = userMatchModel.MATCH_STATUS.ACCEPTED;
      
      const existingMatch = {
        id: matchId,
        userId: 'user-123',
        matchedUserId: 'user-456',
        matchType: userMatchModel.MATCH_TYPES.INTEREST,
        matchStatus: userMatchModel.MATCH_STATUS.PENDING
      };
      
      // 设置存根
      sandbox.stub(userMatchRepository, 'getMatchById').resolves(existingMatch);
      
      // 执行测试并验证结果
      try {
        await userMatchService.updateMatchStatus(matchId, userId, status);
        // 如果没有抛出错误，测试应该失败
        expect.fail('应该抛出UnauthorizedError');
      } catch (error) {
        expect(error).to.be.instanceOf(UnauthorizedError);
        expect(error.message).to.equal('无权更新此匹配状态');
      }
    });
    
    it('当状态无效时应该抛出BadRequestError', async () => {
      // 准备模拟数据
      const matchId = 'match-123';
      const userId = 'user-123';
      const status = 'invalid-status';
      
      const existingMatch = {
        id: matchId,
        userId,
        matchedUserId: 'user-456',
        matchType: userMatchModel.MATCH_TYPES.INTEREST,
        matchStatus: userMatchModel.MATCH_STATUS.PENDING
      };
      
      // 设置存根
      sandbox.stub(userMatchRepository, 'getMatchById').resolves(existingMatch);
      
      // 执行测试并验证结果
      try {
        await userMatchService.updateMatchStatus(matchId, userId, status);
        // 如果没有抛出错误，测试应该失败
        expect.fail('应该抛出BadRequestError');
      } catch (error) {
        expect(error).to.be.instanceOf(BadRequestError);
        expect(error.message).to.equal('无效的匹配状态');
      }
    });
  });
  
  describe('calculateUserInterestVector', () => {
    it('应该成功计算用户兴趣向量', async () => {
      // 准备模拟数据
      const userId = 'user-123';
      const user = { id: userId, username: 'testuser' };
      
      const preferences = [
        { id: 'pref-1', userId, preferenceType: 'interest', preferenceKey: 'health', preferenceName: '健康', preferenceValue: 0.8 },
        { id: 'pref-2', userId, preferenceType: 'interest', preferenceKey: 'tcm', preferenceName: '中医', preferenceValue: 0.9 },
        { id: 'pref-3', userId, preferenceType: 'other', preferenceKey: 'sport', preferenceName: '运动', preferenceValue: 0.7 }
      ];
      
      const knowledgePreferences = [
        { id: 'kpref-1', userId, domainId: 'domain-1', domainName: '营养学', preferenceLevel: 3 },
        { id: 'kpref-2', userId, domainId: 'domain-2', domainName: '中药学', preferenceLevel: 4 }
      ];
      
      const storedVector = {
        id: 'vector-123',
        userId,
        vectorType: 'interest',
        vectorData: [
          { type: 'interest', id: 'health', name: '健康', value: 0.8, weight: 0.7 },
          { type: 'interest', id: 'tcm', name: '中医', value: 0.9, weight: 0.7 },
          { type: 'knowledge', id: 'domain-1', name: '营养学', value: 3, weight: 0.5 },
          { type: 'knowledge', id: 'domain-2', name: '中药学', value: 4, weight: 0.5 }
        ],
        metadata: {
          userPreferenceCount: 3,
          knowledgePreferenceCount: 2,
          lastUpdated: sinon.match.string
        },
        createdAt: new Date()
      };
      
      // 设置存根
      sandbox.stub(userRepository, 'getUserById').resolves(user);
      sandbox.stub(userPreferenceRepository, 'getUserPreferences').resolves(preferences);
      sandbox.stub(knowledgePreferenceRepository, 'getUserKnowledgePreferences').resolves(knowledgePreferences);
      sandbox.stub(userMatchRepository, 'storeUserInterestVector').resolves(storedVector);
      
      // 执行测试
      const result = await userMatchService.calculateUserInterestVector(userId);
      
      // 验证结果
      expect(result).to.deep.equal(storedVector);
      expect(userRepository.getUserById).to.have.been.calledWith(userId);
      expect(userPreferenceRepository.getUserPreferences).to.have.been.calledWith(userId);
      expect(knowledgePreferenceRepository.getUserKnowledgePreferences).to.have.been.calledWith(userId);
      expect(userMatchRepository.storeUserInterestVector).to.have.been.calledWith(
        userId,
        'interest',
        sinon.match.array,
        sinon.match.object
      );
    });
    
    it('当用户不存在时应该抛出NotFoundError', async () => {
      // 准备模拟数据
      const userId = 'non-existent-user';
      
      // 设置存根
      sandbox.stub(userRepository, 'getUserById').resolves(null);
      
      // 执行测试并验证结果
      try {
        await userMatchService.calculateUserInterestVector(userId);
        // 如果没有抛出错误，测试应该失败
        expect.fail('应该抛出NotFoundError');
      } catch (error) {
        expect(error).to.be.instanceOf(NotFoundError);
        expect(error.message).to.equal('用户不存在');
      }
    });
  });
  
  describe('createConnection', () => {
    it('应该成功创建用户连接请求', async () => {
      // 准备模拟数据
      const userId = 'user-123';
      const connectedUserId = 'user-456';
      const connectionData = {
        connectionType: userMatchModel.CONNECTION_TYPES.FRIEND,
        matchId: 'match-123',
        message: '想和你交朋友'
      };
      
      const user = { id: userId, username: 'testuser' };
      const connectedUser = { id: connectedUserId, username: 'connecteduser' };
      const createdConnection = {
        id: 'connection-123',
        userId,
        connectedUserId,
        connectionType: connectionData.connectionType,
        initiatedFromMatchId: connectionData.matchId,
        message: connectionData.message,
        connectionStatus: 'pending',
        createdAt: new Date()
      };
      
      // 设置存根
      sandbox.stub(userRepository, 'getUserById')
        .withArgs(userId).resolves(user)
        .withArgs(connectedUserId).resolves(connectedUser);
      sandbox.stub(userMatchRepository, 'createConnection').resolves(createdConnection);
      sandbox.stub(userMatchRepository, 'updateMatch').resolves(true);
      
      // 执行测试
      const result = await userMatchService.createConnection(userId, connectedUserId, connectionData);
      
      // 验证结果
      expect(result).to.deep.equal(createdConnection);
      expect(userRepository.getUserById).to.have.been.calledWith(userId);
      expect(userRepository.getUserById).to.have.been.calledWith(connectedUserId);
      expect(userMatchRepository.createConnection).to.have.been.calledOnce;
      expect(userMatchRepository.updateMatch).to.have.been.calledWith(
        connectionData.matchId,
        { matchStatus: userMatchModel.MATCH_STATUS.CONNECTION_REQUESTED }
      );
    });
  });
});