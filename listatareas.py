import customtkinter as ctk
import json
import os
from tkinter import messagebox

# --- Configuración Visual ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ==========================================
# 1. EL BACKEND: GESTIÓN DE DATOS Y ESTADO
# ==========================================
class GestorTareas:
    def __init__(self, archivo_datos="mis_tareas.json"):
        self.archivo_datos = archivo_datos
        self.tareas = self.cargar_tareas()

    def cargar_tareas(self):
        # Si el archivo existe, leemos los datos. 
        if os.path.exists(self.archivo_datos):
            try:
                with open(self.archivo_datos, "r", encoding="utf-8") as archivo:
                    return json.load(archivo)
            except json.JSONDecodeError:
                return []
        return []

    def guardar_tareas(self):
        # Escribimos la lista actual de tareas en el archivo JSON
        with open(self.archivo_datos, "w", encoding="utf-8") as archivo:
            json.dump(self.tareas, archivo, indent=4, ensure_ascii=False)

    def agregar_tarea(self, descripcion):
        # Asignamos un ID único basado en la cantidad de tareas o el último ID
        nuevo_id = 1 if not self.tareas else max(t["id"] for t in self.tareas) + 1
        nueva_tarea = {
            "id": nuevo_id,
            "descripcion": descripcion,
            "completada": False
        }
        self.tareas.append(nueva_tarea)
        self.guardar_tareas()

    def alternar_estado(self, id_tarea, estado_actual):
        # Cambiamos el estado (True/False) de la tarea seleccionada
        for tarea in self.tareas:
            if tarea["id"] == id_tarea:
                tarea["completada"] = estado_actual
                break
        self.guardar_tareas()

    def eliminar_tarea(self, id_tarea):
        # Filtramos la lista para dejar todas las tareas EXCEPTO la que queremos borrar
        self.tareas = [t for t in self.tareas if t["id"] != id_tarea]
        self.guardar_tareas()

    def obtener_tareas(self):
        return self.tareas

