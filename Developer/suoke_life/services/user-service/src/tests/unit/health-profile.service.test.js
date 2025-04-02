/**
 * 健康档案服务单元测试
 */
const { BusinessError } = require('@suoke/shared').utils;
const { expect } = require('@jest/globals');
const HealthProfileService = require('../../services/health-profile.service');

describe('健康档案服务单元测试', () => {
  let healthProfileService;
  let mockHealthProfileRepository;
  const testUserId = '12345';
  
  beforeEach(() => {
    // 创建模拟仓库
    mockHealthProfileRepository = {
      findByUserId: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
      delete: jest.fn()
    };
    
    // 替换服务中的仓库依赖
    healthProfileService = new HealthProfileService();
    healthProfileService.healthProfileRepository = mockHealthProfileRepository;
  });

  describe('createHealthProfile', () => {
    it('应该创建健康档案', async () => {
      // 模拟用户没有现有健康档案
      mockHealthProfileRepository.findByUserId.mockResolvedValue(null);
      
      const testData = {
        height: 175,
        weight: 70,
        bloodType: 'A',
        allergies: ['花粉']
      };
      
      const expectedProfile = {
        id: 'profile-id',
        userId: testUserId,
        ...testData,
        createdAt: new Date(),
        updatedAt: new Date()
      };
      
      // 模拟创建成功
      mockHealthProfileRepository.create.mockResolvedValue(expectedProfile);
      
      // 调用测试方法
      const result = await healthProfileService.createHealthProfile(testData, testUserId);
      
      // 验证结果
      expect(mockHealthProfileRepository.findByUserId.calledWith(testUserId)).to.be.true;
      expect(mockHealthProfileRepository.create.calledOnce).to.be.true;
      expect(result).to.deep.equal(expectedProfile);
    });
    
    it('用户已有健康档案时应抛出409错误', async () => {
      // 模拟用户已有健康档案
      mockHealthProfileRepository.findByUserId.mockResolvedValue({
        id: 'existing-profile-id',
        userId: testUserId
      });

      await expect(healthProfileService.createHealthProfile({}, testUserId))
        .rejects.toThrow(BusinessError);
      
      const error = await healthProfileService.createHealthProfile({}, testUserId).catch(e => e);
      expect(error.statusCode).toBe(409);
      expect(error.message).toContain('已存在健康档案');
    });
  });

  describe('getHealthProfileByUserId', () => {
    it('应该返回用户的健康档案', async () => {
      const expectedProfile = {
        id: 'profile-id',
        userId: testUserId,
        height: 175,
        weight: 70
      };
      
      // 模拟找到健康档案
      mockHealthProfileRepository.findByUserId.mockResolvedValue(expectedProfile);
      
      // 调用测试方法
      const result = await healthProfileService.getHealthProfileByUserId(testUserId);
      
      // 验证结果
      expect(result).toEqual(expectedProfile);
      expect(mockHealthProfileRepository.findByUserId).toHaveBeenCalledWith(testUserId);
    });
    
    it('健康档案不存在时应抛出404错误', async () => {
      // 模拟健康档案不存在
      mockHealthProfileRepository.findByUserId.mockResolvedValue(null);

      await expect(healthProfileService.getHealthProfileByUserId(testUserId))
        .rejects.toThrow(BusinessError);
      
      const error = await healthProfileService.getHealthProfileByUserId(testUserId).catch(e => e);
      expect(error.statusCode).toBe(404);
      expect(error.message).toContain('未找到健康档案');
    });
  });

  describe('updateHealthProfile', () => {
    it('应该更新健康档案', async () => {
      const existingProfile = {
        id: 'profile-id',
        userId: testUserId,
        height: 175,
        weight: 70
      };
      
      const updateData = {
        weight: 68,
        bloodPressure: '120/80'
      };
      
      const updatedProfile = {
        ...existingProfile,
        ...updateData,
        updatedAt: new Date()
      };
      
      // 模拟找到健康档案
      mockHealthProfileRepository.findByUserId.mockResolvedValue(existingProfile);
      // 模拟更新成功
      mockHealthProfileRepository.update.mockResolvedValue(updatedProfile);
      
      // 调用测试方法
      const result = await healthProfileService.updateHealthProfile(testUserId, updateData);
      
      // 验证结果
      expect(mockHealthProfileRepository.findByUserId).toHaveBeenCalledWith(testUserId);
      expect(mockHealthProfileRepository.update).toHaveBeenCalledWith(existingProfile.id, updateData);
      expect(result).toEqual(updatedProfile);
    });
    
    it('健康档案不存在时应抛出404错误', async () => {
      // 模拟健康档案不存在
      mockHealthProfileRepository.findByUserId.withArgs(testUserId).resolves(null);
      
      try {
        await healthProfileService.updateHealthProfile(testUserId, {});
        // 如果没有抛出错误，测试应该失败
        expect.fail('应该抛出错误');
      } catch (error) {
        expect(error).to.be.instanceOf(BusinessError);
        expect(error.statusCode).to.equal(404);
        expect(error.message).to.include('未找到健康档案');
      }
    });
  });

  describe('deleteHealthProfile', () => {
    it('应该删除健康档案', async () => {
      const existingProfile = {
        id: 'profile-id',
        userId: testUserId
      };
      
      // 模拟找到健康档案
      mockHealthProfileRepository.findByUserId.mockResolvedValue(existingProfile);
      // 模拟删除成功
      mockHealthProfileRepository.delete.mockResolvedValue(true);
      
      // 调用测试方法
      const result = await healthProfileService.deleteHealthProfile(testUserId);
      
      // 验证结果
      expect(mockHealthProfileRepository.findByUserId).toHaveBeenCalledWith(testUserId);
      expect(mockHealthProfileRepository.delete).toHaveBeenCalledWith(existingProfile.id);
      expect(result).toBe(true);
    });
    
    it('健康档案不存在时应抛出404错误', async () => {
      // 模拟健康档案不存在
      mockHealthProfileRepository.findByUserId.withArgs(testUserId).resolves(null);
      
      try {
        await healthProfileService.deleteHealthProfile(testUserId);
        // 如果没有抛出错误，测试应该失败
        expect.fail('应该抛出错误');
      } catch (error) {
        expect(error).to.be.instanceOf(BusinessError);
        expect(error.statusCode).to.equal(404);
        expect(error.message).to.include('未找到健康档案');
      }
    });
  });

  describe('体质测评功能', () => {
    describe('getConstitutionAssessment', () => {
      it('应该返回体质测评结果', async () => {
        const assessment = {
          constitutionType: '平和质',
          score: 85,
          date: new Date().toISOString()
        };
        
        // 模拟找到带有体质测评的健康档案
        mockHealthProfileRepository.findByUserId.mockResolvedValue({
          id: 'profile-id',
          userId: testUserId,
          constitutionAssessment: assessment
        });
        
        // 调用测试方法
        const result = await healthProfileService.getConstitutionAssessment(testUserId);
        
        // 验证结果
        expect(result).toEqual(assessment);
      });
      
      it('体质测评数据不存在时应抛出404错误', async () => {
        // 模拟健康档案存在但没有体质测评数据
        mockHealthProfileRepository.findByUserId.mockResolvedValue({
          id: 'profile-id',
          userId: testUserId
        });

        await expect(healthProfileService.getConstitutionAssessment(testUserId))
          .rejects.toThrow(BusinessError);
        
        const error = await healthProfileService.getConstitutionAssessment(testUserId).catch(e => e);
        expect(error.statusCode).toBe(404);
        expect(error.message).toContain('未找到体质测评数据');
      });
    });

    describe('saveConstitutionAssessment', () => {
      it('已有健康档案时应该更新体质测评结果', async () => {
        const existingProfile = {
          id: 'profile-id',
          userId: testUserId
        };
        
        const assessmentData = {
          constitutionType: '平和质',
          score: 85,
          date: new Date().toISOString()
        };
        
        const updatedProfile = {
          ...existingProfile,
          constitutionAssessment: assessmentData,
          updatedAt: new Date()
        };
        
        // 模拟找到健康档案
        mockHealthProfileRepository.findByUserId.withArgs(testUserId).resolves(existingProfile);
        // 模拟更新成功
        mockHealthProfileRepository.update.resolves(updatedProfile);
        
        // 调用测试方法
        const result = await healthProfileService.saveConstitutionAssessment(testUserId, assessmentData);
        
        // 验证结果
        expect(mockHealthProfileRepository.update.calledWith(existingProfile.id, {
          constitutionAssessment: assessmentData
        })).to.be.true;
        expect(result).to.deep.equal(updatedProfile);
      });
      
      it('没有健康档案时应该创建新的健康档案', async () => {
        // 模拟健康档案不存在
        mockHealthProfileRepository.findByUserId.withArgs(testUserId).resolves(null);
        
        const assessmentData = {
          constitutionType: '平和质',
          score: 85,
          date: new Date().toISOString()
        };
        
        const newProfile = {
          id: 'new-profile-id',
          userId: testUserId,
          constitutionAssessment: assessmentData,
          createdAt: new Date(),
          updatedAt: new Date()
        };
        
        // 模拟创建成功
        mockHealthProfileRepository.create.resolves(newProfile);
        
        // 调用测试方法
        const result = await healthProfileService.saveConstitutionAssessment(testUserId, assessmentData);
        
        // 验证结果
        expect(mockHealthProfileRepository.create.calledWith({
          userId: testUserId,
          constitutionAssessment: assessmentData
        })).to.be.true;
        expect(result).to.deep.equal(newProfile);
      });
    });
  });
});
