import tkinter as tk
from tkinter import messagebox

import win32print
import win32ui
from PIL import Image, ImageDraw, ImageFont, ImageWin


WIDTH = 576
MARGIN = 20
FONT_PATH = "C:/Windows/Fonts/consola.ttf"
TITLE_FONT_SIZE = 54
BODY_FONT_SIZE = 30
META_FONT_SIZE = 28
LINE_SPACING = 8
BLOCK_SPACING = 20
BOTTOM_PADDING = 80
FEED_MARK_SIZE = 2

INK_DARK = "#171421"
INK_PANEL = "#241d35"
INK_PANEL_ALT = "#302542"
INK_GREEN = "#b6ff00"
INK_PINK = "#ff2bd6"
INK_ORANGE = "#ff8a00"
INK_CYAN = "#11e7ff"
INK_TEXT = "#f7f3ff"
INK_MUTED = "#b8adc9"
INK_FIELD = "#0f0d18"
INK_BORDER = "#57496d"

CATEGORY_OPTIONS = [
    ("[!]", "Tarkea"),
    ("[i]", "Info"),
    ("[*]", "Idea"),
    ("[ ]", "Tehtava"),
    ("[OK]", "Valmis"),
]


def draw_ink_splat(canvas, x, y, color, scale=1):
    canvas.create_oval(
        x - 28 * scale,
        y - 20 * scale,
        x + 30 * scale,
        y + 24 * scale,
        fill=color,
        outline=color,
    )
    canvas.create_oval(
        x - 45 * scale,
        y - 8 * scale,
        x - 15 * scale,
        y + 22 * scale,
        fill=color,
        outline=color,
    )
    canvas.create_oval(
        x + 10 * scale,
        y - 38 * scale,
        x + 38 * scale,
        y - 8 * scale,
        fill=color,
        outline=color,
    )
    canvas.create_oval(
        x + 28 * scale,
        y + 16 * scale,
        x + 48 * scale,
        y + 36 * scale,
        fill=color,
        outline=color,
    )
    canvas.create_oval(
        x - 10 * scale,
        y + 26 * scale,
        x + 8 * scale,
        y + 44 * scale,
        fill=color,
        outline=color,
    )


def style_entry(widget):
    widget.configure(
        bg=INK_FIELD,
        fg=INK_TEXT,
        insertbackground=INK_GREEN,
        relief=tk.FLAT,
        highlightthickness=2,
        highlightbackground=INK_BORDER,
        highlightcolor=INK_GREEN,
    )


def style_spinbox(widget):
    widget.configure(
        bg=INK_FIELD,
        fg=INK_TEXT,
        buttonbackground=INK_PANEL_ALT,
        insertbackground=INK_GREEN,
        relief=tk.FLAT,
        highlightthickness=2,
        highlightbackground=INK_BORDER,
        highlightcolor=INK_GREEN,
    )


def style_label(widget, muted=False):
    widget.configure(
        bg=widget.master.cget("bg"),
        fg=INK_MUTED if muted else INK_TEXT,
        font=("Consolas", 10, "bold"),
    )


def style_checkbutton(widget):
    widget.configure(
        bg=INK_DARK,
        fg=INK_TEXT,
        activebackground=INK_DARK,
        activeforeground=INK_GREEN,
        selectcolor=INK_PANEL_ALT,
        font=("Consolas", 10, "bold"),
        relief=tk.FLAT,
    )


def load_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except OSError:
        return ImageFont.load_default()


def text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def wrap_line(draw, line, font, max_width):
    if not line:
        return [""]

    words = line.split(" ")
    lines = []
    current = ""

    for word in words:
        candidate = word if not current else f"{current} {word}"
        width, _ = text_size(draw, candidate, font)

        if width <= max_width:
            current = candidate
            continue

        if current:
            lines.append(current)
            current = word
        else:
            current = word

        while text_size(draw, current, font)[0] > max_width and len(current) > 1:
            piece = current
            while text_size(draw, piece, font)[0] > max_width and len(piece) > 1:
                piece = piece[:-1]
            lines.append(piece)
            current = current[len(piece):]

    if current:
        lines.append(current)

    return lines


def wrap_text(draw, text, font, max_width):
    wrapped = []

    for raw_line in text.splitlines():
        wrapped.extend(wrap_line(draw, raw_line, font, max_width))

    return wrapped or [""]


def draw_wrapped_text(draw, text, font, y, max_width, x=MARGIN):
    _, line_height = text_size(draw, "Ag", font)
    lines = wrap_text(draw, text, font, max_width)

    for line in lines:
        draw.text((x, y), line, font=font, fill=0)
        y += line_height + LINE_SPACING

    return y


