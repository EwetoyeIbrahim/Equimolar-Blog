import os
from equimolar_blog import create_app
app = create_app(os.getenv('CONFIG_NAME', default='default'))
if __name__ == '__main__':
    #print(app.url_map)
    app.run(host='127.0.0.1', port=5000)
    
