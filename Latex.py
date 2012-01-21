import subprocess
from collections import OrderedDict

import Bank

HEADER = """
\documentclass[12pt]{article}
\usepackage[pdftex]{graphicx}
\usepackage[top=0.4in, bottom=0.5in,left=0.5in, landscape]{geometry}
\\title{Releve de compte}
\date{\\today}
\\usepackage{pdflscape}
\\usepackage{multicol}
\\usepackage{eurosym}
\\begin{document}
\\maketitle
"""

FOOTER = """
\\end{document}
"""

document = HEADER
first_sec = True
def new_part(name):
    global document, first_sec
    first_sec = False
    document += "\n" + "\\newpage"
    document += "\n" + "\part{%s}" % name
    
def new_section(name):
    global document, first_sec
    first_subsec = True
    if first_sec:
        first_sec = False
    else:
        document += "\n" + "\\newpage"
    document += "\n" + "\section{%s}" % name

first_subsec = True
def new_subsection(name):
    global document, first_subsec
    if first_subsec:
        first_subsec = False
    else:
        document += "\n" + "\\newpage"
    document += "\n" + "\subsection{%s}" % name  
    
def add_graph(fname1, fname2=None):
    global document

    if fname2 != None:
        document += "\n" + "\\begin{figure}"
        document += "\n" + "\\centering"
        document += "\n" + "\includegraphics[width=400px]{%s}" % fname1
        document += "\n" + "\includegraphics[width=400px]{%s}" % fname2
        document += "\n" + "\\end{figure}"
    else:
        document += "\n" + "\\begin{center}"
        document += "\n" + "\includegraphics[width=400px]{%s}" % fname1
        document += "\n" + "\\end{center}"
    
maths = None
mathsList = None
def start_maths():
    global document, maths, mathsList
    maths = OrderedDict()
    mathsList = []

def add_maths(name, values):
    global maths
    maths[name] = values
    mathsList.append(name)

def stop_maths():
    global document, maths, mathsList
    if len(maths.values()[0]) == 1:
        stop_maths_single()
    else:
        stop_maths_monthly()
        
def stop_maths_single():
    global document, maths, mathsList
    opKeys = maths.values()[0][0].keys()
    document += "\n" + "\\begin{center}"
    document += "\n" + "\\begin{tabular}{ l %s}" % (" | l "*len(opKeys))
    
    document += "\n &" + " & ".join(opKeys) + "\\\\"
    document += "\n" + "\\hline\n"
    first = True
    for name in mathsList:  
        document += name + " &" + " & ".join(["%.0f\euro" % maths[name][0][key] for key in opKeys]) + "\\\\\n"
        if first:
            first = False
            document += "\n\\hline\n" 
    document += "\n" + "\\end{tabular}"
    document += "\n" + "\\end{center}"
    maths = None
    
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
def stop_maths_monthly():
    global document, maths, mathsList
    opKeys = maths.values()[0][0].keys()
    first = True
    months = [ i for i in range(1, len(maths.values()[0])+1)]
    
    for name in mathsList:
        
        if first:
            first = False
            cat = name
        else:
            document += "\n" + "\\begin{center}\n"
            document += "\n\\textbf{%s/%s}~\\\\"  % (cat, name)
            document += "\n" + "\\end{center}\n"
        document += "\n" + "\\begin{center}\n"
        document += "\n" + "\\begin{tabular}{ l %s}" % ("| p{1.25cm} "*len(months))
        
        document += "&" + " & ".join([MONTHS[(month-1)%12] for month in months]) + "\\\\"
        document += "\n" + "\\hline\n"
        for key in opKeys:
            document += key
            for month in months:
                val = maths[name][month-1][key]
                if val is None:
                    val = -1
                if val == 0:
                    document += "& . "
                else:
                    document += "& %.0f" % val
            document += "\\\\\n"
        document += "\n" + "\\end{tabular}"
        document += "\n" + "\\end{center}"
    document += "\n"

def dump():
    global document
    document += "\n" + FOOTER 
    print "Generating pdf ..."
    texfile = open(Bank.OUT_FOLDER+"/report.tex", "w")
    texfile.write(document)
    texfile.close()
    pdflatex = subprocess.Popen(["pdflatex", "-output-directory", Bank.OUT_FOLDER, "%s/report.tex" % Bank.OUT_FOLDER], 
                                stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    pdflatex.communicate(document)
    if pdflatex.returncode == 0:
        print "PDF generated in %s/report.pdf" % Bank.OUT_FOLDER
    else:
        print "pdflatex return with error code %d" % pdflatex.returncode
    print "Done"