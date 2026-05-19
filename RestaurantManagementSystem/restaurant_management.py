"""
Restaurant Management System
Full CRUD · Dark/Light Theme · Mouse Hover Effects
Requirements:  pip install pyodbc
Run:           python restaurant_management.py
"""
import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc, sys
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# THEME
# ─────────────────────────────────────────────────────────────────────────────
DARK = dict(
    name="dark", bg="#0d0f1a", panel="#161929", card="#1e2235",
    card2="#252840", border="#2d3155", accent="#7c6ffc",
    accent_hov="#6557f5", accent2="#00d4aa", accent2_hov="#00b894",
    success="#2ecc71", success_hov="#27ae60", danger="#e74c3c",
    danger_hov="#c0392b", warning="#f39c12", text="#dde1f5",
    text_dim="#6c7099", text_head="#7c6ffc", sel="#2d3155",
    tree_sel="#7c6ffc", toggle="☀"
)
LIGHT = dict(
    name="light", bg="#f0f2fb", panel="#ffffff", card="#f7f8fd",
    card2="#eceffe", border="#d5d9f0", accent="#5b52e8",
    accent_hov="#4a42d6", accent2="#00b89b", accent2_hov="#009e85",
    success="#27ae60", success_hov="#219a52", danger="#e53935",
    danger_hov="#c62828", warning="#e67e22", text="#1a1d2e",
    text_dim="#656888", text_head="#5b52e8", sel="#eceffe",
    tree_sel="#5b52e8", toggle="🌙"
)

T = DARK.copy()

def apply_theme(src):
    T.clear(); T.update(src)


# ─────────────────────────────────────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────────────────────────────────────
class DB:
    def __init__(self):
        self.conn = self.cur = None

    def connect(self, server, db_name, auth, user="", pwd=""):
        try:
            cs = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={db_name};"
            cs += "Trusted_Connection=yes;" if auth == "Windows Authentication" \
                  else f"UID={user};PWD={pwd};"
            self.conn = pyodbc.connect(cs, autocommit=False)
            self.cur  = self.conn.cursor()
            return True, ""
        except Exception as e:
            return False, str(e)

    def run(self, sql, params=None):
        """Execute INSERT / UPDATE / DELETE. Returns (ok, error_msg)."""
        try:
            self.cur.execute(sql, params or [])
            self.conn.commit()
            return True, ""
        except Exception as e:
            try: self.conn.rollback()
            except: pass
            return False, str(e)

    def rows(self, sql, params=None):
        """Fetch all rows. Returns (list_of_rows, list_of_col_names)."""
        try:
            self.cur.execute(sql, params or [])
            data = self.cur.fetchall()
            cols = [d[0] for d in self.cur.description]
            return data, cols
        except:
            return [], []

    def one(self, sql, params=None):
        """Fetch single row or None."""
        try:
            self.cur.execute(sql, params or [])
            return self.cur.fetchone()
        except:
            return None

    def scalar(self, sql, params=None):
        """Fetch first column of first row."""
        r = self.one(sql, params)
        return r[0] if r else None

    def close(self):
        if self.conn:
            try: self.conn.close()
            except: pass

db = DB()


# ─────────────────────────────────────────────────────────────────────────────
# WIDGETS
# ─────────────────────────────────────────────────────────────────────────────
class Btn(tk.Label):
    """Clickable label with hover colour animation."""
    def __init__(self, parent, text, cmd=None, *, bg, hov, fg="#ffffff",
                 font=("Segoe UI", 9, "bold"), px=14, py=7, **kw):
        self._bg = bg; self._hov = hov; self._fg = fg; self._cmd = cmd
        super().__init__(parent, text=text, bg=bg, fg=fg, font=font,
                         padx=px, pady=py, cursor="hand2", relief="flat", **kw)
        self.bind("<Enter>",           lambda _: self.config(bg=hov))
        self.bind("<Leave>",           lambda _: self.config(bg=bg))
        self.bind("<ButtonRelease-1>", lambda _: cmd() if cmd else None)

    def update_theme(self, bg, hov):
        self._bg = bg; self._hov = hov
        self.config(bg=bg)


def _btn(parent, text, cmd, color, hov_color, px=12, py=6):
    return Btn(parent, text, cmd, bg=T[color], hov=T[hov_color], px=px, py=py)


def btn_primary(parent, text, cmd):
    return _btn(parent, text, cmd, "accent", "accent_hov")

def btn_success(parent, text, cmd):
    return _btn(parent, text, cmd, "success", "success_hov")

def btn_danger(parent, text, cmd):
    return _btn(parent, text, cmd, "danger", "danger_hov", px=10, py=6)

def btn_ghost(parent, text, cmd):
    return Btn(parent, text, cmd, bg=T["panel"], hov=T["sel"],
               fg=T["text_dim"], font=("Segoe UI", 9), px=10, py=6)

def btn_accent2(parent, text, cmd):
    return _btn(parent, text, cmd, "accent2", "accent2_hov")


class NavItem(tk.Frame):
    def __init__(self, parent, icon, label, cmd):
        super().__init__(parent, bg=T["panel"], cursor="hand2")
        self._cmd = cmd; self._on = False
        self.bar  = tk.Frame(self, bg=T["panel"], width=3); self.bar.pack(side="left")
        self.ico  = tk.Label(self, text=icon, bg=T["panel"], fg=T["text_dim"],
                              font=("Segoe UI Emoji", 11), width=3, padx=2)
        self.ico.pack(side="left", pady=8)
        self.lbl  = tk.Label(self, text=label, bg=T["panel"], fg=T["text_dim"],
                              font=("Segoe UI", 9), anchor="w")
        self.lbl.pack(side="left", fill="x", expand=True, padx=2)
        for w in (self, self.ico, self.lbl, self.bar):
            w.bind("<Enter>",          self._hover_on)
            w.bind("<Leave>",          self._hover_off)
            w.bind("<ButtonRelease-1>",self._click)

    def _hover_on(self, _=None):
        if not self._on:
            for w in (self, self.ico, self.lbl): w.config(bg=T["sel"])
            self.ico.config(fg=T["accent"])
            self.lbl.config(fg=T["text"])

    def _hover_off(self, _=None):
        if not self._on:
            for w in (self, self.ico, self.lbl): w.config(bg=T["panel"])
            self.ico.config(fg=T["text_dim"]); self.lbl.config(fg=T["text_dim"])

    def _click(self, _=None):
        if self._cmd: self._cmd()

    def activate(self, state):
        self._on = state
        if state:
            for w in (self, self.ico, self.lbl): w.config(bg=T["sel"])
            self.ico.config(fg=T["accent"])
            self.lbl.config(fg=T["text"], font=("Segoe UI", 9, "bold"))
            self.bar.config(bg=T["accent"])
        else:
            for w in (self, self.ico, self.lbl): w.config(bg=T["panel"])
            self.ico.config(fg=T["text_dim"])
            self.lbl.config(fg=T["text_dim"], font=("Segoe UI", 9))
            self.bar.config(bg=T["panel"])


def entry(parent, width=28, show=None):
    e = tk.Entry(parent, bg=T["card"], fg=T["text"], insertbackground=T["text"],
                 font=("Segoe UI", 10), width=width, relief="flat",
                 highlightthickness=1, highlightbackground=T["border"],
                 highlightcolor=T["accent"],
                 disabledbackground=T["card2"], disabledforeground=T["text_dim"])
    if show: e["show"] = show
    e.bind("<FocusIn>",  lambda _: e.config(highlightbackground=T["accent"]))
    e.bind("<FocusOut>", lambda _: e.config(highlightbackground=T["border"]))
    return e


def combo(parent, values, width=24):
    cb = ttk.Combobox(parent, values=values, width=width,
                      font=("Segoe UI", 10), state="readonly")
    return cb


def h_line(parent):
    return tk.Frame(parent, bg=T["border"], height=1)


def lbl(parent, text, size=9, bold=False, dim=False, color=None):
    fg = color or (T["text_dim"] if dim else T["text"])
    font = ("Segoe UI", size, "bold") if bold else ("Segoe UI", size)
    return tk.Label(parent, text=text, bg=parent["bg"], fg=fg, font=font)


