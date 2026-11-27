import math
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk

# 1. PEACH COLOR PALETTE AND FONT
PEACH_BG = "#FFE8D6"       # window background
PEACH_PANEL = "#FFD7BA"    # toolbar background
PEACH_BUTTON = "#FFBE98"   # button color
PEACH_HOVER = "#FFA877"    # button color while it is pressed / active tool
TEXT_COLOR = "#5C3D2E"     # text color
FONT_MAIN = ("Arial", 10, "bold")

# 2. MAIN WINDOW AND CANVAS SETTINGS
CANVAS_WIDTH = 900
CANVAS_HEIGHT = 550
MAX_UNDO = 30

root = tk.Tk()
root.title("My Paint Application")
root.geometry("1000x780")
root.configure(bg=PEACH_BG)

canvas_frame = tk.Frame(root, bg=PEACH_BUTTON, padx=4, pady=4)
canvas_frame.pack(padx=20, pady=15)

canvas = tk.Canvas(canvas_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT,
                   bg="white", cursor="cross", highlightthickness=0)
canvas.pack()

# Pillow image stores the drawing so it can be saved.
image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), "white")
draw = ImageDraw.Draw(image)
canvas_image = None

# 3. DRAWING SETTINGS
current_color = "black"
brush_size = 5
tool = "brush"
start_x = start_y = None
last_x = last_y = None
preview_shape = None
undo_stack = []                      # earlier versions of the image
fill_var = tk.BooleanVar(value=False)  # "Fill shapes" checkbox
tool_buttons = {}                    # tool name -> button (for highlighting)
SHAPE_TOOLS = ("line", "rectangle", "oval", "triangle", "star", "hexagon")


# 4. UNDO SUPPORT
def save_undo_state():
    """Store a copy of the image BEFORE a new action changes it."""
    undo_stack.append(image.copy())
    if len(undo_stack) > MAX_UNDO:
        undo_stack.pop(0)

def undo():
    """Remove the most recent drawing action (stroke, shape, clear, open)."""
    global image, draw, preview_shape
    if not undo_stack:
        return
    image = undo_stack.pop()
    draw = ImageDraw.Draw(image)
    preview_shape = None
    refresh_canvas()


# 5. TOOL FUNCTIONS
def set_color(color):
    """Set the drawing color (used by the quick-color buttons)."""
    global current_color, tool
    current_color = color
    if tool == "eraser":
        set_tool("brush")
    color_button.config(bg=current_color)

def choose_color():
    """Open the color chooser and update the drawing color."""
    selected = colorchooser.askcolor(title="Choose a color")
    if selected[1] is not None:
        set_color(selected[1])

def set_tool(selected_tool):
    """Change the active drawing tool and highlight its button."""
    global tool
    tool = selected_tool
    for name, button in tool_buttons.items():
        button.config(bg=PEACH_HOVER if name == tool else PEACH_BUTTON)

def change_brush_size(value):
    """Update the brush size using the slider (1 - 100)."""
    global brush_size
    brush_size = int(float(value))


# 6. SHAPE GEOMETRY
def shape_points(name, x0, y0, x1, y1):
    """Return the corner points of triangle / star / hexagon in the dragged box."""
    left, right = min(x0, x1), max(x0, x1)
    top, bottom = min(y0, y1), max(y0, y1)
    cx, cy = (left + right) / 2, (top + bottom) / 2
    rx, ry = (right - left) / 2, (bottom - top) / 2

    if name == "triangle":
        return [(cx, top), (right, bottom), (left, bottom)]
    if name == "hexagon":
        return [(cx + rx * math.cos(math.radians(a)),
                 cy + ry * math.sin(math.radians(a)))
                for a in range(0, 360, 60)]
    if name == "star":
        points = []
        for i in range(10):
            angle = math.radians(-90 + i * 36)
            r = 1.0 if i % 2 == 0 else 0.4   # outer / inner radius
            points.append((cx + rx * r * math.cos(angle),
                           cy + ry * r * math.sin(angle)))
        return points
    return []

def flat(points):
    """[(x, y), ...] -> [x, y, x, y, ...] for Tkinter."""
    return [value for point in points for value in point]


# 7. FREEHAND DRAWING
def draw_dot(x, y, color):
    """Round brush tip on the Pillow image (so it matches the canvas)."""
    r = brush_size / 2
    draw.ellipse((x - r, y - r, x + r, y + r), fill=color)

