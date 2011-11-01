import subprocess

HEADER = """
\documentclass[12pt]{article}
\usepackage[pdftex]{graphicx}
\usepackage{geometry}
\\title{Releve de compte}
\date{\\today}

\\begin{document}
"""

FOOTER = """
\\end{document}
"""

document = HEADER

def new_part(name):
    global document
    document += "\n" + "\section{%s}" % name
    
def new_section(name):
    global document
    document += "\n" + "\subsection{%s}" % name

def add_graph(fname):
    global document
    document += "\n" + "\includegraphics[width=\\textwidth]{%s}" % fname

def start_maths():
    global document
    document += "\n" + "\paragraph{Informations}:\\\\" 

def add_math(name, value):
    global document
    document += "\n" + "%s $\\rightarrow$ %s\\\\" % (name, value)

def dump():
    global document
    document += "\n" + FOOTER 
    print "Generating pdf ..."
    print document
    out, err = subprocess.Popen(["pdflatex", "-output-directory=out/"], 
                                #stdout=subprocess.PIPE, 
                                stdin=subprocess.PIPE).communicate(document)
    print "Done"
    #write document to a file