# ─────────────────────────────────────────────────────────────────────────────
# TREEVIEW FACTORY
# ─────────────────────────────────────────────────────────────────────────────
def make_tree(parent, cols, widths=None):
    s = ttk.Style()
    s.configure("T.Treeview",
        background=T["card"], foreground=T["text"],
        fieldbackground=T["card"], rowheight=30,
        font=("Segoe UI", 9))
    s.configure("T.Treeview.Heading",
        background=T["card2"], foreground=T["text_head"],
        font=("Segoe UI", 9, "bold"), relief="flat")
    s.map("T.Treeview",
        background=[("selected", T["tree_sel"])],
        foreground=[("selected", "#ffffff")])
    s.map("T.Treeview.Heading",
        background=[("active", T["border"])])

    wrap = tk.Frame(parent, bg=T["bg"])
    wrap.pack(fill="both", expand=True, padx=8, pady=4)
    tree = ttk.Treeview(wrap, columns=cols, show="headings", style="T.Treeview")
    for i, c in enumerate(cols):
        w = (widths[i] if widths and i < len(widths) else 140)
        tree.heading(c, text=c.replace("_", " ").title())
        tree.column(c, width=w, anchor="w", minwidth=50)
    vsb = ttk.Scrollbar(wrap, orient="vertical",   command=tree.yview)
    hsb = ttk.Scrollbar(wrap, orient="horizontal",  command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    wrap.grid_rowconfigure(0, weight=1)
    wrap.grid_columnconfigure(0, weight=1)

    # Row hover
    tag = "hover"
    def _mv(e):
        iid = tree.identify_row(e.y)
        tree.tag_configure(tag, background=T["card2"])
        [tree.item(r, tags=()) for r in tree.get_children()]
        if iid and iid not in tree.selection():
            tree.item(iid, tags=(tag,))
    tree.bind("<Motion>", _mv)
    tree.bind("<Leave>",  lambda _: [tree.item(r, tags=()) for r in tree.get_children()])
    return tree


# ─────────────────────────────────────────────────────────────────────────────
# FORM DIALOG BASE  ← buttons are ALWAYS visible, never inside scroll area
# ─────────────────────────────────────────────────────────────────────────────
class FormDlg(tk.Toplevel):
    """
    ┌──────────────────────────────┐
    │ Title                  fixed │
    ├──────────────────────────────┤
    │ fields          scrollable   │
    ├──────────────────────────────┤
    │ error msg              fixed │
    │ [Save]  [Cancel]       fixed │  ← always on screen
    └──────────────────────────────┘
    """
    def __init__(self, parent, title, vals, tab, w=500, h=480):
        super().__init__(parent)
        self.title(title); self.vals = vals
        self.is_edit = vals is not None
        self.tab = tab; self._ents = {}
        self.configure(bg=T["bg"])
        self.geometry(f"{w}x{h}"); self.minsize(420, 320)
        self.resizable(True, True); self.grab_set()
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")
        self._build()

    def _build(self):
        # ── fixed title bar ────────────────────────────────────────────
        top = tk.Frame(self, bg=T["panel"], padx=18, pady=12)
        top.pack(fill="x")
        tk.Label(top, text=self.title(), bg=T["panel"], fg=T["text"],
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        h_line(self).pack(fill="x")

        # ── scrollable field area ──────────────────────────────────────
        mid = tk.Frame(self, bg=T["bg"]); mid.pack(fill="both", expand=True)
        cv  = tk.Canvas(mid, bg=T["bg"], highlightthickness=0)
        sb  = ttk.Scrollbar(mid, orient="vertical", command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y"); cv.pack(side="left", fill="both", expand=True)
        body = tk.Frame(cv, bg=T["bg"], padx=22, pady=14)
        wid  = cv.create_window((0, 0), window=body, anchor="nw")
        body.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>",  lambda e: cv.itemconfig(wid, width=cv.winfo_width()))
        cv.bind_all("<MouseWheel>",
                    lambda e: cv.yview_scroll(int(-e.delta / 120), "units"))

        fields = self.tab.form_fields()
        for idx, (label, ftype, opts) in enumerate(fields):
            raw = ""
            if self.is_edit and idx + 1 < len(self.vals):
                v = self.vals[idx + 1]
                raw = "" if v is None else str(v)

            row = tk.Frame(body, bg=T["bg"]); row.pack(fill="x", pady=5)
            tk.Label(row, text=label + ":", bg=T["bg"], fg=T["text_dim"],
                     font=("Segoe UI", 9), width=22, anchor="w").pack(side="left")

            if ftype == "entry":
                w = entry(row, width=28)
                if raw: w.insert(0, raw)
                w.pack(side="left", fill="x", expand=True)

            elif ftype == "combo":
                w = combo(row, opts.get("v", []), width=26)
                if raw and raw in opts.get("v", []): w.set(raw)
                elif opts.get("v"): w.set(opts["v"][0])
                w.pack(side="left")

            elif ftype == "text":
                w = tk.Text(row, height=3, width=28, bg=T["card"], fg=T["text"],
                            insertbackground=T["text"], font=("Segoe UI", 9),
                            relief="flat", highlightthickness=1,
                            highlightbackground=T["border"])
                if raw: w.insert("1.0", raw)
                w.pack(side="left", fill="x", expand=True)

            elif ftype == "check":
                var = tk.BooleanVar(value=(raw == "1" or raw.lower() == "true"))
                w = tk.Checkbutton(row, variable=var, bg=T["bg"], fg=T["text"],
                                   selectcolor=T["card"], activebackground=T["bg"],
                                   font=("Segoe UI", 9), text=opts.get("label", ""))
                w.var = var; w.pack(side="left")

            self._ents[label] = (w, ftype)

        # ── fixed bottom bar ───────────────────────────────────────────
        h_line(self).pack(fill="x")
        bot = tk.Frame(self, bg=T["panel"], padx=18, pady=10)
        bot.pack(fill="x")
        self.err = tk.Label(bot, text="", bg=T["panel"], fg=T["danger"],
                             font=("Segoe UI", 9), wraplength=450, anchor="w")
        self.err.pack(fill="x", pady=(0, 7))
        br = tk.Frame(bot, bg=T["panel"]); br.pack(anchor="w")
        btn_success(br,  "✓  Save",   self._save ).pack(side="left", padx=(0, 8))
        btn_ghost(br, "✕  Cancel", self.destroy).pack(side="left")

    def _val(self, label, ftype):
        w, _ = self._ents[label]
        if ftype == "entry": return w.get().strip() or None
        if ftype == "combo": return w.get() or None
        if ftype == "text":  return w.get("1.0", "end").strip() or None
        if ftype == "check": return 1 if w.var.get() else 0

    def _save(self):
        fields = self.tab.form_fields()
        vals   = [self._val(l, t) for l, t, _ in fields]
        # run required check
        reqs = [l for l, t, o in fields if o.get("required") and not self._val(l, t) and t != "check"]
        if reqs:
            self.err.config(text="Required: " + ", ".join(reqs)); return
        if self.is_edit:
            pk = self.vals[0]
            try: pk = int(pk)
            except: pass
            ok, msg = db.run(self.tab.sql_update(), vals + [pk])
        else:
            ok, msg = db.run(self.tab.sql_insert(), vals)
        if ok:
            self.tab.load(); self.destroy()
        else:
            self.err.config(text=f"✗  {msg}")


# ─────────────────────────────────────────────────────────────────────────────
# CRUD TAB BASE
# ─────────────────────────────────────────────────────────────────────────────
class CrudTab(tk.Frame):
    TITLE    = "Records"
    SUB      = ""
    SQL_LIST = ""
    COLS     = []
    WIDTHS   = None

    def __init__(self, parent):
        super().__init__(parent, bg=T["bg"])
        self._build(); self.load()

    def _build(self):
        self._header()
        self._action_bar()
        self.tree = make_tree(self, self.COLS, self.WIDTHS)
        self.tree.bind("<Double-1>", lambda _: self.do_edit())

    def _header(self):
        f = tk.Frame(self, bg=T["bg"]); f.pack(fill="x", padx=12, pady=(12, 4))
        tk.Label(f, text=self.TITLE, bg=T["bg"], fg=T["text"],
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        if self.SUB:
            tk.Label(f, text=f"  ·  {self.SUB}", bg=T["bg"], fg=T["text_dim"],
                     font=("Segoe UI", 9)).pack(side="left", pady=2)
        self.count_lbl = tk.Label(f, text="", bg=T["bg"], fg=T["text_dim"],
                                   font=("Segoe UI", 9))
        self.count_lbl.pack(side="right")
        h_line(self).pack(fill="x", padx=12, pady=(2, 5))

    def _action_bar(self):
        bar = tk.Frame(self, bg=T["panel"], pady=6)
        bar.pack(fill="x", padx=12, pady=(0, 4))
        btn_accent2(bar,  "⟳  Refresh",   self.load    ).pack(side="left", padx=2)
        btn_success(bar,  "+  Add New",    self.do_add  ).pack(side="left", padx=2)
        btn_primary(bar,  "✎  Edit",       self.do_edit ).pack(side="left", padx=2)
        btn_danger( bar,  "🗑  Delete",    self.do_delete).pack(side="left", padx=2)
        self.extra_btns(bar)

    def extra_btns(self, bar): pass

    def load(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        rows, _ = db.rows(self.SQL_LIST)
        for r in rows: self.tree.insert("", "end", values=list(r))
        self.count_lbl.config(text=f"{len(rows)} records")

    def _sel(self):
        s = self.tree.selection()
        if not s: return None, None
        v = self.tree.item(s[0])["values"]
        pk = v[0]
        try: pk = int(pk)
        except: pass
        return pk, v

    def do_add(self):
        self._form(None)

    def do_edit(self):
        pk, vals = self._sel()
        if pk is None:
            messagebox.showinfo("Nothing selected", "Please click on a row first."); return
        self._form(vals)

    def _form(self, vals):
        title = f"Edit {self.TITLE}" if vals else f"Add {self.TITLE}"
        FormDlg(self, title, vals, self)

    def do_delete(self):
        pk, vals = self._sel()
        if pk is None:
            messagebox.showinfo("Nothing selected", "Please click on a row first."); return
        name = vals[1] if len(vals) > 1 else f"ID {pk}"
        if not messagebox.askyesno("Confirm Delete",
            f"Delete  '{name}'?\n\nThis cannot be undone.", icon="warning"): return
        ok, msg = db.run(self.sql_delete(), [pk])
        if ok:   self.load()
        else:    messagebox.showerror("Delete failed", msg)

    # ── Subclass contract ────────────────────────────────────────────────────
    def form_fields(self): return []
    def sql_insert(self):  return ""
    def sql_update(self):  return ""
    def sql_delete(self):  return ""


# ─────────────────────────────────────────────────────────────────────────────
# CONNECTION DIALOG
# ─────────────────────────────────────────────────────────────────────────────
class ConnDlg(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Connect to SQL Server"); self.result = False
        self.configure(bg=T["bg"]); self.resizable(False, False); self.grab_set()
        self._build()
        self.update_idletasks()
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        self.geometry(f"+{(self.winfo_screenwidth()-w)//2}+{(self.winfo_screenheight()-h)//2}")

    def _build(self):
        outer = tk.Frame(self, bg=T["bg"], padx=30, pady=30); outer.pack()
        card  = tk.Frame(outer, bg=T["panel"], padx=38, pady=32,
                         highlightthickness=1, highlightbackground=T["border"])
        card.pack()

        # Logo row
        logo = tk.Frame(card, bg=T["panel"])
        logo.grid(row=0, column=0, columnspan=2, pady=(0, 8))
        tk.Label(logo, text="🍽", bg=T["panel"],
                 font=("Segoe UI Emoji", 30)).pack(side="left", padx=4)
        tf = tk.Frame(logo, bg=T["panel"]); tf.pack(side="left", padx=6)
        tk.Label(tf, text="Restaurant MS", bg=T["panel"], fg=T["text"],
                 font=("Segoe UI", 18, "bold")).pack(anchor="w")
        tk.Label(tf, text="Management System", bg=T["panel"], fg=T["text_dim"],
                 font=("Segoe UI", 9)).pack(anchor="w")

        tk.Frame(card, bg=T["border"], height=1).grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=(8, 18))

        def field(r, ltext, widget):
            tk.Label(card, text=ltext, bg=T["panel"], fg=T["text_dim"],
                     font=("Segoe UI", 9), width=18, anchor="w"
                     ).grid(row=r, column=0, sticky="w", pady=5)
            widget.grid(row=r, column=1, sticky="ew", pady=5, padx=(6, 0))
        card.columnconfigure(1, weight=1)

        self.e_srv = entry(card, 28); self.e_srv.insert(0, "localhost")
        field(2, "Server:", self.e_srv)
        self.e_db  = entry(card, 28); self.e_db.insert(0, "RestaurantDB")
        field(3, "Database:", self.e_db)
        self.cb_auth = combo(card, ["Windows Authentication","SQL Server Authentication"], 26)
        self.cb_auth.set("Windows Authentication")
        self.cb_auth.bind("<<ComboboxSelected>>", self._tog_auth)
        field(4, "Authentication:", self.cb_auth)
        self.e_usr = entry(card, 28); self.e_usr.config(state="disabled")
        field(5, "Username:", self.e_usr)
        self.e_pwd = entry(card, 28, show="*"); self.e_pwd.config(state="disabled")
        field(6, "Password:", self.e_pwd)

        self.msg = tk.Label(card, text="", bg=T["panel"], fg=T["danger"],
                             font=("Segoe UI", 9), wraplength=380)
        self.msg.grid(row=7, column=0, columnspan=2, pady=(12, 4))

        wrap = tk.Frame(card, bg=T["panel"])
        wrap.grid(row=8, column=0, columnspan=2, sticky="ew")
        Btn(wrap, "  Connect  →", self._connect,
            bg=T["accent"], hov=T["accent_hov"],
            font=("Segoe UI", 10, "bold"), px=0, py=11).pack(fill="x")

    def _tog_auth(self, _=None):
        s = "normal" if self.cb_auth.get() == "SQL Server Authentication" else "disabled"
        self.e_usr.config(state=s); self.e_pwd.config(state=s)

    def _connect(self):
        srv = self.e_srv.get().strip(); dbn = self.e_db.get().strip()
        if not srv or not dbn:
            self.msg.config(text="Server and Database are required.", fg=T["danger"]); return
        self.msg.config(text="Connecting…", fg=T["warning"]); self.update()
        ok, err = db.connect(srv, dbn, self.cb_auth.get(),
                             self.e_usr.get().strip(), self.e_pwd.get().strip())
        if ok:
            self.msg.config(text="✓  Connected!", fg=T["success"])
            self.result = True; self.after(600, self.destroy)
        else:
            self.msg.config(text=f"✗  {err}", fg=T["danger"])


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
class StatCard(tk.Frame):
    def __init__(self, parent, title, q, color, icon):
        super().__init__(parent, bg=T["card"], padx=14, pady=12, cursor="hand2",
                         highlightthickness=1, highlightbackground=T["border"])
        self._q = q; self._c = color
        tk.Label(self, text=icon, bg=T["card"], font=("Segoe UI Emoji", 15)).pack(anchor="w")
        self._v = tk.Label(self, text="—", bg=T["card"], fg=color,
                            font=("Segoe UI", 24, "bold"))
        self._v.pack(anchor="w")
        tk.Label(self, text=title, bg=T["card"], fg=T["text_dim"],
                 font=("Segoe UI", 9)).pack(anchor="w")
        for w in list(self.winfo_children()) + [self]:
            w.bind("<Enter>", lambda _, s=self: s.config(highlightbackground=s._c))
            w.bind("<Leave>", lambda _, s=self: s.config(highlightbackground=T["border"]))

    def refresh(self):
        r = db.scalar(self._q)
        self._v.config(text=str(r) if r is not None else "—")


class DashboardTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=T["bg"])
        self._cards = []; self._tree = None; self._build()

    def _build(self):
        f = tk.Frame(self, bg=T["bg"]); f.pack(fill="x", padx=12, pady=(12, 4))
        tk.Label(f, text="Dashboard", bg=T["bg"], fg=T["text"],
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        tk.Label(f, text="  ·  Live overview", bg=T["bg"], fg=T["text_dim"],
                 font=("Segoe UI", 9)).pack(side="left")
        btn_accent2(f, "⟳  Refresh", self._load).pack(side="right")
        h_line(self).pack(fill="x", padx=12, pady=(2, 8))

        row = tk.Frame(self, bg=T["bg"]); row.pack(fill="x", padx=12, pady=(0, 10))
        cards_cfg = [
            ("Customers",    "SELECT COUNT(*) FROM Customers",                             T["accent"],  "👥"),
            ("Active Staff", "SELECT COUNT(*) FROM Employees WHERE is_active=1",           T["accent2"], "👤"),
            ("Menu Items",   "SELECT COUNT(*) FROM MenuItems WHERE is_available=1",        T["warning"], "🍔"),
            ("Today Orders", "SELECT COUNT(*) FROM Orders WHERE CAST(order_date AS DATE)=CAST(GETDATE() AS DATE)", T["success"], "📋"),
            ("Free Tables",  "SELECT COUNT(*) FROM Tables WHERE status='available'",       "#5cb8f7",    "🪑"),
            ("Low Stock",    "SELECT COUNT(*) FROM Ingredients WHERE stock_quantity<=reorder_level", T["danger"], "⚠"),
        ]
        for t, q, c, i in cards_cfg:
            card = StatCard(row, t, q, c, i)
            card.pack(side="left", fill="both", expand=True, padx=3)
            self._cards.append(card)

        # Recent orders label
        rh = tk.Frame(self, bg=T["bg"]); rh.pack(fill="x", padx=12, pady=(0, 4))
        tk.Label(rh, text="Recent Orders", bg=T["bg"], fg=T["text"],
                 font=("Segoe UI", 11, "bold")).pack(side="left")
        self._load()

    def _load(self):
        for c in self._cards: c.refresh()
        if self._tree is None:
            self._tree = make_tree(self,
                ["order_id", "customer", "type", "status", "total", "date"],
                [70, 200, 100, 110, 90, 160])
        for r in self._tree.get_children(): self._tree.delete(r)
        rows, _ = db.rows(
            "SELECT TOP 30 o.order_id, c.first_name+' '+c.last_name,"
            "o.order_type, o.status, o.total_price, o.order_date"
            " FROM Orders o JOIN Customers c ON c.customer_id=o.customer_id"
            " ORDER BY o.order_date DESC")
        for r in rows: self._tree.insert("", "end", values=list(r))


# ─────────────────────────────────────────────────────────────────────────────
# CUSTOMERS
# ─────────────────────────────────────────────────────────────────────────────
class CustomersTab(CrudTab):
    TITLE = "Customers"; SUB = "Manage customer records"
    COLS  = ["ID", "First Name", "Last Name", "Email", "Street", "City", "Postal"]
    WIDTHS = [60, 130, 130, 200, 160, 120, 90]
    SQL_LIST = ("SELECT customer_id,first_name,last_name,email,"
                "address_street,address_city,address_postal "
                "FROM Customers ORDER BY last_name,first_name")

    def form_fields(self):
        return [
            ("First Name", "entry", {"required": True}),
            ("Last Name",  "entry", {"required": True}),
            ("Email",      "entry", {}),
            ("Street",     "entry", {}),
            ("City",       "entry", {}),
            ("Postal Code","entry", {}),
        ]
    def sql_insert(self):
        return ("INSERT INTO Customers(first_name,last_name,email,"
                "address_street,address_city,address_postal) VALUES(?,?,?,?,?,?)")
    def sql_update(self):
        return ("UPDATE Customers SET first_name=?,last_name=?,email=?,"
                "address_street=?,address_city=?,address_postal=? WHERE customer_id=?")
    def sql_delete(self): return "DELETE FROM Customers WHERE customer_id=?"


# ─────────────────────────────────────────────────────────────────────────────
# DEPARTMENTS
# ─────────────────────────────────────────────────────────────────────────────
class DepartmentsTab(CrudTab):
    TITLE = "Departments"; SUB = "Organisational units"
    COLS  = ["ID", "Name", "Description"]
    SQL_LIST = "SELECT department_id,name,description FROM Departments ORDER BY name"

    def form_fields(self):
        return [("Name","entry",{"required":True}), ("Description","text",{})]
    def sql_insert(self): return "INSERT INTO Departments(name,description) VALUES(?,?)"
    def sql_update(self): return "UPDATE Departments SET name=?,description=? WHERE department_id=?"
    def sql_delete(self): return "DELETE FROM Departments WHERE department_id=?"

    def do_delete(self):
        pk, vals = self._sel()
        if pk is None:
            messagebox.showinfo("Nothing selected", "Please click on a row first."); return
        # Check if any employees belong to this department
        count = db.scalar("SELECT COUNT(*) FROM Employees WHERE department_id=?", [pk])
        if count and count > 0:
            messagebox.showerror("Cannot Delete",
                f"Department '{vals[1]}' has {count} employee(s) assigned to it.\n"
                "Reassign or delete those employees first."); return
        if not messagebox.askyesno("Confirm Delete",
            f"Delete department '{vals[1]}'?\nThis cannot be undone.", icon="warning"): return
        ok, msg = db.run(self.sql_delete(), [pk])
        if ok:   self.load()
        else:    messagebox.showerror("Delete failed", msg)


# ─────────────────────────────────────────────────────────────────────────────
# ROLES
# ─────────────────────────────────────────────────────────────────────────────
class RolesTab(CrudTab):
    TITLE = "Roles"; SUB = "Employee role definitions"
    COLS  = ["ID", "Role Name", "Description"]
    SQL_LIST = "SELECT role_id,role_name,description FROM Roles ORDER BY role_name"

    def form_fields(self):
        return [("Role Name","entry",{"required":True}), ("Description","text",{})]
    def sql_insert(self): return "INSERT INTO Roles(role_name,description) VALUES(?,?)"
    def sql_update(self): return "UPDATE Roles SET role_name=?,description=? WHERE role_id=?"
    def sql_delete(self): return "DELETE FROM Roles WHERE role_id=?"


# ─────────────────────────────────────────────────────────────────────────────
# MENU CATEGORIES
# ─────────────────────────────────────────────────────────────────────────────
class MenuCatTab(CrudTab):
    TITLE = "Menu Categories"; SUB = "Manage menu sections"
    COLS  = ["ID", "Name", "Description", "Order", "Active"]
    SQL_LIST = ("SELECT category_id,name,description,display_order,is_active "
                "FROM MenuCategories ORDER BY display_order")

    def form_fields(self):
        return [
            ("Name",          "entry", {"required": True}),
            ("Description",   "text",  {}),
            ("Display Order", "entry", {}),
            ("Active",        "check", {"label": "Visible on menu"}),
        ]
    def sql_insert(self):
        return "INSERT INTO MenuCategories(name,description,display_order,is_active) VALUES(?,?,?,?)"
    def sql_update(self):
        return ("UPDATE MenuCategories SET name=?,description=?,display_order=?,is_active=?"
                " WHERE category_id=?")
    def sql_delete(self): return "DELETE FROM MenuCategories WHERE category_id=?"


# ─────────────────────────────────────────────────────────────────────────────
# MENU ITEMS  — custom dialog (needs category dropdown)
# ─────────────────────────────────────────────────────────────────────────────
class MenuItemsTab(CrudTab):
    TITLE = "Menu Items"; SUB = "Full menu with pricing"
    COLS  = ["ID", "Name", "Category", "Price", "Prep (min)", "Available"]
    WIDTHS = [60, 200, 140, 80, 90, 80]
    SQL_LIST = ("SELECT mi.item_id,mi.name,mc.name,mi.price,"
                "mi.preparation_time_min,mi.is_available "
                "FROM MenuItems mi "
                "JOIN MenuCategories mc ON mc.category_id=mi.category_id "
                "ORDER BY mc.display_order,mi.name")

    def _form(self, vals): _MenuItemDlg(self, vals)
    def sql_delete(self): return "DELETE FROM MenuItems WHERE item_id=?"


class _MenuItemDlg(tk.Toplevel):
    def __init__(self, tab, vals):
        super().__init__(tab)
        self.tab = tab; self.vals = vals; self.is_edit = vals is not None
        self.title("Edit Menu Item" if self.is_edit else "Add Menu Item")
        self.configure(bg=T["bg"]); self.geometry("520x470")
        self.resizable(True, True); self.grab_set()
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 520) // 2
        y = (self.winfo_screenheight() - 470) // 2
        self.geometry(f"+{x}+{y}")
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=T["panel"], padx=18, pady=12); top.pack(fill="x")
        tk.Label(top, text=self.title(), bg=T["panel"], fg=T["text"],
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        h_line(self).pack(fill="x")

        body = tk.Frame(self, bg=T["bg"], padx=22, pady=14)
        body.pack(fill="both", expand=True)

        cat_rows, _ = db.rows(
            "SELECT category_id,name FROM MenuCategories WHERE is_active=1 ORDER BY display_order")
        self.cat_map = {name: cid for cid, name in cat_rows}
        cat_names = list(self.cat_map.keys())

        # ── helper: creates label+widget in same row frame ────────────
        def mk(lbl_text):
            f = tk.Frame(body, bg=T["bg"]); f.pack(fill="x", pady=5)
            tk.Label(f, text=lbl_text+":", bg=T["bg"], fg=T["text_dim"],
                     font=("Segoe UI", 9), width=20, anchor="w").pack(side="left")
            return f

        f = mk("Category *")
        self.cb_cat = ttk.Combobox(f, values=cat_names, width=28,
                                    font=("Segoe UI",10), state="readonly")
        self.cb_cat.pack(side="left")

        f = mk("Name *")
        self.e_name = tk.Entry(f, bg=T["card"], fg=T["text"], insertbackground=T["text"],
                                font=("Segoe UI",10), width=30, relief="flat",
                                highlightthickness=1, highlightbackground=T["border"])
        self.e_name.pack(side="left", fill="x", expand=True)

        f = mk("Description")
        self.e_desc = tk.Text(f, height=3, width=30, bg=T["card"], fg=T["text"],
                               insertbackground=T["text"], font=("Segoe UI",9),
                               relief="flat", highlightthickness=1,
                               highlightbackground=T["border"])
        self.e_desc.pack(side="left", fill="x", expand=True)

        f = mk("Price * ($)")
        self.e_price = tk.Entry(f, bg=T["card"], fg=T["text"], insertbackground=T["text"],
                                 font=("Segoe UI",10), width=14, relief="flat",
                                 highlightthickness=1, highlightbackground=T["border"])
        self.e_price.pack(side="left")

        f = mk("Prep Time (min)")
        self.e_prep = tk.Entry(f, bg=T["card"], fg=T["text"], insertbackground=T["text"],
                                font=("Segoe UI",10), width=10, relief="flat",
                                highlightthickness=1, highlightbackground=T["border"])
        self.e_prep.pack(side="left")

        self.avl = tk.BooleanVar(value=True)
        tk.Checkbutton(body, text="Available on menu", variable=self.avl,
                       bg=T["bg"], fg=T["text"], selectcolor=T["card"],
                       activebackground=T["bg"], font=("Segoe UI", 9)
                       ).pack(anchor="w", pady=5)

        # Pre-fill for edit: [item_id, name, category_name, price, prep_min, is_available]
        if self.is_edit:
            v = self.vals
            if str(v[2]) in self.cat_map: self.cb_cat.set(str(v[2]))
            self.e_name.insert(0, str(v[1]))
            self.e_price.insert(0, str(v[3]))
            if v[4] is not None: self.e_prep.insert(0, str(v[4]))
            self.avl.set(bool(int(v[5])) if str(v[5]).isdigit() else bool(v[5]))

        # Fixed bottom
        h_line(self).pack(fill="x")
        bot = tk.Frame(self, bg=T["panel"], padx=18, pady=10); bot.pack(fill="x")
        self.err_lbl = tk.Label(bot, text="", bg=T["panel"], fg=T["danger"],
                                 font=("Segoe UI", 9)); self.err_lbl.pack(anchor="w", pady=(0, 6))
        br = tk.Frame(bot, bg=T["panel"]); br.pack(anchor="w")
        btn_success(br, "✓  Save Item",  self._save  ).pack(side="left", padx=(0, 8))
        btn_ghost(br,   "✕  Cancel",     self.destroy).pack(side="left")

    def _save(self):
        cat_name = self.cb_cat.get()
        cat_id   = self.cat_map.get(cat_name)
        name     = self.e_name.get().strip()
        price    = self.e_price.get().strip()
        if not cat_id:
            self.err_lbl.config(text="✗  Please select a category."); return
        if not name:
            self.err_lbl.config(text="✗  Name is required."); return
        if not price:
            self.err_lbl.config(text="✗  Price is required."); return
        try:    float(price)
        except: self.err_lbl.config(text="✗  Price must be a number."); return
        prep  = self.e_prep.get().strip() or None
        desc  = self.e_desc.get("1.0", "end").strip() or None
        avail = 1 if self.avl.get() else 0
        if self.is_edit:
            pk = self.vals[0]
            try: pk = int(pk)
            except: pass
            ok, msg = db.run(
                "UPDATE MenuItems SET category_id=?,name=?,description=?,"
                "price=?,preparation_time_min=?,is_available=? WHERE item_id=?",
                [cat_id, name, desc, price, prep, avail, pk])
        else:
            ok, msg = db.run(
                "INSERT INTO MenuItems(category_id,name,description,price,"
                "preparation_time_min,is_available) VALUES(?,?,?,?,?,?)",
                [cat_id, name, desc, price, prep, avail])
        if ok:  self.tab.load(); self.destroy()
        else:   self.err_lbl.config(text=f"✗  {msg}")


# ─────────────────────────────────────────────────────────────────────────────
# EMPLOYEES  — custom dialog (needs dept/role dropdowns + extra fields)
# ─────────────────────────────────────────────────────────────────────────────
class EmployeesTab(CrudTab):
    TITLE = "Employees"; SUB = "Staff management"
    COLS  = ["ID", "First Name", "Last Name", "Email", "Department", "Role", "Salary", "Active"]
    WIDTHS = [60, 120, 120, 190, 140, 130, 90, 60]
    SQL_LIST = ("SELECT e.employee_id,e.first_name,e.last_name,e.email,"
                "d.name,r.role_name,e.salary,e.is_active "
                "FROM Employees e "
                "JOIN Departments d ON d.department_id=e.department_id "
                "JOIN Roles r ON r.role_id=e.role_id "
                "ORDER BY e.last_name,e.first_name")

    def _form(self, vals): _EmpDlg(self, vals)
    def sql_delete(self): return "DELETE FROM Employees WHERE employee_id=?"

    def do_delete(self):
        pk, vals = self._sel()
        if pk is None:
            messagebox.showinfo("Nothing selected", "Please click on a row first."); return
        name = f"{vals[1]} {vals[2]}"
        if not messagebox.askyesno("Confirm Delete",
            f"Delete employee '{name}'?\nThis cannot be undone.", icon="warning"): return
        # Nullify self-referencing FK (manager relationship) before delete
        db.run("UPDATE Employees SET reports_to_employee_id=NULL WHERE reports_to_employee_id=?", [pk])
        ok, msg = db.run(self.sql_delete(), [pk])
        if ok:   self.load()
        else:    messagebox.showerror("Delete failed", msg)


class _EmpDlg(tk.Toplevel):
    """Employee form — scrollable fields, fixed Save/Cancel always visible."""
    def __init__(self, tab, vals):
        super().__init__(tab)
        self.tab = tab; self.vals = vals; self.is_edit = vals is not None
        self.title("Edit Employee" if self.is_edit else "Add Employee")
        self.configure(bg=T["bg"]); self.geometry("530x600")
        self.resizable(True, True); self.grab_set()
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 530) // 2
        y = (self.winfo_screenheight() - 600) // 2
        self.geometry(f"+{x}+{y}")
        self._build()

    def _build(self):
        # Fixed title
        top = tk.Frame(self, bg=T["panel"], padx=18, pady=12); top.pack(fill="x")
        tk.Label(top, text=self.title(), bg=T["panel"], fg=T["text"],
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        h_line(self).pack(fill="x")

        # Scrollable fields
        mid = tk.Frame(self, bg=T["bg"]); mid.pack(fill="both", expand=True)
        cv  = tk.Canvas(mid, bg=T["bg"], highlightthickness=0)
        sb  = ttk.Scrollbar(mid, orient="vertical", command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y"); cv.pack(side="left", fill="both", expand=True)
        body = tk.Frame(cv, bg=T["bg"], padx=22, pady=14)
        wid  = cv.create_window((0, 0), window=body, anchor="nw")
        body.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>",  lambda e: cv.itemconfig(wid, width=cv.winfo_width()))
        cv.bind_all("<MouseWheel>",
                    lambda e: cv.yview_scroll(int(-e.delta / 120), "units"))

        # Load lookup data
        dept_r, _ = db.rows("SELECT department_id,name FROM Departments ORDER BY name")
        role_r, _ = db.rows("SELECT role_id,role_name FROM Roles ORDER BY role_name")
        self.dept_m = {n: d for d, n in dept_r}
        self.role_m = {n: r for r, n in role_r}

        # ── helper: returns a row-frame with label already packed ─────
        def mk(label_text):
            f = tk.Frame(body, bg=T["bg"]); f.pack(fill="x", pady=4)
            tk.Label(f, text=label_text, bg=T["bg"], fg=T["text_dim"],
                     font=("Segoe UI", 9), width=28, anchor="w").pack(side="left")
            return f

        def ent(f, w=26):
            e = tk.Entry(f, bg=T["card"], fg=T["text"], insertbackground=T["text"],
                         font=("Segoe UI", 10), width=w, relief="flat",
                         highlightthickness=1, highlightbackground=T["border"])
            return e

        def cmb(f, vals, w=26):
            c = ttk.Combobox(f, values=vals, width=w, font=("Segoe UI", 10), state="readonly")
            return c

        f = mk("First Name *:");  self.e_fn  = ent(f, 28); self.e_fn.pack(side="left", fill="x", expand=True)
        f = mk("Last Name *:");   self.e_ln  = ent(f, 28); self.e_ln.pack(side="left", fill="x", expand=True)
        f = mk("Email *:");       self.e_em  = ent(f, 28); self.e_em.pack(side="left", fill="x", expand=True)
        f = mk("Department *:");  self.cb_d  = cmb(f, list(self.dept_m), 28); self.cb_d.pack(side="left")
        f = mk("Role *:");        self.cb_r  = cmb(f, list(self.role_m), 28); self.cb_r.pack(side="left")
        f = mk("Phone:");         self.e_ph  = ent(f, 22); self.e_ph.pack(side="left")
        f = mk("Address Street:"); self.e_st = ent(f, 28); self.e_st.pack(side="left", fill="x", expand=True)
        f = mk("City:");          self.e_ct  = ent(f, 22); self.e_ct.pack(side="left")
        f = mk("Salary *:");      self.e_sal = ent(f, 14); self.e_sal.pack(side="left")
        f = mk("Date of Birth * (YYYY-MM-DD):"); self.e_dob = ent(f, 14); self.e_dob.pack(side="left")
        f = mk("Hire Date * (YYYY-MM-DD):");    self.e_hd  = ent(f, 14); self.e_hd.pack(side="left")
        self.act = tk.BooleanVar(value=True)
        tk.Checkbutton(body, text="Active employee", variable=self.act,
                       bg=T["bg"], fg=T["text"], selectcolor=T["card"],
                       activebackground=T["bg"], font=("Segoe UI", 9)
                       ).pack(anchor="w", pady=5)

        # Pre-fill: [id, first, last, email, dept_name, role_name, salary, is_active]
        if self.is_edit:
            v = self.vals
            for wgt, val in [(self.e_fn,  v[1]), (self.e_ln, v[2]),
                              (self.e_em, v[3]), (self.e_sal, v[6])]:
                if val is not None: wgt.insert(0, str(val))
            if v[4] and str(v[4]) in self.dept_m: self.cb_d.set(str(v[4]))
            if v[5] and str(v[5]) in self.role_m: self.cb_r.set(str(v[5]))
            self.act.set(bool(int(v[7])) if str(v[7]).isdigit() else bool(v[7]))
            # Fetch extra fields from DB for this employee
            full = db.one(
                "SELECT phone,address_street,address_city,date_of_birth,hire_date"
                " FROM Employees WHERE employee_id=?", [v[0]])
            if full:
                for wgt, val in [(self.e_ph, full[0]), (self.e_st, full[1]),
                                  (self.e_ct, full[2]), (self.e_dob, full[3]),
                                  (self.e_hd, full[4])]:
                    if val is not None: wgt.insert(0, str(val).split(" ")[0])

        # Fixed bottom
        h_line(self).pack(fill="x")
        bot = tk.Frame(self, bg=T["panel"], padx=18, pady=10); bot.pack(fill="x")
        self.err_lbl = tk.Label(bot, text="", bg=T["panel"], fg=T["danger"],
                                 font=("Segoe UI", 9)); self.err_lbl.pack(anchor="w", pady=(0, 6))
        br = tk.Frame(bot, bg=T["panel"]); br.pack(anchor="w")
        btn_success(br, "✓  Save Employee", self._save  ).pack(side="left", padx=(0, 8))
        btn_ghost(br,   "✕  Cancel",        self.destroy).pack(side="left")

    def _save(self):
        fn   = self.e_fn.get().strip();   ln  = self.e_ln.get().strip()
        em   = self.e_em.get().strip();   sal = self.e_sal.get().strip()
        dob  = self.e_dob.get().strip();  hd  = self.e_hd.get().strip()
        dept = self.dept_m.get(self.cb_d.get())
        role = self.role_m.get(self.cb_r.get())
        errs = []
        if not fn:   errs.append("First Name")
        if not ln:   errs.append("Last Name")
        if not em:   errs.append("Email")
        if not sal:  errs.append("Salary")
        if not dob:  errs.append("Date of Birth")
        if not hd:   errs.append("Hire Date")
        if not dept: errs.append("Department")
        if not role: errs.append("Role")
        if errs:
            self.err_lbl.config(text="Required: " + ", ".join(errs)); return
        try: float(sal)
        except: self.err_lbl.config(text="✗  Salary must be a number."); return

        ph   = self.e_ph.get().strip() or None
        st   = self.e_st.get().strip() or None
        ct   = self.e_ct.get().strip() or None
        act  = 1 if self.act.get() else 0
        params = [dept, role, fn, ln, em, ph, st, ct, dob, hd, sal, act]

        if self.is_edit:
            pk = self.vals[0]
            try: pk = int(pk)
            except: pass
            ok, msg = db.run(
                "UPDATE Employees SET department_id=?,role_id=?,first_name=?,last_name=?,"
                "email=?,phone=?,address_street=?,address_city=?,"
                "date_of_birth=?,hire_date=?,salary=?,is_active=? WHERE employee_id=?",
                params + [pk])
        else:
            ok, msg = db.run(
                "INSERT INTO Employees(department_id,role_id,first_name,last_name,email,"
                "phone,address_street,address_city,date_of_birth,hire_date,salary,is_active)"
                " VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", params)

        if ok:  self.tab.load(); self.destroy()
        else:   self.err_lbl.config(text=f"✗  {msg}")


# ─────────────────────────────────────────────────────────────────────────────
# TABLES
# ─────────────────────────────────────────────────────────────────────────────
class TablesTab(CrudTab):
    TITLE = "Restaurant Tables"; SUB = "Seating layout"
    COLS  = ["ID", "Number", "Capacity", "Location", "Status"]
    WIDTHS = [60, 90, 90, 130, 110]
    SQL_LIST = ("SELECT table_id,table_number,capacity,location,status"
                " FROM Tables ORDER BY table_number")

    def form_fields(self):
        return [
            ("Table Number","entry", {"required": True}),
            ("Capacity",    "entry", {"required": True}),
            ("Location","combo",{"v":["indoor","outdoor","private room"],"required":True}),
            ("Status","combo",{"v":["available","occupied","reserved","maintenance"],"required":True}),
        ]
    def sql_insert(self):
        return "INSERT INTO Tables(table_number,capacity,location,status) VALUES(?,?,?,?)"
    def sql_update(self):
        return "UPDATE Tables SET table_number=?,capacity=?,location=?,status=? WHERE table_id=?"
    def sql_delete(self): return "DELETE FROM Tables WHERE table_id=?"


# ─────────────────────────────────────────────────────────────────────────────
# SUPPLIERS
# ─────────────────────────────────────────────────────────────────────────────
class SuppliersTab(CrudTab):
    TITLE = "Suppliers"; SUB = "Ingredient vendors"
    COLS  = ["ID", "Name", "Contact", "Email", "Phone", "Address", "Active"]
    WIDTHS = [60, 150, 130, 180, 120, 160, 60]
    SQL_LIST = ("SELECT supplier_id,name,contact_name,email,phone,address,is_active"
                " FROM Suppliers ORDER BY name")

    def form_fields(self):
        return [
            ("Name",         "entry", {"required": True}),
            ("Contact Name", "entry", {}),
            ("Email",        "entry", {}),
            ("Phone",        "entry", {}),
            ("Address",      "entry", {}),
            ("Active",       "check", {"label": "Active supplier"}),
        ]
    def sql_insert(self):
        return "INSERT INTO Suppliers(name,contact_name,email,phone,address,is_active) VALUES(?,?,?,?,?,?)"
    def sql_update(self):
        return ("UPDATE Suppliers SET name=?,contact_name=?,email=?,phone=?,address=?,is_active=?"
                " WHERE supplier_id=?")
    def sql_delete(self): return "DELETE FROM Suppliers WHERE supplier_id=?"


# ─────────────────────────────────────────────────────────────────────────────
# ORDERS
# ─────────────────────────────────────────────────────────────────────────────
class OrdersTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=T["bg"]); self._build(); self.load()

    def _build(self):
        # Header
        f = tk.Frame(self, bg=T["bg"]); f.pack(fill="x", padx=12, pady=(12, 4))
        tk.Label(f, text="Orders", bg=T["bg"], fg=T["text"],
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        tk.Label(f, text="  ·  Track and manage orders", bg=T["bg"],
                 fg=T["text_dim"], font=("Segoe UI", 9)).pack(side="left")
        self.cnt = tk.Label(f, text="", bg=T["bg"], fg=T["text_dim"],
                             font=("Segoe UI", 9)); self.cnt.pack(side="right")
        h_line(self).pack(fill="x", padx=12, pady=(2, 5))

        # Action bar
        bar = tk.Frame(self, bg=T["panel"], pady=6)
        bar.pack(fill="x", padx=12, pady=(0, 4))
        btn_accent2(bar, "⟳  Refresh",        self.load           ).pack(side="left", padx=2)
        btn_success(bar, "+  New Order",        self.do_new         ).pack(side="left", padx=2)
        btn_primary(bar, "↕  Update Status",   self.do_status      ).pack(side="left", padx=2)
        btn_ghost(bar,   "≡  View Items",       self.do_view_items  ).pack(side="left", padx=2)
        btn_danger(bar,  "🗑  Delete",          self.do_delete      ).pack(side="left", padx=2)
        # Filter
        fi = tk.Frame(bar, bg=T["panel"]); fi.pack(side="right", padx=6)
        tk.Label(fi, text="Status:", bg=T["panel"], fg=T["text_dim"],
                 font=("Segoe UI", 9)).pack(side="left", padx=4)
        self.cb_f = combo(fi, ["All","pending","confirmed",
                               "preparing","ready","delivered","cancelled"], 14)
        self.cb_f.set("All")
        self.cb_f.bind("<<ComboboxSelected>>", lambda _: self.load())
        self.cb_f.pack(side="left")

        self.tree = make_tree(self,
            ["order_id","customer","employee","table","type","status","total","date"],
            [70, 180, 150, 70, 90, 100, 80, 155])
        self.tree.bind("<Double-1>", lambda _: self.do_view_items())

    def load(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        st = self.cb_f.get()
        base = ("SELECT o.order_id, c.first_name+' '+c.last_name,"
                "ISNULL(e.first_name+' '+e.last_name,'—'),"
                "ISNULL(CAST(t.table_number AS NVARCHAR),'—'),"
                "o.order_type, o.status, o.total_price, o.order_date"
                " FROM Orders o"
                " JOIN Customers c ON c.customer_id=o.customer_id"
                " LEFT JOIN Employees e ON e.employee_id=o.employee_id"
                " LEFT JOIN Tables t ON t.table_id=o.table_id")
        if st == "All":
            rows, _ = db.rows(base + " ORDER BY o.order_date DESC")
        else:
            rows, _ = db.rows(base + " WHERE o.status=? ORDER BY o.order_date DESC", [st])
        for r in rows: self.tree.insert("", "end", values=list(r))
        self.cnt.config(text=f"{len(rows)} records")

    def _sel(self):
        s = self.tree.selection()
        if not s:
            messagebox.showinfo("Nothing selected", "Please click on an order first.")
            return None
        pk = self.tree.item(s[0])["values"][0]
        try: pk = int(pk)
        except: pass
        return pk

    def do_status(self):
        oid = self._sel()
        if oid is None: return
        self._mini_dlg(f"Update Status — Order #{oid}",
                       ["pending","confirmed","preparing","ready","delivered","cancelled"],
                       lambda v: db.run("UPDATE Orders SET status=? WHERE order_id=?", [v, oid]))

    def _mini_dlg(self, title, choices, action):
        d = tk.Toplevel(self); d.title(title)
        d.configure(bg=T["bg"]); d.geometry("360x220"); d.grab_set()
        d.update_idletasks()
        x = (d.winfo_screenwidth()  - 360) // 2
        y = (d.winfo_screenheight() - 220) // 2
        d.geometry(f"+{x}+{y}")

        top = tk.Frame(d, bg=T["panel"], padx=18, pady=12); top.pack(fill="x")
        tk.Label(top, text=title, bg=T["panel"], fg=T["text"],
                 font=("Segoe UI", 11, "bold")).pack(side="left")
        h_line(d).pack(fill="x")
        body = tk.Frame(d, bg=T["bg"], padx=22, pady=16); body.pack(fill="both", expand=True)
        tk.Label(body, text="Select new value:", bg=T["bg"], fg=T["text_dim"],
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 6))
        cb = combo(body, choices, 28); cb.pack(anchor="w")
        h_line(d).pack(fill="x")
        bot = tk.Frame(d, bg=T["panel"], padx=18, pady=10); bot.pack(fill="x")
        err = tk.Label(bot, text="", bg=T["panel"], fg=T["danger"],
                        font=("Segoe UI", 9)); err.pack(anchor="w", pady=(0, 6))
        br  = tk.Frame(bot, bg=T["panel"]); br.pack(anchor="w")

        def save():
            if not cb.get(): err.config(text="Please select a value."); return
            ok, msg = action(cb.get())
            if ok: self.load(); d.destroy()
            else:  err.config(text=f"✗  {msg}")

        btn_success(br, "✓  Save",   save     ).pack(side="left", padx=(0, 8))
        btn_ghost(br,   "✕  Cancel", d.destroy).pack(side="left")

    def do_view_items(self):
        oid = self._sel()
        if oid is None: return
        d = tk.Toplevel(self)
        d.title(f"Items — Order #{oid}"); d.configure(bg=T["bg"])
        d.geometry("660x380"); d.grab_set()
        tk.Label(d, text=f"Order #{oid}  —  Items", bg=T["bg"], fg=T["text"],
                 font=("Segoe UI", 12, "bold")).pack(padx=12, pady=10, anchor="w")
        tree = make_tree(d,
            ["item_id","item_name","qty","unit_price","subtotal","note"],
            [70, 220, 60, 100, 100, 180])
        rows, _ = db.rows(
            "SELECT oi.order_item_id,mi.name,oi.quantity,"
            "oi.unit_price,oi.subtotal,ISNULL(oi.special_requests,'—')"
            " FROM OrderItems oi"
            " JOIN MenuItems mi ON mi.item_id=oi.item_id"
            " WHERE oi.order_id=?", [oid])
        for r in rows: tree.insert("", "end", values=list(r))

    def do_new(self): _NewOrderDlg(self)

    def do_delete(self):
        oid = self._sel()
        if oid is None: return
        if not messagebox.askyesno("Confirm Delete",
            f"Delete Order #{oid}? This cannot be undone.", icon="warning"): return
        ok, msg = db.run("DELETE FROM Orders WHERE order_id=?", [oid])
        if ok:  self.load()
        else:   messagebox.showerror("Delete failed", msg)


class _NewOrderDlg(tk.Toplevel):
    def __init__(self, tab):
        super().__init__(tab)
        self.tab = tab; self.items = []
        self.title("New Order"); self.configure(bg=T["bg"])
        self.geometry("760x620"); self.grab_set()
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 760) // 2
        y = (self.winfo_screenheight() - 620) // 2
        self.geometry(f"+{x}+{y}")
        self._build()

    def _build(self):
        left  = tk.Frame(self, bg=T["panel"], padx=18, pady=16, width=300)
        left.pack(side="left", fill="y"); left.pack_propagate(False)
        right = tk.Frame(self, bg=T["bg"]); right.pack(side="left", fill="both", expand=True)

        tk.Label(left, text="Order Details", bg=T["panel"], fg=T["text"],
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 10))

        cust, _ = db.rows("SELECT customer_id,first_name+' '+last_name FROM Customers ORDER BY last_name")
        emp, _  = db.rows("SELECT employee_id,first_name+' '+last_name FROM Employees WHERE is_active=1 ORDER BY last_name")
        tbl, _  = db.rows("SELECT table_id,table_number FROM Tables WHERE status='available' ORDER BY table_number")
        itm, _  = db.rows("SELECT item_id,name,price FROM MenuItems WHERE is_available=1 ORDER BY name")

        self.cust_m = {n: i for i, n in cust}
        self.emp_m  = {n: i for i, n in emp}
        self.tbl_m  = {str(n): i for i, n in tbl}
        self.item_m = {f"{n}  (${p})": (i, float(p)) for i, n, p in itm}

        # ── helper: label+widget in same row inside `left` panel ────────
        def mk(label_text, parent=left):
            f = tk.Frame(parent, bg=T["panel"]); f.pack(fill="x", pady=4)
            tk.Label(f, text=label_text+":", bg=T["panel"], fg=T["text_dim"],
                     font=("Segoe UI", 9), width=10, anchor="w").pack(side="left")
            return f

        def ent(f, w=22):
            return tk.Entry(f, bg=T["card"], fg=T["text"], insertbackground=T["text"],
                            font=("Segoe UI",10), width=w, relief="flat",
                            highlightthickness=1, highlightbackground=T["border"])

        def cmb(f, vals, w=22):
            return ttk.Combobox(f, values=vals, width=w, font=("Segoe UI",10), state="readonly")

        f = mk("Customer *"); self.cb_c = cmb(f, list(self.cust_m)); self.cb_c.pack(side="left")
        f = mk("Waiter");     self.cb_e = cmb(f, list(self.emp_m));  self.cb_e.pack(side="left")
        f = mk("Type")
        self.cb_t = cmb(f, ["dine_in","takeaway","delivery"]); self.cb_t.set("dine_in"); self.cb_t.pack(side="left")
        f = mk("Table");      self.cb_tb = cmb(f, list(self.tbl_m)); self.cb_tb.pack(side="left")

        h_line(left).pack(fill="x", pady=10)
        tk.Label(left, text="Add Items", bg=T["panel"], fg=T["accent2"],
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 6))

        f = mk("Item");  self.cb_i = cmb(f, list(self.item_m), 22); self.cb_i.pack(side="left")
        f = mk("Qty");   self.e_q  = ent(f, 5); self.e_q.insert(0, "1"); self.e_q.pack(side="left")
        f = mk("Note");  self.e_n  = ent(f, 18); self.e_n.pack(side="left")
        btn_accent2(left, "+  Add Item", self._add).pack(anchor="w", pady=8)

        self.tot = tk.Label(left, text="Total: $0.00", bg=T["panel"], fg=T["success"],
                             font=("Segoe UI", 13, "bold")); self.tot.pack(anchor="w")
        self.err = tk.Label(left, text="", bg=T["panel"], fg=T["danger"],
                             font=("Segoe UI", 9), wraplength=240); self.err.pack(pady=4)
        btn_success(left, "✓  Place Order", self._place).pack(anchor="w", pady=6)

        tk.Label(right, text="Items in this order", bg=T["bg"], fg=T["text"],
                 font=("Segoe UI", 11, "bold")).pack(padx=8, pady=8, anchor="w")
        self.itree = make_tree(right,
            ["name","qty","unit_price","subtotal","note"],
            [200, 50, 90, 90, 160])
        btn_ghost(right, "✕  Remove Selected", self._remove).pack(pady=4)

    def _add(self):
        sel = self.cb_i.get()
        if not sel: self.err.config(text="Select an item."); return
        iid, price = self.item_m[sel]
        try:   qty = int(self.e_q.get()); assert qty > 0
        except: self.err.config(text="Qty must be a positive number."); return
        note = self.e_n.get().strip() or None
        sub  = round(price * qty, 2)
        name = sel.split("  ($")[0]
        self.items.append((iid, name, qty, price, sub, note))
        self.itree.insert("", "end", values=(name, qty, price, sub, note or ""))
        self.tot.config(text=f"Total: ${sum(x[4] for x in self.items):.2f}")
        self.err.config(text="")
        self.e_q.delete(0, "end"); self.e_q.insert(0, "1")
        self.e_n.delete(0, "end")

    def _remove(self):
        s = self.itree.selection()
        if not s: return
        idx = self.itree.index(s[0])
        self.items.pop(idx); self.itree.delete(s[0])
        self.tot.config(text=f"Total: ${sum(x[4] for x in self.items):.2f}")

    def _place(self):
        cid = self.cust_m.get(self.cb_c.get())
        if not cid: self.err.config(text="Please select a customer."); return
        if not self.items: self.err.config(text="Add at least one item."); return
        eid   = self.emp_m.get(self.cb_e.get()) or None
        tid   = self.tbl_m.get(self.cb_tb.get()) or None
        total = sum(x[4] for x in self.items)
        ok, msg = db.run(
            "INSERT INTO Orders(customer_id,employee_id,table_id,"
            "order_type,status,total_price) VALUES(?,?,?,?,'pending',?)",
            [cid, eid, tid, self.cb_t.get(), total])
        if not ok: self.err.config(text=f"✗  {msg}"); return
        oid = db.scalar("SELECT MAX(order_id) FROM Orders")
        for iid, name, qty, price, sub, note in self.items:
            db.run(
                "INSERT INTO OrderItems(order_id,item_id,quantity,"
                "unit_price,subtotal,special_requests) VALUES(?,?,?,?,?,?)",
                [oid, iid, qty, price, sub, note])
        self.tab.load()
        messagebox.showinfo("Order Placed", f"Order #{oid} placed!\nTotal: ${total:.2f}")
        self.destroy()


# ─────────────────────────────────────────────────────────────────────────────
# RESERVATIONS
# ─────────────────────────────────────────────────────────────────────────────
class ReservationsTab(CrudTab):
    TITLE = "Reservations"; SUB = "Table bookings"
    COLS  = ["ID","Customer","Table","Date","Time","Party","Status"]
    WIDTHS = [60, 190, 70, 110, 90, 70, 110]
    SQL_LIST = ("SELECT r.reservation_id, c.first_name+' '+c.last_name,"
                "t.table_number, r.reservation_date, r.reservation_time,"
                "r.party_size, r.status"
                " FROM Reservations r"
                " JOIN Customers c ON c.customer_id=r.customer_id"
                " JOIN Tables t ON t.table_id=r.table_id"
                " ORDER BY r.reservation_date DESC, r.reservation_time DESC")

    def _form(self, vals): _ResDlg(self, vals)
    def sql_delete(self): return "DELETE FROM Reservations WHERE reservation_id=?"


class _ResDlg(tk.Toplevel):
    def __init__(self, tab, vals):
        super().__init__(tab)
        self.tab = tab; self.vals = vals; self.is_edit = vals is not None
        self.title("Edit Reservation" if self.is_edit else "Add Reservation")
        self.configure(bg=T["bg"]); self.geometry("500x420")
        self.resizable(True, True); self.grab_set()
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 500) // 2
        y = (self.winfo_screenheight() - 420) // 2
        self.geometry(f"+{x}+{y}")
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=T["panel"], padx=18, pady=12); top.pack(fill="x")
        tk.Label(top, text=self.title(), bg=T["panel"], fg=T["text"],
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        h_line(self).pack(fill="x")
        body = tk.Frame(self, bg=T["bg"], padx=22, pady=14)
        body.pack(fill="both", expand=True)

        cust, _ = db.rows("SELECT customer_id,first_name+' '+last_name FROM Customers ORDER BY last_name")
        tbls, _ = db.rows("SELECT table_id,table_number FROM Tables ORDER BY table_number")
        self.cm = {n: i for i, n in cust}
        self.tm = {str(n): i for i, n in tbls}

        # ── helper: label+widget in same row ──────────────────────────
        def mk(label_text):
            f = tk.Frame(body, bg=T["bg"]); f.pack(fill="x", pady=6)
            tk.Label(f, text=label_text+":", bg=T["bg"], fg=T["text_dim"],
                     font=("Segoe UI", 9), width=24, anchor="w").pack(side="left")
            return f

        f = mk("Customer *")
        self.cb_c = ttk.Combobox(f, values=list(self.cm), width=26,
                                  font=("Segoe UI",10), state="readonly")
        self.cb_c.pack(side="left")

        f = mk("Table *")
        self.cb_t = ttk.Combobox(f, values=list(self.tm), width=14,
                                  font=("Segoe UI",10), state="readonly")
        self.cb_t.pack(side="left")

        f = mk("Date * (YYYY-MM-DD)")
        self.e_d = tk.Entry(f, bg=T["card"], fg=T["text"], insertbackground=T["text"],
                             font=("Segoe UI",10), width=16, relief="flat",
                             highlightthickness=1, highlightbackground=T["border"])
        self.e_d.pack(side="left")
        self.e_d.insert(0, datetime.now().strftime("%Y-%m-%d"))

        f = mk("Time * (HH:MM)")
        self.e_ti = tk.Entry(f, bg=T["card"], fg=T["text"], insertbackground=T["text"],
                              font=("Segoe UI",10), width=12, relief="flat",
                              highlightthickness=1, highlightbackground=T["border"])
        self.e_ti.pack(side="left")
        self.e_ti.insert(0, "19:00")

        f = mk("Party Size *")
        self.e_ps = tk.Entry(f, bg=T["card"], fg=T["text"], insertbackground=T["text"],
                              font=("Segoe UI",10), width=8, relief="flat",
                              highlightthickness=1, highlightbackground=T["border"])
        self.e_ps.pack(side="left")

        f = mk("Status")
        self.cb_s = ttk.Combobox(f,
            values=["pending","confirmed","seated","cancelled","no_show"],
            width=18, font=("Segoe UI",10), state="readonly")
        self.cb_s.set("pending"); self.cb_s.pack(side="left")

        # Pre-fill: [id, customer_name, table_number, date, time, party, status]
        if self.is_edit:
            v = self.vals
            if str(v[1]) in self.cm: self.cb_c.set(str(v[1]))
            if str(v[2]) in self.tm: self.cb_t.set(str(v[2]))
            self.e_d.delete(0, "end");  self.e_d.insert(0,  str(v[3]).split(" ")[0])
            self.e_ti.delete(0, "end"); self.e_ti.insert(0, str(v[4])[:5])
            self.e_ps.delete(0, "end"); self.e_ps.insert(0, str(v[5]))
            self.cb_s.set(str(v[6]))

        h_line(self).pack(fill="x")
        bot = tk.Frame(self, bg=T["panel"], padx=18, pady=10); bot.pack(fill="x")
        self.err = tk.Label(bot, text="", bg=T["panel"], fg=T["danger"],
                             font=("Segoe UI", 9)); self.err.pack(anchor="w", pady=(0, 6))
        br = tk.Frame(bot, bg=T["panel"]); br.pack(anchor="w")
        btn_success(br, "✓  Save",   self._save  ).pack(side="left", padx=(0, 8))
        btn_ghost(br,   "✕  Cancel", self.destroy).pack(side="left")

    def _save(self):
        cid = self.cm.get(self.cb_c.get())
        tid = self.tm.get(self.cb_t.get())
        d   = self.e_d.get().strip()
        t   = self.e_ti.get().strip()
        ps  = self.e_ps.get().strip()
        s   = self.cb_s.get()
        if not cid: self.err.config(text="✗  Select a customer."); return
        if not tid: self.err.config(text="✗  Select a table."); return
        if not d or not t or not ps:
            self.err.config(text="✗  Date, time and party size are required."); return
        # Validate date format (YYYY-MM-DD)
        try:
            datetime.strptime(d, "%Y-%m-%d")
        except ValueError:
            self.err.config(text="✗  Date must be YYYY-MM-DD (e.g. 2025-12-31)"); return
        # Ensure time has seconds for SQL Server
        if len(t) == 5: t = t + ":00"
        args = [cid, tid, d, t, ps, s]
        if self.is_edit:
            pk = self.vals[0]
            try: pk = int(pk)
            except: pass
            ok, msg = db.run(
                "UPDATE Reservations SET customer_id=?,table_id=?,"
                "reservation_date=?,reservation_time=?,party_size=?,status=?"
                " WHERE reservation_id=?", args + [pk])
        else:
            ok, msg = db.run(
                "INSERT INTO Reservations(customer_id,table_id,"
                "reservation_date,reservation_time,party_size,status)"
                " VALUES(?,?,?,?,?,?)", args)
        if ok:  self.tab.load(); self.destroy()
        else:   self.err.config(text=f"✗  {msg}")


# ─────────────────────────────────────────────────────────────────────────────
# INVENTORY
# ─────────────────────────────────────────────────────────────────────────────
class InventoryTab(CrudTab):
    TITLE = "Inventory"; SUB = "Ingredients & stock levels"
    COLS  = ["ID","Name","Unit","Stock Qty","Reorder Level","Status"]
    WIDTHS = [60, 200, 80, 100, 120, 110]
    SQL_LIST = (
        "SELECT ingredient_id, name, unit, stock_quantity, reorder_level,"
        "CASE WHEN stock_quantity<=reorder_level THEN '⚠ LOW' ELSE '✓ OK' END"
        " FROM Ingredients ORDER BY name")

    def form_fields(self):
        return [
            ("Name",           "entry", {"required": True}),
            ("Unit",           "entry", {"required": True}),
            ("Stock Quantity", "entry", {"required": True}),
            ("Reorder Level",  "entry", {"required": True}),
        ]
    def sql_insert(self):
        return "INSERT INTO Ingredients(name,unit,stock_quantity,reorder_level) VALUES(?,?,?,?)"
    def sql_update(self):
        return ("UPDATE Ingredients SET name=?,unit=?,stock_quantity=?,reorder_level=?"
                " WHERE ingredient_id=?")
    def sql_delete(self): return "DELETE FROM Ingredients WHERE ingredient_id=?"

    def extra_btns(self, bar):
        Btn(bar, "↕  Adjust Stock", self._adjust,
            bg=T["warning"], hov="#d68910", px=12, py=6).pack(side="left", padx=2)

    def _adjust(self):
        pk, vals = self._sel()
        if pk is None:
            messagebox.showinfo("Nothing selected","Select an ingredient first."); return

        d = tk.Toplevel(self); d.title(f"Adjust Stock: {vals[1]}")
        d.configure(bg=T["bg"]); d.geometry("380x240"); d.grab_set()
        d.update_idletasks()
        x = (d.winfo_screenwidth()  - 380) // 2
        y = (d.winfo_screenheight() - 240) // 2
        d.geometry(f"+{x}+{y}")

        top = tk.Frame(d, bg=T["panel"], padx=18, pady=12); top.pack(fill="x")
        tk.Label(top, text=f"Adjust: {vals[1]}", bg=T["panel"], fg=T["text"],
                 font=("Segoe UI", 11, "bold")).pack(side="left")
        h_line(d).pack(fill="x")
        body = tk.Frame(d, bg=T["bg"], padx=22, pady=14); body.pack(fill="both", expand=True)
        tk.Label(body, text=f"Current:  {vals[3]} {vals[2]}", bg=T["bg"], fg=T["text"],
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 10))
        tk.Label(body, text="Enter change  (+ to add ,  − to remove):",
                 bg=T["bg"], fg=T["text_dim"], font=("Segoe UI", 9)).pack(anchor="w")
        e = entry(body, 14); e.pack(anchor="w", pady=6)
        h_line(d).pack(fill="x")
        bot = tk.Frame(d, bg=T["panel"], padx=18, pady=10); bot.pack(fill="x")
        err = tk.Label(bot, text="", bg=T["panel"], fg=T["danger"],
                        font=("Segoe UI", 9)); err.pack(anchor="w", pady=(0, 6))
        br  = tk.Frame(bot, bg=T["panel"]); br.pack(anchor="w")

        def apply():
            try:   amt = float(e.get())
            except: err.config(text="✗  Enter a valid number."); return
            ok, msg = db.run(
                "UPDATE Ingredients SET stock_quantity=stock_quantity+?"
                " WHERE ingredient_id=?", [amt, pk])
            if ok: self.load(); d.destroy()
            else:  err.config(text=f"✗  {msg}")

        btn_success(br, "✓  Apply",  apply    ).pack(side="left", padx=(0, 8))
        btn_ghost(br,   "✕  Cancel", d.destroy).pack(side="left")


