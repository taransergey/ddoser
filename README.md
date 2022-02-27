# The ddoser
Small application for ddos attack, was developed special for kill russian's resources :)  
## Install 
```shell
pip install -r requirements.txt
```
## Run
```shell
Usage: ddoser.py [OPTIONS]

  Run ddoser

Options:
  --target-url TEXT      ddos target url  [required]
  --proxy-url TEXT       url to proxy resourse
  --proxy-file TEXT      path to file with proxy list
  --concurrency INTEGER  concurrency level
  --count INTEGER        requests count
  --timeout INTEGER      requests timeout
  --verbose              Show verbose log
  --help                 Show this message and exit.
```
proxy-file or proxy-url should contain proxy list in format like:
```text
ip1:port1#sock5
ip2:port2#sock4
...
ipN:portN#sock4
```
**ddoser** supports only sock proxy, also can work directly without proxy
