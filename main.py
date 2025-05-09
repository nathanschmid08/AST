import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import json
import traceback

# Wir verwenden pyjsparser für das JavaScript-Parsing
try:
    from pyjsparser import parse
    JS_PARSER = "pyjsparser"
except ImportError:
    # Wenn pyjsparser nicht verfügbar ist, versuchen wir es mit esprima-python
    try:
        import esprima
        JS_PARSER = "esprima"
    except ImportError:
        JS_PARSER = None

class JSASTParser(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("JavaScript AST Parser")
        self.geometry("1000x700")
        
        # Überprüfen ob eine Parser-Bibliothek verfügbar ist
        if JS_PARSER is None:
            self.check_dependencies()
        
        # Menü erstellen
        self.create_menu()
        
        # Hauptframe
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Paned window für flexible Größenanpassung
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Linke Seite - JavaScript Code
        left_frame = ttk.LabelFrame(paned, text="JavaScript Code")
        paned.add(left_frame, weight=1)
        
        # JavaScript Editor
        self.js_editor = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD, font=("Courier New", 11))
        self.js_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Button-Frame
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Parse-Button
        parse_button = ttk.Button(button_frame, text="Parse AST", command=self.parse_ast)
        parse_button.pack(side=tk.LEFT, padx=5)
        
        # Rechte Seite - AST Anzeige
        right_frame = ttk.LabelFrame(paned, text="Abstract Syntax Tree")
        paned.add(right_frame, weight=1)
        
        # Notebook für verschiedene Ansichten
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab für Baum-Ansicht
        tree_tab = ttk.Frame(self.notebook)
        self.notebook.add(tree_tab, text="Tree View")
        
        # AST Baum
        self.tree = ttk.Treeview(tree_tab)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Scrollbar für den Baum
        tree_scrollbar = ttk.Scrollbar(tree_tab, orient="vertical", command=self.tree.yview)
        tree_scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Tab für JSON-Ansicht
        json_tab = ttk.Frame(self.notebook)
        self.notebook.add(json_tab, text="JSON View")
        
        # JSON Textfeld
        self.json_view = scrolledtext.ScrolledText(json_tab, wrap=tk.WORD, font=("Courier New", 11))
        self.json_view.pack(fill=tk.BOTH, expand=True)
        
        # Beispiel-Code einfügen
        self.insert_example_code()
        
        # Status Bar
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        if JS_PARSER:
            self.status_var.set(f"Bereit: Verwende {JS_PARSER} Parser")
        else:
            self.status_var.set("Fehler: Keine Parser-Bibliothek gefunden!")

    def check_dependencies(self):
        """Überprüft, ob mindestens eine der benötigten Parser-Bibliotheken installiert ist"""
        msg = """Keine JavaScript Parser-Bibliothek gefunden!

Bitte installieren Sie eine der folgenden Bibliotheken mit pip:

pip install pyjsparser
oder
pip install esprima-python

Das Programm wird trotzdem gestartet, aber das Parsen wird nicht funktionieren.
"""
        messagebox.showwarning("Abhängigkeiten fehlen", msg)

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open...", command=self.open_file)
        file_menu.add_command(label="Save AST...", command=self.save_ast)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        
        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear", command=self.clear_editor)
        edit_menu.add_command(label="Insert Example", command=self.insert_example_code)
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Install Dependencies", command=self.show_install_help)

    def parse_ast(self):
        """JavaScript-Code parsen und AST generieren"""
        if JS_PARSER is None:
            messagebox.showerror("Fehler", "Keine JavaScript Parser-Bibliothek installiert")
            self.show_install_help()
            return

        js_code = self.js_editor.get("1.0", tk.END)
        if not js_code.strip():
            messagebox.showinfo("Info", "Bitte geben Sie JavaScript-Code ein.")
            return
        
        try:
            self.status_var.set("Generiere AST...")
            
            # Je nach verfügbarer Bibliothek den Parser auswählen
            if JS_PARSER == "pyjsparser":
                ast_data = parse(js_code)
            else:  # esprima
                ast_data = esprima.parseScript(js_code, options={'loc': True, 'range': True})
                # esprima gibt ein Objekt zurück, das wir in dict umwandeln müssen
                ast_data = ast_data.toDict()
            
            self.display_ast(ast_data)
            self.status_var.set("AST erfolgreich generiert!")
            
        except Exception as e:
            error_msg = f"JavaScript Parse Fehler: {str(e)}"
            messagebox.showerror("Parse Error", error_msg)
            self.status_var.set("Fehler beim Parsen!")
            traceback.print_exc()  # Ausführliche Fehlerinfo in der Konsole

    def display_ast(self, ast_data):
        """Den AST in der GUI anzeigen"""
        # JSON-Ansicht aktualisieren
        self.json_view.delete("1.0", tk.END)
        self.json_view.insert("1.0", json.dumps(ast_data, indent=2))
        
        # Baum zurücksetzen
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Root-Element hinzufügen
        if 'type' in ast_data:
            root_type = ast_data['type']
        else:
            root_type = 'Program'  # pyjsparser verwendet nicht immer 'type'
        
        root = self.tree.insert("", "end", text=f"Program ({root_type})", open=True)
        
        # Rekursive Baumbildung
        self._build_tree(root, ast_data)
    
    def _build_tree(self, parent, node, key=""):
        """Rekursiv den AST-Baum aufbauen"""
        if isinstance(node, dict):
            for k, v in node.items():
                # Wichtige Eigenschaften wie Typ und Name zuerst anzeigen
                if k in ['type', 'name', 'value', 'operator', 'kind']:
                    continue
                
                if k == 'body' and isinstance(v, list):
                    # Body-Knoten für Statements
                    body_node = self.tree.insert(parent, "end", text=f"{k} [{len(v)} items]", open=False)
                    for i, item in enumerate(v):
                        item_type = item.get('type', '') if isinstance(item, dict) else ''
                        item_node = self.tree.insert(body_node, "end", text=f"[{i}] {item_type}", open=False)
                        self._build_tree(item_node, item)
                elif isinstance(v, (dict, list)) and k not in ['loc', 'range', 'start', 'end']:
                    # Komplexe Objekte als Unterknoten darstellen
                    node_text = f"{k}"
                    if isinstance(v, dict) and 'type' in v:
                        node_text = f"{k} ({v['type']})"
                    child = self.tree.insert(parent, "end", text=node_text, open=False)
                    self._build_tree(child, v, k)
                elif k not in ['loc', 'range', 'start', 'end']:  # Positionsinfo überspringen
                    if k == 'type' or k == 'name' or k == 'value' or k == 'operator' or k == 'kind':
                        # Typ, Name und Wert direkt am Parent anzeigen
                        current_text = self.tree.item(parent, "text")
                        if k == 'type' and key != "":
                            pass  # Bereits im Parent-Text
                        elif k == 'value' and v is not None:
                            # Wert formatieren je nach Typ
                            if isinstance(v, str):
                                val_str = f'"{v}"'
                            else:
                                val_str = str(v)
                            self.tree.item(parent, text=f"{current_text}: {val_str}")
                        elif k == 'name' and v is not None:
                            self.tree.item(parent, text=f"{current_text} '{v}'")
                        elif k == 'operator' and v is not None:
                            self.tree.item(parent, text=f"{current_text} [{v}]")
                        elif k == 'kind' and v is not None:
                            self.tree.item(parent, text=f"{current_text} ({v})")
                    else:
                        # Andere Eigenschaften als Kinder
                        self.tree.insert(parent, "end", text=f"{k}: {v}")
        elif isinstance(node, list):
            for i, item in enumerate(node):
                if isinstance(item, (dict, list)):
                    item_text = f"[{i}]"
                    if isinstance(item, dict) and 'type' in item:
                        item_text = f"[{i}] {item['type']}"
                    child = self.tree.insert(parent, "end", text=item_text, open=False)
                    self._build_tree(child, item)
                else:
                    self.tree.insert(parent, "end", text=f"[{i}]: {item}")

    def insert_example_code(self):
        """Beispiel-JavaScript-Code im Editor einfügen"""
        example_code = """// JavaScript Beispiel-Code
function greet(name) {
    return "Hello, " + name + "!";
}

const add = (a, b) => a + b;

class Person {
    constructor(name, age) {
        this.name = name;
        this.age = age;
    }
    
    sayHello() {
        console.log(`Hi, I'm ${this.name} and I'm ${this.age} years old.`);
    }
}

const numbers = [1, 2, 3].map(n => n * 2);
"""
        self.js_editor.delete("1.0", tk.END)
        self.js_editor.insert("1.0", example_code)

    def clear_editor(self):
        """Editor und Anzeigen leeren"""
        self.js_editor.delete("1.0", tk.END)
        # Baum zurücksetzen
        for item in self.tree.get_children():
            self.tree.delete(item)
        # JSON-Ansicht zurücksetzen
        self.json_view.delete("1.0", tk.END)

    def open_file(self):
        """JavaScript-Datei öffnen"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JavaScript Files", "*.js"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    self.js_editor.delete("1.0", tk.END)
                    self.js_editor.insert("1.0", content)
                self.status_var.set(f"Datei geladen: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Konnte Datei nicht öffnen: {str(e)}")

    def save_ast(self):
        """AST als JSON-Datei speichern"""
        if not self.json_view.get("1.0", tk.END).strip():
            messagebox.showinfo("Info", "Es gibt keinen AST zum Speichern.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(self.json_view.get("1.0", tk.END))
                self.status_var.set(f"AST gespeichert: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Konnte AST nicht speichern: {str(e)}")

    def show_about(self):
        """Über-Dialog anzeigen"""
        messagebox.showinfo(
            "Über JavaScript AST Parser",
            "JavaScript AST Parser\n\n"
            "Ein Programm zum Parsen von JavaScript-Code und Anzeigen des abstrakten Syntaxbaums (AST).\n\n"
            f"Verwendet: {JS_PARSER or 'Kein Parser installiert'}"
        )
    
    def show_install_help(self):
        """Installationsanleitung für Abhängigkeiten anzeigen"""
        messagebox.showinfo(
            "Abhängigkeiten installieren",
            "Um den JavaScript AST Parser zu nutzen, benötigen Sie eine der folgenden Python-Bibliotheken:\n\n"
            "1. pyjsparser (empfohlen)\n"
            "   pip install pyjsparser\n\n"
            "2. esprima-python\n"
            "   pip install esprima-python\n\n"
            "Öffnen Sie die Kommandozeile/Terminal und führen Sie einen der obigen Befehle aus."
        )

if __name__ == "__main__":
    app = JSASTParser()
    app.mainloop()
