from templite import Templite

a = Templite('''<h1> Hello {{name|a.upper|bb:"3, 0"}}!</h1>
            {% for topic in topics %}
                {% if not topic %}
                    <p>You are interested in {{topic}}.</p>
                {% endif %}
            {% endfor %}
            {# aaa #}
            ''', {'bb': lambda x, a, b: x + str(a) + str(b)})

print(a.render({
    'name': 'xxxxx',
    'a': str,
    'topics': ['a', 'b', '']
}))
