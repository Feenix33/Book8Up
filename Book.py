import sys
import os
from fpdf import FPDF
import csv
import datetime
import configparser
import logging
from pprint import pprint
#import re

'''
ToDo
x Create an ini file for reading in doc parameters
x Base class has the ini and defn files
x Frame on title and backpage and each page
x Better control on book defn file
x Other page types besides recipe
x image as a pane; add actual, width, height fit, left, centered
x standard error output / python std?
x logging

o default image sizing
o Book publishing with defn on command line
o pass body txt in ini file
o nroff parser for text
o pocket planner pages
o   calendar
o   weekly
o   daily
o   checkboxes
o   lines
o   grid / dots
'''

class Booklet(FPDF):
    def __init__(self, *args, **kwargs):
        super(Booklet, self).__init__('L', 'in','Letter')
        self.config = configparser.ConfigParser()

        # added stuff
        self.fname = "Boomlet.pdf"
        ini_file = "book.ini"
        if 'ini' in kwargs:
            logging.debug ("Processing new ini file = {}".format( kwargs['ini']))
            ini_file = kwargs['ini']
        self.read_ini(ini_file)
        self.build_panes()


    def read_ini(self, iniFile):
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
        self.infiles = infiles.split(",")
        self.infiles = [t.strip() for t in self.infiles]

        self.pictures = default.get("Pictures","")
        self.pictures = self.pictures.split(",")
        self.pictures = [t.strip() for t in self.pictures]

        self.pictures_fit = default.get("PicturesFit","")
        self.pictures_fit = self.pictures_fit.split(",")
        self.pictures_fit = [t.strip() for t in self.pictures_fit]

        self.title = default.get('Title', "Booklet Title")
        self.author = default.get('Author', "<< author >>")
        self.date = default.get('Date', "<< date >>")
        self.edition = default.get('Edition', "<< edition >>")
        self.book8up = "1.0" # no get

    def build_panes(self):
        # hardcoded
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

    def bold(self):
        self.set_font('Arial','B',self.pane_font_size)

    def normal(self):
        self.set_font('Arial','',self.pane_font_size)

    def process(self):
        self.add_page()
        self.set_margins(self.page_margin, self.page_margin, self.page_margin)

        jinf = 0
        jpf = 0
        jpic = 0
        for pfmt in self.pane_format:
            if pfmt == "front":
                self.gen_front(jpf)
            elif pfmt == "back":
                self.gen_back(jpf)
            elif pfmt == "recipe":
                self.gen_recipe(jpf, self.infiles[jinf])
                jinf += 1
            elif pfmt == "text":
                self.gen_text(jpf, self.infiles[jinf])
                jinf += 1
            elif pfmt == "picture":
                self.gen_picture(jpf, self.pictures[jpic], self.pictures_fit[jpic])
                jpic += 1
            else:
                logging.error ("Error unknown format {}".format(pfmt))
            jpf += 1

    def gen_picture(self, pane_index, infile, fit):
        px = self.panes[pane_index][0]
        py = self.panes[pane_index][1]
        pw = self.pane_width
        self.normal()
        #self.image(infile, px, py, pw, self.pane_height)
        if fit=="actual":
            self.image(infile, px, py)
        elif fit=="width":
            self.image(infile, px, py, pw)
        elif fit=="height":
            self.image(infile, px, py, h=self.pane_height)
        elif fit=="fit":
            self.image(infile, px, py, pw, self.pane_height)
        else:
            logging.error ("Error unknown image fit= {}".format(fit))

    def gen_text(self, pane_index, infile):
        txt = self.get_file_text(infile)
        px = self.panes[pane_index][0]
        py = self.panes[pane_index][1]
        pw = self.pane_width
        
        mch = self.pane_font_size * 1.2 * self.pt2in

        self.normal()
        self.set_xy(px, py)
        self.multi_cell(pw, mch, txt)

    def gen_recipe(self, pane_index, infile):
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

    def gen_back(self, pane_index=2):
        self.set_font('Arial','', self.back_font_size)
        mch = self.back_font_size * 1.3 * self.pt2in

        #adjust width to make narrower
        pw_adjustment = 2
        back_align = 'C'
        px = self.panes[pane_index][0] + pw_adjustment *self.pane_margin
        py = self.panes[pane_index][1] + (1*self.pane_height/2)
        pw = self.pane_width - 2*pw_adjustment *self.pane_margin #double for left&right

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


    def gen_front(self, pane_index=7, title_text=None):
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
        logging.debug("publish() booklet to file {}".format(self.fname))
        self.output(self.fname)



if __name__ == "__main__":

    logging.basicConfig(format='%(asctime)s %(message)s', 
            datefmt='%I:%M:%S', level=logging.DEBUG)


    logging.debug("Running book.py")


    logging.debug ("Creating object")
    book = Booklet(ini="book.ini")
    
    logging.debug ("Processing")
    book.process()
    
    logging.debug ("Publishing")
    book.publish()
    logging.debug ("Fini\n")
