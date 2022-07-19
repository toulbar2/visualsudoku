""" Visual Sudoku App """ 

__author__    = "Nathalie Rousse"
__copyright__ = "Copyright 2020, INRAE"
__license__   = "MIT"

MODE = "WS" # MODE values : "WS" (default), "LOCAL" (not delivered)

import time, os
from PIL import Image
import kivy
from kivy.logger import Logger
from kivy.app import App
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.settings import SettingsWithTabbedPanel
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider

if kivy.platform == "android" :
    DEFAULT_FONT_SIZE = 42
else : # 'linux' (...)
    DEFAULT_FONT_SIZE = 14
DEFAULT_SPACING = 2
DEFAULT_PADDING = 2

#------------------------------------------------------------------------------
# Solve
#------------------------------------------------------------------------------

if MODE=="LOCAL":
    from visualsudoku.toulbar2_visual_sudoku_puzzle import read_and_solve
else : # MODE=="WS", default
    from ws import read_and_solve

def cr_solve(outputfilepath) :
    """Analyze the solution/response from read_and_solve

    In cr_ok case, outputfilepath should be an image file.
    In some not cr_ok cases, outputfilepath may be a txt file containing some 
    error information
    """

    (cr_ok, error_txt) = (True, "") # default

    if not is_a_file(outputfilepath):
        Logger.debug("App : [cr_solve] : file %s not is_a_file" %
                     (outputfilepath))
        cr_ok = False

    else : # outputfilepath file exists

        try : # txt file ?
            txt = ""
            with open(outputfilepath, 'rt') as f :
                lines = f.readlines()
                for line in lines:
                    txt += line
            cr_ok = False # txt file (containing information about error)
            Logger.debug("App : [cr_solve] : %s is txt file, containing : %s" %
                         (outputfilepath, txt))
        except : # not txt file
            pass

    if not cr_ok :
        error_txt = "Solving FAILURE"
    return (cr_ok, error_txt)

#------------------------------------------------------------------------------
# Folders
#------------------------------------------------------------------------------

if kivy.platform == "android" :
    from android.permissions import Permission
    from android.permissions import request_permissions, check_permission
    from android.storage import app_storage_path
    from android.storage import primary_external_storage_path

APP_PATH = os.path.dirname(os.path.abspath(__file__)) # for 'linux' case
HOME_PATH = os.path.dirname(APP_PATH) # for 'linux' case

def get_config_file_path():
    """Returns .ini file path

    Supposing only one '.ini' file into expected folder
    """

    if kivy.platform == "android" :
        config_path = app_storage_path()
    else : # 'linux' (...)
        config_path = APP_PATH

    if os.path.exists(config_path):
        lst = os.listdir(config_path)
        for name in lst :
            if name.endswith('.ini') :
                filepath = os.path.join(config_path, name)
                if os.path.isfile(filepath) :
                    return filepath
    return ""

def get_img_path():
    if kivy.platform == "android" :
        root_path = primary_external_storage_path()
        img_path = os.path.join(root_path, "VisualSudoku")
        if not os.path.exists(img_path) :
            os.mkdir(img_path)
    else : # 'linux' (...)
        img_path = os.path.join(HOME_PATH, "img")
    return img_path

def is_a_file(filepath):
    if os.path.exists(filepath):
        if os.path.isfile(filepath):
            return True
    return False

def check_permissions(perms):
    for perm in perms:
        if check_permission(perm) != True:
            Logger.debug("App : [check_permissions] : %s permission NOT OK" %
                         (perm))
            return False
    Logger.info("App : [check_permissions] : ALL required permissions OK")
    return True

#------------------------------------------------------------------------------
# Config
#------------------------------------------------------------------------------

INI = {
        'keep_default': 0,
        'border_default': 0,
        'time_default': 5,
        'model':"visualsudoku/mixed_classifier.h5",
        'debug' : 0
      }

SETTINGS = {}

json_data_app = \
"""[
      {"type": "bool",
       "title": "expert",
       "desc": "Expert Mode to access some more settings",
       "section": "app", "key": "expert"},

      {"type": "path",
       "title": "imagepath",
       "desc": "Image path where images are saved",
       "section": "app", "key": "imagepath"},

      {"type": "bool",
       "title": "savingoutputfile",
       "desc": "Saving solution file",
       "section": "app", "key": "savingoutputfile"},

      {"type": "bool",
       "title": "savinginputfile",
       "desc": "Saving captured partial grid file (from camera)",
       "section": "app", "key": "savinginputfile"}
]"""

