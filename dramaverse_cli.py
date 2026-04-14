#!/usr/bin/env python3
"""
Dramaverse CLI - ByteDrama 短剧查询与下载工具
"""

from dramaverse_api import DramaverseAPI
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# ==================== 配置区 ====================
VERSION = "v1.0.0"
OUTPUT_DIR = os.path.expanduser("~/Downloads/BanYun-Dramaverse")

# 凭证配置（从环境变量读取，如未设置则使用默认值）
# 本地使用: 设置环境变量 DRAMAVERSE_USER_ID, DRAMAVERSE_ROLE_ID, DRAMAVERSE_TOKEN
# 或创建 .env 文件
USER_ID = int(os.environ.get("DRAMAVERSE_USER_ID", "0"))
ROLE_ID = int(os.environ.get("DRAMAVERSE_ROLE_ID", "0"))
TOKEN = os.environ.get("DRAMAVERSE_TOKEN", "")

# Logo
LOGO = """
╔═════════════════════════════════════════════════════════════════════╗
║  ____                  ____          _   ____                       ║
║ | __ ) _ __ _____  ___|  _ \\ ___  __| | |  _ \\  __ _ _ __ ___       ║
║ |  _ \\| '__/ _ _ \\/ _ \\| |_) / _ \\/ _` | | | | |/ _` | '_ ` _ \\     ║
║ | |_) | | |  __/  __/|  __/  __/ (_| | | |_| | (_| | | | | | |      ║
║ |____/|_|  \\___|\\___||_|   \\___|\\__,_| |____/ \\__,_|_| |_| |_|      ║
║                                                                     ║
║           Dramaverse CLI                           {}           ║
╚═════════════════════════════════════════════════════════════════════╝
""".format(VERSION)

# 语言选项
LANG_OPTIONS = {
    '1': 'zh_hans', '2': 'zh_hant', '3': 'en', '4': 'vi',
    '5': 'id', '6': 'th', '7': 'es', '8': 'ko', '9': 'pt', '10': 'ja'
}

# 完结状态
PROGRESS_OPTIONS = {'1': 1, '2': 2}  # 1=已完结, 2=未完结

# ==================== UI 辅助函数 ====================

def print_header(title):
    """打印标题"""
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)

def print_table(headers, rows, max_width=40):
    """打印表格"""
    # 计算每列宽度
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            cell_str = str(cell)[:max_width]
            widths[i] = max(widths[i], len(cell_str))

    # 打印表头
    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
    print(header_line)
    print("-" * len(header_line))

    # 打印数据行
    for row in rows:
        row_line = " | ".join(str(cell)[:max_width].ljust(w) for cell, w in zip(row, widths))
        print(row_line)

def input_choice(prompt, options=None):
    """获取用户输入"""
    while True:
        choice = input(prompt).strip()
        if options is None or choice in options:
            return choice
        print(f"无效输入，请选择: {list(options.keys())}")

def input_int(prompt, default=None, min_val=None, max_val=None):
    """获取整数输入"""
    while True:
        try:
            val = input(prompt).strip()
            if val == '' and default is not None:
                return default
            val = int(val)
            if min_val and val < min_val:
                print(f"最小值为 {min_val}")
                continue
            if max_val and val > max_val:
                print(f"最大值为 {max_val}")
                continue
            return val
        except ValueError:
            print("请输入数字")

def confirm(prompt):
    """确认操作（回车默认确认）"""
    return input(f"{prompt} [y/n]: ").strip().lower() in ('', 'y')

# ==================== 功能函数 ====================

def query_categories(api):
    """查询分类列表"""
    print_header("分类列表")
    result = api.get_category_list()

    if not result or result.get('code') != '100':
        print("查询失败")
        return

    rows = [(item['id'], item['name']) for item in result['data']]
    print_table(['ID', '分类名称'], rows)
    print(f"\n共 {len(rows)} 个分类")

def query_shortplays(api, page=1, filters=None):
    """查询剧目列表"""
    params = {'page': page, 'page_size': 10}

    if filters:
        if filters.get('category_ids'):
            params['category_ids'] = filters['category_ids']
        if filters.get('display_language'):
            params['display_language'] = filters['display_language']
        if filters.get('progress_state'):
            params['progress_state'] = filters['progress_state']
        if filters.get('title'):
            params['title'] = filters['title']

    # 调用 API（关闭调试输出）
    result = api.get_shortplay_list(**params)

    if not result or result.get('code') != '100':
        print("查询失败")
        return None

    data = result['data']
    page_info = result['page_info']

    print_header(f"剧目列表 (第{page}/{page_info['total_page']}页)")

    rows = []
    for i, item in enumerate(data):
        status = "已完结" if item['progress_state'] == 1 else "连载中"
        lang = item.get('display_language') or item.get('lang', '-')
        rows.append((
            i + 1,
            item['shortplay_id'],
            item['title'][:25],
            item['total'],
            status,
            lang,
            item['file_id']
        ))

    print_table(['序号', '剧ID', '标题', '集数', '状态', '语言', 'FileID'], rows)
    print(f"\n共 {page_info['total']} 个剧目")

    return data, page_info

