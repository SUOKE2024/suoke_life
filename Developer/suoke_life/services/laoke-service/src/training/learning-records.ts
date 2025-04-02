/**
 * 学习记录服务
 * 负责用户学习记录的管理和跟踪
 */
import {
  UserLearningRecord,
  NodeProgress,
  ResourceProgress,
  QuizAttempt,
  QuestionAnswer,
  LearningNote,
  Certification,
  LearningStatus,
  CertificationType
} from './types';
import { logger } from '../utils/logger';
import pathManagement from './path-management';

class LearningRecords {
  // 模拟数据存储
  private recordsStore: Map<string, UserLearningRecord> = new Map();
  private certificationsStore: Map<string, Certification> = new Map();
  
  /**
   * 构造函数
   */
  constructor() {
    logger.info('学习记录服务初始化');
  }
  
  /**
   * 创建或获取用户学习记录
   * @param userId 用户ID
   * @param pathId 路径ID
   * @returns 学习记录
   */
  public async getOrCreateUserRecord(
    userId: string,
    pathId: string
  ): Promise<UserLearningRecord> {
    // 检查路径是否存在
    const path = await pathManagement.getPath(pathId);
    if (!path) {
      throw new Error(`学习路径不存在: ${pathId}`);
    }
    
    // 查找现有记录
    const existingRecord = await this.findUserRecord(userId, pathId);
    if (existingRecord) {
      return existingRecord;
    }
    
    // 创建新记录
    const recordId = `record-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    const now = new Date();
    
    // 初始化节点进度
    const nodeProgress: NodeProgress[] = path.nodes.map(node => ({
      nodeId: node.id,
      status: LearningStatus.NOT_STARTED,
      completionPercentage: 0,
      learningTime: 0,
      resourceProgress: node.resources.map(resource => ({
        resourceId: resource.id,
        status: LearningStatus.NOT_STARTED,
        completionPercentage: 0,
        learningTime: 0,
        lastActivityAt: now
      })),
      lastActivityAt: now
    }));
    
    const newRecord: UserLearningRecord = {
      id: recordId,
      userId,
      pathId,
      status: LearningStatus.NOT_STARTED,
      startedAt: now,
      lastActivityAt: now,
      totalLearningTime: 0,
      nodeProgress,
      quizAttempts: [],
      earnedBadgeIds: [],
      notes: []
    };
    
    this.recordsStore.set(recordId, newRecord);
    
    // 更新路径学习人数
    await this.incrementPathEnrollment(pathId);
    
    logger.info(`创建用户学习记录: ${recordId}`, {
      userId,
      pathId
    });
    
    return newRecord;
  }
  
  /**
   * 查找用户学习记录
   * @param userId 用户ID
   * @param pathId 路径ID
   * @returns 学习记录或null
   */
  public async findUserRecord(
    userId: string,
    pathId: string
  ): Promise<UserLearningRecord | null> {
    const records = Array.from(this.recordsStore.values())
      .filter(record => record.userId === userId && record.pathId === pathId);
    
    if (records.length === 0) {
      return null;
    }
    
    return records[0];
  }
  
  /**
   * 获取用户所有学习记录
   * @param userId 用户ID
   * @returns 学习记录列表
   */
  public async getUserRecords(userId: string): Promise<UserLearningRecord[]> {
    const records = Array.from(this.recordsStore.values())
      .filter(record => record.userId === userId);
    
    logger.info(`获取用户学习记录列表`, {
      userId,
      count: records.length
    });
    
    return records;
  }
  
  /**
   * 获取路径所有学习记录
   * @param pathId 路径ID
   * @returns 学习记录列表
   */
  public async getPathRecords(pathId: string): Promise<UserLearningRecord[]> {
    const records = Array.from(this.recordsStore.values())
      .filter(record => record.pathId === pathId);
    
    logger.info(`获取路径学习记录列表`, {
      pathId,
      count: records.length
    });
    
    return records;
  }
  
  /**
   * 更新用户学习进度
   * @param recordId 记录ID
   * @param nodeId 节点ID
   * @param resourceId 资源ID
   * @param progress 进度百分比
   * @param learningTime 学习时间(分钟)
   * @param position 位置标记
   * @returns 是否更新成功
   */
  public async updateProgress(
    recordId: string,
    nodeId: string,
    resourceId: string,
    progress: number,
    learningTime: number,
    position?: number
  ): Promise<boolean> {
    if (!this.recordsStore.has(recordId)) {
      logger.warn(`更新失败，学习记录不存在: ${recordId}`);
      return false;
    }
    
    const record = this.recordsStore.get(recordId)!;
    const now = new Date();
    
    // 查找节点进度
    const nodeIndex = record.nodeProgress.findIndex(np => np.nodeId === nodeId);
    if (nodeIndex === -1) {
      logger.warn(`更新失败，节点不存在: ${nodeId}`);
      return false;
    }
    
    // 查找资源进度
    const nodeProgress = record.nodeProgress[nodeIndex];
    const resourceIndex = nodeProgress.resourceProgress.findIndex(rp => rp.resourceId === resourceId);
    if (resourceIndex === -1) {
      logger.warn(`更新失败，资源不存在: ${resourceId}`);
      return false;
    }
    
    // 限制进度在0-100范围内
    const safeProgress = Math.max(0, Math.min(100, progress));
    
    // 更新资源进度
    const resourceProgress = nodeProgress.resourceProgress[resourceIndex];
    const updatedResourceProgress: ResourceProgress = {
      ...resourceProgress,
      completionPercentage: safeProgress,
      learningTime: resourceProgress.learningTime + learningTime,
      position,
      lastActivityAt: now
    };
    
    // 更新资源状态
    if (safeProgress === 0) {
      updatedResourceProgress.status = LearningStatus.NOT_STARTED;
    } else if (safeProgress < 100) {
      updatedResourceProgress.status = LearningStatus.IN_PROGRESS;
    } else {
      updatedResourceProgress.status = LearningStatus.COMPLETED;
    }
    
    // 更新节点资源进度
    const updatedResourceProgressList = [...nodeProgress.resourceProgress];
    updatedResourceProgressList[resourceIndex] = updatedResourceProgress;
    
    // 计算节点整体进度
    const totalResources = updatedResourceProgressList.length;
    const nodeCompletionPercentage = totalResources > 0
      ? updatedResourceProgressList.reduce((sum, rp) => sum + rp.completionPercentage, 0) / totalResources
      : 0;
      
    // 计算节点总学习时间
    const nodeLearningTime = updatedResourceProgressList.reduce((sum, rp) => sum + rp.learningTime, 0);
    
    // 更新节点状态
    let nodeStatus = LearningStatus.NOT_STARTED;
    if (nodeCompletionPercentage === 100) {
      nodeStatus = LearningStatus.COMPLETED;
    } else if (nodeCompletionPercentage > 0) {
      nodeStatus = LearningStatus.IN_PROGRESS;
    }
    
    // 更新节点进度
    const updatedNodeProgress: NodeProgress = {
      ...nodeProgress,
      status: nodeStatus,
      completionPercentage: nodeCompletionPercentage,
      learningTime: nodeLearningTime,
      resourceProgress: updatedResourceProgressList,
      lastActivityAt: now
    };
    
    // 更新节点列表
    const updatedNodeProgressList = [...record.nodeProgress];
    updatedNodeProgressList[nodeIndex] = updatedNodeProgress;
    
    // 计算总体进度
    const totalNodes = updatedNodeProgressList.length;
    const overallCompletionPercentage = totalNodes > 0
      ? updatedNodeProgressList.reduce((sum, np) => sum + np.completionPercentage, 0) / totalNodes
      : 0;
      
    // 计算总学习时间
    const totalLearningTime = updatedNodeProgressList.reduce((sum, np) => sum + np.learningTime, 0);
    
    // 更新总体状态
    let overallStatus = LearningStatus.NOT_STARTED;
    if (overallCompletionPercentage === 100) {
      overallStatus = LearningStatus.COMPLETED;
    } else if (overallCompletionPercentage > 0) {
      overallStatus = LearningStatus.IN_PROGRESS;
    }
    
    // 如果状态从其他状态变为已完成，记录完成时间
    let completedAt = record.completedAt;
    if (overallStatus === LearningStatus.COMPLETED && record.status !== LearningStatus.COMPLETED) {
      completedAt = now;
      // 更新路径完成人数
      await this.incrementPathCompletion(record.pathId);
    }
    
    // 更新整体记录
    const updatedRecord: UserLearningRecord = {
      ...record,
      status: overallStatus,
      lastActivityAt: now,
      completedAt,
      totalLearningTime,
      nodeProgress: updatedNodeProgressList
    };
    
    this.recordsStore.set(recordId, updatedRecord);
    
    logger.info(`更新学习进度`, {
      recordId,
      nodeId,
      resourceId,
      progress: safeProgress,
      learningTime,
      overallProgress: overallCompletionPercentage
    });
    
    return true;
  }
  
  /**
   * 记录测验尝试
   * @param recordId 记录ID
   * @param quizAttempt 测验尝试
   * @returns 是否记录成功
   */
  public async recordQuizAttempt(
    recordId: string,
    quizAttempt: Omit<QuizAttempt, 'id'>
  ): Promise<boolean> {
    if (!this.recordsStore.has(recordId)) {
      logger.warn(`记录失败，学习记录不存在: ${recordId}`);
      return false;
    }
    
    const record = this.recordsStore.get(recordId)!;
    
    const attemptId = `attempt-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    
    const newAttempt: QuizAttempt = {
      ...quizAttempt,
      id: attemptId
    };
    
    // 添加尝试记录
    const updatedRecord: UserLearningRecord = {
      ...record,
      quizAttempts: [...record.quizAttempts, newAttempt],
      lastActivityAt: new Date()
    };
    
    this.recordsStore.set(recordId, updatedRecord);
    
    logger.info(`记录测验尝试: ${attemptId}`, {
      recordId,
      quizId: quizAttempt.quizId,
      score: quizAttempt.score,
      percentage: quizAttempt.percentage,
      passed: quizAttempt.passed
    });
    
    return true;
  }
  