#------------------------------------------------------------------------------
# Popup message
#------------------------------------------------------------------------------

class CustomPopup(Popup):
    contentBox = ObjectProperty()

class ScrollPopup(BoxLayout):
    popup = None

    def build(self, title, text):
        self.popup = CustomPopup(title=title, size_hint=(0.94, 0.6))
        self.popup.contentBox.content.text = text

    def open(self):
        self.popup.open()

class ScrollPopupMsg(ScrollPopup):

    def build(self, title, text, rgba_color):

        super().build(title, text)

        content_box = self.popup.ids['content_box']
        close_button = Button(text="Close",
                              size_hint_y=None, height="40dp")
        close_button.background_normal = ''
        close_button.background_color = rgba_color
        content_box.add_widget(close_button)
        close_button.bind(on_press=self.popup.dismiss)

class ScrollPopupMsgValid(ScrollPopup):

    def build(self, title, text, rgba_color, valid_action):

        super().build(title, text)

        content_box = self.popup.ids['content_box']

        validate_button = Button(text="Confirm",
                                 size_hint_y=None, height="40dp")
        validate_button.background_normal = ''
        validate_button.background_color = rgba_color
        content_box.add_widget(validate_button)
        validate_button.bind(on_press=valid_action)

        close_button = Button(text="Cancel",
                              size_hint_y=None, height="40dp")
        close_button.background_normal = ''
        close_button.background_color = rgba_color
        content_box.add_widget(close_button)
        close_button.bind(on_press=self.popup.dismiss)

#------------------------------------------------------------------------------
# Errors
#------------------------------------------------------------------------------

def error_msg(text):
    s = ScrollPopupMsg()
    s.build(title="ERROR", text=text,
            rgba_color=(0/255.0, 47/255.0, 167/255.0, 1.0))
    s.open()

def failed_msg(exception) :
    errortype = type(exception).__name__
    errordetails = exception.args
    error_text = "Error " + errortype + ": "
    for m in errordetails :
        error_text = error_text + str(m) + " -- "
    Logger.debug("App : [failed_msg] : [FAILED ] ERROR %s : %s" %
                 (errortype, str(exception)))
    error_msg(text=error_text)

#------------------------------------------------------------------------------
# Screens
#------------------------------------------------------------------------------

class MainScreen(Screen):
    pass

class SetScreen(Screen):
    pass

class SelectImageFileScreen(Screen):
    """Selection of the image file (existing on device) to be solved"""

    def select_file(self, *args):

        if len(self.ids.fc.selection) > 0 :
            sm = self.manager
            if SETTINGS["expert"] == 1 :
                next_name = 'displayimagexp'
            else :
                next_name = 'displayimage'
            screen = sm.screens[sm.number[next_name]]
            screen.ids.imagepath.text = self.ids.fc.selection[0]
            screen.ids.imageView.reload()
            screen.angle = -90 if (kivy.platform=="android") else 0
            Logger.info("App : [select_file] : selected file : %s" %
                        (screen.ids.imagepath.text))
            sm.current = next_name
        #else :
            #pass # nothing

