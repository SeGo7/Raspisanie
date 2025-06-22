from flask import Flask, render_template_string, request
import plotly.graph_objects as go
import webview
import threading

DAY_RASPISANIE = {
    '10 а': [
        {'урок': 1, 'предмет': 'Разговоры о важном', 'кабинет': '224', 'учитель': 'Середухина Е.Н.'},
        {'урок': 2, 'предмет': 'Литература', 'кабинет': '318', 'учитель': 'Лёзова Е.А.'},
        {'урок': 3, 'предмет': 'Обществознание', 'кабинет': '114', 'учитель': 'Анисимова О.В.'},
        {'урок': 4, 'предмет': 'Литература', 'кабинет': '318', 'учитель': 'Лёзова Е.А.'},
        {'урок': 5, 'предмет': 'История', 'кабинет': '224', 'учитель': 'Сергеева Д.С.'},
        {'урок': 6, 'предмет': 'Алгебра', 'кабинет': '115', 'учитель': 'Каткова Г.Г.'},
        {'урок': 7, 'предмет': 'Геометрия', 'кабинет': '115', 'учитель': 'Каткова Г.Г.'}
    ]
}

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Расписание</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="p-4">
    <div class="container">
        <h2 class="mb-4">Выберите класс</h2>
        <form method="POST">
            <div class="input-group mb-3">
                <select class="form-select" name="klass">
                    {% for klass in klasses %}
                        <option value="{{ klass }}" {% if selected == klass %}selected{% endif %}>{{ klass }}</option>
                    {% endfor %}
                </select>
                <button class="btn btn-primary" type="submit">Показать</button>
            </div>
        </form>
        {% if table_html %}
            <h4>Расписание для {{ selected }}</h4>
            <div>{{ table_html|safe }}</div>
        {% endif %}
    </div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    selected = None
    table_html = ""
    klasses = list(DAY_RASPISANIE.keys())

    if request.method == "POST":
        selected = request.form["klass"]
        data = DAY_RASPISANIE.get(selected, [])

        rows = {}
        for row in data:
            urok = row['урок']
            entry = f"{row['предмет']}<br>{row['кабинет']}<br>{row['учитель']}"
            rows.setdefault(urok, []).append(entry)

        urok_numbers = []
        predmets = []

        for i in sorted(rows.keys()):
            urok_numbers.append(str(i))
            predmets.append('<hr>'.join(rows[i]))

        fig = go.Figure(data=[go.Table(
            header=dict(values=["Урок", "Предмет / Кабинет / Учитель"],
                        fill_color='paleturquoise',
                        align='left'),
            cells=dict(values=[urok_numbers, predmets],
                       fill_color='lavender',
                       align='left'))
        ])
        fig.update_layout(margin=dict(t=10, b=10, l=0, r=0), height=400)
        table_html = fig.to_html(full_html=False)

    return render_template_string(HTML_TEMPLATE, klasses=klasses, selected=selected, table_html=table_html)


def start_app():
    app.run()


def start_gui():
    webview.create_window("Расписание", "http://localhost:5000", width=900, height=700)


threading.Thread(target=start_app).start()
threading.Thread(target=start_gui).start()
