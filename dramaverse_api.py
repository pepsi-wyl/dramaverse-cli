#!/usr/bin/env python3
"""
ByteDrama API 请求封装工具
支持签名生成和自动发起请求
"""

import hashlib
import time
import json
import urllib.request
import urllib.error
import os
import ssl

# 解决打包后 SSL 证书问题
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


class DramaverseMediaUtil:

    @classmethod
    def sign_gen(cls, params, token):
        """
        生成签名

        Args:
            params: 请求参数字典
            token: 签名密钥

        Returns:
            包含签名的字典 {'sign': 'md5_value'}
        """
        result = {'sign': ''}

        try:
            if not isinstance(params, dict):
                print("invalid params: ", params)
                return result

            # 按参数名升序排序
            param_orders = sorted(params.items(), key=lambda x: x[0], reverse=False)

            # 拼接参数字符串
            raw_str = ''
            for k, v in param_orders:
                if v == '':
                    continue
                raw_str += (str(k) + '=' + str(v) + '&')

            if len(raw_str) == 0:
                return ''

            # 去除末尾 '&' 并追加 token
            sign_str = raw_str[0:-1] + token

            # MD5 加密
            sign = hashlib.md5(sign_str.encode()).hexdigest()
            result['sign'] = sign

            return result

        except Exception as err:
            print("sign_gen Exception:", err)
            return result


