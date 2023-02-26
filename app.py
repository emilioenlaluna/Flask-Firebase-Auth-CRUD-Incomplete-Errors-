from curses import flash
import json
from flask import Flask, render_template, request, redirect, session,url_for,jsonify
import pyrebase
import json
import urllib.parse
app = Flask(__name__)
app.secret_key = "secret"

config = {
  "apiKey": "AIzaSyB1OB6Y58-o-YySmJcSrv3MoCV0MB3aEK8",
  "authDomain": "hopelinku.firebaseapp.com",
  "databaseURL": "https://hopelinku-default-rtdb.firebaseio.com",
  "projectId": "hopelinku",
  "storageBucket": "hopelinku.appspot.com",
  "messagingSenderId": "829128138012",
  "appId": "1:829128138012:web:6bf6e437343f8483eb6ed9"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

@app.route("/")
def home():
    if "user" in session:
        user = session["user"]
        p = 'user_id'
        id = user["localId"]
        blogs = db.child("blogs").get()
        posts = []
        for blog in blogs.each():
            post = blog.val()
            post["id"] = blog.key()
            posts.append(post)
        return render_template("dashboard.html", user=user, blogs=posts)
    else:
        return redirect("/login")

@app.route("/blogs/<blog_id>")
def view_blog(blog_id):
    blog = db.child("blogs").child(blog_id).get()
    if not blog.val():
        return "Blog entry not found"
    return render_template("view_blog.html", blog=blog.val())


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session["user"] = user
            return redirect("/")
        except:
            message = "Invalid credentials. Please try again."
            return render_template("login.html", message=message)
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        try:
            user = auth.create_user_with_email_and_password(email, password)
            session["user"] = user
            return redirect("/")
        except:
            message = "The email address is already in use by another account."
            return render_template("register.html", message=message)
    else:
        return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

@app.route("/blogs/new", methods=["GET", "POST"])
def new_blog():
    if "user" not in session:
        return redirect("/login")
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        user_id = session["user"]["localId"]
        db.child("blogs").push({"title": title, "content": content, "user_id": user_id})
        return redirect(url_for("login"))
    else:
        return render_template("home")

@app.route("/blogs/<blog_id>/edit", methods=["GET", "POST"])
def edit_blog(blog_id):
    if "user" not in session:
        return redirect("/login")
    blog = db.child("blogs").child(blog_id).get()
    if not blog.val():
        return "Blog entry not found"
    if blog.val()["user_id"] != session["user"]["localId"]:
        return "You are not authorized to edit this blog entry"
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        db.child("blogs").child(blog_id).update({"title": title, "content": content})
        return redirect("/")
    else:
        return render_template("edit_blog.html", blog=blog.val())

@app.route("/blogs/<blog_id>/delete", methods=["POST","GET"])
def delete_blog(blog_id):
    # Get the current user's ID
    current_user_id = session.get('user')

    # Check if the user is logged in
    if not current_user_id:
        flash("You must be logged in to delete a blog.")
        return redirect(url_for("login"))

    # Get a reference to the blog's document in Firebase
    blog_ref = db.collection("blogs").document(blog_id)

    # Check if the blog exists
    if not blog_ref.get().exists:
        flash("Blog does not exist.")
        return redirect(url_for("blogs.index"))

    # Check if the user is the creator of the blog
    blog = blog_ref.get().to_dict()
    if blog["user_id"] != current_user_id:
        flash("You can only delete blogs that you have created.")
        return redirect(url_for("blogs.index"))

    # Delete the blog
    blog_ref.delete()

    flash("Blog deleted successfully.")
    return redirect(url_for("blogs.index"))


if __name__ == '__main__':
   app.run()

  
