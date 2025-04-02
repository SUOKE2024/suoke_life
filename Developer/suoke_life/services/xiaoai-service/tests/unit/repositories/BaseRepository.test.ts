/**
 * BaseRepository单元测试
 */
import { Document } from 'mongoose';
import { BaseRepository } from '../../../src/repositories/BaseRepository';
import { createMockModel, createMockDocument, clearAllMocks } from '../helpers/mockMongoose';

// 为测试定义一个简单的文档接口
interface ITestDoc extends Document {
  name: string;
  value: number;
}

describe('BaseRepository', () => {
  // 测试数据
  const testDocs = [
    { _id: 'id1', name: 'test1', value: 10 },
    { _id: 'id2', name: 'test2', value: 20 }
  ] as any[];
  
  // 模拟模型和存储库实例
  const mockModel = createMockModel<ITestDoc>(testDocs);
  let repository: BaseRepository<ITestDoc>;
  
  beforeEach(() => {
    clearAllMocks();
    repository = new BaseRepository<ITestDoc>(mockModel);
  });
  
  describe('findById', () => {
    it('应该通过ID查找文档', async () => {
      await repository.findById('id1');
      expect(mockModel.findById).toHaveBeenCalledWith('id1');
    });
    
    it('应该返回找到的文档', async () => {
      const result = await repository.findById('id1');
      expect(result).toEqual(testDocs[0]);
    });
  });
  
  describe('findOne', () => {
    it('应该使用过滤器查找文档', async () => {
      const filter = { name: 'test1' };
      await repository.findOne(filter);
      expect(mockModel.findOne).toHaveBeenCalledWith(filter);
    });
  });
  
  describe('find', () => {
    it('应该使用过滤器和选项查找文档', async () => {
      const filter = { value: { $gt: 15 } };
      const options = { limit: 10, skip: 0 };
      
      await repository.find(filter, options);
      
      expect(mockModel.find).toHaveBeenCalledWith(filter, null, options);
    });
    
    it('应该在没有参数时返回所有文档', async () => {
      await repository.find();
      expect(mockModel.find).toHaveBeenCalledWith({}, null, {});
    });
  });
  
  describe('create', () => {
    it('应该创建新文档', async () => {
      const newDoc = { name: 'new', value: 30 };
      await repository.create(newDoc);
      expect(mockModel.create).toHaveBeenCalledWith(newDoc);
    });
  });
  
  describe('updateById', () => {
    it('应该通过ID更新文档', async () => {
      const update = { $set: { value: 25 } };
      await repository.updateById('id1', update);
      
      expect(mockModel.findByIdAndUpdate).toHaveBeenCalledWith(
        'id1',
        update,
        { new: true }
      );
    });
  });
  
  describe('updateOne', () => {
    it('应该使用过滤器更新单个文档', async () => {
      const filter = { name: 'test1' };
      const update = { $set: { value: 15 } };
      
      await repository.updateOne(filter, update);
      
      expect(mockModel.findOneAndUpdate).toHaveBeenCalledWith(
        filter,
        update,
        { new: true }
      );
    });
  });
  
  describe('updateMany', () => {
    it('应该更新多个文档并返回修改数量', async () => {
      const filter = { value: { $lt: 30 } };
      const update = { $inc: { value: 5 } };
      
      await repository.updateMany(filter, update);
      
      expect(mockModel.updateMany).toHaveBeenCalledWith(filter, update);
    });
  });
  
  describe('deleteById', () => {
    it('应该通过ID删除文档', async () => {
      await repository.deleteById('id1');
      expect(mockModel.findByIdAndDelete).toHaveBeenCalledWith('id1');
    });
    
    it('如果找到并删除文档应该返回true', async () => {
      const result = await repository.deleteById('id1');
      expect(result).toBe(true);
    });
    
    it('如果没有找到文档应该返回false', async () => {
      mockModel.findByIdAndDelete.mockImplementationOnce(() => 
        ({ exec: jest.fn().mockResolvedValue(null) }));
      
      const result = await repository.deleteById('non-existent');
      expect(result).toBe(false);
    });
  });
  
  describe('deleteOne', () => {
    it('应该删除单个文档', async () => {
      const filter = { name: 'test1' };
      await repository.deleteOne(filter);
      expect(mockModel.deleteOne).toHaveBeenCalledWith(filter);
    });
  });
  
  describe('deleteMany', () => {
    it('应该删除多个文档并返回删除数量', async () => {
      const filter = { value: { $gt: 15 } };
      await repository.deleteMany(filter);
      expect(mockModel.deleteMany).toHaveBeenCalledWith(filter);
    });
  });
  
  describe('count', () => {
    it('应该计算符合条件的文档数量', async () => {
      const filter = { value: { $gt: 15 } };
      await repository.count(filter);
      expect(mockModel.countDocuments).toHaveBeenCalledWith(filter);
    });
    
    it('没有过滤器时应该计算所有文档', async () => {
      await repository.count();
      expect(mockModel.countDocuments).toHaveBeenCalledWith({});
    });
  });
  
  describe('exists', () => {
    it('应该检查文档是否存在', async () => {
      const filter = { name: 'test1' };
      
      mockModel.countDocuments.mockImplementationOnce(() => ({
        limit: jest.fn().mockReturnThis(),
        exec: jest.fn().mockResolvedValue(1)
      }));
      
      const result = await repository.exists(filter);
      
      expect(mockModel.countDocuments).toHaveBeenCalledWith(filter);
      expect(result).toBe(true);
    });
    
    it('文档不存在时应该返回false', async () => {
      mockModel.countDocuments.mockImplementationOnce(() => ({
        limit: jest.fn().mockReturnThis(),
        exec: jest.fn().mockResolvedValue(0)
      }));
      
      const result = await repository.exists({ name: 'non-existent' });
      expect(result).toBe(false);
    });
  });
}); 