class DisplayImageScreen(Screen):
    """Display the chosen image file (existing or captured) to be solved

    Button : solve
    """

    angle = NumericProperty(0.0)

    def image_text(self, filepath):
        name = ""
        if os.path.isfile(filepath) :
            name = os.path.basename(filepath)
        text = "[i]"+ "Grid file: "+name +"[/i]"
        return text

    def getname_outputfilepath(self, inputfilepath=None):
        """name as .jpg """

        dirname = SETTINGS["imagepath"]
        out_name = "solution.jpg" # default"
        if inputfilepath is not None :
            timestr = time.strftime("%m%d_%H%M%S")
            in_name = os.path.basename(inputfilepath)
            s = os.path.splitext(in_name)
            extension = s[1]
            if extension != '.jpg' :
                root = s[0]
                in_name = root + '.jpg'
            out_name = "SOL_{}_{}".format(timestr, in_name)
        outputfilepath = os.path.join(dirname, out_name)
        return outputfilepath

    def solve(self, inputfilepath):

        try:
            sm = self.manager

            Logger.info("App : [solve] : SETTINGS : %s" % (SETTINGS))

            if SETTINGS["expert"] == 1 :
                Logger.info("App : [solve] : 'Expert' mode => menu values for keep border time")
                keep_value = int(self.ids.keep.value)
                border_value = int(self.ids.border.value)
                time_value = int(self.ids.time.value)
            else :
                Logger.info("App : [solve] : NOT 'Expert' mode => default values for keep border time")
                keep_value = INI['keep_default']
                border_value = INI['border_default']
                time_value = INI['time_default']

            Logger.debug("App : [solve] : keep_value: %d, border_value: %d, time_value: %d" % (keep_value, border_value, time_value))

            Logger.info("App : [solve] : SETTINGS['savingoutputfile']= %d" %
                        (SETTINGS["savingoutputfile"]))
            if SETTINGS["savingoutputfile"]==1 :
                outputfilepath = self.getname_outputfilepath(inputfilepath)
            else :
                outputfilepath = self.getname_outputfilepath()

            if MODE=="LOCAL" :
                Logger.info("App : [solve] : 'LOCAL' mode")
                args = {"model" : INI['model'],
                        "image" : inputfilepath,
                        "output" : outputfilepath,
                        "debug" : INI['debug'],
                        "keep" : keep_value, "border" : border_value,
                        "time" : time_value}
                read_and_solve(args)

            else : # MODE=="WS", default
                Logger.info("App : [solve] : 'WS' mode")
                read_and_solve(image=inputfilepath, output=outputfilepath,
                               keep=keep_value, border=border_value,
                               time=time_value)
            Logger.info("App : [solve] : calls read_and_solve")

            Logger.info("App : [solve] : outputfilepath : %s" %
                        (outputfilepath))

            (cr_ok, error_txt) = cr_solve(outputfilepath)

            Logger.debug("App : [solve] : from cr_solve, cr_ok= %s, error_txt= %s " %
                        (cr_ok, error_txt))
            if cr_ok :
                screen = sm.screens[sm.number['displaysolution']]
                screen.ids.solutionpath.text = outputfilepath
                screen.ids.imagepath.text = inputfilepath
                self.manager.current = 'displaysolution'
            else :
                error_msg(text=error_txt)
                self.manager.current = 'main'

        except Exception as e :
            failed_msg(e)

class DisplayImageScreenXp(DisplayImageScreen):
    """Case Expert mode (+ parameters : keep, border...) """
    pass

class DisplaySolutionScreen(Screen):
    """Display the solution image file """

    def image_text(self, filepath):
        name = ""
        if os.path.isfile(filepath) :
            name = os.path.basename(filepath)
        text = "[i]"+ "Grid file: "+name +"[/i]"
        return text

    def solution_text(self, filepath):
        name = ""
        if os.path.isfile(filepath) :
            name = os.path.basename(filepath)
        text = "[i]"+ "Solution file: "+name +"[/i]"
        return text

