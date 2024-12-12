from jinja2 import Environment, FileSystemLoader, select_autoescape
import yaml
import glob
import os
import shutil

def default_title(name):
    return name.replace("_", " ").replace("-", " ").title()

def load_gallery(gallery):
    name = os.path.basename(gallery)
    return {
        "type": "gallery",
        "name": name,
        "title": default_title(name),        
        "images": [
            load_image(image) for image in sorted(glob.iglob(f"{gallery}/*"))
        ]
    }

def load_image(image):
    name = os.path.splitext(os.path.basename(image))[0]
    return {
        "type": "image",
        "name": name,
        "title": default_title(name),
        "src": image.removeprefix("static/"),
        "thumb": f"thumbnails{image.removeprefix("static/images")}"
    }

def filter_entry(entries, entry_data):
    entry = next((e for e in entries if e["name"] == entry_data["name"]), None)
    if entry == None:
        raise KeyError(f"entry '{entry_data["name"]}' not found")

    if "title" in entry_data:
        entry["title"] = entry_data["title"]
    
    if "select" in entry_data:
        if entry["type"] != "gallery":
            raise RuntimeError(f"'select' attribute found, but corresponding entry {entry} is not a gallery")
        entry["selected_images"] = [entry["images"][i-1] for i in entry_data["select"]]
    elif entry["type"] == "gallery":
        entry["selected_images"] = entry["images"][0:3]

    return entry 
        

def load_section(section, section_data):
    entries = [
        load_image(entry) if os.path.isfile(entry) else load_gallery(entry)
        for entry in sorted(glob.iglob(f"static/images/{section}/*"))
    ]

    if section_data != None and "order" in section_data:
        entries = [filter_entry(entries, data) for data in section_data["order"]]
    
    return {
        "title": os.path.basename(section),
        "entries": entries
    }

def load_sections(metadata):
    return [load_section(section, section_data) for section, section_data in metadata["sections"].items()]
    
def copy_static():
    for tree in glob.iglob("static/*"):
        dest = "public/"+tree.removeprefix("static/")
        if os.path.isdir(tree):
            shutil.copytree(tree, dest, dirs_exist_ok=True)
        else:
            shutil.copy(tree, dest)
    

def generate():
    env = Environment(
        loader = FileSystemLoader("templates"),
        autoescape = select_autoescape(),
        trim_blocks = True,
        lstrip_blocks = True,
    )

    with open("metadata.yml") as f:
        metadata = yaml.safe_load(f)

    sections = load_sections(metadata)

    copy_static()

    index = env.get_template("index.html")
    with open("public/index.html", "w") as f:
        f.write(index.render(sections=sections))
    about = env.get_template("about.html")
    with open("public/about.html", "w") as f:
        f.write(about.render(sections=sections))

    single = env.get_template("single.html")
    for section in sections:
        for entry in section["entries"]:
            directory = f"public/{section["title"]}"
            if not os.path.isdir(f"public/{section["title"]}"):
                os.makedirs(directory)
            with open(f"{directory}/{entry["name"]}.html", "w") as f:
                f.write(single.render(entry=entry))
            


generate()

    
