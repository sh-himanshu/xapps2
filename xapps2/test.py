import re

import yaml

with open("config.yaml", "r") as f:
    apps_conf = yaml.load(f, Loader=yaml.FullLoader)
for app in apps_conf["custom"]:
    print("_".join(re.sub(r"[^A-Za-z0-9]", " ", app["app"]).split()) + ".apk")
