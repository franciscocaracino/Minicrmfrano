import tkinter as tk
from tkinter import messagebox, simpledialog
import datetime
import requests
from flask import jsonify
import pywhatkit as kit


API_URL = "http://127.0.0.1:5000"
root = tk.Tk()
# --- Autenticación ---
def login():
    login_win = tk.Toplevel()
    login_win.title("Login")
    login_win.geometry("300x150")
    login_win.resizable(False, False)
    login_win.grab_set()  # bloqueo modal

    tk.Label(login_win, text="Usuario:").pack(pady=5)
    entry_user = tk.Entry(login_win)
    entry_user.pack(pady=5)

    tk.Label(login_win, text="Contraseña:").pack(pady=5)
    entry_pass = tk.Entry(login_win, show="*")
    entry_pass.pack(pady=5)

    def verificar():
        usuario = entry_user.get()
        contraseña = entry_pass.get()
        # Cambiar aquí usuario y contraseña deseados
        if usuario == "admin" and contraseña == "1234":
            login_win.destroy()
            root.deiconify()  # Mostrar ventana principal
            refrescar_lista_api()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    btn_login = tk.Button(login_win, text="Ingresar", command=verificar)
    btn_login.pack(pady=10)

    root.withdraw()  # Ocultar ventana principal mientras no se loguea

# --- Variables y Estadísticas ---
filtro_estado = tk.StringVar(value="Todos")

stats_total = tk.StringVar()
stats_alerta = tk.StringVar()
stats_promedio_frecuencia = tk.StringVar()
stats_compras_hoy = tk.StringVar()

# --- Funciones para usar API ---

def refrescar_lista_api():
    lista.delete(0, tk.END)

    filtro = filtro_estado.get()
    filtro_busqueda = entry_busqueda.get().strip().lower()
    hoy = datetime.datetime.now().date()

    try:
        response = requests.get(f"{API_URL}/clientes")
        if response.status_code != 200:
            messagebox.showerror("Error", "No se pudo obtener la lista de clientes")
            return

        registros = response.json()

        total = 0
        en_alerta = 0
        total_frecuencias = 0
        compras_hoy = 0

        for cliente in registros:
            id_ = cliente['id']
            nombre = cliente['nombre']
            tel = cliente['telefono']
            ult_compra = cliente['ultima_compra']
            freq = cliente['frecuencia']

            try:
                dias = (hoy - datetime.datetime.strptime(ult_compra, "%Y-%m-%d").date()).days
            except:
                continue

            if dias <= freq:
                estado = "✓"
                color = "green"
            else:
                estado = "⚠"
                color = "red"

            # Aplicar filtro estado
            if filtro == "Al día" and estado != "✓":
                continue
            elif filtro == "Vencidos" and estado != "⚠":
                continue
            elif filtro == "Próximos":
                dias_restantes = freq - dias
                if dias_restantes > 1 or dias_restantes < 0:
                    continue

            # Aplicar filtro de búsqueda por nombre
            if filtro_busqueda and filtro_busqueda not in nombre.lower():
                continue

            lista.insert(tk.END, f"{estado} {id_} - {nombre} | {tel} | Última: {ult_compra} | Frec: {freq} días")
            lista.itemconfig(tk.END, fg=color)

            # Estadísticas
            total += 1
            if estado == "⚠":
                en_alerta += 1
            total_frecuencias += freq
            if dias == 0:
                compras_hoy += 1

        stats_total.set(f"Total clientes: {total}")
        stats_alerta.set(f"En alerta: {en_alerta}")
        stats_promedio_frecuencia.set(f"Prom. frecuencia: {round(total_frecuencias / total, 2) if total else 0} días")
        stats_compras_hoy.set(f"Compras hoy: {compras_hoy}")

    except Exception as e:
        messagebox.showerror("Error", f"Error al conectar con API: {e}")

#def enviar_mensaje():
    #seleccionado = lista.curselection()
    #if not seleccionado:



def agregar_cliente_api():
    nombre = entry_nombre.get().strip()
    telefono = entry_telefono.get().strip()
    ultima_compra = entry_ultima_compra.get().strip()
    frecuencia = entry_frecuencia.get().strip()

    if not (nombre and telefono and ultima_compra and frecuencia):
        messagebox.showwarning("Aviso", "Complete todos los campos")
        return
    try:
        datetime.datetime.strptime(ultima_compra, '%Y-%m-%d')
        frecuencia = int(frecuencia)
    except ValueError:
        messagebox.showerror("Error", "Fecha o frecuencia inválida")
        return

    cliente = {
        "nombre": nombre,
        "telefono": telefono,
        "ultima_compra": ultima_compra,
        "frecuencia": frecuencia
    }
    #cliente = jsonify(cliente)

    try:
        response = requests.post("http://127.0.0.1:5000/cliente", json=cliente)   ###ACA ESTA EL PROBLEMA
        #response = requests.post("http://127.0.0.1:5000/clientes", json=cliente)
        if response.status_code == 201:
            messagebox.showinfo("Éxito", "Cliente agregado correctamente")
            refrescar_lista_api()
            entry_nombre.delete(0, tk.END)
            entry_telefono.delete(0, tk.END)
            entry_ultima_compra.delete(0, tk.END)
            entry_frecuencia.delete(0, tk.END)
        else:
            messagebox.showerror("Error", f"No se pudo agregar el cliente: {response.json().get('error')}")
    except Exception as e:
        messagebox.showerror("Error", f"Error de conexión: {e}")


def buscar_clientes(event=None):
    refrescar_lista_api()

def obtener_id_cliente_seleccionado():
    try:
        seleccionado = lista.get(lista.curselection())
        id_str = seleccionado.split(" - ")[0].split()[-1]  # Extrae el id
        return int(id_str)
    except:
        messagebox.showwarning("Aviso", "Seleccioná un cliente de la lista")
        return None


def actualizar_cliente_api():
    id_cliente = obtener_id_cliente_seleccionado()
    if id_cliente is None:
        return

    nombre = entry_nombre.get().strip()
    telefono = entry_telefono.get().strip()
    ultima_compra = entry_ultima_compra.get().strip()
    frecuencia = entry_frecuencia.get().strip()

    if not (nombre and telefono and ultima_compra and frecuencia):
        messagebox.showwarning("Aviso", "Complete todos los campos para actualizar")
        return
    try:
        datetime.datetime.strptime(ultima_compra, '%Y-%m-%d')
        frecuencia = int(frecuencia)
    except ValueError:
        messagebox.showerror("Error", "Fecha o frecuencia inválida")
        return

    cliente = {
        "nombre": nombre,
        "telefono": telefono,
        "ultima_compra": ultima_compra,
        "frecuencia": frecuencia
    }

    try:
        response = requests.put(f"{API_URL}/cliente/{id_cliente}", json=cliente)
        if response.status_code == 200:
            messagebox.showinfo("Éxito", "Cliente actualizado")
            refrescar_lista_api()
        else:
            messagebox.showerror("Error", f"No se pudo actualizar: {response.json().get('error')}")
    except Exception as e:
        messagebox.showerror("Error", f"Error de conexión: {e}")


def eliminar_cliente_api():
    id_cliente = obtener_id_cliente_seleccionado()
    if id_cliente is None:
        return

    confirmar = messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar este cliente?")
    if not confirmar:
        return

    try:
        response = requests.delete(f"{API_URL}/cliente/{id_cliente}")
        if response.status_code == 200:
            messagebox.showinfo("Éxito", "Cliente eliminado")
            refrescar_lista_api()
        else:
            messagebox.showerror("Error", f"No se pudo eliminar: {response.json().get('error')}")
    except Exception as e:
        messagebox.showerror("Error", f"Error de conexión: {e}")

def enviar_whatsapp():
    id_cliente = obtener_id_cliente_seleccionado()
    if id_cliente is None:
        return

    try:
        response = requests.get(f"{API_URL}/cliente/{id_cliente}")
        if response.status_code != 200:
            messagebox.showerror("Error", "No se pudo obtener el cliente")
            return

        cliente = response.json()
        telefono = cliente["telefono"]
        nombre = cliente["nombre"]

        mensaje = f"Hola {nombre}, te recordamos que estás a tiempo de realizar tu próxima compra. ¡Gracias por confiar en nosotros!"

        ahora = datetime.datetime.now()
        hora = ahora.hour
        minuto = (ahora.minute + 2) % 60
        if ahora.minute >= 58:
            hora += 1

        kit.sendwhatmsg(telefono, mensaje, hora, minuto)
        messagebox.showinfo("Éxito", f"Mensaje programado a {telefono}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo enviar el mensaje: {e}")
def actualizar_ultima_compra():
    id_cliente = obtener_id_cliente_seleccionado()
    if id_cliente is None:
        return

    nueva_fecha = datetime.datetime.now().strftime('%Y-%m-%d')

    # Solo actualizamos la fecha de última compra, mantenemos lo demás igual
    try:
        # Primero obtenemos los datos actuales del cliente
        response_get = requests.get(f"{API_URL}/cliente/{id_cliente}")
        if response_get.status_code != 200:
            messagebox.showerror("Error", "No se pudo obtener el cliente")
            return

        cliente = response_get.json()
        cliente["ultima_compra"] = nueva_fecha  # Actualizamos solo la fecha

        # Hacemos el PUT
        response_put = requests.put(f"{API_URL}/cliente/{id_cliente}", json=cliente)
        if response_put.status_code == 200:
            messagebox.showinfo("Éxito", "Última compra actualizada")
            refrescar_lista_api()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el cliente")
    except Exception as e:
        messagebox.showerror("Error", f"Error al actualizar: {e}")