  /**
   * 添加学习笔记
   * @param recordId 记录ID
   * @param note 学习笔记
   * @returns 笔记ID
   */
  public async addNote(
    recordId: string,
    note: Omit<LearningNote, 'id' | 'createdAt' | 'updatedAt'>
  ): Promise<string> {
    if (!this.recordsStore.has(recordId)) {
      throw new Error(`学习记录不存在: ${recordId}`);
    }
    
    const record = this.recordsStore.get(recordId)!;
    const now = new Date();
    
    const noteId = `note-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    
    const newNote: LearningNote = {
      ...note,
      id: noteId,
      createdAt: now,
      updatedAt: now
    };
    
    // 添加笔记
    const updatedRecord: UserLearningRecord = {
      ...record,
      notes: [...record.notes, newNote],
      lastActivityAt: now
    };
    
    this.recordsStore.set(recordId, updatedRecord);
    
    logger.info(`添加学习笔记: ${noteId}`, {
      recordId,
      nodeId: note.nodeId,
      resourceId: note.resourceId
    });
    
    return noteId;
  }
  
  /**
   * 更新学习笔记
   * @param recordId 记录ID
   * @param noteId 笔记ID
   * @param updates 更新内容
   * @returns 是否更新成功
   */
  public async updateNote(
    recordId: string,
    noteId: string,
    updates: Partial<Omit<LearningNote, 'id' | 'createdAt' | 'updatedAt'>>
  ): Promise<boolean> {
    if (!this.recordsStore.has(recordId)) {
      logger.warn(`更新失败，学习记录不存在: ${recordId}`);
      return false;
    }
    
    const record = this.recordsStore.get(recordId)!;
    const now = new Date();
    
    // 查找笔记
    const noteIndex = record.notes.findIndex(note => note.id === noteId);
    if (noteIndex === -1) {
      logger.warn(`更新失败，笔记不存在: ${noteId}`);
      return false;
    }
    
    // 更新笔记
    const updatedNotes = [...record.notes];
    updatedNotes[noteIndex] = {
      ...updatedNotes[noteIndex],
      ...updates,
      updatedAt: now
    };
    
    // 更新记录
    const updatedRecord: UserLearningRecord = {
      ...record,
      notes: updatedNotes,
      lastActivityAt: now
    };
    
    this.recordsStore.set(recordId, updatedRecord);
    
    logger.info(`更新学习笔记: ${noteId}`, {
      recordId
    });
    
    return true;
  }
  
  /**
   * 删除学习笔记
   * @param recordId 记录ID
   * @param noteId 笔记ID
   * @returns 是否删除成功
   */
  public async deleteNote(
    recordId: string,
    noteId: string
  ): Promise<boolean> {
    if (!this.recordsStore.has(recordId)) {
      logger.warn(`删除失败，学习记录不存在: ${recordId}`);
      return false;
    }
    
    const record = this.recordsStore.get(recordId)!;
    
    // 查找笔记
    const noteIndex = record.notes.findIndex(note => note.id === noteId);
    if (noteIndex === -1) {
      logger.warn(`删除失败，笔记不存在: ${noteId}`);
      return false;
    }
    
    // 删除笔记
    const updatedNotes = record.notes.filter(note => note.id !== noteId);
    
    // 更新记录
    const updatedRecord: UserLearningRecord = {
      ...record,
      notes: updatedNotes,
      lastActivityAt: new Date()
    };
    
    this.recordsStore.set(recordId, updatedRecord);
    
    logger.info(`删除学习笔记: ${noteId}`, {
      recordId
    });
    
    return true;
  }
  
  /**
   * 授予徽章
   * @param recordId 记录ID
   * @param badgeId 徽章ID
   * @returns 是否授予成功
   */
  public async awardBadge(
    recordId: string,
    badgeId: string
  ): Promise<boolean> {
    if (!this.recordsStore.has(recordId)) {
      logger.warn(`授予失败，学习记录不存在: ${recordId}`);
      return false;
    }
    
    const record = this.recordsStore.get(recordId)!;
    
    // 检查是否已有该徽章
    if (record.earnedBadgeIds.includes(badgeId)) {
      logger.info(`用户已拥有徽章: ${badgeId}`);
      return true;
    }
    
    // 检查徽章是否存在
    const badge = await pathManagement.getBadge(badgeId);
    if (!badge) {
      logger.warn(`授予失败，徽章不存在: ${badgeId}`);
      return false;
    }
    
    // 更新徽章获得数量
    await pathManagement.updateBadge(badgeId, {
      ...badge,
      earnedCount: badge.earnedCount + 1
    });
    
    // 授予徽章
    const updatedRecord: UserLearningRecord = {
      ...record,
      earnedBadgeIds: [...record.earnedBadgeIds, badgeId],
      lastActivityAt: new Date()
    };
    
    this.recordsStore.set(recordId, updatedRecord);
    
    logger.info(`授予徽章: ${badgeId}`, {
      recordId,
      userId: record.userId,
      pathId: record.pathId
    });
    
    return true;
  }
  
  /**
   * 创建认证
   * @param userId 用户ID
   * @param pathId 路径ID
   * @param certification 认证信息
   * @returns 认证ID
   */
  public async createCertification(
    userId: string,
    pathId: string,
    certification: Omit<Certification, 'id' | 'userId' | 'pathId' | 'issuedAt'>
  ): Promise<string> {
    // 检查路径是否存在
    const path = await pathManagement.getPath(pathId);
    if (!path) {
      throw new Error(`学习路径不存在: ${pathId}`);
    }
    
    // 检查用户是否完成了路径
    const record = await this.findUserRecord(userId, pathId);
    if (!record || record.status !== LearningStatus.COMPLETED) {
      throw new Error(`用户未完成学习路径: ${pathId}`);
    }
    
    const certId = `cert-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    const now = new Date();
    
    const newCertification: Certification = {
      ...certification,
      id: certId,
      userId,
      pathId,
      issuedAt: now
    };
    
    this.certificationsStore.set(certId, newCertification);
    
    // 更新学习记录
    if (record) {
      const updatedRecord: UserLearningRecord = {
        ...record,
        certificationId: certId,
        lastActivityAt: now
      };
      
      this.recordsStore.set(record.id, updatedRecord);
    }
    
    logger.info(`创建认证: ${certId}`, {
      userId,
      pathId,
      type: certification.type
    });
    
    return certId;
  }
  
