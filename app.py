from flask import Flask, jsonify
from flask_cors import CORS
from jinja2 import Template

from models.author import Author
from models.blog import Blog
from models.message import Message
from models.world import World
from models.linkedin_profile import LinkedInProfile

app = Flask(__name__)
CORS(app)

for model in [Message, World, Author, Blog, LinkedInProfile]:
    model.add_routes(app)

    template = """<html>
    <head>
        <title>LinkedIn Profiles</title>
    </head>
    <body>
        <h1>LinkedIn Profiles</h1>
        <ul>
            {% for profile in profiles %}
            <li>
                         {% if profile.profilePicture %}

                <img src="{{ profile.profilePicture }}" />
{% endif %}            
                <a href="{{ profile.profileLink }}">{{ profile.firstName }} {{ profile.lastName }}</a>
            </li>


            {% endfor %}
        </ul>
    </body>
</html>"""

@app.route("/")
def show_profiles():
    profiles = LinkedInProfile.get_all()
    t = Template(template)
    print(t.render(profiles=profiles))

    return t.render(profiles=profiles)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
