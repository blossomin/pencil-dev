cd pencil-fullhe
python3 server_costs.py -p agnews_gpt2 > logs/costs_nn5.log &
sleep 5
python3 client_costs.py > /dev/null &
cd ..
