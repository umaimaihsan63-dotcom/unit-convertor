# app.py
# Unit Converter (ChemE-friendly) for Hugging Face Spaces (Gradio)
# No external APIs or keys required.

import math
import gradio as gr

# ---------- Conversion tables (to SI base units) ----------
to_base = {
    "Length": {  # base: meter (m)
        "mm": 1e-3, "cm": 1e-2, "m": 1.0, "km": 1e3,
        "in": 0.0254, "ft": 0.3048, "yd": 0.9144, "mi": 1609.344
    },
    "Mass": {  # base: kilogram (kg)
        "mg": 1e-6, "g": 1e-3, "kg": 1.0, "t (metric)": 1000.0,
        "oz": 0.028349523125, "lb": 0.45359237
    },
    "Area": {  # base: m²
        "mm²": 1e-6, "cm²": 1e-4, "m²": 1.0, "km²": 1e6,
        "in²": 0.0254**2, "ft²": 0.3048**2, "yd²": 0.9144**2,
        "acre": 4046.8564224, "hectare": 10000.0
    },
    "Volume": {  # base: m³
        "m³": 1.0, "L": 1e-3, "mL": 1e-6, "cm³": 1e-6,
        "in³": 0.0254**3, "ft³": 0.3048**3,
        "gal (US)": 0.003785411784, "qt (US)": 0.000946352946
    },
    "Pressure": {  # base: Pa
        "Pa": 1.0, "kPa": 1e3, "MPa": 1e6,
        "bar": 1e5, "atm": 101325.0,
        "psi": 6894.757293168, "torr": 133.32236842105263
    },
    "Density": {  # base: kg/m³
        "kg/m³": 1.0, "g/cm³": 1000.0, "g/mL": 1000.0,
        "lb/ft³": 16.01846337
    },
    "Dynamic Viscosity": {  # base: Pa·s
        "Pa·s": 1.0, "P (poise)": 0.1, "cP": 0.001, "mPa·s": 0.001
    },
    "Energy": {  # base: J
        "J": 1.0, "kJ": 1e3, "MJ": 1e6,
        "cal": 4.184, "kcal": 4184.0,
        "BTU (IT)": 1055.05585262
    },
    "Volumetric Flow": {  # base: m³/s
        "m³/s": 1.0,
        "m³/h": 1.0/3600.0,
        "L/min": (1e-3)/60.0,
        "ft³/min (CFM)": (0.3048**3)/60.0,
        "gal/min (US gpm)": 0.003785411784/60.0
    },
    "Amount (moles)": {  # base: mol
        "mmol": 1e-3, "mol": 1.0, "kmol": 1e3
    },
    "Molar Flow": {  # base: mol/s
        "mol/s": 1.0, "mol/h": 1.0/3600.0, "kmol/h": (1e3)/3600.0
    },
    "Heat Transfer Coefficient": {  # base: W/m²·K
        "W/m²·K": 1.0,
        "BTU/hr·ft²·°F": 5.678263
    }
}

TEMP_UNITS = ["C", "F", "K"]
CATEGORIES = list(to_base.keys()) + ["Temperature"]

# ---------- Helpers ----------
def temp_to_kelvin(value, unit):
    if unit == "K":
        return value
    elif unit == "C":
        return value + 273.15
    elif unit == "F":
        return (value - 32.0) * 5.0/9.0 + 273.15
    else:
        raise ValueError("Unknown temperature unit.")

def kelvin_to_temp(K, unit):
    if unit == "K":
        return K
    elif unit == "C":
        return K - 273.15
    elif unit == "F":
        return (K - 273.15) * 9.0/5.0 + 32.0
    else:
        raise ValueError("Unknown temperature unit.")

def pretty(x):
    try:
        return f"{x:.10g}"
    except Exception:
        return str(x)

# ---------- Core conversion function ----------
def convert_value(category, from_unit, to_unit, value):
    if category is None or from_unit is None or to_unit is None:
        return "Please select category and units."
    if value is None:
        return "Please enter a numeric value."

    if category == "Temperature":
        if from_unit not in TEMP_UNITS or to_unit not in TEMP_UNITS:
            return "Pick valid temperature units (C, F, K)."
        if from_unit == "K" and value < 0:
            return "Kelvin cannot be negative."
        K = temp_to_kelvin(value, from_unit)
        result = kelvin_to_temp(K, to_unit)
        return f"{pretty(value)} {from_unit} = {pretty(result)} {to_unit}"

    factors = to_base.get(category)
    if factors is None:
        return "Unknown category."
    if from_unit not in factors or to_unit not in factors:
        return "Selected units do not match the chosen category."

    base_val = value * factors[from_unit]
    result = base_val / factors[to_unit]
    return f"{pretty(value)} {from_unit} = {pretty(result)} {to_unit}"

# ---------- Gradio UI ----------
with gr.Blocks(title="Unit Converter (ChemE-friendly)") as demo:
    gr.Markdown("# 🧪 Unit Converter (ChemE-friendly)\nSimple, no-API web app for common engineering units.")
    with gr.Row():
        with gr.Column(scale=1):
            category = gr.Dropdown(label="Category", choices=CATEGORIES, value="Length")
            from_unit = gr.Dropdown(label="From unit", choices=list(to_base["Length"].keys()), value="m")
            to_unit = gr.Dropdown(label="To unit", choices=list(to_base["Length"].keys()), value="ft")
            value_in = gr.Number(label="Value", value=1.0, precision=6)
            with gr.Row():
                convert_btn = gr.Button("Convert")
                swap_btn = gr.Button("Swap")
                clear_btn = gr.Button("Clear")
        with gr.Column(scale=1):
            result = gr.Textbox(label="Result", interactive=False, lines=2)
            gr.Markdown("Tip: Temperature handles C/F/K correctly. Edit the dicts in code to add more units.")

    # update unit lists when category changes
    def update_unit_dropdowns(cat):
        if cat == "Temperature":
            units = TEMP_UNITS
        else:
            units = list(to_base.get(cat, {}).keys())
        if not units:
            units = ["--"]
        default_from = units[0]
        default_to = units[1] if len(units) > 1 else units[0]
        return gr.update(choices=units, value=default_from), gr.update(choices=units, value=default_to)

    category.change(fn=update_unit_dropdowns, inputs=category, outputs=[from_unit, to_unit])

    # convert
    convert_btn.click(fn=convert_value, inputs=[category, from_unit, to_unit, value_in], outputs=result)

    # swap
    def do_swap(a, b):
        return b, a
    swap_btn.click(fn=do_swap, inputs=[from_unit, to_unit], outputs=[from_unit, to_unit])

    # clear
    def do_clear():
        return "", 1.0
    clear_btn.click(fn=do_clear, inputs=None, outputs=[result, value_in])

    # examples
    gr.Examples(
        examples=[
            ["Length", "m", "ft", 3],
            ["Mass", "kg", "g", 2.5],
            ["Pressure", "bar", "psi", 1.2],
            ["Temperature", "C", "F", 25],
            ["Volumetric Flow", "L/min", "m³/h", 120],
            ["Density", "g/cm³", "kg/m³", 1.2],
        ],
        inputs=[category, from_unit, to_unit, value_in],
    )

# On Spaces you can leave launch() default — do not use share=True here.
if __name__ == "__main__":
    demo.launch()