def start_drawing(event):
    """Remember the mouse position when drawing starts."""
    global last_x, last_y, start_x, start_y
    last_x, last_y = event.x, event.y
    start_x, start_y = event.x, event.y
    save_undo_state()                      # so Undo can bring this back
    if tool in ("brush", "eraser"):
        color = "white" if tool == "eraser" else current_color
        r = brush_size / 2
        canvas.create_oval(event.x - r, event.y - r, event.x + r, event.y + r,
                           fill=color, outline=color)
        draw_dot(event.x, event.y, color)

def draw_motion(event):
    """Draw while the left mouse button is held."""
    global last_x, last_y
    if tool in ("brush", "eraser"):
        color = "white" if tool == "eraser" else current_color
        canvas.create_line(last_x, last_y, event.x, event.y,
                           fill=color, width=brush_size,
                           capstyle=tk.ROUND, joinstyle=tk.ROUND)
        draw.line((last_x, last_y, event.x, event.y),
                  fill=color, width=brush_size)
        draw_dot(event.x, event.y, color)   # round joint
        last_x, last_y = event.x, event.y
    else:
        preview_shape_drawing(event)


# 8. SHAPE DRAWING
def preview_shape_drawing(event):
    """Show a temporary shape while the mouse is dragged."""
    global preview_shape
    if preview_shape is not None:
        canvas.delete(preview_shape)
    preview_shape = None
    fill = current_color if fill_var.get() else ""

    if tool == "line":
        preview_shape = canvas.create_line(
            start_x, start_y, event.x, event.y,
            fill=current_color, width=brush_size)
    elif tool == "rectangle":
        preview_shape = canvas.create_rectangle(
            start_x, start_y, event.x, event.y,
            outline=current_color, fill=fill, width=brush_size)
    elif tool == "oval":
        preview_shape = canvas.create_oval(
            start_x, start_y, event.x, event.y,
            outline=current_color, fill=fill, width=brush_size)
    elif tool in ("triangle", "star", "hexagon"):
        pts = shape_points(tool, start_x, start_y, event.x, event.y)
        preview_shape = canvas.create_polygon(
            flat(pts), outline=current_color, fill=fill,
            width=brush_size, joinstyle=tk.ROUND)

def finish_drawing(event):
    """Store the selected shape in the Pillow image."""
    global preview_shape
    if start_x is None:
        return
    x0, y0 = min(start_x, event.x), min(start_y, event.y)
    x1, y1 = max(start_x, event.x), max(start_y, event.y)
    fill = current_color if fill_var.get() else None

    if tool == "line":
        draw.line((start_x, start_y, event.x, event.y),
                  fill=current_color, width=brush_size)
    elif tool == "rectangle":
        draw.rectangle((x0, y0, x1, y1), outline=current_color,
                       fill=fill, width=brush_size)
    elif tool == "oval":
        draw.ellipse((x0, y0, x1, y1), outline=current_color,
                     fill=fill, width=brush_size)
    elif tool in ("triangle", "star", "hexagon"):
        pts = shape_points(tool, start_x, start_y, event.x, event.y)
        if fill:
            draw.polygon(pts, fill=fill)
        draw.line(pts + [pts[0]], fill=current_color,
                  width=brush_size, joint="curve")
    if tool in SHAPE_TOOLS:
        preview_shape = None
        refresh_canvas()


# 9. CANVAS MANAGEMENT
def refresh_canvas():
    """Display the current Pillow image on the Tkinter canvas."""
    global canvas_image
    canvas.delete("all")
    canvas_image = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, anchor="nw", image=canvas_image)

def clear_canvas():
    """Ask first, then replace the drawing with a blank white image."""
    global image, draw, preview_shape
    answer = messagebox.askyesno("Clear canvas",
                                 "Do you really want to clear the canvas?")
    if not answer:                         # user clicked "No"
        return
    save_undo_state()                      # clearing can be undone
    image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), "white")
    draw = ImageDraw.Draw(image)
    preview_shape = None
    refresh_canvas()


# 10. OPEN AND SAVE IMAGE
def open_image():
    """Open an image and display it on the canvas."""
    global image, draw
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
    if file_path:
        try:
            opened_image = Image.open(file_path).convert("RGB")
            opened_image = opened_image.resize((CANVAS_WIDTH, CANVAS_HEIGHT))
            save_undo_state()
            image = opened_image
            draw = ImageDraw.Draw(image)
            refresh_canvas()
        except Exception as error:
            messagebox.showerror("Error", f"Could not open image:\n{error}")

