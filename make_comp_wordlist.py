#!/usr/bin/python
import time
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import re

kb = pd.read_csv('~/Downloads/KhoBwa_LeipzipJakarta - Data.csv')
kb = kb.iloc[:200,]

kbchar = kb.iloc[1::2,]#odd rows
kbword = kb.iloc[::2,]#even rows
kbchar = kbchar.fillna(0)
colnames = list(kbchar.columns.values)
abbreviations = ['dh', 'kp', 'rp', 'shg', 'rh', 'kt', 'jg', 'kn', 'dk', 'sc', 'wh', 'bc', 'kap', 'np', 'b', 'kr', 'rw', 'sr', 'sc', 'lp', 'zm', 'ld', 'tsb', 'bm', 'wt', 'pt', 'pbg', 'ph', 'pkc']
colnum = len(colnames)

def uniform ( oldchars ):
    'replace some ugly character combinations'
    newchars = re.sub('t͡ɕ', 'ʨ', oldchars)
    newchars = re.sub('t͡s', 'ʦ', newchars)
    newchars = re.sub('t͡ʃ', 'ʧ', newchars)
    newchars = re.sub('d͡ʑ', 'ʥ', newchars)
    newchars = re.sub('d͡ʒ', 'ʤ', newchars)
    newchars = re.sub('d͡z', 'ʣ', newchars)
    newchars = re.sub('tʃ', 'ʧ', newchars)
    newchars = re.sub('tɕ', 'ʨ', newchars)
    newchars = re.sub('ts', 'ʦ', newchars)
    newchars = re.sub('dʒ', 'ʤ', newchars)
    newchars = re.sub('dʑ', 'ʥ', newchars)
    newchars = re.sub('dz', 'ʣ', newchars)
    newchars = re.sub('ɴ', 'N', newchars)
    newchars = re.sub('nan', 'NA', newchars)
    newchars = re.sub('⪤', '\\\\af ', newchars)
    newchars = re.sub('~', '\\wave ', newchars)
    newchars = re.sub('\-\) ', '-)', newchars)
    return newchars




out = open("../data/wordlistcolumns.tex",'w', encoding="utf-8")
out.write('%!TEX root = ../main.tex\n')
out.write("[Word list created on: " + time.strftime("%c") + "]\\\\\n")
out.write('\\footnotesize\n')
out.write('\\begin{multicols}{3}\n')
out.write('\\noindent')
for wordrow, charrow in zip(kbword.values,kbchar.values):
         wordlists = charrow[0]
         if wordlists == 'L':
             wl = 'LJ'
         elif wordlists == 'S':
             wl = 'S100'
         elif wordlists == 'LS' or wordlists == 'SL':
             wl = 'LJ, S100'
         else:
             wl = 'NA'
         word = wordrow[1].strip()
         out.write('\\textbf{\\textsc{' + word + '}}\\hfill [' + wl + ']\\\\\n')
         for word, character, abbr in zip(wordrow[2::], charrow[2::], abbreviations):
            out.write("\\enskip\\textbf{"+abbr+"}\\tabto{0.5cm}")
            out.write("\\colorbox{rb")
            if character != 0 and word != 'NA' and character != ' ':
                out.write(str(character))
            else:
                out.write('0')
            out.write('}{\\begin{minipage}{3cm}')
            out.write(uniform(str(word)))
            out.write("\\end{minipage}}")
            if character is not 0:
                out.write("\\tabto{4cm}("+ str(character) + ")")
            out.write("\\\\\n")    
         out.write('\\\\\n')
out.write('\\end{multicols}\n')        
out.close()

#no warranty that the rest works

out = open("../data/wordlisttable.tex",'w', encoding="utf-8")
#out.write(kbchar.to_latex(longtable=True))
out.write('%!TEX root = ../khobwa.tex\n')
out.write("Word list created on: " + time.strftime("%c") + "\\\\\n")
out.write('\\newgeometry{margin=0.3cm}\n')
out.write('\\begin{landscape}\n')
out.write('\\thispagestyle{empty}\n')
out.write('\\tiny\n')
out.write('\\begin{longtable}{' + 'p{0.525cm}'*(colnum-1) + 'p{1.2cm}' + '}\n')
out.write('\\toprule\n')
for language in colnames:
    out.write('&' + language)
out.write('\\\\\\endhead\n')
for language in colnames:
    out.write('&' + language)
out.write('\\\\\\endfoot\n')
out.write('\\midrule\n')
for wordrow, charrow in zip(kbword.values,kbchar.values):     
         for word, character in zip(wordrow,charrow):
            if character == 'cognacy':
                out.write('\\textsc{' + word + '}')
            else:
                out.write("&\\cellcolor{rb"+ str(character) + '}{' + uniform(str(word)) + " ")
                if character is not 0:
                      out.write("\\textsuperscript{(" + str(character) + ")}")
                out.write('}')
         out.write('\\\\\n')
out.write('\\bottomrule\n')
out.write('\\end{longtable}\n')
out.write('\\end{landscape}')
out.write('\\restoregeometry')
out.close()

out = open("../data/wordlisttable2.tex",'w', encoding="utf-8")
#out.write(kbchar.to_latex(longtable=True))
out.write('%!TEX root = ../khobwa.tex\n')
out.write("Word list created on: " + time.strftime("%c") + "\\\\\n")
out.write('\\newgeometry{margin=0.3cm}\n')
out.write('\\begin{landscape}\n')
out.write('\\thispagestyle{empty}\n')
out.write('\\tiny\n')
out.write('\\begin{longtable}{' + 'p{0.525cm}'*(colnum-1) + 'p{1.2cm}' + '}\n')
out.write('\\toprule\n')
for language in colnames:
    out.write('&' + language)
out.write('\\\\\\endhead\n')
for language in colnames:
    out.write('&' + language)
out.write('\\\\\\endfoot\n')
out.write('\\midrule\n')
for wordrow, charrow in zip(kbword.values,kbchar.values):     
         for word, character in zip(wordrow,charrow):
            if character == 'cognacy':
                out.write('\\textsc{' + word + '}')
            else:
                out.write("&\\cellcolor{rb"+ str(character) + '}{' + uniform(str(word)) + " ")
                out.write('}')
         out.write('\\\\\n')
         for character in charrow:
             if character == 'cognacy':
                out.write('cognacy')
             else:
                out.write("&(" + str(character) + ")")
         out.write("\\\\\n")
out.write('\\bottomrule\n')
out.write('\\end{longtable}\n')
out.write('\\end{landscape}')
out.write('\\restoregeometry')
out.close()


out = open("../data/wordlistlist.tex",'w', encoding="utf-8")
out.write('%!TEX root = ../khobwa.tex\n')
out.write("Word list created on: " + time.strftime("%c") + "\\\\\n")
out.write('\\footnotesize\n')
for wordrow, charrow in zip(kbword.values,kbchar.values):     
         for word, character, abbr in zip(wordrow,charrow,abbreviations):
            if character == 'cognacy':
                out.write('\\textbf{\\textsc{' + word + '}}\n')
            else:
                out.write("\\colorbox{rb"+ str(character) + '}{')
                out.write(uniform(str(word)))
                if character is 0:
                    out.write("\\textsubscript{" + abbr + "}")
                else:
                    out.write("\\textsubscript{" + abbr +"("+ str(character) + ")}")
                out.write("} ")
         out.write('\\\\\n')
out.close()
