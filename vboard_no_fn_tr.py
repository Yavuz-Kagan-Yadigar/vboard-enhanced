#!/usr/bin/env python3
import gi
import uinput
import os
import configparser

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib


key_mapping = {
    uinput.KEY_ESC: "Esc",
    uinput.KEY_1: "1",  uinput.KEY_2: "2",  uinput.KEY_3: "3",
    uinput.KEY_4: "4",  uinput.KEY_5: "5",  uinput.KEY_6: "6",
    uinput.KEY_7: "7",  uinput.KEY_8: "8",  uinput.KEY_9: "9",
    uinput.KEY_0: "0",
    uinput.KEY_MINUS: "*",    # TR fiziksel: * tuşu
    uinput.KEY_EQUAL: "-",    # TR fiziksel: - tuşu
    uinput.KEY_BACKSPACE: "Backspace",
    uinput.KEY_TAB: "Tab",
    uinput.KEY_Q: "Q",  uinput.KEY_W: "W",  uinput.KEY_E: "E",
    uinput.KEY_R: "R",  uinput.KEY_T: "T",  uinput.KEY_Y: "Y",
    uinput.KEY_U: "U",  uinput.KEY_I: "I",  uinput.KEY_O: "O",
    uinput.KEY_P: "P",
    uinput.KEY_LEFTBRACE: "Ğ",
    uinput.KEY_RIGHTBRACE: "Ü",
    uinput.KEY_ENTER: "Enter",
    uinput.KEY_LEFTCTRL: "Ctrl_L",
    uinput.KEY_A: "A",  uinput.KEY_S: "S",  uinput.KEY_D: "D",
    uinput.KEY_F: "F",  uinput.KEY_G: "G",  uinput.KEY_H: "H",
    uinput.KEY_J: "J",  uinput.KEY_K: "K",  uinput.KEY_L: "L",
    uinput.KEY_SEMICOLON: "Ş",
    uinput.KEY_APOSTROPHE: "İ",
    uinput.KEY_GRAVE: '"',    # TR fiziksel: " tuşu (sol üst)
    uinput.KEY_LEFTSHIFT: "Shift_L",
    uinput.KEY_102ND: "><|",    # TR fiziksel: <>/| tuşu
    uinput.KEY_BACKSLASH: ",",  # TR fiziksel: , tuşu
    uinput.KEY_Z: "Z",  uinput.KEY_X: "X",  uinput.KEY_C: "C",
    uinput.KEY_V: "V",  uinput.KEY_B: "B",  uinput.KEY_N: "N",
    uinput.KEY_M: "M",
    uinput.KEY_COMMA: "Ö",
    uinput.KEY_DOT: "Ç",
    uinput.KEY_SLASH: ".",    # TR fiziksel: . tuşu
    uinput.KEY_RIGHTSHIFT: "Shift_R",
    uinput.KEY_KPENTER: "Enter",
    uinput.KEY_LEFTALT: "Alt_L",  uinput.KEY_RIGHTALT: "Alt_R",
    uinput.KEY_SPACE: "Space",
    uinput.KEY_CAPSLOCK: "CapsLock",
    uinput.KEY_F1: "F1",   uinput.KEY_F2: "F2",   uinput.KEY_F3: "F3",
    uinput.KEY_F4: "F4",   uinput.KEY_F5: "F5",   uinput.KEY_F6: "F6",
    uinput.KEY_F7: "F7",   uinput.KEY_F8: "F8",   uinput.KEY_F9: "F9",
    uinput.KEY_F10: "F10", uinput.KEY_F11: "F11", uinput.KEY_F12: "F12",
    uinput.KEY_SCROLLLOCK: "ScrollLock", uinput.KEY_PAUSE: "Pause",
    uinput.KEY_INSERT: "Insert",   uinput.KEY_HOME: "Home",
    uinput.KEY_PAGEUP: "PageUp",
    uinput.KEY_DELETE: "Delete",   uinput.KEY_END: "End",
    uinput.KEY_PAGEDOWN: "PageDown",
    uinput.KEY_RIGHT: "→", uinput.KEY_LEFT: "←",
    uinput.KEY_DOWN: "↓",  uinput.KEY_UP: "↑",
    uinput.KEY_NUMLOCK: "NumLock",
    uinput.KEY_RIGHTCTRL: "Ctrl_R",
    uinput.KEY_LEFTMETA: "Super_L", uinput.KEY_RIGHTMETA: "Super_R",
}

