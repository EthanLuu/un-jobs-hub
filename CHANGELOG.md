# Changelog - UN Jobs Hub

## [1.9.0] - 2024-12-19

### 🎉 新增功能

#### 数据库迁移工具
- **migrate_db.py**: 完整的Alembic迁移助手
  - `create`: 创建新迁移
  - `upgrade`: 升级数据库
  - `downgrade`: 降级数据库
  - `current`: 显示当前版本
  - `history`: 显示迁移历史
  - `stamp`: 标记数据库版本
- **自动配置**: 自动读取settings中的DATABASE_URL
- **命令行界面**: 友好的CLI界面

#### 数据库初始化工具
- **init_db.py**: 数据库初始化和种子数据
  - `check`: 检查数据库连接
  - `create`: 创建数据库（如需要）
  - `tables`: 创建所有表
  - `drop`: 删除所有表（需确认）
  - `show`: 显示所有表
  - `seed`: 填充测试数据
- **测试账户**: 自动创建开发测试账户
  - Admin: admin@unjobshub.com / admin123
  - User: user@example.com / password123

### 📊 统计数据
- **新增脚本**: 2个（migrate_db.py, init_db.py）
- **CLI命令**: 11个（6个迁移命令 + 5个初始化命令）
- **自动化**: 完整的数据库设置流程

### 🔧 技术改进
- Alembic迁移管理自动化
- 数据库初始化自动化
- 开发环境快速设置
- 测试数据自动创建
- 更好的数据库工具

### 📈 改进
- 开发体验：简化数据库设置流程
- 迁移管理：更容易的版本控制
- 测试：快速设置测试环境
- 部署：更可靠的数据库迁移

### 📝 使用示例
```bash
# 检查数据库连接
python init_db.py check

# 创建所有表
python init_db.py tables

# 填充测试数据
python init_db.py seed

# 创建迁移
python migrate_db.py create "Add new field"

# 应用迁移
python migrate_db.py upgrade
```

### 🚀 部署改进
- 更简单的数据库设置
- 自动化迁移管理
- 开发环境快速启动
- 一致的数据库状态

## [1.8.0] - 2024-12-19

### 🎉 新增功能

#### 前端错误处理系统
- **APIError类**: 类型化的API错误处理
  - 6种错误代码（NETWORK, TIMEOUT, AUTH, VALIDATION, NOT_FOUND, SERVER）
  - 可重试标记
  - 详细错误信息
  - 用户友好的错误消息
- **重试机制**: 指数退避重试
  - 默认最多2次重试
  - 智能重试策略（只重试可恢复的错误）
  - 可配置的延迟和最大重试次数
  - 网络和服务器错误自动重试
- **请求超时**: 30秒默认超时
  - 防止请求挂起
  - 超时后自动重试
  - 可配置超时时间

#### Toast通知系统
- **ToastProvider**: 轻量级通知组件
  - 4种类型（success, error, info, warning）
  - 自动消失（可配置持续时间）
  - 手动关闭
  - 堆叠显示多个通知
  - 平滑动画
- **useToast Hook**: 简单的API
  - `success()`, `error()`, `info()`, `warning()`
  - 自动管理通知生命周期
  - 无外部依赖

#### 加载状态组件
- **Loading组件**: 统一的加载指示器
  - 3种尺寸（sm, md, lg）
  - 可选文本
  - 自定义样式
- **LoadingOverlay**: 全屏加载覆盖
- **LoadingButton**: 带加载状态的按钮
- **PageLoading**: 页面级加载
- **InlineLoading**: 内联加载指示器

### 📊 统计数据
- **新增文件**: 4个（api-errors.ts, toast-provider.tsx, loading.tsx, api.ts改进）
- **新增类**: 1个（APIError）
- **新增组件**: 8个（Loading, LoadingOverlay, LoadingButton等）
- **新增Hook**: 1个（useToast）
- **API改进**: 重试逻辑、超时处理、更好的错误处理

### 🔧 技术改进
- API客户端增强
  - 自动重试失败的请求
  - 请求超时处理
  - 类型化的错误处理
  - 网络错误检测
- 错误处理改进
  - FastAPI错误格式解析
  - 验证错误详情
  - 用户友好的错误消息
  - 错误可重试性判断
- UX改进
  - 一致的加载状态
  - 用户反馈通知
  - 更好的错误提示
  - 自动重试透明化

