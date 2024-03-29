'''
Copyright (C) 2010 Zachary Varberg
@author: Zachary Varberg

This file is part of Steganogra-py.

Steganogra-py is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Steganogra-py is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Steganogra-py.  If not, see <http://www.gnu.org/licenses/>.

icon provided by www.fasticon.com
'''


import sys
import time

from PyQt4.QtGui import *
from PyQt4.QtCore import *
##Recompile UI from QT Designer
#from PyQt4 import uic
#tmp = open('MainWindow.py', 'w')
#uic.compileUi('MainWindow.ui', tmp)
#tmp.close()
#tmp = open('encode_dialog_ui.py', 'w')
#uic.compileUi('encode_dialog.ui', tmp)
#tmp.close()

from GUI import MainWindow
#from GUI import encode_dialog
from Logic import stegthreads
from Logic import steganography
from GUI import progress_dialog
from Logic import detect_steg

class MyGUI(MainWindow.Ui_MainWindow):
    """
    This is the main GUI class that will run the Steganogra-py app.
    """
    
    def __init__(self):
        self.mw = QMainWindow()
        self.setupUi(self.mw)
        self.mw.show()
        
        self.encode_red_bits = 1
        self.encode_blue_bits = 1
        self.encode_green_bits = 1
        
        self.decode_red_bits = 1
        self.decode_blue_bits = 1
        self.decode_green_bits = 1
        
        self.encode_image_filename = ""
        self.encode_new_image_filename = ""
        self.encode_txt_filename = ""
        
        self.decode_image_filename = ""
        self.decode_txt_filename = ""
        
        self.encode_thread = stegthreads.EncodeWorker()
        self.decode_thread = stegthreads.DecodeWorker()
        
        self.prog_dialog = progress_dialog.ProgressDialog(self.mw)
        self.progress_thread = stegthreads.ProgressWorker(self.prog_dialog)
         
        self.auto_detect = False    
        self.auto_encode = False    
        
        self.auto_bits_set = False

        # Encode events 
        QObject.connect(self.encode_file_browse_button, SIGNAL("clicked()"),
                        self.on_encode_file_browse_button_press)
        QObject.connect(self.encode_image_browse_button, SIGNAL("clicked()"),
                        self.on_encode_image_browse_button_press)
        QObject.connect(self.encode_new_image_browse_button, SIGNAL("clicked()"),
                        self.on_encode_new_image_browse_button_press)
        QObject.connect(self.encode_new_image_text, SIGNAL("textEdited(QString)"),
                        self.on_encode_new_image_text_change)
        QObject.connect(self.encode_file_text, SIGNAL("textEdited(QString)"),
                        self.on_encode_file_text_change)
        QObject.connect(self.encode_image_text, SIGNAL("textEdited(QString)"),
                        self.on_encode_image_text_change)
        QObject.connect(self.encode_red_bits_combo, SIGNAL("currentIndexChanged(int)"),
                        self.on_encode_red_bits_change)
        QObject.connect(self.encode_green_bits_combo, SIGNAL("currentIndexChanged(int)"),
                        self.on_encode_green_bits_change)
        QObject.connect(self.encode_blue_bits_combo, SIGNAL("currentIndexChanged(int)"),
                        self.on_encode_blue_bits_change)
