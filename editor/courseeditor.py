import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os

# Assuming core_logic.py is in the same directory or accessible
import core_logic

class LivygoEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Livygo Course Editor")
        self.root.geometry("1300x850") # Slightly wider for more editor space

        # --- State Variables ---
        self.current_lang = tk.StringVar()
        self.current_sub_course_id = tk.StringVar() # ID like "General"
        self.current_section_code = tk.StringVar() # Code like "S01"
        self.current_chapter_guidcode = tk.StringVar()
        
        self.active_sub_course_defs = [] # For lang/sub_courses.json
        self.active_pathway_data = []    # For lang/sc_id/pathway_structure.json
        self.active_lesson_progress_data = []
        self.active_cutscenes_data = []
        self.active_type1_data = []
        self.active_type2_data = []
        self.active_type3_data = [] 
        self.active_type4_data = []
        self.active_type5_data = []
        self.active_guidebook_data = {"categories": [], "guidebooks": []}
        self.md_editor_window = None


        # --- Main Panes ---
        top_frame = ttk.Frame(root, padding="10")
        top_frame.pack(fill=tk.X)

        left_nav_frame = ttk.Labelframe(root, text="Navigation & Global", padding="10")
        left_nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10, ipadx=5)

        right_editor_frame = ttk.Frame(root, padding="10")
        right_editor_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10, pady=10)

        # --- Top Frame Widgets (Path Selection) ---
        ttk.Label(top_frame, text="Livygo Courses Path:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.path_entry = ttk.Entry(top_frame, width=60)
        self.path_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.browse_btn = ttk.Button(top_frame, text="Browse...", command=self.browse_base_path)
        self.browse_btn.grid(row=0, column=2, padx=5, pady=5)
        self.set_path_btn = ttk.Button(top_frame, text="Set Path & Load", command=self.set_and_load_initial)
        self.set_path_btn.grid(row=0, column=3, padx=5, pady=5)
        top_frame.columnconfigure(1, weight=1)

        # --- Left Navigation Frame Widgets ---
        # Language Selection
        lang_frame = ttk.LabelFrame(left_nav_frame, text="1. Language", padding="5")
        lang_frame.pack(fill=tk.X, pady=5)
        self.lang_combobox = ttk.Combobox(lang_frame, textvariable=self.current_lang, state="readonly", postcommand=self.populate_languages_dropdown)
        self.lang_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=(0,5))
        self.lang_combobox.bind("<<ComboboxSelected>>", self.on_lang_selected)
        # ttk.Button(lang_frame, text="Add Lang", command=self.add_new_language_ui).pack(side=tk.LEFT, padx=5) # TBI

        # Sub-course Selection (based on active dirs and definitions)
        sc_frame = ttk.LabelFrame(left_nav_frame, text="2. Sub-course", padding="5")
        sc_frame.pack(fill=tk.X, pady=5)
        self.sub_course_combobox = ttk.Combobox(sc_frame, textvariable=self.current_sub_course_id, state="readonly")
        self.sub_course_combobox.pack(fill=tk.X, pady=(0,5))
        self.sub_course_combobox.bind("<<ComboboxSelected>>", self.on_sub_course_selected)
        # ttk.Button(sc_frame, text="Manage Defs", command=self.open_sub_course_def_editor).pack(fill=tk.X) # TBI

        # Section Selection
        sec_frame = ttk.LabelFrame(left_nav_frame, text="3. Section (from Pathway)", padding="5")
        sec_frame.pack(fill=tk.X, pady=5)
        self.section_combobox = ttk.Combobox(sec_frame, textvariable=self.current_section_code, state="readonly")
        self.section_combobox.pack(fill=tk.X, pady=(0,5))
        self.section_combobox.bind("<<ComboboxSelected>>", self.on_section_selected)
        # ttk.Button(sec_frame, text="Edit Pathway", command=self.open_pathway_editor).pack(fill=tk.X) # TBI

        self.load_section_btn = ttk.Button(left_nav_frame, text="Load Section Editors", command=self.load_section_editors, state=tk.DISABLED)
        self.load_section_btn.pack(fill=tk.X, pady=10)
        
        # --- Right Editor Frame Widgets (Main Notebook for Tabs) ---
        self.main_notebook = ttk.Notebook(right_editor_frame)
        self.main_notebook.pack(expand=True, fill=tk.BOTH, pady=(0,5))

        # Global/Language Level Editors Tab
        self.lang_level_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.lang_level_tab, text="Language/Course Setup")
        self.create_lang_level_editors(self.lang_level_tab)


        # Section Level Editors Tab (initially empty, populated on load_section_editors)
        self.section_level_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.section_level_tab, text="Section Content", state=tk.DISABLED) # Disabled initially
        # Section notebook will go inside section_level_tab
        self.section_notebook = ttk.Notebook(self.section_level_tab)
        self.section_notebook.pack(expand=True, fill=tk.BOTH)


        # Preview Area (Common for all editors, context will change)
        preview_labelframe = ttk.Labelframe(right_editor_frame, text="File Preview", padding="5")
        preview_labelframe.pack(expand=True, fill=tk.BOTH, pady=(5,0))
        self.preview_text = scrolledtext.ScrolledText(preview_labelframe, wrap=tk.WORD, height=8, state=tk.DISABLED)
        self.preview_text.pack(expand=True, fill=tk.BOTH)
        self.current_editing_file_label = ttk.Label(preview_labelframe, text="Previewing: None")
        self.current_editing_file_label.pack(fill=tk.X, pady=(5,0))

        # Initialize section-specific tabs (will be populated later)
        self.lp_tab = ttk.Frame(self.section_notebook)
        self.cs_tab = ttk.Frame(self.section_notebook)
        self.t1_tab = ttk.Frame(self.section_notebook)
        self.t2_tab = ttk.Frame(self.section_notebook)
        self.t3_tab = ttk.Frame(self.section_notebook)
        self.t4_tab = ttk.Frame(self.section_notebook) 
        self.t5_tab = ttk.Frame(self.section_notebook)
        # ... add more tab frames if needed

    # --- Editor Creation Methods (called once) ---
    def create_lang_level_editors(self, parent_tab):
        self.lang_level_notebook = ttk.Notebook(parent_tab)
        self.lang_level_notebook.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Tab for sub_courses.json
        sc_def_tab = ttk.Frame(self.lang_level_notebook)
        self.lang_level_notebook.add(sc_def_tab, text="Sub-course Definitions")
        self.create_sub_course_def_editor(sc_def_tab)

        # Tab for pathway_structure.json
        pathway_tab = ttk.Frame(self.lang_level_notebook)
        self.lang_level_notebook.add(pathway_tab, text="Pathway Structure (Sections)")
        self.create_pathway_structure_editor(pathway_tab)
        
        # Tab for guide_structure.json
        guidebook_tab = ttk.Frame(self.lang_level_notebook)
        self.lang_level_notebook.add(guidebook_tab, text="Guidebooks")
        self.create_guidebook_editor(guidebook_tab) # New method call
    
    def setup_section_specific_editors(self):
        """Clears and recreates tabs in section_notebook. Called by load_section_editors."""
        # Clear existing tabs if any
        for i in reversed(range(len(self.section_notebook.tabs()))):
            self.section_notebook.forget(i)

        # Recreate tab frames
        self.lp_tab = ttk.Frame(self.section_notebook)
        self.section_notebook.add(self.lp_tab, text="Lesson Progress")
        self.create_lesson_progress_editor(self.lp_tab) # LP editor UI

        self.cs_tab = ttk.Frame(self.section_notebook)
        self.section_notebook.add(self.cs_tab, text="Cutscenes")
        self.create_cutscenes_editor(self.cs_tab) # Cutscenes editor UI

        self.t1_tab = ttk.Frame(self.section_notebook)
        self.section_notebook.add(self.t1_tab, text="Type 1 Vocab")
        self.create_type1_editor(self.t1_tab) # Type 1 editor UI

        self.t2_tab = ttk.Frame(self.section_notebook)
        self.section_notebook.add(self.t2_tab, text="Type 2 Grammar")
        self.create_type2_editor(self.t2_tab)

        self.t3_tab = ttk.Frame(self.section_notebook)
        self.section_notebook.add(self.t3_tab, text="Type 3 Listening")
        self.create_type3_editor(self.t3_tab)

        self.t4_tab = ttk.Frame(self.section_notebook)
        self.section_notebook.add(self.t4_tab, text="Type 4 Sentence")
        self.create_type4_editor(self.t4_tab)

        self.t5_tab = ttk.Frame(self.section_notebook)
        self.section_notebook.add(self.t5_tab, text="Type 5 Context")
        self.create_type5_editor(self.t5_tab)
        
        self.section_notebook.bind("<<NotebookTabChanged>>", self.on_section_tab_changed)


    # --- UI Element Population and Event Handlers ---
    def browse_base_path(self):
        # ... (same as before) ...
        directory = filedialog.askdirectory()
        if directory:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, directory)

    def set_and_load_initial(self):
        # ... (same as before, but also clear lang-level editors) ...
        path = self.path_entry.get()
        if not path:
            messagebox.showerror("Error", "Please select a Livygo courses base path.")
            return
        if core_logic.set_courses_base_path(path):
            messagebox.showinfo("Success", f"Base path set to: {path}")
            self.populate_languages_dropdown()
            self.current_lang.set("")
            self.lang_combobox.set("")
            self.on_lang_selected() # This will clear downstream comboboxes and editors
        else:
            messagebox.showerror("Error", "Invalid base path.")
            
    def populate_languages_dropdown(self):
        # ... (same as before) ...
        if core_logic.CONFIG["courses_base_path"]:
            langs = core_logic.list_languages()
            self.lang_combobox['values'] = langs
        else:
            self.lang_combobox['values'] = []


    def on_lang_selected(self, event=None):
        lang = self.current_lang.get()
        # Clear downstream selections and editors
        self.current_sub_course_id.set("")
        self.sub_course_combobox.set("")
        self.sub_course_combobox['values'] = []
        self.current_section_code.set("")
        self.section_combobox.set("")
        self.section_combobox['values'] = []
        self.load_section_btn.config(state=tk.DISABLED)
        self.main_notebook.tab(self.section_level_tab, state=tk.DISABLED) # Disable section tab
        self.clear_preview_area()

        if lang:
            # Load for Language Level Editors (Sub-course defs, Pathway for selected sub-course)
            self.active_sub_course_defs = core_logic.load_sub_courses_for_lang(lang)
            self.populate_sc_def_listbox() # For sub_courses.json editor
            self.update_preview_area("sub_course_defs") # Preview sub_courses.json
            
            # Populate sub-course combobox for navigation
            active_sc_ids = core_logic.list_active_sub_course_ids_for_lang(lang)
            display_values = []
            self.sub_course_map = {}
            for sc_id in active_sc_ids:
                definition = next((item for item in self.active_sub_course_defs if item["id"] == sc_id), None)
                display_name = f"{sc_id} - {definition['title']}" if definition and definition.get('title') else sc_id
                display_values.append(display_name)
                self.sub_course_map[display_name] = sc_id
            self.sub_course_combobox['values'] = display_values

            self.active_guidebook_data = {} # Clear previous
            self.populate_gb_category_listbox() # Clear guidebook UI
            # (Guidebook data loading will happen when a sub-course is selected)
            
            # Default to first tab in lang-level notebook
            # (Assuming lang_level_notebook exists and is correctly configured)
            try:
                 first_lang_level_tab_id = self.lang_level_notebook.tabs()[0]
                 self.lang_level_notebook.select(first_lang_level_tab_id)
            except tk.TclError: # If notebook or tabs don't exist yet
                pass


        else: # No language selected
            self.active_sub_course_defs = []
            self.populate_sc_def_listbox()
            self.active_pathway_data = []
            self.populate_pathway_listbox()
            self.active_guidebook_data = {}
            self.populate_gb_category_listbox()


    def on_sub_course_selected(self, event=None): # Navigational sub-course selection
        display_name = self.sub_course_combobox.get()
        sub_course_id = self.sub_course_map.get(display_name, "")
        self.current_sub_course_id.set(sub_course_id)

        self.current_section_code.set("")
        self.section_combobox.set("")
        self.section_combobox['values'] = []
        self.load_section_btn.config(state=tk.DISABLED)
        self.main_notebook.tab(self.section_level_tab, state=tk.DISABLED)
        self.clear_preview_area()

        lang = self.current_lang.get()
        if lang and sub_course_id:
            self.active_pathway_data = core_logic.load_pathway_structure(lang, sub_course_id)
            self.populate_pathway_listbox() # For pathway_structure.json editor
            self.update_preview_area("pathway_structure")

            # Populate section combobox for navigation
            display_values = [f"{s['code']} - {s.get('title', 'Untitled Section')}" for s in self.active_pathway_data]
            self.section_map = {f"{s['code']} - {s.get('title', 'Untitled Section')}": s['code'] for s in self.active_pathway_data}
            self.section_combobox['values'] = display_values
            
            try: # Switch to pathway editor tab
                self.lang_level_notebook.select(self.pathway_tab_id_in_lang_notebook)
            except (AttributeError, tk.TclError): pass

            # Load Guidebook data for this lang/sub-course
            self.active_guidebook_data = core_logic.load_guidebook_structure(lang, sub_course_id)
            self.populate_gb_category_listbox()
            self.populate_gb_guidebook_listbox() # Assuming it lists all guidebooks initially
            # Default preview to pathway, or guidebook if pathway tab is selected
            if self.lang_level_notebook.tab(self.lang_level_notebook.select(), "text") == "Guidebooks":
                 self.update_preview_area("guidebook_structure")
            else:
                 self.update_preview_area("pathway_structure") # Default preview

            try: # Switch to pathway editor tab unless guidebook tab was already active
                current_tab_text = self.lang_level_notebook.tab(self.lang_level_notebook.select(), "text")
                if current_tab_text != "Guidebooks":
                    self.lang_level_notebook.select(self.pathway_tab_id_in_lang_notebook)
            except (AttributeError, tk.TclError): pass

        else: # No sub-course selected
            self.active_pathway_data = []
            self.populate_pathway_listbox()
            self.active_guidebook_data = {}
            self.populate_gb_category_listbox()
            self.populate_gb_guidebook_listbox()


    def on_section_selected(self, event=None): # Navigational section selection
        display_name = self.section_combobox.get()
        section_code = self.section_map.get(display_name, "")
        self.current_section_code.set(section_code)
        self.main_notebook.tab(self.section_level_tab, state=tk.DISABLED)
        self.clear_preview_area()

        if section_code:
            self.load_section_btn.config(state=tk.NORMAL)
            # Previewing lesson_progress by default when a section is chosen for loading
            # self.update_preview_area("lesson_progress") # Or handled by load_section_editors
        else:
            self.load_section_btn.config(state=tk.DISABLED)

    def clear_preview_area(self):
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.config(state=tk.DISABLED)
        self.current_editing_file_label.config(text="Previewing: None")

    def load_section_editors(self):
        lang = self.current_lang.get()
        sc_id = self.current_sub_course_id.get()
        sec_code = self.current_section_code.get()

        if not (lang and sc_id and sec_code):
            messagebox.showwarning("Warning", "Please select Language, Sub-course, and Section first.")
            return
        
        self.main_notebook.tab(self.section_level_tab, state=tk.NORMAL) # Enable the section content tab
        self.main_notebook.select(self.section_level_tab) # Switch to it

        self.setup_section_specific_editors() # Rebuild tabs inside section_notebook

        # Load Lesson Progress Data
        self.active_lesson_progress_data = core_logic.load_lesson_progress(lang, sc_id, sec_code)
        self.populate_lp_listbox()
        
        # Load Cutscenes Data
        self.active_cutscenes_data = core_logic.load_cutscenes(lang, sc_id, sec_code)
        self.populate_cs_listbox()

        # Load Type 1 Data
        self.active_type1_data = core_logic.load_lesson_data(lang, sc_id, sec_code, "type1")
        self.populate_t1_listbox()

        self.active_type2_data = core_logic.load_lesson_data(lang, sc_id, sec_code, "type2")
        self.populate_t2_listbox()

        self.active_type3_data = core_logic.load_lesson_data(lang, sc_id, sec_code, "type3")
        self.populate_t3_listbox()

        self.active_type4_data = core_logic.load_lesson_data(lang, sc_id, sec_code, "type4")
        self.populate_t4_listbox()

        self.active_type5_data = core_logic.load_lesson_data(lang, sc_id, sec_code, "type5")
        self.populate_t5_listbox()

        # Default to previewing lesson_progress and selecting its tab
        self.section_notebook.select(self.lp_tab) # Select first tab in section notebook
        self.update_preview_area("lesson_progress")


    def update_preview_area(self, file_type_key, data_override=None):
        # ... (logic similar to before, but fetch data if not overridden) ...
        lang = self.current_lang.get()
        sc_id = self.current_sub_course_id.get()
        sec_code = self.current_section_code.get()
        
        file_content_str = ""
        actual_filename = "N/A"
        data_to_display = data_override

        if not lang: # Can't form path if no lang
            self.clear_preview_area()
            return

        if file_type_key == "sub_course_defs":
            if data_to_display is None: data_to_display = self.active_sub_course_defs
            file_content_str = json.dumps({"sub_courses": data_to_display}, indent=2, ensure_ascii=False)
            actual_filename = os.path.basename(core_logic.get_sub_courses_file_path(lang))
        elif file_type_key == "pathway_structure":
            if not sc_id: return self.clear_preview_area()
            if data_to_display is None: data_to_display = self.active_pathway_data
            file_content_str = json.dumps(data_to_display, indent=2, ensure_ascii=False)
            actual_filename = os.path.basename(core_logic.get_pathway_structure_path(lang, sc_id))
        elif file_type_key == "lesson_progress":
            if not sc_id or not sec_code: return self.clear_preview_area()
            if data_to_display is None: data_to_display = self.active_lesson_progress_data
            file_content_str = json.dumps(data_to_display, indent=2, ensure_ascii=False)
            actual_filename = os.path.basename(core_logic.get_lesson_progress_path(lang, sc_id, sec_code))
        elif file_type_key == "cutscenes":
            if not sc_id or not sec_code: return self.clear_preview_area()
            if data_to_display is None: data_to_display = self.active_cutscenes_data
            file_content_str = json.dumps(data_to_display, indent=2, ensure_ascii=False)
            actual_filename = os.path.basename(core_logic.get_cutscenes_path(lang, sc_id, sec_code))
        elif file_type_key == "type1":
            if not sc_id or not sec_code: return self.clear_preview_area()
            if data_to_display is None: data_to_display = self.active_type1_data
            file_content_str = json.dumps(data_to_display, indent=2, ensure_ascii=False)
            actual_filename = os.path.basename(core_logic.get_lesson_data_file_path(lang, sc_id, sec_code, "type1"))

        elif file_type_key == "guidebook_structure": # New case
            if not sc_id: return self.clear_preview_area()
            if data_to_display is None: data_to_display = self.active_guidebook_data
            file_content_str = json.dumps(data_to_display, indent=2, ensure_ascii=False)
            if lang and sc_id: # Check if lang and sc_id are available
                actual_filename = os.path.basename(core_logic.get_guidebook_structure_path(lang, sc_id))
            else:
                actual_filename = "guide_structure.json (select lang/sub-course)"
        elif file_type_key == "type2":
            if not sc_id or not sec_code: return self.clear_preview_area()
            if data_to_display is None: data_to_display = self.active_type2_data
            file_content_str = json.dumps(data_to_display, indent=2, ensure_ascii=False)
            actual_filename = os.path.basename(core_logic.get_lesson_data_file_path(lang, sc_id, sec_code, "type2"))
        elif file_type_key == "type3":
            if not sc_id or not sec_code: return self.clear_preview_area()
            if data_to_display is None: data_to_display = self.active_type3_data
            file_content_str = json.dumps(data_to_display, indent=2, ensure_ascii=False)
            actual_filename = os.path.basename(core_logic.get_lesson_data_file_path(lang, sc_id, sec_code, "type3"))
        elif file_type_key == "type4":
            if not sc_id or not sec_code: return self.clear_preview_area()
            if data_to_display is None: data_to_display = self.active_type4_data
            file_content_str = json.dumps(data_to_display, indent=2, ensure_ascii=False)
            actual_filename = os.path.basename(core_logic.get_lesson_data_file_path(lang, sc_id, sec_code, "type4"))
        elif file_type_key == "type5":
            if not sc_id or not sec_code: return self.clear_preview_area()
            if data_to_display is None: data_to_display = self.active_type5_data
            file_content_str = json.dumps(data_to_display, indent=2, ensure_ascii=False)
            actual_filename = os.path.basename(core_logic.get_lesson_data_file_path(lang, sc_id, sec_code, "type5"))
        # Add other types...

        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, file_content_str)
        self.preview_text.config(state=tk.DISABLED)
        self.current_editing_file_label.config(text=f"Previewing: {actual_filename}")
        
    def on_section_tab_changed(self, event):
        selected_tab_text = self.section_notebook.tab(self.section_notebook.select(), "text")
        if selected_tab_text == "Lesson Progress": self.update_preview_area("lesson_progress")
        elif selected_tab_text == "Cutscenes": self.update_preview_area("cutscenes")
        elif selected_tab_text == "Type 1 Vocab": self.update_preview_area("type1")
        elif selected_tab_text == "Type 2 Grammar": self.update_preview_area("type2")
        elif selected_tab_text == "Type 3 Listening": self.update_preview_area("type3")
        elif selected_tab_text == "Type 4 Sentence": self.update_preview_area("type4")
        elif selected_tab_text == "Type 5 Context": self.update_preview_area("type5")


    # --- Sub-course Definitions Editor (for lang/sub_courses.json) ---
    def create_sub_course_def_editor(self, parent_tab):
        # This editor manages the items in the current language's sub_courses.json
        # (List of {"id": "general", "title": "General", "icon": "G"})
        editor_frame = ttk.Frame(parent_tab, padding="5")
        editor_frame.pack(expand=True, fill=tk.BOTH)
        
        ttk.Button(editor_frame, text="Refresh Definitions List", command=lambda: self.on_lang_selected()).pack(anchor="nw", pady=5)


        list_frame = ttk.Frame(editor_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))
        
        self.sc_def_listbox = tk.Listbox(list_frame, width=35, height=10)
        self.sc_def_listbox.pack(side=tk.LEFT, fill=tk.Y)
        sc_def_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.sc_def_listbox.yview)
        sc_def_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sc_def_listbox.config(yscrollcommand=sc_def_scrollbar.set)
        self.sc_def_listbox.bind('<<ListboxSelect>>', self.on_sc_def_item_select)

        btn_frame_list = ttk.Frame(list_frame)
        btn_frame_list.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame_list, text="Add New Def", command=self.add_new_sc_def_item).pack(side=tk.LEFT, padx=2)
        self.edit_sc_def_btn = ttk.Button(btn_frame_list, text="Edit Def", command=self.edit_selected_sc_def_item, state=tk.DISABLED)
        self.edit_sc_def_btn.pack(side=tk.LEFT, padx=2)
        self.delete_sc_def_btn = ttk.Button(btn_frame_list, text="Delete Def", command=self.delete_selected_sc_def_item, state=tk.DISABLED)
        self.delete_sc_def_btn.pack(side=tk.LEFT, padx=2)

        # Form for editing/adding
        self.sc_def_form_frame = ttk.Labelframe(editor_frame, text="Edit Sub-course Definition", padding="10")
        self.sc_def_form_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        self.sc_def_edit_mode = tk.BooleanVar(value=False)
        self.sc_def_current_edit_id = tk.StringVar(value="") # Store ID of item being edited

        fields = {"ID:": tk.StringVar(), "Title:": tk.StringVar(), "Icon (emoji):": tk.StringVar()}
        self.sc_def_form_vars = fields
        
        for i, (text, var) in enumerate(fields.items()):
            ttk.Label(self.sc_def_form_frame, text=text).grid(row=i, column=0, sticky="w", padx=5, pady=3)
            entry = ttk.Entry(self.sc_def_form_frame, textvariable=var, width=35)
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=3)
        
        form_btn_frame = ttk.Frame(self.sc_def_form_frame)
        form_btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        ttk.Button(form_btn_frame, text="Save Definition", command=self.save_sc_def_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(form_btn_frame, text="Cancel", command=self.hide_sc_def_form).pack(side=tk.LEFT, padx=5)
        
        self.sc_def_form_frame.columnconfigure(1, weight=1)
        self.hide_sc_def_form()

    def populate_sc_def_listbox(self):
        self.sc_def_listbox.delete(0, tk.END)
        for item in self.active_sub_course_defs:
            self.sc_def_listbox.insert(tk.END, f"{item.get('id','N/A')} - {item.get('title', 'No Title')} ({item.get('icon','')})")
        self.on_sc_def_item_select() # Update button states

    def on_sc_def_item_select(self, event=None):
        is_selected = bool(self.sc_def_listbox.curselection())
        self.edit_sc_def_btn.config(state=tk.NORMAL if is_selected else tk.DISABLED)
        self.delete_sc_def_btn.config(state=tk.NORMAL if is_selected else tk.DISABLED)

    def show_sc_def_form(self, edit_mode=False, item_data=None):
        self.sc_def_edit_mode.set(edit_mode)
        self.sc_def_form_frame.config(text="Edit Definition" if edit_mode else "Add New Definition")
        if edit_mode and item_data:
            self.sc_def_current_edit_id.set(item_data.get('id', ''))
            self.sc_def_form_vars["ID:"].set(item_data.get('id', ''))
            self.sc_def_form_vars["Title:"].set(item_data.get('title', ''))
            self.sc_def_form_vars["Icon (emoji):"].set(item_data.get('icon', ''))
        else: # Add mode
            self.sc_def_current_edit_id.set("")
            for var in self.sc_def_form_vars.values(): var.set("")
        self.sc_def_form_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)

    def hide_sc_def_form(self):
        self.sc_def_form_frame.pack_forget()
        self.sc_def_listbox.selection_clear(0, tk.END)
        self.on_sc_def_item_select()

    def add_new_sc_def_item(self): self.show_sc_def_form(edit_mode=False)
    def edit_selected_sc_def_item(self):
        idx = self.sc_def_listbox.curselection()
        if idx: self.show_sc_def_form(edit_mode=True, item_data=self.active_sub_course_defs[idx[0]])

    def delete_selected_sc_def_item(self):
        idx = self.sc_def_listbox.curselection()
        if not idx: return
        item_id = self.active_sub_course_defs[idx[0]].get('id')
        if messagebox.askyesno("Confirm Delete", f"Delete sub-course definition '{item_id}'?\n(This does not delete the content directory, only the definition in sub_courses.json)"):
            del self.active_sub_course_defs[idx[0]]
            self.save_active_sub_course_defs()

    def save_sc_def_item(self):
        new_id = self.sc_def_form_vars["ID:"].get().strip()
        if not new_id: messagebox.showerror("Error", "Sub-course ID is required."); return

        new_item = {
            "id": new_id,
            "title": self.sc_def_form_vars["Title:"].get().strip(),
            "icon": self.sc_def_form_vars["Icon (emoji):"].get().strip()
        }
        
        original_id = self.sc_def_current_edit_id.get() if self.sc_def_edit_mode.get() else None

        # Check for duplicate ID
        for i, item in enumerate(self.active_sub_course_defs):
            if item.get('id') == new_id:
                if not self.sc_def_edit_mode.get() or (self.sc_def_edit_mode.get() and item.get('id') != original_id):
                    messagebox.showerror("Error", f"Sub-course ID '{new_id}' already exists."); return
        
        if self.sc_def_edit_mode.get() and original_id: # Editing
            found = False
            for i, item in enumerate(self.active_sub_course_defs):
                if item.get('id') == original_id:
                    self.active_sub_course_defs[i] = new_item
                    found = True; break
            if not found: messagebox.showerror("Error", "Original item to edit not found."); return
        else: # Adding
            self.active_sub_course_defs.append(new_item)
        
        self.save_active_sub_course_defs()

    def save_active_sub_course_defs(self):
        lang = self.current_lang.get()
        if not lang: return
        if core_logic.save_sub_courses_for_lang(lang, self.active_sub_course_defs):
            messagebox.showinfo("Success", f"Sub-course definitions for '{lang}' saved.")
            self.populate_sc_def_listbox()
            self.hide_sc_def_form()
            self.update_preview_area("sub_course_defs")
            self.on_lang_selected() # Refresh downstream elements like sub-course combobox
        else:
            messagebox.showerror("Error", "Failed to save sub-course definitions.")


    # --- Pathway Structure Editor (for lang/sc_id/pathway_structure.json) ---
    def create_pathway_structure_editor(self, parent_tab):
        self.pathway_tab_id_in_lang_notebook = parent_tab
        editor_frame = ttk.Frame(parent_tab, padding="5")
        editor_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Button(editor_frame, text="Refresh Pathway List", command=lambda: self.on_sub_course_selected()).pack(anchor="nw", pady=5)

        list_frame = ttk.Frame(editor_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))
        
        self.pathway_listbox = tk.Listbox(list_frame, width=40, height=15) # Adjust width as needed
        self.pathway_listbox.pack(side=tk.LEFT, fill=tk.Y)
        pathway_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.pathway_listbox.yview)
        pathway_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.pathway_listbox.config(yscrollcommand=pathway_scrollbar.set)
        self.pathway_listbox.bind('<<ListboxSelect>>', self.on_pathway_item_select)

        btn_frame_list = ttk.Frame(list_frame)
        btn_frame_list.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame_list, text="Add New Section", command=self.add_new_pathway_item).pack(side=tk.LEFT, padx=2)
        self.edit_pathway_btn = ttk.Button(btn_frame_list, text="Edit Section", command=self.edit_selected_pathway_item, state=tk.DISABLED)
        self.edit_pathway_btn.pack(side=tk.LEFT, padx=2)
        self.delete_pathway_btn = ttk.Button(btn_frame_list, text="Delete Section", command=self.delete_selected_pathway_item, state=tk.DISABLED)
        self.delete_pathway_btn.pack(side=tk.LEFT, padx=2)

        # Form for pathway section
        self.pathway_form_frame = ttk.Labelframe(editor_frame, text="Edit Section Details", padding="10")
        
        self.pathway_edit_mode = tk.BooleanVar(value=False)
        self.pathway_current_edit_code = tk.StringVar(value="")

        # Basic Info Frame
        basic_info_frame = ttk.Frame(self.pathway_form_frame)
        basic_info_frame.pack(fill=tk.X, pady=5)
        self.pathway_form_vars = {} # To store StringVars for basic fields

        fields_basic = {"Code (e.g. 001):": tk.StringVar(), "Title:": tk.StringVar(), 
                        "Num Circles:": tk.StringVar(), "Default Address:": tk.StringVar()}
        for i, (text, var_obj) in enumerate(fields_basic.items()):
            ttk.Label(basic_info_frame, text=text).grid(row=i, column=0, sticky="w", padx=5, pady=2)
            entry = ttk.Entry(basic_info_frame, textvariable=var_obj, width=50) # Wider entry
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
            self.pathway_form_vars[text.split(':')[0].lower().replace(' (e.g. 001)','')] = var_obj
        basic_info_frame.columnconfigure(1, weight=1)

        # Address Map Editor Frame
        address_map_frame = ttk.Labelframe(self.pathway_form_frame, text="Address Map", padding="5")
        address_map_frame.pack(fill=tk.X, pady=5)
        self.address_map_entries_frame = ttk.Frame(address_map_frame) # Container for dynamic rows
        self.address_map_entries_frame.pack(fill=tk.X)
        ttk.Button(address_map_frame, text="Add Address Map Entry", command=self.add_address_map_row_ui).pack(pady=5)
        self.address_map_ui_rows = [] # List to hold dicts of StringVars for each row


        # Settings Editor Frame
        settings_frame = ttk.Labelframe(self.pathway_form_frame, text="Settings", padding="5")
        settings_frame.pack(fill=tk.X, pady=5)
        self.pathway_settings_vars = {
            "practicecirc": tk.BooleanVar(),
            "relearnpool": tk.BooleanVar(value=True), # Default True
            "newQuestionRatio": tk.StringVar(value="0.8"),
            "enabledQuestionTypes": {} # Dict of {type_name: BooleanVar}
        }
        ttk.Checkbutton(settings_frame, text="Practice Circle", variable=self.pathway_settings_vars["practicecirc"]).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(settings_frame, text="Relearn Pool", variable=self.pathway_settings_vars["relearnpool"]).grid(row=0, column=1, sticky="w")
        
        ttk.Label(settings_frame, text="New Q Ratio (0-1):").grid(row=1, column=0, sticky="w")
        ttk.Entry(settings_frame, textvariable=self.pathway_settings_vars["newQuestionRatio"], width=10).grid(row=1, column=1, sticky="w")

        ttk.Label(settings_frame, text="Enabled Q Types:").grid(row=2, column=0, sticky="nw")
        q_types_frame = ttk.Frame(settings_frame)
        q_types_frame.grid(row=2, column=1, sticky="w")
        all_q_types = ["type1", "type2", "type3", "type4", "type5", "type6"] # Define all possible
        for i, q_type in enumerate(all_q_types):
            var = tk.BooleanVar(value=(q_type in ["type1", "type2", "type3", "type4"])) # Default enabled
            ttk.Checkbutton(q_types_frame, text=q_type, variable=var).pack(side=tk.LEFT)
            self.pathway_settings_vars["enabledQuestionTypes"][q_type] = var
        

        # Form Buttons
        form_btn_frame = ttk.Frame(self.pathway_form_frame)
        form_btn_frame.pack(pady=10)
        ttk.Button(form_btn_frame, text="Save Section", command=self.save_pathway_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(form_btn_frame, text="Cancel", command=self.hide_pathway_form).pack(side=tk.LEFT, padx=5)
        
        self.hide_pathway_form() # Hide form initially

    def add_address_map_row_ui(self, range_start="", range_end="", path=""):
        row_frame = ttk.Frame(self.address_map_entries_frame)
        row_frame.pack(fill=tk.X, pady=2)

        vars = {"rangeStart": tk.StringVar(value=range_start),
                "rangeEnd": tk.StringVar(value=range_end),
                "path": tk.StringVar(value=path)}
        
        ttk.Label(row_frame, text="Start:").pack(side=tk.LEFT, padx=2)
        ttk.Entry(row_frame, textvariable=vars["rangeStart"], width=10).pack(side=tk.LEFT, padx=2)
        ttk.Label(row_frame, text="End:").pack(side=tk.LEFT, padx=2)
        ttk.Entry(row_frame, textvariable=vars["rangeEnd"], width=10).pack(side=tk.LEFT, padx=2)
        ttk.Label(row_frame, text="Path:").pack(side=tk.LEFT, padx=2)
        ttk.Entry(row_frame, textvariable=vars["path"], width=30).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(row_frame, text="X", width=2, command=lambda rf=row_frame: self.remove_address_map_row_ui(rf)).pack(side=tk.LEFT, padx=2)
        
        self.address_map_ui_rows.append({"frame": row_frame, "vars": vars})

    def remove_address_map_row_ui(self, row_frame_to_remove):
        for i, row_data in enumerate(self.address_map_ui_rows):
            if row_data["frame"] == row_frame_to_remove:
                del self.address_map_ui_rows[i]
                break
        row_frame_to_remove.destroy()

    def clear_address_map_ui(self):
        for row_data in self.address_map_ui_rows:
            row_data["frame"].destroy()
        self.address_map_ui_rows = []


    def show_pathway_form(self, edit_mode=False, item_data=None):
        self.pathway_edit_mode.set(edit_mode)
        self.pathway_form_frame.config(text="Edit Section Details" if edit_mode else "Add New Section Details")
        self.clear_address_map_ui() # Clear previous rows

        if edit_mode and item_data:
            self.pathway_current_edit_code.set(item_data.get('code', ''))
            self.pathway_form_vars["code"].set(item_data.get('code', ''))
            self.pathway_form_vars["title"].set(item_data.get('title', ''))
            self.pathway_form_vars["num circles"].set(str(item_data.get('numCircles', '')))
            self.pathway_form_vars["default address"].set(item_data.get('defaultAddress', ''))

            for map_entry in item_data.get("addressMap", []):
                self.add_address_map_row_ui(map_entry.get("rangeStart",""), map_entry.get("rangeEnd",""), map_entry.get("path",""))
            
            settings = item_data.get("settings", {})
            self.pathway_settings_vars["practicecirc"].set(settings.get("practicecirc", False))
            self.pathway_settings_vars["relearnpool"].set(settings.get("relearnpool", True))
            self.pathway_settings_vars["newQuestionRatio"].set(str(settings.get("newQuestionRatio", 0.8)))
            enabled_types = settings.get("enabledQuestionTypes", ["type1", "type2", "type3", "type4"])
            for q_type, var in self.pathway_settings_vars["enabledQuestionTypes"].items():
                var.set(q_type in enabled_types)
        else: # Add mode
            self.pathway_current_edit_code.set("")
            for var in self.pathway_form_vars.values(): var.set("") # Clear basic fields
            # Set default settings
            self.pathway_settings_vars["practicecirc"].set(False)
            self.pathway_settings_vars["relearnpool"].set(True)
            self.pathway_settings_vars["newQuestionRatio"].set("0.8")
            default_enabled = ["type1", "type2", "type3", "type4"]
            for q_type, var in self.pathway_settings_vars["enabledQuestionTypes"].items():
                var.set(q_type in default_enabled)

        self.pathway_form_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)


    def populate_pathway_listbox(self):
        self.pathway_listbox.delete(0, tk.END)
        for item in self.active_pathway_data:
            self.pathway_listbox.insert(tk.END, f"{item.get('code','N/A')} - {item.get('title', 'No Title')}")
        self.on_pathway_item_select()

    def on_pathway_item_select(self, event=None):
        is_selected = bool(self.pathway_listbox.curselection())
        self.edit_pathway_btn.config(state=tk.NORMAL if is_selected else tk.DISABLED)
        self.delete_pathway_btn.config(state=tk.NORMAL if is_selected else tk.DISABLED)


    def hide_pathway_form(self):
        self.pathway_form_frame.pack_forget()
        self.pathway_listbox.selection_clear(0, tk.END)
        self.on_pathway_item_select()

    def add_new_pathway_item(self): self.show_pathway_form(edit_mode=False)
    def edit_selected_pathway_item(self):
        idx = self.pathway_listbox.curselection()
        if idx: self.show_pathway_form(edit_mode=True, item_data=self.active_pathway_data[idx[0]])
    
    def delete_selected_pathway_item(self):
        idx = self.pathway_listbox.curselection()
        if not idx: return
        item_code = self.active_pathway_data[idx[0]].get('code')
        if messagebox.askyesno("Confirm Delete", f"Delete section '{item_code}' from pathway?\n(This also implies its content directory should ideally be removed manually or via another utility if no longer needed)"):
            del self.active_pathway_data[idx[0]]
            self.save_active_pathway_data()

    def save_pathway_item(self):
        code = self.pathway_form_vars["code"].get().strip()
        if not code: messagebox.showerror("Error", "Section Code is required."); return
        
        num_circles_str = self.pathway_form_vars["num circles"].get()
        try:
            num_circles = int(num_circles_str) if num_circles_str else 0
        except ValueError:
            messagebox.showerror("Error", "Number of Circles must be an integer."); return

        address_map_data = []
        for row_data in self.address_map_ui_rows:
            address_map_data.append({
                "rangeStart": row_data["vars"]["rangeStart"].get(),
                "rangeEnd": row_data["vars"]["rangeEnd"].get(),
                "path": row_data["vars"]["path"].get()
            })
        
        ratio_str = self.pathway_settings_vars["newQuestionRatio"].get()
        try:
            new_q_ratio = float(ratio_str) if ratio_str else 0.8
            if not (0.0 <= new_q_ratio <= 1.0):
                raise ValueError("Ratio out of bounds")
        except ValueError:
            messagebox.showerror("Error", "New Question Ratio must be a number between 0.0 and 1.0."); return

        enabled_q_types_data = [q_type for q_type, var in self.pathway_settings_vars["enabledQuestionTypes"].items() if var.get()]

        new_item = {
            "code": code,
            "title": self.pathway_form_vars["title"].get().strip(),
            "numCircles": num_circles,
            "defaultAddress": self.pathway_form_vars["default address"].get().strip(),
            "addressMap": address_map_data,
            "settings": {
                "practicecirc": self.pathway_settings_vars["practicecirc"].get(),
                "relearnpool": self.pathway_settings_vars["relearnpool"].get(),
                "newQuestionRatio": new_q_ratio,
                "enabledQuestionTypes": enabled_q_types_data
            }
        }

        original_code = self.pathway_current_edit_code.get() if self.pathway_edit_mode.get() else None
        
        # Check for duplicate codes (similar to other save methods)
        for i, item in enumerate(self.active_pathway_data):
            if item.get('code') == new_item['code']:
                if not self.pathway_edit_mode.get() or (self.pathway_edit_mode.get() and item.get('code') != original_code):
                    messagebox.showerror("Error", f"Section Code '{new_item['code']}' already exists."); return
        
        if self.pathway_edit_mode.get() and original_code:
            found = False
            for i, item in enumerate(self.active_pathway_data):
                if item.get('code') == original_code:
                    self.active_pathway_data[i] = new_item
                    found = True; break
            if not found: messagebox.showerror("Error", "Original section to edit not found."); return
        else:
            self.active_pathway_data.append(new_item)
        
        self.save_active_pathway_data() # This function already calls populate, hide, update_preview

    def save_active_pathway_data(self):
        lang = self.current_lang.get()
        sc_id = self.current_sub_course_id.get()
        if not (lang and sc_id): return
        if core_logic.save_pathway_structure(lang, sc_id, self.active_pathway_data):
            messagebox.showinfo("Success", f"Pathway structure for '{lang}/{sc_id}' saved.")
            self.populate_pathway_listbox()
            self.hide_pathway_form()
            self.update_preview_area("pathway_structure")
            self.on_sub_course_selected() # Refresh section combobox
        else:
            messagebox.showerror("Error", "Failed to save pathway structure.")


    # --- Lesson Progress Editor (Methods from previous version, mostly unchanged) ---
    def create_lesson_progress_editor(self, parent_tab):
        # ... (same as before) ...
        editor_frame = ttk.Frame(parent_tab, padding="5")
        editor_frame.pack(expand=True, fill=tk.BOTH)
        list_frame = ttk.Frame(editor_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))
        self.lp_listbox = tk.Listbox(list_frame, width=40, height=15)
        self.lp_listbox.pack(side=tk.LEFT, fill=tk.Y)
        lp_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.lp_listbox.yview)
        lp_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.lp_listbox.config(yscrollcommand=lp_scrollbar.set)
        self.lp_listbox.bind('<<ListboxSelect>>', self.on_lp_item_select_for_edit)
        btn_frame_list = ttk.Frame(list_frame)
        btn_frame_list.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame_list, text="Add New Circle", command=self.add_new_lp_item).pack(side=tk.LEFT, padx=2)
        self.edit_lp_btn = ttk.Button(btn_frame_list, text="Edit Selected", command=self.edit_selected_lp_item, state=tk.DISABLED)
        self.edit_lp_btn.pack(side=tk.LEFT, padx=2)
        self.delete_lp_btn = ttk.Button(btn_frame_list, text="Delete Selected", command=self.delete_selected_lp_item, state=tk.DISABLED)
        self.delete_lp_btn.pack(side=tk.LEFT, padx=2)
        self.lp_form_frame = ttk.Labelframe(editor_frame, text="Edit Circle Progress", padding="10")
        self.lp_edit_mode = tk.BooleanVar(value=False)
        self.lp_current_edit_index = tk.IntVar(value=-1)
        fields = ["Code:", "Title:", "Questions/Lesson:", "Prac. Repetition:", "Prac. Limit:", "Question Ratio (CSV):"]
        self.lp_form_entries = {}
        self.lp_form_vars = {}
        for i, field_text in enumerate(fields):
            ttk.Label(self.lp_form_frame, text=field_text).grid(row=i, column=0, sticky="w", padx=5, pady=2)
            var = tk.StringVar()
            entry = ttk.Entry(self.lp_form_frame, textvariable=var, width=40)
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
            self.lp_form_entries[field_text.split(':')[0].lower().replace('.','').replace(' (csv)','_csv')] = entry
            self.lp_form_vars[field_text.split(':')[0].lower().replace('.','').replace(' (csv)','_csv')] = var
        self.lp_practicecirc_var = tk.BooleanVar()
        ttk.Checkbutton(self.lp_form_frame, text="Practice Circle", variable=self.lp_practicecirc_var).grid(row=len(fields), column=0, columnspan=2, sticky="w", padx=5, pady=2)
        self.lp_relearnpool_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.lp_form_frame, text="Relearn Pool", variable=self.lp_relearnpool_var).grid(row=len(fields)+1, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        self.lp_allow_unlimited_var = tk.BooleanVar()
        ttk.Checkbutton(self.lp_form_frame, text="Allow Unlimited Practice Pool", variable=self.lp_allow_unlimited_var).grid(row=len(fields)+2, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        form_btn_frame = ttk.Frame(self.lp_form_frame)
        form_btn_frame.grid(row=len(fields)+3, column=0, columnspan=2, pady=10)
        ttk.Button(form_btn_frame, text="Save Circle", command=self.save_lp_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(form_btn_frame, text="Cancel", command=self.hide_lp_form).pack(side=tk.LEFT, padx=5)
        self.lp_form_frame.columnconfigure(1, weight=1)
        self.hide_lp_form()
    def populate_lp_listbox(self):
        # ... (same as before) ...
        self.lp_listbox.delete(0, tk.END)
        for item in self.active_lesson_progress_data:
            self.lp_listbox.insert(tk.END, f"{item.get('code','N/A Code')} - {item.get('title', 'Untitled')}")
        self.edit_lp_btn.config(state=tk.DISABLED)
        self.delete_lp_btn.config(state=tk.DISABLED)
    def on_lp_item_select_for_edit(self, event=None):
        # ... (same as before) ...
        if self.lp_listbox.curselection():
            self.edit_lp_btn.config(state=tk.NORMAL)
            self.delete_lp_btn.config(state=tk.NORMAL)
        else:
            self.edit_lp_btn.config(state=tk.DISABLED)
            self.delete_lp_btn.config(state=tk.DISABLED)
    def show_lp_form(self, edit_mode=False, index=-1):
        # ... (same as before) ...
        self.lp_edit_mode.set(edit_mode)
        self.lp_current_edit_index.set(index)
        self.lp_form_frame.config(text="Edit Circle Progress" if edit_mode else "Add New Circle Progress")
        if edit_mode and index >= 0 and index < len(self.active_lesson_progress_data):
            item = self.active_lesson_progress_data[index]
            self.lp_form_vars['code'].set(item.get('code', ''))
            self.lp_form_vars['title'].set(item.get('title', ''))
            self.lp_form_vars['questions/lesson'].set(str(item.get('questionsPerLesson', 10)))
            self.lp_practicecirc_var.set(item.get('practicecirc', False))
            self.lp_relearnpool_var.set(item.get('relearnpool', True))
            self.lp_allow_unlimited_var.set(item.get('allowUnlimitedPracticePool', False))
            self.lp_form_vars['prac repetition'].set(str(item.get('pracrepetition', 3)))
            self.lp_form_vars['prac limit'].set(item.get('praclimit', ''))
            self.lp_form_vars['question ratio_csv'].set(",".join(map(str, item.get('questionRatio', []))))
        else: # Add mode or error
            self.lp_form_vars['code'].set("")
            self.lp_form_vars['title'].set("")
            self.lp_form_vars['questions/lesson'].set("10")
            self.lp_practicecirc_var.set(False)
            self.lp_relearnpool_var.set(True)
            self.lp_allow_unlimited_var.set(False)
            self.lp_form_vars['prac repetition'].set("3")
            self.lp_form_vars['prac limit'].set("")
            self.lp_form_vars['question ratio_csv'].set("")
        self.lp_form_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)
    def hide_lp_form(self):
        # ... (same as before) ...
        self.lp_form_frame.pack_forget()
        self.lp_listbox.selection_clear(0, tk.END) # Deselect
        self.on_lp_item_select_for_edit() # Update button states
    def add_new_lp_item(self):
        # ... (same as before) ...
        self.show_lp_form(edit_mode=False)
    def edit_selected_lp_item(self):
        # ... (same as before) ...
        selected_indices = self.lp_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Selection Error", "Please select a circle progress item to edit.")
            return
        self.show_lp_form(edit_mode=True, index=selected_indices[0])
    def delete_selected_lp_item(self):
        # ... (same as before) ...
        selected_indices = self.lp_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Selection Error", "Please select an item to delete.")
            return
        index_to_delete = selected_indices[0]
        item_code = self.active_lesson_progress_data[index_to_delete].get('code', 'Unknown')
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete circle '{item_code}'?"):
            del self.active_lesson_progress_data[index_to_delete]
            self.save_active_lesson_progress()
            self.populate_lp_listbox()
            self.hide_lp_form()
    def save_lp_item(self):
        # ... (same as before) ...
        code = self.lp_form_vars['code'].get().strip()
        if not code: messagebox.showerror("Validation Error", "Circle Code cannot be empty."); return
        new_item = {
            "code": code, "title": self.lp_form_vars['title'].get().strip(),
            "questionsPerLesson": int(self.lp_form_vars['questions/lesson'].get() or 10),
            "practicecirc": self.lp_practicecirc_var.get(), "relearnpool": self.lp_relearnpool_var.get(),
            "allowUnlimitedPracticePool": self.lp_allow_unlimited_var.get(),
            "pracrepetition": int(self.lp_form_vars['prac repetition'].get() or 3),
            "praclimit": self.lp_form_vars['prac limit'].get().strip(),
            "questionRatio": [int(x.strip()) for x in self.lp_form_vars['question ratio_csv'].get().split(',') if x.strip().isdigit()]
        }
        index = self.lp_current_edit_index.get(); is_editing = self.lp_edit_mode.get()
        for i, item in enumerate(self.active_lesson_progress_data):
            if item.get('code') == new_item['code'] and (not is_editing or i != index) :
                messagebox.showerror("Validation Error", f"Circle Code '{new_item['code']}' already exists."); return
        if is_editing and index >= 0: self.active_lesson_progress_data[index] = new_item
        else: self.active_lesson_progress_data.append(new_item)
        if self.save_active_lesson_progress():
            self.populate_lp_listbox(); self.hide_lp_form(); self.update_preview_area("lesson_progress")
    def save_active_lesson_progress(self):
        # ... (same as before) ...
        lang = self.current_lang.get(); sc_id = self.current_sub_course_id.get(); sec_code = self.current_section_code.get()
        if core_logic.save_lesson_progress(lang, sc_id, sec_code, self.active_lesson_progress_data):
            messagebox.showinfo("Success", "Lesson progress saved successfully."); return True
        else: messagebox.showerror("Error", "Failed to save lesson progress."); return False

    # --- Cutscenes Editor ---
    def create_cutscenes_editor(self, parent_tab):
        editor_frame = ttk.Frame(parent_tab, padding="5")
        editor_frame.pack(expand=True, fill=tk.BOTH)

        # Listbox for cutscene entries (code, nocutsc, sequence)
        list_frame = ttk.Frame(editor_frame); list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))
        self.cs_listbox = tk.Listbox(list_frame, width=40, height=15); self.cs_listbox.pack(side=tk.LEFT, fill=tk.Y)
        cs_scrollbar_list = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.cs_listbox.yview); cs_scrollbar_list.pack(side=tk.RIGHT, fill=tk.Y)
        self.cs_listbox.config(yscrollcommand=cs_scrollbar_list.set)
        self.cs_listbox.bind('<<ListboxSelect>>', self.on_cs_item_select)

        btn_frame_list = ttk.Frame(list_frame); btn_frame_list.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame_list, text="Add Entry", command=self.add_new_cs_item).pack(side=tk.LEFT)
        self.edit_cs_btn = ttk.Button(btn_frame_list, text="Edit", command=self.edit_selected_cs_item, state=tk.DISABLED); self.edit_cs_btn.pack(side=tk.LEFT)
        self.delete_cs_btn = ttk.Button(btn_frame_list, text="Delete", command=self.delete_selected_cs_item, state=tk.DISABLED); self.delete_cs_btn.pack(side=tk.LEFT)

        # Form for editing a single cutscene entry
        self.cs_form_frame = ttk.Labelframe(editor_frame, text="Edit Cutscene Entry", padding="10")
        # self.cs_form_frame will be packed/unpacked by show_cs_form/hide_cs_form
        
        self.cs_edit_mode = tk.BooleanVar(); self.cs_current_edit_code = tk.StringVar()

        # Top part of the form (Code, NoCutsc checkbox)
        cs_form_top_fields = ttk.Frame(self.cs_form_frame)
        cs_form_top_fields.pack(fill=tk.X, pady=5)

        ttk.Label(cs_form_top_fields, text="Circle Code:").grid(row=0, column=0, sticky="w")
        self.cs_code_var = tk.StringVar()
        ttk.Entry(cs_form_top_fields, textvariable=self.cs_code_var, width=30).grid(row=0, column=1, sticky="ew")
        
        self.cs_nocutsc_var = tk.BooleanVar()
        self.cs_nocutsc_cb = ttk.Checkbutton(cs_form_top_fields, text="No Cutscene for this Circle", variable=self.cs_nocutsc_var, command=self.toggle_cs_sequence_editor)
        self.cs_nocutsc_cb.grid(row=1, column=0, columnspan=2, sticky="w")
        cs_form_top_fields.columnconfigure(1, weight=1)

        # --- Scrollable Frame for Sequence Pages ---
        # This is the main change area for scrollability
        scrollable_outer_frame = ttk.Frame(self.cs_form_frame, relief=tk.GROOVE, borderwidth=1)
        scrollable_outer_frame.pack(expand=True, fill=tk.BOTH, pady=5) # Let this frame expand

        cs_canvas = tk.Canvas(scrollable_outer_frame, borderwidth=0) # Canvas for scrolling
        # self.cs_sequence_frame is now the frame *inside* the canvas
        self.cs_sequence_frame = ttk.Frame(cs_canvas, padding="5") 
        
        cs_scrollbar_seq = ttk.Scrollbar(scrollable_outer_frame, orient=tk.VERTICAL, command=cs_canvas.yview)
        cs_canvas.configure(yscrollcommand=cs_scrollbar_seq.set)

        cs_scrollbar_seq.pack(side=tk.RIGHT, fill=tk.Y)
        cs_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # This creates a window in the canvas that holds self.cs_sequence_frame
        self.cs_sequence_frame_id_on_canvas = cs_canvas.create_window((0,0), window=self.cs_sequence_frame, anchor="nw") 

        def _configure_cs_sequence_frame(event):
            # Update the scrollregion of the canvas to encompass the Bbox of the frame
            cs_canvas.configure(scrollregion=cs_canvas.bbox("all"))
            # Make the frame width match the canvas width
            cs_canvas.itemconfig(self.cs_sequence_frame_id_on_canvas, width=event.width)

        def _on_mousewheel_cs(event): # For Windows/some Linux
            cs_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        def _on_mousewheel_cs_unix(event): # For some Linux/macOS
            if event.num == 4:
                cs_canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                cs_canvas.yview_scroll(1, "units")

        # Bind canvas to configure the scrollable frame and mousewheel
        cs_canvas.bind('<Configure>', _configure_cs_sequence_frame)
        self.cs_sequence_frame.bind('<Configure>', lambda e: cs_canvas.configure(scrollregion=cs_canvas.bbox("all"))) # Also when frame size changes
        cs_canvas.bind_all("<MouseWheel>", _on_mousewheel_cs, add="+") # Bind to all for simplicity, consider specific widget if issues
        cs_canvas.bind_all("<Button-4>", _on_mousewheel_cs_unix, add="+")
        cs_canvas.bind_all("<Button-5>", _on_mousewheel_cs_unix, add="+")
        # --- End Scrollable Frame Setup ---

        self.cs_add_page_btn = ttk.Button(
            self.cs_form_frame, # Parent is cs_form_frame, not scrollable_outer_frame
            text="Add Sequence Page",
            command=lambda: self.add_cs_sequence_page_ui(from_button_click=True)
        )
        self.cs_add_page_btn.pack(pady=5) # Pack below the scrollable area

        form_btn_frame = ttk.Frame(self.cs_form_frame); form_btn_frame.pack(pady=10)
        ttk.Button(form_btn_frame, text="Save Entry", command=self.save_cs_item).pack(side=tk.LEFT)
        ttk.Button(form_btn_frame, text="Cancel", command=self.hide_cs_form).pack(side=tk.LEFT)
        
        self.hide_cs_form() # Hide the whole cs_form_frame initially

    def populate_cs_listbox(self):
        self.cs_listbox.delete(0, tk.END)
        for item in self.active_cutscenes_data:
            status = "Disabled" if item.get('nocutsc') else f"{len(item.get('sequence',[]))} pages"
            self.cs_listbox.insert(tk.END, f"{item.get('code','N/A Code')} ({status})")
        self.on_cs_item_select()

    def on_cs_item_select(self, event=None):
        is_selected = bool(self.cs_listbox.curselection())
        self.edit_cs_btn.config(state=tk.NORMAL if is_selected else tk.DISABLED)
        self.delete_cs_btn.config(state=tk.NORMAL if is_selected else tk.DISABLED)

    def show_cs_form(self, edit_mode=False, item_data=None):
        self.cs_edit_mode.set(edit_mode)
        self.cs_form_frame.config(text="Edit Cutscene Entry" if edit_mode else "Add New Cutscene Entry")
        if edit_mode and item_data:
            self.cs_current_edit_code.set(item_data.get('code',''))
            self.cs_code_var.set(item_data.get('code',''))
            self.cs_nocutsc_var.set(item_data.get('nocutsc', False))
            self.rebuild_cs_sequence_ui(item_data.get('sequence', []))
        else:
            self.cs_current_edit_code.set('')
            self.cs_code_var.set('')
            self.cs_nocutsc_var.set(False)
            self.rebuild_cs_sequence_ui([])
        self.toggle_cs_sequence_editor()
        self.cs_form_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)

    def hide_cs_form(self): self.cs_form_frame.pack_forget(); self.on_cs_item_select()
    def add_new_cs_item(self): self.show_cs_form(False)
    def edit_selected_cs_item(self):
        idx = self.cs_listbox.curselection()
        if idx: self.show_cs_form(True, self.active_cutscenes_data[idx[0]])
    
    def delete_selected_cs_item(self):
        idx = self.cs_listbox.curselection();
        if not idx: return
        item_code = self.active_cutscenes_data[idx[0]].get('code')
        if messagebox.askyesno("Confirm", f"Delete cutscene for '{item_code}'?"):
            del self.active_cutscenes_data[idx[0]]
            self.save_active_cutscenes()
    
    def toggle_cs_sequence_editor(self):
        # Instead of grid_remove/grid on cs_sequence_frame, we control visibility of its parent
        # or just the elements within if cs_form_frame itself is already managed
        scrollable_parent = self.cs_sequence_frame.master.master # This should be scrollable_outer_frame
        
        if self.cs_nocutsc_var.get():
            scrollable_parent.pack_forget() # Hide the scrollable area
            self.cs_add_page_btn.pack_forget() 
        else:
            scrollable_parent.pack(expand=True, fill=tk.BOTH, pady=5) # Show scrollable area
            self.cs_add_page_btn.pack(pady=5)

    def rebuild_cs_sequence_ui(self, sequence_data):
        # Clear previous widgets from self.cs_sequence_frame (the one inside canvas)
        for widget in self.cs_sequence_frame.winfo_children(): widget.destroy()
        self.cs_sequence_text_widgets = []
        
        for i, page_data in enumerate(sequence_data):
            page_frame = ttk.Frame(self.cs_sequence_frame, relief=tk.GROOVE, borderwidth=1, padding=3)
            
            ttk.Label(page_frame, text=f"Page {i + 1}:").pack(anchor="nw") # Use i for correct numbering
            text_widget = scrolledtext.ScrolledText(page_frame, height=4, width=45, wrap=tk.WORD)
            text_widget.insert(tk.END, "\n".join(page_data.get('lines',[])))
            text_widget.pack(expand=True, fill=tk.BOTH, pady=2)
            self.cs_sequence_text_widgets.append(text_widget)

            remove_btn = ttk.Button(page_frame, text="Remove Page", command=lambda pf=page_frame, tw=text_widget: self.remove_cs_sequence_page_ui(pf, tw))
            remove_btn.pack(anchor="ne", pady=2)

            page_frame.pack(fill=tk.X, pady=3, padx=2) # Add some internal padding
        # self.update_cs_page_labels() # Not strictly needed if labels are set on creation
        # The canvas scrollregion will update due to self.cs_sequence_frame.bind('<Configure>')

    def add_cs_sequence_page_ui(self, lines_list=None, from_button_click=False):
        if lines_list is None: lines_list = ["New line on new page."]
        
        page_idx = len(self.cs_sequence_text_widgets) # Index for the new page
        page_frame = ttk.Frame(self.cs_sequence_frame, relief=tk.GROOVE, borderwidth=1, padding=3)
        
        ttk.Label(page_frame, text=f"Page {page_idx + 1}:").pack(anchor="nw")
        text_widget = scrolledtext.ScrolledText(page_frame, height=4, width=45, wrap=tk.WORD)
        text_widget.insert(tk.END, "\n".join(lines_list))
        text_widget.pack(expand=True, fill=tk.BOTH, pady=2)
        self.cs_sequence_text_widgets.append(text_widget)

        remove_btn = ttk.Button(page_frame, text="Remove Page", command=lambda pf=page_frame, tw=text_widget: self.remove_cs_sequence_page_ui(pf, tw))
        remove_btn.pack(anchor="ne", pady=2)

        page_frame.pack(fill=tk.X, pady=3, padx=2)
        # self.update_cs_page_labels() # update_cs_page_labels will re-label all.
        # Canvas scrollregion update is handled by frame's configure binding.


    def remove_cs_sequence_page_ui(self, page_frame_to_remove, text_widget_to_remove):
        if text_widget_to_remove in self.cs_sequence_text_widgets:
            self.cs_sequence_text_widgets.remove(text_widget_to_remove)
        
        page_frame_to_remove.destroy()
        self.update_cs_page_labels() # Re-label the remaining pages

    def update_cs_page_labels(self):
        # This needs to iterate through frames and update their labels based on new order
        # Assuming each page_frame's first child is the Label
        for i, page_frame_widget in enumerate(self.cs_sequence_frame.winfo_children()):
            if isinstance(page_frame_widget, ttk.Frame) and page_frame_widget.winfo_children():
                label_candidate = page_frame_widget.winfo_children()[0]
                if isinstance(label_candidate, ttk.Label):
                    label_candidate.config(text=f"Page {i + 1}:")
        
    # Adjust the "Add Sequence Page" button in create_cutscenes_editor
    # ... inside create_cutscenes_editor ...
        # ttk.Button(self.cs_form_frame, text="Add Sequence Page", command=self.add_cs_sequence_page_ui).grid(row=3, column=0, pady=5)
        # Change to:

    def update_cs_page_labels(self):
        for i, page_frame in enumerate(self.cs_sequence_frame.winfo_children()):
            if page_frame.winfo_children(): # Check if frame has children
                 # Assuming the label is the first child
                label_widget = page_frame.winfo_children()[0]
                if isinstance(label_widget, ttk.Label):
                    label_widget.config(text=f"Page {i+1}:")


    def save_cs_item(self):
        code = self.cs_code_var.get().strip()
        if not code: messagebox.showerror("Error", "Circle Code is required."); return

        new_sequence = []
        if not self.cs_nocutsc_var.get():
            for text_widget in self.cs_sequence_text_widgets:
                lines = text_widget.get(1.0, tk.END).strip().split('\n')
                new_sequence.append({"lines": [line.strip() for line in lines if line.strip()]})
        
        new_item = {"code": code, "nocutsc": self.cs_nocutsc_var.get(), "sequence": new_sequence}
        
        original_code = self.cs_current_edit_code.get() if self.cs_edit_mode.get() else None
        # ... (duplicate check and add/update logic similar to LP or SC Defs) ...
        is_editing = self.cs_edit_mode.get()
        found_existing = False
        for i, item in enumerate(self.active_cutscenes_data):
            if item.get('code') == new_item['code']:
                if not is_editing or (is_editing and item.get('code') != original_code) :
                    messagebox.showerror("Error", f"Cutscene Code '{new_item['code']}' already exists."); return
                if is_editing and item.get('code') == original_code: # This is the item we are editing
                     self.active_cutscenes_data[i] = new_item
                     found_existing = True; break
        if not found_existing and is_editing: # Trying to edit but original code not found
            messagebox.showerror("Error", f"Original cutscene with code '{original_code}' not found to update."); return
        if not is_editing: # Adding new
             self.active_cutscenes_data.append(new_item)
        elif is_editing and not found_existing and new_item['code'] != original_code : # Editing and changing code to a new unique one
            # This case needs careful handling: is it an update of old to new, or add new and delete old?
            # For simplicity, let's assume if original_code is set, we find and update it. If not, we add.
            # If original_code not found, it's effectively an add if the new code is unique.
            # The current logic for editing finds by original_code. If that's changed, it becomes an add.
            # We might need to remove the old entry if code was changed.
             # For now: if original_code differs from new_item['code'] and new_item['code'] is unique, treat as add.
            # This means the user has to manually delete the old one if they *changed* the code.
            # A better UI would handle renaming.
            self.active_cutscenes_data.append(new_item) # simplified
        
        self.save_active_cutscenes()

    def save_active_cutscenes(self):
        lang=self.current_lang.get(); sc_id=self.current_sub_course_id.get(); sec_code=self.current_section_code.get()
        if core_logic.save_cutscenes(lang, sc_id, sec_code, self.active_cutscenes_data):
            messagebox.showinfo("Success", "Cutscenes saved."); self.populate_cs_listbox(); self.hide_cs_form(); self.update_preview_area("cutscenes")
        else: messagebox.showerror("Error", "Failed to save cutscenes.")

    # --- Type 1 Vocabulary Editor ---
    def create_type1_editor(self, parent_tab):
        editor_frame = ttk.Frame(parent_tab, padding="5"); editor_frame.pack(expand=True, fill=tk.BOTH)
        # Listbox
        list_frame = ttk.Frame(editor_frame); list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))
        self.t1_listbox = tk.Listbox(list_frame, width=50, height=15); self.t1_listbox.pack(side=tk.LEFT, fill=tk.Y)
        # ... (scrollbar, bind, buttons: Add, Edit, Delete) ...
        t1_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.t1_listbox.yview); t1_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.t1_listbox.config(yscrollcommand=t1_scrollbar.set)
        self.t1_listbox.bind('<<ListboxSelect>>', self.on_t1_item_select)

        btn_frame_list = ttk.Frame(list_frame); btn_frame_list.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame_list, text="Add Vocab", command=self.add_new_t1_item).pack(side=tk.LEFT)
        self.edit_t1_btn = ttk.Button(btn_frame_list, text="Edit", command=self.edit_selected_t1_item, state=tk.DISABLED); self.edit_t1_btn.pack(side=tk.LEFT)
        self.delete_t1_btn = ttk.Button(btn_frame_list, text="Delete", command=self.delete_selected_t1_item, state=tk.DISABLED); self.delete_t1_btn.pack(side=tk.LEFT)

        # Form
        self.t1_form_frame = ttk.Labelframe(editor_frame, text="Edit Vocabulary Item", padding="10")
        self.t1_edit_mode = tk.BooleanVar(); self.t1_current_edit_idx = tk.IntVar(value=-1)
        
        fields = {"Circle Code:":tk.StringVar(), "Word:":tk.StringVar(), "Translation:":tk.StringVar()}
        self.t1_form_vars = fields
        for i, (text, var) in enumerate(fields.items()):
            ttk.Label(self.t1_form_frame, text=text).grid(row=i, column=0, sticky="w")
            ttk.Entry(self.t1_form_frame, textvariable=var, width=40).grid(row=i, column=1, sticky="ew")
        
        form_btn_frame = ttk.Frame(self.t1_form_frame); form_btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        ttk.Button(form_btn_frame, text="Save Item", command=self.save_t1_item).pack(side=tk.LEFT)
        ttk.Button(form_btn_frame, text="Cancel", command=self.hide_t1_form).pack(side=tk.LEFT)
        self.t1_form_frame.columnconfigure(1, weight=1)
        self.hide_t1_form()

    def populate_t1_listbox(self):
        self.t1_listbox.delete(0, tk.END)
        for item in self.active_type1_data:
            self.t1_listbox.insert(tk.END, f"C:{item.get('code','?')} W:{item.get('word','?')} T:{item.get('translation','?')}")
        self.on_t1_item_select()

    def on_t1_item_select(self, event=None):
        is_selected = bool(self.t1_listbox.curselection())
        self.edit_t1_btn.config(state=tk.NORMAL if is_selected else tk.DISABLED)
        self.delete_t1_btn.config(state=tk.NORMAL if is_selected else tk.DISABLED)

    def show_t1_form(self, edit_mode=False, item_data=None, index=-1):
        self.t1_edit_mode.set(edit_mode); self.t1_current_edit_idx.set(index)
        self.t1_form_frame.config(text="Edit Vocab Item" if edit_mode else "Add New Vocab Item")
        if edit_mode and item_data:
            self.t1_form_vars["Circle Code:"].set(item_data.get('code',''))
            self.t1_form_vars["Word:"].set(item_data.get('word',''))
            self.t1_form_vars["Translation:"].set(item_data.get('translation',''))
        else:
            self.t1_form_vars["Circle Code:"].set(self.current_section_code.get() + "XXX") # Suggest a code
            self.t1_form_vars["Word:"].set('')
            self.t1_form_vars["Translation:"].set('')
        self.t1_form_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)

    def hide_t1_form(self): self.t1_form_frame.pack_forget(); self.on_t1_item_select()
    def add_new_t1_item(self): self.show_t1_form(False)
    def edit_selected_t1_item(self):
        idx = self.t1_listbox.curselection()
        if idx: self.show_t1_form(True, self.active_type1_data[idx[0]], idx[0])
    
    def delete_selected_t1_item(self):
        idx = self.t1_listbox.curselection();
        if not idx: return
        item_word = self.active_type1_data[idx[0]].get('word')
        if messagebox.askyesno("Confirm", f"Delete vocab '{item_word}'?"):
            del self.active_type1_data[idx[0]]
            self.save_active_type1_data()

    def save_t1_item(self):
        code = self.t1_form_vars["Circle Code:"].get().strip()
        word = self.t1_form_vars["Word:"].get().strip()
        trans = self.t1_form_vars["Translation:"].get().strip()
        if not (code and word and trans): messagebox.showerror("Error", "All fields required for Type 1."); return
        
        new_item = {"code": code, "word": word, "translation": trans}
        idx = self.t1_current_edit_idx.get()
        if self.t1_edit_mode.get() and idx != -1:
            self.active_type1_data[idx] = new_item
        else: # Adding (no duplicate check for simple Type 1 items in this demo)
            self.active_type1_data.append(new_item)
        self.save_active_type1_data()

    def save_active_type1_data(self):
        lang=self.current_lang.get(); sc_id=self.current_sub_course_id.get(); sec_code=self.current_section_code.get()
        if core_logic.save_lesson_data(lang, sc_id, sec_code, "type1", self.active_type1_data):
            messagebox.showinfo("Success", "Type 1 vocabulary saved.")
            self.populate_t1_listbox(); self.hide_t1_form(); self.update_preview_area("type1")
        else: messagebox.showerror("Error", "Failed to save Type 1 vocabulary.")

    # --- Type 2 Grammar Editor ---
    def create_type2_editor(self, parent_tab):
        editor_frame = ttk.Frame(parent_tab, padding="5"); editor_frame.pack(expand=True, fill=tk.BOTH)
        # Listbox
        list_frame = ttk.Frame(editor_frame); list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))
        self.t2_listbox = tk.Listbox(list_frame, width=60, height=15); self.t2_listbox.pack(side=tk.LEFT, fill=tk.Y)
        t2_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.t2_listbox.yview); t2_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.t2_listbox.config(yscrollcommand=t2_scrollbar.set)
        self.t2_listbox.bind('<<ListboxSelect>>', self.on_t2_item_select)

        btn_frame_list = ttk.Frame(list_frame); btn_frame_list.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame_list, text="Add Grammar", command=self.add_new_t2_item).pack(side=tk.LEFT)
        self.edit_t2_btn = ttk.Button(btn_frame_list, text="Edit", command=self.edit_selected_t2_item, state=tk.DISABLED); self.edit_t2_btn.pack(side=tk.LEFT)
        self.delete_t2_btn = ttk.Button(btn_frame_list, text="Delete", command=self.delete_selected_t2_item, state=tk.DISABLED); self.delete_t2_btn.pack(side=tk.LEFT)

        # Form
        self.t2_form_frame = ttk.Labelframe(editor_frame, text="Edit Type 2 Grammar Item", padding="10")
        self.t2_edit_mode = tk.BooleanVar(); self.t2_current_edit_idx = tk.IntVar(value=-1)
        
        self.t2_form_vars = {
            "code": tk.StringVar(), "sentence": tk.StringVar(), "translation": tk.StringVar(),
            "blank": tk.StringVar(), "possibleAnswers": tk.StringVar() # Comma-separated for UI
        }
        row = 0
        ttk.Label(self.t2_form_frame, text="Circle Code:").grid(row=row, column=0, sticky="w");
        ttk.Entry(self.t2_form_frame, textvariable=self.t2_form_vars["code"], width=40).grid(row=row, column=1, sticky="ew"); row+=1
        ttk.Label(self.t2_form_frame, text="Sentence (use [__]):").grid(row=row, column=0, sticky="w");
        ttk.Entry(self.t2_form_frame, textvariable=self.t2_form_vars["sentence"], width=40).grid(row=row, column=1, sticky="ew"); row+=1
        ttk.Label(self.t2_form_frame, text="Translation:").grid(row=row, column=0, sticky="w");
        ttk.Entry(self.t2_form_frame, textvariable=self.t2_form_vars["translation"], width=40).grid(row=row, column=1, sticky="ew"); row+=1
        ttk.Label(self.t2_form_frame, text="Blank (Correct Answer):").grid(row=row, column=0, sticky="w");
        ttk.Entry(self.t2_form_frame, textvariable=self.t2_form_vars["blank"], width=40).grid(row=row, column=1, sticky="ew"); row+=1
        ttk.Label(self.t2_form_frame, text="Possible Answers (CSV):").grid(row=row, column=0, sticky="w");
        ttk.Entry(self.t2_form_frame, textvariable=self.t2_form_vars["possibleAnswers"], width=40).grid(row=row, column=1, sticky="ew"); row+=1
        
        form_btn_frame = ttk.Frame(self.t2_form_frame); form_btn_frame.grid(row=row, column=0, columnspan=2, pady=10)
        ttk.Button(form_btn_frame, text="Save Item", command=self.save_t2_item).pack(side=tk.LEFT)
        ttk.Button(form_btn_frame, text="Cancel", command=self.hide_t2_form).pack(side=tk.LEFT)
        self.t2_form_frame.columnconfigure(1, weight=1)
        self.hide_t2_form()

    def populate_t2_listbox(self):
        self.t2_listbox.delete(0, tk.END)
        for item in self.active_type2_data: self.t2_listbox.insert(tk.END, f"C:{item.get('code','?')} S: {item.get('sentence','?'):.40s}...")
        self.on_t2_item_select()
    def on_t2_item_select(self,ev=None): s=bool(self.t2_listbox.curselection()); self.edit_t2_btn.config(state=tk.NORMAL if s else tk.DISABLED); self.delete_t2_btn.config(state=tk.NORMAL if s else tk.DISABLED)
    def show_t2_form(self, edit=False, item=None, idx=-1):
        self.t2_edit_mode.set(edit); self.t2_current_edit_idx.set(idx)
        self.t2_form_frame.config(text="Edit" if edit else "Add New")
        if edit and item:
            for key, var in self.t2_form_vars.items():
                if key == "possibleAnswers": var.set(", ".join(item.get(key,[])))
                else: var.set(item.get(key,''))
        else:
            for key, var in self.t2_form_vars.items(): var.set('')
            self.t2_form_vars["code"].set(self.current_section_code.get() + "XXX")
        self.t2_form_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)
    def hide_t2_form(self): self.t2_form_frame.pack_forget(); self.on_t2_item_select()
    def add_new_t2_item(self): self.show_t2_form(False)
    def edit_selected_t2_item(self): 
        idx=self.t2_listbox.curselection()
        if idx:
            self.show_t2_form(True,self.active_type2_data[idx[0]],idx[0])
    def delete_selected_t2_item(self):
        idx=self.t2_listbox.curselection();
        if not idx: return
        if messagebox.askyesno("Confirm", f"Delete Type 2: '{self.active_type2_data[idx[0]].get('sentence','')[:30]}...'?"):
            del self.active_type2_data[idx[0]]; self.save_active_type_data("type2")
    def save_t2_item(self):
        item = {k: v.get().strip() for k,v in self.t2_form_vars.items() if k != "possibleAnswers"}
        item["possibleAnswers"] = [s.strip() for s in self.t2_form_vars["possibleAnswers"].get().split(',') if s.strip()]
        if not item["code"] or not item["sentence"] or not item["blank"]: messagebox.showerror("Error", "Code, Sentence, Blank are required."); return
        idx = self.t2_current_edit_idx.get()
        if self.t2_edit_mode.get() and idx != -1: self.active_type2_data[idx] = item
        else: self.active_type2_data.append(item)
        self.save_active_type_data("type2")
    
    # --- Generic Save for Type Data ---
    def save_active_type_data(self, type_key): # e.g., "type1", "type2"
        lang=self.current_lang.get(); sc_id=self.current_sub_course_id.get(); sec_code=self.current_section_code.get()
        data_map = { "type1": self.active_type1_data, "type2": self.active_type2_data,
                     "type3": self.active_type3_data, "type4": self.active_type4_data,
                     "type5": self.active_type5_data }
        listbox_map = { "type1": self.populate_t1_listbox, "type2": self.populate_t2_listbox,
                        "type3": self.populate_t3_listbox, "type4": self.populate_t4_listbox,
                        "type5": self.populate_t5_listbox }
        form_hide_map = { "type1": self.hide_t1_form, "type2": self.hide_t2_form,
                          "type3": self.hide_t3_form, "type4": self.hide_t4_form,
                          "type5": self.hide_t5_form }

        if core_logic.save_lesson_data(lang, sc_id, sec_code, type_key, data_map[type_key]):
            messagebox.showinfo("Success", f"{type_key.capitalize()} data saved.")
            if listbox_map.get(type_key): listbox_map[type_key]()
            if form_hide_map.get(type_key): form_hide_map[type_key]()
            self.update_preview_area(type_key)
        else: messagebox.showerror("Error", f"Failed to save {type_key.capitalize()} data.")


    # --- Type 3 Listening Editor ---
    def create_type3_editor(self, parent_tab):
        editor_frame = ttk.Frame(parent_tab, padding="5"); editor_frame.pack(expand=True, fill=tk.BOTH)
        list_frame = ttk.Frame(editor_frame); list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))
        self.t3_listbox = tk.Listbox(list_frame, width=50, height=15); self.t3_listbox.pack(side=tk.LEFT, fill=tk.Y)
        # ... scrollbar, bind, buttons ...
        t3_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.t3_listbox.yview); t3_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.t3_listbox.config(yscrollcommand=t3_scrollbar.set)
        self.t3_listbox.bind('<<ListboxSelect>>', self.on_t3_item_select)
        btn_frame_list = ttk.Frame(list_frame); btn_frame_list.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame_list, text="Add Listening", command=self.add_new_t3_item).pack(side=tk.LEFT)
        self.edit_t3_btn = ttk.Button(btn_frame_list, text="Edit", command=self.edit_selected_t3_item, state=tk.DISABLED); self.edit_t3_btn.pack(side=tk.LEFT)
        self.delete_t3_btn = ttk.Button(btn_frame_list, text="Delete", command=self.delete_selected_t3_item, state=tk.DISABLED); self.delete_t3_btn.pack(side=tk.LEFT)


        self.t3_form_frame = ttk.Labelframe(editor_frame, text="Edit Type 3 Listening Item", padding="10")
        self.t3_edit_mode = tk.BooleanVar(); self.t3_current_edit_idx = tk.IntVar(value=-1)
        self.t3_form_vars = {"code": tk.StringVar(), "audio": tk.StringVar(), "answers_selection": tk.StringVar(), "answers_text": tk.StringVar()}
        
        row=0
        ttk.Label(self.t3_form_frame, text="Code:").grid(row=row, column=0, sticky="w"); ttk.Entry(self.t3_form_frame, textvariable=self.t3_form_vars["code"]).grid(row=row, column=1, sticky="ew"); row+=1
        ttk.Label(self.t3_form_frame, text="Audio Path:").grid(row=row, column=0, sticky="w");
        audio_frame = ttk.Frame(self.t3_form_frame); audio_frame.grid(row=row, column=1, sticky="ew")
        ttk.Entry(audio_frame, textvariable=self.t3_form_vars["audio"], width=30).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(audio_frame, text="Browse", command=lambda: self.browse_audio_file(self.t3_form_vars["audio"])).pack(side=tk.LEFT, padx=2); row+=1
        ttk.Label(self.t3_form_frame, text="Selection Ans (CSV):").grid(row=row, column=0, sticky="w"); ttk.Entry(self.t3_form_frame, textvariable=self.t3_form_vars["answers_selection"]).grid(row=row, column=1, sticky="ew"); row+=1
        ttk.Label(self.t3_form_frame, text="Text Ans (CSV):").grid(row=row, column=0, sticky="w"); ttk.Entry(self.t3_form_frame, textvariable=self.t3_form_vars["answers_text"]).grid(row=row, column=1, sticky="ew"); row+=1
        
        form_btn_frame = ttk.Frame(self.t3_form_frame); form_btn_frame.grid(row=row, column=0, columnspan=2, pady=10)
        ttk.Button(form_btn_frame, text="Save", command=self.save_t3_item).pack(side=tk.LEFT)
        ttk.Button(form_btn_frame, text="Cancel", command=self.hide_t3_form).pack(side=tk.LEFT)
        self.t3_form_frame.columnconfigure(1, weight=1); self.hide_t3_form()

    def browse_audio_file(self, string_var_to_set):
        lang=self.current_lang.get(); sc_id=self.current_sub_course_id.get(); sec_code=self.current_section_code.get()
        if not (lang and sc_id and sec_code):
            messagebox.showwarning("Context Missing", "Select Language, Sub-course, and Section first.")
            return
        # Default to section's audiofiles, then courses_base_path if not found
        initial_dir = os.path.join(core_logic.get_section_base_path(lang, sc_id, sec_code), "audiofiles")
        if not os.path.isdir(initial_dir): initial_dir = core_logic.CONFIG["courses_base_path"]
        
        filepath = filedialog.askopenfilename(
            initialdir=initial_dir,
            title="Select Audio File",
            filetypes=(("Audio Files", "*.wav *.mp3 *.ogg"), ("All files", "*.*"))
        )
        if filepath:
            # Try to make path relative to section's audiofiles/ or lang/subcourse/audiofiles/ or even courses_base_path/audiofiles
            # This needs a robust path relativization logic based on your conventions
            # For simplicity, store path relative to section's audiofiles if possible
            sec_audio_path = os.path.join(core_logic.get_section_base_path(lang, sc_id, sec_code), "audiofiles")
            try:
                rel_path = os.path.relpath(filepath, sec_audio_path)
                if not rel_path.startswith(".."): # If it's within or below
                    string_var_to_set.set(rel_path.replace(os.sep, "/")) # Use forward slashes
                    return
            except ValueError: pass # Different drive
            
            # Fallback: just use filename if in a common audio directory or store full path if desperate
            # This part depends heavily on your project's audio file organization.
            # For now, let's assume we store it relative to section/audiofiles if possible
            # or just the filename if user selects from elsewhere (less ideal)
            messagebox.showwarning("Path Warning", f"Storing audio path as '{os.path.basename(filepath)}'. Ensure it's correctly placed for the game.")
            string_var_to_set.set(os.path.basename(filepath)) # Simplified fallback

    def populate_t3_listbox(self):
        self.t3_listbox.delete(0,tk.END)
        for item in self.active_type3_data: self.t3_listbox.insert(tk.END, f"C:{item.get('code','?')} A: {item.get('audio','?'):.40s}...")
        self.on_t3_item_select()
    def on_t3_item_select(self,ev=None): s=bool(self.t3_listbox.curselection()); self.edit_t3_btn.config(state=tk.NORMAL if s else tk.DISABLED); self.delete_t3_btn.config(state=tk.NORMAL if s else tk.DISABLED)
    def show_t3_form(self, edit=False, item=None, idx=-1):
        self.t3_edit_mode.set(edit); self.t3_current_edit_idx.set(idx); self.t3_form_frame.config(text="Edit" if edit else "Add")
        if edit and item:
            self.t3_form_vars["code"].set(item.get('code',''))
            self.t3_form_vars["audio"].set(item.get('audio',''))
            self.t3_form_vars["answers_selection"].set(", ".join(item.get('answers',{}).get('selection',[])))
            self.t3_form_vars["answers_text"].set(", ".join(item.get('answers',{}).get('text',[])))
        else:
            for k,v in self.t3_form_vars.items(): v.set('')
            self.t3_form_vars["code"].set(self.current_section_code.get() + "XXX")
        self.t3_form_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)
    def hide_t3_form(self): self.t3_form_frame.pack_forget(); self.on_t3_item_select()
    def add_new_t3_item(self): self.show_t3_form(False)
    def edit_selected_t3_item(self): 
        idx=self.t3_listbox.curselection()
        if idx:
            self.show_t3_form(True,self.active_type3_data[idx[0]],idx[0])
    def delete_selected_t3_item(self):
        idx=self.t3_listbox.curselection()
        if not idx: return
        if messagebox.askyesno("Confirm", f"Delete Type 3: '{self.active_type3_data[idx[0]].get('audio','')}...'?"):
            del self.active_type3_data[idx[0]]; self.save_active_type_data("type3")
    def save_t3_item(self):
        item = {"code": self.t3_form_vars["code"].get().strip(), "audio": self.t3_form_vars["audio"].get().strip()}
        if not item["code"] or not item["audio"]: messagebox.showerror("Error", "Code and Audio Path are required."); return
        item["answers"] = {
            "selection": [s.strip() for s in self.t3_form_vars["answers_selection"].get().split(',') if s.strip()],
            "text": [s.strip() for s in self.t3_form_vars["answers_text"].get().split(',') if s.strip()]
        }
        idx = self.t3_current_edit_idx.get()
        if self.t3_edit_mode.get() and idx != -1: self.active_type3_data[idx] = item
        else: self.active_type3_data.append(item)
        self.save_active_type_data("type3")


    # --- Type 4 Sentence Editor ---
    def create_type4_editor(self, parent_tab):
        editor_frame = ttk.Frame(parent_tab, padding="5"); editor_frame.pack(expand=True, fill=tk.BOTH)
        # ... (Listbox, scrollbar, buttons similar to Type 3) ...
        list_frame = ttk.Frame(editor_frame); list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))
        self.t4_listbox = tk.Listbox(list_frame, width=60, height=15); self.t4_listbox.pack(side=tk.LEFT, fill=tk.Y)
        t4_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.t4_listbox.yview); t4_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.t4_listbox.config(yscrollcommand=t4_scrollbar.set); self.t4_listbox.bind('<<ListboxSelect>>', self.on_t4_item_select)
        btn_frame_list = ttk.Frame(list_frame); btn_frame_list.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame_list, text="Add Sentence", command=self.add_new_t4_item).pack(side=tk.LEFT)
        self.edit_t4_btn = ttk.Button(btn_frame_list, text="Edit", command=self.edit_selected_t4_item, state=tk.DISABLED); self.edit_t4_btn.pack(side=tk.LEFT)
        self.delete_t4_btn = ttk.Button(btn_frame_list, text="Delete", command=self.delete_selected_t4_item, state=tk.DISABLED); self.delete_t4_btn.pack(side=tk.LEFT)

        self.t4_form_frame = ttk.Labelframe(editor_frame, text="Edit Type 4 Sentence", padding="10")
        self.t4_edit_mode = tk.BooleanVar(); self.t4_current_edit_idx = tk.IntVar(value=-1)
        self.t4_form_vars = {"code":tk.StringVar(), "audio":tk.StringVar(), "sentence":tk.StringVar(), 
                             "blocks":tk.StringVar(), "translation":tk.StringVar(), "possibleAnswers":tk.StringVar()}
        row=0
        fields_t4 = [("Code","code"), ("Audio Path","audio", True), ("Full Sentence","sentence"), 
                     ("Blocks (CSV)","blocks"), ("Translation","translation"), ("Possible Ans (CSV)","possibleAnswers")]
        for label, key, is_audio in [(f[0], f[1], f[2] if len(f)>2 else False) for f in fields_t4]:
            ttk.Label(self.t4_form_frame, text=f"{label}:").grid(row=row, column=0, sticky="w")
            if is_audio:
                af = ttk.Frame(self.t4_form_frame); af.grid(row=row, column=1, sticky="ew")
                ttk.Entry(af, textvariable=self.t4_form_vars[key], width=30).pack(side=tk.LEFT, expand=True, fill=tk.X)
                ttk.Button(af, text="Browse", command=lambda v=self.t4_form_vars[key]: self.browse_audio_file(v)).pack(side=tk.LEFT)
            else:
                ttk.Entry(self.t4_form_frame, textvariable=self.t4_form_vars[key]).grid(row=row, column=1, sticky="ew")
            row+=1
        
        form_btn_frame = ttk.Frame(self.t4_form_frame); form_btn_frame.grid(row=row,column=0,columnspan=2,pady=10)
        ttk.Button(form_btn_frame, text="Save", command=self.save_t4_item).pack(side=tk.LEFT)
        ttk.Button(form_btn_frame, text="Cancel", command=self.hide_t4_form).pack(side=tk.LEFT)
        self.t4_form_frame.columnconfigure(1,weight=1); self.hide_t4_form()

    def populate_t4_listbox(self):
        self.t4_listbox.delete(0,tk.END)
        for item in self.active_type4_data: self.t4_listbox.insert(tk.END, f"C:{item.get('code','?')} S: {item.get('sentence','?'):.40s}...")
        self.on_t4_item_select()
    def on_t4_item_select(self,ev=None): s=bool(self.t4_listbox.curselection()); self.edit_t4_btn.config(state=tk.NORMAL if s else tk.DISABLED); self.delete_t4_btn.config(state=tk.NORMAL if s else tk.DISABLED)
    def show_t4_form(self, edit=False, item=None, idx=-1):
        self.t4_edit_mode.set(edit); self.t4_current_edit_idx.set(idx); self.t4_form_frame.config(text="Edit" if edit else "Add")
        if edit and item:
            for key, var in self.t4_form_vars.items():
                if key in ["blocks", "possibleAnswers"]: var.set(", ".join(item.get(key,[])))
                else: var.set(item.get(key,''))
        else:
            for k,v in self.t4_form_vars.items(): v.set('')
            self.t4_form_vars["code"].set(self.current_section_code.get() + "XXX")
        self.t4_form_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)
    def hide_t4_form(self): self.t4_form_frame.pack_forget(); self.on_t4_item_select()
    def add_new_t4_item(self): self.show_t4_form(False)
    def edit_selected_t4_item(self): 
        idx=self.t4_listbox.curselection()
        if idx:
            self.show_t4_form(True,self.active_type4_data[idx[0]],idx[0])
    def delete_selected_t4_item(self):
        idx=self.t4_listbox.curselection()
        if not idx: return
        if messagebox.askyesno("Confirm", f"Delete Type 4: '{self.active_type4_data[idx[0]].get('sentence','')}...'?"):
            del self.active_type4_data[idx[0]]; self.save_active_type_data("type4")
    def save_t4_item(self):
        item = {k:v.get().strip() for k,v in self.t4_form_vars.items() if k not in ["blocks", "possibleAnswers"]}
        if not item["code"] or not item["sentence"] or not item["audio"]: messagebox.showerror("Error","Code, Audio, Sentence required."); return
        item["blocks"] = [s.strip() for s in self.t4_form_vars["blocks"].get().split(',') if s.strip()]
        item["possibleAnswers"] = [s.strip() for s in self.t4_form_vars["possibleAnswers"].get().split(',') if s.strip()]
        idx=self.t4_current_edit_idx.get()
        if self.t4_edit_mode.get() and idx != -1: self.active_type4_data[idx] = item
        else: self.active_type4_data.append(item)
        self.save_active_type_data("type4")


    # --- Type 5 Context Editor ---
    def create_type5_editor(self, parent_tab):
        editor_frame = ttk.Frame(parent_tab, padding="5"); editor_frame.pack(expand=True, fill=tk.BOTH)
        # ... (Listbox, scrollbar, buttons) ...
        list_frame = ttk.Frame(editor_frame); list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))
        self.t5_listbox = tk.Listbox(list_frame, width=60, height=15); self.t5_listbox.pack(side=tk.LEFT, fill=tk.Y)
        t5_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.t5_listbox.yview); t5_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.t5_listbox.config(yscrollcommand=t5_scrollbar.set); self.t5_listbox.bind('<<ListboxSelect>>', self.on_t5_item_select)
        btn_frame_list = ttk.Frame(list_frame); btn_frame_list.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame_list, text="Add Context", command=self.add_new_t5_item).pack(side=tk.LEFT)
        self.edit_t5_btn = ttk.Button(btn_frame_list, text="Edit", command=self.edit_selected_t5_item, state=tk.DISABLED); self.edit_t5_btn.pack(side=tk.LEFT)
        self.delete_t5_btn = ttk.Button(btn_frame_list, text="Delete", command=self.delete_selected_t5_item, state=tk.DISABLED); self.delete_t5_btn.pack(side=tk.LEFT)

        self.t5_form_frame = ttk.Labelframe(editor_frame, text="Edit Type 5 Context Item", padding="10")
        self.t5_edit_mode = tk.BooleanVar(); self.t5_current_edit_idx = tk.IntVar(value=-1)
        self.t5_form_vars = {"code":tk.StringVar(), "sentence":tk.StringVar(), "translation":tk.StringVar(), "blocks":tk.StringVar()}
        
        row=0; fields_t5 = [("Code","code"), ("Sentence (use [__])","sentence"), ("Translation","translation"), ("Distractor Blocks (CSV)","blocks")]
        for label, key in fields_t5:
            ttk.Label(self.t5_form_frame, text=f"{label}:").grid(row=row, column=0, sticky="nw" if "Sentence" in label else "w")
            if "Sentence" in label: # Use Text widget for sentence for better multi-line view
                 self.t5_sentence_text = scrolledtext.ScrolledText(self.t5_form_frame, height=3, width=40, wrap=tk.WORD)
                 self.t5_sentence_text.grid(row=row, column=1, sticky="ew", pady=2)
            else:
                 ttk.Entry(self.t5_form_frame, textvariable=self.t5_form_vars[key]).grid(row=row, column=1, sticky="ew", pady=2)
            row+=1

        # Valid Combinations Editor (Simplified: Text area, each line is a CSV of a combination)
        ttk.Label(self.t5_form_frame, text="Valid Combinations\n(one combo per line, CSV):").grid(row=row, column=0, sticky="nw");
        self.t5_valid_comb_text = scrolledtext.ScrolledText(self.t5_form_frame, height=5, width=40, wrap=tk.WORD)
        self.t5_valid_comb_text.grid(row=row, column=1, sticky="ew", pady=2); row+=1
        
        form_btn_frame = ttk.Frame(self.t5_form_frame); form_btn_frame.grid(row=row,column=0,columnspan=2,pady=10)
        ttk.Button(form_btn_frame, text="Save", command=self.save_t5_item).pack(side=tk.LEFT)
        ttk.Button(form_btn_frame, text="Cancel", command=self.hide_t5_form).pack(side=tk.LEFT)
        self.t5_form_frame.columnconfigure(1,weight=1); self.hide_t5_form()

    def populate_t5_listbox(self):
        self.t5_listbox.delete(0,tk.END)
        for item in self.active_type5_data: self.t5_listbox.insert(tk.END, f"C:{item.get('code','?')} S: {item.get('sentence','?'):.40s}...")
        self.on_t5_item_select()
    def on_t5_item_select(self,ev=None): s=bool(self.t5_listbox.curselection()); self.edit_t5_btn.config(state=tk.NORMAL if s else tk.DISABLED); self.delete_t5_btn.config(state=tk.NORMAL if s else tk.DISABLED)
    def show_t5_form(self, edit=False, item=None, idx=-1):
        self.t5_edit_mode.set(edit); self.t5_current_edit_idx.set(idx); self.t5_form_frame.config(text="Edit" if edit else "Add")
        self.t5_sentence_text.config(state=tk.NORMAL); self.t5_sentence_text.delete(1.0, tk.END)
        self.t5_valid_comb_text.config(state=tk.NORMAL); self.t5_valid_comb_text.delete(1.0, tk.END)
        if edit and item:
            for key, var in self.t5_form_vars.items(): var.set(item.get(key,'') if key != "blocks" else ", ".join(item.get(key,[])))
            self.t5_sentence_text.insert(tk.END, item.get('sentence',''))
            valid_combs_str = "\n".join([",".join(comb) for comb in item.get('validCombinations',[])])
            self.t5_valid_comb_text.insert(tk.END, valid_combs_str)
        else:
            for k,v in self.t5_form_vars.items(): v.set('')
            self.t5_form_vars["code"].set(self.current_section_code.get() + "XXX")
        self.t5_form_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)
    def hide_t5_form(self): self.t5_form_frame.pack_forget(); self.on_t5_item_select()
    def add_new_t5_item(self): self.show_t5_form(False)
    def edit_selected_t5_item(self): 
        idx=self.t5_listbox.curselection()
        if idx: # Corrected
            self.show_t5_form(True,self.active_type5_data[idx[0]],idx[0])
    def delete_selected_t5_item(self):
        idx=self.t5_listbox.curselection()
        if not idx: return
        if messagebox.askyesno("Confirm", f"Delete Type 5: '{self.active_type5_data[idx[0]].get('sentence','')}...'?"):
            del self.active_type5_data[idx[0]]; self.save_active_type_data("type5")
    def save_t5_item(self):
        item = {k:v.get().strip() for k,v in self.t5_form_vars.items() if k != "blocks"}
        item["sentence"] = self.t5_sentence_text.get(1.0, tk.END).strip()
        if not item["code"] or not item["sentence"]: messagebox.showerror("Error","Code and Sentence required."); return
        item["blocks"] = [s.strip() for s in self.t5_form_vars["blocks"].get().split(',') if s.strip()]
        
        raw_combs = self.t5_valid_comb_text.get(1.0, tk.END).strip().split('\n')
        item["validCombinations"] = [[s.strip() for s in line.split(',') if s.strip()] for line in raw_combs if line.strip()]

        idx=self.t5_current_edit_idx.get()
        if self.t5_edit_mode.get() and idx != -1: self.active_type5_data[idx] = item
        else: self.active_type5_data.append(item)
        self.save_active_type_data("type5")

    # --- Guidebook Editor ---
    def create_guidebook_editor(self, parent_tab):
        self.guidebook_tab_id_in_lang_notebook = parent_tab # Store ref if needed for selection
        editor_frame = ttk.Frame(parent_tab, padding="5")
        editor_frame.pack(expand=True, fill=tk.BOTH)
        
        top_controls_frame = ttk.Frame(editor_frame)
        top_controls_frame.pack(fill=tk.X, pady=5)
        ttk.Label(top_controls_frame, text="Manages: lang/sub_course/guidebook/guide_structure.json").pack(side=tk.LEFT)
        ttk.Button(top_controls_frame, text="Refresh/Load Guidebook Data", command=self.load_guidebook_data_for_ui).pack(side=tk.LEFT, padx=10)

        main_gb_pane = ttk.PanedWindow(editor_frame, orient=tk.HORIZONTAL)
        main_gb_pane.pack(expand=True, fill=tk.BOTH)

        # Categories Pane (Left of PanedWindow)
        cat_pane = ttk.Labelframe(main_gb_pane, text="Categories", padding="5", width=350) # Give initial width
        main_gb_pane.add(cat_pane, weight=1)

        self.gb_cat_listbox = tk.Listbox(cat_pane, width=40, height=10, exportselection=False)
        cat_scrollbar = ttk.Scrollbar(cat_pane, orient=tk.VERTICAL, command=self.gb_cat_listbox.yview)
        self.gb_cat_listbox.config(yscrollcommand=cat_scrollbar.set)
        self.gb_cat_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.gb_cat_listbox.bind('<<ListboxSelect>>', self.on_gb_category_select)

        cat_btn_frame = ttk.Frame(cat_pane); cat_btn_frame.pack(fill=tk.X, pady=3)
        ttk.Button(cat_btn_frame, text="Add", command=self.add_gb_category_ui).pack(side=tk.LEFT)
        self.edit_gb_cat_btn = ttk.Button(cat_btn_frame, text="Edit", state=tk.DISABLED, command=self.edit_selected_gb_category); self.edit_gb_cat_btn.pack(side=tk.LEFT)
        self.del_gb_cat_btn = ttk.Button(cat_btn_frame, text="Del", state=tk.DISABLED, command=self.delete_selected_gb_category); self.del_gb_cat_btn.pack(side=tk.LEFT)

        # Guidebook Chapters Pane (Right of PanedWindow)
        chap_pane = ttk.Labelframe(main_gb_pane, text="Guidebook Chapters", padding="5", width=350)
        main_gb_pane.add(chap_pane, weight=1)

        self.gb_chap_listbox = tk.Listbox(chap_pane, width=40, height=10, exportselection=False)
        chap_scrollbar = ttk.Scrollbar(chap_pane, orient=tk.VERTICAL, command=self.gb_chap_listbox.yview)
        self.gb_chap_listbox.config(yscrollcommand=chap_scrollbar.set)
        self.gb_chap_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        chap_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.gb_chap_listbox.bind('<<ListboxSelect>>', self.on_gb_chapter_select)
        # Add button to edit chapter meta.json content later
        self.edit_gb_chap_content_btn = ttk.Button(chap_pane, text="Edit Chapter Content (meta.json)", state=tk.DISABLED, command=self.open_chapter_meta_editor) # TBI
        self.edit_gb_chap_content_btn.pack(fill=tk.X, pady=2)


        chap_btn_frame = ttk.Frame(chap_pane); chap_btn_frame.pack(fill=tk.X, pady=3)
        ttk.Button(chap_btn_frame, text="Add", command=self.add_gb_chapter_ui).pack(side=tk.LEFT)
        self.edit_gb_chap_btn = ttk.Button(chap_btn_frame, text="Edit", state=tk.DISABLED, command=self.edit_selected_gb_chapter); self.edit_gb_chap_btn.pack(side=tk.LEFT)
        self.del_gb_chap_btn = ttk.Button(chap_btn_frame, text="Del", state=tk.DISABLED, command=self.delete_selected_gb_chapter); self.del_gb_chap_btn.pack(side=tk.LEFT)
        
        # Forms (initially hidden or in popups)
        self.gb_cat_form_popup = None
        self.gb_chap_form_popup = None
        
        save_all_btn = ttk.Button(editor_frame, text="Save All Guidebook Structure Changes", command=self.save_active_guidebook_data)
        save_all_btn.pack(pady=10)


    def open_chapter_meta_editor(self):
        idx = self.gb_chap_listbox.curselection()
        if not idx:
            messagebox.showwarning("Selection", "Please select a guidebook chapter first.")
            return
        
        selected_chapter_data = self.active_guidebook_data.get("guidebooks", [])[idx[0]]
        chapter_guidcode = selected_chapter_data.get('guidcode')
        if not chapter_guidcode:
            messagebox.showerror("Error", "Selected chapter has no GUIDCode.")
            return

        self.current_chapter_guidcode.set(chapter_guidcode) # Set context

        # Load meta.json data for this chapter
        lang = self.current_lang.get()
        sc_id = self.current_sub_course_id.get()
        self.active_chapter_meta_data = core_logic.load_guidebook_chapter_meta(lang, sc_id, chapter_guidcode)

        self._create_meta_editor_popup()

    def _create_meta_editor_popup(self):
        if hasattr(self, 'meta_editor_popup') and self.meta_editor_popup and self.meta_editor_popup.winfo_exists():
            self.meta_editor_popup.destroy()

        self.meta_editor_popup = tk.Toplevel(self.root)
        self.meta_editor_popup.title(f"Edit meta.json for Chapter: {self.current_chapter_guidcode.get()}")
        self.meta_editor_popup.geometry("600x450")

        # Top frame for file info and save button
        top_meta_frame = ttk.Frame(self.meta_editor_popup, padding=5)
        top_meta_frame.pack(fill=tk.X)
        ttk.Label(top_meta_frame, text=f"meta.json (Format Version: {self.active_chapter_meta_data.get('formatVersion', 'N/A')})").pack(side=tk.LEFT)
        ttk.Button(top_meta_frame, text="Save meta.json", command=self.save_active_chapter_meta).pack(side=tk.RIGHT)

        # Listbox for sections
        list_frame = ttk.Frame(self.meta_editor_popup, padding=5)
        list_frame.pack(expand=True, fill=tk.BOTH, pady=5)
        
        self.meta_sections_listbox = tk.Listbox(list_frame, width=70, height=10, exportselection=False)
        meta_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.meta_sections_listbox.yview)
        self.meta_sections_listbox.config(yscrollcommand=meta_scrollbar.set)
        self.meta_sections_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        meta_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.meta_sections_listbox.bind("<<ListboxSelect>>", self.on_meta_section_select)

        # Buttons for managing sections
        meta_btn_frame = ttk.Frame(self.meta_editor_popup, padding=5)
        meta_btn_frame.pack(fill=tk.X)
        ttk.Button(meta_btn_frame, text="Add Text Section", command=self.add_meta_text_section_ui).pack(side=tk.LEFT)
        ttk.Button(meta_btn_frame, text="Add Media Section", command=self.add_meta_media_section_ui).pack(side=tk.LEFT) # TBI
        self.edit_meta_section_btn = ttk.Button(meta_btn_frame, text="Edit Section", state=tk.DISABLED, command=self.edit_selected_meta_section); self.edit_meta_section_btn.pack(side=tk.LEFT)
        self.del_meta_section_btn = ttk.Button(meta_btn_frame, text="Delete Section", state=tk.DISABLED, command=self.delete_selected_meta_section); self.del_meta_section_btn.pack(side=tk.LEFT)
        self.move_meta_up_btn = ttk.Button(meta_btn_frame, text="Move Up", state=tk.DISABLED, command=lambda: self.move_meta_section(-1)); self.move_meta_up_btn.pack(side=tk.LEFT)
        self.move_meta_down_btn = ttk.Button(meta_btn_frame, text="Move Down", state=tk.DISABLED, command=lambda: self.move_meta_section(1)); self.move_meta_down_btn.pack(side=tk.LEFT)

        self.populate_meta_sections_listbox()
        self.on_meta_section_select() # Update button states

    def populate_meta_sections_listbox(self):
        if not (hasattr(self, 'meta_sections_listbox') and self.meta_sections_listbox.winfo_exists()): return
        self.meta_sections_listbox.delete(0, tk.END)
        for section in self.active_chapter_meta_data.get("sections", []):
            self.meta_sections_listbox.insert(tk.END, f"Type: {section.get('type', '?')}, Content: {section.get('content', '?')}")
        self.on_meta_section_select()

    def on_meta_section_select(self, event=None):
        if not (hasattr(self, 'meta_sections_listbox') and self.meta_sections_listbox.winfo_exists()): return
        is_selected = bool(self.meta_sections_listbox.curselection())
        idx_tuple = self.meta_sections_listbox.curselection()
        idx = idx_tuple[0] if idx_tuple else -1
        
        self.edit_meta_section_btn.config(state=tk.NORMAL if is_selected else tk.DISABLED)
        self.del_meta_section_btn.config(state=tk.NORMAL if is_selected else tk.DISABLED)
        self.move_meta_up_btn.config(state=tk.NORMAL if is_selected and idx > 0 else tk.DISABLED)
        self.move_meta_down_btn.config(state=tk.NORMAL if is_selected and idx < self.meta_sections_listbox.size() - 1 else tk.DISABLED)

    def add_meta_text_section_ui(self):
        filename = filedialog.asksaveasfilename(
            title="Enter new Markdown filename for Text Section",
            initialdir=core_logic.get_guidebook_chapter_base_path(self.current_lang.get(), self.current_sub_course_id.get(), self.current_chapter_guidcode.get()),
            defaultextension=".md",
            filetypes=(("Markdown files", "*.md"),("All files", "*.*"))
        )
        if filename:
            # We only want the filename relative to the chapter folder for meta.json
            relative_filename = os.path.basename(filename) 
            sections = self.active_chapter_meta_data.setdefault("sections", [])
            sections.append({"type": "text", "content": relative_filename})
            self.populate_meta_sections_listbox()
            # Optionally, create an empty file or open editor immediately
            full_path = core_logic.get_guidebook_chapter_content_path(self.current_lang.get(), self.current_sub_course_id.get(), self.current_chapter_guidcode.get(), relative_filename)
            if not os.path.exists(full_path):
                core_logic.save_text_file_content(full_path, f"# {relative_filename}\n\nStart writing content here.")
            self.open_markdown_editor(relative_filename)

    def add_meta_media_section_ui(self):
        # Similar to add_meta_text_section_ui, but for media
        # Use filedialog.askopenfilename to select an existing media file
        # The path stored in meta.json should be relative to the chapter's 'media' subfolder
        initial_media_dir = os.path.join(core_logic.get_guidebook_chapter_base_path(self.current_lang.get(), self.current_sub_course_id.get(), self.current_chapter_guidcode.get()), "media")
        if not os.path.exists(initial_media_dir): os.makedirs(initial_media_dir, exist_ok=True)

        filepath = filedialog.askopenfilename(
            title="Select Media File for Section",
            initialdir=initial_media_dir,
            filetypes=(("Images", "*.png *.jpg *.jpeg *.gif"), ("Audio", "*.mp3 *.wav *.ogg"), ("Video", "*.mp4"), ("All files", "*.*"))
        )
        if filepath:
            media_filename = os.path.basename(filepath)
            # Ensure the selected file is (or will be copied to) the chapter's media folder
            target_media_path = core_logic.get_guidebook_chapter_media_path(self.current_lang.get(), self.current_sub_course_id.get(), self.current_chapter_guidcode.get(), media_filename)
            if not os.path.exists(target_media_path) or not os.path.samefile(filepath, target_media_path):
                if messagebox.askyesno("Copy File?", f"Copy '{media_filename}' to this chapter's media folder?"):
                    try:
                        shutil.copy(filepath, target_media_path)
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not copy file: {e}"); return
                else: # User chose not to copy
                    messagebox.showinfo("Info", "Media file not copied. Storing original path relative to media folder if possible, otherwise just filename.");
                    # Attempt to make it relative to media dir, else just filename
                    try:
                        rel_path_to_media_dir = os.path.relpath(filepath, initial_media_dir)
                        if not rel_path_to_media_dir.startswith(".."):
                             media_filename = rel_path_to_media_dir.replace(os.sep, "/")
                        # else it's outside, just use basename
                    except ValueError: pass # Different drive

            sections = self.active_chapter_meta_data.setdefault("sections", [])
            sections.append({"type": "media", "content": media_filename}) # Store filename (relative to media/)
            self.populate_meta_sections_listbox()

    def edit_selected_meta_section(self):
        idx_tuple = self.meta_sections_listbox.curselection()
        if not idx_tuple: return
        idx = idx_tuple[0]
        
        sections = self.active_chapter_meta_data.get("sections", [])
        if not (0 <= idx < len(sections)): return
        
        section_data = sections[idx]
        sec_type = section_data.get("type")
        content_filename = section_data.get("content")

        if sec_type == "text":
            self.open_markdown_editor(content_filename)
        elif sec_type == "media":
            # For media, "editing" might mean changing the file or its properties (TBI)
            # For now, let's allow changing the filename
            new_filename = filedialog.askopenfilename(
                title=f"Change Media File for: {content_filename}",
                initialdir=os.path.join(core_logic.get_guidebook_chapter_base_path(self.current_lang.get(), self.current_sub_course_id.get(), self.current_chapter_guidcode.get()), "media"),
                 filetypes=(("Images", "*.png *.jpg *.jpeg *.gif"), ("Audio", "*.mp3 *.wav *.ogg"), ("Video", "*.mp4"), ("All files", "*.*"))
            )
            if new_filename:
                # Similar copy logic as in add_meta_media_section_ui
                target_media_path = core_logic.get_guidebook_chapter_media_path(self.current_lang.get(), self.current_sub_course_id.get(), self.current_chapter_guidcode.get(), os.path.basename(new_filename))
                if not os.path.exists(target_media_path) or not os.path.samefile(new_filename, target_media_path):
                    if messagebox.askyesno("Copy File?", f"Copy '{os.path.basename(new_filename)}' to this chapter's media folder?"):
                        try: shutil.copy(new_filename, target_media_path)
                        except Exception as e: messagebox.showerror("Error", f"Could not copy file: {e}"); return
                sections[idx]["content"] = os.path.basename(new_filename) # Store just filename relative to media/
                self.populate_meta_sections_listbox()
        else:
            messagebox.showinfo("Edit", f"Editing for type '{sec_type}' not fully implemented.")


    def delete_selected_meta_section(self):
        idx_tuple = self.meta_sections_listbox.curselection()
        if not idx_tuple: return
        idx = idx_tuple[0]
        sections = self.active_chapter_meta_data.get("sections", [])
        if not (0 <= idx < len(sections)): return
        
        section_content = sections[idx].get("content")
        if messagebox.askyesno("Confirm Delete", f"Delete section: '{section_content}' from meta.json?\n(This does NOT delete the actual .md or media file on disk)"):
            del sections[idx]
            self.populate_meta_sections_listbox()

    def move_meta_section(self, direction): # direction is -1 for up, 1 for down
        idx_tuple = self.meta_sections_listbox.curselection()
        if not idx_tuple: return
        idx = idx_tuple[0]
        
        sections = self.active_chapter_meta_data.get("sections", [])
        if not sections: return

        new_idx = idx + direction
        if 0 <= new_idx < len(sections):
            sections.insert(new_idx, sections.pop(idx))
            self.populate_meta_sections_listbox()
            self.meta_sections_listbox.selection_set(new_idx)
            self.meta_sections_listbox.activate(new_idx)
        self.on_meta_section_select() # Update button states


    def save_active_chapter_meta(self):
        lang = self.current_lang.get()
        sc_id = self.current_sub_course_id.get()
        chap_guid = self.current_chapter_guidcode.get()
        if not (lang and sc_id and chap_guid):
            messagebox.showerror("Error", "Context (Lang/SubCourse/Chapter) missing to save meta.json.")
            return

        # Ensure formatVersion exists
        if "formatVersion" not in self.active_chapter_meta_data:
            self.active_chapter_meta_data["formatVersion"] = 2 # or your current version

        if core_logic.save_guidebook_chapter_meta(lang, sc_id, chap_guid, self.active_chapter_meta_data):
            messagebox.showinfo("Success", f"meta.json for chapter '{chap_guid}' saved.")
            # Optionally close the meta editor popup or just refresh its list
            self.populate_meta_sections_listbox() 
        else:
            messagebox.showerror("Error", "Failed to save meta.json.")


    def open_markdown_editor(self, markdown_filename):
        if self.md_editor_window and self.md_editor_window.winfo_exists():
            messagebox.showwarning("Editor Open", "A Markdown editor window is already open. Please close it first.")
            self.md_editor_window.lift()
            return

        lang = self.current_lang.get()
        sc_id = self.current_sub_course_id.get()
        chap_guid = self.current_chapter_guidcode.get()
        if not (lang and sc_id and chap_guid): return

        self.md_editor_current_file_path = core_logic.get_guidebook_chapter_content_path(lang, sc_id, chap_guid, markdown_filename)
        
        content = core_logic.load_text_file_content(self.md_editor_current_file_path)
        if content is None: content = f"# {markdown_filename}\n\nNew file content..." # Default for new/empty

        self.md_editor_window = tk.Toplevel(self.root)
        self.md_editor_window.title(f"Edit: {markdown_filename}")
        self.md_editor_window.geometry("700x500")

        self.md_editor_text_widget = scrolledtext.ScrolledText(self.md_editor_window, wrap=tk.WORD, height=20, undo=True)
        self.md_editor_text_widget.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.md_editor_text_widget.insert(tk.END, content)

        btn_frame = ttk.Frame(self.md_editor_window, padding=5)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="Save Markdown", command=self.save_markdown_content).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel/Close", command=self.md_editor_window.destroy).pack(side=tk.LEFT, padx=5)
        
        self.md_editor_window.protocol("WM_DELETE_WINDOW", self.md_editor_window.destroy) # Handle closing


    def save_markdown_content(self):
        if not (self.md_editor_window and self.md_editor_window.winfo_exists() and self.md_editor_text_widget and self.md_editor_current_file_path):
            messagebox.showerror("Error", "Markdown editor or file context is lost.")
            return
        
        content = self.md_editor_text_widget.get(1.0, tk.END).strip() # Get all content
        if core_logic.save_text_file_content(self.md_editor_current_file_path, content):
            messagebox.showinfo("Success", f"Saved: {os.path.basename(self.md_editor_current_file_path)}", parent=self.md_editor_window)
            # self.md_editor_window.destroy() # Optionally close after save
        else:
            messagebox.showerror("Error", f"Failed to save: {os.path.basename(self.md_editor_current_file_path)}", parent=self.md_editor_window)

        


    def load_guidebook_data_for_ui(self):
        # ... (same as before, but also trigger preview) ...
        lang = self.current_lang.get(); sc_id = self.current_sub_course_id.get()
        if not (lang and sc_id):
            messagebox.showwarning("Context Missing", "Select Language and Sub-course to load Guidebooks.")
            self.active_guidebook_data = {"categories": [], "guidebooks": []}
        else:
            self.active_guidebook_data = core_logic.load_guidebook_structure(lang, sc_id)
        
        self.populate_gb_category_listbox()
        self.populate_gb_guidebook_listbox()
        self.update_preview_area("guidebook_structure")

    def populate_gb_category_listbox(self):
        # ... (same as before) ...
        if not hasattr(self, 'gb_cat_listbox'): return
        self.gb_cat_listbox.delete(0,tk.END)
        for cat in self.active_guidebook_data.get("categories", []):
            self.gb_cat_listbox.insert(tk.END, f"{cat.get('guidcode')} - {cat.get('title','Untitled Category')}")
        self.on_gb_category_select()

    def populate_gb_guidebook_listbox(self):
        # ... (same as before) ...
        if not hasattr(self, 'gb_chap_listbox'): return
        self.gb_chap_listbox.delete(0,tk.END)
        for gb in self.active_guidebook_data.get("guidebooks", []):
            self.gb_chap_listbox.insert(tk.END, f"{gb.get('guidcode')} - {gb.get('title','Untitled Chapter')}")
        self.on_gb_chapter_select()


    def on_gb_category_select(self, event=None):
        is_selected = bool(self.gb_cat_listbox.curselection())
        self.edit_gb_cat_btn.config(state=tk.NORMAL if is_selected else tk.DISABLED)
        self.del_gb_cat_btn.config(state=tk.NORMAL if is_selected else tk.DISABLED)

    def on_gb_chapter_select(self, event=None):
        is_selected = bool(self.gb_chap_listbox.curselection())
        self.edit_gb_chap_btn.config(state=tk.NORMAL if is_selected else tk.DISABLED)
        self.del_gb_chap_btn.config(state=tk.NORMAL if is_selected else tk.DISABLED)
        self.edit_gb_chap_content_btn.config(state=tk.NORMAL if is_selected else tk.DISABLED)


    def _create_gb_cat_form_popup(self, edit_mode=False, item_data=None):
        if self.gb_cat_form_popup and self.gb_cat_form_popup.winfo_exists():
            self.gb_cat_form_popup.destroy()

        self.gb_cat_form_popup = tk.Toplevel(self.root)
        self.gb_cat_form_popup.title("Edit Category" if edit_mode else "Add Category")
        # self.gb_cat_form_popup.geometry("400x300") # Optional

        form_vars = {
            "guidcode": tk.StringVar(), "title": tk.StringVar(),
            "chapters_csv": tk.StringVar(), "relatedCircles_csv": tk.StringVar(), "icon": tk.StringVar()
        }
        original_guidcode = item_data.get('guidcode', '') if item_data else ''

        if edit_mode and item_data:
            form_vars["guidcode"].set(item_data.get('guidcode', ''))
            form_vars["title"].set(item_data.get('title', ''))
            form_vars["chapters_csv"].set(", ".join(item_data.get('chapters', [])))
            form_vars["relatedCircles_csv"].set(", ".join(item_data.get('relatedCircles', [])))
            form_vars["icon"].set(item_data.get('icon', ''))
        
        row = 0
        fields = [("GUIDCode:", "guidcode"), ("Title:", "title"), ("Icon (emoji):", "icon"),
                  ("Chapters (CSV of GB-Codes):", "chapters_csv"), ("Related Circles (CSV):", "relatedCircles_csv")]
        for label_text, key in fields:
            ttk.Label(self.gb_cat_form_popup, text=label_text).grid(row=row, column=0, sticky="w", padx=5, pady=3)
            ttk.Entry(self.gb_cat_form_popup, textvariable=form_vars[key], width=40).grid(row=row, column=1, sticky="ew", padx=5, pady=3)
            row += 1
        
        ttk.Button(self.gb_cat_form_popup, text="Save", 
                   command=lambda: self.save_gb_category_from_popup(form_vars, edit_mode, original_guidcode)).grid(row=row, column=0, pady=10)
        ttk.Button(self.gb_cat_form_popup, text="Cancel", 
                   command=self.gb_cat_form_popup.destroy).grid(row=row, column=1, pady=10)
        self.gb_cat_form_popup.columnconfigure(1, weight=1)

    def add_gb_category_ui(self): self._create_gb_cat_form_popup(False)
    def edit_selected_gb_category(self):
        idx = self.gb_cat_listbox.curselection()
        if idx: self._create_gb_cat_form_popup(True, self.active_guidebook_data.get("categories",[])[idx[0]])

    def save_gb_category_from_popup(self, form_vars, edit_mode, original_guidcode):
        guidcode = form_vars["guidcode"].get().strip()
        if not guidcode: messagebox.showerror("Error", "Category GUIDCode is required."); return

        new_cat_data = {
            "guidcode": guidcode,
            "title": form_vars["title"].get().strip(),
            "chapters": [c.strip() for c in form_vars["chapters_csv"].get().split(',') if c.strip()],
            "relatedCircles": [c.strip() for c in form_vars["relatedCircles_csv"].get().split(',') if c.strip()],
            "icon": form_vars["icon"].get().strip()
        }
        
        cats = self.active_guidebook_data.setdefault("categories", [])
        if edit_mode:
            found = False
            for i, cat in enumerate(cats):
                if cat.get('guidcode') == original_guidcode:
                    # Check if new guidcode conflicts (if changed)
                    if guidcode != original_guidcode and any(c.get('guidcode') == guidcode for c in cats if c.get('guidcode') != original_guidcode):
                        messagebox.showerror("Error", f"New GUIDCode '{guidcode}' already exists."); return
                    cats[i] = new_cat_data
                    found = True; break
            if not found: messagebox.showerror("Error", "Original category not found."); return
        else: # Adding
            if any(c.get('guidcode') == guidcode for c in cats):
                messagebox.showerror("Error", f"Category GUIDCode '{guidcode}' already exists."); return
            cats.append(new_cat_data)
        
        self.gb_cat_form_popup.destroy()
        self.populate_gb_category_listbox()
        # Consider immediate save or mark as dirty for "Save All" button
        # self.save_active_guidebook_data() # Or let user click "Save All"

    def delete_selected_gb_category(self):
        idx = self.gb_cat_listbox.curselection()
        if not idx: return
        cat_guid = self.active_guidebook_data.get("categories",[])[idx[0]].get('guidcode')
        if messagebox.askyesno("Confirm Delete", f"Delete category '{cat_guid}'? This will also remove it as a parent from chapters."):
            del self.active_guidebook_data["categories"][idx[0]]
            # Also update chapters that might have had this as parentCategory
            for chap in self.active_guidebook_data.get("guidebooks", []):
                if chap.get("parentCategory") == cat_guid:
                    chap["parentCategory"] = "" # Or None, or remove key
            self.populate_gb_category_listbox()
            self.populate_gb_guidebook_listbox()
            # self.save_active_guidebook_data()

    def _create_gb_chap_form_popup(self, edit_mode=False, item_data=None):
        if self.gb_chap_form_popup and self.gb_chap_form_popup.winfo_exists():
            self.gb_chap_form_popup.destroy()
        self.gb_chap_form_popup = tk.Toplevel(self.root)
        self.gb_chap_form_popup.title("Edit Chapter" if edit_mode else "Add Chapter")

        form_vars = {"guidcode": tk.StringVar(), "title": tk.StringVar(), "parentCategory": tk.StringVar()}
        original_guidcode = item_data.get('guidcode','') if item_data else ''

        if edit_mode and item_data:
            for key, var in form_vars.items(): var.set(item_data.get(key,''))

        row=0
        fields = [("GUIDCode (GB-XXX):","guidcode"), ("Title:","title")]
        for label_text, key in fields:
            ttk.Label(self.gb_chap_form_popup, text=label_text).grid(row=row,column=0,sticky="w",padx=5,pady=3)
            ttk.Entry(self.gb_chap_form_popup, textvariable=form_vars[key], width=40).grid(row=row,column=1,sticky="ew",padx=5,pady=3); row+=1
        
        ttk.Label(self.gb_chap_form_popup, text="Parent Category:").grid(row=row,column=0,sticky="w",padx=5,pady=3)
        category_guidcodes = [cat.get('guidcode') for cat in self.active_guidebook_data.get("categories",[]) if cat.get('guidcode')]
        parent_cat_combo = ttk.Combobox(self.gb_chap_form_popup, textvariable=form_vars["parentCategory"], values=category_guidcodes, state="readonly", width=38)
        parent_cat_combo.grid(row=row,column=1,sticky="ew",padx=5,pady=3); row+=1
        if item_data and item_data.get("parentCategory") in category_guidcodes:
            form_vars["parentCategory"].set(item_data.get("parentCategory"))
        elif category_guidcodes : # Default to first if adding and categories exist
             if not edit_mode: form_vars["parentCategory"].set(category_guidcodes[0])


        ttk.Button(self.gb_chap_form_popup, text="Save", 
                   command=lambda: self.save_gb_chapter_from_popup(form_vars, edit_mode, original_guidcode)).grid(row=row,column=0,pady=10)
        ttk.Button(self.gb_chap_form_popup, text="Cancel",
                   command=self.gb_chap_form_popup.destroy).grid(row=row,column=1,pady=10)
        self.gb_chap_form_popup.columnconfigure(1,weight=1)

    def add_gb_chapter_ui(self): self._create_gb_chap_form_popup(False)
    def edit_selected_gb_chapter(self):
        idx = self.gb_chap_listbox.curselection()
        if idx: self._create_gb_chap_form_popup(True, self.active_guidebook_data.get("guidebooks",[])[idx[0]])
    
    def save_gb_chapter_from_popup(self, form_vars, edit_mode, original_guidcode):
        guidcode = form_vars["guidcode"].get().strip()
        if not guidcode: messagebox.showerror("Error", "Chapter GUIDCode required."); return
        
        new_chap_data = {
            "guidcode": guidcode,
            "title": form_vars["title"].get().strip(),
            "parentCategory": form_vars["parentCategory"].get().strip()
        }
        chaps = self.active_guidebook_data.setdefault("guidebooks", [])
        # ... (Logic for add/edit/duplicate check for chapters similar to categories) ...
        if edit_mode:
            found = False
            for i, chap in enumerate(chaps):
                if chap.get('guidcode') == original_guidcode:
                    if guidcode != original_guidcode and any(c.get('guidcode') == guidcode for c in chaps if c.get('guidcode') != original_guidcode):
                        messagebox.showerror("Error", f"New GUIDCode '{guidcode}' already exists."); return
                    chaps[i] = new_chap_data
                    found = True; break
            if not found: messagebox.showerror("Error", "Original chapter not found."); return
        else: # Adding
            if any(c.get('guidcode') == guidcode for c in chaps):
                messagebox.showerror("Error", f"Chapter GUIDCode '{guidcode}' already exists."); return
            chaps.append(new_chap_data)

        self.gb_chap_form_popup.destroy()
        self.populate_gb_guidebook_listbox()
        # self.save_active_guidebook_data() # Or let user click "Save All"

    def delete_selected_gb_chapter(self):
        idx = self.gb_chap_listbox.curselection()
        if not idx: return
        chap_guid = self.active_guidebook_data.get("guidebooks",[])[idx[0]].get('guidcode')
        if messagebox.askyesno("Confirm Delete", f"Delete chapter '{chap_guid}'? This also removes it from category chapter lists."):
            del self.active_guidebook_data["guidebooks"][idx[0]]
            # Remove from any category's chapter list
            for cat in self.active_guidebook_data.get("categories", []):
                if chap_guid in cat.get("chapters",[]):
                    cat["chapters"].remove(chap_guid)
            self.populate_gb_category_listbox() # In case chapters list changed display
            self.populate_gb_guidebook_listbox()
            # self.save_active_guidebook_data()


    def save_active_guidebook_data(self):
        # ... (same as before) ...
        lang=self.current_lang.get(); sc_id=self.current_sub_course_id.get()
        if not (lang and sc_id): messagebox.showerror("Error", "Language and Sub-course not selected."); return
        if core_logic.save_guidebook_structure(lang, sc_id, self.active_guidebook_data):
            messagebox.showinfo("Success", "Guidebook structure saved.")
            self.load_guidebook_data_for_ui() # Refresh lists and preview
        else: messagebox.showerror("Error", "Failed to save guidebook structure.")

# Helper for on_X_selected_item, P(idx) was a placeholder for 'if idx'
def P(idx): return bool(idx)


if __name__ == "__main__":
    root = tk.Tk()
    app = LivygoEditorApp(root)
    # For quicker testing, you can pre-fill the path if you know it
    # app.path_entry.insert(0, "/path/to/your/Livygo/courses_test_directory") 
    # app.set_and_load_initial()
    root.mainloop()