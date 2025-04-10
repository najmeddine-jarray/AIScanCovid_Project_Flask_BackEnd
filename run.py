import os
from main import app
if __name__ == '__main__':
    print("welcome ")
    # port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', debug=True)
    # app.run()