# ─────────────────────────────────────────────────────────────────────────────
# PAYMENTS & INVOICES
# ─────────────────────────────────────────────────────────────────────────────
class PaymentsTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=T["bg"]); self._build(); self.load()

    def _build(self):
        f = tk.Frame(self, bg=T["bg"]); f.pack(fill="x", padx=12, pady=(12, 4))
        tk.Label(f, text="Payments & Invoices", bg=T["bg"], fg=T["text"],
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        self.cnt = tk.Label(f, text="", bg=T["bg"], fg=T["text_dim"],
                             font=("Segoe UI", 9)); self.cnt.pack(side="right")
        h_line(self).pack(fill="x", padx=12, pady=(2, 5))

        bar = tk.Frame(self, bg=T["panel"], pady=6)
        bar.pack(fill="x", padx=12, pady=(0, 4))
        btn_accent2(bar, "⟳  Refresh",       self.load           ).pack(side="left", padx=2)
        btn_primary(bar, "+  Create Invoice", self.do_invoice     ).pack(side="left", padx=2)
        btn_success(bar, "💳  Add Payment",   self.do_payment     ).pack(side="left", padx=2)

        self.tree = make_tree(self,
            ["invoice_id","order_id","subtotal","tax","discount","total","status","issued_at"],
            [90, 80, 90, 90, 90, 90, 80, 155])

    def load(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        rows, _ = db.rows(
            "SELECT invoice_id,order_id,subtotal,tax_amount,discount_amount,"
            "total_amount,status,issued_at FROM Invoices ORDER BY invoice_id DESC")
        for r in rows: self.tree.insert("", "end", values=list(r))
        self.cnt.config(text=f"{len(rows)} records")

    def do_invoice(self):
        d = tk.Toplevel(self); d.title("Create Invoice")
        d.configure(bg=T["bg"]); d.geometry("500x350"); d.grab_set()
        d.update_idletasks()
        x = (d.winfo_screenwidth()  - 500) // 2
        y = (d.winfo_screenheight() - 350) // 2
        d.geometry(f"+{x}+{y}")

        top = tk.Frame(d, bg=T["panel"], padx=18, pady=12); top.pack(fill="x")
        tk.Label(top, text="Create Invoice", bg=T["panel"], fg=T["text"],
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        h_line(d).pack(fill="x")
        body = tk.Frame(d, bg=T["bg"], padx=22, pady=14)
        body.pack(fill="both", expand=True)

        # Use NOT EXISTS to avoid the SQL NULL quirk with NOT IN
        ord_r, _ = db.rows(
            "SELECT o.order_id,"
            "CAST(o.order_id AS NVARCHAR)+' | '+c.first_name+' '+c.last_name"
            "+'  ($'+CONVERT(NVARCHAR,ISNULL(o.total_price,0),0)+')'"
            " FROM Orders o JOIN Customers c ON c.customer_id=o.customer_id"
            " WHERE NOT EXISTS("
            "   SELECT 1 FROM Invoices i WHERE i.order_id=o.order_id)"
            " ORDER BY o.order_id DESC")
        ord_m = {t: i for i, t in ord_r}

        # ── helper: label+widget in same row ──────────────────────────
        def mk(label_text):
            f = tk.Frame(body, bg=T["bg"]); f.pack(fill="x", pady=6)
            tk.Label(f, text=label_text+":", bg=T["bg"], fg=T["text_dim"],
                     font=("Segoe UI", 9), width=22, anchor="w").pack(side="left")
            return f

        f = mk("Order *")
        if ord_m:
            cb_o = ttk.Combobox(f, values=list(ord_m), width=32,
                                 font=("Segoe UI",10), state="readonly")
        else:
            cb_o = ttk.Combobox(f, values=["— No uninvoiced orders —"], width=32,
                                 font=("Segoe UI",10), state="readonly")
            cb_o.set("— No uninvoiced orders —")
        cb_o.pack(side="left")

        f = mk("Tax Rate (e.g. 0.14)")
        e_tx = tk.Entry(f, bg=T["card"], fg=T["text"], insertbackground=T["text"],
                         font=("Segoe UI",10), width=10, relief="flat",
                         highlightthickness=1, highlightbackground=T["border"])
        e_tx.insert(0, "0.14"); e_tx.pack(side="left")

        f = mk("Discount Amount ($)")
        e_di = tk.Entry(f, bg=T["card"], fg=T["text"], insertbackground=T["text"],
                         font=("Segoe UI",10), width=10, relief="flat",
                         highlightthickness=1, highlightbackground=T["border"])
        e_di.insert(0, "0.00"); e_di.pack(side="left")

        h_line(d).pack(fill="x")
        bot = tk.Frame(d, bg=T["panel"], padx=18, pady=10); bot.pack(fill="x")
        err = tk.Label(bot, text="", bg=T["panel"], fg=T["danger"],
                        font=("Segoe UI", 9)); err.pack(anchor="w", pady=(0, 6))
        br = tk.Frame(bot, bg=T["panel"]); br.pack(anchor="w")

        def save():
            oid = ord_m.get(cb_o.get())
            if not oid: err.config(text="✗  Please select an order."); return
            try:   tax = float(e_tx.get()); disc = float(e_di.get())
            except: err.config(text="✗  Tax and discount must be numbers."); return
            r = db.one("SELECT total_price FROM Orders WHERE order_id=?", [oid])
            if not r: return
            sub = float(r[0]); tax_a = round(sub * tax, 2); total = round(sub + tax_a - disc, 2)
            ok, msg = db.run(
                "INSERT INTO Invoices(order_id,subtotal,tax_rate,tax_amount,"
                "discount_amount,total_amount,status,issued_at)"
                " VALUES(?,?,?,?,?,?,'issued',GETDATE())",
                [oid, sub, tax, tax_a, disc, total])
            if ok:
                self.load(); d.destroy()
                messagebox.showinfo("Invoice Created", f"Total: ${total:.2f}")
            else: err.config(text=f"✗  {msg}")

        btn_primary(br, "✓  Create", save     ).pack(side="left", padx=(0, 8))
        btn_ghost(br,   "✕  Cancel", d.destroy).pack(side="left")

    def do_payment(self):
        s = self.tree.selection()
        if not s:
            messagebox.showinfo("Nothing selected", "Select an invoice first."); return
        inv_id = self.tree.item(s[0])["values"][0]
        total  = self.tree.item(s[0])["values"][5]

        d = tk.Toplevel(self); d.title(f"Record Payment — Invoice #{inv_id}")
        d.configure(bg=T["bg"]); d.geometry("480x340"); d.grab_set()
        d.update_idletasks()
        x = (d.winfo_screenwidth()  - 480) // 2
        y = (d.winfo_screenheight() - 340) // 2
        d.geometry(f"+{x}+{y}")

        top = tk.Frame(d, bg=T["panel"], padx=18, pady=12); top.pack(fill="x")
        tk.Label(top, text=f"Invoice #{inv_id}  —  Due: ${total}",
                 bg=T["panel"], fg=T["text"], font=("Segoe UI", 12, "bold")).pack(side="left")
        h_line(d).pack(fill="x")
        body = tk.Frame(d, bg=T["bg"], padx=22, pady=14)
        body.pack(fill="both", expand=True)

        meth, _ = db.rows("SELECT method_id,name FROM PaymentMethods WHERE is_active=1 ORDER BY name")
        mm = {n: i for i, n in meth}

        def mk(label_text):
            f = tk.Frame(body, bg=T["bg"]); f.pack(fill="x", pady=6)
            tk.Label(f, text=label_text+":", bg=T["bg"], fg=T["text_dim"],
                     font=("Segoe UI", 9), width=20, anchor="w").pack(side="left")
            return f

        f = mk("Payment Method *")
        cb_m = ttk.Combobox(f, values=list(mm), width=22,
                             font=("Segoe UI",10), state="readonly")
        cb_m.pack(side="left")

        f = mk("Amount *")
        e_a = tk.Entry(f, bg=T["card"], fg=T["text"], insertbackground=T["text"],
                        font=("Segoe UI",10), width=14, relief="flat",
                        highlightthickness=1, highlightbackground=T["border"])
        e_a.insert(0, str(total)); e_a.pack(side="left")

        f = mk("Reference #")
        e_r = tk.Entry(f, bg=T["card"], fg=T["text"], insertbackground=T["text"],
                        font=("Segoe UI",10), width=22, relief="flat",
                        highlightthickness=1, highlightbackground=T["border"])
        e_r.pack(side="left")

        h_line(d).pack(fill="x")
        bot = tk.Frame(d, bg=T["panel"], padx=18, pady=10); bot.pack(fill="x")
        err = tk.Label(bot, text="", bg=T["panel"], fg=T["danger"],
                        font=("Segoe UI", 9)); err.pack(anchor="w", pady=(0, 6))
        br  = tk.Frame(bot, bg=T["panel"]); br.pack(anchor="w")

        def save():
            mid = mm.get(cb_m.get())
            if not mid: err.config(text="✗  Select a payment method."); return
            try:   amt = float(e_a.get()); assert amt > 0
            except: err.config(text="✗  Amount must be a positive number."); return
            ok, msg = db.run(
                "INSERT INTO Payments(invoice_id,method_id,amount,"
                "reference_number,status,paid_at) VALUES(?,?,?,?,'completed',GETDATE())",
                [inv_id, mid, amt, e_r.get().strip() or None])
            if ok:
                db.run("UPDATE Invoices SET status='paid' WHERE invoice_id=?", [inv_id])
                self.load(); d.destroy()
                messagebox.showinfo("Payment Recorded", f"${amt:.2f} recorded.")
            else: err.config(text=f"✗  {msg}")

        btn_success(br, "✓  Record",  save     ).pack(side="left", padx=(0, 8))
        btn_ghost(br,   "✕  Cancel",  d.destroy).pack(side="left")


# ─────────────────────────────────────────────────────────────────────────────
# REPORTS
# ─────────────────────────────────────────────────────────────────────────────
class ReportsTab(tk.Frame):
    REPORTS = {
        "🏆  Top 10 Selling Items":
            "SELECT TOP 10 mi.name,SUM(oi.quantity) AS sold,SUM(oi.subtotal) AS revenue "
            "FROM OrderItems oi JOIN MenuItems mi ON mi.item_id=oi.item_id "
            "GROUP BY mi.name ORDER BY sold DESC",

        "📊  Revenue by Category":
            "SELECT mc.name,SUM(oi.subtotal) AS revenue "
            "FROM OrderItems oi JOIN MenuItems mi ON mi.item_id=oi.item_id "
            "JOIN MenuCategories mc ON mc.category_id=mi.category_id "
            "GROUP BY mc.name ORDER BY revenue DESC",

        "👤  Employee Performance":
            "SELECT e.first_name+' '+e.last_name AS employee,"
            "COUNT(*) AS orders,SUM(o.total_price) AS revenue "
            "FROM Orders o JOIN Employees e ON e.employee_id=o.employee_id "
            "GROUP BY e.first_name,e.last_name ORDER BY orders DESC",

        "👥  Top Spending Customers":
            "SELECT TOP 20 c.first_name+' '+c.last_name AS customer,"
            "COUNT(*) AS orders,SUM(o.total_price) AS total_spent "
            "FROM Orders o JOIN Customers c ON c.customer_id=o.customer_id "
            "GROUP BY c.first_name,c.last_name ORDER BY total_spent DESC",

        "⚠  Low Stock Alert":
            "SELECT name,unit,stock_quantity,reorder_level,"
            "reorder_level-stock_quantity AS shortage "
            "FROM Ingredients WHERE stock_quantity<=reorder_level ORDER BY shortage DESC",

        "📅  Daily Revenue (Last 30 Days)":
            "SELECT CAST(order_date AS DATE) AS day,COUNT(*) AS orders,"
            "SUM(total_price) AS revenue "
            "FROM Orders WHERE order_date>=DATEADD(DAY,-30,GETDATE()) AND status<>'cancelled' "
            "GROUP BY CAST(order_date AS DATE) ORDER BY day DESC",

        "🪑  Table Utilisation":
            "SELECT t.table_number,t.capacity,t.location,"
            "COUNT(o.order_id) AS uses,ISNULL(SUM(o.total_price),0) AS revenue "
            "FROM Tables t LEFT JOIN Orders o ON o.table_id=t.table_id "
            "GROUP BY t.table_number,t.capacity,t.location ORDER BY uses DESC",

        "💳  Payment Methods":
            "SELECT pm.name,COUNT(*) AS transactions,SUM(p.amount) AS collected "
            "FROM Payments p JOIN PaymentMethods pm ON pm.method_id=p.method_id "
            "WHERE p.status='completed' GROUP BY pm.name ORDER BY collected DESC",

        "📋  All Orders Summary":
            "SELECT o.status,COUNT(*) AS orders,SUM(o.total_price) AS revenue "
            "FROM Orders o GROUP BY o.status ORDER BY revenue DESC",
    }

    def __init__(self, parent):
        super().__init__(parent, bg=T["bg"]); self._build()

    def _build(self):
        f = tk.Frame(self, bg=T["bg"]); f.pack(fill="x", padx=12, pady=(12, 4))
        tk.Label(f, text="Reports", bg=T["bg"], fg=T["text"],
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        h_line(self).pack(fill="x", padx=12, pady=(2, 6))

        top = tk.Frame(self, bg=T["panel"]); top.pack(fill="x", padx=12, pady=(0, 6))
        tk.Label(top, text="Report:", bg=T["panel"], fg=T["text_dim"],
                 font=("Segoe UI", 9)).pack(side="left", padx=8, pady=10)
        self.cb  = combo(top, list(self.REPORTS), 48); self.cb.pack(side="left", padx=6)
        btn_primary(top, "▶  Run Report", self._run).pack(side="left", padx=6)
        self.cnt = tk.Label(top, text="", bg=T["panel"], fg=T["text_dim"],
                             font=("Segoe UI", 9)); self.cnt.pack(side="right", padx=12)
        self.wrap = tk.Frame(self, bg=T["bg"]); self.wrap.pack(fill="both", expand=True)

    def _run(self):
        sel = self.cb.get()
        if not sel: messagebox.showinfo("", "Please select a report first."); return
        rows, cols = db.rows(self.REPORTS[sel])
        for w in self.wrap.winfo_children(): w.destroy()
        tree = make_tree(self.wrap, cols)
        for r in rows: tree.insert("", "end", values=list(r))
        self.cnt.config(text=f"{len(rows)} rows")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APPLICATION
# ─────────────────────────────────────────────────────────────────────────────
SECTIONS = [
    ("📊", "Dashboard",       DashboardTab),
    ("👥", "Customers",       CustomersTab),
    ("👤", "Employees",       EmployeesTab),
    ("🏢", "Departments",     DepartmentsTab),
    ("🎭", "Roles",           RolesTab),
    ("📂", "Menu Categories", MenuCatTab),
    ("🍔", "Menu Items",      MenuItemsTab),
    ("📋", "Orders",          OrdersTab),
    ("🪑", "Tables",          TablesTab),
    ("📅", "Reservations",    ReservationsTab),
    ("📦", "Inventory",       InventoryTab),
    ("🚚", "Suppliers",       SuppliersTab),
    ("💳", "Payments",        PaymentsTab),
    ("📈", "Reports",         ReportsTab),
]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Restaurant Management System")
        self.configure(bg=T["bg"]); self.geometry("1300x760"); self.minsize(960, 600)
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{(sw-1300)//2}+{(sh-760)//2}")
        self._cur = None; self._nav = {}; self._tabs = {}
        self._build()
        self.switch("Dashboard")

    def _build(self):
        # ── Top bar ───────────────────────────────────────────────────
        topbar = tk.Frame(self, bg=T["panel"], height=54,
                          highlightthickness=1, highlightbackground=T["border"])
        topbar.pack(fill="x"); topbar.pack_propagate(False)

        logo = tk.Frame(topbar, bg=T["panel"]); logo.pack(side="left", padx=14)
        tk.Label(logo, text="🍽", bg=T["panel"],
                 font=("Segoe UI Emoji", 22)).pack(side="left", padx=(0, 6))
        lf = tk.Frame(logo, bg=T["panel"]); lf.pack(side="left")
        tk.Label(lf, text="Restaurant MS", bg=T["panel"], fg=T["text"],
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Label(lf, text="Management System", bg=T["panel"], fg=T["text_dim"],
                 font=("Segoe UI", 8)).pack(anchor="w")

        right = tk.Frame(topbar, bg=T["panel"]); right.pack(side="right", padx=12)
        self._theme_btn = Btn(right, f" {T['toggle']}  Theme ", self._toggle_theme,
                               bg=T["card2"], hov=T["border"],
                               fg=T["text"], font=("Segoe UI", 9), px=10, py=7)
        self._theme_btn.pack(side="right", padx=6)
        tk.Label(right, text="●  Connected", bg=T["panel"], fg=T["success"],
                 font=("Segoe UI", 9)).pack(side="right", padx=10)

        # ── Body ──────────────────────────────────────────────────────
        body = tk.Frame(self, bg=T["bg"]); body.pack(fill="both", expand=True)

        # Sidebar
        side = tk.Frame(body, bg=T["panel"], width=200,
                        highlightthickness=1, highlightbackground=T["border"])
        side.pack(side="left", fill="y"); side.pack_propagate(False)
        tk.Label(side, text="NAVIGATION", bg=T["panel"], fg=T["text_dim"],
                 font=("Segoe UI", 8, "bold")).pack(pady=(16, 4), padx=14, anchor="w")
        for icon, name, cls in SECTIONS:
            item = NavItem(side, icon, name, lambda n=name: self.switch(n))
            item.pack(fill="x", pady=1, padx=6)
            self._nav[name] = item

        # Content area
        self.content = tk.Frame(body, bg=T["bg"])
        self.content.pack(side="left", fill="both", expand=True)
        for icon, name, cls in SECTIONS:
            try:
                frame = cls(self.content)
            except Exception as e:
                frame = tk.Frame(self.content, bg=T["bg"])
                tk.Label(frame, text=f"Error loading tab:\n{e}",
                         bg=T["bg"], fg=T["danger"], font=("Segoe UI", 10),
                         wraplength=500, justify="left").pack(pady=40, padx=40)
            self._tabs[name] = frame

        # Status bar
        sbar = tk.Frame(self, bg=T["panel"], height=26,
                        highlightthickness=1, highlightbackground=T["border"])
        sbar.pack(fill="x", side="bottom"); sbar.pack_propagate(False)
        self.status = tk.Label(sbar, text="Ready", bg=T["panel"], fg=T["text_dim"],
                                font=("Segoe UI", 8))
        self.status.pack(side="left", padx=12)
        tk.Label(sbar, text=datetime.now().strftime("%d %b %Y"), bg=T["panel"],
                 fg=T["text_dim"], font=("Segoe UI", 8)).pack(side="right", padx=12)

    def switch(self, name):
        if self._cur:
            self._tabs[self._cur].pack_forget()
            self._nav[self._cur].activate(False)
        self._tabs[name].pack(fill="both", expand=True)
        self._nav[name].activate(True)
        self._cur = name
        self.status.config(text=f"Section: {name}")

    def _toggle_theme(self):
        apply_theme(LIGHT if T["name"] == "dark" else DARK)
        for w in self.winfo_children(): w.destroy()
        self._nav.clear(); self._tabs.clear(); self._cur = None
        self._build(); self.switch("Dashboard")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
def main():
    root = tk.Tk(); root.withdraw()
    dlg  = ConnDlg(root); root.wait_window(dlg)
    if not dlg.result:
        root.destroy(); sys.exit(0)
    root.destroy()
    App().mainloop()
    db.close()

if __name__ == "__main__":
    main()