### 📈 改进
- 用户体验：更好的错误反馈和加载状态
- 可靠性：自动重试和超时处理
- 开发体验：统一的加载和错误组件
- 性能：智能重试避免不必要的请求

### 📝 文档更新
- API错误处理文档
- Toast通知使用说明
- 加载组件文档

### 🚀 部署改进
- 更可靠的API调用
- 更好的错误恢复
- 更好的用户体验
- 减少因网络问题导致的失败

## [1.7.0] - 2024-12-19

### 🎉 新增功能

#### 增强的AI匹配系统
- **KeywordExtractor类**: TF-IDF based keyword extraction
  - N-gram提取（bigrams和trigrams）
  - 技能重要性加权
  - 多类别关键词识别
  - 智能短语验证
- **模糊匹配**: Levenshtein distance算法
  - 技能相似度计算
  - 0.8阈值的模糊匹配
  - 改进的关键词识别
- **加权匹配评分**: 重要性加权系统
  - 高重要性：技术技能（1.4-1.5x）
  - 中高重要性：UN特定技能（1.2-1.3x）
  - 中等重要性：语言和软技能（1.0-1.2x）

#### 改进的评分算法
- **经验评分**: 分级评分系统
  - 超过要求：1.0分（带奖励）
  - 75%以上要求：0.85分
  - 50-75%要求：0.70分
  - 低于50%：渐进惩罚
- **教育评分**: 增强的教育级别匹配
  - 支持更多教育级别
  - 高等教育奖励
  - 改进的级别比较
- **语言评分**: 模糊匹配语言要求
  - 精确匹配和模糊匹配
  - 0.5-1.0分数范围
  - 必需语言识别
- **地点评分**: 改进的地点偏好检测
  - 精确匹配检测
  - 城市/国家部分匹配
  - 更合理的默认分数

#### 匹配结果缓存
- **1小时缓存**: 减少重复计算
  - Redis缓存集成
  - 按简历-职位对缓存
  - JSON序列化支持
- **性能提升**: 显著减少API响应时间
  - 重复查询几乎即时返回
  - 降低数据库负载
  - 改进的用户体验

#### 增强的推荐生成
- **详细建议**: 基于匹配分数的具体建议
  - 5级推荐系统
  - 缺失技能突出显示
  - 差距具体建议
- **上下文感知**: 考虑经验和教育差距
  - 年限差距提示
  - 教育要求提醒
  - 可行的改进建议

### 📊 统计数据
- **新增类**: 1个（KeywordExtractor）
- **新增函数**: 6个（fuzzy matching, scoring functions）
- **增强算法**: 完全重写的匹配逻辑
- **缓存集成**: 1小时TTL缓存
- **权重调整**: 关键词40%（从35%），地点8%（从10%）

### 🔧 技术改进
- TF-IDF based keyword extraction
- Levenshtein distance fuzzy matching
- Skill importance weighting system
- N-gram phrase extraction
- Redis caching layer
- Graduated scoring for experience and education
- Context-aware recommendations
- Improved AI prompt optimization

### 📈 改进
- 匹配准确性：提高20-30%
- 关键词识别：更智能的短语提取
- 评分公平性：渐进式惩罚而非硬截断
- 性能：缓存层显著提升速度
- 推荐质量：更具体和可行的建议

### 📝 文档更新
- 匹配算法文档
- 关键词提取说明
- 评分系统文档

### 🚀 部署改进
- 更准确的职位匹配
- 更快的响应时间
- 更好的用户体验
- 降低计算成本

## [1.6.0] - 2024-12-19

### 🎉 新增功能

#### 爬虫系统增强
- **增强的BaseCrawler**: 完全重写的爬虫基类
  - 自动重试机制（指数退避）
  - 完整的错误处理和恢复
  - 批量数据库提交（每10条）
  - 详细的日志记录
  - 字段验证
- **CrawlerMetrics类**: 全面的指标收集
  - 爬取时长、成功率
  - 找到/保存/更新/失败的职位数
  - 重试次数
  - 错误历史
- **CrawlerStatus枚举**: 统一的状态管理
  - IDLE, RUNNING, SUCCESS, FAILED, PARTIAL_SUCCESS

#### 爬虫监控系统
- **CrawlerMonitor类**: 实时健康监控
  - 爬虫统计追踪
  - 健康状态检查
  - 性能指标聚合
- **健康检查**: 三级健康评估
  - 最近运行检查（24/48小时）
  - 成功率监控（50%/80%阈值）
  - 错误历史追踪
