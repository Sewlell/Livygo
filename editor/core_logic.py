import json
import os
import shutil

# --- Configuration ---
CONFIG = {
    # This will now be set/updated by the UI or a main app script
    "courses_base_path": None # Needs to be set by the application
}

def set_courses_base_path(path):
    """Sets the base path for all course operations."""
    if os.path.isdir(path):
        CONFIG["courses_base_path"] = path
        print(f"Info: Courses base path set to '{path}'")
        return True
    else:
        print(f"Error: Invalid courses base path '{path}'")
        CONFIG["courses_base_path"] = None
        return False

def _get_full_path(*path_segments):
    """Constructs a full path from the configured base and segments."""
    if not CONFIG["courses_base_path"]:
        raise ValueError("Courses base path is not set. Call set_courses_base_path() first.")
    return os.path.join(CONFIG["courses_base_path"], *path_segments)

def _ensure_dir(file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

def load_json_file(file_path, default_value=None):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Info: File not found '{file_path}', returning default.")
        return default_value if default_value is not None else ([] if not isinstance(default_value, dict) else {})
    except json.JSONDecodeError:
        print(f"Error: Corrupted JSON in '{file_path}'.")
        return default_value if default_value is not None else ([] if not isinstance(default_value, dict) else {})

def save_json_file(file_path, data, indent=4):
    _ensure_dir(file_path)
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        print(f"Info: Saved '{file_path}'")
        return True
    except IOError as e:
        print(f"Error: Could not write to '{file_path}': {e}")
        return False

# --- Language Management ---
def list_languages():
    if not CONFIG["courses_base_path"]:
        print("Error: Courses base path not set.")
        return []
    base = CONFIG["courses_base_path"]
    if not os.path.exists(base):
        return []
    return [d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))]

def add_language(lang_code):
    if not lang_code.strip():
        print("Error: Language code cannot be empty.")
        return False
    try:
        lang_path = _get_full_path(lang_code)
        if os.path.exists(lang_path):
            print(f"Info: Language '{lang_code}' already exists.")
            return False
        os.makedirs(lang_path)
        # Initialize with an empty sub_courses.json for this new language
        save_json_file(os.path.join(lang_path, "sub_courses.json"), {"sub_courses": []})
        print(f"Info: Language '{lang_code}' created with empty sub_courses.json.")
        return True
    except OSError as e:
        print(f"Error creating language '{lang_code}': {e}")
        return False
    except ValueError as e: # From _get_full_path if base path not set
        print(f"Error: {e}")
        return False


# --- Sub-course Management (per language) ---
def get_sub_courses_file_path(lang_code):
    return _get_full_path(lang_code, "sub_courses.json")

def load_sub_courses_for_lang(lang_code):
    """Loads sub-course definitions for a specific language."""
    try:
        path = get_sub_courses_file_path(lang_code)
        data = load_json_file(path, {"sub_courses": []})
        return data.get("sub_courses", []) # Ensure it returns the list
    except ValueError as e:
        print(f"Error: {e}")
        return []


def save_sub_courses_for_lang(lang_code, sub_courses_list_data):
    """Saves sub-course definitions for a specific language."""
    try:
        path = get_sub_courses_file_path(lang_code)
        return save_json_file(path, {"sub_courses": sub_courses_list_data})
    except ValueError as e:
        print(f"Error: {e}")
        return False

def list_active_sub_course_ids_for_lang(lang_code):
    """Lists active sub-course IDs by checking directory existence under the language."""
    try:
        lang_path = _get_full_path(lang_code)
        if not os.path.isdir(lang_path):
            return []
        # List directories, excluding 'sub_courses.json' file itself
        return [d for d in os.listdir(lang_path) if os.path.isdir(os.path.join(lang_path, d))]
    except ValueError as e:
        print(f"Error: {e}")
        return []


def create_sub_course_directory(lang_code, sub_course_id_from_definition):
    """Creates the actual directory for a sub-course if it's defined in lang's sub_courses.json."""
    # This function assumes sub_course_id_from_definition is an ID that *should* exist
    # in the lang_code/sub_courses.json file.
    # The UI would typically list sub-courses from that JSON, and then an "activate" or
    # "create content for" action would lead here.
    try:
        sub_course_dir_path = _get_full_path(lang_code, sub_course_id_from_definition)
        if os.path.exists(sub_course_dir_path):
            print(f"Info: Directory for sub-course '{sub_course_id_from_definition}' in '{lang_code}' already exists.")
            return True # Or false if you want to signal no action taken
        os.makedirs(sub_course_dir_path)
        # Initialize with an empty pathway_structure.json
        save_json_file(os.path.join(sub_course_dir_path, "pathway_structure.json"), [])
        print(f"Info: Directory and empty pathway_structure.json created for sub-course '{sub_course_id_from_definition}' in '{lang_code}'.")
        return True
    except OSError as e:
        print(f"Error creating directory for sub-course '{sub_course_id_from_definition}': {e}")
        return False
    except ValueError as e:
        print(f"Error: {e}")
        return False

