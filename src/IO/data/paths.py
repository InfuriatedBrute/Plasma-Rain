import os

project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
print(project_dir)
mods_dir = os.path.join(project_dir, "data\\mods\\")
print(mods_dir)
saves_dir = os.path.join(project_dir, "data\\saves\\")
settings_dir = os.path.join(project_dir, "data\\settings\\")