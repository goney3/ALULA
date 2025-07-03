# -*- coding: utf-8 -*-
"""
================================================================================

 █▀█ █   █ █ █   █▀█⠀⠀⠀⠀⠀⠀⢠⠁⠀⠀Accessible Learning Ultralight Layout Assistant⠀ 
 █▀█ █   █ █ █   █▀█⠀⠀⠀⠀⠀⣰⠃⠀⠀⠀Version: 0.19⠀⠀ 
 ▀ ▀ ▀▀▀ ▀▀▀ ▀▀▀ ▀ ▀⠀⠀⠀⠀⣜⠞⠀⠀⠀⠀Date: 2025-07-01
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⢀⣾⠕⠀⠀⡼⠀⠀Author: Keith F. — ultralightairplaneworkshop.com⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡴⠀⣴⣿⠋⠀⣴⠟⠀⠀⠀License: Dedicated to the Public Domain. 
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⢂⡽⣫⠁⣤⡿⠋⠀⠀⠄⠀         Use at own risk! No Rights Reserved.
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  ⢀⣿⢃⣋⡾⣠⣿⡵⠁⢀⣶⠏  Description: A preliminary design and analysis tool
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⢁⣾⠏⣼⡿⠋⣤⠿⡫⠂   for single-seat ultralight aircraft under FAA FAR
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣿⢟⣾⣿⣡⢟⡵⢡⣾⠶⠉⠀⠀⡤ Part 103. This application provides real-time
⠀⠀⠀⠀⠀⠀⠀⠀⠀⡺⡟⣵⣿⠟⣚⣶⠿⣡⡫⠊⢀⣤⡾⠋  performance estimates, weight & balance calculations,
⠀⠀⠀⠀⠀⠀⠀⣴⠁⣿⣿⢟⣴⣿⠟⣡⢟⣤⢊⡾⡛⠁    and stability feedback for various types of
⠀⠀⠀⢀⠜⣴⢟⡾⠀⢫⣾⣿⢟⣠⣶⣿⣩⠾⠋       ultralight vehicles, including fixed-wing, rotorcraft,
⠀⢞⡵⣫⠾⣩⣾⠗⣚⣵⣿⣿⢛⣡⣖⣒⣭⣤⣶       gliders, and lighter-than-air designs.
⣾⣞⡴⣋⠶⣛⣩⣥⠨⣛⣩⣤⣶⣭⣭⠛⠛⠉
⣝⣄⠫⠾⣛⣭⣭⣁⠐⠿⠛⢋⣭⣴⣿⣿⣥
⠀⠣⣱⠷⠶⣶⣤⠠⠿⠿⠿⠟⣂⣄              alula [al-yuh-luh]
⠀⠀⡸⣭⡛⣓⣘⠿⠿⢷⣳⡀                 "small thumb feathers that helps with flight control
⠀⠀⠈⠓⢷⣎⠙⠋⠿                      at low speeds"

================================================================================
"""

# Standard library imports for GUI, math, and file operations.
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import math
import json
from typing import Any, List, Tuple, Dict, Callable

