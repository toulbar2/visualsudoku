# visualsudoku

Visual Sudoku Application with kivy

# Desc

main.py App developed with kivy, calling toulbar2_visual_sudoku_puzzle.py 
from ws web services, in order to solve sudoku grid image.

Note : current version with "WS" mode, "LOCAL" mode not delivered.

# App

  - code : 'app' folder

  - main.py solves sudoku by calling ws web services (see ws.py)

  - visualsudoku.kv

# Python virtual environment :

  - create _kivy_venv

        pip3 install --upgrade pip wheel setuptools virtualenv
        python3 -m venv _kivy_venv
        source _kivy_venv/bin/activate

  - for App and kivy :

        pip3 install -r fab/requirements_ws.txt

  - for buildozer :

        pip3 install -r fab/requirements_buildozer.txt

# Linux - Run App :

  - requirements_ws.txt required

  - commands :

        source _kivy_venv/bin/activate
        cd app
        python3 main.py

# Android - Init :

  - requirements_ws.txt and requirements_buildozer.txt required

  - create :

        source _kivy_venv/bin/activate
        cd app
        buildozer init

  => buildozer.spec  ... modify ...

# Android - Build install and run App (debug) :

  - requirements_ws.txt and requirements_buildozer.txt required

  - prepare smartphone :

    - Activate "options de developpement" (cf "numero de version")
    - And into "paramètres developpeur" : USB debugging, Stay awake

  - plug in your android device and run :
    !!! Smartphone connected with PC/Linux (debug screen)

  - build install and run apk :

        buildozer android debug deploy run
        => bin/*-debug.apk

        buildozer -v android debug deploy run logcat > my_log.txt
        buildozer -v android debug deploy run logcat | grep App

  => .buildozer

# Android - APK delivery :

- Generate a key by Android Studio

  - Install Android Studio
    (https://developer.android.com/studio)

  - Open Android Studio

        cd ~/android-studio-2021.2.1.15-linux/android-studio/bin
        ./studio.sh

  - Generate key

    See https://www.youtube.com/watch?v=vZ0Ar9JCua8

  => Path fab/key
     File  visualsudoku_key.jks
     Alias visualsudoku_key
     (and passwords)

- Create an account as developer for Google Play Console

See https://accounts.google.com/signin/v2/identifier?service=androiddeveloper&passive=1209600&continue=https%3A%2F%2Fplay.google.com%2Fconsole%2Fsignup&followup=https%3A%2F%2Fplay.google.com%2Fconsole%2Fsignup&flowName=GlifWebSignIn&flowEntry=ServiceLogin

- Publish the application (on Google Play)

See https://wiki.labomedia.org/index.php/Publier_une_application_sur_Google_Play.html

  - Create a key (see above)

  - Export some variables

        export P4A_RELEASE_KEYSTORE=<path-to>key/visualsudoku_key.jks
        export P4A_RELEASE_KEYSTORE_PASSWD=<passwd-value>
        export P4A_RELEASE_KEYALIAS_PASSWD=<passwd-value>
        export P4A_RELEASE_KEYALIAS=visualsudoku_key

  - Make release aab

        cd app
        buildozer -v android release

  => bin/visualsudoku-0.1-arm64-v8a_armeabi-v7a-release.aab

  - Optimize (zipalign NOT DONE)

  - Publish aab on Google Play : TODO

## aab to apk :

Android Developers > Android Studio > User guide > bundletool
https://developer.android.com/studio/command-line/bundletool

  - Download bundletool https://github.com/google/bundletool/releases

  => fab/bundletool/bundletool-all-1.11.0.jar

  - Generate a set of APKs from your app bundle (by bundletool command)

        cp bin/visualsudoku-0.1-arm64-v8a_armeabi-v7a-release.aab ../fab/bundletool/.
        cd ../fab/bundletool

        java -jar bundletool-all-1.11.0.jar build-apks --bundle=visualsudoku-0.1-arm64-v8a_armeabi-v7a-release.aab --output=visualsudoku-release.apks --ks=<path-to>key/visualsudoku_key.jks --ks-pass=pass:<passd-value> --ks-key-alias=visualsudoku_key --key-pass=pass:<passd-value> --mode=universal

  => visualsudoku-release.apks

        unzip -p visualsudoku-release.apks universal.apk > visualsudoku-release.apk

  => APK visualsudoku-release.apk

     (or mv visualsudoku.apks visualsudoku.zip unzip ... => universal.apk ...)

        cp fab/bundletool/visualsudoku-0.1-arm64-v8a_armeabi-v7a-release.aab release/.
        cp fab/bundletool/visualsudoku-release.apk release/.

- See also https://fr.techbriefly.com/comment-convertir-un-app-bundle-au-format-aab-en-fichier-apk-tech-42080/