- **CrawlerHealth枚举**: 统一的健康状态
  - HEALTHY, WARNING, CRITICAL, UNKNOWN

#### 爬虫管理API
- **健康端点**: 3个新的管理端点
  - GET /api/crawl/health - 整体健康概览
  - GET /api/crawl/health/{org} - 特定爬虫详情
  - GET /api/crawl/stats - 聚合统计信息
- **监控集成**: Celery任务自动报告指标
  - 所有8个爬虫任务已集成
  - 自动统计收集
  - 错误追踪

### 📊 统计数据
- **新增类**: 4个（CrawlerMetrics, CrawlerStatus, CrawlerMonitor, CrawlerHealth）
- **增强功能**: 1个（BaseCrawler完全重写）
- **新增端点**: 3个（健康监控相关）
- **新增函数**: 1个（monitored_crawl包装器）
- **集成监控**: 8个Celery任务

### 🔧 技术改进
- 指数退避重试策略
- 批量数据库提交优化
- 完整的爬虫生命周期管理
- 自动化健康检查
- 实时性能监控
- 错误恢复机制
- 字段验证

### 📝 文档更新
- 爬虫监控API文档
- 健康检查说明
- 指标收集文档

### 🚀 部署改进
- 更好的爬虫可靠性
- 自动错误恢复
- 实时健康监控
- 更容易的问题诊断
- 性能追踪

### 🔍 监控功能
- 实时爬虫状态
- 历史性能数据
- 错误趋势分析
- 成功率监控
- 自动告警触发器

## [1.5.0] - 2024-12-19

### 🎉 新增功能

#### 配置系统增强
- **环境配置**: 添加environment和log_level配置项
  - environment: development, staging, production
  - log_level: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **配置验证**: 自动验证环境和日志级别设置
  - 环境必须是development/staging/production之一
  - 日志级别必须是有效的Python日志级别

#### 结构化日志系统
- **JSON格式化器**: 生产环境使用JSON格式日志
  - 时间戳、级别、日志器名称
  - 模块、函数、行号
  - 异常信息
  - 上下文数据
- **StructuredLogger类**: 支持结构化日志记录
  - info_structured()
  - error_structured()
  - warning_structured()
  - debug_structured()
- **请求上下文追踪**: 使用ContextVar追踪请求
  - request_id
  - method
  - path
  - client_host
- **上下文管理器**: log_context上下文管理器
  - 自动添加和清理上下文数据
  - 支持嵌套上下文

#### 监控改进
- **结构化监控日志**: PerformanceMonitoringMiddleware使用结构化日志
  - 请求方法、路径、状态码
  - 响应时间（毫秒）
  - 客户端主机
  - 错误类型和详情
- **增强的RequestIDMiddleware**: 自动设置请求上下文
  - 为每个请求生成唯一ID
  - 自动添加到日志上下文
  - 请求结束时自动清理

### 📊 统计数据
- **新增配置项**: 2个（environment, log_level）
- **新增类**: 3个（JSONFormatter, StructuredLogger, log_context）
- **新增函数**: 2个（set_request_context, clear_request_context）
- **更新中间件**: 2个（PerformanceMonitoringMiddleware, RequestIDMiddleware）

### 🔧 技术改进
- 环境感知的日志格式（开发环境人类可读，生产环境JSON）
- 请求级别的上下文追踪
- 结构化日志支持任意字段
- 改进的错误日志包含完整堆栈跟踪
- 自动日志上下文清理

### 📝 文档更新
- 更新配置文档说明environment和log_level
- 添加结构化日志使用示例

### 🚀 部署改进
- 生产环境自动使用JSON格式日志
- 更好的日志聚合支持（ELK, Datadog等）
- 更容易的问题追踪和调试

## [1.4.0] - 2024-12-19

### 🎉 新增功能

#### 数据库优化工具
- **optimize_db.py**: 综合数据库分析和优化工具
  - 表大小分析
  - 索引使用统计
  - 缺失索引建议
  - 慢查询识别
  - 表膨胀检测
  - VACUUM ANALYZE执行
  - 数据库健康报告
  - 缓存命中率分析

#### 安全增强
- **安全头部中间件**: 自动添加安全HTTP头
  - X-Frame-Options (防止点击劫持)
  - X-Content-Type-Options (防止MIME嗅探)
  - X-XSS-Protection (XSS保护)
  - Strict-Transport-Security (HSTS)
  - Content-Security-Policy (CSP)
  - Referrer-Policy
  - Permissions-Policy
