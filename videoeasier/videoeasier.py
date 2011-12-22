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

    def on_cellrenderertoggle_toggled(self, widget, row):
        iter = self.liststoreFile.get_iter(row)
        if self.liststoreFile.get_value(iter, 0):
            self.liststoreFile.set_value(iter, 0,0)
        else:
            self.liststoreFile.set_value(iter, 0,1)

    def load_Dir(self,dir):
        """Load dir and subdirs recursively"""
        self.treestoreDir.clear()
        dirList=os.listdir(os.getcwd())
        dircontents = []
        for item in dirList:
            if item[0] != '.':
                if os.path.isdir(item):
                    dircontents.append([item])
        dircontents.sort()
        for act in dircontents:
            self.treestoreDir.append(None,act)

    def load_File(self,dir):
        self.labelMaskRoot.set_text(dir + "/")
        self.liststoreFile.clear()
        for item in os.listdir(dir):
            if item[0] != '.':
                if os.path.isfile(os.path.join(dir,item)):
                    item=File(item)
                    if item.kind_checker() == "tv":
                        tv=TVObject(item.name + item.extension)
                        self.liststoreFile.append([1,0,item.name+ item.extension,""])
                    else:
                        if item.kind_checker() == "movie":
                            self.liststoreFile.append([0,0,item.name,""])
                            pass

        
    
    def on_filechooserbutton_current_folder_changed(self, widget, data=None):
        """Clear and refresh the TreeViews"""
        os.chdir(self.filechooserbutton.get_current_folder())
        self.load_Dir(self.filechooserbutton.get_current_folder())
        self.liststoreFile.clear()
        self.load_File (self.filechooserbutton.get_current_folder())
        self.labelMaskRoot.set_text(os.getcwd() + "/")       

    def on_buttonTestSelected_clicked(self, widget, data=None):
        self.liststoreFile.foreach(self.FillTest)

    def on_buttonBatchRename_clicked(self, widget, data=None):
        self.liststoreFile.foreach(self.BatchRename)

    def on_buttonRename_clicked(self, widget, data=None):
        if self.get_src_and_dst()[0]:
            print self.get_src_and_dst()[0], self.file_fullpath + "/" + self.entryFilename.get_text()
            shutil.move(self.get_src_and_dst()[0], self.file_fullpath + "/" + self.entryFilename.get_text())
            self.load_File (self.get_src_and_dst()[2])

    def get_src_and_dst (self):
        self.file_fullpath = os.getcwd()
        if self.treeviewDir.get_cursor()[0]:
            selection = self.treeviewDir.get_selection()
            treeviewDir_model, treeviewDir_iter = selection.get_selected()
            self.file_fullpath = self.file_fullpath + "/" + treeviewDir_model.get_value(treeviewDir_iter,0)

        if self.treeviewFile.get_cursor()[0]:
            selection = self.treeviewFile.get_selection()
            treeviewFile_model, treeviewFile_iter = selection.get_selected()
            src = self.file_fullpath + '/' + treeviewFile_model.get_value(treeviewFile_iter,2)
            if treeviewFile_model.get_value(treeviewFile_iter,3):
                dst = self.file_fullpath + '/' + treeviewFile_model.get_value(treeviewFile_iter,3)
            #self.liststoreFile.set_value(treeviewFile_iter,3,self.entryRename.get_text())
            #shutil.move(src, dst)
                return src,dst,self.file_fullpath
        return src,None,self.file_fullpath
        
    def BatchRename (self, model, path, iter):
        self.treeviewFile.set_cursor(path)
        if self.get_src_and_dst()[1]:
                    print self.get_src_and_dst()[0],self.get_src_and_dst()[1]
  
           
    def on_treeviewDir_cursor_changed(self, widget, data=None):

        treeviewDir_model, treeviewDir_iter = self.treeviewDir.get_selection().get_selected()
        self.file_fullpath = os.getcwd() + "/" + treeviewDir_model.get_value(treeviewDir_iter,0)
        
        
        self.clear_Info_window ()

        self.load_File (self.file_fullpath)

        
     
    def on_treeviewDir_row_activated(self, widget, row, col):
        os.chdir(os.getcwd()+"/"+widget.get_model()[row][0])
        self.filechooserbutton.set_current_folder(os.getcwd())

    def clear_Info_window(self):
        self.entryTitle.set_text('')
        self.textbufferOverview.set_text('')
        self.textviewOverview.set_buffer(self.textbufferOverview)
        self.entryFilename.set_text('')
        self.entryShowname.set_text('')
        self.entryEpisode.set_text('')
        self.entrySeason.set_text('') 
        self.entryRename.set_text('')
        self.imageBanner.set_visible(False)
    
    def on_treeviewFile_cursor_changed(self, widget, data=None):
        """When a file is selected with clear every entry first and the populate those entries with the TVObject attributes"""
        self.clear_Info_window ()
        selection = self.treeviewFile.get_selection()
        tree_model, tree_iter = selection.get_selected()

        if tree_model.get_value(tree_iter,0):
            self.tv = TVObject(tree_model.get_value(tree_iter,2))
            self.entryFilename.set_text(self.tv.clean_name)
            self.entryShowname.set_text(self.tv.ep_showname)
            self.entryEpisode.set_text(str(self.tv.ep_number))
            self.entrySeason.set_text(str(self.tv.ep_season))
            self.scrolledwindowInfoTV.set_visible(True)
            self.change_entryMask()
            #self.liststoreFile.set_value(tree_iter,3,self.entryRename.get_text())

    def cleanNewName (self, model, path, iter):
        self.liststoreFile.set_value(iter,3,"")
    
    def change_entryMask(self):
        if self.entryMask.get_text_length() > 0:
            entryMaskHelper = self.entryMask.get_text()
            filename = os.path.splitext(self.entryFilename.get_text())[0]
            ext = os.path.splitext(self.entryFilename.get_text())[-1]
            if self.entryTitle.get_text():
                self.subs=[['%t',"-" + self.entryTitle.get_text()],
                ['%e', self.entryEpisode.get_text()],
                ['%n',self.entryShowname.get_text()],
                ['%f',filename],
                ['%s',self.entrySeason.get_text()]
                ]
            else:
                self.subs=[['%t',''],
                ['%e', self.entryEpisode.get_text()],
                ['%n',self.entryShowname.get_text()],
                ['%f',filename],
                ['%s',self.entrySeason.get_text()]
                ]
            
            for item in self.subs:
                entryMaskHelper  = re.sub(item[0],item[1],entryMaskHelper)
            self.entryRename.set_text(entryMaskHelper + ext)
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

    def on_togglebuttonShowInfo_toggled(self, widget, data=None):  
        if self.togglebuttonShowInfo.get_active():
            self.frameInfo.set_visible(True)
        else:
            self.frameInfo.set_visible(False)

        
    def on_buttonReset_clicked(self, widget, data=None):  
        self.filechooserbutton.set_current_folder(os.getcwd ())

    def on_buttonBack_clicked(self, widget, data=None):  
        self.filechooserbutton.set_current_folder(os.pardir)

    def on_buttonTVDB_clicked(self, widget, data=None):
        """Whe the TVDB button is clicked we create the tvdb object, fill the title entry, fill the overview /
         and display banner"""
        t = tvdb.tvdb_api.Tvdb(banners = self.checkbuttonBanner.get_active())
        self.ep_object = t[self.tv.ep_showname][self.tv.ep_season][self.tv.ep_number]
        self.ep_title = self.ep_object['episodename'].strip()
        self.entryTitle.set_text(self.ep_title)
        self.change_entryMask ()

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

         
    def FillTest(self, model, path, iter):
        self.treeviewFile.set_cursor(path)
        selection = self.treeviewFile.get_selection()
        tree_model, tree_iter = selection.get_selected()
        if tree_model.get_value(tree_iter,0):
            if self.checkbuttonBatchTVDB.get_active():
                t = tvdb.tvdb_api.Tvdb()
                self.ep_object = t[self.tv.ep_showname][self.tv.ep_season][self.tv.ep_number]
                self.ep_title = self.ep_object['episodename'].strip()
                self.entryTitle.set_text(self.ep_title)
            self.change_entryMask ()
            self.liststoreFile.set_value(tree_iter,3,self.entryRename.get_text())
        

            
    def resize_image(self):
        """Resize the image based on the widget width, we create a scale factor from that to get the right height"""
        scale_factor = float(self.scrolledwindowInfoTV.get_allocation().width) / float(self.image_loader.get_pixbuf().get_width())
        self.imageBanner.set_from_pixbuf(self.image_loader.get_pixbuf().scale_simple(self.scrolledwindowInfoTV.get_allocation().width,int(self.image_loader.get_pixbuf().get_height() * scale_factor),gtk.gdk.INTERP_BILINEAR))
        self.imageBanner.set_visible(True)

    def resize_image2(self, widget, data=None):
        if  self.imageBanner.get_visible() == True:
            scale_factor = float(self.scrolledwindowInfoTV.get_allocation().width) / float(self.image_loader.get_pixbuf().get_width())
            self.imageBanner.set_from_pixbuf(self.image_loader.get_pixbuf().scale_simple(self.scrolledwindowInfoTV.get_allocation().width,int(self.image_loader.get_pixbuf().get_height() * scale_factor),gtk.gdk.INTERP_NEAREST))

        
  
    def __init__(self,dir):
    
        builder = gtk.Builder()
        builder.add_from_file(os.path.dirname(os.path.realpath(__file__)) + "/videoeasier.glade")
        
        self.window = builder.get_object("mainWindow")
        self.entryFilename = builder.get_object("entryFilename")
        self.entryShowname = builder.get_object("entryShowname")
        self.entryEpisode = builder.get_object("entryEpisode")
        self.entrySeason = builder.get_object("entrySeason")
        self.entryTitle = builder.get_object("entryTitle")
        self.entryRename = builder.get_object("entryRename")
        self.entryMask = builder.get_object("entryMask")
        self.filechooserbutton = builder.get_object("filechooserbutton")
        self.treestoreDir = builder.get_object("treestoreDir")
        self.treeviewDir = builder.get_object("treeviewDir")
        self.liststoreFile = builder.get_object("liststoreFile")
        self.treeviewFile = builder.get_object("treeviewFile")
        self.imageBanner = builder.get_object("imageBanner")
        self.scrolledwindowInfoTV = builder.get_object("scrolledwindowInfoTV")
        self.textviewOverview = builder.get_object("textviewOverview")
        self.textbufferOverview = builder.get_object("textbufferOverview")
        self.statusbar = builder.get_object("statusbar")
        self.checkbuttonBanner = builder.get_object("checkbuttonBanner")
        self.checkbuttonBatchTVDB = builder.get_object("checkbuttonBatchTVDB")
        self.labelMaskRoot = builder.get_object("labelMaskRoot")
        self.frameInfo = builder.get_object("frameInfo")
        self.togglebuttonShowInfo = builder.get_object("togglebuttonShowInfo")

        self.entryFilenameMovie = builder.get_object("entryFilenameMovie")
        builder.connect_signals(self)

        self.filechooserbutton.set_current_folder(dir)
        self.entryMask.set_text("%n/Season %s/%f%t")