# --- Pathway Structure (Sections) Management ---
def get_pathway_structure_path(lang_code, sub_course_id):
    return _get_full_path(lang_code, sub_course_id, "pathway_structure.json")

def load_pathway_structure(lang_code, sub_course_id):
    try:
        path = get_pathway_structure_path(lang_code, sub_course_id)
        return load_json_file(path, [])
    except ValueError as e:
        print(f"Error: {e}")
        return []

def save_pathway_structure(lang_code, sub_course_id, pathway_data_list):
    try:
        path = get_pathway_structure_path(lang_code, sub_course_id)
        return save_json_file(path, pathway_data_list)
    except ValueError as e:
        print(f"Error: {e}")
        return False


def get_section_base_path(lang_code, sub_course_id, section_code_from_pathway):
    # section_code_from_pathway is the "001", "002" string
    return _get_full_path(lang_code, sub_course_id, section_code_from_pathway)

# --- Lesson Progress, Cutscenes, Lesson Data Files (mostly unchanged, but use _get_full_path indirectly) ---
# These functions will now correctly use the base_path set in CONFIG via _get_full_path.

def get_lesson_progress_path(lang_code, sub_course_id, section_code):
    return os.path.join(get_section_base_path(lang_code, sub_course_id, section_code), "lesson_progress.json")

def load_lesson_progress(lang_code, sub_course_id, section_code):
    try:
        path = get_lesson_progress_path(lang_code, sub_course_id, section_code)
        return load_json_file(path, [])
    except ValueError as e: # Catch if base path not set leading to section path error
        print(f"Error loading lesson progress: {e}")
        return []


def save_lesson_progress(lang_code, sub_course_id, section_code, lesson_progress_data):
    try:
        section_dir = get_section_base_path(lang_code, sub_course_id, section_code)
        if not os.path.exists(section_dir):
            os.makedirs(section_dir)
            print(f"Info: Created section directory '{section_dir}'")
        path = get_lesson_progress_path(lang_code, sub_course_id, section_code)
        return save_json_file(path, lesson_progress_data)
    except OSError as e:
        print(f"Error ensuring section directory or saving lesson progress: {e}")
        return False
    except ValueError as e:
        print(f"Error saving lesson progress: {e}")
        return False


def get_cutscenes_path(lang_code, sub_course_id, section_code):
    return os.path.join(get_section_base_path(lang_code, sub_course_id, section_code), "cutscenes.json")

def load_cutscenes(lang_code, sub_course_id, section_code):
    try:
        path = get_cutscenes_path(lang_code, sub_course_id, section_code)
        return load_json_file(path, [])
    except ValueError as e:
        print(f"Error loading cutscenes: {e}")
        return []

def save_cutscenes(lang_code, sub_course_id, section_code, cutscenes_data):
    try:
        section_dir = get_section_base_path(lang_code, sub_course_id, section_code)
        if not os.path.exists(section_dir):
            os.makedirs(section_dir)
        path = get_cutscenes_path(lang_code, sub_course_id, section_code)
        return save_json_file(path, cutscenes_data)
    except OSError as e:
        print(f"Error ensuring section directory or saving cutscenes: {e}")
        return False
    except ValueError as e:
        print(f"Error saving cutscenes: {e}")
        return False


LESSON_FILE_TYPES = {
    "type1": "type1_vocabulary.json", "type2": "type2_grammar.json",
    "type3": "type3_listening.json", "type4": "type4_sentence.json",
    "type5": "type5_context.json",
}

def get_lesson_data_file_path(lang_code, sub_course_id, section_code, file_type_key):
    filename = LESSON_FILE_TYPES.get(file_type_key)
    if not filename:
        raise ValueError(f"Unknown lesson file type key: {file_type_key}")
    return os.path.join(get_section_base_path(lang_code, sub_course_id, section_code), filename)

def load_lesson_data(lang_code, sub_course_id, section_code, file_type_key):
    try:
        path = get_lesson_data_file_path(lang_code, sub_course_id, section_code, file_type_key)
        return load_json_file(path, [])
    except ValueError as e:
        print(f"Error loading lesson data ({file_type_key}): {e}")
        return []


def save_lesson_data(lang_code, sub_course_id, section_code, file_type_key, data):
    try:
        section_dir = get_section_base_path(lang_code, sub_course_id, section_code)
        if not os.path.exists(section_dir):
            os.makedirs(section_dir)
        path = get_lesson_data_file_path(lang_code, sub_course_id, section_code, file_type_key)
        return save_json_file(path, data)
    except OSError as e:
        print(f"Error ensuring section directory or saving lesson data ({file_type_key}): {e}")
        return False
    except ValueError as e:
        print(f"Error saving lesson data ({file_type_key}): {e}")
        return False
    
