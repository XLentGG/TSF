# -*- coding: utf-8 -*-
"""
goost_modern_full_admin_v2.py

Fixes & upgrades:
- Admin/UAC elevation (Windows)
- Hover-only descriptions (no click overwrite)
- Real commands for actions (Defender/Firewall/cleanup/libs)
- Russian texts fit: smart word-wrap + auto font shrink (2 lines)
- Compact UI (height ~460), draggable, rounded aqua background
- Bottom buttons readable in dark theme; RU layout-friendly font sizes
- Privacy/About: long texts
- Mini-stats (CPU/RAM/Disk) + simple progress bar for actions
"""
import sys, os, ctypes, subprocess, json, random
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QLocale, QPoint, QRect
from PySide6.QtGui import QColor, QPainter, QFont, QPainterPath, QLinearGradient, QBrush, QFontMetrics
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QGridLayout, QFrame, QDialog, QTextEdit, QGraphicsDropShadowEffect,
    QSizePolicy, QMessageBox, QProgressBar
)

# ---------------- Admin / UAC ----------------
def ensure_admin():
    if os.name != "nt":
        return
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        is_admin = False
    if not is_admin:
        try:
            QMessageBox.information(None, "Admin rights required",
                                    "Требуются права администратора. Приложение перезапустится с повышенными правами.")
        except Exception:
            pass
        params = " ".join([f'"{a}"' if " " in a else a for a in sys.argv])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        sys.exit(0)

# ---------------- Optional psutil ----------------
try:
    import psutil
    HAS_PSUTIL = True
except Exception:
    HAS_PSUTIL = False

CONFIG = Path("config.json")

TR = {
    "ru": {
        "title": "Touch Skins Fix ⚡",
        "version": "v1.0.112",
        "version": "v1.0.112",
        "internet_clean": "Очистка интернета",
        "system_clean": "Очистка системы",
        "libs": "Установить компоненты",
        "disable_defender": "Отключить Defender",
        "disable_firewall": "Отключить брандмауэр",
        "clean_all": "Все сразу",
        "desc_title": "Описание",
        "privacy": "📜 Конфиденциальность",
        "about": "ℹ️ О программе",
        "author": "👤 Автор",
        "author_title": "Автор",
        "author_creator": "Создатель: Atl1s",
        "author_support": "Support: chatgpt.com",
        "theme_dark": "🌙 Тёмная",
        "theme_light": "☀️ Светлая",
        "status_ready": "Готово",
        "stats_title": "Мини-статистика",
        "stats_cpu": "CPU",
        "stats_ram": "RAM",
        "stats_disk": "Диск",
        "stats_na": "Нет данных (psutil не установлен)",
        "lang_ru": "RU",
        "lang_en": "EN",
        "policy_title": "Политика конфиденциальности",
        "policy_body": (
            "Мы уважаем вашу конфиденциальность:\n\n"
            "• Программа не собирает, не хранит и не передаёт персональные данные.\n"
            "• Все операции выполняются локально. Доступ в интернет используется только для установки библиотек через pip.\n"
            "• Утилита не создаёт скрытых служб и задач планировщика, не внедряется в автозагрузку без вашего согласия.\n"
            "• Изменения системы происходят лишь по вашей команде (нажатие кнопок) и обратимы стандартными средствами Windows.\n\n"
            "Ответственность за применение функций (например, отключение средств защиты) несёт пользователь."
        ),
        "about_title": "О программе",
        "about_body": (
            "Touch Skins Fix — компактная утилита для обслуживания Windows:\n\n"
            "— Очистка интернета: сброс DNS-кэша, очистка временных файлов.\n"
            "— Очистка системы: Temp, Prefetch, Корзина.\n"
            "— Установка компонентов: VC++ Redistributable, .NET Framework.\n"
            "— Отключение Defender и брандмауэра (требуются права администратора).\n\n"
            "Внимание: отключение системной защиты снижает безопасность. Используйте ответственно."
        ),
        "desc": {
            "internet": "Сбрасывает DNS-кэш и очищает временные интернет-файлы (Temp).",
            "system": "Удаляет Prefetch/Temp и очищает Корзину для освобождения места.",
            "libs": "Скачивает и открывает ссылки для установки библиотек и компонентов Windows (VC++ Redistributable, .NET Framework).",
            "defender": "Отключает защиту в реальном времени Microsoft Defender.",
            "firewall": "Отключает брандмауэр Windows для всех профилей.",
            "all": "Выполняет все операции последовательно."
        }
    },
    "en": {
        "title": "Touch Skins Fix ⚡",
        "version": "v1.0.112",
        "version": "v1.0.112",
        "internet_clean": "Internet Cleanup",
        "system_clean": "System Cleanup",
        "libs": "Install Components",
        "disable_defender": "Disable Defender",
        "disable_firewall": "Disable Firewall",
        "clean_all": "Clean All",
        "desc_title": "Description",
        "privacy": "Privacy Policy",
        "about": "About",
        "author": "👤 Author",
        "author_title": "Author",
        "author_creator": "Creator: Atl1s",
        "author_support": "Support: chatgpt.com",
        "theme_dark": "🌙 Dark",
        "theme_light": "☀️ Light",
        "status_ready": "Ready",
        "stats_title": "Mini-Stats",
        "stats_cpu": "CPU",
        "stats_ram": "RAM",
        "stats_disk": "Disk",
        "stats_na": "No data (psutil not installed)",
        "lang_ru": "RU",
        "lang_en": "EN",
        "policy_title": "Privacy Policy",
        "policy_body": (
            "We respect your privacy:\n\n"
            "• The app does not collect, store, or transmit personal data.\n"
            "• All operations run locally. Internet is used only for pip installs.\n"
            "• The tool does not create hidden services or scheduled tasks, nor does it inject itself into startup without consent.\n"
            "• System changes occur only on your command (buttons) and are reversible via standard Windows tools.\n\n"
            "You are responsible for using features (e.g., disabling security)."
        ),
        "about_title": "About",
        "about_body": (
            "Touch Skins Fix is a compact Windows maintenance utility:\n\n"
            "— Internet cleanup: flush DNS cache and temp files.\n"
            "— System cleanup: Temp, Prefetch, Recycle Bin.\n"
            "— Install components: VC++ Redistributable, .NET Framework.\n"
            "— Disable Defender and Firewall (admin rights required).\n\n"
            "Warning: disabling protection lowers security. Use responsibly."
        ),
        "desc": {
            "internet": "Flushes DNS cache and clears Internet temp files.",
            "system": "Removes Prefetch/Temp and empties Recycle Bin.",
            "libs": "Opens links to download and install Windows components (VC++ Redistributable, .NET Framework).",
            "defender": "Disables Microsoft Defender real-time protection.",
            "firewall": "Disables Windows Firewall for all profiles.",
            "all": "Runs all operations sequentially."
        }
    }
}