class TVObject():
    """class for tv object"""
    def __init__(self,file):
        self.name = file
        self.clean_name = self.clean().replace(' ','.')
        self.ep_showname, self.ep_number, self.ep_season, self.name = self.tv_parser(self.clean())
        #self.clean_name_noext = os.path.splitext(self.clean_name)[:-1]
        #print self.clean_name_noext
        #self.newname = self.getNewName()

    
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


        return ('', '', '', file)

class Movie():
    """class for tv object"""
    def __init__(self,file):
        self.name = file

class File():
    """Generic class for file, does some job before deciding if it is a movie or tv file"""
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
        return s

    def tv_checker(self):
        """Extract info from the file"""
    
        results = re.search(r'[s|S](\d+)[e|E](\d+)', self.clean_name)
        if results:
            return "tv"

        results = re.search(' (\d)(\d\d) ', self.clean_name)
        if results:
            return "tv"

        results = re.search('(\d+)[Xx](\d\d)', self.clean_name)
        if results:
            return "tv"

        return "movie"

    def kind_checker(self):
        extensions = ['avi','mkv','mp4','mpg','mpeg','mov','wmv']
        for ext in extensions:
            if self.extension.lstrip('.') == ext:
                #print "ext2"
                return self.tv_checker()
        return "novideo"

    def __init__(self,file):
        results = os.path.splitext(file)
        self.extension = results[1].lower()
        self.name = results[0]
        #print self.extension
        self.clean_name = self.clean()
        self.kind = self.kind_checker()
        


if __name__ == "__main__":
    if len(sys.argv) > 1:
        dir = sys.argv[1]
    else:
        dir = os.getcwd()
    videoeasier = VideoEasier(dir)
    videoeasier.window.show()
    gtk.main()
