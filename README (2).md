# My Paint Application
Name: John David I. Dalawis
Section: SE-3A

A desktop paint program built with **Python, Tkinter and Pillow**. It started from the
sample peach-themed Paint Application and was extended with the required features below.

## How to run

```
python -m pip install pillow
python paint_application.py
```

## Original features (kept from the sample code)
Freehand brush, color picker, eraser, line/rectangle/oval tools, clear, open image, save image.

## REQUIREMENTS COMPLETED

### 1. Bigger brush range (5 pts)
**What I changed:** the brush-size slider originally went from 1 to 30.

Original:
```python
size_slider = tk.Scale(toolbar, from_=1, to=30, ...)
```
Now:
```python
size_slider = tk.Scale(toolbar2, from_=1, to=100, ...)
```
**How it works:** `change_brush_size()` reads the slider and stores it in `brush_size`.
To make the saved image match the canvas, the brush draws on the Tkinter canvas *and* on the
Pillow image with the same width. Pillow's lines have flat ends, so I also draw a round dot
(`draw_dot()`) at every point; this matches Tkinter's round brush tip. The Pillow image is the
same size as the canvas (900 x 550), so the saved file looks like what you see.

### 2. Undo button (15 pts)
**How it works:** before every action (a freehand stroke, a shape, Clear, or Open) the function
`save_undo_state()` pushes a copy of the Pillow image onto a list called `undo_stack`.
Pressing **Undo** (or `Ctrl+Z`) calls `undo()`, which pops the last copy, makes it the current
image and redraws the canvas. Up to 30 steps are kept (`MAX_UNDO`).

### 3. Filled shapes (20 pts)
**How it works:** a **Fill shapes** checkbox (`fill_var`). When it is ticked, rectangles, ovals
and the new shapes are filled with the current color, both in the live preview
(`fill=current_color`) and in the saved image (`fill=current_color` in Pillow). When it is
unticked, only the outline is drawn.

### 4. Extra shape tools (20 pts)
I added **Triangle**, **Star** and **Hexagon** buttons (the task asked for one).
`shape_points()` calculates the corner points inside the box you drag:
- Triangle: 3 points, Hexagon: 6 points, Star: 10 points (alternating outer/inner radius).

While dragging, `preview_shape_drawing()` shows the shape with `canvas.create_polygon()`.
On mouse release, `finish_drawing()` draws it onto the Pillow image (`draw.polygon()` for the
fill and `draw.line()` for the outline), so it appears in the saved picture.

### 5. Confirm before clearing (20 pts)
**How it works:** `clear_canvas()` first calls `messagebox.askyesno()`, which shows a dialog
with **Yes** and **No**. If the user clicks **No**, nothing happens. If **Yes**, the canvas is
cleared (and this can still be undone).

### 6. Quick colors (20 pts)
Six one-click buttons: **black, red, blue, green, yellow, purple**. Each button calls
`set_color(name)`, which immediately changes `current_color` and the color of the
"Choose Color" button. If the eraser was active, it switches back to the brush.

## Extra improvements
- The active tool button stays highlighted so you can see what is selected.
- `Ctrl+Z` keyboard shortcut for Undo.
- Clicking once without dragging draws a dot.
- Toolbar split into three rows so everything fits in the window.

## UI customization
Peach palette kept in named constants at the top of the file (`PEACH_BG`, `PEACH_PANEL`,
`PEACH_BUTTON`, `PEACH_HOVER`, `TEXT_COLOR`) - change them to restyle the whole app.
The window is taller (1000x780) to fit the extra toolbar rows.

## Screenshot
![UI screenshot](screenshot.png)
