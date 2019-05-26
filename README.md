# Czech unemployment statistics

This is a Dash website I created for fun&learning purposes. 
Live example is [here](https://statistiky-nezamestnanosti-cz.herokuapp.com/)

# Installation and Running

* Run the command `git clone <repository-url>` to have this repository locally in your computer
* Change into the new directory
* Create virtual env based on requirements.txt/environment.yml
* Run the command `python dashboard/app.py`
* Open your web browser and enter the address of your local server (usually its http://127.0.0.1:5000 )
* Data are in sqlite3 DB for years 2014-2019. If you want newer data, just run `python getting_data/main_data_getter.py`