import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty

from kivy.core.clipboard import Clipboard
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox

from kivymd.bottomsheet import MDListBottomSheet
from kivymd.button import MDRaisedButton
from kivymd.button import MDFloatingActionButton
from kivymd.label import MDLabel
from kivymd.list import ILeftBodyTouch
from kivymd.selectioncontrols import MDCheckbox
from kivymd.snackbar import Snackbar
from kivymd.theming import ThemeManager

import thread
import time
from pytube import YouTube

# https://www.youtube.com/watch?v=TnCY6Apxibk
class IconLeftSampleWidget(ILeftBodyTouch, MDCheckbox):
    pass

class MyBoxLayout(BoxLayout):

	file_size = 0
	download_status = 0

	def __init__(self, **kwargs):
        	super(MyBoxLayout, self).__init__(**kwargs)
        	self.ids.inputUrl.text = 'https://youtu.be/TrDZOK-kXAg'

	def goButtonClicked(self, url):
		self.ids.spinner.active = True
		thread.start_new_thread( self.fetchVideo, (url,))


	def fetchVideo(self, url):
		box_vertical = self.ids.b1
		self.yt = YouTube(url)
		self.yt.register_on_complete_callback(self.downloadComplete)
		self.yt.register_on_progress_callback(self.showProgressBar)

		v_strms = self.yt.streams.filter(progressive=True).all()
		a_strms = self.yt.streams.filter(only_audio=True).first()
		self.selected = self.yt.streams.first()

		v_strms.append(a_strms)
		self.streams = v_strms

		for index,eachStream in enumerate(self.streams):
		    box_horizontal = BoxLayout(orientation='horizontal')
		    checkbox = MDCheckbox(id=str(index), group='test', size_hint_x=.2 )
		    checkbox.bind(active=self.cb_clicked)
		    video_details = 'Format: ' + str(eachStream.mime_type) + ', Resolution: ' + str(eachStream.resolution)
		    label = MDLabel(text=video_details,
		    			font_style= 'Body1',
                        theme_text_color= 'Primary',
                        size_hint_x= .8,
                        width= '56dp')
		    box_horizontal.add_widget(checkbox)
		    box_horizontal.add_widget(label)
		    box_vertical.add_widget(box_horizontal)

		self.ids.spinner.active = False

	def print_test(self):
		print 'hello '

	def resetApp(self):

		box_vertical = self.ids.b1
		box_vertical.clear_widgets()

		self.streams = []
		self.file_size = 0
		self.download_status = 0

	def cb_clicked(self, checkbox, value):
		self.selected = self.streams[int(checkbox.id)]
	
	def updateProgressBar(self, init_download):
		while True:
			print round(self.download_status)
			time.sleep(1)
			self.ids.progress_bar.value = round(self.download_status)
			if self.ids.progress_bar.value == 100.0:
				break

	def showProgressBar(self, stream, chunk, file_handle, bytes_remaining):
		if self.file_size > bytes_remaining :
			self.download_status = ((self.file_size - float(bytes_remaining))/self.file_size)*100
		else:
			self.file_size = bytes_remaining
			#thread.start_new_thread(self.updateProgressBar, (self.download_status,))
		

	def downloadVideo(self, selectedVideo):
		selectedVideo.download()

	def downloadButtonClicked(self):
		self.ids.spinner.active = True
		thread.start_new_thread(self.downloadVideo, (self.selected,))
		thread.start_new_thread(self.updateProgressBar, (self.download_status,))

	def downloadComplete(self, stream, file_handle):
		self.ids.spinner.active = False
		self.ids.progress_bar.value = 100.0
		self.showSnackBar()

	def showSnackBar(self):
		Snackbar(text="Download Complete!").show()

	def pasteURL(self):
		self.ids.inputUrl.text = Clipboard.paste()

class MyApp(App):
	theme_cls = ThemeManager()
	def build(self):
		return MyBoxLayout()

MyApp().run()
