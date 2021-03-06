# results-sisa-online
Check whether your exam results are online.
Sends a message on Discord once the results are online. 

## Results history
| Uiterste datum examens     | Uiterste datum bekendmaking resultaten | Datum bekendmaking resultaten |
|----------------------------|----------------------------------------|-------------------------------|
| Zaterdag 1 februari 2020 ? |                                        | Maandag 3 februari 2020       |
| Zaterdag 30 januari 2021   | Vrijdag 12 februari 2021               |                               |
|                            |                                        |                               |
| Zaterdag 29 juni 2019 ?    |                                        | Maandag 1 juli 2019           |
| Zaterdag 4 juli 2020 ?     |                                        | Dinsdag 7 juli 2020           |
| Zaterdag 26 juni 2021      | Vrijdag 2 juli 2021                    |                               |
|                            |                                        |                               |
|                            |                                        | Maandag 9 september 2019      |
| Zaterdag 11 september 2021 | Vrijdag 17 september 2021              |                               |

## Dependencies
```shell
sudo apt install firefox-geckodriver

python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Configuration
Open `config.py` and enter here your sisa username and password. 
Also enter your discord bot token and the id of the channel where you want to post something once the results are online. 

If the first course in your result list of this year is not from the current semester, change the id of result (in main.py). 
You can find the idea by using inspect element and searching for the id of the location where your score should be. 

## Running manually
```shell
python3 main.py
```


## Timer
This currently runs every 10 minutes. You can change this frequency by changing `OnCalender` in `systemd/sisa-results.timer`.
Change `ExecStart` in `systemd/sisa-results.service` to the location on your machine (both the python executable from the venv and the `main.py` location).
Copy these files to your `/etc/systemd/system` directory and enable the service. 
```shell
sudo cp systemd/* /etc/systemd/system/
sudo systemctl enable sisa-results.timer --now
sudo systemctl enable sisa-bot --now
```
In `get_page_driver` (`main.py`), change opts.headless to `True`. This runs your browser in the background.  

## Note
Once it has found results, it stops running. If you want to check again, you can remove `online.pickle`
