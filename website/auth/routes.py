from website.auth import bp
from website.auth.forms import LoginForm, RegisterForm
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user
from website.models import User
from werkzeug.urls import url_parse
from website import db

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user or not user.check_password(password=form.password.data):
            flash("Sai email hoặc mật khẩu.")
            return redirect(url_for('auth.login'))
        login_user(user=user, remember=form.remember_me.data)
        flash("Đăng nhập thành công")
        next_page = request.args.get("next")
        if next_page is None or url_parse(next_page).netloc!='':
            return redirect(url_for('main.index'))
        return redirect(next_page)
    return render_template("auth/login.html", title="Login", form=form)

@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        u = User(username=form.username.data,\
            email=form.email.data)
        u.set_password(password=form.password.data)
        db.session.add(u)
        db.session.commit()
        flash("Chúc mừng bạn, bạn hiện là một người dùng, hãy đăng nhập!")
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title="register", form=form)
    