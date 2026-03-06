import os
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.camera import Camera
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.clock import Clock
import cryptomatic4000
from cryptomatic4000 import PasswordFileEncryptor
import numpy as np
import cv2
import CRUD

# Directory anchored to this file's location
BASE_DIR = os.path.dirname(__file__)

# ─── UI Definition ────────────────────────────────────────────────────────────
Builder.load_string('''
<LoginScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 50
        spacing: 20
        canvas.before:
            Color:
                rgba: 0.98, 0.98, 0.98, 1
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: 'Welcome Back'
            font_size: '32sp'
            bold: True
            color: 0.2, 0.2, 0.2, 1

        TextInput:
            id: username_input
            hint_text: 'Username'
            multiline: False
            size_hint_y: None
            height: '48dp'
            padding: [15, 12]
            background_normal: ''
            background_color: 1, 1, 1, 1
            foreground_color: 0.1, 0.1, 0.1, 1
            cursor_color: 0.1, 0.1, 0.1, 1
            canvas.after:
                Color:
                    rgba: 0.8, 0.8, 0.8, 1
                Line:
                    width: 1
                    rectangle: (self.x, self.y, self.width, self.height)

        BoxLayout:
            id: login_camera_container
            orientation: 'vertical'
            size_hint_y: None
            height: '250dp'
            padding: 5
            canvas.before:
                Color:
                    rgba: 0.9, 0.9, 0.9, 1
                Rectangle:
                    pos: self.pos
                    size: self.size

        Button:
            text: 'Sign In & Capture'
            size_hint_y: None
            height: '48dp'
            background_normal: ''
            background_color: 0.1, 0.45, 0.9, 1
            color: 1, 1, 1, 1
            on_press: root.capture_and_login()
            canvas.before:
                Color:
                    rgba: 0.1, 0.45, 0.9, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [4, ]

        Button:
            text: "Don't have an account? Sign Up"
            size_hint_y: None
            height: '40dp'
            background_normal: ''
            background_color: 0, 0, 0, 0
            color: 0.1, 0.45, 0.9, 1
            on_press: root.manager.current = 'signup'

        Widget:

<SignUpScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 20
        canvas.before:
            Color:
                rgba: 0.98, 0.98, 0.98, 1
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: 'Create Account'
            font_size: '28sp'
            bold: True
            color: 0.2, 0.2, 0.2, 1
            size_hint_y: None
            height: '50dp'

        TextInput:
            id: signup_username
            hint_text: 'Choose Username'
            multiline: False
            size_hint_y: None
            height: '48dp'
            padding: [15, 12]
            background_normal: ''
            background_color: 1, 1, 1, 1
            foreground_color: 0.1, 0.1, 0.1, 1
            canvas.after:
                Color:
                    rgba: 0.8, 0.8, 0.8, 1
                Line:
                    width: 1
                    rectangle: (self.x, self.y, self.width, self.height)

        BoxLayout:
            id: signup_camera_container
            orientation: 'vertical'
            size_hint_y: None
            height: '300dp'
            padding: 5
            canvas.before:
                Color:
                    rgba: 0.9, 0.9, 0.9, 1
                Rectangle:
                    pos: self.pos
                    size: self.size

        Button:
            text: 'Capture & Register'
            size_hint_y: None
            height: '48dp'
            background_normal: ''
            background_color: 0.1, 0.45, 0.9, 1
            color: 1, 1, 1, 1
            on_press: root.capture_and_signup()
            canvas.before:
                Color:
                    rgba: 0.1, 0.45, 0.9, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [4, ]

        Button:
            text: "Already have an account? Login"
            size_hint_y: None
            height: '40dp'
            background_normal: ''
            background_color: 0, 0, 0, 0
            color: 0.1, 0.45, 0.9, 1
            on_press: root.manager.current = 'login'

<DashboardScreen>:
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size

        # Header
        BoxLayout:
            size_hint_y: None
            height: '64dp'
            padding: [20, 10]
            spacing: 10
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
                Color:
                    rgba: 0.9, 0.9, 0.9, 1
                Line:
                    points: [self.x, self.y, self.x + self.width, self.y]
                    width: 1

            Label:
                text: 'Bionicrypt'
                bold: True
                font_size: '22sp'
                halign: 'left'
                valign: 'middle'
                text_size: self.size
                color: 0.3, 0.3, 0.3, 1

            Button:
                text: 'Logout'
                size_hint: None, None
                size: '90dp', '36dp'
                pos_hint: {'center_y': 0.5}
                background_normal: ''
                background_color: 0, 0, 0, 0
                color: 0.85, 0.25, 0.25, 1
                font_size: '14sp'
                bold: True
                on_press: root.logout()
                canvas.before:
                    Color:
                        rgba: 1, 0.92, 0.92, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [6, ]
                    Color:
                        rgba: 0.85, 0.25, 0.25, 0.4
                    Line:
                        width: 1
                        rounded_rectangle: (self.x, self.y, self.width, self.height, 6)

        ScrollView:
            GridLayout:
                id: file_grid
                cols: 1
                padding: 20
                spacing: 15
                size_hint_y: None
                height: self.minimum_height

        AnchorLayout:
            anchor_x: 'right'
            anchor_y: 'bottom'
            padding: 30
            size_hint_y: None
            height: '120dp'

            Button:
                text: '+'
                size_hint: None, None
                size: '56dp', '56dp'
                font_size: '32sp'
                background_normal: ''
                background_color: 1, 1, 1, 0
                color: 0.2, 0.6, 1, 1
                on_press: root.open_file_chooser()
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [16, ]
                    Color:
                        rgba: 0.9, 0.9, 0.9, 1
                    Line:
                        width: 1.1
                        rounded_rectangle: (self.x, self.y, self.width, self.height, 16)

<FileEntry>:
    orientation: 'horizontal'
    size_hint_y: None
    height: '60dp'
    padding: [15, 8]
    spacing: 10
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [8, ]
        Color:
            rgba: 0.95, 0.95, 0.95, 1
        Line:
            width: 1
            rounded_rectangle: (self.x, self.y, self.width, self.height, 8)

    Label:
        id: file_name
        text: 'filename.txt'
        halign: 'left'
        valign: 'middle'
        text_size: self.size
        color: 0.2, 0.2, 0.2, 1
        font_size: '15sp'

    Button:
        id: download_decrypt_btn
        text: 'Download & Decrypt'
        size_hint: None, None
        size: '160dp', '36dp'
        pos_hint: {'center_y': 0.5}
        background_normal: ''
        background_color: 0, 0, 0, 0
        color: 0.1, 0.55, 0.3, 1
        font_size: '13sp'
        bold: True
        canvas.before:
            Color:
                rgba: 0.9, 1, 0.93, 1
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [6, ]
            Color:
                rgba: 0.1, 0.55, 0.3, 0.4
            Line:
                width: 1
                rounded_rectangle: (self.x, self.y, self.width, self.height, 6)
''')


