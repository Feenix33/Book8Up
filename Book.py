import sys
import os
from fpdf import FPDF
import csv
"""
01 Basics, page in in
02 Switch to multi_cell, page in mm
03 Play w/the multi cell height and width, page in pt
04 Try layout
05 Set hardcoded panes try with inches
06 Add text from files
07 Generate 8pg booklet. First version
08 Recipe titles
09 Convert to a class
10 Adding control file
"""

# margins all in inches
#marPage = 0.25
#marPane = 0.2

#crayons = [(0,0,0),(255,0,0),(0,255,0),(0,0,255),(255,0,255),(255,255,0),(0,255,255),(128,128,128)]

class Booklet(FPDF):
    def __init__(self, *args, **kwargs):
        super(Booklet, self).__init__(*args, **kwargs)
        print ("Created")

    def build_panes(self, page_margin, pane_margin):
        # hardcoded
        print ("Building panes")
        self.page_margin = page_margin
        self.pane_margin = pane_margin
        paneW = (11 - 2*page_margin - 3*pane_margin)/4
        paneH = (8.5 - 2*page_margin - pane_margin)/2
        self.panes = []
        for h  in range (1,3):
            for w in range (1,5):
                x1 = page_margin + (w-1)*(paneW + pane_margin)
                y1 = page_margin + (h-1)*(paneH + pane_margin)
                x2 = x1 + paneW
                y2 = y1 + paneH
                self.panes.append([x1, y1, x2, y2])
        #for pane in self.panes:
        #    print (pane)

    def bold(self):
        self.set_font('Arial','B',7)
    def normal(self):
        self.set_font('Arial','',7)

    def process_definition(self, fname):
        with open(fname) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                print(f'\t{row[0]} {row[1]}.')
                line_count += 1
            print(f'processed {line_count} lines.')




    def process(self, fname, define_file):
        marPage = 0.25
        marPane = 0.2
        print ("Processing " + define_file)

        self.process_definition(define_file)

        #define = self.get_file_text(define_file)
        #print (define)
        self.fname = fname
        self.add_page()
        self.set_margins(marPage, marPage, marPage)
        #self.print_pane(0, "rWonderpot.txt")
        #self.print_pane(1, "rLentils.txt")
        #self.print_title(2, "rTitle.txt")

    def print_pane(self, pane_index, infile):
        txt = self.get_file_text(infile)
        px = self.panes[pane_index][0]
        py = self.panes[pane_index][1]
        pw = self.panes[pane_index][2] - self.panes[pane_index][0]
        
        j = txt.find('\n')
        self.set_xy(px, py)
        self.bold()
        self.multi_cell(pw, 0.15, txt[:j], align='C')
        self.set_x(px)
        self.normal()
        self.multi_cell(pw, 0.1, txt[(j+1):])


    def print_title(self, pane_index, infile):
        txt = self.get_file_text(infile)
        px = self.panes[pane_index][0]
        py = self.panes[pane_index][1]
        pw = self.panes[pane_index][2] - self.panes[pane_index][0]
        self.set_font('Arial','B',12)
        self.set_xy(px, py)
        txt = "\n\n" + txt
        self.multi_cell(pw, 0.3, txt, align='C')

    def get_file_text(self, infile):
        # convert to a try catch eventually for file does not exist cases
        with open(infile, 'r') as fh:
            txt = fh.read()
        fh.close ()
        return txt

    def publish(self):
        print("writing booklet to file {}".format(self.fname))
        self.output(self.fname)




if __name__ == "__main__":

    book = Booklet('L', 'in','Letter')
    book.build_panes(page_margin = 0.25, pane_margin=0.2)
    book.process("Boomlet.pdf", "DaddyO.txt")
    book.publish()
