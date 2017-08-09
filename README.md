# auto_crawler_ptt_beauty_image

Auto Crawler Ptt Beauty Image Use Python Schedule

Thanks to  

[auto_crawler_ptt_beauty_image](https://github.com/twtrubiks/auto_crawler_ptt_beauty_image)
[PTT_Beauty_Spider](https://github.com/twtrubiks/PTT_Beauty_Spider) 
[schedule](https://github.com/dbader/schedule)

Deploy on Google App Engine 

## Features

* The target board and frequency could be set in the app.yaml file and deploy to a specific gae service.

* Comments below articles will be updated.

* Url of images will be saved in the database.

* Crawler multiple boards in a deployment.

* Database is a MySQL on GCP.

## How to use

* pre-requirement

`python 3.5+`

[cloud_sql_proxy](https://cloud.google.com/sql/docs/mysql/sql-proxy)

* install python packages
```cmd
virtualenv .
./bin/activate
pip install -r requirements.txt
```

* Export env variable (test the crawler on your local machine)
```bash
./cloud_sql_proxy -instances=[instance_name]:[region]:[project]=tcp:5432
export SQLALCHEMY_DATABASE_URI=mysql+mysqlconnector://[username]:[password]@localhost:3306/database
export PTT_BOARDS="target1 tager2 wanted "
export PTT_PAGES=3
export PTT_CRAWLER_INTERVAL=30
```

* start the crawler
```bash
python dbModel.py (create tables if need)
python app.py
```

## Reference

* [sqlalchemy](http://docs.sqlalchemy.org/en/latest/intro.html)
* [schedule](https://github.com/dbader/schedule)

## License

MIT license