# ─── Camera Helper ────────────────────────────────────────────────────────────

def _camera_to_cv2(camera):
    """Convert a Kivy Camera widget's current texture to an OpenCV BGR image."""
    texture = camera.texture
    if texture is None:
        return None
    size = texture.size
    pixels = texture.pixels
    arr = np.frombuffer(pixels, dtype=np.uint8).reshape((size[1], size[0], 4))
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
    return cv2.flip(bgr, 0)   # Kivy: origin bottom-left → OpenCV: top-left


# ─── File Entry Row ───────────────────────────────────────────────────────────

class FileEntry(BoxLayout):
    """
    A single row in the drive list.
    'Download & Decrypt' button:
      1. Fetch the .enc file from the server (falls back to local enc_file/ copy)
      2. Decrypt on device using the vault key
      3. Save to dec_file/
    """

    def __init__(self, filename, filepath, **kwargs):
        super().__init__(**kwargs)
        self.enc_filename = filename          # e.g. photo.jpg.enc
        self.enc_filepath = filepath          # full path to local .enc file
        self.ids.file_name.text = filename
        self.ids.download_decrypt_btn.bind(on_release=self.download_and_decrypt)

    def download_and_decrypt(self, *args):
        app = App.get_running_app()
        if not app.vault_key:
            self._show_popup("Not Logged In", "No vault key found. Please log in again.")
            return

        username = app.current_username or "unknown"
        enc_dir = os.path.join(BASE_DIR, 'enc_file')
        os.makedirs(enc_dir, exist_ok=True)
        local_enc_path = os.path.join(enc_dir, self.enc_filename)

        # ── Step 1: Fetch encrypted file from server ──────────────────────────
        fetched = False
        try:
            fetched = CRUD.retrieveFile(username, self.enc_filename, local_enc_path)
        except Exception as e:
            print(f"[CRUD] retrieveFile error (will use local copy): {e}")

        if not fetched:
            # Fall back to whatever is already in enc_file/
            if not os.path.exists(local_enc_path):
                self._show_popup(
                    "File Not Found",
                    f"Could not download '{self.enc_filename}' from server and no local copy exists."
                )
                return
            print(f"[Offline] Using local copy: {local_enc_path}")

        # ── Step 2: Decrypt on device ─────────────────────────────────────────
        dec_dir = os.path.join(BASE_DIR, 'dec_file')
        os.makedirs(dec_dir, exist_ok=True)
        base_name = os.path.basename(local_enc_path)
        out_name = base_name[:-4] if base_name.endswith('.enc') else base_name + '.decrypted'
        out_path = os.path.join(dec_dir, out_name)

        try:
            encryptor = PasswordFileEncryptor(str(app.vault_key))
            encryptor.decrypt_file(local_enc_path, out_path)
            self._show_popup(
                "Downloaded & Decrypted",
                f"File saved to dec_file/:\n{out_name}"
            )
            print(f"Decrypted: {local_enc_path} -> {out_path}")
        except Exception as e:
            self._show_popup("Decryption Failed", f"Could not decrypt:\n{e}")
            print(f"Decryption error: {e}")

    def _show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message))
        btn = Button(text='OK', size_hint=(1, 0.3))
        content.add_widget(btn)
        popup = Popup(title=title, content=content, size_hint=(0.85, 0.5))
        btn.bind(on_release=popup.dismiss)
        popup.open()


