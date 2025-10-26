# UN Jobs Hub - 测试指南

## 📋 概述

本文档介绍了 UN Jobs Hub 项目的测试策略、测试套件和运行方法。项目包含全面的单元测试、集成测试和端到端测试。

## 🧪 测试结构

### 后端测试

```
backend/
├── tests/
│   ├── conftest.py              # 测试配置和fixtures
│   ├── unit/                   # 单元测试
│   │   ├── test_models.py      # 数据模型测试
│   │   ├── test_services.py    # 服务层测试
│   │   ├── test_utils.py       # 工具函数测试
│   │   └── test_crawlers.py    # 爬虫测试
│   └── integration/            # 集成测试
│       └── test_api.py         # API端点测试
├── pytest.ini                 # pytest配置
└── requirements-test.txt       # 测试依赖
```

### 前端测试

```
frontend/
├── src/
│   ├── components/
│   │   ├── __tests__/         # 组件测试
│   │   └── ...
│   ├── lib/
│   │   ├── __tests__/         # 工具函数测试
│   │   └── ...
│   └── __tests__/
│       └── integration/       # 集成测试
├── jest.config.js            # Jest配置
├── jest.setup.js             # Jest设置
└── package.json              # 包含测试脚本
```

## 🚀 快速开始

### 安装测试依赖

```bash
# 安装所有测试依赖
make test-coverage

# 或者手动安装
cd backend && pip install -r requirements-test.txt
cd frontend && npm install
```

### 运行所有测试

```bash
# 运行所有测试
make test

# 或者使用Python脚本
python run_tests.py
```

## 📊 测试类型

### 1. 单元测试 (Unit Tests)

测试单个函数、类或组件的功能。

**后端单元测试:**
- 数据模型 (User, Job, Resume, Favorite)
- 服务层 (匹配算法、简历解析)
- 工具函数 (认证、验证、数据处理)
- 爬虫功能

**前端单元测试:**
- React组件 (Hero, Features, Stats, Button, Input)
- 工具函数 (格式化、验证、API客户端)
- 自定义hooks

### 2. 集成测试 (Integration Tests)

测试多个组件或模块之间的交互。

**后端集成测试:**
- API端点完整流程
- 数据库操作
- 认证流程
- 文件上传处理

**前端集成测试:**
- 页面级组件交互
- API调用流程
- 用户交互流程

### 3. 端到端测试 (E2E Tests)

测试完整的用户流程。

## 🔧 测试命令

### 使用 Makefile

```bash
# 运行所有测试
make test

# 只运行后端测试
make test-backend

# 只运行前端测试
make test-frontend

# 只运行单元测试
make test-unit

# 只运行集成测试
make test-integration

# 运行测试并生成覆盖率报告
make test-coverage

# 监视模式运行测试
make test-watch

# CI/CD环境运行测试
make test-ci
```

### 使用 Python 脚本

```bash
# 运行所有测试
python run_tests.py

# 只运行后端测试
python run_tests.py --backend

# 只运行前端测试
python run_tests.py --frontend

# 运行所有测试包括代码检查
python run_tests.py --all

# 安装依赖并运行测试
python run_tests.py --install-deps
```

### 直接使用测试工具

**后端测试:**
```bash
cd backend

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/unit/test_models.py

# 运行特定测试类
pytest tests/unit/test_models.py::TestUserModel

# 运行特定测试方法
pytest tests/unit/test_models.py::TestUserModel::test_create_user

# 生成覆盖率报告
pytest --cov=. --cov-report=html

# 运行测试并监视文件变化
pytest -f
```

**前端测试:**
```bash
cd frontend

# 运行所有测试
npm test

# 运行测试并生成覆盖率报告
npm run test:coverage

# 监视模式运行测试
npm run test:watch

# CI模式运行测试
npm run test:ci
```

## 📈 覆盖率要求

项目设置了以下覆盖率要求：

- **后端**: 80% 以上
- **前端**: 70% 以上

### 查看覆盖率报告