# --- Guidebook Structure Management (per sub-course) ---
def get_guidebook_structure_path(lang_code, sub_course_id):
    # Assumes guide_structure.json is directly under the sub-course directory
    return _get_full_path(lang_code, sub_course_id, "guide_structure.json")

def load_guidebook_structure(lang_code, sub_course_id):
    path = get_guidebook_structure_path(lang_code, sub_course_id)
    return load_json_file(path, {"categories": [], "guidebooks": []}) 

def save_guidebook_structure(lang_code, sub_course_id, guidebook_data_obj):
    path = get_guidebook_structure_path(lang_code, sub_course_id)
    sub_course_dir = _get_full_path(lang_code, sub_course_id) # Path to lang/subcourse/
    guidebook_base_dir = os.path.join(sub_course_dir, "guidebook") # Path to lang/subcourse/guidebook/
        
    # Ensure the lang/subcourse/ directory exists for guide_structure.json
    if not os.path.exists(sub_course_dir):
        try:
            os.makedirs(sub_course_dir)
        except OSError as e:
            print(f"Error creating sub-course directory '{sub_course_dir}': {e}")
            return False
                
        # The guide_structure.json itself is directly in the sub-course folder.
        # The 'guidebook' folder is for chapter content.
        # We don't strictly need to create the 'guidebook' folder just to save guide_structure.json,
        # but it's good practice if we anticipate chapter folders being made soon.
        # For now, let's just ensure the parent of guide_structure.json exists.
                
    return save_json_file(path, guidebook_data_obj)

# --- Guidebook Structure Management (per sub-course, inside 'guidebook' folder) ---
def get_guidebook_base_folder_path(lang_code, sub_course_id):
    """Returns the path to Livygo/courses/{lang}/{subcourse}/guidebook/ """
    return _get_full_path(lang_code, sub_course_id, "guidebook")

def get_guidebook_structure_path(lang_code, sub_course_id):
    """Path to guide_structure.json, e.g., .../{lang}/{subcourse}/guidebook/guide_structure.json"""
    return os.path.join(get_guidebook_base_folder_path(lang_code, sub_course_id), "guide_structure.json")

def load_guidebook_structure(lang_code, sub_course_id):
    path = get_guidebook_structure_path(lang_code, sub_course_id)
    return load_json_file(path, {"categories": [], "guidebooks": []}) 

def save_guidebook_structure(lang_code, sub_course_id, guidebook_data_obj):
    path = get_guidebook_structure_path(lang_code, sub_course_id)
    # Ensure the .../{lang}/{subcourse}/guidebook/ directory itself exists before saving guide_structure.json
    guidebook_dir = get_guidebook_base_folder_path(lang_code, sub_course_id)
    if not os.path.exists(guidebook_dir):
        try:
            os.makedirs(guidebook_dir) # This creates .../guidebook/
            print(f"Info: Created guidebook directory '{guidebook_dir}'")
        except OSError as e:
            print(f"Error creating guidebook directory '{guidebook_dir}': {e}")
            return False
            
    return save_json_file(path, guidebook_data_obj)

# --- Guidebook Chapter Meta and Content (New Helpers) ---
def get_guidebook_chapter_base_path(lang_code, sub_course_id, chapter_guidcode):
    """Path to .../{lang}/{subcourse}/guidebook/{chapter_guidcode}/"""
    return os.path.join(get_guidebook_base_folder_path(lang_code, sub_course_id), chapter_guidcode)

def get_guidebook_chapter_meta_path(lang_code, sub_course_id, chapter_guidcode):
    return os.path.join(get_guidebook_chapter_base_path(lang_code, sub_course_id, chapter_guidcode), "meta.json")

def load_guidebook_chapter_meta(lang_code, sub_course_id, chapter_guidcode):
    path = get_guidebook_chapter_meta_path(lang_code, sub_course_id, chapter_guidcode)
    return load_json_file(path, {"formatVersion": 2, "sections": []})

def save_guidebook_chapter_meta(lang_code, sub_course_id, chapter_guidcode, meta_data_obj):
    path = get_guidebook_chapter_meta_path(lang_code, sub_course_id, chapter_guidcode)
    # Ensure chapter directory exists before saving meta.json
    chapter_dir = get_guidebook_chapter_base_path(lang_code, sub_course_id, chapter_guidcode)
    if not os.path.exists(chapter_dir):
        try:
            os.makedirs(os.path.join(chapter_dir, "media"), exist_ok=True) # Create media subfolder too
            print(f"Info: Created chapter directory with media subfolder: '{chapter_dir}'")
        except OSError as e:
            print(f"Error creating chapter directory '{chapter_dir}': {e}")
            return False
    return save_json_file(path, meta_data_obj)

