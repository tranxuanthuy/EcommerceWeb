from website.main import bp
from flask import render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required
from flask_login import current_user
from datetime import datetime
from website.models import db, User, Post, Comment
from website.main.form import EditProfile, PostForm, CommentForm, PostUpdate

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page=page, per_page=current_app.config["POSTS_PER_PAGE"]
    )
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("main/index.html", title="Home", \
        posts=posts.items, next_url=next_url, prev_url=prev_url)

@bp.route("/explore")
def explore():
    page = request.args.get("page", 1, type=int)
    posts = Post.all_posts().paginate(
        page=page, per_page=current_app.config["POSTS_PER_PAGE"]
    )
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('main/index.html', posts=posts.items, title="Explore", \
        next_url=next_url, prev_url=prev_url)

@bp.route("/upload_post", methods=["GET", "POST"])
@login_required
def upload_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, image_url=form.image_url.data, \
            category=form.category.data, price=form.price.data,\
                detail=form.detail.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Đã đăng lên trang chủ.")
        return redirect(url_for("main.index"))
    return render_template('main/upload_post.html', title="post", form=form)


@bp.route("/user/<id>")
def user(id):
    user = User.query.filter_by(id=id).first_or_404()
    page = request.args.get("page", 1, type=int)
    posts = user.my_posts().paginate(
        page=page, per_page=current_app.config["POSTS_PER_PAGE"]
    )
    next_url = url_for('main.user', id=id , page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user', id=id , page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("main/user.html", user=user, posts=posts.items, \
         title="Profile", next_url=next_url, prev_url=prev_url)

@bp.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfile()
    if form.validate_on_submit():
        current_user.username=form.username.data
        current_user.about_me=form.about_me.data
        db.session.commit()
        flash("Thay đổi đã được lưu.")
        return redirect(url_for('main.user', id=current_user.id))
    elif request.method == "GET":
        form.about_me.data = current_user.about_me
        form.username.data = current_user.username
    return render_template('main/edit_profile.html', title="Edit profile", \
        form=form)

@bp.route("/follow/<id>")
@login_required
def follow(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        flash("Không tìm thấy người dùng")
        return redirect(url_for('main.index'))
    elif user == current_user:
        flash("Bạn không thể tự theo dõi chính mình!")
        return redirect(url_for('main.user', id=id))
    current_user.follow(user)
    db.session.commit()
    flash('Bạn đang theo dõi %s' % user.username)
    return redirect(url_for('main.user', id=id))

@bp.route('/unfollow/<id>')
@login_required
def unfollow(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        flash("Không tìm thấy người dùng")
        return redirect(url_for('main.index'))
    elif user == current_user:
        flash("Bạn không thể bỏ theo dõi chính mình!")
        return redirect(url_for('main.user', id=id))
    current_user.unfollow(user)
    db.session.commit()
    flash('Bạn đã bỏ theo dõi %s' % user.username)
    return redirect(url_for('main.user', id=id))

@bp.route('/post_detail/<post_id>', methods=["GET", "POST"])
def post_detail(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Bạn phải đăng nhập trước khi sử dụng chức năng này.")
            return redirect(url_for('auth.login'))
        c = Comment(comment=form.comment.data, post_id=post_id, user_id=current_user.id)
        db.session.add(c)
        db.session.commit()
        flash("Đã thêm một bình luận vào bài viết")
        return redirect(url_for('main.post_detail', post_id=post_id)) 
    post = Post.query.filter_by(id=post_id).first_or_404()
    page = request.args.get('page', 1, type=int)
    comments = post.comments.order_by(Comment.timestamp.desc()).paginate(
        page=page, per_page=current_app.config["POSTS_PER_PAGE"]
    )
    next_url = url_for('main.post_detail', post_id=post_id, page=comments.next_num) \
        if comments.has_next else None
    prev_url = url_for('main.post_detail', post_id=post_id, page=comments.prev_num) \
        if comments.has_prev else None
    return render_template('main/post_detail.html', title="Post detail", post=post, \
        form=form, comments = comments, next_url=next_url, prev_url=prev_url)

@bp.route('/edit_post/<post_id>', methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if current_user != post.author:
        flash('Bạn không thể chỉnh sửa bài viết này!')
        return redirect(url_for('main.explore'))
    form = PostUpdate()
    if form.validate_on_submit():
        post.title = form.title.data
        post.image_url = form.image_url.data
        post.category = form.category.data
        post.price = form.price.data
        post.detail = form.detail.data
        post.status = 1 if form.status.data == 'Đã bán' else 0
        db.session.add(post)
        db.session.commit()
        flash('Thay đổi đã được lưu.')
        return redirect(url_for('main.post_detail', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.image_url.data = post.image_url
        form.category.data = post.category
        form.price.data = post.price
        form.detail.data = post.detail
        form.status.data = 'Chưa bán' if post.status == 0 else 1
    return render_template('main/edit_post.html', title='Edit post', \
        form = form)

@bp.route('/selled/<user_id>')
def selled(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.selled().paginate(page=page, \
        per_page=current_app.config["POSTS_PER_PAGE"])
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('main/selled.html', title='selled', \
        posts=posts, next_url=next_url, prev_url=prev_url)

    

