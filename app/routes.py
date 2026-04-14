import toml
import json
import datetime
import os
import signal
import subprocess
import time
import threading
import sys
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask import current_app as app

FRPC_TOML_PATH = "frpc.toml"
APP_CONFIG_PATH = "app_config.json"
FRPC_BIN_PATH = "frp/frpc"
FRPC_PID_PATH = "logs/frpc.pid"
FRPC_LOG_PATH = "logs/frpc.log"


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


def _ensure_frpc_dirs():
    for path in (FRPC_LOG_PATH, FRPC_PID_PATH):
        dir_path = os.path.dirname(path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)


def _log_frpc(message: str):
    _ensure_frpc_dirs()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}\n"
    try:
        with open(FRPC_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass
    sys.stdout.write(line)
    sys.stdout.flush()


def _is_process_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False
    except OSError:
        return False


def get_frpc_pid():
    if not os.path.exists(FRPC_PID_PATH):
        return None
    try:
        with open(FRPC_PID_PATH, "r", encoding="utf-8") as f:
            pid = int(f.read().strip())
        if _is_process_running(pid):
            return pid
    except Exception:
        return None
    return None


def start_frpc():
    running_pid = get_frpc_pid()
    if running_pid:
        _log_frpc(f"frpc 已在运行，PID={running_pid}，将先停止再启动")
        ok, message = stop_frpc()
        if not ok:
            return False, f"启动前停止失败: {message}"

    if not os.path.exists(FRPC_BIN_PATH):
        _log_frpc(f"frpc 不存在: {FRPC_BIN_PATH}")
        return False, f"frpc 不存在: {FRPC_BIN_PATH}"

    try:
        os.chmod(FRPC_BIN_PATH, 0o755)
        _ensure_frpc_dirs()
        log_file = open(FRPC_LOG_PATH, "a", encoding="utf-8")
        process = subprocess.Popen(
            [f"{FRPC_BIN_PATH}", "-c", FRPC_TOML_PATH],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        _log_frpc(f"frpc 启动命令: {FRPC_BIN_PATH} -c {FRPC_TOML_PATH}")
        _log_frpc(f"frpc 启动中，PID={process.pid}")

        def _stream_logs():
            try:
                if process.stdout is None:
                    return
                for line in process.stdout:
                    log_file.write(line)
                    log_file.flush()
                    sys.stdout.write(line)
                    sys.stdout.flush()
            finally:
                try:
                    log_file.close()
                except Exception:
                    pass

        threading.Thread(target=_stream_logs, daemon=True).start()

        with open(FRPC_PID_PATH, "w", encoding="utf-8") as f:
            f.write(str(process.pid))
        return True, f"frpc 已启动，PID={process.pid}，日志: {FRPC_LOG_PATH}"
    except Exception as exc:
        _log_frpc(f"启动 frpc 失败: {exc}")
        return False, f"启动 frpc 失败: {exc}"
    except Exception as exc:
        return False, f"启动 frpc 失败: {exc}"


def stop_frpc():
    pid = get_frpc_pid()
    if not pid:
        _log_frpc("frpc 未运行，无需停止")
        return True, "frpc 未运行"
    try:
        _log_frpc(f"尝试停止 frpc，PID={pid}")
        os.kill(pid, signal.SIGTERM)
        timeout_at = time.time() + 8
        while time.time() < timeout_at:
            if not _is_process_running(pid):
                break
            time.sleep(0.2)
        if _is_process_running(pid):
            _log_frpc(f"SIGTERM 超时，发送 SIGKILL，PID={pid}")
            os.kill(pid, signal.SIGKILL)
        if os.path.exists(FRPC_PID_PATH):
            os.remove(FRPC_PID_PATH)
        _log_frpc("frpc 已停止")
        return True, "frpc 已停止"
    except Exception as exc:
        _log_frpc(f"停止 frpc 失败: {exc}")
        return False, f"停止 frpc 失败: {exc}"


def restart_frpc():
    _log_frpc("开始重启 frpc")
    ok, message = stop_frpc()
    if not ok:
        _log_frpc(f"重启失败，停止阶段错误: {message}")
        return False, message
    ok, message = start_frpc()
    if ok:
        _log_frpc("重启完成")
    else:
        _log_frpc(f"重启失败，启动阶段错误: {message}")
    return ok, message


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

    proxies = []
    for proxy in frpc_config.get("proxies", []):
        display_settings = app_config.get("proxies_display", {}).get(
            proxy.get("name", ""),
            {"visible": True, "displayName": proxy.get("name", "")},
        )
        proxy_info = proxy.copy()
        proxy_info["displayName"] = display_settings.get(
            "displayName", proxy.get("name", "")
        )
        proxy_info["visible"] = display_settings.get("visible", True)
        proxies.append(proxy_info)

    proxies.sort(
        key=lambda item: (
            item.get("remotePort") or 0,
            item.get("localIP") or "",
            item.get("localPort") or 0,
            item.get("type") or "",
        )
    )

    return render_template(
        "config.html",
        proxies=proxies,
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


@app.route("/frpc/restart", methods=["POST"])
def frpc_restart():
    ok, message = restart_frpc()
    status = "success" if ok else "error"
    if request.is_json:
        return jsonify({"status": status, "message": message})
    flash(message, status)
    return redirect(url_for("home"))


@app.route("/frpc/log")
def frpc_log():
    if not os.path.exists(FRPC_LOG_PATH):
        return jsonify({"status": "error", "message": "frpc 日志不存在"}), 404
    try:
        with open(FRPC_LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return jsonify({"status": "success", "log": content[-8000:]})
    except Exception as exc:
        return jsonify({"status": "error", "message": f"读取日志失败: {exc}"}), 500


@app.route("/frpc/log/view")
def frpc_log_view():
    if not os.path.exists(FRPC_LOG_PATH):
        return render_template("frpc_log.html", log="frpc 日志不存在")
    try:
        with open(FRPC_LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return render_template("frpc_log.html", log=content[-8000:])
    except Exception as exc:
        return render_template("frpc_log.html", log=f"读取日志失败: {exc}")


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

    proxies.insert(0, new_proxy)
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
