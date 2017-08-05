# auto_crawler_ptt_beauty_image

Auto Crawler Ptt Beauty Image Use Python Schedule

本專案是經由 [PTT_Beauty_Spider](https://github.com/twtrubiks/PTT_Beauty_Spider) 小修改 + [schedule](https://github.com/dbader/schedule) 完成的。

Deploy on Google App Engine 

## Features

* The target board and frequency could be set in the app.yaml file and deploy to a specific gae service.

* Comments below articles will be updated.

* Image url will be saved in the database.

* Database is a Postgresql on GCP.

## How to use

* pre-requirement

`python 3.5+`

`[cloud_sql_proxy](https://cloud.google.com/sql/docs/mysql/sql-proxy)`

* install python packages
```cmd
virtualenv .
./bin/activate
pip install -r requirements.txt
```

* Export env variable (test the crawler on your local machine)
```bash
./cloud_sql_proxy -instances=[instance_name]:[region]:[project]=tcp:5432
export SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://[username]:[password]@localhost
export PTT_BOARD=wanted
export PTT_PAGES=3
export PTT_CRAWLER_INTERVAL=10
```

* start the crawler
```bash
python app.py
```

## schedule

由於要每半小時爬取網頁一次，所以我用了 [schedule](https://github.com/dbader/schedule) , 讓程式依照我們設定的 schedule 下去執行

## Reference

* [sqlalchemy](http://docs.sqlalchemy.org/en/latest/intro.html)
* [schedule](https://github.com/dbader/schedule)

## License

MIT license
