from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, validators
from wtforms.validators import DataRequired, URL, InputRequired
from flask_ckeditor import CKEditorField
from wtforms.fields.html5 import DateField, TimeField
from datetime import datetime

##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Título del post", validators=[DataRequired()])
    subtitle = StringField("Subtítulo", validators=[DataRequired()])
    img_url = StringField("Url de imagen", validators=[DataRequired(), URL()])
    body = CKEditorField("Contenido", validators=[DataRequired()])
    submit = SubmitField("Enviar Post")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    name = StringField("Nombre", validators=[DataRequired()])
    submit = SubmitField("Registrarme!")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    submit = SubmitField("Ingresar!")


class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comentario", validators=[DataRequired()])
    submit = SubmitField("Enviar comentario")


class DateForm(FlaskForm):
    name = StringField("Nombre Completo", validators=[DataRequired()])
    date = DateField("Fecha", validators=([InputRequired(), DataRequired()]))
    hour = TimeField("Hora", validators=([InputRequired(), DataRequired()]))
    submit = SubmitField("Agendar cita")
