#!/usr/bin/env python

# First run tutorial.glade through gtk-builder-convert with this command:
# gtk-builder-convert tutorial.glade tutorial.xml
# Then save this file as tutorial.py and make it executable using this command:
# chmod a+x tutorial.py
# And execute it:
# ./tutorial.py

import sys
import gtk
import os
import re
import tvdb.tvdb_api
import urllib2
import shutil
import sys

class VideoEasier():
    """Main class for the GTK interface"""
    count=0

    def on_mainWindow_destroy(self, widget, data=None):
        gtk.main_quit()

    def on_filechooserbutton_current_folder_changed(self, widget, data=None):
        """Clear and refresh the TreeViews"""
        os.chdir(self.filechooserbutton.get_current_folder())
        #print os.getcwd()
        self.liststoreDir.clear()
        self.liststoreFile.clear()
        #self.treeviewDir.freeze_child_notify()
        #self.treeviewDir.set_model(None)
        #self.labelMaskRoot.set_text(self.filechooserbutton.get_current_folder() + "/")
        dirList=os.listdir(os.getcwd())
        dircontents = []
        dircontents.append(['..'])
        for item in dirList:
            if item[0] != '.':
                if os.path.isdir(item):
                    dircontents.append(['/'+item])
        dircontents.sort()
        for act in dircontents:
            self.liststoreDir.append([act[0]])
            #print "for"
        #for item in os.listdir(self.root_dir):
         #   if os.path.isfile(os.path.join(self.root_dir,item)):
         #       self.treestoreFile.append(None, [item]) 
        #self.treeviewDir.set_model(self.liststoreDir)
        #self.treeviewDir.thaw_child_notify()
        #print "ok"    
    
    def push_message(self, message):
        buff = self.count
	self.count = self.count + 1
        self.statusbar.push(buff, message)
        return

    def pop_message(self, widget, message):
        #buff = " Item %d" % self.count
	#self.count = self.count + 1
        #self.status_bar.push(data, buff)
        pass
    
    def refresh_view(self):
        pass
            
           
    def on_treeviewDir_cursor_changed(self, widget, data=None):
        """When a directory is selected we create the fullpath from the selection and populate treestoreFile with /
           all the files found in fullpath"""       
        treeviewDir_model, treeviewDir_iter = self.treeviewDir.get_selection().get_selected()    
        self.file_fullpath = os.getcwd() + "/" + treeviewDir_model.get_value(treeviewDir_iter,0)

        self.liststoreFile.clear()

        for item in os.listdir(self.file_fullpath):
            if os.path.isfile(os.path.join(self.file_fullpath,item)):
                self.liststoreFile.append([item])
     
    def on_treeviewDir_row_activated(self, widget, row, col):
        if widget.get_model()[row][0] == "..":
            os.chdir(os.pardir)
            self.filechooserbutton.set_current_folder(os.getcwd())

        else:
            os.chdir(os.getcwd()+widget.get_model()[row][0])
            self.filechooserbutton.set_current_folder(os.getcwd())

        
    
    def on_treeviewFile_cursor_changed(self, widget, data=None):
        """When a file is selected with clear every entry first and the populate those entries with the TVObject attributes"""

        self.entryTitle.set_text('')
        self.textbufferOverview.set_text('')
        self.textviewOverview.set_buffer(self.textbufferOverview)
        self.entryFilename.set_text('')
        self.entryShowname.set_text('')
        self.entryEpisode.set_text('')
        self.entrySeason.set_text('')

        selection = self.treeviewFile.get_selection()
        tree_model, tree_iter = selection.get_selected()
        self.tv = TVObject(tree_model.get_value(tree_iter,0))
        self.entryFilename.set_text(self.tv.clean_name)
        self.entryShowname.set_text(self.tv.ep_showname)
        self.entryEpisode.set_text(str(self.tv.ep_number))
        self.entrySeason.set_text(str(self.tv.ep_season))
        #self.entryRename.set_text(self.entryFilename.get_text())
        self.change_entryMask()
       
    def change_entryMask(self):
        if self.entryMask.get_text_length() > 0:
            entryMaskHelper = self.entryMask.get_text()
            self.subs=[['%t',''],
            ['%e', 'episode number'],
            ['%n','season number'],
            ['%s','show name']
            ]
            for item in subs:
               entryMaskHelper  = re.sub(item[0],item[1],entryMaskHelper)
               self.entryRename.set_text(entryMaskHelper)
        else:
            self.entryRename.set_text(self.entryFilename.get_text())
    def on_entryMask_changed(self, widget, data=None):
        self.change_entryMask()
        




        self.imageBanner.set_visible(False)
        
    def getNewName(self):
        """return a string with for the rename entry"""
        results = os.path.splitext(self.entryFilename.get_text())
        extension = results[1]
        s = results[0]
        NewName = s + '.' + self.entryTitle.get_text().replace(' ','.') + extension
        return NewName.replace(' ','') 
        
        

    def on_buttonTVDB_clicked(self, widget, data=None):
        """Whe the TVDB button is clicked we create the tvdb object, fill the title entry, fill the overview /
         and display banner"""
        self.push_message('doing the tvdb stuff')
        t = tvdb.tvdb_api.Tvdb(banners = self.checkbuttonBanner.get_active())
        self.ep_object = t[self.tv.ep_showname][self.tv.ep_season][self.tv.ep_number]
        self.ep_title = self.ep_object['episodename'].strip()
        self.entryTitle.set_text(self.ep_title)
        #self.
        self.entryRename.set_text(self.getNewName())

        if self.checkbuttonBanner.get_active():
            d = t[self.tv.ep_showname]['_banners']['series']['graphical'].values()[0].items()
            for item in d:
                if item[0] == '_bannerpath':
                    bannerpath = item[1]
            response=urllib2.urlopen(bannerpath)
            self.image_loader = gtk.gdk.PixbufLoader()
            self.image_loader.write(response.read())
            self.image_loader.close()
            self.resize_image()

        self.textbufferOverview.set_text(self.ep_object['overview'])
        self.textviewOverview.set_buffer(self.textbufferOverview)

    def on_buttonRename_clicked(self, widget, data=None):
        """Rename files"""

        selection = self.treeviewFile.get_selection()
        tree_model, tree_iter = selection.get_selected()
        src = self.file_fullpath + '/' + tree_model.get_value(tree_iter,0)
        dst = self.file_fullpath + '/' + self.entryRename.get_text()
        shutil.move(src, dst)   

    def resize_image(self):
        """Resize the image based on the widget width, we create a scale factor from that to get the right height"""
        scale_factor = float(self.scrolledwindow3.get_allocation().width) / float(self.image_loader.get_pixbuf().get_width())
        self.imageBanner.set_from_pixbuf(self.image_loader.get_pixbuf().scale_simple(self.scrolledwindow3.get_allocation().width,int(self.image_loader.get_pixbuf().get_height() * scale_factor),gtk.gdk.INTERP_BILINEAR))
        self.imageBanner.set_visible(True)

    def resize_image2(self, widget, data=None):
        if  self.imageBanner.get_visible() == True:
            scale_factor = float(self.scrolledwindow3.get_allocation().width) / float(self.image_loader.get_pixbuf().get_width())
            #self.imageBanner.set_from_pixbuf(self.image_loader.get_pixbuf().scale_simple(self.scrolledwindow3.get_allocation().width,int(self.image_loader.get_pixbuf().get_height() * scale_factor),gtk.gdk.INTERP_BILINEAR))
            self.imageBanner.set_from_pixbuf(self.image_loader.get_pixbuf().scale_simple(self.scrolledwindow3.get_allocation().width,int(self.image_loader.get_pixbuf().get_height() * scale_factor),gtk.gdk.INTERP_NEAREST))

        
  
    def __init__(self,dir):
    
        builder = gtk.Builder()
        builder.add_from_file("videoeasier.glade") 
        
        self.window = builder.get_object("mainWindow")
        self.entryFilename = builder.get_object("entryFilename")
        self.entryShowname = builder.get_object("entryShowname")
        self.entryEpisode = builder.get_object("entryEpisode")
        self.entrySeason = builder.get_object("entrySeason")
        self.entryTitle = builder.get_object("entryTitle")
        self.entryRename = builder.get_object("entryRename")
        self.entryMask = builder.get_object("entryMask")
        self.filechooserbutton = builder.get_object("filechooserbutton")
        self.liststoreDir = builder.get_object("liststoreDir")
        self.treeviewDir = builder.get_object("treeviewDir")
        self.liststoreFile = builder.get_object("liststoreFile")
        self.treeviewFile = builder.get_object("treeviewFile")
        self.imageBanner = builder.get_object("imageBanner")
        self.scrolledwindow3 = builder.get_object("scrolledwindow3")
        self.textviewOverview = builder.get_object("textviewOverview")
        self.textbufferOverview = builder.get_object("textbufferOverview")
        self.statusbar = builder.get_object("statusbar")
        self.checkbuttonBanner = builder.get_object("checkbuttonBanner")
        self.labelMaskRoot = builder.get_object("labelMaskRoot")

        builder.connect_signals(self)

        self.filechooserbutton.set_current_folder(dir)
        os.chdir(dir)

        self.file_fullpath = dir
        #for item in os.listdir(self.filechooserbutton.get_current_folder()):
            #if os.path.isfile(os.path.join(self.filechooserbutton.get_current_folder(),item)):
                #self.treestoreFile.append(None, [item])     
            
