/**
 * Passport配置
 */
const JwtStrategy = require('passport-jwt').Strategy;
const ExtractJwt = require('passport-jwt').ExtractJwt;
const LocalStrategy = require('passport-local').Strategy;
const { db } = require('./database');
const { logger } = require('@suoke/shared').utils;
const bcrypt = require('bcrypt');
const config = require('./index');

module.exports = (passport) => {
  // JWT策略配置
  const jwtOptions = {
    jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
    secretOrKey: config.jwt.secret
  };

  passport.use(new JwtStrategy(jwtOptions, async (jwtPayload, done) => {
    try {
      // 查找用户
      const user = await db('users')
        .where('id', jwtPayload.id)
        .first();

      if (!user) {
        return done(null, false, { message: '用户不存在' });
      }

      // 检查令牌是否已过期
      if (jwtPayload.exp < Date.now() / 1000) {
        return done(null, false, { message: '令牌已过期' });
      }

      // 移除敏感信息
      delete user.password;

      return done(null, user);
    } catch (error) {
      logger.error(`JWT验证错误: ${error.message}`);
      return done(error, false);
    }
  }));

  // 本地策略配置 (用户名密码登录)
  passport.use(new LocalStrategy(
    {
      usernameField: 'username',
      passwordField: 'password'
    },
    async (username, password, done) => {
      try {
        // 查找用户
        const user = await db('users')
          .where('username', username)
          .orWhere('email', username)
          .first();

        if (!user) {
          return done(null, false, { message: '用户名或密码错误' });
        }

        // 检查密码
        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) {
          return done(null, false, { message: '用户名或密码错误' });
        }

        // 移除敏感信息
        delete user.password;

        return done(null, user);
      } catch (error) {
        logger.error(`本地验证错误: ${error.message}`);
        return done(error, false);
      }
    }
  ));
}; 