from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
import os, json, threading
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# ── CONFIG ──────────────────────────────────────────────
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'sportfactory-secret-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///sportfactory.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('GMAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv('GMAIL_APP_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('GMAIL_USER')

db = SQLAlchemy(app)
mail = Mail(app)

# ── MODELS ──────────────────────────────────────────────
class Order(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    order_code    = db.Column(db.String(10), unique=True, nullable=False)
    client_name   = db.Column(db.String(120), nullable=False)
    client_email  = db.Column(db.String(120), nullable=False)
    client_phone  = db.Column(db.String(40))
    empresa       = db.Column(db.String(120))
    products      = db.Column(db.Text)
    quantities    = db.Column(db.Text)
    colors        = db.Column(db.String(200))
    impresion     = db.Column(db.String(200))
    specs         = db.Column(db.Text)
    fecha_deseada = db.Column(db.String(60))
    presupuesto   = db.Column(db.String(50))
    products_detail = db.Column(db.Text)
    stage         = db.Column(db.String(30), default='recibido')
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':           self.order_code,
            'client':       self.client_name,
            'email':        self.client_email,
            'phone':        self.client_phone or '',
            'empresa':      self.empresa or '',
            'products':     json.loads(self.products or '[]'),
            'qty':          json.loads(self.quantities or '{}'),
            'colors':       self.colors or '',
            'impresion':    self.impresion or '',
            'specs':        self.specs or '',
            'fecha_deseada':self.fecha_deseada or '',
            'presupuesto':  self.presupuesto or '',
            'products_detail': json.loads(self.products_detail or '[]'),
            'stage':        self.stage,
            'date':         self.created_at.strftime('%Y-%m-%d'),
        }

# ── HELPERS ─────────────────────────────────────────────
STAGE_LABELS = {
    'recibido':    'Recibido',
    'proceso':     'En Proceso',
    'terminacion': 'Terminación',
    'despacho':    'Despacho',
}
STAGES = ['recibido', 'proceso', 'terminacion', 'despacho']

def generate_order_code():
    last = Order.query.order_by(Order.id.desc()).first()
    num = (last.id + 1) if last else 1
    return f'#{str(num).zfill(3)}'

def build_products_detail_text(products_detail):
    lines = []
    for p in products_detail:
        name = p.get('name', '')
        sizes = p.get('sizes', {})
        color = p.get('color', '')
        print_type = p.get('print', '')
        specs = p.get('specs', '')
        sizes_str = ', '.join(f"{k}: {v}" for k, v in sizes.items() if v)
        line = f"• {name}"
        if sizes_str: line += f" | Tallas: {sizes_str}"
        if color:     line += f" | Color: {color}"
        if print_type: line += f" | Impresión: {print_type}"
        if specs:     line += f" | Diseño: {specs}"
        lines.append(line)
    return '\n'.join(lines)

def send_status_email(order, stage):
    if not app.config['MAIL_USERNAME']:
        print(f"[EMAIL SKIPPED] No Gmail configurado.")
        return

    try:
        detail = json.loads(order.products_detail or '[]')
        detail_text = build_products_detail_text(detail) if detail else order.products
    except:
        detail_text = order.products or ''

    messages = {
        'recibido': f"""
¡Hola {order.client_name}!

✅ Recibimos tu pedido {order.order_code} con éxito.

Nuestro equipo ya tiene tu orden y comenzará la producción pronto.
Te vamos a ir avisando en cada etapa del proceso.

📦 Detalle de tu pedido:
{detail_text}

⏱️ Entrega estimada: 5 días hábiles

¡Gracias por confiar en SportFactory!
        """,
        'proceso': f"""
¡Hola {order.client_name}!

⚙️ Tu pedido {order.order_code} está ahora EN PRODUCCIÓN.

Nuestro equipo está trabajando en tu ropa deportiva.
Te avisaremos cuando entre en etapa de terminación.

Si tienes alguna duda puedes responder este email.

¡Saludos, SportFactory!
        """,
        'terminacion': f"""
¡Hola {order.client_name}!

🔍 Tu pedido {order.order_code} está en TERMINACIÓN y control de calidad.

Estamos haciendo los últimos retoques y verificando que todo
esté perfecto antes de despachártelo.

Ya casi está listo — te avisamos cuando salga para ti.

¡Saludos, SportFactory!
        """,
        'despacho': f"""
¡Hola {order.client_name}!

🚚 ¡Tu pedido {order.order_code} está en camino!

Tu ropa deportiva ya fue despachada y pronto llegará a tus manos.

Gracias por confiar en SportFactory. ¡Esperamos que te encante!

— Saury, Paola y Angela
        """,
    }

    subject_map = {
        'recibido':    f'✅ Pedido {order.order_code} recibido — SportFactory',
        'proceso':     f'⚙️ Tu pedido {order.order_code} está en producción',
        'terminacion': f'🔍 Tu pedido {order.order_code} en terminación',
        'despacho':    f'🚚 ¡Tu pedido {order.order_code} fue despachado!',
    }

    # ── Enviar en hilo separado pa' no bloquear el worker ──
    def _send(subject, recipient, body):
        try:
            with app.app_context():
                msg = Message(
                    subject=subject,
                    recipients=[recipient],
                    body=body,
                )
                mail.send(msg)
                print(f"[EMAIL SENT] {recipient} — stage: {stage}")
        except Exception as e:
            print(f"[EMAIL ERROR] {e}")

    t = threading.Thread(target=_send, args=(
        subject_map.get(stage, f'Actualización pedido {order.order_code}'),
        order.client_email,
        messages.get(stage, ''),
    ))
    t.daemon = True
    t.start()

# ── ROUTES ──────────────────────────────────────────────
@app.route('/api/verify-pin', methods=['POST'])
def verify_pin():
    data = request.json or {}
    if data.get('pin') == os.getenv('ADMIN_PIN', '2024'):
        return jsonify({'ok': True})
    return jsonify({'error': 'PIN incorrecto'}), 403

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/orders', methods=['GET'])
def get_orders():
    orders = Order.query.order_by(Order.id.desc()).all()
    return jsonify([o.to_dict() for o in orders])

@app.route('/api/orders', methods=['POST'])
def create_order():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400
        if not data.get('client') or not data.get('email'):
            return jsonify({'error': 'Nombre y email son requeridos'}), 400

        products_list = data.get('products', [])
        if isinstance(products_list, str):
            products_list = [products_list]

        qty_data = data.get('qty', {})
        if not isinstance(qty_data, dict):
            qty_data = {}

        products_detail = data.get('products_detail', [])
        if not isinstance(products_detail, list):
            products_detail = []

        order = Order(
            order_code      = generate_order_code(),
            client_name     = str(data['client']),
            client_email    = str(data['email']),
            client_phone    = str(data.get('phone', '')),
            empresa         = str(data.get('empresa', '')),
            products        = json.dumps(products_list, ensure_ascii=False),
            quantities      = json.dumps(qty_data, ensure_ascii=False),
            colors          = str(data.get('colors', ''))[:200],
            impresion       = str(data.get('impresion', ''))[:200],
            specs           = str(data.get('specs', '')),
            fecha_deseada   = str(data.get('fecha_deseada', '')),
            presupuesto     = str(data.get('presupuesto', '')),
            products_detail = json.dumps(products_detail, ensure_ascii=False),
            stage           = 'recibido',
        )
        db.session.add(order)
        db.session.commit()

        send_status_email(order, 'recibido')
        return jsonify(order.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        print(f"[ORDER ERROR] {e}")
        import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/<order_code>/advance', methods=['POST'])
def advance_order(order_code):
    try:
        data = request.json or {}
        if data.get('pin') != os.getenv('ADMIN_PIN', '2024'):
            return jsonify({'error': 'PIN incorrecto'}), 403

        order = Order.query.filter_by(order_code=order_code).first()
        if not order:
            return jsonify({'error': 'Orden no encontrada'}), 404

        si = STAGES.index(order.stage)
        if si >= len(STAGES) - 1:
            return jsonify({'error': 'Ya está en la última etapa'}), 400

        order.stage = STAGES[si + 1]
        db.session.commit()

        send_status_email(order, order.stage)
        return jsonify(order.to_dict())
    except Exception as e:
        db.session.rollback()
        print(f"[ADVANCE ERROR] {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/search', methods=['GET'])
def search_orders():
    q = request.args.get('q', '').lower()
    stage = request.args.get('stage', '')
    query = Order.query
    if stage:
        query = query.filter_by(stage=stage)
    orders = query.order_by(Order.id.desc()).all()
    if q:
        orders = [o for o in orders if q in o.client_name.lower() or q in o.order_code.lower()]
    return jsonify([o.to_dict() for o in orders])

with app.app_context():
    db.create_all()
    print("✅ Base de datos lista")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
