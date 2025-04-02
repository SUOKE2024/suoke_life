import mongoose from 'mongoose';
import * as dialectService from '../services/dialect/dialect.service';
import { DialectModel } from '../models/dialect.model';
import { ApiError } from '../core/utils/errors';
import { expect } from 'chai';
import sinon from 'sinon';
import axios from 'axios';

// 创建测试方言数据
const testDialects = [
  {
    code: 'test-canton',
    name: '测试粤语',
    region: '华南',
    description: '测试用粤语方言数据',
    isActive: true,
    supportLevel: 'full',
    features: ['recognition', 'synthesis', 'translation'],
    accuracy: 85
  },
  {
    code: 'test-hakka',
    name: '测试客家话',
    region: '华南',
    description: '测试用客家话方言数据',
    isActive: true,
    supportLevel: 'partial',
    features: ['recognition', 'translation'],
    accuracy: 75
  }
];

describe('方言服务测试', () => {
  before(async () => {
    // 连接测试数据库
    await mongoose.connect(process.env.MONGODB_TEST_URI || 'mongodb://localhost:27017/laoke-test');
    
    // 清空方言集合
    await DialectModel.deleteMany({});
  });
  
  after(async () => {
    // 清空方言集合
    await DialectModel.deleteMany({});
    
    // 关闭数据库连接
    await mongoose.connection.close();
  });
  
  beforeEach(async () => {
    // 每个测试前清空方言集合
    await DialectModel.deleteMany({});
  });
  
  describe('getAllDialects', () => {
    it('应返回所有活动方言', async () => {
      // 创建测试数据
      await DialectModel.create([
        { ...testDialects[0], isActive: true },
        { ...testDialects[1], isActive: true },
        { ...testDialects[0], code: 'inactive-dialect', isActive: false }
      ]);
      
      // 执行测试
      const result = await dialectService.getAllDialects(false);
      
      // 验证结果
      expect(result).to.be.an('array');
      expect(result).to.have.lengthOf(2);
      expect(result[0].isActive).to.be.true;
      expect(result[1].isActive).to.be.true;
    });
    
    it('包含非活动方言时应返回所有方言', async () => {
      // 创建测试数据
      await DialectModel.create([
        { ...testDialects[0], isActive: true },
        { ...testDialects[1], isActive: true },
        { ...testDialects[0], code: 'inactive-dialect', isActive: false }
      ]);
      
      // 执行测试
      const result = await dialectService.getAllDialects(true);
      
      // 验证结果
      expect(result).to.be.an('array');
      expect(result).to.have.lengthOf(3);
    });
  });
  
  describe('getDialectsByRegion', () => {
    it('应按地区分组返回方言', async () => {
      // 创建测试数据
      await DialectModel.create([
        { ...testDialects[0], region: '华南' },
        { ...testDialects[1], region: '华南' },
        { ...testDialects[0], code: 'northeast-dialect', region: '东北', name: '东北话' }
      ]);
      
      // 执行测试
      const result = await dialectService.getDialectsByRegion(true);
      
      // 验证结果
      expect(result).to.be.an('object');
      expect(result).to.have.property('华南');
      expect(result).to.have.property('东北');
      expect(result['华南']).to.have.lengthOf(2);
      expect(result['东北']).to.have.lengthOf(1);
    });
  });
  
  describe('getDialectByCode', () => {
    it('应返回指定代码的方言', async () => {
      // 创建测试数据
      const dialect = await DialectModel.create(testDialects[0]);
      
      // 执行测试
      const result = await dialectService.getDialectByCode(testDialects[0].code);
      
      // 验证结果
      expect(result).to.be.an('object');
      expect(result).to.have.property('code', testDialects[0].code);
      expect(result).to.have.property('name', testDialects[0].name);
    });
    
    it('方言不存在时应返回null', async () => {
      // 执行测试
      const result = await dialectService.getDialectByCode('non-existent');
      
      // 验证结果
      expect(result).to.be.null;
    });
  });
  
  describe('createDialect', () => {
    it('应成功创建新方言', async () => {
      // 执行测试
      const result = await dialectService.createDialect(testDialects[0]);
      
      // 验证结果
      expect(result).to.be.an('object');
      expect(result).to.have.property('code', testDialects[0].code);
      expect(result).to.have.property('name', testDialects[0].name);
      
      // 验证数据库中是否存在
      const savedDialect = await DialectModel.findOne({ code: testDialects[0].code });
      expect(savedDialect).to.exist;
    });
    
    it('创建重复代码的方言时应抛出错误', async () => {
      // 先创建一个方言
      await DialectModel.create(testDialects[0]);
      
      // 执行测试，期望抛出错误
      try {
        await dialectService.createDialect(testDialects[0]);
        expect.fail('应抛出方言代码已存在错误');
      } catch (error) {
        expect(error).to.be.instanceOf(ApiError);
        expect((error as ApiError).statusCode).to.equal(409);
      }
    });
  });
  
  describe('updateDialect', () => {
    it('应成功更新现有方言', async () => {
      // 先创建一个方言
      await DialectModel.create(testDialects[0]);
      
      // 准备更新数据
      const updateData = {
        name: '更新后的粤语',
        description: '这是更新后的描述',
        accuracy: 90
      };
      
      // 执行测试
      const result = await dialectService.updateDialect(testDialects[0].code, updateData);
      
      // 验证结果
      expect(result).to.be.an('object');
      expect(result).to.have.property('code', testDialects[0].code);
      expect(result).to.have.property('name', updateData.name);
      expect(result).to.have.property('description', updateData.description);
      expect(result).to.have.property('accuracy', updateData.accuracy);
    });
    
    it('更新不存在的方言时应抛出错误', async () => {
      // 执行测试，期望抛出错误
      try {
        await dialectService.updateDialect('non-existent', { name: '新名称' });
        expect.fail('应抛出方言不存在错误');
      } catch (error) {
        expect(error).to.be.instanceOf(ApiError);
        expect((error as ApiError).statusCode).to.equal(404);
      }
    });
  });
  
  describe('deleteDialect', () => {
    it('应成功删除现有方言', async () => {
      // 先创建一个方言
      await DialectModel.create(testDialects[0]);
      
      // 执行测试
      const result = await dialectService.deleteDialect(testDialects[0].code);
      
      // 验证结果
      expect(result).to.be.true;
      
      // 验证数据库中是否已删除
      const deletedDialect = await DialectModel.findOne({ code: testDialects[0].code });
      expect(deletedDialect).to.be.null;
    });
    
    it('删除不存在的方言时应抛出错误', async () => {
      // 执行测试，期望抛出错误
      try {
        await dialectService.deleteDialect('non-existent');
        expect.fail('应抛出方言不存在错误');
      } catch (error) {
        expect(error).to.be.instanceOf(ApiError);
        expect((error as ApiError).statusCode).to.equal(404);
      }
    });
  });
  
  describe('detectDialect', () => {
    it('应成功检测音频中的方言', async () => {
      // Mock axios接口
      const axiosStub = sinon.stub(axios, 'post').resolves({
        data: {
          dialect: 'canton',
          confidence: 0.85,
          alternatives: [
            { dialect: 'canton', confidence: 0.85 },
            { dialect: 'hakka', confidence: 0.12 }
          ]
        }
      });
      
      // 执行测试
      const result = await dialectService.detectDialect('https://example.com/audio.webm');
      
      // 验证结果
      expect(result).to.be.an('object');
      expect(result).to.have.property('dialect', 'canton');
      expect(result).to.have.property('confidence', 0.85);
      expect(result).to.have.property('alternatives');
      
      // 恢复stub
      axiosStub.restore();
    });
  });
  
  describe('translateDialectToStandard', () => {
    beforeEach(async () => {
      // 创建测试方言
      await DialectModel.create(testDialects[0]);
    });
    
    it('应成功将方言转换为标准普通话', async () => {
      // Mock axios接口
      const axiosStub = sinon.stub(axios, 'post').resolves({
        data: {
          original: '我喺广州',
          translated: '我在广州',
          dialect: 'canton',
          confidence: 0.95
        }
      });
      
      // 执行测试
      const result = await dialectService.translateDialectToStandard('我喺广州', 'test-canton');
      
      // 验证结果
      expect(result).to.be.an('object');
      expect(result).to.have.property('original', '我喺广州');
      expect(result).to.have.property('translated', '我在广州');
      
      // 恢复stub
      axiosStub.restore();
    });
    
    it('使用不存在的方言代码时应抛出错误', async () => {
      // 执行测试，期望抛出错误
      try {
        await dialectService.translateDialectToStandard('测试文本', 'non-existent');
        expect.fail('应抛出方言不存在错误');
      } catch (error) {
        expect(error).to.be.instanceOf(ApiError);
        expect((error as ApiError).statusCode).to.equal(404);
      }
    });
  });
  
  describe('initializeDefaultDialects', () => {
    it('应成功初始化默认方言数据', async () => {
      // 执行测试
      const result = await dialectService.initializeDefaultDialects();
      
      // 验证结果
      expect(typeof result).to.equal('number');
      expect(result).to.be.at.least(1);
      
      // 验证数据库中是否存在默认方言
      const count = await DialectModel.countDocuments();
      expect(count).to.equal(result);
    });
    
    it('如果已存在方言数据则不重复初始化', async () => {
      // 先创建一个方言
      await DialectModel.create(testDialects[0]);
      
      // 执行测试
      const result = await dialectService.initializeDefaultDialects();
      
      // 验证结果：应该返回undefined或null
      expect(result).to.not.exist;
      
      // 验证数据库中的方言数
      const count = await DialectModel.countDocuments();
      expect(count).to.equal(1);
    });
  });
}); 