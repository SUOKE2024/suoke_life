/**
 * 用户存储库
 * 处理用户数据的存储和检索
 */
import { BaseRepository } from './BaseRepository';
import User, { IUser } from '../models/User';

export interface IUserRepository extends BaseRepository<IUser> {
  findByUserId(userId: string): Promise<IUser | null>;
  findByUsername(username: string): Promise<IUser | null>;
  findByEmail(email: string): Promise<IUser | null>;
  findByPhoneNumber(phoneNumber: string): Promise<IUser | null>;
  findUsersWithAccessibilityNeeds(): Promise<IUser[]>;
  findUsersByDialect(dialect: string): Promise<IUser[]>;
  updateLastLogin(userId: string): Promise<void>;
}

export class UserRepository extends BaseRepository<IUser> implements IUserRepository {
  constructor() {
    super(User);
  }

  async findByUserId(userId: string): Promise<IUser | null> {
    return this.findOne({ userId });
  }

  async findByUsername(username: string): Promise<IUser | null> {
    return this.findOne({ username });
  }

  async findByEmail(email: string): Promise<IUser | null> {
    return this.findOne({ email });
  }

  async findByPhoneNumber(phoneNumber: string): Promise<IUser | null> {
    return this.findOne({ phoneNumber });
  }

  async findUsersWithAccessibilityNeeds(): Promise<IUser[]> {
    return this.find({
      $or: [
        { 'accessibilityPreferences.needsVoiceGuidance': true },
        { 'accessibilityPreferences.needsSimplifiedContent': true },
        { 'accessibilityPreferences.needsHighContrast': true },
        { 'accessibilityPreferences.needsScreenReader': true },
        { 'accessibilityPreferences.hasVisualImpairment': true },
        { 'accessibilityPreferences.hasHearingImpairment': true },
        { 'accessibilityPreferences.hasCognitiveImpairment': true },
        { 'accessibilityPreferences.hasMotorImpairment': true }
      ]
    });
  }

  async findUsersByDialect(dialect: string): Promise<IUser[]> {
    return this.find({
      $or: [
        { 'dialectPreferences.primary': dialect },
        { 'dialectPreferences.secondary': dialect }
      ]
    });
  }

  async updateLastLogin(userId: string): Promise<void> {
    await this.updateOne(
      { userId },
      { $set: { lastLogin: new Date() } }
    );
  }
} 