def get_filters():
    """获取筛选条件"""
    filters = {}

    print_header("设置筛选条件")
    print("提示: 空输入直接跳过\n")

    # 分类
    cat_input = input("分类ID (多个用逗号分隔, 如: 1,2,1704): ").strip()
    if cat_input:
        filters['category_ids'] = [int(x.strip()) for x in cat_input.split(',')]

    # 语言
    print("\n语言选项:")
    print("  1=简中   2=繁中   3=英文   4=越南   5=印尼")
    print("  6=泰语   7=西语   8=韩语   9=葡语   10=日语")
    lang_input = input("\n选择语言编号: ").strip()
    if lang_input in LANG_OPTIONS:
        filters['display_language'] = LANG_OPTIONS[lang_input]

    # 完结状态
    print("\n完结状态:")
    print("  0=全部   1=已完结   2=连载中")
    prog_input = input("\n选择状态: ").strip()
    if prog_input == '0':
        # 全部，不设置筛选
        pass
    elif prog_input in PROGRESS_OPTIONS:
        filters['progress_state'] = PROGRESS_OPTIONS[prog_input]

    # 标题搜索
    title_input = input("\n剧目名称关键词: ").strip()
    if title_input:
        filters['title'] = title_input

    return filters

def parse_episode_input(input_str, max_ep):
    """解析集数输入"""
    input_str = input_str.strip().lower()

    if input_str == 'all' or input_str == '':
        return list(range(1, min(max_ep, 15) + 1))

    episodes = []
    parts = input_str.replace(' ', '').split(',')

    for part in parts:
        if '-' in part:
            start, end = part.split('-')
            episodes.extend(range(int(start), int(end) + 1))
        else:
            episodes.append(int(part))

    # 过滤有效范围
    episodes = [ep for ep in episodes if 1 <= ep <= max_ep]
    return sorted(set(episodes))

def view_shortplay_detail(api, item):
    """查看剧目详情"""
    print_header("剧目详情")

    status = "已完结" if item['progress_state'] == 1 else "连载中"
    lang = item.get('display_language') or item.get('lang', '-')
    voice_lang = item.get('voice_language') or item.get('voice_lang', '-')

    print(f"标题: {item['title']}")
    print(f"剧ID: {item['shortplay_id']}")
    print(f"FileID: {item['file_id']}")
    print(f"集数: {item['total']}")
    print(f"状态: {status}")
    print(f"字幕: {lang}")
    print(f"配音: {voice_lang}")
    print(f"原始: {item.get('original_language', '-')}")
    print(f"分类: {', '.join(c['name'] for c in item.get('category', []))}")
    print(f"简介: {item.get('desc', '无')[:100]}...")
    print(f"封面: {item.get('cover_image', '-')}")
    print(f"上线: {item.get('first_online_time', '-')}")

    print("\n操作: [d]下载 [q]返回")
    action = input("请选择: ").strip().lower()

    if action == 'd':
        download_shortplay(api, item['file_id'], item['shortplay_id'], item['total'])

def download_shortplay(api, file_id, shortplay_id, total_eps):
    """下载剧目"""
    print_header(f"下载剧目 (ID: {shortplay_id})")
    print(f"总集数: {total_eps}，可下载前15集")

    # 获取集数输入
    ep_input = input("下载集数 (如: 1-5 或 1,3,5 或 all): ").strip()
    episodes = parse_episode_input(ep_input, total_eps)

    if not episodes:
        print("无效集数")
        return

    print(f"将下载: {episodes} 集")
    if not confirm("确认下载?"):
        return

    # 查询下载链接
    print("\n获取下载链接...")
    download_config = [{'file_id': file_id, 'target_index': episodes}]
    result = api.get_download_links(download_config)

    if not result or result.get('code') != '100':
        print("获取链接失败")
        return

    # 解析并下载
    parsed = api.parse_download_links(result)

    print(f"\n开始下载 {len(parsed)} 个视频...")
    success, fail = api.download_all_videos(parsed, OUTPUT_DIR)

    print(f"\n下载完成: 成功 {success}, 失败 {fail}")