# TR Türkçe karakter çiftleri — module-level sabit, her update_label çağrısında yeniden oluşturulmuyor
_TR_PAIRS = [("ğ", "Ğ"), ("ü", "Ü"), ("ş", "Ş"), ("ı", "İ"), ("ö", "Ö"), ("ç", "Ç")]
_TR_LOWER = {lo for lo, _ in _TR_PAIRS}
_TR_UPPER = {up for _, up in _TR_PAIRS}
_TR_TO_UPPER = {lo: up for lo, up in _TR_PAIRS}
_TR_TO_LOWER = {up: lo for lo, up in _TR_PAIRS}


class VirtualKeyboard(Gtk.Window):
    def __init__(self):
        super().__init__(title="Virtual Keyboard", name="toplevel")

        self.set_border_width(0)
        self.set_resizable(True)
        self.set_keep_above(True)
        self.set_modal(False)
        self.set_focus_on_map(False)
        self.set_can_focus(False)
        self.set_accept_focus(False)

        self.CONFIG_DIR = os.path.expanduser("~/.config/vboard")
        self.CONFIG_FILE = os.path.join(self.CONFIG_DIR, "settings.conf")
        self.config = configparser.ConfigParser()

        self.bg_color = "0, 0, 0"
        self.opacity = "0.90"
        self.text_color = "white"
        self.width = 0
        self.height = 0
        self.prtsc_command = ""
        self.custom_command = ""
        self.read_settings()

        self.modifiers = {
            uinput.KEY_LEFTSHIFT:  False,
            uinput.KEY_RIGHTSHIFT: False,
            uinput.KEY_LEFTCTRL:   False,
            uinput.KEY_RIGHTCTRL:  False,
            uinput.KEY_LEFTALT:    False,
            uinput.KEY_RIGHTALT:   False,
            uinput.KEY_LEFTMETA:   False,
            uinput.KEY_RIGHTMETA:  False,
        }
        self.caps_lock_on = False
        self.colors = [
            ("Black",     "0,0,0"),
            ("Red",       "255,0,0"),
            ("Pink",      "255,105,183"),
            ("White",     "255,255,255"),
            ("Green",     "0,255,0"),
            ("Blue",      "0,0,110"),
            ("Gray",      "128,128,128"),
            ("Dark Gray", "64,64,64"),
            ("Orange",    "255,165,0"),
            ("Yellow",    "255,255,0"),
            ("Purple",    "128,0,128"),
            ("Cyan",      "0,255,255"),
            ("Teal",      "0,128,128"),
            ("Brown",     "139,69,19"),
            ("Gold",      "255,215,0"),
            ("Silver",    "192,192,192"),
            ("Turquoise", "64,224,208"),
            ("Magenta",   "255,0,255"),
            ("Olive",     "128,128,0"),
            ("Maroon",    "128,0,0"),
            ("Indigo",    "75,0,130"),
            ("Beige",     "245,245,220"),
            ("Lavender",  "230,230,250"),
        ]

        if self.width != 0:
            self.set_default_size(self.width, self.height)

        self.header = Gtk.HeaderBar()
        self.header.set_show_close_button(True)
        self.buttons = []
        self.modifier_buttons = {}
        self.row_buttons = []
        self.color_combobox = Gtk.ComboBoxText()
        self.set_titlebar(self.header)
        self.set_default_icon_name("preferences-desktop-keyboard")
        self.header.set_decoration_layout(":minimize,maximize,close")

        self.create_settings()

        grid = Gtk.Grid()
        grid.set_row_homogeneous(True)
        grid.set_column_homogeneous(True)
        grid.set_margin_start(3)
        grid.set_margin_end(3)
        grid.set_name("grid")
        self.add(grid)
        self.apply_css()
        self.device = uinput.Device(list(key_mapping.keys()))

        # TR Q layout — grid genişlik planı (SC=32):
        # 1 birim = yarım standart tuş genişliği.
        # row_offsets: her satırın başına eklenecek spacer birim sayısı.
        # Şu an tümü 0; stagger gerekirse buradan ayarlanır.
        rows = [
            ['"', "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "*", "-", "Backspace"],
            ["Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "Ğ", "Ü"],
            ["CapsLock", "A", "S", "D", "F", "G", "H", "J", "K", "L", "Ş", "İ", ",", "Home"],
            ["Shift_L", "><|", "Z", "X", "C", "V", "B", "N", "M", "Ö", "Ç", ".", "Shift_R"],
            ["Ctrl_L", "Super_L", "Alt_L", "Space", "Alt_R", "Super_R", "Ctrl_R"],
        ]
        self.row_offsets = [0, 0, 0, 0, 0]

        for row_index, keys in enumerate(rows):
            self.create_row(grid, row_index, keys)
        self.create_side_column(grid)
        self.update_label(False)

    # ------------------------------------------------------------------ settings bar

    def create_settings(self):
        self._add_header_button("☰", self.change_visibility)
        self._add_header_button("+", self.change_opacity, True)
        self._add_header_button("-", self.change_opacity, False)
        self._add_header_button(self.opacity)          # opacity label button (no callback)
        self.color_combobox.append_text("Change Background")
        self.color_combobox.set_active(0)
        self.color_combobox.connect("changed", self.change_color)
        self.color_combobox.set_name("combobox")
        self.header.add(self.color_combobox)
        for label, _ in self.colors:
            self.color_combobox.append_text(label)

    def _add_header_button(self, label, callback=None, cb_arg=None):
        button = Gtk.Button(label=label)
        button.set_name("headbar-button")
        if callback is not None:
            if cb_arg is not None:
                button.connect("clicked", callback, cb_arg)
            else:
                button.connect("clicked", callback)
        if label == self.opacity:
            self.opacity_btn = button
            self.opacity_btn.set_tooltip_text("opacity")
        self.header.add(button)
        self.buttons.append(button)

    def on_resize(self, widget, event):
        self.width, self.height = self.get_size()

    def change_visibility(self, widget=None):
        for button in self.buttons:
            if button.get_label() != "☰":
                button.set_visible(not button.get_visible())
        self.color_combobox.set_visible(not self.color_combobox.get_visible())

    def change_color(self, widget):
        label = self.color_combobox.get_active_text()
        for label_, color_ in self.colors:
            if label_ == label:
                self.bg_color = color_
                break
        light_colors = {"255,255,255", "0,255,0", "255,255,0", "245,245,220", "230,230,250", "255,215,0"}
        self.text_color = "#1C1C1C" if self.bg_color in light_colors else "white"
        self.apply_css()

    def change_opacity(self, widget, increase):
        op = float(self.opacity)
        op = min(1.0, op + 0.01) if increase else max(0.0, op - 0.01)
        self.opacity = str(round(op, 2))
        self.opacity_btn.set_label(self.opacity)
        self.apply_css()

    # ------------------------------------------------------------------ color helpers

    def _parse_bg(self):
        return [int(x.strip()) for x in self.bg_color.split(",")]

    def _darker_color(self, amount=40):
        try:
            r, g, b = self._parse_bg()
            return f"{max(0, r-amount)}, {max(0, g-amount)}, {max(0, b-amount)}"
        except Exception:
            return self.bg_color

    def _lighter_color(self, amount=30):
        try:
            r, g, b = self._parse_bg()
            return f"{min(255, r+amount)}, {min(255, g+amount)}, {min(255, b+amount)}"
        except Exception:
            return self.bg_color

    def _accent_color(self):
        """bg_color'dan accent rengi türetir (S=1, V=1 doygun ton)."""
        try:
            r, g, b = self._parse_bg()
        except Exception:
            return "#FFFFFF"
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        mx = max(r, g, b)
        sat = (mx - min(r, g, b)) / mx if mx > 0 else 0
        if sat < 0.25:
            return "#000000" if lum >= 128 else "#FFFFFF"
        mn = min(r, g, b)
        rng = mx - mn
        if mx == r:   h = ((g - b) / rng) % 6
        elif mx == g: h = (b - r) / rng + 2
        else:         h = (r - g) / rng + 4
        h /= 6.0
        i = int(h * 6)
        f = h * 6 - i
        palette = [
            (1, f, 0), (1-f, 1, 0), (0, 1, f),
            (0, 1-f, 1), (f, 0, 1), (1, 0, 1-f),
        ]
        ar, ag, ab = palette[i % 6]
        return f"#{int(ar*255):02X}{int(ag*255):02X}{int(ab*255):02X}"

    def _pressed_bg_color(self):
        """Lighter rengin HSV S'ini azaltır, V'sini artırır (basılı tuş feedback)."""
        try:
            r, g, b = self._parse_bg()
            r, g, b = min(255, r+30), min(255, g+30), min(255, b+30)
            mx = max(r, g, b) / 255.0
            mn = min(r, g, b) / 255.0
            if mx == 0:
                return "80, 80, 80"
            s = max(0.0, (mx - mn) / mx - 0.25)
            v = min(1.0, mx + 0.20)
            if s == 0:
                c = int(v * 255)
                return f"{c}, {c}, {c}"
            # hue from original lighter rgb
            rng_i = max(r, g, b) - min(r, g, b)
            if r >= g and r >= b:   h = ((g - b) / rng_i) % 6
            elif g >= r and g >= b: h = (b - r) / rng_i + 2
            else:                   h = (r - g) / rng_i + 4
            h /= 6.0
            i = int(h * 6) % 6
            f = h * 6 - int(h * 6)
            p = v * (1 - s)
            q = v * (1 - f * s)
            t = v * (1 - (1 - f) * s)
            rgb = [(v,t,p),(q,v,p),(p,v,t),(p,q,v),(t,p,v),(v,p,q)][i]
            return f"{int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)}"
        except Exception:
            return self._lighter_color()

    # ------------------------------------------------------------------ CSS

    def apply_css(self):
        provider = Gtk.CssProvider()
        css = f"""
        headerbar {{
            background-color: rgba({self.bg_color}, {self.opacity});
            border: 0px;
            box-shadow: none;
        }}
        headerbar button {{
            min-width: 20px;
            padding: 0px;
            border: 0px;
            margin: 0px;
        }}
        headerbar .titlebutton {{
            min-width: 30px;
            min-height: 20px;
        }}
        headerbar button label {{
            color: {self.text_color};
        }}
        #headbar-button, #combobox button.combo {{
            background-image: none;
        }}
        #toplevel {{
            background-color: rgba({self._darker_color()}, {self.opacity});
        }}
        #grid button label {{
            color: {self.text_color};
        }}
        #grid button {{
            border: none;
            background-image: none;
            background-color: rgba({self._lighter_color()}, {self.opacity});
            padding: 0px;
            margin: 2px;
        }}
        button {{
            background-color: transparent;
            color: {self.text_color};
        }}
        #grid button:hover {{
            border: 1px solid {self._accent_color()};
        }}
        #grid button.pressed,
        #grid button.pressed:hover {{
            border: 1px solid {self.text_color};
            background-color: rgba({self._pressed_bg_color()}, {self.opacity});
        }}
        tooltip {{
            color: white;
            padding: 5px;
        }}
        #combobox button.combo {{
            color: {self.text_color};
            padding: 2px;
        }}
        """
        try:
            provider.load_from_data(css.encode("utf-8"))
        except GLib.GError as e:
            print(f"CSS Error: {e.message}")
        Gtk.StyleContext.add_provider_for_screen(
            self.get_screen(), provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

    # ------------------------------------------------------------------ layout

    # Tuş genişlikleri (1 birim = 0.5 standart tuş); varsayılan 2 (kare tuş)
    _KEY_WIDTHS = {
        '"': 2, "*": 2, "-": 2,
        "Backspace": 4,
        "Tab": 4,
        "Ğ": 2, "Ü": 2,
        "CapsLock": 5,
        ",": 2,
        "Enter": 3, "Home": 3,
        "Shift_L": 4, "Shift_R": 3,
        "Space": 14,
        "Ctrl_L": 3, "Ctrl_R": 2,
        "Super_L": 3, "Super_R": 2,
        "Alt_L": 3, "Alt_R": 2,
    }
    _MODIFIER_SUFFIXES = ("Shift_R", "Shift_L", "Alt_L", "Alt_R", "Ctrl_L", "Ctrl_R", "Super_L", "Super_R")

    def create_row(self, grid, row_index, keys):
        col = 0
        offset = self.row_offsets[row_index]
        if offset > 0:
            spacer = Gtk.Label(label="")
            spacer.set_hexpand(False)
            grid.attach(spacer, 0, row_index, offset, 1)
            col = offset

        for key_label in keys:
            key_event = next((k for k, v in key_mapping.items() if v == key_label), None)
            if key_event is None:
                continue
            display = key_label[:-2] if key_label in self._MODIFIER_SUFFIXES else key_label
            button = Gtk.Button(label=display)
            button.connect("pressed", self.on_button_press, key_event)
            button.connect("released", self.on_button_release)
            button.connect("leave-notify-event", self.on_button_release)
            self.row_buttons.append(button)
            if key_event in self.modifiers:
                self.modifier_buttons[key_event] = button
            if key_event == uinput.KEY_CAPSLOCK:
                self.caps_lock_btn = button
            width = self._KEY_WIDTHS.get(key_label, 2)
            grid.attach(button, col, row_index, width, 1)
            col += width

    def update_label(self, show_symbols):
        # Satır 0: " 1 2 3 4 5 6 7 8 9 0 * -  (indeks 0-12)
        symbol_map = [
            (0,  '"', 'é'),
            (1,  '1', '!'),
            (2,  '2', "'"),
            (3,  '3', '^'),
            (4,  '4', '+'),
            (5,  '5', '%'),
            (6,  '6', '&'),
            (7,  '7', '/'),
            (8,  '8', '('),
            (9,  '9', ')'),
            (10, '0', '='),
            (11, '*', '?'),
            (12, '-', '_'),
        ]
        for pos, normal, shifted in symbol_map:
            self.row_buttons[pos].set_label(shifted if show_symbols else normal)

        use_upper = show_symbols ^ self.caps_lock_on
        letter_keys = set("QWERTYUIOPASDFGHJKLZXCVBNM")
        for btn in self.row_buttons:
            lbl = btn.get_label()
            if lbl.upper() in letter_keys:
                btn.set_label(lbl.upper() if use_upper else lbl.lower())
            elif lbl in _TR_LOWER or lbl in _TR_UPPER:
                btn.set_label(_TR_TO_UPPER[lbl] if use_upper else _TR_TO_LOWER.get(lbl, lbl))

    def create_side_column(self, grid):
        """Side column — sağ kenar=35.
        Del:   row=0, col=30, w=5
        Enter: row=1, col=28, w=7
        End:   row=2, col=32, w=3
        CMD:   row=3, col=29, w=2  ↑: row=3, col=31, w=2
        ←:     row=4, col=29, w=2  ↓: row=4, col=31, w=2  →: row=4, col=33, w=2
        PrtSc: row=3, col=33, w=2
        """
        # (row, col, label, key_event, width)
        side_keys = [
            (0, 30, "Del",   uinput.KEY_DELETE, 5),
            (1, 28, "Enter", uinput.KEY_ENTER,  7),
            (2, 32, "End",   uinput.KEY_END,    3),
            (3, 29, "CMD",   None,              2),
            (3, 31, "↑",     uinput.KEY_UP,     2),
            (4, 29, "←",     uinput.KEY_LEFT,   2),
            (4, 31, "↓",     uinput.KEY_DOWN,   2),
            (4, 33, "→",     uinput.KEY_RIGHT,  2),
            (3, 33, "PrtSc", None,              2),
        ]
        tooltips = {
            "Del": "Delete", "Enter": "Enter", "End": "End",
            "CMD": "custom_command (config)",
            "↑": "Up", "←": "Left", "↓": "Down", "→": "Right",
            "PrtSc": "Print Screen",
        }
        for row_i, col, label, key_event, width in side_keys:
            button = Gtk.Button(label=label)
            button.set_tooltip_text(tooltips[label])
            if label == "PrtSc":
                button.connect("pressed", self.on_prtsc_press)
            elif label == "CMD":
                button.connect("pressed", self.on_cmd_press)
            else:
                button.connect("pressed", self.on_button_press, key_event)
            button.connect("released", self.on_button_release)
            button.connect("leave-notify-event", self.on_button_release)
            grid.attach(button, col, row_i, width, 1)

    # ------------------------------------------------------------------ key events

    def on_combo_press(self, widget, mod_key, key_event):
        """Modifier toggle state'ini bozmadan mod+tuş combo gönderir."""
        self.device.emit(mod_key, 1)
        self.device.emit(key_event, 1)
        self.device.emit(key_event, 0)
        self.device.emit(mod_key, 0)

    def _show_config_dialog(self, title, key_name):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.format_secondary_text(
            f"Lütfen aşağıdaki dosyayı açıp\n"
            f"  {key_name} = <komutunuz>\n"
            f"satırını ekleyin:\n\n{self.CONFIG_FILE}"
        )
        dialog.run()
        dialog.destroy()

    def on_cmd_press(self, widget):
        if self.custom_command.strip():
            GLib.spawn_command_line_async(self.custom_command.strip())
        else:
            self._show_config_dialog("CMD komutu tanımlı değil", "custom_command")

    def on_prtsc_press(self, widget):
        if self.prtsc_command.strip():
            GLib.spawn_command_line_async(self.prtsc_command.strip())
        else:
            self._show_config_dialog("Print Screen komutu tanımlı değil", "prtsc_command")

    def update_modifier(self, key_event, value):
        self.modifiers[key_event] = value
        ctx = self.modifier_buttons[key_event].get_style_context()
        if value:
            ctx.add_class("pressed")
        else:
            ctx.remove_class("pressed")

    def on_button_press(self, widget, key_event):
        if key_event == uinput.KEY_CAPSLOCK:
            self.caps_lock_on = not self.caps_lock_on
            ctx = self.caps_lock_btn.get_style_context()
            if self.caps_lock_on:
                ctx.add_class("pressed")
            else:
                ctx.remove_class("pressed")
            shift_active = self.modifiers[uinput.KEY_LEFTSHIFT] or self.modifiers[uinput.KEY_RIGHTSHIFT]
            self.update_label(shift_active)
            self.device.emit(key_event, 1)
            self.device.emit(key_event, 0)
            return

        if key_event in self.modifiers:
            self.update_modifier(key_event, not self.modifiers[key_event])
            if self.modifiers[uinput.KEY_LEFTSHIFT] and self.modifiers[uinput.KEY_RIGHTSHIFT]:
                self.update_modifier(uinput.KEY_LEFTSHIFT, False)
                self.update_modifier(uinput.KEY_RIGHTSHIFT, False)
            self.update_label(
                self.modifiers[uinput.KEY_LEFTSHIFT] or self.modifiers[uinput.KEY_RIGHTSHIFT]
            )
            return

        self.emit_key(key_event)
        widget.get_style_context().add_class("pressed")
        self.delay_source = GLib.timeout_add(400, self.start_repeat, key_event)

    def on_button_release(self, widget, *args):
        if hasattr(self, "delay_source"):
            GLib.source_remove(self.delay_source)
            del self.delay_source
        if hasattr(self, "repeat_source"):
            GLib.source_remove(self.repeat_source)
            del self.repeat_source
        # Modifier ve CapsLock butonların pressed görünümünü koruyoruz
        is_modifier = widget in self.modifier_buttons.values()
        is_capslock = hasattr(self, "caps_lock_btn") and widget is self.caps_lock_btn
        if not is_modifier and not is_capslock:
            widget.get_style_context().remove_class("pressed")
        widget.set_state_flags(Gtk.StateFlags.NORMAL, True)

    def start_repeat(self, key_event):
        self.repeat_source = GLib.timeout_add(100, self.repeat_key, key_event)
        return False

    def repeat_key(self, key_event):
        self.emit_key(key_event)
        return True

    def emit_key(self, key_event):
        for mod_key, active in self.modifiers.items():
            if active:
                self.device.emit(mod_key, 1)
        self.device.emit(key_event, 1)
        self.device.emit(key_event, 0)
        for mod_key, active in self.modifiers.items():
            if active:
                self.device.emit(mod_key, 0)
                self.update_modifier(mod_key, False)
        self.update_label(False)

    # ------------------------------------------------------------------ config

    def read_settings(self):
        try:
            os.makedirs(self.CONFIG_DIR, exist_ok=True)
        except PermissionError:
            print("Warning: No permission to create the config directory.")
        try:
            if os.path.exists(self.CONFIG_FILE):
                self.config.read(self.CONFIG_FILE)
                self.bg_color      = self.config.get("DEFAULT", "bg_color")
                self.opacity       = self.config.get("DEFAULT", "opacity")
                self.text_color    = self.config.get("DEFAULT", "text_color",    fallback="white")
                self.width         = self.config.getint("DEFAULT", "width",      fallback=0)
                self.height        = self.config.getint("DEFAULT", "height",     fallback=0)
                self.prtsc_command = self.config.get("DEFAULT", "prtsc_command", fallback="")
                self.custom_command= self.config.get("DEFAULT", "custom_command",fallback="")
                print(f"rgba: {self.bg_color}, {self.opacity}")
        except configparser.Error as e:
            print(f"Warning: Could not read config file ({e}). Using defaults.")

    def save_settings(self):
        self.config["DEFAULT"] = {
            "bg_color":      self.bg_color,
            "opacity":       self.opacity,
            "text_color":    self.text_color,
            "width":         self.width,
            "height":        self.height,
            "prtsc_command": self.prtsc_command,
            "custom_command":self.custom_command,
        }
        try:
            with open(self.CONFIG_FILE, "w") as f:
                self.config.write(f)
        except (configparser.Error, IOError) as e:
            print(f"Warning: Could not write config file ({e}).")


if __name__ == "__main__":
    win = VirtualKeyboard()
    win.connect("configure-event", win.on_resize)
    win.connect("delete-event", lambda w, e: win.save_settings() or False)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    win.change_visibility()
    Gtk.main()
