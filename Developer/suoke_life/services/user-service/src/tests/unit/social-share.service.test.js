/**
 * 社交分享服务单元测试
 */
const chai = require('chai');
const sinon = require('sinon');
const expect = chai.expect;
const sinonChai = require('sinon-chai');
chai.use(sinonChai);

const socialShareService = require('../../services/social-share.service');
const socialShareRepository = require('../../repositories/social-share.repository');
const userRepository = require('../../repositories/user.repository');
const contentRepository = require('../../repositories/content.repository');
const socialShareModel = require('../../models/social-share.model');
const { NotFoundError, BadRequestError, UnauthorizedError } = require('../../utils/errors');

describe('社交分享服务', () => {
  let sandbox;
  
  beforeEach(() => {
    sandbox = sinon.createSandbox();
  });
  
  afterEach(() => {
    sandbox.restore();
  });
  
  describe('createShare', () => {
    it('应该成功创建分享', async () => {
      // 准备模拟数据
      const userId = 'user-123';
      const shareData = {
        shareType: socialShareModel.SHARE_TYPES.CONTENT,
        contentId: 'content-123',
        title: '测试分享',
        description: '测试分享描述',
        platform: socialShareModel.PLATFORMS.WECHAT
      };
      
      const user = { id: userId, username: 'testuser' };
      const content = { id: 'content-123', title: '测试内容', summary: '内容摘要' };
      const createdShare = {
        id: 'share-123',
        userId,
        shareType: shareData.shareType,
        contentId: shareData.contentId,
        title: shareData.title,
        description: shareData.description,
        platform: shareData.platform,
        shareStatus: socialShareModel.SHARE_STATUS.ACTIVE,
        createdAt: new Date()
      };
      
      // 设置存根
      sandbox.stub(userRepository, 'getUserById').resolves(user);
      sandbox.stub(contentRepository, 'getContentById').resolves(content);
      sandbox.stub(socialShareRepository, 'createShare').resolves(createdShare);
      
      // 执行测试
      const result = await socialShareService.createShare(userId, shareData);
      
      // 验证结果
      expect(result).to.deep.equal(createdShare);
      expect(userRepository.getUserById).to.have.been.calledWith(userId);
      expect(contentRepository.getContentById).to.have.been.calledWith(shareData.contentId);
      expect(socialShareRepository.createShare).to.have.been.calledOnce;
    });
    
    it('当用户不存在时应该抛出NotFoundError', async () => {
      // 准备模拟数据
      const userId = 'non-existent-user';
      const shareData = {
        shareType: socialShareModel.SHARE_TYPES.CONTENT,
        contentId: 'content-123',
        title: '测试分享'
      };
      
      // 设置存根
      sandbox.stub(userRepository, 'getUserById').resolves(null);
      
      // 执行测试并验证结果
      try {
        await socialShareService.createShare(userId, shareData);
        // 如果没有抛出错误，测试应该失败
        expect.fail('应该抛出NotFoundError');
      } catch (error) {
        expect(error).to.be.instanceOf(NotFoundError);
        expect(error.message).to.equal('用户不存在');
      }
    });
    
    it('当分享类型无效时应该抛出BadRequestError', async () => {
      // 准备模拟数据
      const userId = 'user-123';
      const shareData = {
        shareType: 'invalid-type',
        contentId: 'content-123',
        title: '测试分享'
      };
      
      const user = { id: userId, username: 'testuser' };
      
      // 设置存根
      sandbox.stub(userRepository, 'getUserById').resolves(user);
      
      // 执行测试并验证结果
      try {
        await socialShareService.createShare(userId, shareData);
        // 如果没有抛出错误，测试应该失败
        expect.fail('应该抛出BadRequestError');
      } catch (error) {
        expect(error).to.be.instanceOf(BadRequestError);
        expect(error.message).to.equal('无效的分享类型');
      }
    });
    
    it('当分享内容不存在时应该抛出NotFoundError', async () => {
      // 准备模拟数据
      const userId = 'user-123';
      const shareData = {
        shareType: socialShareModel.SHARE_TYPES.CONTENT,
        contentId: 'non-existent-content',
        title: '测试分享'
      };
      
      const user = { id: userId, username: 'testuser' };
      
      // 设置存根
      sandbox.stub(userRepository, 'getUserById').resolves(user);
      sandbox.stub(contentRepository, 'getContentById').resolves(null);
      
      // 执行测试并验证结果
      try {
        await socialShareService.createShare(userId, shareData);
        // 如果没有抛出错误，测试应该失败
        expect.fail('应该抛出NotFoundError');
      } catch (error) {
        expect(error).to.be.instanceOf(NotFoundError);
        expect(error.message).to.equal('分享内容不存在');
      }
    });
  });
  
  describe('updateShare', () => {
    it('应该成功更新分享', async () => {
      // 准备模拟数据
      const shareId = 'share-123';
      const userId = 'user-123';
      const updateData = {
        title: '更新的标题',
        description: '更新的描述',
        platform: socialShareModel.PLATFORMS.WEIBO
      };
      
      const existingShare = {
        id: shareId,
        userId,
        shareType: socialShareModel.SHARE_TYPES.CONTENT,
        title: '原标题',
        description: '原描述',
        platform: socialShareModel.PLATFORMS.WECHAT,
        shareStatus: socialShareModel.SHARE_STATUS.ACTIVE
      };
      
      const updatedShare = {
        ...existingShare,
        title: updateData.title,
        description: updateData.description,
        platform: updateData.platform
      };
      
      // 设置存根
      sandbox.stub(socialShareRepository, 'getShareById')
        .onFirstCall().resolves(existingShare)
        .onSecondCall().resolves(updatedShare);
      sandbox.stub(socialShareRepository, 'updateShare').resolves(true);
      
      // 执行测试
      const result = await socialShareService.updateShare(shareId, userId, updateData);
      
      // 验证结果
      expect(result).to.deep.equal(updatedShare);
      expect(socialShareRepository.getShareById).to.have.been.calledWith(shareId);
      expect(socialShareRepository.updateShare).to.have.been.calledWith(shareId, sinon.match({
        title: updateData.title,
        description: updateData.description,
        platform: updateData.platform
      }));
    });
    
    it('当分享不存在时应该抛出NotFoundError', async () => {
      // 准备模拟数据
      const shareId = 'non-existent-share';
      const userId = 'user-123';
      const updateData = { title: '更新的标题' };
      
      // 设置存根
      sandbox.stub(socialShareRepository, 'getShareById').resolves(null);
      
      // 执行测试并验证结果
      try {
        await socialShareService.updateShare(shareId, userId, updateData);
        // 如果没有抛出错误，测试应该失败
        expect.fail('应该抛出NotFoundError');
      } catch (error) {
        expect(error).to.be.instanceOf(NotFoundError);
        expect(error.message).to.equal('分享不存在');
      }
    });
    
    it('当用户不是分享的所有者时应该抛出UnauthorizedError', async () => {
      // 准备模拟数据
      const shareId = 'share-123';
      const userId = 'user-456'; // 不是分享所有者
      const updateData = { title: '更新的标题' };
      
      const existingShare = {
        id: shareId,
        userId: 'user-123', // 不同的用户ID
        shareType: socialShareModel.SHARE_TYPES.CONTENT,
        title: '原标题'
      };
      
      // 设置存根
      sandbox.stub(socialShareRepository, 'getShareById').resolves(existingShare);
      
      // 执行测试并验证结果
      try {
        await socialShareService.updateShare(shareId, userId, updateData);
        // 如果没有抛出错误，测试应该失败
        expect.fail('应该抛出UnauthorizedError');
      } catch (error) {
        expect(error).to.be.instanceOf(UnauthorizedError);
        expect(error.message).to.equal('无权更新分享');
      }
    });
  });
  
  describe('deleteShare', () => {
    it('应该成功删除分享', async () => {
      // 准备模拟数据
      const shareId = 'share-123';
      const userId = 'user-123';
      
      const existingShare = {
        id: shareId,
        userId,
        shareType: socialShareModel.SHARE_TYPES.CONTENT,
        title: '标题'
      };
      
      // 设置存根
      sandbox.stub(socialShareRepository, 'getShareById').resolves(existingShare);
      sandbox.stub(socialShareRepository, 'deleteShare').resolves(true);
      
      // 执行测试
      const result = await socialShareService.deleteShare(shareId, userId);
      
      // 验证结果
      expect(result).to.be.true;
      expect(socialShareRepository.getShareById).to.have.been.calledWith(shareId);
      expect(socialShareRepository.deleteShare).to.have.been.calledWith(shareId, userId);
    });
  });
  
  describe('recordShareInteraction', () => {
    it('应该成功记录分享互动', async () => {
      // 准备模拟数据
      const shareId = 'share-123';
      const interactionUserId = 'user-456';
      const interactionType = socialShareModel.INTERACTION_TYPES.LIKE;
      const interactionData = { comment: '很棒的分享！' };
      
      const existingShare = {
        id: shareId,
        userId: 'user-123',
        shareType: socialShareModel.SHARE_TYPES.CONTENT
      };
      
      const createdInteraction = {
        id: 'interaction-123',
        shareId,
        userId: interactionUserId,
        interactionType,
        interactionData,
        createdAt: new Date()
      };
      
      // 设置存根
      sandbox.stub(socialShareRepository, 'getShareById').resolves(existingShare);
      sandbox.stub(socialShareRepository, 'recordShareInteraction').resolves(createdInteraction);
      sandbox.stub(socialShareRepository, 'updateShareViewCount').resolves();
      sandbox.stub(socialShareRepository, 'updateShareInteractionCount').resolves();
      
      // 执行测试
      const result = await socialShareService.recordShareInteraction(
        shareId,
        interactionUserId,
        interactionType,
        interactionData
      );
      
      // 验证结果
      expect(result).to.deep.equal(createdInteraction);
      expect(socialShareRepository.getShareById).to.have.been.calledWith(shareId);
      expect(socialShareRepository.recordShareInteraction).to.have.been.calledWith({
        shareId,
        userId: interactionUserId,
        interactionType,
        interactionData
      });
      expect(socialShareRepository.updateShareInteractionCount).to.have.been.calledWith(shareId);
      expect(socialShareRepository.updateShareViewCount).to.not.have.been.called;
    });
    
    it('对于查看类型的互动应该更新查看计数', async () => {
      // 准备模拟数据
      const shareId = 'share-123';
      const interactionUserId = 'user-456';
      const interactionType = socialShareModel.INTERACTION_TYPES.VIEW;
      const interactionData = { source: 'wechat' };
      
      const existingShare = {
        id: shareId,
        userId: 'user-123',
        shareType: socialShareModel.SHARE_TYPES.CONTENT
      };
      
      const createdInteraction = {
        id: 'interaction-123',
        shareId,
        userId: interactionUserId,
        interactionType,
        interactionData,
        createdAt: new Date()
      };
      
      // 设置存根
      sandbox.stub(socialShareRepository, 'getShareById').resolves(existingShare);
      sandbox.stub(socialShareRepository, 'recordShareInteraction').resolves(createdInteraction);
      sandbox.stub(socialShareRepository, 'updateShareViewCount').resolves();
      sandbox.stub(socialShareRepository, 'updateShareInteractionCount').resolves();
      
      // 执行测试
      const result = await socialShareService.recordShareInteraction(
        shareId,
        interactionUserId,
        interactionType,
        interactionData
      );
      
      // 验证结果
      expect(result).to.deep.equal(createdInteraction);
      expect(socialShareRepository.updateShareViewCount).to.have.been.calledWith(shareId);
      expect(socialShareRepository.updateShareInteractionCount).to.not.have.been.called;
    });
  });
  
  describe('generateShareLink', () => {
    it('应该生成正确的分享链接', async () => {
      // 准备模拟数据
      const shareId = 'share-123';
      const options = {
        utm_source: 'wechat',
        utm_medium: 'social',
        utm_campaign: 'spring_festival'
      };
      
      const existingShare = {
        id: shareId,
        userId: 'user-123',
        shareType: socialShareModel.SHARE_TYPES.CONTENT,
        platform: socialShareModel.PLATFORMS.WECHAT
      };
      
      // 保存原环境变量并设置测试环境变量
      const oldEnv = process.env.SHARE_BASE_URL;
      process.env.SHARE_BASE_URL = 'https://suoke.life/share';
      
      // 设置存根
      sandbox.stub(socialShareRepository, 'getShareById').resolves(existingShare);
      
      // 执行测试
      const result = await socialShareService.generateShareLink(shareId, options);
      
      // 验证结果
      expect(result).to.equal(
        'https://suoke.life/share?id=share-123&utm_source=wechat&utm_medium=social&utm_campaign=spring_festival&platform=wechat'
      );
      
      // 恢复环境变量
      if (oldEnv === undefined) {
        delete process.env.SHARE_BASE_URL;
      } else {
        process.env.SHARE_BASE_URL = oldEnv;
      }
    });
  });
});