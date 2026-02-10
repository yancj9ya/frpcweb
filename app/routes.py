import toml
import json
import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask import current_app as app

FRPC_TOML_PATH = "frpc.toml"
APP_CONFIG_PATH = "app_config.json"


def read_config():
    """Reads and parses the frpc.toml file."""
    try:
        with open(FRPC_TOML_PATH, "r", encoding="utf-8") as f:
            return toml.load(f)
    except (FileNotFoundError, toml.TomlDecodeError) as e:
        flash(f"Error reading frpc.toml: {e}", "error")
        return {}


def write_config(config_data):
    """Writes the config data back to the frpc.toml file."""
    try:
        with open(FRPC_TOML_PATH, "w", encoding="utf-8") as f:
            toml.dump(config_data, f)
        flash("frpc.toml saved successfully!", "success")
    except Exception as e:
        flash(f"Error writing frpc.toml: {e}", "error")


def read_app_config():
    """Reads and parses the app_config.json file."""
    try:
        with open(APP_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"target_ip": "127.0.0.1", "proxies_display": {}}


def write_app_config(config_data):
    """Writes the config data back to the app_config.json file."""
    try:
        with open(APP_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)
        flash("App config saved successfully!", "success")
    except Exception as e:
        flash(f"Error writing app config: {e}", "error")


@app.route("/")
def home():
    frpc_config = read_config()
    app_config = read_app_config()
    now = datetime.datetime.now().timestamp()

    visible_proxies = []
    for proxy in frpc_config.get("proxies", []):
        display_settings = app_config.get("proxies_display", {}).get(
            proxy["name"], {"visible": True}
        )
        if display_settings.get("visible", True):
            proxy_info = proxy.copy()
            proxy_info["displayName"] = display_settings.get(
                "displayName", proxy["name"]
            )
            visible_proxies.append(proxy_info)

    return render_template(
        "index.html",
        proxies=visible_proxies,
        target_ip=app_config.get("target_ip", "127.0.0.1"),
        now=now,
    )


@app.route("/config")
def config():
    frpc_config = read_config()
    app_config = read_app_config()
    now = datetime.datetime.now().timestamp()
    return render_template(
        "config.html",
        proxies=frpc_config.get("proxies", []),
        app_config=app_config,
        now=now,
    )


@app.route("/settings", methods=["GET", "POST"])
def settings():
    now = datetime.datetime.now().timestamp()
    if request.method == "POST":
        app_config = read_app_config()
        app_config["target_ip"] = request.form["target_ip"]
        write_app_config(app_config)
        return redirect(url_for("settings"))

    app_config = read_app_config()
    return render_template(
        "settings.html",
        target_ip=app_config.get("target_ip", "127.0.0.1"),
        now=now,
    )


@app.route("/add_proxy", methods=["POST"])
def add_proxy():
    config = read_config()
    proxies = config.get("proxies", [])

    new_proxy = {
        "name": request.form["name"],
        "type": request.form["type"],
        "localIP": request.form["local_ip"],
        "localPort": int(request.form["local_port"]),
        "remotePort": int(request.form["remote_port"]),
    }

    proxies.append(new_proxy)
    config["proxies"] = proxies
    write_config(config)

    return redirect(url_for("config"))


@app.route("/edit_proxy/<proxy_name>", methods=["POST"])
def edit_proxy(proxy_name):
    # 处理JSON请求
    if request.is_json:
        data = request.get_json()
        print(f"Received JSON data: {data}")  # 调试信息
        frpc_config = read_config()
        app_config = read_app_config()
        proxies = frpc_config.get("proxies", [])

        # 更新frpc.toml
        proxy_found = False
        for proxy in proxies:
            if proxy["name"] == proxy_name:
                proxy_found = True
                proxy["type"] = data["type"]
                proxy["localIP"] = data["local_ip"]
                proxy["localPort"] = int(data["local_port"])
                proxy["remotePort"] = int(data["remote_port"])
                break

        if not proxy_found:
            print(f"Proxy {proxy_name} not found")  # 调试信息
            return jsonify({"status": "error", "message": "Proxy not found"}), 404

        frpc_config["proxies"] = proxies
        write_config(frpc_config)

        # 更新app_config.json
        display_name = data.get("display_name", proxy_name)
        is_visible = data.get("visible", True)
        app_config.setdefault("proxies_display", {})[proxy_name] = {
            "displayName": display_name,
            "visible": is_visible,
        }
        write_app_config(app_config)

        return jsonify({"status": "success"})

    # 处理表单请求（向后兼容）
    frpc_config = read_config()
    app_config = read_app_config()
    proxies = frpc_config.get("proxies", [])

    # 更新frpc.toml
    proxy_found = False
    for proxy in proxies:
        if proxy["name"] == proxy_name:
            proxy_found = True
            proxy["type"] = request.form["type"]
            proxy["localIP"] = request.form["local_ip"]
            proxy["localPort"] = int(request.form["local_port"])
            proxy["remotePort"] = int(request.form["remote_port"])
            break

    if not proxy_found:
        flash(f"Proxy {proxy_name} not found", "error")
        return redirect(url_for("config"))

    frpc_config["proxies"] = proxies
    write_config(frpc_config)

    # 更新app_config.json
    display_name = request.form.get("display_name", proxy_name)
    is_visible = "visible" in request.form
    app_config.setdefault("proxies_display", {})[proxy_name] = {
        "displayName": display_name,
        "visible": is_visible,
    }
    write_app_config(app_config)

    return redirect(url_for("config"))


@app.route("/delete_proxy/<proxy_name>")
def delete_proxy(proxy_name):
    frpc_config = read_config()
    app_config = read_app_config()

    # Remove from frpc.toml
    proxies = frpc_config.get("proxies", [])
    proxies = [p for p in proxies if p["name"] != proxy_name]
    frpc_config["proxies"] = proxies
    write_config(frpc_config)

    # Remove from app_config.json
    if proxy_name in app_config.get("proxies_display", {}):
        del app_config["proxies_display"][proxy_name]
        write_app_config(app_config)

    return redirect(url_for("config"))