# ==========================================
# 2. EL FRONTEND: INTERFAZ DE USUARIO
# ==========================================
class AppTareas(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gestor de Tareas Pro")
        self.geometry("500x600")
        self.minsize(400, 500)

        # Instanciamos nuestra base de datos lógica
        self.gestor = GestorTareas()

        self.crear_interfaz()

    def crear_interfaz(self):
        self.vista_actual = "pendientes"

        # Contenedor superior
        self.frame_superior = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_superior.pack(pady=(20, 15), fill="x", padx=20)

        # Título
        self.lbl_titulo = ctk.CTkLabel(self.frame_superior, text="Mis Tareas Pendientes", font=("Segoe UI", 24, "bold"))
        self.lbl_titulo.pack(side="left")

        # Botón para cambiar vista
        self.btn_cambiar_vista = ctk.CTkButton(self.frame_superior, text="Ver Completadas", font=("Segoe UI", 12, "bold"), width=120, height=30, fg_color="#27ae60", hover_color="#2ecc71", command=self.alternar_vista)
        self.btn_cambiar_vista.pack(side="right")

        # Panel de Entrada 
        self.frame_entrada = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_entrada.pack(padx=20, fill="x")

        self.entrada_tarea = ctk.CTkEntry(self.frame_entrada, font=("Segoe UI", 16), placeholder_text="¿Qué necesitas hacer hoy?", height=40)
        self.entrada_tarea.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Permitir agregar tarea presionando "Enter"
        self.entrada_tarea.bind('<Return>', lambda event: self.agregar_nueva_tarea())

        self.btn_agregar = ctk.CTkButton(self.frame_entrada, text="Agregar", font=("Segoe UI", 14, "bold"), width=80, height=40, command=self.agregar_nueva_tarea)
        self.btn_agregar.pack(side="right")

        # Contenedor con Scroll para la lista de tareas
        self.frame_lista = ctk.CTkScrollableFrame(self, corner_radius=10, fg_color="#1e1e1e")
        self.frame_lista.pack(padx=20, pady=20, fill="both", expand=True)

        # Dibujar las tareas que ya existen en el JSON al abrir la app
        self.dibujar_lista_tareas()

    def alternar_vista(self):
        if self.vista_actual == "pendientes":
            self.vista_actual = "completadas"
            self.lbl_titulo.configure(text="Tareas Completadas")
            self.btn_cambiar_vista.configure(text="Ver Pendientes", fg_color="#2980b9", hover_color="#3498db")
            self.frame_entrada.pack_forget()
        else:
            self.vista_actual = "pendientes"
            self.lbl_titulo.configure(text="Mis Tareas Pendientes")
            self.btn_cambiar_vista.configure(text="Ver Completadas", fg_color="#27ae60", hover_color="#2ecc71")
            self.frame_entrada.pack(padx=20, fill="x", after=self.frame_superior)
            
        self.dibujar_lista_tareas()

    def agregar_nueva_tarea(self):
        texto_tarea = self.entrada_tarea.get().strip()
        if not texto_tarea:
            messagebox.showwarning("Campo vacío", "Escribe una tarea antes de agregarla.")
            return

        # 1. Guardar en el backend
        self.gestor.agregar_tarea(texto_tarea)
        
        # 2. Limpiar el input
        self.entrada_tarea.delete(0, 'end')
        
        # 3. Recargar la interfaz visual
        self.dibujar_lista_tareas()

    def dibujar_lista_tareas(self):
        # Limpiar el frame visual antes de redibujar para no duplicar elementos
        for widget in self.frame_lista.winfo_children():
            widget.destroy()

        todas_las_tareas = self.gestor.obtener_tareas()
        
        if self.vista_actual == "pendientes":
            tareas_filtradas = [t for t in todas_las_tareas if not t["completada"]]
            msg_vacio = "No hay tareas pendientes. ¡Estás al día!"
        else:
            tareas_filtradas = [t for t in todas_las_tareas if t["completada"]]
            msg_vacio = "No hay tareas completadas aún."

        if not tareas_filtradas:
            lbl_vacio = ctk.CTkLabel(self.frame_lista, text=msg_vacio, text_color="gray", font=("Segoe UI", 14))
            lbl_vacio.pack(pady=20)
            return

        # Dibujar cada tarea dinámicamente
        for tarea in tareas_filtradas:
            self.crear_fila_tarea(tarea)

    def crear_fila_tarea(self, tarea):
        frame_fila = ctk.CTkFrame(self.frame_lista, fg_color="transparent")
        frame_fila.pack(fill="x", pady=5)

        fuente = ("Segoe UI", 16, "overstrike") if tarea["completada"] else ("Segoe UI", 16)
        color_texto = "gray" if tarea["completada"] else "white"

        # Checkbox nativo que incluye el texto de la tarea
        checkbox = ctk.CTkCheckBox(
            frame_fila, 
            text=tarea["descripcion"], 
            font=fuente, 
            text_color=color_texto,
            command=lambda t=tarea: self.al_marcar_checkbox(t)
        )
        # Seleccionamos visualmente la casilla si ya estaba completada en la base de datos
        if tarea["completada"]:
            checkbox.select()
            
        checkbox.pack(side="left", padx=10, fill="x", expand=True)

        # Botón de eliminar 
        btn_eliminar = ctk.CTkButton(
            frame_fila, 
            text="❌", 
            width=30, 
            fg_color="transparent", 
            hover_color="#c0392b",
            command=lambda id_t=tarea["id"]: self.al_eliminar_tarea(id_t)
        )
        btn_eliminar.pack(side="right", padx=5)

    def al_marcar_checkbox(self, tarea):
        nuevo_estado = not tarea["completada"]
        self.gestor.alternar_estado(tarea["id"], nuevo_estado)
        self.dibujar_lista_tareas()

    def al_eliminar_tarea(self, id_tarea):
        self.gestor.eliminar_tarea(id_tarea)
        self.dibujar_lista_tareas()

# --- Arranque del Programa ---
if __name__ == "__main__":
    app = AppTareas()
    app.mainloop()