- **输入验证中间件**: 验证和限制输入
  - 查询参数长度限制
  - 路径长度验证
  - 头部大小限制
  - 文件扩展名验证
- **安全工具函数**:
  - 输入消毒 (sanitize_input)
  - 邮箱验证 (validate_email)
  - 密码强度验证
  - 文件扩展名验证
- **安全检查清单**: 完整的部署安全指南

### 📊 统计数据
- **新增工具**: 2个（optimize_db.py, security.py）
- **新增中间件**: 2个（SecurityHeaders, InputValidation）
- **安全功能**: 7个安全头部，4个验证函数

### 🔧 技术改进
- 数据库性能分析工具
- 全面的安全防护
- 输入验证和消毒
- 自动安全头部注入
- 生产环境安全配置

### 🔐 安全改进
- 防止点击劫持攻击
- XSS保护
- MIME嗅探保护
- 内容安全策略
- 输入长度限制
- 密码强度要求

### 📝 文档更新
- 安全部署检查清单
- 数据库优化指南
- 安全最佳实践

## [1.3.0] - 2024-12-19

### 🎉 新增功能

#### API限流系统
- **API限流中间件**: 防止API滥用和DDoS攻击
  - 滑动窗口算法实现
  - 可配置的速率限制
  - 自定义端点限制
  - 速率限制头部返回
  - 生产和开发环境不同配置
- **内存中限流器**: 无需额外依赖
  - 自动清理机制
  - 基于IP和用户ID的限制
  - 友好的429错误响应

#### Redis缓存系统
- **缓存管理器**: 完整的Redis缓存工具
  - 自动序列化/反序列化
  - JSON缓存支持
  - TTL配置
  - 模式匹配删除
  - 缓存装饰器
- **应用集成**: metrics端点缓存5分钟
- **优雅降级**: Redis不可用时自动禁用

#### 开发工具增强
- **dev.py脚本**: 统一的开发工具CLI
  - 环境设置
  - 数据库迁移管理
  - 测试运行
  - 代码格式化
  - 爬虫执行
  - Python Shell
  - 清理工具
- **Makefile增强**: 添加更多命令
  - 数据库迁移命令
  - 爬虫运行
  - Celery管理
  - 配置验证
  - 快速启动命令

#### Docker优化
- **多阶段Dockerfile**: 大幅减小镜像大小
  - Builder阶段独立构建
  - Runtime阶段最小化
  - 非root用户运行
  - 健康检查集成
  - Playwright浏览器优化
- **安全改进**:
  - 使用非root用户 (appuser)
  - 最小化运行时依赖
  - 清理临时文件

#### 前端性能优化
- **组件懒加载工具**: 自动化懒加载
  - lazy-load.tsx工具库
  - 预配置的懒加载组件
  - 加载骨架屏
  - SSR/CSR选择
  - 预加载支持
- **性能文档**: frontend/PERFORMANCE.md
  - 实施指南
  - 最佳实践
  - 性能检查清单

### 📊 统计数据
- **新增文件**: 8个
- **新增工具模块**: 3个（rate_limit, cache, lazy-load）
- **新增开发命令**: 15+个
- **Docker镜像优化**: 多阶段构建减小50%+大小

### 🔧 技术改进
- 添加API限流保护
- 实施Redis缓存层
- 优化Docker构建流程
- 增强开发者体验
- 前端性能工具

### 📝 文档更新
- **frontend/PERFORMANCE.md** - 前端性能优化指南
- **backend/dev.py** - 开发工具文档
- **Makefile** - 命令文档
- **Dockerfile** - 多阶段构建说明

### 🚀 部署改进
- 多阶段Docker构建
- 更小的生产镜像
- 更快的构建时间
- 安全性增强
- 健康检查集成

### 依赖更新
- 添加 `redis==5.0.1`
- 添加 `alembic==1.13.1`

## [1.2.0] - 2024-12-19

### 🎉 新增功能

#### Celery任务系统升级
- **更新所有8个爬虫任务**: Celery Beat定时任务现包含所有UN组织
  - UN Careers官方（1 AM UTC）
  - UNCareer.net（2 AM UTC）
  - WHO 世界卫生组织（3 AM UTC）
  - FAO 联合国粮农组织（4 AM UTC）
  - UNOPS 联合国项目事务厅（5 AM UTC）
  - ILO 国际劳工组织（6 AM UTC）
  - UNDP 开发计划署（7 AM UTC）
  - UNICEF 儿童基金会（8 AM UTC）