class CaptureImageScreen(Screen):
    """Capture and save the image file to be solved

    Buttons : play (camera on/off), capture

    Note : not finding a camera (for example because gstreamer not installed)
    will throw an exception during the kv language processing
    """

    def is_android(self, *args):
        return (kivy.platform=="android")

    def camera_onoff(self, *args):
        sm = self.manager
        camera = self.ids['camera']
        cameraonoff = self.ids['cameraonoff']
        camera.play = not camera.play
        if camera.play :
            cameraonoff.text = 'Camera ON --> OFF'
        else :
            cameraonoff.text = 'Camera OFF --> ON'
        Logger.info("App : [camera_onoff] : camera.play : %s" % (camera.play))
        Logger.info("App : [camera_onoff] : cameraonoff.text : %s" %
                    (cameraonoff.text))

    def getname_inputfilepath(self, default=False):
        dirpath = SETTINGS["imagepath"]
        if default :
            in_name = "GRD.png" # default"
        else :
            timestr = time.strftime("%m%d_%H%M%S")
            in_name = "GRD_{}.png".format(timestr)
        inputfilepath = os.path.join(dirpath, in_name)
        return inputfilepath

    def capture(self):
        try:
            sm = self.manager
            camera = self.ids['camera']
            if SETTINGS["savinginputfile"]==1 :
                inputfilepath = self.getname_inputfilepath(default=False)
            else :
                inputfilepath = self.getname_inputfilepath(default=True)

            if self.is_android() :
                tmp_inputfilepath = os.path.join(SETTINGS["imagepath"],
                                                 "GRD_tmp.png")
                camera.texture.save(filename=tmp_inputfilepath)
                # image from camera has been rotated for screen (see .kv)
                image = Image.open(tmp_inputfilepath)
                rotated_image = image.rotate(-90, expand=True)
                rotated_image.save(inputfilepath)
            else :
                camera.export_to_png(inputfilepath)

            Logger.info("App : [capture] Image captured, saved as file %s" %
                        (inputfilepath))

            if SETTINGS["expert"] == 1 :
                Logger.info("App : [capture] 'Expert' mode : display image XP")
                n = 'displayimagexp'
            else :
                Logger.info("App : [capture] NOT 'Expert' mode : display image")
                n = 'displayimage'
            sm.current = n
            screen = sm.screens[sm.number[n]]
            screen.ids.imagepath.text = inputfilepath
            screen.ids.imageView.reload()
            screen.angle = 0

        except Exception as e :
            failed_msg(e)

#------------------------------------------------------------------------------

class VisualSudokuScreenManager(ScreenManager):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.number = dict()

#------------------------------------------------------------------------------