# ─── Login Screen ─────────────────────────────────────────────────────────────

class LoginScreen(Screen):
    def on_enter(self):
        self.camera = Camera(resolution=(640, 480), play=True, index=0)
        self.ids.login_camera_container.add_widget(self.camera)

    def on_leave(self):
        if hasattr(self, 'camera') and self.camera:
            self.ids.login_camera_container.remove_widget(self.camera)
            self.camera.play = False
            self.camera = None

    def capture_and_login(self):
        username = self.ids.username_input.text.strip()
        if not username:
            self._show_popup("Missing Info", "Please enter a username.")
            return
        if not self.camera:
            self._show_popup("Camera Error", "Camera not available.")
            return

        image_cv = _camera_to_cv2(self.camera)
        if image_cv is None:
            self._show_popup("Capture Error", "Could not capture image from camera.")
            return

        # ── Step 1: Pull vault from server (non-fatal fallback to local) ───────
        vault_path = os.path.join(BASE_DIR, "vault.pkl")
        try:
            CRUD.retrieveVault(username, vault_path)
            print(f"[Login] Vault fetched from server for '{username}'.")
        except Exception as e:
            print(f"[Login][CRUD] Could not fetch vault from server: {e}")
            print("[Login] Falling back to local vault.pkl if it exists.")

        # ── Step 2: Verify face against vault ─────────────────────────────────
        print(f"Verifying vault for '{username}'...")
        recovered_key = cryptomatic4000.verify_vault(image_cv, username)

        if recovered_key:
            app = App.get_running_app()
            app.vault_key = recovered_key
            app.current_username = username
            print(f"[Login] Successful. Key stored.")
            self.manager.current = 'dashboard'
        else:
            self._show_popup("Verification Failed", "Face verification failed or user not found.")

    def _show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message))
        btn = Button(text='OK', size_hint=(1, 0.3))
        content.add_widget(btn)
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        btn.bind(on_release=popup.dismiss)
        popup.open()


# ─── Sign Up Screen ───────────────────────────────────────────────────────────

class SignUpScreen(Screen):
    def on_enter(self):
        self.camera = Camera(resolution=(640, 480), play=True, index=0)
        self.ids.signup_camera_container.add_widget(self.camera)

    def on_leave(self):
        if hasattr(self, 'camera') and self.camera:
            self.ids.signup_camera_container.remove_widget(self.camera)
            self.camera.play = False
            self.camera = None

    def capture_and_signup(self):
        username = self.ids.signup_username.text.strip()
        if not username:
            self._show_popup("Missing Info", "Please enter a username.")
            return
        if not self.camera:
            self._show_popup("Camera Error", "Camera not available.")
            return

        image_cv = _camera_to_cv2(self.camera)
        if image_cv is None or image_cv.size == 0:
            self._show_popup("Capture Error", "Captured image is empty. Check your camera.")
            return

        print(f"Creating vault for '{username}'...")

        # ── Step 1: Enroll face → create local vault.pkl ──────────────────────
        success = cryptomatic4000.enroll_vault(image_cv, username)

        if not success:
            self._show_popup("Enrollment Failed", "Could not create vault. Make sure your face is visible.")
            return

        print(f"[SignUp] Vault created for '{username}'.")

        # ── Step 2: Upload vault to server ────────────────────────────────────
        vault_path = os.path.join(BASE_DIR, "vault.pkl")
        try:
            CRUD.vaultUpload(username, vault_path)
            print(f"[SignUp] Vault uploaded to server for '{username}'.")
        except Exception as e:
            print(f"[SignUp][CRUD] Vault upload failed (continuing anyway): {e}")

        # ── Step 3: Verify immediately to get the vault key ───────────────────
        recovered_key = cryptomatic4000.verify_vault(image_cv, username)
        if recovered_key:
            app = App.get_running_app()
            app.vault_key = recovered_key
            app.current_username = username
            print("[SignUp] Vault key stored after enrolment.")

        self.manager.current = 'dashboard'

    def _show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message))
        btn = Button(text='OK', size_hint=(1, 0.3))
        content.add_widget(btn)
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        btn.bind(on_release=popup.dismiss)
        popup.open()