#        QObject.connect(self.encode_button, SIGNAL("clicked()"),
#                        self.on_encode_button_press)
        self.encode_button.clicked.connect(self.on_encode_button_press)
        QObject.connect(self.auto_encode_checkbox, SIGNAL("clicked()"),
                        self.auto_encode_toggled)

        QObject.connect(self.encode_thread, SIGNAL("terminated()"), self.unknown_error)
        QObject.connect(self.encode_thread, SIGNAL("complete()"), self.encode_success)
        QObject.connect(self.encode_thread, SIGNAL("error()"), self.encode_error)
        QObject.connect(self.progress_thread, SIGNAL("complete()"), self.progress_complete)
        

        # Decode events
        QObject.connect(self.decode_file_browse_button, SIGNAL("clicked()"),
                        self.on_decode_file_browse_button_press)
        QObject.connect(self.decode_image_browse_button, SIGNAL("clicked()"),
                        self.on_decode_image_browse_button_press)
        QObject.connect(self.decode_file_text, SIGNAL("textEdited(QString)"),
                        self.on_decode_file_text_change)
        QObject.connect(self.decode_image_text, SIGNAL("textEdited(QString)"),
                        self.on_decode_image_text_change)
        QObject.connect(self.decode_red_bits_combo, SIGNAL("currentIndexChanged(int)"),
                        self.on_decode_red_bits_change)
        QObject.connect(self.decode_green_bits_combo, SIGNAL("currentIndexChanged(int)"),
                        self.on_decode_green_bits_change)
        QObject.connect(self.decode_blue_bits_combo, SIGNAL("currentIndexChanged(int)"),
                        self.on_decode_blue_bits_change)
        QObject.connect(self.decode_button, SIGNAL("clicked()"),
                        self.on_decode_button_press)
        QObject.connect(self.decode_thread, SIGNAL("terminated()"), self.unknown_error)
        QObject.connect(self.decode_thread, SIGNAL("complete()"), self.decode_success)
        QObject.connect(self.auto_detect_checkbox, SIGNAL("clicked()"),
                        self.auto_detect_toggled)
        
        
    # Encode event handlers
    def on_encode_file_browse_button_press(self):
        self.encode_txt_filename=str(QFileDialog.getOpenFileName(self.mw, "FileDialog","*.txt"))
        tmp = self.encode_txt_filename.split("/")[-1]
        self.encode_file_text.setText(tmp)

    def on_encode_image_browse_button_press(self):
        self.encode_image_filename=str(QFileDialog.getOpenFileName(self.mw, "FileDialog","*.png"))
        tmp = self.encode_image_filename.split("/")[-1]
        self.encode_image_text.setText(tmp)

    def on_encode_new_image_browse_button_press(self):
        self.encode_new_image_filename=str(QFileDialog.getOpenFileName(self.mw, "FileDialog","*.png"))
        tmp = self.encode_new_image_filename.split("/")[-1]
        self.encode_new_image_text.setText(tmp)
        
    def on_encode_red_bits_change(self, index):
        self.encode_red_bits = (index+1)%9

    def on_encode_green_bits_change(self, index):
        self.encode_green_bits = (index+1)%9
    
    def on_encode_blue_bits_change(self, index):
        self.encode_blue_bits = (index+1)%9

    def on_encode_new_image_text_change(self, myStr):
        self.encode_new_image_filename = str(myStr)

    def on_encode_image_text_change(self, myStr):
        self.encode_image_filename = str(myStr)
    
    def on_encode_file_text_change(self, myStr):
        self.encode_txt_filename = str(myStr)
        
    def on_encode_button_press(self):
        if (self.encode_image_filename != "" and 
            self.encode_new_image_filename != "" and
            self.encode_txt_filename != ""):
            self.run_progress()
            if not self.auto_bits_set:
                bits = steganography.get_recommended_encoding(self.encode_txt_filename, self.encode_image_filename)
                self.encode_red_bits_combo.setCurrentIndex((bits[0]-1)%8)
                self.encode_green_bits_combo.setCurrentIndex((bits[1]-1)%8)
                self.encode_blue_bits_combo.setCurrentIndex((bits[2]-1)%8)
                self.auto_bits_set = True
            bits = [self.encode_red_bits, self.encode_green_bits, self.encode_blue_bits]
            self.encode_thread.setup(self.encode_image_filename, self.encode_txt_filename, 
                                     self.encode_new_image_filename, [self.encode_red_bits, 
                                     self.encode_green_bits, self.encode_blue_bits])
        else:
            tmp = QErrorMessage(self.mw)
            tmp.showMessage("Please specify all filenames.")
            
    def encode_success(self):
        #encode_dialog.EncodeDialog(self.mw, self.encode_image_filename, self.encode_txt_filename, self.encode_new_image_filename)
        tmp = QErrorMessage(self.mw)
        tmp.showMessage(self.encode_txt_filename.split("/")[-1] + " encoded into " + 
                        self.encode_image_filename.split("/")[-1] + " and written to " + 
                        self.encode_new_image_filename.split("/")[-1] + ".")
        self.progress_complete()
        
    def encode_error(self, msg =""):
        tmp = QErrorMessage(self.mw)
        tmp.showMessage("The image is not large enough to contain the specified file" +
                            " with the current settings")
        self.progress_complete()
            
    def run_progress(self):
        self.prog_dialog.show()
        self.progress_thread.start()
    
    def progress_complete(self):
        self.progress_thread.end()
        self.progress_thread.__del__()
        self.prog_dialog.hide()
        self.progress_thread = stegthreads.ProgressWorker(self.prog_dialog)
        
    def auto_encode_toggled(self):
        if self.auto_encode_checkbox.checkState():
            if self.encode_txt_filename != '' and self.encode_image_filename != '':
                bits = steganography.get_recommended_encoding(self.encode_txt_filename, self.encode_image_filename)
                self.encode_red_bits_combo.setCurrentIndex((bits[0]-1)%8)
                self.encode_green_bits_combo.setCurrentIndex((bits[1]-1)%8)
                self.encode_blue_bits_combo.setCurrentIndex((bits[2]-1)%8)
                self.auto_bits_set = True
            self.encode_blue_bits_combo.setEnabled(False)
            self.encode_red_bits_combo.setEnabled(False)
            self.encode_green_bits_combo.setEnabled(False)
            self.auto_encode = True
        else:
            self.encode_blue_bits_combo.setEnabled(True)
            self.encode_red_bits_combo.setEnabled(True)
            self.encode_green_bits_combo.setEnabled(True)
            self.auto_encode = False 
            self.auto_bits_set = False

    # Decode event handlers
    def on_decode_file_browse_button_press(self):
        self.decode_txt_filename=str(QFileDialog.getOpenFileName(self.mw, "FileDialog","*.txt"))
        tmp = self.decode_txt_filename.split("/")[-1]
        self.decode_file_text.setText(tmp)

    def on_decode_image_browse_button_press(self):
        self.decode_image_filename=str(QFileDialog.getOpenFileName(self.mw, "FileDialog","*.png"))
        tmp = self.decode_image_filename.split("/")[-1]
        self.decode_image_text.setText(tmp)
        
    def on_decode_red_bits_change(self, index):
        self.decode_red_bits = (index+1)%9

    def on_decode_green_bits_change(self, index):
        self.decode_green_bits = (index+1)%9
    
    def on_decode_blue_bits_change(self, index):
        self.decode_blue_bits = (index+1)%9

    def on_decode_file_text_change(self, myStr=""):
        self.decode_txt_filename = str(myStr)

    def on_decode_image_text_change(self, myStr=""):
        self.decode_image_filename = str(myStr)
        
    def on_decode_button_press(self):
        if(self.decode_image_filename != "" and self.decode_txt_filename != ""):
            if not self.auto_detect:
                self.decode_thread.setup(self.decode_image_filename, self.decode_txt_filename,
                                         [self.decode_red_bits, self.decode_green_bits,
                                          self.decode_blue_bits])
                self.run_progress()
            else:
                prob_encoding = detect_steg.dictionary_steg_detect(self.decode_image_filename)
                if len(prob_encoding['forward']) >= 1:
                    self.decode_thread.setup(self.decode_image_filename, self.decode_txt_filename,
                                             prob_encoding['forward'][0])
                    self.run_progress()
                elif len(prob_encoding['backward']) >= 1:
                    self.decode_thread.setup(self.decode_image_filename, self.decode_txt_filename,
                                             prob_encoding['backward'][0])
                    self.run_progress()
                else:
                    tmp = QErrorMessage(self.mw)
                    tmp.showMessage("No encoding detected, cannot decode.")
        else:
            tmp = QErrorMessage(self.mw)
            tmp.showMessage("Please specify all filenames.")

    def decode_success(self):
        self.progress_complete()
        tmp = QErrorMessage(self.mw)
        tmp.showMessage(self.decode_image_filename.split("/")[-1] + " decoded and written to " +
                        self.decode_txt_filename.split("/")[-1] + ".")

    def unknown_error(self):
        tmp = QErrorMessage(self.mw)
        tmp.showMessage("An unknown error has occurred")
        self.progress_complete()
        
    def auto_detect_toggled(self):
        if self.auto_detect_checkbox.checkState():
            self.decode_blue_bits_combo.setEnabled(False)
            self.decode_red_bits_combo.setEnabled(False)
            self.decode_green_bits_combo.setEnabled(False)
            self.auto_detect = True
        else:
            self.decode_blue_bits_combo.setEnabled(True)
            self.decode_red_bits_combo.setEnabled(True)
            self.decode_green_bits_combo.setEnabled(True)
            self.auto_detect = False 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myg = MyGUI()
    app.exec_()
    
    