def draw_separator(draw, y):
    draw.line((MARGIN, y, WIDTH - MARGIN, y), fill=0, width=2)
    return y + BLOCK_SPACING


def make_receipt_image(receipt):
    title_font = load_font(receipt.get("title_size", TITLE_FONT_SIZE))
    body_font = load_font(receipt.get("body_size", BODY_FONT_SIZE))
    meta_font = load_font(receipt.get("meta_size", META_FONT_SIZE))

    img = Image.new("L", (WIDTH, 3000), 255)
    draw = ImageDraw.Draw(img)
    max_width = WIDTH - 2 * MARGIN
    y = MARGIN

    if receipt["use_category"]:
        category_text = f'{receipt["category_icon"]} {receipt["category_name"]}'
        y = draw_wrapped_text(draw, category_text, meta_font, y, max_width)
        y += 4

    if receipt["use_title"]:
        if y > MARGIN:
            y = draw_separator(draw, y)
        y = draw_wrapped_text(draw, receipt["title"], title_font, y, max_width)
        y += BLOCK_SPACING

    if receipt["use_body"]:
        y = draw_wrapped_text(draw, receipt["body"], body_font, y, max_width)
        y += BLOCK_SPACING

    if receipt["use_deadline"]:
        if y > MARGIN:
            y = draw_separator(draw, y)
        y = draw_wrapped_text(draw, f'Deadline: {receipt["deadline"]}', meta_font, y, max_width)
        y += BLOCK_SPACING

    bottom_padding = max(0, receipt.get("bottom_padding", BOTTOM_PADDING))
    final_height = max(y + MARGIN + bottom_padding, 120)

    if bottom_padding > 0:
        mark_x = WIDTH - MARGIN
        mark_y = final_height - MARGIN
        draw.rectangle(
            (
                mark_x,
                mark_y,
                mark_x + FEED_MARK_SIZE,
                mark_y + FEED_MARK_SIZE,
            ),
            fill=0,
        )

    return img.crop((0, 0, WIDTH, final_height))


def print_receipt(receipt):
    printer_name = win32print.GetDefaultPrinter()
    hdc = win32ui.CreateDC()
    hdc.CreatePrinterDC(printer_name)

    try:
        img = make_receipt_image(receipt)
        dib = ImageWin.Dib(img)

        hdc.StartDoc("Receipt")
        hdc.StartPage()
        dib.draw(hdc.GetHandleOutput(), (0, 0, img.width, img.height))
        hdc.EndPage()
        hdc.EndDoc()
    finally:
        hdc.DeleteDC()


def set_widget_state(widget, enabled):
    state = tk.NORMAL if enabled else tk.DISABLED
    widget.configure(state=state)