class VisualSudokuApp(App):

    #--------------------------------------------------------------------------
    # config and settings
    #--------------------------------------------------------------------------

    use_kivy_settings = True # False

    @classmethod
    def get_default_settings(cls) :
        """ Return default setting dictionary """

        return { 'expert': 0,
                 'imagepath': get_img_path(),
                 'savingoutputfile': 1,
                 'savinginputfile': 0 }

    @classmethod
    def set_default_settings(cls, settings) :
        """ setting default values --> into settings"""

        S = cls.get_default_settings()
        for k in S.keys() :
            settings[k] = S[k]

    @classmethod
    def set_settings(cls, settings, config) :
        """ setting values from config --> into settings"""

        settings['expert'] = config.getint('app', 'expert')
        settings['imagepath'] = config.get('app', 'imagepath')
        settings['savingoutputfile'] = config.getint('app', 'savingoutputfile')
        settings['savinginputfile'] = config.getint('app', 'savinginputfile')

    def build_config(self, config): # before build()
        """ setting values into config

        Values from visualsudoku.ini if existing file, and else
        default values from here (and create file)
        """

        S = self.get_default_settings()
        config.setdefaults('app', S)

        log_name = 'loggin.txt'
        log_dir = os.path.abspath(get_img_path())
        config.setdefaults('kivy', {'log_name': log_name, 'log_dir': log_dir,
                                    'log_maxfiles':20 })

    def build_settings(self, settings): # called by open_settings()
        """Build Settings screen (+ Kivy by default) """

        settings.add_json_panel('App', self.config, data=json_data_app)

    def on_config_change(self, config, section, key, value):
        """ Update SETTINGS from config """

        super(VisualSudokuApp, self).on_config_change(config,
                                                     section, key, value)
        if section == 'app' :
            self.set_settings(SETTINGS, config)
            Logger.info("App : [on_config_change] end : SETTINGS= %s" %
                        (SETTINGS))

    def reset_settings_msg(self, *args):
        text = "App is going to be closed for RESET to be taken into account\n"
        text += "Do you really want to RESET ?"
        s = ScrollPopupMsgValid()
        s.build(title="RESET", text=text,
                rgba_color=(0/255.0, 47/255.0, 167/255.0, 1.0),
                valid_action=self.reset_settings)
        s.open()

    def reset_settings(self, *args):
        inifile_path = get_config_file_path()
        try :
            if is_a_file(inifile_path):
                Logger.debug("App : [reset_settings] : Remove file %s..." %
                            (inifile_path))
                os.remove(inifile_path)
                Logger.info("App : [reset_settings] : %s removed" %
                            (inifile_path))
            self.do_quit()
        except Exception as e :
            failed_msg(e)

    def close_settings(self, settings=None):
        super(VisualSudokuApp, self).close_settings(settings)
        self.root.current = 'main'

    #--------------------------------------------------------------------------
    # menus
    #--------------------------------------------------------------------------

    def classical_menu(self, layout,
                       b_settings=False, t_settings='SETTINGS',
                       b_file=False, t_file='FILE',
                       b_camera=False, t_camera='CAMERA',
                       b_home=True, t_home='HOME',
                       b_quit=True, t_quit='QUIT',
                       font_size=DEFAULT_FONT_SIZE):
        background_color_general=(128/255.0, 128/255.0, 128/255.0, 1.0)
        background_color_choices=(169/255.0, 169/255.0, 169/255.0, 1.0)
        if b_home :
            text = t_home
            home_button = Button(text=text, font_size=font_size,
                                 background_normal='',
                                 background_color=background_color_general)
            home_button.id = 'b_HOME'
            home_button.bind(on_press=self.manage_menu)
            layout.add_widget(home_button)       
        if b_settings :
            text = t_settings
            settings_button = Button(text=text, font_size=font_size,
                                     background_normal='',
                                     background_color=background_color_choices)
            settings_button.id = 'b_SETTINGS'
            settings_button.bind(on_press=self.manage_menu)
            layout.add_widget(settings_button)       
        if b_file :
            text = t_file
            file_button = Button(text=text, font_size=font_size,
                                 background_normal='',
                                 background_color=background_color_choices)
            file_button.id = 'b_FILE'
            file_button.bind(on_press=self.manage_menu)
            layout.add_widget(file_button)       
        if b_camera :
            text = t_camera
            camera_button = Button(text=text, font_size=font_size,
                                   background_normal='',
                                   background_color=background_color_choices)
            camera_button.id = 'b_CAMERA'
            camera_button.bind(on_press=self.manage_menu)
            layout.add_widget(camera_button)       

        if b_quit :
            text = t_quit
            quit_button = Button(text=text, font_size=font_size,
                                 background_normal='',
                                 background_color=background_color_general)
            quit_button.id = 'b_QUIT'
            quit_button.bind(on_press=self.do_quit)
            layout.add_widget(quit_button)       

    def manage_menu(self, args):
        """Change screen according to button id"""

        button_id = args.id
        if button_id == 'b_SETTINGS' :
            self.manager.current = 'set'
        elif button_id == 'b_FILE' : 
            self.manager.current = 'selectimagefile'
            sm = self.manager
            screen = sm.screens[sm.number['selectimagefile']]
            screen.ids.fc._update_files()
        elif button_id == 'b_CAMERA' :
            self.manager.current = 'captureimage'
        else : # b_home, default
            self.manager.current = 'main'

    #--------------------------------------------------------------------------
    # parameters
    #--------------------------------------------------------------------------

    def parameters_part(self, layout, ids, font_size=DEFAULT_FONT_SIZE,
                        background_color=(1.0, 0.0, 0.0, 1.0)):
        """Screen part to choose parameters values (Expert mode case)"""

        layout_params = BoxLayout(orientation='vertical')

        layout_keep = BoxLayout(orientation='horizontal')
        default_value_keep = INI['keep_default']
        text_keep = 'keep = {}'.format(int(default_value_keep))
        label_keep = Label(text=text_keep)
        slider_keep = Slider(min=0, max=100, value=default_value_keep)
        ids['keep'] = slider_keep
        def keep_slider_value_change(instance,value):
            label_keep.text = 'keep = {}'.format(int(value))
        slider_keep.bind(value=keep_slider_value_change)
        layout_keep.add_widget(label_keep)
        layout_keep.add_widget(slider_keep)
        layout_params.add_widget(layout_keep)

        layout_border = BoxLayout(orientation='horizontal')
        default_value_border = INI['border_default']
        text_border = 'border = {}'.format(int(default_value_border))
        label_border = Label(text=text_border)
        slider_border = Slider(min=0, max=100, value=default_value_border)
        ids['border'] = slider_border
        def border_slider_value_change(instance,value):
            label_border.text = 'border = {}'.format(int(value))
        slider_border.bind(value=border_slider_value_change)
        layout_border.add_widget(label_border)
        layout_border.add_widget(slider_border)
        layout_params.add_widget(layout_border)

        layout_time = BoxLayout(orientation='horizontal')
        default_value_time = INI['time_default']
        text_time = 'time = {}'.format(int(default_value_time))
        label_time = Label(text=text_time)
        slider_time = Slider(min=1, max=60, value=default_value_time)
        ids['time'] = slider_time
        def time_slider_value_change(instance,value):
            label_time.text = 'time = {}'.format(int(value))
        slider_time.bind(value=time_slider_value_change)
        layout_time.add_widget(label_time)
        layout_time.add_widget(slider_time)
        layout_params.add_widget(layout_time)
        layout.add_widget(layout_params)

        layout_btns = BoxLayout(orientation='vertical', size_hint=(0.2, 1),
                                         spacing=DEFAULT_SPACING)
        params_color = (38/255.0, 196/255.0, 236/255.0, 1.0)
        btn_help = Button(text='Help', background_normal='',
                          background_color=params_color)
        def help_msg(*args):
            text = "- keep : Percentage of the center of cell images to be kept\n"
            text += "- border : Enlarge the cell image region by some extra percentage\n"
            text += "- time : CPU time limit in seconds for solving sudoku\n"
            text += "- Note : try keep=40 and border=15 if the hand-digits cross cell boundaries\n"
            s = ScrollPopupMsg()
            s.build(title="Parameters", text=text, rgba_color=params_color)
            s.open()

        btn_help.bind(on_press=help_msg)
        layout_btns.add_widget(btn_help)

        btn_reset = Button(text='Reset', background_normal='',
                           background_color=params_color)
        def reset_values(*args):
            slider_keep.value = default_value_keep
            slider_border.value = default_value_border
            slider_time.value = default_value_time
        btn_reset.bind(on_press=reset_values)
        layout_btns.add_widget(btn_reset)

        layout.add_widget(layout_btns)

    def callback(instance, value):
        Logger.debug("App : [callback] : My button <%s> state is <%s>" %
                     (instance, value))

    def build(self):

        try:
            if kivy.platform == "android" :
                # permissions
                perms = [Permission.CAMERA, Permission.INTERNET,
                         Permission.WRITE_EXTERNAL_STORAGE,
                         Permission.READ_EXTERNAL_STORAGE]
                if not check_permissions(perms) :
                    request_permissions(perms)

            Logger.info("App : [build] : kivy.platform : %s" % (kivy.platform))
            Logger.info("App : [build] : HOME_PATH (for linux case) : %s" %
                        (HOME_PATH))
            Logger.info("App : [build] : APP_PATH (for linux case) : %s" %
                        (APP_PATH))
            Logger.info("App : [build] : get_config_file_path() : %s" %
                        (get_config_file_path()))
            Logger.info("App : [build] : get_img_path() : %s" %
                        (get_img_path()))
            #------------
            #print("os.environ : ")
            #e = dict(os.environ)
            #for k in e.keys() :
            #    print(k, " : ", e[k])
            #------------

            self.title = 'Visual Sudoku'

            self.settings_cls = SettingsWithTabbedPanel

            sm = VisualSudokuScreenManager()
            self.manager = sm

            # main screen -----------------------------------------------------

            main_screen = MainScreen(name='main')
            ids = main_screen.ids

            layout_menu_main = BoxLayout(orientation='vertical',
                                         spacing=DEFAULT_SPACING,
                                         padding=DEFAULT_PADDING,
                                         size_hint=(1, 0.1))
            t_settings = 'SETTINGS'
            t_file = 'FILE (select existing file of partial grid to be solved)'
            t_camera = 'CAMERA (capture image of partial grid to be solved)'
            t_quit = 'QUIT'
            self.classical_menu(layout=layout_menu_main,
                                b_home=False,
                                b_quit=True, t_quit=t_quit,
                                b_settings=True, t_settings=t_settings,
                                b_file=True, t_file=t_file,
                                b_camera=True, t_camera=t_camera)
            ids.main.add_widget(layout_menu_main)

            sm.add_widget(main_screen)

            # set screen ------------------------------------------------------

            self.set_default_settings(SETTINGS)
            self.set_settings(SETTINGS, self.config)
            Logger.info("App : [build] : SETTINGS= %s" % (SETTINGS))

            set_screen = SetScreen(name='set')
            ids = set_screen.ids
            s = self.create_settings()
            ids.settings_content.add_widget(s)
            ids.reset_settings_msg.bind(on_press=self.reset_settings_msg)
            sm.add_widget(set_screen)

            # captureimage screen ---------------------------------------------

            captureimage_screen = CaptureImageScreen(name='captureimage')
            ids = captureimage_screen.ids
            layout_menu_captureimage = BoxLayout(orientation='horizontal',
                                                 spacing=DEFAULT_SPACING,
                                                 padding=DEFAULT_PADDING,
                                                 size_hint=(1, 0.1))
            self.classical_menu(layout=layout_menu_captureimage,
                                b_home=True, b_quit=True,
                                b_settings=True, b_file=True, b_camera=False)
            ids.captureimage.add_widget(layout_menu_captureimage)
            sm.add_widget(captureimage_screen)

            # selectimagefile screen ------------------------------------------

            selectimagefile_screen = SelectImageFileScreen(
                                                       name='selectimagefile')
            ids = selectimagefile_screen.ids
            ids.fc.bind(selection=selectimagefile_screen.select_file)
            ids.fc.path = SETTINGS["imagepath"]
            layout_menu_selectimagefile = BoxLayout(orientation='horizontal',
                                                    spacing=DEFAULT_SPACING,
                                                    padding=DEFAULT_PADDING,
                                                    size_hint=(1, 0.1))
            self.classical_menu(layout=layout_menu_selectimagefile,
                                b_home=True, b_quit=True,
                                b_settings=True, b_file=False, b_camera=True)
            ids.selectimagefile.add_widget(layout_menu_selectimagefile)
            sm.add_widget(selectimagefile_screen)

            # displayimage screen ---------------------------------------------

            displayimage_screen = DisplayImageScreen(name='displayimage')
            ids = displayimage_screen.ids
            layout_menu_displayimage = BoxLayout(orientation='horizontal',
                                                 spacing=DEFAULT_SPACING,
                                                 padding=DEFAULT_PADDING,
                                                 size_hint=(1, 0.1))
            self.classical_menu(layout=layout_menu_displayimage,
                                b_home=True, b_quit=True,
                                b_settings=True, b_file=True, b_camera=True)
            ids.displayimage.add_widget(layout_menu_displayimage)
            sm.add_widget(displayimage_screen)

            # displayimagexp screen -------------------------------------------

            displayimagexp_screen = DisplayImageScreenXp(name='displayimagexp')
            ids = displayimagexp_screen.ids
            layout_parameters = BoxLayout(orientation='horizontal',
                                          size_hint=(1, 0.3))
            self.parameters_part(layout=layout_parameters, ids=ids)
            ids.displayimage.add_widget(layout_parameters)
            layout_menu_displayimagexp = BoxLayout(orientation='horizontal',
                                                   spacing=DEFAULT_SPACING,
                                                   padding=DEFAULT_PADDING,
                                                   size_hint=(1, 0.1))
            self.classical_menu(layout=layout_menu_displayimagexp,
                                b_home=True, b_quit=True,
                                b_settings=True, b_file=True, b_camera=True)
            ids.displayimage.add_widget(layout_menu_displayimagexp)
            sm.add_widget(displayimagexp_screen)

            # displaysolution screen ------------------------------------------

            displaysolution_screen = DisplaySolutionScreen(
                                                        name='displaysolution')
            ids = displaysolution_screen.ids
            layout_menu_displaysolution = BoxLayout(orientation='horizontal',
                                                    spacing=DEFAULT_SPACING,
                                                    padding=DEFAULT_PADDING,
                                                    size_hint=(1, 0.1))
            self.classical_menu(layout=layout_menu_displaysolution,
                                b_home=True, b_quit=True,
                                b_settings=True, b_file=True, b_camera=True)
            ids.displaysolution.add_widget(layout_menu_displaysolution)
            sm.add_widget(displaysolution_screen)

            for n,screen in enumerate(sm.screens) :
                sm.number[screen.name] = n

            return sm

        except Exception as e :
            failed_msg(e)

    def do_quit(self, *args):
        VisualSudokuApp.get_running_app().stop()
        os._exit(0)

if __name__ == '__main__':
    Config.set('graphics', 'fullscreen', '0')
    Config.set('graphics', 'width', '350')
    Config.set('graphics', 'height', '500')
    Config.write()
    VisualSudokuApp().run()

