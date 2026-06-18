import os
import sqlite3
from waitress import serve
from app import app, db
from database import Category, User

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # 自动迁移：为已有 users 表添加 nickname 列
        try:
            db_path = os.path.join(app.instance_path, 'data.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.execute("PRAGMA table_info(users)")
            cols = [row[1] for row in cursor.fetchall()]
            if 'nickname' not in cols:
                conn.execute("ALTER TABLE users ADD COLUMN nickname VARCHAR(30) DEFAULT ''")
                conn.commit()
                print("自动迁移：users 表已添加 nickname 列")
            if 'is_admin' not in cols:
                conn.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")
                conn.commit()
                print("自动迁移：users 表已添加 is_admin 列")
            conn.close()
        except Exception as e:
            print(f"迁移检查跳过：{e}")

        print("数据库表创建完成")

        # 插入预设分类（仅在分类表为空时）
        if Category.query.count() == 0:
            categories = [
                {'name': '原神', 'description': '提瓦特大陆冒险故事', 'icon': '⚔️', 'cat_type': 'game'},
                {'name': '崩坏：星穹铁道', 'description': '星穹列车穿越银河', 'icon': '🚂', 'cat_type': 'game'},
                {'name': '绝区零', 'description': '新艾利都的都市幻想', 'icon': '🌆', 'cat_type': 'game'},
                {'name': '明日方舟', 'description': '罗德岛制药，策略塔防', 'icon': '🛡️', 'cat_type': 'game'},
                {'name': '碧蓝航线', 'description': '舰船少女，碧海蓝天', 'icon': '⚓', 'cat_type': 'game'},
                {'name': '鬼灭之刃', 'description': '炭治郎的灭鬼之路', 'icon': '👹', 'cat_type': 'anime'},
                {'name': '咒术回战', 'description': '咒术高专的激斗', 'icon': '🔮', 'cat_type': 'anime'},
                {'name': '葬送的芙莉莲', 'description': '千年精灵的旅途', 'icon': '🧝', 'cat_type': 'anime'},
                {'name': '我推的孩子', 'description': '演艺圈的转生复仇剧', 'icon': '⭐', 'cat_type': 'anime'},
                {'name': 'Re:从零开始的异世界生活', 'description': '死亡回归的绝望与希望', 'icon': '🔄', 'cat_type': 'anime'},
            ]
            for c in categories:
                db.session.add(Category(**c))
            db.session.commit()
            print(f"已插入 {len(categories)} 个预设分类")
        else:
            print(f"已有 {Category.query.count()} 个分类，跳过初始化")

        # 确保至少有一个管理员账号
        if User.query.filter_by(is_admin=True).count() == 0:
            admin = User(
                username='admin',
                nickname='管理员',
                email='admin@anime-forum.local',
                is_admin=True
            )
            admin.set_password('admin123456')
            db.session.add(admin)
            db.session.commit()
            print("已创建默认管理员账号：admin / admin123456")
            print("⚠️ 请尽快登录并修改密码！")

    port = int(os.environ.get('PORT', 5000))
    print(f"二次元交流站 - 生产模式启动")
    print(f"访问地址: http://0.0.0.0:{port}")
    serve(app, host='0.0.0.0', port=port, threads=8)
