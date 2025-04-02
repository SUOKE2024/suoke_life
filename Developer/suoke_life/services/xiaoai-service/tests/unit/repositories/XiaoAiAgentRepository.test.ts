import { IXiaoAiAgent } from '../../../src/interfaces/IXiaoAiAgent';
import { XiaoAiAgentRepository } from '../../../src/repositories/XiaoAiAgentRepository';
import { createMockModel, clearAllMocks } from '../helpers/mockMongoose';

jest.mock('../../../src/models/XiaoAiAgent', () => ({
  XiaoAiAgent: createMockModel()
}));

describe('XiaoAiAgentRepository', () => {
  const mockAgents: Partial<IXiaoAiAgent>[] = [
    {
      _id: 'agent1',
      name: '小艾健康顾问',
      description: '专注于健康咨询的AI助手',
      capabilities: ['健康咨询', '体质分析', '饮食建议'],
      personalityTraits: ['专业', '友善', '耐心'],
      activeStatus: true,
      version: '1.0.0',
      modelConfig: {
        model: 'gpt-4',
        temperature: 0.7,
        maxTokens: 2000
      },
      createdAt: new Date(),
      updatedAt: new Date()
    },
    {
      _id: 'agent2',
      name: '小艾营养师',
      description: '专注于饮食营养的AI助手',
      capabilities: ['营养分析', '膳食规划', '食材推荐'],
      personalityTraits: ['专业', '鼓励', '细致'],
      activeStatus: true,
      version: '1.0.0',
      modelConfig: {
        model: 'gpt-4',
        temperature: 0.5,
        maxTokens: 1500
      },
      createdAt: new Date(),
      updatedAt: new Date()
    }
  ];

  let repository: XiaoAiAgentRepository;
  const XiaoAiAgentModel = require('../../../src/models/XiaoAiAgent').XiaoAiAgent;

  beforeEach(() => {
    clearAllMocks();
    repository = new XiaoAiAgentRepository();
    
    // 设置模拟返回值
    XiaoAiAgentModel.find.mockImplementation(() => ({
      exec: jest.fn().mockResolvedValue(mockAgents)
    }));

    XiaoAiAgentModel.findOne.mockImplementation(() => ({
      exec: jest.fn().mockResolvedValue(mockAgents[0])
    }));

    XiaoAiAgentModel.create.mockResolvedValue(mockAgents[0]);
    
    XiaoAiAgentModel.updateOne.mockImplementation(() => ({
      exec: jest.fn().mockResolvedValue({ modifiedCount: 1 })
    }));
  });

  describe('findAll', () => {
    it('应该获取所有代理', async () => {
      const result = await repository.findAll();
      
      expect(XiaoAiAgentModel.find).toHaveBeenCalledWith({});
      expect(result).toEqual(mockAgents);
    });
    
    it('应该只获取活跃的代理，当activeOnly为true', async () => {
      await repository.findAll(true);
      
      expect(XiaoAiAgentModel.find).toHaveBeenCalledWith({ activeStatus: true });
    });
  });

  describe('findById', () => {
    it('应该根据ID查找代理', async () => {
      const agentId = 'agent1';
      
      await repository.findById(agentId);
      
      expect(XiaoAiAgentModel.findOne).toHaveBeenCalledWith({
        _id: agentId
      });
    });
  });

  describe('findByName', () => {
    it('应该根据名称查找代理', async () => {
      const agentName = '小艾健康顾问';
      
      await repository.findByName(agentName);
      
      expect(XiaoAiAgentModel.findOne).toHaveBeenCalledWith({
        name: agentName
      });
    });
  });

  describe('findByCapability', () => {
    it('应该根据能力查找代理', async () => {
      const capability = '健康咨询';
      
      await repository.findByCapability(capability);
      
      expect(XiaoAiAgentModel.find).toHaveBeenCalledWith({
        capabilities: capability,
        activeStatus: true
      });
    });
  });

  describe('create', () => {
    it('应该创建新代理', async () => {
      const agentData: Partial<IXiaoAiAgent> = {
        name: '小艾睡眠顾问',
        description: '专注于睡眠健康的AI助手',
        capabilities: ['睡眠分析', '改善建议'],
        personalityTraits: ['温和', '专业'],
        activeStatus: true,
        version: '1.0.0',
        modelConfig: {
          model: 'gpt-4',
          temperature: 0.6,
          maxTokens: 1800
        }
      };
      
      await repository.create(agentData);
      
      expect(XiaoAiAgentModel.create).toHaveBeenCalledWith(agentData);
    });
  });

  describe('updateById', () => {
    it('应该更新代理信息', async () => {
      const agentId = 'agent1';
      const updateData = { 
        description: '更新后的描述',
        capabilities: ['健康咨询', '体质分析', '饮食建议', '睡眠指导'] 
      };
      
      await repository.updateById(agentId, updateData);
      
      expect(XiaoAiAgentModel.updateOne).toHaveBeenCalledWith(
        { _id: agentId },
        { $set: updateData }
      );
    });
  });

  describe('activateAgent', () => {
    it('应该激活代理', async () => {
      const agentId = 'agent1';
      
      await repository.activateAgent(agentId);
      
      expect(XiaoAiAgentModel.updateOne).toHaveBeenCalledWith(
        { _id: agentId },
        { $set: { activeStatus: true, updatedAt: expect.any(Date) } }
      );
    });
  });

  describe('deactivateAgent', () => {
    it('应该停用代理', async () => {
      const agentId = 'agent1';
      
      await repository.deactivateAgent(agentId);
      
      expect(XiaoAiAgentModel.updateOne).toHaveBeenCalledWith(
        { _id: agentId },
        { $set: { activeStatus: false, updatedAt: expect.any(Date) } }
      );
    });
  });

  describe('updateAgentVersion', () => {
    it('应该更新代理版本', async () => {
      const agentId = 'agent1';
      const newVersion = '1.1.0';
      
      await repository.updateAgentVersion(agentId, newVersion);
      
      expect(XiaoAiAgentModel.updateOne).toHaveBeenCalledWith(
        { _id: agentId },
        { $set: { version: newVersion, updatedAt: expect.any(Date) } }
      );
    });
  });

  describe('countAgents', () => {
    it('应该计算代理数量', async () => {
      const mockCount = 10;
      
      XiaoAiAgentModel.countDocuments.mockImplementation(() => ({
        exec: jest.fn().mockResolvedValue(mockCount)
      }));
      
      const result = await repository.countAgents();
      
      expect(XiaoAiAgentModel.countDocuments).toHaveBeenCalledWith({});
      expect(result).toBe(mockCount);
    });
    
    it('应该只计算活跃代理，当activeOnly为true', async () => {
      const mockCount = 8;
      
      XiaoAiAgentModel.countDocuments.mockImplementation(() => ({
        exec: jest.fn().mockResolvedValue(mockCount)
      }));
      
      await repository.countAgents(true);
      
      expect(XiaoAiAgentModel.countDocuments).toHaveBeenCalledWith({ activeStatus: true });
    });
  });
}); 