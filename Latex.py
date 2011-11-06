import subprocess

HEADER = """
\documentclass[12pt]{article}
\usepackage[pdftex]{graphicx}
\usepackage{geometry}
\\title{Releve de compte}
\date{\\today}
\\usepackage{multicol}
\\usepackage{eurosym}
\\begin{document}
\\maketitle
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

def new_subsection(name):
    global document
    document += "\n" + "\subsubsection{%s}" % name
    
def add_graph(fname):
    global document
    document += "\n" + "\includegraphics[width=\\textwidth]{%s}" % fname

maths = None
mathsList = None
def start_maths():
    global document, maths, mathsList
    maths = {}
    mathsList = []

def add_maths(name, values):
    global maths
    maths[name] = values
    mathsList.append(name)
    
def stop_maths():
    global document, maths, mathsList
    keys = maths.values()[0].keys()
    document += "\n" + "\\begin{center}"
    document += "\n" + "\\begin{tabular}{ l %s}" % (" | l "*len(keys))
    
    document += "&" + " & ".join(keys) + "\\\\"
    document += "\n" + "\\hline\n"
    first = True
    for name in mathsList:
        document += name + " &" + " & ".join([u"%.0f\euro" % maths[name][key] for key in keys]) + "\\\\\n"
        document += "\n" 
        if first:
            first = False
            document += "\n\\hline\n" 
    document += "\n" + "\\end{tabular}"
    document += "\n" + "\\end{center}"
    maths = None
    
def dump():
    global document
    document += "\n" + FOOTER 
    print "Generating pdf ..."
    #print document
    out, err = subprocess.Popen(["pdflatex", "-output-directory=out/"], 
                                stdout=subprocess.PIPE, 
                                stdin=subprocess.PIPE).communicate(document)
    print "Done"