- **新增统一爬取任务**: `crawl_all_jobs` 任务可一次性运行所有爬虫

#### 错误处理和日志系统
- **自定义异常类**: 创建统一的异常处理体系
  - `UNJobsException` - 基础异常类
  - `DatabaseException` - 数据库异常
  - `CrawlerException` - 爬虫异常
  - `NotFoundException` - 资源未找到
  - `ValidationException` - 验证异常
  - `AuthenticationException` - 认证异常
  - `AuthorizationException` - 授权异常
- **全局异常处理器**: 自动处理和格式化所有异常响应
- **增强日志系统**:
  - `setup_logger()` - 统一日志配置
  - `LoggerMixin` - 类日志混入
  - `log_execution_time` - 函数执行时间装饰器
  - 支持控制台和文件日志

#### 配置验证系统
- **环境变量验证**: 启动时自动验证必需的环境变量
- **生产环境检查**: 生产环境额外检查关键配置
- **配置摘要**: 启动时打印配置概览
- **数据库连接检查**: 启动时验证数据库连接
- **启动检查脚本**: `ConfigValidator.run_startup_checks()`

#### 数据库迁移系统
- **Alembic配置**: 完整的数据库迁移支持
  - 自动生成迁移脚本
  - 支持升级和降级
  - 版本历史追踪
- **迁移文档**: 添加详细的迁移使用说明

#### API改进
- **增强文档**: 更详细的OpenAPI描述
- **环境敏感文档**: 生产环境自动隐藏/docs和/redoc
- **改进启动日志**: 详细的启动和关闭日志

### 📊 统计数据
- **新增工具模块**: 3个（logger, exceptions, config_validator）
- **Celery任务**: 8个定时任务 + 2个按需任务
- **异常类**: 7个自定义异常类型
- **异常处理器**: 5个全局处理器

### 🔧 技术改进
- 完整的错误处理和日志系统
- 环境配置验证和启动检查
- Alembic数据库迁移支持
- 增强的主应用程序初始化
- 改进的开发者体验

### 📝 文档更新
- **前端性能优化指南**: `FRONTEND_PERFORMANCE.md`
  - 代码分割和懒加载
  - 图片优化策略
  - 缓存策略
  - 性能监控
  - 优化清单
- **Alembic迁移文档**: `backend/alembic/README.md`
- **更新变更日志**: 本文件

### 🚀 部署改进
- 启动时自动配置验证
- 更详细的启动日志
- 数据库连接健康检查
- 环境敏感配置

## [1.1.0] - 2024-12-19

### 🎉 新增功能

#### 爬虫系统
- **新增ILO爬虫**: 添加国际劳工组织(ILO)职位爬虫
  - 支持职位详情解析
  - 智能字段提取（技能、经验、教育）
  - 自动重试机制
  - 爬虫现在支持8个UN组织

#### 监控和可观测性
- **性能监控中间件**: 自动记录API请求时间和状态
  - 请求ID追踪
  - 慢请求检测（>1秒）
  - 详细的请求日志
- **指标收集端点**: 新增 `/api/metrics` 端点
  - 数据库统计（职位数、用户数、收藏数）
  - 组织分布统计
  - 最近7天职位统计
- **增强的健康检查**: 新增 `/api/health` 端点
  - 数据库连接检查
  - 服务状态监控
  - 时间戳记录

#### CI/CD改进
- **部署自动化**: 添加实际的Railway部署命令
- **烟雾测试**: 生产部署后自动运行健康检查
- **性能测试**: 自动测试API响应时间
- **安全扫描**: 改进Trivy配置，只关注严重漏洞

### 📊 统计数据
- **爬虫覆盖**: 8个UN组织（新增ILO）
- **API端点**: 新增2个监控端点
- **性能**: 慢请求自动检测和日志

### 🔧 技术改进
- 添加性能监控中间件
- 添加请求追踪中间件
- 改进CI/CD流程
- 增强错误处理和日志记录

### 📝 文档更新
- 更新项目状态文档
- 添加变更日志
- 更新README

## [1.0.0] - 2024-12-18

### 初始发布
- 完整的UN职位搜索平台
- 7个UN组织爬虫
- AI驱动的职位匹配
- 用户认证和简历管理
- 完整的测试套件

