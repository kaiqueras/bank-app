from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Pessoa(db.Model):
    nome = db.Column(db.String(64), primary_key=True)
    saldo =  db.Column(db.Float, index=True)
    chavePix = db.Column(db.String(64), index=True)

    def to_dict(self):
        return {
            'nome': self.nome,
            'saldo': self.saldo,
            'chavePix': self.chavePix
        }

db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form.get('pix') == 'Fazer um PIX':
            return redirect('/pix')
        elif request.form.get('chave') == 'Cadastrar chave':
            return redirect('/chave')
        elif request.form.get('dados') == 'Banco de dados':
            return redirect('/dados')
        else:
            pass # unknown
    elif request.method == 'GET':
        return render_template('index.html', title='bank-app')
    return render_template('index.html', title='bank-app')

@app.route('/dados')
def dados():
    return render_template('server_table.html', title='bank-app')

@app.route('/pix', methods=['GET', 'POST'])
def pix():
    if request.method == 'POST':
        chave = request.form['chave']
        valor = request.form['valor']
        return ("PIX enviado!")
    elif request.method == 'GET':
        return render_template('pix.html', title='bank-app')


@app.route('/chave', methods=['GET', 'POST'])
def chave():
    if request.method == 'POST':
        nome = request.form['nome']
        chave = request.form['chave']

        return ("Chave cadastrada!")
    elif request.method == 'GET':
        return render_template('chave.html', title='bank-app')
    
    


@app.route('/api/data')
def data():
    query = Pessoa.query

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            Pessoa.nome.like(f'%{search}%'),
            Pessoa.saldo.like(f'%{search}%'),
            Pessoa.chavePix.like(f'%{search}%')
        ))
    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['nome', 'chavePix', 'saldo']:
            col_name = 'nome'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(Pessoa, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [papel.to_dict() for papel in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': Pessoa.query.count(),
        'draw': request.args.get('draw', type=int),
    }


if __name__ == '__main__':
    app.run(port=5001)