class TVObject():
    """class for tv object"""
    def __init__(self,file):
        self.name = file
        self.clean_name = self.clean().replace(' ','.')
        self.ep_showname, self.ep_number, self.ep_season, self.name = self.tv_parser(self.clean())
        #print self.name, self.clean_name, self.ep_season
    
    def clean(self):
        """Replace underscores with spaces, capitalise words and remove
        brackets and anything inbetween them.
        """
        s = self.name
        file =  self.name
        opening_brackets = ['(', '[', '<', '{']
        closing_brackets = [')', ']', '>', '}']
        for i in range(len(opening_brackets)):
            b = opening_brackets[i]
            c = closing_brackets[i]

            while b in s:
                start = s.find(b)
                end = s.find(c) + 1

                s = re.sub(re.escape(s[start:end]), '', s)

        results = os.path.splitext(s)
        extension = results[1]
        s = results[0]

        s = s.replace('_', ' ')
        s = s.replace('.', ' ')
        s = s.strip()
        words = s.split(' ')
        s = ' '.join([w.capitalize() for w in words])
        s = s + extension
        s = re.sub('S\d+(e)\d+', self.fix_episode, s)

        return s

    def fix_episode(self,matchobj):
        """Used by the clean function to fix season capitalisation"""
        return matchobj.group(0).upper()

    def tv_parser(self,file):
        """Extract info from the file"""
        def tv_extractor(file):
            ep_season = int(results.groups()[0])
            ep_number = int(results.groups()[1])
            ep_showname = re.match('(.+?)\^s', file)
            ep_showname = ep_showname.groups()[0].strip(' .')
            ep_showname= os.path.basename(ep_showname)
            return (ep_showname, ep_number, ep_season, file)
    
        results = re.search(r'[s|S](\d+)[e|E](\d+)', file)
        if results:
            file = re.sub('[s|S](\d+)[e|E](\d+)', '^s^e', file)
            return tv_extractor(file)

        results = re.search(' (\d)(\d\d) ', file)
        if results:
            file = re.sub(' \d\d\d ', '^s^e', file)
            return tv_extractor(file)

        results = re.search('(\d+)[Xx](\d\d)', file)
        if results:
            file = re.sub('\d+[Xx]\d\d', '^s^e', file)
            return tv_extractor(file)

        return (ep_showname, ep_number, ep_season, file)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        dir = sys.argv[1]
    else:
        dir = os.getcwd()
    videoeasier = VideoEasier(dir)
    videoeasier.window.show()
    gtk.main()
