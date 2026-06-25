from __future__ import annotations

import math
import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

import pandas as pd


class ScientificToolGui(tk.Tk):
    """Reusable GUI shell for small scientific/data tools.

    This template intentionally contains no domain-specific calculation.
    Replace `compute_results` with your own model or data-processing function.
    """

    def __init__(self) -> None:
        super().__init__()
        self.output_dir = Path(__file__).resolve().parent / "outputs"
        self.results = pd.DataFrame()

        self.title("Scientific Tool GUI")
        self.geometry("1240x760")
        self.minsize(1020, 650)
        self._build_widgets()
        self.reset_plot("Press Run")

    def _build_widgets(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        controls = ttk.Frame(self, padding=12)
        controls.grid(row=0, column=0, sticky="nsw")
        controls.columnconfigure(0, weight=1)

        ttk.Label(controls, text="Tool Controls", font=("Segoe UI", 13, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.dataset_var = tk.StringVar(value="Example A")
        self.range_var = tk.StringVar(value="0:1:10")
        self.scale_var = tk.StringVar(value="1.0")

        row = 1
        row = self._labeled_combo(controls, row, "Dataset", self.dataset_var, ["Example A", "Example B"])
        row = self._labeled_entry(controls, row, "Scan values", self.range_var)
        row = self._labeled_entry(controls, row, "Scale", self.scale_var)

        ttk.Label(controls, text="Run does not save files.").grid(row=row, column=0, sticky="w", pady=(4, 8))
        row += 1

        for text, command in [
            ("Clear / Reset Axis", self.clear_view),
            ("Save Results", self.save_results),
            ("Open Output Folder", self.open_output_folder),
            ("Run", self.run),
        ]:
            ttk.Button(controls, text=text, command=command).grid(row=row, column=0, sticky="ew", pady=3)
            row += 1

        self.status = tk.Text(controls, width=38, height=10, wrap="word")
        self.status.grid(row=row, column=0, sticky="nsew", pady=(8, 0))
        controls.rowconfigure(row, weight=1)
        self.set_status("Ready.")

        right = ttk.Frame(self, padding=(0, 12, 12, 12))
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=2)
        right.rowconfigure(1, weight=1)

        self.canvas = tk.Canvas(right, background="white", highlightthickness=1, highlightbackground="#999")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", lambda _event: self.draw_plot())

        table_frame = ttk.Frame(right)
        table_frame.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        self.table = ttk.Treeview(table_frame, show="headings")
        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        xscroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.table.xview)
        self.table.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.table.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")

    def _labeled_combo(self, parent: ttk.Frame, row: int, label: str, variable: tk.StringVar, values: list[str]) -> int:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=(4, 1))
        ttk.Combobox(parent, textvariable=variable, values=values, state="readonly").grid(row=row + 1, column=0, sticky="ew", pady=(0, 4))
        return row + 2

    def _labeled_entry(self, parent: ttk.Frame, row: int, label: str, variable: tk.StringVar) -> int:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=(4, 1))
        ttk.Entry(parent, textvariable=variable).grid(row=row + 1, column=0, sticky="ew", pady=(0, 4))
        return row + 2

    def set_status(self, text: str) -> None:
        self.status.configure(state="normal")
        self.status.delete("1.0", "end")
        self.status.insert("1.0", text)
        self.status.configure(state="disabled")

    def run(self) -> None:
        self.set_status("Running...")

        def worker() -> None:
            try:
                data = self.compute_results()
                self.after(0, lambda: self.show_results(data))
            except Exception as exc:
                self.after(0, lambda: self.show_error(exc))

        threading.Thread(target=worker, daemon=True).start()

    def compute_results(self) -> pd.DataFrame:
        values = parse_scan_values(self.range_var.get())
        scale = float(self.scale_var.get())
        return pd.DataFrame({"x": values, "y": [scale * math.sin(v) for v in values]})

    def show_results(self, data: pd.DataFrame) -> None:
        self.results = data
        self.populate_table(data)
        self.draw_plot()
        self.set_status(f"Done.\nRows: {len(data)}\nResults are not saved yet.")

    def show_error(self, exc: Exception) -> None:
        self.set_status("Error.\n" + str(exc))
        messagebox.showerror("Scientific Tool GUI", str(exc))

    def populate_table(self, data: pd.DataFrame) -> None:
        self.table.delete(*self.table.get_children())
        self.table["columns"] = list(data.columns)
        for col in data.columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=120, anchor="w")
        for _, row in data.head(500).iterrows():
            self.table.insert("", "end", values=[f"{row[col]:.6g}" if isinstance(row[col], float) else str(row[col]) for col in data.columns])

    def reset_plot(self, title: str) -> None:
        self.canvas.delete("all")
        self.canvas.create_text(18, 18, text=title, anchor="nw", fill="#111")

    def draw_plot(self) -> None:
        self.canvas.delete("all")
        width = max(400, self.canvas.winfo_width())
        height = max(280, self.canvas.winfo_height())
        left, right, top, bottom = 74, 60, 42, 64
        x0, y0 = left, height - bottom
        x1, y1 = width - right, top
        self.canvas.create_rectangle(x0, y1, x1, y0, outline="#333")
        self.canvas.create_text(left, 16, text="Preview Plot", anchor="w", fill="#111")
        if self.results.empty:
            self.canvas.create_text(left + 10, top + 10, text="No data", anchor="nw", fill="#555")
            return

        xs = self.results["x"].to_numpy(dtype=float)
        ys = self.results["y"].to_numpy(dtype=float)
        xmin, xmax = float(xs.min()), float(xs.max())
        ymin, ymax = float(ys.min()), float(ys.max())
        if xmin == xmax:
            xmin -= 1
            xmax += 1
        if ymin == ymax:
            ymin -= 1
            ymax += 1
        points = []
        for x, y in zip(xs, ys):
            px = x0 + (x - xmin) / (xmax - xmin) * (x1 - x0)
            py = y0 - (y - ymin) / (ymax - ymin) * (y0 - y1)
            points.extend([px, py])
        if len(points) >= 4:
            self.canvas.create_line(*points, fill="#1f77b4", width=2)

    def clear_view(self) -> None:
        self.results = pd.DataFrame()
        self.populate_table(self.results)
        self.reset_plot("Cleared. Press Run")
        self.set_status("Cleared.")

    def save_results(self) -> None:
        if self.results.empty:
            messagebox.showinfo("Scientific Tool GUI", "No current results to save.")
            return
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output = self.output_dir / "results.csv"
        self.results.to_csv(output, index=False)
        self.set_status(f"Saved current results.\nOutput: {output}")

    def open_output_folder(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        os.startfile(self.output_dir)


def parse_scan_values(text: str) -> list[float]:
    values: list[float] = []
    for token in text.replace(",", " ").split():
        parts = [float(part) for part in token.split(":")]
        if len(parts) == 1:
            values.append(parts[0])
        elif len(parts) == 2:
            start, stop = parts
            step = 1.0 if stop >= start else -1.0
            values.extend(inclusive_range(start, stop, step))
        elif len(parts) == 3:
            values.extend(inclusive_range(parts[0], parts[2], parts[1]))
        else:
            raise ValueError(f"Could not parse scan token: {token}")
    return values


def inclusive_range(start: float, stop: float, step: float) -> list[float]:
    if step == 0:
        raise ValueError("Step cannot be zero.")
    values = []
    current = start
    if step > 0:
        while current <= stop + 1e-12:
            values.append(current)
            current += step
    else:
        while current >= stop - 1e-12:
            values.append(current)
            current += step
    return values


def main() -> int:
    app = ScientificToolGui()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
