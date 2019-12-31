from equimolar_blog import create_app
app = create_app('config')
if __name__ == '__main__':
    print(app.url_map)
    app.run(host='127.0.0.1', port=8080, debug=True)
    
