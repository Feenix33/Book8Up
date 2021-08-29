import sys
import os
from fpdf import FPDF
import csv
import datetime
import configparser
from pprint import pprint
#import re

'''
ToDo
x Create an ini file for reading in doc parameters
x Base class has the ini and defn files
x Frame on title and backpage and each page

o Book publishing with defn on command line
o Image on Title and back
o Fold lines
o Better control on book defn file
o Other page types besides recipe
'''

class Booklet(FPDF):
    def __init__(self, *args, **kwargs):
        super(Booklet, self).__init__('L', 'in','Letter')
        self.config = configparser.ConfigParser()

        # added stuff
        self.fname = "Boomlet.pdf"
        ini_file = "book.ini"
        if 'ini' in kwargs:
            print ("Processing new ini file = ", kwargs['ini'])
            ini_file = kwargs['ini']
        self.read_ini(ini_file)
        self.build_panes()


    def read_ini(self, iniFile):
        #print ("Exe {}".format("read_ini"))
        #print ("\tinFile = {}".format(iniFile))
        # setup the config parser
        self.config = configparser.ConfigParser()
        self.config.read(iniFile)
        default = self.config['Default']
        # read in the layout parameters
        self.page_margin = default.getfloat('PageMargin', 0.2)
        self.pane_margin = default.getfloat('PaneMargin', 0.2)
        self.pane_font_size = default.getint('PaneFontSize', 7)
        self.back_font_size = default.getint('BackFontSize', 6)
        self.title_font_size = default.getint('TitleFontSize', 14)
        self.author_font_size = default.getint('AuthorFontSize', 10)
        self.title_position = default.getint('TitlePosition', 40)
        self.pane_use_width = default.getfloat('PaneUseWidth', 0.80)
        self.pt2in = 0.0138889
        self.title_frame = default.getboolean('TitleFrame', True)
        self.back_frame = default.getboolean('BackFrame', True)

        default_format = default.get('DefaultFormat', "Text")
        self.pane_format = [default_format] * 8 #init the 8 pages to the default
        for j in range(8):
            self.pane_format[j] = default.get('P'+str(j+1)+'Format', default_format)

        # Read the book specific portions
        infiles = default.get('InFiles', "")

        pprint (self.pane_format)
        self.infiles = infiles.split(",")
        self.infiles = [t.strip() for t in self.infiles]

        self.title = default.get('Title', "Booklet Title")
        self.author = default.get('Author', "<< author >>")
        self.date = default.get('Date', "<< date >>")
        self.edition = default.get('Edition', "<< edition >>")
        self.book8up = "1.0" # no get

        print ("*"*50)
        print (self.infiles)
        print (self.title)
        print (self.author)
        print (self.date)
        print (self.edition)
        #print (infiles.split(",").strip())
        #print (re.split(', ',infiles))
        print ("*"*50)



    def build_panes(self):
        # hardcoded
        print ("building_panes() init")
        #self.page_margin = self.ipage_margin
        #self.pane_margin = self.ipane_margin
        paneW = (11 - 2*self.page_margin - 3*self.pane_margin)/4
        paneH = (8.5 - 2*self.page_margin - self.pane_margin)/2
        self.pane_width = (11 - 2*self.page_margin - 3*self.pane_margin)/4
        self.pane_height = (8.5 - 2*self.page_margin - self.pane_margin)/2
        self.panes = []
        for h  in range (1,3):
            for w in range (1,5):
                x1 = self.page_margin + (w-1)*(self.pane_width + self.pane_margin)
                y1 = self.page_margin + (h-1)*(self.pane_height + self.pane_margin)
                x2 = x1 + self.pane_width
                y2 = y1 + self.pane_height
                self.panes.append([x1, y1])
        j=0
        '''
        for pane in self.panes:
            print ("{} {:.2f} {:.2f}".format(j, pane[0], pane[1]))
            j+=1
        '''

    def bold(self):
        self.set_font('Arial','B',self.pane_font_size)

    def normal(self):
        self.set_font('Arial','',self.pane_font_size)

    def process(self):
        marPage = 0.25
        marPane = 0.2


        self.add_page()
        self.set_margins(marPage, marPage, marPage)

        self.print_pane(0, self.infiles[0])
        self.print_pane(1, self.infiles[1])
        self.print_pane(2, self.infiles[2])
        self.print_pane(3, self.infiles[3])
        self.print_back(pane_index=4)
        self.print_title(5)
        self.print_pane(6, self.infiles[4])
        self.print_pane(7, self.infiles[5])

    def print_pane(self, pane_index, infile):
        #print ("print_pane({})".format(infile))
        txt = self.get_file_text(infile)
        px = self.panes[pane_index][0]
        py = self.panes[pane_index][1]
        #pw = self.panes[pane_index][2] - self.panes[pane_index][0]
        pw = self.pane_width
        
        mch = self.pane_font_size * 1.2 * self.pt2in

        j = txt.find('\n')
        self.set_xy(px, py)
        self.bold()
        self.multi_cell(pw, (mch*1.5), txt[:j], align='C')
        self.set_x(px)
        self.normal()
        self.multi_cell(pw, mch, txt[(j+1):])

    def print_back(self, pane_index=2):
        #print("print_back() on pane {}".format(pane_index))
        self.set_font('Arial','', self.back_font_size)
        mch = self.back_font_size * 1.3 * self.pt2in

        #adjust width to make narrower
        pw_adjustment = 2
        back_align = 'C'
        px = self.panes[pane_index][0] + pw_adjustment *self.pane_margin
        py = self.panes[pane_index][1] + (1*self.pane_height/2)
        pw = self.pane_width - 2*pw_adjustment *self.pane_margin #double for left&right
        #print("\tpx={:.2f} py={:.2f} pw={:.2f}".format(px, py, pw))

        self.set_xy(px, py)
        txt = self.title
        self.multi_cell(pw, mch, txt, align=back_align, border=0)

        if self.author:
            self.set_x(px)
            txt = "by {}".format(self.author)
            self.multi_cell(pw, mch, txt, align=back_align, border=0)

        if self.edition:
            self.set_x(px)
            txt = "{} Edition".format(self.edition)
            self.multi_cell(pw, mch, txt, align=back_align, border=0)

        now = datetime.datetime.now().strftime("%d %B %Y")
        self.set_x(px)
        txt = "Created on {}".format(now)
        self.multi_cell(pw, mch, txt, align=back_align, border=0)

        if self.book8up:
            self.set_x(px)
            txt = "using book8up.py Ver {}".format(self.book8up)
            self.multi_cell(pw, mch, txt, align=back_align, border=0)

        if self.back_frame: self.pane_frame(pane_index)


    def print_title(self, pane_index=7, title_text=None):
        txt = title_text or self.title

        pane_mar = (1.0 - self.pane_use_width)/2
        pw = self.pane_width * self.pane_use_width

        self.set_font('Arial','B', self.title_font_size)
        mch = self.title_font_size * 1.3 * self.pt2in

        sw = self.get_string_width(txt)
        px = self.panes[pane_index][0] + (self.pane_width * pane_mar)
        py = self.panes[pane_index][1] + (self.pane_height*self.title_position/100.0) - mch * (int(sw/pw)+1)
        #xxxx

        self.set_xy(px, py)


        self.multi_cell(pw, mch, txt, align='C', border=0)
        sw = self.get_string_width(txt)

        self.set_font('Arial','', self.author_font_size)
        self.set_x(px)
        self.multi_cell(pw, mch, "\n", align='C', border=0)
        txt = self.author
        self.set_x(px)
        self.multi_cell(pw, mch, txt, align='C', border=0)
        
        if self.title_frame: self.pane_frame(pane_index)


    def pane_frame(self, pane_index):
        px = self.panes[pane_index][0]
        py = self.panes[pane_index][1]
        self.line(px, py, px+self.pane_width, py)
        self.line(px, py+self.pane_height, px+self.pane_width, py+self.pane_height)
        self.line(px, py, px, py+self.pane_height)
        self.line(px+self.pane_width, py, px+self.pane_width, py+self.pane_height)


    def get_file_text(self, infile):
        # convert to a try catch eventually for file does not exist cases
        with open(infile, 'r') as fh:
            txt = fh.read()
        fh.close ()
        return txt

    def publish(self):
        print("publish() booklet to file {}".format(self.fname))
        self.output(self.fname)



if __name__ == "__main__":

    book = Booklet(ini="book.ini")
    #debug print
    book.process()
    book.publish()
