def application(environ, start_response):
    """Simplest possible application object"""
    filename = "/srv/http/meteo/Revel.csv"
    
    output = "<html><body>%s</body></html>"
    
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
    try:
        write_line(filename, form)
    except KeyError as e:
        output = output % "<b>Missing key in the values provided: %s</b><br/>\n%%s" % e
        
    output = output % get_value_table(filename)
    
    status = '200 OK'
    response_headers = [('Content-type', 'text/html'),
    ('Content-Length', str(len(output)))]
    start_response(status, response_headers)
    return [output]