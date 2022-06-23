"""
Poricom Multithreaded Workers

Copyright (C) `2021-2022` `<Alarcon Ace Belen>`

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from PyQt5.QtCore import (QRunnable, QObject, pyqtSignal, pyqtSlot)
from numpy import isin
from utils.config import config
import deepl
import googletrans
import yandex_translate

deepl_conf = config["TRANSLATE"]["DEEPL"]
google_conf = config["TRANSLATE"]["GOOGLE"]
yandex_conf = config["TRANSLATE"]["YANDEX"]
deepl_trans, google_trans, yandex_trans = None, None, None

if deepl_conf["enabled"]:
    deepl_trans = deepl.Translator(deepl_conf["auth_key"])
if google_conf["enabled"]:
    google_trans = googletrans.Translator()
if yandex_conf["enabled"]:
    yandex_trans = yandex_translate.YandexTranslate(yandex_conf["auth_key"])


class BaseWorker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(BaseWorker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignal()

    @pyqtSlot()
    def run(self):
        tex_original = self.fn(*self.args, **self.kwargs)

        if (isinstance(tex_original, str)):
            detected = tex_original.__len__()!=0
            output = ""
            output += "Original: "+tex_original

            if detected and deepl_conf["enabled"]:
                try:
                    tex_translated = deepl_trans.translate_text(
                        tex_original,
                        target_lang=deepl_conf["lang_tar"],
                        source_lang=deepl_conf["lang_ori"]
                    ).text
                    output += "\nDeepL: "+tex_translated
                except:
                    output +="\DeepL: Failed to translate"

            if detected and google_conf["enabled"]:
                try:
                    tex_translated = google_trans.translate(
                        tex_original,
                        dest=google_conf["lang_tar"],
                        src=google_conf["lang_ori"]
                    )
                    if not isinstance(tex_translated, str):
                        tex_translated = tex_translated.text
                    output += "\nGoogle: "+tex_translated
                except:
                    output +="\Google: Failed to translate"
            
            if detected and yandex_conf["enabled"]:
                try:
                    tex_translated = yandex_trans.translate(
                        tex_original,
                        yandex_conf["lang_ori"]+"-"+google_conf["lang_tar"]
                    )
                    output += "\nYandex: "+tex_translated.text
                except:
                    output += "\nYandex: Failed to translate"

            
            if not detected:
                output+="Failed to grab text"

            print(output)
            self.signals.result.emit(output)
        else:
            self.signals.result.emit(tex_original)

        self.signals.finished.emit()


class WorkerSignal(QObject):
    finished = pyqtSignal()
    result = pyqtSignal(object)
