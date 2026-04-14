# BanYun Dramaverse CLI

ByteDrama 短剧查询与下载命令行工具。

## 功能

- 查询分类列表
- 浏览剧目列表（支持筛选、分页）
- 搜索剧目
- 查看剧目详情
- 批量下载剧集

## 下载

从 [Releases](../../releases) 页面下载对应平台的可执行文件：

| 文件 | 适用平台 |
|-----|---------|
| `BanYun-Dramaverse-arm64` | Mac M1/M2/M3/M4 |
| `BanYun-Dramaverse-x64` | Mac Intel |
| `BanYun-Dramaverse.exe` | Windows |

## 使用

### 首次运行

程序启动后会提示输入 API 凭证：
- User ID
- Role ID
- Token

凭证获取请联系 Dramaverse 团队。

### 设置环境变量（可选）

```bash
# Mac/Linux
export DRAMAVERSE_USER_ID=你的ID
export DRAMAVERSE_ROLE_ID=你的ID
export DRAMAVERSE_TOKEN=你的Token

# Windows
set DRAMAVERSE_USER_ID=你的ID
set DRAMAVERSE_ROLE_ID=你的ID
set DRAMAVERSE_TOKEN=你的Token
```

### 或创建配置文件

复制 `.env.example` 为 `.env` 并填入凭证：

```bash
cp .env.example .env
# 编辑 .env 文件
```

## 本地开发

```bash
# 安装依赖
pip install -e .

# 运行
python dramaverse_cli.py
# 或
dramaverse
```

## 打包

```bash
# Mac ARM64
pyinstaller --onefile --name "BanYun-Dramaverse-arm64" --console dramaverse_cli.py

# 发布新版本（触发自动打包）
git tag v1.0.1
git push origin v1.0.1
```

## 下载目录

视频文件保存在 `downloadFiles` 目录。