  /**
   * 获取用户认证
   * @param userId 用户ID
   * @returns 认证列表
   */
  public async getUserCertifications(userId: string): Promise<Certification[]> {
    const certifications = Array.from(this.certificationsStore.values())
      .filter(cert => cert.userId === userId);
    
    logger.info(`获取用户认证列表`, {
      userId,
      count: certifications.length
    });
    
    return certifications;
  }
  
  /**
   * 验证认证
   * @param id 认证ID
   * @returns 认证信息或null
   */
  public async verifyCertification(id: string): Promise<Certification | null> {
    if (!this.certificationsStore.has(id)) {
      logger.warn(`验证失败，认证不存在: ${id}`);
      return null;
    }
    
    const certification = this.certificationsStore.get(id)!;
    
    // 更新为已验证
    const updatedCertification: Certification = {
      ...certification,
      verified: true
    };
    
    this.certificationsStore.set(id, updatedCertification);
    
    logger.info(`验证认证: ${id}`, {
      userId: certification.userId,
      pathId: certification.pathId,
      type: certification.type
    });
    
    return updatedCertification;
  }
  
  /**
   * 获取用户完成的学习路径ID列表
   * @param userId 用户ID
   * @returns 路径ID列表
   */
  public async getUserCompletedPaths(userId: string): Promise<string[]> {
    const records = await this.getUserRecords(userId);
    
    const completedPathIds = records
      .filter(record => record.status === LearningStatus.COMPLETED)
      .map(record => record.pathId);
    
    logger.info(`获取用户完成的学习路径列表`, {
      userId,
      count: completedPathIds.length
    });
    
    return completedPathIds;
  }
  