def main():
    root = tk.Tk()
    root.title("Kuittitulostin")
    root.geometry("680x780")
    root.minsize(560, 680)
    root.configure(bg=INK_DARK)

    header = tk.Canvas(root, height=118, bg=INK_DARK, highlightthickness=0)
    header.pack(fill=tk.X)
    draw_ink_splat(header, 70, 50, INK_GREEN, 1.15)
    draw_ink_splat(header, 590, 52, INK_PINK, 1.05)
    draw_ink_splat(header, 470, 88, INK_CYAN, 0.45)
    header.create_text(
        28,
        38,
        anchor="w",
        text="INK RECEIPT",
        fill=INK_TEXT,
        font=("Consolas", 28, "bold"),
    )
    header.create_text(
        31,
        74,
        anchor="w",
        text="Kuittitulostin",
        fill=INK_GREEN,
        font=("Consolas", 14, "bold"),
    )
    header.create_line(0, 112, 680, 112, fill=INK_PINK, width=4)
    header.create_line(0, 116, 680, 116, fill=INK_GREEN, width=3)

    frame = tk.Frame(root, padx=18, pady=18, bg=INK_DARK)
    frame.pack(fill=tk.BOTH, expand=True)
    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(2, weight=1)

    use_title = tk.BooleanVar(value=True)
    use_body = tk.BooleanVar(value=True)
    use_deadline = tk.BooleanVar(value=False)
    use_category = tk.BooleanVar(value=True)
    title_size = tk.IntVar(value=TITLE_FONT_SIZE)
    body_size = tk.IntVar(value=BODY_FONT_SIZE)
    meta_size = tk.IntVar(value=META_FONT_SIZE)
    bottom_padding = tk.IntVar(value=BOTTOM_PADDING)
    category_var = tk.StringVar(value=f"{CATEGORY_OPTIONS[0][0]} {CATEGORY_OPTIONS[0][1]}")
    status_var = tk.StringVar()

    title_entry = tk.Entry(frame, font=("Consolas", 12))
    body_text = tk.Text(frame, wrap=tk.WORD, font=("Consolas", 12), height=10)
    deadline_entry = tk.Entry(frame, font=("Consolas", 12))
    category_menu = tk.OptionMenu(
        frame,
        category_var,
        *[f"{icon} {name}" for icon, name in CATEGORY_OPTIONS],
    )

    style_entry(title_entry)
    style_entry(deadline_entry)
    body_text.configure(
        bg=INK_FIELD,
        fg=INK_TEXT,
        insertbackground=INK_GREEN,
        relief=tk.FLAT,
        highlightthickness=2,
        highlightbackground=INK_BORDER,
        highlightcolor=INK_GREEN,
        padx=10,
        pady=10,
    )
    category_menu.configure(
        bg=INK_PANEL_ALT,
        fg=INK_TEXT,
        activebackground=INK_PINK,
        activeforeground=INK_TEXT,
        relief=tk.FLAT,
        highlightthickness=2,
        highlightbackground=INK_BORDER,
        font=("Consolas", 10, "bold"),
    )
    category_menu["menu"].configure(
        bg=INK_PANEL_ALT,
        fg=INK_TEXT,
        activebackground=INK_GREEN,
        activeforeground=INK_DARK,
        font=("Consolas", 10),
    )

    title_entry.insert(0, "Otsikko")
    body_text.insert("1.0", "Kirjoita leipateksti tahan.")
    deadline_entry.insert(0, "pp.kk.vvvv klo 12:00")

    title_toggle = tk.Checkbutton(
        frame,
        text="Otsikko",
        variable=use_title,
        command=lambda: set_widget_state(title_entry, use_title.get()),
    )
    body_toggle = tk.Checkbutton(
        frame,
        text="Leipateksti",
        variable=use_body,
        command=lambda: set_widget_state(body_text, use_body.get()),
    )
    deadline_toggle = tk.Checkbutton(
        frame,
        text="Deadline",
        variable=use_deadline,
        command=lambda: set_widget_state(deadline_entry, use_deadline.get()),
    )
    category_toggle = tk.Checkbutton(
        frame,
        text="Kategoria",
        variable=use_category,
        command=lambda: set_widget_state(category_menu, use_category.get()),
    )

    for toggle in (title_toggle, category_toggle, body_toggle, deadline_toggle):
        style_checkbutton(toggle)

    title_toggle.grid(row=0, column=0, sticky="w", pady=(0, 8))
    title_entry.grid(row=0, column=1, sticky="ew", pady=(0, 8))

    category_toggle.grid(row=1, column=0, sticky="w", pady=(0, 8))
    category_menu.grid(row=1, column=1, sticky="ew", pady=(0, 8))

    body_toggle.grid(row=2, column=0, sticky="nw", pady=(0, 8))
    body_text.grid(row=2, column=1, sticky="nsew", pady=(0, 8))

    deadline_toggle.grid(row=3, column=0, sticky="w", pady=(0, 8))
    deadline_entry.grid(row=3, column=1, sticky="ew", pady=(0, 8))

    sizes_frame = tk.Frame(frame, bg=INK_PANEL, padx=12, pady=10)
    sizes_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(4, 8))

    tk.Label(sizes_frame, text="Tekstikoot").grid(row=0, column=0, sticky="w", padx=(0, 12))

    tk.Label(sizes_frame, text="Otsikko").grid(row=0, column=1, sticky="w")
    title_size_spinbox = tk.Spinbox(
        sizes_frame,
        from_=24,
        to=96,
        width=5,
        textvariable=title_size,
    )
    style_spinbox(title_size_spinbox)
    title_size_spinbox.grid(row=0, column=2, sticky="w", padx=(4, 14))

    tk.Label(sizes_frame, text="Leipateksti").grid(row=0, column=3, sticky="w")
    body_size_spinbox = tk.Spinbox(
        sizes_frame,
        from_=18,
        to=72,
        width=5,
        textvariable=body_size,
    )
    style_spinbox(body_size_spinbox)
    body_size_spinbox.grid(row=0, column=4, sticky="w", padx=(4, 14))

    tk.Label(sizes_frame, text="Muut").grid(row=0, column=5, sticky="w")
    meta_size_spinbox = tk.Spinbox(
        sizes_frame,
        from_=18,
        to=72,
        width=5,
        textvariable=meta_size,
    )
    style_spinbox(meta_size_spinbox)
    meta_size_spinbox.grid(row=0, column=6, sticky="w", padx=(4, 0))

    for index, child in enumerate(sizes_frame.winfo_children()):
        if isinstance(child, tk.Label):
            style_label(child, muted=index != 0)
    sizes_frame.winfo_children()[0].configure(fg=INK_GREEN)

    spacing_frame = tk.Frame(frame, bg=INK_PANEL, padx=12, pady=10)
    spacing_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 8))

    tk.Label(spacing_frame, text="Tyhjaa loppuun").grid(
        row=0,
        column=0,
        sticky="w",
        padx=(0, 12),
    )
    bottom_padding_spinbox = tk.Spinbox(
        spacing_frame,
        from_=0,
        to=400,
        increment=10,
        width=5,
        textvariable=bottom_padding,
    )
    style_spinbox(bottom_padding_spinbox)
    bottom_padding_spinbox.grid(row=0, column=1, sticky="w")
    tk.Label(spacing_frame, text="px").grid(row=0, column=2, sticky="w", padx=(4, 0))

    for index, child in enumerate(spacing_frame.winfo_children()):
        if isinstance(child, tk.Label):
            style_label(child, muted=index != 0)
    spacing_frame.winfo_children()[0].configure(fg=INK_PINK)

    set_widget_state(deadline_entry, use_deadline.get())

    def read_category():
        selected = category_var.get()
        for icon, name in CATEGORY_OPTIONS:
            if selected == f"{icon} {name}":
                return icon, name
        return CATEGORY_OPTIONS[0]

    def read_font_sizes():
        try:
            return title_size.get(), body_size.get(), meta_size.get()
        except tk.TclError:
            messagebox.showwarning(
                "Virheellinen tekstikoko",
                "Tekstikokojen taytyy olla numeroita.",
            )
            return None

    def read_bottom_padding():
        try:
            return bottom_padding.get()
        except tk.TclError:
            messagebox.showwarning(
                "Virheellinen tyhja tila",
                "Lopun tyhjan tilan taytyy olla numero.",
            )
            return None

    def build_receipt():
        category_icon, category_name = read_category()
        font_sizes = read_font_sizes()
        if font_sizes is None:
            return None
        extra_bottom_space = read_bottom_padding()
        if extra_bottom_space is None:
            return None

        title_font_size, body_font_size, meta_font_size = font_sizes
        receipt = {
            "use_title": use_title.get(),
            "title": title_entry.get().strip(),
            "use_body": use_body.get(),
            "body": body_text.get("1.0", tk.END).strip(),
            "use_deadline": use_deadline.get(),
            "deadline": deadline_entry.get().strip(),
            "use_category": use_category.get(),
            "category_icon": category_icon,
            "category_name": category_name,
            "title_size": title_font_size,
            "body_size": body_font_size,
            "meta_size": meta_font_size,
            "bottom_padding": extra_bottom_space,
        }

        missing = []
        if receipt["use_title"] and not receipt["title"]:
            missing.append("otsikko")
        if receipt["use_body"] and not receipt["body"]:
            missing.append("leipateksti")
        if receipt["use_deadline"] and not receipt["deadline"]:
            missing.append("deadline")

        if missing:
            messagebox.showwarning(
                "Tietoja puuttuu",
                "Tayta valitut kentat: " + ", ".join(missing),
            )
            return None

        if not any(
            [
                receipt["use_title"],
                receipt["use_body"],
                receipt["use_deadline"],
                receipt["use_category"],
            ]
        ):
            messagebox.showwarning("Ei tulostettavaa", "Valitse ainakin yksi tulostettava kohta.")
            return None

        return receipt

    def handle_print():
        receipt = build_receipt()
        if receipt is None:
            return

        try:
            printer_name = win32print.GetDefaultPrinter()
            print_receipt(receipt)
        except Exception as exc:
            status_var.set("Tulostus epaonnistui.")
            messagebox.showerror("Tulostus epaonnistui", str(exc))
            return

        status_var.set(f"Tulostettu: {printer_name}")

    controls = tk.Frame(frame, bg=INK_DARK)
    controls.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(10, 0))
    controls.columnconfigure(0, weight=1)

    status_label = tk.Label(controls, textvariable=status_var, anchor="w")
    status_label.configure(
        bg=INK_DARK,
        fg=INK_MUTED,
        font=("Consolas", 10, "bold"),
    )
    status_label.grid(row=0, column=0, sticky="ew")

    print_button = tk.Button(controls, text="Tulosta", command=handle_print, width=14)
    print_button.configure(
        bg=INK_GREEN,
        fg=INK_DARK,
        activebackground=INK_PINK,
        activeforeground=INK_TEXT,
        relief=tk.FLAT,
        font=("Consolas", 12, "bold"),
        padx=12,
        pady=8,
    )
    print_button.grid(row=0, column=1, sticky="e")

    title_entry.focus_set()
    root.mainloop()


if __name__ == "__main__":
    main()