**后端覆盖率报告:**
```bash
cd backend
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

**前端覆盖率报告:**
```bash
cd frontend
npm run test:coverage
open coverage/lcov-report/index.html
```

## 🎯 测试最佳实践

### 1. 测试命名

- 使用描述性的测试名称
- 遵循 `test_<function_name>_<scenario>` 格式
- 使用中文描述测试场景

### 2. 测试结构

```python
# 后端测试结构
def test_function_name_scenario():
    """Test description."""
    # Arrange (准备)
    # Act (执行)
    # Assert (断言)
```

```typescript
// 前端测试结构
describe('Component Name', () => {
  it('should do something when condition', () => {
    // Arrange
    // Act
    // Assert
  })
})
```

### 3. 测试数据

- 使用 fixtures 管理测试数据
- 避免硬编码测试数据
- 使用 Faker 生成随机测试数据

### 4. 模拟 (Mocking)

- 模拟外部依赖 (API调用、数据库)
- 模拟用户交互
- 模拟异步操作

## 🐛 调试测试

### 后端测试调试

```bash
# 运行测试并显示详细输出
pytest -v -s

# 在第一个失败时停止
pytest -x

# 运行失败的测试
pytest --lf

# 调试特定测试
pytest --pdb tests/unit/test_models.py::test_create_user
```

### 前端测试调试

```bash
# 运行测试并显示详细输出
npm test -- --verbose

# 调试模式运行测试
npm test -- --detectOpenHandles

# 运行特定测试文件
npm test -- --testPathPattern=hero.test.tsx
```

## 🔄 CI/CD 集成

项目配置了 GitHub Actions 来自动运行测试：

- **触发条件**: Push 到 main/develop 分支，Pull Request
- **测试环境**: Ubuntu Latest, Python 3.11/3.12, Node.js 18/20
- **服务**: PostgreSQL 16, Redis 7
- **检查项目**: 单元测试、集成测试、代码覆盖率、代码质量、安全扫描

### 查看 CI/CD 状态

1. 访问 GitHub Actions 页面
2. 查看最新的测试运行结果
3. 下载测试报告和覆盖率报告

## 📝 编写新测试

### 后端测试

1. 在 `tests/unit/` 或 `tests/integration/` 中创建测试文件
2. 使用现有的 fixtures 和测试工具
3. 遵循测试命名规范
4. 确保测试覆盖率

### 前端测试

1. 在组件目录下创建 `__tests__` 文件夹
2. 创建 `.test.tsx` 文件
3. 使用 React Testing Library
4. 模拟必要的依赖

## 🚨 常见问题

### 1. 测试环境问题

**问题**: 数据库连接失败
**解决**: 确保测试数据库正在运行
```bash
make db-up
```

**问题**: 依赖安装失败
**解决**: 清理缓存并重新安装
```bash
make clean
make install
```

### 2. 测试失败问题

**问题**: 测试超时
**解决**: 检查异步操作是否正确等待
```python
await asyncio.sleep(0.1)  # 等待异步操作完成
```

**问题**: 模拟不工作
**解决**: 确保正确导入和配置模拟
```python
@patch('module.function')
def test_something(mock_function):
    # 测试代码
```

### 3. 覆盖率问题

**问题**: 覆盖率不达标
**解决**: 
1. 检查是否有未测试的代码路径
2. 添加边界条件测试
3. 确保所有分支都被覆盖

## 📚 相关资源

- [pytest 文档](https://docs.pytest.org/)
- [Jest 文档](https://jestjs.io/docs/getting-started)
- [React Testing Library 文档](https://testing-library.com/docs/react-testing-library/intro/)
- [FastAPI 测试文档](https://fastapi.tiangolo.com/tutorial/testing/)

## 🤝 贡献指南

1. 为新功能编写测试
2. 确保所有测试通过
3. 保持或提高测试覆盖率
4. 遵循测试最佳实践
5. 更新测试文档

---

**最后更新**: 2024年12月19日  
**版本**: v1.0.0
