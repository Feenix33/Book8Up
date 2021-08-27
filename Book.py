import sys
import os
from fpdf import FPDF
import csv
import datetime
import configparser
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
        self.element = { # elements in the book
                'title' : "Booklet",
                'author' : '',
                'date' : 'August 1, 2021',
                'edition' : "1.0",
                'book8up' : '1.0',
                '0': '', '1': '', '2': '', '3': '', '4': '', '5': '',
                }
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
        self.config = configparser.ConfigParser()
        self.config.read(iniFile)
        default = self.config['Default']
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

    def load_definition(self, fname):
        with open(fname) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            self.defn = {}
            for row in csv_reader:
            #    print(f'\t{row[0]} {row[1]}.')
                line_count += 1
                self.defn[row[0].lower()] = row[1]
                #if self.element.has_key(row[0]).lower():
                if row[0].lower() in self.element:
                    self.element[row[0].lower()] = row[1]
                else:
                    print ("Foreign key ", row[0].lower(), " ignored")
            
            """
            print ('\n')
            print ("="*50)
            print (self.load_definition.__name__)
            for key, value in self.element.items():
                print (key, " : ", value)
            print ("="*50)
            """



    def process(self, define_file):
        marPage = 0.25
        marPane = 0.2
        print ("process() init with " + define_file)

        self.load_definition(define_file)

        #define = self.get_file_text(define_file)
        #print (define)
        self.add_page()
        self.set_margins(marPage, marPage, marPage)
        self.print_pane(0, self.element['0'])
        self.print_pane(1, self.element['1'])
        self.print_pane(2, self.element['2'])
        self.print_pane(3, self.element['3'])
        self.print_back(pane_index=4)
        self.print_title(5)
        self.print_pane(6, self.element['4'])
        self.print_pane(7, self.element['5'])

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
        txt = self.element['title']
        self.multi_cell(pw, mch, txt, align=back_align, border=0)

        if self.element['author']:
            self.set_x(px)
            txt = "by {}".format(self.element['author'])
            self.multi_cell(pw, mch, txt, align=back_align, border=0)

        if self.element['edition']:
            self.set_x(px)
            txt = "{} Edition".format(self.element['edition'])
            self.multi_cell(pw, mch, txt, align=back_align, border=0)

        #if self.element['date']:
        now = datetime.datetime.now().strftime("%d %B %Y")
        self.set_x(px)
        txt = "Created on {}".format(now)
        self.multi_cell(pw, mch, txt, align=back_align, border=0)

        if self.element['book8up']:
            self.set_x(px)
            txt = "using book8up.py Ver {}".format(self.element['book8up'])
            self.multi_cell(pw, mch, txt, align=back_align, border=0)

        if self.back_frame: self.pane_frame(pane_index)



    def print_title(self, pane_index=7, title_text=None):
        txt = title_text or self.element['title']

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
        txt = self.element['author']
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
    book.process("DaddyO.txt")
    book.publish()
