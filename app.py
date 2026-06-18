import os
import uuid
from functools import wraps
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from PIL import Image
from config import Config
from database import db, User, Category, Post, Comment

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '请先登录后再访问此页面。'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_avatar(file):
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        img = Image.open(file)
        img.thumbnail((200, 200))
        img.save(filepath)
        return filename
    return None

# ==================== 权限装饰器 ====================

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('此操作需要管理员权限。', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== 路由 ====================

@app.route('/')
def index():
    game_cats = Category.query.filter_by(cat_type='game').all()
    anime_cats = Category.query.filter_by(cat_type='anime').all()
    hot_posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    return render_template('index.html', game_cats=game_cats, anime_cats=anime_cats, hot_posts=hot_posts)

@app.route('/category/<int:cat_id>')
def category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(category_id=cat_id).order_by(Post.created_at.desc()).paginate(page=page, per_page=15)
    return render_template('category.html', category=cat, posts=posts)

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('请先登录后再评论。', 'warning')
            return redirect(url_for('login'))
        content = request.form.get('content', '').strip()
        if not content:
            flash('评论内容不能为空。', 'danger')
        else:
            comment = Comment(content=content, user_id=current_user.id, post_id=post.id)
            db.session.add(comment)
            db.session.commit()
            flash('评论发表成功！', 'success')
        return redirect(url_for('view_post', post_id=post.id))
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.asc()).all()
    return render_template('post.html', post=post, comments=comments)

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category_id = request.form.get('category_id', type=int)
        if not title or not content:
            flash('标题和内容不能为空。', 'danger')
        elif not Category.query.get(category_id):
            flash('请选择有效的分类。', 'danger')
        else:
            post = Post(title=title, content=content, user_id=current_user.id, category_id=category_id)
            db.session.add(post)
            db.session.commit()
            flash('帖子发布成功！', 'success')
            return redirect(url_for('view_post', post_id=post.id))
    categories = Category.query.all()
    return render_template('create_post.html', categories=categories)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        nickname = request.form.get('nickname', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm = request.form.get('confirm', '').strip()
        if not username or not email or not password:
            flash('请填写所有必填字段。', 'danger')
        elif password != confirm:
            flash('两次输入的密码不一致。', 'danger')
        elif len(password) < 6:
            flash('密码长度至少为6位。', 'danger')
        elif User.query.filter_by(username=username).first():
            flash('该登录名已被注册。', 'danger')
        elif User.query.filter_by(email=email).first():
            flash('该邮箱已被注册。', 'danger')
        else:
            user = User(username=username, nickname=nickname, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('注册成功，请登录。', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        remember = request.form.get('remember') == 'on'
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'欢迎回来，{user.nickname or user.username}！', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('用户名或密码错误。', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录。', 'info')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        nickname = request.form.get('nickname', '').strip()
        bio = request.form.get('bio', '').strip()
        theme_color = request.form.get('theme_color', '#6c5ce7').strip()
        current_user.nickname = nickname
        current_user.bio = bio
        current_user.theme_color = theme_color
        file = request.files.get('avatar')
        if file and file.filename:
            avatar_name = save_avatar(file)
            if avatar_name:
                if current_user.avatar and current_user.avatar != 'default.png':
                    old_path = os.path.join(Config.UPLOAD_FOLDER, current_user.avatar)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                current_user.avatar = avatar_name
        db.session.commit()
        flash('个人资料更新成功！', 'success')
        return redirect(url_for('profile'))
    user_posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.created_at.desc()).limit(10).all()
    return render_template('profile.html', posts=user_posts)

@app.route('/create_category', methods=['GET', 'POST'])
@admin_required
def create_category():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        icon = request.form.get('icon', '📌').strip()
        cat_type = request.form.get('cat_type', 'game').strip()
        if not name:
            flash('分类名称不能为空。', 'danger')
        elif cat_type not in ('game', 'anime'):
            flash('请选择有效的类型。', 'danger')
        elif Category.query.filter_by(name=name, cat_type=cat_type).first():
            flash(f'该类型下已存在分类「{name}」，请勿重复创建。', 'warning')
        else:
            cat = Category(name=name, description=description, icon=icon, cat_type=cat_type)
            db.session.add(cat)
            db.session.commit()
            flash(f'分类「{name}」创建成功！', 'success')
            return redirect(url_for('index'))
    return render_template('create_category.html')

@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        flash('你只能删除自己的帖子。', 'danger')
        return redirect(url_for('view_post', post_id=post.id))
    cat_id = post.category_id
    db.session.delete(post)
    db.session.commit()
    flash('帖子已删除。', 'info')
    return redirect(url_for('category', cat_id=cat_id))

@app.route('/category/<int:cat_id>/delete', methods=['POST'])
@admin_required
def delete_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    name = cat.name
    db.session.delete(cat)
    db.session.commit()
    flash(f'分类「{name}」及其下所有帖子已删除。', 'info')
    return redirect(url_for('index'))

@app.route('/api/theme', methods=['POST'])
@login_required
def update_theme():
    data = request.get_json()
    theme_color = data.get('theme_color', '#6c5ce7')
    current_user.theme_color = theme_color
    db.session.commit()
    return jsonify({'status': 'ok', 'theme_color': theme_color})

@app.context_processor
def inject_theme():
    if current_user.is_authenticated:
        return {'user_theme': current_user.theme_color}
    return {'user_theme': '#6c5ce7'}

if __name__ == '__main__':
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