class AlulaApp(tk.Tk):
    """
    Main application class for ALULA, handling the GUI, data management,
    calculations, and compliance checks for ultralight aircraft design.
    """
    def __init__(self):
        """
        Initializes the ALULA application, setting up the main window,
        defining constants, configuring styles, initializing data structures,
        creating UI widgets, and performing initial display updates.
        """
        super().__init__()
        self.title("ALULA - Accessible Learning Ultralight Layout Assistant")
        self.geometry("1200x800")
        self.minsize(1000, 700)

        # --- Application Constants ---
        # Defines key FAA FAR Part 103 limits and standard atmospheric/physical constants
        # used throughout the calculation modules.
        self.FAR_103_EMPTY_WEIGHT_LBS = 254
        self.FAR_103_GLIDER_EMPTY_WEIGHT_LBS = 155
        self.FAR_103_MAX_FUEL_GAL = 5
        self.FAR_103_MAX_FUEL_LBS = self.FAR_103_MAX_FUEL_GAL * 6 # Assuming 6 lbs/gallon for aviation fuel
        self.FAR_103_MAX_SPEED_KNOTS = 55
        self.FAR_103_STALL_SPEED_KNOTS = 24
        self.RHO_SEA_LEVEL_SLUG = 0.002377 # Air density at sea level (slugs/cu ft)
        self.HELIUM_DENSITY_SLUG = 0.000332 # Helium density (slugs/cu ft)
        self.KNOTS_TO_FPS = 1.68781 # Conversion factor from knots to feet per second

        # GUI style configuration
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.configure_styles()

        # Initialize the application's data model
        self.data = self.create_data_dictionary()
        self.component_entries: List[dict[str, tk.StringVar]] = [] # Stores references to weight & balance entry widgets
        self.sizing_tab_widgets: Dict[str, Tuple[ttk.Label, ttk.Entry]] = {}
        self.aero_tab_widgets: Dict[str, Tuple[ttk.Label, ttk.Entry]] = {}
        
        # Aerodynamic coefficient maps for various configurations
        self.cockpit_drag_map = {
            "Open Frame Fuselage": 0.025, "Cockpit with Windshield": 0.015,
            "Closed Cockpit": 0.008, "Streamlined Glider Type Cockpit": 0.003
        }
        
        self.tail_drag_map = {
            "Tailless": 0.0000, "V-Tail": 0.0010, "Conventional": 0.0015,
            "Cruciform": 0.0018, "T-Tail": 0.0025, "Twin Tail": 0.0030
        }
        
        self.paraglider_class_map = {
            "EN A (Beginner)": {"cl_trim": 1.2, "cl_max": 2.2, "cd0": 0.08, "oswald": 0.4},
            "EN B (Intermediate)": {"cl_trim": 1.1, "cl_max": 2.0, "cd0": 0.06, "oswald": 0.5},
            "EN C (Advanced)": {"cl_trim": 1.0, "cl_max": 1.8, "cd0": 0.04, "oswald": 0.6},
            "EN D (Expert)": {"cl_trim": 0.9, "cl_max": 1.7, "cd0": 0.03, "oswald": 0.7}
        }

        # Create application menu bar and main UI widgets
        self.create_menu()
        self.create_widgets()
        
        # Schedule initial UI update after the main window has been drawn
        self.after(50, self.initial_draw)

    def initial_draw(self):
        """
        Performs an initial update of the UI to correctly display elements
        based on the default vehicle type selected during application startup.
        """
        self.update_idletasks()
        self.update_ui_for_vehicle_type()

    def configure_styles(self):
        """
        Configures the visual styles for various Tkinter and ttk widgets
        to provide a consistent dark theme for the application.
        """
        bg_color, fg_color, entry_bg = '#383838', '#FFFFFF', '#5A5A5A'
        selected_tab_bg, red_color, green_color = '#6A6A6A', '#FF5757', '#6BFF6B'
        self.configure(bg=bg_color)
        self.style.configure('.', background=bg_color, foreground=fg_color, font=('Helvetica', 10))
        for s in ['TFrame', 'TLabel', 'TRadiobutton', 'TCheckbutton', 'TMenu', 'TMenubutton']: self.style.configure(s, background=bg_color, foreground=fg_color)
        self.style.configure('TButton', background=entry_bg, foreground=fg_color, borderwidth=1, focusthickness=3, focuscolor='none')
        self.style.map('TButton', background=[('active', selected_tab_bg)])
        self.style.configure('TNotebook', background=bg_color, borderwidth=0)
        self.style.configure('TNotebook.Tab', background='#4F4F4F', foreground=fg_color, padding=[10, 5], borderwidth=0)
        self.style.map('TNotebook.Tab', background=[('selected', selected_tab_bg)])
        self.style.configure('TCombobox', fieldbackground=entry_bg, background=entry_bg, foreground=fg_color, selectbackground=entry_bg, selectforeground=fg_color, arrowcolor=fg_color)
        self.style.configure('TEntry', fieldbackground=entry_bg, foreground=fg_color, insertcolor=fg_color)
        self.style.configure('Red.TLabel', foreground=red_color, background=bg_color)
        self.style.configure('Green.TLabel', foreground=green_color, background=bg_color)

    def create_menu(self):
        """
        Creates the application's menu bar with 'File' and 'Help' options,
        including shortcuts for saving and loading designs, and showing
        information dialogs.
        """
        menubar = tk.Menu(self, background='#2A2A2A', foreground='white', activebackground='#4A4A4A', activeforeground='white')
        self.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0, background='#383838', foreground='white')
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Design...", command=self.save_design, accelerator="Ctrl+S")
        file_menu.add_command(label="Load Design...", command=self.load_design, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        help_menu = tk.Menu(menubar, tearoff=0, background='#383838', foreground='white')
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About ALULA...", command=self.show_about_dialog)
        help_menu.add_command(label="Part 103 Rules...", command=self.show_rules_dialog)
        self.bind_all("<Control-s>", lambda event: self.save_design())
        self.bind_all("<Control-o>", lambda event: self.load_design())

    def create_data_dictionary(self):
        """
        Initializes the central data dictionary for the application,
        which stores input variables (as Tkinter StringVars/BooleanVars)
        and calculated results.
        """
        return {
            'inputs': {
                'vehicle_type': tk.StringVar(value='Fixed Wing'),
                'tail_style': tk.StringVar(value='Conventional'),
                'glider_class': tk.StringVar(value='EN B (Intermediate)'),
                'flaps': tk.BooleanVar(value=True),
                'cockpit_style': tk.StringVar(value='Cockpit with Windshield'),
                'pilot_weight': tk.StringVar(value='180'),
                'wing_area': tk.StringVar(value='250'),
                'wing_span': tk.StringVar(value='35'),
                'aspect_ratio': tk.StringVar(value='5.5'),
                'fuselage_length': tk.StringVar(value='17'),
                'lemac_ft': tk.StringVar(value='4.0'),
                'cl_max': tk.StringVar(value='1.5'),
                'cl_max_flaps': tk.StringVar(value='1.9'),
                'cd0': tk.StringVar(value='0.025'),
                'oswald_efficiency': tk.StringVar(value='0.8'),
                'neutral_point_ft': tk.StringVar(value='5.5'),
                'engine_hp': tk.StringVar(value='20'),
                'prop_efficiency': tk.StringVar(value='0.75'),
                'rotor_diameter': tk.StringVar(value='23'),
                'rotor_blade_chord': tk.StringVar(value='0.6'),
                'rotor_rpm': tk.StringVar(value='350'),
                'num_blades': tk.StringVar(value='2'),
                'rotor_blade_cd': tk.StringVar(value='0.012'),
                'envelope_volume': tk.StringVar(value='8000'),
            },
            'calculations': {} # This will store computed results
        }

    def create_widgets(self):
        """
        Sets up the main layout of the application window, including
        left, right, and center frames, and initializes the canvases
        for CG and flight envelope visualizations.
        """
        # Left frame for CG diagram and label
        left_frame = ttk.Frame(self, width=200, style='TFrame')
        left_frame.pack(side='left', fill='y', padx=10, pady=10)
        left_frame.pack_propagate(False) # Prevents frame from shrinking to content size

        # Right frame for results panel
        right_frame = ttk.Frame(self, width=300, style='TFrame')
        right_frame.pack(side='right', fill='y', padx=10, pady=10)
        right_frame.pack_propagate(False)

        # Center frame for notebook tabs and flight envelope diagram
        center_frame = ttk.Frame(self, style='TFrame')
        center_frame.pack(side='top', fill='both', expand=True, padx=10, pady=10)

        # CG Visualization Canvas
        self.cg_canvas_frame = ttk.Frame(left_frame)
        self.cg_canvas_frame.pack(fill='both', expand=True)
        self.cg_label = ttk.Label(self.cg_canvas_frame, text="CG: 0.00 ft\nSM: 0.0%", justify='center', wraplength=180)
        self.cg_label.pack(side='bottom', pady=10)
        self.cg_canvas = tk.Canvas(self.cg_canvas_frame, bg='#2A2A2A', highlightthickness=0)
        self.cg_canvas.pack(side='top', fill='both', expand=True)

        # Initialize the right panel with result displays
        self.create_right_panel(right_frame)

        # Flight Envelope Visualization Canvas
        self.flight_envelope_canvas = tk.Canvas(center_frame, bg='#2A2A2A', highlightthickness=0, height=350)
        self.flight_envelope_canvas.pack(fill='x', side='bottom', pady=(10,0))

        # Create notebook (tabbed interface) for input sections
        notebook = ttk.Notebook(center_frame, style='TNotebook')
        notebook.pack(fill='both', expand=True)

        # Dictionaries to hold references to widgets for dynamic updates are initialized in __init__
        
        # Define and create each tab in the notebook
        tab_funcs = {
            "Configuration": self.create_config_tab,
            "Sizing": self.create_sizing_tab,
            "Weights": self.create_weights_tab,
            "Aerodynamics": self.create_aero_tab,
            "Issues & Feedback": self.create_feedback_tab
        }
        for name, func in tab_funcs.items():
            tab = ttk.Frame(notebook, style='TFrame', padding=10)
            notebook.add(tab, text=name)
            func(tab)

    def create_right_panel(self, parent):
        """
        Creates the right-hand panel of the application, which displays
        calculated results such as weights, loadings, performance estimates,
        CG information, and a pie chart for weight fractions.
        """
        ttk.Button(parent, text="Calculate Design", command=self.update_all_calculations).pack(pady=10, fill='x', ipady=5)
        
        # Dictionaries to store references to result labels for easy updates
        self.results_desc_labels = {} # Stores the static description labels
        self.results_value_labels = {} # Stores the dynamic value labels
        
        # Define sections and their corresponding labels for the results panel
        sections = {
            "Weights (Estimated)": ["Est. Empty Weight:", "Max Gross Weight:", "Max Fuel Weight:"],
            "Loadings": ["Wing Loading:", "Power Loading:", "Span Loading:"],
            "Performance (Estimated)": ["Stall Speed Clean:", "Stall Speed Flaps:", "Max Level Speed (VH):", "Rate of Climb (ROC):"],
            "Center of Gravity (CG)": ["Longitudinal CG:", "Est. Static Margin:", "Calculated CG Location:"]
        }
        
        # Create labels for each section and result
        for title, labels in sections.items():
            ttk.Label(parent, text=title, font=('Helvetica', 12, 'bold')).pack(pady=(10, 2), anchor='w')
            for label_text in labels:
                frame = ttk.Frame(parent)
                frame.pack(fill='x', padx=10)
                desc_label = ttk.Label(frame, text=label_text)
                desc_label.pack(side='left')
                val_label = ttk.Label(frame, text="0.0", anchor='e', width=15)
                val_label.pack(side='right')
                self.results_desc_labels[label_text] = desc_label
                self.results_value_labels[label_text] = val_label
        
        # Create a canvas for the weight fractions pie chart
        ttk.Label(parent, text="Efficiency (Weight Fractions)", font=('Helvetica', 12, 'bold')).pack(pady=(20, 5), anchor='w')
        self.pie_canvas = tk.Canvas(parent, height=150, bg='#383838', highlightthickness=0)
        self.pie_canvas.pack(fill='x', pady=5)

    def create_dynamic_input_tab(self, parent, inputs_map, widget_dict):
        """
        Helper method to create input labels and entry widgets for tabs
        where inputs are dynamically shown/hidden based on vehicle type.
        """
        for key, text in inputs_map.items():
            label = ttk.Label(parent, text=text)
            entry = ttk.Entry(parent, textvariable=self.data['inputs'][key])
            widget_dict[key] = (label, entry)
    
    def create_config_tab(self, parent):
        """
        Creates the 'Configuration' tab, allowing selection of vehicle type,
        tail style, glider class, flap presence, cockpit style, and pilot weight.
        """
        # Vehicle Type Selection
        ttk.Label(parent, text="Vehicle Type:").grid(row=0, column=0, padx=5, pady=10, sticky='w')
        vehicle_combo = ttk.Combobox(parent, textvariable=self.data['inputs']['vehicle_type'], values=["Fixed Wing", "Gyrocopter", "Helicopter", "Lighter Than Air", "Glider", "Paraglider"])
        vehicle_combo.grid(row=0, column=1, padx=5, pady=10, sticky='ew')
        vehicle_combo.bind("<<ComboboxSelected>>", lambda e: self.update_ui_for_vehicle_type())
        
        # Placeholders for conditionally visible elements (Tail Style, Glider Class, Flaps)
        self.tail_style_label = ttk.Label(parent, text="Tail Style:")
        self.tail_style_combo = ttk.Combobox(parent, textvariable=self.data['inputs']['tail_style'], values=list(self.tail_drag_map.keys()))
        self.glider_class_label = ttk.Label(parent, text="Glider Class:")
        self.glider_class_combo = ttk.Combobox(parent, textvariable=self.data['inputs']['glider_class'], values=list(self.paraglider_class_map.keys()))
        
        self.flaps_label = ttk.Label(parent, text="Flaps:")
        self.flaps_check = ttk.Checkbutton(parent, variable=self.data['inputs']['flaps'], style='TCheckbutton')
        
        # Cockpit Style Radio Buttons (constant visibility)
        cockpit_frame = ttk.Frame(parent)
        cockpit_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky='w')
        for option in self.cockpit_drag_map.keys():
            ttk.Radiobutton(cockpit_frame, text=option, variable=self.data['inputs']['cockpit_style'], value=option).pack(anchor='w', pady=2)
        
        # Pilot Weight Input (constant visibility)
        ttk.Label(parent, text="Pilot Weight (lbs):").grid(row=5, column=0, padx=5, pady=10, sticky='w')
        ttk.Entry(parent, textvariable=self.data['inputs']['pilot_weight']).grid(row=5, column=1, padx=5, pady=10, sticky='ew')
        parent.grid_columnconfigure(1, weight=1)

    def create_sizing_tab(self, parent):
        """
        Creates the 'Sizing' tab, containing inputs for geometric parameters
        that vary based on the selected vehicle type. These inputs are
        dynamically managed by `update_ui_for_vehicle_type`.
        """
        inputs = {
            'wing_area': "Wing Area (sq ft):",
            'wing_span': "Wing Span (ft):",
            'aspect_ratio': "Aspect Ratio (Flat):",
            'fuselage_length': "Fuselage Length (ft):",
            'lemac_ft': "MAC Leading Edge (ft):",
            'rotor_diameter': "Rotor Diameter (ft):",
            'rotor_blade_chord': "Rotor Blade Chord (ft):",
            'num_blades': "Number of Blades:",
            'envelope_volume': "Envelope Volume (cu ft):"
        }
        self.create_dynamic_input_tab(parent, inputs, self.sizing_tab_widgets)

    def create_aero_tab(self, parent):
        """
        Creates the 'Aerodynamics' tab, containing inputs for aerodynamic
        coefficients and engine parameters that vary based on the selected
        vehicle type. These inputs are dynamically managed by `update_ui_for_vehicle_type`.
        """
        inputs = {
            'cl_max': "Max Lift Coeff (Cl_max):",
            'cl_max_flaps': "Max Lift Coeff (Flaps):",
            'cd0': "Base Zero-Lift Drag (Cd0):",
            'neutral_point_ft': "Wing Neutral Point (ft):",
            'engine_hp': "Engine Power (HP):",
            'prop_efficiency': "Propeller Efficiency (0-1):",
            'oswald_efficiency': "Oswald Efficiency (e):",
            'rotor_rpm': "Rotor RPM:",
            'rotor_blade_cd': "Rotor Blade Cd (profile):"
        }
        self.create_dynamic_input_tab(parent, inputs, self.aero_tab_widgets)

    def create_weights_tab(self, parent):
        """
        Creates the 'Weights' tab, which provides an editable table for
        entering individual component weights and their arms for weight & balance
        calculations. Default components are pre-filled.
        """
        # Table headers
        ttk.Label(parent, text="Component", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(parent, text="Weight (lbs)", font=('Helvetica', 10, 'bold')).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(parent, text="Arm (ft from datum)", font=('Helvetica', 10, 'bold')).grid(row=0, column=2, padx=5, pady=5)
        
        # Default components for the weight & balance table
        components: List[Tuple[str, str, str]] = [("Wing", "60", "4.5"), ("Fuselage", "50", "8.5"), ("Empennage", "15", "16"), ("Engine & Mount", "45", "1.0"), ("Landing Gear", "25", "4.0"), ("Fuel System", "5", "1.5"), ("Misc Systems", "15", "6.0")]
        self.component_entries = [] # List to hold dictionaries for each component's Tkinter variables
        
        # Create entry widgets for each component
        for i, (name, weight, arm) in enumerate(components):
            name_var, weight_var, arm_var = tk.StringVar(value=name), tk.StringVar(value=weight), tk.StringVar(value=arm)
            ttk.Entry(parent, textvariable=name_var).grid(row=i + 1, column=0, padx=5, pady=2, sticky='ew')
            ttk.Entry(parent, textvariable=weight_var).grid(row=i + 1, column=1, padx=5, pady=2)
            ttk.Entry(parent, textvariable=arm_var).grid(row=i + 1, column=2, padx=5, pady=2)
            self.component_entries.append({'name': name_var, 'weight': weight_var, 'arm': arm_var})
        parent.grid_columnconfigure(0, weight=1)

    def create_feedback_tab(self, parent):
        """
        Creates the 'Issues & Feedback' tab, which displays textual feedback
        and compliance warnings based on the design calculations.
        """
        self.feedback_text = tk.Text(parent, wrap='word', bg='#2A2A2A', fg='#FFFFFF', borderwidth=0, highlightthickness=0, height=10)
        self.feedback_text.pack(fill='both', expand=True, padx=5, pady=5)
        self.feedback_text.insert('1.0', "Design feedback will appear here after clicking 'Calculate Design'.")
        self.feedback_text.config(state='disabled') # Make text widget read-only

    def get_input_value(self, key, default=0.0):
        """
        Safely retrieves a float value from the data['inputs'] dictionary.
        Returns a default value if the key is not found or conversion fails.
        """
        try: return float(self.data['inputs'][key].get())
        except (ValueError, KeyError): return default

    def update_ui_for_vehicle_type(self):
        """
        Adjusts the visibility and default values of input fields in the
        'Configuration', 'Sizing', and 'Aerodynamics' tabs based on the
        selected vehicle type. It also triggers a full calculation update.
        """
        v_type = self.data['inputs']['vehicle_type'].get()
        
        # Update component weights defaults for Paraglider vs. others
        if v_type == 'Paraglider':
            paraglider_weights = [("Canopy", "15", "0"), ("Harness", "10", "0"), ("Reserve", "5", "0"), ("Container", "2", "0"), ("Misc", "3", "0"), ("","",""), ("","","")]
            for i, (name, weight, arm) in enumerate(paraglider_weights):
                if i < len(self.component_entries):
                    self.component_entries[i]['name'].set(name)
                    self.component_entries[i]['weight'].set(weight)
                    self.component_entries[i]['arm'].set(arm)
        else:
            standard_weights = [("Wing", "60", "4.5"), ("Fuselage", "50", "8.5"), ("Empennage", "15", "16"), ("Engine & Mount", "45", "1.0"), ("Landing Gear", "25", "4.0"), ("Fuel System", "5", "1.5"), ("Misc Systems", "15", "6.0")]
            for i, (name, weight, arm) in enumerate(standard_weights):
                if i < len(self.component_entries):
                    self.component_entries[i]['name'].set(name)
                    self.component_entries[i]['weight'].set(weight)
                    self.component_entries[i]['arm'].set(arm)

        # Hide all conditional elements first
        self.tail_style_label.grid_forget(); self.tail_style_combo.grid_forget()
        self.glider_class_label.grid_forget(); self.glider_class_combo.grid_forget()
        self.flaps_label.grid_forget(); self.flaps_check.grid_forget()

        # Show elements specific to the selected vehicle type
        if v_type == 'Paraglider':
            self.glider_class_label.grid(row=1, column=0, padx=5, pady=10, sticky='w')
            self.glider_class_combo.grid(row=1, column=1, padx=5, pady=10, sticky='ew')
        elif v_type in ['Fixed Wing', 'Glider']:
            self.tail_style_label.grid(row=1, column=0, padx=5, pady=10, sticky='w')
            self.tail_style_combo.grid(row=1, column=1, padx=5, pady=10, sticky='ew')
            self.flaps_label.grid(row=2, column=0, padx=5, pady=10, sticky='w')
            self.flaps_check.grid(row=2, column=1, padx=5, pady=10, sticky='w')
        else: # For Gyrocopter, Helicopter, Lighter Than Air (show tail style as general body configuration)
            self.tail_style_label.grid(row=1, column=0, padx=5, pady=10, sticky='w')
            self.tail_style_combo.grid(row=1, column=1, padx=5, pady=10, sticky='ew')

        # Define which inputs are visible for each vehicle type on Sizing and Aerodynamics tabs
        sizing_visibility: Dict[str, List[str]] = {
            'Fixed Wing': ['wing_area', 'wing_span', 'fuselage_length', 'lemac_ft'],
            'Glider': ['wing_area', 'wing_span', 'fuselage_length', 'lemac_ft'],
            'Gyrocopter': ['rotor_diameter', 'rotor_blade_chord', 'num_blades', 'fuselage_length'],
            'Helicopter': ['rotor_diameter', 'rotor_blade_chord', 'num_blades', 'fuselage_length'],
            'Lighter Than Air': ['envelope_volume', 'fuselage_length'],
            'Paraglider': ['wing_area', 'aspect_ratio']
        }
        aero_visibility: Dict[str, List[str]] = {
            'Fixed Wing': ['cl_max', 'cl_max_flaps', 'cd0', 'neutral_point_ft', 'engine_hp', 'prop_efficiency', 'oswald_efficiency'],
            'Glider': ['cl_max', 'cl_max_flaps', 'cd0', 'oswald_efficiency'],
            'Gyrocopter': ['rotor_blade_cd', 'cd0', 'engine_hp', 'prop_efficiency', 'rotor_rpm'],
            'Helicopter': ['rotor_blade_cd', 'cd0', 'engine_hp', 'rotor_rpm'],
            'Lighter Than Air': ['cd0', 'engine_hp', 'prop_efficiency'],
            'Paraglider': [] # No specific aero inputs for Paragliders as they use predefined classes
        }
        
        # Hide all sizing and aero inputs initially
        for key, (label, entry) in self.sizing_tab_widgets.items(): label.grid_forget(); entry.grid_forget()
        for key, (label, entry) in self.aero_tab_widgets.items(): label.grid_forget(); entry.grid_forget()
        
        # Show relevant sizing inputs
        visible_sizing_keys: List[str] = sizing_visibility.get(v_type, [])
        for i, key in enumerate(visible_sizing_keys):
            self.sizing_tab_widgets[key][0].grid(row=i, column=0, padx=5, pady=5, sticky='w')
            self.sizing_tab_widgets[key][1].grid(row=i, column=1, padx=5, pady=5)
        
        # Show relevant aerodynamic inputs
        visible_aero_keys: List[str] = aero_visibility.get(v_type, [])
        for i, key in enumerate(visible_aero_keys):
            self.aero_tab_widgets[key][0].grid(row=i, column=0, padx=5, pady=5, sticky='w')
            self.aero_tab_widgets[key][1].grid(row=i, column=1, padx=5, pady=5)
        
        # Trigger recalculations and UI updates after changing vehicle type
        self.update_all_calculations()

    def update_all_calculations(self):
        """
        Orchestrates all design calculations. It first calculates total weight
        and CG from component entries, then calls the specific calculation
        function based on the selected vehicle type, and finally updates
        all relevant UI elements.
        """
        v_type = self.data['inputs']['vehicle_type'].get()
        total_weight, total_moment, pwr_sys_w = 0.0, 0.0, 0.0
        
        # Calculate total empty weight and CG from component entries
        for entry in self.component_entries:
            try:
                w, a = float(entry['weight'].get()), float(entry['arm'].get())
                total_weight += w
                total_moment += w * a
                if 'engine' in entry['name'].get().lower(): # Identify engine weight for power system
                    pwr_sys_w += w
            except ValueError:
                # Silently ignore invalid entries for calculation purposes
                continue 
        
        cg_location = total_moment / total_weight if total_weight > 0 else 0
        empty_weight = total_weight
        pilot_weight = self.get_input_value('pilot_weight')
        fuel_weight = 0 if v_type in ['Glider', 'Paraglider'] else self.FAR_103_MAX_FUEL_LBS
        gross_weight = empty_weight + pilot_weight + fuel_weight
        
        # Store basic calculated values in the data model
        self.data['calculations'] = {
            "Empty Weight": empty_weight,
            "Gross Weight": gross_weight,
            "Fuel Weight": fuel_weight,
            "Power System Weight": pwr_sys_w,
            "CG Location": cg_location,
            "Pilot Weight": pilot_weight
        }
        
        # Map vehicle types to their specific calculation functions
        calc_map: Dict[str, Callable] = {
            'Fixed Wing': self.calculate_fixed_wing,
            'Glider': self.calculate_glider,
            'Gyrocopter': self.calculate_gyrocopter,
            'Helicopter': self.calculate_helicopter,
            'Lighter Than Air': self.calculate_lta,
            'Paraglider': self.calculate_paraglider
        }
        calc_function = calc_map[v_type]
        
        # Execute the relevant calculation function
        calc_function()
        
        # Update all graphical and textual UI elements
        self.update_results_panel()
        self.update_cg_canvas()
        self.update_pie_chart()
        self.update_flight_envelope()
        self.update_feedback_tab()

    def calculate_fixed_wing(self, is_glider: bool = False):
        """
        Performs aerodynamic and performance calculations specific to
        fixed-wing aircraft (including gliders, with a flag).
        Calculates stall speeds, max level speed (VH), rate of climb (ROC),
        loadings, and static margin.
        """
        calc = self.data['calculations']
        gross_weight = calc['Gross Weight']
        wing_area = self.get_input_value('wing_area', 1)
        wing_span = self.get_input_value('wing_span', 1)
        base_cd0 = self.get_input_value('cd0', 0.025)
        oswald_eff = self.get_input_value('oswald_efficiency', 0.8)
        engine_hp = 0 if is_glider else self.get_input_value('engine_hp', 20)
        prop_eff = self.get_input_value('prop_efficiency', 0.75)
        lemac_ft, np_ft = self.get_input_value('lemac_ft', 4.0), self.get_input_value('neutral_point_ft', 5.5)
        
        # Calculate total zero-lift drag coefficient
        cockpit_drag = self.cockpit_drag_map.get(self.data['inputs']['cockpit_style'].get(), 0)
        tail_drag = self.tail_drag_map.get(self.data['inputs']['tail_style'].get(), 0)
        total_cd0 = base_cd0 + cockpit_drag + tail_drag
        
        # Lift coefficients for stall speed calculation
        cl_max = self.get_input_value('cl_max', 1.5)
        cl_max_flaps = self.get_input_value('cl_max_flaps', 1.9)
        
        # Stall speed calculations
        vs_fps = math.sqrt((2 * gross_weight) / (self.RHO_SEA_LEVEL_SLUG * wing_area * cl_max)) if wing_area * cl_max > 0 else 0
        vs_flaps_fps = math.sqrt((2 * gross_weight) / (self.RHO_SEA_LEVEL_SLUG * wing_area * cl_max_flaps)) if wing_area * cl_max_flaps > 0 else 0
        
        # Aspect Ratio and induced drag factor (k)
        AR = (wing_span ** 2) / wing_area if wing_area > 0 else 0
        k = 1 / (math.pi * AR * oswald_eff) if AR * oswald_eff > 0 else float('inf')
        
        # For gliders, calculate L/D Max and Min Sink Rate
        ld_max = math.sqrt( (total_cd0 / k) ) / (2*total_cd0) if k > 0 and total_cd0 > 0 else 0
        v_ld_max_fps = math.sqrt( (2*gross_weight) / (self.RHO_SEA_LEVEL_SLUG * wing_area * math.sqrt(total_cd0/k)) ) if k > 0 and total_cd0 > 0 else 0
        min_sink_fps = v_ld_max_fps / ld_max if ld_max > 0 else 0
        
        vh_fps: float = 0.0 # Max level speed
        if not is_glider:
            # Powered aircraft performance calculations
            power_avail = engine_hp * prop_eff * 550 # Available power in ft-lbs/sec
            
            # Estimate Max Level Speed (VH) by iterating speeds
            if vs_fps > 0:
                for v_fps in range(int(vs_fps), 300): # Iterate from stall speed up to a reasonable max
                    Cl = (2 * gross_weight) / (self.RHO_SEA_LEVEL_SLUG * wing_area * (v_fps**2))
                    Cd = total_cd0 + k * (Cl**2) # Total drag coefficient
                    power_req = 0.5 * self.RHO_SEA_LEVEL_SLUG * (v_fps**3) * wing_area * Cd # Power required
                    if power_req > power_avail:
                        vh_fps = float(v_fps - 1) # Set VH to the previous speed
                        break
            
            # Estimate Rate of Climb (ROC) at best climb speed
            max_excess_power = -float('inf')
            climb_v_end_float = vh_fps * 1.05 if vh_fps > vs_fps else vs_fps * 1.5
            climb_v_end = int(climb_v_end_float) # Search range for climb speed
            for v_fps in range(int(vs_fps * 1.05), climb_v_end):
                Cl = (2 * gross_weight) / (self.RHO_SEA_LEVEL_SLUG * wing_area * v_fps**2)
                Cd = total_cd0 + k * (Cl**2)
                power_req = 0.5 * self.RHO_SEA_LEVEL_SLUG * (v_fps**3) * wing_area * Cd
                excess_power = power_avail - power_req
                if excess_power > max_excess_power:
                    max_excess_power = excess_power
            
            roc_fpm: float = 0.0
            if gross_weight > 0 and max_excess_power > -float('inf'):
                roc_fpm = (max_excess_power / gross_weight) * 60
            
            # Update calculation results for powered fixed-wing
            calc.update({
                "Wing Loading": gross_weight / wing_area if wing_area > 0 else 0,
                "Power Loading": gross_weight / engine_hp if engine_hp > 0 else 0,
                "Span Loading": gross_weight / wing_span if wing_span > 0 else 0,
                "Stall Speed": vs_fps / self.KNOTS_TO_FPS,
                "Stall Speed Flaps": vs_flaps_fps / self.KNOTS_TO_FPS if self.data['inputs']['flaps'].get() else vs_fps / self.KNOTS_TO_FPS,
                "VH": vh_fps / self.KNOTS_TO_FPS,
                "ROC": roc_fpm if roc_fpm > 0 else 0
            })
        else:
            # Update calculation results for gliders
            calc.update({
                "L/D Max": ld_max,
                "Min Sink Rate": min_sink_fps * 60,
                "Speed @ Min Sink": v_ld_max_fps / self.KNOTS_TO_FPS,
                "Stall Speed": vs_fps / self.KNOTS_TO_FPS,
                "Stall Speed Flaps": vs_flaps_fps / self.KNOTS_TO_FPS if self.data['inputs']['flaps'].get() else vs_fps / self.KNOTS_TO_FPS,
                "Wing Loading": gross_weight / wing_area if wing_area > 0 else 0,
                "VH": v_ld_max_fps / self.KNOTS_TO_FPS * 1.5 # VH for gliders estimated as 1.5 * speed at min sink
            })
        
        # Longitudinal stability calculations (applicable to fixed-wing/gliders)
        mean_chord = wing_area / wing_span if wing_span > 0 else 1
        calc.update({
            "Static Margin": ((np_ft - calc["CG Location"]) / mean_chord) * 100 if mean_chord > 0 else 0,
            "CG MAC Percent": ((calc["CG Location"] - lemac_ft) / mean_chord) * 100 if mean_chord > 0 else 0,
            "Total Cd0": total_cd0,
            "Base Cd0": base_cd0,
            "Cockpit Drag": cockpit_drag,
            "Tail Drag": tail_drag
        })

    def calculate_glider(self):
        """
        Wrapper function to calculate glider performance by calling
        the fixed-wing calculation with the `is_glider` flag set to True.
        """
        self.calculate_fixed_wing(is_glider=True)
    
    def calculate_paraglider(self):
        """
        Performs performance calculations specific to paragliders,
        using predefined aerodynamic characteristics based on the
        selected glider class (EN A/B/C/D).
        """
        calc = self.data['calculations']
        gross_weight = calc['Gross Weight']
        wing_area = self.get_input_value('wing_area', 250)
        ar = self.get_input_value('aspect_ratio', 5.5)
        glider_class = self.data['inputs']['glider_class'].get()
        aero_props: dict[str, Any] | None = self.paraglider_class_map.get(glider_class)
        
        if aero_props is None:
            # If no valid glider class found, return to prevent errors
            calc.update({"L/D Max": 0, "Min Sink Rate": 0, "Trim Speed": 0, "Stall Speed": 0, "Wing Loading": 0, "VH": 0, "Static Margin": "N/A", "CG MAC Percent": "N/A"})
            return
            
        cl_trim, cl_max, cd0, oswald_eff = aero_props['cl_trim'], aero_props['cl_max'], aero_props['cd0'], aero_props['oswald']
        
        # Stall and trim speed calculations
        vs_fps = math.sqrt((2 * gross_weight) / (self.RHO_SEA_LEVEL_SLUG * wing_area * cl_max)) if wing_area * cl_max > 0 else 0
        trim_speed_fps = math.sqrt((2 * gross_weight) / (self.RHO_SEA_LEVEL_SLUG * wing_area * cl_trim)) if wing_area * cl_trim > 0 else 0
        
        # Induced drag factor (k)
        k = 1 / (math.pi * ar * oswald_eff) if ar * oswald_eff > 0 else float('inf')
        
        # L/D Max and Min Sink Rate
        ld_max = math.sqrt( (cd0 / k) ) / (2*cd0) if k > 0 and cd0 > 0 else 0
        v_ld_max_fps = math.sqrt( (2*gross_weight) / (self.RHO_SEA_LEVEL_SLUG * wing_area * math.sqrt(cd0/k)) ) if k > 0 and cd0 > 0 else 0
        min_sink_fps = v_ld_max_fps / ld_max if ld_max > 0 else 0
        
        # Update calculation results for paragliders
        calc.update({
            "L/D Max": ld_max,
            "Min Sink Rate": min_sink_fps * 60,
            "Trim Speed": trim_speed_fps / self.KNOTS_TO_FPS,
            "Stall Speed": vs_fps / self.KNOTS_TO_FPS,
            "Wing Loading": gross_weight / wing_area if wing_area > 0 else 0,
            "VH": trim_speed_fps * 1.4 / self.KNOTS_TO_FPS, # Top speed estimated from trim speed
            "Static Margin": "N/A", # Not applicable for paragliders in this context
            "CG MAC Percent": "N/A" # Not applicable for paragliders in this context
        })

    def calculate_rotorcraft(self, is_helicopter):
        """
        Performs performance calculations for rotorcraft (gyrocopters and helicopters).
        Calculates disc loading, power loading, tip speed, and max level speed (VH).
        """
        calc = self.data['calculations']
        gross_weight = calc['Gross Weight']
        rotor_d, blade_c, num_b = self.get_input_value('rotor_diameter', 23), self.get_input_value('rotor_blade_chord', 0.6), self.get_input_value('num_blades', 2)
        rotor_rpm = self.get_input_value('rotor_rpm', 350)
        base_cd0, blade_cd = self.get_input_value('cd0', 0.05), self.get_input_value('rotor_blade_cd', 0.012)
        engine_hp = self.get_input_value('engine_hp', 20)
        
        # Fuselage drag calculation
        cockpit_drag = self.cockpit_drag_map.get(self.data['inputs']['cockpit_style'].get(), 0)
        fuselage_drag_area = (base_cd0 + cockpit_drag) * 15 # Assumed reference area for fuselage drag
        
        rotor_area = math.pi * (rotor_d / 2)**2
        solidity = (num_b * blade_c) / (math.pi * rotor_d) if rotor_d > 0 else 0
        tip_speed = (rotor_rpm * 2 * math.pi / 60) * (rotor_d / 2)
        power_avail = engine_hp * self.get_input_value('prop_efficiency', 0.75) * 550
        
        # Profile power for rotor
        power_profile = (solidity / 8) * self.RHO_SEA_LEVEL_SLUG * rotor_area * (tip_speed**3) * blade_cd
        
        min_speed_fps = 15 * self.KNOTS_TO_FPS # Minimum forward speed for rotorcraft
        vh_fps = 0.0 # Max level speed
        
        if is_helicopter:
            # Helicopter specific calculations (hover and forward flight)
            power_induced_hover = (gross_weight**1.5) / math.sqrt(2 * self.RHO_SEA_LEVEL_SLUG * rotor_area)
            power_req_hover = power_induced_hover + power_profile
            roc_fpm = (power_avail - power_req_hover) / gross_weight * 60 if gross_weight > 0 else 0
            
            # Max level speed calculation for helicopter by iterating speeds
            for v_fps_int in range(1, 250):
                v_fps = float(v_fps_int)
                power_parasitic = 0.5 * self.RHO_SEA_LEVEL_SLUG * v_fps**3 * fuselage_drag_area
                power_induced = (gross_weight**2) / (2 * self.RHO_SEA_LEVEL_SLUG * rotor_area * v_fps) if v_fps > 0 else float('inf')
                power_req_fwd = power_parasitic + power_profile + power_induced
                if power_req_fwd > power_avail:
                    vh_fps = v_fps - 1
                    break
        else: # Gyrocopter
            # Gyrocopter specific calculations
            roc_fpm = 0.0 # Gyrocopters typically have no significant vertical climb
            rotor_drag_area = rotor_area * 0.05 # Assumed drag area for rotor system
            total_drag_area = fuselage_drag_area + rotor_drag_area
            
            # Max level speed calculation for gyrocopter by iterating speeds
            for v_fps_int in range(1, 250):
                v_fps = float(v_fps_int)
                thrust_req = 0.5 * self.RHO_SEA_LEVEL_SLUG * v_fps**2 * total_drag_area
                thrust_avail = power_avail / v_fps if v_fps > 0 else float('inf')
                if thrust_req > thrust_avail:
                    vh_fps = v_fps - 1
                    break
        
        # Update calculation results for rotorcraft
        calc.update({
            "Disc Loading": gross_weight / rotor_area if rotor_area > 0 else 0,
            "Power Loading": gross_weight / engine_hp if engine_hp > 0 else 0,
            "Tip Speed": tip_speed,
            "Min. Fwd Speed": min_speed_fps / self.KNOTS_TO_FPS,
            "VH": vh_fps / self.KNOTS_TO_FPS,
            "ROC": roc_fpm if roc_fpm > 0 else 0,
            "Static Margin": "N/A", # Not typically calculated for rotorcraft
            "CG MAC Percent": "N/A" # Not typically calculated for rotorcraft
        })

    def calculate_helicopter(self):
        """
        Wrapper function to calculate helicopter performance by calling
        the rotorcraft calculation with the `is_helicopter` flag set to True.
        """
        self.calculate_rotorcraft(is_helicopter=True)

    def calculate_gyrocopter(self):
        """
        Wrapper function to calculate gyrocopter performance by calling
        the rotorcraft calculation with the `is_helicopter` flag set to False.
        """
        self.calculate_rotorcraft(is_helicopter=False)

    def calculate_lta(self):
        """
        Performs calculations specific to Lighter Than Air (LTA) vehicles,
        determining buoyant lift, net lift, static condition, and max level speed (VH).
        """
        calc = self.data['calculations']
        gross_weight = calc['Gross Weight']
        volume, base_cd0 = self.get_input_value('envelope_volume', 8000), self.get_input_value('cd0', 0.025)
        engine_hp, prop_eff = self.get_input_value('engine_hp', 20), self.get_input_value('prop_efficiency', 0.75)
        
        # Buoyant lift calculation (Archimedes' principle)
        buoyant_lift = (self.RHO_SEA_LEVEL_SLUG - self.HELIUM_DENSITY_SLUG) * 32.174 * volume
        net_lift = buoyant_lift - gross_weight
        
        power_avail = engine_hp * prop_eff * 550
        
        # Estimate frontal area for drag calculation (assuming spherical equivalent)
        frontal_area = math.pi * ((volume * 0.75 / math.pi)**(1/3))**2
        
        # Max level speed calculation for LTA
        vh_fps = (power_avail / (0.5 * self.RHO_SEA_LEVEL_SLUG * frontal_area * base_cd0))**(1/3) if base_cd0 > 0 else 0
        
        # Update calculation results for LTA vehicles
        calc.update({
            "Buoyant Lift": buoyant_lift,
            "Net Lift": net_lift,
            "Static Heaviness": "Heavy" if net_lift < 0 else "Light",
            "VH": vh_fps / self.KNOTS_TO_FPS,
            "ROC": "N/A", # Not applicable in the same sense as winged aircraft
            "Stall Speed": "N/A", # Not applicable for LTA
            "Static Margin": "N/A", # Not typically calculated for LTA
            "CG MAC Percent": "N/A" # Not typically calculated for LTA
        })

    def _set_result_value(self, original_text, new_text, calc_key, unit, compliance_val=None):
        """
        Helper method to update a single line in the results panel.
        It sets the description text, retrieves the calculated value,
        formats it, adds units, and applies color coding for compliance checks.
        """
        self.results_desc_labels[original_text].config(text=new_text)
        val = self.data['calculations'].get(calc_key)
        if val is not None:
            style = 'TLabel'
            if isinstance(val, (int, float)):
                text = f"{val:.1f} {unit}"
                if compliance_val is not None:
                    # Apply green/red style based on compliance limit
                    style = 'Green.TLabel' if val <= compliance_val else 'Red.TLabel'
            else:
                text = f"{val} {unit}"
            self.results_value_labels[original_text].config(text=text, style=style)
        else:
            self.results_value_labels[original_text].config(text="N/A", style='TLabel')

    def update_results_panel(self):
        """
        Updates all the labels in the right-hand results panel with the
        latest calculated values, adapting the displayed metrics based on
        the selected vehicle type.
        """
        v_type = self.data['inputs']['vehicle_type'].get()
        
        # Clear all labels before updating to handle dynamic visibility
        for desc_label in self.results_desc_labels.values(): desc_label.config(text="")
        for value_label in self.results_value_labels.values(): value_label.config(text="")
        
        # Populate common results
        self._set_result_value("Est. Empty Weight:", "Est. Empty Weight:", "Empty Weight", "lbs", self.FAR_103_GLIDER_EMPTY_WEIGHT_LBS if v_type in ['Glider', 'Paraglider'] else self.FAR_103_EMPTY_WEIGHT_LBS)
        self._set_result_value("Max Gross Weight:", "Max Gross Weight:", "Gross Weight", "lbs")
        self._set_result_value("Max Fuel Weight:", "Max Fuel Weight:", "Fuel Weight", "lbs")
        self._set_result_value("Calculated CG Location:", "Calculated CG Location:", "CG Location", "ft")

        # Populate type-specific results
        if v_type in ['Fixed Wing', 'Glider', 'Paraglider']:
            self._set_result_value("Wing Loading:", "Wing Loading:", "Wing Loading", "lbs/sqft")
            self._set_result_value("Stall Speed Clean:", "Stall Speed:", "Stall Speed", "knots", self.FAR_103_STALL_SPEED_KNOTS)
            self._set_result_value("Longitudinal CG:", "Longitudinal CG:", "CG MAC Percent", "% MAC")
            self._set_result_value("Est. Static Margin:", "Est. Static Margin:", "Static Margin", "% MAC")
            if v_type == 'Fixed Wing':
                self._set_result_value("Power Loading:", "Power Loading:", "Power Loading", "lbs/HP")
                self._set_result_value("Span Loading:", "Span Loading:", "Span Loading", "lbs/ft")
                self._set_result_value("Stall Speed Flaps:", "Stall Speed Flaps:", "Stall Speed Flaps", "knots")
                self._set_result_value("Max Level Speed (VH):", "Max Level Speed (VH):", "VH", "knots", self.FAR_103_MAX_SPEED_KNOTS)
                self._set_result_value("Rate of Climb (ROC):", "Rate of Climb (ROC):", "ROC", "fpm")
            else: # Glider or Paraglider
                self._set_result_value("Power Loading:", "L/D Max (Glide Ratio):", "L/D Max", ":1")
                self._set_result_value("Rate of Climb (ROC):", "Min Sink Rate:", "Min Sink Rate", "fpm")
                if v_type == 'Paraglider':
                    self._set_result_value("Span Loading:", "Trim Speed:", "Trim Speed", "knots")
                    self._set_result_value("Max Level Speed (VH):", "Top Speed (Accelerated):", "VH", "knots", self.FAR_103_MAX_SPEED_KNOTS)
                else: # Glider
                    self._set_result_value("Max Level Speed (VH):", "Speed @ Min Sink:", "Speed @ Min Sink", "knots")
                    self._set_result_value("Stall Speed Flaps:", "Stall Speed Flaps:", "Stall Speed Flaps", "knots")
        elif v_type in ['Gyrocopter', 'Helicopter']:
            self._set_result_value("Wing Loading:", "Disc Loading:", "Disc Loading", "lbs/sqft")
            self._set_result_value("Power Loading:", "Power Loading:", "Power Loading", "lbs/HP")
            self._set_result_value("Span Loading:", "Rotor Tip Speed:", "Tip Speed", "ft/s")
            self._set_result_value("Stall Speed Clean:", "Min. Fwd Speed:", "Min. Fwd Speed", "knots")
            self._set_result_value("Max Level Speed (VH):", "Max Level Speed (VH):", "VH", "knots", self.FAR_103_MAX_SPEED_KNOTS)
            self._set_result_value("Rate of Climb (ROC):", "Rate of Climb (Hover):" if v_type == 'Helicopter' else "Rate of Climb (ROC):", "ROC", "fpm")
        elif v_type == 'Lighter Than Air':
            self._set_result_value("Wing Loading:", "Buoyant Lift:", "Buoyant Lift", "lbs")
            self._set_result_value("Power Loading:", "Net Lift:", "Net Lift", "lbs")
            self._set_result_value("Span Loading:", "Static Condition:", "Static Heaviness", "")
            self._set_result_value("Max Level Speed (VH):", "Max Level Speed (VH):", "VH", "knots", self.FAR_103_MAX_SPEED_KNOTS)

    def update_cg_canvas(self):
        """
        Draws the Center of Gravity (CG) visualization on the canvas,
        indicating the calculated CG location relative to the fuselage length
        and color-coding the marker based on static margin compliance.
        For paragliders, it displays a "not applicable" message.
        """
        self.cg_canvas.delete("all") # Clear previous drawings
        w, h = self.cg_canvas.winfo_width(), self.cg_canvas.winfo_height()
        if w < 2 or h < 2: return # Prevent drawing on uninitialized canvas
        
        v_type = self.data['inputs']['vehicle_type'].get()
        if v_type == 'Paraglider':
            self.cg_canvas.create_text(w/2, h/2, text="CG is not a fixed design parameter\nfor Paragliders.", fill='white', font=('Helvetica', 10), justify='center')
            self.cg_label.config(text="CG: N/A\nSM: N/A")
            return
        
        calc = self.data['calculations']
        cg_pos, f_len, sm = calc.get("CG Location", 0), self.get_input_value("fuselage_length", 1), calc.get("Static Margin", 0)
        
        margin = 30 # Margin from canvas edges
        marker_color = 'white'
        # Color-code CG marker based on static margin (SM)
        if isinstance(sm, (int, float)) and not (5.0 <= sm <= 15.0):
            marker_color = self.style.lookup('Red.TLabel', 'foreground')
        
        # Draw fuselage representation
        self.cg_canvas.create_rectangle(w/2 - 20, margin, w/2 + 20, h - margin, fill='#4A90E2', outline='')
        self.cg_canvas.create_text(w/2, margin - 10, text="Nose", fill="white")
        self.cg_canvas.create_text(w/2, h - margin + 10, text="Tail", fill="white")
        
        # Draw CG marker if fuselage length is valid
        if f_len > 0 and h > 2 * margin:
            y = margin + ((cg_pos / f_len) * (h - 2 * margin))
            self.cg_canvas.create_oval(w/2 - 10, y - 10, w/2 + 10, y + 10, outline=marker_color, width=2)
            self.cg_canvas.create_line(w/2, y - 15, w/2, y + 15, fill=marker_color, width=2)
            self.cg_canvas.create_line(w/2 - 15, y, w/2 + 15, y, fill=marker_color, width=2)
        
        # Update CG and Static Margin text label
        sm_text = f"{sm:.1f}%" if isinstance(sm, (int, float)) else "N/A"
        self.cg_label.config(text=f"CG: {cg_pos:.2f} ft\nSM: {sm_text}")

    def update_pie_chart(self):
        """
        Draws a pie chart on the canvas representing the weight fractions
        of the aircraft: Empty Structure (E), Power System (V), Fuel (F),
        and Pilot (P).
        """
        self.pie_canvas.delete("all") # Clear previous drawings
        w, h = self.pie_canvas.winfo_width(), self.pie_canvas.winfo_height()
        if w < 2 or h < 2: return # Prevent drawing on uninitialized canvas
        
        calc = self.data['calculations']
        gross = calc.get("Gross Weight", 1)
        if gross <= 0: return # Avoid division by zero
        
        empty_weight, pwr_sys_w = calc.get("Empty Weight", 0), calc.get("Power System Weight", 0)
        struct_w = empty_weight - pwr_sys_w # Calculate structural weight
        
        # Calculate fractions of gross weight
        fractions = {
            "E": struct_w / gross, # Empty Structure
            "V": pwr_sys_w / gross, # Power System
            "F": calc.get("Fuel Weight", 0) / gross, # Fuel
            "P": calc.get("Pilot Weight", 0) / gross # Pilot
        }
        
        colors = {"E": "#4A90E2", "V": "#7ED321", "F": "#F5A623", "P": "#B2DFEE"}
        
        # Sort fractions for consistent drawing order (largest slices first)
        sorted_fractions = sorted(fractions.items(), key=lambda item: item[1], reverse=True)
        
        # Pie chart parameters
        radius, cx, cy, start_angle = min(w, h) / 2 - 25, w / 2, h / 2, 90
        legend_items = []
        
        # Draw pie slices
        for name, frac in sorted_fractions:
            extent = frac * 360
            if extent > 0.5: # Only draw if slice is visible
                self.pie_canvas.create_arc(cx - radius, cy - radius, cx + radius, cy + radius, start=start_angle, extent=extent, fill=colors[name], outline='white')
            legend_items.append((name, colors[name]))
            start_angle += extent
        
        # Draw legend
        legend_x = 20
        for letter, color in legend_items:
            self.pie_canvas.create_rectangle(legend_x, h - 15, legend_x + 10, h - 5, fill=color, outline=color)
            self.pie_canvas.create_text(legend_x + 20, h - 10, text=letter, fill="white", anchor="w")
            legend_x += 45

    def update_flight_envelope(self):
        """
        Draws a V-g (velocity-G-load) diagram on the canvas, illustrating
        the aircraft's safe operating envelope in terms of airspeed and load factor.
        Includes stall speeds, maneuvering speed (Va), and never-exceed speed (Vne).
        Displays a "not applicable" message for LTA vehicles.
        """
        canvas = self.flight_envelope_canvas
        canvas.delete("all") # Clear previous drawings
        
        v_type = self.data['inputs']['vehicle_type'].get()
        if v_type in ['Lighter Than Air']:
            canvas.create_text(canvas.winfo_width()/2, canvas.winfo_height()/2, text=f"V-g Diagram not applicable for {v_type}.", fill='white', font=('Helvetica', 12))
            return
        
        w, h = canvas.winfo_width(), canvas.winfo_height()
        if w < 2 or h < 2: return # Prevent drawing on uninitialized canvas
        
        calc = self.data['calculations']
        # Retrieve calculated speeds, defaulting to reasonable values if not found
        vs = calc.get('Stall Speed') or calc.get('Min. Fwd Speed', 25)
        vh = calc.get('VH', 55)
        
        # Define positive and negative G limits based on vehicle type
        pos_g, neg_g = (2.5, 0) if v_type == 'Paraglider' else (3.8, -2.0)
        
        # Calculate maneuvering speed (Va) and never-exceed speed (Vne)
        va = vs * math.sqrt(pos_g) if vs > 0 else 0
        vne = max(vh * 1.1, vh + 10) # Vne is typically 1.1 * VH or VH + 10 knots, whichever is greater
        
        # Canvas margins and scaling factors
        margin_l, margin_r, margin_t, margin_b = 60, 50, 20, 50
        max_g, min_g, max_v = 4.5, -2.5, max(100, vne * 1.1) # Max G, Min G, and Max Velocity for chart scaling
        
        # Helper function to convert (velocity, G-load) to canvas coordinates
        def to_canvas(v, g):
            x = margin_l + (v / max_v) * (w - margin_l - margin_r)
            y = (h - margin_b) - ((g - min_g) / (max_g - min_g)) * (h - margin_t - margin_b)
            return x, y
        
        # Draw axes
        _, origin_y = to_canvas(0, 0)
        canvas.create_line(margin_l, margin_t, margin_l, h - margin_b, fill='grey') # Y-axis (G-load)
        canvas.create_line(margin_l, origin_y, w - margin_r, origin_y, fill='grey') # X-axis (Airspeed)
        
        # Draw G-load ticks and labels
        for g_val in range(int(min_g)+1, int(max_g)+1):
            if g_val == 0: continue
            _, y_tick = to_canvas(0, g_val)
            canvas.create_line(margin_l - 5, y_tick, margin_l + 5, y_tick, fill='grey')
            canvas.create_text(margin_l - 15, y_tick, text=f"{g_val}.0", fill="white", anchor="e")
        canvas.create_text(margin_l - 30, h / 2, text="Load Factor (g)", fill="white", angle=90) # type: ignore
        
        # Draw Airspeed ticks (every 10 knots)
        for v_tick in range(0, int(max_v), 10):
            x, _ = to_canvas(v_tick, 0)
            canvas.create_line(x, origin_y - 5, x, origin_y + 5, fill='grey')
        canvas.create_text(w - margin_r, h - 15, text="Airspeed (knots CAS)", fill="white", anchor="e")
        
        if vs <= 0: return # Cannot draw envelope if stall speed is zero
        
        # Define points for the V-g envelope polygon
        pos_stall_pts = [to_canvas(v, (v/vs)**2) for v in range(int(vs), int(va) + 1)]
        neg_stall_pts = [to_canvas(v, neg_g) for v in range(int(va), int(vs), -1)]
        p_va_pos, p_vne_pos, p_vne_neg = to_canvas(va, pos_g), to_canvas(vne, pos_g), to_canvas(vne, neg_g)
        
        envelope_poly = pos_stall_pts + [p_vne_pos, p_vne_neg] + neg_stall_pts
        
        # Draw the operating envelope fill
        canvas.create_polygon(envelope_poly, fill='#4A4A4A', stipple='gray50', outline='')
        
        # Draw envelope lines
        canvas.create_line(pos_stall_pts, fill='#E87B33', width=2) # Positive stall curve
        canvas.create_line(p_va_pos, p_vne_pos, fill='#E87B33', width=2) # Positive G limit line
        canvas.create_line(neg_stall_pts, fill='#4A90E2', width=2) # Negative stall/G limit line
        canvas.create_line(p_vne_pos, p_vne_neg, fill='#FF00FF', width=2) # Vne limit line
        
        # Draw flaps stall speed curve if applicable
        vs_flaps = calc.get('Stall Speed Flaps')
        if vs_flaps and vs_flaps > 0:
            flaps_stall_pts = [to_canvas(v, (v/vs_flaps)**2) for v in range(int(vs_flaps), int(va)+1)]
            canvas.create_line(flaps_stall_pts, fill='#87CEEB', width=2, dash=(4, 4))
        
        # Helper function to draw speed labels on the X-axis
        label_y = origin_y + 15
        def draw_speed_label(v, name):
            if v > 0:
                x, _ = to_canvas(v, 0)
                canvas.create_line(x, origin_y - 5, x, origin_y + 5, fill='white')
                canvas.create_text(x, label_y, text=f"{name}\n{v:.1f}", fill="white", anchor="n", justify='center')
        
        # Draw key speed labels
        if vs_flaps: draw_speed_label(vs_flaps, "Vs (flaps)")
        draw_speed_label(vs, "Vs (clean)")
        draw_speed_label(va, "Va")
        draw_speed_label(vne, "Vne")
        
        # Mark and label VH (max level speed)
        x_vh, y_vh = to_canvas(vh, 1.0) # VH is at 1g
        canvas.create_oval(x_vh-3, y_vh-3, x_vh+3, y_vh+3, fill='yellow', outline='')
        canvas.create_text(x_vh + 5, y_vh, text=f"VH {vh:.1f}", fill='yellow', anchor='w')
        
        # Draw vertical line from Va to positive G limit
        x_va, y_va_top = to_canvas(va, pos_g)
        canvas.create_line(x_va, origin_y, x_va, y_va_top, fill='#E87B33', dash=(2, 2))
        
        # Draw legend for envelope lines
        legend_x, legend_y = w - 190, margin_t + 15
        legend_items = [
            ("Clean Stall / Limit", "#E87B33", "solid"),
            ("Flaps Stall", "#87CEEB", "dashed"),
            ("Negative Stall / Limit", "#4A90E2", "solid"),
            ("Vne Limit", "#FF00FF", "solid"),
            ("Operating Envelope", "#4A4A4A", "fill")
        ]
        canvas.create_rectangle(legend_x - 10, legend_y - 10, legend_x + 160, legend_y + 105, fill="#383838", outline="grey")
        for i, (text, color, style) in enumerate(legend_items):
            y = legend_y + i * 20
            if style == "fill": canvas.create_rectangle(legend_x, y, legend_x + 30, y + 10, fill=color, stipple='gray50', outline='grey')
            elif style == "dashed": canvas.create_line(legend_x, y + 5, legend_x + 30, y + 5, fill=color, width=2, dash=(4,4))
            else: canvas.create_line(legend_x, y + 5, legend_x + 30, y + 5, fill=color, width=2)
            canvas.create_text(legend_x + 40, y + 5, text=text, fill="white", anchor="w")

    def update_feedback_tab(self):
        """
        Generates and displays feedback messages in the 'Issues & Feedback' tab,
        including compliance warnings against FAR Part 103 regulations (weight, speed)
        and insights on stability and handling characteristics.
        """
        self.feedback_text.config(state='normal') # Enable editing
        self.feedback_text.delete('1.0', tk.END) # Clear existing text
        
        calc = self.data['calculations']
        v_type = self.data['inputs']['vehicle_type'].get()
        feedback = []
        
        # Aerodynamics summary
        if calc.get('Total Cd0'):
            feedback.append(f"ℹ️ Aerodynamics: Base Cd0 ({calc.get('Base Cd0', 0):.3f}) + Cockpit ({calc.get('Cockpit Drag', 0):.4f}) + Tail ({calc.get('Tail Drag', 0):.4f}) = Total Cd0 ({calc.get('Total Cd0', 0):.3f}).")
        
        # Pitch Stability Feedback
        sm = calc.get("Static Margin")
        if isinstance(sm, (int, float)):
            if 5 <= sm <= 15:
                feedback.append("✔️ Pitch Stability: Good. Static margin is in the ideal 5-15% range.")
            else:
                feedback.append("❌ Pitch Stability: Poor. Static margin is outside the ideal range. Check CG and Neutral Point.")
        
        # FAR Part 103 Compliance: Empty Weight
        weight_limit = self.FAR_103_GLIDER_EMPTY_WEIGHT_LBS if v_type in ['Glider', 'Paraglider'] else self.FAR_103_EMPTY_WEIGHT_LBS
        if calc.get("Empty Weight", 0) > weight_limit:
            feedback.append(f"❌ Compliance: Empty weight exceeds Part 103 limit for this aircraft type ({weight_limit} lbs).")
        else:
            feedback.append(f"✔️ Compliance: Empty weight is within Part 103 limit for this aircraft type ({weight_limit} lbs).")
        
        # FAR Part 103 Compliance: Stall Speed
        v_stall = calc.get("Stall Speed") or calc.get("Min. Fwd Speed")
        if isinstance(v_stall, (int, float)) and v_stall > self.FAR_103_STALL_SPEED_KNOTS:
            feedback.append(f"❌ Compliance: Speed ({v_stall:.1f} knots) exceeds FAR 103 stall speed limit.")
        
        # FAR Part 103 Compliance: Max Level Speed (VH)
        vh = calc.get("VH")
        if isinstance(vh, (int, float)) and vh > self.FAR_103_MAX_SPEED_KNOTS:
            feedback.append(f"❌ Compliance: Max speed ({vh:.1f} knots) exceeds FAR 103 limit.")
        
        # Handling Characteristics (based on wing/disc loading)
        wl = calc.get("Wing Loading") or calc.get("Disc Loading")
        if isinstance(wl, (int, float)):
            if wl < 2.5:
                feedback.append("ℹ️ Handling: Very low loading suggests high sensitivity to turbulence.")
            elif wl > 5.0:
                feedback.append("ℹ️ Handling: High loading suggests higher landing speeds.")
        
        self.feedback_text.insert('1.0', "\n\n".join(feedback)) # Insert feedback messages
        self.feedback_text.config(state='disabled') # Disable editing

    def save_design(self):
        """
        Opens a file dialog to save the current design's input parameters
        (main inputs and component weights) to a JSON file.
        """
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")], title="Save Design As...")
        if not filepath: return # User cancelled
        
        # Prepare data for saving
        data_to_save = {
            'main_inputs': {key: var.get() for key, var in self.data['inputs'].items()},
            'component_weights': [{'name': e['name'].get(), 'weight': e['weight'].get(), 'arm': e['arm'].get()} for e in self.component_entries]
        }
        
        try:
            with open(filepath, 'w', encoding="utf-8") as f:
                json.dump(data_to_save, f, indent=4) # Save as pretty-printed JSON
        except (IOError, TypeError) as e:
            messagebox.showerror("Save Error", f"Failed to save file:\n{e}")

    def load_design(self):
        """
        Opens a file dialog to load design parameters from a JSON file.
        Updates the input fields with the loaded data and triggers a UI refresh.
        """
        filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")], title="Load Design")
        if not filepath: return # User cancelled
        
        try:
            with open(filepath, 'r', encoding="utf-8") as f:
                loaded_data = json.load(f)
            
            # Load main inputs
            if 'main_inputs' in loaded_data:
                for key, value in loaded_data['main_inputs'].items():
                    if key in self.data['inputs']:
                        self.data['inputs'][key].set(value)
            
            # Load component weights
            if 'component_weights' in loaded_data:
                # Iterate and update existing component entries
                for i, loaded_comp in enumerate(loaded_data['component_weights']):
                    if i < len(self.component_entries):
                        self.component_entries[i]['name'].set(loaded_comp.get('name', ''))
                        self.component_entries[i]['weight'].set(loaded_comp.get('weight', '0'))
                        self.component_entries[i]['arm'].set(loaded_comp.get('arm', '0'))
            
            self.update_ui_for_vehicle_type() # Refresh UI based on new loaded data
        except (IOError, json.JSONDecodeError, KeyError) as e:
            messagebox.showerror("Load Error", f"Failed to load or parse file:\n{e}")

    def show_about_dialog(self):
        """
        Displays an 'About ALULA' information dialog with application version
        and author details.
        """
        about_win = tk.Toplevel(self)
        about_win.title("About ALULA")
        about_win.geometry("350x200")
        about_win.resizable(False, False)
        about_win.configure(bg=self.style.lookup('TFrame', 'background'))
        about_win.transient(self) # Make dialog transient to parent window
        about_win.grab_set() # Make dialog modal
        
        ttk.Label(about_win, text="ALULA", font=('Helvetica', 16, 'bold')).pack(pady=(10,5))
        ttk.Label(about_win, text="Accessible Learning Ultralight\nLayout Assistant", justify='center').pack(pady=5)
        ttk.Label(about_win, text="www.ultralightairplaneworkshop.com", justify='center').pack(pady=5)
        ttk.Label(about_win, text="Version 0.18", font=('Helvetica', 8)).pack(pady=5)
        ttk.Button(about_win, text="Close", command=about_win.destroy).pack(pady=15)

    def show_rules_dialog(self):
        """
        Displays a summary of key FAA FAR Part 103 rules in a separate dialog.
        """
        rules_win = tk.Toplevel(self)
        rules_win.title("FAA FAR Part 103 Summary")
        rules_win.geometry("450x250")
        rules_win.resizable(False, False)
        rules_win.configure(bg=self.style.lookup('TFrame', 'background'))
        rules_win.transient(self) # Make dialog transient to parent window
        rules_win.grab_set() # Make dialog modal
        
        ttk.Label(rules_win, text="Powered Ultralight Rules (FAR 103)", font=('Helvetica', 14, 'bold')).pack(pady=(10,5))
        
        rules_frame = ttk.Frame(rules_win, padding=10)
        rules_frame.pack(fill='both', expand=True)
        
        # Define the rules to display
        rules = {
            "Max Empty Weight (Powered):": f"{self.FAR_103_EMPTY_WEIGHT_LBS} lbs",
            "Max Empty Weight (Unpowered):": f"{self.FAR_103_GLIDER_EMPTY_WEIGHT_LBS} lbs",
            "Max Fuel Capacity:": f"{self.FAR_103_MAX_FUEL_GAL} U.S. Gallons",
            "Max Speed (level flight):": f"{self.FAR_103_MAX_SPEED_KNOTS} knots (63 mph)",
            "Max Stall Speed (power-off):": f"{self.FAR_103_STALL_SPEED_KNOTS} knots (28 mph)",
            "Occupants:": "Single (1)"
        }
        
        # Populate rules into a grid layout
        for i, (key, val) in enumerate(rules.items()):
            ttk.Label(rules_frame, text=key, font=('Helvetica', 10, 'bold')).grid(row=i, column=0, sticky='w', pady=4)
            ttk.Label(rules_frame, text=val).grid(row=i, column=1, sticky='w', padx=10)
        rules_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Button(rules_win, text="Close", command=rules_win.destroy).pack(pady=10)

# Main execution block
if __name__ == "__main__":
    # Creates an instance of the application and starts the Tkinter event loop.
    try:
        app = AlulaApp()
        app.mainloop()
    except tk.TclError as ex:
        print(f"Skipping GUI execution in headless environment: {ex}")
