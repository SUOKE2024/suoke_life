// 导入路由模块
const mazeRoutes = require('./routes/maze.routes');
const treasureRoutes = require('./routes/treasure.routes');
const plantRoutes = require('./routes/plant.routes');
const teamRoutes = require('./routes/team.routes');
const arEnhancedRoutes = require('./routes/ar-enhanced.routes');

// 注册API路由
app.use('/api/mazes', mazeRoutes);
app.use('/api/treasures', treasureRoutes);
app.use('/api/plants', plantRoutes);
app.use('/api/teams', teamRoutes);
app.use('/api/ar', arEnhancedRoutes); 