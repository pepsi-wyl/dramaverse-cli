# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

BanYun Dramaverse CLI 是一个用于查询和下载 ByteDrama 短剧的命令行工具。

## 架构

项目采用简单的两层架构：

- **`dramaverse_api.py`** - API 客户端层，封装所有 HTTP 请求、签名生成和下载逻辑
- **`dramaverse_cli.py`** - CLI 交互层，处理用户输入、菜单导航和显示逻辑

### API 签名机制

`DramaverseMediaUtil.sign_gen()` 实现了 API 签名生成：
1. 将参数按键名升序排序
2. 拼接为 `key1=value1&key2=value2&` 格式
3. 去除末尾 `&` 并追加 token
4. 对拼接字符串进行 MD5 加密

### 请求流程

所有 API 请求通过 `DramaverseAPI.request()` 方法：
1. 生成时间戳（整个请求使用同一时间戳）
2. 构建认证信息（包含签名）
3. 发送 POST 请求到 `https://open-api.bytedrama.com/bytedrama/open/api`
4. SSL 证书验证已禁用（用于解决打包后证书问题）

## 常用命令

### 本地开发
```bash
# 安装依赖
pip install -e .

# 运行
python dramaverse_cli.py
# 或
dramaverse
```

### 打包
```bash
# Mac ARM64
pyinstaller --onefile --name "BanYun-Dramaverse" --console dramaverse_cli.py

# Windows
pyinstaller --onefile --name "BanYun-Dramaverse.exe" --console dramaverse_cli.py
```

### 发布新版本
```bash
git tag v1.0.1
git push origin v1.0.1
```
推送标签会自动触发 GitHub Actions 构建和发布 Release。

## API 字段变更（2026-03-10）

API 响应中的语言字段已更新：
- **新字段**: `display_language`, `voice_language`, `original_language`
- **废弃字段**: `lang`, `voice_lang`（仍可用但建议使用新字段）

`get_shortplay_list()` 方法内部已做兼容处理：新字段优先传入，但请求参数名仍为 `lang/voice_lang`。

## 下载目录

视频文件默认保存在：
- Mac: `~/Downloads/BanYun-Dramaverse/`
- Windows: `C:\Users\用户名\Downloads\BanYun-Dramaverse\`

由 `OUTPUT_DIR` 常量控制。

## 凭证配置

API 凭证通过以下方式读取（优先级从高到低）：
1. 环境变量 `DRAMAVERSE_USER_ID`, `DRAMAVERSE_ROLE_ID`, `DRAMAVERSE_TOKEN`
2. 运行时手动输入
3. `.env` 文件（需使用 `python-dotenv` 加载）

## 下载限制

单次查询剧目数量不超过 10 个（`download_config`）。
单个剧目最多下载前 15 集（由 UI 层 `parse_episode_input()` 限制）。