def load_cfg():
    if CONFIG.exists():
        try: return json.loads(CONFIG.read_text(encoding='utf-8'))
        except Exception: return {}
    return {}

def save_cfg(cfg):
    try: CONFIG.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding='utf-8')
    except Exception: pass

def system_lang():
    return "ru" if QLocale.system().name().lower().startswith("ru") else "en"

# --- Cross-binding QApplication resolver (PySide6 -> PyQt5 -> PySide2) ---
def _get_QApplication():
    try:
        from PySide6.QtWidgets import QApplication
        return QApplication
    except Exception:
        try:
            from PyQt5.QtWidgets import QApplication
            return QApplication
        except Exception:
            from PySide2.QtWidgets import QApplication
            return QApplication



class GlitchTitle(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.base_text = text
        f = QFont(); f.setPointSize(18); f.setBold(True); self.setFont(f)
        self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.timer = QTimer(self); self.timer.timeout.connect(self._tick); self.timer.start(10)
    def set_base_text_no_anim(self, text):
        try:
            self.base_text = text
            self.setText(text)
        except Exception:
            pass

    def _tick(self):
        chars = list(self.base_text)
        for i,ch in enumerate(chars):
            if ch != " " and random.random() < 0.03:
                chars[i] = random.choice("█▓▒#@$&?!")
        self.setText("".join(chars))

class ModernButton(QPushButton):
    """Custom button with 2-line word-wrap and auto font shrink."""
    def __init__(self, icon, text, parent=None):
        super().__init__("", parent)
        self.icon = icon
        self._text = text
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setMinimumHeight(60)
        f = QFont(); f.setPointSize(12); f.setBold(False); self.setFont(f)
        self._hover = False
    def setTextLabel(self, text):
        self._text = text; self.update()
    def enterEvent(self, e):
        self._hover = True; self.update(); super().enterEvent(e)
    def leaveEvent(self, e):
        self._hover = False; self.update(); super().leaveEvent(e)
    def _best_font(self, rect_w, rect_h, is_dark):
        f = QFont(self.font())
        # Try to fit text into max 2 lines with shrinking font size
        s = f.pointSize()
        while s >= 9:
            f.setPointSize(s)
            fm = QFontMetrics(f)
            text = f"{self.icon}  {self._text}"
            br = fm.boundingRect(QRect(0,0, max(120, rect_w-24), rect_h-10),
                                 Qt.AlignLeft|Qt.AlignVCenter|Qt.TextWordWrap, text)
            lines_est = max(1, int(br.height() / fm.lineSpacing()))
            if br.width() <= rect_w-24 and lines_est <= 2:
                return f
            s -= 1
        f.setPointSize(9); return f
    def paintEvent(self, e):
        qp = QPainter(self); qp.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(2,2,-2,-2)
        wnd = self.window(); is_dark = getattr(wnd, "theme_dark", True)
        if self._hover:
            grad = QLinearGradient(0,0,rect.width(),rect.height())
            if is_dark:
                grad.setColorAt(0, QColor(100,110,140)); grad.setColorAt(1, QColor(70,80,110))
            else:
                grad.setColorAt(0, QColor(160,190,255)); grad.setColorAt(1, QColor(120,150,240))
            qp.setBrush(QBrush(grad))
        else:
            qp.setBrush(QColor(45,47,55) if is_dark else QColor(235,235,238))
        qp.setPen(Qt.NoPen); qp.drawRoundedRect(rect, 12, 12)

        qp.setFont(self._best_font(rect.width(), rect.height(), is_dark))
        qp.setPen(QColor(245,245,248) if is_dark else QColor(20,20,22))
        qp.drawText(rect.adjusted(12,4,-12,-4),
                    Qt.AlignVCenter|Qt.AlignLeft|Qt.TextWordWrap,
                    f"{self.icon}  {self._text}")

class StatsCard(QFrame):
    def __init__(self, tr, parent=None):
        super().__init__(parent)
        self.tr = tr
        self.setFixedHeight(56)
        lay = QHBoxLayout(self); lay.setContentsMargins(6,6,6,6); lay.setSpacing(8)
        self.lbl_cpu = QLabel(self.tr["stats_cpu"]+": -%")
        self.lbl_ram = QLabel(self.tr["stats_ram"]+": -%")
        self.lbl_disk = QLabel(self.tr["stats_disk"]+": -%")
        for w in (self.lbl_cpu,self.lbl_ram,self.lbl_disk):
            w.setStyleSheet("padding:4px 6px;border-radius:8px;")
            lay.addWidget(w)
        if HAS_PSUTIL:
            self.timer = QTimer(self); self.timer.timeout.connect(self._update); self.timer.start(10)
            self._update()
        else:
            self.lbl_cpu.setText(self.tr["stats_na"])
    def _update(self):
        try:
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage("/").percent
            self.lbl_cpu.setText(f"{self.tr['stats_cpu']}: {cpu}%")
            self.lbl_ram.setText(f"{self.tr['stats_ram']}: {ram}%")
            self.lbl_disk.setText(f"{self.tr['stats_disk']}: {disk}%")
        except Exception:
            pass

class ThemedDialog(QDialog):
    def __init__(self, title, body, dark, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title); self.resize(560,360)
        v = QVBoxLayout(self)
        lab = QLabel(title); f = QFont(); f.setBold(True); lab.setFont(f)
        v.addWidget(lab)
        txt = QTextEdit(); txt.setReadOnly(True); txt.setText(body); v.addWidget(txt)
        btn = QPushButton("OK"); btn.clicked.connect(self.accept); v.addWidget(btn, alignment=Qt.AlignRight)
        self.apply_theme(dark)
    def apply_theme(self, dark: bool):
        if dark:
            self.setStyleSheet("QDialog{background:#0f1114;color:#eef1f3;} QTextEdit{background:#121418;color:#eef1f3;} QPushButton{color:#eef1f3;}")
        else:
            self.setStyleSheet("QDialog{background:#ffffff;color:#141414;} QTextEdit{background:#f6f6f8;color:#141414;} QPushButton{color:#141414;}")

class TouchSkinsFix(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(800)
        cfg = load_cfg()
        self.lang = cfg.get("lang", system_lang())
        self.tr = TR[self.lang]
        self.theme_dark = cfg.get("theme","dark")=="dark"

        # Frameless + translucent
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._drag = None

        # Central
        central = QWidget(self); central.setStyleSheet("background:transparent;"); self.setCentralWidget(central)
        shadow = QGraphicsDropShadowEffect(self); shadow.setBlurRadius(24); shadow.setOffset(0,8); shadow.setColor(QColor(0,0,0,150))
        central.setGraphicsEffect(shadow)

        root = QVBoxLayout(central); root.setContentsMargins(14,14,14,14); root.setSpacing(8)

        # Top
        top = QHBoxLayout()
        self.title = GlitchTitle(self.tr["title"])
        top.addWidget(self.title)
        self.version_lbl = QLabel(self.tr["version"])
        fver = QFont(); fver.setPointSize(9); fver.setBold(False)
        self.version_lbl.setFont(fver)
        top.addWidget(self.version_lbl)
        top.addStretch()
        self.btn_close = QPushButton("✖"); self.btn_close.setFixedSize(28,28); self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.clicked.connect(self.close); top.addWidget(self.btn_close)
        root.addLayout(top)

        # Content
        content = QHBoxLayout(); content.setSpacing(10)

        grid = QGridLayout(); grid.setHorizontalSpacing(10); grid.setVerticalSpacing(10)
        self.btn_inet = ModernButton("🌐", self.tr["internet_clean"], self)
        self.btn_sys  = ModernButton("🧹", self.tr["system_clean"], self)
        self.btn_libs = ModernButton("📦", self.tr["libs"], self)
        self.btn_def  = ModernButton("🛡️", self.tr["disable_defender"], self)
        self.btn_fire = ModernButton("🔥", self.tr["disable_firewall"], self)
        self.btn_all  = ModernButton("⚡",  self.tr["clean_all"], self)
        bigs = [self.btn_inet, self.btn_sys, self.btn_libs, self.btn_def, self.btn_fire, self.btn_all]
        pos  = [(0,0),(0,1),(1,0),(1,1),(2,0),(2,1)]
        for b,p in zip(bigs,pos): grid.addWidget(b,p[0],p[1])
        content.addLayout(grid, 2)

        side = QVBoxLayout(); side.setSpacing(6)
        self.desc_title = QLabel(self.tr["desc_title"]+":"); side.addWidget(self.desc_title)
        self.desc_text  = QLabel("—"); self.desc_text.setWordWrap(True); side.addWidget(self.desc_text)
        self.stats = StatsCard(self.tr, self); side.addWidget(self.stats)
        self.progress = QProgressBar(); self.progress.setRange(0,100); self.progress.setValue(0); side.addWidget(self.progress)
        self.status = QLabel(self.tr["status_ready"]); side.addWidget(self.status)
        content.addLayout(side, 3)

        root.addLayout(content)

        # Bottom
        bottom = QHBoxLayout(); bottom.setSpacing(8)
        self.btn_priv  = QPushButton(self.tr["privacy"])
        self.btn_about = QPushButton(self.tr["about"])
        self.btn_author= QPushButton(self.tr["author"])
        self.btn_theme = QPushButton(self.tr["theme_light"] if self.theme_dark else self.tr["theme_dark"])
        self.btn_lang  = QPushButton(self.tr["lang_ru"] if self.lang=="ru" else self.tr["lang_en"])
        for b in (self.btn_priv,self.btn_about,self.btn_author,self.btn_theme,self.btn_lang):
            b.setCursor(Qt.PointingHandCursor); bottom.addWidget(b)
        root.addLayout(bottom)

        # Connect actions
        self.btn_inet.clicked.connect(lambda: self.run_action("internet"))
        self.btn_sys.clicked.connect(lambda: self.run_action("system"))
        self.btn_libs.clicked.connect(lambda: self.run_action("libs"))
        self.btn_def.clicked.connect(lambda: self.run_action("defender"))
        self.btn_fire.clicked.connect(lambda: self.run_action("firewall"))
        self.btn_all.clicked.connect(lambda: self.run_action("all"))

        # Hover -> description (and clear on leave)
        self._attach_hover(self.btn_inet, "internet")
        self._attach_hover(self.btn_sys, "system")
        self._attach_hover(self.btn_libs, "libs")
        self._attach_hover(self.btn_def, "defender")
        self._attach_hover(self.btn_fire, "firewall")
        self._attach_hover(self.btn_all, "all")

        self.btn_priv.clicked.connect(self.open_privacy)
        self.btn_about.clicked.connect(self.open_about)
        self.btn_author.clicked.connect(self.open_author)
        self.btn_theme.clicked.connect(self.toggle_theme)
        self.btn_lang.clicked.connect(self.toggle_lang)

        # Window
        self.setWindowTitle(self.tr["title"])
        self.resize(900, 460)  # compact
        self.apply_theme()
        self.update_texts()

    # --- Hover helpers ---
    def _attach_hover(self, button: QPushButton, key: str):
        orig_enter = button.enterEvent
        orig_leave = button.leaveEvent
        def enter(e):
            self.set_desc(key); orig_enter(e)
        def leave(e):
            self.set_desc(None); orig_leave(e)
        button.enterEvent = enter
        button.leaveEvent = leave

    # --- Descriptions ---
    def set_desc(self, key):
        if key is None:
            self.desc_text.setText("—")
        else:
            self.desc_text.setText(TR[self.lang]["desc"].get(key, "—"))

    # --- Theme / Lang ---
    def toggle_theme(self):
        self.theme_dark = not self.theme_dark
        save_cfg({"theme":"dark" if self.theme_dark else "light", "lang": self.lang})
        QApplication = _get_QApplication()
        app = QApplication.instance()
        try:
            self.setUpdatesEnabled(False)
            self.apply_theme(); self.update_texts()
        finally:
            self.setUpdatesEnabled(True)
            (app and app.processEvents())
            self.repaint()

    def toggle_lang(self):
        self.lang = "en" if self.lang=="ru" else "ru"
        self.tr = TR[self.lang]
        save_cfg({"theme":"dark" if self.theme_dark else "light", "lang": self.lang})
        self.update_texts()
        QApplication = _get_QApplication()
        app = QApplication.instance()
        try:
            self.setUpdatesEnabled(False)
            self.update_texts(); self.apply_theme()
        finally:
            self.setUpdatesEnabled(True)
            (app and app.processEvents())
            self.repaint()
        return

    def update_texts(self):
        self.title.set_base_text_no_anim(f"{self.tr['title']}") if hasattr(self.title, 'set_base_text_no_anim') else setattr(self.title, 'base_text', f"{self.tr['title']}")
        try:
            self.title.update()
        except Exception:
            pass
        self.setWindowTitle(f"{self.tr['title']} {self.tr['version']}")
        self.version_lbl.setText(self.tr["version"])
        self.btn_inet.setTextLabel(self.tr["internet_clean"])
        self.btn_sys.setTextLabel(self.tr["system_clean"])
        self.btn_libs.setTextLabel(self.tr["libs"])
        self.btn_def.setTextLabel(self.tr["disable_defender"])
        self.btn_fire.setTextLabel(self.tr["disable_firewall"])
        self.btn_all.setTextLabel(self.tr["clean_all"])
        self.desc_title.setText(self.tr["desc_title"] + ":")
        self.btn_priv.setText(self.tr["privacy"])
        self.btn_about.setText(self.tr["about"])
        self.btn_author.setText(self.tr["author"])
        self.btn_theme.setText(self.tr["theme_light"] if self.theme_dark else self.tr["theme_dark"])
        self.btn_lang.setText(self.tr["lang_ru"] if self.lang=="ru" else self.tr["lang_en"])
        self.status.setText(self.tr["status_ready"])
        # reset description on lang change
        self.set_desc(None)
        # refresh stats labels
        try:
            self.stats.lbl_cpu.setText(self.tr["stats_cpu"] + ": -%")
            self.stats.lbl_ram.setText(self.tr["stats_ram"] + ": -%")
            self.stats.lbl_disk.setText(self.tr["stats_disk"] + ": -%")
        except Exception:
            pass

    def apply_theme(self):
        if self.theme_dark:
            label_fg = "#eef1f3"; btn_fg = "#eef1f3"
            close_bg = "#2f2f2f"; close_fg = "#ffffff"
        else:
            label_fg = "#141414"; btn_fg = "#141414"
            close_bg = "#e8e8e8"; close_fg = "#141414"

        base = (
            f"QLabel{{color:{label_fg};}} "
            f"QPushButton{{color:{btn_fg}; background:transparent; border:none}} "
            f"QTextEdit{{background:transparent;color:{label_fg}}} "
            f"QProgressBar{{background:#00000000;border:1px solid rgba(0,0,0,40);border-radius:6px;}} "
            f"QProgressBar::chunk{{margin:1px;border-radius:5px;background:{('#6aa3ff' if not self.theme_dark else '#5b7bd6')};}}"
        )
        self.setStyleSheet(base)
        # bottom buttons smaller font for RU
        font_px = 11 if self.lang=="en" else 10
        for b in (self.btn_priv,self.btn_about,self.btn_author,self.btn_theme,self.btn_lang):
            b.setStyleSheet(
                f"QPushButton{{background:transparent;border:none;color:{btn_fg};padding:6px 8px;font-size:{font_px}px}}"
                "QPushButton:hover{color:#ffd24a}"
            )
        self.btn_close.setStyleSheet(
            f"QPushButton{{border:none;border-radius:14px;background:{close_bg};color:{close_fg};}}"
            "QPushButton:hover{background:#e74c3c;color:white}"
        )
        # version label color
        self.version_lbl.setStyleSheet(f"color:{label_fg};")
        self.version_lbl.setWindowOpacity(0.85)
        self.update()

    # --- Paint rounded aqua bg ---
    def paintEvent(self, event):
        qp = QPainter(self); qp.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(1,1,-1,-1)
        path = QPainterPath(); path.addRoundedRect(rect, 16, 16)
        if self.theme_dark:
            grad = QLinearGradient(0,0,0,self.height())
            grad.setColorAt(0, QColor(30,32,36,230))
            grad.setColorAt(1, QColor(18,20,24,230))
        else:
            grad = QLinearGradient(0,0,0,self.height())
            grad.setColorAt(0, QColor(255,255,255,240))
            grad.setColorAt(1, QColor(238,242,248,240))
        qp.fillPath(path, QBrush(grad))
        super().paintEvent(event)

    # --- Dragging ---
    def mousePressEvent(self, e):
        if e.button()==Qt.LeftButton:
            self._drag = e.globalPosition().toPoint() - self.frameGeometry().topLeft(); e.accept()
        super().mousePressEvent(e)
    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton and self._drag:
            self.move(e.globalPosition().toPoint() - self._drag); e.accept()
        super().mouseMoveEvent(e)

    # --- Dialogs ---
    def open_privacy(self):
        ThemedDialog(self.tr["policy_title"], self.tr["policy_body"], self.theme_dark, self).exec()
    def open_about(self):
        ThemedDialog(self.tr["about_title"], self.tr["about_body"], self.theme_dark, self).exec()
    def open_author(self):
        body = self.tr["author_creator"] + "\n" + self.tr["author_support"]
        ThemedDialog(self.tr["author_title"], body, self.theme_dark, self).exec()

    # --- Helpers ---
    def _run(self, cmd):
        """Run shell command and update status/progress."""
        try:
            cp = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            out = (cp.stdout or "") + (cp.stderr or "")
            self.status.setText("OK" if cp.returncode==0 else f"Error {cp.returncode}")
            QApplication.processEvents()
            return cp.returncode, out.strip()
        except Exception as e:
            self.status.setText(f"Error: {e}"); QApplication.processEvents()
            return 1, str(e)

    def _bump_progress(self, value):
        self.progress.setValue(value); QApplication.processEvents()

    # --- Actions ---
    def run_action(self, name: str):
        self.progress.setValue(0)

        try:
            if name == "internet":
                steps = [
                    'ipconfig /release',
                    'ipconfig /flushdns',
                    'ipconfig /registerdns',
                    'netsh interface set interface name="Ethernet" admin=disable',
                    'netsh interface set interface name="Ethernet" admin=enable'
                ]
                for i, cmd in enumerate(steps, start=1):
                    self.status.setText(cmd)
                    self._bump_progress(int(i/len(steps)*100))
                    self._run(cmd)
                self._bump_progress(100)

            
            elif name == "system":
                steps = [
                    "powershell -NoProfile -Command \"if (Test-Path 'C:\\Windows\\Temp') {Remove-Item 'C:\\Windows\\Temp\\*' -Recurse -Force -ErrorAction SilentlyContinue; Write-Output 'Очистка C:\\Windows\\Temp...'} else {Write-Output 'Папка C:\\Windows\\Temp уже пуста или отсутствует'}\"",
                    "powershell -NoProfile -Command \"if (Test-Path 'C:\\Windows\\Prefetch') {Remove-Item 'C:\\Windows\\Prefetch\\*' -Recurse -Force -ErrorAction SilentlyContinue; Write-Output 'Очистка C:\\Windows\\Prefetch...'} else {Write-Output 'Папка C:\\Windows\\Prefetch уже пуста или отсутствует'}\"",
                    "powershell -NoProfile -Command \"if (Test-Path '%TEMP%') {Remove-Item '%TEMP%\\*' -Recurse -Force -ErrorAction SilentlyContinue; Write-Output 'Очистка %TEMP%...'} else {Write-Output 'Папка %TEMP% уже пуста или отсутствует'}\"",
                    "powershell -NoProfile -Command \"if (Test-Path 'C:\\Windows\\Tempor~1') {Remove-Item 'C:\\Windows\\Tempor~1' -Recurse -Force -ErrorAction SilentlyContinue; Write-Output 'Очистка C:\\Windows\\Tempor~1...'} else {Write-Output 'Папка C:\\Windows\\Tempor~1 уже пуста или отсутствует'}\"",
                    "powershell -NoProfile -Command \"if (Test-Path 'C:\\Windows\\Tmp') {Remove-Item 'C:\\Windows\\Tmp' -Recurse -Force -ErrorAction SilentlyContinue; Write-Output 'Очистка C:\\Windows\\Tmp...'} else {Write-Output 'Папка C:\\Windows\\Tmp уже пуста или отсутствует'}\"",
                    "powershell -NoProfile -Command \"if (Test-Path 'C:\\Windows\\ff*.tmp') {Remove-Item 'C:\\Windows\\ff*.tmp' -Recurse -Force -ErrorAction SilentlyContinue; Write-Output 'Очистка C:\\Windows\\ff*.tmp...'} else {Write-Output 'Папка C:\\Windows\\ff*.tmp уже пуста или отсутствует'}\"",
                    "powershell -NoProfile -Command \"if (Test-Path 'C:\\Windows\\History') {Remove-Item 'C:\\Windows\\History' -Recurse -Force -ErrorAction SilentlyContinue; Write-Output 'Очистка C:\\Windows\\History...'} else {Write-Output 'Папка C:\\Windows\\History уже пуста или отсутствует'}\"",
                    "powershell -NoProfile -Command \"if (Test-Path 'C:\\Windows\\Cookies') {Remove-Item 'C:\\Windows\\Cookies' -Recurse -Force -ErrorAction SilentlyContinue; Write-Output 'Очистка C:\\Windows\\Cookies...'} else {Write-Output 'Папка C:\\Windows\\Cookies уже пуста или отсутствует'}\"",
                    "powershell -NoProfile -Command \"if (Test-Path 'C:\\Windows\\Recent') {Remove-Item 'C:\\Windows\\Recent' -Recurse -Force -ErrorAction SilentlyContinue; Write-Output 'Очистка C:\\Windows\\Recent...'} else {Write-Output 'Папка C:\\Windows\\Recent уже пуста или отсутствует'}\"",
                    "powershell -NoProfile -Command \"if (Test-Path 'C:\\Windows\\Spool\\Printers') {Remove-Item 'C:\\Windows\\Spool\\Printers' -Recurse -Force -ErrorAction SilentlyContinue; Write-Output 'Очистка C:\\Windows\\Spool\\Printers...'} else {Write-Output 'Папка C:\\Windows\\Spool\\Printers уже пуста или отсутствует'}\"",
                ]
                for i, cmd in enumerate(steps, start=1):
                    self.status.setText(cmd)
                    self._bump_progress(int(i/len(steps)*100))
                    self._run(cmd)
                self._bump_progress(100)


            elif name == "libs":
                urls = [
                    "https://www.microsoft.com/ru-ru/download/details.aspx?id=35",
                    "https://dotnet.microsoft.com/en-us/download",
                    "https://www.techpowerup.com/download/visual-c-redistributable-runtime-package-all-in-one/"
                ]
                for i, url in enumerate(urls, start=1):
                    self.status.setText(f"Open: {url}")
                    self._bump_progress(int(i/len(urls)*100))
                    os.startfile(url)
                self._bump_progress(100)

            elif name == "defender":
                steps = [
                    "powershell -NoProfile -Command \"if (Test-Path 'C:\\Windows\\Temp') {Remove-Item 'C:\\Windows\\Temp\\*' -Recurse -Force -ErrorAction SilentlyContinue; Write-Output 'Очистка C:\\Windows\\Temp...'} else {Write-Output 'Папка C:\\Windows\\Temp уже пуста или отсутствует'}\"",
                    "powershell -NoProfile -Command \"if (Test-Path 'C:\\Windows\\Prefetch') {Remove-Item 'C:\\Windows\\Prefetch\\*' -Recurse -Force -ErrorAction SilentlyContinue; Write-Output 'Очистка C:\\Windows\\Prefetch...'} else {Write-Output 'Папка C:\\Windows\\Prefetch уже пуста или отсутствует'}\"",
                    "powershell -NoProfile -Command \"if (Test-Path '%TEMP%') {Remove-Item '%TEMP%\\*' -Recurse -Force -ErrorAction SilentlyContinue; Write-Output 'Очистка %TEMP%...'} else {Write-Output 'Папка %TEMP% уже пуста или отсутствует'}\"",
                    "powershell -NoProfile -Command \"if (Test-Path 'C:\\Windows\\Tempor~1') {Remove-Item 'C:\\Windows\\Tempor~1' -Recurse -Force -ErrorAction SilentlyContinue; Write-Output 'Очистка C:\\Windows\\Tempor~1...'} else {Write-Output 'Папка C:\\Windows\\Tempor~1 уже пуста или отсутствует'}\"",
                    "powershell -NoProfile -Command \"if (Test-Path 'C:\\Windows\\Tmp') {Remove-Item 'C:\\Windows\\Tmp' -Recurse -Force -ErrorAction SilentlyContinue; Write-Output 'Очистка C:\\Windows\\Tmp...'} else {Write-Output 'Папка C:\\Windows\\Tmp уже пуста или отсутствует'}\"",
                    "powershell -NoProfile -Command \"if (Test-Path 'C:\\Windows\\ff*.tmp') {Remove-Item 'C:\\Windows\\ff*.tmp' -Recurse -Force -ErrorAction SilentlyContinue; Write-Output 'Очистка C:\\Windows\\ff*.tmp...'} else {Write-Output 'Папка C:\\Windows\\ff*.tmp уже пуста или отсутствует'}\"",
                    "powershell -NoProfile -Command \"if (Test-Path 'C:\\Windows\\History') {Remove-Item 'C:\\Windows\\History' -Recurse -Force -ErrorAction SilentlyContinue; Write-Output 'Очистка C:\\Windows\\History...'} else {Write-Output 'Папка C:\\Windows\\History уже пуста или отсутствует'}\"",
                    "powershell -NoProfile -Command \"if (Test-Path 'C:\\Windows\\Cookies') {Remove-Item 'C:\\Windows\\Cookies' -Recurse -Force -ErrorAction SilentlyContinue; Write-Output 'Очистка C:\\Windows\\Cookies...'} else {Write-Output 'Папка C:\\Windows\\Cookies уже пуста или отсутствует'}\"",
                    "powershell -NoProfile -Command \"if (Test-Path 'C:\\Windows\\Recent') {Remove-Item 'C:\\Windows\\Recent' -Recurse -Force -ErrorAction SilentlyContinue; Write-Output 'Очистка C:\\Windows\\Recent...'} else {Write-Output 'Папка C:\\Windows\\Recent уже пуста или отсутствует'}\"",
                    "powershell -NoProfile -Command \"if (Test-Path 'C:\\Windows\\Spool\\Printers') {Remove-Item 'C:\\Windows\\Spool\\Printers' -Recurse -Force -ErrorAction SilentlyContinue; Write-Output 'Очистка C:\\Windows\\Spool\\Printers...'} else {Write-Output 'Папка C:\\Windows\\Spool\\Printers уже пуста или отсутствует'}\"",
                ]
                for i, cmd in enumerate(steps, start=1):
                    self.status.setText(cmd)
                    self._bump_progress(int(i/len(steps)*100))
                    self._run(cmd)
                self._bump_progress(100)

            elif name == "firewall":
                cmd = "netsh advfirewall set allprofiles state off"
                self.status.setText(cmd)
                self._run(cmd)
                self._bump_progress(100)

            elif name == "all":
                seq = ["internet","system","libs","defender","firewall"]
                per = 100//len(seq)
                for i,part in enumerate(seq, start=1):
                    self.status.setText(f"Run: {part}")
                    self.run_action(part)
                    self._bump_progress(min(100, i*per))

            else:
                self.status.setText(self.tr["status_ready"])
                self.progress.setValue(0)

        except Exception as e:
            self.status.setText(f"Error: {e}")
            self.progress.setValue(0)


import base64, io

try:
    from PySide6.QtGui import QPixmap, QIcon
    from PySide6.QtCore import QByteArray
    from PySide6.QtWidgets import QSystemTrayIcon
except ImportError:
    from PyQt5.QtGui import QPixmap, QIcon
    from PyQt5.QtCore import QByteArray
    from PyQt5.QtWidgets import QSystemTrayIcon


def get_embedded_icon():
    data = base64.b64decode("""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""")
    pixmap = QPixmap()
    pixmap.loadFromData(QByteArray(data))
    return QIcon(pixmap)


def main():
    app = QApplication(sys.argv)
    ensure_admin()  # UAC elevation if needed
    w = TouchSkinsFix(); w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()