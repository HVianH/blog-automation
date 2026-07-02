import yaml

def load_blogs():
    with open("config/blogs.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["blogs"]


def save_blogs(blogs):
    data = {"blogs": blogs}
    with open("config/blogs.yaml", "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)