  /**
   * 获取用户学习统计
   * @param userId 用户ID
   * @returns 学习统计
   */
  public async getUserLearningStats(userId: string): Promise<{
    totalPaths: number;
    completedPaths: number;
    inProgressPaths: number;
    totalLearningTime: number;
    quizAttempts: number;
    quizPassed: number;
    badgesEarned: number;
    certificationsEarned: number;
    notesCount: number;
  }> {
    const records = await this.getUserRecords(userId);
    const certifications = await this.getUserCertifications(userId);
    
    // 计算统计信息
    const totalPaths = records.length;
    const completedPaths = records.filter(r => r.status === LearningStatus.COMPLETED).length;
    const inProgressPaths = records.filter(r => r.status === LearningStatus.IN_PROGRESS).length;
    const totalLearningTime = records.reduce((sum, r) => sum + r.totalLearningTime, 0);
    
    // 计算测验统计
    const quizAttempts = records.reduce((sum, r) => sum + r.quizAttempts.length, 0);
    const quizPassed = records.reduce((sum, r) => sum + r.quizAttempts.filter(a => a.passed).length, 0);
    
    // 徽章和笔记统计
    const badgesEarned = records.reduce((sum, r) => sum + r.earnedBadgeIds.length, 0);
    const notesCount = records.reduce((sum, r) => sum + r.notes.length, 0);
    
    // 认证统计
    const certificationsEarned = certifications.length;
    
    logger.info(`获取用户学习统计`, {
      userId,
      totalPaths,
      completedPaths,
      totalLearningTime
    });
    
    return {
      totalPaths,
      completedPaths,
      inProgressPaths,
      totalLearningTime,
      quizAttempts,
      quizPassed,
      badgesEarned,
      certificationsEarned,
      notesCount
    };
  }
  
  /**
   * 增加路径学习人数
   * @param pathId 路径ID
   */
  private async incrementPathEnrollment(pathId: string): Promise<void> {
    const path = await pathManagement.getPath(pathId);
    if (path) {
      await pathManagement.updatePath(pathId, {
        enrollmentCount: path.enrollmentCount + 1
      });
    }
  }
  
  /**
   * 增加路径完成人数
   * @param pathId 路径ID
   */
  private async incrementPathCompletion(pathId: string): Promise<void> {
    const path = await pathManagement.getPath(pathId);
    if (path) {
      await pathManagement.updatePath(pathId, {
        completionCount: path.completionCount + 1
      });
    }
  }
}

export default new LearningRecords();