from flask import Flask, request, jsonify
import sqlite3
import datetime

app = Flask(__name__)

# --- Función auxiliar para conectar a la DB ---
def get_db_connection():
    conn = sqlite3.connect('clientes.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- 1. GET /clientes ---
@app.route('/clientes', methods=['GET'])
def obtener_clientes():
    conn = get_db_connection()
    clientes = conn.execute('SELECT * FROM clientes').fetchall()
    conn.close()
    return jsonify([dict(row) for row in clientes])

# --- 2. GET /cliente/<id> ---
@app.route('/cliente/<int:id>', methods=['GET'])
def obtener_cliente(id):
    conn = get_db_connection()
    cliente = conn.execute('SELECT * FROM clientes WHERE id = ?', (id,)).fetchone()
    conn.close()
    if cliente:
        return jsonify(dict(cliente))
    return jsonify({'error': 'Cliente no encontrado'}), 404

# --- 3. POST /cliente ---
@app.route('/cliente', methods=['POST'])
def agregar_cliente():
    data = request.get_json()
    try:
        nombre = data['nombre']
        telefono = data['telefono']
        ultima_compra = data['ultima_compra']
        frecuencia = int(data['frecuencia'])
        datetime.datetime.strptime(ultima_compra, '%Y-%m-%d')  # Validar fecha
    except:
        return jsonify({'error': 'Datos inválidos'}), 400

    conn = get_db_connection()
    conn.execute('INSERT INTO clientes (nombre, telefono, ultima_compra, frecuencia) VALUES (?, ?, ?, ?)',
                 (nombre, telefono, ultima_compra, frecuencia))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Cliente agregado correctamente'}), 201

# --- 4. PUT /cliente/<id> ---
@app.route('/cliente/<int:id>', methods=['PUT'])
def actualizar_cliente(id):
    data = request.get_json()
    campos = []
    valores = []
    for campo in ['nombre', 'telefono', 'ultima_compra', 'frecuencia']:
        if campo in data:
            campos.append(f"{campo} = ?")
            valores.append(data[campo])
    if not campos:
        return jsonify({'error': 'No se proporcionaron campos para actualizar'}), 400

    valores.append(id)
    conn = get_db_connection()
    conn.execute(f"UPDATE clientes SET {', '.join(campos)} WHERE id = ?", valores)
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Cliente actualizado'})

# --- 5. DELETE /cliente/<id> ---
@app.route('/cliente/<int:id>', methods=['DELETE'])
def eliminar_cliente(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM clientes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Cliente eliminado'})

# --- 6. GET /cliente/<id>/estado ---
@app.route('/cliente/<int:id>/estado', methods=['GET'])
def estado_cliente(id):
    conn = get_db_connection()
    cliente = conn.execute('SELECT ultima_compra, frecuencia FROM clientes WHERE id = ?', (id,)).fetchone()
    conn.close()
    if not cliente:
        return jsonify({'error': 'Cliente no encontrado'}), 404

    ult_compra = datetime.datetime.strptime(cliente['ultima_compra'], '%Y-%m-%d').date()
    frecuencia = cliente['frecuencia']
    dias = (datetime.datetime.now().date() - ult_compra).days

    if dias <= frecuencia:
        estado = 'al_dia'
    elif dias - frecuencia == 1:
        estado = 'proximo'
    else:
        estado = 'vencido'

    return jsonify({'estado': estado})

if __name__ == '__main__':
    app.run(debug=True)
