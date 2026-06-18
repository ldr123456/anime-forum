"""初始化数据库：创建表并插入预设分类。"""
from app import app, db
from database import Category

with app.app_context():
    db.create_all()
    print("数据库表创建完成。")

    categories = [
        # 游戏
        {'name': '原神', 'description': '提瓦特大陆冒险故事，旅行者的奇妙旅途', 'icon': '⚔️', 'cat_type': 'game'},
        {'name': '崩坏：星穹铁道', 'description': '星穹列车穿越银河，开拓之旅', 'icon': '🚂', 'cat_type': 'game'},
        {'name': '绝区零', 'description': '新艾利都的都市幻想，空洞探索', 'icon': '🌆', 'cat_type': 'game'},
        {'name': '明日方舟', 'description': '罗德岛制药，策略塔防巅峰', 'icon': '🛡️', 'cat_type': 'game'},
        {'name': '碧蓝航线', 'description': '舰船少女，碧海蓝天之战', 'icon': '⚓', 'cat_type': 'game'},
        # 番剧
        {'name': '鬼灭之刃', 'description': '炭治郎的灭鬼之路，无限城篇', 'icon': '👹', 'cat_type': 'anime'},
        {'name': '咒术回战', 'description': '咒术高专的激斗，涩谷事变', 'icon': '🔮', 'cat_type': 'anime'},
        {'name': '葬送的芙莉莲', 'description': '千年精灵的旅途，理解人心的故事', 'icon': '🧝', 'cat_type': 'anime'},
        {'name': '我推的孩子', 'description': '演艺圈的转生复仇剧', 'icon': '⭐', 'cat_type': 'anime'},
        {'name': 'Re:从零开始的异世界生活', 'description': '死亡回归的绝望与希望', 'icon': '🔄', 'cat_type': 'anime'},
    ]

    for cat_data in categories:
        existing = Category.query.filter_by(name=cat_data['name']).first()
        if not existing:
            cat = Category(**cat_data)
            db.session.add(cat)

    db.session.commit()
    print(f"已插入 {len(categories)} 个预设分类。")
    print("初始化完成！运行 python app.py 启动服务器。")
