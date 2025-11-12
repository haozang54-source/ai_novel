"""
快速测试新增的API接口
运行: python test_api.py
"""
import requests
import json

BASE_URL = 'http://localhost:5001/api'

def test_character_api():
    print("\n=== 测试人物API ===")
    
    # 创建人物
    character_data = {
        'project_id': 1,
        'name': '张三',
        'role_type': '主角',
        'gender': '男',
        'personality': '勇敢、正直',
        'importance': 5,
        'tags': ['主角', '修仙者'],
        'abilities': ['御剑术', '炼丹术']
    }
    
    try:
        response = requests.post(f'{BASE_URL}/characters', json=character_data)
        if response.status_code == 201:
            print("✓ 创建人物成功")
            character = response.json()
            print(f"  ID: {character['id']}, 名字: {character['name']}")
            return character['id']
        else:
            print(f"✗ 创建人物失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return None

def test_worldview_api():
    print("\n=== 测试世界观API ===")
    
    worldview_data = {
        'project_id': 1,
        'category': '力量体系',
        'title': '修仙等级',
        'description': '练气期 → 筑基期 → 金丹期 → 元婴期',
        'importance': 5,
        'tags': ['修炼', '等级']
    }
    
    try:
        response = requests.post(f'{BASE_URL}/worldviews', json=worldview_data)
        if response.status_code == 201:
            print("✓ 创建世界观成功")
            worldview = response.json()
            print(f"  ID: {worldview['id']}, 标题: {worldview['title']}")
        else:
            print(f"✗ 创建世界观失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 请求失败: {e}")

def test_foreshadowing_api():
    print("\n=== 测试伏笔API ===")
    
    foreshadowing_data = {
        'project_id': 1,
        'title': '神秘玉佩',
        'description': '主角在第3章获得的玉佩，似乎隐藏着秘密',
        'category': '物品',
        'planted_chapter': 3,
        'planned_reveal_chapter': 50,
        'status': 'planted',
        'importance': 4,
        'urgency': 3
    }
    
    try:
        response = requests.post(f'{BASE_URL}/foreshadowings', json=foreshadowing_data)
        if response.status_code == 201:
            print("✓ 创建伏笔成功")
            foreshadowing = response.json()
            print(f"  ID: {foreshadowing['id']}, 标题: {foreshadowing['title']}")
        else:
            print(f"✗ 创建伏笔失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 请求失败: {e}")

def test_writing_style_api():
    print("\n=== 测试文风API ===")
    
    style_data = {
        'project_id': 1,
        'narrative_perspective': '第三人称全知',
        'language_style': '网文爽文',
        'dialogue_style': '生动',
        'description_density': '适中',
        'style_samples': [
            {
                'scene_type': '战斗',
                'sample': '剑光如虹，破空而来！'
            }
        ]
    }
    
    try:
        response = requests.post(f'{BASE_URL}/writing-styles', json=style_data)
        if response.status_code == 201:
            print("✓ 创建文风设定成功")
            style = response.json()
            print(f"  ID: {style['id']}, 视角: {style['narrative_perspective']}")
        else:
            print(f"✗ 创建文风设定失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 请求失败: {e}")

def main():
    print("开始测试API接口...")
    print(f"后端地址: {BASE_URL}")
    
    test_character_api()
    test_worldview_api()
    test_foreshadowing_api()
    test_writing_style_api()
    
    print("\n测试完成!")

if __name__ == '__main__':
    main()
