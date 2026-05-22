from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    flash
)

from services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        usuario = AuthService.login(email, password)

        # 🔴 Validación segura
        if usuario and isinstance(usuario, dict):

            # Soporta "email" o "correo" por si tu DB usa otro nombre
            session["user"] = usuario.get("email") or usuario.get("correo")

            return redirect("/dashboard")

        flash("Credenciales incorrectas", "error")
        return redirect("/login")

    return render_template("login.html")


@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():

    if request.method == "POST":

        nombre = request.form.get("nombre")
        email = request.form.get("email")
        password = request.form.get("password")

        AuthService.register(nombre, email, password)

        flash("Usuario registrado correctamente", "success")
        return redirect("/login")

    return render_template("registro.html")


@auth_bp.route("/logout")
def logout():

    session.clear()
    return redirect("/login")