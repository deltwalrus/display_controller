import os
import subprocess
import time
from flask import Flask, render_template_string, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

# --- CONFIGURATION ---
UPLOAD_FOLDER = '/home/ppcpi/display_controller/media/family_photos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MPV_SOCKET = "/tmp/mpv_socket"
CURRENT_MODE = None

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- HTML UI ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Wall Control</title>
    <style>
        body { background: #121212; color: #eee; font-family: system-ui, sans-serif; text-align: center; padding: 20px; }
        h3 { color: #888; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: 1fr; gap: 15px; max-width: 500px; margin: 0 auto 30px auto; }
        
        /* Main Buttons */
        button {
            border: none; border-radius: 12px; padding: 20px; font-size: 1.1rem; font-weight: bold; 
            color: white; cursor: pointer; transition: opacity 0.2s; width: 100%;
        }
        button:active { opacity: 0.7; }
        .btn-photo { background: #e91e63; }
        .btn-art { background: #00bcd4; }
        .btn-retro { background: #ff9800; color: #222; }
        .btn-trippy { background: #9c27b0; }
        .btn-dash { background: #4caf50; }
        .btn-off { background: #444; }

        /* Upload Section */
        .upload-zone {
            background: #1e1e1e; padding: 20px; border-radius: 15px; max-width: 500px; margin: 0 auto;
            border: 2px dashed #333;
        }
        .upload-btn {
            background: #333; margin-top: 10px; padding: 15px; font-size: 1rem;
        }
        input[type="file"] { display: none; }
        .custom-file-upload {
            display: inline-block; padding: 15px 30px; cursor: pointer;
            background: #2196F3; border-radius: 8px; font-weight: bold; width: 80%;
        }
    </style>
</head>
<body>
    <h3>DISPLAY CONTROLLER</h3>
    
    <div class="grid">
        <button class="btn-photo" onclick="mode('photos')">📸 Photos / Next</button>
        <button class="btn-art" onclick="mode('slow_art')">🏔️ Slow Art / Next</button>
        <button class="btn-retro" onclick="mode('retro')">🕹️ Retro / Next</button>
        <button class="btn-trippy" onclick="mode('trippy')">🌀 Trippy</button>
        <button class="btn-dash" onclick="mode('dashboard')">📊 Dashboard</button>
        <button class="btn-off" onclick="mode('off')">🛑 Screen Off</button>
    </div>

    <div class="upload-zone">
        <h4>Add New Photo</h4>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <label class="custom-file-upload">
                <input type="file" name="file" multiple onchange="this.form.submit()">
                📂 Select from Phone
            </label>
        </form>
    </div>

    <script>
        function mode(m) { fetch('/mode/' + m); }
    </script>
</body>
</html>
"""

# --- HELPER FUNCTIONS ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def kill_all():
    os.system("pkill -f chromium")
    os.system("pkill -f mpv")
    os.system("pkill -f glslViewer")
    os.system("pkill -f electron") 

def run_mpv(path, is_playlist=False):
    kill_all()
    time.sleep(0.5)
    cmd = f"mpv --fs --vo=gpu --hwdec=auto --no-osd-bar --input-ipc-server={MPV_SOCKET} "
    if is_playlist: cmd += "--loop-playlist=inf --shuffle "
    else: cmd += "--loop "
    cmd += path
    env = os.environ.copy()
    env["DISPLAY"] = ":0"
    subprocess.Popen(cmd, shell=True, env=env, preexec_fn=os.setsid)

# --- ROUTING ---
@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: return redirect(request.url)
    
    # getlist() allows us to handle multiple selections
    files = request.files.getlist('file')
    
    for file in files:
        if file.filename == '': continue
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
    return redirect(url_for('index'))
@app.route('/mode/photos')
def photos():
    global CURRENT_MODE
    if CURRENT_MODE == 'photos':
        os.system("curl -s http://localhost:8080/api/notification/BACKGROUNDSLIDESHOW_NEXT")
        return "Skipped"
    kill_all()
    CURRENT_MODE = 'photos'
    subprocess.Popen("cd /home/ppcpi/MagicMirror && npm run start", shell=True, env=dict(os.environ, DISPLAY=":0"), preexec_fn=os.setsid)
    return "Started"

@app.route('/mode/slow_art')
def slow_art():
    global CURRENT_MODE
    if CURRENT_MODE == 'slow_art':
        os.system(f"echo 'playlist-next' | socat - {MPV_SOCKET}")
        return "Skipped"
    CURRENT_MODE = 'slow_art'
    run_mpv("/home/ppcpi/display_controller/media/slow_art/", is_playlist=True)
    return "Started"

@app.route('/mode/retro')
def retro():
    global CURRENT_MODE
    if CURRENT_MODE == 'retro':
        os.system(f"echo 'playlist-next' | socat - {MPV_SOCKET}")
        return "Skipped"
    CURRENT_MODE = 'retro'
    run_mpv("/home/ppcpi/display_controller/media/retro/", is_playlist=True)
    return "Started"

@app.route('/mode/trippy')
def trippy():
    global CURRENT_MODE
    kill_all()
    CURRENT_MODE = 'trippy'
    cmd = "glslViewer /home/ppcpi/display_controller/media/trippy/shader.frag --fullscreen"
    subprocess.Popen(cmd, shell=True, env=dict(os.environ, DISPLAY=":0"), preexec_fn=os.setsid)
    return "Started"

@app.route('/mode/dashboard')
def dashboard():
    global CURRENT_MODE
    if CURRENT_MODE == 'dashboard':
        os.system("export DISPLAY=:0 && xdotool key F5")
        return "Reloaded"
    kill_all()
    CURRENT_MODE = 'dashboard'
    # Ensure --password-store=basic is set to avoid keyring popups
    url = "https://cybermap.kaspersky.com/en/widget/dynamic/dark"
    cmd = f"chromium --kiosk --noerrdialogs --disable-infobars --password-store=basic '{url}'"
    subprocess.Popen(cmd, shell=True, env=dict(os.environ, DISPLAY=":0"), preexec_fn=os.setsid)
    return "Started"

@app.route('/mode/off')
def off():
    global CURRENT_MODE
    kill_all()
    CURRENT_MODE = 'off'
    return "Off"

if __name__ == '__main__':
    # Boot into Photos
    kill_all()
    CURRENT_MODE = 'photos'
    print("Booting into Photo Mode...")
    subprocess.Popen("cd /home/ppcpi/MagicMirror && npm run start", shell=True, env=dict(os.environ, DISPLAY=":0"), preexec_fn=os.setsid)
    app.run(host='0.0.0.0', port=5000)
