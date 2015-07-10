import os
import jinja2

##### Jinja template configuration ####
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

SECRET_WORD = "SomeSecret"