def save_image():
    """Save the current drawing as an image file."""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png"),
                   ("JPEG Image", "*.jpg"),
                   ("Bitmap Image", "*.bmp")])
    if file_path:
        try:
            image.save(file_path)
            messagebox.showinfo("Saved", "Your drawing has been saved!")
        except Exception as error:
            messagebox.showerror("Error", f"Could not save image:\n{error}")


# 11. TOOLBAR
def make_button(parent, text, command):
    """Create one peach button so we do not repeat the styling."""
    return tk.Button(parent, text=text, command=command,
                     bg=PEACH_BUTTON, fg=TEXT_COLOR,
                     activebackground=PEACH_HOVER, activeforeground=TEXT_COLOR,
                     font=FONT_MAIN, relief="flat", padx=10, pady=4,
                     cursor="hand2")

def make_tool_button(parent, text, tool_name):
    """A tool button that stays highlighted while its tool is active."""
    button = make_button(parent, text, lambda: set_tool(tool_name))
    button.pack(side="left", padx=3)
    tool_buttons[tool_name] = button

# Row 1: tools
toolbar = tk.Frame(root, bg=PEACH_PANEL, padx=10, pady=6)
toolbar.pack(pady=(5, 0))

color_button = make_button(toolbar, "Choose Color", choose_color)
color_button.pack(side="left", padx=3)
make_tool_button(toolbar, "Brush", "brush")
make_tool_button(toolbar, "Eraser", "eraser")
make_tool_button(toolbar, "Line", "line")
make_tool_button(toolbar, "Rectangle", "rectangle")
make_tool_button(toolbar, "Oval", "oval")
make_tool_button(toolbar, "Triangle", "triangle")
make_tool_button(toolbar, "Star", "star")
make_tool_button(toolbar, "Hexagon", "hexagon")

# Row 2: options and actions
toolbar2 = tk.Frame(root, bg=PEACH_PANEL, padx=10, pady=6)
toolbar2.pack(pady=(0, 5))

tk.Label(toolbar2, text="Brush Size:", bg=PEACH_PANEL,
         fg=TEXT_COLOR, font=FONT_MAIN).pack(side="left", padx=(0, 3))
size_slider = tk.Scale(toolbar2, from_=1, to=100, orient="horizontal",
                       command=change_brush_size, length=180,
                       bg=PEACH_PANEL, fg=TEXT_COLOR,
                       troughcolor=PEACH_BUTTON, highlightthickness=0)
size_slider.set(5)
size_slider.pack(side="left", padx=3)

tk.Checkbutton(toolbar2, text="Fill shapes", variable=fill_var,
               bg=PEACH_PANEL, fg=TEXT_COLOR, font=FONT_MAIN,
               activebackground=PEACH_PANEL, activeforeground=TEXT_COLOR,
               selectcolor=PEACH_BUTTON).pack(side="left", padx=8)

make_button(toolbar2, "Undo", undo).pack(side="left", padx=3)
make_button(toolbar2, "Clear", clear_canvas).pack(side="left", padx=3)
make_button(toolbar2, "Open", open_image).pack(side="left", padx=3)
make_button(toolbar2, "Save", save_image).pack(side="left", padx=3)

# Row 3: six quick colors
quick_bar = tk.Frame(root, bg=PEACH_PANEL, padx=10, pady=6)
quick_bar.pack(pady=5)
tk.Label(quick_bar, text="Quick Colors:", bg=PEACH_PANEL,
         fg=TEXT_COLOR, font=FONT_MAIN).pack(side="left", padx=(0, 6))
for name in ("black", "red", "blue", "green", "yellow", "purple"):
    tk.Button(quick_bar, bg=name, activebackground=name, width=4, height=1,
              relief="raised", cursor="hand2",
              command=lambda c=name: set_color(c)).pack(side="left", padx=4)

# 12. CONNECT MOUSE / KEYBOARD EVENTS
canvas.bind("<Button-1>", start_drawing)
canvas.bind("<B1-Motion>", draw_motion)
canvas.bind("<ButtonRelease-1>", finish_drawing)
root.bind("<Control-z>", lambda event: undo())

set_tool("brush")

# 13. RUN THE APPLICATION
root.mainloop()
