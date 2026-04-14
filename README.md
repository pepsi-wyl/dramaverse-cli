# BanYun Dramaverse CLI

ByteDrama 短剧查询与下载命令行工具。

## 功能

- 查询分类列表
- 浏览剧目列表（支持筛选、分页）
- 搜索剧目
- 查看剧目详情
- 批量下载剧集

## 下载

从 [Releases](../../releases) 页面下载对应平台的文件：

| 文件 | 适用平台 |
|-----|---------|
| `BanYun-Dramaverse-arm64.zip` | Mac M1/M2/M3/M4/M5 |
| `BanYun-Dramaverse-x64.zip` | Mac Intel |
| `BanYun-Dramaverse.exe` | Windows |

## 使用

### Mac 用户

1. 解压下载的 `.zip` 文件
2. 将 `BanYun-Dramaverse.app` 拖到 Applications（或其他目录）
3. **首次使用必须运行以下命令**（绕过 macOS 安全检查）：
   ```bash
   xattr -cr /Applications/BanYun-Dramaverse.app
   ```
4. 将 `.env` 配置文件放到 `.app` 同目录（如 `/Applications/.env`）
5. 双击 `BanYun-Dramaverse.app` 即可运行（自动打开终端）

### Windows 用户

在命令行运行：
```cmd
BanYun-Dramaverse.exe
```

`.env` 文件放在 exe 同目录。

### 配置凭证

复制 `.env.example` 为 `.env` 并填入凭证：

```bash
cp .env.example .env
```

`.env` 文件内容：

```
DRAMAVERSE_USER_ID=你的ID
DRAMAVERSE_ROLE_ID=你的ID
DRAMAVERSE_TOKEN=你的Token
```

凭证获取请联系 Dramaverse 团队。

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

视频文件保存在用户 Downloads 目录下的 `BanYun-Dramaverse` 子文件夹：
- Mac: `~/Downloads/BanYun-Dramaverse/`
- Windows: `C:\Users\用户名\Downloads\BanYun-Dramaverse\`