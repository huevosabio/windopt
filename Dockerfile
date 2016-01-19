#Basic Image
FROM huevosabio/geopy

#Create the folder where app lives
#Assumes the entirety of my app is there
RUN mkdir /var/www/windopt
WORKDIR /var/www/windopt
ADD ./requirements.txt /var/www/windopt/requirements.txt
RUN pip install -r /var/www/windopt/requirements.txt
ADD . /var/www/windopt

#Set nginx and supervisord configs
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
RUN ln -s /var/www/windopt/config/windopt_nginx.conf /etc/nginx/conf.d
RUN ln -s /var/www/windopt/config/fineng_uwsgi.ini /etc/uwsgi/vassals
RUN cp /var/www/windopt/config/uwsgi.conf /etc/init
RUN chown -R www-data:www-data /var/log/uwsgi
RUN mkdir -p /var/log/supervisord
RUN chown -R www-data:www-data /var/log/supervisord
RUN ln -s /var/www/windopt/config/supervisor-app.conf /etc/supervisor/conf.d/
RUN chown -R www-data:www-data /var/www
EXPOSE 80
CMD ["supervisord","-n"]