class DramaverseAPI:
    """ByteDrama API 客户端

    注意: API 于 2026-03-10 更新，响应字段变更：
    - 新增: display_language, voice_language, original_language
    - 废弃: lang, voice_lang (仍可用但建议使用新字段)
    """

    def __init__(self, user_id, role_id, token, verbose=False):
        self.user_id = user_id
        self.role_id = role_id
        self.token = token
        self.base_url = "https://open-api.bytedrama.com/bytedrama/open/api"
        self.verbose = verbose

    def _generate_timestamp(self):
        """生成当前时间戳"""
        return str(int(time.time()))

    def _build_auth_info(self, timestamp):
        """
        构建认证信息（包含签名）

        Args:
            timestamp: 时间戳字符串

        Returns:
            包含签名认证信息的字典
        """
        params = {
            'user_id': self.user_id,
            'role_id': self.role_id,
            'timestamp': timestamp,
        }

        sign_result = DramaverseMediaUtil.sign_gen(params, self.token)
        params['sign'] = sign_result['sign']

        return params

    def request(self, endpoint, data=None):
        """
        发起 API 请求（通用方法）

        Args:
            endpoint: API 端点（如 '/sp/category/list'）
            data: 额外的请求数据

        Returns:
            响应 JSON 或 None（失败时）
        """
        # 生成时间戳（整个请求流程使用同一个时间戳）
        timestamp = self._generate_timestamp()

        # 构建认证信息
        auth_info = self._build_auth_info(timestamp)

        # 构建完整请求体
        request_data = {'auth_info': auth_info}
        if data is not None:
            request_data.update(data)

        # 发起请求
        url = self.base_url + endpoint
        headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'User-Agent': 'okhttp/4.12.0',
        }

        if self.verbose:
            print(f"[Request] URL: {url}")
            print(f"[Request] Timestamp: {timestamp}")
            print(f"[Request] Data: {json.dumps(request_data, indent=2)}")

        try:
            # 构建 POST 请求
            req = urllib.request.Request(
                url,
                data=json.dumps(request_data).encode('utf-8'),
                headers=headers,
                method='POST'
            )

            with urllib.request.urlopen(req, context=ssl_context) as response:
                response_data = response.read().decode('utf-8')

            if self.verbose:
                print(f"[Response] Status: 200")
            result = json.loads(response_data)
            if self.verbose:
                print(f"[Response] Data: {json.dumps(result, indent=2, ensure_ascii=False)}")

            return result

        except urllib.error.URLError as e:
            print(f"[Error] Request failed: {e}")
            return None

    # ==================== 具体API方法 ====================

    def get_category_list(self):
        """
        查询分类列表

        Returns:
            响应 JSON
        """
        return self.request('/sp/category/list')

    def get_shortplay_list(self, page=1, page_size=100, category_ids=None,
                           shortplay_ids=None,
                           display_language=None, voice_language=None,
                           lang=None, voice_lang=None,
                           progress_state=None, title=None):
        """
        查询剧目列表

        Args:
            page: 页码
            page_size: 每页数量（上限1000）
            category_ids: 分类ID列表，如 [1, 2]
            shortplay_ids: 短剧ID列表，如 [1024]
            display_language: 字幕语种（推荐），如 "zh_hans"
            voice_language: 音频语种（推荐），如 "zh_hans"
            lang: 字幕语种（已废弃，建议使用 display_language）
            voice_lang: 音频语种（已废弃，建议使用 voice_language）
            progress_state: 完结状态，1=已完结，2=未完结
            title: 短剧名称搜索

        Returns:
            响应 JSON
        """
        page_info = {
            'page': page,
            'page_size': page_size
        }

        controller = {}
        if category_ids is not None:
            controller['category_ids'] = category_ids
        if shortplay_ids is not None:
            controller['shortplay_ids'] = shortplay_ids

        # 语言参数：新参数优先，旧参数向后兼容
        # 请求参数名仍为 lang/voice_lang，但建议使用新字段名传入
        final_lang = display_language if display_language is not None else lang
        if final_lang is not None:
            controller['lang'] = [final_lang] if isinstance(final_lang, str) else final_lang
            if lang is not None and display_language is None and self.verbose:
                print("[Warning] 'lang' 参数已废弃，建议使用 'display_language'")

        final_voice_lang = voice_language if voice_language is not None else voice_lang
        if final_voice_lang is not None:
            controller['voice_lang'] = [final_voice_lang] if isinstance(final_voice_lang, str) else final_voice_lang
            if voice_lang is not None and voice_language is None and self.verbose:
                print("[Warning] 'voice_lang' 参数已废弃，建议使用 'voice_language'")

        if progress_state is not None:
            controller['progress_state'] = progress_state
        if title is not None:
            controller['title'] = title

        return self.request('/sp/file/list', {
            'page_info': page_info,
            'controller': controller
        })

    def get_download_links(self, download_config, page=1, page_size=100):
        """
        查询剧目下载链接

        Args:
            download_config: 下载配置列表，格式如：
                [
                    {"file_id": 4028},
                    {"file_id": 4028, "target_index": [1, 2, 3]}
                ]
            page: 页码
            page_size: 每页数量

        Returns:
            响应 JSON，包含视频播放链接
        """
        if len(download_config) > 10 and self.verbose:
            print("[Warning] download_config单次查询剧目数量不能超过10个")

        page_info = {
            'page': page,
            'page_size': page_size
        }

        controller = {
            'download_config': download_config
        }

        return self.request('/sp/file/download', {
            'page_info': page_info,
            'controller': controller
        })

    # ==================== 辅助方法 ====================

    def parse_download_links(self, response):
        """
        解析下载链接响应，提取视频下载信息

        Args:
            response: get_download_links的响应

        Returns:
            格式化的下载信息列表，包含：
            - file_id: 剧目id
            - shortplay_id: 短剧id
            - episode_index: 集数下标
            - name: 文件名
            - play_url: 播放链接
            - video_size: 视频大小
            - display_language: 字幕语种（新）
            - voice_language: 音频语种（新）
            - original_language: 原始音频语种（新）
            - lang: 字幕语种（已废弃）
            - voice_lang: 音频语种（已废弃）
        """
        if not response or response.get('code') != '100':
            return []

        results = []
        for item in response.get('data', []):
            for episode in item.get('episode_list', []):
                results.append({
                    'file_id': item.get('file_id'),
                    'shortplay_id': item.get('shortplay_id'),
                    'episode_index': episode.get('index'),
                    'name': episode.get('name'),
                    'play_url': episode.get('play_url'),
                    'video_size': episode.get('video_size'),
                    # 新字段
                    'display_language': item.get('display_language'),
                    'voice_language': item.get('voice_language'),
                    'original_language': item.get('original_language'),
                    # 旧字段（向后兼容）
                    'lang': item.get('lang'),
                    'voice_lang': item.get('voice_lang')
                })
        return results

    def download_video(self, url, filename, output_dir='downloadFiles', chunk_size=8192):
        """
        下载视频文件

        Args:
            url: 视频下载链接
            filename: 保存的文件名
            output_dir: 保存目录
            chunk_size: 下载块大小

        Returns:
            成功返回 True，失败返回 False
        """
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        print(f"[下载] {filename} ...")

        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'okhttp/4.12.0',
            })

            with urllib.request.urlopen(req, context=ssl_context) as response:
                total_size = int(response.headers.get('Content-Length', 0))
                downloaded = 0

                with open(filepath, 'wb') as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)

                        # 显示进度
                        if total_size > 0:
                            progress = int(downloaded / total_size * 100)
                            print(f"\r[进度] {progress}% ({downloaded}/{total_size} bytes)", end='')
                        else:
                            print(f"\r[进度] {downloaded} bytes", end='')

            print(f"\r[完成] {filename} (100%)")
            return True

        except Exception as e:
            print(f"\r[失败] {filename}: {e}")
            return False

    def download_all_videos(self, download_links, output_dir='downloadFiles'):
        """
        批量下载视频

        Args:
            download_links: parse_download_links返回的列表
            output_dir: 保存目录

        Returns:
            (成功数, 失败数)
        """
        success_count = 0
        fail_count = 0
        total = len(download_links)

        print("=" * 50)
        print(f"开始下载 {total} 个视频...")
        print("=" * 50)

        for i, item in enumerate(download_links):
            print(f"\n[{i + 1}/{total}] ", end='')

            # 生成文件名
            filename = f"{item['shortplay_id']}_{item['episode_index']}.mp4"
            if item.get('name'):
                filename = item['name']

            if self.download_video(item['play_url'], filename, output_dir):
                success_count += 1
            else:
                fail_count += 1

        print("\n" + "=" * 50)
        print(f"下载完成！成功: {success_count}, 失败: {fail_count}")
        print("=" * 50)

        return success_count, fail_count