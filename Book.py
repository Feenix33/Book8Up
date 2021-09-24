import sys
import os
from fpdf import FPDF
import csv
from datetime import date, timedelta, datetime
import configparser
from dateutil.parser import parse
import logging
import argparse
import calendar
from pprint import pprint
#import re

'''
ToDo
. monthly with space and grid boxes
. consistencies with start of week
. third ini parameter for subtype (week, month)
. can the ini parameter call the right process routine?
. multiple page text
. subroutine for calendar title block
. consistent drawing w/a current pane y parameter
. subroutine to get the font size
. subroutine to get font size that fits
. Habit Tracker
. habit tracker page: monthly 1/2
. every day in a week w groups of x
. Lines
. with lines
. with grid
. with dots
. with offset dots
'''

class Booklet(FPDF):
    def __init__(self, *args, **kwargs):
        super(Booklet, self).__init__('L', 'in','Letter')
        self.config = configparser.ConfigParser()

        # added stuff
        #ini_file = "book.ini"
        if 'ini' in kwargs:
            logging.warning ("Processing ini file: {}".format( kwargs['ini']))
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
        self.font = "Helvetica"
        #self.font = "Arial"
        self.back_font_size = default.getint('BackFontSize', 6)
        self.title_font_size = default.getint('TitleFontSize', 14)
        self.author_font_size = default.getint('AuthorFontSize', 10)
        self.title_position = default.getint('TitlePosition', 40)
        self.pane_use_width = default.getfloat('PaneUseWidth', 0.80)
        self.max_font_size = 25
        self.pt2in = 0.0138889
        self.title_frame = default.getboolean('TitleFrame', True)
        self.back_frame = default.getboolean('BackFrame', True)
        self.out_fname = default.get('OutputFile', "Boomlet.pdf")

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

        default_fit = default.get("PicturesFitDefault","width")
        self.pictures_fit = [default_fit]*len(self.pictures)
        pictures_fit = default.get("PicturesFit","")
        pictures_fit = pictures_fit.split(",")
        if len(pictures_fit) == len(self.pictures_fit):
            self.pictures_fit = [t.strip() for t in pictures_fit]

        self.title = default.get('Title', "Booklet Title")
        self.author = default.get('Author', "<< author >>")
        self.date = default.get('Date', "<< date >>")
        self.edition = default.get('Edition', "<< edition >>")
        self.book8up = "2.0" # no get

        self.infile_text = []
        for j in range(8):
            txt = default.get('Infile'+str(j+1), "")
            if len(txt) > 0:
                self.infile_text.append (txt)

        self.commands = []
        for j in range(8):
            txt = default.get('Command'+str(j+1), "")
            if len(txt) > 0:
                self.commands.append (txt)

        self.indata = [None]*8
        for j in range(8):
            txt = default.get('P'+str(j+1)+'Input', "")
            if len(txt) > 0:
                self.indata[j] = txt


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
        self.set_font(self.font,'B',self.pane_font_size)

    def normal(self):
        self.set_font(self.font,'',self.pane_font_size)

    def process(self):
        def process_blank(pane):
            pass
        def process_textfile(pane_id):
            txt = self.get_file_text(self.indata[pane_id])
            self.gen_text_pane(pane_id, txt, title=False)
        def process_textin(pane_id):
            txt = self.indata[pane_id]
            self.gen_text_pane(pane_id, txt, title=False)
        def process_chapter(pane_id):
            txt = self.get_file_text(self.indata[pane_id])
            self.gen_text_pane(pane_id, txt, title=True)
        def process_chapterin(pane_id):
            txt = self.indata[pane_id]
            self.gen_text_pane(pane_id, txt, title=True)
        def process_recipe(pane_id):
            process_chapterin(pane_id)
        def process_recipein(pane_id):
            process_chapterin(pane_id)
        def process_picture(pane_id):
            self.gen_picture(jpf, self.indata[pane_id], fit='actual')
        def process_picwidth(pane_id):
            self.gen_picture(jpf, self.indata[pane_id], fit='width')
        def process_picheight(pane_id):
            self.gen_picture(jpf, self.indata[pane_id], fit='height')
        def process_picfit(pane_id):
            self.gen_picture(jpf, self.indata[pane_id], fit='fit')
        def process_calyear(pane_id):
            self.gen_calendar(pane_id)
        def process_command(pane_id):
            txt = self.get_file_text(self.indata[pane_id])
            self.gen_command(pane_index, txt)
        def process_commandin(pane_id):
            self.gen_command(pane_index, self.indata[pane_id])
        def process_checklist(pane_id):
            logging.warning("Checklist {} with format {}".format(pane_index, self.indata[pane_id]))
            self.gen_checklist(pane_index, self.indata[pane_id])
        def process_weekly(pane_id):
            logging.warning("weekly {} with format {}".format(pane_index, self.indata[pane_id]))
            self.gen_weekly(pane_index, self.indata[pane_id])
        def process_week2(pane_id):
            logging.warning("week2 {} with format {}".format(pane_index, self.indata[pane_id]))
            self.gen_week2(pane_index, self.indata[pane_id])
        def process_month(pane_id):
            logging.warning("month {} with format {}".format(pane_index, self.indata[pane_id]))
            self.gen_month(pane_index, self.indata[pane_id])

        self.add_page()
        self.set_margins(self.page_margin, self.page_margin, self.page_margin)

        pane_processors = {
            'front' : self.gen_front,
            'back' : self.gen_back,
            'blank' : process_blank,
            'textfile' : process_textfile,
            'textin' : process_textin,
            'chapter' : process_chapter,
            'chapterin' : process_chapterin,
            'recipe' : process_recipe,
            'recipein' : process_recipein,
            'picture' : process_picture,
            'picwidth' : process_picwidth,
            'picheight' : process_picheight,
            'picfit' : process_picfit,
            'calyear' : process_calyear,
            'command' : process_command,
            'commandin' : process_commandin,
            'checklist' : process_checklist,
            'weekly' : process_weekly,
            'week2' : process_week2,
            'month' : process_month,
        }
        pane_index = 0
        for pfmt in self.pane_format:
            #logging.warning("Processing {} with format {}".format(pane_index, pfmt))
            func = pane_processors.get(pfmt)
            func(pane_index)
            pane_index += 1

    def gen_checklist(self, pane_index, title=""):
        self.pane_frame(pane_index)

        px = self.panes[pane_index][0]
        py = self.panes[pane_index][1]
        pw = self.pane_width
        ph = self.pane_height
        cellh = ph / 12
        cellhm = cellh/2
        y = cellhm + 2*cellh
        boxsz = cellh * 0.8
        xm = pw*0.05
        x = px + xm
        xe = px+pw-xm
        def abox(x, y, dim):
            dim2 = dim/2
            self.line (x, y-dim2, x+dim, y-dim2)
            self.line (x, y+dim2, x+dim, y+dim2)
            self.line (x+dim, y-dim2, x+dim, y+dim2)
            self.line (x, y-dim2, x, y+dim2)
        while y < ph:
            #self.line(px+pw*0.1, y, px+pw*0.9, y) 
            abox(x, y, boxsz)
            self.line(x+boxsz+xm, y+boxsz/2, xe, y+boxsz/2) 
            y += cellh
        # title
        font_size = min(int(cellh / self.pt2in), self.max_font_size)
        textwidth = 99
        while textwidth > pw:
            self.set_font(self.font,'',font_size)
            textwidth = self.get_string_width(title)
            font_size -= 1
        self.set_xy(px, py+cellhm)
        self.cell(w=pw, txt=title, border=0, align='C')

    def gen_month(self, pane_index, date_str):
        px = self.panes[pane_index][0]
        py = self.panes[pane_index][1]
        pw = self.pane_width
        ph = self.pane_height

        cellw = pw / 7  #cells, one for each day
        cellh = cellw #square cells
        cellm = cellh * 0.1 #cell margin

        #get the month
        if date_str == 'today':
            today = date.today() #datetime.now()
        else:
            today = parse(date_str)
        month_name = today.strftime("%B")
        year_name = today.year

        #write the month year as the title
        title = month_name + ' ' + str(year_name)
        font_size = min(int(cellh / self.pt2in), self.max_font_size)
        textwidth = 99
        while textwidth > pw*0.8:
            self.set_font(self.font,'',font_size)
            textwidth = self.get_string_width(title)
            font_size -= 1
        self.set_xy(px, py+cellh*0.2)
        self.cell(w=pw, txt=title, border=0, align='C')

        #write the days of the week
        #for now mon is first column and weekday=0
        start_day = parse(month_name + " 1, " + str(year_name))
        num_days = calendar.monthrange(today.year, today.month)[1]

        font_size = min(int(cellh*0.8 / self.pt2in), self.max_font_size)
        cy = py + cellh + cellm
        cx = px + cellw * start_day.weekday()
        for daynum in range(num_days):
            self.set_xy(cx, cy)
            self.cell(w=cellw, txt=str(daynum+1), border=0, align='C')
            cx += cellw
            if cx >= px + pw:
                cx = px
                cy += cellh


    def gen_week2(self, pane_index, date_str):
        self.gen_weekly_base(pane_index, date_str, form=2)

    def gen_weekly(self, pane_index, date_str):
        self.gen_weekly_base(pane_index, date_str, form=1)

    def gen_weekly_base(self, pane_index, date_str, form=1):
        px = self.panes[pane_index][0]
        py = self.panes[pane_index][1]
        pw = self.pane_width
        ph = self.pane_height

        day1, daylist = self.str2date_list(date_str)
        month_name = day1.strftime("%B")
        year_name = day1.year

        cellh = ph / 7  # 7 cells = title, M-F, S+S one line
        cellm = cellh*0.1 #cell margin
        cellw = pw - cellm*2
        cellw2 = cellh
        cellx = px

        # draw the lines for each day
        y = py
        while y <= py+ph:
            self.line(px, y, px+pw, y)
            y+= (ph/7)
        self.line(px+pw/2, py+ph-cellh, px+pw/2, py+ph)
        self.line(px, py, px, py+ph)
        self.line(px+pw, py, px+pw, py+ph)

        # write the days
        if form==1: day_fontsize = int(0.5 * cellh / self.pt2in)
        else: day_fontsize = int(0.2 * cellh / self.pt2in)
        self.set_font(self.font,'', day_fontsize)
        y = py+cellh + cellm
        x = cellx #+ cellm
        for n in daylist[:-1]:
            self.set_xy(x, y)
            self.cell(w=cellw2, txt=str(n), align='C', border=0)
            y += cellh
        x = cellx + pw/2
        self.set_x(x)
        self.cell(w=cellw2, txt=str(daylist[6]), align='C', border=0)

        # write the days of the week
        if form==1:
            dow = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
            dow_fontsz = int(0.3 * cellh / self.pt2in)
            y = py+ (cellh* 1.65)
            x = cellx #+ cellm
        else:
            dow = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sun']
            dow_fontsz = int(0.2 * cellh / self.pt2in)
            y = py+cellh + cellm
            x = cellx + cellw - cellh

        self.set_font(self.font,'', dow_fontsz)

        for day in dow:
            self.set_xy(x, y)
            self.cell(w=cellw2, txt=day, align='C', border=0)
            y += cellh
        if form==1: x = cellx + pw/2
        else: x = cellx + pw/2 - cellh
        self.set_x(x)
        if form==1: self.cell(w=cellw2, txt='Sun', align='C', border=0)
        else: self.cell(w=cellw2, txt='Sat', align='C', border=0)

        # write the title
        title = calendar.month_name[day1.month] + ' ' + str(day1.year)
        font_size = min(int(cellh / self.pt2in), self.max_font_size)
        textwidth = 99
        while textwidth > pw*0.8:
            self.set_font(self.font,'',font_size)
            textwidth = self.get_string_width(title)
            font_size -= 1
        self.set_xy(px, py+cellh*0.2)
        self.cell(w=pw, txt=title, border=0, align='C')

    def str2date_list(self, date_str):
        #take a string date in and convert to a list of the next seven day values
        #start date is the most recent monday
        #return the start date and a list of the week
        if date_str == "today":
            today = date.today() #datetime.now()
        else:
            today = parse(date_str)

        start = today - timedelta(days=today.weekday())

        daylist = [start.day]
        for add in range(1, 7):
            daylist.append ((start+timedelta(days=add)).day)

        return start, daylist

    def gen_calendar(self, pane_index):
        txt = calendar.calendar(2021,w=1,c=1,m=2)
        font_size = 5
        font = 'Courier'
        self.set_font(font,'',font_size)
        px = self.panes[pane_index][0]
        py = self.panes[pane_index][1]
        pw = self.pane_width
        mch = font_size * 0.9 * self.pt2in
        self.set_xy(px, py)
        self.multi_cell(pw, mch, txt, align='L')
        self.normal()


    def gen_command(self, pane_index, cmds_in):
        '''
         box 10 20 50 dim x y
         color 255 0 0
        '''
        xp = lambda x: px + (x*pw/100.)
        yp = lambda y: py + (y*ph/100.)
        def cmd_frame(stack):
            logging.debug("frame command")
            self.line (px, py, px+pw, py)
            self.line (px, py+ph, px+pw, py+ph)
            self.line (px, py, px, py+ph)
            self.line (px+pw, py, px+pw, py+ph)

        def cmd_horzs(stack):
            # s1 number of horizontal lines
            # s2 if present then put a line at the top
            logging.debug("horzs command: {}".format(stack))
            number = int(stack.pop(0))
            delta_y = 100/number
            if stack: # assume second variable is true, TODO test later? 
                y = 0
                number += 1
            else: 
                y = delta_y
            for n in range(number):
                self.line(xp(0), yp(y), xp(100), yp(y))
                y += delta_y

        def cmd_verts(stack):
            logging.debug("verts command {}".format(stack))
            number = int(stack.pop(0))
            delta_x = 100/number
            if stack: # assume second variable is true, TODO test later? 
                x = 0
                number += 1
            else:
                x = delta_x
            for n in range(number):
                self.line(xp(x), yp(0), xp(x), yp(100))
                x += delta_x

        def cmd_rect(stack):
            logging.debug("rect command")
            x1, y1, x2, y2 = map(int, stack)
            self.rect ( xp(x1), yp(y1), xp(x2)-xp(x1), yp(y2)-yp(y1))

        def cmd_box(stack):
            aspect = ph / pw
            logging.debug("box command aspect {}".format(aspect))
            x1, y1, dim = map(int, stack)
            self.rect (xp(x1), yp(y1), (dim*pw/100.), (dim / aspect *ph/100.))

        def cmd_grid(stack):
            # 0 % witdh across
            # 1 number of grid buffer
            logging.debug("grid command {}".format(stack))
            dim = int(stack[0]) * pw / 100.
            margin = int(stack[1]) if 1 < len(stack)  else 0
            nx = int(pw/dim) - 2 *margin #number of lines so no spill
            ny = int(ph/dim) - 2 *margin
            width = nx*dim
            height = ny*dim
            xoff = (pw-width) / 2
            yoff = (ph-height) / 2
            logging.debug("     grid x y   {} {}".format(nx, ny))
            logging.debug("     grid margin {}".format(margin))
            #for n in range(margin, nx+1-margin):
            for n in range(nx+1):
                self.line(n*dim+xoff, yoff, n*dim+xoff, height+yoff)
            for n in range(ny+1):
                self.line(xoff, n*dim+yoff, width+xoff, n*dim+yoff)

        def cmd_color(stack):
            self.set_draw_color(int(stack[0]), int(stack[1]), int(stack[2]))


        processor = {
                'frame' : cmd_frame,
                'horzs' : cmd_horzs,
                'verts' : cmd_verts,
                'box': cmd_box,
                'color' : cmd_color,
                'rect' : cmd_rect,
                'grid' : cmd_grid,
                }

        px = self.panes[pane_index][0]
        py = self.panes[pane_index][1]
        pw = self.pane_width
        ph = self.pane_height
        logging.debug ("Processing commands on {}".format (pane_index))
        cmds = cmds_in.splitlines()
        for cmd in cmds:
            tokens = cmd.split()
            if tokens[0][0] == '#': continue
            func = processor.get(tokens[0])
            func(tokens[1:])
                


    def gen_picture(self, pane_index, infile, fit="actual"):
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


    def gen_text_pane(self, pane_index, txt, title=False):
        '''
        Text is passed in
        title=true look for the first CR and bold then rest is normal
        '''
        px = self.panes[pane_index][0]
        py = self.panes[pane_index][1]
        pw = self.pane_width
        mch = self.pane_font_size * 1.1 * self.pt2in

        j = -1
        if title:
            j = txt.find('\n')
            self.set_xy(px, py)
            self.bold()
            self.multi_cell(pw, (mch*1.2), txt[:j], align='C')
            py = self.get_y()
        self.normal()
        self.set_xy(px, py)
        self.multi_cell(pw, mch, txt[(j+1):], align='L')

    def gen_back(self, pane_index):
        #self.set_font('Arial','', self.back_font_size)
        self.set_font(self.font, '', self.back_font_size)
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

        #now = datetime.datetime.now().strftime("%d %B %Y")
        now = datetime.now().strftime("%d %B %Y")
        self.set_x(px)
        txt = "Created on {}".format(now)
        self.multi_cell(pw, mch, txt, align=back_align, border=0)

        if self.book8up:
            self.set_x(px)
            txt = "using book8up.py Ver {}".format(self.book8up)
            self.multi_cell(pw, mch, txt, align=back_align, border=0)

        if self.back_frame: self.pane_frame(pane_index)


    def gen_front(self, pane_index):
        txt = self.title or "Missing Title"

        pane_mar = (1.0 - self.pane_use_width)/2
        pw = self.pane_width * self.pane_use_width

        #self.set_font('Arial','B', self.title_font_size)
        self.set_font(self.font, 'B', self.title_font_size)
        mch = self.title_font_size * 1.3 * self.pt2in

        sw = self.get_string_width(txt)
        px = self.panes[pane_index][0] + (self.pane_width * pane_mar)
        py = self.panes[pane_index][1] + (self.pane_height*self.title_position/100.0) - mch * (int(sw/pw)+1)
        #xxxx

        self.set_xy(px, py)


        self.multi_cell(pw, mch, txt, align='C', border=0)
        sw = self.get_string_width(txt)

        #self.set_font('Arial','', self.author_font_size)
        self.set_font(self.font, '', self.author_font_size)
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
        logging.warning("publish() booklet to file {}".format(self.out_fname))
        self.output(self.out_fname)



if __name__ == "__main__":

    logging.basicConfig(format='%(asctime)s %(message)s', 
            datefmt='%I:%M:%S', level=logging.WARNING)
    parser = argparse.ArgumentParser()
    parser.add_argument("defn_file", nargs='?', default='book.ini', help="Booklet definition file")
    args = parser.parse_args()

    book = Booklet(ini=args.defn_file)
    book.process()
    book.publish()
