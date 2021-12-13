# Configuration instructions

```bash
cd ~
mkdir run
mkdir logs
touch logs/gunicorn-error.log

cd text-to-speech-app
cp conf/gunicorn_start /home/tts/.cache/pypoetry/virtualenvs/text-to-audiobook-app-_fR320Lp-py3.9/bin/gunicorn_start
chmod u+x /home/tts/.cache/pypoetry/virtualenvs/text-to-audiobook-app-_fR320Lp-py3.9/bin/gunicorn_start

sudo cp conf/supervisor.conf /etc/supervisor/conf.d/text-to-speech-app.conf
sudo supervisorctl reread
sudo supervisorctl update

sudo supervisorctl restart text_to_speech_app

sudo cp conf/nginx.conf /etc/nginx/sites-available/text-to-speech-app
sudo ln -s /etc/nginx/sites-available/text-to-speech-app /etc/nginx/sites-enabled/text-to-speech-app
sudo rm /etc/nginx/sites-enabled/default
sudo service nginx restart

```