from flask import render_template, abort, redirect, url_for, request
from flask_login import login_required, current_user
from models import app, db, Class, ClassUser, Post, Work, WorkFile, rootclass_id
import forms

def get_validate_class(class_id):
    class_ = Class.query.get(class_id)
    if not class_:
        abort(403)
    return class_

def define_route():
    @app.route("/class/")
    @login_required
    def class_index():
        classes = db.session.query(Class).join(ClassUser).filter(
            ClassUser.user_id == current_user.id
        ).all()
        return render_template(
            "class/index.html",
            classes=classes,
            role=int(current_user.role)
        )

    @app.route("/class/new/", methods=["GET", "POST"])
    @login_required
    def new_class():
        if current_user.role >= 20:
            form = forms.CreateClassForm()
            classes = Class.query.all()
            class_names = [(class_.id, class_.name) for class_ in classes]
            form.parent.choices = class_names
            if form.validate_on_submit():
                if not form.parent.data:
                    parent_id = rootclass_id
                else:
                    parent_id = form.parent.data
                class_ = Class(name=form.name.data, parent_id=parent_id)
                db.session.add(class_)
                db.session.commit()
                db.session.add(ClassUser(class_id=class_.id, user_id=current_user.id))
                db.session.commit()
                return redirect(url_for("class_from_id", class_id=class_.id))
            else:
                return render_template("class/new.html", form=form)
        else:
            abort(403)

    @app.route("/class/<int:class_id>", methods=["GET", "POST"])
    @login_required
    def class_from_id(class_id):
        form = forms.PostForm()
        if form.validate_on_submit():
            print(form.body.data)
            post = Post(poster_id=current_user.id, content=form.body.data, class_id=class_id)
            db.session.add(post)
            db.session.commit()
            return redirect(request.url)
        else:
            return render_template(
                "class/stream.html",
                class_=get_validate_class(class_id),
                posts=db.session.query(Post)
                    .filter(Post.class_id == class_id)
                    .all(),
                form=form
            )

    @app.route("/class/<int:class_id>/work")
    @login_required
    def works(class_id):
        return render_template(
            "class/works.html",
            class_=get_validate_class(class_id),
            works=Work.query.all()
        )

    @app.route("/class/<int:class_id>/work/<int:work_id>")
    @login_required
    def work(class_id, work_id):
        return render_template(
            "class/work.html",
            class_=get_validate_class(class_id),
            work=Work.query.get(work_id),
            workfiles=db.session.query(WorkFile)
                .filter(WorkFile.user_id == current_user.id)
                .all()
        )
