import os
from equimolar_blog import create_app
app = create_app(os.getenv('CONFIG_NAME', default='default'))
if __name__ == '__main__':
    #print(app.url_map)
    app.run(host='0.0.0.0', port=5000)
    
