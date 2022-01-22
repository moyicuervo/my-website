from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, validators
from wtforms.validators import DataRequired, URL, InputRequired, ValidationError
from flask_ckeditor import CKEditorField
from wtforms.fields.html5 import DateField, TimeField
from datetime import datetime, date

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
    name = StringField("Nombre", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    phone = StringField("Teléfono", validators=[DataRequired()])
    date = DateField("Fecha", validators=([InputRequired(), DataRequired()]))
    hour = TimeField("Hora", validators=([InputRequired(), DataRequired()]))
    submit = SubmitField("Agendar cita")

    def validate_date(form, field):
        if form.date.data < date.today():
            raise ValidationError("No es posible elegir un día anterior")
        elif form.date.data == date.today():
            raise ValidationError("No es posible elegir la cita en el mismo día. Por favor, elegir con al menos un día de anticipación.")
        elif form.date.data.isoweekday() > 5:
            raise ValidationError("No es posible elegir fin de semana")

    def validate_hour(form,field):
        now = datetime.now()
        start = now.replace(hour=9, minute=59)
        stop = now.replace(hour=18, minute=00)
        if form.hour.data < datetime.time(start):
            raise ValidationError("No es posible elegir antes de las 10hs")
        elif form.hour.data > datetime.time(stop):
            raise ValidationError("No es posible elegir después de las 18hs")
        elif form.hour.data.minute != 0:
            raise ValidationError("No es posible elegir minutos distintos a 00. Los turnos son al comienzo de la hora, por ejemplo 14:00")