def browse_shortplays(api):
    """浏览剧目列表"""
    filters = get_filters()
    page = 1

    while True:
        result = query_shortplays(api, page, filters)
        if not result:
            break

        data, page_info = result

        print("\n操作: [n]下一页 [p]上一页 [v]查看详情 [s]直接下载 [r]重新筛选 [q]返回")
        action = input("请选择: ").strip().lower()

        if action == 'n' and page < page_info['total_page']:
            page += 1
        elif action == 'p' and page > 1:
            page -= 1
        elif action == 'v':
            idx = input_int("输入序号: ", min_val=1, max_val=len(data))
            view_shortplay_detail(api, data[idx - 1])
        elif action == 's':
            idx = input_int("输入序号: ", min_val=1, max_val=len(data))
            item = data[idx - 1]
            download_shortplay(api, item['file_id'], item['shortplay_id'], item['total'])
        elif action == 'r':
            filters = get_filters()
            page = 1
        elif action == 'q':
            break

def search_shortplay(api):
    """搜索剧目"""
    print_header("搜索剧目")

    keyword = input("输入剧目名称或ID: ").strip()
    if not keyword:
        return

    # 尝试作为ID搜索
    try:
        shortplay_id = int(keyword)
        result = api.get_shortplay_list(shortplay_ids=[shortplay_id])
    except ValueError:
        # 名称搜索
        result = api.get_shortplay_list(title=keyword)

    if not result or result.get('code') != '100' or not result['data']:
        print("未找到剧目")
        return

    data = result['data']

    while True:
        # 显示搜索结果
        print_header("搜索结果")
        rows = [(i+1, item['shortplay_id'], item['title'][:30], item['total'],
                 item['file_id']) for i, item in enumerate(data)]
        print_table(['序号', '剧ID', '标题', '集数', 'FileID'], rows)

        print("\n[v]查看详情 [s]直接下载 [r]重新搜索 [q]返回")
        action = input("请选择: ").strip().lower()

        if action == 'v':
            idx = input_int("输入序号: ", min_val=1, max_val=len(data))
            view_shortplay_detail(api, data[idx - 1])
        elif action == 's':
            idx = input_int("输入序号: ", min_val=1, max_val=len(data))
            item = data[idx - 1]
            download_shortplay(api, item['file_id'], item['shortplay_id'], item['total'])
        elif action == 'r':
            # 重新搜索
            keyword = input("输入剧目名称或ID: ").strip()
            if not keyword:
                continue
            try:
                shortplay_id = int(keyword)
                result = api.get_shortplay_list(shortplay_ids=[shortplay_id])
            except ValueError:
                result = api.get_shortplay_list(title=keyword)
            if result and result.get('code') == '100' and result['data']:
                data = result['data']
            else:
                print("未找到剧目")
        elif action == 'q':
            break

# ==================== 主菜单 ====================

def main_menu():
    """主菜单"""
    global USER_ID, ROLE_ID, TOKEN
    # 检查凭证
    if USER_ID == 0 or ROLE_ID == 0 or not TOKEN:
        print_header("凭证配置")
        print("未检测到凭证，请设置环境变量或输入凭证：")
        print("  环境变量: DRAMAVERSE_USER_ID, DRAMAVERSE_ROLE_ID, DRAMAVERSE_TOKEN")
        print()
        USER_ID = input_int("请输入 User ID: ")
        ROLE_ID = input_int("请输入 Role ID: ")
        TOKEN = input("请输入 Token: ").strip()
        if not TOKEN:
            print("凭证无效，退出")
            return

    api = DramaverseAPI(USER_ID, ROLE_ID, TOKEN)

    # 显示 Logo
    print(LOGO)

    # 预加载分类信息
    print("正在加载分类信息...")
    cat_result = api.get_category_list()
    categories = cat_result['data'] if cat_result and cat_result.get('code') == '100' else []

    while True:
        # 显示分类信息（常驻顶部）
        print_header("分类列表")
        if categories:
            cat_rows = [(item['id'], item['name']) for item in categories]
            print_table(['ID', '分类'], cat_rows)
            print(f"共 {len(categories)} 个分类")

        print("\n主菜单:")
        print("  1. 浏览剧目")
        print("  2. 搜索剧目")
        print("  0. 退出")

        choice = input_choice("\n请选择: ", ['0', '1', '2'])

        if choice == '1':
            browse_shortplays(api)
        elif choice == '2':
            search_shortplay(api)
        elif choice == '0':
            print("\n感谢使用 BanYun Dramaverse CLI，再见!")
            break

if __name__ == "__main__":
    # 创建下载目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    main_menu()


def main():
    """入口函数（供 pip 安装后使用）"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    main_menu()