def get_guidebook_chapter_content_path(lang_code, sub_course_id, chapter_guidcode, content_filename):
    return os.path.join(get_guidebook_chapter_base_path(lang_code, sub_course_id, chapter_guidcode), content_filename)

def get_guidebook_chapter_media_path(lang_code, sub_course_id, chapter_guidcode, media_filename):
    return os.path.join(get_guidebook_chapter_base_path(lang_code, sub_course_id, chapter_guidcode), "media", media_filename)

def load_text_file_content(file_path):
    """Loads the content of a text file (e.g., markdown)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Info: Text file not found '{file_path}'")
        return None # Or empty string ""
    except Exception as e:
        print(f"Error reading text file '{file_path}': {e}")
        return None

def save_text_file_content(file_path, content_str):
    """Saves string content to a text file."""
    _ensure_dir(file_path) # Ensure parent directory exists
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content_str)
        print(f"Info: Saved text file '{file_path}'")
        return True
    except IOError as e:
        print(f"Error writing text file '{file_path}': {e}")
        return False


# --- Example Usage ---
if __name__ == "__main__":
    # IMPORTANT: User needs to set this path, e.g., via a file dialog in a real app
    # For this test, we create a temporary one.
    temp_courses_root = "temp_livygo_courses_test"
    if os.path.exists(temp_courses_root): # Clean up from previous run
        shutil.rmtree(temp_courses_root)
    os.makedirs(temp_courses_root)

    if not set_courses_base_path(temp_courses_root):
        print("Failed to set base path for testing. Exiting.")
        exit()

    print(f"Livygo Editor - Core Logic Test (using base: {CONFIG['courses_base_path']})")

    # Test Language & its sub_courses.json
    print("\n--- Languages & Sub-courses ---")
    add_language("XY-testlang")
    print(f"Current languages: {list_languages()}")

    sub_courses_xy = load_sub_courses_for_lang("XY-testlang")
    print(f"Initial sub_courses for XY-testlang: {sub_courses_xy}")
    sub_courses_xy.append({"id": "main", "title": "Main Course", "icon": "🌟"})
    sub_courses_xy.append({"id": "extra", "title": "Extra Practice", "icon": "🎯"})
    save_sub_courses_for_lang("XY-testlang", sub_courses_xy)
    print(f"Updated sub_courses for XY-testlang: {load_sub_courses_for_lang('XY-testlang')}")

    # Test creating sub-course directory
    print("\n--- Creating Sub-course Directory ---")
    create_sub_course_directory("XY-testlang", "main") # 'main' is from the sub_courses_xy list
    print(f"Active sub-course IDs for XY-testlang: {list_active_sub_course_ids_for_lang('XY-testlang')}")

    # Test Pathway Structure for XY-testlang/main
    print("\n--- Pathway Structure (XY-testlang/main) ---")
    pathway = load_pathway_structure("XY-testlang", "main")
    new_section = {
        "code": "S01", "title": "Starter Section", "numCircles": 5,
        "defaultAddress": f'/courses/XY-testlang/main/S01/',
        "addressMap": [{"rangeStart": "S01C01", "rangeEnd": "S01C05", "path": f'/courses/XY-testlang/main/S01/'}],
        "settings": {"relearnpool": True, "enabledQuestionTypes": ["type1", "type2"]}
    }
    pathway.append(new_section)
    save_pathway_structure("XY-testlang", "main", pathway)
    print(f"Updated pathway for XY-testlang/main: {load_pathway_structure('XY-testlang', 'main')}")

    # Test Lesson Progress for the new section S01
    print("\n--- Lesson Progress (XY-testlang/main/S01) ---")
    lp = load_lesson_progress("XY-testlang", "main", "S01")
    lp.append({"code": "S01C01", "title": "First Circle", "questionsPerLesson": 3})
    save_lesson_progress("XY-testlang", "main", "S01", lp)
    print(f"Updated LP for S01: {load_lesson_progress('XY-testlang', 'main', 'S01')}")

    # Test Type 1 data for section S01
    print("\n--- Type 1 Data (XY-testlang/main/S01) ---")
    t1 = load_lesson_data("XY-testlang", "main", "S01", "type1")
    t1.append({"code": "S01C01", "word": "hello", "translation": "hola"})
    save_lesson_data("XY-testlang", "main", "S01", "type1", t1)
    print(f"Updated Type 1 for S01: {load_lesson_data('XY-testlang', 'main', 'S01', 'type1')}")

    # # Optional: Clean up the temporary directory after tests
    # if input("Clean up temp_livygo_courses_test? (y/n): ").lower() == 'y':
    #     shutil.rmtree(temp_courses_root)
    #     print(f"Cleaned up {temp_courses_root}")