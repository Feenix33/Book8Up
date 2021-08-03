import sys
import os
from fpdf import FPDF
import csv
import datetime

# margins all in inches
#marPage = 0.25
#marPane = 0.2

class Booklet(FPDF):
    def __init__(self, *args, **kwargs):
        super(Booklet, self).__init__(*args, **kwargs)
        self.element = { # elements in the book
                'title' : "Booklet",
                'author' : '',
                'date' : 'August 1, 2021',
                'edition' : "1.0",
                'book8up' : '1.0',
                '0': '', '1': '', '2': '', '3': '', '4': '', '5': '',
                }
        print ("init() exec")

    def build_panes(self, page_margin, pane_margin):
        # hardcoded
        print ("building_panes() init")
        self.page_margin = page_margin
        self.pane_margin = pane_margin
        paneW = (11 - 2*page_margin - 3*pane_margin)/4
        paneH = (8.5 - 2*page_margin - pane_margin)/2
        self.pane_width = (11 - 2*page_margin - 3*pane_margin)/4
        self.pane_height = (8.5 - 2*page_margin - pane_margin)/2
        self.panes = []
        for h  in range (1,3):
            for w in range (1,5):
                x1 = page_margin + (w-1)*(self.pane_width + pane_margin)
                y1 = page_margin + (h-1)*(self.pane_height + pane_margin)
                x2 = x1 + self.pane_width
                y2 = y1 + self.pane_height
                #self.panes.append([x1, y1, x2, y2])
                self.panes.append([x1, y1])
        j=0
        for pane in self.panes:
            print ("{} {:.2f} {:.2f}".format(j, pane[0], pane[1]))
            j+=1

    def bold(self):
        self.set_font('Arial','B',7)
    def normal(self):
        self.set_font('Arial','',7)

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
            """
            print (self.load_definition.__name__)
            for key, value in self.element.items():
                print (key, " : ", value)
            print ("="*50)




    def process(self, fname, define_file):
        marPage = 0.25
        marPane = 0.2
        print ("process() init with " + define_file)

        self.load_definition(define_file)

        #define = self.get_file_text(define_file)
        #print (define)
        self.fname = fname
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
        print ("print_pane({})".format(infile))
        txt = self.get_file_text(infile)
        px = self.panes[pane_index][0]
        py = self.panes[pane_index][1]
        #pw = self.panes[pane_index][2] - self.panes[pane_index][0]
        pw = self.pane_width
        
        j = txt.find('\n')
        self.set_xy(px, py)
        self.bold()
        self.multi_cell(pw, 0.15, txt[:j], align='C')
        self.set_x(px)
        self.normal()
        self.multi_cell(pw, 0.1, txt[(j+1):])

    def print_back(self, pane_index=2):
        print("print_back() on pane {}".format(pane_index))
        self.set_font('Arial','',6)
        pt2in = 0.0138889
        mch = 6 * 1.3 * pt2in

        #adjust width to make narrower
        pw_adjustment = 2
        back_align = 'C'
        px = self.panes[pane_index][0] + pw_adjustment *self.pane_margin
        py = self.panes[pane_index][1] + (1*self.pane_height/2)
        pw = self.pane_width - 2*pw_adjustment *self.pane_margin #double for left&right
        print("\tpx={:.2f} py={:.2f} pw={:.2f}".format(px, py, pw))

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

        self.pane_frame(pane_index)



    def print_title(self, pane_index=7, title_text=None):
        txt = title_text or self.element['title']

        pane_use = 0.8
        pane_mar = (1.0 - pane_use)/2
        pw = self.pane_width * pane_use

        title_size = 14 #points
        self.set_font('Arial','B',title_size)
        pt2in = 0.0138889
        mch = title_size * 1.3 * pt2in

        sw = self.get_string_width(txt)
        px = self.panes[pane_index][0] + (self.pane_width * pane_mar)
        py = self.panes[pane_index][1] + (self.pane_height/2) - mch * (int(sw/pw)+1)

        self.set_xy(px, py)


        self.multi_cell(pw, mch, txt, align='C', border=0)
        sw = self.get_string_width(txt)
        #print ("print_title() width={:.2f} for [{}] panelw={:.2f} with x={:.2f}->{:.2f} y={:.2f}->{:.2f} h={:.3f}". \
        #        format(sw, txt, pw, px, self.get_x(), py, self.get_y(), mch))
        #print ("print_title() of {}".format(txt))
        #print ("\tx= {:.2f} to {:.2f} delta {:.2f}".format(px,self.get_x(),self.get_x()-px))
        #print ("\ty= {:.2f} to {:.2f} delta {:.2f}".format(py,self.get_y(),self.get_y()-py))
        #print ("\tcomputed w={:.3f} h={:.3f}".format(sw, mch))
        #print ("\n")

        self.set_font('Arial','',10)
        self.set_x(px)
        self.multi_cell(pw, mch, "\n", align='C', border=0)
        txt = self.element['author']
        self.set_x(px)
        self.multi_cell(pw, mch, txt, align='C', border=0)
        #print ("Fini title")

        self.pane_frame(pane_index)


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

    book = Booklet('L', 'in','Letter')
    book.build_panes(page_margin = 0.25, pane_margin=0.2)
    book.process("Boomlet.pdf", "DaddyO.txt")
    book.publish()
