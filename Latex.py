import subprocess

HEADER = """
\documentclass[12pt]{article}
\usepackage[pdftex]{graphicx}
\usepackage[top=0.5in, bottom=0.5in,left=0.5in, landscape]{geometry}
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
    
def add_graph(fname):
    global document
    document += "\n" + "\\begin{center}"
    document += "\n" + "\includegraphics[width=\\textwidth]{%s}" % fname
    document += "\n" + "\\end{center}"
    document += "\n" + "\\vspace{-5em}"
    
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
    if len(maths.values()[0]) == 1:
        stop_maths_single()
    else:
        stop_maths_monthly()
def stop_maths_single():
    global document, maths, mathsList
    opKeys = maths.values()[0][0].keys()
    document += "\n" + "\\begin{center}"
    document += "\n" + "\\begin{tabular}{ l %s}" % (" | l "*len(opKeys))
    
    document += "&" + " & ".join(opKeys) + "\\\\"
    document += "\n" + "\\hline\n"
    first = True
    for name in mathsList:
        document += name + " &" + " & ".join(["%.0f\euro" % maths[name][0][key] for key in opKeys]) + "\\\\\n"
        document += "\n" 
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
            document += "\n\paragraph{%s}~\\\\"  % name
            cat = name
        else:
            document += "\n" + "\\vspace{-1em}"
            document += "\n\paragraph{%s/%s}~\\\\"  % (cat, name)
        document += "\n" + "\\begin{tabular}{ l %s}" % (" | p{1.25cm} "*len(months))
        
        document += "&" + " & ".join([MONTHS[month-1] for month in months]) + "\\\\"
        document += "\n" + "\\hline\n"
        for key in opKeys:
            document += key
            for month in months:
                val = maths[name][month-1][key] 
                if val == 0:
                    document += "& . "
                else:
                    document += "& %.0f" % val
            document += "\\\\\n"
        document += "\n" + "\\end{tabular}"
        document += "\\\\\n"

def dump():
    global document
    document += "\n" + FOOTER 
    print "Generating pdf ..."
    texfile = open("out/report-Comptes.tex", "w")
    texfile.write(document)
    texfile.close()
    out, err = subprocess.Popen(["pdflatex", "-output-directory", "out/", "out/report-Comptes.tex"], 
                                stdout=subprocess.PIPE, 
                                stdin=subprocess.PIPE).communicate(document)
    print "Done"