# ─── Dashboard Screen ─────────────────────────────────────────────────────────

class DashboardScreen(Screen):

    def on_enter(self):
        """Reload enc_file/ contents every time the dashboard is shown."""
        self.ids.file_grid.clear_widgets()
        enc_dir = os.path.join(BASE_DIR, 'enc_file')
        os.makedirs(enc_dir, exist_ok=True)
        for fname in sorted(os.listdir(enc_dir)):
            fpath = os.path.join(enc_dir, fname)
            if os.path.isfile(fpath):
                self._add_file_entry(fname, fpath)

    def logout(self):
        """Clear vault key and username, return to login screen."""
        app = App.get_running_app()
        app.vault_key = None
        app.current_username = None
        self.ids.file_grid.clear_widgets()
        print("Logged out.")
        self.manager.current = 'login'

    def open_file_chooser(self):
        content = BoxLayout(orientation='vertical')
        file_chooser = FileChooserIconView()
        content.add_widget(file_chooser)

        button_layout = BoxLayout(size_hint_y=None, height='50dp', spacing=10, padding=5)
        select_button = Button(text='Select & Encrypt File')
        cancel_button = Button(text='Cancel')
        button_layout.add_widget(select_button)
        button_layout.add_widget(cancel_button)
        content.add_widget(button_layout)

        popup = Popup(title='Select File to Encrypt & Upload', content=content, size_hint=(0.9, 0.9))

        def on_selection(instance):
            if file_chooser.selection:
                filepath = file_chooser.selection[0]
                popup.dismiss()
                self.encrypt_and_upload(filepath)

        select_button.bind(on_release=on_selection)
        cancel_button.bind(on_release=popup.dismiss)
        popup.open()

    def encrypt_and_upload(self, filepath):
        """
        Full upload flow:
          1. Encrypt the file locally into enc_file/
          2. Upload the encrypted .enc file to the server
          3. Add to the dashboard grid
        """
        app = App.get_running_app()
        if not app.vault_key:
            self._show_popup("Not Logged In", "No vault key available. Please log in again.")
            return

        enc_dir = os.path.join(BASE_DIR, 'enc_file')
        os.makedirs(enc_dir, exist_ok=True)
        enc_path = os.path.join(enc_dir, os.path.basename(filepath) + '.enc')

        # ── Step 1: Encrypt locally ───────────────────────────────────────────
        try:
            encryptor = PasswordFileEncryptor(str(app.vault_key))
            encryptor.encrypt_file(filepath, enc_path)
            print(f"[Upload] Encrypted: {filepath} -> {enc_path}")
        except Exception as e:
            self._show_popup("Encryption Failed", f"Could not encrypt file:\n{e}")
            print(f"[Upload] Encryption error: {e}")
            return

        # ── Step 2: Upload encrypted file to server ───────────────────────────
        username = app.current_username or "unknown"
        try:
            CRUD.fileUpload(username, enc_path)
            print(f"[Upload] Encrypted file uploaded to server: {enc_path}")
        except Exception as e:
            print(f"[Upload][CRUD] Server upload failed (file still saved locally): {e}")

        # ── Step 3: Add to dashboard ──────────────────────────────────────────
        display_name = os.path.basename(enc_path)
        self._add_file_entry(display_name, enc_path)
        self._show_popup("Encrypted & Uploaded", f"File encrypted and uploaded:\n{display_name}")

    def _add_file_entry(self, filename, filepath):
        self.ids.file_grid.add_widget(FileEntry(filename=filename, filepath=filepath))

    def _show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message))
        btn = Button(text='OK', size_hint=(1, 0.3))
        content.add_widget(btn)
        popup = Popup(title=title, content=content, size_hint=(0.85, 0.5))
        btn.bind(on_release=popup.dismiss)
        popup.open()


# ─── App Entry Point ──────────────────────────────────────────────────────────

class BionicryptApp(App):
    vault_key = None           # Shared vault key — set on login/signup, cleared on logout
    current_username = None    # Active username — used for CRUD server calls

    def build(self):
        self.title = 'Bionicrypt'
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(SignUpScreen(name='signup'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        return sm


if __name__ == '__main__':
    BionicryptApp().run()