# --- UI ---
root.title("Mini CRM Clientes")
root.geometry("900x600")
root.configure(bg="#f2f2f2")

frame = tk.Frame(root, bg="#f2f2f2")
frame.pack(padx=10, pady=10, fill="x")

tk.Label(frame, text="Nombre", bg="#f2f2f2").grid(row=0, column=0, sticky="w")
entry_nombre = tk.Entry(frame)
entry_nombre.grid(row=0, column=1, sticky="ew")

tk.Label(frame, text="Teléfono (+549...)", bg="#f2f2f2").grid(row=1, column=0, sticky="w")
entry_telefono = tk.Entry(frame)
entry_telefono.grid(row=1, column=1, sticky="ew")

tk.Label(frame, text="Última compra (AAAA-MM-DD)", bg="#f2f2f2").grid(row=2, column=0, sticky="w")
entry_ultima_compra = tk.Entry(frame)
entry_ultima_compra.grid(row=2, column=1, sticky="ew")

tk.Label(frame, text="Frecuencia (días)", bg="#f2f2f2").grid(row=3, column=0, sticky="w")
entry_frecuencia = tk.Entry(frame)
entry_frecuencia.grid(row=3, column=1, sticky="ew")

frame_botones = tk.Frame(frame, bg="#f2f2f2")
frame_botones.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

btn_agregar = tk.Button(frame_botones, text="Agregar", bg="#4CAF50", fg="white", width=20, command=agregar_cliente_api)
btn_agregar.grid(row=0, column=0, padx=5, pady=5)

btn_actualizar = tk.Button(frame_botones, text="Actualizar", bg="#2196F3", fg="white", width=20, command=actualizar_cliente_api)
btn_actualizar.grid(row=0, column=1, padx=5, pady=5)

btn_eliminar = tk.Button(frame_botones, text="Eliminar", bg="#f44336", fg="white", width=20, command=eliminar_cliente_api)
btn_eliminar.grid(row=1, column=0, padx=5, pady=5)

btn_whatsapp = tk.Button(frame_botones, text="WhatsApp", bg="#25D366", fg="white", width=20, command=enviar_whatsapp)
btn_whatsapp.grid(row=1, column=1, padx=5, pady=5)

btn_actualizar_fecha = tk.Button(frame_botones, text="Actualizar ultima compra", bg="#FF9800", fg="white", width=20, command=actualizar_ultima_compra)
btn_actualizar_fecha.grid(row=2, column=0, columnspan=2, pady=5)


frame.columnconfigure(1, weight=1)

frame_filtro = tk.Frame(root, bg="#f2f2f2")
frame_filtro.pack(padx=10, pady=5, fill="x")

tk.Label(frame_filtro, text="Filtrar por estado:", bg="#f2f2f2").pack(side="left")

opciones = ["Todos", "Al día", "Vencidos", "Próximos"]
tk.OptionMenu(frame_filtro, filtro_estado, *opciones, command=lambda _: refrescar_lista_api()).pack(side="left", padx=5)

frame_busqueda = tk.Frame(root, bg="#f2f2f2")
frame_busqueda.pack(pady=5)
tk.Label(frame_busqueda, text="Buscar por nombre:", bg="#f2f2f2").pack(side="left")
entry_busqueda = tk.Entry(frame_busqueda)
entry_busqueda.pack(side="left")
entry_busqueda.bind("<KeyRelease>", buscar_clientes)

lista = tk.Listbox(root, height=20, font=("Consolas", 10))
lista.pack(padx=10, pady=5, fill="both", expand=True)

frame_stats = tk.Frame(root, bg="#f2f2f2")
frame_stats.pack(padx=10, pady=10, fill="x")

tk.Label(frame_stats, textvariable=stats_total, bg="#f2f2f2").pack(side="left", padx=10)
tk.Label(frame_stats, textvariable=stats_alerta, fg="red", bg="#f2f2f2").pack(side="left", padx=10)
tk.Label(frame_stats, textvariable=stats_promedio_frecuencia, bg="#f2f2f2").pack(side="left", padx=10)
tk.Label(frame_stats, textvariable=stats_compras_hoy, fg="green", bg="#f2f2f2").pack(side="left", padx=10)



# --- Ejecutar login y app ---
login()

root.mainloop()

