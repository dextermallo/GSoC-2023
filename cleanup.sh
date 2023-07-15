rm -rf data tmp report
rm -rf tests/docker-compose-after.yml
rm -rf tests/docker-compose-after.yml-e
rm -rf tests/docker-compose-before.yml
rm -rf tests/docker-compose-before.yml-e
rm -rf tests/logs

docker kill $(docker ps -aq) && docker rm $(docker ps -aq)