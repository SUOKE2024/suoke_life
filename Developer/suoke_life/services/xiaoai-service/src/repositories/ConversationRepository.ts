/**
 * 会话存储库
 * 处理用户与小艾智能体的对话数据
 */
import { BaseRepository } from './BaseRepository';
import Conversation, { IConversation } from '../models/Conversation';

export interface IConversationRepository extends BaseRepository<IConversation> {
  findByConversationId(conversationId: string): Promise<IConversation | null>;
  findByUserId(userId: string, options?: { limit?: number; skip?: number; sort?: string }): Promise<IConversation[]>;
  findRecentConversations(userId: string, limit?: number): Promise<IConversation[]>;
  addMessageToConversation(conversationId: string, message: any): Promise<IConversation | null>;
  markAsRead(conversationId: string): Promise<void>;
  getUnreadCount(userId: string): Promise<number>;
  searchConversationsByContent(userId: string, searchTerm: string): Promise<IConversation[]>;
}

export class ConversationRepository extends BaseRepository<IConversation> implements IConversationRepository {
  constructor() {
    super(Conversation);
  }

  async findByConversationId(conversationId: string): Promise<IConversation | null> {
    return this.findOne({ conversationId });
  }

  async findByUserId(
    userId: string, 
    options: { limit?: number; skip?: number; sort?: string } = {}
  ): Promise<IConversation[]> {
    const { limit = 10, skip = 0, sort = '-updatedAt' } = options;
    
    return this.model
      .find({ userId })
      .sort(sort)
      .skip(skip)
      .limit(limit)
      .exec();
  }

  async findRecentConversations(userId: string, limit = 5): Promise<IConversation[]> {
    return this.model
      .find({ userId })
      .sort({ updatedAt: -1 })
      .limit(limit)
      .exec();
  }

  async addMessageToConversation(conversationId: string, message: any): Promise<IConversation | null> {
    return this.model
      .findOneAndUpdate(
        { conversationId },
        { 
          $push: { messages: message },
          $set: { updatedAt: new Date() }
        },
        { new: true }
      )
      .exec();
  }

  async markAsRead(conversationId: string): Promise<void> {
    await this.model
      .updateOne(
        { conversationId },
        { $set: { unread: false, lastReadAt: new Date() } }
      )
      .exec();
  }

  async getUnreadCount(userId: string): Promise<number> {
    return this.model
      .countDocuments({ userId, unread: true })
      .exec();
  }

  async searchConversationsByContent(userId: string, searchTerm: string): Promise<IConversation[]> {
    return this.model
      .find({
        userId,
        $or: [
          { title: { $regex: searchTerm, $options: 'i' } },
          { 'messages.content': { $regex: searchTerm, $options: 'i' } }
        ]
      })
      .sort({ updatedAt: -1 })
      .exec();
  }
} 