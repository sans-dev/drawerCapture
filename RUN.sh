mkdir $HOME/named_pipes
mkfifo -m a+rw $HOME/named_pipes/drawercapture_host
./eval_pipe.sh &
# docker compose build
docker compose up
rm -r $HOME/named_pipes